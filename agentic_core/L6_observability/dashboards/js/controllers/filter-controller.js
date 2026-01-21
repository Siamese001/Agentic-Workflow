/**
 * Filter Controller
 * Manages state for table filters, sorts, and data export.
 */

// Initialize global state object
window.tableFilterState = {
    table1: { showOnlyOutliers: false, sortByOutliers: false, showZombies: false },
    table2: { showOnlyOutliers: false, sortByOutliers: false, showZombies: false }
};

window.toxicityFilterEnabled = false;

const FilterController = {
    toggleFilter: function(tableType, key) {
        if (window.tableFilterState[tableType]) {
            window.tableFilterState[tableType][key] = !window.tableFilterState[tableType][key];

            // Trigger re-render
            if (typeof renderTerritorySummaryTable === 'function' && window.dashboardData) {
                renderTerritorySummaryTable(window.dashboardData);
            }
            if (typeof renderCodeQualityTable === 'function' && window.dashboardData) {
                renderCodeQualityTable(window.dashboardData);
            }
        }
    },

    exportCSV: function() {
        if (!window.dashboardData) return;

        const headers = Object.keys(window.dashboardData[0]);
        const csvRows = [];

        // Add header row
        csvRows.push(headers.join(','));

        // Add data rows
        window.dashboardData.forEach(row => {
            const values = headers.map(header => {
                const escaped = ('' + row[header]).replace(/"/g, '\\"');
                return `"${escaped}"`;
            });
            csvRows.push(values.join(','));
        });

        // Create download
        const blob = new Blob([csvRows.join('\n')], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.setAttribute('hidden', '');
        a.setAttribute('href', url);
        a.setAttribute('download', 'dashboard_export.csv');
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    }
};

// Expose legacy global hook for checkbox onchange="window.toggleFilter(...)"
window.toggleFilter = FilterController.toggleFilter;
