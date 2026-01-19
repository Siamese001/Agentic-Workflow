/**
 * Refresh Controller
 * Handles auto-refresh timers and manual reload triggers.
 */

const RefreshController = {
    timer: null,
    timeLeft: 300, // 5 minutes default
    
    init: function(intervalSeconds = 300) {
        this.timeLeft = intervalSeconds;
        this.updateUI();
        
        // Setup interval
        if (this.timer) clearInterval(this.timer);
        this.timer = setInterval(() => {
            this.tick();
        }, 1000);

        // Bind manual refresh button if exists
        const refreshBtn = document.querySelector('.refresh-button');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.manualRefresh());
        }
    },

    tick: function() {
        this.timeLeft--;
        if (this.timeLeft <= 0) {
            this.manualRefresh();
        } else {
            this.updateUI();
        }
    },

    manualRefresh: function() {
        window.location.reload();
    },

    updateUI: function() {
        // Optional: Update a countdown element if one existed
    }
};
