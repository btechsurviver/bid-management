package engine;

import java.util.ArrayList;
import java.util.List;

/**
 * ConcurrentBidSimulation runs a demonstration of multiple bidder threads
 * competing for the same auction simultaneously.
 * 
 * This class is used in two ways:
 *   1. As a standalone test: java engine.Main concurrent
 *   2. Called by AuctionServer when Flask sends a /simulate-concurrent-bids request
 * 
 * ============================================================
 * HOW THE SIMULATION WORKS
 * ============================================================
 * 
 * 1. Create N BidderThread objects, each with a planned bid amount.
 * 2. Wrap each in a java.lang.Thread.
 * 3. Call Thread.start() on ALL threads to begin concurrent execution.
 *    (start() creates a new OS thread; run() would be sequential)
 * 4. Call Thread.join() on each thread to wait for all to finish.
 *    (join() blocks the main thread until the target thread completes)
 * 5. Collect results and display accepted/rejected bids.
 * 
 * Because AuctionManager uses a ReentrantLock, even though all threads
 * run concurrently, only one can enter the bid-validation critical section
 * at a time. This prevents race conditions.
 */
public class ConcurrentBidSimulation {

    /**
     * Run a concurrent bid simulation for the given auction.
     * 
     * @param auctionManager  the shared auction manager (with ReentrantLock)
     * @param auctionId       the auction to bid on
     * @param bidders         list of bidder entries (name + amount)
     * @return list of results for each bidder
     */
    public static List<SimulationResult> runSimulation(
            AuctionManager auctionManager, int auctionId,
            List<BidderEntry> bidders) {

        System.out.println("\n=========================================");
        System.out.println(" CONCURRENT AUCTION SIMULATION");
        System.out.println("=========================================");
        System.out.println("Auction ID: " + auctionId);
        System.out.println("Number of bidder threads: " + bidders.size());
        System.out.println("-----------------------------------------\n");

        // Step 1: Create BidderThread objects
        List<BidderThread> bidderThreads = new ArrayList<>();
        List<Thread> threads = new ArrayList<>();

        for (int i = 0; i < bidders.size(); i++) {
            BidderEntry entry = bidders.get(i);
            BidderThread bt = new BidderThread(
                entry.name, auctionId, entry.amount, auctionManager
            );
            bidderThreads.add(bt);

            // Wrap in a Thread with a meaningful name for logging
            Thread t = new Thread(bt, "Bidder-" + (i + 1));
            threads.add(t);
        }

        // Step 2: Start ALL threads (concurrent execution begins)
        // Using Thread.start() — NOT Thread.run()
        // start() creates a new OS-level thread; run() would execute sequentially
        for (Thread t : threads) {
            t.start();
        }

        // Step 3: Wait for ALL threads to finish using Thread.join()
        // join() blocks the calling thread until the target thread completes
        for (Thread t : threads) {
            try {
                t.join();
            } catch (InterruptedException e) {
                System.err.println("Thread interrupted: " + t.getName());
            }
        }

        // Step 4: Collect results
        System.out.println("\n-----------------------------------------");
        System.out.println(" SIMULATION RESULTS");
        System.out.println("-----------------------------------------");

        List<SimulationResult> results = new ArrayList<>();
        int accepted = 0;
        int rejected = 0;

        for (BidderThread bt : bidderThreads) {
            AuctionManager.BidResult res = bt.getResult();
            String status = (res != null && res.success) ? "ACCEPTED" : "REJECTED";
            String message = (res != null) ? res.message : "No result";

            if ("ACCEPTED".equals(status)) accepted++;
            else rejected++;

            results.add(new SimulationResult(
                bt.getBidderName(), bt.getBidAmount(), status, message
            ));

            System.out.printf(" %-12s  \u20B9%-10.0f  %s%n",
                bt.getBidderName(), bt.getBidAmount(), status);
        }

        // Final state
        Auction auction = auctionManager.getAuction(auctionId);
        double finalHighest = (auction != null) ? auction.getCurrentHighestBid() : 0;

        System.out.println("-----------------------------------------");
        System.out.println(" Final Highest Bid: \u20B9" + finalHighest);
        System.out.println(" Accepted: " + accepted + " | Rejected: " + rejected);
        System.out.println("=========================================\n");

        return results;
    }

    /**
     * Input data for one bidder in the simulation.
     */
    public static class BidderEntry {
        public String name;
        public double amount;

        public BidderEntry(String name, double amount) {
            this.name = name;
            this.amount = amount;
        }
    }

    /**
     * Result for one bidder after the simulation.
     */
    public static class SimulationResult {
        public String bidder;
        public double amount;
        public String status;
        public String message;

        public SimulationResult(String bidder, double amount, String status, String message) {
            this.bidder = bidder;
            this.amount = amount;
            this.status = status;
            this.message = message;
        }
    }
}
