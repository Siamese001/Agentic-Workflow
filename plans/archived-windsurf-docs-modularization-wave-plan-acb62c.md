---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\modularization-wave-plan-acb62c.md'
original_relative_path: 'modularization-wave-plan-acb62c.md'
source_sha256: f176045f1a9b0fc708a932ffeecd5aa905e6fcbed1fda404e28c276f93d94193
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-04-03'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Modularization Wave Plan: Top 3 High-Impact Files

Modularize the three most complex, high-traffic files identified via ADG analysis to improve maintainability, reduce coupling, and establish cleaner architectural boundaries.

## Wave Summary Table

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| 1 | P1.1-P1.3 | execute_ssot.py decomposition | ~45K | L0 routing stable, tests pass | PENDING | <200KB, 20+ classes extracted, imports fixed |
| 2 | P2.1-P2.3 | FileClassificationAgent.py extraction | ~35K | Wave 1 complete, L5 agents stable | PENDING | <150KB, shared reasoning lib created |
| 3 | P3.1-P3.3 | LocationHealerAgent.py + shared utils | ~30K | Waves 1-2 complete | PENDING | <150KB, LocationHealer uses shared lib |
| 4 | P4.1-P4.2 | Cross-cutting cleanup & validation | ~20K | All waves complete | PENDING | All tests pass, ADG hotspots reduced 50% |

**Total Estimated Tokens:** ~130K  
**Target Completion:** 4 waves over 2-3 sessions  
**Risk Level:** MEDIUM (high fan-in/out requires careful staging)

---

## Current State Analysis

### ADG Hotspot Data (04022026_2136)

**Top 3 Candidates by Combined Fan-In + Fan-Out:**

| File | Fan-In | Fan-Out | Total | Lines | Size | Layer |
|------|--------|---------|-------|-------|------|-------|
| execute_ssot.py | 1,015 | 1,027 | 2,042 | 8,566 | ~340KB | L0 |
| FileClassificationAgent.py | 393 | 639 | 1,032 | ~3,000 | ~120KB | L5 |
| LocationHealerAgent.py | 316 | 609 | 925 | ~2,800 | ~110KB | L5 |

### Why These Files

1. **execute_ssot.py** - Central orchestration hub with 1,015 modules depending on it and 1,027 dependencies. Contains multi-phase execution logic (discovery, validation, alignment, healing) that should be split into focused modules.

2. **FileClassificationAgent.py** - High coupling L5 reasoning agent. Shares patterns with LocationHealerAgent that can be extracted into a shared reasoning library.

3. **LocationHealerAgent.py** - Similar structure to FileClassificationAgent. Extracting common patterns first enables both to use shared utilities.

---

## Wave 1: execute_ssot.py Decomposition

**Goal:** Break 8,566-line orchestration monolith into focused modules

### Phase P1.1: Discovery & Scope Declaration (Tokens: ~8K, GREEN)

**Tasks:**
1. Build AST dependency graph for execute_ssot.py
2. Identify logical cohesion clusters:
   - Phase orchestration (discovery, validation, alignment, healing)
   - Agent lazy loading
   - Meta-learning integration
   - Error handling/recovery
   - ADG behavioral signal integration
3. Map external dependencies (lifecycle_trace_contract emitters)
4. Document blast radius: 1,015 downstream modules

**Deliverables:**
- `docs/reports/plans/wave1_execute_ssot_scope.md`
- DEPENDENCY_GRAPH section with upstream/downstream analysis
- List of extractable classes/functions per cluster

**Gate:** HITL review of scope document before any edits

### Phase P1.2: Core Extraction (Tokens: ~25K, YELLOW)

**Extract to new modules:**

| New Module | Extracted From | Lines Est | Rationale |
|------------|--------------|-----------|-----------|
| `execute_ssot_phases.py` | Phase execution logic | ~2,000 | Isolate 4-phase orchestration |
| `execute_ssot_agents.py` | Agent lazy loading | ~1,500 | Separate agent lifecycle |
| `execute_ssot_meta.py` | Meta-learning integration | ~1,200 | ML routing decisions |
| `execute_ssot_errors.py` | Error handling/recovery | ~1,800 | Recovery protocols |
| `execute_ssot_adg.py` | ADG behavioral signals | ~1,000 | Signal extraction only |

**Integration Pattern:**
- `execute_ssot.py` becomes thin orchestrator (~2,000 lines)
- Delegates to extracted modules via clean interfaces
- Preserves backward compatibility through shim imports

**Testing:**
- Verify 19/19 scanner tests still pass
- Run full compliance test suite
- Validate no regression in ADG edge counts

### Phase P1.3: Cleanup & Validation (Tokens: ~12K, GREEN)

**Tasks:**
1. Remove extracted code from original file
2. Update all internal imports
3. Fix lint errors
4. Verify file size < 200KB (target: ~150KB)
5. Update `__all__` exports
6. Document API changes

**Validation Gates:**
- Syntax check: `python -c "import ast; ast.parse(open('execute_ssot.py').read())"`
- Import check: `python -c "from agentic_core.L0_routing.scripts.execute_ssot import main"`
- Test check: `pytest tests/unit/routing/test_execute_ssot.py -v`
- Size check: File must be < 200KB

---

## Wave 2: FileClassificationAgent.py Extraction

**Goal:** Extract shared L5 reasoning patterns and reduce agent complexity

### Phase P2.1: Shared Library Design (Tokens: ~10K, GREEN)

**Analyze patterns shared with LocationHealerAgent:**
- Classification heuristics
- Safety boundary checks
- Hierarchy traversal
- Reporting/formatting

**Design:**
- New module: `agentic_core/L5_safety/reasoning/base_classification.py`
- Abstract base class for classification agents
- Shared utilities for file/location analysis

### Phase P2.2: Agent Refactoring (Tokens: ~20K, YELLOW)

**Extract from FileClassificationAgent.py:**
- `ClassificationHeuristics` class → `base_classification.py`
- `SafetyBoundaryChecker` class → `safety_boundary_utils.py`
- `HierarchyTraverser` class → `hierarchy_utils.py`
- Reporting functions → `classification_reporting.py`

**Result:**
- FileClassificationAgent.py: ~120KB → ~80KB
- Clean inheritance from base classes
- No functional changes to external API

### Phase P2.3: Integration Testing (Tokens: ~5K, GREEN)

**Tests:**
- Unit tests for extracted base classes
- Integration tests with FileClassificationAgent
- Verify no regression in L5 safety coverage

---

## Wave 3: LocationHealerAgent.py + Shared Utils

**Goal:** Leverage Wave 2 shared library for LocationHealerAgent

### Phase P3.1: Migration to Shared Library (Tokens: ~15K, GREEN)

**Refactor LocationHealerAgent to use:**
- `base_classification.BaseClassificationAgent`
- `safety_boundary_utils.SafetyBoundaryChecker`
- `hierarchy_utils.HierarchyTraverser`

**Remove duplicate code:**
- Similar classification logic
- Duplicate safety checks
- Redundant hierarchy traversal

### Phase P3.2: Location-Specific Extraction (Tokens: ~12K, GREEN)

**Extract location-specific logic:**
- `LocationPatternMatcher` → `location_pattern_utils.py`
- `PathHeuristics` → `path_heuristics.py`
- Location healing strategies → `healing_strategies.py`

**Result:**
- LocationHealerAgent.py: ~110KB → ~70KB
- Clean separation of concerns

### Phase P3.3: Cross-Agent Validation (Tokens: ~3K, GREEN)

**Verify both agents work correctly:**
- FileClassificationAgent still classifies correctly
- LocationHealerAgent still heals correctly
- No interference between shared utilities

---

## Wave 4: Cross-Cutting Cleanup & Validation

### Phase P4.1: Orphaned Code Removal (Tokens: ~12K, GREEN)

**Repository-wide cleanup:**
1. Find orphaned functions after modularization
2. Remove dead code identified by ADG `dead_imports` (7,019 instances)
3. Consolidate duplicate utilities
4. Update import statements across codebase

### Phase P4.2: Final Validation (Tokens: ~8K, GREEN)

**ADG Verification:**
- Re-run ADG generation
- Verify hotspot reduction:
  - execute_ssot.py: 2,042 → <1,000 (50% reduction)
  - FileClassificationAgent.py: 1,032 → <600 (40% reduction)
  - LocationHealerAgent.py: 925 → <500 (45% reduction)
- Confirm no new layer violations

**Test Suite:**
- All 19/19 scanner tests pass
- L0 routing tests pass
- L5 safety tests pass
- Full integration test suite passes

**Performance:**
- Import time not degraded
- No circular dependencies introduced

---

## Token Budget Summary

| Wave | Phase | Est. Tokens | Status | Risk |
|------|-------|-------------|--------|------|
| 1 | P1.1 Discovery | 8K | GREEN | Low |
| 1 | P1.2 Extraction | 25K | YELLOW | Medium |
| 1 | P1.3 Cleanup | 12K | GREEN | Low |
| 2 | P2.1 Shared Lib | 10K | GREEN | Low |
| 2 | P2.2 Refactoring | 20K | YELLOW | Medium |
| 2 | P2.3 Testing | 5K | GREEN | Low |
| 3 | P3.1 Migration | 15K | GREEN | Low |
| 3 | P3.2 Extraction | 12K | GREEN | Low |
| 3 | P3.3 Validation | 3K | GREEN | Low |
| 4 | P4.1 Cleanup | 12K | GREEN | Low |
| 4 | P4.2 Validation | 8K | GREEN | Low |
| **TOTAL** | | **130K** | | **MEDIUM** |

---

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Breaking changes to 1,015 dependents | Medium | HIGH | Shim imports, backward compatibility layer, staged rollout |
| Circular dependencies | Low | MEDIUM | Graph-first analysis before each wave, fail-closed discipline |
| Test regressions | Medium | MEDIUM | Run full test suite after each wave, gate on 19/19 scanner tests |
| Scope creep | Medium | LOW | Strict wave boundaries, HITL gates at phase exits |
| File size not reducing as expected | Low | LOW | Monitor size after each extraction, pivot if needed |

---

## Success Criteria (Per Wave)

**Wave 1 Success:**
- [ ] execute_ssot.py < 200KB (target: 150KB)
- [ ] 5+ modules extracted with clean interfaces
- [ ] All 19 scanner tests pass
- [ ] No new ADG layer violations
- [ ] HITL approval of scope and implementation

**Wave 2 Success:**
- [ ] FileClassificationAgent.py < 100KB (target: 80KB)
- [ ] Shared reasoning library created
- [ ] BaseClassificationAgent abstract class functional
- [ ] All L5 safety tests pass

**Wave 3 Success:**
- [ ] LocationHealerAgent.py < 100KB (target: 70KB)
- [ ] Uses shared library from Wave 2
- [ ] No duplicate logic with FileClassificationAgent
- [ ] Both agents tested independently

**Wave 4 Success:**
- [ ] Combined hotspot reduction > 40%
- [ ] 7,019 dead imports addressed
- [ ] Full test suite passes
- [ ] ADG regeneration confirms clean graph

---

## Dependencies & Ordering

**Wave 1 → Wave 2:**
- Wave 1 must complete before Wave 2 (L0 must be stable)
- execute_ssot.py contains orchestration that tests L5 agents

**Wave 2 → Wave 3:**
- Wave 2 shared library is prerequisite for Wave 3
- FileClassificationAgent patterns inform LocationHealerAgent refactoring

**Wave 4 depends on all:**
- Final cleanup requires all extractions complete
- Dead code analysis needs final state

---

## Evidence Artifacts

Each wave must produce:
1. Scope declaration with DEPENDENCY_GRAPH section
2. DEDUP_SEARCH for any new classes/functions
3. Test execution logs (19/19 scanner tests)
4. File size before/after metrics
5. ADG hotspot delta report

---

*Plan generated: 04022026_2136*  
*ADG Reference: adg_indexed_04022026_2136.sqlite*  
*Template: .windsurf/templates/execution-plan-template.md*
