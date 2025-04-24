# Denna modul ansvarar för att logga SMS-meddelanden i databasen som skickats från systemet till prenumeranter.
# Den loggar:
# - Vilken tidning som skickat meddelandet
# - Till vilken prenumerant
# - Mottagarens nummer samt själva meddelandet

# Importerar funktion för att skapa en databasanslutning
from database.database import get_db_connection

# =========================================================================================
# SMS-log funktion
# Lagrar information om ett skickat SMS i tabellen sms_logs.
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