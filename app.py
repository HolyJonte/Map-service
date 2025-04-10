# Denna fil är huvudfilen för Flask-applikationen.
# Den startar servern, registrerar blueprints och hanterar statiska filer från 
# frontend-delen (HTML, JS, CSS).

# Importerar systemmodulen för att hantera sökvägar
import sys
# Importerar os-modulen för att hantera filsystemet
import os
# Importerar Flask och render_template
from flask import Flask, render_template, send_from_directory
# Importerar trafik_bp från routes-modulen, som innehåller kameror-endpointen
from api.routes import trafik_bp

# Lägg till projektroten så att Python hittar andra moduler/mappar
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Anger sökvägen till frontend-mappen där statiska filer finns (tex index, JS och CSS)
frontend_path = os.path.join(os.path.dirname(__file__), '../frontend/static')

# Skapar en Flask-applikation och anger sökvägen till frontend-mappen som statisk mapp
app = Flask(
    __name__,
    static_folder='frontend/static',
    template_folder='frontend/templates'
    )


# Registrerar trafik_bp (kameror-endpointen) som en blueprint i Flask-applikationen
app.register_blueprint(trafik_bp)

# Definierar en route för att servera index.html-filen från frontend-mappen
@app.route('/')
def serve_index():
    return render_template("index.html")

# Definierar en route för att servera andra statiska filer (tex JS, CSS) från frontend-mappen
@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(frontend_path, filename)

# Om detta skript körs direkt, starta Flask-servern
if __name__ == '__main__':
    app.run(debug=True)

