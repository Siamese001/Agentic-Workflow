/**
 * Execution Flow Components
 * Phase 3.4: Real-time visualization of agent execution flow
 *
 * Components:
 * - AgentExecutionTimeline: Timeline visualization
 * - LayerFlowDiagram: Layer progression diagram
 */

/**
 * AgentExecutionTimeline - Displays agent execution timeline
 */
class AgentExecutionTimeline {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.timeline = [];
    }

    addExecution(agent, layer, start, end, success) {
        this.timeline.push({
            agent, layer, start, end,
            duration: end - start,
            success
        });
        this.render();
    }

    setTimeline(timeline) {
        this.timeline = timeline;
        this.render();
    }

    render() {
        if (!this.container) return;

        if (this.timeline.length === 0) {
            this.container.innerHTML = '<div class="empty-state">No executions recorded yet</div>';
            return;
        }

        const maxDuration = Math.max(...this.timeline.map(t => t.duration || 0.1));

        const html = `
            <div class="execution-timeline">
                ${this.timeline.map((exec, i) => {
                    const widthPct = Math.max(5, ((exec.duration || 0) / maxDuration) * 100);
                    const statusClass = exec.success ? 'exec-success' : 'exec-failure';

                    return `
                        <div class="timeline-row">
                            <div class="timeline-label">
                                <span class="agent-name">${exec.agent}</span>
                                <span class="layer-badge">${exec.layer}</span>
                            </div>
                            <div class="timeline-bar-container">
                                <div class="timeline-bar ${statusClass}" style="width: ${widthPct}%;">
                                    <span class="duration-label">${(exec.duration || 0).toFixed(2)}s</span>
                                </div>
                            </div>
                            <div class="timeline-status">
                                ${exec.success ? '✅' : '❌'}
                            </div>
                        </div>
                    `;
                }).join('')}
            </div>
        `;

        this.container.innerHTML = html;
    }
}

/**
 * LayerFlowDiagram - Displays layer progression
 */
class LayerFlowDiagram {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.layers = ['L6', 'L5', 'L4', 'L3', 'L2', 'L1', 'L0'];
        this.currentLayer = null;
        this.completedLayers = [];
    }

    update(currentLayer, completedLayers) {
        this.currentLayer = currentLayer;
        this.completedLayers = completedLayers || [];
        this.render();
    }

    render() {
        if (!this.container) return;

        const html = `
            <div class="layer-flow">
                ${this.layers.map(layer => `
                    <div class="layer-node ${this.getLayerClass(layer)}">
                        <div class="layer-name">${layer}</div>
                        <div class="layer-status">${this.getLayerStatus(layer)}</div>
                    </div>
                    ${layer !== 'L0' ? '<div class="layer-arrow">→</div>' : ''}
                `).join('')}
            </div>
        `;

        this.container.innerHTML = html;
    }

    getLayerClass(layer) {
        if (this.completedLayers.includes(layer)) return 'layer-completed';
        if (layer === this.currentLayer) return 'layer-active';
        return 'layer-pending';
    }

    getLayerStatus(layer) {
        if (this.completedLayers.includes(layer)) return '✓';
        if (layer === this.currentLayer) return '●';
        return '○';
    }
}

/**
 * ExecutionSummaryPanel - Summary of execution statistics
 */
class ExecutionSummaryPanel {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
    }

    update(timeline) {
        if (!this.container) return;

        const totalExecutions = timeline.length;
        const successCount = timeline.filter(e => e.success).length;
        const failureCount = totalExecutions - successCount;
        const totalDuration = timeline.reduce((sum, e) => sum + (e.duration || 0), 0);
        const avgDuration = totalExecutions > 0 ? totalDuration / totalExecutions : 0;

        const html = `
            <div class="execution-summary-grid">
                <div class="stat-box">
                    <div class="stat-label">Total Executions</div>
                    <div class="stat-value">${totalExecutions}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Successful</div>
                    <div class="stat-value success-count">${successCount}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Failed</div>
                    <div class="stat-value failure-count">${failureCount}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Total Duration</div>
                    <div class="stat-value">${totalDuration.toFixed(2)}s</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Avg Duration</div>
                    <div class="stat-value">${avgDuration.toFixed(2)}s</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Success Rate</div>
                    <div class="stat-value">${totalExecutions > 0 ? ((successCount / totalExecutions) * 100).toFixed(1) : 0}%</div>
                </div>
            </div>
        `;

        this.container.innerHTML = html;
    }
}

// Export globally
window.AgentExecutionTimeline = AgentExecutionTimeline;
window.LayerFlowDiagram = LayerFlowDiagram;
window.ExecutionSummaryPanel = ExecutionSummaryPanel;
