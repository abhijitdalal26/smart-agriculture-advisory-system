#!/usr/bin/env bash
# ============================================================
# KrishiMitra — Pi-Side Quick Deploy Script
# Run this ON the Pi AFTER cloning the repo
# Usage: bash quick_deploy.sh
# ============================================================

set -e
PROJECT_DIR="/home/ess/.openclaw/workspace/krishimitra"
WORKSPACE_DIR="/home/ess/.openclaw/workspace"

echo ""
echo "🌿 KrishiMitra Quick Deploy"
echo "==========================="

# 1. Python deps
echo "[1/4] Installing Python dependencies..."
pip3 install fastapi uvicorn sqlalchemy xgboost scikit-learn pandas numpy joblib requests httpx aiohttp python-dotenv --break-system-packages -q
pip3 install luma.lcd Pillow --break-system-packages -q
echo "  ✅ Python deps done"

# 2. Node / frontend build
echo "[2/4] Building React frontend..."
cd "$PROJECT_DIR/frontend"
npm install -q
npm run build
echo "  ✅ Frontend built"

# 3. Install serve for frontend hosting
echo "[3/4] Installing serve..."
npm install -g serve -q
echo "  ✅ serve installed"

# 4. Copy OpenClaw files
echo "[4/4] Copying OpenClaw knowledge files..."
cd "$PROJECT_DIR"
mkdir -p "$WORKSPACE_DIR/memory" "$WORKSPACE_DIR/projects"
for f in SOUL AGENTS USER TOOLS MEMORY; do
  cp -f "openclaw/${f}.md" "$WORKSPACE_DIR/${f}.md"
done
echo "  ✅ OpenClaw files installed"

echo ""
echo "✅ Setup complete! Now start the services:"
echo ""
echo "  Terminal 1 (Backend):"
echo "    cd $PROJECT_DIR && python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000"
echo ""
echo "  Terminal 2 (Sensors + LCD):"
echo "    cd $PROJECT_DIR && python3 sensor_hub.py"
echo ""
echo "  Terminal 3 (Frontend):"
echo "    cd $PROJECT_DIR/frontend && serve -s dist -l 3000"
echo ""
echo "  Terminal 4 (TFT Display — optional):"
echo "    cd $PROJECT_DIR && python3 display_tft.py"
echo ""
echo "  🌐 Dashboard: http://$(hostname -I | awk '{print $1}'):3000"
echo "  📡 API Docs : http://$(hostname -I | awk '{print $1}'):8000/docs"
