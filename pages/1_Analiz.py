import streamlit as st
import os
import time
import threading
from dotenv import load_dotenv
from core.auth import require_login
from core.db import init_db, save_analysis, check_duplicate, get_analysis_pdf
from core.ui_helpers import (
    apply_css, render_footer, render_topbar,
    hesapla_potansiyel, render_analiz_sonuclari
)
from core.input_handler import get_combined_text
from core.llm_client import (
    analyze_cv_with_ollama, check_ollama_status,
    get_model_name, warmup_model, MODELS
)
from core.response_parser import parse_and_validate
from core.pdf_rapor import pdf_rapor_olustur
from core.email_sender import send_pdf_email

load_dotenv()
init_db()

st.set_page_config(
    page_title="FIGES CV Analyzer — Analiz",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={"Get Help": None, "Report a bug": None, "About": None},
)

apply_css()
user = require_login()

# ─── Üst Çubuk ───────────────────────────────────────────────────
render_topbar()
st.markdown("**MathWorks Ürün Öneri Motoru** — Yerel LLM | Ollama `localhost:11434`")
st.divider()

# ─── Ollama Bağlantı Kontrolü ────────────────────────────────────
if not check_ollama_status():
    st.error("⚠️ Yerel Ollama servisine bağlanılamıyor (127.0.0.1:11434).")
    st.info(
        "💡 **Kontrol listesi:**\n"
        "- Ollama çalışıyor mu? (`ollama serve`)\n"
        "- `qwen2.5:14b` ve `phi4` modelleri yüklü mü?\n"
        "- 11434 portu güvenlik duvarında açık mı?"
    )
    st.stop()

# ─── Model Warm-up ───────────────────────────────────────────────
@st.cache_resource
def _baslat_warmup() -> dict:
    threads = {}
    for lang in MODELS:
        t = threading.Thread(
            target=warmup_model, args=(lang,),
            name=f"warmup-{MODELS[lang]}", daemon=True
        )
        t.start()
        threads[lang] = t
    return threads

_warmup_threads = _baslat_warmup()

# ─── Dil Seçimi ──────────────────────────────────────────────────
st.subheader("🌐 CV Dili Seçin")
lc1, lc2 = st.columns(2)
with lc1:
    tr_btn = st.button(
        "🇹🇷  Türkçe CV\n\n`qwen2.5:14b`",
        use_container_width=True,
        type="primary" if st.session_state.get("language", "tr") == "tr" else "secondary",
        key="btn_tr"
    )
with lc2:
    en_btn = st.button(
        "🇬🇧  İngilizce CV\n\n`phi4` — çıktı Türkçe",
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
_yukleniyor = _warmup_threads[language].is_alive()
_ikon   = "⏳ Belleğe alınıyor..." if _yukleniyor else "✅ Hazır"
_renk   = "#e67e22"                if _yukleniyor else "#27ae60"
st.markdown(
    f'<div class="model-bilgi">'
    f'<span style="color:{_renk};font-weight:bold">{_ikon}</span>'
    f' &nbsp;|&nbsp; Model: <code>{model_adi}</code>'
    f' &nbsp;|&nbsp; Çıktı: <b>Türkçe</b></div>',
    unsafe_allow_html=True
)
st.divider()

# ─── Veri Girişi ─────────────────────────────────────────────────
st.subheader("📋 Veri Girişi")
input_mode = st.radio(
    "Yöntem:", ["📄 PDF", "📝 Metin", "📄+📝 İkisi"],
    horizontal=True, label_visibility="collapsed"
)
uploaded_file = None
manual_text   = ""
if input_mode in ["📄 PDF", "📄+📝 İkisi"]:
    uploaded_file = st.file_uploader(
        "📂 CV dosyasını sürükleyin (PDF)", type=["pdf"],
        help="LinkedIn'den 'Dışa Aktar → PDF' ile indirilen dosya."
    )
if input_mode in ["📝 Metin", "📄+📝 İkisi"]:
    manual_text = st.text_area(
        "✏️ CV metnini yapıştırın", height=200,
        placeholder="CV veya LinkedIn profilini yapıştırabilirsiniz..."
    )

can_analyze = (
    ("PDF" in input_mode and uploaded_file is not None)
    or ("Metin" in input_mode and manual_text.strip())
    or ("İkisi" in input_mode and (uploaded_file is not None or manual_text.strip()))
)
if not can_analyze:
    st.info("ℹ️ Analiz için PDF yükleyin veya metin yapıştırın.")

# ─── Butonlar ────────────────────────────────────────────────────
btn_col1, btn_col2 = st.columns([3, 1])
with btn_col1:
    analiz_btn = st.button(
        "🚀 ANALİZİ BAŞLAT", type="primary",
        use_container_width=True, disabled=not can_analyze, key="btn_analiz"
    )
with btn_col2:
    if st.button("🗑️ Temizle", use_container_width=True, key="btn_temizle"):
        for k in ["analiz_result", "analiz_pdf", "analiz_ad_soyad",
                  "analiz_sure_str", "analiz_hatalar",
                  "analiz_potansiyel", "analiz_db_id", "eski_analiz_goster"]:
            st.session_state.pop(k, None)
        st.rerun()

st.divider()

# ─── Analiz İşlemi ───────────────────────────────────────────────
if analiz_btn:
    # Temizle
    for k in ["analiz_result", "analiz_pdf", "analiz_ad_soyad",
              "analiz_sure_str", "analiz_hatalar",
              "analiz_potansiyel", "analiz_db_id", "eski_analiz_goster"]:
        st.session_state.pop(k, None)

    durum = st.empty()
    bar   = st.progress(0)

    def asama(p, m):
        bar.progress(p)
        durum.markdown(
            f'<div class="asama-kutusu">🔹 <b>{m}</b>'
            f'<span style="float:right;color:#0076A8;font-weight:bold">{p}%</span></div>',
            unsafe_allow_html=True
        )

    try:
        t0 = time.time()
        asama(10, "📖 Dosyalar okunuyor...")
        cv_text = get_combined_text(uploaded_file, manual_text)
        asama(40, f"🤖 {model_adi} modeline gönderiliyor...")
        raw     = analyze_cv_with_ollama(cv_text, language)
        asama(80, "🔍 Yanıt işleniyor...")
        result, errors = parse_and_validate(raw)

        gecen = time.time() - t0
        sure_str = f"{gecen:.0f} sn" if gecen < 60 else f"{int(gecen//60)} dk {int(gecen%60):02d} sn"

        asama(100, "✅ Tamamlandı!")
        bar.empty()
        durum.empty()

        if errors and not result:
            st.error(f"❌ {', '.join(errors)}")
            st.stop()

        # Potansiyel hesapla
        potansiyel_sinif, potansiyel_label = hesapla_potansiyel(
            result.get("yetkinlik_puanlari", {})
        )

        # PDF üret
        pdf_bytes = None
        try:
            pdf_bytes = pdf_rapor_olustur(result)
        except Exception as pdf_err:
            st.warning(f"⚠️ PDF oluşturulamadı: {pdf_err}")

        # Veritabanına kaydet
        ad_soyad = (result.get("kisisel_bilgiler") or {}).get("ad_soyad") or "Bilinmiyor"
        sektor   = (result.get("kisisel_bilgiler") or {}).get("sektor_veya_uzmanlik_alani") or "—"
        db_id = save_analysis(
            user_id=user["id"],
            ad_soyad=ad_soyad, sektor=sektor,
            model=model_adi, language=language,
            sure_str=sure_str, potansiyel=potansiyel_sinif,
            json_result=result, pdf_data=pdf_bytes
        )

        # Duplikat kontrolü (bu çalıştırmadan önceki kayıt var mıydı?)
        eski = check_duplicate(user["id"], ad_soyad)
        if eski and eski["id"] != db_id:
            st.session_state["eski_analiz_id"]   = eski["id"]
            st.session_state["eski_analiz_tarih"] = eski["created_at"]
            st.session_state["eski_potansiyel"]   = eski["potansiyel"]
        else:
            st.session_state.pop("eski_analiz_id", None)

        # Session state'e kaydet
        st.session_state["analiz_result"]     = result
        st.session_state["analiz_pdf"]        = pdf_bytes
        st.session_state["analiz_ad_soyad"]   = ad_soyad
        st.session_state["analiz_sure_str"]   = sure_str
        st.session_state["analiz_hatalar"]    = errors
        st.session_state["analiz_potansiyel"] = (potansiyel_sinif, potansiyel_label)
        st.session_state["analiz_db_id"]      = db_id

    except Exception as e:
        bar.empty()
        durum.empty()
        st.error(f"❌ {str(e)}")
        st.info("💡 Ollama'nın çalıştığını ve modellerin yüklü olduğunu kontrol edin.")

# ─── Sonuçları Göster ────────────────────────────────────────────
if "analiz_result" in st.session_state:
    result           = st.session_state["analiz_result"]
    pdf_bytes        = st.session_state["analiz_pdf"]
    ad_soyad         = st.session_state["analiz_ad_soyad"]
    sure_str         = st.session_state["analiz_sure_str"]
    errors           = st.session_state["analiz_hatalar"]
    pot_sinif, pot_l = st.session_state["analiz_potansiyel"]

    # Daha önce analiz edildi bildirimi
    if st.session_state.get("eski_analiz_id"):
        eski_tarih = st.session_state["eski_analiz_tarih"]
        eski_pot   = st.session_state.get("eski_potansiyel", "?")
        st.info(
            f"ℹ️ **{ad_soyad}** daha önce analiz edildi "
            f"({eski_tarih}, Sınıf {eski_pot}). "
            f"Eski sonuçlara **Geçmiş** sayfasından ulaşabilirsiniz."
        )

    # Ana sonuçlar
    render_analiz_sonuclari(result, sure_str, pot_sinif, pot_l, errors)

    # ─── PDF İndir ──────────────────────────────────────────
    st.divider()
    st.markdown("### 📤 Raporu İndir")
    aday_dosya = ad_soyad.replace(" ", "_")

    if pdf_bytes:
        st.download_button(
            label="📄 PDF Raporu İndir",
            data=pdf_bytes,
            file_name=f"mathworks_{aday_dosya}.pdf",
            mime="application/pdf",
            use_container_width=True,
            type="primary",
            key="pdf_indir_btn",
        )
    else:
        if st.button("🔄 PDF'i Yeniden Oluştur", key="pdf_yenile_btn"):
            try:
                yeni_pdf = pdf_rapor_olustur(result)
                st.session_state["analiz_pdf"] = yeni_pdf
                st.rerun()
            except Exception as e:
                st.error(f"PDF hatası: {e}")

    # ─── E-Posta ────────────────────────────────────────────
    st.markdown("### 📧 E-Posta ile Gönder")
    mail_adresi = st.text_input(
        "Alıcı adres(ler) — virgülle ayırın:",
        placeholder="ornek@sirket.com, ikinci@mail.com",
        key="mail_input_analiz"
    )
    if st.button("📤 E-Posta Gönder", key="mail_gonder_analiz"):
        if not mail_adresi.strip():
            st.warning("⚠️ Lütfen en az bir e-posta adresi girin.")
        elif not pdf_bytes:
            st.error("❌ PDF mevcut değil. Önce PDF'i oluşturun.")
        else:
            with st.spinner("📨 Gönderiliyor..."):
                basari, msg = send_pdf_email(
                    to_email=mail_adresi,
                    subject=f"FIGES MathWorks Öneri Raporu — {ad_soyad}",
                    body=(
                        f"Merhaba,\n\n{ad_soyad} için hazırlanan MathWorks "
                        f"ürün öneri raporu ekte sunulmuştur.\n\n"
                        f"İyi çalışmalar,\nFIGES CV Analyzer"
                    ),
                    pdf_bytes=pdf_bytes,
                    pdf_filename=f"mathworks_{aday_dosya}.pdf",
                )
            if basari:
                st.success(msg)
            else:
                st.error(msg)

render_footer()
