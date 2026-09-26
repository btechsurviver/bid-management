// Home page logic — loads auction listings from the backend
document.addEventListener('DOMContentLoaded', async () => {
    checkSystemStatus();
    loadAuctions();
});

async function checkSystemStatus() {
    const statusBadge = document.getElementById('api-status');
    const health = await api.checkHealth();

    if (health && health.status === 'ok') {
        const javaStatus = health.java_engine === 'connected' ? 'Java Engine Connected' : 'Java Engine Offline';
        statusBadge.textContent = 'Backend Connected | ' + javaStatus;
        statusBadge.className = health.java_engine === 'connected' ? 'badge badge-active' : 'badge badge-upcoming';
    } else {
        statusBadge.textContent = 'Backend Offline';
        statusBadge.className = 'badge badge-ended';
    }
}

async function loadAuctions() {
    const container = document.getElementById('auction-list');
    const auctions = await api.getAuctions();

    if (!auctions || auctions.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <p>No auctions available yet.</p>
                <p>Go to the <a href="admin.html">Admin page</a> to create one.</p>
            </div>
        `;
        return;
    }

    container.innerHTML = '';

    auctions.forEach(auction => {
        const card = document.createElement('div');
        card.className = 'card';

        const currentBid = auction.current_highest_bid > 0
            ? formatCurrency(auction.current_highest_bid)
            : 'No bids yet';
        const minNext = formatCurrency(auction.minimum_next_bid);

        card.innerHTML = `
            <div class="card-header">
                <h3>${auction.title}</h3>
                <span class="badge ${statusBadgeClass(auction.status)}">${auction.status}</span>
            </div>
            <p class="card-desc">${auction.description}</p>
            <div class="card-stats">
                <div class="stat">
                    <span class="stat-label">Current Bid</span>
                    <span class="stat-value">${currentBid}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Min Next Bid</span>
                    <span class="stat-value">${minNext}</span>
                </div>
            </div>
            <div class="card-meta">
                <span>Starts: ${formatDateTime(auction.start_time)}</span>
                <span>Ends: ${formatDateTime(auction.end_time)}</span>
            </div>
            <a href="auction.html?id=${auction.id}" class="btn">View Auction</a>
        `;
        container.appendChild(card);
    });
}
