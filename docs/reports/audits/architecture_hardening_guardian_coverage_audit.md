# Architecture Hardening & SSOT Enforcement — Guardian Test Coverage Audit

**Generated:** 2026-02-18  
**Scope:** 6-Phase Windsurf System Prompt Audit Items  
**Purpose:** Map each audit requirement to existing Guardian test coverage (Y/N)

---

## Legend

| Symbol | Meaning |
|--------|---------|
| **Y** | Guardian test(s) exist that cover this item |
| **P** | Partial coverage (related tests exist but not comprehensive) |
| **N** | No Guardian test coverage identified |

---

## Phase 1: AST, Syntax & Initialization Sequencing

| # | Audit Item | Guardian Coverage | Test File(s) / Notes |
|---|------------|:-----------------:|----------------------|
| 1.1 | `from __future__` placement (first executable line) | **P** | `test_import_safety.py` validates syntax but not future-import ordering specifically |
| 1.2 | Missing `super().__init__(**kwargs)` calls | **Y** | `test_mro_integrity.py` → `test_redundant_mixin_check`, `test_dataclass_initialization_fuzz` |
| 1.3 | Root state initialization before `super().__init__` | **P** | `test_mro_integrity.py` → `test_sovereign_seal_integrity` (partial) |

---

## Phase 2: MRO "Diamond Problem" & Mixin Purge

| # | Audit Item | Guardian Coverage | Test File(s) / Notes |
|---|------------|:-----------------:|----------------------|
| 2.1 | Enforce strict hierarchy: `Agent → Layer → SovereignBaseAgent` | **Y** | `test_mro_integrity.py` → `TestDiamondDefense.test_mixin_order_safety` |
| 2.2 | Eradicate redundant mixin declarations | **Y** | `test_mro_integrity.py` → `test_redundant_mixin_check`, `test_duplicate_mixin_injection` |
| 2.3 | Diamond of Death detection | **Y** | `test_mro_integrity.py` → `test_diamond_of_death_detection`, `test_detect_diamond_pattern` |
| 2.4 | MRO TypeError prevention | **Y** | `test_imports_no_mro_error.py` → `test_import_no_mro_crash` |
| 2.5 | Mixin naming convention (`*Mixin` suffix) | **Y** | `test_mro_integrity.py` → `test_mixin_naming_convention_and_inheritance` |
| 2.6 | Mixin order safety (safety mixins before base) | **Y** | `test_mro_mixin_order.py` → `TestMROMixinOrder` |

---

## Phase 3: Circular Imports & Dependency Chains

| # | Audit Item | Guardian Coverage | Test File(s) / Notes |
|---|------------|:-----------------:|----------------------|
| 3.1 | Decouple agent cross-imports (no loops) | **Y** | `test_import_safety.py` → `test_circular_dependency_scanner`, `test_circular_dependency_trap` |
| 3.2 | `if TYPE_CHECKING:` for type-only imports | **P** | `test_import_safety.py` detects cycles but doesn't enforce TYPE_CHECKING pattern |
| 3.3 | Re-export verification in `__init__.py` | **P** | `test_import_safety.py` → `test_init_completeness` (existence check, not re-export validation) |
| 3.4 | Resolve missing definitions (`prompt_governance`, `ValidationContext`, `generate_ascii_tree`) | **N** | No specific Guardian test for these missing imports |
| 3.5 | Cross-territory import boundaries | **Y** | `test_import_graph_contract.py` → `test_no_forbidden_cross_territory_edges` |

---

## Phase 4: "Half-Migrated State" & Boundary Enforcement

| # | Audit Item | Guardian Coverage | Test File(s) / Notes |
|---|------------|:-----------------:|----------------------|
| 4.1 | Directory audit (orphaned files, duplicates) | **Y** | `test_location_alignment.py`, `test_folder_purity_hardening.py`, `test_orphan_agent_detection.py` |
| 4.2 | `patterns/agent_roles/` strictly for implementation | **Y** | `test_subatomic_compliance.py` → `test_layer_zoning_alignment` |
| 4.3 | Unified state context (type-safe `HealResult` objects) | **P** | `test_subatomic_compliance.py` → type erasure checks (partial) |
| 4.4 | Root hygiene (no unapproved files at root) | **Y** | `test_root_hygiene_contract.py` → `TestRootHygiene` |
| 4.5 | Drift detection | **Y** | `test_drift_detection.py`, `run_guardian_drift_detection.py` |

---

## Phase 5: Tool Registration & Runtime Safety

| # | Audit Item | Guardian Coverage | Test File(s) / Notes |
|---|------------|:-----------------:|----------------------|
| 5.1 | ToolRegistry consolidation (single registry) | **P** | `test_tool_registry.py` (import test only, not consolidation validation) |
| 5.2 | Case-sensitivity collisions in tool names | **N** | No Guardian test for tool name case collisions |
| 5.3 | Missing tool runtimes (`repository_get_file_content`) | **N** | No Guardian test for unbound tool methods |
| 5.4 | LocationAgent sandboxing (boundary checks) | **P** | `test_agent_capability_limits.py` (partial capability limits) |
| 5.5 | CodeDeduplicationAgent strict identity match | **N** | No Guardian test for deduplication identity strictness |

---

## Phase 6: Test Harness, Dashboard & Telemetry

| # | Audit Item | Guardian Coverage | Test File(s) / Notes |
|---|------------|:-----------------:|----------------------|
| 6.1 | 111 Signal Blocks audit (I/O signature compliance) | **P** | `test_l6_signal_contract.py` (partial signal contract) |
| 6.2 | Live Runtime Dashboard API initialization | **N** | No Guardian test for dashboard API bootstrap |
| 6.3 | AST-based test bypasses for broken imports | **P** | `test_import_safety.py` uses AST parsing; no dynamic bypass mechanism tested |

---

## Summary

| Phase | Total Items | Y (Full) | P (Partial) | N (None) | Coverage % |
|-------|:-----------:|:--------:|:-----------:|:--------:|:----------:|
| **Phase 1** | 3 | 1 | 2 | 0 | 67% |
| **Phase 2** | 6 | 6 | 0 | 0 | **100%** |
| **Phase 3** | 5 | 2 | 2 | 1 | 60% |
| **Phase 4** | 5 | 4 | 1 | 0 | 90% |
| **Phase 5** | 5 | 0 | 2 | 3 | 20% |
| **Phase 6** | 3 | 0 | 2 | 1 | 33% |
| **TOTAL** | **27** | **13** | **9** | **5** | **65%** |

---

## Key Guardian Test Files Referenced

| Test File | Primary Coverage |
|-----------|------------------|
| `tests/guardian/test_mro_integrity.py` | Phase 1 & 2 (MRO, Diamond, Mixins) |
| `tests/guardian/test_mro_mixin_order.py` | Phase 2 (Mixin ordering) |
| `tests/guardian/test_import_safety.py` | Phase 3 (Circular deps, Syntax) |
| `tests/guardian/test_subatomic_compliance.py` | Phase 4 (Layer zoning, LOC limits) |
| `tests/guardian/test_folder_purity_hardening.py` | Phase 4 (Directory structure) |
| `tests/guardian/test_location_alignment.py` | Phase 4 (File placement) |
| `tests/guardian/test_anti_patterns.py` | Cross-phase (Anti-pattern detection) |
| `tests/unit_min_deps/test_import_graph_contract.py` | Phase 3 (Import boundaries) |
| `tests/unit_min_deps/test_root_hygiene_contract.py` | Phase 4 (Root hygiene) |
| `tests/unit_min_deps/test_inspector_mro_contracts.py` | Phase 2 (MRO contracts) |
| `tests/integration/agentic_core/test_imports_no_mro_error.py` | Phase 2 (MRO crash prevention) |

---

## Gaps Requiring New Guardian Tests

1. **Phase 3.4** — Missing definition resolution (`prompt_governance`, `ValidationContext`, `generate_ascii_tree`)
2. **Phase 5.2** — Tool name case-sensitivity collision detection
3. **Phase 5.3** — Unbound tool method validation (`repository_get_file_content`)
4. **Phase 5.5** — CodeDeduplicationAgent identity match strictness
5. **Phase 6.2** — Dashboard API initialization sequence validation

---

*This audit is based on static analysis of Guardian test files in `tests/guardian/`, `tests/unit_min_deps/`, and `tests/integration/`.*
