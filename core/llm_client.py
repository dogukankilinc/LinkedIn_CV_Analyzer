import os
from openai import OpenAI
from dotenv import load_dotenv
from core.prompt_builder import build_system_prompt, build_user_prompt

load_dotenv()

MODEL_NAME = "qwen2.5:72b"
BASE_URL   = "http://127.0.0.1:11434/v1"


def _get_client() -> OpenAI:
    """Yerel Ollama sunucusuna bağlanan OpenAI uyumlu istemciyi döndürür."""
    return OpenAI(base_url=BASE_URL, api_key="ollama")


def check_ollama_status() -> bool:
    """Yerel Ollama servisine erişilebilir mi kontrol eder."""
    try:
        _get_client().models.list()
        return True
    except Exception:
        return False


def analyze_cv_with_ollama(cv_text: str) -> str:
    """
    CV metnini yerel Ollama'ya (OpenAI uyumlu endpoint) gönderir,
    ham JSON string döndürür.
    """
    client = _get_client()

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            temperature=0.1,
            messages=[
                {"role": "system", "content": build_system_prompt()},
                {"role": "user",   "content": build_user_prompt(cv_text)},
            ],
            extra_body={"format": "json"},  # Ollama katı JSON modu
        )
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(
            f"Ollama bağlantı hatası: {str(e)}\n"
            f"Lütfen yerel Ollama servisinin (127.0.0.1:11434) çalıştığından "
            f"ve '{MODEL_NAME}' modelinin yüklü olduğundan emin olun."
        )
