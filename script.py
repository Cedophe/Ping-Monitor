import os
import time
import smtplib
import platform
import requests
from email.mime.text import MIMEText
from datetime import datetime


# ==== CONFIGURATION ====
DEVICE_FILE = "devices.txt"
PING_INTERVAL = 10  # seconds

EMAIL_SENDER = "cedophe@gmail.com"
EMAIL_PASSWORD = "xhhi crce lkch yscm"  # Gmail App Password
EMAIL_RECEIVER = "cedophe@gmail.com"

TELEGRAM_TOKEN = "7508783139:AAH6QLpLVcMLdQlxSVs8XSeW64d1AtOAbfM"
TELEGRAM_CHAT_ID = "5971065330"

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

# ==== TELEGRAM FUNCTION ====
def send_telegram_alert(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message
        }
        response = requests.post(url, data=data)
        if response.status_code == 200:
            log(f"[TELEGRAM SENT] {message}")
        else:
            log(f"[TELEGRAM FAILED] {response.text}")
    except Exception as e:
        log(f"[TELEGRAM ERROR] {e}")


# ==== PING FUNCTION (OS-Compatible) ====
def is_reachable(ip):
    if platform.system().lower() == "windows":
        command = f"ping -n 1 -w 1000 {ip} > nul"
    else:
        command = f"ping -c 1 -W 1 {ip} > /dev/null 2>&1"
    return os.system(command) == 0


# ==== MAIN MONITORING LOOP ====
def monitor_devices(): # Define the main loop function
    status_map = {}  # Create a dictionary to track last known status of each IP

    while True: # Infinite loop to keep checking
        log("🔄 Checking devices...") # Print/log the current monitoring cycle
        with open(DEVICE_FILE, "r") as f: # Open the file with device list
            for line in f: # Loop through each line in the file
                if not line.strip(): # Skip empty lines
                    continue
                try:
                    # Split the line into name and IP (e.g., Router1,192.168.1.1)
                    name, ip = line.strip().split(",")
                except ValueError:
                    # If line format is invalid, log an error and skip it
                    log(f"[FORMAT ERROR] Check line: {line}")
                    continue
                    # Ping the device to check if it’s currently reachable
                reachable = is_reachable(ip)
                
                # If the IP is seen for the first time, store its current state
                if ip not in status_map:
                    status_map[ip] = reachable

                # DOWN alert
                if not reachable and status_map[ip]:
                    msg = f"⚠️ ALERT: {name} ({ip}) is DOWN!"
                    log(f"[❌ DOWN] {msg}")
                    send_email_alert(f"{name} DOWN", f"⚠️ ALERT: {name} ({ip}) is DOWN!")
                    send_telegram_alert(msg)

                # UP recovery
                elif reachable and not status_map[ip]:
                    msg = f"✅ {name} ({ip}) is back online."
                    log(f"[✅ BACK ONLINE] {msg}")
                    send_email_alert(f"{name} is BACK ONLINE", f"✅ {name} ({ip}) is back online.")
                    send_telegram_alert(msg)

                else:
                    log(f"[OK] {name} ({ip}) status unchanged.")

                # Update status
                status_map[ip] = reachable

        time.sleep(PING_INTERVAL)


# ==== START SCRIPT ====
if __name__ == "__main__":
    log("🚀 Starting network monitoring...")
    monitor_devices()
