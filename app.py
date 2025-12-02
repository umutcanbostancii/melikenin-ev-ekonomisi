import streamlit as st
import pandas as pd
import datetime
import time
import yfinance as yf
import plotly.express as px
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import google.generativeai as genai

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Melike'nin Ev Ekonomisi", page_icon="🏠", layout="wide")

# --- THEME CONFIG ---
with st.sidebar:
    st.title("Melike'nin Ev Ekonomisi 🏠")
    dark_mode = st.toggle("🌙 Dark Mode", value=False)

# --- CSS: DYNAMIC THEME ---
if dark_mode:
    # Dark Mode Palette
    bg_color = "#0e1117"
    text_color = "#f1f5f9"
    card_bg = "#1e293b"
    card_border = "#334155"
    metric_label = "#94a3b8"
    metric_value = "#f8fafc"
    sidebar_bg = "#1e293b"
    input_bg = "#262730"
    input_text = "#f1f5f9"
else:
    # Light Mode Palette
    bg_color = "#f0f2f5"
    text_color = "#1e293b"
    card_bg = "white"
    card_border = "#eef0f2"
    metric_label = "#64748b"
    metric_value = "#1e293b"
    sidebar_bg = "#1e293b"
    input_bg = "white"
    input_text = "#1e293b"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    /* Genel Stil */
    .stApp {{
        background-color: {bg_color};
        color: {text_color};
        font-family: 'Inter', sans-serif;
    }}
    
    /* Headers & Text Visibility Fix (Global) */
    h1, h2, h3, h4, h5, h6, p, span, label, li {{
        color: {text_color} !important;
    }}
    
    /* Dropdown & Input Fixes */
    div[data-baseweb="select"] > div {{
        background-color: {card_bg} !important;
        color: {text_color} !important;
        border-color: {card_border} !important;
    }}
    div[data-baseweb="menu"] {{
        background-color: {card_bg} !important;
    }}
    div[data-baseweb="menu"] div {{
        color: {text_color} !important;
    }}
    div[data-baseweb="popover"] {{
        background-color: {card_bg} !important;
    }}
    input {{
        color: {text_color} !important;
    }}
    div[data-baseweb="input"] > div {{
        background-color: {card_bg} !important;
        color: {text_color} !important;
    }}
    
    /* Native Metric Fix */
    [data-testid="stMetricValue"] {{
        color: {text_color} !important;
    }}
    [data-testid="stMetricLabel"] {{
        color: {text_color} !important;
    }}
    
    /* Kart Tasarımı */
    .metric-card {{
        background-color: {card_bg};
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        border: 1px solid {card_border};
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}
    .metric-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    }}
    
    .metric-label {{
        font-size: 0.9rem;
        color: {metric_label};
        font-weight: 600;
        margin-bottom: 5px;
    }}
    
    .metric-value {{
        font-size: 1.8rem;
        color: {metric_value};
        font-weight: 700;
    }}
    
    .metric-delta {{
        font-size: 0.85rem;
        margin-top: 5px;
        font-weight: 500;
    }}
    .delta-pos {{ color: #10b981; }}
    .delta-neg {{ color: #ef4444; }}
    
    /* Eminevim Grid */
    .installment-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(45px, 1fr));
        gap: 8px;
        margin-top: 20px;
    }}
    .installment-box {{
        height: 45px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 10px;
        font-weight: bold;
        font-size: 14px;
        color: white;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }}
    .paid {{ 
        background: linear-gradient(135deg, #10b981 0%, #059669 100%); 
    }}
    .unpaid {{ 
        background-color: #e2e8f0; 
        color: #94a3b8; 
    }}
    
    /* Sidebar (Always Dark) */
    section[data-testid="stSidebar"] {{
        background-color: {sidebar_bg};
    }}
    /* Gizleme */
    #MainMenu {{visibility: visible;}}
    footer {{visibility: hidden;}}
    header {{visibility: visible;}}
    
    /* Sidebar Metin ve Başlıklar (Always White) */
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] .stMarkdown, 
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] div {{
        color: #f8fafc !important;
    }}
    
    /* Sidebar İkonlar (SVG) */
    section[data-testid="stSidebar"] svg {{
        fill: #f8fafc !important;
        color: #f8fafc !important;
    }}

    /* Sidebar Button (Verileri Yenile) */
    section[data-testid="stSidebar"] button {{
        background-color: #334155 !important;
        color: #f8fafc !important;
        border: 1px solid #475569 !important;
        transition: all 0.2s ease;
    }}
    section[data-testid="stSidebar"] button:hover {{
        background-color: #475569 !important;
        color: white !important;
        border-color: #94a3b8 !important;
    }}
    
    /* Expander (Diğer Altınlar) */
    section[data-testid="stSidebar"] .streamlit-expanderHeader {{
        color: #f8fafc !important;
        background-color: #334155 !important;
        border-radius: 4px;
    }}
    section[data-testid="stSidebar"] .streamlit-expanderContent {{
        color: #f8fafc !important;
        background-color: #1e293b !important;
        border: 1px solid #334155;
    }}
    /* Expander Hover Fix */
    section[data-testid="stSidebar"] .streamlit-expanderHeader:hover {{
        background-color: #475569 !important;
        color: white !important;
    }}
    
    /* Input alanlarının içindeki metni düzelt */
    section[data-testid="stSidebar"] input, 
    section[data-testid="stSidebar"] textarea, 
    section[data-testid="stSidebar"] select {{
        color: #1e293b !important;
    }}
    
    /* Araba Resimleri */
    .car-container {{
        width: 100%;
        height: 260px;
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 10px;
        position: relative;
    }}
    .car-img {{
        width: 100%;
        height: 100%;
        object-fit: cover;
    }}
    .car-img-zoom {{
        transform: scale(1.2);
        transform-origin: center;
    }}
</style>
""", unsafe_allow_html=True)

# --- GOOGLE SHEETS BAĞLANTISI ---
@st.cache_resource
def init_connection():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
    client = gspread.authorize(creds)
    return client

@st.cache_resource
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

    # Accounts Tab (New)
    try:
        ws_acc = sheet.worksheet("accounts")
    except:
        ws_acc = sheet.add_worksheet(title="accounts", rows="100", cols="7")
        ws_acc.append_row(["id", "owner", "name", "type", "bank_name", "currency", "initial_balance"])
        # Default Accounts
        defaults = [
            [1, "Umutcan", "Nakit Cüzdan", "Nakit", "", "TL", 0],
            [2, "Melike", "Nakit Cüzdan", "Nakit", "", "TL", 0],
            [3, "Ortak", "Ev Kasası", "Nakit", "", "TL", 0],
            [4, "Umutcan", "Maaş Hesabı", "Banka", "QNB", "TL", 0],
            [5, "Melike", "Maaş Hesabı", "Banka", "İş Bankası", "TL", 0]
        ]
        for row in defaults:
            ws_acc.append_row(row)

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
        headers = ws.row_values(1)
        try:
            col_idx = headers.index(col_name) + 1
            ws.update_cell(cell.row, col_idx, new_val)
            clear_cache()
        except ValueError:
            pass

def update_row(worksheet_name, filter_col, filter_val, updates_dict):
    """
    Updates a row where filter_col == filter_val with values in updates_dict.
    updates_dict: { 'col_name': new_value }
    """
    sheet = get_sheet()
    ws = sheet.worksheet(worksheet_name)
    
    # 1. Find the row
    # We need to find the column index for filter_col first
    headers = ws.row_values(1)
    try:
        filter_col_idx = headers.index(filter_col) + 1
    except ValueError:
        return False # Filter column not found
        
    cell = ws.find(str(filter_val), in_column=filter_col_idx)
    
    if cell:
        # 2. Update columns
        for col_key, new_val in updates_dict.items():
            try:
                target_col_idx = headers.index(col_key) + 1
                ws.update_cell(cell.row, target_col_idx, new_val)
            except ValueError:
                continue # Target column not found
        clear_cache()
        return True
    return False


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

def add_account(owner, name, type, bank_name, currency, initial_balance):
    next_id = get_next_id("accounts")
    add_row("accounts", [next_id, owner, name, type, bank_name, currency, initial_balance])

def get_accounts():
    df = get_data("accounts")
    if df.empty: return []
    return df.to_dict('records')

def update_account_balance(account_name, target_balance):
    """
    Updates the initial_balance of an account such that the CURRENT balance becomes target_balance.
    New Initial = Target - (Current - Old Initial)
    """
    # 1. Get Current State
    balances, _, _, _, _, _, accounts = get_financial_summary()
    
    # 2. Find the account
    acc = next((a for a in accounts if a['name'] == account_name), None)
    if not acc:
        return False, f"Hesap bulunamadı: {account_name}"
        
    current_bal = balances.get(account_name, 0)
    old_initial = float(acc['initial_balance'])
    
    # 3. Calculate necessary initial balance
    # Current = Initial + Delta  => Delta = Current - Initial
    # Target = New_Initial + Delta
    # New_Initial = Target - Delta = Target - (Current - Initial)
    
    delta = current_bal - old_initial
    new_initial = target_balance - delta
    
    # 4. Update DB
    update_row("accounts", "name", account_name, {"initial_balance": new_initial})
    return True, f"{account_name} bakiyesi {target_balance} TL olarak güncellendi."

def modify_account_balance(account_name, amount, operation="add"):
    """
    Directly modifies the account balance by adding or subtracting an amount.
    This updates the 'initial_balance' in the database.
    Returns: (Success, Old Balance, New Balance)
    """
    accounts = get_accounts()
    acc = next((a for a in accounts if a['name'] == account_name), None)
    
    if not acc:
        return False, 0, 0
        
    old_initial = float(acc['initial_balance'])
    
    if operation == "add":
        new_initial = old_initial + amount
    elif operation == "subtract":
        new_initial = old_initial - amount
    else:
        return False, 0, 0
        
    update_row("accounts", "name", account_name, {"initial_balance": new_initial})
    return True, old_initial, new_initial

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
    accounts = get_accounts()
    
    # --- 1. Calculate Balances from Accounts (Source of Truth) ---
    # We now trust the 'accounts' table for current balances.
    # The 'initial_balance' in accounts table is actually treated as 'current_balance' 
    # by the update_account_balance logic.
    
    balances = {
        "Umutcan Kasa": 0, 
        "Melike Kasa": 0, 
        "Ortak Kasa": 0, 
        "Kredi Kartı Borcu": 0
    }
    
    # Aggregation Logic
    for acc in accounts:
        owner = acc['owner']
        name = acc['name']
        bal = float(acc['initial_balance'])
        
        # Map specific accounts to summary keys
        if owner == "Umutcan":
            balances["Umutcan Kasa"] += bal
        elif owner == "Melike":
            balances["Melike Kasa"] += bal
        elif owner == "Ortak":
            balances["Ortak Kasa"] += bal
            
    # Credit Card Debt is still separate in settings for now, or should be an account?
    # For now, let's keep reading it from settings as legacy, unless we migrate it to an account.
    df_set = get_data("settings")
    sets = dict(zip(df_set['key'], df_set['value']))
    balances["Kredi Kartı Borcu"] = float(sets.get('start_debt_cc', 0))
    
    # Adjust CC debt based on transactions (Legacy logic, maybe keep?)
    # If we want "Current Debt", we should probably just use the setting if AI updates it directly.
    # But if AI adds "Expense" -> "Credit Card", debt should increase.
    # Let's keep the CC logic for now as it's not fully migrated to 'accounts' table yet.
    
    if not df.empty:
        # Ensure numeric columns
        cols = ['amount', 'gold_gram', 'gold_price']
        for c in cols:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)

        # CC Logic
        expenses = df[df['type'] == 'Gider'].groupby('source')['amount'].sum().to_dict()
        paid_cc = df[(df['type'] == 'Gider') & (df['category'] == 'Kredi Kartı Ödeme')]['amount'].sum()
        
        cc_expense = expenses.get("Kredi Kartı", 0)
        balances["Kredi Kartı Borcu"] += cc_expense
        balances["Kredi Kartı Borcu"] -= paid_cc

    # --- 2. Calculate Totals ---
    total_home_safe = balances["Umutcan Kasa"] + balances["Melike Kasa"] + balances["Ortak Kasa"]
    
    # --- 3. Gold & Other Stats ---
    total_pure_gold = 0
    total_gold_cost = 0
    gold_inventory = {}
    total_expense_all_time = 0
    
    if not df.empty:
        total_expense_all_time = df[df['type'] == 'Gider']['amount'].sum()
        
        gold_df = df[df['type'] == 'Altın Alım']
        total_gold_cost = gold_df['amount'].sum()
        
        if not gold_df.empty:
            g_grouped = gold_df.groupby('gold_type')['gold_gram'].sum()
            for g_type, count in g_grouped.items():
                multiplier = GOLD_TYPES.get(g_type, 1.0)
                pure_equivalent = count * multiplier
                total_pure_gold += pure_equivalent
                gold_inventory[g_type] = count

    return balances, total_pure_gold, total_gold_cost, total_home_safe, gold_inventory, total_expense_all_time, accounts

# --- AI HELPER ---
def get_monthly_summary():
    df = get_data("transactions")
    if df.empty: return "Veri yok"
    
    df['date'] = pd.to_datetime(df['date'])
    # Son 12 ayın özeti
    monthly = df.groupby([pd.Grouper(key='date', freq='M'), 'type'])['amount'].sum().reset_index()
    monthly['date'] = monthly['date'].dt.strftime('%Y-%m')
    return monthly.to_string(index=False)

def get_gemini_advice(summary_text):
    if "gemini_api_key" not in st.secrets:
        return "⚠️ API Anahtarı bulunamadı. Lütfen secrets.toml dosyasını kontrol edin."
    
    try:
        genai.configure(api_key=st.secrets["gemini_api_key"])
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(summary_text)
        return response.text
    except Exception as e:
        return f"❌ Bir hata oluştu: {str(e)}"

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
if 'db_initialized' not in st.session_state:
    init_db()
    st.session_state.db_initialized = True

# Piyasa Verilerini Çek
market_data = get_market_data()

if 'gold_manual_mode' not in st.session_state: st.session_state.gold_manual_mode = False
if 'manual_gold_price' not in st.session_state: st.session_state.manual_gold_price = 5700.0 

with st.sidebar:
    # st.title("Melike'nin Ev Ekonomisi 🏠") # Moved to top
    if st.button("🔄 Verileri Yenile"):
        clear_cache()
        st.rerun()
    page = st.radio("Menü", ["Ana Sayfa 📊", "Raporlar 📈", "Gider Planla 📅", "İşlem Ekle ➕", "Geçmiş & Düzenle 📝", "Eminevim 🏠", "Ayarlar 🛠️", "AI Asistan 🤖"])
    
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
    
    balances, total_pure_gold, total_gold_cost, total_home_safe, gold_inv, total_expense, accounts = get_financial_summary()
    
    usd_rate = market_data['usd'] if market_data else sets['usd_rate']
    eur_rate = market_data['eur'] if market_data else sets['eur_rate']
    
    target = sets['target_amount']
    current_gold_value = total_pure_gold * (market_data['gold'] if market_data else st.session_state.manual_gold_price)
    
    # --- ASSET SUMMARY ON DASHBOARD (NEW) ---
    st.markdown("### 💼 Varlık Özeti")
    
    # Simple aggregated view for dashboard
    c1, c2, c3 = st.columns(3)
    
    # Umutcan Total
    u_total = sum([float(a['initial_balance']) for a in accounts if a['owner'] == 'Umutcan'])
    c1.metric("👨🏻‍💻 Umutcan", f"{u_total:,.0f} TL")
    
    # Melike Total
    m_total = sum([float(a['initial_balance']) for a in accounts if a['owner'] == 'Melike'])
    c2.metric("👩🏻‍💼 Melike", f"{m_total:,.0f} TL")
    
    # Common Total
    o_total = sum([float(a['initial_balance']) for a in accounts if a['owner'] == 'Ortak'])
    c3.metric("🤝 Ortak", f"{o_total:,.0f} TL")
    
    st.markdown("---")
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


        
# --- SAYFA: VARLIKLAR (YENİ) ---
elif page == "Varlıklar 💼":
    st.markdown("## 💼 Varlık Yönetimi")
    
    # Get Data
    balances, total_pure_gold, total_gold_cost, total_home_safe, gold_inv, total_expense, accounts = get_financial_summary()
    
    # Calculate Net Worth
    current_gold_value = total_pure_gold * (market_data['gold'] if market_data else st.session_state.manual_gold_price)
    net_worth = total_home_safe + current_gold_value - balances["Kredi Kartı Borcu"]
    
    # Top Summary
    m1, m2, m3 = st.columns(3)
    metric_card(m1, "Toplam Net Varlık", f"{net_worth:,.0f} TL", "Nakit + Altın - Borç")
    metric_card(m2, "Toplam Nakit", f"{total_home_safe:,.0f} TL", "Bankalar + Cüzdan")
    metric_card(m3, "Altın Değeri", f"{current_gold_value:,.0f} TL", f"{total_pure_gold:.2f} Gram Has")
    
    st.markdown("---")
    
    # Tabs for Owners
    tab_umut, tab_melike, tab_common = st.tabs(["👨🏻‍💻 Umutcan", "👩🏻‍💼 Melike", "🤝 Ortak"])
    
    def render_account_card(acc):
        # Bank Logo Mapping (Simple Text/Icon for now, can be image later)
        bank_logos = {
            "QNB": "🏦", "Garanti": "🍀", "İş Bankası": "💲", "Yapı Kredi": "🐏", "Akbank": "🔴"
        }
        icon = bank_logos.get(acc['bank_name'], "💵") if acc['type'] == 'Banka' else "👛"
        
        # Calculate current balance (This needs real tx calculation later)
        # For now showing initial + dummy logic or just initial
        # In full implementation, we filter transactions by account_id
        
        # Placeholder balance logic for demo
        balance = float(acc['initial_balance']) 
        
        st.markdown(f"""
        <div class="metric-card" style="margin-bottom: 10px;">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="font-size: 2rem;">{icon}</div>
                    <div>
                        <div style="font-weight: bold; color: #f8fafc;">{acc['name']}</div>
                        <div style="font-size: 0.8rem; color: #94a3b8;">{acc['bank_name'] if acc['bank_name'] else 'Nakit'}</div>
                    </div>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 1.2rem; font-weight: bold; color: #f8fafc;">{balance:,.0f} {acc['currency']}</div>
                    <div style="font-size: 0.8rem; color: #10b981;">Aktif</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with tab_umut:
        st.subheader("Umutcan'ın Varlıkları")
        my_accs = [a for a in accounts if a['owner'] == 'Umutcan']
        for acc in my_accs:
            render_account_card(acc)
            
    with tab_melike:
        st.subheader("Melike'nin Varlıkları")
        her_accs = [a for a in accounts if a['owner'] == 'Melike']
        for acc in her_accs:
            render_account_card(acc)
            
    with tab_common:
        st.subheader("Ortak Varlıklar")
        common_accs = [a for a in accounts if a['owner'] == 'Ortak']
        for acc in common_accs:
            render_account_card(acc)
            
        st.subheader("🥇 Altınlar")
        if gold_inv:
            for g_type, count in gold_inv.items():
                st.markdown(f"""
                <div class="metric-card" style="margin-bottom: 10px; border-left: 5px solid #eab308;">
                    <div style="display: flex; justify-content: space-between;">
                        <span><b>{g_type}</b></span>
                        <span>{count} Adet</span>
                    </div>
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
        
        # Dynamic Account List
        acc_list = [a['name'] for a in get_accounts()]
        if "Kredi Kartı" not in acc_list: acc_list.append("Kredi Kartı")
        
        src = c2.selectbox("Kaynak", acc_list, key="g_src")
        desc = c2.text_input("Açıklama", key="g_desc")
        
        if st.button("Gideri Kaydet", key="btn_gider"):
            final_cat = cat_select
            
            if cat_select == "➕ Yeni Kategori Ekle..." and new_cat_name:
                add_category(new_cat_name, "Gider", 1 if is_inst else 0, inst_total, inst_months)
                final_cat = new_cat_name
                st.success(f"Yeni kategori '{new_cat_name}' oluşturuldu.")
            
            add_transaction(datetime.date.today(), 'Gider', final_cat, amt, src, desc, 1, installment_number=current_inst_no)
            
            # Update Balance
            success, old_bal, new_bal = modify_account_balance(src, amt, "subtract")
            
            if success:
                st.markdown(f"""
                <div style="background-color: #fef2f2; border: 1px solid #ef4444; padding: 15px; border-radius: 10px; margin-top: 10px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="color: #991b1b; font-weight: bold;">💸 İşlem Başarılı!</span>
                        <span style="font-size: 0.8em; color: #7f1d1d;">Önceki: {old_bal:,.0f} TL</span>
                    </div>
                    <div style="font-size: 1.5em; font-weight: bold; color: #dc2626;">-{amt:,.0f} TL</div>
                    <div style="font-size: 1.1em; color: #1e293b; margin-top: 5px;">Yeni Bakiye: <b>{new_bal:,.0f} TL</b> ({src})</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.success("İşlem Kaydedildi (Bakiye güncellenemedi - Kredi Kartı olabilir).")
                
            time.sleep(3)
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
        
        # Dynamic Account List
        acc_list = [a['name'] for a in get_accounts()]
        src = c2.selectbox("Kasa", acc_list, key="i_src")
        desc = st.text_input("Açıklama", key="i_desc")
        
        if st.button("Geliri Kaydet", key="btn_gelir"):
            final_cat = cat_select
            if cat_select == "➕ Yeni Kategori Ekle..." and new_cat_name:
                add_category(new_cat_name, "Gelir")
                final_cat = new_cat_name
            
            add_transaction(datetime.date.today(), 'Gelir', final_cat, amt, src, desc, 1)
            
            # Update Balance
            success, old_bal, new_bal = modify_account_balance(src, amt, "add")
            
            if success:
                st.markdown(f"""
                <div style="background-color: #f0fdf4; border: 1px solid #22c55e; padding: 15px; border-radius: 10px; margin-top: 10px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="color: #14532d; font-weight: bold;">💰 Gelir Eklendi!</span>
                        <span style="font-size: 0.8em; color: #14532d;">Önceki: {old_bal:,.0f} TL</span>
                    </div>
                    <div style="font-size: 1.5em; font-weight: bold; color: #16a34a;">+{amt:,.0f} TL</div>
                    <div style="font-size: 1.1em; color: #1e293b; margin-top: 5px;">Yeni Bakiye: <b>{new_bal:,.0f} TL</b> ({src})</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.success("Kaydedildi.")
                
            time.sleep(3)
            st.rerun()
            
    with t3:
        c1, c2 = st.columns(2)
        g_type = c1.selectbox("Altın Tipi", list(GOLD_TYPES.keys()), key="gold_type")
        count = c2.number_input("Adet / Gram", min_value=0.0, step=0.5, key="gold_count")
        tl = c1.number_input("Toplam Ödenen TL", step=100.0, key="gold_tl")
        
        # Dynamic Account List
        acc_list = [a['name'] for a in get_accounts()]
        if "Kredi Kartı" not in acc_list: acc_list.append("Kredi Kartı")
        
        src = c2.selectbox("Ödeme Kaynağı", acc_list, key="gold_src")
        
        if st.button("Altın Alımını Kaydet", key="btn_gold"):
            add_transaction(datetime.date.today(), 'Altın Alım', 'Yatırım', tl, src, 'Altın', 1, gold_gram=count, gold_price=tl/count if count>0 else 0, gold_type=g_type)
            
            # Update Balance (Expense)
            success, old_bal, new_bal = modify_account_balance(src, tl, "subtract")
            
            if success:
                st.markdown(f"""
                <div style="background-color: #fffbeb; border: 1px solid #f59e0b; padding: 15px; border-radius: 10px; margin-top: 10px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="color: #78350f; font-weight: bold;">🥇 Altın Alındı!</span>
                        <span style="font-size: 0.8em; color: #78350f;">Önceki: {old_bal:,.0f} TL</span>
                    </div>
                    <div style="font-size: 1.5em; font-weight: bold; color: #d97706;">-{tl:,.0f} TL</div>
                    <div style="font-size: 1.1em; color: #1e293b; margin-top: 5px;">Yeni Bakiye: <b>{new_bal:,.0f} TL</b> ({src})</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.success("Portföye Eklendi.")
                
            time.sleep(3)
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
            # Headers
            h1, h2, h3, h4, h5, h6 = st.columns([2, 2, 2, 2, 4, 2])
            h1.markdown("**📅 Tarih**")
            h2.markdown("**📌 Tür**")
            h3.markdown("**💰 Tutar**")
            h4.markdown("**👤 Kaynak**")
            h5.markdown("**📝 Açıklama**")
            h6.markdown("**⚙️ İşlem**")
            st.markdown("---")

            for idx, tx in df.iterrows():
                with st.container():
                    c1, c2, c3, c4, c5, c6 = st.columns([2, 2, 2, 2, 4, 2])
                    c1.write(f"{tx['date']}")
                    
                    type_lbl = tx['type']
                    if tx['type'] == "Altın Alım": type_lbl = f"{tx['gold_type']} ({tx['gold_gram']})"
                    
                    c2.write(type_lbl)
                    c3.write(f"{tx['amount']:,.0f} TL")
                    c4.write(f"{tx['source']}")
                    c5.write(f"**{tx['category']}** - {tx['description']}")
                    
                    b1, b2 = c6.columns(2)
                    if b1.button("✏️", key=f"edit_{tx['id']}"):
                        st.session_state.edit_id = tx['id']
                        st.rerun()
                    if b2.button("🗑️", key=f"del_{tx['id']}"):
                        delete_row_by_id("transactions", tx['id'])
                        st.rerun()
                    st.markdown("<hr style='margin: 5px 0;'>", unsafe_allow_html=True)

# --- SAYFA: EMİNEVİM ---
elif page == "Eminevim 🏠":
    st.markdown("## 🚗 Araba Hedefi & Eminevim")
    
    img_col1, img_col2, img_col3 = st.columns(3)
    with img_col1:
        st.markdown('<div class="car-container"><img src="https://www.arabahabercisi.com/wp-content/uploads/2022/10/2022-VW-Golf-Fiyatlar%C4%B1-Ekim-600x381.jpg" class="car-img car-img-zoom"></div>', unsafe_allow_html=True)
    with img_col2:
        st.markdown('<div class="car-container"><img src="https://arabavs.com/images/car_images/2_2_a4223_19.jpg" class="car-img car-img-zoom"></div>', unsafe_allow_html=True)
    with img_col3:
        st.markdown('<div class="car-container"><img src="https://arabavs.com/images/car_images/2_2_e3c2a_0.jpg" class="car-img car-img-zoom"></div>', unsafe_allow_html=True)
    
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

        st.subheader("💰 Açılış Bakiyeleri (Nakit/Kart)")
        st.caption("Sisteme başlarken elinizde olan nakit veya mevcut kart borcunuzu buraya girin.")
        
        b1, b2 = st.columns(2)
        init_umutcan = b1.number_input("Umutcan Kasa (Başlangıç)", value=float(sets.get('start_balance_umutcan', 0)))
        init_melike = b2.number_input("Melike Kasa (Başlangıç)", value=float(sets.get('start_balance_melike', 0)))
        
        b3, b4 = st.columns(2)
        init_common = b3.number_input("Ortak Kasa (Başlangıç)", value=float(sets.get('start_balance_common', 0)))
        init_cc_debt = b4.number_input("Kredi Kartı Mevcut Borç", value=float(sets.get('start_debt_cc', 0)))

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
            
            update_settings('start_balance_umutcan', init_umutcan)
            update_settings('start_balance_melike', init_melike)
            update_settings('start_balance_common', init_common)
            update_settings('start_debt_cc', init_cc_debt)
            
            update_settings('salary_umutcan', su)
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

# --- SAYFA: AI ASISTAN ---
# --- SAYFA: AI ASISTAN ---
elif page == "AI Asistan 🤖":
    st.markdown("## 🤖 AI Finansal Asistan")
    st.info("Gemini AI, finansal verilerinizi analiz ederek size tasarruf ve bütçe tavsiyeleri verir.")

    # Session State Başlatma
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "pending_txs" not in st.session_state:
        st.session_state.pending_txs = []

    # Mesaj Geçmişini Göster
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Analiz Butonu (Sadece hiç mesaj yoksa veya kullanıcı isterse)
    if st.button("✨ Detaylı Analiz Başlat", type="primary"):
        with st.spinner("Veriler analiz ediliyor ve Gemini'ye soruluyor..."):
            # Verileri Hazırla
            balances, total_pure_gold, total_gold_cost, total_home_safe, gold_inv, total_expense, accounts = get_financial_summary()
            df_tx = get_data("transactions")
            
            # Son 30 günlük harcamalar
            if not df_tx.empty:
                df_tx['date'] = pd.to_datetime(df_tx['date'])
                last_30_days = df_tx[df_tx['date'] > (pd.Timestamp.now() - pd.Timedelta(days=30))]
                top_expenses = last_30_days[last_30_days['type'] == 'Gider'].groupby('category')['amount'].sum().sort_values(ascending=False).head(5)
                top_expenses_str = top_expenses.to_string()
            else:
                top_expenses_str = "Veri yok"

            # Altın Değeri
            gold_val = total_pure_gold * (market_data['gold'] if market_data else st.session_state.manual_gold_price)
            
            summary_text = f"""
            Sen uzman bir finansal danışmansın. Aşağıdaki verilere göre bana Türkçe olarak, samimi bir dille finansal durumumu yorumla ve tasarruf tavsiyeleri ver.
            
            **Genel Durum:**
            - Toplam Nakit Varlık: {total_home_safe:,.0f} TL
            - Toplam Altın Değeri: {gold_val:,.0f} TL
            - Kredi Kartı Borcu: {balances['Kredi Kartı Borcu']:,.0f} TL
            - Toplam Net Varlık: {total_home_safe + gold_val - balances['Kredi Kartı Borcu']:,.0f} TL
            
            **Son 30 Günün En Yüksek Harcamaları:**
            {top_expenses_str}
            
            Lütfen şunlara odaklan:
            1. Harcama alışkanlıklarım nasıl?
            2. Nereden tasarruf edebilirim?
            3. Altın yatırımı stratejim mantıklı mı?
            4. Kredi kartı borcum riskli seviyede mi?
            
            Cevabı maddeler halinde, emojiler kullanarak ve motive edici bir tonda ver.
            """
            
            advice = get_gemini_advice(summary_text)
            
            # Mesajı Ekle ve Göster
            st.session_state.messages.append({"role": "assistant", "content": advice})
            st.rerun()

    # Kullanıcıdan Soru Al
    if prompt := st.chat_input("Finansal bir soru sor veya işlem ekle (Örn: Migros 500 TL)..."):
        # Kullanıcı mesajını ekle
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # AI Cevabı
        with st.chat_message("assistant"):
            with st.spinner("Düşünüyor..."):
                import json
                
                balances, total_pure_gold, total_gold_cost, total_home_safe, gold_inv, total_expense, accounts = get_financial_summary()
                gold_val = total_pure_gold * (market_data['gold'] if market_data else st.session_state.manual_gold_price)
                
                # Mevcut Kategoriler
                cats_gider = get_categories("Gider")
                cats_gelir = get_categories("Gelir")
                all_cats = cats_gider + cats_gelir
                
                # Son işlemleri çek
                df_tx = get_data("transactions")
                recent_tx_str = "Henüz işlem yok."
                if not df_tx.empty:
                    df_tx['date'] = pd.to_datetime(df_tx['date'])
                    last_txs = df_tx.sort_values(by='date', ascending=False).head(10)
                    recent_tx_str = last_txs[['date', 'type', 'category', 'amount', 'description']].to_string(index=False)

                # Aylık Özet (Tahmin ve Anormallik için)
                monthly_summary = get_monthly_summary()
                
                # Hesap Listesi ve Bakiyeler
                acc_details = []
                for a in accounts:
                    bal = balances.get(a['name'], 0)
                    acc_details.append(f"{a['name']}: {bal:,.0f} {a['currency']}")
                acc_context_str = "\n                ".join(acc_details)

                context = f"""
                Sen akıllı bir finansal asistansın. Kullanıcı sana bir soru sorabilir, işlem eklemek/silmek isteyebilir, grafik isteyebilir veya hesap bakiyelerini güncelleyebilir.
                
                **Mevcut Kategoriler:** {', '.join(all_cats)}
                
                **Mevcut Hesaplar ve Bakiyeler:**
                {acc_context_str}
                
                **Kredi Kartı:** "Kredi Kartı" da bir kaynaktır. Borç: {balances.get('Kredi Kartı Borcu', 0):,.0f} TL
                
                **Kullanıcı Girdisi:** {prompt}
                
                1. EĞER kullanıcı bir işlem EKLEMEK istiyorsa (Harcama, Gelir, Transfer):
                   - Harcama: type="Gider"
                   - Gelir: type="Gelir"
                   - Transfer (Örn: "Hesaptan 200 çektim"): Bunu iki işlem olarak yap:
                     1. Gider (Kaynak: Banka, Kategori: Transfer, Açıklama: Nakite Transfer)
                     2. Gelir (Kaynak: Nakit, Kategori: Transfer, Açıklama: Bankadan Transfer)
                   
                {{
                    "action": "add_transaction",
                    "type": "Gider" veya "Gelir" veya "Altın Alım",
                    "amount": 0.0,
                    "category": "En uygun kategori",
                    "source": "En uygun kaynak (Mevcut Hesaplardan biri)",
                    "description": "Açıklama",
                    "is_new_category": true/false,
                    "gold_gram": 0.0,
                    "gold_type": "Gram 24k"
                }}
                
                2. EĞER kullanıcı BAKİYE GÜNCELLEMEK istiyorsa (Örn: "Şu an cebimde 500 TL var", "Bankada 10.000 TL var"):
                {{
                    "action": "update_balance",
                    "account_name": "Hesap Adı (Tam eşleşmeli)",
                    "amount": 0.0 (Yeni güncel bakiye)
                }}
                
                3. EĞER kullanıcı bir işlem SİLMEK istiyorsa:
                {{
                    "action": "delete_transaction",
                    "query": "Silinecek işlemi tanımlayan kısa metin"
                }}
                
                4. EĞER kullanıcı GRAFİK istiyorsa:
                {{
                    "action": "plot",
                    "plot_type": "line" veya "pie" veya "bar",
                    "category": "Hepsi" veya spesifik kategori,
                    "title": "Grafik Başlığı"
                }}

                5. EĞER kullanıcı SOHBET ediyorsa:
                {{
                    "action": "chat",
                    "response": "Cevabın"
                }}
                
                **ÖNEMLİ:** Birden fazla işlem varsa (örn: "Markete gittim 100 TL, sonra 200 TL çektim"), JSON listesi döndür: [{{...}}, {{...}}]
                """
                
                try:
                    # Configure API Key explicitly here as well, or ensure it's global
                    if "gemini_api_key" in st.secrets:
                        genai.configure(api_key=st.secrets["gemini_api_key"])
                    
                    model = genai.GenerativeModel('gemini-3-pro-preview')
                    response = model.generate_content(context)
                    
                    cleaned_response = response.text.strip()
                    if cleaned_response.startswith("```json"):
                        cleaned_response = cleaned_response[7:-3]
                    
                    data = json.loads(cleaned_response)
                    
                    # Normalize to list
                    actions_list = data if isinstance(data, list) else [data]
                    added_tx_count = 0
                    
                    for action_data in actions_list:
                        action = action_data.get("action")
                        
                        if action == "add_transaction":
                            st.session_state.pending_txs.append(action_data)
                            added_tx_count += 1
                            
                        elif action == "update_balance":
                            acc_name = action_data.get("account_name")
                            tgt_bal = action_data.get("amount")
                            success, msg = update_account_balance(acc_name, tgt_bal)
                            if success:
                                st.session_state.messages.append({"role": "assistant", "content": f"✅ {msg}"})
                            else:
                                st.session_state.messages.append({"role": "assistant", "content": f"❌ {msg}"})
                            
                        elif action == "delete_transaction":
                            query = action_data.get("query")
                            # Simple fuzzy match on description or category
                            # This part needs a real search function, for now just listing last 5 to delete?
                            # Or better, just ask user to delete manually from list.
                            # Let's implement a simple "Find and Delete" candidate
                            
                            candidates = df_tx[df_tx['description'].str.contains(query, case=False, na=False) | df_tx['category'].str.contains(query, case=False, na=False)]
                            if not candidates.empty:
                                to_del = candidates.iloc[0]
                                st.session_state.pending_delete = to_del.to_dict()
                                st.session_state.messages.append({"role": "assistant", "content": f"🗑️ Şu işlemi silmek istiyor musun: {to_del['description']} ({to_del['amount']} TL)?"})
                                st.rerun()
                            else:
                                st.session_state.messages.append({"role": "assistant", "content": f"❌ '{query}' ile eşleşen işlem bulunamadı."})

                        elif action == "plot":
                            p_type = action_data.get("plot_type")
                            p_cat = action_data.get("category")
                            p_title = action_data.get("title")
                            
                            st.session_state.messages.append({"role": "assistant", "content": f"📊 {p_title} grafiği hazırlanıyor..."})
                            
                            # Filter Data
                            plot_df = df_tx.copy()
                            if p_cat != "Hepsi":
                                plot_df = plot_df[plot_df['category'] == p_cat]
                                
                            if p_type == "line":
                                fig = px.line(plot_df, x='date', y='amount', title=p_title)
                                st.plotly_chart(fig)
                            elif p_type == "pie":
                                fig = px.pie(plot_df, values='amount', names='category', title=p_title)
                                st.plotly_chart(fig)
                            elif p_type == "bar":
                                fig = px.bar(plot_df, x='category', y='amount', title=p_title)
                                st.plotly_chart(fig)

                        elif action == "chat":
                             st.session_state.messages.append({"role": "assistant", "content": action_data.get("response")})
                        
                        else:
                             # Fallback
                             response_text = action_data.get("response", cleaned_response)
                             st.session_state.messages.append({"role": "assistant", "content": response_text})

                    if added_tx_count > 0:
                        st.session_state.messages.append({"role": "assistant", "content": f"✅ {added_tx_count} işlem hazırlandı. Aşağıdan onaylayabilirsin."})
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"AI Hatası: {e}")
                    st.session_state.messages.append({"role": "assistant", "content": "Üzgünüm, bir hata oluştu."})

    # Bekleyen İşlem Onayı (EKLEME)
    if "pending_txs" in st.session_state and st.session_state.pending_txs:
        with st.chat_message("assistant"):
            st.write("⏳ **Bekleyen İşlemler**")
            
            for i, tx in enumerate(st.session_state.pending_txs):
                with st.expander(f"{i+1}. {tx.get('description', 'İşlem')} ({tx.get('amount')} TL)", expanded=True):
                    st.write(f"**Kategori:** {tx.get('category')} | **Tip:** {tx.get('type')}")
                    c1, c2 = st.columns(2)
                    if c1.button("✅ Onayla", key=f"confirm_{i}"):
                        if tx.get("is_new_category"):
                            add_category(tx['category'], tx['type'])
                        
                        if tx['type'] == 'Altın Alım':
                             add_transaction(datetime.date.today(), 'Altın Alım', 'Yatırım', tx['amount'], tx['source'], 'Altın Alımı', 1, gold_gram=tx.get('gold_gram', 0), gold_price=tx['amount']/tx.get('gold_gram', 1), gold_type=tx.get('gold_type', 'Gram 24k'))
                        else:
                            add_transaction(datetime.date.today(), tx['type'], tx['category'], tx['amount'], tx['source'], tx['description'], 1)
                        
                        st.success("İşlem Başarıyla Kaydedildi! 🎉")
                        st.session_state.messages.append({"role": "assistant", "content": f"✅ İşlem kaydedildi: {tx.get('description')}"})
                        st.session_state.pending_txs.pop(i)
                        st.rerun()
                        
                    if c2.button("❌ İptal", key=f"cancel_{i}"):
                        st.warning("İşlem iptal edildi.")
                        st.session_state.pending_txs.pop(i)
                        st.rerun()

    # Bekleyen İşlem Onayı (SİLME)
    if "pending_delete" in st.session_state and st.session_state.pending_delete:
        with st.chat_message("assistant"):
            st.write("⚠️ Bu işlemi silmek istediğine emin misin?")
            c1, c2 = st.columns(2)
            if c1.button("🗑️ Evet, Sil", type="primary", use_container_width=True):
                delete_row_by_id("transactions", st.session_state.pending_delete)
                st.success("İşlem Silindi.")
                st.session_state.messages.append({"role": "assistant", "content": "✅ İşlem silindi."})
                del st.session_state.pending_delete
                time.sleep(1)
                st.rerun()
                
            if c2.button("❌ Vazgeç", type="secondary", use_container_width=True):
                st.info("Silme işlemi iptal edildi.")
                st.session_state.messages.append({"role": "assistant", "content": "❌ Silme iptal edildi."})
                del st.session_state.pending_delete
                st.rerun()