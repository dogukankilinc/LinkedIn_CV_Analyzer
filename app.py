import streamlit as st
import json
from core.input_handler import get_combined_text
from core.llm_client import analyze_cv_with_ollama, check_ollama_status
from core.response_parser import parse_and_validate
from core.pdf_rapor import pdf_rapor_olustur
from ui.components import render_candidate_card, render_toolbox_recommendations
from ui.charts import create_radar_chart

# ─── Sayfa Konfigürasyonu ───────────────────────────────────────
st.set_page_config(
    page_title="FIGES CV Analyzer | MathWorks",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "**FIGES CV Analyzer** — MathWorks Ürün Öneri Sistemi\n\nGeliştirici: Doğukan Mehmet KILINÇ\nhttps://www.linkedin.com/in/dgkilinc/"
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
</style>
""", unsafe_allow_html=True)

# ─── Başlık ─────────────────────────────────────────────────────
st.markdown("# 🔬 FIGES CV Analyzer")
st.markdown("**MathWorks Ürün Öneri Sistemi** — Dışarı veri çıkarmaz, tamamen cihaz üzerinde çalışır.")
st.divider()

# ─── Ollama Kontrol ─────────────────────────────────────────────
if not check_ollama_status():
    st.error("⚠️ Ollama servisine bağlanılamıyor. Lütfen Ollama uygulamasının arka planda açık olduğundan emin olun.")
    st.info("💡 **Çözüm:** Başlat menüsünden 'Ollama' uygulamasını açın, sağ alt köşede 🦙 simgesi belirmelidir.")
    st.stop()

# ─── Girdi Yöntemi Seçimi ───────────────────────────────────────
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
            "📂 CV dosyasını buraya sürükleyin veya seçin (PDF)",
            type=["pdf"],
            help="LinkedIn profilinizden 'Dışa Aktar → PDF Kaydet' seçeneğiyle indirilen dosyayı yükleyin."
        )

    if input_mode in ["📝 Sadece Metin Yapıştır", "📄+📝 PDF ve Metni Birlikte Kullan"]:
        manual_text = st.text_area(
            "✏️ Özgeçmiş metnini veya ek notlarınızı buraya yapıştırın",
            height=220,
            placeholder="CV metnini, proje açıklamalarını veya müşteri hakkındaki notlarınızı buraya yapıştırabilirsiniz..."
        )

# ─── Form Doğrulama ─────────────────────────────────────────────
can_analyze = False
if "PDF Yükle" in input_mode and uploaded_file is not None:
    can_analyze = True
elif "Metin Yapıştır" in input_mode and manual_text.strip() != "":
    can_analyze = True
elif "Birlikte Kullan" in input_mode and (uploaded_file is not None or manual_text.strip() != ""):
    can_analyze = True

if not can_analyze:
    st.info("ℹ️ Analiz başlatmak için lütfen bir PDF yükleyin veya metin girin.")

# ─── Analiz Butonu ──────────────────────────────────────────────
st.divider()
analiz_btn = st.button(
    "🚀 ANALİZİ BAŞLAT",
    type="primary",
    use_container_width=True,
    disabled=not can_analyze
)

if analiz_btn:
    durum_metni  = st.empty()
    ilerleme_bar = st.progress(0)

    def asama(yuzde: int, mesaj: str):
        ilerleme_bar.progress(yuzde)
        durum_metni.markdown(
            f'<div class="asama-kutusu">🔹 <b>{mesaj}</b> &nbsp;<span style="float:right;color:#0076A8;font-weight:bold">{yuzde}%</span></div>',
            unsafe_allow_html=True
        )

    try:
        asama(10, "📖 Dosyalar okunuyor ve birleştiriliyor...")
        cv_text = get_combined_text(uploaded_file, manual_text)

        asama(30, "📝 Analiz için metin hazırlanıyor...")

        asama(50, "🤖 Yapay zeka modeline gönderiliyor — bu adım en fazla süren kısımdır, lütfen bekleyin...")
        raw_response = analyze_cv_with_ollama(cv_text)

        asama(80, "🔍 Model yanıtı doğrulanıyor ve sonuçlar düzenleniyor...")
        result, errors = parse_and_validate(raw_response)

        asama(100, "✅ Analiz tamamlandı!")
        ilerleme_bar.empty()
        durum_metni.empty()

        # ─── Hata Kontrolü ──────────────────────────────────────
        if errors and not result:
            st.error(f"❌ Analiz tamamlanamadı: {', '.join(errors)}")
        else:
            if errors:
                st.warning(f"⚠️ Analiz tamamlandı, bazı uyarılar oluştu: {', '.join(errors)}")
            else:
                st.success("✅ Analiz başarıyla tamamlandı!")

            # ─── Sonuç Paneli ────────────────────────────────────
            c_left, c_right = st.columns([1, 1])
            with c_left:
                render_candidate_card(result.get("candidate_summary", {}))
            with c_right:
                scores_data = result.get("scores", {})
                st.plotly_chart(create_radar_chart(scores_data), use_container_width=True)

            # ─── Puan Çubukları ──────────────────────────────────
            st.divider()
            ai_p = scores_data.get('ai', {}).get('percentage', 0)
            sm_p = scores_data.get('system_modeling', {}).get('percentage', 0)
            es_p = scores_data.get('embedded_systems', {}).get('percentage', 0)

            st.markdown("##### 📊 Kategori Puanları")
            p1, p2, p3 = st.columns(3)
            with p1:
                st.markdown("**🤖 Yapay Zeka & Veri Bilimi**")
                st.progress(ai_p)
                st.markdown(f"**%{ai_p}**")
            with p2:
                st.markdown("**⚙️ Sistem Modelleme & Kontrol**")
                st.progress(sm_p)
                st.markdown(f"**%{sm_p}**")
            with p3:
                st.markdown("**🔧 Gömülü Sistemler & Kod Üretimi**")
                st.progress(es_p)
                st.markdown(f"**%{es_p}**")

            st.divider()

            # ─── Kategori Sekmeleri ──────────────────────────────
            tab_ai, tab_sm, tab_es = st.tabs([
                f"🤖 Yapay Zeka & Veri Bilimi ({ai_p}%)",
                f"⚙️ Sistem Modelleme & Kontrol ({sm_p}%)",
                f"🔧 Gömülü Sistemler & Kod Üretimi ({es_p}%)"
            ])
            recs = result.get("recommendations", {})
            with tab_ai:
                render_toolbox_recommendations(recs.get("ai", {}), include_pitch=True)
            with tab_sm:
                render_toolbox_recommendations(recs.get("system_modeling", {}), include_pitch=True)
            with tab_es:
                render_toolbox_recommendations(recs.get("embedded_systems", {}), include_pitch=True)

            # ─── Genel Değerlendirme ─────────────────────────────
            st.divider()
            genel = result.get('overall_assessment', '')
            if genel:
                st.info(f"💡 **Genel Değerlendirme:** {genel}")

            # ─── RAPOR DIŞA AKTARMA ──────────────────────────────
            st.divider()
            st.markdown("### 📤 Raporu Dışa Aktar")

            aday_adi = result.get('candidate_summary', {}).get('name', 'Bilinmeyen').replace(' ', '_')

            exp_col1, exp_col2 = st.columns(2)

            with exp_col1:
                # PDF İndir
                with st.spinner("PDF hazırlanıyor..."):
                    try:
                        pdf_bytes = pdf_rapor_olustur(result)
                        st.download_button(
                            label="📄 PDF Olarak İndir",
                            data=pdf_bytes,
                            file_name=f"cv_analiz_{aday_adi}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                    except Exception as pdf_err:
                        st.error(f"PDF oluşturulamadı: {pdf_err}")

            with exp_col2:
                # JSON İndir
                st.download_button(
                    label="🗂️ JSON Olarak İndir",
                    data=json.dumps(result, ensure_ascii=False, indent=2),
                    file_name=f"cv_analiz_{aday_adi}.json",
                    mime="application/json",
                    use_container_width=True
                )

    except Exception as e:
        ilerleme_bar.empty()
        durum_metni.empty()
        st.error(f"❌ Beklenmeyen bir hata oluştu: {str(e)}")
        st.info("💡 Ollama uygulamasının çalıştığından ve modelin yüklü olduğundan emin olun.")

# ─── Alt Bilgi (Footer) ──────────────────────────────────────────
st.markdown("""
<div class="custom-footer">
    🔬 <strong>FIGES CV Analyzer</strong> &nbsp;|&nbsp; MathWorks Ürün Öneri Sistemi &nbsp;|&nbsp;
    Geliştirici: <a href="https://www.linkedin.com/in/dgkilinc/" target="_blank">Doğukan Mehmet KILINÇ</a>
    &nbsp;|&nbsp; Tüm veriler yerel cihazda işlenir
</div>
""", unsafe_allow_html=True)
