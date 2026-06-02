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
    echo Eger qwen2.5:14b veya phi4 modeli yoksa, CMD acip su komutlari calistirin:
    echo   ollama pull qwen2.5:14b
    echo   ollama pull phi4
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
echo Modeller RAM'e alinıyor (arka planda)...
echo Bu islem USB SSD'den ilk okuma bekleme suresini sifira indirir.

:: Türkçe model (öncelikli) — arka planda yükle
start /b powershell -WindowStyle Hidden -Command ^
  "Invoke-RestMethod -Uri 'http://localhost:11434/api/generate' -Method POST -ContentType 'application/json' -Body '{\"model\":\"qwen2.5:14b\",\"prompt\":\"\",\"keep_alive\":\"4h\",\"stream\":false}'" ^
  2>nul

:: İngilizce model — arka planda yükle
start /b powershell -WindowStyle Hidden -Command ^
  "Invoke-RestMethod -Uri 'http://localhost:11434/api/generate' -Method POST -ContentType 'application/json' -Body '{\"model\":\"phi4\",\"prompt\":\"\",\"keep_alive\":\"4h\",\"stream\":false}'" ^
  2>nul

echo [OK] Warm-up istekleri gonderildi. Modeller arka planda RAM'e yuklenirken arayuz aciliyor...
echo.
echo Arayuz aciliyor... Lutfen tarayicinin acilmasini bekleyin (http://localhost:8501)
streamlit run app.py
