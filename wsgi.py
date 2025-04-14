import sys
import os

# Lägg till din projektmapp i sökvägen
path = '/home/holyjonte/Map-service'
if path not in sys.path:
    sys.path.append(path)

# Sätt rätt miljö (valfritt men bra)
os.environ['FLASK_ENV'] = 'production'

# Importera din Flask-app
from app import app as application  # app är Flask-objektet i app.py
