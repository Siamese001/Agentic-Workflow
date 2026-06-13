# Parallel Workstreams Status — Cross-Chat Summary

**Date**: 2026-02-08
**Source chats**: "Refactor Mixin and CI" (667 steps), "RCA: Dedup Report SSOT Violation" (227 steps)
**Purpose**: Consolidate all threads of work opened across both sessions, identify what's done, what's partially done, and what's still pending.

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


## Master Status Table

| # | Theme | Status | Chat | Summary | Next Steps |
|---|-------|--------|------|---------|------------|
| 1 | **Classification Kernel SSOT** | ✅ DONE | Refactor | Created `agentic_core/core/classification_kernel.py` — zero-dependency, LRU-cached. 15+ files with duplicate logic refactored to delegate. Agent count stabilized at 190 (was 397). | None — locked by contract tests + CI guardrail. |
| 2 | **SSOT Guardrail (Shadow Detection)** | ✅ DONE | Refactor | Created `ssot_guardrail.py` — AST scanner detecting shadow classification. 7 initial errors → 0 after Phase 2b. 2601 files scanned. | None — locked by `.github/workflows/ssot-kernel-guardrail.yml`. |
| 3 | **Contract Tests (Kernel)** | ✅ DONE | Refactor | 68 parametrized tests in `tests/core/test_classification_contract.py`. Golden set covers 15 of 20 FileTypes. Agent count regression band [170, 220]. | None — locked by CI workflow. |
| 4 | **Mixin → Pure Capability Refactor** | ✅ DONE | Refactor | `CodeToolRunnerMixin(SovereignBaseAgent)` → `CodeToolRunnerCapability` (no base class). Diamond Problem eliminated. Backward-compat alias preserved. | None — 4 architectural tests lock the fix. |
| 5 | **CI Sprawl Gate** | ✅ DONE | Refactor | Created `artifacts/dedup/sprawl_gate.py` — hard threshold gate (code sim, prompt sim, responsibility overlap). Exits non-zero on breach. Waiver system for known-acceptable pairs. | **Wire into actual CI** — `.github/workflows/agent-sprawl-check.yml` created but not yet validated in real PR. |
| 6 | **HOP Shared Plumbing Extraction** | ⚠️ PARTIAL | Refactor | Created `apps_lic/utils/hop_stage_capability.py` — pure capability class extracting IO/State edge plumbing from 9 HOP agents. 9/9 unit tests pass. | **Migrate 9 HOP agents** to actually use `HOPStageCapability`. Currently the capability exists but no agent consumes it yet. |
| 7 | **Import Complexity Metrics** | ✅ DONE | Refactor | Added blast-radius analysis to `run_dedup_analysis.py`. 190 agents analyzed: avg=4.3 internal imports, max=29 (FileClassificationAgent). Output: `artifacts/dedup/similarity/import_complexity.md`. | None — pipeline produces metrics on every run. |
| 8 | **Dedup Analysis Pipeline** | ✅ DONE | Both | Full `run_dedup_analysis.py` pipeline: Phase 0 (discovery), Phase 1 (similarity + import complexity), Phase 2 (clustering + plans + policy). Produces 8+ artifacts. | Consider adding import complexity delta tracking over time. |
| 9 | **Dedup Report SSOT Placement** | ✅ DONE | RCA | Reports moved from `artifacts/dedup/` → correct `docs/reports/` subfolders. `run_dedup_analysis.py` now imports `DOCS_REPORTS_PLANS` from blueprint. Content-signal routing via `ARTIFACT_ROUTING_MAP`. | None — hardened. |
| 10 | **ARTIFACT_ROUTING_MAP Compliance** | ✅ DONE | RCA | Files classified against content signals: plans → `docs/reports/plans/`, audit/compliance → `docs/reports/audit/`. Flat-file convention enforced (no sub-subfolders). Root-level `docs/reports/` files evacuated. | None. |
| 11 | **Shadow Classification Liquidation (Phase 2b)** | ✅ DONE | Refactor | 7 shadow errors eliminated. 3 files delegated to kernel. 4 files renamed to avoid `classify_file()` name collision (e.g., `analyze_app_files_util` → `classify_app_domain`). | None — guardrail now at 0 errors. |
| 12 | **Agent Dedup Consolidation (Clusters)** | ⚠️ PARTIAL | Refactor | Cluster 6 (CodeFormatter + UnusedCleanup): DONE — shared core extracted. Cluster 7 (ContentStrategyAgent): DONE — retired with deprecation shim. Clusters 1–5: DEFERRED. | **Cluster 4** (HOP): capability ready, agents not yet migrated. **Clusters 1–3, 5**: need re-assessment after HOP migration completes. |
| 13 | **Mixin Compound Suffix Hardening** | ✅ DONE | Prior work | 7 MIXIN compound patterns added to `COMPOUND_SUFFIX_CONFLICTS`. `"mixins": "MIXIN"` added to FCA folder-to-filetype. `autonomy_mixin_agent_mixin.py` deleted (duplicate). `neuralautoimmuneagent_mixin.py` → `neural_autoimmune_mixin.py`. | None. |
| 14 | **PSF (Pascal Sovereignty Fixer) Kernel Delegation** | ✅ DONE | Refactor | 86-line `classify_file()` in PSF replaced with 10-line kernel delegation + type mapping. | None. |
| 15 | **`run_classification.py` Kernel Delegation** | ✅ DONE | Refactor | 130-line independent `classify_file()` replaced with kernel `classify_file_standalone()` call. | None. |

---

## Risk / Attention Items

| Risk | Severity | Detail |
|------|----------|--------|
| **HOP agents not yet migrated** | Medium | `HOPStageCapability` exists with 9/9 tests passing, but zero HOP agents actually use it yet. Without migration, the shared plumbing extraction is "ready but unused." |
| **Deferred clusters (1–3, 5)** | Low | These represent potential future consolidation but were consciously deferred due to higher risk / lower confidence. The sprawl gate will flag if they regress. |
| **22 regression tests all SKIP** | Medium | `test_consolidation_regression.py` has 22 tests that all skip due to missing runtime deps (same as all existing agent tests). They validate structure only when deps are available. |
| **6 root-level RCA files** | Low | `RCA_Adapter_Classification.md`, `RCA_Mixin_Agent_Compound_Suffix.md`, etc. still sit at repo root. Should be routed to `docs/reports/audit/` per ARTIFACT_ROUTING_MAP. |
| **GitHub Actions workflows untested** | Medium | `agent-sprawl-check.yml` and `ssot-kernel-guardrail.yml` were created but haven't been validated in a real CI run / PR yet. |

---

## Recommended Priority for Next Session

1. **Validate CI workflows** — Push a test PR to confirm both `ssot-kernel-guardrail.yml` and `agent-sprawl-check.yml` run correctly.
2. **Migrate 1–2 HOP agents** to `HOPStageCapability` as proof-of-concept, then batch the remaining 7.
3. **Evacuate 6 root-level RCA files** to `docs/reports/audit/` using content-signal classification.
4. **Investigate skipped tests** — Determine if missing runtime deps can be stubbed to get real test coverage.
5. **Re-assess deferred clusters** (1–3, 5) with current similarity data.

---

## Files Created / Modified Across Both Sessions

### New files (12)
- `agentic_core/core/__init__.py`
- `agentic_core/core/classification_kernel.py`
- `agentic_core/L0_maintenance/enforcement/ssot_guardrail.py`
- `agentic_core/L5_safety/reasoning/code_tool_runner_core.py`
- `apps_lic/utils/hop_stage_capability.py`
- `artifacts/dedup/sprawl_gate.py`
- `.github/workflows/ssot-kernel-guardrail.yml`
- `.github/workflows/agent-sprawl-check.yml`
- `tests/core/__init__.py`
- `tests/core/test_classification_contract.py`
- `tests/unit/dedup/test_consolidation_regression.py`
- `tests/unit/dedup/test_hop_stage_capability.py`

### Modified files (20+)
- `agentic_core/L5_safety/reasoning/FileClassificationAgent.py`
- `agentic_core/L0_maintenance/utils/complexity_visitor_util.py`
- `agentic_core/L0_maintenance/scripts/full_agent_discovery.py`
- `agentic_core/runtime/utils/discovery_util.py`
- `agentic_core/prompt_governance/scripts/file_intent.py`
- `agentic_core/L5_safety/validators/type_erasure_validator.py`
- `agentic_core/L5_safety/enforcement/ssot_scanner_enforcer.py`
- `agentic_core/L0_maintenance/scripts/extract_agent_duplicates_util.py`
- `agentic_core/L0_maintenance/scripts/find_real_duplicates_v2_util.py`
- `agentic_core/L0_maintenance/scripts/pascal_sovereignty_fixer.py`
- `agentic_core/L0_maintenance/scripts/generate_agent_table_simple_util.py`
- `agentic_core/L5_safety/reasoning/CodeFormatterAgent.py`
- `agentic_core/L5_safety/reasoning/UnusedCleanupAgent.py`
- `ops_scripts/maintenance/run_classification.py`
- `ops_scripts/general/mece_test_rebaseline.py`
- `ops_scripts/general/agent_disposition_analyzer.py`
- `ops_scripts/general/file_classification.py`
- `agentic_core/L0_maintenance/scripts/analyze_app_files_util.py`
- `agentic_core/L0_maintenance/scripts/class_info.py`
- `artifacts/dedup/run_dedup_analysis.py`

### Reports generated (6)
- `docs/reports/plans/fca-ssot-kernel-consolidation.md`
- `docs/reports/plans/phase3b-architectural-hardening-report.md`
- `docs/reports/plans/dedup_consolidation_plan.md`
- `docs/reports/plans/dedup_stop_sprawl_policy.md`
- `docs/reports/audit/dedup_validation_report.md`
- `docs/reports/audit/RCA_dedup_report_SSOT_violation.md`

## Violation

[Describe the violation or issue that triggered this RCA]

---

## Root Cause

[Identify and explain the root cause of the violation]

---

## Corrective Actions

[List the corrective actions taken to resolve the issue]

---

