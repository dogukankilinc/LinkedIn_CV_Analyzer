import core.md5_patch
import streamlit as st
import os
from dotenv import load_dotenv
from core.db import init_db
from core.auth import ensure_admin, login, register
from core.ui_helpers import apply_css, render_footer

load_dotenv()
init_db()
ensure_admin()

st.set_page_config(
    page_title="FIGES MathWorks CV Analyzer — Giriş",
    page_icon="🔬",
    layout="centered",
    initial_sidebar_state="collapsed",
    menu_items={"Get Help": None, "Report a bug": None, "About": None},
)

apply_css()

# Zaten giriş yapılmışsa analiz sayfasına yönlendir
if st.session_state.get("user"):
    st.switch_page("pages/1_Analiz.py")

# ─── Logo / Başlık ────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:32px 0 16px 0">
  <div style="font-size:48px">🔬</div>
  <h1 style="color:#63b3ed;margin:8px 0 4px 0;font-size:26px">
    FIGES MathWorks CV Analyzer
  </h1>
  <p style="color:#7fb3d3;font-size:14px;margin:0">
    Yerel LLM · Ollama · Tamamen Gizli
  </p>
</div>
""", unsafe_allow_html=True)

# ─── Sekmeli Giriş / Kayıt ────────────────────────────────────────
tab_giris, tab_kayit = st.tabs(["🔑 Giriş Yap", "📝 Hesap Oluştur"])

with tab_giris:
    st.markdown("<br>", unsafe_allow_html=True)
    kullanici_adi = st.text_input(
        "Kullanıcı Adı", placeholder="kullanici_adi", key="login_user"
    )
    sifre = st.text_input(
        "Şifre", type="password", placeholder="••••••••", key="login_pass"
    )
    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🔑 Giriş Yap", use_container_width=True, type="primary", key="btn_login"):
        if not kullanici_adi or not sifre:
            st.warning("Lütfen tüm alanları doldurun.")
        else:
            ok, mesaj, user = login(kullanici_adi, sifre)
            if ok:
                st.session_state["user"] = user
                st.success(f"✅ Hoş geldiniz, **{user['username']}**!")
                st.switch_page("pages/1_Analiz.py")
            else:
                st.error(f"❌ {mesaj}")

with tab_kayit:
    st.markdown("<br>", unsafe_allow_html=True)
    yeni_kullanici = st.text_input(
        "Kullanıcı Adı (min. 3 karakter)",
        placeholder="yeni_kullanici",
        key="reg_user"
    )
    yeni_sifre = st.text_input(
        "Şifre (min. 4 karakter)",
        type="password",
        placeholder="••••••••",
        key="reg_pass"
    )
    yeni_sifre2 = st.text_input(
        "Şifre (tekrar)",
        type="password",
        placeholder="••••••••",
        key="reg_pass2"
    )
    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("📝 Hesap Oluştur", use_container_width=True, type="primary", key="btn_register"):
        if not yeni_kullanici or not yeni_sifre:
            st.warning("Lütfen tüm alanları doldurun.")
        elif yeni_sifre != yeni_sifre2:
            st.error("❌ Şifreler eşleşmiyor.")
        else:
            ok, mesaj = register(yeni_kullanici, yeni_sifre)
            if ok:
                st.success(f"✅ {mesaj} Şimdi giriş yapabilirsiniz.")
            else:
                st.error(f"❌ {mesaj}")

render_footer()
