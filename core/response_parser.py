import json

def parse_and_validate(raw_response: str) -> tuple[dict, list[str]]:
    """
    LLM yanıtını parse eder, doğrular ve normalize eder.
    """
    errors = []

    # ─── 1. JSON Parse ──────────────────────────────────────────
    try:
        cleaned = raw_response.strip()

        # format='json' olmadan model bazen JSON öncesi/sonrası metin ekler
        # { ... } bloğunu bul ve çıkar
        if not cleaned.startswith("{"):
            start = cleaned.find("{")
            if start != -1:
                # Eşleşen kapanış parantezini bul
                depth = 0
                end = start
                for i, ch in enumerate(cleaned[start:], start):
                    if ch == "{":
                        depth += 1
                    elif ch == "}":
                        depth -= 1
                        if depth == 0:
                            end = i
                            break
                cleaned = cleaned[start:end + 1]

        # ```json ``` bloğu sarmalanmış olabilir
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        return {}, [f"JSON Parse Hatası: {str(e)}", "Model geçerli bir JSON döndürmedi."]

    # ─── 2. Skor Normalizasyonu ──────────────────────────────────
    try:
        scores = data.get("scores", {})

        def safe_pct(cat_key):
            val = scores.get(cat_key, {})
            if isinstance(val, dict):
                return int(val.get("percentage", 0))
            return 0

        ai_score = safe_pct("ai")
        sm_score = safe_pct("system_modeling")
        es_score = safe_pct("embedded_systems")
        total = ai_score + sm_score + es_score

        if total > 0 and total != 100:
            data["scores"]["ai"]["percentage"]               = round(ai_score / total * 100)
            data["scores"]["system_modeling"]["percentage"]  = round(sm_score / total * 100)
            data["scores"]["embedded_systems"]["percentage"] = round(es_score / total * 100)

    except Exception as e:
        errors.append(f"Skor normalizasyon hatası: {str(e)}")

    # ─── 3. Öneri Yapısı Düzeltme ───────────────────────────────
    try:
        recs = data.get("recommendations", {})

        # Model bazen recommendations'ı list döndürebiliyor — sıfırla
        if not isinstance(recs, dict):
            recs = {}

        for cat in ["ai", "system_modeling", "embedded_systems"]:
            cat_data = recs.get(cat, {})

            # Kategori yoksa boş oluştur
            if cat_data is None or not isinstance(cat_data, dict):
                recs[cat] = {"toolboxes": [], "sales_pitch": ""}
                continue

            # toolboxes alanını al — yoksa veya hatalıysa boş liste ver
            raw_tbs = cat_data.get("toolboxes", [])
            if not isinstance(raw_tbs, list):
                raw_tbs = []

            # Her elemanın dict olduğundan emin ol
            clean_tbs = [tb for tb in raw_tbs if isinstance(tb, dict)]
            cat_data["toolboxes"] = clean_tbs

            # sales_pitch kontrolü
            if not isinstance(cat_data.get("sales_pitch"), str):
                cat_data["sales_pitch"] = ""

            recs[cat] = cat_data

        data["recommendations"] = recs

    except Exception as e:
        errors.append(f"Öneri yapısı düzeltme hatası: {str(e)}")

    return data, errors
