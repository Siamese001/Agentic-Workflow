/**
 * Application Configuration
 * Centralizes constants, thresholds, and feature flags.
 */

window.AppConfig = {
    // Feature Flags
    features: {
        enableLiveLogs: true,
        enableAutoRefresh: true,
        enableAnimations: true,
        offlineMode: typeof Plotly === 'undefined' // Detect if Plotly loaded
    },

    // Refresh Settings
    refresh: {
        intervalSeconds: 300, // 5 minutes
        retryDelay: 5000
    },

    // UI Constants
    ui: {
        colors: {
            primary: '#2563eb',
            success: '#16a34a',
            danger: '#dc2626'
        }
    }
};
