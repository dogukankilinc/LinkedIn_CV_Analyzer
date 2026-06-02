@echo off
echo FIGES CV Analyzer (Yerel Versiyon) Baslatiliyor...

:: Ollama kontrolu
ollama list >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo ====================================================
    echo DIKKAT: Ollama calismiyor veya kurulamamis.
    echo Lutfen once Ollama uygulamasini actiginiza emin olun.
    echo Eger yuklu degilse: https://ollama.com/download
    echo Eger qwen2.5:72b modeli yoksa, CMD acip su komutu calistirin:
    echo   ollama pull qwen2.5:72b
    echo ====================================================
    echo.
    pause
    exit
)

:: Sanal ortam kontrolu
IF NOT EXIST ".venv" (
    echo.
    echo Ilk kurulum yapiliyor, lutfen bekleyin... Bu islem birkac dakika surebilir.
    python -m venv .venv
    call .venv\Scripts\activate.bat
    
    echo Bagimliliklar yukleniyor...
    pip install -r requirements.txt
    echo Kurulum tamamlandi.
) ELSE (
    call .venv\Scripts\activate.bat
)

echo.
echo Arayuz aciliyor... Lutfen tarayicinin acilmasini bekleyin (http://localhost:8501)
streamlit run app.py
