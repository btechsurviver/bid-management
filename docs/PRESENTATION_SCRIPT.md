# College Viva Presentation Script (5–7 Minutes)

**Project Title:** Online Auction Bid Management System  
**Presenter(s):** B.Tech Student Team  
**Focus:** Data Structures (Priority Queue) & Operating Systems (Concurrency Control)  

---

### Slide 1 / Section 1: Introduction (0:00 - 0:45)

> *"Good morning, respected external examiner and faculty members. Today we are presenting our B.Tech computer science project titled **Online Auction Bid Management System**.*
>
> *Online auctions are an ideal domain to study two core computer science concepts:*
> 1. *First, how to retrieve the highest winning bid in $O(1)$ constant time using a **Priority Queue**.*
> 2. *Second, how to handle multiple concurrent bidders without data corruption using **Operating System Concurrency Control**.*
>
> *Our project is a working multi-tier web application built using HTML, CSS, JavaScript, Python Flask, Java, and SQLite."*

---

### Slide 2 / Section 2: Problem Statement & Motivation (0:45 - 1:30)

> *"In real-world auction websites, thousands of users might attempt to place a bid on an item during the final seconds of an auction.*
>
> *If two users submit bids at the exact same millisecond, a classic OS **race condition** occurs. Both threads read the same current price, both pass validation, and both update the database with duplicate amounts. This violates the auction minimum increment rule.*
>
> *Furthermore, searching through an unsorted array of thousands of bids to find the highest bid takes $O(n)$ linear time, which is inefficient. We solved both problems in our architecture."*

---

### Slide 3 / Section 3: Architecture & Tech Stack (1:30 - 2:30)

> *"Let us briefly look at our architecture:*
> - *Our **Frontend** is built using HTML, clean Vanilla CSS, and JavaScript fetch API.*
> - *Our **API Layer** is written in Python Flask, which handles HTTP routes and database persistence in SQLite.*
> - *Our **Core Auction Engine** is implemented in Java. It hosts our **Priority Queue** data structure and manages multithreading using Java's `ReentrantLock`.*
>
> *Communication between Flask and Java occurs via HTTP REST API on port 9090."*

---

### Slide 4 / Section 4: Live Demo — Normal Bidding & Increment Rules (2:30 - 3:30)

> *(Demonstrator opens `demo.html` in browser)*
>
> *"Now let us show the live system in action. On our Demo dashboard, we select our demo auction item: **Wireless Headphones**.*
> - *The starting price is ₹2,500 with a minimum increment of ₹100. So the minimum required next bid is ₹2,600.*
> - *First, we enter bidder name 'Ashish' and amount ₹2,600. When we click **Place Bid**, the bid is forwarded to the Java Engine, validated, accepted, and saved to SQLite. The minimum required next bid automatically updates to ₹2,700.*
> - *Now, to test validation, if we attempt an invalid bid of ₹2,650, our system rejects it immediately with the exact error message: 'Bid must be at least ₹2,700.00'."*

---

### Slide 5 / Section 5: Priority Queue Demonstration (3:30 - 4:30)

> *(Demonstrator scrolls to Section 3: Priority Queue visualizer)*
>
> *"Next, we demonstrate our Data Structure implementation: **Priority Queue**.*
>
> *In `Bid.java`, we implemented the `Comparable` interface and reversed the comparison order. This transforms Java's default Min-Heap into a Max-Heap.*
> - *As shown on screen, the Priority Queue root always displays the highest bid at position #1 with the **Highest Priority** badge.*
> - *This gives us $O(1)$ constant time complexity for `peek()` operations to get the winning bid, and $O(\log n)$ logarithmic insertion time via `add()`. If two bids have the exact same amount, our comparator breaks ties by selecting the earlier timestamp."*

---

### Slide 6 / Section 6: Concurrent Bidding & Concurrency Control (4:30 - 5:45)

> *(Demonstrator scrolls to Section 4: Concurrent Bidding Simulator)*
>
> *"Now we demonstrate our Operating System concept: **Concurrency Control and Multithreading**.*
>
> *We select 5 bidder threads and click **Run Concurrent Simulation**.*
> - *Under the hood, Java creates 5 separate `BidderThread` objects running on real native OS threads.*
> - *In `AuctionManager.java`, our `placeBid()` method is protected by a `ReentrantLock` in `ConcurrencyManager.java`.*
> - *When all 5 threads execute simultaneously, the lock serializes access to the critical section. Thread 1 acquires the lock, updates the price, and releases it. Thread 2 then reads the updated price and gets rejected because its bid is now below the new requirement.*
> - *As you can see in our results table, 3 bids were accepted and 2 were rejected, maintaining total auction consistency without race conditions."*

---

### Slide 7 / Section 7: Conclusion & Summary (5:45 - 6:30)

> *"Finally, we click **End Auction**. The auction status changes to `ENDED`, bidding is disabled, and winning bidder 'Ashish' is announced with the winning bid.*
>
> *If we refresh the page, all state remains persistent from our SQLite database.*
>
> *In summary, our project successfully implements a **Priority Queue** for $O(1)$ highest bid retrieval and **ReentrantLock Concurrency Control** for thread-safe bidding.*
>
> *Thank you, and we are now ready for your questions."*
