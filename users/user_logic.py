import pyotp
import qrcode
import base64
import json
import os
from io import BytesIO
from werkzeug.security import generate_password_hash, check_password_hash

# Sökväg till filen där användardata sparas
BASE_DIR = os.path.dirname(__file__)
USER_FILE = os.path.join(BASE_DIR, 'users.json')

# ===========================
# Ladda och spara användare
# ===========================
def load_users():
    if not os.path.exists(USER_FILE):
        return []
    with open(USER_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_users(users):
    with open(USER_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=2)

# ===========================
# Generera QR-kod för en användare
# ===========================
def generate_user_qr_base64(user):
    secret = user.get("totp_secret")
    if not secret:
        secret = pyotp.random_base32()
        user["totp_secret"] = secret

    totp = pyotp.TOTP(secret)
    uri = totp.provisioning_uri(name=user['email'], issuer_name="TrafikVida")

    img = qrcode.make(uri)
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return img_base64

# ===========================
# Hjälpmetoder
# ===========================
def find_user_by_email(email):
    users = load_users()
    return next((u for u in users if u['email'] == email), None)

def create_user(email, password):
    users = load_users()
    hashed_pw = generate_password_hash(password)
    totp_secret = pyotp.random_base32()
    user = {
        'email': email,
        'password': hashed_pw,
        'totp_secret': totp_secret
    }
    users.append(user)
    save_users(users)
    return user

def validate_login(email, password):
    user = find_user_by_email(email)
    if user and check_password_hash(user['password'], password):
        return user
    return None

def verify_totp_code(user, code):
    return pyotp.TOTP(user['totp_secret']).verify(code)

