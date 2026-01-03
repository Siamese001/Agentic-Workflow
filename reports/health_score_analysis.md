# Health Score Formula Analysis & Recommendations

**Generated:** January 3, 2026  
**Purpose:** Assess current health score weighting and propose improvements

---

## Current Health Score Formula

```python
# Formula: (Heal Cap + Invocation + Tests + Observability + Inverted CC) / 5
cc_health_component = max(0, min(100, 100 - (avg_cc * 2)))
health = (perc_healing_cap + perc_healing_invoke + perc_tests + perc_observable + cc_health_component) / 5
```

### Current Weights (Equal: 20% each)

| Metric | Weight | Rationale | Current Impact |
|--------|--------|-----------|----------------|
| **Heal Capability %** | 20% | Measures if agents have HealerMixin | Foundational - enables self-repair |
| **Heal Invocation %** | 20% | Measures actual super().heal_repository() calls | Critical - shows actual usage |
| **Test Coverage %** | 20% | Measures test presence | Quality gate - prevents regressions |
| **Observability %** | 20% | Measures logging/metrics/tracing | Operational visibility |
| **Inverted Complexity** | 20% | Penalizes high cyclomatic complexity | Maintainability proxy |

---

## Critical Metrics MISSING from Health Score

### 1. **MCP Hardened % (Security)**
- **Current Status:** Tracked but NOT in health score
- **Why It Matters:** Agents without MCPShield can execute dangerous operations (os.system, subprocess) without protection
- **Risk:** Security vulnerabilities, production incidents
- **Recommendation:** Add to health score with 15% weight

### 2. **MCP Capable % (Modernization)**
- **Current Status:** Just added, NOT in health score
- **Why It Matters:** Measures adoption of MCP protocol for external tool integration
- **Risk:** Technical debt, missed opportunities for agent enhancement
- **Recommendation:** Add to health score with 10% weight (lower priority than security)

### 3. **Typing % (Code Quality)**
- **Current Status:** Tracked but NOT in health score
- **Why It Matters:** Type annotations prevent runtime errors, improve IDE support
- **Risk:** Runtime type errors, poor developer experience
- **Recommendation:** Add to health score with 10% weight

### 4. **Usage % (Business Impact)**
- **Current Status:** Tracked but NOT in health score
- **Why It Matters:** Unused agents are technical debt
- **Risk:** Wasted maintenance effort on dead code
- **Recommendation:** Consider as multiplier rather than additive component

---

## Proposed Health Score Formula (Enhanced)

### Option A: Comprehensive (8 components)
```python
# Weights total to 100%
health = (
    perc_healing_cap * 0.15 +      # 15% - Foundational capability
    perc_healing_invoke * 0.20 +    # 20% - Critical usage (highest weight)
    perc_tests * 0.15 +             # 15% - Quality gate
    perc_observable * 0.10 +        # 10% - Operational visibility
    perc_hardened * 0.15 +          # 15% - Security (NEW)
    perc_mcp_capable * 0.05 +       # 5% - Modernization (NEW)
    perc_typed * 0.10 +             # 10% - Code quality (NEW)
    cc_health_component * 0.10      # 10% - Maintainability (reduced from 20%)
)
```

**Rationale:**
- **Invocation gets highest weight (20%)** - actual behavior > potential
- **Security (Hardened) gets 15%** - critical for production safety
- **Capability, Tests, Typing each 10-15%** - balanced importance
- **Complexity reduced to 10%** - still important but not dominant
- **MCP Capable only 5%** - nice-to-have, not critical

### Option B: Simplified (6 components - recommended)
```python
# Weights total to 100%
health = (
    perc_healing_cap * 0.15 +      # 15% - Foundational
    perc_healing_invoke * 0.25 +    # 25% - Critical (increased)
    perc_tests * 0.20 +             # 20% - Quality
    perc_observable * 0.10 +        # 10% - Visibility
    perc_hardened * 0.20 +          # 20% - Security (NEW)
    cc_health_component * 0.10      # 10% - Maintainability
)
```

**Rationale:**
- Focuses on **critical operational metrics**
- Drops MCP Capable and Typing (tracked separately)
- **Invocation and Hardening are top priorities** (45% combined)
- Simpler formula, easier to understand and explain

---

## Weighting Justification

### High Priority (20-25% weight)
1. **Heal Invocation (25%)** - Actual self-repair behavior
2. **MCP Hardened (20%)** - Security protection
3. **Test Coverage (20%)** - Quality assurance

### Medium Priority (10-15% weight)
4. **Heal Capability (15%)** - Foundational infrastructure
5. **Observability (10%)** - Operational visibility
6. **Inverted Complexity (10%)** - Maintainability

### Low Priority (5% weight or separate tracking)
7. **MCP Capable (5%)** - Modernization indicator
8. **Typing %** - Track separately as "Code Quality Score"
9. **Usage %** - Use as risk multiplier, not additive

---

## Alternative: Multi-Dimensional Scoring

Instead of single health score, consider **3 separate scores**:

### 1. **Operational Health (40%)**
```python
operational = (
    perc_healing_invoke * 0.40 +
    perc_tests * 0.30 +
    perc_observable * 0.30
)
```

### 2. **Security Health (30%)**
```python
security = (
    perc_hardened * 0.60 +
    perc_healing_cap * 0.40
)
```

### 3. **Code Quality (30%)**
```python
quality = (
    perc_typed * 0.40 +
    cc_health_component * 0.30 +
    perc_mcp_capable * 0.30
)
```

**Overall Health = (Operational * 0.40) + (Security * 0.30) + (Quality * 0.30)**

---

## Recommendations

### Immediate Actions
1. ✅ **Add MCP Hardened % to health score** (20% weight)
2. ✅ **Add MCP Capable % column to dashboard** (completed)
3. ✅ **Update tooltips to clarify MCP Hardening vs Capability** (completed)
4. ⚠️ **Increase Heal Invocation weight** from 20% to 25%
5. ⚠️ **Reduce Complexity weight** from 20% to 10%

### Short-Term (Next Sprint)
1. Add Typing % to health score (10% weight)
2. Create separate "Code Quality Score" dashboard
3. Add Usage % as risk multiplier (not additive)

### Long-Term (Next Quarter)
1. Implement multi-dimensional scoring (Operational, Security, Quality)
2. Add historical trending for health scores
3. Create health score benchmarks by layer (L1, L2, L3, L4, L5)

---

## Impact Analysis

### Current Formula Issues
- **Over-weights complexity** (20%) - penalizes complex but necessary agents
- **Under-weights security** (0%) - no credit for MCP hardening
- **Ignores typing** (0%) - misses important code quality signal
- **Equal weights** - doesn't reflect true criticality

### Proposed Formula Benefits
- **Security-first** - 20% weight for MCP hardening
- **Behavior-focused** - 25% weight for actual invocation
- **Balanced** - No single metric dominates
- **Actionable** - Clear priorities for improvement

---

## Dashboard Changes Required

### Backend (AutonomyGuardianAgent.py)
```python
# Update health calculation (line ~1385)
health = round((
    perc_healing_cap * 0.15 +
    perc_healing_invoke * 0.25 +
    perc_tests * 0.20 +
    perc_observable * 0.10 +
    perc_hardened * 0.20 +
    cc_health_component * 0.10
), 1)
```

### Frontend (dashboard_template.html)
```html
<!-- Update tooltip (line ~492) -->
<th title="Composite health: Invocation(25%) + Hardened(20%) + Tests(20%) + Capability(15%) + Observability(10%) + Inverted CC(10%)">
    Health Score
</th>
```

### Metrics Key
```
Health Score: Weighted composite of critical metrics
- Heal Invocation: 25% (highest - actual behavior)
- MCP Hardened: 20% (security protection)
- Test Coverage: 20% (quality gate)
- Heal Capability: 15% (foundational)
- Observability: 10% (visibility)
- Inverted Complexity: 10% (maintainability)
```

---

## Conclusion

**Recommended Action:** Implement **Option B (Simplified 6-component formula)** with the following weights:

| Metric | Current | Proposed | Change |
|--------|---------|----------|--------|
| Heal Invocation | 20% | **25%** | +5% ⬆️ |
| MCP Hardened | 0% | **20%** | +20% ⬆️ NEW |
| Test Coverage | 20% | **20%** | 0% ➡️ |
| Heal Capability | 20% | **15%** | -5% ⬇️ |
| Observability | 20% | **10%** | -10% ⬇️ |
| Inverted Complexity | 20% | **10%** | -10% ⬇️ |

This formula prioritizes **security and actual behavior** while maintaining balance across operational metrics.
