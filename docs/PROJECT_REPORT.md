# Academic Project Report

## ONLINE AUCTION BID MANAGEMENT SYSTEM

**A Multi-Tier Web Application Demonstrating Priority Queue Data Structures and Operating System Concurrency Control**

---

### Table of Contents
1. [Title Page](#1-title-page)
2. [Abstract](#2-abstract)
3. [Introduction](#3-introduction)
4. [Problem Statement](#4-problem-statement)
5. [Objectives](#5-objectives)
6. [Existing System vs. Proposed System](#6-existing-system-vs-proposed-system)
7. [Technologies Used](#7-technologies-used)
8. [System Architecture](#8-system-architecture)
9. [Data Structures Implementation](#9-data-structures-implementation)
10. [Operating System Concepts](#10-operating-system-concepts)
11. [System Modules](#11-system-modules)
12. [Database Design](#12-database-design)
13. [Algorithms](#13-algorithms)
14. [Pseudocode](#14-pseudocode)
15. [Implementation Details](#15-implementation-details)
16. [Testing & Verification](#16-testing--verification)
17. [Results & Discussions](#17-results--discussions)
18. [Limitations](#18-limitations)
19. [Future Scope](#19-future-scope)
20. [Conclusion](#20-conclusion)
21. [References](#21-references)

---

### 1. Title Page
- **Project Title:** Online Auction Bid Management System
- **Academic Degree:** Bachelor of Technology (B.Tech) in Computer Science & Engineering
- **Domain:** Data Structures & Operating System Architecture
- **Implementation Stack:** HTML5, CSS3, JavaScript, Python Flask, Java, SQLite

---

### 2. Abstract
The Online Auction Bid Management System is a robust multi-tier web application designed to demonstrate the practical application of core computer science principles: Priority Queue data structures for efficient top-element retrieval and Operating System concurrency controls for thread-safe concurrent execution. Online auctions frequently experience high-concurrency traffic during closing seconds, leading to race conditions if state mutations are unsynchronized. Furthermore, finding the highest bid in a large bid history requires optimal heap storage. 

This project implements a decoupled architecture: an HTML/CSS/JS presentation layer, a Python Flask REST API gateway, an SQLite relational database, and an authoritative Java Auction Engine. The Java engine utilizes a max-heap `PriorityQueue<Bid>` providing $O(1)$ peek retrieval and $O(\log n)$ bid insertion, while enforcing mutual exclusion over critical sections using `ReentrantLock`. Experimental results confirm complete race condition prevention and $100\%$ persistent state consistency under multi-threaded bidding stress.

---

### 3. Introduction
Online auction platforms allow users to place competitive bids on items within set time windows. In modern web architectures, handling concurrent user actions requires solving two primary engineering challenges:
1. **Data Ordering:** Rapidly identifying the current highest valid bid without scanning linear arrays.
2. **Concurrency Control:** Ensuring that multiple simultaneous bid submissions from different users do not create race conditions or stale-read state corruption.

This project addresses both challenges by combining web technologies with core Java concurrency primitives.

---

### 4. Problem Statement
In an un-synchronized auction system:
1. **Race Conditions:** When two users submit bids simultaneously, both user threads read the same current highest bid (e.g., ₹10,000). Both calculate the minimum next bid as ₹10,500 and submit ₹10,500. Without locking, both bids are accepted, violating the minimum increment rule and corrupting auction state.
2. **Search Inefficiency:** Storing bids in an unsorted list requires $O(n)$ scan time or $O(n \log n)$ sorting time per query to identify the winning bid.

---

### 5. Objectives
- Implement a **Priority Queue** ($O(1)$ peek, $O(\log n)$ insertion) for highest bid management.
- Implement **Concurrency Control** using `ReentrantLock` to serialize critical section access.
- Build a **Multithreaded Simulation Engine** using native `java.lang.Thread` objects to simulate concurrent users.
- Provide a clean, responsive UI with a live Priority Queue visualizer and interactive demonstration controls.
- Maintain persistent database storage in SQLite.

---

### 6. Existing System vs. Proposed System

| Parameter | Existing / Naive System | Proposed System |
| :--- | :--- | :--- |
| **Data Structure** | Unsorted Array / List ($O(n)$ search) | Binary Heap `PriorityQueue<Bid>` ($O(1)$ peek) |
| **Concurrency Control** | None / Naive database locks | Thread-safe Java `ReentrantLock` critical section |
| **Thread Management** | Single-threaded sequential processing | Multi-threaded simulation using native OS threads |
| **Bid Validation** | Non-atomic check-then-act | Atomic read-validate-update sequence |
| **Architecture** | Monolithic or un-synchronized script | Decoupled HTML/Flask/Java Engine/SQLite architecture |

---

### 7. Technologies Used
- **Frontend:** HTML5, Vanilla CSS, JavaScript (Fetch API).
- **Backend Gateway:** Python Flask REST API.
- **Auction Engine:** Java 17+ (`com.sun.net.httpserver`, `java.util.PriorityQueue`, `java.util.concurrent.locks.ReentrantLock`).
- **Database:** SQLite 3 (`auction.db`).

---

### 8. System Architecture
*(Refer to `docs/SYSTEM_ARCHITECTURE.md` for full detailed diagrams).*

The presentation tier sends HTTP JSON requests to Flask (port 5000). Flask validates schemas, syncs state with SQLite, and forwards auction state mutations to the Java Auction Engine (port 9090). Java serializes critical section access using `ReentrantLock` and updates its internal `BidPriorityQueue`.

---

### 9. Data Structures Implementation
- **Class:** `BidPriorityQueue.java` encapsulating `java.util.PriorityQueue<Bid>`.
- **Comparator (`Bid.java`):** Reverses default Min-Heap behavior by comparing `Double.compare(other.amount, this.amount)` to achieve Max-Heap behavior. Ties are broken by `Long.compare(this.timestamp, other.timestamp)` (First-Come, First-Served).
- **Complexity:** $O(1)$ peek retrieval, $O(\log n)$ bid insertion.

---

### 10. Operating System Concepts
- **Critical Section:** `AuctionManager.placeBid()` method reading price, checking status, validating minimum increment, inserting into Priority Queue, and updating highest bid.
- **Synchronization:** `ReentrantLock` with fairness enabled (`new ReentrantLock(true)`).
- **Thread Management:** `BidderThread` implementing `Runnable`, started via `Thread.start()` and synchronized via `Thread.join()`.

---

### 11. System Modules
1. **Auction Management Module:** Handles auction creation, start time, end time, and status calculation (`UPCOMING`, `ACTIVE`, `ENDED`).
2. **Bid Validation Module:** Enforces starting price and minimum bid increment rules.
3. **Concurrency Simulation Module:** Spawns 3–20 concurrent bidder threads to test lock serialization.
4. **Priority Queue Visualizer Module:** Renders the internal heap order in real time.
5. **Database Persistence Module:** Stores relational auction and bid records in SQLite.

---

### 12. Database Design
- **`auctions` Table:** `id`, `title`, `description`, `starting_price`, `current_highest_bid`, `minimum_increment`, `start_time`, `end_time`, `status`, `created_at`.
- **`bids` Table:** `id`, `auction_id` (FK $\rightarrow$ `auctions.id`), `bidder_name`, `amount`, `created_at`.

---

### 13. Algorithms
*(Refer to `docs/ALGORITHMS.md` for full step-by-step algorithms).*

---

### 14. Pseudocode
*(Refer to `docs/ALGORITHMS.md` for complete pseudocode listings).*

---

### 15. Implementation Details
- Core Java Engine compiled using `javac engine/*.java` and started via `java engine.Main`.
- Embedded HTTP server uses thread pool `Executors.newFixedThreadPool(10)`.
- Python Flask backend registered under `/api` blueprint.

---

### 16. Testing & Verification
*(Refer to `docs/TEST_CASES.md` for complete 14-point test cases table).*
All test cases (TC01 through TC14) passed with $100\%$ verification status.

---

### 17. Results & Discussions
Experimental multithreaded simulations confirmed:
- Zero race conditions observed under 20-thread stress tests.
- Constant $O(1)$ time performance for winning bid lookup.
- Complete data consistency between Java in-memory heap and SQLite database.

---

### 18. Limitations
- Single Java Engine process (not distributed across multiple nodes).
- Lack of user authentication (scope focused on DS/OS core concepts).

---

### 19. Future Scope
- Distributed lock implementation (e.g., Redis Redlock).
- Real-time WebSocket push notifications for active bids.
- User authentication and payment gateway integration.

---

### 20. Conclusion
The Online Auction Bid Management System successfully achieves all project goals. By combining a Java Max-Heap Priority Queue with `ReentrantLock` concurrency control, the application guarantees $O(1)$ winning bid retrieval and bulletproof thread safety during high-concurrency bidding events.

---

### 21. References
1. Silberschatz, A., Galvin, P. B., & Gagne, G. (2018). *Operating System Concepts* (10th ed.). Wiley.
2. Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C. (2009). *Introduction to Algorithms* (3rd ed.). MIT Press.
3. Oracle Java Documentation: `java.util.PriorityQueue` & `java.util.concurrent.locks.ReentrantLock`.
4. Flask Documentation: Pallets Projects (Python Web Development).
