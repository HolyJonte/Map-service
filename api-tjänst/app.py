import sys
import os
from flask import Flask, send_from_directory

# Lägg till projektroten så att Python hittar andra mappar
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from användardata.api import trafik_bp  # ← nu fungerar denna!

# Pekar på din frontend/static-mapp
frontend_path = os.path.join(os.path.dirname(__file__), '../frontend/static')

app = Flask(__name__, static_folder=frontend_path)
app.register_blueprint(trafik_bp)  # Registrera kameror-endpointen

@app.route('/')
def serve_index():
    return send_from_directory(frontend_path, 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(frontend_path, filename)

if __name__ == '__main__':
    app.run(debug=True)

