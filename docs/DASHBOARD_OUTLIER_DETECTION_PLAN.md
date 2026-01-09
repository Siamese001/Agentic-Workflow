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

### New Columns to Add

#### Table 1: Territory Summary (Health Metrics)
| Current Columns | New Columns to Add |
|-----------------|-------------------|
| Territory | — |
| # Agents | — |
| Heal Capability % | **Min/Max**, **# at 0%**, **Worst Agent** |
| Heal Invocation % | **Min/Max**, **# at 0%**, **Worst Agent** |
| MCP Hardened % | **Min/Max**, **# at 0%**, **Worst Agent** |
| Test Coverage % | **Min/Max**, **# at 0%**, **Worst Agent** |
| Complexity Health % | **Min/Max**, **# Critical (CC>30)**, **Worst Agent** |
| Health Score | **Min/Max**, **Std Dev**, **# Below 50%** |

#### Table 2: Code Quality Table
| Current Columns | New Columns to Add |
|-----------------|-------------------|
| Territory | — |
| # Agents | — |
| Typed % | **Min/Max**, **# at 0%** |
| Documented % | **Min/Max**, **# at 0%** |
| Schema Strictness % | **Min/Max**, **# Below 80%** |
| Proper Base % | **Min/Max**, **# at 0%** |
| Code Quality Score | **Min/Max**, **Std Dev**, **# Below 60%** |

---

## Implementation Phases

### Phase 1: Distribution Statistics (Foundation)
**Goal**: Add Min/Max/Std Dev columns to expose value ranges

#### Table 1 Changes
```javascript
// New helper function
function computeDistributionStats(values) {
    if (!values || values.length === 0) return { min: 0, max: 0, avg: 0, stdDev: 0 };
    const min = Math.min(...values);
    const max = Math.max(...values);
    const avg = values.reduce((a, b) => a + b, 0) / values.length;
    const variance = values.reduce((sum, v) => sum + Math.pow(v - avg, 2), 0) / values.length;
    const stdDev = Math.sqrt(variance);
    return { min, max, avg, stdDev };
}
```

#### New Column Headers (Table 1)
```html
<th title="Min-Max range showing distribution spread">Range</th>
<th title="Standard deviation - higher = more variance">σ (Spread)</th>
```

#### Cell Display Format
```
75.2% (45-100, σ=18.3)
```
- Main value: Average
- Parentheses: Min-Max range, standard deviation
- Color: Based on Min value (worst case), not average

#### Completion Criteria - Phase 1
- [ ] `computeDistributionStats()` function implemented
- [ ] Range column added to Table 1 for Health Score
- [ ] Std Dev displayed in TOTAL row
- [ ] Color coding uses Min value for gradient (worst-case coloring)

#### Test Cases - Phase 1
| Test | Input | Expected Output |
|------|-------|-----------------|
| TC1.1 | [100, 100, 100] | min=100, max=100, σ=0 |
| TC1.2 | [0, 50, 100] | min=0, max=100, σ=40.8 |
| TC1.3 | [90, 92, 88, 91] | min=88, max=92, σ≈1.5 |
| TC1.4 | Empty array | min=0, max=0, σ=0 |
| TC1.5 | [0] | min=0, max=0, σ=0 |

---

### Phase 2: Outlier Flagging (Critical Gaps)
**Goal**: Add columns showing count of agents at critical thresholds

#### New Columns for Table 1
| Metric | Outlier Column | Threshold |
|--------|---------------|-----------|
| Heal Capability % | `# at 0%` | = 0 |
| Heal Invocation % | `# at 0%` | = 0 |
| MCP Hardened % | `# at 0%` | = 0 |
| Test Coverage % | `# at 0%` | = 0 |
| Complexity Health % | `# Critical` | CC > 30 |
| Health Score | `# Below 50%` | < 50 |

#### Helper Function
```javascript
function countOutliers(values, threshold, comparison = 'below') {
    if (!values || values.length === 0) return 0;
    if (comparison === 'below') return values.filter(v => v < threshold).length;
    if (comparison === 'above') return values.filter(v => v > threshold).length;
    if (comparison === 'equals') return values.filter(v => v === threshold).length;
    return 0;
}
```

#### Cell Display Format
```
75.2% (3 at 0%)
```
- Red badge if count > 0
- Tooltip shows which agents are outliers

#### Completion Criteria - Phase 2
- [ ] `countOutliers()` function implemented
- [ ] Outlier count badge added to each metric column
- [ ] Red highlighting when outlier count > 0
- [ ] Tooltip lists outlier agent names

#### Test Cases - Phase 2
| Test | Input | Threshold | Expected |
|------|-------|-----------|----------|
| TC2.1 | [0, 50, 100, 0] | 0 (equals) | 2 |
| TC2.2 | [80, 90, 45, 30] | 50 (below) | 2 |
| TC2.3 | [10, 15, 35, 40] | 30 (above) | 2 |
| TC2.4 | [100, 100, 100] | 0 (equals) | 0 |
| TC2.5 | [] | any | 0 |

---

### Phase 3: Worst Performer Column
**Goal**: Show the single worst agent per territory for immediate action

#### New Column: "Worst Agent"
Display format:
```
AgentName.py (12%)
```
- Clickable link to VS Code
- Shows agent with lowest value for that metric
- Red background if below critical threshold

#### Helper Function
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
```

#### Completion Criteria - Phase 3
- [ ] `findWorstPerformer()` function implemented
- [ ] Worst Agent column added to Table 1
- [ ] VS Code link functional
- [ ] Critical threshold highlighting applied

#### Test Cases - Phase 3
| Test | Agents | Metric | Expected Worst |
|------|--------|--------|----------------|
| TC3.1 | [{name: 'A', health: 90}, {name: 'B', health: 20}] | health | B (20%) |
| TC3.2 | [{name: 'A', cc: 10}, {name: 'B', cc: 50}] | cc (lower better) | B (50) |
| TC3.3 | Single agent | any | That agent |
| TC3.4 | Empty | any | null |

---

### Phase 4: Apply to Table 2 (Code Quality)
**Goal**: Mirror Phase 1-3 enhancements to Code Quality table

#### Columns to Enhance
| Metric | Distribution | Outlier Count | Worst Agent |
|--------|-------------|---------------|-------------|
| Typed % | Min/Max/σ | # at 0% | ✓ |
| Documented % | Min/Max/σ | # at 0% | ✓ |
| Schema Strictness % | Min/Max/σ | # Below 80% | ✓ |
| Proper Base % | Min/Max/σ | # at 0% | ✓ |
| Code Quality Score | Min/Max/σ | # Below 60% | ✓ |

#### Completion Criteria - Phase 4
- [ ] All Phase 1-3 functions reused for Table 2
- [ ] Distribution stats added to all Code Quality columns
- [ ] Outlier counts with appropriate thresholds
- [ ] Worst performer links functional

#### Test Cases - Phase 4
| Test | Scenario | Expected |
|------|----------|----------|
| TC4.1 | Territory with 0% typed agent | Shows "1 at 0%" badge |
| TC4.2 | All agents 100% documented | No outlier badge |
| TC4.3 | Schema strictness 50% agent | Shows in worst performer |

---

### Phase 5: Visual Enhancements
**Goal**: Make outliers immediately visible through visual design

#### Enhancements
1. **Heatmap Intensity**: Color cells by worst value, not average
2. **Warning Icons**: ⚠️ badge when outliers exist
3. **Expandable Rows**: Click to see all outliers for that territory
4. **Outlier Summary Card**: Top of dashboard showing critical outliers across all territories

#### New Component: Outlier Alert Banner
```html
<div class="outlier-alert-banner">
    <h4>⚠️ Critical Outliers Detected</h4>
    <ul>
        <li>L1 Cognition: 3 agents at 0% test coverage</li>
        <li>Apps Lic: 2 agents with CC > 50</li>
        <li>L5 Safety: 1 agent at 0% healing</li>
    </ul>
</div>
```

#### Completion Criteria - Phase 5
- [ ] Outlier alert banner implemented
- [ ] Heatmap uses worst-case coloring
- [ ] Warning icons on rows with outliers
- [ ] Expandable row detail view

#### Test Cases - Phase 5
| Test | Scenario | Expected |
|------|----------|----------|
| TC5.1 | No outliers | Banner hidden |
| TC5.2 | 1 outlier | Banner shows with 1 item |
| TC5.3 | Multiple outliers | Banner shows sorted by severity |

---

## Data Model Changes

### Current Data Structure
```javascript
{
    "Territory": "L5 Safety/Validators",
    "Total": 18,
    "Heal Cap %": 72.2,  // Average only
    "Test %": 72.2,      // Average only
    "Health": 72.4       // Average only
}
```

### Enhanced Data Structure
```javascript
{
    "Territory": "L5 Safety/Validators",
    "Total": 18,
    "Heal Cap %": 72.2,
    "Heal Cap Min": 0,
    "Heal Cap Max": 100,
    "Heal Cap StdDev": 28.5,
    "Heal Cap Zeros": 2,
    "Heal Cap Worst": "BrokenValidator.py",
    "Test %": 72.2,
    "Test Min": 0,
    "Test Max": 100,
    "Test StdDev": 35.2,
    "Test Zeros": 3,
    "Test Worst": "UntestableAgent.py",
    // ... similar for all metrics
    "agents": [
        { "name": "ValidatorA", "heal_cap": 100, "test": 100, ... },
        { "name": "BrokenValidator", "heal_cap": 0, "test": 0, ... }
    ]
}
```

---

## Implementation Timeline

| Phase | Effort | Dependencies | Priority |
|-------|--------|--------------|----------|
| Phase 1 | 2-3 hours | None | P0 |
| Phase 2 | 2-3 hours | Phase 1 | P0 |
| Phase 3 | 2-3 hours | Phase 2 | P1 |
| Phase 4 | 2-3 hours | Phase 1-3 | P1 |
| Phase 5 | 3-4 hours | Phase 1-4 | P2 |

**Total Estimated Effort**: 11-16 hours

---

## Success Metrics

1. **Outlier Visibility**: 100% of agents at 0% for any metric are flagged
2. **False Confidence Reduction**: No territory shows "green" if any agent is critical
3. **Actionability**: Every outlier has a direct VS Code link
4. **Performance**: Dashboard load time < 2 seconds with enhanced data

---

## Rollback Plan

If issues arise:
1. Keep original average-only columns
2. Add new columns as separate "Distribution" tab
3. Feature flag to toggle between views

---

## Appendix: Helper Functions Reference

```javascript
// Phase 1: Distribution Statistics
function computeDistributionStats(values) {
    if (!values || values.length === 0) return { min: 0, max: 0, avg: 0, stdDev: 0 };
    const min = Math.min(...values);
    const max = Math.max(...values);
    const avg = values.reduce((a, b) => a + b, 0) / values.length;
    const variance = values.reduce((sum, v) => sum + Math.pow(v - avg, 2), 0) / values.length;
    const stdDev = Math.sqrt(variance);
    return { min, max, avg, stdDev };
}

// Phase 2: Outlier Counting
function countOutliers(values, threshold, comparison = 'below') {
    if (!values || values.length === 0) return 0;
    if (comparison === 'below') return values.filter(v => v < threshold).length;
    if (comparison === 'above') return values.filter(v => v > threshold).length;
    if (comparison === 'equals') return values.filter(v => v === threshold).length;
    return 0;
}

// Phase 3: Worst Performer
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

// Phase 5: Outlier Alert Aggregation
function aggregateOutlierAlerts(territoryData) {
    const alerts = [];
    territoryData.forEach(territory => {
        if (territory.agents) {
            const testZeros = territory.agents.filter(a => (a.test_pct || 0) === 0);
            if (testZeros.length > 0) {
                alerts.push({
                    territory: territory.Territory,
                    metric: 'Test Coverage',
                    count: testZeros.length,
                    severity: 'critical',
                    agents: testZeros.map(a => a.name)
                });
            }
            // Similar for other metrics...
        }
    });
    return alerts.sort((a, b) => b.count - a.count);
}
```

---

## Document History

| Date | Author | Changes |
|------|--------|---------|
| 2026-01-09 | Cascade | Initial implementation plan |
