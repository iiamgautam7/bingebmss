import sqlite3
from config import DB_PATH

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Create requests table for booking requests
    c.execute('''
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            movie TEXT NOT NULL,
            showtime TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'PENDING',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            processed_at DATETIME
        )
    ''')
    # Create bookings table for finalized bookings
    c.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id INTEGER,
            username TEXT,
            movie TEXT,
            showtime TEXT,
            status TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    print(f"DB initialized at {DB_PATH}")

def insert_sample_requests():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    sample_requests = [
        ('testuser1', 'Interstellar', '10:00 AM', 'PENDING'),
        ('testuser2', 'Inception', '2:00 PM', 'PENDING'),
        ('testuser3', 'The Matrix', '3:00 PM', 'PENDING'),
        ('testuser4', 'Arjun Reddy', '9:00 PM', 'PENDING'),
        ('testuser5', 'Avengers', '4:00 PM', 'PENDING'),
    ]
    c.executemany(
        "INSERT INTO requests (username, movie, showtime, status) VALUES (?, ?, ?, ?)",
        sample_requests
    )
    conn.commit()
    conn.close()
    print(f"Inserted {len(sample_requests)} sample pending requests.")

if __name__ == "__main__":
    init_db()
    insert_sample_requests()
