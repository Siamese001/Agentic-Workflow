/**
 * Meta-Learning Controller
 * Phase 4.1: Dashboard Polling Controller
 * 
 * Polls API endpoints and updates all UI components in real-time.
 * Integrates: MetaLearning, Redis, Pinecone, and Execution Timeline panels.
 */

const MetaLearningController = {
    pollingInterval: null,
    isPolling: false,
    intervalMs: 2000,  // 2 second polling interval
    
    // Component instances
    components: {
        experienceStream: null,
        strategyWeights: null,
        patternTimeline: null,
        metaStats: null,
        redisMonitor: null,
        redisLog: null,
        pineconeMonitor: null,
        pineconeQueries: null,
        executionTimeline: null,
        executionSummary: null,
        layerFlow: null
    },
    
    // Tracking for incremental updates
    lastState: {
        experienceCount: 0,
        redisOpCount: 0,
        pineconeOpCount: 0,
        timelineCount: 0
    },
    
    /**
     * Initialize the controller and all components
     */
    init: function(intervalMs = 2000) {
        console.log('[MetaLearningController] Initializing...');
        this.intervalMs = intervalMs;
        
        // Initialize components if their containers exist
        this.initializeComponents();
        
        // Start polling
        this.startPolling();
        
        console.log('[MetaLearningController] Initialized with', Object.keys(this.components).filter(k => this.components[k]).length, 'components');
    },
    
    /**
     * Initialize all UI components
     */
    initializeComponents: function() {
        // Meta-Learning components
        if (document.getElementById('experience-stream')) {
            this.components.experienceStream = new ExperienceStream('experience-stream');
        }
        if (document.getElementById('strategy-weights')) {
            this.components.strategyWeights = new StrategyWeightsChart('strategy-weights');
        }
        if (document.getElementById('pattern-timeline')) {
            this.components.patternTimeline = new PatternTimeline('pattern-timeline');
        }
        if (document.getElementById('meta-stats')) {
            this.components.metaStats = new MetaLearningStatsPanel('meta-stats');
        }
        
        // Redis components
        if (document.getElementById('redis-stats')) {
            this.components.redisMonitor = new RedisOperationCounter('redis-stats');
        }
        if (document.getElementById('redis-log')) {
            this.components.redisLog = new RedisOperationLog('redis-log');
        }
        
        // Pinecone components
        if (document.getElementById('pinecone-stats')) {
            this.components.pineconeMonitor = new PineconeOperationsDashboard('pinecone-stats');
        }
        if (document.getElementById('pinecone-queries')) {
            this.components.pineconeQueries = new QueryResultsVisualizer('pinecone-queries');
        }
        
        // Execution components
        if (document.getElementById('execution-timeline')) {
            this.components.executionTimeline = new AgentExecutionTimeline('execution-timeline');
        }
        if (document.getElementById('execution-summary')) {
            this.components.executionSummary = new ExecutionSummaryPanel('execution-summary');
        }
        if (document.getElementById('layer-flow')) {
            this.components.layerFlow = new LayerFlowDiagram('layer-flow');
        }
    },
    
    /**
     * Start polling the API endpoints
     */
    startPolling: function() {
        if (this.isPolling) return;
        this.isPolling = true;
        
        // Initial update
        this.poll();
        
        // Set up interval
        this.pollingInterval = setInterval(() => this.poll(), this.intervalMs);
        console.log('[MetaLearningController] Polling started at', this.intervalMs, 'ms interval');
    },
    
    /**
     * Stop polling
     */
    stopPolling: function() {
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
            this.pollingInterval = null;
        }
        this.isPolling = false;
        console.log('[MetaLearningController] Polling stopped');
    },
    
    /**
     * Poll all API endpoints and update components
     */
    poll: async function() {
        try {
            // Fetch all data in parallel
            const [metaData, redisData, pineconeData, timelineData, runtimeState] = await Promise.all([
                this.fetchJSON('http://localhost:8081/api/meta-learning/statistics'),
                this.fetchJSON('http://localhost:8081/api/redis/stats'),
                this.fetchJSON('http://localhost:8081/api/pinecone/stats'),
                this.fetchJSON('http://localhost:8081/api/execution/timeline'),
                this.fetchJSON('http://localhost:8081/api/runtime/state')
            ]);
            
            // Update all components
            if (metaData) this.updateMetaLearning(metaData);
            if (redisData) this.updateRedis(redisData);
            if (pineconeData) this.updatePinecone(pineconeData);
            if (timelineData) this.updateTimeline(timelineData);
            if (runtimeState) this.updateRuntimeState(runtimeState);
            
            console.debug('[MetaLearningController] Poll complete');
        } catch (error) {
            console.debug('[MetaLearningController] Poll error:', error.message);
        }
    },
    
    /**
     * Fetch JSON from URL with error handling
     */
    fetchJSON: async function(url) {
        try {
            const response = await fetch(url);
            if (!response.ok) return null;
            return await response.json();
        } catch (e) {
            return null;
        }
    },
    
    /**
     * Update meta-learning components
     */
    updateMetaLearning: function(data) {
        // Update stats panel
        if (this.components.metaStats) {
            this.components.metaStats.update(data);
        }
        
        // Update strategy weights
        if (this.components.strategyWeights && data.strategy_weights) {
            this.components.strategyWeights.update(data.strategy_weights);
        }
        
        // Update experience stream
        if (this.components.experienceStream && data.recent_experiences) {
            this.components.experienceStream.setExperiences(data.recent_experiences);
        }
        
        // Update pattern timeline
        if (this.components.patternTimeline && data.pattern_history) {
            this.components.patternTimeline.setPatterns(data.pattern_history);
        }
        
        // Update legacy elements if they exist
        const expEl = document.getElementById('exp-count');
        const patternEl = document.getElementById('pattern-count');
        if (expEl) expEl.textContent = data.total_experiences || '0';
        if (patternEl) patternEl.textContent = data.patterns_extracted || '0';
    },
    
    /**
     * Update Redis components
     */
    updateRedis: function(data) {
        // Update stats panel
        if (this.components.redisMonitor) {
            this.components.redisMonitor.update(data);
        }
        
        // Update operation log
        if (this.components.redisLog && data.recent_operations) {
            this.components.redisLog.setOperations(data.recent_operations);
        }
    },
    
    /**
     * Update Pinecone components
     */
    updatePinecone: function(data) {
        // Update stats panel
        if (this.components.pineconeMonitor) {
            this.components.pineconeMonitor.update(data);
        }
        
        // Update query results
        if (this.components.pineconeQueries && data.recent_queries) {
            this.components.pineconeQueries.setQueries(data.recent_queries);
        }
    },
    
    /**
     * Update execution timeline components
     */
    updateTimeline: function(data) {
        if (!Array.isArray(data)) return;
        
        // Update timeline visualization
        if (this.components.executionTimeline) {
            this.components.executionTimeline.setTimeline(data);
        }
        
        // Update summary panel
        if (this.components.executionSummary) {
            this.components.executionSummary.update(data);
        }
    },
    
    /**
     * Update runtime state components
     */
    updateRuntimeState: function(data) {
        // Update layer flow diagram
        if (this.components.layerFlow) {
            const completedLayers = (data.completed_agents || [])
                .map(a => a.layer)
                .filter((v, i, a) => a.indexOf(v) === i);
            this.components.layerFlow.update(data.current_layer, completedLayers);
        }
        
        // Update status elements
        const statusEl = document.getElementById('liveStatus');
        if (statusEl) {
            statusEl.textContent = data.status || 'Idle';
            statusEl.className = 'status-' + (data.status || 'idle').toLowerCase();
        }
        
        const agentEl = document.getElementById('liveAgent');
        if (agentEl) agentEl.textContent = data.current_agent || '--';
        
        const layerEl = document.getElementById('liveLayer');
        if (layerEl) layerEl.textContent = data.current_layer || '--';
    }
};

/**
 * Initialize meta-learning dashboard on page load
 */
function initializeMetaLearningDashboard() {
    // Check if we're on the runtime tab or if meta-learning elements exist
    const hasMetaElements = document.getElementById('meta-stats') || 
                           document.getElementById('experience-stream') ||
                           document.getElementById('strategy-weights');
    
    if (hasMetaElements) {
        MetaLearningController.init(2000);
    }
}

// Export globally
window.MetaLearningController = MetaLearningController;
window.initializeMetaLearningDashboard = initializeMetaLearningDashboard;
