# user_database.py
import sqlite3
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import pyotp


## BEHÖVER LÄGGA TILL: Schemaläggare av betalningar så att man årsvis kallar på create_recurring_order
### för de prenumeranter där ett år passerat
### BEHÖVER LÄGGA TILL: get_subscribers_by_county för att kunna hämta prenumeranter per län

# Initierar SQLite-databasen och skapar nödvändiga tabeller
def initialize_database():
    conn = sqlite3.connect("trafikvida.db")
    cursor = conn.cursor()
    # Skapa tabellen för prenumeranter
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscribers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,  
            phone_number TEXT UNIQUE NOT NULL,  
            county INTEGER NOT NULL,  
            active INTEGER DEFAULT 1,  
            subscription_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  
            last_payment TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  
            klarna_token TEXT  
        )
    ''')
    # Skapa tabellen för väntande prenumeranter innan betalning gått igenom
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pending_subscribers (
            session_id TEXT PRIMARY KEY,  
            phone_number TEXT NOT NULL,  
            county INTEGER NOT NULL,  
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  
        )
    ''')

# =========================================================================================
# Newpapers (Madde och Jontes del)
# =========================================================================================

    # Skapa tabell för admin för att lägga till och tabort tidningar
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS newspapers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            contact_email TEXT,
            sms_quota INTEGER
        )
    ''')

    # Skapa tabell för users för registrering och inloggning
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            totp_secret TEXT NOT NULL
        )
    ''')

    # Skapa tabell för sms-loggar
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sms_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        newspaper_id INTEGER NOT NULL,
        subscriber_id INTEGER NOT NULL,
        recipient TEXT NOT NULL,
        message TEXT NOT NULL,
        sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (newspaper_id) REFERENCES newspapers(id),
        FOREIGN KEY (subscriber_id) REFERENCES subscribers(id)
    )
''')



# =========================================================================================
# Avslut
# =========================================================================================
    conn.commit()
    conn.close()

# Skapar en anslutning till SQLite-databasen
def get_db_connection():
    conn = sqlite3.connect("trafikvida.db")
    return conn
# Lägger till en väntande prenumerant i pending_subscribers-tabellen
def add_pending_subscriber(session_id, phone_number, county):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO pending_subscribers (session_id, phone_number, county) VALUES (?, ?, ?)',
                       (session_id, phone_number, county))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()
# Hämtar en väntande prenumerant baserat på session_id
def get_pending_subscriber(session_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT phone_number, county FROM pending_subscribers WHERE session_id = ?', (session_id,))
    result = cursor.fetchone()
    conn.close()
    return result
# Tar bort en väntande prenumerant baserat på session_id
def delete_pending_subscriber(session_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM pending_subscribers WHERE session_id = ?', (session_id,))
    conn.commit()
    conn.close()
# Kolla om en prenumerant redan finns i subscribers-tabellen
def subscriber_exists(phone_number):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM subscribers WHERE phone_number = ?', (phone_number,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None
# Lägger till en ny prenumerant i subscribers-tabellen
def add_subscriber(phone_number, county, klarna_token):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO subscribers (phone_number, county, active, subscription_start, last_payment, klarna_token) 
            VALUES (?, ?, 1, ?, ?, ?)
        ''', (phone_number, county, datetime.now(), datetime.now(), klarna_token))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        conn.rollback()
        return False
    finally:
        conn.close()
# Uppdaterar en befintlig prenumerants status och betalningsdatum
def update_subscriber(phone_number, klarna_token):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE subscribers SET last_payment = ?, active = 1, klarna_token = ? WHERE phone_number = ?',
                   (datetime.now(), klarna_token, phone_number))
    conn.commit()
    conn.close()
# Hämtar en prenumerants Klarna-token baserat på subscriber_id och telefonnummer
def get_subscriber_klarna_token(subscriber_id, phone_number):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT klarna_token FROM subscribers WHERE id = ? AND phone_number = ?', 
                   (subscriber_id, phone_number))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None
# Avaktiverar en prenumerant genom att sätta status till inaktiv
def deactivate_subscriber(subscriber_id, phone_number):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE subscribers SET active = 0 WHERE id = ? AND phone_number = ?', 
                   (subscriber_id, phone_number))
    conn.commit()
    conn.close()
# Lägga till en prenumerant manuellt i subscribers-tabellen för test eller backup
def manual_add_subscriber(phone_number, county, active=1, subscription_start=None, last_payment=None, klarna_token=None):
    if subscription_start is None:
        subscription_start = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if last_payment is None:
        last_payment = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO subscribers (phone_number, county, active, subscription_start, last_payment, klarna_token)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (phone_number, county, active, subscription_start, last_payment, klarna_token))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        conn.rollback()
        return False
    finally:
        conn.close()
# Hämtar alla prenumeranter från subscribers-tabellen
def get_all_subscribers():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM subscribers')
    subscribers = cursor.fetchall()
    columns = [description[0] for description in cursor.description]
    result = [dict(zip(columns, row)) for row in subscribers]
    conn.close()
    return result
# Tar bort prenumeranter som är inaktiva och vars sista betalning var för mer än ett år sedan
def remove_inactive_subscribers():
    """
    Tar bort prenumeranter som är inaktiva och vars sista betalning var för mer än ett år sedan.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    one_year_ago = datetime.now() - timedelta(days=365)
    cursor.execute('DELETE FROM subscribers WHERE active = 0 AND last_payment < ?', (one_year_ago,))
    conn.commit()
    conn.close()
    
    #Hämtar prenumeranter per län
""" def get_subscribers_by_county(county):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT phone_number FROM subscribers WHERE county = ? AND active = 1', (county,))
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows] """


# =========================================================================================
# Newpaper funktion (Madde och Jontes del)
# =========================================================================================
def get_all_newspapers():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, contact_email, sms_quota FROM newspapers')
    rows = cursor.fetchall()
    conn.close()
    return [dict(zip(['id', 'name', 'contact_email', 'sms_quota'], row)) for row in rows]

def add_newspaper(name, contact_email=None, sms_quota=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO newspapers (name, contact_email, sms_quota) 
            VALUES (?, ?, ?)
        ''', (name, contact_email, sms_quota))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def delete_newspaper(newspaper_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM newspapers WHERE id = ?', (newspaper_id,))
    conn.commit()
    conn.close()


# =========================================================================================
# User funktion (Madde och Jontes del)
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
        return False  # Användare finns redan
    finally:
        conn.close()

def get_user_by_email(email):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "id": row[0],
            "email": row[1],
            "password": row[2],
            "totp_secret": row[3]
        }
    return None

def validate_user_login(email, password):
    user = get_user_by_email(email)
    if user and check_password_hash(user["password"], password):
        return user
    return None

def verify_user_2fa_code(user, code):
    return pyotp.TOTP(user["totp_secret"]).verify(code)



# =========================================================================================
# SMS-log funktion (Madde och Jontes del)
# =========================================================================================
def log_sms(newspaper_id, subscriber_id, recipient, message):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO sms_logs (newspaper_id, subscriber_id, recipient, message)
        VALUES (?, ?, ?, ?)
    ''', (newspaper_id, subscriber_id, recipient, message))
    conn.commit()
    conn.close()
