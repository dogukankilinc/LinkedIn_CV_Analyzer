import streamlit as st
import json
import os
import time
import threading
from dotenv import load_dotenv
from core.input_handler import get_combined_text
from core.llm_client import (
    analyze_cv_with_ollama, check_ollama_status,
    get_model_name, warmup_model, MODELS
)
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
        background: #0f2537; border: 1px solid #1e4060;
        border-radius: 12px; padding: 18px 20px; margin-bottom: 14px;
    }
    .tavsiye-kart h4 { color: #63b3ed; margin: 0 0 8px 0; font-size: 15px; }
    .bulgu-kutusu {
        background: #1a2d40; border-left: 3px solid #e67e22;
        border-radius: 4px; padding: 8px 12px;
        color: #fbd38d; font-size: 13px; margin-bottom: 6px;
    }
    .kaynak-kutusu {
        background: #1a2540; border-left: 3px solid #9b59b6;
        border-radius: 4px; padding: 6px 12px;
        color: #d7bde2; font-size: 12px; margin-bottom: 10px;
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
        margin-top: 6px; line-height: 1.6;
    }
    .ipucu-kutusu {
        background: #1a1a2e; border-left: 3px solid #f39c12;
        border-radius: 4px; padding: 8px 12px;
        color: #fdebd0; font-size: 12.5px; margin-top: 6px;
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
    .puan-kutu {
        background: #0f2537; border: 1px solid #1e4060;
        border-radius: 10px; padding: 14px 18px; text-align: center;
    }
    .puan-sayi { font-size: 32px; font-weight: 700; color: #63b3ed; }
    .puan-etiket { font-size: 12px; color: #7fb3d3; margin-top: 4px; }
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
        "- `qwen2.5:14b` ve `phi4` modelleri yüklü mü?\n"
        "- Güvenlik duvarı 11434 portunu engelliyor mu?"
    )
    st.stop()

# ─── ARKA PLAN MODEL WARM-UP ────────────────────────────────────
@st.cache_resource
def _baslat_warmup() -> dict:
    threads = {}
    for lang in MODELS:
        t = threading.Thread(target=warmup_model, args=(lang,),
                             name=f"warmup-{MODELS[lang]}", daemon=True)
        t.start()
        threads[lang] = t
    return threads

_warmup_threads = _baslat_warmup()
_tr_yukleniyor  = _warmup_threads["tr"].is_alive()
_en_yukleniyor  = _warmup_threads["en"].is_alive()

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
        "🇬🇧  İngilizce CV\n\n`phi4` — Çıktı yine Türkçe üretilir",
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
_yukleniyor  = _tr_yukleniyor if language == "tr" else _en_yukleniyor
_durum_ikon  = "⏳ Belleğe alınıyor..." if _yukleniyor else "✅ Belleğe alındı, hazır!"
_durum_renk  = "#e67e22" if _yukleniyor else "#27ae60"
lang_icon    = "🇹🇷 Türkçe" if language == "tr" else "🇬🇧 İngilizce"

st.markdown(
    f'<div class="model-bilgi">'
    f'<span style="color:{_durum_renk};font-weight:bold">{_durum_ikon}</span>'
    f' &nbsp;|&nbsp; CV Dili: <b>{lang_icon}</b>'
    f' &nbsp;|&nbsp; Model: <code>{model_adi}</code>'
    f' &nbsp;|&nbsp; Çıktı: <b>Türkçe</b>'
    f'</div>',
    unsafe_allow_html=True
)
st.divider()

# ─── Veri Girişi ────────────────────────────────────────────────
st.subheader("📋 Veri Girişi")
input_mode = st.radio(
    "Yöntem:",
    ["📄 PDF", "📝 Metin", "📄+📝 İkisi"],
    horizontal=True,
    label_visibility="collapsed"
)

uploaded_file = None
manual_text   = ""

with st.container():
    if input_mode in ["📄 PDF", "📄+📝 İkisi"]:
        uploaded_file = st.file_uploader(
            "📂 CV dosyasını buraya sürükleyin (PDF)",
            type=["pdf"],
            help="LinkedIn'den 'Dışa Aktar → PDF Kaydet' ile indirilen dosyayı yükleyin."
        )
    if input_mode in ["📝 Metin", "📄+📝 İkisi"]:
        manual_text = st.text_area(
            "✏️ CV metnini buraya yapıştırın",
            height=220,
            placeholder="CV metnini veya LinkedIn profilini buraya yapıştırabilirsiniz..."
        )

can_analyze = False
if "PDF" in input_mode and uploaded_file is not None:
    can_analyze = True
elif "Metin" in input_mode and manual_text.strip():
    can_analyze = True
elif "İkisi" in input_mode and (uploaded_file is not None or manual_text.strip()):
    can_analyze = True

if not can_analyze:
    st.info("ℹ️ Analiz başlatmak için lütfen bir PDF yükleyin veya CV metnini yapıştırın.")

st.divider()
analiz_btn = st.button("🚀 ANALİZİ BAŞLAT", type="primary",
                       use_container_width=True, disabled=not can_analyze)

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
        start_time = time.time()
        asama(10, "📖 Dosyalar okunuyor ve birleştiriliyor...")
        cv_text = get_combined_text(uploaded_file, manual_text)

        asama(30, "📝 Analiz için metin hazırlanıyor...")

        asama(50, f"🤖 {model_adi} modeline gönderiliyor, lütfen bekleyin...")
        raw_response = analyze_cv_with_ollama(cv_text, language)

        asama(80, "🔍 Yanıt doğrulanıyor ve düzenleniyor...")
        result, errors = parse_and_validate(raw_response)
        
        end_time = time.time()
        gecen_sure = end_time - start_time

        asama(100, "✅ Analiz tamamlandı!")
        ilerleme_bar.empty()
        durum_metni.empty()

        if errors and not result:
            st.error(f"❌ {', '.join(errors)}")
            st.stop()
        if errors:
            st.warning(f"⚠️ {', '.join(errors)}\n\n(Süre: {gecen_sure:.1f} saniye)")
        else:
            st.success(f"✅ Analiz başarıyla tamamlandı! (Süre: {gecen_sure:.1f} saniye)")

        # ─── MÜŞTERİ PROFİLİ ────────────────────────────────────
        kisiler  = result.get("kisisel_bilgiler", {})
        ad_soyad = kisiler.get("ad_soyad") or "Bilinmiyor"
        sektor   = kisiler.get("sektor_veya_uzmanlik_alani") or "—"

        st.markdown(f"## 👤 {ad_soyad}")
        st.markdown(f"**Sektör / Uzmanlık Alanı:** `{sektor}`")
        st.divider()

        # ─── YETKİNLİK PUANLARI ─────────────────────────────────
        puanlar = result.get("yetkinlik_puanlari", {})
        ai_puan  = puanlar.get("yapay_zeka_ve_veri", 0)
        gs_puan  = puanlar.get("gomulu_sistemler", 0)
        sk_puan  = puanlar.get("sistem_ve_kontrol_modelleme", 0)

        st.markdown("### 📊 Yetkinlik Puanları")
        p1, p2, p3 = st.columns(3)
        with p1:
            st.markdown(
                f'<div class="puan-kutu">'
                f'<div class="puan-sayi">{ai_puan}</div>'
                f'<div class="puan-etiket">🤖 Yapay Zeka & Veri Bilimi</div>'
                f'</div>', unsafe_allow_html=True
            )
            st.progress(ai_puan)
        with p2:
            st.markdown(
                f'<div class="puan-kutu">'
                f'<div class="puan-sayi">{gs_puan}</div>'
                f'<div class="puan-etiket">🔧 Gömülü Sistemler</div>'
                f'</div>', unsafe_allow_html=True
            )
            st.progress(gs_puan)
        with p3:
            st.markdown(
                f'<div class="puan-kutu">'
                f'<div class="puan-sayi">{sk_puan}</div>'
                f'<div class="puan-etiket">⚙️ Sistem & Kontrol Modelleme</div>'
                f'</div>', unsafe_allow_html=True
            )
            st.progress(sk_puan)

        st.divider()

        # ─── MÜHENDİSLİK YETKİNLİKLERİ ─────────────────────────
        yetkinlikler = result.get("mevcut_muhendislik_yetkinlikleri", [])
        if yetkinlikler:
            st.markdown("### 🛠️ Müşteri Yetkinlikleri")
            badges = " ".join([f'<span class="beceri-badge">{y}</span>' for y in yetkinlikler])
            st.markdown(badges, unsafe_allow_html=True)
            st.divider()

        # ─── MATHWORKS ÖNERİLERİ ────────────────────────────────
        tavsiyeleri = result.get("mathworks_urun_tavsiyeleri", [])
        st.markdown(f"### 📦 Önerilen MathWorks Çözümleri  `({len(tavsiyeleri)} öneri)`")

        for i, tb in enumerate(tavsiyeleri, 1):
            ana_urun  = tb.get("onerilen_ana_urun", "MATLAB")
            toolboxlar = tb.get("onerilen_toolboxlar", [])
            bulgu     = tb.get("tespit_edilen_ihtiyac", "")
            kaynak    = tb.get("kaynak_bolum", "")
            arguman   = tb.get("satis_ve_kullanim_argumani", "")
            ipuclari  = tb.get("satis_stratejisi_ipuclari", [])

            toolbox_badges = " ".join(
                [f'<span class="toolbox-badge">📦 {t}</span>' for t in toolboxlar]
            )
            ipucu_html = "".join(
                [f'<div class="ipucu-kutusu">💡 {ip}</div>' for ip in ipuclari]
            )

            st.markdown(f"""
<div class="tavsiye-kart">
    <h4>#{i} — <span class="ana-urun-etiket">{ana_urun}</span></h4>
    <div class="bulgu-kutusu">🔍 <b>Tespit Edilen İhtiyaç:</b> {bulgu}</div>
    <div class="kaynak-kutusu">📂 <b>CV'deki Kaynak:</b> {kaynak}</div>
    <div style="margin-bottom:10px">{toolbox_badges}</div>
    <div class="arguman-kutusu">💬 <b>Satış Argümanı:</b> {arguman}</div>
    {ipucu_html}
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
                        file_name=f"mathworks_{aday_dosya_adi}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                except Exception as pdf_err:
                    st.error(f"PDF hatası: {pdf_err}")

        with exp_col2:
            st.download_button(
                label="🗂️ JSON Olarak İndir",
                data=json.dumps(result, ensure_ascii=False, indent=2),
                file_name=f"mathworks_{aday_dosya_adi}.json",
                mime="application/json",
                use_container_width=True
            )

        # ─── E-POSTA İLE GÖNDERİM ─────────────────────────────────
        st.markdown("### 📧 E-Posta ile Gönder")
        with st.expander("PDF Raporunu Doğrudan E-Posta ile Gönder"):
            st.info("💡 Not: Gönderim için `.env` dosyasında `SMTP_SERVER`, `SMTP_PORT`, `SMTP_USER` ve `SMTP_PASS` ayarları yapılmış olmalıdır.")
            hedef_mail = st.text_input("Alıcı E-Posta Adresi:", placeholder="ornek@sirket.com")
            if st.button("📤 E-Posta Gönder"):
                if not hedef_mail:
                    st.warning("Lütfen geçerli bir e-posta adresi girin.")
                else:
                    if 'pdf_bytes' not in locals():
                        try:
                            pdf_bytes = pdf_rapor_olustur(result)
                        except Exception as pdf_err:
                            st.error(f"PDF oluşturulamadı: {pdf_err}")
                            st.stop()
                            
                    with st.spinner("E-posta gönderiliyor..."):
                        from core.email_sender import send_pdf_email
                        baslik = f"FIGES MathWorks Öneri Raporu - {ad_soyad}"
                        mesaj = f"Merhaba,\n\n{ad_soyad} için oluşturulan MathWorks ürün öneri raporu ekte sunulmuştur.\n\nİyi çalışmalar,\nFIGES CV Analyzer"
                        
                        basari, msg = send_pdf_email(
                            to_email=hedef_mail,
                            subject=baslik,
                            body=mesaj,
                            pdf_bytes=pdf_bytes,
                            pdf_filename=f"mathworks_{aday_dosya_adi}.pdf"
                        )
                        if basari:
                            st.success(msg)
                        else:
                            st.error(msg)

    except Exception as e:
        ilerleme_bar.empty()
        durum_metni.empty()
        st.error(f"❌ {str(e)}")
        st.info("💡 Ollama servisinin çalıştığını ve modellerin yüklü olduğunu kontrol edin.")

# ─── Footer ──────────────────────────────────────────────────────
st.markdown("""
<div class="custom-footer">
    🔬 <strong>FIGES MathWorks CV Analyzer</strong> &nbsp;|&nbsp;
    🇹🇷 qwen2.5:14b &nbsp;·&nbsp; 🇬🇧 phi4 &nbsp;·&nbsp; Çıktı: Türkçe &nbsp;|&nbsp;
    Geliştirici: <a href="https://www.linkedin.com/in/dgkilinc/" target="_blank">Doğukan Mehmet KILINÇ</a>
    &nbsp;|&nbsp; Tüm veriler yerel cihazda işlenir
</div>
""", unsafe_allow_html=True)
