from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
import io
from datetime import datetime

# ─── Renk Paleti ───────────────────────────────────────────────
FIGES_MAVI   = colors.HexColor("#0076A8")
FIGES_KOYU   = colors.HexColor("#0f2537")
ACIK_MAVI    = colors.HexColor("#e8f4fb")
GRI_ARKAPLAN = colors.HexColor("#f5f7fa")
YESIL        = colors.HexColor("#27ae60")
TURUNCU      = colors.HexColor("#e67e22")
KIRMIZI      = colors.HexColor("#e74c3c")
BEYAZ        = colors.white
KARANLIK_YAZI = colors.HexColor("#1a2632")

def guvence_rengi(guven: str):
    if guven in ("Yuksek", "Yüksek"):
        return YESIL
    elif guven == "Orta":
        return TURUNCU
    return KIRMIZI

def pdf_rapor_olustur(analiz_sonucu: dict) -> bytes:
    """
    Analiz sonucundan profesyonel bir PDF raporu oluşturur.
    Bytes olarak döndürür — Streamlit download_button ile kullanılabilir.
    """
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2.5*cm,
        bottomMargin=3*cm,
        title="FIGES CV Analiz Raporu",
        author="Doğukan Mehmet KILINÇ"
    )

    styles = getSampleStyleSheet()

    # ─── Özel Stiller ──────────────────────────────────────────
    baslik_stil = ParagraphStyle(
        "Baslik", parent=styles["Title"],
        fontSize=22, textColor=FIGES_MAVI,
        spaceAfter=4, fontName="Helvetica-Bold"
    )
    alt_baslik_stil = ParagraphStyle(
        "AltBaslik", parent=styles["Normal"],
        fontSize=10, textColor=colors.white,
        fontName="Helvetica"
    )
    bolum_baslik_stil = ParagraphStyle(
        "BolumBaslik", parent=styles["Heading2"],
        fontSize=13, textColor=FIGES_MAVI,
        spaceBefore=14, spaceAfter=4,
        fontName="Helvetica-Bold",
        borderPad=4
    )
    kart_baslik_stil = ParagraphStyle(
        "KartBaslik", parent=styles["Normal"],
        fontSize=11, textColor=KARANLIK_YAZI,
        fontName="Helvetica-Bold",
        spaceAfter=2
    )
    normal_stil = ParagraphStyle(
        "Normal2", parent=styles["Normal"],
        fontSize=9.5, textColor=KARANLIK_YAZI,
        spaceAfter=3, leading=14,
        fontName="Helvetica"
    )
    kanit_stil = ParagraphStyle(
        "Kanit", parent=styles["Normal"],
        fontSize=9, textColor=colors.HexColor("#34495e"),
        fontName="Helvetica-Oblique",
        leftIndent=12, spaceAfter=4, leading=13
    )
    kucuk_stil = ParagraphStyle(
        "Kucuk", parent=styles["Normal"],
        fontSize=8.5, textColor=colors.HexColor("#7f8c8d"),
        fontName="Helvetica"
    )
    pitch_stil = ParagraphStyle(
        "Pitch", parent=styles["Normal"],
        fontSize=9.5, textColor=colors.HexColor("#1a5276"),
        fontName="Helvetica",
        backColor=colors.HexColor("#d6eaf8"),
        borderPad=8, leftIndent=8, leading=14, spaceAfter=6
    )

    hikaye = []  # PDF içeriği buraya eklenir

    # ─── BAŞLIK BLOĞU ──────────────────────────────────────────
    tarih = datetime.now().strftime("%d.%m.%Y %H:%M")
    aday  = analiz_sonucu.get("candidate_summary", {})
    meta  = analiz_sonucu.get("metadata", {})

    baslik_tablo = Table(
        [[
            Paragraph("🔬 FIGES CV Analyzer", baslik_stil),
            Paragraph(f"MathWorks Ürün Öneri Raporu\nOluşturulma: {tarih}", kucuk_stil)
        ]],
        colWidths=["65%", "35%"]
    )
    baslik_tablo.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, -1), FIGES_KOYU),
        ("TEXTCOLOR",    (0, 0), (-1, -1), BEYAZ),
        ("PADDING",      (0, 0), (-1, -1), 12),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ("ROUNDEDCORNERS", [6]),
    ]))
    hikaye.append(baslik_tablo)
    hikaye.append(Spacer(1, 0.4*cm))

    # ─── ADAY ÖZET KARTI ────────────────────────────────────────
    hikaye.append(Paragraph("👤 Aday Özeti", bolum_baslik_stil))
    hikaye.append(HRFlowable(width="100%", thickness=1.5, color=FIGES_MAVI, spaceAfter=6))

    ozet_data = [
        ["Ad Soyad",            aday.get("name", "Belirtilmemiş")],
        ["Güncel Pozisyon",     aday.get("current_position", "-")],
        ["Şirket",              aday.get("current_company", "-")],
        ["Deneyim",             f"~{aday.get('total_experience_years', '?')} yıl"],
        ["Eğitim",              f"{aday.get('education', {}).get('level', '-')} — {aday.get('education', {}).get('field', '-')}"],
        ["Sektör",              ", ".join(aday.get("sectors", ["-"]))],
        ["MATLAB Deneyimi",     aday.get("matlab_experience", "Belirsiz")],
        ["Öne Çıkan Beceriler", " • ".join(aday.get("top_skills", ["-"]))],
    ]
    ozet_tablo = Table(ozet_data, colWidths=["35%", "65%"])
    ozet_tablo.setStyle(TableStyle([
        ("FONTNAME",    (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME",    (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE",    (0, 0), (-1, -1), 9.5),
        ("TEXTCOLOR",   (0, 0), (0, -1), FIGES_MAVI),
        ("TEXTCOLOR",   (1, 0), (1, -1), KARANLIK_YAZI),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [GRI_ARKAPLAN, BEYAZ]),
        ("PADDING",     (0, 0), (-1, -1), 7),
        ("GRID",        (0, 0), (-1, -1), 0.3, colors.HexColor("#dce3ea")),
    ]))
    hikaye.append(ozet_tablo)
    hikaye.append(Spacer(1, 0.5*cm))

    # ─── KATEGORİ PUANLARI ──────────────────────────────────────
    hikaye.append(Paragraph("📊 Kategori Puanları", bolum_baslik_stil))
    hikaye.append(HRFlowable(width="100%", thickness=1.5, color=FIGES_MAVI, spaceAfter=6))

    scores = analiz_sonucu.get("scores", {})
    kategoriler = [
        ("ai",              "🤖 Yapay Zeka & Veri Bilimi"),
        ("system_modeling", "⚙️ Sistem Modelleme & Kontrol"),
        ("embedded_systems","🔧 Gömülü Sistemler & Kod Üretimi"),
    ]
    puan_data = [["Kategori", "Puan", "Gerekçe"]]
    for key, label in kategoriler:
        s = scores.get(key, {})
        puan = s.get("percentage", 0)
        aciklama = s.get("rationale", "-")
        puan_data.append([label, f"%{puan}", Paragraph(aciklama, kucuk_stil)])

    puan_tablo = Table(puan_data, colWidths=["32%", "10%", "58%"])
    puan_tablo.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (-1, 0), FIGES_MAVI),
        ("TEXTCOLOR",   (0, 0), (-1, 0), BEYAZ),
        ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1, -1), 9.5),
        ("FONTNAME",    (1, 1), (1, -1), "Helvetica-Bold"),
        ("TEXTCOLOR",   (1, 1), (1, -1), FIGES_MAVI),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [GRI_ARKAPLAN, BEYAZ]),
        ("PADDING",     (0, 0), (-1, -1), 8),
        ("GRID",        (0, 0), (-1, -1), 0.3, colors.HexColor("#dce3ea")),
        ("ALIGN",       (1, 0), (1, -1), "CENTER"),
        ("VALIGN",      (0, 0), (-1, -1), "TOP"),
    ]))
    hikaye.append(puan_tablo)
    hikaye.append(Spacer(1, 0.5*cm))

    # ─── TOOLBOX ÖNERİLERİ ──────────────────────────────────────
    hikaye.append(Paragraph("📦 MathWorks Toolbox Önerileri", bolum_baslik_stil))
    hikaye.append(HRFlowable(width="100%", thickness=1.5, color=FIGES_MAVI, spaceAfter=8))

    recs = analiz_sonucu.get("recommendations", {})
    kategori_ikon = {
        "ai": "🤖 Yapay Zeka & Veri Bilimi",
        "system_modeling": "⚙️ Sistem Modelleme & Kontrol",
        "embedded_systems": "🔧 Gömülü Sistemler & Kod Üretimi"
    }

    for cat_key, cat_label in kategori_ikon.items():
        cat_data = recs.get(cat_key, {})
        toolboxes = cat_data.get("toolboxes", [])
        pitch     = cat_data.get("sales_pitch", "")
        puan_val  = scores.get(cat_key, {}).get("percentage", 0)

        if puan_val == 0:
            continue

        # Kategori başlığı
        hikaye.append(Paragraph(f"{cat_label}  —  %{puan_val}", kart_baslik_stil))

        if pitch:
            hikaye.append(Paragraph(f"💬 Görüşme Önerisi: {pitch}", pitch_stil))

        for tb in toolboxes:
            guven = tb.get("confidence", "Belirsiz")
            guven_renk = guvence_rengi(guven)
            tb_baslik = f"{tb.get('rank', '')}. {tb.get('name', '')}   [{guven}]"
            hikaye.append(Paragraph(tb_baslik, ParagraphStyle(
                "TBBaslik",
                fontSize=10, textColor=FIGES_MAVI,
                fontName="Helvetica-Bold", spaceBefore=8, spaceAfter=2
            )))
            hikaye.append(Paragraph(f"<b>Neden Önerildi:</b> {tb.get('rationale', '')}", normal_stil))
            kanit_metni = tb.get("evidence", {}).get("original_text", "")
            kaynak      = tb.get("evidence", {}).get("source_section", "")
            if kanit_metni:
                hikaye.append(Paragraph(f"📍 Kanıt ({kaynak}): \"{kanit_metni}\"", kanit_stil))

        hikaye.append(Spacer(1, 0.3*cm))
        hikaye.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#d5dde5"), spaceAfter=4))

    # ─── GENEL DEĞERLENDİRME ────────────────────────────────────
    genel = analiz_sonucu.get("overall_assessment", "")
    if genel:
        hikaye.append(Spacer(1, 0.3*cm))
        hikaye.append(Paragraph("💡 Genel Değerlendirme", bolum_baslik_stil))
        hikaye.append(HRFlowable(width="100%", thickness=1.5, color=FIGES_MAVI, spaceAfter=6))
        hikaye.append(Paragraph(genel, normal_stil))

    # ─── FOOTER ─────────────────────────────────────────────────
    hikaye.append(Spacer(1, 0.8*cm))
    hikaye.append(HRFlowable(width="100%", thickness=0.8, color=FIGES_MAVI))
    footer_tablo = Table(
        [["Geliştirici: Doğukan Mehmet KILINÇ  |  linkedin.com/in/dgkilinc",
          f"FIGES CV Analyzer  |  {tarih}"]],
        colWidths=["60%", "40%"]
    )
    footer_tablo.setStyle(TableStyle([
        ("FONTNAME",  (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE",  (0, 0), (-1, -1), 8),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#7f8c8d")),
        ("TOPPADDING",(0, 0), (-1, -1), 4),
        ("ALIGN",     (1, 0), (1, 0),  "RIGHT"),
    ]))
    hikaye.append(footer_tablo)

    doc.build(hikaye)
    buffer.seek(0)
    return buffer.read()
