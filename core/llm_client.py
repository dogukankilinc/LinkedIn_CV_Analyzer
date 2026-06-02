import os
from openai import OpenAI
from dotenv import load_dotenv
from core.prompt_builder import build_system_prompt, build_user_prompt

load_dotenv()

BASE_URL = "http://127.0.0.1:11434/v1"

# Dile göre model seçimi
MODELS = {
    "tr": "qwen2.5:14b",   # Türkçe: Qwen ailesi — Türkçe'de açık ara en iyi
    "en": "phi4",           # İngilizce: Microsoft Phi-4 — JSON + instruction following şampiyonu
}


def _get_client() -> OpenAI:
    return OpenAI(base_url=BASE_URL, api_key="ollama")


def check_ollama_status() -> bool:
    try:
        _get_client().models.list()
        return True
    except Exception:
        return False


def get_model_name(language: str) -> str:
    return MODELS.get(language, MODELS["tr"])


def analyze_cv_with_ollama(cv_text: str, language: str = "tr") -> str:
    """
    CV metnini dile göre seçilen modele gönderir, ham JSON string döndürür.
    language: 'tr' → qwen2.5:14b | 'en' → phi4
    """
    client    = _get_client()
    model     = get_model_name(language)
    sys_prompt = build_system_prompt(language)
    user_msg  = build_user_prompt(cv_text, language)

    try:
        response = client.chat.completions.create(
            model=model,
            temperature=0.1,
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user",   "content": user_msg},
            ],
            extra_body={"format": "json"},
        )
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(
            f"Ollama bağlantı hatası ({model}): {str(e)}\n"
            f"'ollama pull {model}' komutunu çalıştırdığınızdan emin olun."
        )
