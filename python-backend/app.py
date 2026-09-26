from flask import Flask
from flask_cors import CORS
from database.db import init_db, get_connection
from routes.auction_routes import auction_bp, datetime_to_millis
from services.java_bridge import load_auction_in_engine, check_java_engine

app = Flask(__name__)
CORS(app)

# Register the auction routes blueprint under /api
app.register_blueprint(auction_bp, url_prefix='/api')

from services.java_bridge import load_auction_in_engine, check_java_engine, sync_single_auction_to_java

def sync_auctions_to_java():
    """
    On Flask startup, load all existing auctions and their bid history from SQLite into
    the Java engine so its BidPriorityQueue can be reconstructed.
    
    This ensures that even if the Java engine is restarted, the auction
    data and PriorityQueue state are fully reconstructed from the database.
    """
    if not check_java_engine():
        print("WARNING: Java engine is offline. Auctions will not be synced.")
        print("Start the Java engine and restart Flask to sync.")
        return

    conn = get_connection()
    rows = conn.execute("SELECT id, title FROM auctions").fetchall()
    conn.close()

    for row in rows:
        result = sync_single_auction_to_java(row["id"])
        print(f"  Synced auction #{row['id']}: {row['title']} -> {result}")

    print(f"Synced {len(rows)} auction(s) and their PriorityQueue states to Java engine.")


if __name__ == '__main__':
    # Initialize the database tables
    init_db()
    
    # Sync existing auctions to the Java engine
    sync_auctions_to_java()
    
    print("\nFlask server starting on http://localhost:5000")
    app.run(debug=True, port=5000, use_reloader=False)
