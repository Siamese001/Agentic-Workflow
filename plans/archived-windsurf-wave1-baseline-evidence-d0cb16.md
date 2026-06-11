---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\wave1-baseline-evidence-d0cb16.md'
original_relative_path: 'wave1-baseline-evidence-d0cb16.md'
source_sha256: 60cf9013fdd6caf7cba8563ad94a18182990183686dd67397222a57373442df8
recovered_status: SURVIVED_IN_CURRENT
last_commit: '153652b9eb3'
last_commit_date: '2026-06-07 06:37:48 -0400'
created_date: '2026-04-04'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Wave 1 Baseline Evidence Snapshot

**Date:** 2026-04-04
**Wave:** W1-P2 Baseline Evidence Snapshot

## Current State Inventory

### Top-level `tests/` folders (35 total)

```
_config, _quarantine, adg, apps_eval, apps_exec, apps_research, apps_rfp, apps_rg,
architecture, audit, ci, contracts, e2e, e2e_data, evaluation, fixtures, governance,
guardian, helpers, infrastructure, integration, integration_full_deps, knowledge, misc,
ops_scripts, performance, reasoning, smoke, sovereign_hardening, stress, system,
system_learning, tools, unit
```

**Low-signal lanes to remove from SSOT:**
- `misc`, `contracts`, `fixtures`, `helpers`, `stress`, `sovereign_hardening`
- `audit`, `reasoning`, `system`, `tools`, `knowledge` (re-home by type)

### `tests/unit/` subfolders (19 total)

```
L0_routing, agentic_core, apps_eval, apps_exec, apps_lic, apps_research, apps_rfp,
apps_rg, apps_shared, ci, consolidated, evaluation, knowledge, ops_scripts,
prompt_governance, system_learning, tools, windsurf
```

**Overlaps with top-level:** `apps_eval`, `apps_exec`, `apps_research`, `apps_rfp`, `apps_rg`, `ci`, `evaluation`, `knowledge`, `ops_scripts`, `system_learning`, `tools`

### `tests/architecture/` files (26 total)

All files:
- `test_adg_branches_and_robustness.py`
- `test_adg_composition_graph.py`
- `test_adg_digest_stable.py`
- `test_adg_enhancements_6_10.py`
- `test_adg_gap_coverage.py`
- `test_adg_inheritance_graph.py`
- `test_adg_invariants.py`
- `test_adg_negative_controls.py`
- `test_adg_p1_enhancements.py` through `test_adg_p5_enhancements.py`
- `test_apps_rationalization_verification.py`
- `test_contracts_fixture_placement.py`
- `test_cross_cutting_invariants.py`
- `test_discovery_cache.py`
- `test_hierarchy_agent_invariants.py`
- `test_injection_canon_completeness.py`
- `test_new_cache_opportunities.py`
- `test_no_legacy_shells.py`
- `test_phantom_folder_regression.py`
- `test_redis_cache_non_authoritative.py`
- `test_redis_cache_wiring_invariants.py`
- `test_sovereign_territories_migration_verification.py`

### Consolidation targets

| Source | Target | Files |
|--------|--------|-------|
| `tests/unit/consolidated/unit_min_deps/` | `tests/unit_min_deps/` | 20+ files |
| `tests/integration_full_deps/` | `tests/integration/` (re-home) | 1 file: `test_seed_pack_full_build_b5.py` |

## Drift Summary

1. **SSOT gaps:** Low-signal lanes still in SSOT
2. **Missing:** `tests/unit_min_deps/` folder (needs creation)
3. **Duplication:** `unit_min_deps` exists in two locations
4. **Overlap:** 11 folders appear in both top-level and `tests/unit/`
5. **Placeholder risk:** `tests/architecture/` has 26 files needing audit
