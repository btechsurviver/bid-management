// Auction details page logic
let currentAuctionId = null;

document.addEventListener('DOMContentLoaded', async () => {
    const urlParams = new URLSearchParams(window.location.search);
    currentAuctionId = urlParams.get('id');

    if (currentAuctionId) {
        await loadAuctionDetails(currentAuctionId);
        await loadBidHistory(currentAuctionId);
    } else {
        document.getElementById('auction-details-container').innerHTML =
            '<p>No auction ID provided. <a href="index.html">Go back to listings.</a></p>';
    }
});

async function loadAuctionDetails(id) {
    const container = document.getElementById('auction-details-container');
    const auction = await api.getAuction(id);

    if (!auction) {
        container.innerHTML = '<p>Auction not found. <a href="index.html">Go back to listings.</a></p>';
        return;
    }

    const currentBid = auction.current_highest_bid > 0
        ? formatCurrency(auction.current_highest_bid)
        : 'No bids yet';
    const minNext = formatCurrency(auction.minimum_next_bid);
    const isActive = auction.status === 'ACTIVE';

    container.innerHTML = `
        <div class="details-header">
            <div>
                <h2 style="border:none; padding:0; margin-bottom:0.5rem;">${auction.title}</h2>
                <span class="badge ${statusBadgeClass(auction.status)}">${auction.status}</span>
            </div>
        </div>

        <p class="auction-description">${auction.description}</p>

        <div class="info-grid">
            <div class="info-item">
                <span class="info-label">Starting Price</span>
                <span class="info-value">${formatCurrency(auction.starting_price)}</span>
            </div>
            <div class="info-item">
                <span class="info-label">Current Highest Bid</span>
                <span class="info-value" id="display-current-bid">${currentBid}</span>
            </div>
            <div class="info-item">
                <span class="info-label">Minimum Next Bid</span>
                <span class="info-value" id="display-min-bid">${minNext}</span>
            </div>
            <div class="info-item">
                <span class="info-label">Minimum Increment</span>
                <span class="info-value">${formatCurrency(auction.minimum_increment)}</span>
            </div>
            <div class="info-item">
                <span class="info-label">Starts</span>
                <span class="info-value">${formatDateTime(auction.start_time)}</span>
            </div>
            <div class="info-item">
                <span class="info-label">Ends</span>
                <span class="info-value">${formatDateTime(auction.end_time)}</span>
            </div>
        </div>

        ${isActive ? `
        <div class="bidding-section">
            <h3>Place Your Bid</h3>
            <div id="bid-message"></div>
            <div class="bid-form">
                <input type="text" class="form-input" id="bidder-name" placeholder="Your name" required>
                <input type="number" class="form-input" id="bid-amount"
                       min="${auction.minimum_next_bid}" step="1"
                       value="${Math.ceil(auction.minimum_next_bid)}" placeholder="Bid amount (₹)">
                <button class="btn" id="bid-btn" onclick="submitBid()">Place Bid</button>
            </div>
            <p class="bid-hint">Minimum bid: ${minNext}</p>
        </div>
        ` : `
        <div class="bidding-section bidding-disabled">
            <h3>Bidding ${auction.status === 'UPCOMING' ? 'Not Yet Open' : 'Closed'}</h3>
            <p>${auction.status === 'UPCOMING'
                ? 'This auction has not started yet. Bidding will open at ' + formatDateTime(auction.start_time) + '.'
                : 'This auction has ended. No more bids are accepted.'}</p>
        </div>
        `}

        <div class="bid-history-section">
            <h3>Bid History</h3>
            <div id="bid-history">
                <p>Loading bid history...</p>
            </div>
        </div>
    `;
}

async function loadBidHistory(auctionId) {
    const container = document.getElementById('bid-history');
    const bids = await api.getBids(auctionId);

    if (!bids || bids.length === 0) {
        container.innerHTML = '<p class="no-bids">No bids have been placed yet.</p>';
        return;
    }

    // Build a responsive list instead of a table (works on mobile)
    let html = '<div class="bid-list">';
    bids.forEach((bid, index) => {
        html += `
            <div class="bid-item ${index === 0 ? 'bid-highest' : ''}">
                <div class="bid-item-main">
                    <span class="bid-bidder">${bid.bidder_name}</span>
                    <span class="bid-amount">${formatCurrency(bid.amount)}</span>
                </div>
                <span class="bid-time">${formatDateTime(bid.created_at)}</span>
                ${index === 0 ? '<span class="badge badge-active" style="font-size:0.75rem;">Highest</span>' : ''}
            </div>
        `;
    });
    html += '</div>';
    container.innerHTML = html;
}

async function submitBid() {
    const bidBtn = document.getElementById('bid-btn');
    const messageDiv = document.getElementById('bid-message');
    const bidderName = document.getElementById('bidder-name').value.trim();
    const bidAmount = parseFloat(document.getElementById('bid-amount').value);

    // Client-side validation
    if (!bidderName) {
        showMessage(messageDiv, 'Please enter your name.', 'error');
        return;
    }
    if (isNaN(bidAmount) || bidAmount <= 0) {
        showMessage(messageDiv, 'Please enter a valid bid amount.', 'error');
        return;
    }

    // Disable button to prevent double-click
    bidBtn.disabled = true;
    bidBtn.textContent = 'Placing bid...';

    const result = await api.placeBid(currentAuctionId, bidderName, bidAmount);

    if (result.success) {
        // Bug Fix #7: Show the message BEFORE reloading the details panel
        // so the user actually sees the success confirmation
        showMessage(messageDiv, 'Bid accepted! You are now the highest bidder.', 'success');
        // Wait 1.5 seconds so the user sees the message, then refresh data
        await new Promise(resolve => setTimeout(resolve, 1500));
        // Reload the full auction block (this replaces the container content)
        await loadAuctionDetails(currentAuctionId);
        await loadBidHistory(currentAuctionId);
    } else {
        showMessage(messageDiv, result.message || 'Bid was rejected.', 'error');
        bidBtn.disabled = false;
        bidBtn.textContent = 'Place Bid';
    }
}

function showMessage(container, text, type) {
    if (!container) return;
    container.innerHTML = `<div class="alert alert-${type}">${text}</div>`;
    // Auto-clear error messages after 6 seconds; success messages are cleared by page reload
    if (type !== 'success') {
        setTimeout(() => {
            if (container && container.parentNode) {
                container.innerHTML = '';
            }
        }, 6000);
    }
}

