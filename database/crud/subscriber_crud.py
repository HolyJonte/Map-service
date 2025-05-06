# Denna modul hanterar CRUD-operationer för prenumenranter i databasen.
# Funktionerna i denna modul inkluderar:
# - Kontrollera om en prenumerant redan finns
# - Lägga till, uppdatera, inaktivera eller manuellet lägga till en prenumerant
# - Hämta prenumeranter baserat på olika kriterier
# - Ta bort inaktiva prenumeranter

# Importerar SQLite-modulen för databasoperationer
import sqlite3

# Funktion för att öppna en databasanslutning (finns i database.py)
from database.database import get_db_connection

#from database.models.sms_model import Subscriber
# Importerar modellen som representerar en prenumerant
from database.models.subscriber_model import Subscriber
# Importerar datetime och timedelta för att hantera datum och tid
from datetime import datetime, timedelta

#====================================================================================================================
# Kolla om en prenumerant redan finns i subscribers-tabellen
#====================================================================================================================
def subscriber_exists(phone_number):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM subscribers WHERE phone_number = ?', (phone_number,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None


#=====================================================================================================================
# Lägger till en ny prenumerant i subscribers-tabellen
#=====================================================================================================================
def add_subscriber(phone_number, user_id, county, newspaper_id, klarna_token):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO subscribers (phone_number, user_id, county, newspaper_id, active, subscription_start, last_payment, klarna_token) 
            VALUES (?, ?, ?, ?, 1, ?, ?, ?)
        ''', (phone_number, user_id, county, newspaper_id, datetime.now(), datetime.now(), klarna_token))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        conn.rollback()
        return False
    finally:
        conn.close()


#========================================================================================================================
# KANSKE ÖVERFLÖDIG???
# Uppdaterar en befintlig prenumerants status och betalningsdatum
#========================================================================================================================
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



#========================================================================================================================
# Hämtar en prenumerants Klarna-token baserat på subscriber_id och telefonnummer
#========================================================================================================================
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

#==========================================================================================================================
# Avaktiverar en prenumerant genom att sätta status till inaktiv
#==========================================================================================================================
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


#============================================================================================================================
# Lägger till en prenumerant manuellt för t.ex. test eller backup
#============================================================================================================================
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
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (phone_number, user_id, county, newspaper_id, active, subscription_start, last_payment, klarna_token))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        conn.rollback()
        return False
    finally:
        conn.close()


#===========================================================================================================================
# Hämtar alla prenumeranter
#===========================================================================================================================
def get_all_subscribers():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM subscribers')
    rows = cursor.fetchall()
    conn.close()
    return [Subscriber(**dict(row)) for row in rows]


#=============================================================================================================================
# Hämtar en prenumerant baserat på län (county)
#=============================================================================================================================
def get_subscribers_by_county(county):
    conn = get_db_connection()
    cursor = conn.cursor()
    county_str = str(county)
    like_pattern = f"%,{county_str},%"  # Mellan två kommatecken
    like_start = f"{county_str},%"      # I början
    like_end = f"%,{county_str}"         # I slutet
    like_exact = f"{county_str}"         # Enda värdet

    cursor.execute('''
        SELECT * FROM subscribers
        WHERE active = 1
        AND (
            county = ?
            OR county LIKE ?
            OR county LIKE ?
            OR county LIKE ?
        )
    ''', (like_exact, like_start, like_end, like_pattern))
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


#===============================================================================================================================
# Tar bort prenumeranter som är inaktiva och vars sista betalning var för mer än ett år sedan
#===============================================================================================================================
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

#===============================================================================================================================
# Hämta subscriber baserat på user_id
#===============================================================================================================================
def get_subscriber_by_user_id(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM subscribers WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    return Subscriber(**dict(row)) if row else None

#========================================================================================================================
# Uppdaterar en prenumerants län
#========================================================================================================================
def update_subscriber_county(subscriber_id, phone_number, new_county):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE subscribers
        SET county = ?
        WHERE id = ? AND phone_number = ?
    ''', (new_county, subscriber_id, phone_number))
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return success

#========================================================================================================================
# Ta bort prenumerant
#========================================================================================================================
def delete_subscriber(subscriber_id):
    try:
        # Kontrollera att subscriber_id är ett heltal
        if not isinstance(subscriber_id, int):
            try:
                subscriber_id = int(subscriber_id)  # Försök konvertera till int
            except (TypeError, ValueError):
                print(f"Ogiltig subscriber_id-typ: {type(subscriber_id)}, värde: {subscriber_id}")
                return False

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM subscribers
            WHERE id = ?
        ''', (subscriber_id,))  # Använd korrekt tuple-syntax
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success
    except Exception as e:
        print(f"Fel i delete_subscriber: {str(e)}")
        return False
    
#========================================================================================================================
# Uppdater inaktiv prenumerant till aktiv
#========================================================================================================================
def update_inactive_subscriber(subscriber_id, phone_number, county, newspaper_id, klarna_token):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            UPDATE subscribers
            SET phone_number = ?, county = ?, newspaper_id = ?, active = 1, 
                subscription_start = ?, last_payment = ?, klarna_token = ?
            WHERE id = ?
        ''', (phone_number, county, newspaper_id, datetime.now(), datetime.now(), klarna_token, subscriber_id))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.IntegrityError:
        conn.rollback()
        return False
    finally:
        conn.close()