import os
import time
import smtplib
import platform
from email.mime.text import MIMEText
from datetime import datetime

# ==== CONFIGURATION ====
DEVICE_FILE = "devices.txt"
PING_INTERVAL = 10  # seconds

EMAIL_SENDER = "cedophe@gmail.com"
EMAIL_PASSWORD = "wpvu ikgv tllc bfpy"  # Gmail App Password
EMAIL_RECEIVER = "cedophe@gmail.com"

LOG_FILE = "monitor_log.txt"  # Optional: local logging


# ==== LOGGING FUNCTION ====
def log(msg):
    timestamped = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(timestamped)
    with open(LOG_FILE, "a", encoding="utf-8") as logf:
        logf.write(timestamped + "\n")


# ==== EMAIL FUNCTION ====
def send_email_alert(subject, message):
    try:
        msg = MIMEText(message)
        msg["Subject"] = subject
        msg["From"] = EMAIL_SENDER
        msg["To"] = EMAIL_RECEIVER

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())

        log(f"[EMAIL SENT] {subject}")
    except Exception as e:
        log(f"[EMAIL FAILED] {e}")


# ==== PING FUNCTION (OS-Compatible) ====
def is_reachable(ip):
    if platform.system().lower() == "windows":
        command = f"ping -n 1 -w 1000 {ip} > nul"
    else:
        command = f"ping -c 1 -W 1 {ip} > /dev/null 2>&1"
    return os.system(command) == 0


# ==== MAIN MONITORING LOOP ====
def monitor_devices():
    status_map = {}  # Tracks known status of devices

    while True:
        log("🔄 Checking devices...")
        with open(DEVICE_FILE, "r") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    name, ip = line.strip().split(",")
                except ValueError:
                    log(f"[FORMAT ERROR] Check line: {line}")
                    continue

                reachable = is_reachable(ip)

                if ip not in status_map:
                    status_map[ip] = reachable

                # DOWN alert
                if not reachable and status_map[ip]:
                    log(f"[❌ DOWN] {name} ({ip}) is NOT reachable!")
                    send_email_alert(f"{name} DOWN", f"⚠️ ALERT: {name} ({ip}) is DOWN!")

                # UP recovery
                elif reachable and not status_map[ip]:
                    log(f"[✅ BACK ONLINE] {name} ({ip}) is reachable.")
                    send_email_alert(f"{name} is BACK ONLINE", f"✅ {name} ({ip}) is back online.")

                else:
                    log(f"[OK] {name} ({ip}) status unchanged.")

                # Update status
                status_map[ip] = reachable

        time.sleep(PING_INTERVAL)


# ==== START SCRIPT ====
if __name__ == "__main__":
    log("🚀 Starting network monitoring...")
    monitor_devices()
