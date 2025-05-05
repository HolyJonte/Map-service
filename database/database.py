# Denna fil styr hur databasen skapas upp och hur tabellerna som finns i den ska se ut.
# Efter att tabellerna har skapats upp eller om de redan finns så kommer den att
# hårdkoda in 3 tidningar och en användare i databasen. Detta är endast för testning.
# När allt är klart så kommer den att stänga ner databasen.
# =========================================================================================
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
            totp_secret TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0
        )
    ''')

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

# =========================================================================================
# Skapar en admin och lägger in den i databasen (ska vara kvar i slutversionen)
# =========================================================================================

    # Lägger in en adminanvändare med hashat lösenord för 'hemligt123'
    admin_user = (
        "admin@trafikvida.se",
        "scrypt:32768:8:1$uXeUgDr1LfYWGC8l$05f8c449a9d7b48aea4e0dfd30de987969406a591abc7323372c1c81bdbdd9483c6dc384a5644671a7af923750039932cfbbc4ebc033a8b6834263048f59e472",
        "GJLQJC35LECNNZE6SYSR6HNSSBVJOPN6",
        1
    )

    cursor.execute('''
        INSERT OR IGNORE INTO users (email, password, totp_secret, is_admin)
        VALUES (?, ?, ?, ?)
    ''', admin_user)

# =========================================================================================
# Fyller tabellen med innehåll (för testning)
# =========================================================================================
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

    # Hårdkodar in en användare (TA BORT SEDAN)
    default_user = ("testuser@example.com", "hashed_password", "totp_secret_123")
    cursor.execute('''
        INSERT OR IGNORE INTO users (email, password, totp_secret)
        VALUES (?, ?, ?)
    ''', default_user)

    # Hämta user_id för default-användaren (TA BORT SEDAN)
    cursor.execute("SELECT id FROM users WHERE email = ?", (default_user[0],))
    user = cursor.fetchone()
    if not user:
        raise Exception("Kunde inte skapa eller hitta default-användaren!")
    user_id = user["id"]

    # Hårdkodar in en prenumerant för county = 1 (TA BORT SEDAN)
    default_subscriber = (user_id, "+46701234567", 1, 1, "test_klarna_token")
    cursor.execute('''
        INSERT OR IGNORE INTO subscribers (user_id, phone_number, county, newspaper_id, klarna_token)
        VALUES (?, ?, ?, ?, ?)
    ''', default_subscriber)

    conn.commit()
    conn.close()
