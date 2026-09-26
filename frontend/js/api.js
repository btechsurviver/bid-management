// API communication module
// All frontend-to-backend communication goes through this module.
const API_BASE_URL = 'http://localhost:5000/api';

const api = {
    async checkHealth() {
        try {
            const response = await fetch(`${API_BASE_URL}/health`);
            return await response.json();
        } catch (error) {
            console.error('Backend is unreachable', error);
            return null;
        }
    },

    async getAuctions() {
        try {
            const response = await fetch(`${API_BASE_URL}/auctions`);
            return await response.json();
        } catch (error) {
            console.error('Error fetching auctions', error);
            return [];
        }
    },

    async getAuction(id) {
        try {
            const response = await fetch(`${API_BASE_URL}/auctions/${id}`);
            if (!response.ok) throw new Error('Auction not found');
            return await response.json();
        } catch (error) {
            console.error(`Error fetching auction ${id}`, error);
            return null;
        }
    },

    async createAuction(data) {
        try {
            const response = await fetch(`${API_BASE_URL}/auctions`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            return await response.json();
        } catch (error) {
            console.error('Error creating auction', error);
            return { error: 'Server unreachable' };
        }
    },

    async placeBid(auctionId, bidderName, amount) {
        try {
            const response = await fetch(`${API_BASE_URL}/auctions/${auctionId}/bids`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ bidder_name: bidderName, amount: amount })
            });
            return await response.json();
        } catch (error) {
            console.error('Error placing bid', error);
            return { success: false, message: 'Server unreachable' };
        }
    },

    async getBids(auctionId) {
        try {
            const response = await fetch(`${API_BASE_URL}/auctions/${auctionId}/bids`);
            return await response.json();
        } catch (error) {
            console.error('Error fetching bids', error);
            return [];
        }
    },

    async startAuction(auctionId) {
        try {
            const response = await fetch(`${API_BASE_URL}/auctions/${auctionId}/start`, {
                method: 'POST'
            });
            return await response.json();
        } catch (error) {
            console.error('Error starting auction', error);
            return { error: 'Server unreachable' };
        }
    },

    async endAuction(auctionId) {
        try {
            const response = await fetch(`${API_BASE_URL}/auctions/${auctionId}/end`, {
                method: 'POST'
            });
            return await response.json();
        } catch (error) {
            console.error('Error ending auction', error);
            return { error: 'Server unreachable' };
        }
    },

    async simulateConcurrentBids(auctionId, bidders) {
        try {
            const response = await fetch(`${API_BASE_URL}/auctions/${auctionId}/simulate-concurrent-bids`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ bidders: bidders })
            });
            return await response.json();
        } catch (error) {
            console.error('Error running simulation', error);
            return { success: false, message: 'Server unreachable' };
        }
    },

    async getAuctionQueue(auctionId) {
        try {
            const response = await fetch(`${API_BASE_URL}/auctions/${auctionId}/queue`);
            return await response.json();
        } catch (error) {
            console.error('Error fetching priority queue', error);
            return null;
        }
    },

    async seedDemoData() {
        try {
            const response = await fetch(`${API_BASE_URL}/demo/seed`, {
                method: 'POST'
            });
            return await response.json();
        } catch (error) {
            console.error('Error seeding demo data', error);
            return { success: false, message: 'Server unreachable' };
        }
    }
};

// Utility: format currency in INR
function formatCurrency(amount) {
    return '₹' + Number(amount).toLocaleString('en-IN', { minimumFractionDigits: 0, maximumFractionDigits: 2 });
}

// Utility: format a datetime string for display
function formatDateTime(dtStr) {
    if (!dtStr) return '';
    try {
        const dt = new Date(dtStr);
        if (isNaN(dt.getTime())) return dtStr;
        return dt.toLocaleString('en-IN', {
            day: 'numeric', month: 'short', year: 'numeric',
            hour: 'numeric', minute: '2-digit', hour12: true
        });
    } catch (e) {
        return dtStr;
    }
}

// Utility: get status badge class
function statusBadgeClass(status) {
    switch (status) {
        case 'ACTIVE': return 'badge-active';
        case 'UPCOMING': return 'badge-upcoming';
        case 'ENDED': return 'badge-ended';
        default: return '';
    }
}
