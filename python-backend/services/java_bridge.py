import requests
import json

# The Java Auction Engine runs on this address
JAVA_ENGINE_URL = "http://localhost:9090"

def check_java_engine():
    """Check if the Java Auction Engine is running."""
    try:
        resp = requests.get(f"{JAVA_ENGINE_URL}/health", timeout=3)
        return resp.status_code == 200
    except requests.ConnectionError:
        return False

def load_auction_in_engine(auction_data):
    """
    Send auction data to the Java engine so it knows about this auction.
    This is called whenever an auction is created or when the Flask app starts
    (to sync existing auctions from the database).
    
    The Java engine uses this data to validate bids using its PriorityQueue.
    """
    try:
        payload = {
            "id": auction_data["id"],
            "title": auction_data["title"],
            "description": auction_data["description"],
            "startingPrice": auction_data["starting_price"],
            "minimumIncrement": auction_data["minimum_increment"],
            "currentHighestBid": auction_data.get("current_highest_bid", 0),
            "startTime": auction_data["start_time_ms"],
            "endTime": auction_data["end_time_ms"]
        }
        resp = requests.post(
            f"{JAVA_ENGINE_URL}/load-auction",
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        return resp.json()
    except requests.ConnectionError:
        return {"success": False, "message": "Java engine is not running"}

def place_bid_in_engine(auction_id, bidder_name, amount):
    """
    Send a bid to the Java engine for validation.
    
    The Java engine checks:
    1. Does the auction exist?
    2. Is the auction ACTIVE?
    3. Is the bid amount >= minimum required bid?
    
    If valid, the bid is added to the PriorityQueue.
    """
    try:
        payload = {
            "auctionId": auction_id,
            "bidderName": bidder_name,
            "amount": amount
        }
        resp = requests.post(
            f"{JAVA_ENGINE_URL}/place-bid",
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        return resp.json()
    except requests.ConnectionError:
        return {"success": False, "message": "Java engine is not running. Please start the Java engine first."}

def get_auction_status_from_engine(auction_id):
    """Get the current status and highest bid from the Java engine."""
    try:
        resp = requests.get(
            f"{JAVA_ENGINE_URL}/auction-status?id={auction_id}",
            timeout=5
        )
        if resp.status_code == 200:
            return resp.json()
        return None
    except requests.ConnectionError:
        return None

def get_bids_from_engine(auction_id):
    """Get the current PriorityQueue bids from the Java engine."""
    try:
        resp = requests.get(
            f"{JAVA_ENGINE_URL}/get-bids?id={auction_id}",
            timeout=5
        )
        if resp.status_code == 200:
            return resp.json()
        return None
    except requests.ConnectionError:
        return None

def simulate_concurrent_bids(auction_id, bidders):
    """
    Send a concurrent bidding simulation request to the Java engine.
    
    The Java engine will create multiple threads, each attempting to
    place a bid. The ReentrantLock ensures thread-safe bid validation.
    
    bidders: list of dicts with 'name' and 'amount' keys
    """
    try:
        payload = {
            "auctionId": auction_id,
            "bidders": [{"name": b["name"], "amount": b["amount"]} for b in bidders]
        }
        resp = requests.post(
            f"{JAVA_ENGINE_URL}/simulate-concurrent-bids",
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
            timeout=30  # longer timeout for simulation
        )
        return resp.json()
    except requests.ConnectionError:
        return {"success": False, "message": "Java engine is not running"}
    except Exception as e:
        return {"success": False, "message": str(e)}
