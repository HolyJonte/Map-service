import sys
import os

# Lägg till din projektmapp i systemets sökväg
project_home = '/home/MaMaJoViDa/Map-service'
if project_home not in sys.path:
    sys.path.append(project_home)

# Sätt rätt miljövariabler om du vill (valfritt)
os.environ['FLASK_ENV'] = 'production'

# =====================================================
# Valfritt: Uppdatera automatiskt från GitHub vid reload
# =====================================================
try:
    exec(open("/home/MaMaJoViDa/post_reload.py").read())
except Exception as e:
    print(f"Fel vid GitHub-pull: {e}")

# Importera din app från app.py
from app import app as application

