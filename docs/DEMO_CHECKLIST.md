# Faculty Demonstration Checklist

**Project Title:** Online Auction Bid Management System  
**Academic Domain:** Data Structures & Operating System Concepts  

---

## Pre-Demonstration Setup Checklist

- [x] **Step 1: Start Java Auction Engine**
  - Terminal Command: `cd java-engine/src && javac engine/*.java && java engine.Main`
  - Expected Output: `Java Auction Engine running on port 9090`

- [x] **Step 2: Start Python Flask Backend**
  - Terminal Command: `cd python-backend && python app.py`
  - Expected Output: `Synced N auction(s) to Java engine. Flask server starting on http://localhost:5000`

- [x] **Step 3: Open Browser Interface**
  - Action: Open `frontend/index.html` or `frontend/demo.html` in Chrome/Firefox/Edge.
  - Expected Output: Top header status badge shows `CONNECTED`.

---

## Live Demonstration Step-by-Step Sequence

- [x] **Step 4: Open Demo Page**
  - Click `Demo` in top navigation bar (`demo.html`).
  - Verify academic badges display: `DATA STRUCTURE: Priority Queue`, `OPERATING SYSTEM: Concurrency Control`, `IMPLEMENTATION: Java Multithreading`.

- [x] **Step 5: Select Auction**
  - Select item `Wireless Headphones` (or click `Reset Demo Data`).
  - Verify Current Highest Bid (₹2,500) and Minimum Next Bid (₹2,600) display correctly.

- [x] **Step 6: Demonstrate Normal Valid Bid**
  - In Section 2, enter Bidder Name `Ashish` and Amount `2600`.
  - Click `Place Bid`.
  - Verify success alert: `Bid accepted! New highest bid is ₹2,600.`

- [x] **Step 7: Demonstrate Invalid Bid Rejection (Increment Rule)**
  - Enter Amount `2650` (below minimum required next bid of ₹2,700).
  - Click `Place Bid`.
  - Verify rejection error alert: `Bid rejected. Bid must be at least ₹2,700.00.`

- [x] **Step 8: Demonstrate Priority Queue Visualizer**
  - Scroll to Section 3 (`Priority Queue Demonstration`).
  - Show how top element has `Highest Priority` badge at position #1.
  - Explain $O(1)$ `peek()` retrieval and $O(\log n)$ `add()` insertion.

- [x] **Step 9: Run Concurrent Bidding Simulation**
  - Scroll to Section 4 (`Concurrent Bidding Simulation`).
  - Select `5 Threads`.
  - Click `Run Concurrent Simulation`.
  - Verify Java spawns native OS threads, serializes critical section with `ReentrantLock`, and returns per-thread results.

- [x] **Step 10: Show Accepted & Rejected Threads**
  - Review results list: Bids meeting updated minimums show `ACCEPTED`, stale/low bids show `REJECTED`.
  - Verify final summary counts (Accepted vs Rejected).

- [x] **Step 11: Explain Critical Section & Locking**
  - Refer to Section 5 (`Concurrency Control Architecture`).
  - Walk through 5-step critical section sequence and `ReentrantLock` in `AuctionManager.java`.

- [x] **Step 12: Demonstrate Auction Completion (End Auction)**
  - Scroll to top action buttons, click `End Auction (Complete)`.
  - Verify status updates to `ENDED`.
  - Verify winning bidder and highest bid display.

- [x] **Step 13: Verify Rejection on Ended Auction**
  - Attempt to submit a new bid on the ended auction.
  - Verify rejection message: `Auction has already ended.`

- [x] **Step 14: Demonstrate Database Persistence**
  - Refresh browser page (`F5`).
  - Verify auction status and bid records persist from SQLite database `auction.db`.

- [x] **Step 15: Demonstrate Mobile Responsiveness**
  - Press `F12` to open Developer Tools, select Mobile Emulator (375px/390px).
  - Verify cards, forms, Priority Queue list, and simulation results stack vertically without horizontal scrollbar.
