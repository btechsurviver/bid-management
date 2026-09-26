// Phase 5 Concurrency & Priority Queue Demo Logic
let currentAuctions = [];
let selectedAuction = null;

document.addEventListener('DOMContentLoaded', async () => {
    await loadAuctionsForDemo();

    document.getElementById('auction-select').addEventListener('change', handleAuctionSelect);
    document.getElementById('thread-count').addEventListener('change', generateBidders);
});

async function loadAuctionsForDemo() {
    const select = document.getElementById('auction-select');
    currentAuctions = await api.getAuctions();

    if (!currentAuctions || currentAuctions.length === 0) {
        select.innerHTML = '<option value="">No auctions found. Click "Reset Demo Data" to seed.</option>';
        hideSections();
        return;
    }

    const previousId = selectedAuction ? selectedAuction.id : null;

    select.innerHTML = '<option value="">-- Select an auction --</option>';
    currentAuctions.forEach(a => {
        select.innerHTML += `<option value="${a.id}">${a.title} [${a.status}] — ID #${a.id}</option>`;
    });

    if (previousId) {
        select.value = previousId;
        if (select.value) {
            handleAuctionSelect({ target: { value: previousId } });
        }
    }
}

async function handleAuctionSelect(e) {
    const id = parseInt(e.target.value);
    selectedAuction = currentAuctions.find(a => a.id === id);

    const infoDiv = document.getElementById('auction-info');
    const actionsDiv = document.getElementById('auction-actions');
    const normalSection = document.getElementById('normal-bidding-section');
    const pqSection = document.getElementById('priority-queue-section');
    const concurrencySection = document.getElementById('concurrency-section');
    const runBtn = document.getElementById('run-simulation-btn');

    if (selectedAuction) {
        // Fetch freshest auction detail from backend
        const freshAuction = await api.getAuction(selectedAuction.id);
        if (freshAuction) {
            selectedAuction = freshAuction;
        }

        infoDiv.style.display = 'block';
        actionsDiv.style.display = 'flex';
        normalSection.style.display = 'block';
        pqSection.style.display = 'block';
        concurrencySection.style.display = 'block';

        const statusBadge = `<span class="badge ${statusBadgeClass(selectedAuction.status)}">${selectedAuction.status}</span>`;

        infoDiv.innerHTML = `
            <div class="info-grid">
                <div class="info-item">
                    <span class="info-label">Current Highest Bid</span>
                    <span class="info-value" style="color: var(--accent-color);">${formatCurrency(selectedAuction.current_highest_bid)}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Minimum Next Bid</span>
                    <span class="info-value" style="color: var(--success-color);">${formatCurrency(selectedAuction.minimum_next_bid)}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Status</span>
                    <span class="info-value">${statusBadge}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Starting Price</span>
                    <span class="info-value">${formatCurrency(selectedAuction.starting_price)}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Minimum Increment</span>
                    <span class="info-value">${formatCurrency(selectedAuction.minimum_increment)}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Item Description</span>
                    <span class="info-value" style="font-weight: normal; font-size: 0.85rem;">${selectedAuction.description}</span>
                </div>
            </div>
        `;

        // Pre-fill normal bid input with minimum required next bid
        const bidAmountInput = document.getElementById('demo-bid-amount');
        if (bidAmountInput) {
            bidAmountInput.value = selectedAuction.minimum_next_bid;
            bidAmountInput.step = selectedAuction.minimum_increment;
        }

        // Action buttons visibility depending on status
        const startBtn = document.getElementById('start-btn');
        const endBtn = document.getElementById('end-btn');
        const placeBidBtn = document.getElementById('place-bid-btn');

        if (selectedAuction.status === 'ACTIVE') {
            startBtn.disabled = true;
            endBtn.disabled = false;
            if (placeBidBtn) placeBidBtn.disabled = false;
            runBtn.disabled = false;
        } else if (selectedAuction.status === 'UPCOMING') {
            startBtn.disabled = false;
            endBtn.disabled = false;
            if (placeBidBtn) placeBidBtn.disabled = true;
            runBtn.disabled = true;
        } else { // ENDED
            startBtn.disabled = true;
            endBtn.disabled = true;
            if (placeBidBtn) placeBidBtn.disabled = true;
            runBtn.disabled = true;
        }

        generateBidders();
        await renderPriorityQueue();
    } else {
        hideSections();
    }
}

function hideSections() {
    document.getElementById('auction-info').style.display = 'none';
    document.getElementById('auction-actions').style.display = 'none';
    document.getElementById('normal-bidding-section').style.display = 'none';
    document.getElementById('priority-queue-section').style.display = 'none';
    document.getElementById('concurrency-section').style.display = 'none';
}

async function renderPriorityQueue() {
    if (!selectedAuction) return;

    const container = document.getElementById('priority-queue-container');
    const queueData = await api.getAuctionQueue(selectedAuction.id);

    if (!queueData || !queueData.bids || queueData.bids.length === 0) {
        container.innerHTML = `
            <div class="no-bids">
                No bids in PriorityQueue yet. Place a bid or run the concurrent simulation above!
            </div>
        `;
        return;
    }

    let html = `
        <div style="font-size: 0.8rem; color: var(--text-muted); margin-bottom: 0.5rem;">
            Source: <strong>${queueData.source}</strong> | Total elements in queue: <strong>${queueData.size}</strong>
        </div>
        <div class="pq-display-list">
    `;

    queueData.bids.forEach((bid, idx) => {
        const isTop = (idx === 0);
        html += `
            <div class="pq-item ${isTop ? 'pq-item-highest' : ''}">
                <div class="pq-item-rank">#${idx + 1}</div>
                <div class="pq-item-content">
                    <span class="pq-bidder">${bid.bidderName || bid.bidder_name}</span>
                    <span class="pq-amount">${formatCurrency(bid.amount)}</span>
                    ${isTop ? '<span class="badge badge-active" style="font-size: 0.7rem; margin-left: 0.5rem;">Highest Priority</span>' : ''}
                </div>
            </div>
        `;
    });

    html += '</div>';
    container.innerHTML = html;
}

async function placeNormalBid() {
    if (!selectedAuction) return;

    const bidderName = document.getElementById('demo-bidder-name').value.trim();
    const amount = parseFloat(document.getElementById('demo-bid-amount').value);
    const msgDiv = document.getElementById('normal-bid-message');
    const placeBtn = document.getElementById('place-bid-btn');

    if (!bidderName) {
        msgDiv.innerHTML = `<div class="alert alert-error">Please enter a bidder name.</div>`;
        return;
    }
    if (isNaN(amount) || amount <= 0) {
        msgDiv.innerHTML = `<div class="alert alert-error">Please enter a valid bid amount.</div>`;
        return;
    }

    placeBtn.disabled = true;
    msgDiv.innerHTML = '';

    const result = await api.placeBid(selectedAuction.id, bidderName, amount);

    if (result.success) {
        msgDiv.innerHTML = `<div class="alert alert-success">Bid accepted! New highest bid is ${formatCurrency(result.highestBid)}.</div>`;
    } else {
        msgDiv.innerHTML = `<div class="alert alert-error">Bid rejected. ${result.message}</div>`;
    }

    placeBtn.disabled = false;
    await refreshSelectedAuction();
}

function generateBidders() {
    if (!selectedAuction) return;

    const count = parseInt(document.getElementById('thread-count').value);
    const container = document.getElementById('bidder-inputs');

    let html = '<div class="demo-bidders-grid">';

    const baseAmount = selectedAuction.minimum_next_bid;
    const increment = selectedAuction.minimum_increment;

    for (let i = 1; i <= count; i++) {
        // Create an interesting mix of bids so some succeed and some get rejected
        let plannedBid = baseAmount + (Math.floor((i - 1) / 2) * increment);

        html += `
            <div class="demo-bidder-row">
                <span class="demo-bidder-name">BidderThread-${i}</span>
                <input type="number" id="bidder-amount-${i}" class="form-input demo-amount-input" 
                       value="${plannedBid}" step="${increment}">
            </div>
        `;
    }

    html += '</div>';
    container.innerHTML = html;
}

async function runSimulation() {
    if (!selectedAuction) return;

    const count = parseInt(document.getElementById('thread-count').value);
    const runBtn = document.getElementById('run-simulation-btn');
    const msgDiv = document.getElementById('demo-message');
    const resultsDiv = document.getElementById('demo-results');

    const bidders = [];
    for (let i = 1; i <= count; i++) {
        bidders.push({
            name: `Bidder-${i}`,
            amount: parseFloat(document.getElementById(`bidder-amount-${i}`).value)
        });
    }

    runBtn.disabled = true;
    runBtn.textContent = 'Executing Java Threads...';
    msgDiv.innerHTML = '';
    resultsDiv.style.display = 'none';

    const result = await api.simulateConcurrentBids(selectedAuction.id, bidders);

    if (result.success) {
        displayResults(result);
        await refreshSelectedAuction();
    } else {
        msgDiv.innerHTML = `<div class="alert alert-error">${result.message || 'Simulation failed'}</div>`;
    }

    runBtn.disabled = false;
    runBtn.textContent = 'Run Concurrent Simulation';
}

function displayResults(data) {
    const resultsDiv = document.getElementById('demo-results');
    const listDiv = document.getElementById('results-list');
    const summaryDiv = document.getElementById('results-summary');

    resultsDiv.style.display = 'block';

    let listHtml = '<div class="bid-list">';
    let accepted = 0;
    let rejected = 0;

    data.results.forEach(r => {
        const isAcc = r.status === 'ACCEPTED';
        if (isAcc) accepted++; else rejected++;

        listHtml += `
            <div class="bid-item" style="border-left: 4px solid ${isAcc ? 'var(--success-color)' : 'var(--danger-color)'}; padding-left: 0.75rem;">
                <div class="bid-item-main">
                    <span class="bid-bidder">${r.bidder}</span>
                    <span class="bid-amount">${formatCurrency(r.amount)}</span>
                </div>
                <div style="font-size: 0.85rem; color: ${isAcc ? 'var(--success-color)' : 'var(--danger-color)'}; font-weight: 600;">
                    ${r.status} <span style="color:var(--text-muted); font-weight:normal; font-size: 0.75rem;">(${r.message})</span>
                </div>
            </div>
        `;
    });

    listHtml += '</div>';
    listDiv.innerHTML = listHtml;

    summaryDiv.innerHTML = `
        <div class="info-grid" style="margin-top: 1rem;">
            <div class="info-item">
                <span class="info-label">Final Highest Bid</span>
                <span class="info-value" style="color:var(--accent-color);">${formatCurrency(data.highestBid)}</span>
            </div>
            <div class="info-item">
                <span class="info-label">Accepted Bids</span>
                <span class="info-value" style="color:var(--success-color);">${accepted}</span>
            </div>
            <div class="info-item">
                <span class="info-label">Rejected Bids</span>
                <span class="info-value" style="color:var(--danger-color);">${rejected}</span>
            </div>
        </div>
    `;
}

async function startCurrentAuction() {
    if (!selectedAuction) return;
    const res = await api.startAuction(selectedAuction.id);
    if (res.message) {
        alert(`Auction #${selectedAuction.id} activated!`);
        await loadAuctionsForDemo();
    } else {
        alert(res.error || 'Failed to start auction.');
    }
}

async function endCurrentAuction() {
    if (!selectedAuction) return;
    if (!confirm(`Are you sure you want to end auction #${selectedAuction.id}?`)) return;
    const res = await api.endAuction(selectedAuction.id);
    if (res.message) {
        alert(`Auction #${selectedAuction.id} ended.`);
        await loadAuctionsForDemo();
    } else {
        alert(res.error || 'Failed to end auction.');
    }
}

async function seedDemoData() {
    const res = await api.seedDemoData();
    if (res.success) {
        alert('Demo auctions seeded and synced to Java engine!');
        await loadAuctionsForDemo();
    } else {
        alert('Failed to seed demo data: ' + res.message);
    }
}

async function refreshSelectedAuction() {
    if (!selectedAuction) return;
    await loadAuctionsForDemo();
    const select = document.getElementById('auction-select');
    select.value = selectedAuction.id;
    await handleAuctionSelect({ target: { value: selectedAuction.id } });
}
