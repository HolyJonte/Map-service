import pyotp
import qrcode
import base64
from io import BytesIO

def generate_user_qr_base64(user):
    # Använd en unik secret per användare eller en gemensam test-secret
    secret = user.get("totp_secret")
    if not secret:
        secret = pyotp.random_base32()
        user["totp_secret"] = secret
        save_users()  # du behöver spara den nya hemliga nyckeln!

    totp = pyotp.TOTP(secret)
    uri = totp.provisioning_uri(name=user['email'], issuer_name="TrafikVida")

    # Skapa QR-kod
    img = qrcode.make(uri)
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return img_base64
