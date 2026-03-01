import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

URL = "https://tickets.wiener-staatsoper.at/webshop/webticket/bestseatselect?eventId=11649&upsellNo=0"
BOT_TOKEN = "8710128594:AAHRu1wQgO0rsYJUVbprXATJNVlVRMM-QBc"
CHAT_ID = "92745369"
CHECK_INTERVAL = 120
IGNORED_CATEGORIES = [9]

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": message})

def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def check_tickets():
    driver = get_driver()
    try:
        driver.get(URL)
        time.sleep(5)
        page_text = driver.find_element("tag name", "body").text
        print("Seite geladen, Länge:", len(page_text))

        import re
        page_text_filtered = re.sub(
            r'Kategorie\s*9.*?(?=Kategorie\s*\d|$)', '',
            page_text, flags=re.DOTALL | re.IGNORECASE
        )

        sold_out_count = page_text_filtered.lower().count("ausverkauft")
        total_cats = len(re.findall(r'Kategorie\s*\d', page_text_filtered, re.IGNORECASE))

        print(f"Kategorien gefunden: {total_cats}, Ausverkauft: {sold_out_count}")

        if total_cats > 0 and sold_out_count < total_cats:
            send_telegram(
                f"🎭 БИЛЕТЫ ПОЯВИЛИСЬ!\n"
                f"Eugen Onegin 24.05.2026 — Wiener Staatsoper\n"
                f"(Kategorie 9 ignoriert)\n"
                f"👉 {URL}"
            )
            return True

        return False

    finally:
        driver.quit()

print("Monitoring gestartet...")
send_telegram("✅ Monitoring gestartet — Eugen Onegin 24.05.2026 (Kat. 9 ignoriert)")

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