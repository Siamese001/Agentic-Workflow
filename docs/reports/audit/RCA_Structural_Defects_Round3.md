# RCA: knowledge/ Structure, config/ Subfolders, LocalDiskAdapter, Validator Alignment, L0/scripts Dump

**Date:** 2026-02-07
**Severity:** Medium-High (structural misplacement, naming violations, dumping ground)
**Scope:** 7 files fixed, 4 blueprint rules hardened

---

## Issue 1: `knowledge/document_loaders/` PascalCase Files

**Symptom:** `ResearchCache.py` and `SourceDocument.py` use PascalCase in `document_loaders/` — a non-agent folder.

**Root cause:** Both files were restored from archived drift (`archives/unmapped_drift/`). The restoration preserved the original PascalCase class-name-as-filename convention. No `validate_pascal_case_placement()` existed at the time to reject PascalCase in non-agent folders.

- `ResearchCache.py` — contains `class ResearchCache`, a file-based JSONL cache. Not an agent.
- `SourceDocument.py` — contains `class SourceDocument(BaseEntity)` and `class KnowledgeChunk(BaseEntity)`. Pydantic types.

**Fix:**
- `ResearchCache.py` → `research_cache.py` (snake_case utility class)
- `SourceDocument.py` → `source_document_types.py` (types suffix for Pydantic models)
- Fixed hardcoded `"ResearchCache"` directory path in `rag_orchestrator.py` → `"research_cache"`

**Additional knowledge/ issues found and fixed:**
- `reasoning/` subfolder existed on disk but was missing from `CORE_SUBFOLDER_MAP` → added
- `engine/` and `healing/` also missing from blueprint → added all 3

---

## Issue 2: `agentic_core/config/` Subfolders

**Symptom:** Config root has 7 .py files alongside `core/` (10 .py + 1 .json) and `agent_configs/` (12 .yaml). Are subfolders needed?

**Analysis:**

| Folder | Contents | Purpose |
|--------|----------|---------|
| Root | 7 .py files | Feature-specific configs (colors, gateway, injection, etc.) |
| `core/` | 10 .py + `golden_baseline.json` (275KB) | Infrastructure configs (sovereign, constants, registry) |
| `agent_configs/` | 12 .yaml files | Agent behavior YAML definitions |

**Recommendation: Keep current structure.** The split is functional:
- Root = feature configs (change often)
- `core/` = infrastructure configs + large JSON baseline (stable)
- `agent_configs/` = YAML (different file type, different consumers)

Flattening would put 30+ files in one directory with mixed Python/YAML/JSON — harder to navigate.

**Fix:** Added `agent_configs` to `CORE_SUBFOLDER_MAP["config"]` — it existed on disk but was missing from the blueprint, causing subfolder violation flags.

---

## Issue 3: `L4_state/enforcement/LocalDiskAdapter.py`

**Symptom:** PascalCase file in `enforcement/` that's not an enforcement mechanism.

**Root cause:** In the Adapter Classification RCA, we renamed `local_disk_adapter.py` → `LocalDiskAdapter.py` for PascalCase compliance (adapters get PascalCase). But `enforcement/` is wrong — `LocalDiskAdapter` wraps filesystem I/O for state persistence. It's a **storage utility**, not enforcement.

The original `"ADAPTER": "enforcement"` hardcoding (since removed) placed it in enforcement/. The Adapter RCA fixed the naming but didn't challenge the folder placement.

**Fix:** Moved `L4_state/enforcement/LocalDiskAdapter.py` → `L4_state/utils/local_disk_adapter_util.py`. Now in the correct domain folder with snake_case naming (PascalCase is only for files in reasoning/enforcement/base_agents/mixins).

---

## Issue 4: No L0 Validators? + Misplaced Validators in L0/scripts

**Symptom:** L0 appears to have no `validators/` folder. L4 has only 1 validator. Meanwhile, L0/scripts has 3 `_validator.py` files.

**Analysis:**
- L0 **DOES** have a `validators/` folder (confirmed)
- The 3 validators in L0/scripts are **misnamed** — they're not actual validators:
  - `budget_auditor_validator.py` → 81-line utility class tracking token spend (UTILITY, not VALIDATOR)
  - `routing_decision_validator.py` → 760-line routing script with AST analysis (SCRIPT)
  - `full_agent_discovery_validator.py` → 686-line discovery script with AST analysis (SCRIPT)

**Root cause:** The `_validator.py` suffix was applied by a healing pass that detected validation-like keywords in the content. But these files validate as a VERB (they perform validation actions) — they are not VALIDATOR as a NOUN (reusable validation components). The FCA's suffix-based classification can't distinguish verb-vs-noun usage.

**Validator distribution across layers:**
| Layer | Count | Status |
|-------|-------|--------|
| L0_maintenance | exists (folder) | Validators present in separate folder |
| L1_cognition | 6 | ✓ |
| L3_orchestration | 1 | ✓ |
| L4_state | 1 | ✓ (low count is normal — L4 is state, not safety) |
| L5_safety | 30+ | ✓ (expected — safety is the validation layer) |

L0 and L4 having few validators is **architecturally correct**. Validators concentrate in L5 (safety) where validation is the core purpose. L0 (maintenance) does validation as a side effect of scripts, not as primary purpose.

**Fix:** Renamed the 3 misnamed files:
- `budget_auditor_validator.py` → `budget_auditor_util.py`
- `routing_decision_validator.py` → `routing_decision_script.py`
- `full_agent_discovery_validator.py` → `full_agent_discovery_script.py`

---

## Issue 5: `L0_maintenance/scripts/` is a Dumping Ground

**Symptom:** ~280 files including PascalCase agents, test files, misnamed validators, non-Python artifacts (.sh, .ps1, .html, .yml, .json, .dockerignore, etc.), and a 116KB monolith script.

**Root cause:** Multiple converging factors:
1. **FCA routes `_script.py` → scripts/** — but many L0 utilities also have `_util.py` suffix, and healing passes put them in scripts/ as a "catch-all"
2. **No purity enforcement** — `FOLDER_PURITY_RULES["scripts"]` only checked for `_script.py`, so `_util.py` files were never flagged as violations (they were silently accepted)
3. **PascalCase agents dumped** — 8 PascalCase files (`AgentAuditResult.py`, `BatchEmbeddingService.py`, etc.) were placed in scripts/ by healing passes that couldn't find a better home
4. **Non-Python artifacts** — workspace files, shell scripts, Dockerfiles, HTML test pages accumulated over time

**Hardening applied:**
- Expanded `FOLDER_PURITY_RULES["scripts"]` to include `_util.py` pattern (legitimizes the ~150 existing utils, prevents false eviction)
- The `validate_pascal_case_placement()` method (added in prior RCA) now catches PascalCase files in scripts/
- The `[MISPLACED-TEST]` warning (added in prior RCA) catches test files in scripts/

**Remaining debt (out of scope):**
- 8 PascalCase files in scripts/ need manual triage (each needs content analysis to determine correct layer)
- Non-Python files need NON_PYTHON_FOLDER_ROUTES rules for scripts/
- Consider splitting L0/scripts into L0/scripts + L0/utils when file count justifies it

---

## Summary of All Changes

| File | Action | Detail |
|------|--------|--------|
| `knowledge/document_loaders/ResearchCache.py` | **Renamed** | → `research_cache.py` (snake_case) |
| `knowledge/document_loaders/SourceDocument.py` | **Renamed** | → `source_document_types.py` (types suffix) |
| `knowledge/engine/rag_orchestrator.py` | **Fixed path** | Hardcoded `"ResearchCache"` → `"research_cache"` |
| `L4_state/enforcement/LocalDiskAdapter.py` | **Moved+Renamed** | → `L4_state/utils/local_disk_adapter_util.py` |
| `L0/scripts/budget_auditor_validator.py` | **Renamed** | → `budget_auditor_util.py` (not a validator) |
| `L0/scripts/routing_decision_validator.py` | **Renamed** | → `routing_decision_script.py` |
| `L0/scripts/full_agent_discovery_validator.py` | **Renamed** | → `full_agent_discovery_script.py` |
| `structure_blueprint_config.py` | **Hardened** | +knowledge subfolders, +agent_configs, +scripts purity |
