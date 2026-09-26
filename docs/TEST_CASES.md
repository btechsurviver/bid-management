# Test Cases & Requirements Mapping Matrix

**Project Title:** Online Auction Bid Management System  
**Academic Domain:** Data Structures & Operating System Concepts  

---

## 1. Test Case Table

| Test ID | Test Description | Preconditions | Input Data | Expected Result | Actual Result | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TC01** | **Create Auction** | Flask backend and SQLite database active | Title: "Wireless Headphones", Starting Price: 2500, Min Inc: 100 | Auction created successfully with HTTP 201 response and loaded into Java Engine. | Auction created with ID #1 and synced to Java engine. | **PASS** |
| **TC02** | **View Auction** | Auction ID #1 exists in system | GET `/api/auctions/1` | Returns JSON containing title, starting price, current highest bid, and calculated status. | Returns auction dict with status `ACTIVE` and `minimum_next_bid: 2500`. | **PASS** |
| **TC03** | **Valid Bid** | Auction #1 is `ACTIVE`, highest bid = ₹0, min next = ₹2500 | Bidder: "Ashish", Amount: ₹2500 | Bid accepted (HTTP 200), added to Java PriorityQueue, highest bid updated to ₹2500. | `Bid accepted`, highest bid updated to ₹2500, minimum next bid updated to ₹2600. | **PASS** |
| **TC04** | **Bid Below Minimum** | Auction #1 is `ACTIVE`, highest bid = ₹2500, min inc = ₹100 | Bidder: "Rahul", Amount: ₹2550 | Bid rejected (HTTP 400). Message: "Bid must be at least ₹2600.00." | `Bid rejected. Bid must be at least ₹2600.00.` Current highest bid unchanged. | **PASS** |
| **TC05** | **Bid on Upcoming Auction** | Auction #2 status is `UPCOMING` | Bidder: "Priya", Amount: ₹5000 | Bid rejected (HTTP 409). Message: "Auction has not started yet." | `Bid rejected. Auction has not started yet.` | **PASS** |
| **TC06** | **Bid on Ended Auction** | Auction #3 status is `ENDED` | Bidder: "Aman", Amount: ₹10000 | Bid rejected (HTTP 409). Message: "Auction has already ended." | `Bid rejected. Auction has already ended.` | **PASS** |
| **TC07** | **Multiple Concurrent Bidders** | Auction #1 is `ACTIVE`, min next = ₹2600 | 5 Threads: B1=₹2600, B2=₹2700, B3=₹2600, B4=₹2800, B5=₹2700 | Java engine spawns 5 OS threads. ReentrantLock serializes execution. Bids meeting increment pass; stale/low bids get rejected. | Thread simulation executes cleanly. Accepted: 3, Rejected: 2. Final highest: ₹2800. | **PASS** |
| **TC08** | **Same Amount Submitted Concurrently** | Auction #1 is `ACTIVE`, min next = ₹2800 | 3 Threads all bidding ₹2800 simultaneously | Exactly ONE thread acquires lock first and is ACCEPTED. The remaining 2 threads are REJECTED. | 1 bid ACCEPTED, 2 bids REJECTED due to updated minimum bid requirement. | **PASS** |
| **TC09** | **Priority Queue Ordering** | Multiple valid bids placed on Auction #1 | Bids: ₹2500, ₹2600, ₹2800, ₹3000 | `PriorityQueue.peek()` returns ₹3000. `getBids()` returns list sorted in descending order: [₹3000, ₹2800, ₹2600, ₹2500]. | PriorityQueue visualizer displays ₹3000 with "Highest Priority" badge at root position #1. | **PASS** |
| **TC10** | **Database Persistence** | Bids placed and simulation executed | Server restart or page refresh | All auction states and bid history records persist in SQLite database `auction.db`. | Database records loaded on startup; Flask syncs SQLite state to Java engine. | **PASS** |
| **TC11** | **Java Engine Unavailable** | Java engine process stopped | Bid submitted via Flask API | Flask returns graceful error: "Java engine is not running. Please start the Java engine first." | Graceful HTTP 500/400 error message rendered; database remains uncorrupted. | **PASS** |
| **TC12** | **Invalid Input Validation** | Create auction form or bid input | Bidder: "", Amount: -500 | Validation error returned (HTTP 400): "Bidder name is required", "Bid amount must be positive". | Validation error message displayed in UI alert banner; invalid bid rejected. | **PASS** |
| **TC13** | **Auction Completion** | ACTIVE auction ended via Admin/Demo | Click "End Auction" button | Status updates to `ENDED`. Highest valid bid remains winning bid. Subsequent bids rejected. | Status changes to `ENDED`. Winner displayed as "Ashish (₹3000)". Bidding disabled. | **PASS** |
| **TC14** | **Mobile Interface** | Page rendered on mobile viewports (320px, 375px, 390px, 430px) | Resize viewport to 375px width | Cards, forms, priority queue list, and thread results stack vertically without horizontal overflow. | Clean vertical stacking; all buttons and form inputs easily tap-friendly ($\ge 44\text{px}$). | **PASS** |

---

## 2. Requirements Traceability Mapping Matrix

| Requirement | Description | System Implementation | Verification Test |
| :--- | :--- | :--- | :--- |
| **REQ-DS-01** | Priority Queue Data Structure | `java.util.PriorityQueue<Bid>` wrapped in `BidPriorityQueue.java` | **TC09** |
| **REQ-DS-02** | Highest Bid Retrieval | $O(1)$ `peek()` implementation via reversed `Comparable<Bid>` | **TC02, TC09** |
| **REQ-OS-01** | Concurrency Control | `ReentrantLock` in `ConcurrencyManager.java` wrapping critical section | **TC07, TC08** |
| **REQ-OS-02** | Multiple Bidder Threads | `BidderThread.java` implementing `Runnable` executed on native `Thread`s | **TC07, TC08** |
| **REQ-OS-03** | Thread Barrier / Synchronization | `Thread.join()` in `ConcurrentBidSimulation.java` | **TC07** |
| **REQ-APP-01** | Minimum Bid Increment Validation | Atomic check in `AuctionManager.placeBid()` | **TC03, TC04** |
| **REQ-APP-02** | Auction Lifecycle Management | State transitions (`UPCOMING`, `ACTIVE`, `ENDED`) | **TC01, TC05, TC06, TC13** |
| **REQ-DB-01** | Persistent Bid Storage | SQLite relational schema (`auctions` & `bids` tables) | **TC10** |
| **REQ-UI-01** | Demonstration Dashboard | Interactive `/demo` page with PQ visualizer & simulation controls | **TC07, TC09, TC14** |
