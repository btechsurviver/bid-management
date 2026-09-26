package engine;

/**
 * Auction represents a single auction item with its rules and state.
 * 
 * Each auction has:
 *   - Basic info (title, description)
 *   - Pricing rules (starting price, minimum bid increment)
 *   - Timing (start time, end time)
 *   - A BidPriorityQueue to manage all bids efficiently
 *   - A status that is computed based on the current time
 */
public class Auction {
    private int id;
    private String title;
    private String description;
    private double startingPrice;
    private double minimumIncrement;
    private double currentHighestBid;
    private long startTime;  // epoch millis
    private long endTime;    // epoch millis
    private String status;   // UPCOMING, ACTIVE, ENDED

    // Each auction has its own priority queue of bids
    private BidPriorityQueue bidQueue;

    public Auction(int id, String title, String description, double startingPrice,
                   double minimumIncrement, long startTime, long endTime) {
        this.id = id;
        this.title = title;
        this.description = description;
        this.startingPrice = startingPrice;
        this.minimumIncrement = minimumIncrement;
        this.currentHighestBid = 0;
        this.startTime = startTime;
        this.endTime = endTime;
        this.bidQueue = new BidPriorityQueue();
        updateStatus();
    }

    /**
     * Determine auction status based on the current time.
     * 
     * UPCOMING: Current time is before start time.
     * ACTIVE:   Current time is between start and end time.
     * ENDED:    Current time is after end time.
     */
    public void updateStatus() {
        long now = System.currentTimeMillis();
        if (now < startTime) {
            this.status = "UPCOMING";
        } else if (now >= startTime && now <= endTime) {
            this.status = "ACTIVE";
        } else {
            this.status = "ENDED";
        }
    }

    /**
     * Calculate the minimum amount required for the next valid bid.
     * 
     * If no bids have been placed yet, the minimum bid equals the starting price.
     * Otherwise, it's the current highest bid + the minimum increment.
     * 
     * Example:
     *   Starting price = 10000, increment = 500
     *   No bids yet -> minimum bid = 10000
     *   Highest bid = 12000 -> minimum bid = 12500
     */
    public double getMinimumNextBid() {
        if (currentHighestBid <= 0) {
            return startingPrice;
        }
        return currentHighestBid + minimumIncrement;
    }

    // --- Getters and Setters ---

    public int getId() { return id; }
    public String getTitle() { return title; }
    public String getDescription() { return description; }
    public double getStartingPrice() { return startingPrice; }
    public double getMinimumIncrement() { return minimumIncrement; }
    public double getCurrentHighestBid() { return currentHighestBid; }
    public long getStartTime() { return startTime; }
    public long getEndTime() { return endTime; }
    public String getStatus() { return status; }
    public BidPriorityQueue getBidQueue() { return bidQueue; }

    public void setCurrentHighestBid(double amount) {
        this.currentHighestBid = amount;
    }

    public void setStatus(String status) {
        this.status = status;
    }
}
