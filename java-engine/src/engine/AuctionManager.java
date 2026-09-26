package engine;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * AuctionManager is the central controller for all auction operations.
 * 
 * It manages a collection of Auction objects (stored in a HashMap for O(1) lookup by ID)
 * and handles:
 *   - Loading auctions (from data sent by Flask)
 *   - Bid validation against auction rules
 *   - Adding valid bids to the correct auction's PriorityQueue
 *   - Retrieving auction state and bid history
 * 
 * ============================================================
 * CONCURRENCY CONTROL (Phase 3)
 * ============================================================
 * 
 * The placeBid() method is the CRITICAL SECTION of this application.
 * It must read the current state, validate, and update atomically.
 * 
 * We use ConcurrencyManager (which wraps a ReentrantLock) to ensure
 * that only one thread can execute the critical section at a time.
 * 
 * The lock/unlock pattern:
 * 
 *   concurrencyManager.lock();
 *   try {
 *       // --- CRITICAL SECTION START ---
 *       // Read current highest bid
 *       // Validate bid amount against minimum
 *       // If valid: insert into PriorityQueue + update highest bid
 *       // --- CRITICAL SECTION END ---
 *   } finally {
 *       concurrencyManager.unlock();  // ALWAYS unlock, even on exceptions
 *   }
 * 
 * The finally block guarantees that the lock is released even if an
 * exception occurs, preventing deadlocks.
 */
public class AuctionManager {
    // Map of auction ID -> Auction object for fast lookup
    private Map<Integer, Auction> auctions;

    // Concurrency control using ReentrantLock
    private ConcurrencyManager concurrencyManager;

    public AuctionManager() {
        this.auctions = new HashMap<>();
        this.concurrencyManager = new ConcurrencyManager();
    }

    /**
     * Register an auction so the engine knows about it.
     * Called by AuctionServer when Flask sends auction data.
     */
    public void loadAuction(Auction auction) {
        concurrencyManager.lock();
        try {
            auctions.put(auction.getId(), auction);
        } finally {
            concurrencyManager.unlock();
        }
    }

    /**
     * Remove an auction from the engine.
     */
    public void removeAuction(int auctionId) {
        concurrencyManager.lock();
        try {
            auctions.remove(auctionId);
        } finally {
            concurrencyManager.unlock();
        }
    }

    /**
     * Get an auction by its ID.
     */
    public Auction getAuction(int auctionId) {
        concurrencyManager.lock();
        try {
            return auctions.get(auctionId);
        } finally {
            concurrencyManager.unlock();
        }
    }

    /**
     * Validate and place a bid on an auction.
     * 
     * THIS IS THE CRITICAL SECTION.
     * 
     * The entire sequence is protected by a ReentrantLock:
     * 
     *   LOCK
     *   ↓ Read current highest bid
     *   ↓ Calculate minimum allowed bid (highest + increment)
     *   ↓ Validate incoming bid amount
     *   ↓ If valid → add to PriorityQueue, update highest bid
     *   UNLOCK
     * 
     * Without the lock, two threads could both read the same
     * highest bid, both pass validation, and both update the state —
     * leading to duplicate accepted bids that violate the increment rule.
     * 
     * @param auctionId   the ID of the auction
     * @param bidderName  name of the bidder
     * @param amount      the bid amount
     * @return BidResult  containing success/failure and a message
     */
    public BidResult placeBid(int auctionId, String bidderName, double amount) {
        // Acquire the lock — only one thread can proceed past this point
        concurrencyManager.lock();
        try {
            String threadName = Thread.currentThread().getName();
            System.out.println("[" + threadName + "] Lock acquired for bid validation");

            Auction auction = auctions.get(auctionId);

            // Rule 1: Auction must exist
            if (auction == null) {
                return new BidResult(false, "Auction not found.", 0);
            }

            // Refresh auction status based on current time
            auction.updateStatus();

            // Rule 2: Auction must be ACTIVE
            if ("UPCOMING".equals(auction.getStatus())) {
                return new BidResult(false, "Auction has not started yet.", 0);
            }
            if ("ENDED".equals(auction.getStatus())) {
                return new BidResult(false, "Auction has already ended.", 0);
            }

            // Rule 3: Bid must meet minimum amount
            double minimumBid = auction.getMinimumNextBid();
            System.out.println("[" + threadName + "] Current highest: \u20B9" 
                             + auction.getCurrentHighestBid()
                             + " | Minimum allowed: \u20B9" + minimumBid
                             + " | Bid: \u20B9" + amount);

            if (amount < minimumBid) {
                return new BidResult(false,
                    "Bid must be at least \u20B9" + String.format("%.2f", minimumBid) + ".",
                    auction.getCurrentHighestBid());
            }

            // All rules passed — accept the bid
            Bid bid = new Bid(auctionId, bidderName, amount);

            // Add to the PriorityQueue (O(log n) insertion, thread-safe via lock)
            auction.getBidQueue().addBid(bid);

            // Update the current highest bid
            auction.setCurrentHighestBid(amount);

            System.out.println("[" + threadName + "] Bid ACCEPTED: \u20B9" + amount);
            return new BidResult(true, "Bid accepted.", amount);

        } finally {
            // ALWAYS release the lock, even if an exception occurs
            String threadName = Thread.currentThread().getName();
            System.out.println("[" + threadName + "] Lock released");
            concurrencyManager.unlock();
        }
    }

    /**
     * Get all bids for an auction, sorted highest to lowest.
     */
    public List<Bid> getBids(int auctionId) {
        concurrencyManager.lock();
        try {
            Auction auction = auctions.get(auctionId);
            if (auction == null) {
                return null;
            }
            return auction.getBidQueue().getAllBidsSorted();
        } finally {
            concurrencyManager.unlock();
        }
    }

    /**
     * Get the ConcurrencyManager for external inspection (e.g., logging).
     */
    public ConcurrencyManager getConcurrencyManager() {
        return concurrencyManager;
    }

    /**
     * Simple inner class to hold the result of a bid attempt.
     */
    public static class BidResult {
        public boolean success;
        public String message;
        public double highestBid;

        public BidResult(boolean success, String message, double highestBid) {
            this.success = success;
            this.message = message;
            this.highestBid = highestBid;
        }
    }
}
