from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
from datetime import datetime

# ─── Font Ayarları (Türkçe Karakter Desteği) ────────────────────
try:
    pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
    pdfmetrics.registerFont(TTFont('Arial-Bold', 'arialbd.ttf'))
    pdfmetrics.registerFont(TTFont('Arial-Italic', 'ariali.ttf'))
    FONT_NORMAL = 'Arial'
    FONT_BOLD   = 'Arial-Bold'
    FONT_ITALIC = 'Arial-Italic'
except Exception:
    FONT_NORMAL = 'Helvetica'
    FONT_BOLD   = 'Helvetica-Bold'
    FONT_ITALIC = 'Helvetica-Oblique'

# ─── Renk Paleti ────────────────────────────────────────────────
FIGES_MAVI    = colors.HexColor("#0076A8")
FIGES_KOYU    = colors.HexColor("#0f2537")
GRI_ARKAPLAN  = colors.HexColor("#f5f7fa")
TURUNCU_ACIK  = colors.HexColor("#fef3e2")
TURUNCU       = colors.HexColor("#e67e22")
YESIL_ACIK    = colors.HexColor("#eafaf1")
YESIL         = colors.HexColor("#27ae60")
MAVI_ACIK     = colors.HexColor("#ebf5fb")
BEYAZ         = colors.white
KARANLIK_YAZI = colors.HexColor("#1a2632")


def pdf_rapor_olustur(analiz_sonucu: dict) -> bytes:
    """
    MathWorks ürün öneri analizinden profesyonel A4 satış raporu oluşturur.
    Her öneri bloğu için tespit, toolbox'lar ve satış argümanı ayrı kutularda gösterilir.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2.5*cm, bottomMargin=3*cm,
        title="FIGES MathWorks Ürün Öneri Raporu",
        author="Doğukan Mehmet KILINÇ"
    )

    styles = getSampleStyleSheet()

    # Stiller
    baslik_stil = ParagraphStyle("Baslik", parent=styles["Title"],
        fontSize=20, textColor=FIGES_MAVI, spaceAfter=4, fontName=FONT_BOLD)

    bolum_stil = ParagraphStyle("Bolum", parent=styles["Heading2"],
        fontSize=13, textColor=FIGES_MAVI, spaceBefore=14, spaceAfter=6,
        fontName=FONT_BOLD)

    normal_stil = ParagraphStyle("Normal2", parent=styles["Normal"],
        fontSize=9.5, textColor=KARANLIK_YAZI, spaceAfter=3, leading=14,
        fontName=FONT_NORMAL)

    kucuk_stil = ParagraphStyle("Kucuk", parent=styles["Normal"],
        fontSize=8.5, textColor=colors.HexColor("#7f8c8d"), fontName=FONT_NORMAL)

    bulgu_stil = ParagraphStyle("Bulgu", parent=styles["Normal"],
        fontSize=9.5, textColor=colors.HexColor("#7d4e00"),
        fontName=FONT_ITALIC, leading=14, spaceAfter=4,
        backColor=TURUNCU_ACIK, leftIndent=6, borderPad=6)

    arguman_stil = ParagraphStyle("Arguman", parent=styles["Normal"],
        fontSize=10, textColor=colors.HexColor("#1a4731"),
        fontName=FONT_NORMAL, leading=15, spaceAfter=4,
        backColor=YESIL_ACIK, leftIndent=6, borderPad=8)

    toolbox_stil = ParagraphStyle("Toolbox", parent=styles["Normal"],
        fontSize=9.5, textColor=colors.HexColor("#1a365d"),
        fontName=FONT_BOLD, leading=14)

    tarih  = datetime.now().strftime("%d.%m.%Y %H:%M")
    hikaye = []

    # ─── BAŞLIK BLOĞU ──────────────────────────────────────────
    kisiler  = analiz_sonucu.get("kisisel_bilgiler", {})
    ad_soyad = kisiler.get("ad_soyad") or "Bilinmiyor"
    sektor   = kisiler.get("sektor_veya_uzmanlik_alani") or "—"

    baslik_tablo = Table([[
        Paragraph("🔬 FIGES MathWorks Ürün Öneri Raporu", baslik_stil),
        Paragraph(f"Oluşturulma: {tarih}\nModel: qwen2.5:14b (TR) · phi4 (EN)", kucuk_stil)
    ]], colWidths=["65%", "35%"])
    baslik_tablo.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), FIGES_KOYU),
        ("TEXTCOLOR",  (0, 0), (-1, -1), BEYAZ),
        ("PADDING",    (0, 0), (-1, -1), 14),
        ("VALIGN",     (0, 0), (-1, -1), "MIDDLE"),
    ]))
    hikaye.append(baslik_tablo)
    hikaye.append(Spacer(1, 0.5*cm))

    # ─── MÜŞTERİ PROFİLİ ───────────────────────────────────────
    hikaye.append(Paragraph("👤 Müşteri Profili", bolum_stil))
    hikaye.append(HRFlowable(width="100%", thickness=1.5, color=FIGES_MAVI, spaceAfter=6))

    profil_data = [
        ["Ad Soyad",               ad_soyad],
        ["Sektör / Uzmanlık Alanı", sektor],
    ]
    profil_tablo = Table(profil_data, colWidths=["35%", "65%"])
    profil_tablo.setStyle(TableStyle([
        ("FONTNAME",  (0, 0), (0, -1), FONT_BOLD),
        ("FONTNAME",  (1, 0), (1, -1), FONT_NORMAL),
        ("FONTSIZE",  (0, 0), (-1, -1), 10),
        ("TEXTCOLOR", (0, 0), (0, -1), FIGES_MAVI),
        ("TEXTCOLOR", (1, 0), (1, -1), KARANLIK_YAZI),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [GRI_ARKAPLAN, BEYAZ]),
        ("PADDING",   (0, 0), (-1, -1), 8),
        ("GRID",      (0, 0), (-1, -1), 0.3, colors.HexColor("#dce3ea")),
    ]))
    hikaye.append(profil_tablo)
    hikaye.append(Spacer(1, 0.5*cm))

    # ─── MÜHENDİSLİK YETKİNLİKLERİ ─────────────────────────────
    yetkinlikler = analiz_sonucu.get("mevcut_muhendislik_yetkinlikleri", [])
    if yetkinlikler:
        hikaye.append(Paragraph("🛠️ Müşteri Yetkinlikleri", bolum_stil))
        hikaye.append(HRFlowable(width="100%", thickness=1.5, color=FIGES_MAVI, spaceAfter=6))
        yetki_metni = "  •  ".join(yetkinlikler)
        hikaye.append(Paragraph(yetki_metni, normal_stil))
        hikaye.append(Spacer(1, 0.5*cm))

    # ─── MATHWORKS ÖNERİLERİ ────────────────────────────────────
    tavsiyeleri = analiz_sonucu.get("mathworks_urun_tavsiyeleri", [])
    hikaye.append(Paragraph(f"📦 Önerilen MathWorks Çözümleri  ({len(tavsiyeleri)} öneri)", bolum_stil))
    hikaye.append(HRFlowable(width="100%", thickness=1.5, color=FIGES_MAVI, spaceAfter=8))

    for i, tb in enumerate(tavsiyeleri, 1):
        ana_urun   = tb.get("onerilen_ana_urun", "MATLAB")
        toolboxlar = tb.get("onerilen_toolboxlar", [])
        bulgu      = tb.get("tespit_edilen_ihtiyac", "")
        arguman    = tb.get("satis_ve_kullanim_argumani", "")

        # Öneri başlığı
        hikaye.append(Paragraph(
            f"<b>#{i} — {ana_urun}</b>",
            ParagraphStyle("OneriBaslik", parent=styles["Normal"],
                fontSize=11, fontName=FONT_BOLD, textColor=FIGES_MAVI,
                spaceBefore=10, spaceAfter=4)
        ))

        # Tespit edilen ihtiyaç (turuncu kutu)
        hikaye.append(Paragraph(f"🔍 Tespit Edilen İhtiyaç: {bulgu}", bulgu_stil))

        # Önerilen Toolbox'lar (mavi tablo satırı)
        if toolboxlar:
            tb_metni = "   ".join([f"📦 {t}" for t in toolboxlar])
            toolbox_tablo = Table([[Paragraph(tb_metni, toolbox_stil)]],
                                  colWidths=["100%"])
            toolbox_tablo.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), MAVI_ACIK),
                ("PADDING",    (0, 0), (-1, -1), 8),
                ("BOX",        (0, 0), (-1, -1), 0.5, colors.HexColor("#2b6cb0")),
            ]))
            hikaye.append(toolbox_tablo)
            hikaye.append(Spacer(1, 0.15*cm))

        # Satış argümanı (yeşil kutu — öne çıkarılan alan)
        hikaye.append(Paragraph(f"💬 Satış Argümanı: {arguman}", arguman_stil))
        hikaye.append(HRFlowable(
            width="100%", thickness=0.4,
            color=colors.HexColor("#d5dde5"), spaceAfter=4
        ))

    # ─── FOOTER ─────────────────────────────────────────────────
    hikaye.append(Spacer(1, 0.8*cm))
    hikaye.append(HRFlowable(width="100%", thickness=0.8, color=FIGES_MAVI))
    footer = Table([[
        "Geliştirici: Doğukan Mehmet KILINÇ  |  linkedin.com/in/dgkilinc",
        f"FIGES MathWorks CV Analyzer  |  {tarih}"
    ]], colWidths=["60%", "40%"])
    footer.setStyle(TableStyle([
        ("FONTNAME",   (0, 0), (-1, -1), FONT_NORMAL),
        ("FONTSIZE",   (0, 0), (-1, -1), 8),
        ("TEXTCOLOR",  (0, 0), (-1, -1), colors.HexColor("#7f8c8d")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("ALIGN",      (1, 0), (1, 0), "RIGHT"),
    ]))
    hikaye.append(footer)

    doc.build(hikaye)
    buffer.seek(0)
    return buffer.read()
