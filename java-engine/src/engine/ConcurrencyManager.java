package engine;

import java.util.concurrent.locks.ReentrantLock;

/**
 * ConcurrencyManager provides thread synchronization for the auction engine.
 * 
 * ============================================================
 * WHY IS CONCURRENCY CONTROL NEEDED?
 * ============================================================
 * 
 * In a real auction system, multiple bidders may submit bids at almost
 * the same time. Without synchronization, this creates a RACE CONDITION:
 * 
 *   Thread A reads currentHighestBid = ₹10,000
 *   Thread B reads currentHighestBid = ₹10,000   (stale read!)
 *   Thread A writes new bid ₹10,500 → ACCEPTED
 *   Thread B writes new bid ₹10,500 → ALSO ACCEPTED (BUG!)
 * 
 * Both threads saw the same old value and both thought their bid was valid.
 * This violates the minimum increment rule.
 * 
 * ============================================================
 * SOLUTION: ReentrantLock
 * ============================================================
 * 
 * We use java.util.concurrent.locks.ReentrantLock to protect the
 * CRITICAL SECTION — the region of code where we:
 * 
 *   1. Read the current highest bid
 *   2. Calculate the minimum valid next bid
 *   3. Validate the incoming bid
 *   4. Insert the bid into the PriorityQueue
 *   5. Update the current highest bid
 * 
 * Only ONE thread can hold the lock at a time. Other threads must WAIT
 * until the lock is released. This guarantees that the entire
 * read-validate-update sequence is ATOMIC (all-or-nothing).
 * 
 * WHY ReentrantLock instead of synchronized?
 *   - More explicit: lock() and unlock() are visible in the code
 *   - Can be used with try/finally to guarantee unlock even on exceptions
 *   - Easier to explain during a viva
 *   - Supports fairness (FIFO ordering of waiting threads)
 * 
 * The lock is created with fairness=true, meaning threads that waited
 * longer get priority. This prevents thread starvation.
 */
public class ConcurrencyManager {
    
    // ReentrantLock with fairness=true ensures FIFO ordering of waiting threads
    private final ReentrantLock auctionLock;

    public ConcurrencyManager() {
        this.auctionLock = new ReentrantLock(true); // fair lock
    }

    /**
     * Acquire the lock before entering the critical section.
     * If another thread already holds the lock, this thread will WAIT.
     */
    public void lock() {
        auctionLock.lock();
    }

    /**
     * Release the lock after the critical section is complete.
     * This allows the next waiting thread to proceed.
     * MUST be called in a finally block to prevent deadlocks.
     */
    public void unlock() {
        auctionLock.unlock();
    }

    /**
     * Check if any thread is currently waiting for the lock.
     * Useful for logging/debugging.
     */
    public boolean hasWaitingThreads() {
        return auctionLock.hasQueuedThreads();
    }

    /**
     * Get the number of threads waiting for the lock.
     */
    public int getWaitingCount() {
        return auctionLock.getQueueLength();
    }
}
