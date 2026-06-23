#!/data/data/com.termux/files/usr/bin/bash
# ══ KHỞI ĐỘNG WEB DASHBOARD TU TIÊN BOT ══

cd "$(dirname "$0")"

echo "📦 Kiểm tra Flask..."
pip install flask --break-system-packages -q

echo "🌐 Khởi động Web Dashboard..."
echo "   Local:  http://localhost:5000"
echo "   Nhấn Ctrl+C để dừng"
echo ""

python web/app.py
