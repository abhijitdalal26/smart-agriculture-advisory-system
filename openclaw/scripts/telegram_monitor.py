#!/usr/bin/env python3
"""
telegram_monitor.py — KrishiMitra Proactive Alert Sender

Runs as a background daemon on the Raspberry Pi.
Polls the local /api/alerts endpoint every 5 minutes.
If a CRITICAL alert is found, sends a Telegram message to the farmer.
Includes cooldown per-alert to prevent spam — will not resend the same
alert for 6 hours. A reminder is sent after the cooldown expires only
if the alert is still active.

Managed by: krishimitra-telegram.service (systemd)
"""

import time
import json
import os
import requests
import hashlib
from datetime import datetime, timedelta
from pathlib import Path

# ─── Configuration ────────────────────────────────────────────────────────────
TELEGRAM_BOT_TOKEN = "8784796498:AAEnIB4fQ4MbNqQc6Cjt66hIJ9W45XKowRQ"
TELEGRAM_CHAT_ID   = "1778968172"
API_BASE_URL       = "http://localhost:8000"
POLL_INTERVAL_SEC  = 300          # 5 minutes
COOLDOWN_HOURS     = 6            # Don't resend same alert for 6 hours
STATE_FILE         = Path(__file__).parent / ".monitor_state.json"

TELEGRAM_API_URL   = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

# ─── Severity levels to trigger a message ────────────────────────────────────
TRIGGER_SEVERITIES = {"critical"}  # Only send for critical alerts

# ─── Helpers ─────────────────────────────────────────────────────────────────

def load_state() -> dict:
    """Load the sent-alert cooldown state from disk."""
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_state(state: dict):
    """Persist the cooldown state to disk."""
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def alert_hash(alert: dict) -> str:
    """Create a stable fingerprint for an alert based on its message."""
    return hashlib.md5(alert.get("message", "").encode()).hexdigest()

def is_in_cooldown(alert_id: str, state: dict) -> bool:
    """Check if this alert was recently sent and is still in cooldown."""
    if alert_id not in state:
        return False
    last_sent_str = state[alert_id]
    last_sent = datetime.fromisoformat(last_sent_str)
    return datetime.utcnow() < last_sent + timedelta(hours=COOLDOWN_HOURS)

def mark_sent(alert_id: str, state: dict):
    """Record when this alert was last sent."""
    state[alert_id] = datetime.utcnow().isoformat()

def send_telegram(message: str) -> bool:
    """Send a message to the configured Telegram chat."""
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        r = requests.post(TELEGRAM_API_URL, json=payload, timeout=10)
        return r.status_code == 200
    except Exception as e:
        print(f"[TelegramMonitor] Failed to send message: {e}")
        return False

def get_sensor_summary() -> str:
    """Fetch current sensor data for context in alert messages."""
    try:
        r = requests.get(f"{API_BASE_URL}/api/sensors/latest", timeout=5)
        if r.status_code == 200:
            d = r.json()
            return (
                f"🌡️ Air: {d.get('air_temp', 'N/A')}°C  "
                f"💧 Moisture: {d.get('soil_moisture', 'N/A')}%  "
                f"🧪 pH: {d.get('soil_ph', 'N/A')}  "
                f"☀️ Light: {d.get('light_lux', 'N/A')} Lux"
            )
    except Exception:
        pass
    return "*(sensor data unavailable)*"

def format_alert_message(alert: dict, sensor_summary: str) -> str:
    """Format a Telegram-friendly alert message."""
    severity = alert.get("severity", "info").upper()
    message  = alert.get("message", "Unknown alert")
    now_str  = datetime.now().strftime("%d %b %Y, %I:%M %p")

    icon_map = {"CRITICAL": "🚨", "WARNING": "⚠️", "INFO": "ℹ️"}
    icon = icon_map.get(severity, "🔔")

    return (
        f"{icon} *KrishiMitra Alert — {severity}*\n"
        f"🕐 {now_str}\n\n"
        f"{message}\n\n"
        f"📊 *Current Readings:*\n{sensor_summary}\n\n"
        f"_Reply to this bot for live advice_"
    )

def check_and_notify():
    """Main monitoring loop: fetch alerts and send if needed."""
    state = load_state()
    sensor_summary = get_sensor_summary()
    changed = False

    try:
        r = requests.get(f"{API_BASE_URL}/api/alerts", timeout=10)
        if r.status_code != 200:
            print(f"[TelegramMonitor] /api/alerts returned {r.status_code}")
            return
        data = r.json()
        alerts = data.get("alerts", [])
    except Exception as e:
        print(f"[TelegramMonitor] Failed to fetch alerts: {e}")
        return

    # Prune cooldown state for alerts no longer active
    active_hashes = {alert_hash(a) for a in alerts}
    stale_keys = [k for k in state if k not in active_hashes]
    for k in stale_keys:
        del state[k]
    if stale_keys:
        changed = True

    for alert in alerts:
        severity = alert.get("severity", "info")
        if severity not in TRIGGER_SEVERITIES:
            continue

        aid = alert_hash(alert)
        if is_in_cooldown(aid, state):
            # Still in cooldown; skip this alert
            continue

        # Send it
        msg = format_alert_message(alert, sensor_summary)
        success = send_telegram(msg)
        if success:
            print(f"[TelegramMonitor] Sent alert: {alert.get('message','')[:60]}")
            mark_sent(aid, state)
            changed = True
        else:
            print(f"[TelegramMonitor] Failed to send alert.")

    if changed:
        save_state(state)

def main():
    print("[TelegramMonitor] Starting KrishiMitra Telegram Alert Monitor...")
    print(f"  Poll interval : {POLL_INTERVAL_SEC // 60} minutes")
    print(f"  Cooldown      : {COOLDOWN_HOURS} hours per alert")
    print(f"  Watching      : {API_BASE_URL}/api/alerts")

    # Send startup notification
    time.sleep(5)  # Wait for backend to be ready
    send_telegram(
        "🌱 *KrishiMitra is Online!*\n"
        "Your smart farm monitor has started.\n\n"
        "I will alert you here if any *critical* conditions are detected "
        f"(checked every {POLL_INTERVAL_SEC // 60} minutes).\n\n"
        "_Send me a message or use the dashboard for live advice._"
    )

    while True:
        try:
            check_and_notify()
        except Exception as e:
            print(f"[TelegramMonitor] Unhandled error in monitor loop: {e}")
        time.sleep(POLL_INTERVAL_SEC)

if __name__ == "__main__":
    main()
