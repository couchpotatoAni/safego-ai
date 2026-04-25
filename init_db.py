import sqlite3

def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS users')
    c.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            phone TEXT NOT NULL,
            emergency_contact1 TEXT NOT NULL,
            emergency_contact2 TEXT,
            address TEXT NOT NULL,
            photo_filename TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
    print("Database initialized successfully.")

if __name__ == '__main__':
    init_db()