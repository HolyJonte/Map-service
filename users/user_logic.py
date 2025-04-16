import pyotp
import qrcode
import base64
from io import BytesIO

from database.crud.user_crud import (
    create_user,
    get_user_by_email,
    validate_user_login,
    verify_user_2fa_code
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
    return get_user_by_email(email)

def register_user(email, password):
    secret = pyotp.random_base32()
    success = create_user(email, password, secret)
    if success:
        return get_user_by_email(email)
    return None


def validate_login(email, password):
    return validate_user_login(email, password)


def verify_totp_code(user, code):
    return verify_user_2fa_code(user, code)

