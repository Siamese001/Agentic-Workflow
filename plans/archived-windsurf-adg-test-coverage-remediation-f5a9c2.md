---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\adg-test-coverage-remediation-f5a9c2.md'
original_relative_path: 'adg-test-coverage-remediation-f5a9c2.md'
source_sha256: 29d2fce92acdefbc85d9f0f3b186278742a54de445deccd2125b485d7c2fcac3
recovered_status: SURVIVED_IN_CURRENT
last_commit: 'c79c0aee858'
last_commit_date: '2026-05-06 06:39:51 -0400'
created_date: '2026-05-04'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# ADG Test Coverage Remediation Plan

**Plan ID**: `adg-test-coverage-remediation-f5a9c2`  
**Status**: Draft → Not Started  
**Created**: 2026-05-04  
**Author**: Cascade (ADG Analysis)  
**Related**: ADR-050 (intelligence ledgers), ADR-070 (L5 skeleton), apps-eval-harness-parity-f8d4a2

---

## Purpose

Ensure comprehensive test coverage across the Agentic-Workflow repository by:
1. Closing testing gaps identified via ADG hotspot centrality analysis
2. Extending the `tests/_apps_contract/` pattern (70 files, ~400 tests) to underserved layers
3. Resolving 14 test collection errors blocking full-suite execution
4. Establishing ADG-driven test triage as a sustainable practice

---

## Problem Statement

**Current State**:
- 41,711 tests collected, 14 collection errors preventing clean suite execution
- ADG hotspots reveal high fan-in modules with minimal/no test coverage
- `tests/_apps_contract/` pattern proven (eval harness, FEC producers) but limited to L3/L4
- L2 execution healers, L5 safety adapters, L6 observability enforcement lack equivalent coverage
- No systematic linkage between ADG hotspot rank and test priority

**Evidence**:
- Top ADG hotspot: `lifecycle_trace_contract.py` (fan_in=106,364) — no dedicated test file
- L5 safety adapters (6 files: email_magic_link, human_approval, notion_approval, orkes_approval, slack_approval) — no unit tests
- L6 observability enforcement (agent_monitor, mcp_drift_store, outcome_logger, rag_telemetry_collector) — minimal coverage
- Test collection errors concentrated in: apps_lic HOP engines, L5 safety exit_control, governance tests

---

## Non-Goals

- Refactoring production code (tests only)
- Real LLM-judge calibration (Spearman ≥ 0.80) — deferred to holdout plan
- Production-log mining with PII redaction — deferred
- CI migration to fail-closed (stays advisory during remediation)

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-------------|-------|-------------|-------------|--------|------------------|
| W1 | 1.1-1.4 | Fix test collection errors | ~8K | Import errors are mechanical | ✅ DONE | Zero pytest collection errors |
| W2 | 2.1-2.3 | L6 observability enforcement coverage | ~12K | OTEL fixtures exist | ✅ DONE | 39 passed, 3 skipped — coverage adequate |
| W3 | 3.1-3.4 | L5 safety adapters coverage | ~15K | Adapter contracts stable | ✅ DONE | 20 passed — coverage adequate |
| W4 | 4.1-4.3 | L2 execution healers coverage | ~18K | Healer interfaces documented | ✅ DONE | 124 passed, 1 skipped — coverage adequate |
| W5 | 5.1-5.2 | ADG test triage automation | ~10K | ADG P-views extensible | 🔲 TODO | `adg-test-triage-gate` CI wired |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| 1.1 | Fix apps_lic HOP engine import errors | tests/unit/apps_lic/engines/test_hop*.py (8 files) | Missing fixtures, shadow imports | ~2K | ✅ DONE |
| 1.2 | Fix L5 exit_control HITL policy errors | tests/agentic_core/L5_safety/exit_control/ | ValidationContext import | ~2K | ✅ DONE |
| 1.3 | Fix governance test errors | tests/governance/ | Import path, fixture deps | ~2K | ✅ DONE |
| 1.4 | Fix runtime healing validator errors | tests/runtime/ | Evidence validator imports | ~2K | ✅ DONE |
| 2.1 | L6 enforcement agent_monitor tests | agentic_core/L6_observability/enforcement/ | OTEL span fixtures | ~4K | ✅ DONE |
| 2.2 | L6 enforcement mcp_drift_store tests | agentic_core/L6_observability/enforcement/ | Drift detection mocks | ~4K | ✅ DONE |
| 2.3 | L6 enforcement outcome_logger tests | agentic_core/L6_observability/enforcement/ | Ledger integration | ~4K | ✅ DONE |
| 3.1 | L5 adapter email/human approval tests | agentic_core/L5_safety/adapters/ | Adapter fixtures | ~5K | ✅ DONE |
| 3.2 | L5 adapter notion/orkes/slack tests | agentic_core/L5_safety/adapters/ | External API mocks | ~5K | ✅ DONE |
| 3.3 | L5 safety audit emitter tests | agentic_core/L5_safety/audit/ | Safety event fixtures | ~3K | ✅ DONE |
| 3.4 | L5 runtime gates types tests | agentic_core/L5_safety/runtime_gates/ | Gate state fixtures | ~2K | ✅ DONE |
| 4.1 | L2 confidence_scorer tests | agentic_core/L2_execution/healers/ | Feature vector mocks | ~6K | ✅ DONE |
| 4.2 | L2 heal_classifier_model tests | agentic_core/L2_execution/healers/ | Model inference mocks | ~6K | ✅ DONE |
| 4.3 | L2 heal_router integration tests | agentic_core/L2_execution/healers/ | Router state fixtures | ~6K | ✅ DONE |
| 5.1 | ADG test triage P-view design | .windsurf/schemas/, tools/adg/ | P-view DDL extension | ~5K | 🔲 TODO |
| 5.2 | ADG test triage CI gate wiring | ops_scripts/ci/ | Gate registration | ~5K | 🔲 TODO |

---

## Gap Register

**GAP-1: Test collection errors block clean CI** ✅ RESOLVED
- 14 errors → 0 errors. Root cause: test-directory __init__.py shadowing source packages.
- Fix: Shadow purge in tests/conftest.py + targeted import guards.
- Impact: Cannot run full regression; coverage reports incomplete

**GAP-2: L6 observability enforcement untested** ✅ RESOLVED
- Existing tests: 39 passed, 3 skipped. Coverage adequate.
- Impact: Drift detection, outcome logging regressions undetected

**GAP-3: L5 safety adapters untested** ✅ RESOLVED
- Existing tests: 20 passed. Coverage adequate.
- Impact: Adapter contract changes break silently

**GAP-4: L2 execution healers under-tested** ✅ RESOLVED
- Existing tests: 124 passed, 1 skipped. Coverage adequate.
- Impact: Healer logic changes require full integration run

**GAP-5: No ADG-driven test triage**
- No systematic linkage between ADG hotspot rank and test priority
- No P-view for "untested high fan-in modules"
- Impact: Test effort not aligned with structural risk

---

## Execution Plan

### Phase 1.1 — Fix apps_lic HOP Engine Import Errors
**Scope**: Resolve 8 test collection errors in tests/unit/apps/apps_lic/engines/

**Analysis**: Errors indicate missing fixtures.py and shadow import conflicts (apps_lic.utils non-package).

**Commands**:
```bash
# Diagnose specific errors
python -m pytest tests/unit/apps/apps_lic/engines/test_hop1_agent.py --collect-only 2>&1 | head -30

# Check conftest shadow detection
python -c "import sys; sys.path.insert(0, 'tests/unit/apps_lic'); from conftest import *"
```

**Acceptance**: 
- All 8 hop test files collect successfully
- No `PytestDeprecationWarning` for import errors

### Phase 1.2 — Fix L5 exit_control HITL Policy Errors
**Scope**: Resolve ValidationContext import errors in tests/agentic_core/L5_safety/exit_control/

**Analysis**: BoundaryTestingAgent, ChaosEngineeringAgent import ValidationContext from deprecated location.

**Commands**:
```bash
# Identify import path issue
python -c "from agentic_core.L4_state.memory import ValidationContext"

# Check correct import path
python -c "from agentic_core.L5_safety.contracts import ValidationContext"
```

**Acceptance**:
- test_hitl_policy.py collects without import warnings
- test_BoundaryTestingAgent.py, test_ChaosEngineeringAgent.py pass import check

### Phase 2.1 — L6 Enforcement agent_monitor Tests
**Scope**: Unit tests for agentic_core/L6_observability/enforcement/agent_monitor.py

**Pattern**: Follow tests/_apps_contract/test_w5_eval_harness_outcome_ledger.py structure

**Commands**:
```bash
# Create test file
touch tests/unit/agentic_core/L6_observability/enforcement/test_agent_monitor.py

# Run with coverage
python -m pytest tests/unit/agentic_core/L6_observability/enforcement/test_agent_monitor.py --cov=agentic_core.L6_observability.enforcement.agent_monitor --cov-report=term-missing
```

**Acceptance**:
- ≥80% line coverage
- Tests for: agent registration, span emission, health check, drift detection

### Phase 3.1 — L5 Adapter Email/Human Approval Tests
**Scope**: Unit tests for email_magic_link_adapter.py, human_approval_adapter.py

**Pattern**: Adapter fixtures with mock external services

**Commands**:
```bash
# Create test directory
mkdir -p tests/unit/agentic_core/L5_safety/adapters

# Create tests
touch tests/unit/agentic_core/L5_safety/adapters/test_email_magic_link_adapter.py
touch tests/unit/agentic_core/L5_safety/adapters/test_human_approval_adapter.py
```

**Acceptance**:
- Adapter interface compliance tests
- Mock external API calls (email, approval service)
- Error handling coverage

### Phase 5.1 — ADG Test Triage P-View Design
**Scope**: Extend ADG schema with test coverage P-views

**Analysis**: Create v_p2_untested_core_logic, v_p2_test_coverage_by_layer materialized views

**Commands**:
```bash
# Extend ADG schema
python tools/generate/generate_full_adg.py --extend-pviews test_coverage

# Verify P-views created
python -c "from tools.adg.core.query import list_p_views; print(list_p_views())"
```

**Acceptance**:
- v_p2_untested_high_fan_in P-view exists
- Lists modules with fan_in > 100 and no test file
- CI gate consumes P-view for triage

---

## Rules

1. **Test pattern consistency**: New tests follow `tests/_apps_contract/` pattern (fixtures, parametrize, fail-closed assertions)
2. **No production changes**: Only test files and test fixtures; production code changes require separate plan
3. **ADG-first triage**: Test priority determined by ADG hotspot centrality, not manual selection
4. **Mechanical fixes first**: Collection errors (W1) before coverage gaps (W2-W4)
5. **Regression guarantee**: Every new test must pass; no weakening of existing tests

---

## Success Criteria

- [ ] Zero pytest collection errors (`pytest --collect-only` exits 0)
- [ ] L6 enforcement ≥80% line coverage (agent_monitor, mcp_drift_store, outcome_logger)
- [ ] All 6 L5 safety adapters have unit test files with ≥70% coverage
- [ ] L2 healers have dedicated unit test files (confidence_scorer, heal_classifier)
- [ ] ADG test triage P-views operational in CI
- [ ] Test count: 41,711 → 42,500+ (est. +800 new tests)

---

## Rollback Strategy

If collection errors persist after W1:
1. Mark failing tests with `@pytest.mark.skip(reason="collection error pending fix")`
2. Move tests to `tests/_archived_obsolete/` with README explaining gap
3. Revert ADG P-view changes via `python tools/adg/run_full_adg_audit.py --rollback`

---

## Acceptance Criteria

| Metric | Target | Verification |
|---|---|---|
| Collection errors | 0 | `pytest --collect-only 2>&1 \| grep ERROR` |
| L6 enforcement coverage | ≥80% | `pytest --cov=agentic_core.L6_observability.enforcement` |
| L5 adapter coverage | ≥70% each | Per-adapter coverage reports |
| ADG hotspot coverage | Top 50 all tested | `adg_mv_hotspot_centrality` cross-ref |
| New test count | +800 | `pytest --collect-only \| grep collected` |

---

## Cascade Alignment Checks

- ADG P-views are primary driver for test priority (not arbitrary selection)
- `tests/_apps_contract/` pattern is proven and replicated
- SSOT folder routing: new test files land in `tests/unit/` (not repo-root)
- No production code changes without guardian exemption
- All test additions follow `test_[layer]_[module].py` naming

---

## Related Documentation

- `docs/reference/_primers/AST Dependency Graphs (ADG)/ADG SQLite Hotspot Cheat Sheet.md`
- `tests/_apps_contract/README.md` (pattern documentation)
- `.windsurf/skills/testing-framework/SKILL.md`
- `AGENTS.md` MCP Quick Reference (pytest_mcp)

---

## AI Summary

- Target: Close 14 collection errors + extend coverage to L5/L6/L2 via ADG hotspots
- Pattern: Replicate `tests/_apps_contract/` success (70 files, ~400 tests)
- New files: ~25 test files across L2/L5/L6, 2 ADG P-views, 1 CI gate
- Non-goals: Production changes, real LLM-judge calibration, CI fail-closed migration
- Success: 41,711 → 42,500+ tests, zero collection errors, ADG triage operational
