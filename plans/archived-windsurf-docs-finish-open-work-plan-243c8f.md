---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\finish-open-work-plan-243c8f.md'
original_relative_path: 'finish-open-work-plan-243c8f.md'
source_sha256: b9e243ab740c8f150b6127712a62c67b47208d39da40ce7edca65b7932182654
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-17'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Finish Open Workstreams — Detailed Implementation Plan

Close all open threads from the "Refactor Mixin and CI" and "RCA: Dedup Report SSOT Violation" sessions, covering 5 workstreams across HOP migration, CI validation, root-file evacuation, test coverage, and deferred cluster re-assessment.

**NOTE**: After approval, the final copy of this plan will be saved to `docs/reports/plans/` per Constitutional Rule #0.

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


## Phase 1: Evacuate Root-Level Report Files (Low risk, quick wins)

**Problem**: 10 `.md` files sit at repo root — violates `ARTIFACT_ROUTING_MAP` and ROOT_ALLOWED_PATTERNS.

**Steps**:

1. Classify each root `.md` file against `ARTIFACT_ROUTING_MAP` content signals:

   | File | Signals | Destination |
   | ---- | ------- | ----------- |
   | `RCA_Adapter_Classification.md` | RCA, SSOT, compliance | `docs/reports/audit/` |
   | `RCA_Dashboard_SSOT_Placement.md` | RCA, SSOT, compliance | `docs/reports/audit/` |
   | `RCA_LCD_MIGRATION_FAILURES_2026-02-07.md` | RCA, migration | `docs/reports/audit/` |
   | `RCA_Mixin_Agent_Compound_Suffix.md` | RCA, classification | `docs/reports/audit/` |
   | `RCA_Six_Structural_Defects.md` | RCA, structural | `docs/reports/audit/` |
   | `RCA_Structural_Defects_Round3.md` | RCA, structural | `docs/reports/audit/` |
   | `APPS_ARCHITECTURAL_ANOMALIES.md` | architecture, assessment | `docs/reports/assessments/` |
   | `ARCHITECTURAL_ANOMALIES.md` | architecture, assessment | `docs/reports/assessments/` |
   | `constitutional_compliance_manifest.md` | compliance, audit | `docs/reports/audit/` |
   | `final_variance_audit.md` | audit, variance | `docs/reports/audit/` |

2. Move each file to its classified destination.
3. Grep for any internal cross-references to these files and update them.
4. Verify repo root is clean: only allowed files per `ROOT_ALLOWED_PATTERNS`.

**Verification**: `fd --max-depth 1 --extension md` at repo root should return 0 results.

---

## Phase 2: Migrate HOP Agents to HOPStageCapability (Medium risk, high value)

**Problem**: `HOPStageCapability` exists with 9/9 tests, but 0 of 9 HOP agents use it.

**Agents** (9 total):
- `Hop1ProfileAnalysisAgent.py` (285 lines)
- `Hop2ResearchAgent.py`
- `HOP3SenderGroundingAgent.py`
- `Hop4RoutingAgent.py`
- `HOP5GenerationAgent.py` (411 lines)
- `Hop6ValidationAgent.py`
- `HOP7GateDecisionAgent.py`
- `HOP8QAReportAgent.py`
- `HOP9IntegrationAgent.py`

**Migration pattern per agent**:

1. **Add `HOPStageCapability` to MRO** (before `LICAgentBase`):
   ```python
   # BEFORE
   class HOP5GenerationAgent(SubatomicTestingMixin, LICAgentBase):
   # AFTER
   class HOP5GenerationAgent(HOPStageCapability, SubatomicTestingMixin, LICAgentBase):
   ```
2. **Set class variables**:
   ```python
   HOP_STAGE_NAME: ClassVar[str] = "hop5_generation"
   REQUIRED_INPUTS: ClassVar[list[str]] = ["hop1_analysis", "hop2_research", "hop3_sender_grounding", "hop4_routing"]
   ```
3. **Replace manual input reads** in `_process()` with `self.read_required_inputs(buffer, registry)`.
4. **Replace manual output writes** with `self.write_output(buffer, registry, output_data)`.
5. **Replace manual `PHASE_START`** trace with inherited `run_stage()` (if agent entry point calls `_process` directly, this is already handled).
6. **Keep all business logic** in `_process()` unchanged.

**Strategy**: Start with **HOP9IntegrationAgent** (simplest, shortest) as proof-of-concept, then batch remaining 8.

**Testing per agent**:
- AST parse check
- Import verification
- Existing `test_hop_stage_capability.py` tests still pass
- New test: verify each migrated agent has `HOPStageCapability` in MRO

**Verification**: All 9 agents have `HOPStageCapability` in MRO + all existing tests still pass/skip.

---

## Phase 3: Validate CI Workflows Locally (Medium risk)

**Problem**: Two GitHub Actions workflows were created but never ran in CI.

**Steps**:

1. **Dry-run `ssot-kernel-guardrail.yml` locally**:
   ```bash
   python -m agentic_core.L0_maintenance.enforcement.ssot_guardrail --fail --errors-only
   python -m pytest tests/core/test_classification_contract.py -xvv
   ```
   Both should pass (already verified in prior sessions).

2. **Dry-run `agent-sprawl-check.yml` locally**:
   ```bash
   python -m agentic_core.L0_maintenance.scripts.full_agent_discovery --summary
   python artifacts/dedup/run_dedup_analysis.py
   python artifacts/dedup/sprawl_gate.py --max-code-sim 0.85 --max-prompt-sim 0.85
   ```
   Discovery + dedup should succeed. Sprawl gate should report known breaches.

3. **Fix workflow issues** (found during exploration):
   - `ssot-kernel-guardrail.yml` uses `actions/setup-python@v4` — should be `v5` for consistency.
   - Neither workflow installs project deps — may need `pip install -e .` or at minimum `PYTHONPATH` (already set).
   - Sprawl gate threshold (0.85) may need tuning — current data shows 8 pairs ≥ 0.75, highest is 0.925 (CodeFormatter/UnusedCleanup, waived).

4. **Tune sprawl gate thresholds** based on current similarity data:
   - Code sim: 0.85 passes (only 1 pair above, waived)
   - Consider adding more waivers for known-acceptable pairs (e.g., HOP agent pairs at 0.75–0.78)

**Verification**: All 3 local dry-runs pass with exit code 0.

---

## Phase 4: Fix Test Skipping in Dedup Regression Tests (Medium risk)

**Problem**: All 22 tests in `test_consolidation_regression.py` skip due to cascading import failures (missing runtime deps like `timeout_decorator`, `security` modules).

**Steps**:

1. **Diagnose root import chain** — run one test with verbose skip output to see exact failing import.
2. **Determine fix approach**:
   - **Option A**: Add missing packages to dev dependencies in `pyproject.toml` — if they're real project deps that should be installed.
   - **Option B**: Mock the transitive imports in conftest — if the tests only need class structure, not runtime behavior.
   - **Option C**: Restructure tests to use AST-only verification (no live imports) — most resilient but more work.
3. **Implement fix** for at least the 4 `CodeToolRunnerCapability` architecture tests (Diamond Problem, pure capability, backward compat) — these are the highest-value tests to un-skip.
4. **Add regression test** for HOP capability migration (new test class `TestHOPStageCapabilityMigration`).

**Verification**: At least 4 core architecture tests pass (not skip), 0 fail.

---

## Phase 5: Re-Assess Deferred Clusters (Low risk, analysis only)

**Problem**: Clusters 1–5 were deferred. Current similarity data can inform next moves.

**Steps**:

1. **Review current similarity data** for each deferred cluster:

   | Cluster | Members | Top Score | Assessment |
   | ------- | ------- | --------- | ---------- |
   | 1 (13) | CoordinateObservabilityOps + 12 | 0.625 | RE-SCOPE — too broad, median sim low |
   | 2 (4) | ATSCompat + Brand + Fact + Section | 0.802 | **CANDIDATE** — all RGAgentBase, high code sim |
   | 3 (4) | DynamicSeal + HOP6 + Historian + LicS2 | 1.0 resp | **CANDIDATE** — 100% responsibility overlap ("validation") |
   | 4 (3) | HOP4 + HOP7 + HOP9 | 0.779 | **IN PROGRESS** — HOPStageCapability addresses this |
   | 5 (2) | CampaignBalance + Deliverability | 0.828 | **CANDIDATE** — high code sim, shared LIC base |

2. **Prioritize**:
   - Cluster 4: Handled by Phase 2 (HOP migration).
   - Cluster 5 (CampaignBalance + Deliverability): Extract shared LIC validation capability — same pure-mixin pattern.
   - Cluster 2 (RG agents): Extract shared RG validation/check capability.
   - Cluster 3: Investigate whether "validation" overlap is superficial (keyword match) or structural.
   - Cluster 1: Skip — too broad.

3. **Write updated consolidation roadmap** with priorities.

**Verification**: Updated `dedup_consolidation_plan.md` with cluster re-assessment.

---

## Execution Order & Time Estimates

| Phase | Description | Est. Effort | Dependencies |
| ----- | ----------- | ----------- | ------------ |
| 1 | Root file evacuation |  | None |
| 2 | HOP agent migration (9 agents) |  | None |
| 3 | CI workflow validation |  | None |
| 4 | Fix test skipping |  | Phase 2 |
| 5 | Cluster re-assessment |  | Phase 2 |

**Total**: ~. Phases 1, 2, 3 are independent and can be done in any order.

## Violation

[Describe the violation or issue that triggered this RCA]

---

## Root Cause

[Identify and explain the root cause of the violation]

---

## Corrective Actions

[List the corrective actions taken to resolve the issue]

---

