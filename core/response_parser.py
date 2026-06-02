import json


def parse_and_validate(raw_response: str) -> tuple[dict, list[str]]:
    """
    qwen2.5:14b / phi4 modelinden gelen yanıtı parse eder ve doğrular.
    extra_body={"format":"json"} ile saf JSON beklenir, yine de temizlik yapılır.
    """
    errors = []

    # ─── 1. JSON Parse ──────────────────────────────────────────
    try:
        cleaned = raw_response.strip()

        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

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
            data["kisisel_bilgiler"] = {"ad_soyad": None, "sektor_veya_uzmanlik_alani": None}

        # mevcut_muhendislik_yetkinlikleri
        if not isinstance(data.get("mevcut_muhendislik_yetkinlikleri"), list):
            data["mevcut_muhendislik_yetkinlikleri"] = []

        # yetkinlik_puanlari — yeni alan
        puanlar = data.get("yetkinlik_puanlari", {})
        if not isinstance(puanlar, dict):
            puanlar = {}

        def _guvenceli_puan(key: str) -> int:
            try:
                val = int(puanlar.get(key, 0) or 0)
                return max(0, min(100, val))   # 0-100 aralığında zorla
            except (ValueError, TypeError):
                return 0

        data["yetkinlik_puanlari"] = {
            "yapay_zeka_ve_veri":          _guvenceli_puan("yapay_zeka_ve_veri"),
            "gomulu_sistemler":             _guvenceli_puan("gomulu_sistemler"),
            "sistem_ve_kontrol_modelleme":  _guvenceli_puan("sistem_ve_kontrol_modelleme"),
        }

        # mathworks_urun_tavsiyeleri
        tavsiyeleri = data.get("mathworks_urun_tavsiyeleri", [])
        if not isinstance(tavsiyeleri, list):
            tavsiyeleri = []

        temiz = []
        for tb in tavsiyeleri:
            if not isinstance(tb, dict):
                continue
            temiz.append({
                "tespit_edilen_ihtiyac":      tb.get("tespit_edilen_ihtiyac") or "",
                "kaynak_bolum":               tb.get("kaynak_bolum") or "Belirtilmemiş",
                "onerilen_ana_urun":          tb.get("onerilen_ana_urun") or "MATLAB",
                "onerilen_toolboxlar":        tb.get("onerilen_toolboxlar")
                                              if isinstance(tb.get("onerilen_toolboxlar"), list) else [],
                "satis_ve_kullanim_argumani": tb.get("satis_ve_kullanim_argumani") or "",
                "satis_stratejisi_ipuclari":  tb.get("satis_stratejisi_ipuclari")
                                              if isinstance(tb.get("satis_stratejisi_ipuclari"), list) else [],
            })

        data["mathworks_urun_tavsiyeleri"] = temiz

    except Exception as e:
        errors.append(f"Alan doğrulama hatası: {str(e)}")

    return data, errors
