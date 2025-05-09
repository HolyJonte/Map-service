# Denna modul ansvarar för att logga SMS-meddelanden i databasen som skickats från systemet till prenumeranter.
# Den loggar:
# - Vilken tidning som skickat meddelandet
# - Till vilken prenumerant
# - Mottagarens nummer samt själva meddelandet

# Importerar funktion för att skapa en databasanslutning
from database.database import get_db_connection

# =========================================================================================
# SMS-log funktion
# =========================================================================================

# Denna funktion loggar ett SMS-meddelande i databasen.
def log_sms(newspaper_id, subscriber_id, recipient, message):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO sms_logs (newspaper_id, subscriber_id, recipient, message)
        VALUES (?, ?, ?, ?)
    ''', (newspaper_id, subscriber_id, recipient, message))
    conn.commit()
    conn.close()

# Denna funktion hämtar alla SMS-loggar från databasen.
def get_sms_count_for_newspaper(newspaper_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT COUNT(*) AS sms_count
        FROM sms_logs
        WHERE newspaper_id = ?
    ''', (newspaper_id,))
    result = cursor.fetchone()
    conn.close()
    return result["sms_count"] if result else 0