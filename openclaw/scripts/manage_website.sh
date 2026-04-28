#!/usr/bin/env bash
# ============================================================
# manage_website.sh — KrishiMitra Website Manager
# For OpenClaw to start, stop, check, and get the URL of the
# KrishiMitra web dashboard.
#
# Usage:
#   bash manage_website.sh status   → check if running
#   bash manage_website.sh start    → start the website
#   bash manage_website.sh stop     → stop the website
#   bash manage_website.sh restart  → restart the website
# ============================================================

ACTION=${1:-"status"}
PI_IP=$(hostname -I | awk '{print $1}')
PORT=8000
DASHBOARD_URL="http://${PI_IP}:${PORT}"

check_status() {
    systemctl is-active --quiet krishimitra-backend.service
    return $?
}

case "$ACTION" in
  "status")
    if check_status; then
        echo "✅ KrishiMitra website is RUNNING"
        echo "🌐 Dashboard URL: ${DASHBOARD_URL}"
        echo "📡 API Docs: ${DASHBOARD_URL}/docs"
        echo ""
        echo "--- Service Info ---"
        systemctl status krishimitra-backend.service --no-pager -l | head -20
    else
        echo "❌ KrishiMitra website is STOPPED"
        echo "Run 'bash manage_website.sh start' to start it."
    fi
    ;;

  "start")
    echo "🚀 Starting KrishiMitra website..."
    systemctl start krishimitra-backend.service
    sleep 3
    if check_status; then
        echo "✅ KrishiMitra website started successfully!"
        echo "🌐 Access your dashboard at: ${DASHBOARD_URL}"
        echo "📡 API Docs available at:  ${DASHBOARD_URL}/docs"
    else
        echo "❌ Failed to start. Check logs: journalctl -u krishimitra-backend -n 30"
        exit 1
    fi
    ;;

  "stop")
    echo "🛑 Stopping KrishiMitra website..."
    systemctl stop krishimitra-backend.service
    echo "✅ Website stopped."
    ;;

  "restart")
    echo "🔄 Restarting KrishiMitra website..."
    systemctl restart krishimitra-backend.service
    sleep 3
    if check_status; then
        echo "✅ KrishiMitra website restarted successfully!"
        echo "🌐 Dashboard: ${DASHBOARD_URL}"
    else
        echo "❌ Restart failed. Check logs: journalctl -u krishimitra-backend -n 30"
        exit 1
    fi
    ;;

  *)
    echo "Usage: bash manage_website.sh [start|stop|restart|status]"
    exit 1
    ;;
esac
