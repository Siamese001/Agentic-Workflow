# Pre-Commit Configuration Redesign Proposal

**Date:** 2026-04-06  
**Current State:** 42 hooks (too many, unclear ordering)  
**Target:** ~15 hooks (clean, clear ordering, ADG-dependent)

## Current Hook Inventory (42 total)

### Admission Guards (4 hooks)
- windsurf-plan-ci (manual)
- guard-no-verify (commit-msg)
- guard-guardian-hitl (commit-msg)
- guard-agent-deletion

### Fast Syntax & Formatting (8 hooks)
- trailing-whitespace
- end-of-file-fixer
- mixed-line-ending
- check-merge-conflict
- python-syntax-check
- ruff (3 separate tiers: P0, P1, P2)
- ruff-format
- guardian-comment-fixer

### Structural Validation (7 hooks)
- hollow-file-gate
- check-report-location
- plan-location-gate
- windsurf-governance-health (**removed** — windsurf-gha-cutover-d9f2a7)
- reject-generated-artifacts-tracked
- check-tooling-apps-boundary
- module-collision-guard
- eager-import-lint

### Configuration Validation (4 hooks)
- mcp-config-sovereignty
- mcp-config-drift-check
- pytest-config-ssot
- pre-commit-summary-init

### ADG-Dependent Gates (7 hooks)
- adg-preflight
- adg-burndown-gate (DUPLICATE - already done by generate_full_adg.py)
- adg-layer-violation-gate (DUPLICATE - already done by generate_full_adg.py)
- adg-p1-defect-gate (DUPLICATE - already done by generate_full_adg.py)
- adg-python-ban-gate (NOT duplicate - source-code check)
- adg-yaml-grep-ban-gate (NOT duplicate - source-code check)
- adg-skip-file-ratchet (NOT duplicate - source-code check)

### Policy Enforcement (2 hooks)
- guardian-exemption-gate
- adg-skip-file-ratchet

### CI-Only Manual Lane (5 hooks)
- adg-ci-gates (manual)
- check-c0-sovereignty
- check-dedup-violations
- check-script-sprawl
- check-shim-discipline
- check-rollback-checkpoints

### Cleanup & Reporting (2 hooks)
- purge-cache
- pre-commit-summary-report

## Problems with Current Design

1. **Too many hooks (42)** - Cognitive overload, hard to understand
2. **Unclear ordering** - T0-T21 numbering doesn't match actual dependencies
3. **Redundant checks** - 3 ADG gates duplicate what generate_full_adg.py already does:
   - `adg-burndown-gate` - duplicates `route_violations()` in generate_full_adg.py
   - `adg-layer-violation-gate` - duplicates layer violation counting in generate_full_adg.py
   - `adg-p1-defect-gate` - duplicates `_check_p1_defects()` in generate_full_adg.py
4. **No clear ADG dependency** - Some ADG gates are optional, others required
5. **Scattered concerns** - Configuration checks mixed with structural checks

### Duplication Analysis

**generate_full_adg.py already does:**
- P1 defect checking (line 291-306, 508)
- Layer violation analysis (line 501-505, 547)
- Burndown/routing summary (line 504-505)

**Current pre-commit hooks duplicate:**
- `adg-p1-defect-gate` - Same as generate_full_adg.py strict mode
- `adg-layer-violation-gate` - Same as layer violation counting in generate_full_adg.py
- `adg-burndown-gate` - Same as routing summary in generate_full_adg.py

**Should NOT duplicate (source-code checks):**
- `adg-python-ban-gate` - Checks for grep/mypy/pytest in Python files (not ADG data)
- `adg-yaml-grep-ban-gate` - Checks for grep in YAML workflows (not ADG data)
- `adg-skip-file-ratchet` - Checks skip-file directive count (not ADG data)

## Proposed Clean Design (15 hooks)

### Phase 0: Admission Guards (commit-msg stage) - 3 hooks
**Purpose:** Authorize dangerous operations before they happen

1. `guard-no-verify` - Block --no-verify bypass
2. `guard-guardian-hitl` - HITL for new guardian exemptions
3. `guard-agent-deletion` - Authorize agent file deletions

### Phase 1: Normalize & Validate Syntax (no ADG) - 4 hooks
**Purpose:** Fix formatting and catch syntax errors immediately

1. `whitespace-normalize` - Combine trailing-whitespace, end-of-file-fixer, mixed-line-ending, check-merge-conflict
2. `python-syntax-check` - Fast syntax validation
3. `ruff-lint-and-format` - Combine all ruff tiers + ruff-format into single pass
4. `guardian-comment-fixer` - Canonicalize guardian comments

### Phase 2: Structural Validation (no ADG) - 4 hooks
**Purpose:** Validate code structure without ADG dependency

1. `reject-artifacts` - Reject tracked generated artifacts
2. `hollow-file-gate` - AST semantic validity
3. `architectural-guards` - Combine module-collision, tooling-boundary, eager-import
4. `ssot-location-gates` - Combine report-location, plan-location

### Phase 3: Configuration Validation (no ADG) - 2 hooks
**Purpose:** Validate configuration files

1. `config-validation` - Combine MCP config, pytest config, windsurf governance
2. `exemption-ratchet` - Guardian exemption quality gate

### Phase 4: ADG-Dependent Gates (requires ADG) - 1 hook
**Purpose:** ADG generation + source-code checks NOT done by generate_full_adg.py

1. `adg-unified-gate` - Orchestrates:
   - **Step 1:** Check if ADG-relevant files changed
     - If YES → Run `python tools/generate/generate_full_adg.py --strict` (~95s)
       - This ALREADY does: P1 defect check, layer violation check, burndown/routing analysis
     - If NO → Skip ADG generation, use existing ADG
   - **Step 2:** Run source-code checks NOT done by generate_full_adg.py:
     - Python grep ban (grep/mypy/pytest usage in Python files)
     - YAML grep ban (grep usage in GitHub Actions workflows)
     - Skip-file ratchet (skip-file directive count ceiling)

**Key Design Decision:** 
- `generate_full_adg.py` handles: P1 defects, layer violations, burndown
- Unified gate handles: Source-code pattern bans (grep/mypy/pytest), skip-file ratchet
- No duplication of checks

### Phase 5: Cleanup - 1 hook
**Purpose:** Final cleanup

1. `purge-cache-and-report` - Combine purge-cache + summary report

## ADG Dependency Design

### When to Generate ADG
ADG generation should run when any of these file patterns change:
- `agentic_core/**/*.py` - ADG infrastructure
- `tools/generate/**/*.py` - ADG generation scripts
- `tools/adg/**/*.py` - ADG analysis tools
- `config/**/*.yaml` - Layer/territory configuration

### ADG Generation Flow
```
git commit
  ↓
Phase 0-3: Fast checks (no ADG needed, ~5s)
  ↓
Phase 4: Check if ADG-relevant files changed
  ├─ YES → Run python tools/generate/generate_full_adg.py (~95s)
  │        → Run ADG-dependent checks on fresh ADG
  └─ NO  → Use existing ADG (if available)
           → Run ADG-dependent checks on existing ADG
  ↓
Phase 5: Cleanup (~1s)
```

### Benefits of This Design

1. **Fewer hooks (15 vs 42)** - Clearer, easier to understand
2. **Explicit ADG dependency** - Clear when ADG is generated
3. **Logical grouping** - Related checks combined
4. **Fast path for non-ADG changes** - No 95s penalty for simple changes
5. **Clear ordering** - Phases 0-5 with explicit dependencies

## Implementation Plan

1. Create combined hook scripts:
   - `ops_scripts/hooks/whitespace_normalize.py`
   - `ops_scripts/hooks/architectural_guards.py`
   - `ops_scripts/hooks/config_validation.py`
   - `ops_scripts/hooks/adg_unified_gate.py` (NEW - main ADG orchestrator)
     - Checks if ADG-relevant files changed
     - Runs `generate_full_adg.py --strict` if needed
     - Runs source-code checks: grep bans, skip-file ratchet
     - Does NOT duplicate P1/layer/burndown (already done by generate_full_adg.py)
   - `ops_scripts/hooks/purge_cache_and_report.py`

2. Update `.pre-commit-config.yaml` with new structure

3. Test with various change scenarios:
   - Non-ADG file change (no ADG generation, only source-code checks)
   - ADG file change (full ADG generation + source-code checks)
   - Config file change (ADG generation + source-code checks)

## Migration Strategy

1. Implement new hooks alongside existing ones
2. Gradually migrate to new structure
3. Remove old hooks once validated
4. Update documentation
