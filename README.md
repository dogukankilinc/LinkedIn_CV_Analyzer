# 🔬 FIGES CV Analyzer — MathWorks Ürün Öneri Sistemi

> Satış mühendislerinin potansiyel müşterilerin CV'lerini saniyeler içinde analiz edip, adayın profiline en uygun MathWorks Toolbox'larını önerebildiği, **tamamen yerel ve bulut bağımsız (gizlilik odaklı)** bir yapay zeka asistanıdır.

---

## 📌 Neler Yapabiliyor?

- **Akıllı Çıkarım:** Yüklenen PDF veya metin üzerinden adayın deneyimini MathWorks ürün ailesiyle otomatik eşleştirir.
- **Kategorize Edilmiş Puanlama:** Adayı **Yapay Zeka**, **Sistem Modelleme** ve **Gömülü Sistemler** olmak üzere 3 ana kategoride puanlar.
- **Kanıtlı Toolbox Önerileri:** Rastgele değil; "neden bu ürünü satmalıyız?" sorusunun cevabını direkt adayın CV'sinden orijinal ve spesifik ifadelerle (Türkçeye çevirerek) destekler.
- **Otomatik PDF Raporu:** Analiz sonuçlarını şirketinize özel antetli ve profesyonel bir PDF dosyasına döküp dışa aktarmanızı sağlar.
- **Satış Notları:** Görüşme sırasında satış ekibinin hızlıca kullanabileceği pitch notları (satış söylemleri) üretir.

---

## ⚙️ Özellikler ve Teknoloji

| Özellik | Detay |
|---|---|
| 🔒 **Tam Gizlilik** | Llama 3 / Qwen tabanlı yerel LLM kullanımı. Veriler cihazdan çıkmaz. |
| 🌐 **Yerleşik Çeviri** | İngilizce CV'leri bile tamamen Türkçeleştirip analiz eder. |
| 📄 **Format Desteği** | LinkedIn'den indirilen PDF'ler, direkt metin kopyalama veya her ikisi. |
| 📊 **Görsel Sunum** | Interaktif kategori puanları (Radar Grafikleri, İlerleme Çubukları). |
| 💾 **Dışa Aktarma** | Şık tasarımlı A4 rapor (`.pdf` olarak) ve teknik veriler (`.json` olarak). |

**Altyapı:**
- **Arayüz:** `Streamlit`
- **Yapay Zeka:** `Ollama` (Varsayılan model: `qwen2.5:7b`)
- **PDF İşleme:** `PyMuPDF (fitz)` & `pdfplumber`
- **Raporlama:** `ReportLab`
- **Grafikler:** `Plotly`

---

## 🚀 Kurulum ve İlk Çalıştırma

### 1. Ön Koşullar ve Veritabanı Kurulumu
Bu sistem tam gizlilik odaklı olduğu için Python ve Yapay Zeka modeli kendi bilgisayarınızda çalışır. Yepyeni bir bilgisayara kurarken şu adımları izleyin:

**A) Python Kurulumu (Kritik Adım):**
1. [python.org/downloads](https://www.python.org/downloads/) adresinden Python 3.10 veya üzerini indirin.
2. Kurulum dosyasını açtığınızda en alttaki **"Add Python to PATH"** kutucuğunu **MUTLAKA** işaretleyin. (İşaretlenmezse sistem çalışmaz).
3. "Install Now" diyerek kurulumu bitirin.

**B) Ollama ve Dil Modeli Kurulumu:**
1. [ollama.com/download](https://ollama.com/download) adresinden Ollama uygulamasını indirip kurun. Sağ altta (saat yanında) çalıştığından emin olun.
2. Başlat menüsünden `CMD` (Komut İstemcisi) açın ve şu komutu yazıp Enter'a basın:
   ```cmd
   ollama pull qwen2.5:7b
   ```
3. İndirme (%100) tamamlandığında CMD'yi kapatabilirsiniz. Artık ana beyin hazır.

### 2. Uygulamayı Başlatma (Windows)
Sistemi tek tıkla kurup çalıştırmak için yazılmış otomatik bir script bulunur.

1. Proje klasörüne (`cv_analyzer`) girin.
2. `baslat.bat` dosyasına çift tıklayın.
3. Script kendi kendine arkaplanda sanal ortam (`.venv`) kuracak, gerekli kütüphaneleri indirecek, Ollama bağlantısını kontrol edip uygulamayı tarayıcınızda açacaktır.

---

## 📁 Proje Klasör Yapısı

```
cv_analyzer/
├── app.py                  # Streamlit arayüzünün (UI) ana dosyası
├── baslat.bat              # Tek tıkla otomatik başlatan Windows scripti
├── requirements.txt        # Python kütüphane bağımlılıkları
├── README.md               # Proje dokümantasyonu (Bu dosya)
├── .gitignore              # Git tarafından takip edilmeyeceklerin listesi
│
├── .streamlit/
│   └── config.toml         # UI ayarları (Deploy butonunu gizler)
│
├── core/
│   ├── input_handler.py    # Gelen PDF veya metni temizleyip birleştirir
│   ├── llm_client.py       # Ollama ile iletişimi yönetir (model seçimi vb.)
│   ├── pdf_extractor.py    # PDF içerisinden metin ayıklar
│   ├── pdf_rapor.py        # Sonuçları profesyonel PDF'e dönüştürür
│   ├── prompt_builder.py   # Sistemin zekasını belirten detaylı System Prompt
│   └── response_parser.py  # Model listesini doğrular, eksikleri onarır
│
└── ui/
    ├── charts.py           # Kategori puanları için Plotly radar kodları
    └── components.py       # Aday kartı, toolbox kartları tasarımı
```

---

## 🛠 Model Değişimi veya İnce Ayarlar

Eğer performanstan veya analiz süresinden memnun kalmazsanız, kod içerisinden modeli değiştirebilirsiniz. `core/llm_client.py` dosyasını açıp 5. satırda bulunan ifadeyi güncelleyin:

```python
# Güncel model (Hızlı, akıllı, Türkçe destekli)
MODEL_NAME = "qwen2.5:7b"

# Bilgisayarınız çok daha güçlü ise (Daha detaylı sonuç):
# MODEL_NAME = "qwen2.5:14b"
```

Aynı şekilde `core/prompt_builder.py` dosyasını açarak, modelin ürün kataloglarını tararken baz aldığı eşleştirme kurallarını dilediğiniz gibi satış stratejinize göre güncelleyebilirsiniz.

---

## 👨‍💻 Geliştirici
**Doğukan Mehmet KILINÇ**  
*[LinkedIn Profiline Git](https://www.linkedin.com/in/dgkilinc/)*
