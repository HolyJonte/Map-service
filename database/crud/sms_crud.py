from database.database import get_db_connection

# =========================================================================================
# SMS-log funktion
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