"""
För att titta vad som finns i databasen, kör:
python inspect_db.py
"""

import sqlite3

conn = sqlite3.connect("trafikvida.db")
cursor = conn.cursor()

# Visa innehåll i varje tabell
def inspect_table(table_name):
    print(f"\n📋 Innehåll i tabellen {table_name}:")
    try:
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        if rows:
            for row in rows:
                print(row)
        else:
            print("– Inga rader hittades.")
    except Exception as e:
        print(f"⚠️ Kunde inte läsa tabellen {table_name}: {e}")

# Lista av tabeller att inspektera
tables = [
    "sms_logs",
    "newspapers",
    "users",
    "subscribers",
    "pending_subscribers"
]

for table in tables:
    inspect_table(table)

# Förklaring vad alla kolumner betyder
print("")
print("Subscribers har de här kolumnerna:")
print("id, user_id, phone_number, county, newspaper_id, active, subscription_start, last_payment, klarna_token")
print("Pednding Subscribers har de här kolumnerna:")
print("session_id, user_id, phone_number, county, newspaper_id, created_at")
conn.close()
