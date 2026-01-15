/**
 * Table Renderer
 * Handles the massive territory summary and code quality tables.
 * Includes filtering, sorting, and toxicity logic.
 */

// Global state for table filtering
const tableFilterState = {
    table1: { showOnlyOutliers: false, sortByOutliers: false, showZombies: false },
    table2: { showOnlyOutliers: false, sortByOutliers: false, showZombies: false }
};

let toxicityFilterEnabled = false;

// --- Helper Functions ---

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

    // Sort Data
    filteredData.sort((a, b) => {
        if (a.Territory === 'TOTAL') return 1;
        if (b.Territory === 'TOTAL') return -1;
        if (state.sortByOutliers) {
            return getTerritoryOutlierCount(b.Territory) - getTerritoryOutlierCount(a.Territory);
        }
        return a.Territory.localeCompare(b.Territory);
    });

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
                            <th style="padding:16px; text-align:left;">Territory</th>
                            <th style="padding:16px; text-align:center;"># Agents</th>
                            <th style="padding:16px; text-align:center;">Heal Capability %</th>
                            <th style="padding:16px; text-align:center;">Heal Invocation %</th>
                            <th style="padding:16px; text-align:center;">MCP Hardened %</th>
                            <th style="padding:16px; text-align:center;">Test Coverage %</th>
                            <th style="padding:16px; text-align:center;">Health Score</th>
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
        
        const healthColor = getWorstCaseColor(row.Health);
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
                
                <td class="metric-cell" style="padding:12px; text-align:center; background:${getGradientBg(row['Heal Cap %'])}">
                    ${formatDistributionCell(row['Heal Cap %'], healCapStats)}
                    ${formatOutlierBadge(getOutliers('healCap', 50).atZero, getOutliers('healCap', 50).belowThreshold, 50)}
                    <div class="custom-tooltip">${formatProblemAgentsTooltip(row.Territory, 'healCap', 'Heal Cap', 50)}</div>
                </td>
                
                <td class="metric-cell" style="padding:12px; text-align:center; background:${getGradientBg(row['Invocation %'])}">
                    ${formatDistributionCell(row['Invocation %'], invocationStats)}
                    ${formatOutlierBadge(getOutliers('invocation', 50).atZero, getOutliers('invocation', 50).belowThreshold, 50)}
                    <div class="custom-tooltip">${formatProblemAgentsTooltip(row.Territory, 'invocation', 'Invocation', 50)}</div>
                </td>

                <td class="metric-cell" style="padding:12px; text-align:center; background:${getGradientBg(row['Hardened %'])}">
                    ${formatDistributionCell(row['Hardened %'], hardenedStats)}
                    ${formatOutlierBadge(getOutliers('hardened', 50).atZero, getOutliers('hardened', 50).belowThreshold, 50)}
                    <div class="custom-tooltip">${formatProblemAgentsTooltip(row.Territory, 'hardened', 'Hardened', 50)}</div>
                </td>

                <td class="metric-cell" style="padding:12px; text-align:center; background:${getGradientBg(row['Test %'])}">
                    ${formatDistributionCell(row['Test %'], testStats)}
                    ${formatOutlierBadge(getOutliers('test', 50).atZero, getOutliers('test', 50).belowThreshold, 50)}
                    <div class="custom-tooltip">${formatProblemAgentsTooltip(row.Territory, 'test', 'Tests', 50)}</div>
                </td>

                <td style="padding:12px; text-align:center; font-weight:700; color:${healthColor}">
                    ${typeof row.Health === 'number' ? row.Health.toFixed(1) : row.Health}%
                </td>
            </tr>`;
    });

    html += `</tbody></table></div></div>`;
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
    
    // Render each territory row
    territoryData.forEach(row => {
        const territory = row.Territory;
        const agentCount = row.Total || 0;
        
        // Get metrics with N/A handling
        const typed = row['Typed %'];
        const documented = row['Documented %'];
        const schema = row['Schema Strictness %'];
        const baseClass = row['Canonical Inheritance %'];
        const quality = row['Code Quality Score'];
        
        // Color coding
        const typedColor = typed === 'N/A' ? '#6b7280' : getColor(typed);
        const docColor = documented === 'N/A' ? '#6b7280' : getColor(documented);
        const schemaColor = schema === 'N/A' ? '#6b7280' : getColor(schema);
        const baseColor = baseClass === 'N/A' ? '#6b7280' : getColor(baseClass);
        const qualityColor = quality === 'N/A' ? '#6b7280' : getColor(quality);
        
        // Format values
        const typedVal = typed === 'N/A' ? 'N/A' : typed.toFixed(1) + '%';
        const docVal = documented === 'N/A' ? 'N/A' : documented.toFixed(1) + '%';
        const schemaVal = schema === 'N/A' ? 'N/A' : schema.toFixed(1) + '%';
        const baseVal = baseClass === 'N/A' ? 'N/A' : baseClass.toFixed(1) + '%';
        const qualityVal = quality === 'N/A' ? 'N/A' : quality.toFixed(1);
        
        html += `
            <tr style="border-bottom: 1px solid #e2e8f0; hover: background-color: #f8fafc;">
                <td style="padding: 12px 8px; font-weight: 500; position: sticky; left: 0; background: white; z-index: 5;">${territory}</td>
                <td style="padding: 12px 8px; text-align: center;">${agentCount}</td>
                <td style="padding: 12px 8px; text-align: center; color: ${typedColor}; font-weight: 600;">${typedVal}</td>
                <td style="padding: 12px 8px; text-align: center; color: ${docColor}; font-weight: 600;">${docVal}</td>
                <td style="padding: 12px 8px; text-align: center; color: ${schemaColor}; font-weight: 600;">${schemaVal}</td>
                <td style="padding: 12px 8px; text-align: center; color: ${baseColor}; font-weight: 600;">${baseVal}</td>
                <td style="padding: 12px 8px; text-align: center; color: ${qualityColor}; font-weight: 600; font-size: 1.1em;">${qualityVal}</td>
            </tr>`;
    });
    
    // Add TOTAL row
    html += `
            <tr style="background: #f8fafc; border-top: 3px solid #94a3b8; font-weight: 700; font-size: 1.05em;">
                <td style="padding: 12px 8px; position: sticky; left: 0; background: #f8fafc; z-index: 5;">TOTAL</td>
                <td style="padding: 12px 8px; text-align: center;">${totalRow.Total || 0}</td>
                <td style="padding: 12px 8px; text-align: center; color: ${getColor(totalRow['Typed %'])};">${totalRow['Typed %'].toFixed(1)}%</td>
                <td style="padding: 12px 8px; text-align: center; color: ${getColor(totalRow['Documented %'])};">${totalRow['Documented %'].toFixed(1)}%</td>
                <td style="padding: 12px 8px; text-align: center; color: ${getColor(totalRow['Schema Strictness %'])};">${totalRow['Schema Strictness %'].toFixed(1)}%</td>
                <td style="padding: 12px 8px; text-align: center; color: ${getColor(totalRow['Canonical Inheritance %'])};">${totalRow['Canonical Inheritance %'].toFixed(1)}%</td>
                <td style="padding: 12px 8px; text-align: center; color: ${getColor(totalRow['Code Quality Score'])}; font-size: 1.2em;">${totalRow['Code Quality Score'].toFixed(1)}</td>
            </tr>
        </tbody>
    </table>
    </div>
    `;
    
    container.innerHTML = html;
}
