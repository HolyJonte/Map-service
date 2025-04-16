import sqlite3
import pyotp
from database.database import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash
from database.models.user_model import User


# =========================================================================================
# User-funktioner
# =========================================================================================

def create_user(email, password, totp_secret):
    """
    Skapar en ny användare med hashat lösenord och TOTP-secret.
    """
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


def get_user_by_email(email):
    """
    Hämtar en användare med hjälp av e-postadress.
    Returnerar en User-instans eller None.
    """
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


def validate_user_login(email, password):
    """
    Validerar inloggning med e-post och lösenord.
    Returnerar användaren om korrekt, annars None.
    """
    user = get_user_by_email(email)
    if user and check_password_hash(user.password, password):
        return user
    return None


def verify_user_2fa_code(user, code):
    """
    Verifierar 2FA-koden från användarens TOTP-secret.
    """
    return pyotp.TOTP(user.totp_secret).verify(code)
