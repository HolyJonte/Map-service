import sqlite3

def get_db_connection():
    conn = sqlite3.connect("trafikvida.db")
    conn.row_factory = sqlite3.Row  # så vi får dict-aktiga rader
    return conn

def initialize_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscribers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone_number TEXT UNIQUE NOT NULL,
            county INTEGER NOT NULL,
            active INTEGER DEFAULT 1,
            subscription_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_payment TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            klarna_token TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pending_subscribers (
            session_id TEXT PRIMARY KEY,
            phone_number TEXT UNIQUE NOT NULL,
            county INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS newspapers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            contact_email TEXT,
            sms_quota INTEGER
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            totp_secret TEXT NOT NULL
        )
    ''')

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

    conn.commit()
    conn.close()
