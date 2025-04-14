import os
import json
import pyotp
import qrcode

# Hårdkodat lösenord
ADMIN_PASSWORD = "hemligt123"

# Sökväg till newspapers.json
BASE_DIR = os.path.dirname(__file__)
JSON_PATH = os.path.join(BASE_DIR, 'newspapers.json')

def get_admin_password():
    return ADMIN_PASSWORD

def load_newspapers():
    if not os.path.exists(JSON_PATH):
        return []
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_newspapers(papers):
    with open(JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(papers, f, ensure_ascii=False, indent=2)

# Hemlig nyckel för TOTP – denna måste alltid vara samma
TOTP_SECRET = "JBSWY3DPEHPK3PXP"  # Du kan byta till annan base32-sträng

# Skapar URI som scannas av Authenticator-appar
def get_totp_uri():
    return pyotp.totp.TOTP(TOTP_SECRET).provisioning_uri(
        name="admin@trafikvida",
        issuer_name="TrafikVida"
    )

# Skapar QR-kod som kan skannas av användare
def generate_qr(path="admin/admin_qr.png"):
    uri = get_totp_uri()
    img = qrcode.make(uri)
    img.save(path)
    print(f"[QR-KOD] Sparad som {path}. Skanna med Authenticator.")

# Verifierar kod som användaren skriver in
def verify_totp_code(code):
    return pyotp.TOTP(TOTP_SECRET).verify(code)
