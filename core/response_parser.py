import json


def parse_and_validate(raw_response: str) -> tuple[dict, list[str]]:
    """
    qwen2.5:72b modelinden gelen yanıtı parse eder ve doğrular.
    extra_body={"format":"json"} ile saf JSON beklenir, yine de temizlik yapılır.
    """
    errors = []

    # ─── 1. JSON Parse ──────────────────────────────────────────
    try:
        cleaned = raw_response.strip()

        # Olası markdown sarmalayıcıları temizle
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        # JSON bloğunu bul (model bazen önüne metin ekleyebilir)
        if not cleaned.startswith("{"):
            start = cleaned.find("{")
            if start != -1:
                depth, end = 0, start
                for i, ch in enumerate(cleaned[start:], start):
                    if ch == "{":
                        depth += 1
                    elif ch == "}":
                        depth -= 1
                        if depth == 0:
                            end = i
                            break
                cleaned = cleaned[start:end + 1]

        data = json.loads(cleaned)

    except json.JSONDecodeError as e:
        return {}, [f"JSON Parse Hatası: {str(e)} — Model geçerli bir JSON döndürmedi."]

    # ─── 2. Alan Garantileri ────────────────────────────────────
    try:
        # kisisel_bilgiler
        if not isinstance(data.get("kisisel_bilgiler"), dict):
            data["kisisel_bilgiler"] = {
                "ad_soyad": None,
                "sektor_veya_uzmanlik_alani": None
            }

        # mevcut_muhendislik_yetkinlikleri — liste olmalı
        if not isinstance(data.get("mevcut_muhendislik_yetkinlikleri"), list):
            data["mevcut_muhendislik_yetkinlikleri"] = []

        # mathworks_urun_tavsiyeleri — liste olmalı, her eleman dict
        tavsiyeleri = data.get("mathworks_urun_tavsiyeleri", [])
        if not isinstance(tavsiyeleri, list):
            tavsiyeleri = []

        temiz_tavsiyeleri = []
        for i, tb in enumerate(tavsiyeleri):
            if not isinstance(tb, dict):
                continue
            # zorunlu alanlar garantisi
            temiz = {
                "tespit_edilen_ihtiyac":   tb.get("tespit_edilen_ihtiyac") or "",
                "onerilen_ana_urun":       tb.get("onerilen_ana_urun") or "MATLAB",
                "onerilen_toolboxlar":     tb.get("onerilen_toolboxlar") if isinstance(tb.get("onerilen_toolboxlar"), list) else [],
                "satis_ve_kullanim_argumani": tb.get("satis_ve_kullanim_argumani") or "",
            }
            temiz_tavsiyeleri.append(temiz)

        data["mathworks_urun_tavsiyeleri"] = temiz_tavsiyeleri

    except Exception as e:
        errors.append(f"Alan doğrulama hatası: {str(e)}")

    return data, errors
