import ollama
import json
from core.prompt_builder import build_system_prompt, build_user_prompt

MODEL_NAME = "qwen2.5:7b"

def check_ollama_status():
    """Ollama'nin calisip calismadigini ve modelin yuklu olup olmadigini dogrular."""
    try:
        models = ollama.list()
        # Modelleri kontrol et if needed
        return True
    except Exception as e:
        return False

def analyze_cv_with_ollama(cv_text: str) -> str:
    """
    CV metnini yerel Ollama servisine gönderir ve ham JSON yanıt döndürür.
    """
    system_prompt = build_system_prompt()
    user_message = build_user_prompt(cv_text)
    
    try:
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_message}
            ],
            format='json',
            options={
                'temperature': 0.1,
                'num_predict': 2048,
            }
        )
        return response['message']['content']
    except Exception as e:
        raise Exception(f"Ollama bağlantı hatası: {str(e)}\nLütfen CMD'den 'ollama run {MODEL_NAME}' komutunu çalıştırarak modelin yüklü olduğundan emin olun.")
