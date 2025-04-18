import sqlite3
from database.database import get_db_connection
from database.models.newspaper_model import Newspaper

# =========================================================================================
# Newspaper-funktioner
# =========================================================================================

def get_all_newspapers():
    """
    Hämtar alla tidningar som Newspaper-objekt.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM newspapers')
    rows = cursor.fetchall()
    conn.close()
    return [
        Newspaper(
            id=row["id"],
            name=row["name"],
            contact_email=row["contact_email"],
            sms_quota=row["sms_quota"]
        ) for row in rows
    ]
def get_all_newspaper_names():
    """
    Hämtar alla tidningar som en dict med namn.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM newspapers')
    rows = cursor.fetchall()
    
    conn.close()
    return {str(row['id']): row['name'] for row in rows} # Omvandla till strängar för att matcha JSON-formatet


def add_newspaper(name, contact_email=None, sms_quota=None):
    """
    Lägger till en ny tidning i databasen.
    """
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
    """
    Tar bort en tidning från databasen med ID.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM newspapers WHERE id = ?', (newspaper_id,))
    conn.commit()
    conn.close()
