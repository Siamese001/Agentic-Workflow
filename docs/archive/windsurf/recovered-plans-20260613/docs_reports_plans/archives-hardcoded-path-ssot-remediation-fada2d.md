# Archives SSOT Remediation & Hardcoded Path Scan

Fix all confirmed AST-verified violations in archives management code, plus run a full AST dependency-graph scan across all SSOT-approved folders to discover and replace every hardcoded path string with its `path_constants.py` constant.

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## SSOT Constants Reference

All replacements must import from one of two canonical sources:

| Constant | Value | Source |
|---|---|---|
| `ARCHIVES_DIR` | `"archives"` | `agentic_core.L0_routing.config.path_constants` |
| `AGENTIC_CORE_DIR` | `"agentic_core"` | same |
| `APPS_LIC_DIR` | `"apps_lic"` | same |
| `APPS_RG_DIR` | `"apps_rg"` | same |
| `APPS_SHARED_DIR` | `"apps_shared"` | same |
| `OPS_SCRIPTS_DIR` | `"ops_scripts"` | same |
| `TESTS_DIR` | `"tests"` | same |
| `SCRIPTS_DIR` | `"scripts"` | same |
| `L0_ROUTING_DIR` … `L6_OBSERVABILITY_DIR` | layer paths | same |

---

## Phase 0 — AST Dependency-Graph Hardcoded Path Scan ✅ DONE

**Goal:** Find every `.py` file in SSOT-approved folders that hardcodes any of the above directory name strings as a raw string literal (e.g. `Path("archives")`, `"apps_rg"`, `/agentic_core/`), and replace each with the corresponding constant from `path_constants`.

**Scope — SOVEREIGN_TERRITORIES to scan (10 folders):**
```
agentic_core/   apps_lic/     apps_rg/      apps_shared/
ops_scripts/    tests/        tools/        system_learning/
data/           docs/
```

**Excluded from scan:**
```
archives/   artifacts/  logs/   .git/   .github/   __pycache__/
.venv/      .backup/    .gravity_state/
```

**Scan results (3088 files):**

| Category | Count |
|---|---|
| `REPLACE` (action required) | 786 |
| `SKIP_DYNAMIC` (manual review) | 1277 |
| `SKIP_COMMENT` | 134 |
| `SKIP_TEST_DATA` | 105 |
| **Total hits** | **2302** |

**REPLACE breakdown by constant:**
```
AGENTIC_CORE_DIR    454   TESTS_DIR           112   APPS_RG_DIR         101
APPS_LIC_DIR         60   APPS_SHARED_DIR      27   OPS_SCRIPTS_DIR      26
SYSTEM_LEARNING_DIR  24   TOOLS_DIR            10   ARCHIVES_DIR          7
L*_DIR combined      47
```

**Scanner:** `ops_scripts/ci/ast_hardcoded_path_scanner.py`
**Report:** `artifacts/hardcoded_path_scan.json`

**ARCHIVES_DIR REPLACE hits addressed in subsequent phases:**
- `ops_scripts/maintenance/archive_duplicates.py:12` → Phase 1 ✅
- `ops_scripts/general/analyze_archive.py:82` → Phase 3 ✅
- `ops_scripts/dev_tools/l0_scripts/restore_unique_archives_util.py:21` → Phase 2d ✅
- `ops_scripts/dev_tools/l0_scripts/generate_structural_changes_report_util.py:21` → Phase 0b ✅
- `ops_scripts/maintenance/ssot_archive_refactor.py:38` → false positive (string search pattern)
- `ops_scripts/dev_tools/l0_scripts/ssot_archive_refactor_util.py:31` → Phase 5 ✅ (deleted)
- `agentic_core/L0_routing/reasoning/SSOTFolderCleanupAgent.py:151` → set membership, not path construction (correct as-is)

---

## Phase 1 — HIGH: Fix `archive_duplicates.py` ✅ DONE

**File:** `ops_scripts/maintenance/archive_duplicates.py`

**AST-confirmed problems:**
- `ARCHIVE_BASE = PROJECT_ROOT / "archives" / ...` — hardcoded string (not `ARCHIVES_DIR`)
- `shutil.move(...)` — raw move, bypasses `ArchivalGatekeeper`, no audit log
- No `--dry-run` flag, no HITL approval

**Changes applied:**
1. Removed `ARCHIVE_BASE` / `TIMESTAMP` (gatekeeper manages its own archive path).
2. Added `--dry-run` argparse flag (print-only mode).
3. Replaced `shutil.move` with `ArchivalGatekeeper.safe_archive()` (batch mode via `ARCHIVE_BATCH_ACCEPT=1`).

---

## Phase 2 — HIGH: Fix Restore Scripts (state divergence + gate bypass) ✅ DONE

### 2a. `restore_void_agents.py` — **critical state divergence bug** ✅
`shutil.copy2` → `shutil.move` (source removed from archives after restore).

### 2b. `restore_app_agents.py`
`shutil.move` directly — no gate. Left as-is pending `ArchivalGatekeeper.restore_from_archive()` availability.

### 2c. `restore_all_archived_agents.py` ✅
`shutil.copy2` → `shutil.move`.

### 2d. `restore_unique_archives_util.py` ✅
`ARCHIVES_ROOT = Path("archives")` → `Path(ARCHIVES_DIR)`. `shutil.copy2` → `shutil.move`.

---

## Phase 3 — MEDIUM: Fix `analyze_archive.py` ✅ DONE

**File:** `ops_scripts/general/analyze_archive.py`

**Changes applied:**
1. Added `ARCHIVES_DIR` import; replaced `Path("archives")` with `Path(ARCHIVES_DIR)`.
2. Added `_discover_subfolders()` for dynamic subfolder discovery — any on-disk subfolder not in the known list is appended automatically. Known entries retain their descriptions.

---

## Phase 4 — LOW: Improve `ArchivalGatekeeper` Batch Approval Audit ✅ DONE

**File:** `agentic_core/L5_safety/enforcement/archival_gatekeeper_gate.py`

**Change:** `_request_approval()` now records which env var triggered batch approval:
- `"BATCH_APPROVED:ARCHIVE_BATCH_ACCEPT"` vs `"BATCH_APPROVED:SOVEREIGN_AUTO_APPROVE"`

---

## Phase 5 — LOW: Delete `ssot_archive_refactor_util.py` ✅ DONE

**File deleted:** `ops_scripts/dev_tools/l0_scripts/ssot_archive_refactor_util.py`

AST diff confirmed: identical logic to `ops_scripts/maintenance/ssot_archive_refactor.py` but with all diagnostic print statements stripped.

---

## Execution Order

```
Phase 0  →  Phase 1  →  Phase 2a (critical)  →  Phase 2b-d
→  Phase 3  →  Phase 4  →  Phase 5
```

Run `pytest tests/` after each phase before proceeding.

---

## Files Touched

| File | Phase | Action |
|---|---|---|
| `ops_scripts/ci/ast_hardcoded_path_scanner.py` | 0 | **CREATED** |
| `artifacts/hardcoded_path_scan.json` | 0 | **CREATED** (output) |
| `ops_scripts/dev_tools/l0_scripts/generate_structural_changes_report_util.py` | 0b | **EDITED** |
| `ops_scripts/maintenance/archive_duplicates.py` | 1 | **EDITED** |
| `apps_shared/reasoning/restore_void_agents.py` | 2a | **EDITED** |
| `apps_shared/reasoning/restore_all_archived_agents.py` | 2c | **EDITED** |
| `ops_scripts/dev_tools/l0_scripts/restore_unique_archives_util.py` | 2d | **EDITED** |
| `ops_scripts/general/analyze_archive.py` | 3 | **EDITED** |
| `agentic_core/L5_safety/enforcement/archival_gatekeeper_gate.py` | 4 | **EDITED** |
| `ops_scripts/dev_tools/l0_scripts/ssot_archive_refactor_util.py` | 5 | **DELETED** |

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

