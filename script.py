import time
import requests
from bs4 import BeautifulSoup

URL = "https://www.wiener-staatsoper.at/kalender/detail/eugen-onegin/2026-05-24/"
BOT_TOKEN = "8710128594:AAHRu1wQgO0rsYJUVbprXATJNVlVRMM-QBc"
CHAT_ID = "92745369"
CHECK_INTERVAL = 120

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": message})

def check_tickets():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "de-AT,de;q=0.9",
    }
    response = requests.get(URL, headers=headers, timeout=15)
    soup = BeautifulSoup(response.text, "html.parser")
    page_text = soup.get_text()

    print("Länge:", len(page_text))
    print("Vorschau:", page_text[:2000])

    if "Restkarten" in page_text or "Tickets verfügbar" in page_text:
        send_telegram(
            f"🎭 БИЛЕТЫ ПОЯВИЛИСЬ!\n"
            f"Eugen Onegin 24.05.2026\n"
            f"👉 {URL}"
        )
        return True

    return False

print("Monitoring gestartet...")
send_telegram("✅ Monitoring gestartet — Eugen Onegin 24.05.2026")

while True:
    try:
        if check_tickets():
            time.sleep(3600)
        else:
            print(f"Keine Tickets. Nächste Prüfung in {CHECK_INTERVAL}s...")
            time.sleep(CHECK_INTERVAL)
    except Exception as e:
        print("Fehler:", e)
        time.sleep(60)
