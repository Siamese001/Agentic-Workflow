# SSOT Dashboard System - L6 Observability

## Single Source of Truth

**ALL dashboard data generation MUST use this directory's scripts. NO exceptions.**

---

## Core Scripts

### 1. `generate_dashboard.py` - SSOT Generator
**Purpose:** Generate dashboard data from agent_discovery_full.json

**Usage:**
```bash
python agentic_core/L6_observability/dashboards/generate_dashboard.py
```

**What it does:**
1. Loads agent_discovery_full.json
2. Groups agents by FIXED territory structure
3. Generates dashboard rows with FIXED field schema
4. Updates autonomy_dashboard.html
5. Validates output

**FIXED Territory Structure (NEVER CHANGES):**
- TOTAL (always first)
- L5, L4, L3, L2, L1, L0
- Apps Lic, Apps Rg, Apps Shared

**FIXED Field Schema (24 fields - NEVER CHANGES):**
- Territory, Total, Compliant
- Heal Cap %, Heal Invocation %, Invocation %
- Hardened %, MCP Capable %
- Test %, Observable %
- Avg CC, Avg LOC
- Typed %, Documented %
- Metadata %, Proper Base %, Schema Strictness %
- Complexity Health, Code Quality Score
- Criticality, Health, Health Breakdown, Risk
- Used %, Priority

---

### 2. `test_dashboard.py` - SSOT Test Suite
**Purpose:** Validate dashboard wireframe consistency

**Usage:**
```bash
python agentic_core/L6_observability/dashboards/test_dashboard.py
```

**Test Coverage (6 tests):**
1. **Wireframe Consistency** - All required fields present
2. **Territory Order** - Matches FIXED structure
3. **Data Consistency** - Matches agent_discovery_full.json
4. **Field Types** - Correct data types
5. **Regeneration Stability** - Same structure on regeneration
6. **HTML Rendering Elements** - Required functions present

**Expected Output:**
```
✅ ALL TESTS PASSED - Dashboard is ready
```

---

## Workflow

### When to Regenerate Dashboard

**ALWAYS regenerate after:**
- Changes to agent_discovery_full.json
- Adding/removing agents
- Modifying agent healing status
- Any data changes

**Process:**
```bash
# 1. Regenerate dashboard
python agentic_core/L6_observability/dashboards/generate_dashboard.py

# 2. Test dashboard
python agentic_core/L6_observability/dashboards/test_dashboard.py

# 3. If all tests pass, commit
git add agentic_core/L6_observability/dashboards/autonomy_dashboard.html
git commit -m "chore: regenerate dashboard data"
```

---

## Rules

### ✅ DO
- Use `generate_dashboard.py` for ALL dashboard generation
- Run `test_dashboard.py` before committing
- Keep FIXED territory structure
- Keep FIXED field schema
- Maintain wireframe consistency

### ❌ DO NOT
- Create scripts in `/scripts` folder for dashboard generation
- Modify territory structure
- Modify field schema
- Skip testing before commit
- Hardcode dashboard data manually
- Create duplicate generation logic

---

## Script Sprawl Prevention

**Problem:** Multiple scripts in `/scripts` folder were generating dashboard data inconsistently.

**Solution:** Single SSOT in `L6_observability/dashboards/`

**Deprecated Scripts (DO NOT USE):**
- `scripts/regenerate_dashboard_complete.py` ❌
- `scripts/regenerate_dashboard_properly.py` ❌
- `scripts/update_dashboard_data.py` ❌
- `scripts/update_heal_cap_only.py` ❌
- Any other dashboard generation scripts in `/scripts` ❌

**These will be removed.**

---

## Architecture

```
L6_observability/dashboards/
├── generate_dashboard.py     # SSOT Generator
├── test_dashboard.py          # SSOT Test Suite
├── autonomy_dashboard.html    # Dashboard HTML (updated by generator)
├── data_generator.py          # Legacy (not used)
├── renderer.py                # Legacy (not used)
└── README.md                  # This file
```

---

## Troubleshooting

### Dashboard tables not rendering?
```bash
# Regenerate with SSOT generator
python agentic_core/L6_observability/dashboards/generate_dashboard.py

# Verify with tests
python agentic_core/L6_observability/dashboards/test_dashboard.py
```

### Territory structure changed?
**This should NEVER happen.** The territory structure is FIXED.
If it changed, the generator was not used correctly.

### Missing fields?
**This should NEVER happen.** The field schema is FIXED.
If fields are missing, the generator was not used correctly.

---

## Contact

For questions about dashboard generation, refer to this README.
For issues, ensure you're using the SSOT generator and tests.
