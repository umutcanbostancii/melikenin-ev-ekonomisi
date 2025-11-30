import yfinance as yf

def piyasa_verilerini_getir():
    print("Veriler çekiliyor... Lütfen bekleyin.")
    
    # Tek seferde Dolar, Euro ve Ons Altın verisini çekiyoruz
    # TRY=X  -> Dolar/TL
    # EURTRY=X -> Euro/TL
    # GC=F   -> Ons Altın (Dolar bazlı)
    tickers = yf.download("TRY=X EURTRY=X GC=F", period="5d", progress=False)['Close']
    print(tickers)

    # Son kapanış (güncel) fiyatlarını al (NaN leri temizleyerek)
    dolar_tl = tickers['TRY=X'].dropna().iloc[-1]
    euro_tl = tickers['EURTRY=X'].dropna().iloc[-1]
    ons_dolar = tickers['GC=F'].dropna().iloc[-1]

    # --- KRİTİK HESAP: GRAM ALTIN ---
    # Formül: (Ons Fiyatı * Dolar Kuru) / 31.1035
    gram_altin_tl = (ons_dolar * dolar_tl) / 31.1035

    return {
        "Dolar ($)": round(dolar_tl, 2),
        "Euro (€)": round(euro_tl, 2),
        "Gram Altın (TL)": round(gram_altin_tl, 2),
        "Ons Altın ($)": round(ons_dolar, 2)
    }

# Test edelim
try:
    sonuc = piyasa_verilerini_getir()

    print("-" * 30)
    print(f"💵 Dolar: {sonuc['Dolar ($)']} TL")
    print(f"💶 Euro:  {sonuc['Euro (€)']} TL")
    print(f"🥇 Gram Altın: {sonuc['Gram Altın (TL)']} TL")
    print("-" * 30)
except Exception as e:
    print(f"Hata oluştu: {e}")
