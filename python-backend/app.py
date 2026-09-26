from flask import Flask
from flask_cors import CORS
from database.db import init_db, get_connection
from routes.auction_routes import auction_bp, datetime_to_millis
from services.java_bridge import load_auction_in_engine, check_java_engine

app = Flask(__name__)
CORS(app)

# Register the auction routes blueprint under /api
app.register_blueprint(auction_bp, url_prefix='/api')

def sync_auctions_to_java():
    """
    On Flask startup, load all existing auctions from SQLite into
    the Java engine so it can validate bids correctly.
    
    This ensures that even if the Java engine is restarted, the auction
    data is reconstructed from the database.
    """
    if not check_java_engine():
        print("WARNING: Java engine is offline. Auctions will not be synced.")
        print("Start the Java engine and restart Flask to sync.")
        return

    conn = get_connection()
    rows = conn.execute("SELECT * FROM auctions").fetchall()
    conn.close()

    for row in rows:
        engine_data = {
            "id": row["id"],
            "title": row["title"],
            "description": row["description"],
            "starting_price": row["starting_price"],
            "minimum_increment": row["minimum_increment"],
            "current_highest_bid": row["current_highest_bid"],
            "start_time_ms": datetime_to_millis(row["start_time"]),
            "end_time_ms": datetime_to_millis(row["end_time"])
        }
        result = load_auction_in_engine(engine_data)
        print(f"  Synced auction #{row['id']}: {row['title']} -> {result}")

    print(f"Synced {len(rows)} auction(s) to Java engine.")


if __name__ == '__main__':
    # Initialize the database tables
    init_db()
    
    # Sync existing auctions to the Java engine
    sync_auctions_to_java()
    
    print("\nFlask server starting on http://localhost:5000")
    app.run(debug=True, port=5000, use_reloader=False)
