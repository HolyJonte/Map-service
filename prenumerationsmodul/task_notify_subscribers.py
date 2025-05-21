# Schemalagd task som skickar SMS till användare när nya händelser matchar deras län

import time
from datetime import datetime
import sys
import os

# Lägg till sökvägen till prenumerationsmodulen
sys.path.append("/home/MaMaJoViDa/Map-service")
os.chdir("/home/MaMaJoViDa/Map-service")

from prenumerationsmodul.notifications import notify_accidents

# Loggfilens sökväg
LOG_FILE = "/home/MaMaJoViDa/Map-service/notify_log.txt"

# Funktion för att logga meddelanden
def log(message):
    with open(LOG_FILE, "a") as f:
        f.write(f"[{datetime.now()}] {message}\n")

# Kör funktionen notify_accidents var 10:e minut
if __name__ == "__main__":
    while True:
        try:
            notify_accidents()
            log("✔ Notifieringar körda klart")
        except Exception as e:
            log(f"❌ Fel vid notifiering: {str(e)}")
        time.sleep(600)  # kör var 10:e minut
