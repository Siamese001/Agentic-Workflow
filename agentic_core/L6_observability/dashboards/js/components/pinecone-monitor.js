/**
 * Pinecone Monitor Components
 * Phase 3.3: Real-time visualization of Pinecone vector operations
 * 
 * Components:
 * - PineconeOperationsDashboard: Statistics dashboard
 * - QueryResultsVisualizer: Recent query results display
 */

/**
 * PineconeOperationsDashboard - Displays Pinecone operation statistics
 */
class PineconeOperationsDashboard {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
    }
    
    update(stats) {
        if (!this.container) return;
        
        const operations = stats.operations || {};
        const avgSimilarity = ((stats.avg_similarity || 0) * 100).toFixed(1);
        
        const html = `
            <div class="pinecone-stats-grid">
                <div class="stat-box">
                    <div class="stat-label">Vectors Stored</div>
                    <div class="stat-value">${stats.vectors_stored || 0}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Upsert Operations</div>
                    <div class="stat-value">${operations.upsert || 0}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Query Operations</div>
                    <div class="stat-value">${operations.query || 0}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Delete Operations</div>
                    <div class="stat-value">${operations.delete || 0}</div>
                </div>
                <div class="stat-box wide">
                    <div class="stat-label">Avg Similarity Score</div>
                    <div class="stat-value ${this.getSimilarityClass(avgSimilarity)}">${avgSimilarity}%</div>
                    <div class="similarity-bar">
                        <div class="similarity-fill" style="width: ${avgSimilarity}%;"></div>
                    </div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Total Operations</div>
                    <div class="stat-value">${operations.total || 0}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Connection</div>
                    <div class="stat-value ${stats.connected ? 'connected' : 'disconnected'}">
                        ${stats.connected ? '✓ Connected' : '✗ Disconnected'}
                    </div>
                </div>
            </div>
        `;
        
        this.container.innerHTML = html;
    }
    
    getSimilarityClass(similarity) {
        if (similarity > 80) return 'similarity-excellent';
        if (similarity > 60) return 'similarity-good';
        if (similarity > 40) return 'similarity-fair';
        return 'similarity-poor';
    }
}

/**
 * QueryResultsVisualizer - Displays recent Pinecone query results
 */
class QueryResultsVisualizer {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.queries = [];
        this.maxDisplay = 10;
    }
    
    setQueries(queries) {
        this.queries = queries.slice(0, this.maxDisplay);
        this.render();
    }
    
    addQuery(query) {
        this.queries.unshift(query);
        if (this.queries.length > this.maxDisplay) {
            this.queries.pop();
        }
        this.render();
    }
    
    render() {
        if (!this.container) return;
        
        if (this.queries.length === 0) {
            this.container.innerHTML = '<div class="empty-state">No queries recorded yet</div>';
            return;
        }
        
        const html = `
            <div class="query-results">
                ${this.queries.map(q => `
                    <div class="query-item">
                        <div class="query-header">
                            <span class="query-topk">Top-${q.top_k || 10}</span>
                            <span class="query-results-count">${q.results_count || 0} results</span>
                            <span class="query-score">Avg: ${((q.avg_score || 0) * 100).toFixed(1)}%</span>
                            <span class="query-time">${this.formatTime(q.timestamp)}</span>
                        </div>
                        ${this.renderResults(q.results)}
                    </div>
                `).join('')}
            </div>
        `;
        
        this.container.innerHTML = html;
    }
    
    renderResults(results) {
        if (!results || results.length === 0) {
            return '<div class="no-results">No results</div>';
        }
        
        return `
            <div class="query-results-list">
                ${results.slice(0, 5).map((r, i) => `
                    <div class="result-item">
                        <span class="result-rank">#${i + 1}</span>
                        <span class="result-id">${r.id || 'N/A'}</span>
                        <span class="result-score">${((r.score || 0) * 100).toFixed(1)}%</span>
                    </div>
                `).join('')}
            </div>
        `;
    }
    
    formatTime(timestamp) {
        if (!timestamp) return '';
        const date = new Date(timestamp);
        return date.toLocaleTimeString();
    }
}

// Export globally
window.PineconeOperationsDashboard = PineconeOperationsDashboard;
window.QueryResultsVisualizer = QueryResultsVisualizer;
