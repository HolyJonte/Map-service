# Denna fil hanterar schemalagda uppgifter för att uppdatera cache-minnet.

import sys
import os
import time
from datetime import datetime

# Se till att rätt mapp används
sys.path.append("/home/MaMaJoViDa/Map-service")
os.chdir("/home/MaMaJoViDa/Map-service")

from api.logic import update_cache

if __name__ == "__main__":
    while True:
        print(f"[{datetime.now()}] ▶ Kör cacheuppdatering...")
        try:
            update_cache()
            print(f"[{datetime.now()}] Cache uppdaterad")
        except Exception as e:
            print(f"[{datetime.now()}] Fel vid cacheuppdatering: {str(e)}")

        time.sleep(300)  # Vänta 5 minuter

