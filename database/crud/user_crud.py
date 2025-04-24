# Denna modul hanterar allt kring användare i databasen såsom:
# - Skapa ny användare med hashat lösenord och TOTP-secret
# - Hämta användare med e-post
# - Validera inloggning (lösenord och 2FA)


# Importerar SQLite-modulen för databasoperationer
import sqlite3
# Importerar pyotp för TOTP-verifiering
import pyotp

# Funktion för att öppna en databasanslutning (finns i database.py)
from database.database import get_db_connection

# Lösenordssäkerhetsfunktioner från werkzeug
from werkzeug.security import generate_password_hash, check_password_hash
# Importerar modellen som representerar en användare
from database.models.user_model import User


# =========================================================================================
# Skapa ny användare
# =========================================================================================

def create_user(email, password, totp_secret):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        hashed_pw = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO users (email, password, totp_secret) VALUES (?, ?, ?)",
            (email, hashed_pw, totp_secret)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Användaren finns redan
    finally:
        conn.close()


# ===========================================================================================
# Hämtar användare via e-post
# ===========================================================================================
def get_user_by_email(email):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return User(
            id=row["id"],
            email=row["email"],
            password=row["password"],
            totp_secret=row["totp_secret"]
        )
    return None



#=============================================================================================
#  Validerar inloggning med e-post och lösenord.
#=============================================================================================
def validate_user_login(email, password):
    user = get_user_by_email(email)
    if user and check_password_hash(user.password, password):
        return user
    return None



# =============================================================================================
# Verifierar 2FA-kod
# =============================================================================================
def verify_user_2fa_code(user, code):
    return pyotp.TOTP(user.totp_secret).verify(code)
