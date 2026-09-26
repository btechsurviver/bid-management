// Admin page logic — auction creation
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('create-auction-form');
    form.addEventListener('submit', handleCreateAuction);
    loadAdminAuctionList();
});

async function handleCreateAuction(e) {
    e.preventDefault();

    const messageDiv = document.getElementById('form-message');
    const submitBtn = document.getElementById('submit-btn');

    const title = document.getElementById('item-title').value.trim();
    const description = document.getElementById('item-desc').value.trim();
    const startingPrice = parseFloat(document.getElementById('starting-price').value);
    const minimumIncrement = parseFloat(document.getElementById('min-increment').value);
    const startTime = document.getElementById('start-time').value;
    const endTime = document.getElementById('end-time').value;

    // Validation
    if (!title || !description) {
        showFormMessage(messageDiv, 'Please fill in all fields.', 'error');
        return;
    }
    if (isNaN(startingPrice) || startingPrice <= 0) {
        showFormMessage(messageDiv, 'Starting price must be a positive number.', 'error');
        return;
    }
    if (isNaN(minimumIncrement) || minimumIncrement <= 0) {
        showFormMessage(messageDiv, 'Minimum increment must be a positive number.', 'error');
        return;
    }
    if (!startTime || !endTime) {
        showFormMessage(messageDiv, 'Please set both start and end times.', 'error');
        return;
    }
    if (new Date(endTime) <= new Date(startTime)) {
        showFormMessage(messageDiv, 'End time must be after start time.', 'error');
        return;
    }

    submitBtn.disabled = true;
    submitBtn.textContent = 'Creating...';

    const result = await api.createAuction({
        title: title,
        description: description,
        starting_price: startingPrice,
        minimum_increment: minimumIncrement,
        start_time: startTime,
        end_time: endTime
    });

    if (result.id) {
        showFormMessage(messageDiv, `Auction "${title}" created successfully! (ID: ${result.id})`, 'success');
        document.getElementById('create-auction-form').reset();
        loadAdminAuctionList();
    } else {
        showFormMessage(messageDiv, result.error || 'Failed to create auction.', 'error');
    }

    submitBtn.disabled = false;
    submitBtn.textContent = 'Create Auction';
}

async function loadAdminAuctionList() {
    const container = document.getElementById('admin-auction-list');
    const auctions = await api.getAuctions();

    if (!auctions || auctions.length === 0) {
        container.innerHTML = '<p>No auctions created yet.</p>';
        return;
    }

    let html = '';
    auctions.forEach(auction => {
        html += `
            <div class="admin-auction-row">
                <div class="admin-auction-info">
                    <strong>${auction.title}</strong>
                    <span class="badge ${statusBadgeClass(auction.status)}">${auction.status}</span>
                </div>
                <div class="admin-auction-details">
                    <span>Start: ${formatCurrency(auction.starting_price)}</span>
                    <span>Current: ${auction.current_highest_bid > 0 ? formatCurrency(auction.current_highest_bid) : '—'}</span>
                </div>
                <div class="admin-auction-actions">
                    ${auction.status === 'UPCOMING' ? `<button class="btn btn-sm" onclick="forceStart(${auction.id})">Start Now</button>` : ''}
                    ${auction.status === 'ACTIVE' ? `<button class="btn btn-sm btn-danger" onclick="forceEnd(${auction.id})">End Now</button>` : ''}
                    <a href="auction.html?id=${auction.id}" class="btn btn-sm btn-secondary">View</a>
                </div>
            </div>
        `;
    });
    container.innerHTML = html;
}

async function forceStart(id) {
    if (!confirm('Start this auction now?')) return;
    await api.startAuction(id);
    loadAdminAuctionList();
}

async function forceEnd(id) {
    if (!confirm('End this auction now? This cannot be undone.')) return;
    await api.endAuction(id);
    loadAdminAuctionList();
}

function showFormMessage(container, text, type) {
    container.innerHTML = `<div class="alert alert-${type}">${text}</div>`;
}
