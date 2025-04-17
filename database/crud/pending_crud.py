import sqlite3
from database.database import get_db_connection
from database.models.pending_model import PendingSubscriber


# Lägger till en väntande prenumerant i pending_subscribers-tabellen
# Tar också bort eventuell gammal rad för detta telefonnummer och lägger in ny
def add_pending_subscriber(session_id, phone_number, county):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Ta bort eventuell gammal rad för detta telefonnummer
        cursor.execute('''
            DELETE FROM pending_subscribers WHERE phone_number = ?
        ''', (phone_number,))

        # Lägg in ny pending-rad
        cursor.execute('''
            INSERT INTO pending_subscribers (session_id, phone_number, county)
            VALUES (?, ?, ?)
        ''', (session_id, phone_number, county))

        conn.commit()
        return True
    except sqlite3.IntegrityError:
        conn.rollback()
        return False
    finally:
        conn.close()


# Hämtar en väntande prenumerant baserat på session_id
def get_pending_subscriber(session_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT session_id, phone_number, county, created_at
        FROM pending_subscribers
        WHERE session_id = ?
    ''', (session_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return PendingSubscriber(
            session_id=row["session_id"],
            phone_number=row["phone_number"],
            county=row["county"],
            created_at=row["created_at"]
        )
    return None


# Tar bort en väntande prenumerant baserat på session_id
def delete_pending_subscriber(session_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM pending_subscribers WHERE session_id = ?', (session_id,))
    conn.commit()
    conn.close()
