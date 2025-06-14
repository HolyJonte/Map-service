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
def add_subscriber(phone_number, email, user_id, county, newspaper_id, klarna_token):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO subscribers (phone_number, email, user_id, county, newspaper_id, active, klarna_token)
            VALUES (?, ?, ?, ?, ?, 1, ?)
        ''', (phone_number, email, user_id, county, newspaper_id, klarna_token))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        conn.rollback()
        return False
    finally:
        conn.close()


#========================================================================================================================
# Uppdaterar en befintlig prenumerants status och betalningsdatum
#========================================================================================================================
def update_subscriber(phone_number, klarna_token, subscription_start):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE subscribers
        SET last_payment = ?, subscription_start= ?, klarna_token = ?
        WHERE phone_number = ?
    ''', (datetime.now(), subscription_start.strftime('%Y-%m-%d %H:%M:%S'), klarna_token, phone_number))
    conn.commit()
    conn.close()



#==========================================================================================================================
# Sätter en prenumerant till inaktiv om ett år gått och ej förnyat, använder tid och last_payment. Körs som Task i bakgrunden
#==========================================================================================================================
def deactivate_expired_subscribers():
    cutoff = datetime.now() - timedelta(days=365)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE subscribers
        SET active = 0
        WHERE active = 1 AND last_payment < ?
    ''', (cutoff,))
    conn.commit()
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
    like_pattern = f"%,{county_str},%"
    like_start = f"{county_str},%"
    like_end = f"%,{county_str}"
    like_exact = f"{county_str}"

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
# Tar bort prenumeranter som redan är inaktiva och inte betalat på mer än två år
#===============================================================================================================================
def remove_inactive_subscribers():
    conn = get_db_connection()
    cursor = conn.cursor()
    one_year_ago = datetime.now() - timedelta(days=730)
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
                subscriber_id = int(subscriber_id)
            except (TypeError, ValueError):
                print(f"Ogiltig subscriber_id-typ: {type(subscriber_id)}, värde: {subscriber_id}")
                return False

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM subscribers
            WHERE id = ?
        ''', (subscriber_id,))
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success
    except Exception as e:
        print(f"Fel i delete_subscriber: {str(e)}")
        return False


#========================================================================================================================
# Hämta prenumeranter med prenumeration som går ut om 14 dagar
#========================================================================================================================
def get_subscriptions_due_in_14_days():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM subscribers WHERE date(subscription_start) = date('now', '-351 days')")
    rows = cursor.fetchall()
    conn.close()
    return [Subscriber(**dict(row)) for row in rows]