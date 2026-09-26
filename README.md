# Online Auction Bid Management System

**Academic B.Tech Project** | *Data Structures & Operating Systems*

---

## 1. Project Title & Objective

### Project Title
**Online Auction Bid Management System**

### Project Objective
The primary objective of this project is to construct a practical, multi-tier web application that demonstrates two fundamental computer science principles:
1. **Data Structures:** Efficient priority-based bid tracking using Java's `PriorityQueue`.
2. **Operating System Concepts:** Thread-safe concurrent bid processing and race condition prevention using `ReentrantLock` and multiple Java bidder threads.

---

## 2. Problem Statement

In an online auction system, multiple users (or automated bidding bots) frequently attempt to place bids on the same item at the exact same moment. 

Without concurrency control, a classic **race condition** occurs:
1. Bidder A and Bidder B both read the current highest bid (e.g., ₹10,000).
2. Both calculate the minimum required bid as ₹10,500.
3. Both submit a bid of ₹10,500 simultaneously.
4. Without synchronization, both bids are accepted, corrupting the auction state and violating the minimum increment rule.

To solve this problem, bid validation and state updates must form an **atomic critical section** protected by proper concurrency controls. Furthermore, retrieving the winning bid must be computationally efficient (`O(1)` time complexity) using a Priority Queue.

---

## 3. Technology Stack

- **Frontend UI:** HTML5, Vanilla CSS, JavaScript (ES6 Fetch API)
- **Backend API Server:** Python Flask RESTful API
- **Auction Core Engine:** Java 17+ (Multithreading, `PriorityQueue`, `ReentrantLock`, HTTP Server)
- **Database:** SQLite 3 (Persistent relational database)

---

## 4. System Architecture

```
[ Web Browser / Frontend UI ]
            │ (HTTP REST JSON)
            ▼
   [ Python Flask API ] ──────► [ SQLite Database ]
            │ (HTTP REST JSON)      (Persistent Storage)
            ▼
[ Java Auction Engine (Port 9090) ]
   ├── Concurrency Control (ReentrantLock)
   ├── Multiple Bidder Threads (Thread.start / Thread.join)
   └── Priority Queue (PriorityQueue<Bid>)
```

1. **Browser Frontend:** Renders responsive pages (`index.html`, `admin.html`, `demo.html`, `about.html`) and sends REST API calls.
2. **Python Flask Backend:** Validates HTTP request schemas, routes requests, persists transactions in SQLite, and forwards bids to Java.
3. **Java Auction Engine:** Acts as the authoritative state engine. Executes bid validation in a thread-safe critical section and manages `PriorityQueue<Bid>`.

---

## 5. Data Structure: Priority Queue

### Why Priority Queue?
In an auction, the system frequently needs to query the current winning (highest) bid. 
- A standard unsorted list requires `O(n)` scan time.
- Sorting a list on every bid requires `O(n log n)` time.
- A **Priority Queue** (binary max-heap) provides `O(1)` time complexity for `peek()` (retrieving highest bid) and `O(log n)` time complexity for `add()` (inserting new bid).

### Implementation Details (`BidPriorityQueue.java` & `Bid.java`)
- `Bid.java` implements `Comparable<Bid>`.
- Java's `PriorityQueue` is a Min-Heap by default. We reversed the amount comparison in `compareTo()`:
  ```java
  public int compareTo(Bid other) {
      if (this.amount != other.amount) {
          return Double.compare(other.amount, this.amount); // Descending by amount
      }
      return Long.compare(this.timestamp, other.timestamp); // Ascending by time (earlier wins)
  }
  ```
- **Tie-Breaking Rule:** If two bids have the exact same amount, the earlier timestamp wins (First-Come, First-Served).

---

## 6. Operating System Concept: Concurrency Control

### Critical Section Identification
In `AuctionManager.java`, the `placeBid()` method represents the **critical section**:
1. Read current highest bid.
2. Calculate minimum valid next bid (`highest + minimum_increment`).
3. Validate incoming bid amount against requirement.
4. Insert valid bid into `PriorityQueue<Bid>`.
5. Update current highest bid.

### Synchronization Mechanism (`ReentrantLock`)
We use `java.util.concurrent.locks.ReentrantLock` with fairness enabled (`new ReentrantLock(true)`) to guarantee FIFO ordering among waiting threads.

```java
concurrencyManager.lock();
try {
    // CRITICAL SECTION
    // Read -> Validate -> Insert to PriorityQueue -> Update Highest Bid
} finally {
    concurrencyManager.unlock(); // Always release lock in finally block
}
```

The `try...finally` block ensures that the lock is released even if an unhandled runtime exception occurs, preventing deadlocks.

---

## 7. Multithreading Approach

- **`BidderThread.java`**: Implements `Runnable`. Each instance represents a separate bidder attempting a bid.
- **`Thread.start()` vs `Thread.run()`**: `start()` is used to request the OS kernel to instantiate a new execution thread. Calling `run()` directly would execute sequentially in the main thread.
- **`Thread.join()`**: The main simulation thread calls `join()` on all bidder threads to create a synchronization barrier, ensuring all threads complete before final results are summarized.

---

## 8. Database Schema (SQLite)

### `auctions` Table
```sql
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
);
```

### `bids` Table
```sql
CREATE TABLE IF NOT EXISTS bids (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    auction_id INTEGER NOT NULL,
    bidder_name TEXT NOT NULL,
    amount REAL NOT NULL,
    created_at TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (auction_id) REFERENCES auctions(id)
);
```

---

## 9. Main Features

- **Auction Management:** Create, activate, and end auctions with custom prices and start/end times.
- **Normal Bidding & Increment Rule:** Instant validation against minimum increment rules.
- **Priority Queue Visualizer:** Live inspection of the Java `PriorityQueue<Bid>` structure.
- **Concurrent Bidding Simulator:** Configurable 3 to 20 Java bidder threads running concurrently.
- **Concurrency Control Explanation:** Interactive dashboard explaining critical sections and locking.
- **Persistent Storage:** SQLite database maintains auction and bid records.
- **Responsive Interface:** Works seamlessly on desktop, tablet, and mobile viewports (320px - 430px).

---

## 10. How to Run the Project

### Prerequisites
- Java JDK 17 or higher (`javac`, `java`)
- Python 3.8 or higher (`python`, `pip`)
- Any modern web browser (Chrome, Firefox, Edge, Safari)

### Step 1: Start Java Auction Engine
Open Terminal #1:
```bash
cd java-engine/src
javac engine/*.java
java engine.Main
```
*(Runs on `http://localhost:9090`)*

### Step 2: Start Python Flask Backend
Open Terminal #2:
```bash
cd python-backend
python -m pip install -r requirements.txt
python app.py
```
*(Runs on `http://localhost:5000`)*

### Step 3: Open Frontend Interface
Open your web browser and open `frontend/index.html` (or serve via any local static web server).

---

## 11. How to Demonstrate (Step-by-Step Viva Walkthrough)

Perform this sequence during your project evaluation:

1. **Open Application:** Navigate to `index.html` in your browser. Verify system health badge shows connected.
2. **Open Demo Dashboard:** Click **Demo** in the top navigation bar to access `demo.html`.
3. **Select Demo Auction:** Choose an item (e.g., Wireless Headphones) from the auction dropdown.
4. **Show Starting/Current Bid:** Inspect the Current Bid (e.g., ₹2,500) and Minimum Next Bid (e.g., ₹2,600).
5. **Place Valid Bid:** In the Normal Bidding card, enter Bidder Name `Ashish` and Amount `2600`. Click **Place Bid**.
6. **Show Updated Highest Bid:** Verify the highest bid updates to ₹2,600 and minimum next bid becomes ₹2,700.
7. **Attempt Invalid Bid:** Enter Amount `2650` (below minimum increment ₹100). Click **Place Bid**.
8. **Show Rejection:** Observe the rejection alert: *"Bid rejected. Minimum valid bid is ₹2,700."*
9. **Open Priority Queue Visualizer:** Scroll to Section 3 (Priority Queue Demonstration).
10. **Explain Priority Queue:** Point out how the top item has the `Highest Priority` badge. Explain `O(1)` retrieval via `peek()`.
11. **Run Concurrent Simulation:** Scroll to Section 4 (Concurrent Bidding Simulation). Select `5 Threads`.
12. **Show Multithreaded Execution:** Click **Run Concurrent Simulation**. Watch 5 Java OS threads submit bids concurrently.
13. **Show Accepted & Rejected Bids:** Examine the per-thread results (some accepted, lower/duplicate bids rejected).
14. **Show Final Highest Bid:** Note the consistent final highest bid and accepted/rejected counts.
15. **Explain Concurrency Control:** Refer to Section 5. Explain how `ReentrantLock` in `AuctionManager.java` serializes the critical section.
16. **End Auction:** Click **End Auction (Complete)** in the top auction actions bar.
17. **Show Winning Bid:** Verify status becomes `ENDED`, display winning bid and winning bidder.
18. **Verify Rejection on Ended Auction:** Attempt to place a new bid; observe rejection message: *"Auction has already ended."*
19. **Refresh Page:** Reload the browser page to verify persistent storage from SQLite.
20. **Mobile Viewport Test:** Resize window or enable Mobile Developer Tools (375px/390px) to show clean vertical stacking.

---

## 12. Standalone Testing Commands

You can also test the Java engine independently via CLI:

```bash
cd java-engine/src
javac engine/*.java

# Run standalone PriorityQueue test:
java engine.Main test

# Run standalone multithreaded concurrency stress test:
java engine.Main concurrent
```

---

## 13. Known Limitations

- **Single Engine Instance:** Designed for single-server execution suitable for university lab evaluation.
- **Authentication:** Focuses on core DS/OS concepts rather than user account/authentication management.