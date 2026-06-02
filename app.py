import streamlit as st
import json
import os
from dotenv import load_dotenv
from core.input_handler import get_combined_text
from core.llm_client import analyze_cv_with_ollama, check_ollama_status
from core.response_parser import parse_and_validate
from core.pdf_rapor import pdf_rapor_olustur

load_dotenv()

# ─── Sayfa Konfigürasyonu ───────────────────────────────────────
st.set_page_config(
    page_title="FIGES MathWorks CV Analyzer",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "**FIGES MathWorks CV Analyzer**\n\nGeliştirici: Doğukan Mehmet KILINÇ\nhttps://www.linkedin.com/in/dgkilinc/"
    }
)

# ─── CSS ────────────────────────────────────────────────────────
st.markdown("""
<style>
    .stDeployButton { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }
    footer { display: none !important; }
    header[data-testid="stHeader"] { display: none !important; }

    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #0076A8, #00a3e0);
    }
    .custom-footer {
        position: fixed; bottom: 0; left: 0; right: 0;
        background: linear-gradient(90deg, #0f2537 0%, #1a3a5c 100%);
        color: #aac8e4; text-align: center;
        padding: 8px 20px; font-size: 13px;
        z-index: 999; border-top: 1px solid #2c5282;
    }
    .custom-footer a { color: #63b3ed; text-decoration: none; }
    .custom-footer a:hover { color: #90cdf4; text-decoration: underline; }
    .main .block-container { padding-bottom: 60px; }

    .asama-kutusu {
        background: #1a2d40; border-left: 4px solid #0076A8;
        border-radius: 6px; padding: 10px 16px; margin-bottom: 8px;
        color: #cce5f6; font-size: 14px;
    }
    .beceri-badge {
        display: inline-block; background: #1a365d;
        color: #90cdf4; border: 1px solid #2b6cb0;
        border-radius: 20px; padding: 4px 12px;
        font-size: 12px; margin: 3px 4px 3px 0;
    }
    .tavsiye-kart {
        background: #0f2537;
        border: 1px solid #1e4060;
        border-radius: 12px;
        padding: 18px 20px;
        margin-bottom: 14px;
    }
    .tavsiye-kart h4 {
        color: #63b3ed;
        margin: 0 0 8px 0;
        font-size: 15px;
    }
    .bulgu-kutusu {
        background: #1a2d40;
        border-left: 3px solid #e67e22;
        border-radius: 4px;
        padding: 8px 12px;
        color: #fbd38d;
        font-size: 13px;
        margin-bottom: 10px;
    }
    .toolbox-badge {
        display: inline-block;
        background: #1c4f82;
        color: #bee3f8;
        border: 1px solid #2b6cb0;
        border-radius: 6px;
        padding: 4px 12px;
        font-size: 12px;
        margin: 3px 4px 3px 0;
        font-weight: 600;
    }
    .arguman-kutusu {
        background: #0d3b2e;
        border-left: 3px solid #27ae60;
        border-radius: 4px;
        padding: 10px 14px;
        color: #c6f6d5;
        font-size: 13.5px;
        margin-top: 10px;
        line-height: 1.6;
    }
    .ana-urun-etiket {
        display: inline-block;
        background: #0076A8;
        color: white;
        border-radius: 20px;
        padding: 3px 14px;
        font-size: 12px;
        font-weight: 700;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ─── Başlık ─────────────────────────────────────────────────────
orin_ip = "127.0.0.1"
st.markdown("# 🔬 FIGES MathWorks CV Analyzer")
st.markdown(
    f"**MathWorks Ürün Öneri Motoru** — Model: `qwen2.5:72b` | "
    f"Ollama: `localhost:11434`"
)
st.divider()

# ─── Bağlantı Kontrolü ──────────────────────────────────────────
if not check_ollama_status():
    st.error("⚠️ Yerel Ollama servisine (127.0.0.1:11434) bağlanılamıyor.")
    st.info(
        "💡 **Kontrol listesi:**\n"
        "- Ollama uygulaması başlatıldı mı? (`ollama serve`)\n"
        "- `qwen2.5:72b` modeli yüklü mü? (`ollama pull qwen2.5:72b`)\n"
        "- Güvenlik duvarı 11434 portunu engelliyor mu?"
    )
    st.stop()

# ─── Veri Girişi ────────────────────────────────────────────────
st.subheader("📋 Veri Girişi")
input_mode = st.radio(
    "Yöntem:",
    ["📄 Sadece PDF Yükle", "📝 Sadece Metin Yapıştır", "📄+📝 PDF ve Metni Birlikte Kullan"],
    horizontal=True,
    label_visibility="collapsed"
)

uploaded_file = None
manual_text = ""

with st.container():
    if input_mode in ["📄 Sadece PDF Yükle", "📄+📝 PDF ve Metni Birlikte Kullan"]:
        uploaded_file = st.file_uploader(
            "📂 CV dosyasını buraya sürükleyin (PDF)",
            type=["pdf"],
            help="LinkedIn profilinizden 'Dışa Aktar → PDF Kaydet' ile indirilen dosyayı yükleyin."
        )
    if input_mode in ["📝 Sadece Metin Yapıştır", "📄+📝 PDF ve Metni Birlikte Kullan"]:
        manual_text = st.text_area(
            "✏️ CV metnini buraya yapıştırın",
            height=220,
            placeholder="CV metnini, proje açıklamalarını veya LinkedIn profilini buraya yapıştırabilirsiniz..."
        )

# ─── Form Doğrulama ─────────────────────────────────────────────
can_analyze = False
if "PDF Yükle" in input_mode and uploaded_file is not None:
    can_analyze = True
elif "Metin Yapıştır" in input_mode and manual_text.strip():
    can_analyze = True
elif "Birlikte Kullan" in input_mode and (uploaded_file is not None or manual_text.strip()):
    can_analyze = True

if not can_analyze:
    st.info("ℹ️ Analiz başlatmak için lütfen bir PDF yükleyin veya metin girin.")

st.divider()
analiz_btn = st.button(
    "🚀 ANALİZİ BAŞLAT",
    type="primary",
    use_container_width=True,
    disabled=not can_analyze
)

# ─── Analiz ─────────────────────────────────────────────────────
if analiz_btn:
    durum_metni  = st.empty()
    ilerleme_bar = st.progress(0)

    def asama(yuzde: int, mesaj: str):
        ilerleme_bar.progress(yuzde)
        durum_metni.markdown(
            f'<div class="asama-kutusu">🔹 <b>{mesaj}</b>'
            f'&nbsp;<span style="float:right;color:#0076A8;font-weight:bold">{yuzde}%</span></div>',
            unsafe_allow_html=True
        )

    try:
        asama(10, "📖 Dosyalar okunuyor ve birleştiriliyor...")
        cv_text = get_combined_text(uploaded_file, manual_text)

        asama(30, "📝 Analiz için metin hazırlanıyor...")

        asama(50, "🤖 Jetson AGX Orin'e gönderiliyor — qwen2.5:72b analiz ediyor, lütfen bekleyin...")
        raw_response = analyze_cv_with_ollama(cv_text)

        asama(80, "🔍 Yanıt doğrulanıyor ve MathWorks önerileri düzenleniyor...")
        result, errors = parse_and_validate(raw_response)

        asama(100, "✅ Analiz tamamlandı!")
        ilerleme_bar.empty()
        durum_metni.empty()

        # ─── Hata Kontrolü ──────────────────────────────────────
        if errors and not result:
            st.error(f"❌ Analiz tamamlanamadı: {', '.join(errors)}")
            st.stop()
        if errors:
            st.warning(f"⚠️ Analiz tamamlandı, bazı uyarılar: {', '.join(errors)}")
        else:
            st.success("✅ Analiz başarıyla tamamlandı!")

        # ─── MÜŞTERİ PROFİLİ ────────────────────────────────────
        kisiler  = result.get("kisisel_bilgiler", {})
        ad_soyad = kisiler.get("ad_soyad") or "Bilinmiyor"
        sektor   = kisiler.get("sektor_veya_uzmanlik_alani") or "—"

        st.markdown(f"## 👤 {ad_soyad}")
        st.markdown(f"**Sektör / Uzmanlık Alanı:** `{sektor}`")
        st.divider()

        # ─── MÜHENDİSLİK YETKİNLİKLERİ ─────────────────────────
        yetkinlikler = result.get("mevcut_muhendislik_yetkinlikleri", [])
        if yetkinlikler:
            st.markdown("### 🛠️ Müşteri Yetkinlikleri")
            badges = " ".join(
                [f'<span class="beceri-badge">{y}</span>' for y in yetkinlikler]
            )
            st.markdown(badges, unsafe_allow_html=True)
            st.divider()

        # ─── MATHWORKS ÖNERİLERİ ────────────────────────────────
        tavsiyeleri = result.get("mathworks_urun_tavsiyeleri", [])
        st.markdown(f"### 📦 Önerilen MathWorks Çözümleri  `({len(tavsiyeleri)} öneri)`")

        for i, tb in enumerate(tavsiyeleri, 1):
            ana_urun   = tb.get("onerilen_ana_urun", "MATLAB")
            toolboxlar = tb.get("onerilen_toolboxlar", [])
            bulgu      = tb.get("tespit_edilen_ihtiyac", "")
            arguman    = tb.get("satis_ve_kullanim_argumani", "")

            toolbox_badges = " ".join(
                [f'<span class="toolbox-badge">📦 {t}</span>' for t in toolboxlar]
            )

            st.markdown(f"""
<div class="tavsiye-kart">
    <h4>#{i} — <span class="ana-urun-etiket">{ana_urun}</span></h4>
    <div class="bulgu-kutusu">🔍 <b>Tespit Edilen İhtiyaç:</b> {bulgu}</div>
    <div style="margin-bottom:8px">{toolbox_badges}</div>
    <div class="arguman-kutusu">💬 <b>Satış Argümanı:</b> {arguman}</div>
</div>
""", unsafe_allow_html=True)

        # ─── RAPOR DIŞA AKTARMA ──────────────────────────────────
        st.divider()
        st.markdown("### 📤 Raporu Dışa Aktar")
        aday_dosya_adi = ad_soyad.replace(" ", "_")

        exp_col1, exp_col2 = st.columns(2)
        with exp_col1:
            with st.spinner("PDF hazırlanıyor..."):
                try:
                    pdf_bytes = pdf_rapor_olustur(result)
                    st.download_button(
                        label="📄 PDF Olarak İndir",
                        data=pdf_bytes,
                        file_name=f"mathworks_analiz_{aday_dosya_adi}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                except Exception as pdf_err:
                    st.error(f"PDF oluşturulamadı: {pdf_err}")

        with exp_col2:
            st.download_button(
                label="🗂️ JSON Olarak İndir",
                data=json.dumps(result, ensure_ascii=False, indent=2),
                file_name=f"mathworks_analiz_{aday_dosya_adi}.json",
                mime="application/json",
                use_container_width=True
            )

    except Exception as e:
        ilerleme_bar.empty()
        durum_metni.empty()
        st.error(f"❌ Beklenmeyen bir hata oluştu: {str(e)}")
        st.info(
            "💡 Yerel Ollama servisinin çalıştığını ve "
            "`qwen2.5:72b` modelinin yüklü olduğunu kontrol edin."
        )

# ─── Footer ──────────────────────────────────────────────────────
st.markdown("""
<div class="custom-footer">
    🔬 <strong>FIGES MathWorks CV Analyzer</strong> &nbsp;|&nbsp;
    Ollama · qwen2.5:72b · localhost &nbsp;|&nbsp;
    Geliştirici: <a href="https://www.linkedin.com/in/dgkilinc/" target="_blank">Doğukan Mehmet KILINÇ</a>
    &nbsp;|&nbsp; Tüm veriler yerel cihazda işlenir
</div>
""", unsafe_allow_html=True)
