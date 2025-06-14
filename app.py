# Denna fil är huvudfilen för Flask-applikationen.
# Den startar servern, registrerar blueprints och hanterar statiska filer från
# frontend-delen (HTML, JS, CSS).

# Importerar systemmodulen för att hantera sökvägar
import sys
# Importerar os-modulen för att hantera filsystemet
import os
# Importerar Flask och render_template
from flask import Flask, render_template, send_from_directory, request
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
# Importerar trafik_bp från routes-modulen, som innehåller kameror-endpointen
from api.routes import trafik_bp
# Importerar subscription_routes
from prenumerationsmodul.subscription_routes import subscription_routes
#Importerar admin_routes
from admin.admin_routes import admin_routes
from dotenv import load_dotenv
import os

from users.user_routes import user_routes

# Importerar dotenv för att läsa in miljövariabler från en .env-fil
load_dotenv()

# Importerar notify_accidents för att schemalägga SMS-notifikationer
from prenumerationsmodul.notifications import notify_accidents

# Lägg till projektroten så att Python hittar andra moduler/mappar
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Anger sökvägen till frontend-mappen där statiska filer finns (tex index, JS och CSS)
frontend_path = os.path.join(os.path.dirname(__file__), '../frontend/static')

# Anger sökvägen till templates-mappen där HTML-mallar finns
templates_path = os.path.join(os.path.dirname(__file__), 'templates')

# Skapar en Flask-applikation och anger sökvägen till frontend-mappen som statisk mapp
app = Flask(
    __name__,
    static_folder='frontend/static',
    template_folder='frontend/templates'
    )

# Aktiverar CORS för alla domäner och alla endpoints
CORS(app, resources={r"/notification/*": {"origins": "*"}})

app.secret_key = os.getenv("FLASK_SECRET_KEY")

# Registrerar trafik_bp (kameror-endpointen) som en blueprint i Flask-applikationen
app.register_blueprint(trafik_bp)
# Registrerar prenumerationsmodulens routes (subscription_routes) som en blueprint
app.register_blueprint(subscription_routes, url_prefix='/subscriptions')
# Registrerar admin-rutter (admin_routes) som en blueprint
app.register_blueprint(admin_routes)

app.register_blueprint(user_routes, url_prefix='/users')

# Definierar en route för att servera index.html-filen från frontend-mappen
@app.route('/')
def serve_index():
    return render_template("index.html")

# Definierar en route för att servera andra statiska filer (tex JS, CSS) från frontend-mappen
@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(frontend_path, filename)

# Definierar en route för att visa login.html-mallen
@app.route('/login')
def login_choice():
    return render_template("login_choice.html")

# Definierar en route för att visa aboutus.html-mallen
@app.route('/aboutus')
def about():
    return render_template("aboutus.html")

# För att visa förhandsvisning av karta på webbsajt för kund
@app.route('/embed/<path:filename>')
def embed_files(filename):
    # Använd Flask-konfigurationens static_folder istället för hardkodad
    embed_dir = os.path.join(app.static_folder, 'embed')
    return send_from_directory(embed_dir, filename)

# Definierar en route för att visa embed_map.html-mallen
@app.route("/embed-map")
def embed_map():
    lat = request.args.get("lat", default=62.0)
    lng = request.args.get("lng", default=15.0)
    zoom = request.args.get("zoom", default=6)
    return render_template("embed_map.html", lat=lat, lng=lng, zoom=zoom)


# Kör appen
if __name__ == '__main__':

    try:
        app.run(debug=True)

    except (KeyboardInterrupt, SystemExit):
        # Vid fel skrivs följande meddelande ut
        print("Lyckades inte starta appen.")
