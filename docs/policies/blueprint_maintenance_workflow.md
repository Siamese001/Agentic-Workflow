# Blueprint Maintenance Workflow

This document defines the **only allowed procedures** for updating governance baselines
in the blueprint enforcement system. All maintenance flags are **CI-forbidden** — they
can only be used locally by developers, never in automated pipelines.

---

## 1. Baseline Files

| Baseline | Purpose | Ceiling | Current |
|----------|---------|---------|---------|
| `missing_optional_baseline.json` | Track declared-but-not-yet-created subfolders | 20 | 16 |
| `known_debt_baseline.json` | Track allowed cross-layer import violations | 3 | 2 |
| `blueprint_integrity.sha256` | Lock blueprint file contents against tampering | N/A | 20 files |

---

## 2. Maintenance Flag Reference

### `--acknowledge-optional-growth`

**Use when**: A new optional subfolder is declared in `_constants.py` and is intentionally
missing from disk (planned scaffolding).

**Procedure**:
```bash
# 1. Add subfolder to blueprint in _constants.py
# 2. Run verify to confirm the new warning
python -m agentic_core.L5_safety.config.structure_blueprint._verify

# 3. If missing_optional_count exceeds ceiling, update baseline locally:
#    - Edit missing_optional_baseline.json
#    - Increase ceiling (add headroom, don't set at exact count)
#    - Add entry to entries_by_territory

# 4. Re-run verify to confirm PASS
python -m agentic_core.L5_safety.config.structure_blueprint._verify

# 5. Commit all changes together (blueprint + baseline)
git add agentic_core/L5_safety/config/structure_blueprint/
git commit -m "feat(blueprint): add optional subfolder X with ceiling update"
```

### `--acknowledge-debt`

**Use when**: A new cross-layer import violation must be temporarily allowed (lazy import
with fallback stub, runtime-only dependency).

**Procedure**:
```bash
# 1. Document the debt item with full context:
#    - source file path
#    - target import
#    - rationale (why can't this be refactored now?)
#    - owner (who will burn it down?)
#    - added date
#    - expires (quarter when debt must be resolved, e.g., "2026-Q2")
#    - burn_down_plan (specific refactor strategy)

# 2. Add entry to known_debt_baseline.json with all required fields
# 3. Increase ceiling if needed (current ceiling=3, current=2, headroom=1)
#    - New ceiling must provide headroom for operational safety
#    - Every entry MUST have expires + burn_down_plan fields

# 4. Re-run verify to confirm PASS with new warning count
python -m agentic_core.L5_safety.config.structure_blueprint._verify

# 5. Commit with clear debt acknowledgment
git commit -m "debt(cross-layer): add X lazy import, ceiling=N, expires=YYYY-QN"
```

### `--update-blueprint-hash`

**Use when**: Any file in `enforcement/` or blueprint config is modified.

**Procedure**:
```bash
# 1. Make your changes to blueprint files

# 2. Update the hash (automatically done by running with update=True):
python -c "
from pathlib import Path
from agentic_core.L5_safety.config.structure_blueprint.enforcement import blueprint_hash
r = blueprint_hash.check(Path('agentic_core/L5_safety/config/structure_blueprint'), update=True)
print('Hash updated:', r['stats'])
"

# 3. Verify the hash now matches
python -m agentic_core.L5_safety.config.structure_blueprint._verify

# 4. Commit hash file with your changes
git add agentic_core/L5_safety/config/structure_blueprint/blueprint_integrity.sha256
```

---

## 3. CI Enforcement

The following flags are **forbidden in CI** (`.github/workflows/ssot_verify.yml`):

```yaml
FORBIDDEN = [
    '--init-phantom-baseline',
    '--update-phantom-baseline',
    '--repair-phantom-baseline',
    '--acknowledge-import-change',
    '--update-blueprint-hash',
    '--acknowledge-debt',
    '--acknowledge-optional-growth',
]
```

If any of these flags appear in the `_verify.py` invocation in CI, the workflow **hard-fails**.

---

## 4. Budget Governance

### Warning Categories

| Category | Budgeted | Enforcement |
|----------|----------|-------------|
| `missing_optional_subfolder` | ✓ | ceiling in `missing_optional_baseline.json` |
| `config_execution_violation` | ✓ | ceiling in `known_debt_baseline.json` |
| All other warnings | ✗ | CI fails if `warnings_unbudgeted > 0` |

### Headroom Policy

Ceilings should be set **above** current counts to allow operational flexibility:

- **Minimum headroom**: 2-4 items
- **Example**: current=16, ceiling=20 (headroom=4)
- Headroom must remain ≥1 unless a burn-down PR is open.

Operating at 100% ceiling utilization is **brittle** — any legitimate addition requires
a maintenance action before CI will pass.

---

## 5. Scheduled Burn-Down Targets

### Known Debt: gateway_config.py Lazy Imports (2 items)

**Current state**: `gateway_config.py` uses lazy imports from `L2_execution` to avoid
circular dependencies. This is tracked as known debt with ceiling=3 (headroom=1).

**Target refactor**: Define abstract protocols in `agentic_core/config/protocols/` that
`L2_execution` implementations satisfy. Config layer imports protocols, not implementations.

**Owner**: Architecture team
**Target date**: Q2 2026

---

## 6. Artifact Outputs

After any maintenance action, verify these artifacts are updated correctly:

| Artifact | Location |
|----------|----------|
| Enforcement report | `docs/reports/verification/enforcement_report.json` |
| Blueprint hash | `agentic_core/L5_safety/config/structure_blueprint/blueprint_integrity.sha256` |
| Optional baseline | `agentic_core/L5_safety/config/structure_blueprint/enforcement/missing_optional_baseline.json` |
| Debt baseline | `agentic_core/L5_safety/config/structure_blueprint/enforcement/known_debt_baseline.json` |

---

## 7. Verification Commands

```bash
# Full verification (CI-equivalent)
python -m agentic_core.L5_safety.config.structure_blueprint._verify

# Regression tests
python -m pytest tests/unit/structure_blueprint/test_enforcement_counters.py -xvv

# Quick budget check
python -c "
import json
r = json.load(open('docs/reports/verification/enforcement_report.json'))
s = r['summary']
print(f'errors={s[\"errors\"]}, budgeted={s[\"warnings_budgeted\"]}, unbudgeted={s[\"warnings_unbudgeted\"]}')
"
```
