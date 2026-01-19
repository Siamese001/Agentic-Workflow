/**
 * Statistical Analysis Utilities
 */

// SSOT: Constants loaded from dashboard-constants.js via window globals
// Access via: window.THRESHOLDS

function computeDistributionStats(values) {
    // Filter out N/A and non-numbers
    const numbers = values.filter(v => typeof v === 'number' && !isNaN(v));
    
    if (numbers.length === 0) return { min: 0, max: 0, avg: 0, stdDev: 0, count: 0 };
    
    const min = Math.min(...numbers);
    const max = Math.max(...numbers);
    const sum = numbers.reduce((a, b) => a + b, 0);
    const avg = sum / numbers.length;
    
    // Standard Deviation
    const sqDiff = numbers.map(v => Math.pow(v - avg, 2));
    const avgSqDiff = sqDiff.reduce((a, b) => a + b, 0) / numbers.length;
    const stdDev = Math.sqrt(avgSqDiff);
    
    return { min, max, avg, stdDev, count: numbers.length };
}

function countOutliers(values, threshold, direction = 'below') {
    const numbers = values.filter(v => typeof v === 'number' && !isNaN(v));
    if (direction === 'below') {
        return numbers.filter(v => v < threshold).length;
    } else {
        return numbers.filter(v => v > threshold).length;
    }
}

function getOutlierSummary(values, threshold = THRESHOLDS.OUTLIER_THRESHOLD_DEFAULT, direction = 'below') {
    const numbers = values.filter(v => typeof v === 'number' && !isNaN(v));
    let atZero = 0;
    let belowThreshold = 0;
    
    numbers.forEach(v => {
        if (v === 0) atZero++;
        if (direction === 'below' && v < threshold) belowThreshold++;
        if (direction === 'above' && v > threshold) belowThreshold++;
    });
    
    return { atZero, belowThreshold, total: numbers.length, hasCritical: atZero > 0, hasWarning: belowThreshold > atZero };
}

// Format outlier badge with count and label
function formatOutlierBadge(countAtZero, countBelowThreshold, threshold = THRESHOLDS.OUTLIER_THRESHOLD_DEFAULT) {
    let badges = '';
    if (countAtZero > 0) {
        badges += `<span style="background:#dc2626; color:white; padding:2px 6px; border-radius:4px; font-size:0.7em; margin-left:4px; white-space:nowrap;" title="${countAtZero} agent(s) at 0%">${countAtZero} @0%</span>`;
    }
    if (countBelowThreshold > countAtZero) {
        const belowOnly = countBelowThreshold - countAtZero;
        badges += `<span style="background:#f59e0b; color:white; padding:2px 6px; border-radius:4px; font-size:0.7em; margin-left:4px; white-space:nowrap;" title="${belowOnly} agent(s) below ${threshold}%">${belowOnly} <${threshold}%</span>`;
    }
    return badges;
}

// Format distribution stats for display in table cells
function formatDistributionCell(avg, stats, showStdDev = true) {
    if (avg === "N/A") {
        return `<span style="color:#6b7280; font-style:italic;">N/A</span>`;
    }
    if (typeof avg !== 'number' || isNaN(avg)) {
        return `<span style="color:#6b7280;">--</span>`;
    }
    
    // FIX: Only hide distribution stats when:
    // 1. No stats available or count <= 1 (single agent - no distribution)
    // 2. All values are BOTH identical AND at 100% (perfect uniform score)
    // CHANGED: Show min/max/stdev for cells < 100% even if uniform
    // This ensures users see distribution info for imperfect scores
    if (!stats || stats.count <= 1) {
        return `${avg.toFixed(1)}%`;
    }
    
    // Only hide stats if ALL values are identical AND perfect (100%)
    if (stats.min === stats.max && stats.min >= 99.9) {
        return `${avg.toFixed(1)}%`;
    }
    
    const rangeStr = `${stats.min.toFixed(0)}-${stats.max.toFixed(0)}`;
    if (showStdDev && stats.stdDev > 0) {
        return `${avg.toFixed(1)}% <span style="font-size:0.8em; color:#6b7280;">(${rangeStr}, σ=${stats.stdDev.toFixed(1)})</span>`;
    }
    // Show range even if stdDev is 0 (uniform non-100% values)
    if (stats.min !== stats.max) {
        return `${avg.toFixed(1)}% <span style="font-size:0.8em; color:#6b7280;">(${rangeStr})</span>`;
    }
    // Uniform values < 100%: show the uniform value indicator
    return `${avg.toFixed(1)}% <span style="font-size:0.8em; color:#6b7280;">(all ${stats.min.toFixed(0)}%)</span>`;
}

// Get worst performer for a territory's metric
function getWorstPerformerForMetric(territory, metricKey, criticalThreshold = 50) {
    const agentData = window.realAgentData ? window.realAgentData[territory] : null;
    if (!agentData || !agentData[metricKey] || agentData[metricKey].length === 0) {
        return { agent: null, value: 0 };
    }
    
    const values = agentData[metricKey];
    let minIndex = 0;
    let minValue = values[0];
    for (let i = 1; i < values.length; i++) {
        if (values[i] < minValue) {
            minValue = values[i];
            minIndex = i;
        }
    }
    
    const agents = agentData.agents || [];
    const realAgent = agents[minIndex] || {
        name: `Agent_${minIndex + 1}`,
        path: `agentic_core/${territory.toLowerCase().replace(/[\s\/]+/g, '_')}/agent_${minIndex + 1}.py`
    };
    
    return { agent: realAgent, value: minValue };
}

// Format worst performer as a VS Code link
function formatWorstPerformerLink(agent, value, criticalThreshold = 50) {
    if (!agent) return '<span style="color:#9ca3af;">—</span>';
    const isCritical = value < criticalThreshold;
    const bgColor = isCritical ? 'rgba(220, 38, 38, 0.15)' : 'rgba(59, 130, 246, 0.1)';
    const textColor = isCritical ? '#dc2626' : '#2563eb';
    const path = agent.path || agent.file_path || '';
    const name = agent.name || agent.agent_name || path.split('/').pop() || 'Unknown';
    const displayName = name.length > 20 ? name.substring(0, 18) + '...' : name;
    
    if (path) {
        return `<a href="vscode://file/${path}" style="color:${textColor}; text-decoration:none; background:${bgColor}; padding:2px 6px; border-radius:4px; font-size:0.85em; white-space:nowrap;" title="Open ${name} in VS Code (${path})">${displayName} (${value.toFixed(0)}%)</a>`;
    }
    return `<span style="color:${textColor}; background:${bgColor}; padding:2px 6px; border-radius:4px; font-size:0.85em; white-space:nowrap;" title="${name}">${displayName} (${value.toFixed(0)}%)</span>`;
}

// Check if a territory row has any critical outliers
function hasRowCriticalOutliers(territory) {
    const agentData = window.realAgentData ? window.realAgentData[territory] : null;
    if (!agentData) return { hasCritical: false, hasWarning: false, criticalCount: 0, warningCount: 0 };
    
    let criticalCount = 0;
    let warningCount = 0;
    
    const metrics = ['healCap', 'invocation', 'hardened', 'test', 'complexityHealth', 'health'];
    metrics.forEach(key => {
        const summary = getOutlierSummary(agentData[key] || [], 50);
        criticalCount += summary.atZero;
        warningCount += summary.belowThreshold - summary.atZero;
    });
    
    return { hasCritical: criticalCount > 0, hasWarning: warningCount > 0, criticalCount, warningCount };
}

// Export functions globally
window.computeDistributionStats = computeDistributionStats;
window.countOutliers = countOutliers;
window.getOutlierSummary = getOutlierSummary;
window.formatOutlierBadge = formatOutlierBadge;
window.formatDistributionCell = formatDistributionCell;
window.getWorstPerformerForMetric = getWorstPerformerForMetric;
window.formatWorstPerformerLink = formatWorstPerformerLink;
window.hasRowCriticalOutliers = hasRowCriticalOutliers;
