# 🔬 FIGES MathWorks CV Analyzer

> Mühendis ve akademisyen CV'lerini analiz ederek en uygun **MATLAB, Simulink ve MathWorks Toolbox**'larını öneren, **tamamen yerel ve bulut bağımsız** yapay zeka satış asistanı.

---

## 📌 Ne İş Yapar?

Bir müşteri adayının CV'sini (PDF veya metin olarak) yüklersiniz; sistem:

- Adayın **mühendislik yetkinliklerini** ve çalıştığı teknik alanları tespit eder
- CV'deki **somut projelere ve becerilere** dayandırılmış MathWorks ürün önerileri üretir
- Her öneri için **satış argümanı** hazırlar (görüşmeye girmeden önce okuyun)
- Sonuçları **PDF raporu** ve **JSON** olarak dışa aktarır
- **CV diline göre otomatik model seçer** — Türkçe ve İngilizce için ayrı optimize edilmiş LLM

> **Gizlilik:** Veriler hiçbir zaman dışarıya çıkmaz. Model ve uygulama tamamen yerel çalışır.

---

## 🌐 Çift Dil & Çift Model Desteği

| | 🇹🇷 Türkçe CV | 🇬🇧 English CV |
|---|---|---|
| **Model** | `qwen2.5:14b` | `phi4` |
| **Boyut** | ~9 GB | ~9 GB |
| **Tahmini Süre** | ~15 sn | ~12 sn |
| **Neden bu model?** | Qwen ailesi Türkçe'de açık ara en iyi | Microsoft Phi-4 JSON & instruction-following şampiyonu |
| **Prompt dili** | Türkçe | English |
| **Çıktı dili** | Türkçe | English |

Uygulama açıldığında **🇹🇷 / 🇬🇧 butonlarından** biri seçilir. Tüm arayüz, prompt ve model otomatik değişir.

---

## ⚙️ Özellikler

| Özellik | Detay |
|---|---|
| 🔒 **Tam Gizlilik** | Yerel LLM (Ollama). Müşteri verisi dışarı çıkmaz. |
| 🧠 **Halüsinasyon Engeli** | Sistem promptuna gömülü resmi MathWorks ürün kataloğu. Model yalnızca gerçek ürün adlarını önerebilir. |
| 🌐 **Çift Dil Desteği** | Türkçe → `qwen2.5:14b` \| İngilizce → `phi4` |
| 📄 **Format Desteği** | PDF yükleme, metin yapıştırma veya her ikisi. |
| 💬 **Satış Argümanı** | Her öneri, satış ekibine hazır 2-3 cümlelik ikna metni içerir. |
| 📊 **PDF Raporu** | Profesyonel A4 rapor — tespit (turuncu), toolbox (mavi), satış argümanı (yeşil). |
| 🖥️ **Çoklu Platform** | Windows (`baslat.bat`) ve Linux/Jetson AGX Orin (`baslat.sh`) desteği. |

---

## 🛠️ Teknoloji Yığını

| Katman | Teknoloji |
|---|---|
| **Arayüz** | Streamlit |
| **LLM (TR)** | Ollama — `qwen2.5:14b` |
| **LLM (EN)** | Ollama — `phi4` |
| **API** | OpenAI uyumlu endpoint (`http://127.0.0.1:11434/v1`) |
| **PDF İşleme** | PyMuPDF + pdfplumber |
| **Raporlama** | ReportLab |

---

## 🚀 Kurulum ve Çalıştırma

### Windows

**Ön koşullar:**
1. [Python 3.10+](https://www.python.org/downloads/) — kurulumda **"Add Python to PATH"** kutusunu **mutlaka işaretleyin**
2. [Ollama](https://ollama.com/download) — indir ve kur
3. CMD açıp modelleri indir:
   ```cmd
   ollama pull qwen2.5:14b
   ollama pull phi4
   ```

**Başlatma:**
```
cv_analyzer klasörüne gir → baslat.bat dosyasına çift tıkla
```
Script sanal ortamı kurar, kütüphaneleri yükler, uygulamayı açar.

---

### Linux / NVIDIA Jetson AGX Orin

**Projeyi klonla:**
```bash
git clone https://github.com/dogukankilinc/LinkedIn_CV_Analyzer.git
cd LinkedIn_CV_Analyzer
```

**Tek komutla başlat:**
```bash
chmod +x baslat.sh
./baslat.sh
```

`baslat.sh` otomatik olarak:
- Ollama'nın kurulu ve çalışır olduğunu kontrol eder
- Eksik modelleri indirir
- Python sanal ortamı (`.venv`) oluşturur
- `requirements.txt` kütüphanelerini kurar
- Uygulamayı `http://0.0.0.0:8501` adresinde başlatır

Tarayıcıdan erişmek için:
```
http://<cihaz-ip-adresi>:8501
```

---

## 📁 Proje Yapısı

```
cv_analyzer/
├── app.py                  # Streamlit arayüzü (dil seçimi, analiz, sonuç kartları)
├── baslat.bat              # Windows başlatma scripti
├── baslat.sh               # Linux / Jetson AGX Orin başlatma scripti
├── requirements.txt        # Python bağımlılıkları
├── README.md
├── .gitignore
│
├── core/
│   ├── llm_client.py       # OpenAI SDK ile Ollama bağlantısı, dile göre model seçimi
│   ├── prompt_builder.py   # TR/EN sistem promptları + MathWorks ürün kataloğu
│   ├── response_parser.py  # JSON doğrulama ve alan garantisi
│   ├── input_handler.py    # PDF + metin birleştirici
│   ├── pdf_extractor.py    # PDF → metin dönüştürücü
│   └── pdf_rapor.py        # ReportLab ile A4 PDF rapor üretici
│
└── ui/
    ├── components.py
    └── charts.py
```

---

## 📦 Çıktı JSON Şeması

```json
{
  "kisisel_bilgiler": {
    "ad_soyad": "...",
    "sektor_veya_uzmanlik_alani": "Otomotiv / Savunma / Akademik..."
  },
  "mevcut_muhendislik_yetkinlikleri": [
    "Gömülü Sistemler", "Görüntü İşleme", "..."
  ],
  "mathworks_urun_tavsiyeleri": [
    {
      "tespit_edilen_ihtiyac": "CV'deki somut proje veya beceriye dayalı açıklama",
      "onerilen_ana_urun": "MATLAB veya Simulink",
      "onerilen_toolboxlar": ["Computer Vision Toolbox", "Embedded Coder"],
      "satis_ve_kullanim_argumani": "2-3 cümlelik teknik satış argümanı"
    }
  ]
}
```

---

## 🔧 Model veya Endpoint Değişikliği

`core/llm_client.py` içindeki `MODELS` sözlüğünü güncelleyin:

```python
MODELS = {
    "tr": "qwen2.5:14b",  # Türkçe CV için model
    "en": "phi4",          # İngilizce CV için model
}

BASE_URL = "http://127.0.0.1:11434/v1"  # Uzak sunucu için IP değiştirin
```

---

## 👨‍💻 Geliştirici

**Doğukan Mehmet KILINÇ**
*[linkedin.com/in/dgkilinc](https://www.linkedin.com/in/dgkilinc/)*
