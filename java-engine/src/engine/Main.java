package engine;

import java.util.ArrayList;
import java.util.List;

/**
 * Main entry point for the Java Auction Engine.
 * 
 * Usage:
 *   cd java-engine/src
 *   javac engine/*.java
 * 
 *   java engine.Main              → Start HTTP server (for Flask)
 *   java engine.Main test         → Run PriorityQueue test
 *   java engine.Main concurrent   → Run concurrent bidding simulation
 */
public class Main {
    public static void main(String[] args) {
        if (args.length > 0) {
            if ("test".equals(args[0])) {
                runPriorityQueueTest();
                return;
            }
            if ("concurrent".equals(args[0])) {
                runConcurrentTest();
                return;
            }
        }

        // Default: Start the HTTP server
        try {
            System.out.println("========================================");
            System.out.println(" Java Auction Engine — Phase 3");
            System.out.println(" (with Concurrency Control)");
            System.out.println("========================================");
            System.out.println("Starting HTTP server on port 9090...");

            AuctionServer server = new AuctionServer(9090);
            server.start();

            System.out.println("Engine is ready. Waiting for requests from Flask...");
            System.out.println("Press Ctrl+C to stop.");
        } catch (Exception e) {
            System.err.println("Failed to start engine: " + e.getMessage());
            e.printStackTrace();
        }
    }

    /**
     * Standalone PriorityQueue test.
     * Run: java engine.Main test
     */
    private static void runPriorityQueueTest() {
        System.out.println("=== PriorityQueue Test ===\n");

        BidPriorityQueue pq = new BidPriorityQueue();

        System.out.println("Adding bids: 10000, 12000, 11000, 15000, 13000");
        pq.addBid(new Bid(1, "Ashish", 10000));
        pq.addBid(new Bid(1, "Rahul", 12000));
        pq.addBid(new Bid(1, "Priya", 11000));
        pq.addBid(new Bid(1, "Aman", 15000));
        pq.addBid(new Bid(1, "Sneha", 13000));

        Bid highest = pq.getHighestBid();
        System.out.println("\nHighest bid (from peek()): " + highest.getAmount()
                         + " by " + highest.getBidderName());
        System.out.println("Expected: 15000.0 by Aman");

        System.out.println("\nAll bids sorted (highest first):");
        for (Bid b : pq.getAllBidsSorted()) {
            System.out.println("  " + b.getBidderName() + " \u2014 \u20B9" + b.getAmount());
        }

        if (highest.getAmount() == 15000.0) {
            System.out.println("\n[PASS] PriorityQueue is working correctly!");
        } else {
            System.out.println("\n[FAIL] Expected 15000 but got " + highest.getAmount());
        }
    }

    /**
     * Standalone concurrent bidding test.
     * Run: java engine.Main concurrent
     * 
     * This creates an auction and launches multiple bidder threads to
     * demonstrate that the ReentrantLock prevents race conditions.
     */
    private static void runConcurrentTest() {
        System.out.println("========================================");
        System.out.println(" CONCURRENT BIDDING TEST");
        System.out.println("========================================\n");

        AuctionManager manager = new AuctionManager();

        // Create a test auction: starting price ₹10,000, increment ₹500
        // Set it to be ACTIVE (start = past, end = future)
        long now = System.currentTimeMillis();
        Auction testAuction = new Auction(
            999, "Test Laptop", "A laptop for concurrency testing",
            10000, 500,
            now - 60000,          // started 1 minute ago
            now + 3600000         // ends 1 hour from now
        );
        manager.loadAuction(testAuction);

        // Create bidders with various amounts
        List<ConcurrentBidSimulation.BidderEntry> bidders = new ArrayList<>();
        bidders.add(new ConcurrentBidSimulation.BidderEntry("Ashish", 10500));
        bidders.add(new ConcurrentBidSimulation.BidderEntry("Rahul", 11000));
        bidders.add(new ConcurrentBidSimulation.BidderEntry("Priya", 10500)); // should be rejected (too low after Ashish)
        bidders.add(new ConcurrentBidSimulation.BidderEntry("Aman", 12000));
        bidders.add(new ConcurrentBidSimulation.BidderEntry("Sneha", 11500)); // may be rejected depending on ordering

        // Run the simulation
        List<ConcurrentBidSimulation.SimulationResult> results =
            ConcurrentBidSimulation.runSimulation(manager, 999, bidders);

        // Verify final state
        Auction a = manager.getAuction(999);
        System.out.println("Final PriorityQueue peek: \u20B9" + a.getBidQueue().getHighestBid().getAmount());
        System.out.println("Final currentHighestBid: \u20B9" + a.getCurrentHighestBid());

        // Stress test: 20 threads with various amounts
        System.out.println("\n\n========================================");
        System.out.println(" STRESS TEST: 20 CONCURRENT THREADS");
        System.out.println("========================================\n");

        // Reset the auction
        Auction stressAuction = new Auction(
            998, "Stress Test Item", "Testing with many threads",
            1000, 100,
            now - 60000,
            now + 3600000
        );
        manager.loadAuction(stressAuction);

        List<ConcurrentBidSimulation.BidderEntry> stressBidders = new ArrayList<>();
        for (int i = 1; i <= 20; i++) {
            // Each bidder bids a different amount
            stressBidders.add(new ConcurrentBidSimulation.BidderEntry(
                "Thread-" + i, 1000 + (i * 100)
            ));
        }

        ConcurrentBidSimulation.runSimulation(manager, 998, stressBidders);

        Auction sa = manager.getAuction(998);
        System.out.println("Stress test final highest: \u20B9" + sa.getCurrentHighestBid());
        System.out.println("Total bids in PriorityQueue: " + sa.getBidQueue().size());

        // Verify: the highest bid in PQ should match currentHighestBid
        if (sa.getBidQueue().getHighestBid().getAmount() == sa.getCurrentHighestBid()) {
            System.out.println("[PASS] PriorityQueue and currentHighestBid are consistent!");
        } else {
            System.out.println("[FAIL] Inconsistency detected!");
        }
    }
}
