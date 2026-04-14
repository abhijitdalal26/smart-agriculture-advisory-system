#!/bin/bash
# KrishiMitra — One-Shot Setup Script for Raspberry Pi
# Run as: bash setup.sh
# From:   /home/ess/.openclaw/workspace/krishimitra/

set -e
WORKSPACE="/home/ess/.openclaw/workspace"
PROJECT="$WORKSPACE/smart-agriculture-advisory-system"
DEPLOY="$PROJECT/deployment"

echo "============================================="
echo "  KrishiMitra Setup — Raspberry Pi"
echo "============================================="

# ── 1. Clone repo if not already present ─────────────────────────────────────
if [ ! -d "$PROJECT/.git" ]; then
  echo "[1/7] Cloning repository..."
  cd "$WORKSPACE"
  git clone https://github.com/abhijitdalal26/smart-agriculture-advisory-system.git krishimitra
else
  echo "[1/7] Repo already present — pulling latest..."
  cd "$PROJECT"
  git pull origin main
fi

cd "$PROJECT"

# ── 2. Python dependencies ────────────────────────────────────────────────────
echo "[2/7] Installing Python dependencies..."
pip3 install -r backend/requirements.txt --ignore-installed typing_extensions --break-system-packages

# ── 3. luma.lcd and PIL for TFT ───────────────────────────────────────────────
echo "[3/7] Installing TFT display dependencies..."
pip3 install luma.lcd Pillow --break-system-packages

# ── 4. Node / npm dependencies + build ────────────────────────────────────────
echo "[4/7] Building React frontend..."
cd "$PROJECT/frontend"
npm install
npm run build
cd "$PROJECT"

# ── 5. Install 'serve' to host built frontend ─────────────────────────────────
echo "[5/7] Installing 'serve' for frontend hosting..."
npm install -g serve

# ── 6. Copy OpenClaw knowledge files ─────────────────────────────────────────
echo "[6/7] Installing OpenClaw knowledge files..."
cp -u "$PROJECT/openclaw/SOUL.md"   "$WORKSPACE/SOUL.md"
cp -u "$PROJECT/openclaw/AGENTS.md" "$WORKSPACE/AGENTS.md"
cp -u "$PROJECT/openclaw/USER.md"   "$WORKSPACE/USER.md"
cp -u "$PROJECT/openclaw/TOOLS.md"  "$WORKSPACE/TOOLS.md"
cp -u "$PROJECT/openclaw/MEMORY.md" "$WORKSPACE/MEMORY.md"
mkdir -p "$WORKSPACE/memory"
mkdir -p "$WORKSPACE/projects"

# ── 7. Install and enable systemd services ────────────────────────────────────
echo "[7/7] Setting up systemd services..."
cp "$DEPLOY"/*.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable krishimitra-backend.service
systemctl enable krishimitra-sensors.service
systemctl enable krishimitra-tft.service
systemctl enable krishimitra-frontend.service
systemctl start  krishimitra-backend.service
sleep 3
systemctl start  krishimitra-sensors.service
systemctl start  krishimitra-tft.service
systemctl start  krishimitra-frontend.service

echo ""
echo "✅ KrishiMitra is running!"
echo ""
echo "  🌐 Dashboard : http://$(hostname -I | awk '{print $1}'):3000"
echo "  📡 API Docs  : http://$(hostname -I | awk '{print $1}'):8000/docs"
echo ""
echo "Check service status: systemctl status krishimitra-backend"
