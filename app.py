# Denna fil är huvudfilen för Flask-applikationen.
# Den startar servern, registrerar blueprints och hanterar statiska filer från 
# frontend-delen (HTML, JS, CSS).

# Importerar systemmodulen för att hantera sökvägar
import sys
# Importerar os-modulen för att hantera filsystemet
import os
# Importerar Flask och render_template
from flask import Flask, render_template, send_from_directory
from apscheduler.schedulers.background import BackgroundScheduler
# Importerar trafik_bp från routes-modulen, som innehåller kameror-endpointen
from api.routes import trafik_bp
# Importerar subscription_routes
from prenumerationsmodul.subscription_routes import subscription_routes
#Importerar admin_routes
from admin.admin_routes import admin_routes

from users.user_routes import user_routes

# Importerar APScheduler för schemaläggning

# Importerar notify_accidents för att schemalägga SMS-notifikationer
from prenumerationsmodul.notifications import notify_accidents

# Lägg till projektroten så att Python hittar andra moduler/mappar
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Anger sökvägen till frontend-mappen där statiska filer finns (tex index, JS och CSS)
frontend_path = os.path.join(os.path.dirname(__file__), '../frontend/static')

### KANSKE BEHÖVER ÄNDRA FÖR DE LIGGER UNDER FRONTEND
templates_path = os.path.join(os.path.dirname(__file__), 'templates')

# Skapar en Flask-applikation och anger sökvägen till frontend-mappen som statisk mapp
app = Flask(
    __name__,
    static_folder='frontend/static',
    template_folder='frontend/templates'
    )

app.secret_key = "byt-ut-till-något-säkert"

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

@app.route('/login')
def login_choice():
    return render_template("login_choice.html")




# Skapa en scheduler för att köra notify_accidents var 5:e minut
scheduler = BackgroundScheduler()

# ÄNDRA DETTA TILL 5 MIN  OCH MAX_INSTANCES TILL 1!!!
scheduler.add_job(notify_accidents, 'interval', minutes=5, max_instances=1)
# Starta scheduler innan servern startar
scheduler.start()
# Om detta skript körs direkt, starta Flask-servern
if __name__ == '__main__':
    try:
        app.run(debug=True)
    except (KeyboardInterrupt, SystemExit):
        # Stäng av scheduler vid avbrott
        scheduler.shutdown()
