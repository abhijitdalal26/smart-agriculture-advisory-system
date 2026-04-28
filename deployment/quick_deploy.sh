#!/usr/bin/env bash
# ============================================================
# KrishiMitra — Pi-Side Quick Deploy Script
# Run this ON the Pi AFTER cloning the repo
# Usage: bash quick_deploy.sh
# ============================================================

set -e
PROJECT_DIR="/home/ess/.openclaw/workspace/smart-agriculture-advisory-system"
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

# 3. Copy OpenClaw files
echo "[3/4] Copying OpenClaw knowledge files..."
cd "$PROJECT_DIR"
mkdir -p "$WORKSPACE_DIR/memory" "$WORKSPACE_DIR/projects"
for f in SOUL AGENTS USER TOOLS MEMORY KNOWLEDGE_BASE; do
  if [ -f "openclaw/${f}.md" ]; then
    cp -f "openclaw/${f}.md" "$WORKSPACE_DIR/${f}.md"
    echo "  -> ${f}.md"
  fi
done

# Copy the scripts/ directory to workspace
mkdir -p "$WORKSPACE_DIR/scripts"
cp -f openclaw/scripts/*.sh "$WORKSPACE_DIR/scripts/" 2>/dev/null || true
cp -f openclaw/scripts/*.py "$WORKSPACE_DIR/scripts/" 2>/dev/null || true
chmod +x "$WORKSPACE_DIR/scripts/"*.sh 2>/dev/null || true
echo "  ✅ OpenClaw files + scripts installed"

# 4. Install & enable systemd services
echo "[4/4] Installing systemd services..."
sudo cp deployment/*.service /etc/systemd/system/
sudo systemctl daemon-reload
for svc in krishimitra-backend krishimitra-sensors krishimitra-tft krishimitra-telegram; do
  sudo systemctl enable "${svc}.service" 2>/dev/null || true
  sudo systemctl restart "${svc}.service" 2>/dev/null || true
  echo "  -> ${svc}: $(systemctl is-active ${svc}.service)"
done
echo "  ✅ Services installed"

echo ""
echo "✅ Setup complete!"
echo ""
echo "  🌐 Dashboard: http://$(hostname -I | awk '{print $1}'):8000"
echo "  📡 API Docs : http://$(hostname -I | awk '{print $1}'):8000/docs"
echo "  📱 Telegram : @saas_pi_bot (alerts sent to your chat)"
echo ""
echo "  Check service status:"
echo "    systemctl status krishimitra-backend krishimitra-sensors krishimitra-telegram"
