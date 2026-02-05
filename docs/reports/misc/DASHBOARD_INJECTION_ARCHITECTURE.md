# Dashboard Injection Architecture - MANDATORY ATOMIC PROCESS

## Critical Principle

**Dashboard generation and data injection are ATOMIC. They cannot be separate processes.**

If data injection fails, dashboard generation MUST fail. There is no such thing as a "dashboard without data" or "data injected later."

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│  Dashboard Generation Pipeline (ATOMIC)                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  1. PRE-GENERATION VALIDATION                                │
│     ├─ Load template                                         │
│     ├─ Verify all required placeholders exist                │
│     └─ FAIL if placeholders missing                          │
│                                                               │
│  2. DATA PREPARATION                                         │
│     ├─ Generate dashboard_rows (territories + metrics)       │
│     ├─ Generate recommendations (prioritized actions)        │
│     ├─ Generate strategic recommendations (L3 agent)         │
│     └─ Generate gauge data (health, quality, compliance)     │
│                                                               │
│  3. DATA INJECTION (MANDATORY)                               │
│     ├─ Inject dashboardData                                  │
│     ├─ Inject recommendationsData                            │
│     ├─ Inject lastUpdatedStr                                 │
│     ├─ Inject gaugeData                                      │
│     ├─ Inject strategic review                               │
│     └─ Inject top recommendations                            │
│                                                               │
│  4. POST-INJECTION VALIDATION                                │
│     ├─ Verify all placeholders replaced                      │
│     ├─ Verify data content present                           │
│     └─ FAIL HARD if any injection incomplete                 │
│                                                               │
│  5. ATOMIC WRITE                                             │
│     ├─ Write to temp file                                    │
│     ├─ Rename to final location                              │
│     └─ Success only if all steps complete                    │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Required Template Placeholders

Every dashboard template MUST contain these placeholders:

```javascript
// Data placeholders
const dashboardData = [];
const recommendationsData = [];
const lastUpdatedStr = "";
const gaugeData = {};
```

```html
<!-- HTML placeholders -->
<!-- STRATEGIC_REVIEW_INSERT -->
<!-- TOP_RECS_INSERT -->
```

## Validation Points

### Pre-Generation Validation
- **Location:** `AutonomyGuardianAgent._generate_self_contained_dashboard()`
- **Purpose:** Ensure template has all required placeholders before attempting injection
- **Failure Mode:** `RuntimeError` with list of missing placeholders

### Post-Injection Validation
- **Location:** After all `.replace()` calls
- **Purpose:** Verify all placeholders were successfully replaced
- **Failure Mode:** `RuntimeError` with list of failed injections

## Error Handling

### Template Missing Placeholders
```
❌ TEMPLATE VALIDATION FAILED - MISSING REQUIRED PLACEHOLDERS
Template path: /path/to/template.html
Missing placeholders:
  - dashboardData placeholder: 'const dashboardData = [];'
  - strategic review placeholder: '<!-- STRATEGIC_REVIEW_INSERT -->'

Dashboard generation requires these placeholders for data injection.
Update the template to include all required placeholders.
```

### Injection Incomplete
```
❌ DASHBOARD GENERATION FAILED - DATA INJECTION INCOMPLETE
The following injections failed:
  - dashboardData not injected (placeholder still present)
  - Strategic review not injected (placeholder still present)

This is a critical error. Dashboard generation and data injection are atomic.
Template path: /path/to/template.html
Check that template contains all required placeholders.
```

## E2E Test Coverage

The test suite validates:

1. **Dashboard data injection** - Verifies data present and non-empty
2. **Recommendations data injection** - Verifies recommendations array populated
3. **Timestamp injection** - Verifies lastUpdatedStr formatted correctly
4. **Gauge data injection** - Verifies gauge metrics present
5. **Strategic review injection** - Verifies placeholder replaced
6. **Top recommendations injection** - Verifies placeholder replaced
7. **Data content validation** - Verifies Territory fields present
8. **Risk matrix consistency** - Verifies territory count reasonable

## Template Locations

Two templates must be kept in sync:

1. **Primary:** `agentic_core/config/validators/dashboard_template.html`
2. **Fallback:** `agentic_core/L5_safety/validators/dashboard_template.html`

Both must contain all required placeholders.

## Data Sources

All dashboard data comes from a single unified source:

- **dashboard_rows** - Generated from territory metrics
- **Risk matrix** - Uses same dashboard_rows data (no separate source)
- **Recommendations** - Generated from dashboard_rows analysis
- **Strategic recommendations** - Generated by StrategicRecommendationAgent from dashboard_rows

This ensures consistency across all dashboard visualizations.

## Refactoring Guidelines

When refactoring the dashboard:

1. **Never separate generation from injection** - They are atomic
2. **Add new placeholders to both templates** - Keep them in sync
3. **Update validation lists** - Add new placeholders to pre/post validation
4. **Update e2e tests** - Add checks for new injection points
5. **Fail hard on errors** - Use `RuntimeError`, not warnings

## Running Tests

```bash
# E2E test with mandatory injection validation
python scripts/test_dashboard_generation.py

# Expected output:
# ✅ ALL MANDATORY INJECTION CHECKS PASSED
# Dashboard generation and data injection are atomic.
```

## Key Takeaways

- ✅ Dashboard generation = data preparation + injection + validation (atomic)
- ✅ Injection failures cause generation to fail (no partial states)
- ✅ Pre-validation prevents silent failures
- ✅ Post-validation catches injection bugs
- ✅ E2E tests enforce contract
- ❌ Never generate dashboard without data
- ❌ Never inject data as separate process
- ❌ Never allow partial injection states
