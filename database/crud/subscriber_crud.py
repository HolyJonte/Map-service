import sqlite3
from database.database import get_db_connection
from database.models.subscriber_model import Subscriber
from datetime import datetime, timedelta


# Kolla om en prenumerant redan finns i subscribers-tabellen
def subscriber_exists(phone_number):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM subscribers WHERE phone_number = ?', (phone_number,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None


# Lägger till en ny prenumerant i subscribers-tabellen
def add_subscriber(phone_number, user_id, county, newspaper_id, klarna_token):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO subscribers (phone_number, user_id, county, newspaper_id, active, subscription_start, last_payment, klarna_token) 
            VALUES (?, ?, 1, ?, ?, ?, ?)
        ''', (phone_number, user_id, county, newspaper_id, datetime.now(), datetime.now(), klarna_token))
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
    cursor.execute('''
        UPDATE subscribers
        SET last_payment = ?, active = 1, klarna_token = ?
        WHERE phone_number = ?
    ''', (datetime.now(), klarna_token, phone_number))
    conn.commit()
    conn.close()


# Hämtar en prenumerants Klarna-token baserat på subscriber_id och telefonnummer
def get_subscriber_klarna_token(subscriber_id, phone_number):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT klarna_token FROM subscribers
        WHERE id = ? AND phone_number = ?
    ''', (subscriber_id, phone_number))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None


# Avaktiverar en prenumerant genom att sätta status till inaktiv
def deactivate_subscriber(subscriber_id, phone_number):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE subscribers
        SET active = 0
        WHERE id = ? AND phone_number = ?
    ''', (subscriber_id, phone_number))
    conn.commit()
    conn.close()


# Lägger till en prenumerant manuellt för t.ex. test eller backup
def manual_add_subscriber(phone_number, user_id, county, newspaper_id, active=1, subscription_start=None, last_payment=None, klarna_token=None):
    if subscription_start is None:
        subscription_start = datetime.now().isoformat()
    if last_payment is None:
        last_payment = datetime.now().isoformat()

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO subscribers (phone_number, user_id, county, newspaper_id, active, subscription_start, last_payment, klarna_token)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (phone_number, user_id, county, newspaper_id, active, subscription_start, last_payment, klarna_token))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        conn.rollback()
        return False
    finally:
        conn.close()


# Hämtar alla prenumeranter som Subscriber-objekt
def get_all_subscribers():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM subscribers')
    rows = cursor.fetchall()
    conn.close()
    return [Subscriber(**dict(row)) for row in rows]

## Hämtar en prenumerant baserat på län (county)
def get_subscribers_by_county(county):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM subscribers WHERE county = ?', (county,))
    rows = cursor.fetchall()
    conn.close()
    return [Subscriber(**dict(row)) for row in rows]

# Tar bort prenumeranter som är inaktiva och vars sista betalning var för mer än ett år sedan
def remove_inactive_subscribers():
    conn = get_db_connection()
    cursor = conn.cursor()
    one_year_ago = datetime.now() - timedelta(days=365)
    cursor.execute('''
        DELETE FROM subscribers
        WHERE active = 0 AND last_payment < ?
    ''', (one_year_ago,))
    conn.commit()
    conn.close()
