# Phase 0 Validation Findings
**Coverage Gap Discrepancy: SQLite (1,997) vs Accelerator (1,051)**
**Date**: 2026-03-12
**Scripts**: `tools/evidence/_phase0_validation.py`, `tools/evidence/_phase0_deep_analysis.py`
**Raw data**: `docs/reports/plans/phase0_validation_findings.json`, `docs/reports/plans/phase0_deep_analysis.json`

---

## 1. Confirmed Numbers

| Metric | Value |
|--------|-------|
| **SQLite uncovered modules** | 1,997 |
| **Accelerator covered modules** | 1,041 |
| **Accelerator coverage rate** | 49.76% |
| **Accelerator inferred total** | 2,092 |
| **Accelerator inferred gap** | 1,051 |
| **SQLite false gaps** (SQLite said uncovered; accelerator says covered) | **1,031** |
| **Agreed true gaps** (both agree: uncovered) | **966** |
| **Delta** (SQLite - Accelerator inferred gap) | **946** |
| **Phantom modules** (in gaps but not on disk) | **0** |

---

## 2. Root Cause of SQLite False Gaps (1,031 modules)

**Confirmed hypothesis**: SQLite analysis counts only **direct `covers` edges** in the ADG graph. The accelerator uses **transitive import-graph coverage** — if a test imports module A, and A imports B, then B is marked covered.

Evidence: The 1,031 "false gaps" are distributed across **all production layers** (L1–L6, apps_*, system_learning) — exactly the pattern you'd expect from transitive coverage reaching well-integrated modules.

### False gap layer breakdown (modules SQLite missed but accelerator found covered):
| Layer | False Gaps |
|-------|------------|
| L5_safety | 156 |
| L2_execution | 132 |
| system_learning | 106 |
| apps_shared | 79 |
| agentic_core/adg | 52 |
| L1_cognition | 48 |
| L3_orchestration | 47 |
| L4_state | 45 |
| agentic_core/cache+runtime | 34 |
| L6_observability | 20 |
| agentic_core/utils+types | 22 |
| L0 subtotals | ~96 |
| apps_rg/lic | ~55 |

---

## 3. The 966 Agreed True Gaps (Actionable)

All 966 agreed-true-gap modules **exist on disk** — zero phantom/stale entries. These are real production files with no test coverage path.

### True gap breakdown by category:
| Category | Count | Notes |
|----------|-------|-------|
| **L5_safety** | 167 | Largest single layer; enforcement, config, audit submodules |
| **apps_lic/reasoning** | 30 | All LIC reasoning agents (production) |
| **system_learning** | 31 | Adapters, arbitration, enforcement |
| **L4_state** | 45 | Caching, config, state ledger submodules |
| **L3_orchestration** | 43 | Config, enforcement submodules |
| **L2_execution** | 27 | Coordination, determinism init files |
| **apps_rg/engines** | 33 | Bullet generation, brand compliance, etc. |
| **apps_rg/other** | 39 | `__main__`, config modules |
| **agentic_core/utils+types** | 36 | Decorators shim, structural healing engine |
| **agentic_core/cache+runtime** | 31 | Boundary validator, router config |
| **L6_observability** | 25 | Dashboard generators, analyzers |
| **L1_cognition** | 22 | Enforcement, engine inits |
| **agentic_core/adg** | 9 | Adapter/application `__init__` files |
| **L0 scripts (non-util)** | 28 | `base_tool.py`, `c_c_measurement.py` |
| **L0 utils** | 20 | `add_test_coverage_util.py`, etc. |
| **L0 scripts (runner)** | 3 | 3 guardian runners missing coverage |
| **L0 other** | 2 | `seam_audit.py`, `c0_context_retriever.py` |
| **agentic_core enforcement** | 1 | `enforcement/__init__.py` |
| **apps_lic other** | 31 | Config, `__main__`, engines |

---

## 4. Critical Utils — Production Safety Check

All 8 critical utility modules flagged for analysis:

| Module | In SQLite Gap | Accelerator Covered | Verdict |
|--------|--------------|--------------------| --------|
| `subprocess_runner_util.py` | ✅ Yes | ✅ Yes | **Safe** — accelerator covers it |
| `timeout_decorator_util.py` | ✅ Yes | ✅ Yes | **Safe** — accelerator covers it |
| `path_util.py` | ✅ Yes | ✅ Yes | **Safe** — accelerator covers it |
| `project_root_util.py` | ✅ Yes | ✅ Yes | **Safe** — accelerator covers it |
| `core_integrity_util.py` | ✅ Yes | ✅ Yes | **Safe** — accelerator covers it |
| `ssot_discovery_util.py` | ✅ Yes | ✅ Yes | **Safe** — accelerator covers it |
| `scan_util.py` | ✅ Yes | ✅ Yes | **Safe** — accelerator covers it |
| `json_formatter_util.py` | ✅ Yes | ❌ No | ⚠️ **TRUE GAP** — neither source covers it |

**Finding**: 7/8 critical utils are covered transitively by the accelerator. `json_formatter_util.py` is a genuine uncovered production module that should be prioritized.

---

## 5. apps_rg/apps_lic — Production Agents Without Coverage

445 total apps_*/system_learning modules appear in SQLite gaps. Of these, **30 `apps_lic/reasoning/` agents are confirmed true gaps** (exist on disk, no coverage in either system):

- `ArchetypeIndicatorsAgent.py`, `CampaignBalanceAgent.py`, `DeliverabilityAgent.py`
- `DispatchOutreachToolsAgent.py`, `ExecutiveStrategyAgent.py`, `GovernanceShieldAgent.py`
- `HOP3SenderGroundingAgent.py`, `HOP5GenerationAgent.py` … (30 total)

These are **active production reasoning agents** — highest priority for test coverage.

Similarly, `apps_rg/engines/` has **33 true gaps** including:
- `achievement_prioritizer_engine.py`, `brand_compliance_engine.py`, `bullet_generation_task.py`

---

## 6. CI/CD and Test Reference Check

| Check | Result |
|-------|--------|
| `.github/workflows/` references to `coverage_gaps.json` | **NONE** |
| `.github/workflows/` references to `_coverage_analysis.py` | **NONE** |
| `tests/` references to `coverage_gaps.json` | **NONE** |
| `tests/` references to `_coverage_analysis.py` | **NONE** |
| Hardcoded `0.4976` threshold in workflows | **NONE** |
| Hardcoded `0.4976` threshold in tests | **NONE** |

**Conclusion**: Changing coverage definitions or the SQLite analysis script carries **zero CI/CD blast radius**. Safe to proceed.

---

## 7. Key Finding: RCA Update Required

The original RCA estimated the delta at ~946 and attributed it to filter scope differences (utility scripts, config files, data modules). **The actual cause is different**:

- **Estimated cause**: Different module inclusion filters (~150 utils + ~50 configs + ~20 data)
- **Actual cause**: Different **coverage edge semantics** — SQLite uses direct edges only; accelerator uses transitive import-graph coverage
- The filter difference accounts for only ~97 utility scripts in the delta; the remaining **849 false gaps** are well-integrated production modules that are transitively covered via import chains

---

## 8. Revised Action Items (Updated from RCA)

| # | Action | Priority | Rationale |
|---|--------|----------|-----------|
| 1 | **Switch to accelerator as authoritative source** | ✅ Confirmed | Zero CI/CD impact; more accurate via transitive coverage |
| 2 | **Do NOT change SQLite filter logic** | ⚠️ Revised | Root cause is edge semantics, not filters; changing filters won't fix the 849 transitive false gaps |
| 3 | **Add transitive edge support to SQLite analysis** | Medium | To make SQLite match accelerator, add import-graph traversal — not just filter tuning |
| 4 | **Prioritize 966 true gaps** | High | Start with: apps_lic/reasoning (30), apps_rg/engines (33), L5_safety (167) |
| 5 | **Immediate: add test for `json_formatter_util.py`** | High | Only critical util with zero coverage in both systems |
| 6 | **Quarterly re-run** of Phase 0 validation | Medium | Re-confirm gap counts as codebase evolves |

---

## 9. Recommended Coverage Priority Order

Based on production criticality × true gap count:

1. **apps_lic/reasoning/** (30 agents) — active production LIC pipeline
2. **apps_rg/engines/** (33 engines) — active production RG pipeline
3. **L5_safety enforcement** (167 total L5 true gaps) — safety layer
4. **system_learning** (31 gaps) — meta-learning infrastructure
5. **L4_state caching** (45 gaps) — state/caching layer
6. **agentic_core/utils+types** (36 gaps) — includes `json_formatter_util.py`
7. **L3/L2 init files** (70 gaps) — mostly `__init__.py` files needing smoke tests

---

## 10. Artifacts Generated

| File | Description |
|------|-------------|
| `docs/reports/plans/phase0_validation_findings.json` | Raw numeric findings from validation script |
| `docs/reports/plans/phase0_deep_analysis.json` | Deep classification of all gap categories |
| `tools/evidence/_phase0_validation.py` | Validation script (rerunnable) |
| `tools/evidence/_phase0_deep_analysis.py` | Deep analysis script (rerunnable) |
| `docs/reports/plans/RCA_coverage_gap_discrepancy.md` | Original RCA (needs update per Finding #7) |

## Findings

[Document key findings from the investigation]

---

## Evidence

[Provide evidence supporting the findings]

---

