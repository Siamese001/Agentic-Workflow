# FCA SSOT Consolidation: Eliminate Duplicate File Classification Logic

Consolidate all file classification and agent detection logic across the repository to delegate to the single SSOT: `FileClassificationAgent.classify_file()`.

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


## Findings

### The Problem
The codebase has **15+ files** with independent agent/file classification logic that diverges from the SSOT (`FileClassificationAgent.py`). This caused the 397-agent overcount (now fixed to 190). The root cause is organic growth — each script/agent invented its own "is this an agent?" check instead of importing from FCA.

### Competing SSOT Claims
Three files claim or act as SSOT for agent discovery:

| File | Claim | Agent Definition |
|------|-------|-----------------|
| `L5_safety/reasoning/FileClassificationAgent.py` | **True SSOT** — 18 FileTypes, AST priority queue | Primary class `endswith("Agent")` OR inherits from `*Agent`, after excluding STUB/ORCHESTRATOR/STRATEGY/MIXIN/PROTOCOL/etc. |
| `L0_maintenance/utils/complexity_visitor_util.py` | Header says "CANONICAL AST AGENT DISCOVERY - SINGLE SOURCE OF TRUTH" | Multi-layer scoring: `endswith("Agent")` + healing chain MRO + base class matching + infrastructure exclusion lists |
| `L0_maintenance/scripts/full_agent_discovery.py` | `analyze_agent_integrity()` with `class_score()` | Point-based: SovereignBaseAgent=100, "Agent" in name=10, heal method=20, execute/run/act=8 |

### Category 1: Duplicate `_is_agent_class()` / `is_agent()` Definitions (5 files)

| File | Function | Definition | Divergence from FCA |
|------|----------|-----------|-------------------|
| `runtime/utils/discovery_util.py` | `AgentRegistry._is_agent_class()` | `endswith("Agent")` + 6 agent methods + inheritance | Includes `process`, `handle`, `validate` as agent methods; no priority ordering; no type exclusions |
| `prompt_governance/scripts/file_intent.py` | `_is_agent_class()` + `_inherits_from_agent()` | `endswith("Agent")` + docstring keywords (`validator`, `governor`, `healer`) | Docstring-based classification not in FCA; counts validators/healers as agents |
| `L5_safety/validators/type_erasure_validator.py` | `_is_agent_class()` | `"Agent" in name` OR `"Validator" in name` | Matches "Agent" **anywhere** in name (not just suffix); incorrectly classifies Validators as agents |
| `L0_maintenance/utils/complexity_visitor_util.py` | `is_agent_class()` (~200 lines) | Multi-layer scoring with infrastructure exclusions, healing chain MRO | Completely independent implementation; different exclusion lists; claims to be SSOT |
| `L0_maintenance/scripts/full_agent_discovery.py` | `analyze_agent_integrity()` + `class_score()` | Point-based scoring (SovereignBaseAgent=100, Agent in name=10) | Different scoring model; no FileType awareness; caused 397→190 discrepancy |

### Category 2: Duplicate `classify_file()` Definitions (3 files, 1 already fixed)

| File | Status | Notes |
|------|--------|-------|
| `L0_maintenance/scripts/pascal_sovereignty_fixer.py` | **FIXED** — delegates to FCA | Completed in FCA Dedup Refactor |
| `ops_scripts/maintenance/run_classification.py` | **FULL REIMPLEMENTATION** | Own STUB/test/script/types/class detection; different priority ordering and type list |
| `L0_maintenance/scripts/class_info.py` | Different purpose (archive classification) | Name collision only — keep but rename to `classify_archive_file()` |
| `L0_maintenance/scripts/analyze_app_files_util.py` | Different purpose (domain classification) | Name collision only — keep but rename to `classify_app_domain()` |

### Category 3: Inline `endswith("Agent")` Checks (12+ files)

**Enforcement scripts** (4 files):
- `L5_safety/enforcement/ssot_scanner_enforcer.py` — `node.name.endswith("Agent")`
- `L5_safety/enforcement/registry_verification_enforcer.py` — `node.name.endswith("Agent")`
- `L5_safety/enforcement/data_enforcer.py` — `not name.endswith("Agent")`
- `L5_safety/enforcement/ssot_structure_validation_enforcer.py` — `class_name.endswith("BaseAgent")`

**Test files** (8+ files):
- `tests/integration/test_repo_scan_no_agents_outside_reasoning.py` — 4 inline checks
- `tests/guardian/test_ssot_alignment.py` — 3 inline checks
- `tests/guardian/test_architecture_governance.py` — 2 inline checks
- `tests/guardian/test_agent_validation.py`, `test_agent_autonomy.py`, `test_forensic_audit_unified.py`, `test_subatomic_compliance.py`, `tests/helpers/assertions.py`

### Category 4: Filename-Only Agent Detection (3 utility scripts)

| File | Check | Problem |
|------|-------|---------|
| `L0_maintenance/scripts/extract_agent_duplicates_util.py` | `path.endswith("Agent.py")` | Misses agents in non-PascalCase files |
| `L0_maintenance/scripts/find_real_duplicates_v2_util.py` | `path.name.endswith("Agent.py")` | Same |
| `L0_maintenance/scripts/generate_agent_table_simple_util.py` | `path.endswith("Agent.py")` | Same |

---

## Implementation Plan

### Phase 0: Create Shared Lightweight API (Prerequisite)
**Goal**: Expose FCA classification without requiring full agent instantiation.

1. Add a module-level function to `FileClassificationAgent.py`:
   ```python
   def classify_file_standalone(path: Path, project_root: Path = None) -> FileType:
       """Lightweight SSOT classification — no agent instantiation needed."""
       fca = FileClassificationAgent(project_root=project_root or Path.cwd(), dry_run=True, validate_only=True)
       return fca.classify_file(path)

   def is_agent_file(path: Path, project_root: Path = None) -> bool:
       """SSOT check: Is this file an AGENT per FCA classification?"""
       return classify_file_standalone(path, project_root) == "AGENT"
   ```
2. Add a `FileType` re-export so consumers can `from agentic_core.L5_safety.reasoning.FileClassificationAgent import FileType, is_agent_file`

### Phase 1: Fix Competing SSOT (P0 — High Risk)

| # | File | Action | Risk |
|---|------|--------|------|
| 1a | `complexity_visitor_util.py` | Remove `is_agent_class()` (~200 lines). Replace with `from FCA import is_agent_file`. Remove false SSOT header. Keep AST extraction utilities (`extract_bases`, `extract_methods`, etc.) which are reusable. | **HIGH** — 2000-line file, many consumers |
| 1b | `full_agent_discovery.py` | Replace `analyze_agent_integrity()` `class_score()` with FCA `classify_file()` for the initial classification pass. Keep the integrity report (`AgentIntegrityReport`) for the verification step but source the candidate list from FCA. | **HIGH** — Core discovery script |

### Phase 2: Fix Full Reimplementations (P1 — Medium Risk)

| # | File | Action |
|---|------|--------|
| 2a | `runtime/utils/discovery_util.py` | Replace `AgentRegistry._is_agent_class()` with `from FCA import is_agent_file`. This is 228 lines total; the whole `AgentRegistry.discover_all()` flow should delegate to FCA + `agent_discovery_full.json` instead of rescanning. |
| 2b | `ops_scripts/maintenance/run_classification.py` | Replace local `classify_file()` with `from FCA import classify_file_standalone`. |
| 2c | `prompt_governance/scripts/file_intent.py` | Replace `_is_agent_class()` and `_inherits_from_agent()` with `from FCA import classify_file_standalone`. Map FCA result to FileIntent. |
| 2d | `L5_safety/validators/type_erasure_validator.py` | Replace `_is_agent_class()` with `from FCA import classify_file_standalone`. Check `result in ("AGENT", "ORCHESTRATOR")` instead of `"Agent" in name`. |

### Phase 3: Fix Inline Checks in Enforcement Scripts (P2 — Low Risk)

| # | File | Action |
|---|------|--------|
| 3a | `L5_safety/enforcement/ssot_scanner_enforcer.py` | Replace `node.name.endswith("Agent")` with FCA `is_agent_file(path)` |
| 3b | `L5_safety/enforcement/registry_verification_enforcer.py` | Same pattern |
| 3c | `L5_safety/enforcement/data_enforcer.py` | Same pattern |
| 3d | `L5_safety/enforcement/ssot_structure_validation_enforcer.py` | Same pattern |

### Phase 4: Fix Filename-Only Utilities (P2 — Low Risk)

| # | File | Action |
|---|------|--------|
| 4a | `extract_agent_duplicates_util.py` | Replace `path.endswith("Agent.py")` with `from FCA import is_agent_file` |
| 4b | `find_real_duplicates_v2_util.py` | Same |
| 4c | `generate_agent_table_simple_util.py` | Same |

### Phase 5: Fix Inline Checks in Tests (P3 — Lowest Risk)

For test files, create a shared test helper:
```python
# tests/helpers/classification.py
from agentic_core.L5_safety.reasoning.FileClassificationAgent import classify_file_standalone

def is_agent_class_in_file(path: Path) -> bool:
    return classify_file_standalone(path) == "AGENT"
```

Update these test files to use the helper:
- `test_repo_scan_no_agents_outside_reasoning.py`
- `test_ssot_alignment.py`
- `test_architecture_governance.py`
- `test_agent_validation.py`, `test_agent_autonomy.py`, etc.
- `tests/helpers/assertions.py`

### Phase 6: Rename Ambiguous Functions (P3 — Cosmetic)

| File | Current Name | New Name |
|------|-------------|----------|
| `class_info.py` | `classify_file()` | `classify_archive_file()` |
| `analyze_app_files_util.py` | `classify_file()` | `classify_app_domain()` |

---

## Verification

After each phase:
1. `python -m agentic_core.L0_maintenance.scripts.full_agent_discovery --summary` — must report 190 candidates, ~189 verified
2. `pytest tests/unit/file_classification_agent/ -xvv` — FCA test suite must pass
3. `pytest tests/guardian/ -xvv` — governance tests must pass
4. Grep `def _is_agent_class\|def is_agent_class\|def is_agent_file\|def is_agent\b` to confirm only FCA definitions remain

## Summary Metrics

| Metric | Before | After |
|--------|--------|-------|
| Files with independent agent detection | 15+ | 1 (FCA) |
| `_is_agent_class()` definitions | 4 | 0 (all delegate to FCA) |
| `classify_file()` reimplementations | 3 | 0 (all delegate to FCA) |
| Inline `endswith("Agent")` in production code | 8+ files | 0 |
| SSOT claims in docstrings | 3 | 1 (FCA) |

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

