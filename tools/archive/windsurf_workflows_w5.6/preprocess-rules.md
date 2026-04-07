# Windsurf Rules Preprocessing Workflow
---
description: Preprocess Windsurf rules to expand ${VAR} variables from _variables.yaml SSOT
---

# Windsurf Rules Variable System

This workflow preprocesses `.windsurf/rules/*.md` files to expand `${VAR}` variables
defined in `.windsurf/rules/_variables.yaml`.

## Quick Commands

```bash
# Validate all variables are defined
python tools/windsurf/preprocess_rules.py --validate

# Expand variables and write to _build/
python tools/windsurf/preprocess_rules.py --process

# Check if _build/ is up-to-date (for CI)
python tools/windsurf/preprocess_rules.py --check

# Full pipeline: validate + process
python tools/windsurf/preprocess_rules.py --validate && python tools/windsurf/preprocess_rules.py --process
```

## Using Variables in Rules

1. **Define variable in `_variables.yaml`:**
   ```yaml
   paths:
     PLAN_DIR: ".windsurf/plans"
   ```

2. **Use in rule file (e.g., `plan-location.md`):**
   ```markdown
   Save plans to `${PLAN_DIR}/`
   ```

3. **Process to generate expanded version:**
   ```bash
   python tools/windsurf/preprocess_rules.py --process
   ```

4. **Result in `_build/plan-location.md`:**
   ```markdown
   Save plans to `.windsurf/plans/`
   ```

## Available Variables

See `.windsurf/rules/_variables.yaml` for full list. Common ones:

| Variable | Value | Purpose |
|----------|-------|---------|
| `${PLAN_DIR}` | `.windsurf/plans` | Execution plans location |
| `${EVIDENCE_DIR}` | `docs/reports/plans` | Evidence/reports location |
| `${CONSTITUTIONAL_RULES}` | `.windsurf/rules/.windsurfrules` | Main rules file |
| `${EXECUTION_PLAN_TEMPLATE}` | `.windsurf/templates/execution-plan-template.md` | Plan template |
| `${TOKEN_ESTIMATOR}` | `tools/utils/planning/token_estimator.py` | Token tool |
| `${ADG_TEST_ACCELERATOR}` | `tools/adg/adg_test_accelerator.py` | Test accelerator |
| `${CONTRACT_GATES}` | `ops_scripts/ci/run_contract_gates.py` | CI gates |

## CI Integration

The pre-commit hook (`tools/windsurf/pre_commit_rules.py`) ensures:
- All `${VAR}` references are valid before commit
- `_build/` directory stays synchronized with source rules

Add to `.git/hooks/pre-commit`:
```bash
python tools/windsurf/pre_commit_rules.py || exit 1
```
