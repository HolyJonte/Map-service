from flask import Blueprint, render_template, request, redirect, url_for, session
import os, json
import pyotp
import qrcode
from io import BytesIO
import base64
from werkzeug.security import generate_password_hash, check_password_hash
from users.user_logic import generate_user_qr_base64


# Skapa blueprint för användarrelaterade routes
user_routes = Blueprint('user_routes', __name__, template_folder='../frontend/templates')

# Sökväg till filen där användardata sparas
USER_FILE = os.path.join(os.path.dirname(__file__), 'users.json')

# ===============================
# Hjälpfunktioner
# ===============================

# Läser in alla användare från JSON-filen
def load_users():
    if not os.path.exists(USER_FILE):
        return []
    with open(USER_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

# Sparar användardata till JSON-filen
def save_users(users):
    with open(USER_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=2)

# ===============================
# Registrering av ny användare
# ===============================

@user_routes.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        users = load_users()

        # Kolla om e-posten redan finns
        if any(u['email'] == email for u in users):
            return render_template('user_register.html', error="E-post finns redan")

        # Skapa hemlig nyckel för TOTP
        totp_secret = pyotp.random_base32()
        hashed_pw = generate_password_hash(password)

        # Lägg till ny användare
        users.append({
            'email': email,
            'password': hashed_pw,
            'totp_secret': totp_secret
        })
        save_users(users)

        # Spara nödvändiga session-data för att visa QR och 2FA
        session['user_email'] = email
        session['user_awaiting_2fa'] = True
        session['show_user_qr'] = True
        return redirect(url_for('user_routes.show_user_qr'))

    return render_template('user_register.html')

# ===============================
# Inloggning av befintlig användare
# ===============================

@user_routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        users = load_users()

        # Hitta användaren
        user = next((u for u in users if u['email'] == email), None)

        if user and check_password_hash(user['password'], password):
            # Gå vidare till 2FA
            session['user_email'] = email
            session['user_awaiting_2fa'] = True
            return redirect(url_for('user_routes.verify_user_2fa'))

        return render_template('user_login.html', error="Fel e-post eller lösenord")

    return render_template('user_login.html')

# ===============================
# Visa QR-kod för 2FA
# ===============================

@user_routes.route('/show-qr')
def show_user_qr():
    if not session.get('user_awaiting_2fa'):
        return redirect(url_for('user_routes.login'))

    email = session.get('user_email')
    users = load_users()
    user = next((u for u in users if u['email'] == email), None)

    if not user:
        return redirect(url_for('user_routes.login'))

    qr_data = generate_user_qr_base64(user)

    return render_template('user_show_qr.html', qr_data=qr_data)






# ===============================
# Verifiera engångskod från Authenticator
# ===============================

@user_routes.route('/users/2fa', methods=['GET', 'POST'])
def verify_user_2fa():
    if not session.get('user_awaiting_2fa'):
        return redirect(url_for('user_routes.login'))

    email = session.get('user_email')
    users = load_users()
    user = next((u for u in users if u['email'] == email), None)

    if request.method == 'POST':
        code = request.form.get('code')

        if user and pyotp.TOTP(user['totp_secret']).verify(code):
            session.pop('user_awaiting_2fa', None)
            session['user_logged_in'] = True
            return redirect(url_for('serve_index'))

        return render_template('user_2fa.html', error="Fel kod")

    return render_template('user_two_factor.html')
