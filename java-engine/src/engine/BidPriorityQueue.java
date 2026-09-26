package engine;

import java.util.ArrayList;
import java.util.List;
import java.util.PriorityQueue;

/**
 * BidPriorityQueue manages all bids for a single auction using Java's PriorityQueue.
 * 
 * WHY PRIORITY QUEUE?
 * -------------------
 * In an auction system, we frequently need the highest bid. A PriorityQueue (implemented
 * as a binary heap internally) gives us O(1) access to the highest bid via peek(),
 * and O(log n) insertion via add(). This is more efficient than sorting an ArrayList
 * every time (which would be O(n log n) per query).
 * 
 * The Bid class implements Comparable with reversed amount ordering, so the PriorityQueue
 * treats the highest-amount bid as the "minimum" element, making peek() return
 * the highest bid.
 * 
 * THREAD SAFETY:
 * All public methods are synchronized. This is a basic concurrency control measure
 * that will be expanded in Phase 3 with ReentrantLock and multiple bidder threads.
 */
public class BidPriorityQueue {
    private PriorityQueue<Bid> queue;

    public BidPriorityQueue() {
        this.queue = new PriorityQueue<>();
    }

    /**
     * Add a bid to the priority queue.
     * synchronized ensures only one thread can add a bid at a time.
     */
    public synchronized void addBid(Bid bid) {
        queue.add(bid);
    }

    /**
     * Get the highest bid without removing it.
     * Since our Comparable ordering is reversed, peek() returns the highest amount.
     */
    public synchronized Bid getHighestBid() {
        return queue.peek();
    }

    /**
     * Get all bids as a list, sorted from highest to lowest.
     * This creates a copy so the original queue is not modified.
     */
    public synchronized List<Bid> getAllBidsSorted() {
        List<Bid> sorted = new ArrayList<>(queue);
        sorted.sort(null); // Uses Bid's natural ordering (highest first)
        return sorted;
    }

    /**
     * Get the number of bids in the queue.
     */
    public synchronized int size() {
        return queue.size();
    }

    /**
     * Clear all bids from the queue.
     */
    public synchronized void clear() {
        queue.clear();
    }
}
