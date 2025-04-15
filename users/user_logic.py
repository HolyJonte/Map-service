# users/user_logic.py

import pyotp
import qrcode
from io import BytesIO
import base64

def generate_user_qr_base64(user):
    uri = pyotp.TOTP(user['totp_secret']).provisioning_uri(
        name=user['email'],
        issuer_name="TrafikVida"
    )
    img = qrcode.make(uri)
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode('utf-8')
