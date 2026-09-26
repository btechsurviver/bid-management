# Algorithms & Pseudocode Specifications

**Project Title:** Online Auction Bid Management System  
**Academic Domain:** Data Structures & Operating System Concepts  

---

## 1. Core Algorithms

### 1.1 Bid Validation & Critical Section Algorithm (`AuctionManager.java`)

```
Algorithm: ValidateAndPlaceBid(auctionId, bidderName, amount)
Input: auctionId (Integer), bidderName (String), amount (Double)
Output: BidResult (Boolean success, String message, Double highestBid)

1. Acquire Exclusive Lock (concurrencyManager.lock())
2. Try:
3.     Retrieve auction from internal map using auctionId
4.     If auction IS NULL:
5.         Return BidResult(FALSE, "Auction not found", 0)
6.     
7.     Update auction status based on System.currentTimeMillis()
8.     If status == "UPCOMING":
9.         Return BidResult(FALSE, "Auction has not started yet", 0)
10.    If status == "ENDED":
11.        Return BidResult(FALSE, "Auction has already ended", 0)
12.    
13.    Calculate minimumBid = auction.getMinimumNextBid()
14.    // If currentHighestBid == 0 -> minimumBid = startingPrice
15.    // Else -> minimumBid = currentHighestBid + minimumIncrement
16.    
17.    If amount < minimumBid:
18.        Return BidResult(FALSE, "Bid must be at least minimumBid", auction.currentHighestBid)
19.    
20.    // Bid is valid
21.    Create new Bid object b(auctionId, bidderName, amount, timestamp)
22.    Insert b into PriorityQueue: auction.bidQueue.addBid(b)  [O(log n)]
23.    Update auction.currentHighestBid = amount
24.    
25.    Return BidResult(TRUE, "Bid accepted", amount)
26. Finally:
27.    Release Exclusive Lock (concurrencyManager.unlock())
```

---

### 1.2 Concurrent Simulation & Thread Barrier Algorithm (`ConcurrentBidSimulation.java`)

```
Algorithm: RunConcurrentSimulation(auctionManager, auctionId, biddersList)
Input: auctionManager (AuctionManager instance), auctionId (Integer), biddersList (List of BidderEntry)
Output: List of SimulationResult (bidder, amount, status, message)

1. Create empty List bidderThreads
2. Create empty List OSThreads
3.
4. For i = 0 to biddersList.size() - 1:
5.     Create BidderThread bt(biddersList[i].name, auctionId, biddersList[i].amount, auctionManager)
6.     Add bt to bidderThreads
7.     Create java.lang.Thread t(bt, "Bidder-" + (i + 1))
8.     Add t to OSThreads
9.
10. // Phase 1: Launch all OS threads simultaneously
11. For each Thread t in OSThreads:
12.     t.start()  // Creates a new operating system execution thread
13.
14. // Phase 2: Synchronization Barrier (Wait for all threads to complete)
15. For each Thread t in OSThreads:
16.     Try:
17.         t.join()  // Blocks main thread until thread t terminates
18.     Catch InterruptedException:
19.         Log thread interruption
20.
21. // Phase 3: Collect results
22. Create empty List results
23. For each BidderThread bt in bidderThreads:
24.     res = bt.getResult()
25.     status = (res.success == TRUE) ? "ACCEPTED" : "REJECTED"
26.     Append SimulationResult(bt.name, bt.amount, status, res.message) to results
27.
28. Return results
```

---

### 1.3 Priority Queue Heap Management & Ordering (`Bid.java` & `BidPriorityQueue.java`)

```
Algorithm: PriorityQueueCompare(Bid thisBid, Bid otherBid)
Input: thisBid (Bid), otherBid (Bid)
Output: Integer (-1, 0, 1)

1. If thisBid.amount != otherBid.amount:
2.     Return Compare(otherBid.amount, thisBid.amount)  // Reversed comparison -> Max-Heap behavior
3. Else:
4.     Return Compare(thisBid.timestamp, otherBid.timestamp) // Ascending timestamp -> First-Come First-Served
```

---

## 2. Pseudocode

### 2.1 Normal Bid Submission Pseudocode

```text
PROCEDURE SubmitBid(auction_id, bidder_name, amount)
    INPUT: auction_id, bidder_name, amount
    
    // Step 1: Validate input inputs
    IF bidder_name IS EMPTY OR amount <= 0 THEN
        RETURN Response(400, "Invalid bidder name or amount")
    END IF
    
    // Step 2: Fetch auction record from database
    auction = DB.query("SELECT * FROM auctions WHERE id = ?", auction_id)
    IF auction IS NULL THEN
        RETURN Response(404, "Auction not found")
    END IF
    
    // Step 3: Check state status
    IF CurrentTime() < auction.start_time THEN
        RETURN Response(409, "Auction has not started yet")
    ELSE IF CurrentTime() > auction.end_time THEN
        RETURN Response(409, "Auction has already ended")
    END IF
    
    // Step 4: Delegate to Java Engine for synchronized validation
    engine_result = JavaBridge.post("/place-bid", {auctionId, bidderName, amount})
    
    // Step 5: Handle result & update persistent storage
    IF engine_result.success IS TRUE THEN
        DB.execute("INSERT INTO bids (auction_id, bidder_name, amount) VALUES (?, ?, ?)", 
                   auction_id, bidder_name, amount)
        DB.execute("UPDATE auctions SET current_highest_bid = ? WHERE id = ?", 
                   amount, auction_id)
        RETURN Response(200, "Bid accepted", engine_result.highestBid)
    ELSE
        RETURN Response(400, engine_result.message)
    END IF
END PROCEDURE
```

### 2.2 Concurrent Bid Submission Pseudocode

```text
PROCEDURE RunConcurrentBidders(auction_id, bidders_array)
    INPUT: auction_id, bidders_array (list of name and amount pairs)
    
    threads = []
    results = []
    
    FOR EACH bidder IN bidders_array DO
        // Instantiate executable task
        task = NEW BidderTask(bidder.name, auction_id, bidder.amount)
        // Create operating system thread
        thread = NEW SystemThread(task)
        APPEND thread TO threads
    END FOR
    
    // Start concurrent execution
    FOR EACH thread IN threads DO
        thread.start()
    END FOR
    
    // Synchronize and await thread completion
    FOR EACH thread IN threads DO
        thread.join()
    END FOR
    
    // Gather and evaluate results
    FOR EACH thread IN threads DO
        APPEND thread.task.result TO results
    END FOR
    
    RETURN results
END PROCEDURE
```

### 2.3 Priority Queue Operations Pseudocode

```text
CLASS PriorityQueueManager:
    PRIVATE heapArray = []
    
    PROCEDURE InsertBid(bid):
        // Add element to end of array and heapify up O(log n)
        heapArray.append(bid)
        BubbleUp(heapArray.length - 1)
    END PROCEDURE
    
    PROCEDURE GetHighestBid():
        // Root of max-heap always contains highest priority bid O(1)
        IF heapArray IS EMPTY THEN
            RETURN NULL
        END IF
        RETURN heapArray[0]
    END PROCEDURE
    
    PROCEDURE BubbleUp(index):
        WHILE index > 0 DO
            parentIndex = (index - 1) / 2
            IF PriorityCompare(heapArray[index], heapArray[parentIndex]) < 0 THEN
                Swap(heapArray, index, parentIndex)
                index = parentIndex
            ELSE
                BREAK
            END IF
        END WHILE
    END PROCEDURE
END CLASS
```

---

## 3. Time & Space Complexity Analysis

| Operation | Algorithm / Component | Time Complexity | Space Complexity | Explanation |
| :--- | :--- | :--- | :--- | :--- |
| **Get Highest Bid** | `PriorityQueue.peek()` | $\mathcal{O}(1)$ | $\mathcal{O}(1)$ | Max-Heap root element accessible in constant time. |
| **Insert Bid** | `PriorityQueue.add()` | $\mathcal{O}(\log n)$ | $\mathcal{O}(1)$ | Binary heap tree rebalancing (sift-up). |
| **Get Sorted Queue List** | `getAllBidsSorted()` | $\mathcal{O}(n \log n)$ | $\mathcal{O}(n)$ | Creates copy array and sorts $n$ elements. |
| **Lock Acquisition** | `ReentrantLock.lock()` | $\mathcal{O}(1)$ avg | $\mathcal{O}(1)$ | Atomic CAS operation in Java AQS (`AbstractQueuedSynchronizer`). |
| **Thread Spawning** | `new Thread(task).start()` | $\mathcal{O}(1)$ | $\mathcal{O}(1)$ stack per thread | Allocates OS native thread stack (~1MB default). |
| **Thread Synchronization** | `Thread.join()` | $\mathcal{O}(k)$ for $k$ threads | $\mathcal{O}(1)$ | Main thread waits on thread death notifications. |
| **Database Read** | SQLite `SELECT WHERE id` | $\mathcal{O}(1)$ | $\mathcal{O}(1)$ | Primary key index lookup. |
| **Database Write** | SQLite `INSERT / UPDATE` | $\mathcal{O}(1)$ | $\mathcal{O}(1)$ | Single row insertion with WAL transaction log write. |
