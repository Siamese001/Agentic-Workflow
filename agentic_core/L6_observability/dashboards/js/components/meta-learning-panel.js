/**
 * Meta-Learning Panel Components
 * Phase 3.1: Real-time visualization of meta-learning activity
 * 
 * Components:
 * - ExperienceStream: Live feed of experiences
 * - StrategyWeightsChart: Bar chart of strategy weights
 * - PatternTimeline: Timeline of pattern extractions
 */

/**
 * ExperienceStream - Displays live feed of meta-learning experiences
 */
class ExperienceStream {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.experiences = [];
        this.maxDisplay = 50;
    }
    
    addExperience(exp) {
        this.experiences.unshift(exp);
        if (this.experiences.length > this.maxDisplay) {
            this.experiences.pop();
        }
        this.render();
    }
    
    setExperiences(experiences) {
        this.experiences = experiences.slice(0, this.maxDisplay);
        this.render();
    }
    
    render() {
        if (!this.container) return;
        
        if (this.experiences.length === 0) {
            this.container.innerHTML = '<div class="empty-state">No experiences recorded yet</div>';
            return;
        }
        
        const html = this.experiences.map(exp => `
            <div class="experience-item ${this.getRewardClass(exp.reward)}">
                <span class="exp-type">${this.formatThoughtType(exp.thought_type)}</span>
                <span class="exp-reward">Reward: ${(exp.reward || 0).toFixed(2)}</span>
                <span class="exp-time">${this.formatTime(exp.timestamp)}</span>
            </div>
        `).join('');
        
        this.container.innerHTML = html;
    }
    
    getRewardClass(reward) {
        if (reward > 0.7) return 'reward-high';
        if (reward > 0.3) return 'reward-medium';
        return 'reward-low';
    }
    
    formatThoughtType(type) {
        const icons = {
            'cot': '🔗 CoT',
            'tot': '🌳 ToT',
            'react': '⚡ ReAct',
            'reflection': '🔄 Reflection'
        };
        return icons[type] || type;
    }
    
    formatTime(timestamp) {
        if (!timestamp) return '';
        const date = new Date(timestamp);
        return date.toLocaleTimeString();
    }
}

/**
 * StrategyWeightsChart - Bar chart visualization of strategy weights
 */
class StrategyWeightsChart {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.weights = { cot: 1.0, tot: 1.0, react: 1.0, reflection: 1.0 };
    }
    
    update(weights) {
        this.weights = weights;
        this.render();
    }
    
    render() {
        if (!this.container) return;
        
        const strategies = [
            { key: 'cot', label: 'Chain of Thought', color: '#3b82f6', icon: '🔗' },
            { key: 'tot', label: 'Tree of Thought', color: '#10b981', icon: '🌳' },
            { key: 'react', label: 'ReAct', color: '#f59e0b', icon: '⚡' },
            { key: 'reflection', label: 'Reflection', color: '#8b5cf6', icon: '🔄' }
        ];
        
        const maxWeight = Math.max(2.0, ...Object.values(this.weights));
        
        const html = `
            <div class="strategy-weights-chart">
                ${strategies.map(s => {
                    const weight = this.weights[s.key] || 1.0;
                    const widthPct = (weight / maxWeight) * 100;
                    return `
                        <div class="strategy-bar-row">
                            <div class="strategy-label">${s.icon} ${s.label}</div>
                            <div class="strategy-bar-container">
                                <div class="strategy-bar" style="width: ${widthPct}%; background: ${s.color};">
                                    <span class="strategy-value">${weight.toFixed(2)}</span>
                                </div>
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
 * PatternTimeline - Timeline of pattern extraction events
 */
class PatternTimeline {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.patterns = [];
    }
    
    addPattern(pattern) {
        this.patterns.push(pattern);
        this.render();
    }
    
    setPatterns(patterns) {
        this.patterns = patterns;
        this.render();
    }
    
    render() {
        if (!this.container) return;
        
        if (this.patterns.length === 0) {
            this.container.innerHTML = '<div class="empty-state">No patterns extracted yet</div>';
            return;
        }
        
        const html = `
            <div class="pattern-timeline">
                ${this.patterns.map((p, i) => `
                    <div class="timeline-item">
                        <div class="timeline-marker">${i + 1}</div>
                        <div class="timeline-content">
                            <strong>${p.pattern?.type || p.type || 'Pattern'}</strong>
                            <span class="pattern-threshold">Threshold: ${p.pattern?.threshold || p.threshold || 'N/A'}</span>
                            <span class="pattern-time">${this.formatTime(p.timestamp)}</span>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
        
        this.container.innerHTML = html;
    }
    
    formatTime(timestamp) {
        if (!timestamp) return '';
        const date = new Date(timestamp);
        return date.toLocaleTimeString();
    }
}

/**
 * MetaLearningStatsPanel - Summary statistics for meta-learning
 */
class MetaLearningStatsPanel {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
    }
    
    update(stats) {
        if (!this.container) return;
        
        const html = `
            <div class="meta-stats-grid">
                <div class="stat-box">
                    <div class="stat-label">Total Experiences</div>
                    <div class="stat-value">${stats.total_experiences || 0}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Buffer Size</div>
                    <div class="stat-value">${stats.buffer_size || 0} / ${stats.buffer_capacity || 1000}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Patterns Extracted</div>
                    <div class="stat-value">${stats.patterns_extracted || 0}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Status</div>
                    <div class="stat-value status-active">Active</div>
                </div>
            </div>
        `;
        
        this.container.innerHTML = html;
    }
}

// Export globally
window.ExperienceStream = ExperienceStream;
window.StrategyWeightsChart = StrategyWeightsChart;
window.PatternTimeline = PatternTimeline;
window.MetaLearningStatsPanel = MetaLearningStatsPanel;
