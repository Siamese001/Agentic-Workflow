/**
 * Tab Controller
 * Handles navigation, URL hash updates, and view switching.
 */

// Global openTab function for onclick handlers in HTML
function openTab(evt, tabName) {
    TabController.switchTab(tabName);
    if (evt) evt.preventDefault();
}
window.openTab = openTab;

const TabController = {
    init: function() {
        // Bind click events
        const tabs = document.querySelectorAll('.nav-tab');
        tabs.forEach(tab => {
            tab.addEventListener('click', (e) => {
                e.preventDefault();
                const targetId = tab.getAttribute('data-target') ||
                                 tab.textContent.toLowerCase().replace(' ', '-');
                this.switchTab(targetId);
            });
        });

        // Handle initial load from hash
        const hash = window.location.hash.substring(1); // Remove #
        if (hash) {
            this.switchTab(hash);
        } else {
            // Default to first tab
            const firstTab = document.querySelector('.nav-tab');
            if (firstTab) {
                const targetId = firstTab.getAttribute('data-target') || 'executive';
                this.switchTab(targetId);
            }
        }
    },

    switchTab: function(tabId) {
        // Update URL hash without scrolling
        history.replaceState(null, null, '#' + tabId);

        // Hide all content
        const contents = document.querySelectorAll('.tab-content');
        contents.forEach(content => content.style.display = 'none');

        // Deactivate all tabs
        const tabs = document.querySelectorAll('.nav-tab');
        tabs.forEach(tab => tab.classList.remove('active'));

        // Show target content
        const targetContent = document.getElementById(tabId + '-content');
        if (targetContent) targetContent.style.display = 'block';

        // Activate target tab (try matching data-target or simple string match)
        const activeTab = document.querySelector(`.nav-tab[data-target="${tabId}"]`);
        if (activeTab) activeTab.classList.add('active');
    }
};
