# Viva Cheat Sheet — Online Auction Bid Management System

### 1. Data Structures & Algorithms

**Q1: Why Priority Queue?**
A: Because an auction needs O(1) fast access to the highest valid bid via peek().

**Q2: What is the underlying data structure of Java's PriorityQueue?**
A: A binary heap.

**Q3: What is the time complexity of bid insertion and highest bid retrieval?**
A: Insertion is O(log n), retrieval is O(1).

**Q4: How is Java's PriorityQueue customized to behave as a Max-Heap?**
A: By reversing the natural order in Bid.compareTo() using Double.compare(other.amount, this.amount).

**Q5: How are tie-breaker bids with identical amounts handled?**
A: By timestamp comparison Long.compare(this.timestamp, other.timestamp) — earlier timestamp wins (First-Come, First-Served).

---

### 2. Operating System & Concurrency

**Q6: Why multithreading?**
A: Because multiple bidders can submit bids at the same time.

**Q7: What is a race condition?**
A: It occurs when multiple threads access and modify shared data concurrently and the result depends on their execution timing.

**Q8: What is the critical section in this project?**
A: The AuctionManager.placeBid() method where the current highest bid is read, validated against rules, added to the Priority Queue, and the highest bid is updated.

**Q9: How do you prevent the race condition?**
A: By protecting the critical section using ReentrantLock in ConcurrencyManager.java.

**Q10: Why ReentrantLock instead of synchronized block?**
A: ReentrantLock allows explicit locking/unlocking, supports fair FIFO queueing, and guarantees lock release using try-finally blocks.

**Q11: What is a fair lock?**
A: A lock configured with new ReentrantLock(true) that grants lock access to threads in the exact order they requested it (FIFO).

**Q12: How do you prevent deadlocks during exception handling?**
A: By placing concurrencyManager.unlock() inside a mandatory finally block.

**Q13: How are bidder threads created and started?**
A: Created as BidderThread objects implementing Runnable, wrapped in Thread instances, and started using Thread.start().

**Q14: Why Thread.start() instead of Thread.run()?**
A: Thread.start() spawns a new OS thread for concurrent execution, while Thread.run() executes sequentially on the main thread.

**Q15: How does the main thread wait for all bidder threads to finish?**
A: By calling Thread.join() on every created bidder thread.

---

### 3. System Architecture & Tech Stack

**Q16: What is the overall 3-tier architecture?**
A: Presentation Tier (HTML/CSS/JS) -> Application Tier (Python Flask REST API) -> Execution Engine (Java Core Engine) -> Data Tier (SQLite DB).

**Q17: How does Python Flask communicate with the Java Engine?**
A: Via HTTP JSON requests sent through Python's requests library to Java's embedded HttpServer on port 9090.

**Q18: What HTTP server library is used in Java?**
A: com.sun.net.httpserver.HttpServer with Executors.newFixedThreadPool(10).

**Q19: What happens if the Java Engine crashes or restarts?**
A: On startup/recovery, existing SQLite auction and accepted bid data are synchronized into Java memory so each Auction's BidPriorityQueue is reconstructed with original timestamps preserved.

**Q20: Why separate Python Flask and Java Engine?**
A: Flask provides rapid REST web API handling, while Java handles high-performance thread synchronization and Heap data structures.

---

### 4. Auction Business Logic & Rules

**Q21: What are the three possible auction statuses?**
A: UPCOMING, ACTIVE, and ENDED.

**Q22: How is auction status determined?**
A: Dynamically by comparing system time System.currentTimeMillis() against auction startTime and endTime.

**Q23: How is the minimum next valid bid calculated?**
A: If no bids exist, it equals startingPrice. Otherwise, it equals currentHighestBid + minimumIncrement.

**Q24: What happens if a bid is below the minimum required amount?**
A: It is rejected by the Java engine with status 400 and an error message specifying the minimum required bid.

**Q25: Can an auction accept bids when its status is UPCOMING or ENDED?**
A: No, bid attempts on inactive auctions are immediately rejected.

---

### 5. Database & Data Persistence

**Q26: What database engine is used?**
A: SQLite 3 (auction.db).

**Q27: What tables exist in the database?**
A: auctions (auction metadata) and bids (bid records).

**Q28: How is relational integrity enforced between bids and auctions?**
A: Using Foreign Key bids.auction_id REFERENCES auctions(id) with PRAGMA foreign_keys = ON.

**Q29: Are bid history records lost after server restart?**
A: No, all accepted bids are permanently persisted in the SQLite bids table.

**Q30: How is data consistency maintained between Java memory and SQLite DB?**
A: When Java accepts a bid inside the lock, Flask writes the accepted bid record and updates current_highest_bid in SQLite within a database transaction.

---

### 6. Verification & Code Quality

**Q31: What test verifies Priority Queue correctness?**
A: java engine.Main test, which inputs bids ₹10k, ₹15k, ₹12k, ₹18k, ₹11k and verifies peak returns ₹18k.

**Q32: How was concurrency stress tested?**
A: By running 5, 10, 20, and 50 concurrent bidder threads targeting an active auction.

**Q33: Were race conditions detected during stress testing?**
A: Zero race conditions occurred; ReentrantLock correctly serialized all bid attempts.

**Q34: How is mobile responsiveness ensured?**
A: Via CSS Flexbox/Grid layouts and @media queries covering viewports from 320px to 1366px.

**Q35: Are there any third-party dependencies required for Java?**
A: None, Java relies strictly on standard SDK libraries (java.util, java.util.concurrent, com.sun.net.httpserver).
