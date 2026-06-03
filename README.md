# 🔬 FIGES MathWorks CV Analyzer — v2.0

> Mühendis ve akademisyenlerin **LinkedIn profillerinden** indirilen CV'lerini analiz ederek en uygun **MATLAB, Simulink ve MathWorks Toolbox**'larını öneren, **tamamen yerel ve çok kullanıcılı** yapay zeka satış asistanı.

---

## 📌 Kullanım Senaryosu ve İş Akışı

Satış mühendisleri müşteri toplantılarından veya aramalarından önce şu adımları izler:

1. **LinkedIn'den Çıktı Alma:** Adayın LinkedIn profiline girilir, `Daha Fazla` ➔ `PDF olarak kaydet` (Save to PDF) seçeneğiyle profil PDF olarak indirilir.
2. **Sisteme Yükleme:** İndirilen PDF dosyası **FIGES CV Analyzer** arayüzüne sürüklenip bırakılır. (İstenirse profil metni kopyala-yapıştır ile de eklenebilir).
3. **Analiz Süreci:** Sistem saniyeler içinde adayın yetkinliklerini tespit eder ve MathWorks ürün ailesine özel satış argümanları üretir.
4. **Toplu Tarama ve E-Posta:** Analiz sonucu hem profesyonel bir **PDF raporu** olarak indirilebilir hem de arayüzden çıkmadan doğrudan istenen e-posta adresine (veya adreslerine) PDF ekli olarak gönderilebilir. 

*Bu çıktılar, müşteri ile toplantı almayı veya toplantı esnasında adayın ilgisini çekecek en doğru ürünü sunmayı hedefler.*

> **Gizlilik:** Veriler hiçbir zaman dışarıya çıkmaz. Model ve uygulama tamamen yerel (NVIDIA Jetson AGX Orin / Windows) çalışır.

---

## 🚀 v2.0 Yeni Özellikler (Çoklu Sayfa Mimarisi)

Bu sürüm ile birlikte uygulama tamamen kurumsal bir araca dönüştürülmüştür:

| Yeni Özellik | Detay |
|---|---|
| 🔐 **Çok Kullanıcılı Sistem** | Her satış mühendisi kendi "kullanıcı adı" ve "şifresi" ile kayıt olup giriş yapar. Oturumlar izole edilir. |
| 🗄️ **SQLite Veritabanı** | Analiz sonuçları artık kaybolmaz. RAM yerine yerel bir `figes_cv.db` dosyasında kalıcı olarak saklanır. |
| 📋 **Tarama Geçmişi** | **Geçmiş** sayfası üzerinden kullanıcının son 10 analizi listelenir. Eski adaylara ait PDF'ler tekrar indirilebilir veya e-posta atılabilir. |
| 👑 **Admin Paneli** | Geliştirici (`dogukan` / `admin123`) özel **Admin** sayfasından tüm kullanıcıları, kaç analiz yaptıklarını, kayıt tarihlerini ve sistemdeki tüm analiz özetlerini görebilir. Kullanıcı şifrelerini sıfırlayabilir veya hesapları silebilir. |
| 🎯 **A/B/C/D Skorlaması** | Yapay zekanın verdiği teknik puanların ortalamasına göre müşteri otomatik olarak potansiyel sınıfına ayrılır (*A: Yüksek, B: Orta, C: Düşük, D: Potansiyel Yok*). |
| 🔁 **Tekrarlı Analiz Uyarısı** | Aynı adayın CV'si daha önce yüklendiyse sistem bunu otomatik fark eder ve kullanıcıyı uyarır. |
| 📧 **Gelişmiş E-Posta** | SMTP üzerinden doğrudan rapor gönderimi. Virgülle ayrılarak birden fazla adrese gönderim yapılabilir. |
| 🇹🇷 **Mükemmel Türkçe PDF** | PDF oluşturulurken Google'ın orijinal `Roboto` fontları otomatik indirilip gömülür. (İ, Ş, Ğ gibi karakterlerin Linux/Jetson üzerinde bozulması engellenir). |

---

## 🌐 Çift Dil & Çift Model Desteği

| | 🇹🇷 Türkçe CV | 🇬🇧 English CV |
|---|---|---|
| **Model** | `qwen2.5:14b` | `phi4` |
| **Boyut** | ~9 GB | ~9 GB |
| **Tahmini Süre** | ~15 sn | ~12 sn |
| **Neden?** | Qwen ailesi Türkçe'de açık ara en iyi | Microsoft Phi-4, JSON & instruction-following şampiyonu |
| **Prompt dili** | Türkçe | English |
| **Çıktı dili** | Türkçe | English |

---

## 🛠️ Teknoloji Yığını

| Katman | Teknoloji |
|---|---|
| **Arayüz** | Streamlit (Multipage / Çoklu Sayfa) |
| **Veritabanı** | SQLite3 (`data/figes_cv.db`) |
| **LLM** | Ollama (`qwen2.5:14b` ve `phi4`) |
| **Bağlantı** | OpenAI SDK uyumlu endpoint (`http://127.0.0.1:11434/v1`) |
| **Şifreleme** | PBKDF2 (SHA-256) Hashing |
| **PDF İşleme** | PyMuPDF + pdfplumber + ReportLab + Roboto Fonts |

---

## 🚀 Kurulum ve Çalıştırma

### 1. Ön Koşullar (NVIDIA Jetson AGX Orin veya Linux)
- [Ollama](https://ollama.com/download) kurulu ve çalışır durumda olmalı.
- Python 3.10+ yüklü olmalı.
- E-posta atabilmek için Google Hesabı **Uygulama Şifresi** (App Password) alınmış olmalı.

### 2. Projeyi Klonla ve Ayarları Yap
```bash
git clone https://github.com/dogukankilinc/LinkedIn_CV_Analyzer.git
cd LinkedIn_CV_Analyzer

# E-posta gönderebilmek için yapılandırma dosyasını (.env) oluşturun:
cat << 'EOF' > .env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=senin_mail_adresin@gmail.com
SMTP_PASS=senin_uygulama_sifren
EOF
```

### 3. Tek Komutla Başlat
```bash
chmod +x baslat.sh
./baslat.sh
```

`baslat.sh` otomatik olarak:
1. Ollama'nın çalışıp çalışmadığını kontrol eder.
2. `qwen2.5:14b` ve `phi4` modelleri eksikse indirir.
3. Python sanal ortamı (`.venv`) oluşturur ve kütüphaneleri kurar.
4. Her iki modeli arka planda RAM'e alır (`keep_alive: 4h` ile).
5. Uygulamayı `http://0.0.0.0:8501` adresinde başlatır.

Tarayıcınızdan şu adrese giderek uygulamaya erişebilirsiniz:
```
http://<cihaz-ip-adresi>:8501
```

> **Giriş Bilgileri:** Uygulama ilk açıldığında `dogukan` (Şifre: `admin123`) isimli kurucu/admin hesabı otomatik olarak oluşturulur. Diğer kullanıcılar "Hesap Oluştur" sekmesinden kendileri kayıt olabilirler.

---

## 📁 Proje Yapısı

```
cv_analyzer/
├── app.py                  # Streamlit Giriş/Kayıt arayüzü (Entrypoint)
├── pages/
│   ├── 1_Analiz.py         # Ana analiz ekranı, PDF/E-posta işlemleri
│   ├── 2_Gecmis.py         # Kullanıcı geçmişi (Son 10 analiz)
│   └── 3_Admin.py          # Admin yönetim paneli (Kullanıcı sil/şifre sıfırla)
│
├── core/
│   ├── auth.py             # Kimlik doğrulama, hashleme
│   ├── db.py               # SQLite veritabanı CRUD işlemleri
│   ├── llm_client.py       # Ollama API bağlantısı ve Warm-up
│   ├── email_sender.py     # Çoklu alıcı destekli SMTP e-posta gönderici
│   ├── md5_patch.py        # ReportLab MD5 FIPS yaması
│   ├── pdf_rapor.py        # Dinamik TTF font destekli A4 PDF oluşturucu
│   ├── prompt_builder.py   # MathWorks ürün kataloğu içeren asıl prompt
│   ├── response_parser.py  # JSON ayrıştırma ve doğrulama
│   ├── input_handler.py    # PDF ve metin birleştirme (PyMuPDF)
│   └── ui_helpers.py       # Ortak CSS, A/B/C/D skorlaması ve UI bileşenleri
│
├── data/
│   └── figes_cv.db         # (Otomatik oluşur) Veritabanı dosyası
├── fonts/                  
│   └── Roboto-*.ttf        # (Otomatik iner) Türkçe karakter fontları
│
├── baslat.bat              # Windows başlatma scripti
└── baslat.sh               # Jetson/Linux başlatma scripti
```

---

## 👨‍💻 Geliştirici

**Doğukan Mehmet KILINÇ**
*[linkedin.com/in/dgkilinc](https://www.linkedin.com/in/dgkilinc/)*
