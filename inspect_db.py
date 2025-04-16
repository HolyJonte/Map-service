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
    "newspapers",
    "users",
    "subscribers",
    "pending_subscribers"
]

for table in tables:
    inspect_table(table)

conn.close()
