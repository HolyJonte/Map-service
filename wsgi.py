import sys
import os

# Lägg till din projektmapp i systemets sökväg
project_home = '/home/MaMaJoViDa/Map-service'
if project_home not in sys.path:
    sys.path.append(project_home)

# Sätt rätt miljövariabler om du vill (valfritt)
os.environ['FLASK_ENV'] = 'production'

# Importera din app från app.py
from app import app as application

