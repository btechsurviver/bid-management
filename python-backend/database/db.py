import sqlite3
import os

# Database file is stored in the python-backend directory
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'auction.db')

def get_connection():
    """Get a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Access columns by name
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    """
    Create all required tables if they don't already exist.
    This is called automatically when the Flask app starts.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS auctions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            starting_price REAL NOT NULL,
            current_highest_bid REAL DEFAULT 0,
            minimum_increment REAL NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            status TEXT DEFAULT 'UPCOMING',
            created_at TEXT DEFAULT (datetime('now', 'localtime'))
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bids (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            auction_id INTEGER NOT NULL,
            bidder_name TEXT NOT NULL,
            amount REAL NOT NULL,
            created_at TEXT DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (auction_id) REFERENCES auctions(id)
        )
    ''')

    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")

    # Seed demo data if database has no auctions
    seed_demo_data()


def seed_demo_data(force=False):
    """
    Seed standard realistic demo auctions if the database is currently empty
    or if force=True (without overwriting existing user-created auctions).
    """
    from datetime import datetime, timedelta
    conn = get_connection()
    cursor = conn.cursor()

    count = cursor.execute("SELECT COUNT(*) FROM auctions").fetchone()[0]
    if count > 0 and not force:
        conn.close()
        return False

    now = datetime.now()
    start_time = (now - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
    end_time = (now + timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S")

    demo_items = [
        {
            "title": "Wireless Headphones",
            "description": "Noise-cancelling wireless over-ear headphones with 30-hour battery life.",
            "starting_price": 2500.0,
            "minimum_increment": 100.0
        },
        {
            "title": "Mechanical Keyboard",
            "description": "Tactile mechanical gaming keyboard with customizable RGB backlighting.",
            "starting_price": 3000.0,
            "minimum_increment": 200.0
        },
        {
            "title": "Laptop",
            "description": "High-performance laptop with 16GB RAM and fast 512GB SSD storage.",
            "starting_price": 45000.0,
            "minimum_increment": 500.0
        },
        {
            "title": "Smart Watch",
            "description": "Fitness smartwatch with AMOLED display and optical heart rate monitor.",
            "starting_price": 4000.0,
            "minimum_increment": 200.0
        },
        {
            "title": "Gaming Mouse",
            "description": "Ergonomic gaming mouse with high-precision optical sensor and customizable DPI.",
            "starting_price": 1500.0,
            "minimum_increment": 100.0
        }
    ]

    for item in demo_items:
        # Avoid duplicating title if it already exists
        existing = cursor.execute("SELECT id FROM auctions WHERE title = ?", (item["title"],)).fetchone()
        if not existing:
            cursor.execute(
                """INSERT INTO auctions (title, description, starting_price, minimum_increment,
                   start_time, end_time, current_highest_bid)
                   VALUES (?, ?, ?, ?, ?, ?, 0)""",
                (item["title"], item["description"], item["starting_price"],
                 item["minimum_increment"], start_time, end_time)
            )

    conn.commit()
    conn.close()
    print("Demo auctions seeded successfully.")
    return True

