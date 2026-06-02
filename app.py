import streamlit as st
import json
import os
from dotenv import load_dotenv
from core.input_handler import get_combined_text
from core.llm_client import analyze_cv_with_ollama, check_ollama_status, get_model_name
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
    .dil-kart {
        border-radius: 12px; padding: 16px 20px; margin-bottom: 4px;
        text-align: center; cursor: pointer;
    }
    .beceri-badge {
        display: inline-block; background: #1a365d;
        color: #90cdf4; border: 1px solid #2b6cb0;
        border-radius: 20px; padding: 4px 12px;
        font-size: 12px; margin: 3px 4px 3px 0;
    }
    .tavsiye-kart {
        background: #0f2537; border: 1px solid #1e4060;
        border-radius: 12px; padding: 18px 20px; margin-bottom: 14px;
    }
    .tavsiye-kart h4 { color: #63b3ed; margin: 0 0 8px 0; font-size: 15px; }
    .bulgu-kutusu {
        background: #1a2d40; border-left: 3px solid #e67e22;
        border-radius: 4px; padding: 8px 12px;
        color: #fbd38d; font-size: 13px; margin-bottom: 10px;
    }
    .toolbox-badge {
        display: inline-block; background: #1c4f82; color: #bee3f8;
        border: 1px solid #2b6cb0; border-radius: 6px;
        padding: 4px 12px; font-size: 12px;
        margin: 3px 4px 3px 0; font-weight: 600;
    }
    .arguman-kutusu {
        background: #0d3b2e; border-left: 3px solid #27ae60;
        border-radius: 4px; padding: 10px 14px;
        color: #c6f6d5; font-size: 13.5px;
        margin-top: 10px; line-height: 1.6;
    }
    .ana-urun-etiket {
        display: inline-block; background: #0076A8; color: white;
        border-radius: 20px; padding: 3px 14px;
        font-size: 12px; font-weight: 700; margin-bottom: 8px;
    }
    .model-bilgi {
        background: #0d1f2d; border: 1px solid #1e4060;
        border-radius: 8px; padding: 10px 16px;
        font-size: 13px; color: #7fb3d3; margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ─── Başlık ─────────────────────────────────────────────────────
st.markdown("# 🔬 FIGES MathWorks CV Analyzer")
st.markdown("**MathWorks Ürün Öneri Motoru** — Yerel LLM | Ollama `localhost:11434`")
st.divider()

# ─── Bağlantı Kontrolü ──────────────────────────────────────────
if not check_ollama_status():
    st.error("⚠️ Yerel Ollama servisine (127.0.0.1:11434) bağlanılamıyor.")
    st.info(
        "💡 **Kontrol listesi:**\n"
        "- Ollama uygulaması başlatıldı mı? (`ollama serve`)\n"
        "- Güvenlik duvarı 11434 portunu engelliyor mu?"
    )
    st.stop()

# ─── DİL SEÇİMİ ─────────────────────────────────────────────────
st.subheader("🌐 CV Dili Seçin")

lang_col1, lang_col2 = st.columns(2)
with lang_col1:
    tr_btn = st.button(
        "🇹🇷  Türkçe CV\n\n`qwen2.5:14b` — Türkçe'de en güçlü açık model",
        use_container_width=True,
        type="primary" if st.session_state.get("language", "tr") == "tr" else "secondary",
        key="btn_tr"
    )
with lang_col2:
    en_btn = st.button(
        "🇬🇧  English CV\n\n`phi4` — Microsoft's champion for JSON & instructions",
        use_container_width=True,
        type="primary" if st.session_state.get("language", "tr") == "en" else "secondary",
        key="btn_en"
    )

if tr_btn:
    st.session_state["language"] = "tr"
    st.rerun()
if en_btn:
    st.session_state["language"] = "en"
    st.rerun()

language  = st.session_state.get("language", "tr")
model_adi = get_model_name(language)
lang_icon = "🇹🇷 Türkçe" if language == "tr" else "🇬🇧 English"

st.markdown(
    f'<div class="model-bilgi">✅ Aktif mod: <b>{lang_icon}</b> &nbsp;|&nbsp; '
    f'Model: <code>{model_adi}</code> &nbsp;|&nbsp; '
    f'Çıktı dili: <b>{"Türkçe" if language == "tr" else "English"}</b></div>',
    unsafe_allow_html=True
)
st.divider()

# ─── Veri Girişi ────────────────────────────────────────────────
upload_label = "📂 CV dosyasını buraya sürükleyin (PDF)" if language == "tr" else "📂 Drop your CV here (PDF)"
text_label   = "✏️ CV metnini buraya yapıştırın" if language == "tr" else "✏️ Paste your CV text here"
text_ph      = "CV metnini veya LinkedIn profilini buraya yapıştırabilirsiniz..." if language == "tr" else "Paste CV text or LinkedIn profile content here..."

st.subheader("📋 Veri Girişi" if language == "tr" else "📋 Input")
input_mode = st.radio(
    "Yöntem:",
    ["📄 PDF", "📝 Metin / Text", "📄+📝 İkisi / Both"],
    horizontal=True,
    label_visibility="collapsed"
)

uploaded_file = None
manual_text   = ""

with st.container():
    if input_mode in ["📄 PDF", "📄+📝 İkisi / Both"]:
        uploaded_file = st.file_uploader(upload_label, type=["pdf"])
    if input_mode in ["📝 Metin / Text", "📄+📝 İkisi / Both"]:
        manual_text = st.text_area(text_label, height=220, placeholder=text_ph)

# ─── Form Doğrulama ─────────────────────────────────────────────
can_analyze = False
if "PDF" in input_mode and uploaded_file is not None:
    can_analyze = True
elif "Metin" in input_mode and manual_text.strip():
    can_analyze = True
elif "İkisi" in input_mode and (uploaded_file is not None or manual_text.strip()):
    can_analyze = True

if not can_analyze:
    st.info("ℹ️ Lütfen bir PDF yükleyin veya CV metnini yapıştırın." if language == "tr"
            else "ℹ️ Please upload a PDF or paste your CV text.")

st.divider()
btn_label = "🚀 ANALİZİ BAŞLAT" if language == "tr" else "🚀 START ANALYSIS"
analiz_btn = st.button(btn_label, type="primary", use_container_width=True, disabled=not can_analyze)

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
        asama(10, "📖 Dosyalar okunuyor..." if language == "tr" else "📖 Reading files...")
        cv_text = get_combined_text(uploaded_file, manual_text)

        asama(30, "📝 Metin hazırlanıyor..." if language == "tr" else "📝 Preparing text...")

        asama(50, f"🤖 {model_adi} modeline gönderiliyor, lütfen bekleyin..."
              if language == "tr" else f"🤖 Sending to {model_adi}, please wait...")
        raw_response = analyze_cv_with_ollama(cv_text, language)

        asama(80, "🔍 Yanıt doğrulanıyor..." if language == "tr" else "🔍 Validating response...")
        result, errors = parse_and_validate(raw_response)

        asama(100, "✅ Tamamlandı!" if language == "tr" else "✅ Done!")
        ilerleme_bar.empty()
        durum_metni.empty()

        # ─── Hata Kontrolü ──────────────────────────────────────
        if errors and not result:
            st.error(f"❌ {', '.join(errors)}")
            st.stop()
        if errors:
            st.warning(f"⚠️ {', '.join(errors)}")
        else:
            st.success("✅ Analiz başarıyla tamamlandı!" if language == "tr" else "✅ Analysis completed successfully!")

        # ─── MÜŞTERİ PROFİLİ ────────────────────────────────────
        kisiler  = result.get("kisisel_bilgiler", {})
        ad_soyad = kisiler.get("ad_soyad") or ("Bilinmiyor" if language == "tr" else "Unknown")
        sektor   = kisiler.get("sektor_veya_uzmanlik_alani") or "—"

        st.markdown(f"## 👤 {ad_soyad}")
        label = "Sektör / Uzmanlık Alanı" if language == "tr" else "Sector / Expertise"
        st.markdown(f"**{label}:** `{sektor}`")
        st.divider()

        # ─── YETKİNLİKLER ───────────────────────────────────────
        yetkinlikler = result.get("mevcut_muhendislik_yetkinlikleri", [])
        if yetkinlikler:
            title = "🛠️ Müşteri Yetkinlikleri" if language == "tr" else "🛠️ Customer Competencies"
            st.markdown(f"### {title}")
            badges = " ".join([f'<span class="beceri-badge">{y}</span>' for y in yetkinlikler])
            st.markdown(badges, unsafe_allow_html=True)
            st.divider()

        # ─── MATHWORKS ÖNERİLERİ ────────────────────────────────
        tavsiyeleri = result.get("mathworks_urun_tavsiyeleri", [])
        title = f"📦 Önerilen MathWorks Çözümleri  `({len(tavsiyeleri)} öneri)`" if language == "tr" \
                else f"📦 Recommended MathWorks Solutions  `({len(tavsiyeleri)} recommendations)`"
        st.markdown(f"### {title}")

        for i, tb in enumerate(tavsiyeleri, 1):
            ana_urun   = tb.get("onerilen_ana_urun", "MATLAB")
            toolboxlar = tb.get("onerilen_toolboxlar", [])
            bulgu      = tb.get("tespit_edilen_ihtiyac", "")
            arguman    = tb.get("satis_ve_kullanim_argumani", "")

            toolbox_badges = " ".join([f'<span class="toolbox-badge">📦 {t}</span>' for t in toolboxlar])
            bulgu_label  = "Tespit Edilen İhtiyaç" if language == "tr" else "Identified Need"
            arguman_label = "Satış Argümanı" if language == "tr" else "Sales Argument"

            st.markdown(f"""
<div class="tavsiye-kart">
    <h4>#{i} — <span class="ana-urun-etiket">{ana_urun}</span></h4>
    <div class="bulgu-kutusu">🔍 <b>{bulgu_label}:</b> {bulgu}</div>
    <div style="margin-bottom:8px">{toolbox_badges}</div>
    <div class="arguman-kutusu">💬 <b>{arguman_label}:</b> {arguman}</div>
</div>
""", unsafe_allow_html=True)

        # ─── RAPOR DIŞA AKTARMA ──────────────────────────────────
        st.divider()
        export_title = "### 📤 Raporu Dışa Aktar" if language == "tr" else "### 📤 Export Report"
        st.markdown(export_title)
        aday_dosya_adi = ad_soyad.replace(" ", "_")

        exp_col1, exp_col2 = st.columns(2)
        with exp_col1:
            with st.spinner("PDF hazırlanıyor..." if language == "tr" else "Preparing PDF..."):
                try:
                    pdf_bytes = pdf_rapor_olustur(result)
                    st.download_button(
                        label="📄 PDF İndir" if language == "tr" else "📄 Download PDF",
                        data=pdf_bytes,
                        file_name=f"mathworks_{aday_dosya_adi}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                except Exception as pdf_err:
                    st.error(f"PDF hatası: {pdf_err}")

        with exp_col2:
            st.download_button(
                label="🗂️ JSON İndir" if language == "tr" else "🗂️ Download JSON",
                data=json.dumps(result, ensure_ascii=False, indent=2),
                file_name=f"mathworks_{aday_dosya_adi}.json",
                mime="application/json",
                use_container_width=True
            )

    except Exception as e:
        ilerleme_bar.empty()
        durum_metni.empty()
        st.error(f"❌ {str(e)}")
        st.info("💡 Ollama servisinin çalıştığını ve modelin yüklü olduğunu kontrol edin." if language == "tr"
                else "💡 Check that Ollama is running and the model is installed.")

# ─── Footer ──────────────────────────────────────────────────────
st.markdown("""
<div class="custom-footer">
    🔬 <strong>FIGES MathWorks CV Analyzer</strong> &nbsp;|&nbsp;
    🇹🇷 qwen2.5:14b &nbsp;·&nbsp; 🇬🇧 phi4 &nbsp;|&nbsp;
    Geliştirici: <a href="https://www.linkedin.com/in/dgkilinc/" target="_blank">Doğukan Mehmet KILINÇ</a>
    &nbsp;|&nbsp; Tüm veriler yerel cihazda işlenir
</div>
""", unsafe_allow_html=True)
