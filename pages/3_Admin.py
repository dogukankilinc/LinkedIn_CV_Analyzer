import streamlit as st
from dotenv import load_dotenv
from core.auth import require_login, is_admin, hash_password_public
from core.db import init_db, get_all_users, get_all_analyses, update_user_password, delete_user
from core.ui_helpers import apply_css, render_footer, render_topbar, POTANSIYEL_ETIKET

load_dotenv()
init_db()

st.set_page_config(
    page_title="FIGES CV Analyzer — Admin",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={"Get Help": None, "Report a bug": None, "About": None},
)

apply_css()
user = require_login()

if not is_admin():
    st.error("⛔ Bu sayfa yalnızca admin hesabına açıktır.")
    st.stop()

render_topbar()
st.markdown("## 👑 Admin Paneli")
st.divider()

tab_kullanici, tab_analizler = st.tabs(["👥 Kullanıcılar", "📊 Tüm Analizler"])

# ─── Kullanıcılar ────────────────────────────────────────────────
with tab_kullanici:
    kullanicilar = get_all_users()
    st.markdown(f"**Toplam {len(kullanicilar)} kullanıcı**")
    st.divider()

    for u in kullanicilar:
        uid         = u["id"]
        uname       = u["username"]
        admin_flag  = " 👑 Admin" if u["is_admin"] else ""
        tarih       = u["created_at"]
        analiz_say  = u["analiz_sayisi"]

        with st.expander(
            f"👤 **{uname}**{admin_flag} &nbsp;|&nbsp; "
            f"{analiz_say} analiz &nbsp;|&nbsp; Kayıt: {tarih}"
        ):
            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"- **ID:** `{uid}`")
                st.markdown(f"- **Kullanıcı adı:** `{uname}`")
                st.markdown(f"- **Admin:** `{'Evet' if u['is_admin'] else 'Hayır'}`")
                st.markdown(f"- **Kayıt tarihi:** `{tarih}`")
                st.markdown(f"- **Toplam analiz:** `{analiz_say}`")

            with col2:
                st.markdown("**🔑 Şifre Sıfırla:**")
                yeni_sifre = st.text_input(
                    "Yeni şifre", key=f"new_pass_{uid}",
                    type="password", placeholder="min. 4 karakter"
                )
                if st.button("Şifreyi Güncelle", key=f"update_pass_{uid}"):
                    if len(yeni_sifre) < 4:
                        st.warning("Şifre en az 4 karakter olmalı.")
                    else:
                        update_user_password(uid, hash_password_public(yeni_sifre))
                        st.success(f"✅ {uname} şifresi güncellendi.")

                st.markdown("---")
                if uname != "dogukan":
                    if st.button(
                        f"🗑️ {uname} Hesabını Sil",
                        key=f"del_user_{uid}",
                        type="secondary"
                    ):
                        delete_user(uid)
                        st.success(f"✅ {uname} silindi.")
                        st.rerun()
                else:
                    st.caption("⚠️ Admin hesabı silinemez.")

# ─── Tüm Analizler ───────────────────────────────────────────────
with tab_analizler:
    analizler = get_all_analyses()
    st.markdown(f"**Toplam {len(analizler)} analiz kaydı**")
    st.divider()

    if not analizler:
        st.info("Henüz analiz yok.")
    else:
        # Tablo başlığı
        hcols = st.columns([1.5, 2, 2, 1.5, 1.5, 1.5, 1.5])
        for col, baslik in zip(hcols, [
            "Kullanıcı", "Ad Soyad", "Sektör", "Model", "Sınıf", "Süre", "Tarih"
        ]):
            col.markdown(f"**{baslik}**")
        st.markdown("---")

        for a in analizler:
            pot_sinif = a["potansiyel"] or "?"
            pot_label = POTANSIYEL_ETIKET.get(pot_sinif, pot_sinif)
            row = st.columns([1.5, 2, 2, 1.5, 1.5, 1.5, 1.5])
            row[0].write(a["username"])
            row[1].write(a["ad_soyad"] or "—")
            row[2].write(a["sektor"] or "—")
            row[3].write(a["model"] or "—")
            row[4].write(f"{pot_sinif} — {pot_label.split()[0]}")
            row[5].write(a["sure_str"] or "—")
            row[6].write(a["created_at"])

render_footer()
