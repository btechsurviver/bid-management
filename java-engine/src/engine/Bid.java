package engine;

/**
 * Bid represents a single bid placed by a user on an auction.
 * 
 * This class implements Comparable so that Java's PriorityQueue can
 * automatically order bids. The ordering is:
 *   - Higher amount = higher priority (descending by amount)
 *   - If amounts are equal, earlier timestamp wins (ascending by time)
 * 
 * This means PriorityQueue.peek() always returns the highest bid.
 */
public class Bid implements Comparable<Bid> {
    private int id;
    private int auctionId;
    private String bidderName;
    private double amount;
    private long timestamp; // milliseconds since epoch

    public Bid(int auctionId, String bidderName, double amount) {
        this.auctionId = auctionId;
        this.bidderName = bidderName;
        this.amount = amount;
        this.timestamp = System.currentTimeMillis();
    }

    // Constructor used when loading bids from the database
    public Bid(int id, int auctionId, String bidderName, double amount, long timestamp) {
        this.id = id;
        this.auctionId = auctionId;
        this.bidderName = bidderName;
        this.amount = amount;
        this.timestamp = timestamp;
    }

    // --- Getters ---

    public int getId() { return id; }
    public int getAuctionId() { return auctionId; }
    public String getBidderName() { return bidderName; }
    public double getAmount() { return amount; }
    public long getTimestamp() { return timestamp; }

    public void setId(int id) { this.id = id; }

    /**
     * Comparison for PriorityQueue ordering.
     * 
     * Java's PriorityQueue is a MIN-heap by default, meaning peek() returns
     * the "smallest" element. By reversing the amount comparison (other - this),
     * we make the HIGHEST bid the "smallest" in terms of ordering, so peek()
     * returns the highest bid.
     * 
     * If two bids have the same amount, the one placed earlier (smaller timestamp)
     * gets priority — first come, first served.
     */
    @Override
    public int compareTo(Bid other) {
        if (this.amount != other.amount) {
            return Double.compare(other.amount, this.amount); // Descending by amount
        }
        return Long.compare(this.timestamp, other.timestamp); // Ascending by time (earlier wins)
    }

    @Override
    public String toString() {
        return "Bid{bidder='" + bidderName + "', amount=" + amount + "}";
    }
}
