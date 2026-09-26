# Academic Viva Questions & Detailed Answers

**Project Title:** Online Auction Bid Management System  
**Academic Domain:** Data Structures & Operating System Concepts  

---

### Q1: What is a Priority Queue?
**Answer:** A Priority Queue is an abstract data structure where each element is associated with a priority value. Unlike a standard FIFO queue where elements are removed in arrival order, a Priority Queue always serves elements with higher priority before elements with lower priority. In Java, it is implemented as a binary heap tree structure.

### Q2: Why did you use a Priority Queue in this project?
**Answer:** In an online auction, the system constantly needs to retrieve the current winning (highest) bid. A Priority Queue allows $O(1)$ constant time access to the highest bid using `peek()`, and $O(\log n)$ logarithmic insertion of new bids using `add()`. This is vastly superior to scanning an unsorted array ($O(n)$) or sorting an array on every bid ($O(n \log n)$).

### Q3: Why not use a normal FIFO Queue?
**Answer:** A normal FIFO (First-In, First-Out) Queue only removes elements in the order they arrived. In an auction, a later bid with a higher monetary value (e.g., ₹10,000) must take precedence over an earlier lower bid (e.g., ₹5,000). A FIFO queue cannot prioritize by bid amount without exhaustive searching.

### Q4: What is the difference between a Queue and a Priority Queue?
**Answer:**
- **Standard Queue:** Operates on FIFO (First-In-First-Out) principle. Element inserted first is removed first.
- **Priority Queue:** Operates based on element priority regardless of insertion order. The element with the highest priority (e.g., largest bid amount) is always at the root (`peek()`).

### Q5: How did you implement the Priority Queue comparator in Java?
**Answer:** Java's `java.util.PriorityQueue` is a Min-Heap by default. In `Bid.java`, we implemented `Comparable<Bid>` and reversed the amount comparison:
```java
public int compareTo(Bid other) {
    if (this.amount != other.amount) {
        return Double.compare(other.amount, this.amount); // Descending order
    }
    return Long.compare(this.timestamp, other.timestamp); // Ascending timestamp for ties
}
```
This reverses the heap ordering, effectively transforming the Min-Heap into a Max-Heap so `peek()` returns the highest bid.

### Q6: What is multithreading?
**Answer:** Multithreading is an operating system execution model where a process splits into two or more concurrently running execution threads. Each thread shares the process's memory space (heap) but maintains its own execution stack and program counter.

### Q7: Why are multiple threads used in this project?
**Answer:** Multiple threads are used to simulate real-world concurrent bidding where multiple users attempt to place bids on the same auction simultaneously. In `ConcurrentBidSimulation.java`, we instantiate multiple `BidderThread` objects running on native OS threads to test thread synchronization.

### Q8: What is concurrency?
**Answer:** Concurrency is the ability of an operating system to execute multiple tasks or instructions in overlapping time intervals. On multi-core processors, concurrent threads can execute simultaneously across different CPU cores.

### Q9: What is a race condition?
**Answer:** A race condition occurs when two or more threads access shared data concurrently and try to modify it at the same time. If the execution outcome depends on the nondeterministic order of thread scheduling, the system state can become corrupted.

### Q10: What is a critical section?
**Answer:** A critical section is a sequence of instructions accessing shared resources (such as current highest bid) that must not be concurrently accessed by more than one execution thread. It must be executed as an atomic (indivisible) unit.

### Q11: How does your project prevent race conditions?
**Answer:** Our project uses mutual exclusion synchronization via Java's `ReentrantLock` in `ConcurrencyManager.java`. Before entering the critical section in `AuctionManager.placeBid()`, a thread must call `lock()`. Other threads attempting to enter are blocked until the lock holder calls `unlock()`.

### Q12: Why is synchronization required in bid placement?
**Answer:** Without synchronization, if Thread A and Thread B both read a current highest bid of ₹10,000 at the same instant, both will compute the minimum next bid as ₹10,500. Both will submit ₹10,500, resulting in two duplicate bids being accepted and violating the minimum increment rule.

### Q13: What specific synchronization mechanism did you use?
**Answer:** We used `java.util.concurrent.locks.ReentrantLock` with fairness enabled (`new ReentrantLock(true)`). A fair lock guarantees that waiting threads acquire the lock in first-come, first-served (FIFO) order, preventing thread starvation.

### Q14: What happens step-by-step when two users bid simultaneously?
**Answer:**
1. Thread 1 and Thread 2 arrive at `placeBid()`.
2. Thread 1 acquires `concurrencyManager.lock()`. Thread 2 is suspended by the OS scheduler.
3. Thread 1 validates bid ₹10,500 against current highest bid ₹10,000, inserts bid into Priority Queue, updates highest bid to ₹10,500, and calls `unlock()`.
4. Thread 2 is awakened, acquires the lock, reads updated highest bid ₹10,500, calculates minimum required bid ₹11,000, and rejects Thread 2's bid of ₹10,500.
5. Auction state remains completely valid!

### Q15: Why did you use Java for the core auction engine?
**Answer:** Java provides robust multi-core thread support (`java.lang.Thread`), low-level lock primitives (`ReentrantLock`), and built-in optimized data structures (`PriorityQueue`). It allows explicit control over multithreading and memory synchronization.

### Q16: Why did you use Python Flask for the backend?
**Answer:** Flask serves as a lightweight, clean API gateway that handles HTTP route blueprinting, request parsing, JSON formatting, and database persistence (SQLite) efficiently.

### Q17: Why did you use SQLite for database storage?
**Answer:** SQLite is a serverless, file-based relational database that provides full ACID compliance, zero setup overhead, and persistent storage for auctions and bid histories across server restarts.

### Q18: How does Python Flask communicate with the Java Engine?
**Answer:** Flask communicates with Java over an internal HTTP REST protocol. The Java engine runs an embedded `HttpServer` on port 9090. Flask's `java_bridge.py` uses Python's `requests` library to exchange JSON payloads with Java endpoints (`/place-bid`, `/get-bids`, `/simulate-concurrent-bids`).

### Q19: What happens when an invalid bid (below minimum increment) is submitted?
**Answer:** The Java engine calculates `minimumBid = currentHighestBid + minimumIncrement`. If `amount < minimumBid`, `placeBid()` returns `BidResult(false, "Bid must be at least ₹X", currentHighestBid)`. Flask receives this result, does NOT insert any record into SQLite, and returns HTTP 400 with the error message.

### Q20: How is the current highest bid determined?
**Answer:** The current highest bid is maintained in the `Auction` object (`currentHighestBid`) and continuously matches the root element (`peek()`) of the `BidPriorityQueue`.

### Q21: How does minimum bid increment validation work when an auction has NO prior bids?
**Answer:** In `Auction.java`:
```java
public double getMinimumNextBid() {
    if (currentHighestBid <= 0) return startingPrice;
    return currentHighestBid + minimumIncrement;
}
```
If no bids exist, the minimum required bid is the item's starting price.

### Q22: What happens when an auction status becomes `ENDED`?
**Answer:** In `AuctionManager.placeBid()`, the system updates status based on current time. If `now > endTime` or status is set to `ENDED`, `placeBid()` rejects new bids with `"Auction has already ended."` The highest accepted bid remains permanently visible as the winning bid.

### Q23: What happens if the Java engine stops unexpectedly?
**Answer:** Flask's `java_bridge.py` catches `requests.ConnectionError` and returns a clean error payload (`{"success": false, "message": "Java engine is not running"}`). The database remains uncorrupted. Upon restarting Flask and Java, `sync_auctions_to_java()` reloads all SQLite auctions into the Java engine.

### Q24: What is `Thread.start()` and why is it used instead of `Thread.run()`?
**Answer:**
- `Thread.start()` requests the operating system kernel to instantiate a new native execution thread and invoke its `run()` method asynchronously.
- `Thread.run()` simply executes the method sequentially within the calling thread, defeating the purpose of multithreading.

### Q25: What is `Thread.join()` and why is it used?
**Answer:** `Thread.join()` is a synchronization barrier. When the main simulation thread calls `t.join()`, it pauses execution until thread `t` has terminated. This ensures the main thread collects simulation results only after all concurrent bidder threads have finished.

### Q26: What is the exact critical section in your project source code?
**Answer:** The critical section is lines 118–170 of `AuctionManager.java` inside the `placeBid()` method:
```java
concurrencyManager.lock();
try {
    // Read auction state -> Check status -> Compute minimum bid -> Validate -> Insert into PriorityQueue -> Update currentHighestBid
} finally {
    concurrencyManager.unlock();
}
```

### Q27: What shared data is protected by the `ReentrantLock`?
**Answer:** The lock protects:
1. `Auction.currentHighestBid`
2. `BidPriorityQueue` internal binary heap state
3. `auctions` HashMap lookup map

### Q28: What would happen if you removed the `ReentrantLock` from `AuctionManager.java`?
**Answer:** If the lock is removed, concurrent threads would experience race conditions. Multiple threads would read stale values of `currentHighestBid`, leading to duplicate accepted bids at the same price, corrupted Priority Queue node indexes, and violations of auction rules.

### Q29: What are the main limitations of the current system?
**Answer:**
1. Single Java engine process (not distributed across multiple servers).
2. Absence of user authentication (focuses on core DS/OS concepts).
3. HTTP polling/request-response architecture rather than WebSockets.

### Q30: What future improvements could be added in a production environment?
**Answer:**
1. WebSocket/Server-Sent Events for real-time live bid push notifications.
2. Distributed locking (e.g., Redis Redlock) across multiple backend instances.
3. User authentication with JWT and payment gateway integration.
