# Denna modul hanterar CRUD-operationer för tidningar i databasen.
# Den ansvarar för:
# - Hämta alla tidningar
# - Lägga till en ny tidning
# - Ta bort en tidning


# Importera sqlite3 för databasoperationer
import sqlite3

# Funktion för att öppna en databasanslutning (finns i database.py)
from database.database import get_db_connection

# Importera Newspaper-modellen (finns i newspaper_model.py)
from database.models.newspaper_model import Newspaper

# =========================================================================================
# Newspaper-funktioner
# =========================================================================================

# Hämtar alla tidningar från databasen
def get_all_newspapers():
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


# Hämtar alla tidningar som ett dictionary med ID som nyckel och namn som värde
def get_all_newspaper_names():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, name FROM newspapers')
        rows = cursor.fetchall()
        conn.close()
        return {str(row['id']): row['name'] for row in rows}
    except Exception as e:
        return {}

# Lägger till en ny tidning i databasen
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

# Tar bort en tidning från databasen med ID
def delete_newspaper(newspaper_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM newspapers WHERE id = ?', (newspaper_id,))
    conn.commit()
    conn.close()

