# Denna modul innehåller logik för admin-funktioner: autentisering, QR-kod, 2FA och hantering av tidningar.

import os
import pyotp
import qrcode
from database.crud.subscriber_crud import get_all_subscribers
from database.crud.newspaper_crud import (
    get_all_newspapers as db_get_all_newspapers,
    add_newspaper as db_add_newspaper,
    delete_newspaper as db_delete_newspaper
)


# ================================
# Konfiguration
# ================================

ADMIN_PASSWORD = "hemligt123"
TOTP_SECRET = "JBSWY3DPEHPK3PXP"

# ================================
# Lösenordshantering
# ================================

def get_admin_password():
    return ADMIN_PASSWORD

# ================================
# Tidningshantering (via databas)
# ================================

def get_all_newspapers():
    return db_get_all_newspapers()

def add_newspaper(name, contact_email=None, sms_quota=None):
    return db_add_newspaper(name, contact_email, sms_quota)

def delete_newspaper(newspaper_id):
    return db_delete_newspaper(newspaper_id)


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
