# Denna modul innehåller logik för admin-funktioner: autentisering, QR-kod, 2FA och hantering av tidningar.

import os
import json
import pyotp
import qrcode

# ================================
# Konfiguration
# ================================

ADMIN_PASSWORD = "hemligt123"
TOTP_SECRET = "JBSWY3DPEHPK3PXP"
BASE_DIR = os.path.dirname(__file__)
JSON_PATH = os.path.join(BASE_DIR, 'newspapers.json')

# ================================
# Lösenordshantering
# ================================

def get_admin_password():
    return ADMIN_PASSWORD

# ================================
# Tidningshantering
# ================================

def load_newspapers():
    if not os.path.exists(JSON_PATH):
        return []
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_newspapers(papers):
    with open(JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(papers, f, ensure_ascii=False, indent=2)

# ================================
# TOTP och QR-kodshantering
# ================================

def get_totp_uri():
    return pyotp.TOTP(TOTP_SECRET).provisioning_uri(
        name="admin@trafikvida",
        issuer_name="TrafikVida"
    )

def generate_qr_image_base64():
    uri = get_totp_uri()
    img = qrcode.make(uri)
    from io import BytesIO
    import base64
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode('utf-8')

def verify_totp_code(code):
    return pyotp.TOTP(TOTP_SECRET).verify(code)
