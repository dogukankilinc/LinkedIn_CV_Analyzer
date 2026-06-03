import streamlit as st

# ─── Renk Paleti ────────────────────────────────────────────────
POTANSIYEL_RENK = {
    "A": "#27ae60",
    "B": "#f39c12",
    "C": "#e67e22",
    "D": "#e74c3c",
}
POTANSIYEL_ETIKET = {
    "A": "🟢 Yüksek Potansiyel",
    "B": "🟡 Orta Potansiyel",
    "C": "🟠 Düşük Potansiyel",
    "D": "🔴 Potansiyel Yok",
}

FIGES_CSS = """
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
    .potansiyel-badge {
        display: inline-block; border-radius: 20px;
        padding: 6px 20px; font-size: 15px; font-weight: 700;
        margin-bottom: 12px;
    }
    .gecmis-kart {
        background: #0f2537; border: 1px solid #1e4060;
        border-radius: 10px; padding: 14px 18px; margin-bottom: 10px;
    }
    .login-card {
        background: #0f2537; border: 1px solid #1e4060;
        border-radius: 16px; padding: 36px 40px; max-width: 420px;
        margin: 40px auto;
    }
</style>
"""


def apply_css():
    st.markdown(FIGES_CSS, unsafe_allow_html=True)


def render_footer():
    st.markdown("""
<div class="custom-footer">
    🔬 <strong>FIGES MathWorks CV Analyzer</strong> &nbsp;|&nbsp;
    🇹🇷 qwen2.5:14b &nbsp;·&nbsp; 🇬🇧 phi4 &nbsp;·&nbsp; Çıktı: Türkçe &nbsp;|&nbsp;
    Geliştirici: <a href="https://www.linkedin.com/in/dgkilinc/" target="_blank">Doğukan Mehmet KILINÇ</a>
    &nbsp;|&nbsp; Tüm veriler yerel cihazda işlenir
</div>
""", unsafe_allow_html=True)


def render_topbar():
    """Üst çubuk: başlık + kullanıcı adı + çıkış."""
    user = st.session_state.get("user", {})
    username = user.get("username", "")
    admin_badge = " 👑" if user.get("is_admin") else ""

    col1, col2 = st.columns([5, 1])
    with col1:
        st.markdown("# 🔬 FIGES MathWorks CV Analyzer")
    with col2:
        if username:
            st.markdown(
                f"<div style='text-align:right;padding-top:14px;"
                f"color:#63b3ed;font-weight:bold'>👤 {username}{admin_badge}</div>",
                unsafe_allow_html=True,
            )
            if st.button("Çıkış Yap", key="topbar_logout"):
                st.session_state.clear()
                st.rerun()


def hesapla_potansiyel(puanlar: dict) -> tuple[str, str]:
    """(sınıf, etiket) döner."""
    ai = int(puanlar.get("yapay_zeka_ve_veri") or 0)
    gs = int(puanlar.get("gomulu_sistemler") or 0)
    sk = int(puanlar.get("sistem_ve_kontrol_modelleme") or 0)
    ort = (ai + gs + sk) / 3
    if ort >= 70:
        return "A", POTANSIYEL_ETIKET["A"]
    elif ort >= 50:
        return "B", POTANSIYEL_ETIKET["B"]
    elif ort >= 30:
        return "C", POTANSIYEL_ETIKET["C"]
    else:
        return "D", POTANSIYEL_ETIKET["D"]


def render_analiz_sonuclari(result: dict, sure_str: str, potansiyel_sinif: str,
                             potansiyel_label: str, errors: list):
    """Analiz sonuçlarını (profil, puanlar, öneriler) render eder."""
    if errors:
        st.warning(f"⚠️ {', '.join(errors)}\n\n(Süre: {sure_str})")
    else:
        renk = POTANSIYEL_RENK[potansiyel_sinif]
        st.success(f"✅ Analiz başarıyla tamamlandı! ⏱️ {sure_str}")

    # Müşteri profili
    kisiler = result.get("kisisel_bilgiler", {})
    ad_soyad = kisiler.get("ad_soyad") or "Bilinmiyor"
    sektor   = kisiler.get("sektor_veya_uzmanlik_alani") or "—"

    st.markdown(f"## 👤 {ad_soyad}")
    renk = POTANSIYEL_RENK[potansiyel_sinif]
    st.markdown(
        f'<span class="potansiyel-badge" style="background:{renk}22;'
        f'color:{renk};border:1px solid {renk}">'
        f'  {potansiyel_label} — Sınıf {potansiyel_sinif}</span>',
        unsafe_allow_html=True,
    )
    st.markdown(f"**Sektör / Uzmanlık Alanı:** `{sektor}`")
    st.divider()

    # Yetkinlik puanları
    puanlar = result.get("yetkinlik_puanlari", {})
    ai_puan = int(puanlar.get("yapay_zeka_ve_veri") or 0)
    gs_puan = int(puanlar.get("gomulu_sistemler") or 0)
    sk_puan = int(puanlar.get("sistem_ve_kontrol_modelleme") or 0)

    st.markdown("### 📊 Yetkinlik Puanları")
    p1, p2, p3 = st.columns(3)
    with p1:
        st.markdown(
            f'<div class="puan-kutu"><div class="puan-sayi">{ai_puan}</div>'
            f'<div class="puan-etiket">🤖 Yapay Zeka & Veri Bilimi</div></div>',
            unsafe_allow_html=True)
        st.progress(ai_puan)
    with p2:
        st.markdown(
            f'<div class="puan-kutu"><div class="puan-sayi">{gs_puan}</div>'
            f'<div class="puan-etiket">🔧 Gömülü Sistemler</div></div>',
            unsafe_allow_html=True)
        st.progress(gs_puan)
    with p3:
        st.markdown(
            f'<div class="puan-kutu"><div class="puan-sayi">{sk_puan}</div>'
            f'<div class="puan-etiket">⚙️ Sistem & Kontrol Modelleme</div></div>',
            unsafe_allow_html=True)
        st.progress(sk_puan)

    st.divider()

    # Yetkinlik badge'leri
    yetkinlikler = result.get("mevcut_muhendislik_yetkinlikleri", [])
    if yetkinlikler:
        st.markdown("### 🛠️ Müşteri Yetkinlikleri")
        badges = " ".join([f'<span class="beceri-badge">{y}</span>' for y in yetkinlikler])
        st.markdown(badges, unsafe_allow_html=True)
        st.divider()

    # MathWorks önerileri
    tavsiyeleri = result.get("mathworks_urun_tavsiyeleri", [])
    st.markdown(f"### 📦 Önerilen MathWorks Çözümleri  `({len(tavsiyeleri)} öneri)`")
    for i, tb in enumerate(tavsiyeleri, 1):
        ana_urun   = tb.get("onerilen_ana_urun", "MATLAB")
        toolboxlar = tb.get("onerilen_toolboxlar", [])
        bulgu      = tb.get("tespit_edilen_ihtiyac", "")
        kaynak     = tb.get("kaynak_bolum", "")
        arguman    = tb.get("satis_ve_kullanim_argumani", "")
        ipuclari   = tb.get("satis_stratejisi_ipuclari", [])

        toolbox_badges = " ".join(
            [f'<span class="toolbox-badge">📦 {t}</span>' for t in toolboxlar])
        ipucu_html = "".join(
            [f'<div class="ipucu-kutusu">💡 {ip}</div>' for ip in ipuclari])

        st.markdown(f"""
<div class="tavsiye-kart">
  <h4>#{i} — <span class="ana-urun-etiket">{ana_urun}</span></h4>
  <div class="bulgu-kutusu">🔍 <b>Tespit Edilen İhtiyaç:</b> {bulgu}</div>
  <div class="kaynak-kutusu">📂 <b>CV'deki Kaynak:</b> {kaynak}</div>
  <div style="margin-bottom:10px">{toolbox_badges}</div>
  <div class="arguman-kutusu">💬 <b>Satış Argümanı:</b> {arguman}</div>
  {ipucu_html}
</div>""", unsafe_allow_html=True)
