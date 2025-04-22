import sqlite3

def get_db_connection():
    conn = sqlite3.connect("trafikvida.db")
    conn.row_factory = sqlite3.Row  # så vi får dict-aktiga rader
    conn.execute("PRAGMA foreign_keys = ON")  # Aktiverar stöd för FOREIGN KEY
    return conn


# =========================================================================================
# Skapar en databas och nödvändiga tabeller om de inte redan finns
# =========================================================================================
def initialize_database():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Skapar subscribers-tabellen
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscribers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            phone_number TEXT UNIQUE NOT NULL,
            county INTEGER NOT NULL,
            newspaper_id INTEGER NOT NULL,
            active INTEGER DEFAULT 1,
            subscription_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_payment TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            klarna_token TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (newspaper_id) REFERENCES newspapers(id)
        )
    ''')

    # Skapar pending_subscribers-tabellen
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pending_subscribers (
            session_id TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            phone_number TEXT UNIQUE NOT NULL,
            county INTEGER NOT NULL,
            newspaper_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (newspaper_id) REFERENCES newspapers(id)
        )
    ''')

    # Skapar newspapers-tabellen
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS newspapers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            contact_email TEXT,
            sms_quota INTEGER
        )
    ''')

    # Skapar users-tabellen
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            totp_secret TEXT NOT NULL
        )
    ''')

    # Skapar sms_logs-tabellen
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sms_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            newspaper_id INTEGER NOT NULL,
            subscriber_id INTEGER NOT NULL,
            recipient TEXT NOT NULL,
            message TEXT NOT NULL,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (newspaper_id) REFERENCES newspapers(id),
            FOREIGN KEY (subscriber_id) REFERENCES subscribers(id)
        )
    ''')

    # Hårdkodar in 3 tidningar om det inte redan finns (TA BORT SEDAN)
    default_newspapers = [
        ("Dagbladet", "kontakt@dagbladet.se", 1000),
        ("NyhetsPosten", "redaktion@nyhetsposten.se", 750),
        ("Sverige Idag", "info@sverigeidag.se", 500)
    ]

    for name, email, quota in default_newspapers:
        cursor.execute('''
            INSERT OR IGNORE INTO newspapers (name, contact_email, sms_quota)
            VALUES (?, ?, ?)
        ''', (name, email, quota))


    conn.commit()
    conn.close()
