/**
 * HTML Formatting Utilities
 */

function generateSparkline(values, width = 60, height = 20) {
    if (!values || values.length < 2) return '';
    
    const min = Math.min(...values);
    const max = Math.max(...values);
    const range = max - min || 1;
    
    // Generate SVG path
    const points = values.map((val, idx) => {
        const x = (idx / (values.length - 1)) * width;
        const y = height - ((val - min) / range) * height;
        return `${x},${y}`;
    }).join(' ');
    
    const lastVal = values[values.length - 1];
    const prevVal = values[values.length - 2];
    const color = lastVal >= prevVal ? '#16a34a' : '#dc2626'; // Green up, Red down

    return `
        <div class="sparkline-container">
            <svg class="sparkline-svg" width="${width}" height="${height}">
                <polyline points="${points}" fill="none" stroke="${color}" stroke-width="2" />
                <circle cx="${width}" cy="${height - ((lastVal - min) / range) * height}" r="2" fill="${color}" />
            </svg>
        </div>
    `;
}

function formatDistributionCell(val, stats, isPercent = true) {
    if (val === "N/A" || val === undefined) return '<span style="color:#9ca3af; font-style:italic;">N/A</span>';
    
    const numVal = parseFloat(val);
    const formatted = isPercent ? numVal.toFixed(1) + '%' : numVal.toFixed(1);
    
    // Only show detailed stats if we have distribution data
    if (stats && stats.count > 1) {
        return `
            <div style="font-weight:700;">${formatted}</div>
            <div style="font-size:0.7em; color:#6b7280; margin-top:2px;">
                σ=${stats.stdDev.toFixed(1)}<br>
                ${stats.min.toFixed(0)}-${stats.max.toFixed(0)}
            </div>
        `;
    }
    return `<div style="font-weight:700;">${formatted}</div>`;
}

function formatOutlierBadge(atZero, belowThreshold, threshold) {
    if (belowThreshold === 0) return '';
    
    let html = '<div style="margin-top:4px; display:flex; justify-content:center; gap:4px;">';
    
    if (atZero > 0) {
        html += `<span style="background:#fee2e2; color:#991b1b; border:1px solid #fecaca; padding:0 4px; border-radius:4px; font-size:0.7em; font-weight:600;" title="${atZero} agents at 0%">🚫 ${atZero}</span>`;
    }
    
    const remaining = belowThreshold - atZero;
    if (remaining > 0) {
        html += `<span style="background:#fef3c7; color:#92400e; border:1px solid #fde68a; padding:0 4px; border-radius:4px; font-size:0.7em; font-weight:600;" title="${remaining} agents < ${threshold}%">⚠️ ${remaining}</span>`;
    }
    
    html += '</div>';
    return html;
}

function formatRowWarningIcon(territory) {
    // Depends on global functions which will be refactored in later phases
    // For Phase 3, we simply delegate or return empty if logic depends on 
    // not-yet-extracted controllers. 
    // Note: requires hasRowCriticalOutliers which is in main logic currently.
    // We will keep specific complex DOM logic in main for now or pass status in.
    return ''; 
}
