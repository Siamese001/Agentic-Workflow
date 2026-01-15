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
        this.updateMetadata();
        
        if (this.checkDependencies()) {
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
        } else {
            this.handleMissingData();
        }
    },

    checkDependencies: function() {
        // Ensure critical data is loaded
        const hasData = typeof window.dashboardData !== 'undefined';
        const hasAgentData = typeof window.realAgentData !== 'undefined';
        
        if (!hasData) {
            console.error('[Dashboard] dashboardData not loaded!');
        }
        if (!hasAgentData) {
            console.warn('[Dashboard] realAgentData not loaded');
        }
        
        return hasData;
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
            console.log('[Dashboard] KPIs initialized');

        } catch (e) {
            console.error('[Dashboard] Renderer error:', e);
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
        const container = document.querySelector('.container');
        if (container) {
            container.innerHTML = `
                <div class="kpi-box danger" style="margin-top: 50px; text-align: center;">
                    <h3>⚠️ Data Load Error</h3>
                    <p>Could not load dashboard data. Please ensure <code>data/*.js</code> files are present.</p>
                </div>
            `;
        }
    }
};
