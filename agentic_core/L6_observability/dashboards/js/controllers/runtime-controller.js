/**
 * Runtime Controller
 * Handles live polling from API endpoints for real-time dashboard updates.
 * Extracted from monolithic dashboard Phase 4.9: Live Tactical Poller
 */

const RuntimeController = {
    pollingInterval: null,
    isPolling: false,

    init: function(intervalMs = 5000) {
        console.log('[RuntimeController] Initializing live polling...');
        this.startPolling(intervalMs);
    },

    startPolling: function(intervalMs) {
        if (this.isPolling) return;
        this.isPolling = true;
        
        // Initial update
        this.updateRuntime();
        
        // Set up interval
        this.pollingInterval = setInterval(() => {
            this.updateRuntime();
        }, intervalMs);
    },

    stopPolling: function() {
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
            this.pollingInterval = null;
        }
        this.isPolling = false;
    },

    updateRuntime: async function() {
        try {
            const [metaResp, latencyResp, logsResp] = await Promise.all([
                fetch('http://localhost:8081/api/meta-learning/activity').catch(() => null),
                fetch('http://localhost:8081/api/metrics/latency').catch(() => null),
                fetch('http://localhost:8081/api/redis/logs?limit=80').catch(() => null)
            ]);

            // Meta-learning activity
            if (metaResp && metaResp.ok) {
                const meta = await metaResp.json();
                const expEl = document.getElementById('exp-count');
                const patternEl = document.getElementById('pattern-count');
                if (expEl) expEl.textContent = meta.total_experiences || '0';
                if (patternEl) patternEl.textContent = meta.patterns_extracted || '0';
            }

            // Latency metrics
            if (latencyResp && latencyResp.ok) {
                const latency = await latencyResp.json();
                const geminiLatencyEl = document.getElementById('geminiLatency');
                const pineconeLatencyEl = document.getElementById('pineconeLatency');
                if (geminiLatencyEl) geminiLatencyEl.textContent = (latency.gemini_embeddings ?? '--') + 'ms';
                if (pineconeLatencyEl) pineconeLatencyEl.textContent = (latency.pinecone ?? '--') + 'ms';
            }

            // Live logs
            if (logsResp && logsResp.ok) {
                const logs = await logsResp.json();
                const liveLogEl = document.getElementById('liveLog');
                if (liveLogEl && logs && Array.isArray(logs.logs)) {
                    liveLogEl.textContent = logs.logs.join('\n');
                    liveLogEl.scrollTop = liveLogEl.scrollHeight;
                }
            }

            console.log('[RuntimeController] Dashboard updated from Live API');
        } catch (e) {
            // Silent fail - API may not be running
            console.debug('[RuntimeController] Live polling skipped - API unavailable');
        }
    },

    // Update live execution state from runtime_state.json
    updateLiveExecutionState: async function() {
        try {
            const resp = await fetch('runtime_state.json?' + Date.now());
            if (!resp.ok) return;
            
            const state = await resp.json();
            
            // Update status
            const statusEl = document.getElementById('liveStatus');
            if (statusEl) {
                statusEl.textContent = state.status || 'Idle';
                statusEl.style.color = state.status === 'Running' ? '#16a34a' : '#6b7280';
            }
            
            // Update current agent
            const agentEl = document.getElementById('liveAgent');
            const layerEl = document.getElementById('liveLayer');
            if (agentEl) agentEl.textContent = state.current_agent || '--';
            if (layerEl) layerEl.textContent = state.current_layer || '--';
            
            // Update progress bar
            const progressBar = document.getElementById('progressBar');
            if (progressBar && state.progress !== undefined) {
                const pct = Math.min(100, Math.max(0, state.progress));
                progressBar.style.width = pct + '%';
                progressBar.textContent = pct.toFixed(0) + '%';
            }
            
            // Update meta-learning status
            const metaEl = document.getElementById('liveMeta');
            if (metaEl) {
                metaEl.textContent = state.meta_learning_active ? 'Active' : 'Inactive';
                metaEl.style.color = state.meta_learning_active ? '#16a34a' : '#6b7280';
            }
            
            // Update execution sequence table
            if (state.execution_order && Array.isArray(state.execution_order)) {
                this.renderExecutionSequence(state.execution_order, state.current_index || 0);
            }
        } catch (e) {
            // Silent fail - file may not exist
        }
    },

    renderExecutionSequence: function(order, currentIndex) {
        const tbody = document.getElementById('orderTableBody');
        if (!tbody) return;
        
        tbody.innerHTML = order.map((item, idx) => {
            let status = '⏳';
            let bgColor = '';
            if (idx < currentIndex) {
                status = '✅';
                bgColor = 'background:#f0fdf4;';
            } else if (idx === currentIndex) {
                status = '🔄';
                bgColor = 'background:#fef3c7;';
            }
            
            return `<tr style="${bgColor}">
                <td style="padding:6px 8px;">${idx + 1}</td>
                <td style="padding:6px 8px;">${item.agent || item} → ${item.target || 'self'}</td>
                <td style="padding:6px 8px; text-align:center;">${status}</td>
            </tr>`;
        }).join('');
    }
};

// Initialize semantic metrics display
function initializeSemanticMetrics() {
    const reuseEl = document.getElementById('reuseRate');
    const confEl = document.getElementById('retrievalConfidence');
    
    // Set default values - these would be updated by live polling
    if (reuseEl) {
        reuseEl.innerHTML = '87%<span style="color:#16a34a; font-size:0.6em; margin-left:4px;">↑</span>';
    }
    if (confEl) {
        confEl.textContent = '0.94';
    }
}

// Initialize runtime monitoring
function initializeRuntimeMonitoring() {
    // Only start polling if on runtime tab or if elements exist
    const runtimeContent = document.getElementById('runtime-content');
    if (runtimeContent) {
        RuntimeController.init(5000);
    }
}

// Export globally
window.RuntimeController = RuntimeController;
window.initializeSemanticMetrics = initializeSemanticMetrics;
window.initializeRuntimeMonitoring = initializeRuntimeMonitoring;
