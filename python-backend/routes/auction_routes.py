from flask import Blueprint, jsonify, request
from database.db import get_connection
from services.java_bridge import (
    load_auction_in_engine, place_bid_in_engine,
    get_auction_status_from_engine, check_java_engine,
    simulate_concurrent_bids
)
from datetime import datetime
import logging

auction_bp = Blueprint('auctions', __name__)

logger = logging.getLogger(__name__)


def compute_status(start_time_str, end_time_str):
    """Compute auction status from start/end time strings. Returns UNKNOWN on parse error."""
    now = datetime.now()
    try:
        try:
            start = datetime.strptime(start_time_str, "%Y-%m-%dT%H:%M")
        except ValueError:
            start = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")
        try:
            end = datetime.strptime(end_time_str, "%Y-%m-%dT%H:%M")
        except ValueError:
            end = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M:%S")

        if now < start:
            return "UPCOMING"
        elif now <= end:
            return "ACTIVE"
        else:
            return "ENDED"
    except (ValueError, TypeError) as e:
        logger.error(f"compute_status error: {e} (start={start_time_str}, end={end_time_str})")
        return "UNKNOWN"


def datetime_to_millis(dt_str):
    """Convert a datetime string to epoch milliseconds for Java. Returns 0 on error."""
    try:
        try:
            dt = datetime.strptime(dt_str, "%Y-%m-%dT%H:%M")
        except ValueError:
            dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
        return int(dt.timestamp() * 1000)
    except (ValueError, TypeError) as e:
        logger.error(f"datetime_to_millis error: {e} (value={dt_str})")
        return 0


def parse_datetime(dt_str):
    """Parse a datetime string in known formats. Returns None on failure."""
    for fmt in ("%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(dt_str, fmt)
        except ValueError:
            continue
    return None


def build_auction_dict(row):
    """Build a standardized auction dict from a DB row."""
    status = compute_status(row["start_time"], row["end_time"])
    minimum_next = (
        row["starting_price"] if row["current_highest_bid"] <= 0
        else row["current_highest_bid"] + row["minimum_increment"]
    )
    return {
        "id": row["id"],
        "title": row["title"],
        "description": row["description"],
        "starting_price": row["starting_price"],
        "current_highest_bid": row["current_highest_bid"],
        "minimum_increment": row["minimum_increment"],
        "minimum_next_bid": round(minimum_next, 2),
        "start_time": row["start_time"],
        "end_time": row["end_time"],
        "status": status,
        "created_at": row["created_at"]
    }


# ============================================
# GET /api/health
# ============================================
@auction_bp.route('/health', methods=['GET'])
def health_check():
    java_up = check_java_engine()
    return jsonify({
        "status": "ok",
        "message": "Python backend is running",
        "java_engine": "connected" if java_up else "offline"
    })


# ============================================
# GET /api/auctions — List all auctions
# ============================================
@auction_bp.route('/auctions', methods=['GET'])
def get_auctions():
    try:
        conn = get_connection()
        rows = conn.execute("SELECT * FROM auctions ORDER BY created_at DESC").fetchall()
        conn.close()
        return jsonify([build_auction_dict(row) for row in rows])
    except Exception as e:
        logger.error(f"get_auctions error: {e}")
        return jsonify({"error": "Failed to retrieve auctions"}), 500


# ============================================
# GET /api/auctions/<id> — Get single auction
# ============================================
@auction_bp.route('/auctions/<int:auction_id>', methods=['GET'])
def get_auction(auction_id):
    try:
        conn = get_connection()
        row = conn.execute("SELECT * FROM auctions WHERE id = ?", (auction_id,)).fetchone()
        conn.close()
        if not row:
            return jsonify({"error": "Auction not found"}), 404
        return jsonify(build_auction_dict(row))
    except Exception as e:
        logger.error(f"get_auction error: {e}")
        return jsonify({"error": "Failed to retrieve auction"}), 500


# ============================================
# POST /api/auctions — Create a new auction
# ============================================
@auction_bp.route('/auctions', methods=['POST'])
def create_auction():
    # Bug Fix #1: safe JSON parsing — get_json() returns None on malformed body
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid or missing JSON request body"}), 400

    # Validate required fields
    required = ["title", "description", "starting_price", "minimum_increment", "start_time", "end_time"]
    for field in required:
        if field not in data or data[field] == "" or data[field] is None:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    title = str(data["title"]).strip()
    description = str(data["description"]).strip()

    if not title:
        return jsonify({"error": "Title cannot be empty"}), 400
    if not description:
        return jsonify({"error": "Description cannot be empty"}), 400

    try:
        starting_price = float(data["starting_price"])
        minimum_increment = float(data["minimum_increment"])
    except (ValueError, TypeError):
        return jsonify({"error": "Starting price and minimum increment must be numbers"}), 400

    if starting_price <= 0:
        return jsonify({"error": "Starting price must be greater than 0"}), 400
    if minimum_increment <= 0:
        return jsonify({"error": "Minimum increment must be greater than 0"}), 400

    start_time = str(data["start_time"]).strip()
    end_time = str(data["end_time"]).strip()

    # Bug Fix #2: Validate datetime formats and end > start on backend
    start_dt = parse_datetime(start_time)
    end_dt = parse_datetime(end_time)
    if start_dt is None:
        return jsonify({"error": "Invalid start_time format"}), 400
    if end_dt is None:
        return jsonify({"error": "Invalid end_time format"}), 400
    if end_dt <= start_dt:
        return jsonify({"error": "End time must be after start time"}), 400

    try:
        conn = get_connection()
        cursor = conn.execute(
            """INSERT INTO auctions (title, description, starting_price, minimum_increment,
               start_time, end_time, current_highest_bid)
               VALUES (?, ?, ?, ?, ?, ?, 0)""",
            (title, description, starting_price, minimum_increment, start_time, end_time)
        )
        auction_id = cursor.lastrowid
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"create_auction DB error: {e}")
        return jsonify({"error": "Failed to save auction to database"}), 500

    # Load the auction into the Java engine (best-effort; failure is logged, not fatal)
    try:
        engine_data = {
            "id": auction_id,
            "title": title,
            "description": description,
            "starting_price": starting_price,
            "minimum_increment": minimum_increment,
            "current_highest_bid": 0,
            "start_time_ms": datetime_to_millis(start_time),
            "end_time_ms": datetime_to_millis(end_time)
        }
        load_auction_in_engine(engine_data)
    except Exception as e:
        logger.warning(f"Failed to load auction into Java engine: {e}")

    return jsonify({"message": "Auction created successfully", "id": auction_id}), 201


# ============================================
# POST /api/auctions/<id>/bids — Place a bid
# ============================================
@auction_bp.route('/auctions/<int:auction_id>/bids', methods=['POST'])
def place_bid(auction_id):
    try:
        conn = get_connection()
        auction = conn.execute("SELECT * FROM auctions WHERE id = ?", (auction_id,)).fetchone()
        if not auction:
            conn.close()
            return jsonify({"success": False, "message": "Auction not found"}), 404

        # Bug Fix #1: Use silent=True to avoid 400 from Flask on malformed JSON
        data = request.get_json(silent=True)
        if not data:
            conn.close()
            return jsonify({"success": False, "message": "Invalid or missing JSON request body"}), 400

        bidder_name = str(data.get("bidder_name", "")).strip()
        if not bidder_name:
            conn.close()
            return jsonify({"success": False, "message": "Bidder name is required"}), 400

        # Limit bidder name length to prevent abuse
        if len(bidder_name) > 100:
            conn.close()
            return jsonify({"success": False, "message": "Bidder name too long (max 100 chars)"}), 400

        try:
            amount = float(data.get("amount", 0))
        except (ValueError, TypeError):
            conn.close()
            return jsonify({"success": False, "message": "Bid amount must be a number"}), 400

        if amount <= 0:
            conn.close()
            return jsonify({"success": False, "message": "Bid amount must be positive"}), 400

        # Sanity check: reject absurdly large bids (prevent float overflow in Java)
        if amount > 999_999_999:
            conn.close()
            return jsonify({"success": False, "message": "Bid amount exceeds maximum allowed value"}), 400

        # Check auction status (quick server-side check before hitting Java)
        status = compute_status(auction["start_time"], auction["end_time"])
        if status == "UPCOMING":
            conn.close()
            return jsonify({"success": False, "message": "Auction has not started yet"}), 409
        if status == "ENDED":
            conn.close()
            return jsonify({"success": False, "message": "Auction has already ended"}), 409

        # Send bid to Java engine for authoritative validation
        engine_result = place_bid_in_engine(auction_id, bidder_name, amount)

        if engine_result.get("success"):
            conn.execute(
                "INSERT INTO bids (auction_id, bidder_name, amount) VALUES (?, ?, ?)",
                (auction_id, bidder_name, amount)
            )
            conn.execute(
                "UPDATE auctions SET current_highest_bid = ? WHERE id = ?",
                (amount, auction_id)
            )
            conn.commit()
            conn.close()
            return jsonify({
                "success": True,
                "message": "Bid accepted",
                "highestBid": amount
            }), 200
        else:
            conn.close()
            return jsonify({
                "success": False,
                "message": engine_result.get("message", "Bid rejected by auction engine")
            }), 400

    except Exception as e:
        logger.error(f"place_bid error: {e}")
        return jsonify({"success": False, "message": "An internal error occurred. Please try again."}), 500


# ============================================
# GET /api/auctions/<id>/bids — Get bid history
# ============================================
@auction_bp.route('/auctions/<int:auction_id>/bids', methods=['GET'])
def get_bids(auction_id):
    try:
        conn = get_connection()
        auction = conn.execute("SELECT id FROM auctions WHERE id = ?", (auction_id,)).fetchone()
        if not auction:
            conn.close()
            return jsonify({"error": "Auction not found"}), 404

        rows = conn.execute(
            "SELECT * FROM bids WHERE auction_id = ? ORDER BY amount DESC, created_at ASC",
            (auction_id,)
        ).fetchall()
        conn.close()

        bids = [{
            "id": row["id"],
            "bidder_name": row["bidder_name"],
            "amount": row["amount"],
            "created_at": row["created_at"]
        } for row in rows]

        return jsonify(bids)
    except Exception as e:
        logger.error(f"get_bids error: {e}")
        return jsonify({"error": "Failed to retrieve bids"}), 500


# ============================================
# GET /api/auctions/<id>/queue — Get Java PriorityQueue contents
# ============================================
@auction_bp.route('/auctions/<int:auction_id>/queue', methods=['GET'])
def get_auction_queue(auction_id):
    """
    Returns the exact contents of the PriorityQueue for the specified auction.
    Prefers Java engine's live PriorityQueue, falls back to SQLite DB if Java is offline.
    """
    from services.java_bridge import get_bids_from_engine
    try:
        # Try fetching from Java engine first
        java_queue = get_bids_from_engine(auction_id)
        if java_queue and java_queue.get("success"):
            return jsonify({
                "source": "java_priority_queue",
                "auction_id": auction_id,
                "size": java_queue.get("totalBids", 0),
                "bids": java_queue.get("queue", [])
            })

        # Fallback to database if Java is offline or hasn't loaded this auction yet
        conn = get_connection()
        rows = conn.execute(
            "SELECT * FROM bids WHERE auction_id = ? ORDER BY amount DESC, created_at ASC",
            (auction_id,)
        ).fetchall()
        conn.close()

        bids = [{
            "bidderName": row["bidder_name"],
            "amount": row["amount"],
            "timestamp": row["created_at"]
        } for row in rows]

        return jsonify({
            "source": "sqlite_database",
            "auction_id": auction_id,
            "size": len(bids),
            "bids": bids
        })
    except Exception as e:
        logger.error(f"get_auction_queue error: {e}")
        return jsonify({"error": "Failed to retrieve auction queue"}), 500


# ============================================
# POST /api/demo/seed — Seed demo data
# ============================================
@auction_bp.route('/demo/seed', methods=['POST'])
def seed_demo():
    """Seed standard realistic demo auctions and sync to Java engine."""
    from database.db import seed_demo_data
    try:
        seeded = seed_demo_data(force=True)
        # Sync all auctions to Java engine
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
            load_auction_in_engine(engine_data)

        return jsonify({"success": True, "message": "Demo data seeded and synced to Java engine."})
    except Exception as e:
        logger.error(f"seed_demo error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500



# ============================================
# POST /api/auctions/<id>/start — Force start
# ============================================
@auction_bp.route('/auctions/<int:auction_id>/start', methods=['POST'])
def start_auction(auction_id):
    try:
        conn = get_connection()
        auction = conn.execute("SELECT * FROM auctions WHERE id = ?", (auction_id,)).fetchone()
        if not auction:
            conn.close()
            return jsonify({"error": "Auction not found"}), 404

        # Bug Fix #3: Cannot start if end_time is already in the past
        end_dt = parse_datetime(auction["end_time"])
        if end_dt and end_dt <= datetime.now():
            conn.close()
            return jsonify({"error": "Cannot start auction: end time is already in the past"}), 409

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn.execute("UPDATE auctions SET start_time = ? WHERE id = ?", (now_str, auction_id))
        conn.commit()

        engine_data = {
            "id": auction_id,
            "title": auction["title"],
            "description": auction["description"],
            "starting_price": auction["starting_price"],
            "minimum_increment": auction["minimum_increment"],
            "current_highest_bid": auction["current_highest_bid"],
            "start_time_ms": datetime_to_millis(now_str),
            "end_time_ms": datetime_to_millis(auction["end_time"])
        }
        load_auction_in_engine(engine_data)
        conn.close()
        return jsonify({"message": "Auction started", "start_time": now_str})
    except Exception as e:
        logger.error(f"start_auction error: {e}")
        return jsonify({"error": "Failed to start auction"}), 500


# ============================================
# POST /api/auctions/<id>/end — Force end
# ============================================
@auction_bp.route('/auctions/<int:auction_id>/end', methods=['POST'])
def end_auction(auction_id):
    try:
        conn = get_connection()
        auction = conn.execute("SELECT * FROM auctions WHERE id = ?", (auction_id,)).fetchone()
        if not auction:
            conn.close()
            return jsonify({"error": "Auction not found"}), 404

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn.execute("UPDATE auctions SET end_time = ? WHERE id = ?", (now_str, auction_id))
        conn.commit()

        engine_data = {
            "id": auction_id,
            "title": auction["title"],
            "description": auction["description"],
            "starting_price": auction["starting_price"],
            "minimum_increment": auction["minimum_increment"],
            "current_highest_bid": auction["current_highest_bid"],
            "start_time_ms": datetime_to_millis(auction["start_time"]),
            "end_time_ms": datetime_to_millis(now_str)
        }
        load_auction_in_engine(engine_data)
        conn.close()
        return jsonify({"message": "Auction ended", "end_time": now_str})
    except Exception as e:
        logger.error(f"end_auction error: {e}")
        return jsonify({"error": "Failed to end auction"}), 500


# ============================================
# POST /api/auctions/<id>/simulate-concurrent-bids
# ============================================
@auction_bp.route('/auctions/<int:auction_id>/simulate-concurrent-bids', methods=['POST'])
def simulate_bids(auction_id):
    try:
        conn = get_connection()
        auction = conn.execute("SELECT * FROM auctions WHERE id = ?", (auction_id,)).fetchone()
        if not auction:
            conn.close()
            return jsonify({"success": False, "message": "Auction not found"}), 404

        status = compute_status(auction["start_time"], auction["end_time"])
        if status != "ACTIVE":
            conn.close()
            return jsonify({"success": False, "message": f"Auction is {status}. Must be ACTIVE to simulate."}), 409

        data = request.get_json(silent=True)
        if not data or "bidders" not in data:
            conn.close()
            return jsonify({"success": False, "message": "Missing bidders list"}), 400

        bidders = data["bidders"]
        if not isinstance(bidders, list) or len(bidders) == 0:
            conn.close()
            return jsonify({"success": False, "message": "Bidders must be a non-empty list"}), 400

        # Validate each bidder entry
        validated_bidders = []
        for i, b in enumerate(bidders):
            if not isinstance(b, dict):
                conn.close()
                return jsonify({"success": False, "message": f"Bidder {i+1} is invalid"}), 400
            name = str(b.get("name", "")).strip()
            if not name:
                conn.close()
                return jsonify({"success": False, "message": f"Bidder {i+1} is missing a name"}), 400
            try:
                amount = float(b.get("amount", 0))
                if amount <= 0:
                    raise ValueError("non-positive")
            except (ValueError, TypeError):
                conn.close()
                return jsonify({"success": False, "message": f"Bidder {i+1} has an invalid amount"}), 400
            validated_bidders.append({"name": name, "amount": amount})

        # Cap at 50 threads to prevent overload
        if len(validated_bidders) > 50:
            conn.close()
            return jsonify({"success": False, "message": "Maximum 50 bidder threads per simulation"}), 400

        # Bug Fix #4: Close connection BEFORE calling Java (which can take time)
        conn.close()

        result = simulate_concurrent_bids(auction_id, validated_bidders)

        if result.get("success"):
            # Reopen connection for DB writes only after Java is done
            conn2 = get_connection()
            try:
                current_highest = auction["current_highest_bid"]
                for r in result.get("results", []):
                    if r.get("status") == "ACCEPTED":
                        conn2.execute(
                            "INSERT INTO bids (auction_id, bidder_name, amount) VALUES (?, ?, ?)",
                            (auction_id, r["bidder"], r["amount"])
                        )
                        if r["amount"] > current_highest:
                            current_highest = r["amount"]
                conn2.execute(
                    "UPDATE auctions SET current_highest_bid = ? WHERE id = ?",
                    (current_highest, auction_id)
                )
                conn2.commit()
            finally:
                conn2.close()

        return jsonify(result)

    except Exception as e:
        logger.error(f"simulate_bids error: {e}")
        return jsonify({"success": False, "message": "Simulation failed. Internal server error."}), 500
