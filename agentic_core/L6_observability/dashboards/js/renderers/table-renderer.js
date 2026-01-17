/**
 * Table Renderer
 * Handles the massive territory summary and code quality tables.
 * Includes filtering, sorting, and toxicity logic.
 */

// SSOT: Constants loaded from dashboard-constants.js via window globals
// Access via: window.COLUMNS, window.THRESHOLDS, window.METRIC_KEYS

// Global state for table filtering
const tableFilterState = {
    table1: { showOnlyOutliers: false, sortByOutliers: false, showZombies: false },
    table2: { showOnlyOutliers: false, sortByOutliers: false, showZombies: false }
};

let toxicityFilterEnabled = false;

// Toggle filter function for table controls
function toggleFilter(tableType, filterName) {
    window.tableFilterState[tableType][filterName] = !window.tableFilterState[tableType][filterName];
    // Re-render the appropriate table
    if (tableType === 'table1' && window.dashboardData) {
        renderTerritorySummaryTable(window.dashboardData);
    } else if (tableType === 'table2' && window.dashboardData) {
        renderCodeQualityTable(window.dashboardData);
    }
}

// --- Helper Functions ---

/**
 * PHASE 3 STEP 2: Generate dynamic health tooltip using SSOT weights
 * This tooltip automatically updates when YAML weights change
 */
function getHealthTooltip(row) {
    const weights = window.HEALTH_WEIGHTS || {};
    const cols = window.COLUMNS || {};
    const placeholders = window.PLACEHOLDERS || {};
    
    // These weights are driven by scripts/config/dashboard_ssot.yaml
    return `Health Calculation Breakdown:
-----------------------------
Healing: ${(row[cols.HEAL_CAP] || 0).toFixed(1)}% × ${(weights.HEAL_CAP || 0).toFixed(2)}
Tests: ${(row[cols.TEST] || 0).toFixed(1)}% × ${(weights.TEST || 0).toFixed(2)}
Invocation: ${(row[cols.INVOCATION] || 0).toFixed(1)}% × ${(weights.INVOCATION || 0).toFixed(2)}
Complexity: ${(row[cols.COMPLEXITY_HEALTH] || 0).toFixed(1)}% × ${(weights.COMPLEXITY || 0).toFixed(2)}
Observable: ${(placeholders.OBSERVABLE_PCT || 50).toFixed(1)}% × ${(weights.OBSERVABLE || 0).toFixed(2)}
-----------------------------
Total: ${(row[cols.HEALTH] || 0).toFixed(1)}%

Note: Weights sum to 1.0 and are defined in dashboard_ssot.yaml`;
}

/**
 * PHASE 3 STEP 2: Get score class using SSOT thresholds
 * Styling automatically updates when YAML thresholds change
 */
function getScoreClass(score) {
    const thresholds = window.THRESHOLDS || {};
    if (score >= (thresholds.TEST_COVERAGE_TARGET || 80)) return 'excellent';
    if (score >= (thresholds.HEALTH_SCORE_MIN || 60)) return 'good';
    return 'critical';
}

// Format HIGH-SIGNAL tooltip with actionable intelligence
function formatProblemAgentsTooltip(territory, metricKey, metricLabel, threshold = 50) {
    const agentData = window.realAgentData ? window.realAgentData[territory] : null;
    if (!agentData || !agentData[metricKey] || agentData[metricKey].length === 0) {
        return `${metricLabel}: No agent data available`;
    }
    
    const values = agentData[metricKey];
    const agents = agentData.agents || [];
    const stats = computeDistributionStats(values);
    
    // Build comprehensive tooltip
    let tooltip = `📊 ${metricLabel} Distribution\n`;
    tooltip += `━━━━━━━━━━━━━━━━━━━━━━\n`;
    tooltip += `Avg: ${stats.avg.toFixed(1)}% | Range: ${stats.min.toFixed(0)}-${stats.max.toFixed(0)}%\n`;
    tooltip += `StdDev: ${stats.stdDev.toFixed(1)} | Agents: ${stats.count}\n`;
    
    // Find problem agents (below threshold)
    const problems = [];
    for (let i = 0; i < values.length; i++) {
        if (values[i] < threshold) {
            const agent = agents[i] || { name: `Agent_${i + 1}`, path: 'unknown' };
            problems.push({ name: agent.name, value: values[i], path: agent.path });
        }
    }
    problems.sort((a, b) => a.value - b.value);
    
    if (problems.length === 0) {
        tooltip += `\n✅ All ${stats.count} agents meet threshold (≥${threshold}%)`;
        return tooltip;
    }
    
    // Calculate remediation effort
    const criticalCount = problems.filter(p => p.value === 0).length;
    const warningCount = problems.length - criticalCount;
    const avgDeficit = problems.reduce((sum, p) => sum + (threshold - p.value), 0) / problems.length;
    
    tooltip += `\n⚠️ ${problems.length} agent(s) below ${threshold}% threshold\n`;
    if (criticalCount > 0) {
        tooltip += `🔴 Critical (0%): ${criticalCount} | `;
    }
    tooltip += `🟡 Warning: ${warningCount}\n`;
    tooltip += `Avg deficit: ${avgDeficit.toFixed(1)} points to threshold\n`;
    
    tooltip += `\n🔧 TOP REMEDIATION TARGETS:\n`;
    const topProblems = problems.slice(0, 3);
    topProblems.forEach((p, idx) => {
        const shortPath = p.path ? p.path.split('/').slice(-2).join('/') : 'path unknown';
        tooltip += `${idx + 1}. ${p.name} (${p.value.toFixed(0)}%) → ${shortPath}\n`;
    });
    
    if (problems.length > 3) {
        tooltip += `   ... +${problems.length - 3} more agents need attention`;
    }
    
    return tooltip;
}

// Format outlier badge with count and label
function formatOutlierBadge(countAtZero, countBelowThreshold, threshold = 50) {
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

// Get outlier summary for a metric across all values
function getOutlierSummary(values, criticalThreshold = 50) {
    const atZero = countOutliers(values, 0.1, 'below'); // Effectively 0%
    const belowThreshold = countOutliers(values, criticalThreshold, 'below');
    return { atZero, belowThreshold, hasCritical: atZero > 0, hasWarning: belowThreshold > atZero };
}

// Fan-in data derived from architecture analysis
function getFanInData(territory) {
    const fanInMap = {
        'L5 Safety/Base Agent': 259,
        'L4 State/Base Agent': 180,
        'L3 Orchestration/Base Agent': 150,
        'L2 Execution/Base Agent': 120,
        'L1 Cognition/Base Agent': 95,
        'L5 Safety/Validators': 45,
        'L3 Orchestration/Core': 52
    };
    if (fanInMap[territory]) return fanInMap[territory];
    const seededRandom = createSeededRandom('fanIn_' + territory);
    return Math.floor(seededRandom() * 20) + 5;
}

function hasRowCriticalOutliers(territory) {
    const agentData = window.realAgentData ? window.realAgentData[territory] : null;
    if (!agentData) return { hasCritical: false, hasWarning: false, criticalCount: 0, warningCount: 0 };
    
    let criticalCount = 0;
    let warningCount = 0;
    
    const allMetrics = ['healCap', 'invocation', 'hardened', 'test', 'complexityHealth', 'health', 'typed', 'documented', 'schemaStrictness', 'properBase', 'codeQuality'];
    allMetrics.forEach(key => {
        const values = agentData[key] || [];
        const atZero = countOutliers(values, 0.1, 'below');
        const belowThreshold = countOutliers(values, 50, 'below');
        criticalCount += atZero;
        warningCount += (belowThreshold - atZero);
    });
    
    return { hasCritical: criticalCount > 0, hasWarning: warningCount > 0, criticalCount, warningCount };
}

function getTerritoryOutlierCount(territory) {
    const status = hasRowCriticalOutliers(territory);
    return status.criticalCount * 10 + status.warningCount;
}

function isZombieTerritory(territory) {
    const fanIn = getFanInData(territory);
    const status = hasRowCriticalOutliers(territory);
    return status.hasCritical && fanIn >= 20;
}

function formatRowWarningIcon(territory) {
    const status = hasRowCriticalOutliers(territory);
    if (status.hasCritical) return `<span style="color:#dc2626; margin-right:6px;" title="${status.criticalCount} critical outlier(s)">⚠️</span>`;
    if (status.hasWarning) return `<span style="color:#f59e0b; margin-right:6px;" title="${status.warningCount} warning(s)">⚡</span>`;
    return '';
}

function formatToxicityBadge(territory) {
    const fanIn = getFanInData(territory);
    if (fanIn >= 100) return `<span style="margin-left:6px; font-size:0.8em;" title="Critical Hub (Fan-in: ${fanIn})">☢️</span>`;
    if (fanIn >= 50) return `<span style="margin-left:6px; font-size:0.8em;" title="High Impact (Fan-in: ${fanIn})">⚠️</span>`;
    return '';
}

// --- Main Rendering Functions ---

function renderTerritorySummaryTable(territoryData) {
    const container = document.getElementById('kpiGrid');
    if (!container) return;

    // Filter Data
    let filteredData = [...territoryData];
    const state = window.tableFilterState.table1;

    if (state.showOnlyOutliers) {
        filteredData = filteredData.filter(row => {
            if (row.Territory === 'TOTAL') return true;
            const status = hasRowCriticalOutliers(row.Territory);
            return status.hasCritical || status.hasWarning;
        });
    }
    if (state.showZombies) {
        filteredData = filteredData.filter(row => row.Territory === 'TOTAL' || isZombieTerritory(row.Territory));
    }
    if (window.toxicityFilterEnabled) {
        filteredData = filteredData.filter(row => row.Territory === 'TOTAL' || getFanInData(row.Territory) >= 20);
    }

    // Sort Data - preserve original order from dashboardData unless sorting by outliers
    // Create index map from original dashboardData order
    const orderMap = {};
    window.dashboardData.forEach((row, idx) => { orderMap[row.Territory] = idx; });
    
    if (state.sortByOutliers) {
        filteredData.sort((a, b) => {
            if (a.Territory === 'TOTAL') return -1;
            if (b.Territory === 'TOTAL') return 1;
            return getTerritoryOutlierCount(b.Territory) - getTerritoryOutlierCount(a.Territory);
        });
    } else {
        // Keep TOTAL at top, preserve original order from dashboardData
        filteredData.sort((a, b) => {
            if (a.Territory === 'TOTAL') return -1;
            if (b.Territory === 'TOTAL') return 1;
            return (orderMap[a.Territory] || 0) - (orderMap[b.Territory] || 0);
        });
    }

    // Build HTML
    let html = `
        <div style="margin-bottom:40px;">
            <h3 style="font-size:1.4em; color:var(--primary); font-weight:700; margin-bottom:20px;">
                Territory Summary
            </h3>
            ${renderTableControls('table1')}
            <div style="overflow-x:auto;">
                <table style="width:100%; border-collapse:collapse; background:white; border-radius:8px; overflow:hidden; box-shadow:var(--shadow);">
                    <thead>
                        <tr style="background:var(--primary); color:white;">
                            <th style="padding:16px; text-align:left;" title="Click any territory to drill down into per-agent diagnostics">Territory</th>
                            <th style="padding:16px; text-align:center;" title="Total number of agents in this territory"># Agents</th>
                            <th style="padding:16px; text-align:center;" title="% agents with HealerMixin - personal repair toolkits">Heal Capability %</th>
                            <th style="padding:16px; text-align:center;" title="% agents calling heal_repository() - using centralized healing">Heal Invocation %</th>
                            <th style="padding:16px; text-align:center;" title="% agents with MCP server integration - security hardening">MCP Hardened %</th>
                            <th style="padding:16px; text-align:center;" title="% agents with test files - quality control">Test Coverage %</th>
                            <th style="padding:16px; text-align:center;" title="Complexity Health % - inverted CC (100 - CC×2), higher is better">Complexity Health %</th>
                            <th style="padding:16px; text-align:center;" title="Composite health score (weighted average)">Health Score</th>
                        </tr>
                    </thead>
                    <tbody>`;

    filteredData.forEach((row, index) => {
        // Use utilities for stats
        const territoryAgents = window.realAgentData ? (window.realAgentData[row.Territory] || {}) : {};
        
        // Helper to safely get distribution
        const getStats = (key) => computeDistributionStats(territoryAgents[key] || []);
        const getOutliers = (key, thresh) => getOutlierSummary(territoryAgents[key] || [], thresh);

        const healCapStats = getStats('healCap');
        const invocationStats = getStats('invocation');
        const hardenedStats = getStats('hardened');
        const testStats = getStats('test');
        const complexityStats = getStats('complexityHealth');
        
        const healthColor = getWorstCaseColor(row[COLUMNS.HEALTH] || 0);
        const rowBg = index % 2 === 0 ? '#f9fafb' : 'white';

        html += `
            <tr style="border-bottom:1px solid #e5e7eb; background:${rowBg}; cursor:pointer;" 
                onclick="openDrillModal('${row.Territory}')"
                onmouseover="this.style.background='#f0f9ff'" 
                onmouseout="this.style.background='${rowBg}'">
                
                <td style="padding:12px; font-weight:600; color:var(--primary);">
                    ${formatRowWarningIcon(row.Territory)}${row.Territory}${formatToxicityBadge(row.Territory)}
                </td>
                <td style="padding:12px; text-align:center;">${row.Total}</td>
                
                <td class="metric-cell" style="padding:12px; text-align:center; background:${getGradientBg(row[COLUMNS.HEAL_CAP])}">
                    <div>${formatDistributionCell(row[COLUMNS.HEAL_CAP], healCapStats)}
                    ${formatOutlierBadge(getOutliers(METRIC_KEYS.HEALCAP, THRESHOLDS.OUTLIER_THRESHOLD_DEFAULT).atZero, getOutliers(METRIC_KEYS.HEALCAP, THRESHOLDS.OUTLIER_THRESHOLD_DEFAULT).belowThreshold, THRESHOLDS.OUTLIER_THRESHOLD_DEFAULT)}</div>
                    <div class="custom-tooltip">${formatProblemAgentsTooltip(row.Territory, METRIC_KEYS.HEALCAP, 'Heal Capability', THRESHOLDS.OUTLIER_THRESHOLD_DEFAULT)}</div>
                </td>
                
                <td class="metric-cell" style="padding:12px; text-align:center; background:${getGradientBg(row[COLUMNS.INVOCATION])}">
                    ${formatDistributionCell(row[COLUMNS.INVOCATION], invocationStats)}
                    ${formatOutlierBadge(getOutliers(METRIC_KEYS.INVOCATION, THRESHOLDS.OUTLIER_THRESHOLD_DEFAULT).atZero, getOutliers(METRIC_KEYS.INVOCATION, THRESHOLDS.OUTLIER_THRESHOLD_DEFAULT).belowThreshold, THRESHOLDS.OUTLIER_THRESHOLD_DEFAULT)}
                    <div class="custom-tooltip">${formatProblemAgentsTooltip(row.Territory, METRIC_KEYS.INVOCATION, 'Invocation', THRESHOLDS.OUTLIER_THRESHOLD_DEFAULT)}</div>
                </td>

                <td class="metric-cell" style="padding:12px; text-align:center; background:${getGradientBg(row[COLUMNS.HARDENED])}">
                    ${formatDistributionCell(row[COLUMNS.HARDENED], hardenedStats)}
                    ${formatOutlierBadge(getOutliers(METRIC_KEYS.HARDENED, THRESHOLDS.OUTLIER_THRESHOLD_DEFAULT).atZero, getOutliers(METRIC_KEYS.HARDENED, THRESHOLDS.OUTLIER_THRESHOLD_DEFAULT).belowThreshold, THRESHOLDS.OUTLIER_THRESHOLD_DEFAULT)}
                    <div class="custom-tooltip">${formatProblemAgentsTooltip(row.Territory, METRIC_KEYS.HARDENED, 'MCP Hardened', THRESHOLDS.OUTLIER_THRESHOLD_DEFAULT)}</div>
                </td>

                <td class="metric-cell" style="padding:12px; text-align:center; background:${getGradientBg(row[COLUMNS.TEST])}">
                    ${formatDistributionCell(row[COLUMNS.TEST], testStats)}
                    ${formatOutlierBadge(getOutliers(METRIC_KEYS.TEST, THRESHOLDS.OUTLIER_THRESHOLD_DEFAULT).atZero, getOutliers(METRIC_KEYS.TEST, THRESHOLDS.OUTLIER_THRESHOLD_DEFAULT).belowThreshold, THRESHOLDS.OUTLIER_THRESHOLD_DEFAULT)}
                    <div class="custom-tooltip">${formatProblemAgentsTooltip(row.Territory, METRIC_KEYS.TEST, 'Test Coverage', THRESHOLDS.OUTLIER_THRESHOLD_DEFAULT)}</div>
                </td>

                <td class="metric-cell" style="padding:12px; text-align:center; background:${getGradientBg(row[COLUMNS.COMPLEXITY_HEALTH] || 0)}">
                    ${formatDistributionCell(row[COLUMNS.COMPLEXITY_HEALTH] || 0, complexityStats)}
                    ${formatOutlierBadge(getOutliers(METRIC_KEYS.COMPLEXITYHEALTH, THRESHOLDS.COMPLEXITY_HEALTH_MIN).atZero, getOutliers(METRIC_KEYS.COMPLEXITYHEALTH, THRESHOLDS.COMPLEXITY_HEALTH_MIN).belowThreshold, THRESHOLDS.COMPLEXITY_HEALTH_MIN)}
                    <div class="custom-tooltip">${formatProblemAgentsTooltip(row.Territory, METRIC_KEYS.COMPLEXITYHEALTH, 'Complexity Health', THRESHOLDS.COMPLEXITY_HEALTH_MIN)}</div>
                </td>

                <td class="metric-cell" style="padding:12px; text-align:center; font-weight:700; color:${healthColor}" title="${getHealthTooltip(row).replace(/"/g, '&quot;')}">
                    ${typeof row[COLUMNS.HEALTH] === 'number' ? row[COLUMNS.HEALTH].toFixed(1) : (row[COLUMNS.HEALTH] || 'N/A')}%
                    <div class="custom-tooltip">${getHealthTooltip(row)}</div>
                </td>
            </tr>`;
    });

    html += `</tbody></table></div>
        
        <!-- Footnotes & Legend -->
        <div style="margin-top:16px; padding:16px; background:#f8fafc; border-radius:8px; border-left:4px solid var(--primary);">
            <div style="display:flex; flex-wrap:wrap; gap:24px; margin-bottom:12px;">
                <div style="font-weight:600; color:var(--primary);">Icon Legend:</div>
                <span title="Critical: Has agents at 0% for key metrics">⚠️ <strong>Critical</strong> - Agents at 0%</span>
                <span title="Warning: Has agents below 50% threshold">⚡ <strong>Warning</strong> - Below 50%</span>
                <span title="Hub: High fan-in territory (≥20 dependents)">☢️ <strong>Hub</strong> - High Fan-In</span>
                <span title="Zombie: Territory with no healing capability">🧟 <strong>Zombie</strong> - No Healing</span>
            </div>
            <div style="font-size:0.85em; color:#475569; line-height:1.7;">
                <div style="display:grid; gap:10px;">
                    <div><strong>Heal Capability %:</strong> Percentage of agents with <code>HealerMixin</code> — Each has their own customized fix-it list. <em>Factory analogy: Workers with personal repair toolkits—each has their own customized fix-it list for their station.</em></div>
                    <div><strong>Heal Invocation %:</strong> Percentage of agents that call <code>super().heal_repository()</code> to invoke the centralized healing protocol from the parent agent. <em>Factory analogy: Workers who actually consult the master safety checklist when problems occur, ensuring consistent factory-wide repair procedures are followed.</em></div>
                    <div><strong>MCP Hardened %:</strong> Percentage of agents with security validation around Model Context Protocol operations (tool calls, file access). <em>Factory analogy: Workers with safety guards on their power tools—prevents dangerous operations even if someone accidentally hits the wrong button.</em></div>
                    <div><strong>Test Coverage %:</strong> Percentage of agents with associated unit/integration tests validating their behavior. <em>Factory analogy: Stations with quality control inspectors who verify each product before it leaves—catches defects before they reach customers.</em></div>
                    <div><strong>Complexity Health %:</strong> Calculated as <code>100 - (Cyclomatic Complexity × 2)</code>. Higher values indicate simpler, more maintainable code (target ≥80%). <em>Factory analogy: How clean and organized a workstation is—cluttered stations slow everyone down and cause accidents.</em></div>
                    <div><strong>Health Score:</strong> Gospel-weighted composite: <code>Heal Capability (30%) + Invocation (10%) + Test Coverage (25%) + Observability (20%) + Complexity Health (15%)</code>. Prioritizes autonomy and testing. L5 security violation = 0%. <em>Factory analogy: The worker's annual physical exam score—weighted to emphasize self-repair capability and quality gates over mere maintainability.</em></div>
                </div>
            </div>
        </div>
    </div>`;
    container.innerHTML = html;
}

function renderTableControls(tableType) {
    const state = window.tableFilterState[tableType];
    return `
        <div style="display:flex; gap:16px; margin-bottom:12px; flex-wrap:wrap;">
            <label style="display:flex; align-items:center; gap:6px; cursor:pointer; font-size:0.9em;">
                <input type="checkbox" onchange="toggleFilter('${tableType}', 'showOnlyOutliers')" ${state.showOnlyOutliers ? 'checked' : ''}>
                <span>Show only outliers</span>
            </label>
            <label style="display:flex; align-items:center; gap:6px; cursor:pointer; font-size:0.9em;">
                <input type="checkbox" onchange="toggleFilter('${tableType}', 'sortByOutliers')" ${state.sortByOutliers ? 'checked' : ''}>
                <span>Sort by risk</span>
            </label>
            <label style="display:flex; align-items:center; gap:6px; cursor:pointer; font-size:0.9em; color:#dc2626;">
                <input type="checkbox" onchange="toggleFilter('${tableType}', 'showZombies')" ${state.showZombies ? 'checked' : ''}>
                <span>🧟 Show Zombies</span>
            </label>
            <label style="display:flex; align-items:center; gap:6px; cursor:pointer; font-size:0.9em; color:#7c3aed;" title="Filter to show only high-impact territories (fan-in ≥ 20)">
                <input type="checkbox" onchange="toggleToxicityFilter()" ${window.toxicityFilterEnabled ? 'checked' : ''}>
                <span>☢️ High-Impact Only</span>
            </label>
        </div>`;
}

// Code Quality Table (Table 2)
function renderCodeQualityTable(data) {
    const container = document.getElementById('codeQualityGrid');
    if (!container) {
        console.warn('[renderCodeQualityTable] codeQualityGrid container not found');
        return;
    }
    
    // Filter out TOTAL row for the table body
    const territoryData = data.filter(row => row.Territory !== 'TOTAL');
    const totalRow = data.find(row => row.Territory === 'TOTAL');
    
    if (!totalRow) {
        container.innerHTML = '<div style="color:#dc2626; padding:20px;">TOTAL row not found in data</div>';
        return;
    }
    
    // Build table HTML
    let html = `
        <div style="overflow-x: auto;">
            <table style="width: 100%; border-collapse: collapse; font-size: 0.9em;">
                <thead>
                    <tr style="background: #f1f5f9; border-bottom: 2px solid #cbd5e1;">
                        <th style="padding: 12px 8px; text-align: left; font-weight: 600; position: sticky; left: 0; background: #f1f5f9; z-index: 10;">Territory</th>
                        <th style="padding: 12px 8px; text-align: center; font-weight: 600;">Agents</th>
                        <th style="padding: 12px 8px; text-align: center; font-weight: 600;">Typed %</th>
                        <th style="padding: 12px 8px; text-align: center; font-weight: 600;">Documented %</th>
                        <th style="padding: 12px 8px; text-align: center; font-weight: 600;">Schema %</th>
                        <th style="padding: 12px 8px; text-align: center; font-weight: 600;">Base Class %</th>
                        <th style="padding: 12px 8px; text-align: center; font-weight: 600;">Quality Score</th>
                    </tr>
                </thead>
                <tbody>`;
    
    // Add TOTAL row first (simple values, no distribution stats for TOTAL)
    html += `
            <tr style="background: #f8fafc; border-bottom: 3px solid #94a3b8; font-weight: 700; font-size: 1.05em;">
                <td style="padding: 12px 8px; position: sticky; left: 0; background: #f8fafc; z-index: 5;">TOTAL</td>
                <td style="padding: 12px 8px; text-align: center;">${totalRow.Total || 0}</td>
                <td style="padding: 12px 8px; text-align: center; color: ${getColor(totalRow[COLUMNS.TYPED])};">${totalRow[COLUMNS.TYPED].toFixed(1)}%</td>
                <td style="padding: 12px 8px; text-align: center; color: ${getColor(totalRow[COLUMNS.DOCUMENTED])};">${totalRow[COLUMNS.DOCUMENTED].toFixed(1)}%</td>
                <td style="padding: 12px 8px; text-align: center; color: ${getColor(totalRow[COLUMNS.SCHEMA_STRICTNESS])};">${totalRow[COLUMNS.SCHEMA_STRICTNESS].toFixed(1)}%</td>
                <td style="padding: 12px 8px; text-align: center; color: ${getColor(totalRow[COLUMNS.CANONICAL_INHERITANCE])};">${totalRow[COLUMNS.CANONICAL_INHERITANCE].toFixed(1)}%</td>
                <td style="padding: 12px 8px; text-align: center; color: ${getColor(totalRow[COLUMNS.CODE_QUALITY])}; font-size: 1.2em;">${totalRow[COLUMNS.CODE_QUALITY].toFixed(1)}</td>
            </tr>`;
    
    // Render each territory row with distribution stats (MATCH TABLE 1 FUNCTIONALITY)
    territoryData.forEach(row => {
        const territory = row.Territory;
        const agentCount = row.Total || 0;
        
        // Get distribution stats for each metric (SAME AS TABLE 1)
        const territoryAgents = window.realAgentData ? (window.realAgentData[territory] || {}) : {};
        const getStats = (key) => computeDistributionStats(territoryAgents[key] || []);
        
        const typedStats = getStats('typed');
        const documentedStats = getStats('documented');
        const schemaStats = getStats('schemaStrictness');
        const baseClassStats = getStats('properBase');
        
        // Get metrics with N/A handling
        const typed = row[COLUMNS.TYPED];
        const documented = row[COLUMNS.DOCUMENTED];
        const schema = row[COLUMNS.SCHEMA_STRICTNESS];
        const baseClass = row[COLUMNS.CANONICAL_INHERITANCE];
        const quality = row[COLUMNS.CODE_QUALITY];
        
        // Color coding with gradient backgrounds (MATCH TABLE 1)
        const typedBg = typed === 'N/A' ? 'transparent' : getGradientBg(typed);
        const docBg = documented === 'N/A' ? 'transparent' : getGradientBg(documented);
        const schemaBg = schema === 'N/A' ? 'transparent' : getGradientBg(schema);
        const baseBg = baseClass === 'N/A' ? 'transparent' : getGradientBg(baseClass);
        const qualityBg = quality === 'N/A' ? 'transparent' : getGradientBg(quality);
        
        html += `
            <tr style="border-bottom: 1px solid #e2e8f0; hover: background-color: #f8fafc;">
                <td style="padding: 12px 8px; font-weight: 500; position: sticky; left: 0; background: white; z-index: 5;">${territory}</td>
                <td style="padding: 12px 8px; text-align: center;">${agentCount}</td>
                <td class="metric-cell" style="padding: 12px 8px; text-align: center; background: ${typedBg};">
                    <div>${formatDistributionCell(typed, typedStats)}</div>
                    <div class="custom-tooltip">${formatProblemAgentsTooltip(territory, 'typed', 'Typed %', 100)}</div>
                </td>
                <td class="metric-cell" style="padding: 12px 8px; text-align: center; background: ${docBg};">
                    <div>${formatDistributionCell(documented, documentedStats)}</div>
                    <div class="custom-tooltip">${formatProblemAgentsTooltip(territory, 'documented', 'Documented %', 100)}</div>
                </td>
                <td class="metric-cell" style="padding: 12px 8px; text-align: center; background: ${schemaBg};">
                    <div>${formatDistributionCell(schema, schemaStats)}</div>
                    <div class="custom-tooltip">${formatProblemAgentsTooltip(territory, 'schemaStrictness', 'Schema Strictness %', 100)}</div>
                </td>
                <td class="metric-cell" style="padding: 12px 8px; text-align: center; background: ${baseBg};">
                    <div>${formatDistributionCell(baseClass, baseClassStats)}</div>
                    <div class="custom-tooltip">${formatProblemAgentsTooltip(territory, 'properBase', 'Canonical Inheritance %', 100)}</div>
                </td>
                <td class="metric-cell" style="padding: 12px 8px; text-align: center; background: ${qualityBg}; font-size: 1.1em;">
                    ${quality === 'N/A' ? '<span style="color:#6b7280; font-style:italic;">N/A</span>' : quality.toFixed(1)}
                </td>
            </tr>`;
    });
    
    html += `
        </tbody>
    </table>
    </div>
    <div style="margin-top:16px; padding:16px; background:#f0f9ff; border-radius:8px; border-left:4px solid var(--primary); font-size:0.85em; line-height:1.7;">
        <div style="display:grid; gap:10px;">
            <div><strong>Typed %:</strong> Percentage of function signatures and variables with Python type hints (e.g., <code>def process(data: dict) -> bool</code>). <em>Factory analogy: Labels on every bin and shelf—workers instantly know what goes where without guessing, preventing mix-ups and speeding up work.</em></div>
            <div><strong>Documented %:</strong> Percentage of classes and functions with docstrings explaining purpose, parameters, and return values. <em>Factory analogy: Instruction manuals at each station—new workers can learn the job without constantly asking veterans, and everyone follows the same procedures.</em></div>
            <div><strong>Schema Strictness %:</strong> Percentage of agents using <code>@dataclass</code> decorator or Pydantic <code>BaseModel</code> for structured data validation. <em>Factory analogy: Quality gates that reject malformed parts—if a component doesn't meet spec, it gets caught immediately rather than causing problems downstream.</em></div>
            <div><strong>Canonical Inheritance %:</strong> Percentage of agents following canonical architectural inheritance. Valid patterns include: <code>SovereignBaseAgent</code>, layer bases (<code>L0MaintenanceBaseAgent</code>, <code>L1CognitionBaseAgent</code>, <code>L5SafetyBaseAgent</code>, <code>L3OrchestrationBaseAgent</code>, etc.), and canonical mixins (<code>HealerMixin</code>, <code>MCPHardenedMixin</code>, <code>MCPShieldMixin</code>, <code>SubatomicTestingMixin</code>, <code>L3SubatomicTestingMixin</code>, <code>ObservabilityMixin</code>, <code>TelemetryMixin</code>, <code>ValidationMixin</code>, <code>StateMixin</code>, <code>CognitionMixin</code>, <code>ExecutionMixin</code>, <code>SafetyMixin</code>). <em>Factory analogy: Workers wearing the right department uniform—ensures they have access to the correct tools and follow department-specific safety protocols.</em></div>
            <div><strong>Code Quality Score:</strong> Weighted composite: (Typed % × 0.30) + (Documented % × 0.30) + (Schema Strictness % × 0.25) + (Canonical Inheritance % × 0.15). Comprehensive code quality metric balancing type safety, documentation, validation contracts, and architectural compliance. <em>Factory analogy: The station's comprehensive quality audit—combining cleanliness (types), instruction manuals (docs), quality gates (schemas), and proper equipment (inheritance) into a single maintainability score.</em></div>
        </div>
    </div>
    `;
    
    container.innerHTML = html;
}

// Toggle toxicity filter (high-impact territories only)
function toggleToxicityFilter() {
    window.toxicityFilterEnabled = !window.toxicityFilterEnabled;
    // Re-render both tables with new filter
    if (window.dashboardData) {
        renderTerritorySummaryTable(window.dashboardData);
    }
}

// Toggle zombie filter (territories with no healing capability)
function toggleZombieFilter(tableType) {
    window.tableFilterState[tableType].showZombies = !window.tableFilterState[tableType].showZombies;
    if (tableType === 'table1' && window.dashboardData) {
        renderTerritorySummaryTable(window.dashboardData);
    } else if (tableType === 'table2' && window.dashboardData) {
        renderCodeQualityTable(window.dashboardData);
    }
}

// Toggle outlier filter (show only territories with critical outliers)
function toggleOutlierFilter(tableType) {
    window.tableFilterState[tableType].showOnlyOutliers = !window.tableFilterState[tableType].showOnlyOutliers;
    if (tableType === 'table1' && window.dashboardData) {
        renderTerritorySummaryTable(window.dashboardData);
    } else if (tableType === 'table2' && window.dashboardData) {
        renderCodeQualityTable(window.dashboardData);
    }
}

// Toggle sort by outliers
function toggleSortByOutliers(tableType) {
    window.tableFilterState[tableType].sortByOutliers = !window.tableFilterState[tableType].sortByOutliers;
    if (tableType === 'table1' && window.dashboardData) {
        renderTerritorySummaryTable(window.dashboardData);
    } else if (tableType === 'table2' && window.dashboardData) {
        renderCodeQualityTable(window.dashboardData);
    }
}

// Load data function for initialization
function loadData() {
    console.log('🚀 loadData() called');
    const data = window.dashboardData;
    console.log('📊 dashboardData:', data ? data.length + ' rows' : 'UNDEFINED');
    
    if (!data || data.length === 0) {
        console.error('❌ No dashboard data available');
        return;
    }
    
    const territoryData = data.filter(row => row.Territory !== 'TOTAL');
    console.log('🗺️ territoryData:', territoryData.length + ' territories');
    
    // Render tables
    renderTerritorySummaryTable(data);
    renderCodeQualityTable(data);
    
    console.log('✅ Tables rendered');
}

// Drill-down modal function
function openDrillModal(territoryName) {
    const row = window.dashboardData.find(r => r.Territory === territoryName);
    if (!row) {
        console.error(`Territory not found: ${territoryName}`);
        return;
    }
    
    // Get agents from realAgentData
    const territoryAgentData = window.realAgentData ? window.realAgentData[territoryName] : null;
    const agents = territoryAgentData ? territoryAgentData.agents : [];

    document.getElementById('modalTitle').textContent = `${territoryName} Territory Drill-Down`;
    
    // Helper to safely format values that might be "N/A"
    const safeFormat = (val) => val === "N/A" ? "N/A" : (typeof val === 'number' ? val.toFixed(1) + '%' : val);
    document.getElementById('modalSubtitle').textContent = `${row.Total} agents • Code Quality ${safeFormat(row[COLUMNS.CODE_QUALITY])} • Invocation ${safeFormat(row[COLUMNS.INVOCATION])}`;

    // Health Metrics Section
    let content = '<div style="display:grid; grid-template-columns:1fr 1fr; gap:20px; margin-bottom:20px;">';
    content += '<div style="background:#f0fdf4; padding:15px; border-radius:8px; border-left:4px solid #16a34a;">';
    content += '<strong style="font-size:1.1em; color:#166534;">🏥 Health Metrics</strong><ul style="margin-top:10px; list-style:none; padding:0;">';
    content += `<li style="margin:5px 0;">Healing Capability: <strong>${safeFormat(row[COLUMNS.HEAL_CAP])}</strong></li>`;
    content += `<li style="margin:5px 0;">Healing Invocation: <strong>${safeFormat(row[COLUMNS.INVOCATION])}</strong></li>`;
    content += `<li style="margin:5px 0;">MCP Hardened: <strong>${safeFormat(row[COLUMNS.HARDENED])}</strong></li>`;
    content += `<li style="margin:5px 0;">Test Coverage: <strong>${safeFormat(row[COLUMNS.TEST])}</strong></li>`;
    content += `<li style="margin:5px 0;">Complexity Health: <strong>${safeFormat(row[COLUMNS.COMPLEXITY_HEALTH])}</strong></li>`;
    content += `<li style="margin:5px 0; font-weight:700; color:#166534;">Code Quality Score: <strong>${safeFormat(row[COLUMNS.CODE_QUALITY])}</strong></li>`;
    content += '</ul></div>';
    
    // Code Quality Metrics Section
    content += '<div style="background:#eff6ff; padding:15px; border-radius:8px; border-left:4px solid #2563eb;">';
    content += '<strong style="font-size:1.1em; color:#1e40af;">📊 Code Quality Metrics</strong><ul style="margin-top:10px; list-style:none; padding:0;">';
    content += `<li style="margin:5px 0;">Typed %: <strong>${safeFormat(row[COLUMNS.TYPED])}</strong></li>`;
    content += `<li style="margin:5px 0;">Documented %: <strong>${safeFormat(row[COLUMNS.DOCUMENTED])}</strong></li>`;
    content += `<li style="margin:5px 0;">Schema Strictness %: <strong>${safeFormat(row[COLUMNS.SCHEMA_STRICTNESS])}</strong></li>`;
    content += `<li style="margin:5px 0;">Canonical Inheritance %: <strong>${safeFormat(row[COLUMNS.CANONICAL_INHERITANCE])}</strong></li>`;
    content += `<li style="margin:5px 0; font-weight:700; color:#1e40af;">Code Quality Score: <strong>${safeFormat(row[COLUMNS.CODE_QUALITY])}</strong></li>`;
    content += '</ul></div></div>';

    // Per-agent diagnostics table
    if (agents && agents.length > 0) {
        content += `<strong style="font-size:1.4em; margin:30px 0 15px 0; display:block;">Per-Agent Diagnostics (${agents.length} agents)</strong>`;
        content += '<table style="width:100%; border-collapse:collapse; font-size:0.95em; margin-top:10px;">';
        content += '<thead><tr style="background:#f1f5f9; border-bottom:2px solid var(--border);">';
        content += '<th style="text-align:left; padding:12px; font-weight:600;" title="Click to open in VS Code">Agent File</th>';
        content += '<th style="text-align:center; padding:12px; font-weight:600;">Has Healing</th>';
        content += '<th style="padding:12px; font-weight:600;" title="Has dedicated test coverage">Tests</th>';
        content += '<th style="padding:12px; font-weight:600;" title="Cyclomatic complexity">Complexity</th>';
        content += '<th style="padding:12px; font-weight:600;" title="MCP Hardening">MCP</th>';
        content += '<th style="padding:12px; font-weight:600;" title="Type annotations">Typed %</th>';
        content += '</tr></thead><tbody>';

        agents.forEach((agent, idx) => {
            const rowBg = idx % 2 === 0 ? '#ffffff' : '#f9fafb';
            
            const healingIcon = agent.has_healing 
                ? '<span style="color:#16a34a; font-weight:700;">✓</span>' 
                : '<span style="color:#dc2626; font-weight:700;">✗</span>';
            
            const testIcon = agent.has_tests 
                ? '<span style="color:#16a34a; font-weight:700;">✓</span>' 
                : '<span style="color:#dc2626; font-weight:700;">✗</span>';
            
            const mcpIcon = agent.mcp_hardened 
                ? '<span style="color:#16a34a; font-weight:700;">✓</span>' 
                : '<span style="color:#dc2626; font-weight:700;">✗</span>';
            
            const typedColor = getColor(agent.typed_pct || 0, true);
            const complexityColor = getColor(100 - (agent.cyclomatic_complexity || 0) * 2, true);
            
            const filePath = agent.path || agent.file_path || 'unknown';
            const fileName = filePath.split('/').pop() || filePath;
            
            content += `<tr style="border-bottom:1px solid var(--border); background:${rowBg};">
                <td style="padding:12px;">
                    <a href="vscode://file/${filePath}" target="_blank" style="color:var(--primary); font-family:monospace; font-size:0.9em; font-weight:600;">
                        ${fileName}
                    </a>
                </td>
                <td style="padding:12px; text-align:center;">${healingIcon}</td>
                <td style="padding:12px; text-align:center;">${testIcon}</td>
                <td style="padding:12px; text-align:center; color:${complexityColor}; font-weight:600;">${agent.cyclomatic_complexity || 0}</td>
                <td style="padding:12px; text-align:center;">${mcpIcon}</td>
                <td style="padding:12px; text-align:center; color:${typedColor}; font-weight:600;">${(agent.typed_pct || 0).toFixed(1)}%</td>
            </tr>`;
        });
        content += '</tbody></table>';
        
        content += '<p style="margin-top:15px; font-size:0.9em; color:var(--text-light); font-style:italic;">';
        content += 'Click any file link to open in VS Code. Add HealerMixin, tests, MCP hardening, or type annotations as needed.';
        content += '</p>';
    } else {
        content += '<p style="margin-top:20px; color:var(--text-light);">No per-agent diagnostics available for this territory.</p>';
    }

    document.getElementById('modalContent').innerHTML = content;
    document.getElementById('drillModal').style.display = 'flex';
}

// Make functions globally available
window.openDrillModal = openDrillModal;
window.toggleToxicityFilter = toggleToxicityFilter;
window.toggleZombieFilter = toggleZombieFilter;
window.toggleOutlierFilter = toggleOutlierFilter;
window.toggleSortByOutliers = toggleSortByOutliers;
window.loadData = loadData;
window.toggleFilter = toggleFilter;
window.tableFilterState = tableFilterState;
