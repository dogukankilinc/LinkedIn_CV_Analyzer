#!/bin/bash
# ─────────────────────────────────────────────────────────────
# FIGES MathWorks CV Analyzer — Jetson AGX Orin Başlatma Scripti
# Kullanım: chmod +x baslat.sh && ./baslat.sh
# ─────────────────────────────────────────────────────────────

echo ""
echo "======================================================"
echo " FIGES MathWorks CV Analyzer - Baslatiliyor..."
echo "======================================================"
echo ""

# ─── 1. Ollama Kontrol ────────────────────────────────────────
if ! command -v ollama &> /dev/null; then
    echo "[HATA] Ollama kurulu degil!"
    echo "Kurmak icin: curl -fsSL https://ollama.com/install.sh | sh"
    exit 1
fi

if ! ollama list &> /dev/null; then
    echo "[HATA] Ollama servisi calismiyor. Baslatiliyor..."
    ollama serve &
    sleep 3
fi

# qwen2.5:72b modeli yuklu mu kontrol et
if ! ollama list | grep -q "qwen2.5:72b"; then
    echo "[UYARI] qwen2.5:72b modeli bulunamadi."
    echo "Model indiriliyor... (Bu islem uzun surebilir)"
    ollama pull qwen2.5:72b
fi

echo "[OK] Ollama servisi ve model hazir."
echo ""

# ─── 2. Python Kontrol ───────────────────────────────────────
if ! command -v python3 &> /dev/null; then
    echo "[HATA] Python3 kurulu degil!"
    echo "Kurmak icin: sudo apt install python3 python3-pip python3-venv"
    exit 1
fi

echo "[OK] Python3 bulundu: $(python3 --version)"
echo ""

# ─── 3. Sanal Ortam Kurulumu ──────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ ! -d ".venv" ]; then
    echo "Ilk kurulum yapiliyor, lutfen bekleyin..."
    python3 -m venv .venv
    echo "[OK] Sanal ortam olusturuldu."
fi

source .venv/bin/activate

# ─── 4. Kütüphaneler ──────────────────────────────────────────
echo "Kutuphaneler kontrol ediliyor / yukleniyor..."
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
echo "[OK] Tum kutuphaneler hazir."
echo ""

# ─── 5. Model Warm-Up (RAM'e Önceden Yükleme) ────────────────
echo "Modeller RAM'e alinıyor (arka planda)..."
echo "Bu islem USB SSD'den ilk okuma bekleme süresini sifira indirir."

# Türkçe model (öncelikli) — arka planda yükle
curl -s -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{"model":"qwen2.5:14b","prompt":"","keep_alive":"4h","stream":false}' \
  > /dev/null &
WARMUP_TR_PID=$!

# İngilizce model — arka planda yükle
curl -s -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{"model":"phi4","prompt":"","keep_alive":"4h","stream":false}' \
  > /dev/null &
WARMUP_EN_PID=$!

echo "[OK] Warm-up istekleri gonderildi (PID: TR=$WARMUP_TR_PID, EN=$WARMUP_EN_PID)"
echo "     Modeller arka planda RAM'e yuklenirken arayuz aciliyor..."
echo ""

# ─── 6. Uygulamayı Başlat ─────────────────────────────────────
echo "Arayuz baslatiliyor: http://localhost:8501"
echo "(Durdurmak icin CTRL+C)"
echo ""
streamlit run app.py --server.address=0.0.0.0 --server.port=8501

