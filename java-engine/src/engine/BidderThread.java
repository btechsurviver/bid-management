package engine;

/**
 * BidderThread represents a single bidder attempting to place a bid.
 * 
 * This class implements Runnable so it can be executed as a separate thread.
 * Each BidderThread has its own bidder name and bid amount, and it uses
 * the shared AuctionManager to submit its bid.
 * 
 * ============================================================
 * WHY Thread.start() AND NOT Thread.run()?
 * ============================================================
 * 
 * - Thread.run() executes the method in the CURRENT thread (sequential).
 * - Thread.start() creates a NEW OS-level thread and runs the method
 *   concurrently with other threads.
 * 
 * We must use start() so that multiple bidders actually run at the
 * same time, which is the whole point of the concurrency demonstration.
 * 
 * ============================================================
 * HOW IT WORKS
 * ============================================================
 * 
 * 1. The simulation creates multiple BidderThread objects.
 * 2. Each one is wrapped in a Thread and started with Thread.start().
 * 3. All threads run concurrently and call AuctionManager.placeBid().
 * 4. The AuctionManager uses ConcurrencyManager (ReentrantLock) to
 *    ensure only one thread enters the critical section at a time.
 * 5. Thread.join() is used to wait for all threads to finish before
 *    printing the results.
 */
public class BidderThread implements Runnable {
    private String bidderName;
    private int auctionId;
    private double bidAmount;
    private AuctionManager auctionManager;

    // Store the result after the thread finishes
    private AuctionManager.BidResult result;

    public BidderThread(String bidderName, int auctionId, double bidAmount,
                        AuctionManager auctionManager) {
        this.bidderName = bidderName;
        this.auctionId = auctionId;
        this.bidAmount = bidAmount;
        this.auctionManager = auctionManager;
        this.result = null;
    }

    /**
     * The run() method is called when the thread starts.
     * It attempts to place a bid through the AuctionManager.
     * 
     * The AuctionManager internally acquires a ReentrantLock, so even
     * though many threads call this at the same time, only one at a time
     * can execute the critical section (read-validate-insert).
     */
    @Override
    public void run() {
        String threadName = Thread.currentThread().getName();
        System.out.println("[" + threadName + "] Attempting bid: \u20B9" + bidAmount);

        // This call is thread-safe because AuctionManager uses ReentrantLock
        result = auctionManager.placeBid(auctionId, bidderName, bidAmount);

        String status = result.success ? "ACCEPTED" : "REJECTED";
        System.out.println("[" + threadName + "] " + bidderName + " \u20B9" + bidAmount
                         + " -> " + status + " (" + result.message + ")");
    }

    // --- Getters ---
    public String getBidderName() { return bidderName; }
    public double getBidAmount() { return bidAmount; }
    public AuctionManager.BidResult getResult() { return result; }
}
