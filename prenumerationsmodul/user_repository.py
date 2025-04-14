# user_database.py
import sqlite3
from datetime import datetime, timedelta

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