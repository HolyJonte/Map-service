import pyotp
import qrcode
import base64
from io import BytesIO

from prenumerationsmodul.repository import (
    create_user as db_create_user,
    get_user_by_email as db_get_user_by_email,
    validate_user_login as db_validate_login,
    verify_user_2fa_code as db_verify_code
)

# ===========================
# Generera QR-kod för en användare
# ===========================
def generate_user_qr_base64(user):
    secret = user.get("totp_secret")
    if not secret:
        return None  # Kan ej skapa QR utan secret

    totp = pyotp.TOTP(secret)
    uri = totp.provisioning_uri(name=user['email'], issuer_name="TrafikVida")

    img = qrcode.make(uri)
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    return base64.b64encode(buffer.getvalue()).decode('utf-8')

# ===========================
# Hjälpmetoder
# ===========================
def find_user_by_email(email):
    return db_get_user_by_email(email)

def create_user(email, password):
    secret = pyotp.random_base32()
    success = db_create_user(email, password, secret)
    if success:
        return db_get_user_by_email(email)
    return None

def validate_login(email, password):
    return db_validate_login(email, password)

def verify_totp_code(user, code):
    return db_verify_code(user, code)
