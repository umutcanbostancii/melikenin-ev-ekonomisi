# 🚀 Melike'nin Ev Ekonomisi - Yayınlama Rehberi

Uygulamanızı internette herkesin (veya sadece sizin) erişebileceği bir linke dönüştürmek için **Streamlit Cloud** kullanacağız. Bu işlem tamamen ücretsizdir.

## Adım 1: GitHub'a Yükleme
Öncelikle kodlarınızı GitHub'a yüklememiz gerekiyor.

1.  **GitHub Hesabı:** [github.com](https://github.com) adresinden giriş yapın (yoksa üye olun).
2.  **Yeni Depo (Repository):**
    *   Sağ üstteki **+** ikonuna basıp **"New repository"** deyin.
    *   Repository name: `ev-ekonomisi` (veya istediğiniz bir isim).
    *   **Public** veya **Private** seçebilirsiniz (Private öneririm, verileriniz görünmez ama kodlarınız da gizli kalsın).
    *   **"Create repository"** butonuna basın.

3.  **Kodları Gönderme (Terminalden):**
    VS Code terminalinde sırasıyla şu komutları yazın (Her satırdan sonra Enter'a basın):

    ```bash
    git init
    git add .
    git commit -m "İlk sürüm"
    git branch -M main
    git remote add origin https://github.com/KULLANICI_ADINIZ/ev-ekonomisi.git
    git push -u origin main
    ```
    *(Not: `https://github.com/...` kısmını, GitHub'da oluşturduğunuz sayfadaki linkle değiştirin. Size kullanıcı adı/şifre sorarsa girin.)*

## Adım 2: Streamlit Cloud Hesabı
1.  [share.streamlit.io](https://share.streamlit.io) adresine gidin.
2.  **"Continue with GitHub"** diyerek giriş yapın.

## Adım 3: Uygulamayı Bağlama
1.  Sağ üstteki **"New app"** butonuna basın.
2.  **"Use existing repo"** seçeneğini seçin.
3.  **Repository:** `ev-ekonomisi` (az önce açtığınız depo).
4.  **Branch:** `main`
5.  **Main file path:** `app.py`
6.  **"Deploy!"** butonuna basın.

## Adım 4: Gizli Anahtarı Tanımlama (Çok Önemli!) 🔑
Uygulama açılmaya çalışacak ama **HATA VERECEK**. Çünkü Google Sheets şifresini henüz bilmiyor.

1.  Streamlit ekranında sağ alttaki **"Manage app"** butonuna basın.
2.  Üstteki üç noktaya (⋮) tıklayıp **"Settings"** deyin.
3.  Sol menüden **"Secrets"** kısmına gelin.
4.  Aşağıdaki kutuya, bilgisayarınızdaki `.streamlit/secrets.toml` dosyasının içeriğini (JSON bilgileriyle birlikte) yapıştırın.
    *   *Format şöyle olmalı:*
    ```toml
    [gcp_service_account]
    type = "service_account"
    project_id = "..."
    ...
    ```
5.  **"Save"** deyin.

## 🏁 Sonuç
Uygulamanız otomatik olarak yeniden başlayacak ve artık size özel bir linkiniz olacak! (Örn: `https://ev-ekonomisi.streamlit.app`)
Bu linki telefonunuza gönderip dilediğiniz yerden girebilirsiniz.
