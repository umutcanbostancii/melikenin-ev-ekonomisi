import streamlit as st
import pandas as pd
import datetime
import time
import yfinance as yf
import plotly.express as px
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Melike'nin Ev Ekonomisi", page_icon="🏠", layout="wide")

# --- CSS: PREMIUM UI ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    /* Genel Stil */
    .stApp {
        background-color: #f0f2f5;
        font-family: 'Inter', sans-serif;
    }
    
    /* Kart Tasarımı */
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        border: 1px solid #eef0f2;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #64748b;
        font-weight: 600;
        margin-bottom: 5px;
    }
    
    .metric-value {
        font-size: 1.8rem;
        color: #1e293b;
        font-weight: 700;
    }
    
    .metric-delta {
        font-size: 0.85rem;
        margin-top: 5px;
        font-weight: 500;
    }
    .delta-pos { color: #10b981; }
    .delta-neg { color: #ef4444; }
    
    /* Eminevim Grid */
    .installment-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(45px, 1fr));
        gap: 8px;
        margin-top: 20px;
    }
    .installment-box {
        height: 45px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 10px;
        font-weight: bold;
        font-size: 14px;
        color: white;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .paid { 
        background: linear-gradient(135deg, #10b981 0%, #059669 100%); 
    }
    .unpaid { 
        background-color: #e2e8f0; 
        color: #94a3b8; 
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #1e293b;
    }
    /* Gizleme */
    #MainMenu {visibility: visible;}
    footer {visibility: hidden;}
    header {visibility: visible;}
    
    /* Sidebar Metin ve Başlıklar */
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] .stMarkdown, 
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] div {
        color: #f8fafc !important;
    }
    
    /* Sidebar İkonlar (SVG) */
    section[data-testid="stSidebar"] svg {
        fill: #f8fafc !important;
        color: #f8fafc !important;
    }

    /* Sidebar Button (Verileri Yenile) */
    section[data-testid="stSidebar"] button {
        background-color: #334155 !important;
        color: #f8fafc !important;
        border: 1px solid #475569 !important;
        transition: all 0.2s ease;
    }
    section[data-testid="stSidebar"] button:hover {
        background-color: #475569 !important;
        color: white !important;
        border-color: #94a3b8 !important;
    }
    
    /* Expander (Diğer Altınlar) */
    section[data-testid="stSidebar"] .streamlit-expanderHeader {
        color: #f8fafc !important;
        background-color: #334155 !important;
        border-radius: 4px;
    }
    section[data-testid="stSidebar"] .streamlit-expanderContent {
        color: #f8fafc !important;
        background-color: #1e293b !important;
        border: 1px solid #334155;
    }
    /* Expander Hover Fix */
    section[data-testid="stSidebar"] .streamlit-expanderHeader:hover {
        background-color: #475569 !important;
        color: white !important;
    }
    
    /* Input alanlarının içindeki metni düzelt (Siyah kalsın ki okunsun) */
    section[data-testid="stSidebar"] input, 
    section[data-testid="stSidebar"] textarea, 
    section[data-testid="stSidebar"] select {
        color: #1e293b !important;
    }
    
    /* Araba Resimleri */
    .car-img {
        width: 100%;
        height: 260px;
        object-fit: fill;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.01);
    }
</style>
""", unsafe_allow_html=True)

# --- GOOGLE SHEETS BAĞLANTISI ---
@st.cache_resource
def init_connection():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
    client = gspread.authorize(creds)
    return client

def get_sheet():
    client = init_connection()
    try:
        sheet = client.open("TargetLock_DB")
        return sheet
    except gspread.SpreadsheetNotFound:
        st.error("Google Sheet 'TargetLock_DB' bulunamadı. Lütfen oluşturduğunuzdan ve paylaştığınızdan emin olun.")
        st.stop()

# --- VERİTABANI İŞLEMLERİ (SHEETS) ---
def init_db():
    sheet = get_sheet()
    
    # Transactions Tab
    try:
        ws_tx = sheet.worksheet("transactions")
    except:
        ws_tx = sheet.add_worksheet(title="transactions", rows="1000", cols="20")
        ws_tx.append_row(["id", "date", "type", "category", "amount", "source", "description", "is_necessary", "gold_gram", "gold_price", "gold_type", "installment_number"])

    # Settings Tab
    try:
        ws_set = sheet.worksheet("settings")
    except:
        ws_set = sheet.add_worksheet(title="settings", rows="100", cols="2")
        ws_set.append_row(["key", "value"])
        defaults = {
            'target_amount': 1300000,
            'installment_count': 40,
            'installment_amount': 40000,
            'salary_umutcan': 0,
            'salary_melike': 0,
            'usd_rate': 42.0,
            'eur_rate': 49.0
        }
        for k, v in defaults.items():
            ws_set.append_row([k, v])

    # Categories Tab
    try:
        ws_cat = sheet.worksheet("categories")
    except:
        ws_cat = sheet.add_worksheet(title="categories", rows="100", cols="5")
        ws_cat.append_row(["name", "type", "is_installment", "total_amount", "total_months"])
        default_expenses = ["Mutfak", "Fatura", "Akaryakıt", "Eğlence", "Giyim", "Eminevim Taksit", "Kredi Kartı Ödeme", "Diğer"]
        default_incomes = ["Maaş/Kazanç", "Ek Gelir", "Kira Geliri"]
        for cat in default_expenses:
            ws_cat.append_row([cat, "Gider", 0, 0, 0])
        for cat in default_incomes:
            ws_cat.append_row([cat, "Gelir", 0, 0, 0])

    # Planned Expenses Tab
    try:
        ws_plan = sheet.worksheet("planned_expenses")
    except:
        ws_plan = sheet.add_worksheet(title="planned_expenses", rows="100", cols="4")
        ws_plan.append_row(["id", "name", "amount", "frequency"])

@st.cache_data(ttl=600)
def get_data(worksheet_name):
    sheet = get_sheet()
    ws = sheet.worksheet(worksheet_name)
    return pd.DataFrame(ws.get_all_records())

def clear_cache():
    st.cache_data.clear()

def add_row(worksheet_name, row_data):
    sheet = get_sheet()
    ws = sheet.worksheet(worksheet_name)
    ws.append_row(row_data)
    clear_cache()

def delete_row_by_id(worksheet_name, id_val, id_col_name="id"):
    sheet = get_sheet()
    ws = sheet.worksheet(worksheet_name)
    cell = ws.find(str(id_val), in_column=1 if id_col_name=="id" else None) # Assuming ID is usually col 1
    if not cell and id_col_name != "id": # Search by name for categories
         cell = ws.find(str(id_val))
    
    if cell:
        ws.delete_rows(cell.row)
        clear_cache()

def update_row_by_id(worksheet_name, id_val, col_name, new_val):
    sheet = get_sheet()
    ws = sheet.worksheet(worksheet_name)
    cell = ws.find(str(id_val), in_column=1) # Assuming ID is col 1
    if cell:
        # Find col index
        header = ws.row_values(1)
        try:
            col_idx = header.index(col_name) + 1
            ws.update_cell(cell.row, col_idx, new_val)
            clear_cache()
        except:
            pass

def update_settings(key, value):
    sheet = get_sheet()
    ws = sheet.worksheet("settings")
    cell = ws.find(key, in_column=1)
    if cell:
        ws.update_cell(cell.row, 2, value)
    else:
        ws.append_row([key, value])
    clear_cache()

def get_next_id(worksheet_name):
    df = get_data(worksheet_name)
    if df.empty: return 1
    # Check if 'id' column exists and has numeric values
    if 'id' in df.columns and pd.api.types.is_numeric_dtype(df['id']):
        return int(df['id'].max()) + 1
    return 1

# --- HELPER WRAPPERS FOR APP LOGIC ---
def add_transaction(date, type, category, amount, source, description, is_necessary=1, gold_gram=0, gold_price=0, gold_type="", installment_number=0):
    next_id = get_next_id("transactions")
    add_row("transactions", [next_id, str(date), type, category, amount, source, description, is_necessary, gold_gram, gold_price, gold_type, installment_number])

def add_category(name, type, is_inst=0, tot_amt=0, tot_mon=0):
    add_row("categories", [name, type, is_inst, tot_amt, tot_mon])

def add_planned_expense(name, amount, frequency):
    next_id = get_next_id("planned_expenses")
    add_row("planned_expenses", [next_id, name, amount, frequency])

def get_categories(type_filter):
    df = get_data("categories")
    if df.empty: return []
    return df[df['type'] == type_filter]['name'].tolist()

def get_category_details(name):
    df = get_data("categories")
    if df.empty: return (0, 0)
    row = df[df['name'] == name]
    if not row.empty:
        return (row.iloc[0]['is_installment'], row.iloc[0]['total_months'])
    return (0, 0)

# --- FİNANS MOTORU ---
GOLD_TYPES = {
    "Gram 24k": 1.0,
    "Gram 22k": 0.93,
    "Çeyrek Altın": 1.605,
    "Yarım Altın": 3.21,
    "Tam Altın": 6.42,
    "Cumhuriyet": 6.61
}

@st.cache_data(ttl=3600)
def get_market_data():
    try:
        tickers = yf.download("TRY=X EURTRY=X GC=F", period="5d", progress=False)['Close']
        dolar_tl = tickers['TRY=X'].dropna().iloc[-1]
        euro_tl = tickers['EURTRY=X'].dropna().iloc[-1]
        ons_dolar = tickers['GC=F'].dropna().iloc[-1]
        gram_tl = (ons_dolar * dolar_tl) / 31.1035
        return {"usd": round(dolar_tl, 2), "eur": round(euro_tl, 2), "gold": round(gram_tl, 2)}
    except Exception as e:
        print(f"API Hatası: {e}")
        return None

def get_financial_summary():
    df = get_data("transactions")
    if df.empty:
        return {"Umutcan Kasa": 0, "Melike Kasa": 0, "Ortak Kasa": 0, "Kredi Kartı Borcu": 0}, 0, 0, 0, {}, 0

    # Ensure numeric columns are numeric
    cols = ['amount', 'gold_gram', 'gold_price']
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)

    # Incomes
    incomes = df[df['type'] == 'Gelir'].groupby('source')['amount'].sum().to_dict()
    
    # Expenses
    expenses = df[df['type'] == 'Gider'].groupby('source')['amount'].sum().to_dict()
    
    # Total Expense All Time
    total_expense_all_time = df[df['type'] == 'Gider']['amount'].sum()
    
    # Gold
    gold_df = df[df['type'] == 'Altın Alım']
    total_gold_cost = gold_df['amount'].sum()
    
    gold_inventory = {}
    total_pure_gold = 0
    if not gold_df.empty:
        # Group by gold_type
        g_grouped = gold_df.groupby('gold_type')['gold_gram'].sum()
        for g_type, count in g_grouped.items():
            multiplier = GOLD_TYPES.get(g_type, 1.0)
            pure_equivalent = count * multiplier
            total_pure_gold += pure_equivalent
            gold_inventory[g_type] = count
            
    # CC Payments
    paid_cc = df[(df['type'] == 'Gider') & (df['category'] == 'Kredi Kartı Ödeme')]['amount'].sum()

    # Balances
    source_map = {
        "Umutcan Maaş": "Umutcan Kasa", "Melike Temizlik": "Melike Kasa", "Ek Gelir": "Ortak Kasa",
        "Umutcan Kasa": "Umutcan Kasa", "Melike Kasa": "Melike Kasa", "Ortak Kasa": "Ortak Kasa"
    }
    
    balances = {"Umutcan Kasa": 0, "Melike Kasa": 0, "Ortak Kasa": 0, "Kredi Kartı Borcu": 0}
    
    for src, amt in incomes.items():
        mapped = source_map.get(src, "Ortak Kasa")
        if mapped in balances: balances[mapped] += amt
        
    for src, amt in expenses.items():
        if src == "Kredi Kartı":
            balances["Kredi Kartı Borcu"] += amt
        else:
            mapped = source_map.get(src, "Ortak Kasa")
            if mapped in balances: balances[mapped] -= amt

    balances["Kredi Kartı Borcu"] -= paid_cc 
    total_home_safe = balances["Umutcan Kasa"] + balances["Melike Kasa"] + balances["Ortak Kasa"]
    
    return balances, total_pure_gold, total_gold_cost, total_home_safe, gold_inventory, total_expense_all_time

# --- UI HELPER FUNCTIONS ---
def metric_card(col, label, value, delta=None, delta_color="pos"):
    with col:
        delta_html = ""
        if delta:
            color_class = "delta-pos" if delta_color == "pos" else "delta-neg"
            delta_html = f"<div class='metric-delta {color_class}'>{delta}</div>"
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            {delta_html}
        </div>
        """, unsafe_allow_html=True)

# --- UI BAŞLANGICI ---
init_db()

# Piyasa Verilerini Çek
market_data = get_market_data()

if 'gold_manual_mode' not in st.session_state: st.session_state.gold_manual_mode = False
if 'manual_gold_price' not in st.session_state: st.session_state.manual_gold_price = 5700.0 

with st.sidebar:
    st.title("Melike'nin Ev Ekonomisi 🏠")
    if st.button("🔄 Verileri Yenile"):
        clear_cache()
        st.rerun()
    page = st.radio("Menü", ["Ana Sayfa 📊", "Raporlar 📈", "Gider Planla 📅", "İşlem Ekle ➕", "Geçmiş & Düzenle 📝", "Eminevim 🏠", "Ayarlar 🛠️"])
    
    st.markdown("---")
    st.subheader("🥇 Altın Kurları")
    
    if market_data:
        live_gold = market_data['gold']
        st.caption(f"✅ Canlı Veri (Yahoo)")
        st.caption(f"💲 Dolar: {market_data['usd']} | 💶 Euro: {market_data['eur']}")
    else:
        st.warning("⚠️ Manuel Mod")
        live_gold = st.session_state.manual_gold_price
    
    gold_prices = {k: live_gold * v for k, v in GOLD_TYPES.items()}
    
    # Ana Gösterge (Custom HTML for smaller size)
    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
        <div>
            <div style="font-size: 0.8rem; color: #94a3b8;">24 Ayar</div>
            <div style="font-size: 1.1rem; font-weight: 500; color: white;">{gold_prices['Gram 24k']:,.0f} ₺</div>
        </div>
        <div>
            <div style="font-size: 0.8rem; color: #94a3b8;">22 Ayar</div>
            <div style="font-size: 1.1rem; font-weight: 500; color: white;">{gold_prices['Gram 22k']:,.0f} ₺</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("Diğer Altınlar", expanded=True):
        st.write(f"**Çeyrek:** {gold_prices['Çeyrek Altın']:,.0f} ₺")
        st.write(f"**Yarım:** {gold_prices['Yarım Altın']:,.0f} ₺")
        st.write(f"**Tam:** {gold_prices['Tam Altın']:,.0f} ₺")
        st.write(f"**Cumhuriyet:** {gold_prices['Cumhuriyet']:,.0f} ₺")

    st.markdown("---")
    on_manual = st.toggle("Manuel Kur Gir", value=st.session_state.gold_manual_mode)
    st.session_state.gold_manual_mode = on_manual
    
    if on_manual:
        st.session_state.manual_gold_price = st.number_input("Gram (24k) Baz Fiyat", value=st.session_state.manual_gold_price, step=10.0)
        if not market_data:
            live_gold = st.session_state.manual_gold_price

# --- SAYFA: KOKPİT ---
if page == "Ana Sayfa 📊":
    df_set = get_data("settings")
    sets = dict(zip(df_set['key'], df_set['value']))
    
    balances, total_pure_gold, total_gold_cost, total_home_safe, gold_inv, total_expense = get_financial_summary()
    
    usd_rate = market_data['usd'] if market_data else sets['usd_rate']
    eur_rate = market_data['eur'] if market_data else sets['eur_rate']
    
    target = sets['target_amount']
    current_gold_value = total_pure_gold * (market_data['gold'] if market_data else st.session_state.manual_gold_price)
    gold_profit = current_gold_value - total_gold_cost
    net_wealth = total_home_safe + current_gold_value - balances["Kredi Kartı Borcu"]
    
    wealth_usd = net_wealth / usd_rate if usd_rate > 0 else 0
    wealth_eur = net_wealth / eur_rate if eur_rate > 0 else 0
    
    st.markdown(f"""
    ### 🗓️ {datetime.date.today().strftime('%d.%m.%Y')} | 👨🏻‍💻 Umutcan: {sets['salary_umutcan']:,.0f} TL | 👩🏻‍💼 Melike: {sets['salary_melike']:,.0f} TL | 📉 Toplam Gider: {total_expense:,.0f} TL
    """)
    
    h4, h5, h6 = st.columns(3)
    source_lbl = "Canlı Kur (Yahoo)" if market_data else "Manuel Kur"
    metric_card(h4, "💵 Dolar / Euro", f"{usd_rate:.2f} / {eur_rate:.2f}", source_lbl)
    metric_card(h5, "Toplam Varlık ($)", f"${wealth_usd:,.0f}", "Nakit + Altın")
    metric_card(h6, "Toplam Varlık (€)", f"€{wealth_eur:,.0f}", "Nakit + Altın")
    
    st.markdown("---")
    st.markdown("## 🏎️ Finansal Durum")
    
    c1, c2, c3 = st.columns(3)
    metric_card(c1, "🏠 Ev Kasası (Nakit)", f"{total_home_safe:,.0f} TL")
    metric_card(c2, f"💎 Net Varlık ({gold_profit:+,.0f} TL Fark)", f"{net_wealth:,.0f} TL")
    metric_card(c3, "🎯 Hedefe Kalan", f"{target - net_wealth:,.0f} TL")

    st.markdown("<br>", unsafe_allow_html=True)
    
    st.subheader("Kasa Detayları")
    k1, k2, k3, k4 = st.columns(4)
    metric_card(k1, "👨🏻‍💻 Umutcan", f"{balances['Umutcan Kasa']:,.0f} TL")
    metric_card(k2, "👩🏻‍💼 Melike", f"{balances['Melike Kasa']:,.0f} TL")
    metric_card(k3, "🤝 Ortak", f"{balances['Ortak Kasa']:,.0f} TL")
    metric_card(k4, "💳 Kart Borcu", f"{balances['Kredi Kartı Borcu']:,.0f} TL", delta_color="neg")
    
    st.markdown("---")
    
    st.subheader("📦 Aktif Taksitler & Borçlar")
    installments = get_data("categories")
    installments = installments[installments['is_installment'] == 1]
    
    if not installments.empty:
        df_tx = get_data("transactions")
        for idx, row in installments.iterrows():
            inst_name = row['name']
            inst_total = row['total_amount']
            inst_months = row['total_months']
            
            paid_amt = 0
            last_inst_no = 0
            
            if not df_tx.empty:
                inst_txs = df_tx[df_tx['category'] == inst_name]
                if not inst_txs.empty:
                    paid_amt = inst_txs['amount'].sum()
                    last_inst_no = inst_txs['installment_number'].max()
            
            rem_amt = inst_total - paid_amt
            progress = min(paid_amt / inst_total, 1.0) if inst_total > 0 else 0
            
            with st.container():
                c_head, c_del = st.columns([5, 1])
                c_head.write(f"**{inst_name}**")
                if c_del.button("🗑️", key=f"del_cat_{inst_name}", help="Bu taksit takibini sil"):
                    delete_row_by_id("categories", inst_name, id_col_name="name")
                    st.success(f"{inst_name} takibi silindi.")
                    time.sleep(0.5)
                    st.rerun()
                
                st.progress(progress)
                c1, c2, c3 = st.columns(3)
                c1.caption(f"Ödenen: {paid_amt:,.0f} TL")
                c2.caption(f"Kalan: {rem_amt:,.0f} TL")
                c3.caption(f"Durum: {last_inst_no} / {inst_months} Taksit")
                st.markdown("<br>", unsafe_allow_html=True)
    else:
        st.info("Aktif taksit takibi yok.")
    
    st.markdown("---")
    
    g1, g2 = st.columns([2, 1])
    with g1:
        st.subheader("🥇 Altın Portföyü")
        if gold_inv:
            inv_df = pd.DataFrame(list(gold_inv.items()), columns=["Tip", "Adet/Gram"])
            st.dataframe(inv_df, hide_index=True, use_container_width=True)
        else:
            st.info("Henüz altın yok.")
            
    with g2:
        st.subheader("Değerleme")
        st.markdown(f"""
        <div class="metric-card">
            <p><b>Toplam Has Altın:</b> {total_pure_gold:.2f} Gr</p>
            <p><b>Maliyet:</b> {total_gold_cost:,.0f} TL</p>
            <p><b>Güncel Değer:</b> {current_gold_value:,.0f} TL</p>
            <hr>
            <div class="metric-label">Net Kâr/Zarar</div>
            <h3 style="color: {'#10b981' if gold_profit >= 0 else '#ef4444'}; margin-top:0;">
                {gold_profit:+,.0f} TL
            </h3>
        </div>
        """, unsafe_allow_html=True)

# --- SAYFA: GİDER PLANLA ---
elif page == "Gider Planla 📅":
    st.markdown("## 📅 Aylık Gider Planlaması")
    st.info("💡 Burası sadece planlama içindir. Ana bakiyenizi etkilemez.")
    
    c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
    p_name = c1.text_input("Gider Adı (Örn: Metro)", key="p_name")
    p_amt = c2.number_input("Tutar", min_value=0.0, key="p_amt")
    p_freq = c3.selectbox("Sıklık", ["Günlük", "Haftalık", "Aylık", "Yıllık"], key="p_freq")
    
    if c4.button("Ekle", key="p_add"):
        if p_name and p_amt > 0:
            add_planned_expense(p_name, p_amt, p_freq)
            st.success("Eklendi")
            st.rerun()
            
    st.markdown("---")
    
    plans = get_data("planned_expenses")
    total_monthly_need = 0
    
    if not plans.empty:
        for idx, p in plans.iterrows():
            monthly_cost = 0
            freq = p['frequency']
            amt = p['amount']
            
            if freq == "Günlük": monthly_cost = amt * 30
            elif freq == "Haftalık": monthly_cost = amt * 4
            elif freq == "Aylık": monthly_cost = amt
            elif freq == "Yıllık": monthly_cost = amt / 12
            
            total_monthly_need += monthly_cost
            
            with st.container():
                c1, c2, c3, c4, c5 = st.columns([3, 2, 2, 2, 1])
                c1.write(f"**{p['name']}**")
                c2.write(f"{amt:,.0f} TL")
                c3.write(f"{freq}")
                c4.write(f"Ort. Aylık: **{monthly_cost:,.0f} TL**")
                if c5.button("🗑️", key=f"del_plan_{p['id']}"):
                    delete_row_by_id("planned_expenses", p['id'])
                    st.rerun()
                st.markdown("<hr style='margin:5px 0;'>", unsafe_allow_html=True)
    else:
        st.info("Henüz planlanmış gider yok.")
        
    st.markdown("### 📊 Özet Analiz")
    
    df_set = get_data("settings")
    sets = dict(zip(df_set['key'], df_set['value']))
    
    total_income = sets['salary_umutcan'] + sets['salary_melike']
    remaining = total_income - total_monthly_need
    
    m1, m2, m3 = st.columns(3)
    metric_card(m1, "Toplam Hane Geliri", f"{total_income:,.0f} TL", "Maaşlar Toplamı")
    metric_card(m2, "Planlanan Gider", f"{total_monthly_need:,.0f} TL", "Tahmini İhtiyaç", "neg")
    metric_card(m3, "Serbest Bakiye", f"{remaining:,.0f} TL", "Tasarruf Potansiyeli", "pos" if remaining > 0 else "neg")

# --- SAYFA: RAPORLAR ---
elif page == "Raporlar 📈":
    st.markdown("## 📊 Detaylı Analiz")
    
    df = get_data("transactions")
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])
        
        c1, c2, c3 = st.columns(3)
        period = c1.selectbox("Dönem", ["Tüm Zamanlar", "Bu Ay", "Geçen Ay", "Bu Yıl"])
        tx_type = c2.multiselect("İşlem Tipi", df['type'].unique(), default=df['type'].unique())
        
        today = datetime.datetime.now()
        if period == "Bu Ay":
            df = df[df['date'].dt.month == today.month]
        elif period == "Geçen Ay":
            last_month = today.month - 1 if today.month > 1 else 12
            df = df[df['date'].dt.month == last_month]
        elif period == "Bu Yıl":
            df = df[df['date'].dt.year == today.year]
            
        df = df[df['type'].isin(tx_type)]
        
        total_in = df[df['type']=='Gelir']['amount'].sum()
        total_out = df[df['type']=='Gider']['amount'].sum()
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Toplam Gelir", f"{total_in:,.0f} TL")
        m2.metric("Toplam Gider", f"{total_out:,.0f} TL")
        m3.metric("Net Akış", f"{total_in - total_out:,.0f} TL")
        
        st.subheader("Kategori Bazlı Harcamalar")
        expense_df = df[df['type']=='Gider']
        if not expense_df.empty:
            fig = px.pie(expense_df, values='amount', names='category', hole=0.4)
            st.plotly_chart(fig, use_container_width=True)
            
        st.subheader("İşlem Dökümü")
        st.dataframe(df.sort_values(by='date', ascending=False), use_container_width=True)
        
    else:
        st.info("Henüz veri yok.")

# --- SAYFA: İŞLEM EKLE ---
elif page == "İşlem Ekle ➕":
    st.markdown("## 📝 Yeni İşlem")
    
    t1, t2, t3 = st.tabs(["💸 Gider", "💰 Gelir", "🥇 Altın"])
    
    with t1:
        c1, c2 = st.columns(2)
        amt = c1.number_input("Tutar", min_value=0.0, step=10.0, key="g_amt")
        
        cats = get_categories("Gider")
        cats.append("➕ Yeni Kategori Ekle...")
        cat_select = c1.selectbox("Kategori", cats, key="g_cat")
        
        new_cat_name = None
        is_inst = False
        inst_total = 0.0
        inst_months = 0
        
        is_selected_inst, selected_inst_months = get_category_details(cat_select)
        current_inst_no = 0
        
        if cat_select == "➕ Yeni Kategori Ekle...":
            st.info("Yeni Kategori Oluşturuluyor...")
            new_cat_name = st.text_input("Kategori Adı (Örn: PS5 Taksidi)", key="g_new_name")
            is_inst = st.toggle("Bu bir Taksit/Borç mu?", key="g_is_inst")
            if is_inst:
                inst_total = st.number_input("Toplam Borç Tutarı", min_value=0.0, key="g_inst_tot")
                inst_months = st.number_input("Toplam Taksit Sayısı", min_value=1, key="g_inst_mon")
        elif is_selected_inst:
            st.info(f"Bu bir taksit ödemesi. ({selected_inst_months} Taksit)")
            current_inst_no = st.number_input("Kaçıncı Taksit?", min_value=1, max_value=selected_inst_months, step=1, key="g_curr_inst")
        
        src = c2.selectbox("Kaynak", ["Umutcan Kasa", "Melike Kasa", "Ortak Kasa", "Kredi Kartı"], key="g_src")
        desc = c2.text_input("Açıklama", key="g_desc")
        
        if st.button("Gideri Kaydet", key="btn_gider"):
            final_cat = cat_select
            
            if cat_select == "➕ Yeni Kategori Ekle..." and new_cat_name:
                add_category(new_cat_name, "Gider", 1 if is_inst else 0, inst_total, inst_months)
                final_cat = new_cat_name
                st.success(f"Yeni kategori '{new_cat_name}' oluşturuldu.")
            
            add_transaction(datetime.date.today(), 'Gider', final_cat, amt, src, desc, 1, installment_number=current_inst_no)
            st.success("İşlem Kaydedildi.")
            time.sleep(1)
            st.rerun()
            
    with t2:
        c1, c2 = st.columns(2)
        amt = c1.number_input("Tutar", min_value=0.0, key="i_amt")
        
        cats = get_categories("Gelir")
        cats.append("➕ Yeni Kategori Ekle...")
        cat_select = c1.selectbox("Kategori", cats, key="i_cat")
        
        new_cat_name = None
        if cat_select == "➕ Yeni Kategori Ekle...":
            new_cat_name = st.text_input("Gelir Kalemi Adı", key="i_new_name")
        
        src = c2.selectbox("Kasa", ["Umutcan Kasa", "Melike Kasa", "Ortak Kasa"], key="i_src")
        desc = st.text_input("Açıklama", key="i_desc")
        
        if st.button("Geliri Kaydet", key="btn_gelir"):
            final_cat = cat_select
            if cat_select == "➕ Yeni Kategori Ekle..." and new_cat_name:
                add_category(new_cat_name, "Gelir")
                final_cat = new_cat_name
            
            add_transaction(datetime.date.today(), 'Gelir', final_cat, amt, src, desc, 1)
            st.success("Kaydedildi.")
            time.sleep(1)
            st.rerun()
            
    with t3:
        c1, c2 = st.columns(2)
        g_type = c1.selectbox("Altın Tipi", list(GOLD_TYPES.keys()), key="gold_type")
        count = c2.number_input("Adet / Gram", min_value=0.0, step=0.5, key="gold_count")
        tl = c1.number_input("Toplam Ödenen TL", step=100.0, key="gold_tl")
        src = c2.selectbox("Ödeme Kaynağı", ["Umutcan Kasa", "Melike Kasa", "Ortak Kasa", "Kredi Kartı"], key="gold_src")
        
        if st.button("Altın Alımını Kaydet", key="btn_gold"):
            add_transaction(datetime.date.today(), 'Altın Alım', 'Yatırım', tl, src, 'Altın', 1, gold_gram=count, gold_price=tl/count if count>0 else 0, gold_type=g_type)
            st.success("Portföye Eklendi.")
            time.sleep(1)
            st.rerun()

# --- SAYFA: GEÇMİŞ & DÜZENLE ---
elif page == "Geçmiş & Düzenle 📝":
    st.markdown("## 📋 İşlem Yönetimi")
    
    if 'edit_id' not in st.session_state: st.session_state.edit_id = None
    
    if st.session_state.edit_id:
        st.warning(f"ID: {st.session_state.edit_id} Düzenleniyor...")
        df = get_data("transactions")
        tx = df[df['id'] == st.session_state.edit_id].iloc[0]
        
        with st.form("edit_form"):
            if tx['type'] == 'Altın Alım':
                st.info("🥇 Altın İşlemi Düzenleme")
                new_type = st.selectbox("Altın Tipi", list(GOLD_TYPES.keys()), index=list(GOLD_TYPES.keys()).index(tx['gold_type']) if tx['gold_type'] in GOLD_TYPES else 0)
                new_gram = st.number_input("Adet / Gram", value=float(tx['gold_gram']), step=0.5)
                new_amt = st.number_input("Toplam Maliyet (TL)", value=float(tx['amount']), step=100.0)
                new_desc = st.text_input("Açıklama", value=tx['description'])
                
                c1, c2 = st.columns(2)
                if c1.form_submit_button("💾 Güncelle"):
                    unit_price = new_amt / new_gram if new_gram > 0 else 0
                    update_row_by_id("transactions", st.session_state.edit_id, "amount", new_amt)
                    update_row_by_id("transactions", st.session_state.edit_id, "description", new_desc)
                    update_row_by_id("transactions", st.session_state.edit_id, "gold_gram", new_gram)
                    update_row_by_id("transactions", st.session_state.edit_id, "gold_price", unit_price)
                    update_row_by_id("transactions", st.session_state.edit_id, "gold_type", new_type)
                    
                    st.session_state.edit_id = None
                    st.success("Altın işlemi güncellendi!")
                    st.rerun()
            else:
                new_amt = st.number_input("Tutar", value=float(tx['amount']))
                new_desc = st.text_input("Açıklama", value=tx['description'])
                
                c1, c2 = st.columns(2)
                if c1.form_submit_button("💾 Güncelle"):
                    update_row_by_id("transactions", st.session_state.edit_id, "amount", new_amt)
                    update_row_by_id("transactions", st.session_state.edit_id, "description", new_desc)
                    st.session_state.edit_id = None
                    st.success("Güncellendi!")
                    st.rerun()
            
            if c2.form_submit_button("❌ İptal"):
                st.session_state.edit_id = None
                st.rerun()
    
    else:
        df = get_data("transactions")
        if not df.empty:
            df = df.sort_values(by='id', ascending=False).head(50)
            for idx, tx in df.iterrows():
                with st.container():
                    c1, c2, c3, c4, c5 = st.columns([2, 2, 2, 3, 2])
                    c1.write(f"**{tx['date']}**")
                    
                    type_lbl = tx['type']
                    if tx['type'] == "Altın Alım": type_lbl = f"{tx['gold_type']} ({tx['gold_gram']})"
                    
                    c2.write(type_lbl)
                    c3.write(f"{tx['amount']:,.0f} TL")
                    c4.write(f"{tx['category']} - {tx['description']}")
                    
                    b1, b2 = c5.columns(2)
                    if b1.button("✏️", key=f"edit_{tx['id']}"):
                        st.session_state.edit_id = tx['id']
                        st.rerun()
                    if b2.button("🗑️", key=f"del_{tx['id']}"):
                        delete_row_by_id("transactions", tx['id'])
                        st.rerun()
                    st.markdown("---")

# --- SAYFA: EMİNEVİM ---
elif page == "Eminevim 🏠":
    st.markdown("## 🚗 Araba Hedefi & Eminevim")
    
    img_col1, img_col2, img_col3 = st.columns(3)
    with img_col1:
        st.markdown('<img src="https://www.arabahabercisi.com/wp-content/uploads/2022/10/2022-VW-Golf-Fiyatlar%C4%B1-Ekim-600x381.jpg" class="car-img">', unsafe_allow_html=True)
    with img_col2:
        st.markdown('<img src="https://arabavs.com/images/car_images/2_2_a4223_19.jpg" class="car-img">', unsafe_allow_html=True)
    with img_col3:
        st.markdown('<img src="https://arabavs.com/images/car_images/2_2_e3c2a_0.jpg" class="car-img">', unsafe_allow_html=True)
    
    df_set = get_data("settings")
    sets = dict(zip(df_set['key'], df_set['value']))
    
    # Varsayılan değerler yoksa ata (Eski veritabanları için koruma)
    target_amt = float(sets.get('target_amount', 1300000))
    fee_rate = float(sets.get('eminevim_fee_rate', 0.07))
    start_date_str = str(sets.get('eminevim_start_date', datetime.date.today().strftime('%Y-%m-%d')))
    delivery_month = int(sets.get('eminevim_delivery_month', 5))
    
    try:
        start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
    except:
        start_date = datetime.date.today()

    # Hesaplamalar
    org_fee = target_amt * fee_rate # Dosya Masrafı
    total_debt = target_amt + org_fee # Toplam Borç (Çekilecek + Masraf)
    delivery_threshold = target_amt * 0.40 # Teslimat Barajı (%40)
    
    # Teslimat Tarihi Hesaplama
    # Basitçe: Başlangıç + X ay
    delivery_date = start_date + datetime.timedelta(days=delivery_month*30)
    days_left = (delivery_date - datetime.date.today()).days
    
    # Ödemeler
    df_tx = get_data("transactions")
    paid_amount = 0
    if not df_tx.empty:
        paid_amount = df_tx[df_tx['category'] == 'Eminevim Taksit']['amount'].sum()
    
    remaining_total = total_debt - paid_amount
    
    # İlerlemeler
    progress_total = min(paid_amount / total_debt, 1.0) if total_debt > 0 else 0
    progress_threshold = min(paid_amount / delivery_threshold, 1.0) if delivery_threshold > 0 else 0
    
    # --- ÜST BİLGİ KARTLARI ---
    k1, k2, k3, k4 = st.columns(4)
    metric_card(k1, "Çekilecek Tutar", f"{target_amt:,.0f} TL")
    metric_card(k2, "Dosya Masrafı (%{:.0f})".format(fee_rate*100), f"{org_fee:,.0f} TL")
    metric_card(k3, "Toplam Geri Ödeme", f"{total_debt:,.0f} TL")
    metric_card(k4, "Kalan Borç", f"{remaining_total:,.0f} TL", "neg")
    
    st.markdown("---")
    
    # --- GRAFİKLER VE DURUM ---
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.subheader("📊 İlerleme Durumu")
        
        st.write(f"**Genel Borç Ödemesi** ({paid_amount:,.0f} / {total_debt:,.0f} TL)")
        st.progress(progress_total)
        
        st.write(f"**Teslimat Barajı (%40)** ({paid_amount:,.0f} / {delivery_threshold:,.0f} TL)")
        # Baraj rengi için custom html bar veya standart bar
        st.progress(progress_threshold)
        if paid_amount >= delivery_threshold:
            st.success("🎉 Tebrikler! %40 Barajı aşıldı, teslimat hakkı kazanıldı!")
        else:
            st.info(f"Teslimat hakkı için **{delivery_threshold - paid_amount:,.0f} TL** daha ödenmeli.")

    with c2:
        st.subheader("⏳ Teslimat Sayacı")
        st.markdown(f"""
        <div class="metric-card" style="text-align: center;">
            <div class="metric-label">Tahmini Teslimat</div>
            <div class="metric-value" style="font-size: 1.5rem;">{delivery_date.strftime('%d.%m.%Y')}</div>
            <hr>
            <div class="metric-label">Kalan Süre</div>
            <h2 style="color: #3b82f6; margin:0;">{max(days_left, 0)} Gün</h2>
            <div style="font-size: 0.8rem; color: #64748b;">({max(days_left//30, 0)} Ay)</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    
    # --- ÖDEME GEÇMİŞİ ---
    st.subheader("📝 Ödeme Geçmişi")
    if not df_tx.empty:
        emi_txs = df_tx[df_tx['category'] == 'Eminevim Taksit'].sort_values(by='date', ascending=False)
        if not emi_txs.empty:
            st.dataframe(emi_txs[['date', 'amount', 'description']], use_container_width=True, hide_index=True)
        else:
            st.info("Henüz ödeme kaydı bulunamadı.")
    else:
        st.info("Henüz işlem yok.")

# --- SAYFA: AYARLAR ---
elif page == "Ayarlar 🛠️":
    st.header("⚙️ Sistem Ayarları")
    
    with st.form("settings"):
        df_set = get_data("settings")
        sets = dict(zip(df_set['key'], df_set['value']))
        
        st.subheader("🏠 Eminevim Ayarları")
        c1, c2 = st.columns(2)
        target_amt = c1.number_input("Çekilecek Tutar (Hedef)", value=float(sets.get('target_amount', 1300000)))
        fee_rate_inp = c2.number_input("Dosya Masrafı Oranı (0.07 = %7)", value=float(sets.get('eminevim_fee_rate', 0.07)), step=0.01, format="%.2f")
        
        c3, c4 = st.columns(2)
        start_date_val = sets.get('eminevim_start_date', datetime.date.today().strftime('%Y-%m-%d'))
        try:
            d_val = datetime.datetime.strptime(str(start_date_val), '%Y-%m-%d').date()
        except:
            d_val = datetime.date.today()
            
        start_date_inp = c3.date_input("Proje Başlangıç Tarihi", value=d_val)
        del_month_inp = c4.number_input("Teslimat Kaçıncı Ayda?", value=int(sets.get('eminevim_delivery_month', 5)))

        st.subheader("Diğer Ayarlar")
        c5, c6 = st.columns(2)
        su = c5.number_input("Umutcan Maaş", value=float(sets.get('salary_umutcan', 0)))
        sm = c6.number_input("Melike Gelir", value=float(sets.get('salary_melike', 0)))
        
        usd = c5.number_input("Dolar Kuru (Sabit)", value=float(sets.get('usd_rate', 42.0)))
        eur = c6.number_input("Euro Kuru (Sabit)", value=float(sets.get('eur_rate', 49.0)))
        
        if st.form_submit_button("Ayarları Kaydet"):
            update_settings('target_amount', target_amt)
            update_settings('eminevim_fee_rate', fee_rate_inp)
            update_settings('eminevim_start_date', start_date_inp.strftime('%Y-%m-%d'))
            update_settings('eminevim_delivery_month', del_month_inp)
            
            update_settings('salary_umutcan', su)
            update_settings('salary_melike', sm)
            update_settings('usd_rate', usd)
            update_settings('eur_rate', eur)
            st.success("Ayarlar güncellendi!")
            time.sleep(1)
            st.rerun()