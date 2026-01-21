/**
 * Main Orchestrator
 * Entry point for the Autonomy Dashboard.
 * Handles initialization, dependency checking, and global error management.
 */

document.addEventListener('DOMContentLoaded', () => {
    DashboardApp.init();
});

const DashboardApp = {
    init: function() {
        console.log('[Dashboard] Initializing...');
        this.setupGlobalErrors();

        // Hardened: Retry mechanism for slow-loading local data files
        let retryCount = 0;
        const tryLoad = () => {
            if (this.checkDependencies()) {
                this.updateMetadata();
                this.renderContent();
                this.initRenderers();
                this.initControllers();

                // Add modal close handlers
                document.addEventListener('keydown', function(e) {
                    if (e.key === 'Escape') {
                        const modal = document.getElementById('drillModal');
                        if (modal && modal.style.display === 'flex') {
                            modal.style.display = 'none';
                        }
                    }
                });

                const drillModal = document.getElementById('drillModal');
                if (drillModal) {
                    drillModal.addEventListener('click', function(e) {
                        if (e.target === this) {
                            this.style.display = 'none';
                        }
                    });
                }

                console.log('[Dashboard] Ready.');
            } else if (retryCount < 10) { // Increased retries for slow local I/O
                retryCount++;
                console.warn(`[Dashboard] Awaiting data hydration (Attempt ${retryCount}/10)...`);
                setTimeout(tryLoad, 300); // Increased backoff to 300ms
            } else {
                this.handleMissingData();
            }
        };
        tryLoad();
    },

    checkDependencies: function() {
        // 1. Universal Variable Mapping: Map all known variants to standard pointers
        if (typeof window.globalAgentData !== 'undefined' && typeof window.realAgentData === 'undefined') {
            window.realAgentData = window.globalAgentData;
        }
        if (typeof window.agentData !== 'undefined' && typeof window.realAgentData === 'undefined') {
            window.realAgentData = window.agentData;
        }

        // 2. Map observations and recommendations variable names
        if (typeof window.strategicObservationsData !== 'undefined' && typeof window.observations === 'undefined') {
            window.observations = window.strategicObservationsData;
        }
        if (typeof window.recommendationsData !== 'undefined' && typeof window.recommendations === 'undefined') {
            window.recommendations = window.recommendationsData;
        }

        // 3. Lenient Dependency Check: Ensure data exists even if empty initially
        const hasData = typeof window.dashboardData !== 'undefined' && Array.isArray(window.dashboardData);
        const hasAgentData = typeof window.realAgentData !== 'undefined';

        // 4. Debug logging to identify which specific variable is missing
        if (!hasData) console.warn('[Dashboard] Missing: dashboardData');
        if (!hasAgentData) console.warn('[Dashboard] Missing: realAgentData');

        if (hasData && hasAgentData) {
            console.log(`[Dashboard] Data loaded: ${window.dashboardData.length} territories`);
            return true;
        }

        return false;
    },

    updateMetadata: function() {
        // Update timestamp
        const ts = document.getElementById('lastUpdated');
        if (ts) ts.textContent = `Generated: ${new Date().toLocaleString()}`;
    },

    renderContent: function() {
        console.log('[Dashboard] Rendering content...');

        try {
            // Get territory data
            const territoryData = window.dashboardData.filter(row => row.Territory !== 'TOTAL');
            const totalRow = window.dashboardData.find(row => row.Territory === 'TOTAL');

            // Strategic observations
            if (typeof renderStrategicObservations === 'function') {
                renderStrategicObservations();
                console.log('[Dashboard] Strategic observations rendered');
            }

            // Alert banner
            if (typeof updateGlobalAlertBanner === 'function') {
                updateGlobalAlertBanner(territoryData);
                console.log('[Dashboard] Alert banner updated');
            }

            // Recommendations
            if (typeof renderRecommendations === 'function') {
                renderRecommendations();
                console.log('[Dashboard] Recommendations rendered');
            }

            // Interview questions
            if (typeof renderInterviewQuestions === 'function' && totalRow) {
                renderInterviewQuestions(totalRow);
                console.log('[Dashboard] Interview questions rendered');
            }
        } catch (e) {
            console.error('[Dashboard] Content render error:', e);
        }
    },

    initRenderers: function() {
        console.log('[Dashboard] Initializing renderers...');

        try {
            // Table 1: Territory Summary
            if (typeof renderTerritorySummaryTable === 'function') {
                renderTerritorySummaryTable(window.dashboardData);
                console.log('[Dashboard] Territory summary table rendered');
            }

            // Table 2: Code Quality
            if (typeof renderCodeQualityTable === 'function') {
                renderCodeQualityTable(window.dashboardData);
                console.log('[Dashboard] Code quality table rendered');
            }

            // KPI & Metrics
            console.log('[Dashboard] Initializing KPIs...');
            if (typeof initializeSemanticMetrics === 'function') {
                initializeSemanticMetrics();
            }
            if (typeof initializeRuntimeMonitoring === 'function') {
                initializeRuntimeMonitoring();
            }

            // Phase 5: Initialize Meta-Learning Dashboard
            if (typeof initializeMetaLearningDashboard === 'function') {
                initializeMetaLearningDashboard();
                console.log('[Dashboard] Meta-Learning dashboard initialized');
            }

            // Initialize SSE Connection for Live Runtime
            this.setupSSE();

            console.log('[Dashboard] KPIs initialized');

        } catch (e) {
            console.error('[Dashboard] Renderer error:', e);
        }
    },

    setupSSE: function() {
        try {
            const eventSource = new EventSource('/api/runtime/stream');
            eventSource.onmessage = (e) => {
                const msg = JSON.parse(e.data);
                const eventType = msg.type === 'state_update' ? 'runtime-state-update' : 'runtime-event';
                window.dispatchEvent(new CustomEvent(eventType, { detail: msg.type === 'state_update' ? msg.data : msg }));
            };
            eventSource.onerror = () => {
                console.warn('[Dashboard] SSE connection failed (Live Runtime may be offline)');
                eventSource.close();
            };
        } catch (e) {
            console.warn('[Dashboard] SSE setup failed:', e);
        }
    },

    initControllers: function() {
        console.log('[Dashboard] Initializing controllers...');

        try {
            // Tab Controller
            if (typeof TabController !== 'undefined') {
                TabController.init();
            }

            // Refresh Controller
            if (typeof RefreshController !== 'undefined') {
                const interval = window.AppConfig?.refresh?.intervalSeconds || 300;
                RefreshController.init(interval);
            }

            // Export CSV globally for UI buttons
            if (typeof FilterController !== 'undefined') {
                window.exportCSV = FilterController.exportCSV;
            }

            console.log('[Dashboard] Controllers initialized');

            // Setup Plotly chart interactivity
            this.setupPlotlyInteractivity();
        } catch (e) {
            console.error('[Dashboard] Controller error:', e);
        }
    },

    setupPlotlyInteractivity: function() {
        // Add click handlers to Plotly charts for drill-down modals
        ['healthChart', 'riskMatrix'].forEach(chartId => {
            const el = document.getElementById(chartId);
            if (el) {
                el.on('plotly_click', function(data) {
                    if (data.points && data.points[0]) {
                        const territory = data.points[0].x || data.points[0].label || data.points[0].text;
                        if (territory && territory !== 'TOTAL' && typeof openDrillModal === 'function') {
                            openDrillModal(territory);
                        }
                    }
                });
            }
        });
    },

    setupGlobalErrors: function() {
        window.onerror = function(msg, url, line) {
            console.error(`[Global Error] ${msg} @ ${line}`);
        };
    },

    handleMissingData: function() {
        // Hardened: Non-destructive error state (Keep UI structure for late-loading scripts)
        const bannerId = 'data-load-error-banner';
        if (document.getElementById(bannerId)) return;

        const banner = document.createElement('div');
        banner.id = bannerId;
        banner.className = 'kpi-box danger';
        banner.style = 'position: fixed; top: 20px; left: 50%; transform: translateX(-50%); z-index: 9999; width: 80%; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.2);';
        banner.innerHTML = `
            <h3>⚠️ Critical Data Delay</h3>
            <p>The dashboard is waiting for <code>data/*.js</code>. If this persists, check if files are blocked by CORS or missing.</p>
            <button onclick="location.reload()" style="margin-top:10px; padding:5px 15px; cursor:pointer;">Retry Full Reload</button>
        `;
        document.body.appendChild(banner);
    }

};
