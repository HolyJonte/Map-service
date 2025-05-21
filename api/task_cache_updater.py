# Denna fil hanterar schemalagda uppgifter för att uppdatera cache-minnet.
# Den körs kontinuerligt och uppdaterar cachen var 5:e minut och loggar resultatet i en textfil.

import time
from datetime import datetime
import sys
import os

# Lägger till sökvägen till projektet så att vi kan importera moduler
sys.path.append("/home/MaMaJoViDa/Map-service")
from api.logic import update_cache

# Definierar sökvägen till loggfilen
LOG_FILE = "/home/MaMaJoViDa/Map-service/cache_log.txt"

# Funktion för att uppdatera cachen och logga resultatet
def log(message):
    with open(LOG_FILE, "a") as f:
        f.write(f"[{datetime.now()}] {message}\n")

# Kör cacheuppdatering och loggar resultatet
if __name__ == "__main__":
    while True:
        try:
            update_cache()
            log("✔ Cache uppdaterad")
        except Exception as e:
            log(f"❌ Fel vid cacheuppdatering: {str(e)}")
        time.sleep(300)  # Vänta 5 minuter

