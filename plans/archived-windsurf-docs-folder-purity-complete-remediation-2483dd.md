---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\folder-purity-complete-remediation-2483dd.md'
original_relative_path: 'folder-purity-complete-remediation-2483dd.md'
source_sha256: 66f7b66387add7f5e3de4bb6c8250e2958a6235e008e307fbb54aa20bad06f40
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-17'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Folder Purity Complete Remediation Plan

This plan systematically fixes all folder purity violations across agentic_core and apps_* folders by renaming/moving files to match strict naming conventions, one folder at a time to maintain manageable scope.

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Current Status
- **validators**: ✅ FIXED (2 files renamed)
- **Remaining folders**: 7 folders with 222 total violations
  - reasoning: 9 files
  - config: 2 files
  - types: 23 files
  - utils: 12 files
  - enforcement: 71 files
  - engines: 28 files
  - tools: 77 files

## Phase 1: agentic_core Folder Remediation (7 waves)

### Wave 1.1: config folder (2 files)
**Target**: Files without `_config.py` suffix
- `agentic_core/L2_execution/config/mcp_registry.py` → `mcp_config.py`
- `agentic_core/L5_safety/config/blueprint_compiler.py` → `blueprint_config.py`
**Actions**: Rename files, update imports

### Wave 1.2: utils folder (12 files)
**Target**: Files without `_util.py` or `_helper.py` suffix
- Rename all files to add appropriate suffix based on function
- Examples:
  - `guardrails.py` → `guardrails_util.py`
  - `history_merger.py` → `history_merger_util.py`
  - `ConstitutionalOverseer.py` → `constitutional_overseer_util.py`
**Actions**: Rename files, update imports

### Wave 1.3: types folder (23 files)
**Target**: Files without `_types.py`, `_protocol.py`, `Error.py`, or `Exception.py` suffix
- Rename contracts to `_types.py`
- Rename protocols to `_protocol.py` or `I*Protocol.py`
- Move actual errors/exceptions if needed
**Actions**: Rename files, update imports

### Wave 1.4: reasoning folder (9 files)
**Target**: Files without Agent/Executor/Orchestrator/Inspector/Healer/Guardian suffix
- Move Strategy files to enforcement/
- Rename or move non-Agent files
**Actions**: Move files, rename as needed, update imports

### Wave 1.5: enforcement folder (71 files)
**Target**: Files without allowed suffixes
- Add appropriate suffixes based on function:
  - `_guardrail.py`, `_enforcer.py`, `_gate.py`, `_strategy.py`
  - `Strategy.py`, `Adapter.py`, `Monitor.py`, `Factory.py`, `Gateway.py`
**Actions**: Rename files, update imports

### Wave 1.6: engines folder (28 files)
**Target**: Files without `_engine.py`, `_executor.py`, or other allowed suffixes
- Rename to match function (e.g., `cache_manager.py` → `cache_engine.py`)
**Actions**: Rename files, update imports

### Wave 1.7: tools folder (77 files)
**Target**: Files without `_tool.py`, `_impl.py`, or `_client.py` suffix
- Rename PascalCase tools to add `_tool.py` suffix
- Move any non-tool files to appropriate folders
**Actions**: Rename files, update imports

## Phase 2: apps_* Folder Remediation (3 waves)

### Wave 2.1: apps_* reasoning/config/types/utils (small scopes)
**Target**: Remaining violations in apps_* core folders
- reasoning: Move Strategy files to enforcement, rename others
- config: Add `_config.py` suffix
- types: Add `_types.py` suffix
- utils: Add `_util.py` suffix
**Actions**: Rename/move files, update imports

### Wave 2.2: apps_* enforcement/engines (medium scopes)
**Target**: Strategy and engine files in apps_*
- enforcement: Add proper suffixes
- engines: Add `_engine.py` suffix or move to reasoning if Agent
**Actions**: Rename files, update imports

### Wave 2.3: apps_* tools (large scope - 76 files)
**Target**: All tools in apps_* folders
- Rename PascalCase tools to add `_tool.py` suffix
- Ensure all tools follow naming convention
**Actions**: Batch rename files, update imports

## Phase 3: Final Verification (2 waves)

### Wave 3.1: Import Cleanup
**Target**: Fix all broken imports from renames
- Search for old module names
- Update import statements
- Verify no broken references remain

### Wave 3.2: Full Test Suite
**Target**: Verify all invariants pass
- Run `python -m pytest -q tests/enforcement/test_folder_purity_invariants.py`
- Run `pre-commit run --all-files`
- Ensure zero failures

## Constraints & Rules
1. **No rule widening** - Only rename/move files to match existing strict rules
2. **One folder at a time** - Complete each wave before proceeding
3. **Deterministic moves** - Use `git mv` for all moves
4. **Import updates** - Always update imports after renames
5. **Green gates** - Each wave must pass tests before commit

## Success Criteria
- All 222 violations eliminated
- `python -m pytest -q` passes with 0 failures
- `pre-commit run --all-files` passes
- Folder purity invariants run by default and pass

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

