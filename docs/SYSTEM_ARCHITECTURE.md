# System Architecture & Flowcharts

**Project Title:** Online Auction Bid Management System  
**Academic Domain:** Data Structures & Operating System Concepts  

---

## 1. High-Level System Architecture

The Online Auction Bid Management System uses a decoupled, three-tier architecture comprising a web-based presentation layer, a Python Flask REST API gateway, an authoritative Java concurrency & Priority Queue engine, and an SQLite relational database.

```
┌─────────────────────────────────────────────────────────────────┐
│                      CLIENT / PRESENTATION                      │
│   HTML5 / Vanilla CSS / JavaScript (Fetch API - Client App)    │
│   (index.html, auction.html, admin.html, demo.html, about.html)  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                │ HTTP REST (JSON)
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     API GATEWAY / BACKEND                       │
│                   Python Flask Server (Port 5000)               │
│   - Route Blueprint (auction_routes.py)                         │
│   - Java Bridge HTTP Service (java_bridge.py)                   │
│   - Database Layer (db.py)                                      │
└─────────────────────────────────────────────────────────────────┘
                   │                               │
    Database SQL   │                               │ HTTP REST (JSON)
    Read / Write   ▼                               ▼ Port 9090
┌──────────────────────┐             ┌────────────────────────────┐
│   SQLite DATABASE    │             │    JAVA AUCTION ENGINE     │
│   (auction.db)       │             │   (com.sun.net.httpserver) │
│ - auctions table     │             │ - AuctionManager.java      │
│ - bids table         │             │ - ConcurrencyManager.java  │
└──────────────────────┘             │   (ReentrantLock)          │
                                     │ - BidPriorityQueue.java    │
                                     │   (PriorityQueue<Bid>)     │
                                     │ - ConcurrentBidSimulation  │
                                     │   (BidderThreads)          │
                                     └────────────────────────────┘
```

### Mermaid Architecture Diagram

```mermaid
graph TD
    Client[Browser Client HTML/JS/CSS] -->|HTTP REST JSON| Flask[Python Flask API Port 5000]
    Flask -->|SQLite SQL| DB[(SQLite Database auction.db)]
    Flask -->|HTTP REST JSON| JavaEngine[Java Auction Engine Port 9090]
    
    subgraph Java Engine Core
        JavaEngine --> Manager[AuctionManager]
        Manager --> Lock[ConcurrencyManager ReentrantLock]
        Manager --> PQ[BidPriorityQueue PriorityQueue<Bid>]
        Manager --> Simulator[ConcurrentBidSimulation]
        Simulator --> Threads[Bidder Threads Thread.start/join]
    end
```

---

## 2. Tier Responsibilities

### 2.1 Presentation Tier (Frontend)
- **Files:** `frontend/index.html`, `frontend/auction.html`, `frontend/admin.html`, `frontend/demo.html`, `frontend/about.html`, `frontend/js/*.js`, `frontend/css/style.css`.
- **Responsibilities:**
  - Provides responsive, accessible views for browsing auctions, placing manual bids, executing concurrent thread simulations, and viewing the live Priority Queue.
  - Communicates asynchronously with the Flask API via `api.js` using `fetch()`.

### 2.2 Application / Gateway Tier (Python Flask)
- **Files:** `python-backend/app.py`, `python-backend/routes/auction_routes.py`, `python-backend/services/java_bridge.py`.
- **Responsibilities:**
  - Exposes RESTful endpoints on `http://localhost:5000/api`.
  - Performs initial schema validation, type checking, and boundary validation.
  - Bridges requests to the Java Auction Engine running on `http://localhost:9090`.
  - Persists accepted auction metadata and bid records into SQLite.
  - On startup (`sync_auctions_to_java()`), reconstructs auction state in the Java engine from SQLite records.

### 2.3 Concurrency & Data Structure Engine (Java Engine)
- **Files:** `java-engine/src/engine/*.java`.
- **Responsibilities:**
  - Serves HTTP requests via built-in `com.sun.net.httpserver.HttpServer` on port 9090 with a 10-thread fixed pool (`Executors.newFixedThreadPool(10)`).
  - Enforces thread safety over critical sections using `ReentrantLock` in `ConcurrencyManager.java`.
  - Maintains `BidPriorityQueue` (binary heap) for $O(1)$ peek retrieval of winning bids and $O(\log n)$ insertion.
  - Executes multi-threaded simulation of concurrent bidders via `BidderThread` objects running on real OS threads.

### 2.4 Database Tier (SQLite)
- **Files:** `python-backend/database/db.py`, `python-backend/database/auction.db`.
- **Responsibilities:**
  - Relational storage for `auctions` and `bids` tables.
  - Enforces foreign key constraints (`PRAGMA foreign_keys = ON`).

---

## 3. Flowcharts

### 3.1 Normal Bidding Flowchart

```mermaid
flowchart TD
    A[START: User Submits Bid] --> B[Client Sends POST to /api/auctions/id/bids]
    B --> C{Flask Schema & Type Check Valid?}
    C -- NO --> D[Return HTTP 400 Bad Request]
    C -- YES --> E{Check Auction Status}
    E -- UPCOMING --> F[Return HTTP 409: Auction Not Started]
    E -- ENDED --> G[Return HTTP 409: Auction Already Ended]
    E -- ACTIVE --> H[Forward Bid to Java Engine POST /place-bid]
    H --> I[Java Engine Acquires ReentrantLock]
    I --> J{Bid Amount >= Minimum Next Bid?}
    J -- NO --> K[Reject Bid in Engine]
    K --> L[Release ReentrantLock]
    L --> M[Return HTTP 400: Bid Rejected]
    J -- YES --> N[Add Bid to PriorityQueue O log n]
    N --> O[Update currentHighestBid]
    O --> P[Release ReentrantLock]
    P --> Q[Flask Receives Success from Java]
    Q --> R[Insert Bid Record into SQLite Database]
    R --> S[UPDATE auctions SET current_highest_bid in SQLite]
    S --> T[Return HTTP 200: Bid Accepted]
    T --> U[END]
```

### 3.2 Concurrent Bidding Flowchart (Multithreaded Execution)

```mermaid
flowchart TD
    A[START: User Triggers Concurrent Simulation] --> B[Flask Sends POST /simulate-concurrent-bids to Java]
    B --> C[Java Instantiates N BidderThread Objects]
    C --> D[Wrap BidderThreads in java.lang.Thread Objects]
    D --> E[Call Thread.start on ALL Threads Concurrently]
    
    subgraph Parallel Execution Phase OS Threads
        F1[Thread 1] --> L1[Acquire ReentrantLock]
        F2[Thread 2] --> L2[Acquire ReentrantLock]
        F3[Thread N] --> L3[Acquire ReentrantLock]
        
        L1 --> V1[Validate & Update State / PriorityQueue]
        L2 --> V2[Validate & Update State / PriorityQueue]
        L3 --> V3[Validate & Update State / PriorityQueue]
        
        V1 --> R1[Release ReentrantLock]
        V2 --> R2[Release ReentrantLock]
        V3 --> R3[Release ReentrantLock]
    end
    
    R1 --> J[Main Simulation Thread Calls Thread.join]
    R2 --> J
    R3 --> J
    
    J --> K[All Threads Joined Synchronization Barrier Passed]
    K --> L[Collect Simulation Results ACCEPTED / REJECTED]
    L --> M[Flask Persists Accepted Bids to SQLite]
    M --> N[Return Final Simulation Summary JSON to Client]
    N --> O[END]
```
