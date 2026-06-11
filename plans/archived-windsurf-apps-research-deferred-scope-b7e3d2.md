---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\apps-research-deferred-scope-b7e3d2.md'
original_relative_path: 'apps-research-deferred-scope-b7e3d2.md'
source_sha256: ef675e7b37792aae9414e67d113d19a0d9515a0ad8ed85bf9ac1338d2fe0db83
recovered_status: SURVIVED_IN_CURRENT
last_commit: '315fd11926d'
last_commit_date: '2026-05-06 06:26:53 -0400'
created_date: '2026-05-04'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Plan: apps-research-deferred-scope-b7e3d2

**Status**: Completed  
**Parent**: `apps-research-spine-deferred-followup-9c3e1a` (Completed 2026-05-04)  
**Created**: 2026-05-04  
**Completed**: 2026-05-04  

---

## Goal

Implement the deferred scope items explicitly excluded from
`apps-research-spine-deferred-followup-9c3e1a`. These items are out-of-scope
for the parent plan but represent known gaps that must be closed to reach
full production readiness for the `apps_research` engine.

---

## Deferred Scope Items

### DS-1: Real LLM-judge scoring for briefing rubric dims

**Source**: parent Out Of Scope § "Real LLM-judge scoring for briefing rubric dims (separate eval-harness plan)"

The eval-harness plan (`apps-eval-harness-deferred-e4a1b7`) landed LLM-judge
stubs (IS_STUB=True, GRADER_UNKNOWN_SENTINEL). `apps_research` briefing rubric
dims still use stub graders with no real Spearman ≥ 0.80 calibration.

**Acceptance criteria**:
- At least one briefing rubric dim (e.g. `citation_quality`, `coverage_depth`)
  wired to a non-stub grader with human-labeled holdout ≥ 50 pairs.
- Spearman correlation ≥ 0.80 between model scores and holdout labels.
- `judge_agreement_tracker.py` reports non-null `holdout_comparison` for dim.

---

### DS-2: `apps_rg` / `apps_lic` internal C0 binding changes

**Source**: parent Out Of Scope § "`apps_rg` / `apps_lic` internal C0 binding changes"

`apps_rg` and `apps_lic` have no equivalent of the `query_decomposer` C0
fan-out path. Their engines produce FEC output without a structured
`c0_bundle` or `depth_profile`. This mirrors the pre-W2 state of
`apps_research` and should be resolved to close AUDIT BLOCKER #4
(C0 FEC producer binding) for those apps.

**Acceptance criteria**:
- `apps_rg` and `apps_lic` FEC producers emit `schema_version == "1.1"`.
- Each has a coverage-family or equivalent structured retrieval plan driving
  the C0 bundle.
- `AEH1` gate reports 0 ERRORs for both apps.

---

### DS-3: UWG / L4 durable write path for research briefs

**Source**: parent Out Of Scope § "UWG / L4 durable write path"

Research brief outputs are not written through the `DurableWriteGateway`
(UWG). Briefs produced by `GovernedResearchRun` are ephemeral — they are
returned to the caller but not committed to any durable store. This means
brief provenance is not auditable at the L4 level.

**Acceptance criteria**:
- `GovernedResearchRun.run_governed_e2e()` commits the final brief (or a
  provenance record) through UWG before returning.
- UWG commit decision emits `ROUTER_DECISION:` + `emit_ledger_event` per §29.
- `L4_state` has a `research_brief_record` schema or equivalent.

---

### DS-4: `agentic_core` contract type modifications for research depth

**Source**: parent Out Of Scope § "`agentic_core` contract type modifications"

`ResearchRequest` in `apps_research/types/research_types.py` does not
include `depth_profile` or `jd_context` as typed fields. The current
implementation extracts these via `dict.get()` from `input_data`, which
bypasses the contract layer.

**Acceptance criteria**:
- `ResearchRequest` gains `depth_profile: str` (default `"standard"`) and
  `jd_context: dict` (default `{}`) typed fields.
- All call sites updated to use typed access.
- Pre-existing `test_l2_receipt_names_use_spine_terminology` passes (this
  test is currently failing due to stale `ResearchRequest` schema — fixing
  the schema closes it).

---

### DS-5: New depth profiles beyond DOSSIER

**Source**: parent Out Of Scope § "New depth profiles beyond DOSSIER"

`_DEPTH_PROFILES` in `query_decomposer.py` currently tops out at
`COMPANY_BRIEF_DOSSIER` (15 queries, 25 sources). Future use cases
(e.g. competitive intelligence, regulatory due diligence) may require
richer profiles. This item tracks the design and implementation of any
post-DOSSIER tier.

**Acceptance criteria**:
- At least one new profile (e.g. `COMPANY_BRIEF_FORENSIC` or similar)
  documented in `query_decomposer.py` with gate thresholds and SLO entry.
- `SLO.md` updated with new profile row.
- Mocked test (matching P3.1 pattern) added for the new profile.

---

## Wave Structure (placeholder — do not implement)

| Wave | Focus | Files | Est. Tokens | Status |
|------|-------|-------|-------------|--------|
| W1 | DS-4: `ResearchRequest` contract types + fix stale test | `apps_research/types/research_types.py`, call sites, tests | ~10K | ✅ DONE |
| W2 | DS-2: `apps_rg` + `apps_lic` C0 binding | `apps_rg/engines/`, `apps_lic/engines/`, cert producers | ~20K | ✅ DONE |
| W3 | DS-3: UWG durable write path for research briefs | `apps_research/integrations/governed_research_run.py`, `agentic_core/L4_state/` | ~15K | ✅ DONE |
| W4 | DS-1: LLM-judge scoring calibration for briefing dims | `apps_research/config/rubrics/`, judge calibration, holdout data | ~15K | ✅ DONE |
| W5 | DS-5: New depth profiles beyond DOSSIER | `apps_research/engines/query_decomposer.py`, `SLO.md`, tests | ~8K | ✅ DONE |

**Status legend**: 🔲 TODO · 🔄 IN PROGRESS · ✅ DONE · ❌ BLOCKED

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| 1.1 | Add `depth_profile` + `jd_context` to `ResearchRequest` | `apps_research/types/research_types.py` | Stale schema breaks `test_l2_receipt_names` | ~5K | 🔲 TODO |
| 1.2 | Update call sites to typed access | `company_brief_engine.py`, `governed_research_run.py` | Risk of regression on dict-access paths | ~5K | 🔲 TODO |
| 2.1 | `apps_rg` C0 fan-out + FEC v1.1 | `apps_rg/engines/`, `apps_rg/cert/fec_producer.py` | No query_decomposer equivalent | ~10K | 🔲 TODO |
| 2.2 | `apps_lic` C0 fan-out + FEC v1.1 | `apps_lic/engines/`, `apps_lic/cert/fec_producer.py` | Multi-hop complexity | ~10K | 🔲 TODO |
| 3.1 | UWG write path for research briefs | `governed_research_run.py`, `DurableWriteGateway` | ROUTER_DECISION emit required | ~10K | 🔲 TODO |
| 3.2 | L4 research_brief_record schema | `agentic_core/L4_state/` | agentic_core contract freeze risk | ~5K | 🔲 TODO |
| 4.1 | Human-labeled holdout for citation_quality dim | `apps_research/config/rubrics/`, `data/judge_calibration/` | Manual annotation burden | ~8K | 🔲 TODO |
| 4.2 | Wire non-stub grader + calibrate Spearman | judge files, `judge_agreement_tracker.py` | Requires real LLM calls | ~7K | 🔲 TODO |
| 5.1 | New depth profile design + implementation | `query_decomposer.py`, `SLO.md`, tests | Profile naming, gate threshold design | ~8K | 🔲 TODO |

---

## Prerequisites

- `apps-research-spine-deferred-followup-9c3e1a` **Completed** ✅
- `apps-eval-harness-deferred-e4a1b7` **Completed** ✅ (judge stub infra in place)
- Human-labeled holdout data for DS-1 (external dependency — blocks W4)
- ADG MCP green before W2/W3 (cross-layer changes)

---

## Out Of Scope

- `apps_exec`, `apps_rfp`, `apps_underwriting_ai`, `apps_qna` C0 binding (separate plan per app)
- Production log mining with PII redaction
- SSOT consolidation of legacy policy/threshold YAMLs
- Holdout vs dev eval-set separation (parent eval-harness W5.P1)
