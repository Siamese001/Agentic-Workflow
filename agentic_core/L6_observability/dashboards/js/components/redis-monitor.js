/**
 * Redis Monitor Components
 * Phase 3.2: Real-time visualization of Redis cache operations
 * 
 * Components:
 * - RedisOperationCounter: Statistics dashboard
 * - RedisOperationLog: Recent operations log
 */

/**
 * RedisOperationCounter - Displays Redis operation statistics
 */
class RedisOperationCounter {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
    }
    
    update(stats) {
        if (!this.container) return;
        
        const hitRate = ((stats.hit_rate || 0) * 100).toFixed(1);
        const operations = stats.operations || {};
        
        const html = `
            <div class="redis-stats-grid">
                <div class="stat-box">
                    <div class="stat-label">GET Operations</div>
                    <div class="stat-value">${operations.get || 0}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">SET Operations</div>
                    <div class="stat-value">${operations.set || 0}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">DELETE Operations</div>
                    <div class="stat-value">${operations.delete || 0}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Total Operations</div>
                    <div class="stat-value">${operations.total || 0}</div>
                </div>
                <div class="stat-box wide">
                    <div class="stat-label">Cache Hit Rate</div>
                    <div class="stat-value ${this.getHitRateClass(hitRate)}">${hitRate}%</div>
                    <div class="hit-rate-bar">
                        <div class="hit-rate-fill" style="width: ${hitRate}%;"></div>
                    </div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Cache Hits</div>
                    <div class="stat-value hit-count">${stats.cache_hits || 0}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Cache Misses</div>
                    <div class="stat-value miss-count">${stats.cache_misses || 0}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Connection</div>
                    <div class="stat-value ${stats.connected ? 'connected' : 'disconnected'}">
                        ${stats.connected ? '✓ Connected' : '✗ Fallback'}
                    </div>
                </div>
            </div>
        `;
        
        this.container.innerHTML = html;
    }
    
    getHitRateClass(rate) {
        if (rate > 80) return 'hit-rate-excellent';
        if (rate > 60) return 'hit-rate-good';
        if (rate > 40) return 'hit-rate-fair';
        return 'hit-rate-poor';
    }
}

/**
 * RedisOperationLog - Displays recent Redis operations
 */
class RedisOperationLog {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.operations = [];
        this.maxDisplay = 20;
    }
    
    addOperation(op) {
        this.operations.unshift(op);
        if (this.operations.length > this.maxDisplay) {
            this.operations.pop();
        }
        this.render();
    }
    
    setOperations(operations) {
        this.operations = operations.slice(0, this.maxDisplay);
        this.render();
    }
    
    render() {
        if (!this.container) return;
        
        if (this.operations.length === 0) {
            this.container.innerHTML = '<div class="empty-state">No operations recorded yet</div>';
            return;
        }
        
        const html = `
            <div class="operation-log">
                ${this.operations.map(op => `
                    <div class="log-entry ${this.getHitClass(op.hit)}">
                        <span class="op-type op-${op.operation}">${op.operation.toUpperCase()}</span>
                        <span class="op-key" title="${op.key}">${this.truncateKey(op.key)}</span>
                        <span class="op-result">${this.getResultIcon(op)}</span>
                        <span class="op-time">${this.formatTime(op.timestamp)}</span>
                    </div>
                `).join('')}
            </div>
        `;
        
        this.container.innerHTML = html;
    }
    
    getHitClass(hit) {
        if (hit === true) return 'cache-hit';
        if (hit === false) return 'cache-miss';
        return '';
    }
    
    getResultIcon(op) {
        if (op.hit === true) return '✓ HIT';
        if (op.hit === false) return '✗ MISS';
        if (op.operation === 'set') return '✓ SET';
        if (op.operation === 'delete') return '✓ DEL';
        return '';
    }
    
    truncateKey(key) {
        if (!key) return '';
        return key.length > 30 ? key.substring(0, 27) + '...' : key;
    }
    
    formatTime(timestamp) {
        if (!timestamp) return '';
        const date = new Date(timestamp);
        return date.toLocaleTimeString();
    }
}

// Export globally
window.RedisOperationCounter = RedisOperationCounter;
window.RedisOperationLog = RedisOperationLog;
