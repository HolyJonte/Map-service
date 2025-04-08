from flask import Flask, send_from_directory
import os

# Pekar på din frontend/static-mapp
frontend_path = os.path.join(os.path.dirname(__file__), '../frontend/static')

app = Flask(__name__, static_folder=frontend_path)

@app.route('/')
def serve_index():
    return send_from_directory(frontend_path, 'index.html')

# Tillåt statiska filer att laddas automatiskt
@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(frontend_path, filename)

if __name__ == '__main__':
    app.run(debug=True)
