# Denna modul hanterar  CRUD-operationer för tabellen "pending_subscribers" i databasen.
# som används för att lagra prenumeranter som ännu inte bekräftats.
# Funktionerna i denna modul inkluderar:
# - Lägga till en väntande prenumerant
# - Hämta eller ta bort en väntande prenumerant baserat på session_id
# - Hämta alla väntande prenumeranter


# Importerar SQLite-modulen för databasoperationer
import sqlite3

# Funktion för att öppna en databasanslutning (finns i database.py)
from database.database import get_db_connection

# Importerar modellen som representerar en väntande prenumerant
from database.models.pending_model import PendingSubscriber


# ===================================================================================================
# Lägg till en väntande prenumerant
# ===================================================================================================
def add_pending_subscriber(session_id, user_id, phone_number, email, county, newspaper_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            DELETE FROM pending_subscribers WHERE phone_number = ?
        ''', (phone_number,))

        cursor.execute('''
            INSERT INTO pending_subscribers (session_id, user_id, phone_number, email, county, newspaper_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (session_id, user_id, phone_number, email, county, newspaper_id))

        conn.commit()
        return True
    except sqlite3.IntegrityError:
        conn.rollback()
        return False
    finally:
        conn.close()


# ====================================================================================================
# Hämta en väntande prenumerant baserat på session_id
# ====================================================================================================
def get_pending_subscriber(session_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT session_id, user_id, phone_number, email, county, newspaper_id, created_at
        FROM pending_subscribers
        WHERE session_id = ?
    ''', (session_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return PendingSubscriber(
            session_id=row["session_id"],
            user_id=row["user_id"],
            phone_number=row["phone_number"],
            email=row["email"],
            county=row["county"],
            newspaper_id=row["newspaper_id"],
            created_at=row["created_at"]
        )
    return None


# ===================================================================================================
# Ta bort en väntande prenumerant med session_id
# ===================================================================================================
def delete_pending_subscriber(session_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM pending_subscribers WHERE session_id = ?', (session_id,))
    conn.commit()
    conn.close()



# ===================================================================================================
# Hämta alla väntande prenumeranter
# ===================================================================================================
def get_all_pending_subscribers():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM pending_subscribers')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]