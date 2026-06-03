import streamlit as st
import json
from dotenv import load_dotenv
from core.auth import require_login
from core.db import init_db, get_user_history, get_analysis_pdf
from core.ui_helpers import (
    apply_css, render_footer, render_topbar,
    hesapla_potansiyel, render_analiz_sonuclari,
    POTANSIYEL_RENK, POTANSIYEL_ETIKET
)
from core.pdf_rapor import pdf_rapor_olustur
from core.email_sender import send_pdf_email

load_dotenv()
init_db()

st.set_page_config(
    page_title="FIGES CV Analyzer — Geçmiş",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={"Get Help": None, "Report a bug": None, "About": None},
)

apply_css()
user = require_login()
render_topbar()

st.markdown("## 📋 Tarama Geçmişi")
st.markdown(f"*Son 10 analiz — {user['username']} hesabı*")
st.divider()

history = get_user_history(user["id"])

if not history:
    st.info("ℹ️ Henüz bir analiz yapılmamış. Analiz sayfasından başlayın.")
    if st.button("🔬 Analiz Sayfasına Git"):
        st.switch_page("pages/1_Analiz.py")
else:
    for kayit in history:
        ad_soyad  = kayit["ad_soyad"] or "Bilinmiyor"
        sektor    = kayit["sektor"] or "—"
        tarih     = kayit["created_at"]
        sure_str  = kayit["sure_str"] or "—"
        pot_sinif = kayit["potansiyel"] or "D"
        pot_label = POTANSIYEL_ETIKET.get(pot_sinif, pot_sinif)
        renk      = POTANSIYEL_RENK.get(pot_sinif, "#888")
        model     = kayit["model"] or "—"
        db_id     = kayit["id"]

        with st.expander(
            f"👤 **{ad_soyad}** &nbsp;|&nbsp; "
            f"{pot_label} — Sınıf **{pot_sinif}** &nbsp;|&nbsp; "
            f"{tarih}",
            expanded=False
        ):
            ic1, ic2, ic3 = st.columns(3)
            with ic1:
                st.markdown(f"**Sektör:** `{sektor}`")
            with ic2:
                st.markdown(f"**Model:** `{model}`")
            with ic3:
                st.markdown(f"**Süre:** `{sure_str}`")

            st.divider()

            # JSON'dan sonuçları göster
            try:
                result = json.loads(kayit["json_result"])
                pot_s, pot_l = hesapla_potansiyel(result.get("yetkinlik_puanlari", {}))
                render_analiz_sonuclari(result, sure_str, pot_s, pot_l, [])
            except Exception as e:
                st.warning(f"Sonuçlar görüntülenemiyor: {e}")

            st.divider()

            # PDF indir
            pdf_key = f"pdf_gecmis_{db_id}"
            if pdf_key not in st.session_state:
                # DB'den yükle
                pdf_bytes = get_analysis_pdf(db_id)
                if pdf_bytes:
                    st.session_state[pdf_key] = pdf_bytes

            pdf_bytes = st.session_state.get(pdf_key)

            col_pdf, col_mail = st.columns(2)
            with col_pdf:
                if pdf_bytes:
                    st.download_button(
                        label="📄 PDF İndir",
                        data=pdf_bytes,
                        file_name=f"mathworks_{ad_soyad.replace(' ', '_')}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                        key=f"dl_{db_id}",
                    )
                else:
                    if st.button("🔄 PDF Oluştur", key=f"pdf_olustur_{db_id}",
                                 use_container_width=True):
                        try:
                            result_j = json.loads(kayit["json_result"])
                            yeni_pdf = pdf_rapor_olustur(result_j)
                            st.session_state[pdf_key] = yeni_pdf
                            st.rerun()
                        except Exception as e:
                            st.error(f"PDF hatası: {e}")

            with col_mail:
                mail_key = f"mail_input_{db_id}"
                mail_adr = st.text_input(
                    "E-posta:", placeholder="ornek@sirket.com",
                    key=mail_key, label_visibility="collapsed"
                )
                if st.button("📤 Gönder", key=f"mail_btn_{db_id}", use_container_width=True):
                    if not mail_adr.strip():
                        st.warning("Adres girin.")
                    elif not pdf_bytes:
                        st.error("Önce PDF oluşturun.")
                    else:
                        with st.spinner("Gönderiliyor..."):
                            ok, msg = send_pdf_email(
                                to_email=mail_adr,
                                subject=f"FIGES MathWorks Öneri Raporu — {ad_soyad}",
                                body=(
                                    f"Merhaba,\n\n{ad_soyad} için hazırlanan "
                                    f"MathWorks öneri raporu ektedir.\n\n"
                                    f"İyi çalışmalar,\nFIGES CV Analyzer"
                                ),
                                pdf_bytes=pdf_bytes,
                                pdf_filename=f"mathworks_{ad_soyad.replace(' ', '_')}.pdf",
                            )
                        if ok:
                            st.success(msg)
                        else:
                            st.error(msg)

render_footer()
