# Google Sheets Bağlantısı Kurulum Rehberi ☁️

Uygulamanızın verilerini Google Sheets'te (Excel) saklayabilmesi için Google'dan ücretsiz bir "Servis Anahtarı" almanız gerekiyor. Bu işlem 5-10 dakika sürer ve tamamen ücretsizdir.

## 1. Google Cloud Projesi Oluşturma
1.  [Google Cloud Console](https://console.cloud.google.com/) adresine gidin.
2.  Google hesabınızla giriş yapın.
3.  Sol üstteki proje seçme menüsüne tıklayın ve **"New Project"** (Yeni Proje) deyin.
4.  Proje adına `TargetLock-Finance` gibi bir isim verin ve **"Create"** butonuna basın.
5.  Bildirimlerden projenin oluşturulmasını bekleyin ve **"Select Project"** diyerek projeyi seçin.

## 2. Gerekli API'leri Açma
Uygulamanın hem Drive'a hem de Sheets'e erişmesi lazım.
1.  Sol menüden **"APIs & Services" > "Library"** kısmına gidin.
2.  Arama kutusuna `Google Sheets API` yazın. Çıkan sonuca tıklayıp **"Enable"** (Etkinleştir) deyin.
3.  Geri dönüp tekrar Library'e gelin.
4.  Bu sefer `Google Drive API` yazın. Çıkan sonuca tıklayıp **"Enable"** deyin.

## 3. Servis Hesabı (Robot) Oluşturma
1.  Sol menüden **"APIs & Services" > "Credentials"** (Kimlik Bilgileri) kısmına gidin.
2.  Üstteki **"+ CREATE CREDENTIALS"** butonuna basıp **"Service Account"** seçeneğini seçin.
3.  **Service account name:** `finance-bot` gibi bir isim verin.
4.  **"Create and Continue"** deyin.
5.  **Role:** `Editor` (veya `Basic > Editor`) seçin. (Bu çok önemli, yoksa yazamaz).
6.  **"Done"** diyerek bitirin.

## 4. Anahtarı (JSON) İndirme
1.  Oluşturduğunuz `finance-bot` hesabının üzerine tıklayın (Credentials sayfasında altta listelenir).
2.  Üstteki sekmelerden **"KEYS"** sekmesine gelin.
3.  **"ADD KEY" > "Create new key"** butonuna basın.
4.  **JSON** seçili olsun. **"CREATE"** butonuna basın.
5.  Bilgisayarınıza bir dosya inecek (Örn: `targetlock-finance-12345.json`).
    *   ⚠️ **BU DOSYAYI SAKLAYIN VE KİMSEYLE PAYLAŞMAYIN.** Bu dosya kasanızın anahtarıdır.

## 5. Google Sheet Oluşturma ve Paylaşma
1.  [Google Sheets](https://docs.google.com/spreadsheets/) adresine gidin ve **"Boş"** (Blank) bir tablo oluşturun.
2.  Tablonun adını `TargetLock_DB` yapın.
3.  İndirdiğiniz JSON dosyasını not defteriyle açın. İçinde `client_email` yazan yeri bulun (Örn: `finance-bot@targetlock-finance.iam.gserviceaccount.com`). Bu mail adresini kopyalayın.
4.  Google Sheet'te sağ üstteki **"Paylaş"** (Share) butonuna basın.
5.  Kopyaladığınız mail adresini yapıştırın, yetkinin **"Düzenleyen"** (Editor) olduğundan emin olun ve **"Gönder"** deyin.

🎉 **Tebrikler!** Artık Google tarafı hazır.
Şimdi o indirdiğiniz JSON dosyasının içeriğini bana (veya Streamlit Secrets kısmına) vermeniz gerekecek.
