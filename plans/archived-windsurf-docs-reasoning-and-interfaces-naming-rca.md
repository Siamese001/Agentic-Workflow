---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\reasoning-and-interfaces-naming-rca.md'
original_relative_path: 'reasoning-and-interfaces-naming-rca.md'
source_sha256: 6a78bcc5fcc9f35bc083139d3e40c4c2f9a69ec8aaa4bc50915f29f6dee4114c
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-03'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# RCA: Codebase Naming & Structure Audit

**Date:** 2026-03-03
**Scope:** Duplicate files, reasoning/ naming, interfaces/ convention, config/ structure, mixins placement

---

## 1. Byte-Identical Duplicate Files (23 groups deleted)

### Root Cause

Commit `04651c8e1` copied files to create naming-convention-compliant copies (e.g., `foo.py` → `foo_enforcer.py`) but **never deleted the originals**. This created byte-identical pairs where the suffixed copy had zero imports (dead code).

The same pattern that was previously fixed in `L5_safety/enforcement/` existed across **all layers**.

### Groups Deleted

| Category | Count | Layers | Pattern |
|----------|-------|--------|---------|
| enforcement duplicates | 18 | L1, L2, L3, L4, L6 | `foo.py` + `foo_enforcer.py` (byte-identical) |
| config duplicates | 2 | L2, L5 | `foo.py` + `foo_config.py` (byte-identical) |
| utils duplicates | 2 | L5 | Case/prefix variants (byte-identical) |
| runtime dupe | 1 | L5 | `fca_safety_gates_util.py` + `_fca_safety_gates_util.py` |

All 23 dead copies had **0 imports** across the codebase. The canonical (imported) file was retained in every case.

### Cascade Fix

`FileClassificationAgent.py` imported from `_fca_safety_gates_util` (deleted dead copy). Updated to import from `fca_safety_gates_util` (canonical).

---

## 2. project_root.py Rename (completed)

### Root Cause

`project_root.py` in `L0_routing/utils/` violated the `_util` suffix convention. It had a different-content sibling `project_root_util.py` — not a byte-identical duplicate. Compatibility aliases (`get_validated_project_root`, `PROJECT_ROOT_MARKERS`) were already added to `project_root_util.py` in the previous session.

### Remediation

- Updated 16 import references from `project_root` → `project_root_util`
- Deleted `project_root.py`
- Removed from `UTILS_SUFFIX_ALLOWLIST`
- Purity tests: 36/36 passing

---

## 3. reasoning/ Non-Agent Files

### Convention

`reasoning/` subdirectories must contain **only Agent files**: PascalCase filenames ending in `Agent`.

### Violations Found (not remediated — documenting only)

| File | Layer | Is Agent? | Issue |
|------|-------|-----------|-------|
| `CachedStateLedger.py` | L4_state | YES (extends SovereignBaseAgent) | Missing `Agent` suffix |
| `CheckpointManager.py` | L4_state | YES (extends SovereignBaseAgent) | Missing `Agent` suffix |
| `InspectorExecutor.py` | L5_safety | YES (extends SovereignBaseAgent) | Missing `Agent` suffix |
| `guardian_decision.py` | L5_safety | NO (dataclass + utility) | Non-agent misplaced in reasoning/ |

**Root cause:** Agent suffix dropped during consolidation commits. `guardian_decision.py` was misplaced during authority hardening (`ace6057e8`).

**Future remediation:** Rename 3 agents to add `Agent` suffix; relocate `guardian_decision.py` to `types/` or `enforcement/`.

---

## 4. interfaces/ Naming Convention (Option B — Accepted)

### Decision

**Accept the split.** Two architecturally distinct file types coexist in `interfaces/`:

| Type | Count | Naming | Purpose | Origin |
|------|-------|--------|---------|--------|
| Protocol definitions | 7 | `I*.py` (e.g., `IHealerProtocol.py`) | Abstract `typing.Protocol` contracts | `dcd37b699` (Kernel Hardening) |
| Re-export facades | 19 | `snake_case.py` (e.g., `gateway.py`) | Approved import boundaries for apps_* | `7a4b19c01` (sealed interface boundary) |

### Convention (documented)

- **I-prefixed files** = abstract Protocol/ABC definitions
- **snake_case files** = re-export facades providing approved import boundaries
- No renames required — 171 import references across 112 files preserved

---

## 5. mixins.py in interfaces/ — RCA

### Finding

`mixins.py` is a **re-export facade**, architecturally identical to the other 18 facade files in `interfaces/`. It re-exports `HealerMixin` and `MetaLearningMixin` from internal layers (`L5_safety`, `L1_cognition`) so `apps_*` can import from the approved boundary.

### Verdict

**Correctly placed** under Option B convention. It is not an abstract interface definition — it is a re-export boundary module with fallback stubs. Consistent with `gateway.py`, `spine.py`, `safety.py`, etc.

---

## 6. layer_hierarchy.json in config/ Root — RCA & Fix

### Root Cause

`layer_hierarchy.json` was placed in `agentic_core/config/` root alongside subfolders `agent_configs/` and `core/`. This violates the principle: **no files at folder root when subfolders exist** (files should be organized into the appropriate subfolder).

### Remediation

- Moved `config/layer_hierarchy.json` → `config/core/layer_hierarchy.json`
- Updated the 1 Python reference in `L5_safety/enforcement/hierarchy_validator_enforcer.py`
- Test files hardcode their own `LAYER_HIERARCHY` dicts (no JSON loading) — unaffected

---

## Summary

| Action | Count | Status |
|--------|-------|--------|
| Deleted byte-identical dead copies | 23 files | DONE |
| Fixed cascade import (fca_safety_gates) | 1 file | DONE |
| Renamed project_root.py → project_root_util.py | 16 imports + 1 delete | DONE |
| Moved layer_hierarchy.json to config/core/ | 1 move + 1 path update | DONE |
| Documented interfaces/ Option B convention | N/A | DONE |
| Documented mixins.py placement (correct) | N/A | DONE |
| Documented reasoning/ non-Agent files | 4 files | DOCUMENTED (future work) |

## Corrective Actions

[List the corrective actions taken to resolve the issue]

---

