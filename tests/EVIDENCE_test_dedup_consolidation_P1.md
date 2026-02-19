# Phase 1 / Wave 1 — Baseline + Manifest Generation

## Branch

```
test_consolidation (off main)
```

## Scope Declaration

Files added this wave:
- `tests/scripts/generate_unit_mirror_manifest.py` (new)
- `tests/scripts/manifest_unit_mirror_duplicates.json` (new)
- `tests/EVIDENCE_test_dedup_consolidation_P1.md` (this file)

No production code edits. No test deletions.

---

## Wave 1 Step 1 — git status --porcelain (pre-wave)

```
Command: git status --porcelain
Output:
?? tests_filelist.txt
Branch: test_consolidation
```

---

## Wave 1 Step 2 — Baseline collect-only

```
Command: python -m pytest -q tests/unit_min_deps tests/integration/agentic_core tests/enforcement tests/governance --collect-only
```

Tail of output:
```
======================== 917 tests collected in 0.53s =========================
```

**Baseline collect count: 917**

---

## Wave 1 Step 3 — Baseline pytest run

```
Command: python -m pytest -q tests/unit_min_deps tests/integration/agentic_core tests/enforcement tests/governance
```

Tail of output:
```
✅ GUARDIAN STATUS: PASS
All architectural integrity checks passed.
================= 841 passed, 4 warnings in 73.83s (0:01:13) ==================
```

**Baseline: 841 passed, 0 failed, 4 warnings**

Note: pytest.ini testpaths = tests/unit_min_deps, tests/integration/agentic_core,
tests/enforcement, tests/governance. tests/unit/** is NOT in the authoritative suite.

---

## Wave 1 Step 4 — Manifest Generation

```
Command: python tests/scripts/generate_unit_mirror_manifest.py
```

Output:
```
Manifest written to: tests/scripts/manifest_unit_mirror_duplicates.json
  identical_count   : 482
  different_count   : 33
  unit_only_count   : 266
  canonical_only_cnt: 1505
  total_pairs       : 515
```

### Manifest Summary

| Category | Count |
|---|---|
| identical (byte-for-byte) | 482 |
| different (near-duplicate) | 33 |
| unit-only (no canonical counterpart) | 266 |
| canonical-only (no unit counterpart) | 1505 |
| total pairs compared | 515 |

Stale rename map applied: `L0_maintenance` → `L0_routing`

### Mirror Subtrees Compared

- `tests/unit/agentic_core` vs `tests/agentic_core`
- `tests/unit/apps_lic` vs `tests/apps_lic`
- `tests/unit/apps_rg` vs `tests/apps_rg`
- `tests/unit/apps_shared` vs `tests/apps_shared`

### "Different" Pairs — All 33 Files

All 33 "different" pairs were inspected via `git diff --no-index`. Pattern:
- Unit copies have **commented-out imports** and degraded class stubs
- Canonical top-level files have **real imports** and full class definitions
- Canonical files are strictly stronger — no unique assertions exist in unit copies
- No merge of unit→canonical content is required

Representative diff (test_healer_interface.py):
```diff
-from agentic_core.base_agents.HealerProtocol import (
-    HEAL_RESULT_SCHEMA,
-    HealerAgentMixin,
-    LegacyAgentAdapter,
-)
+# from agentic_core.base_agents.HealerProtocol import (
+#     HEAL_RESULT_SCHEMA,
+#     HealerAgentMixin,
+#     LegacyAgentAdapter,
+# )
```

Representative diff (test_detection_protocol.py):
```diff
-from agentic_core.utils.detection_protocol import (
-    DetectionRequest, DetectionResult, DetectionSignalProtocol, Severity,
-)
+# Placeholder types for testing
+DetectionRequest = Any
+DetectionResult = Any
```

**Conclusion**: Canonical top-level files are the correct canonical copies.
Unit copies are degraded stubs. Wave 2 will delete unit copies, keeping canonical.

### "Unit-Only" Files — 266 Files

These exist in `tests/unit/<subtree>` but have no counterpart in `tests/<subtree>`.
Breakdown includes:
- Many `__init__.py` files (namespace packages)
- `tests/unit/agentic_core/L0_maintenance/**` → will migrate to `tests/agentic_core/L0_routing/**`
- `tests/unit/agentic_core/context_engineering/` subtree
- `tests/unit/agentic_core/L1_cognition/thought_engine/` subtree
- `tests/unit/consolidation/`, `tests/unit/dedup/`, `tests/unit/core/`, etc.
- `tests/unit/file_classification_agent/` subtree
- `tests/unit/structure_blueprint/` subtree
- `tests/unit/L5_safety/` subtree
- `tests/unit/docs/`, `tests/unit/anomaly_tests/`

### Namespace Findings

- `tests/_helpers/` (3 files): `__init__.py`, `robust_fs.py`, `test_robust_fs.py`
- `tests/helpers/` (5 files): `__init__.py`, `assertions.py`, `dev_tools_loader.py`, `repo_builder.py`, `write_module.py`
- No overlap — different content. Wave 2 will move `_helpers/` files into `helpers/`.

- `tests/_contracts/` (6 files): yaml/json/py contracts
- `tests/contracts/` (11 files): different contract tests
- No overlap — different content. Wave 2 will move `_contracts/` files into `contracts/`.

---

## Wave 1 Commit Scope

Files staged:
1. `tests/scripts/generate_unit_mirror_manifest.py`
2. `tests/scripts/manifest_unit_mirror_duplicates.json`
3. `tests/EVIDENCE_test_dedup_consolidation_P1.md`

---

<!-- Wave 2 and Wave 3 sections appended below after execution -->
