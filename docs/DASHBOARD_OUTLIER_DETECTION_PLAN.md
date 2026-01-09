# Dashboard Outlier Detection Implementation Plan

## Problem Statement

The current Autonomy Dashboard uses **simple averages** for all metrics, which can **hide critical outliers**:

| Scenario | Average | Reality |
|----------|---------|---------|
| 10 agents: 9 at 100%, 1 at 0% | **90%** ✅ | 1 agent completely broken |
| 5 agents: 4 at 95%, 1 at 15% | **79%** ⚠️ | 1 severe outlier masked |
| 20 agents: 19 at 85%, 1 at 5% | **81%** ✅ | Critical gap hidden |

**Impact**: A territory can appear "green" while containing agents with zero test coverage, zero healing, or extreme complexity.

---

## Solution Architecture

### Tables Covered

Both tables will be enhanced **in parallel** during each phase:

| Table | Purpose | Metrics |
|-------|---------|---------|
| **Table 1: Territory Summary** | Health & Autonomy Metrics | Heal Cap %, Heal Invocation %, MCP Hardened %, Test %, Complexity Health %, Health Score |
| **Table 2: Code Quality** | Code Hygiene Metrics | Typed %, Documented %, Schema Strictness %, Proper Base %, Code Quality Score |

### New Columns to Add

#### Table 1: Territory Summary (Health Metrics)
| Current Columns | New Columns to Add |
|-----------------|-------------------|
| Territory | — |
| # Agents | — |
| Heal Capability % | **Min/Max/σ**, **# at 0%**, **Worst Agent** |
| Heal Invocation % | **Min/Max/σ**, **# at 0%**, **Worst Agent** |
| MCP Hardened % | **Min/Max/σ**, **# at 0%**, **Worst Agent** |
| Test Coverage % | **Min/Max/σ**, **# at 0%**, **Worst Agent** |
| Complexity Health % | **Min/Max/σ**, **# Critical (CC>30)**, **Worst Agent** |
| Health Score | **Min/Max/σ**, **# Below 50%**, **Worst Agent** |

#### Table 2: Code Quality Table
| Current Columns | New Columns to Add |
|-----------------|-------------------|
| Territory | — |
| # Agents | — |
| Typed % | **Min/Max/σ**, **# at 0%**, **Worst Agent** |
| Documented % | **Min/Max/σ**, **# at 0%**, **Worst Agent** |
| Schema Strictness % | **Min/Max/σ**, **# Below 80%**, **Worst Agent** |
| Proper Base % | **Min/Max/σ**, **# at 0%**, **Worst Agent** |
| Code Quality Score | **Min/Max/σ**, **# Below 60%**, **Worst Agent** |

---

## Implementation Phases

> **IMPORTANT**: Each phase applies to **BOTH Table 1 AND Table 2** simultaneously.

---

### Phase 1: Distribution Statistics (Foundation)
**Goal**: Add Min/Max/Std Dev to expose value ranges in BOTH tables

#### Shared Helper Function
```javascript
function computeDistributionStats(values) {
    if (!values || values.length === 0) return { min: 0, max: 0, avg: 0, stdDev: 0, range: 0 };
    const min = Math.min(...values);
    const max = Math.max(...values);
    const avg = values.reduce((a, b) => a + b, 0) / values.length;
    const variance = values.reduce((sum, v) => sum + Math.pow(v - avg, 2), 0) / values.length;
    const stdDev = Math.sqrt(variance);
    return { min, max, avg, stdDev, range: max - min };
}

function formatDistributionCell(avg, stats, showStdDev = true) {
    if (!stats || stats.min === stats.max) return `${avg.toFixed(1)}%`;
    const rangeStr = `${stats.min.toFixed(0)}-${stats.max.toFixed(0)}`;
    if (showStdDev && stats.stdDev > 0) {
        return `${avg.toFixed(1)}% <span style="font-size:0.8em; color:#6b7280;">(${rangeStr}, σ=${stats.stdDev.toFixed(1)})</span>`;
    }
    return `${avg.toFixed(1)}% <span style="font-size:0.8em; color:#6b7280;">(${rangeStr})</span>`;
}

function getWorstCaseColor(minValue) {
    if (minValue >= 85) return '#065f46';  // Dark green
    if (minValue >= 75) return '#047857';  // Green
    if (minValue >= 60) return '#65a30d';  // Yellow-green
    if (minValue >= 40) return '#a16207';  // Orange
    if (minValue >= 20) return '#c2410c';  // Red-orange
    return '#991b1b';  // Dark red
}
```

#### Table 1 Columns to Enhance
| Column | Display Format | Color Logic |
|--------|---------------|-------------|
| Heal Capability % | `86.6% (0-100, σ=23.9)` | Based on Min |
| Heal Invocation % | `91.7% (67-100, σ=8.1)` | Based on Min |
| MCP Hardened % | `73.9% (0-100, σ=30.0)` | Based on Min |
| Test Coverage % | `75.0% (0-100, σ=22.7)` | Based on Min |
| Complexity Health % | `34.3% (1-95, σ=20.3)` | Based on Min |
| Health Score | `76.9% (55-95, σ=7.7)` | Based on Min |

#### Table 2 Columns to Enhance
| Column | Display Format | Color Logic |
|--------|---------------|-------------|
| Typed % | `87.1% (50-100, σ=12.3)` | Based on Min |
| Documented % | `88.5% (45-100, σ=15.2)` | Based on Min |
| Schema Strictness % | `94.2% (55-100, σ=11.8)` | Based on Min |
| Proper Base % | `99.1% (90-100, σ=3.2)` | Based on Min |
| Code Quality Score | `93.5% (60-100, σ=9.4)` | Based on Min |

#### Completion Criteria - Phase 1
- [ ] `computeDistributionStats()` function implemented
- [ ] `formatDistributionCell()` function implemented
- [ ] `getWorstCaseColor()` function implemented
- [ ] **Table 1**: All 6 metric columns show Min/Max/σ format
- [ ] **Table 2**: All 5 metric columns show Min/Max/σ format
- [ ] TOTAL rows in both tables show aggregated distribution stats
- [ ] Color coding uses Min value (worst case) for gradient in both tables
- [ ] Sparklines still functional in TOTAL row

#### Test Cases - Phase 1
| Test | Input | Expected Output |
|------|-------|-----------------|
| TC1.1 | [100, 100, 100] | min=100, max=100, σ=0, display="100.0%" |
| TC1.2 | [0, 50, 100] | min=0, max=100, σ=40.8, display="50.0% (0-100, σ=40.8)" |
| TC1.3 | [90, 92, 88, 91] | min=88, max=92, σ≈1.5 |
| TC1.4 | Empty array | min=0, max=0, σ=0 |
| TC1.5 | [0] | min=0, max=0, σ=0, display="0.0%" |
| TC1.6 | Color for min=0 | Returns '#991b1b' (dark red) |
| TC1.7 | Color for min=85 | Returns '#065f46' (dark green) |

---

### Phase 2: Outlier Flagging (Critical Gaps)
**Goal**: Add outlier count badges to BOTH tables showing agents at critical thresholds

#### Shared Helper Function
```javascript
function countOutliers(values, threshold, comparison = 'below') {
    if (!values || values.length === 0) return 0;
    if (comparison === 'below') return values.filter(v => v < threshold).length;
    if (comparison === 'above') return values.filter(v => v > threshold).length;
    if (comparison === 'equals') return values.filter(v => v === threshold).length;
    return 0;
}

function formatOutlierBadge(count, label = 'at 0%') {
    if (count === 0) return '';
    return `<span style="background:#dc2626; color:white; padding:2px 6px; border-radius:4px; font-size:0.75em; margin-left:4px;">${count} ${label}</span>`;
}
```

#### Table 1 Outlier Thresholds
| Metric | Outlier Label | Threshold | Comparison |
|--------|--------------|-----------|------------|
| Heal Capability % | `# at 0%` | 0 | equals |
| Heal Invocation % | `# at 0%` | 0 | equals |
| MCP Hardened % | `# at 0%` | 0 | equals |
| Test Coverage % | `# at 0%` | 0 | equals |
| Complexity Health % | `# Critical` | 30 | above (CC>30) |
| Health Score | `# <50%` | 50 | below |

#### Table 2 Outlier Thresholds
| Metric | Outlier Label | Threshold | Comparison |
|--------|--------------|-----------|------------|
| Typed % | `# at 0%` | 0 | equals |
| Documented % | `# at 0%` | 0 | equals |
| Schema Strictness % | `# <80%` | 80 | below |
| Proper Base % | `# at 0%` | 0 | equals |
| Code Quality Score | `# <60%` | 60 | below |

#### Cell Display Format
```
75.2% (45-100, σ=18.3) [3 at 0%]
```
- Red badge appears only if count > 0
- Tooltip shows which agents are outliers

#### Completion Criteria - Phase 2
- [ ] `countOutliers()` function implemented
- [ ] `formatOutlierBadge()` function implemented
- [ ] **Table 1**: All 6 columns show outlier badges when applicable
- [ ] **Table 2**: All 5 columns show outlier badges when applicable
- [ ] Red highlighting when outlier count > 0
- [ ] Tooltip lists outlier agent names on hover

#### Test Cases - Phase 2
| Test | Input | Threshold | Expected |
|------|-------|-----------|----------|
| TC2.1 | [0, 50, 100, 0] | 0 (equals) | 2 |
| TC2.2 | [80, 90, 45, 30] | 50 (below) | 2 |
| TC2.3 | [10, 15, 35, 40] | 30 (above) | 2 |
| TC2.4 | [100, 100, 100] | 0 (equals) | 0 (no badge) |
| TC2.5 | [] | any | 0 |
| TC2.6 | Badge for count=3 | — | Red badge "3 at 0%" |

---

### Phase 3: Worst Performer Column
**Goal**: Show the single worst agent per territory in BOTH tables for immediate action

#### Shared Helper Function
```javascript
function findWorstPerformer(agents, metricKey, lowerIsBetter = false) {
    if (!agents || agents.length === 0) return null;
    return agents.reduce((worst, agent) => {
        const currentVal = parseFloat(agent[metricKey]) || 0;
        const worstVal = parseFloat(worst[metricKey]) || 0;
        if (lowerIsBetter) {
            return currentVal > worstVal ? agent : worst;
        }
        return currentVal < worstVal ? agent : worst;
    }, agents[0]);
}

function formatWorstPerformerLink(agent, value, metricName) {
    if (!agent) return '—';
    const isCritical = value < 50;
    const bgColor = isCritical ? 'rgba(220, 38, 38, 0.1)' : 'transparent';
    return `<a href="vscode://file/${agent.path}" style="color:var(--primary); text-decoration:none; background:${bgColor}; padding:2px 4px; border-radius:4px;" title="Open in VS Code">${agent.name} (${value.toFixed(0)}%)</a>`;
}
```

#### Table 1 Worst Performer Metrics
| Metric | Lower is Better? | Critical Threshold |
|--------|-----------------|-------------------|
| Heal Capability % | No | < 50% |
| Heal Invocation % | No | < 50% |
| MCP Hardened % | No | < 50% |
| Test Coverage % | No | < 50% |
| Complexity Health % | No | < 30% |
| Health Score | No | < 50% |

#### Table 2 Worst Performer Metrics
| Metric | Lower is Better? | Critical Threshold |
|--------|-----------------|-------------------|
| Typed % | No | < 50% |
| Documented % | No | < 50% |
| Schema Strictness % | No | < 80% |
| Proper Base % | No | < 50% |
| Code Quality Score | No | < 60% |

#### Display Format
```
AgentName.py (12%)
```
- Clickable link opens VS Code at file
- Red background if below critical threshold
- Tooltip shows full path

#### Completion Criteria - Phase 3
- [ ] `findWorstPerformer()` function implemented
- [ ] `formatWorstPerformerLink()` function implemented
- [ ] **Table 1**: Worst Agent shown for each metric column
- [ ] **Table 2**: Worst Agent shown for each metric column
- [ ] VS Code links functional
- [ ] Critical threshold highlighting (red background)

#### Test Cases - Phase 3
| Test | Agents | Metric | Expected Worst |
|------|--------|--------|----------------|
| TC3.1 | [{name: 'A', health: 90}, {name: 'B', health: 20}] | health | B (20%) |
| TC3.2 | [{name: 'A', cc: 10}, {name: 'B', cc: 50}] | cc (lower better) | B (50) |
| TC3.3 | Single agent | any | That agent |
| TC3.4 | Empty | any | null → "—" |
| TC3.5 | Agent at 12% | — | Red background |

---

### Phase 4: Visual Enhancements
**Goal**: Make outliers immediately visible through visual design in BOTH tables

#### Enhancements for Both Tables
1. **Heatmap Intensity**: Color cells by worst value (Min), not average
2. **Warning Icons**: ⚠️ icon in row header when any outlier exists
3. **Row Highlighting**: Subtle red tint on rows with critical outliers
4. **Expandable Rows**: Click territory to see all agents with their individual values

#### New Component: Outlier Alert Banner (Above Both Tables)
```html
<div class="outlier-alert-banner">
    <h4>⚠️ Critical Outliers Detected</h4>
    <div class="alert-columns">
        <div class="health-alerts">
            <h5>Health Metrics (Table 1)</h5>
            <ul>
                <li>L1 Cognition: 3 agents at 0% test coverage</li>
                <li>Apps Lic: 2 agents with CC > 50</li>
            </ul>
        </div>
        <div class="quality-alerts">
            <h5>Code Quality (Table 2)</h5>
            <ul>
                <li>L5 Safety: 2 agents at 0% typed</li>
                <li>Apps Rg: 1 agent below 60% quality score</li>
            </ul>
        </div>
    </div>
</div>
```

#### Completion Criteria - Phase 4
- [ ] Outlier alert banner implemented (covers both tables)
- [ ] Heatmap uses worst-case coloring in both tables
- [ ] Warning icons on rows with outliers in both tables
- [ ] Row highlighting for critical outliers
- [ ] Expandable row detail view for both tables

#### Test Cases - Phase 4
| Test | Scenario | Expected |
|------|----------|----------|
| TC4.1 | No outliers in either table | Banner hidden |
| TC4.2 | 1 outlier in Table 1 only | Banner shows Table 1 section only |
| TC4.3 | Outliers in both tables | Banner shows both sections |
| TC4.4 | Click territory row | Expands to show agent details |
| TC4.5 | Row with 3 outliers | ⚠️ icon + red tint |

---

### Phase 5: Interactive Drill-down
**Goal**: Enable deep exploration of outliers in BOTH tables

#### Features for Both Tables
1. **Click-to-Expand**: Click any cell to see per-agent breakdown
2. **Sort by Outliers**: Sort territories by outlier count
3. **Filter by Threshold**: Show only territories with outliers
4. **Export Outliers**: Download CSV of all outliers for batch fixing

#### Drill-down Modal Content
```html
<div class="drill-modal">
    <h3>L5 Safety/Validators - Test Coverage Details</h3>
    <p>Average: 72.2% | Min: 0% | Max: 100% | σ: 35.2</p>
    <table>
        <tr><th>Agent</th><th>Value</th><th>Status</th><th>Action</th></tr>
        <tr class="critical"><td>BrokenValidator.py</td><td>0%</td><td>🔴 Critical</td><td><a href="vscode://...">Fix</a></td></tr>
        <tr class="warning"><td>WeakAgent.py</td><td>25%</td><td>🟡 Warning</td><td><a href="vscode://...">Fix</a></td></tr>
        <tr class="ok"><td>GoodAgent.py</td><td>100%</td><td>🟢 OK</td><td>—</td></tr>
    </table>
</div>
```

#### Shared Helper Function
```javascript
function aggregateOutlierAlerts(territoryData, table = 'both') {
    const alerts = { table1: [], table2: [] };
    
    territoryData.forEach(territory => {
        if (!territory.agents) return;
        
        // Table 1 metrics
        if (table === 'both' || table === 'table1') {
            const testZeros = territory.agents.filter(a => (a.test_pct || 0) === 0);
            if (testZeros.length > 0) {
                alerts.table1.push({
                    territory: territory.Territory,
                    metric: 'Test Coverage',
                    count: testZeros.length,
                    severity: 'critical',
                    agents: testZeros.map(a => a.name)
                });
            }
            // ... similar for Heal Cap, Heal Inv, MCP, Complexity, Health
        }
        
        // Table 2 metrics
        if (table === 'both' || table === 'table2') {
            const typedZeros = territory.agents.filter(a => (a.typed_pct || 0) === 0);
            if (typedZeros.length > 0) {
                alerts.table2.push({
                    territory: territory.Territory,
                    metric: 'Typed %',
                    count: typedZeros.length,
                    severity: 'critical',
                    agents: typedZeros.map(a => a.name)
                });
            }
            // ... similar for Documented, Schema, Proper Base, Quality Score
        }
    });
    
    alerts.table1.sort((a, b) => b.count - a.count);
    alerts.table2.sort((a, b) => b.count - a.count);
    return alerts;
}
```

#### Completion Criteria - Phase 5
- [ ] Click-to-expand drill-down modal for both tables
- [ ] Per-agent breakdown with status icons
- [ ] Sort territories by outlier count
- [ ] Filter to show only territories with outliers
- [ ] Export outliers to CSV
- [ ] VS Code links in drill-down modal

#### Test Cases - Phase 5
| Test | Scenario | Expected |
|------|----------|----------|
| TC5.1 | Click Table 1 cell | Opens drill-down with health metrics |
| TC5.2 | Click Table 2 cell | Opens drill-down with quality metrics |
| TC5.3 | Sort by outliers | Territories with most outliers first |
| TC5.4 | Filter outliers only | Hides territories with 0 outliers |
| TC5.5 | Export CSV | Downloads file with all outlier agents |

---

## Data Model Changes

### Current Data Structure
```javascript
{
    "Territory": "L5 Safety/Validators",
    "Total": 18,
    "Heal Cap %": 72.2,      // Average only
    "Test %": 72.2,          // Average only
    "Health": 72.4,          // Average only
    "Typed %": 85.3,         // Average only
    "Code Quality Score": 91.2  // Average only
}
```

### Enhanced Data Structure
```javascript
{
    "Territory": "L5 Safety/Validators",
    "Total": 18,
    
    // Table 1 Metrics (with distribution)
    "Heal Cap %": 72.2,
    "Heal Cap Min": 0, "Heal Cap Max": 100, "Heal Cap StdDev": 28.5,
    "Heal Cap Zeros": 2, "Heal Cap Worst": "BrokenValidator.py",
    
    "Test %": 72.2,
    "Test Min": 0, "Test Max": 100, "Test StdDev": 35.2,
    "Test Zeros": 3, "Test Worst": "UntestableAgent.py",
    
    // Table 2 Metrics (with distribution)
    "Typed %": 85.3,
    "Typed Min": 50, "Typed Max": 100, "Typed StdDev": 12.3,
    "Typed Zeros": 0, "Typed Worst": "LegacyAgent.py",
    
    "Code Quality Score": 91.2,
    "Quality Min": 60, "Quality Max": 100, "Quality StdDev": 9.4,
    "Quality Below60": 1, "Quality Worst": "OldAgent.py",
    
    // Per-agent data for drill-down
    "agents": [
        { 
            "name": "ValidatorA.py", 
            "path": "agentic_core/L5_safety/validators/ValidatorA.py",
            "heal_cap": 100, "test": 100, "health": 95,
            "typed": 92, "documented": 88, "quality": 94
        },
        { 
            "name": "BrokenValidator.py",
            "path": "agentic_core/L5_safety/validators/BrokenValidator.py",
            "heal_cap": 0, "test": 0, "health": 25,
            "typed": 50, "documented": 30, "quality": 45
        }
    ]
}
```

---

## Implementation Timeline

| Phase | Scope | Effort | Dependencies | Priority |
|-------|-------|--------|--------------|----------|
| Phase 1 | Distribution Stats (Table 1 + Table 2) | 3-4 hours | None | P0 |
| Phase 2 | Outlier Flagging (Table 1 + Table 2) | 3-4 hours | Phase 1 | P0 |
| Phase 3 | Worst Performer (Table 1 + Table 2) | 3-4 hours | Phase 2 | P1 |
| Phase 4 | Visual Enhancements (Both Tables) | 3-4 hours | Phase 3 | P1 |
| Phase 5 | Interactive Drill-down (Both Tables) | 4-5 hours | Phase 4 | P2 |

**Total Estimated Effort**: 16-21 hours

---

## Success Metrics

1. **Outlier Visibility**: 100% of agents at 0% for any metric are flagged in both tables
2. **False Confidence Reduction**: No territory shows "green" if any agent is critical
3. **Actionability**: Every outlier has a direct VS Code link
4. **Consistency**: Both tables use identical formatting and interaction patterns
5. **Performance**: Dashboard load time < 2 seconds with enhanced data

---

## Rollback Plan

If issues arise:
1. Keep original average-only columns
2. Add new columns as separate "Distribution" tab
3. Feature flag to toggle between views
4. Phase-specific rollback (e.g., keep Phase 1, rollback Phase 2)

---

## Current Implementation Status

| Phase | Table 1 | Table 2 | Status |
|-------|---------|---------|--------|
| Phase 1 | ✅ Complete | ✅ Complete | **Done** |
| Phase 2 | ❌ Pending | ❌ Pending | Not Started |
| Phase 3 | ❌ Pending | ❌ Pending | Not Started |
| Phase 4 | ❌ Pending | ❌ Pending | Not Started |
| Phase 5 | ❌ Pending | ❌ Pending | Not Started |

**Next Action**: Phase 2 - Add outlier flagging (# at 0%, # below threshold) to both tables

---

## Appendix: Helper Functions Reference

```javascript
// ============================================
// PHASE 1: Distribution Statistics
// ============================================

function computeDistributionStats(values) {
    if (!values || values.length === 0) return { min: 0, max: 0, avg: 0, stdDev: 0, range: 0 };
    const min = Math.min(...values);
    const max = Math.max(...values);
    const avg = values.reduce((a, b) => a + b, 0) / values.length;
    const variance = values.reduce((sum, v) => sum + Math.pow(v - avg, 2), 0) / values.length;
    const stdDev = Math.sqrt(variance);
    return { min, max, avg, stdDev, range: max - min };
}

function formatDistributionCell(avg, stats, showStdDev = true) {
    if (!stats || stats.min === stats.max) return `${avg.toFixed(1)}%`;
    const rangeStr = `${stats.min.toFixed(0)}-${stats.max.toFixed(0)}`;
    if (showStdDev && stats.stdDev > 0) {
        return `${avg.toFixed(1)}% <span style="font-size:0.8em; color:#6b7280;">(${rangeStr}, σ=${stats.stdDev.toFixed(1)})</span>`;
    }
    return `${avg.toFixed(1)}% <span style="font-size:0.8em; color:#6b7280;">(${rangeStr})</span>`;
}

function getWorstCaseColor(minValue) {
    if (minValue >= 85) return '#065f46';
    if (minValue >= 75) return '#047857';
    if (minValue >= 60) return '#65a30d';
    if (minValue >= 40) return '#a16207';
    if (minValue >= 20) return '#c2410c';
    return '#991b1b';
}

// ============================================
// PHASE 2: Outlier Counting
// ============================================

function countOutliers(values, threshold, comparison = 'below') {
    if (!values || values.length === 0) return 0;
    if (comparison === 'below') return values.filter(v => v < threshold).length;
    if (comparison === 'above') return values.filter(v => v > threshold).length;
    if (comparison === 'equals') return values.filter(v => v === threshold).length;
    return 0;
}

function formatOutlierBadge(count, label = 'at 0%') {
    if (count === 0) return '';
    return `<span style="background:#dc2626; color:white; padding:2px 6px; border-radius:4px; font-size:0.75em; margin-left:4px;">${count} ${label}</span>`;
}

// ============================================
// PHASE 3: Worst Performer
// ============================================

function findWorstPerformer(agents, metricKey, lowerIsBetter = false) {
    if (!agents || agents.length === 0) return null;
    return agents.reduce((worst, agent) => {
        const currentVal = parseFloat(agent[metricKey]) || 0;
        const worstVal = parseFloat(worst[metricKey]) || 0;
        if (lowerIsBetter) return currentVal > worstVal ? agent : worst;
        return currentVal < worstVal ? agent : worst;
    }, agents[0]);
}

function formatWorstPerformerLink(agent, value, metricName) {
    if (!agent) return '—';
    const isCritical = value < 50;
    const bgColor = isCritical ? 'rgba(220, 38, 38, 0.1)' : 'transparent';
    return `<a href="vscode://file/${agent.path}" style="color:var(--primary); background:${bgColor}; padding:2px 4px; border-radius:4px;">${agent.name} (${value.toFixed(0)}%)</a>`;
}

// ============================================
// PHASE 5: Outlier Alert Aggregation
// ============================================

function aggregateOutlierAlerts(territoryData) {
    const alerts = { table1: [], table2: [] };
    territoryData.forEach(territory => {
        if (!territory.agents) return;
        
        // Table 1: Test coverage zeros
        const testZeros = territory.agents.filter(a => (a.test_pct || 0) === 0);
        if (testZeros.length > 0) {
            alerts.table1.push({
                territory: territory.Territory,
                metric: 'Test Coverage',
                count: testZeros.length,
                severity: 'critical',
                agents: testZeros.map(a => a.name)
            });
        }
        
        // Table 2: Typed zeros
        const typedZeros = territory.agents.filter(a => (a.typed_pct || 0) === 0);
        if (typedZeros.length > 0) {
            alerts.table2.push({
                territory: territory.Territory,
                metric: 'Typed %',
                count: typedZeros.length,
                severity: 'critical',
                agents: typedZeros.map(a => a.name)
            });
        }
    });
    
    alerts.table1.sort((a, b) => b.count - a.count);
    alerts.table2.sort((a, b) => b.count - a.count);
    return alerts;
}
```

---

## Document History

| Date | Author | Changes |
|------|--------|---------|
| 2026-01-09 | Cascade | Initial implementation plan |
| 2026-01-09 | Cascade | **REVISED**: Incorporated Table 2 into all 5 phases (was previously Phase 4 only) |
