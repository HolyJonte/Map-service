import sqlite3

conn = sqlite3.connect("trafikvida.db")
cursor = conn.cursor()

print("🗞️ Innehåll i tabellen newspapers:")
cursor.execute("SELECT * FROM newspapers")
rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()
