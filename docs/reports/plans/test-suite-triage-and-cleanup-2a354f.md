# Test Suite Triage, Cleanup & Hardening Plan

6-wave plan to triage 3,155 test files — deleting 1,130+ stubs/artifacts, using ADG fan-in/fan-out to retain high-value tests, and fixing failures.

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|--------|
| Wave 0 | 49 deletions | phase/wave files + demo dir | A | 150 🟢 |
| Wave 1 | 700-800 deletions | ADG stub triage | B | 600 🟢 |
| Wave 2 | Fix/delete failures | failing test assessment | C | 500 🟢 |
| Wave 3 | 250-350 populated | high-value stubs | D | 800 🟢 |
| Wave 4 | <30 skips | skip marker cleanup | E | 200 🟢 |
| Wave 5 | Dir rationalization | structure cleanup | F | 150 🟢 |

**Total: 2,400 tokens across 6 waves, all GREEN**

---

## Current State (Inventory)

| Category | Count | Action |
|----------|-------|--------|
| Total test files | 3,155 | — |
| `_adg.py` import-only stubs (≤2 tests, just `test_module_importable`) | 1,087 | Triage via ADG fan-in |
| `_adg.py` non-stub (real tests) | 716 | Keep, assess |
| Low-signal filenames (phase/wave prefix) | 43 | **Delete all** |
| `unit_min_deps_wave1_demo/` directory | 6 files | **Delete entire dir** |
| Files with skip markers | 43 | Assess & fix or delete |
| Files with placeholder/pass bodies | ~944 | Triage per wave |

---

## ADG Runtime Proxy Strategy

Static ADG cannot trace runtime imports. We use **ADG fan-in/fan-out as a proxy**:
- `adg_edge_fanin(node, "imports")` — who imports this module (consumers)
- `adg_edge_fanout(node, "calls")` — what this module calls (dependencies)
- Modules with **fan-in ≥ 5** → high-value (many consumers → breakage risk) → **KEEP test**
- Modules with **fan-in 1-4** in `agentic_core/` → **KEEP**, else **DELETE**
- Modules with **fan-in = 0** and no `calls` edges → likely dead/orphaned → **DELETE test**

---

## Execution Plan

### Wave 0: Housekeeping Deletes (no ADG needed)

**Scope:** 43 phase/wave files + 6 demo files  
**Estimated deletions:** ~49 files

1. Delete all 43 low-signal phase/wave-named test files:
   - `tests/unit/test_phase21_basic.py` through `test_phase24_*`
   - `tests/unit/test_wave30_guardian_sweep.py`, `test_wave40_final_validation.py`
   - `tests/architecture/test_wave1_phase1_*.py` through `test_wave3_phase3_*.py`
   - `tests/infrastructure/test_wave8_final_validation.py`
   - `tests/performance/test_wave1_cpu_optimization.py`, `test_wave2_adg_parallel.py`
   - `tests/integration/test_wave4_simple_integration.py`
   - `tests/agentic_core/test_wave4_wave5_wave6_guardrails.py`
   - `tests/unit/agentic_core/adg/extraction/test_static_scanner_wave2.py`, `test_wave1_scanner_fixes.py`
   - `tests/unit/ml_decision_support/test_phase1_components.py` through `test_phase4_components.py`
   - `tests/system_learning/test_healing_backups_rca_waves.py`
2. Delete entire `tests/unit_min_deps_wave1_demo/` directory
3. Delete `tests/EVIDENCE_test_dedup_consolidation_P1.md`

**Acceptance:** `pytest --collect-only` shows no collection errors from deleted files

### Wave 1: ADG-Driven Stub Triage (1,087 files)

**Scope:** All `_adg.py` import-only stubs  
**Tool:** Python script querying ADG SQLite for fan-in per target module

1. **Build triage script** (`tools/evidence/_triage_adg_stubs.py`):
   - For each stub, extract target module from its import statement
   - Query ADG edges table for fan-in count
   - Classify: KEEP (high fan-in) vs DELETE (low/zero fan-in)
   - Output: `artifacts/test_triage/adg_stub_triage.json`

2. **Execute deletions** — delete all stubs classified as DELETE (~700-800 estimated)

3. **Keep list** (~250-350 estimated) — retained for Wave 3 population

**Acceptance:** Review triage JSON, then bulk delete; verify counts match targets

### Wave 2: Failing Test Assessment

**Scope:** Remaining non-stub tests that fail

1. Run `pytest --collect-only` to identify collection errors
2. Categorize failures:
   - **Import errors** (module moved/deleted) → delete or fix
   - **Assertion rot** (outdated values) → fix or delete
   - **Missing deps** → skip with reason or fix
   - **Runtime errors** → fix if high-value, else delete
3. Sub-waves:
   - 2a: Delete tests whose target module no longer exists
   - 2b: Fix import paths for moved modules
   - 2c: Fix assertion rot in high-value tests
   - 2d: Add proper skip markers for infra-dependent tests

**Acceptance:** `pytest --tb=short -q` — track pass/fail/skip counts

### Wave 3: Populate High-Value Stubs

**Scope:** ~250-350 surviving stubs from Wave 1 KEEP list

1. Use ADG fan-out to understand each module's exports/calls/layer
2. Generate meaningful test skeletons by module type:
   - **Config** → test valid types/ranges
   - **Engine** → test init, method signatures, error handling
   - **Agent** → test class exists, has `execute()`, basic mock
   - **Validator** → test with valid/invalid inputs
3. Batch by directory (apps_lic, apps_rg, agentic_core, etc.)

**Acceptance:** All new tests must pass

### Wave 4: Skip Marker Cleanup

**Scope:** 43 files with 168 skip markers

1. Audit each skip reason for validity
2. Remove invalid skips, fix underlying issue
3. Move permanently-blocked tests to `tests/_quarantine/` with manifest entry

**Acceptance:** `pytest -rs` — all remaining skips documented

### Wave 5: Directory Structure Rationalization

1. Merge `tests/unit_min_deps/` into `tests/unit/` where appropriate
2. Consolidate `tests/hardening/`, `tests/invariants/`, `tests/ssot_equivalence/`
3. Remove empty directories from prior waves

**Acceptance:** Clean `pytest --collect-only`

---

## Rules

1. **ADG-driven triage** — Use fan-in/fan-out as proxy for runtime import knowledge
2. **Delete first** — Remove stubs before populating to reduce noise
3. **High-value retention** — Keep tests for modules with fan-in ≥ 5 or in agentic_core
4. **No partial commits** — Each wave must be complete before next
5. **Evidence-backed** — All deletions must show target module is low-value via ADG

---

## Success Criteria

| Metric | Before | Target | Verification |
|--------|--------|--------|--------------|
| Total test files | 3,155 | ~1,800-2,000 | `find tests -name "test_*.py" \| wc -l` |
| Import-only stubs | 1,087 | 0 (deleted or populated) | ADG triage JSON |
| Phase/wave-named files | 43 | 0 | File search |
| Collection errors | TBD | 0 | `pytest --collect-only` |
| Skip markers | 168 | <30 (valid reasons) | `pytest -rs` |
| Pass rate (non-skipped) | TBD | >95% | `pytest --tb=short` |

---

## Implementation Commands

```bash
# Wave 0: Delete phase/wave files
python tools/evidence/delete_phase_wave_test_files.py --dry-run
python tools/evidence/delete_phase_wave_test_files.py --execute

# Wave 1: ADG stub triage
python tools/evidence/_triage_adg_stubs.py --output artifacts/test_triage/adg_stub_triage.json
python tools/evidence/bulk_delete_stubs.py --input artifacts/test_triage/adg_stub_triage.json

# Wave 2: Assess failing tests
pytest --collect-only 2>&1 | tee artifacts/test_collection_errors.txt
python tools/evidence/classify_test_failures.py --input artifacts/test_collection_errors.txt

# Wave 3: Populate stubs (incremental, multi-session)
python tools/evidence/populate_high_value_stubs.py --batch apps_lic
python tools/evidence/populate_high_value_stubs.py --batch apps_rg
python tools/evidence/populate_high_value_stubs.py --batch agentic_core

# Wave 4: Skip cleanup
python tools/evidence/audit_skip_markers.py --fix

# Wave 5: Directory cleanup
python tools/evidence/rationalize_test_dirs.py

# Final validation
python tools/ci_validate_plans.py  # Validates this plan has proper wave table + tokens
```

---

## Rollback Strategy

If things go wrong:
1. Restore deleted files from git: `git checkout tests/unit/test_phase21_basic.py ...`
2. Revert stub deletions: `git checkout tests/unit/apps_lic/reasoning/test_*_adg.py`
3. Re-run collection check: `pytest --collect-only`
4. If scope contamination detected, reset to baseline per §4.2

---

## Acceptance Criteria

| Wave | Criteria | Verification |
|------|----------|--------------|
| Wave 0 | 49 files deleted, no collection errors | `pytest --collect-only` passes |
| Wave 1 | ~750 stubs deleted, ~300 kept | `adg_stub_triage.json` shows counts |
| Wave 2 | All collection errors resolved | Zero collection errors |
| Wave 3 | All kept stubs have ≥3 real tests | Spot-check _adg.py files |
| Wave 4 | <30 skips with documented reasons | `pytest -rs` output |
| Wave 5 | Clean directory structure | No empty dirs, logical organization |
