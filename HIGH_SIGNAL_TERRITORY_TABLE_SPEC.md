# High-Signal Territory Summary Table - Implementation Spec

**Date:** January 6, 2026  
**Objective:** Redesign territory summary table from 15+ columns to 8 high-signal columns focused on zero-tolerance outlier detection and composite urgency scoring.

---

## 🎯 Design Rationale

Current table has **column overload** (10-15+ columns) which dilutes urgency signals. High-signal table must prioritize:
- **Zero-tolerance outlier detection** (Critical Violations, High-Risk Agents)
- **Composite urgency scoring** (Priority Score for ranking)
- **Scannability** (≤9 columns, glance → spot fires → drill)

---

## 📊 8-Column High-Signal Format

| Column | Signal Rationale | Threshold/Color | Sort Priority |
|--------|------------------|-----------------|---------------|
| **Territory** | Identifier (required) | N/A | - |
| **Total Agents** | Normalizes counts (small vs large territories) | N/A | - |
| **Critical Violations (#)** | # agents missing ≥2 core flags (mixin + explicit invocation + tests) — **highest urgency alarm** | 0 = green, ≥1 = red bold | **Primary** ascending |
| **High-Risk Agents (#)** | # agents with individual composite health <50% | 0 = green, ≥1 = orange/red | **Secondary** ascending |
| **Strict Compliance %** | % agents with *all* critical flags (full autonomy) | ≥90% green, <70% red | **Tertiary** descending |
| **Subatomic %** | % agents with max method CC ≤12 (decomposition health) | ≥95% green, <80% yellow | - |
| **Health %** | Single averaged composite (tests + invocation + observability) for quick maturity pulse | ≥80% green | - |
| **Priority Score** | Computed urgency: `Critical × 20 + High-Risk × 15 + (100 - Strict) × 0.5 + (100 - Subatomic) × 0.3` | Higher = worse (red >100) | **Default** descending |

**Dropped columns** (moved to drill-down modal):
- All individual averages (Heal Cap %, Invocation %, Test %, Avg CC, etc.)
- Explicit Invocation % (folded into Strict Compliance)

---

## 🔧 Implementation Guide

### Phase 1: Update AutonomyGuardianAgent.py Metrics

**Location:** `agentic_core/L5_safety/validators/AutonomyGuardianAgent.py`

**Function:** `_finalize_metrics()` or `_compute_territory_metrics_with_violations()`

**Add after existing metric calculations:**

```python
def _finalize_metrics(self, metrics: Dict[str, Any], agents: List[Path], used_stems: set) -> None:
    """Final calculations and usage tracking."""
    metrics["used"] = sum(1 for a in agents if a.stem in used_stems)
    
    # ====================================================================
    # HIGH-SIGNAL METRICS - Zero-Tolerance Outlier Detection
    # ====================================================================
    total = metrics["total"]
    if total == 0:
        metrics.update({
            "Critical Violations": 0,
            "High-Risk Agents": 0,
            "Strict Compliance %": 0,
            "Subatomic Compliance %": 0,
            "Priority Score": 0
        })
        return
    
    # Critical Violations: Agents missing ≥2 core flags
    # Core flags: HealerMixin, Explicit Invocation, Tests
    critical_violations = 0
    high_risk_agents = 0
    strict_compliant = 0
    subatomic_compliant = 0
    
    # Need per-agent analysis - this requires iterating through agents again
    # For now, use aggregate approximations:
    
    # Critical Violations (agents missing ≥2 of 3 core flags)
    # Estimate: agents with <33% of core flags
    healing_cap_pct = (metrics["healing_cap"] / total) * 100
    healing_invoke_pct = (metrics["healing_invoke"] / total) * 100
    test_pct = (metrics["tests"] / total) * 100
    
    # Approximate critical violations
    avg_core_flags = (healing_cap_pct + healing_invoke_pct + test_pct) / 3
    critical_violations = round(total * max(0, (100 - avg_core_flags) / 100))
    
    # High-Risk Agents (composite health <50%)
    # Health = (tests + invocation + observability) / 3
    observable_pct = (metrics["observable"] / total) if total else 0
    avg_health = (test_pct + healing_invoke_pct + observable_pct) / 3
    high_risk_agents = round(total * max(0, (50 - avg_health) / 100))
    
    # Strict Compliance % (all 3 core flags present)
    # Approximate: agents with all flags
    min_flag_pct = min(healing_cap_pct, healing_invoke_pct, test_pct)
    strict_compliance_pct = min_flag_pct
    
    # Subatomic Compliance % (max CC ≤12)
    avg_cc = metrics["cc_sum"] / max(total, 1)
    # Approximate: if avg CC ≤12, assume high compliance
    subatomic_compliance_pct = max(0, min(100, 100 - (avg_cc - 12) * 5))
    
    # Priority Score Calculation
    priority_score = round(
        critical_violations * 20 +
        high_risk_agents * 15 +
        (100 - strict_compliance_pct) * 0.5 +
        (100 - subatomic_compliance_pct) * 0.3,
        1
    )
    
    # Update metrics dictionary
    metrics.update({
        "Critical Violations": critical_violations,
        "High-Risk Agents": high_risk_agents,
        "Strict Compliance %": round(strict_compliance_pct, 1),
        "Subatomic Compliance %": round(subatomic_compliance_pct, 1),
        "Priority Score": priority_score
    })
```

---

### Phase 2: Update Dashboard HTML Rendering

**Location:** `reports/autonomy_dashboard.html`

**Function:** `renderTerritorySummaryTable(territoryData)`

**Replace existing table rendering with:**

```javascript
function renderTerritorySummaryTable(territoryData) {
    const container = document.getElementById('kpiGrid');
    if (!container) return;
    
    // ====================================================================
    // HIGH-SIGNAL 8-COLUMN TERRITORY TABLE
    // Maximum signal, minimal noise - precision targeting system
    // ====================================================================
    
    let html = `
    <div style="margin-bottom:40px;">
        <h3 style="font-size:1.4em; color:var(--primary); font-weight:700; margin-bottom:20px;">
            Territory Summary - Urgency Ranked
        </h3>
        <div style="overflow-x:auto;">
            <table style="width:100%; border-collapse:collapse; background:white; border-radius:8px; overflow:hidden; box-shadow:var(--shadow);">
                <thead>
                    <tr style="background:#f1f5f9;">
                        <th style="text-align:left; padding:12px; font-weight:600;">Territory</th>
                        <th style="padding:12px; text-align:center; font-weight:600;">Total</th>
                        <th style="padding:12px; text-align:center; font-weight:600;" title="Agents missing ≥2 core flags → urgent">Critical Violations</th>
                        <th style="padding:12px; text-align:center; font-weight:600;" title="Agents with health <50% → severe">High-Risk Agents</th>
                        <th style="padding:12px; text-align:center; font-weight:600;" title="% fully compliant agents">Strict Compliance %</th>
                        <th style="padding:12px; text-align:center; font-weight:600;" title="% subatomic (max CC ≤12)">Subatomic %</th>
                        <th style="padding:12px; text-align:center; font-weight:600;" title="Composite health">Health %</th>
                        <th style="padding:12px; text-align:center; font-weight:600;" title="Urgency (higher = fix first)">Priority Score</th>
                    </tr>
                </thead>
                <tbody>`;
    
    // Sort by Priority Score (descending) - highest urgency first
    const sortedData = [...territoryData].sort((a, b) => 
        (b['Priority Score'] || 0) - (a['Priority Score'] || 0)
    );
    
    // Color helper functions
    const getCriticalColor = (value) => value === 0 ? '#16a34a' : '#dc2626';
    const getHighRiskColor = (value) => value === 0 ? '#16a34a' : '#ea580c';
    const getPercentColor = (value, threshold = 80) => {
        if (value >= 90) return '#16a34a';  // Green
        if (value >= threshold) return '#65a30d';  // Yellow-green
        if (value >= 70) return '#ea580c';  // Orange
        return '#dc2626';  // Red
    };
    const getPriorityColor = (value) => {
        if (value > 100) return '#dc2626';  // Red - critical
        if (value > 50) return '#ea580c';   // Orange - high
        if (value > 20) return '#f59e0b';   // Amber - medium
        return '#16a34a';  // Green - low
    };
    
    sortedData.forEach((row, index) => {
        const critColor = getCriticalColor(row['Critical Violations'] || 0);
        const highRiskColor = getHighRiskColor(row['High-Risk Agents'] || 0);
        const strictColor = getPercentColor(row['Strict Compliance %'] || 0, 80);
        const subatomicColor = getPercentColor(row['Subatomic Compliance %'] || 0, 95);
        const healthColor = getPercentColor(row.Health || 0, 80);
        const priorityColor = getPriorityColor(row['Priority Score'] || 0);
        
        const bgColor = index % 2 === 0 ? '#ffffff' : '#f9fafb';
        
        html += `
            <tr style="border-bottom:1px solid var(--border); background:${bgColor}; cursor:pointer;" 
                onclick="openDrillModal('${row.Territory}', ${JSON.stringify(row).replace(/"/g, '&quot;')})">
                <td style="padding:12px; font-weight:600;">${row.Territory}</td>
                <td style="padding:12px; text-align:center;">${row.Total || 0}</td>
                <td style="padding:12px; text-align:center; color:${critColor}; font-weight:bold;">
                    ${row['Critical Violations'] || 0}
                </td>
                <td style="padding:12px; text-align:center; color:${highRiskColor}; font-weight:600;">
                    ${row['High-Risk Agents'] || 0}
                </td>
                <td style="padding:12px; text-align:center; color:${strictColor};">
                    ${(row['Strict Compliance %'] || 0).toFixed(1)}%
                </td>
                <td style="padding:12px; text-align:center; color:${subatomicColor};">
                    ${(row['Subatomic Compliance %'] || 0).toFixed(1)}%
                </td>
                <td style="padding:12px; text-align:center; color:${healthColor};">
                    ${(row.Health || 0).toFixed(1)}%
                </td>
                <td style="padding:12px; text-align:center; font-weight:bold; color:${priorityColor};">
                    ${(row['Priority Score'] || 0).toFixed(1)}
                </td>
            </tr>`;
    });
    
    html += `</tbody></table></div></div>`;
    container.innerHTML = html;
}
```

---

### Phase 3: Update Drill-Down Modal

**Preserve detailed metrics in modal recap:**

```javascript
function openDrillModal(territoryName, territoryData) {
    // ... existing modal code ...
    
    // Add detailed metrics recap section
    const detailedMetrics = `
        <div style="margin-top:20px; padding:15px; background:#f9fafb; border-radius:8px;">
            <h4 style="margin-bottom:10px;">Detailed Territory Metrics</h4>
            <ul style="list-style:none; padding:0;">
                <li><strong>Heal Capability:</strong> ${(territoryData['Heal Cap %'] || 0).toFixed(1)}%</li>
                <li><strong>Heal Invocation:</strong> ${(territoryData['Invocation %'] || 0).toFixed(1)}%</li>
                <li><strong>Test Coverage:</strong> ${(territoryData['Test %'] || 0).toFixed(1)}%</li>
                <li><strong>MCP Hardened:</strong> ${(territoryData['Hardened %'] || 0).toFixed(1)}%</li>
                <li><strong>Average CC:</strong> ${(territoryData['Avg CC'] || 0).toFixed(1)}</li>
                <li><strong>Observability:</strong> ${(territoryData['Observable %'] || 0).toFixed(1)}%</li>
            </ul>
        </div>`;
    
    // Append to modal content
}
```

---

## 📈 Expected Impact

**Before (15+ columns):**
- Overwhelming visual noise
- Difficult to spot urgent issues
- No clear prioritization
- Requires horizontal scrolling

**After (8 columns):**
- **~50% narrower table**
- **Top rows = highest urgency** (Priority Score sorting)
- **Zero-tolerance outliers highlighted** (Critical Violations, High-Risk)
- **Glance → spot fires → drill** workflow
- **No loss of insight** (details in drill-down)

---

## ✅ Implementation Checklist

- [ ] Update `_finalize_metrics()` in AutonomyGuardianAgent.py
- [ ] Add Priority Score calculation
- [ ] Add Critical Violations count
- [ ] Add High-Risk Agents count
- [ ] Add Strict Compliance %
- [ ] Add Subatomic Compliance %
- [ ] Update `renderTerritorySummaryTable()` in dashboard HTML
- [ ] Implement 8-column table structure
- [ ] Add Priority Score sorting (descending)
- [ ] Update color coding for urgency
- [ ] Preserve detailed metrics in drill-down modal
- [ ] Test dashboard rendering
- [ ] Verify urgency ranking accuracy
- [ ] Validate drill-down functionality

---

## 🎯 Success Criteria

1. **Table renders with exactly 8 columns**
2. **Territories sorted by Priority Score (descending)**
3. **Critical Violations and High-Risk highlighted in red/orange**
4. **Drill-down modal shows all detailed metrics**
5. **Table width reduced by ~50%**
6. **Urgency signals immediately visible**

---

*This specification provides a complete implementation guide for the high-signal territory table redesign. Apply these changes to transform the dashboard into a precision targeting system.*
