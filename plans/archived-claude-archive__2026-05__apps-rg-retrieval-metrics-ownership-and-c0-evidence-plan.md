---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\apps-rg-retrieval-metrics-ownership-and-c0-evidence-plan.md'
original_relative_path: '_archive\\2026-05\\apps-rg-retrieval-metrics-ownership-and-c0-evidence-plan.md'
source_sha256: ced51ca7ffe6eed657e5e36eb0cf716b8773e310f1f3c6d4502c7b67f7f60e80
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_slug: apps-rg-retrieval-metrics-ownership-and-c0-evidence-plan
plan_title: "Apps_RG Retrieval Metrics Ownership + C0 Evidence Serialization Plan"
status: Completed
created_at: 2026-05-14
app_scope: apps_rg
layer_scope: C0, U0/profile, Exit
task_class: resume_generation
dod_exempt: false
---

# Apps_RG Retrieval Metrics Ownership + C0 Evidence Serialization Plan

## 1. Mental Model

```
apps_rg defines what evidence is needed, resume-specific metrics, thresholds, and release criteria.
agentic_core C0 computes generic retrieval evidence metrics.
apps_rg scoring/Exit interprets whether those metrics are good enough for resume generation.
agentic_core Exit applies the configured profile and emits X3.
agentic_core remains pure and app-agnostic throughout.
```

Ownership split (invariant, never blurred):

| Layer | Owns |
|---|---|
| apps_rg U0 / profile | Declares evidence requirements, source classes, thresholds, briefing policy |
| agentic_core C0 | Computes generic retrieval metrics, populates FinalEvidenceContract |
| apps_rg scoring / Exit | Interprets resume-specific quality: JD coverage, overfit, provenance_valid |
| agentic_core Exit | Applies configured profile, emits X3 — never app-specific logic |

---

## 2. Hard Rules

1. Do not add JD/resume-specific logic to `agentic_core`.
2. Do not make `apps_rg` perform generic C0 metric computation.
3. Do not treat uploaded briefing, delegated `apps_research` briefing, and native `apps_rg` C0 as the same path — each must be distinct and explicitly labeled.
4. Do not use `support_status` enum drift. Permitted values only:
   `PASS`, `WEAK_WITH_CAVEATS`, `CONFLICTED`, `EMPTY`, `BLOCKED`, `UNKNOWN`.
   **`PARTIAL` is not in the canonical enum — do not use it.**
5. `UNKNOWN`, `EMPTY`, `BLOCKED`, or `CONFLICTED` must never silently pass Exit.
6. This plan covers metrics/profile/serialization/Exit-consumption only. Do not build deep native `apps_rg` company research.
7. Do not proceed past a wave if its acceptance checks fail.
8. Do not patch around failures by weakening tests.

---

## 3. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| W0 | W0 | Baseline evidence audit — produce ownership table | ~3k | Repo truth already surveyed from previous session | ✅ DONE | Ownership table complete, every row cited |
| W1 | W1 | apps_rg retrieval profile (definition only, no retrieval) | ~5k | `retrieval_profiles.yaml` exists but incomplete | ✅ DONE | Profile file passes validation tests |
| W2 | W2 | Core C0 metrics extraction + enum alignment | ~6k | FinalEvidenceContract shape is stable | ✅ DONE | Enum gate tests pass; agentic_core stays generic |
| W3 | W3 | Durable `c0_metrics.json` artifact per run | ~5k | Exit binding writes artifacts to `artifacts/apps_rg/runs/<run_id>/` | ✅ DONE | c0_metrics.json created with stable schema |
| W4 | W4 | apps_rg scoring/Exit consumption | ~6k | Exit binding shape known from plan d4e8a1 | ✅ DONE | Exit reads C0 metrics; X1D/X2/X3 affected by support_status |
| W5 | W5 | Briefing path proof | ~4k | Three distinct briefing modes already partially wired | ✅ DONE | Each mode produces distinct retrieval_mode in artifact |
| W6 | W6 | Governance + anti-contamination tests | ~5k | Existing test suite is green | ✅ DONE | All boundary tests pass; no core leakage |
| W7 | W7 | Final evidence receipt | ~2k | All prior waves green | ✅ DONE | Receipt complete, gaps listed |

---

## 4. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| W0 | Baseline evidence audit | Read-only survey of `apps_rg/runtime/bindings/c0_binding.py`, `agentic_core/runtime/contracts/final_evidence_contract.py`, `apps_rg/config/domain_contract/retrieval_profiles.yaml`, `resume_c0_minimum_safety_profile.v1.json`, `exit_profile.resume_generation.v1.json`, run artifacts | Legacy ATS/overfit code is commented-out quarantined; current pipeline gaps are not obvious | ~3k | ✅ DONE |
| W1 | apps_rg retrieval profile | `apps_rg/config/domain_contract/retrieval_requirements_profile.resume_generation.v1.yaml` (new), `apps_rg/runtime/profiles/retrieval_requirements.py` | `_NORMATIVE_SOURCE_CLASSES` was hardcoded in C0 binding — moved to profile | ~5k | ✅ DONE |
| W2 | C0 metrics extraction + enum | `agentic_core/runtime/c0/evidence_metrics_extractor.py` (new), `agentic_core/runtime/contracts/final_evidence_contract.py` (PARTIAL removed from PASSING_VALUES) | `PARTIAL` used in c0_binding.py violated canonical enum; extractor coerces PARTIAL→WEAK_WITH_CAVEATS | ~6k | ✅ DONE |
| W3 | c0_metrics.json artifact writer | `apps_rg/runtime/bindings/c0_metrics_writer.py` (new), `apps_rg/runtime/schemas/c0_metrics.schema.json` | Writer lives in apps_rg/runtime/bindings/, never in agentic_core | ~5k | ✅ DONE |
| W4 | Exit consumption | `apps_rg/runtime/bindings/exit_binding.py` (support_status gating, `_BLOCKING_SUPPORT_STATUSES`, `_evaluate_c0_evidence_gates`) | Exit now reads support_status and blocks on UNKNOWN/EMPTY/BLOCKED/CONFLICTED | ~6k | ✅ DONE |
| W5 | Briefing path proof | `apps_rg/runtime/bindings/briefing_mode_classifier.py` (new), briefing path tests | Four briefing modes labeled distinctly in retrieval_mode; classifier owned by apps_rg | ~4k | ✅ DONE |
| W6 | Governance tests | `tests/_apps_contract/test_rg_retrieval_metrics_governance.py` (new, 62 tests); `tests/unit/ops_scripts/ci/test_check_no_shadow_spine.py` (new, 20 tests) | 362/362 W1-W6 tests passing; SS-2 regression guard added for app-owned stage-named bindings; PARTIAL bug fixed in final_evidence_contract.py | ~5k | ✅ DONE |
| W7 | Final receipt | `docs/reports/apps_rg/retrieval_metrics_receipt_20260514.md` | None | ~2k | ✅ DONE |

---

## 5. W0 — Baseline Evidence Audit

### Goal
Find current repo truth before changing anything.

### Scope
- `apps_rg` U0/profile/runtime customization inputs
- `apps_rg` C0 binding and briefing handoff logic
- `agentic_core` C0 / `FinalEvidenceContract` / evidence contracts
- `apps_rg` scoring/reporting/Exit profile
- Run artifact writers

### Deliverable
**Ownership Table** — completed from prior session repo survey (zero-loss below):

| Metric | apps_rg U0/profile role | agentic_core C0 role | apps_rg scoring/Exit role | Current repo location | Status | Notes |
|---|---|---|---|---|---|---|
| `required_source_classes` | **Defines** — `_NORMATIVE_SOURCE_CLASSES` tuple hardcoded in C0 binding (6 classes) | **Consumes** — drives `_compute_support_status()` coverage check | N/A | `apps_rg/runtime/bindings/c0_binding.py:56–63` | **Partial** | Defined inside C0 binding, not in a U0/profile config file. No profile field exposes these. |
| `support_target` | **Defines implicitly** — `retrieval_profiles.yaml` declares `required_evidence_for` per-claim entries | **Computes** — `is_sufficient = has_jd and has_resume`; populates `support_target_met` and `support_target_partial` | N/A | `apps_rg/config/domain_contract/retrieval_profiles.yaml`, `apps_rg/runtime/bindings/c0_binding.py:912–921` | **Partial** | Profile declarative requirements not consumed by C0; sufficiency is JD+resume presence only. |
| `briefing_source_type` | **Defines** — `manual_brief_path`, `auto_research_internal`, `research_via` on `AppsRgIngressPayload`; safety profile bans company research inside C0 | **Consumes if routed** — reads `manual_brief_path` via `policy_refs` dict; appends `manual_brief:<path>` to `retrieval_sources` | N/A | `agentic_core/runtime/contracts/apps_rg_ingress_payload.py:38–43`, `apps_rg/runtime/bindings/c0_binding.py:882–890`, `apps_rg/config/domain_contract/resume_c0_minimum_safety_profile.v1.json:107–117` | **Partial** | Source type not emitted as named enum field in FEC. Raw path only. |
| `company_brief_provenance` | **Defines/tracks** — `company_research.schema.json` mandates `source`, `fetched_at`, `freshness_ttl_days`; safety profile sets `freshness_max_age_hours: 72` | **Carries metadata** — brief read as `EvidenceItem.source="manual_brief:…"` with `retrieval_timestamp`; no structured provenance sub-object | N/A | `apps_rg/config/schemas/company_research.schema.json`, `apps_rg/config/domain_contract/resume_c0_minimum_safety_profile.v1.json:107–117`, `apps_rg/runtime/bindings/c0_binding.py:882–890` | **Partial** | Brief schema exists; C0 does not extract `source`/`fetched_at` into FEC. Visible in legacy `narrative/scorecard.json` artifact-only. |
| `retrieval_sources` | N/A | **Computes** — accumulates string identifiers per source: `jd_payload`, `resume_payload`, `manual_brief:<path>`, `master_resume:header_exec_summary`, `chromadb:<source_class>:<source_id>` | **Reads** — referenced via `FinalEvidenceContract.retrieval_sources`; not inspected in current `exit_binding.py` | `apps_rg/runtime/bindings/c0_binding.py:843–953`, `agentic_core/runtime/contracts/final_evidence_contract.py` | **Present** | Fully computed; not serialized to disk. |
| `support_status` | **Sets expectation** — `resume_exit_checks_profile.v1.json:support_status.sendable_blocking_values`; `resume_c0_minimum_safety_profile.v1.json:support_status_rules` | **Computes** — `_compute_support_status()` returns `PASS/PARTIAL/WEAK/EMPTY/UNKNOWN`; file-only path → `STATUS_UNKNOWN` | **Uses in Exit** — `resume_exit_checks_profile.v1.json` declares blocking values but `exit_binding.py` does not read `fec.support_status` at runtime | `apps_rg/runtime/bindings/c0_binding.py:209–242`, `apps_rg/config/domain_contract/resume_c0_minimum_safety_profile.v1.json`, `apps_rg/config/domain_contract/resume_exit_checks_profile.v1.json` | **Partial** | Profile declares contract; Exit binding does not enforce it. Also: `PARTIAL` is returned by C0 but is not in the canonical enum. |
| `support_target_met` | N/A | **Computes** — `support_target_met = has_jd and has_resume`; `support_target_partial` set identically | N/A | `apps_rg/runtime/bindings/c0_binding.py:948–949`, `agentic_core/runtime/contracts/final_evidence_contract.py` | **Partial** | Field exists and is computed; Exit binding never reads it; no gate checks it. |
| `excluded_evidence_refs` | N/A | **Computes** — chunks with `invalid_for_normative_use=True` or missing `citation_anchor` excluded | N/A | `apps_rg/runtime/bindings/c0_binding.py:193–222`, `agentic_core/runtime/contracts/final_evidence_contract.py` | **Present** | Computed; not serialized to disk; not read at Exit. |
| `confidence_score` | N/A | **Computes** — `max(0.0, 1.0 - chunk._distance)` per Chroma chunk; per-item on `EvidenceItem.confidence_score` | N/A | `apps_rg/runtime/bindings/c0_binding.py:280`, `agentic_core/runtime/contracts/final_evidence_contract.py:EvidenceItem.confidence_score` | **Present** | Per-item; never aggregated, gated, or serialized. |
| `freshness_receipts` | **Provides policy** — `retrieval_profiles.yaml:freshness_class: bounded`; safety profile `briefing_policy.freshness_max_age_hours: 72`; gate G09 declared at `severity: warn` | **Computes** — `freshness_refs` list from chunk `freshness` metadata; `STATUS_UNKNOWN` when absent | N/A | `apps_rg/config/domain_contract/retrieval_profiles.yaml:6`, `apps_rg/config/domain_contract/resume_c0_minimum_safety_profile.v1.json:36–39`, `apps_rg/config/domain_contract/runtime_gate_profile.resume_generation.v1.json:G09`, `apps_rg/runtime/bindings/c0_binding.py:267–270` | **Partial** | Policy declared; C0 populates when Chroma active; never evaluated at Exit; G09 declared but not connected. |
| `citation_map` | **Requires citations** — gate G13 at `severity: hard_fail`; `prompt_profiles.yaml:required_slots` includes `evidence_citation_map`; safety profile `citation_map.absent_verdict: WARN` | **Computes** — `citation_pairs = (evidence_id, citation_anchor)` per valid Chroma chunk; empty on file-only path | N/A | `apps_rg/config/domain_contract/runtime_gate_profile.resume_generation.v1.json:G13`, `apps_rg/config/domain_contract/prompt_profiles.yaml:11`, `apps_rg/runtime/bindings/c0_binding.py:257–263` | **Partial** | Hard-fail gate declared; C0 populates when Chroma active; Exit binding has no code evaluating `fec.citation_map`. |
| `evidence_digest` | N/A | **Computes** — SHA-256 over `source:content[:100]` for all evidence items | **Uses for provenance** — digest threaded into `prompt_artifact.evidence_digest` in `run_metadata.json`; Exit gate G24 chains from it | `apps_rg/runtime/bindings/c0_binding.py:900–905`, `agentic_core/runtime/contracts/final_evidence_contract.py:FinalEvidenceContract.final_evidence_digest`, `apps_rg/runtime/bindings/exit_binding.py:G24` | **Present** | Only metric exercised end-to-end: computed → threaded → validated at Exit. Serialized in `run_metadata.json:prompt_artifact.evidence_digest`. |
| `jd_keyword_coverage` | **Defines target/profile** — `specs/agent_spec.resume_generation.v1.0.0.yaml`; `SLO.md` states ≥80% floor; ATS engine owns logic | N/A | **Computes** — legacy path only: `integrations/ats_coverage.py` (commented-out); narrative scorecard writes `jd_keyword_coverage.coverage_result`; current `exit_binding.py` does not compute this | `apps_rg/integrations/ats_coverage.py` (commented out), `apps_rg/config/specs/agent_spec.resume_generation.v1.0.0.yaml`, artifact: `narrative/scorecard.json:jd_keyword_coverage` | **Partial** | Computed only in legacy narrative pipeline. Current exit_binding.py does not compute or gate on it. |
| `must_have_covered / total` | **Defines must-haves** — JD parsing extracts `must_have` terms; `ats_coverage.py` defines `ATSCoverageResult.must_have_total/covered` | N/A | **Computes** — legacy path only | `apps_rg/integrations/ats_coverage.py:70–82` (commented out), artifact: `narrative/scorecard.json:jd_keyword_coverage.coverage_result.must_have_covered/total` | **Partial** | Artifact-only in current runs; code path commented out. |
| `missing_keywords` | **Defines target terms** — JD parsing implicit | N/A | **Computes** — legacy path only | `apps_rg/integrations/ats_coverage.py:72` (commented out), artifact: `narrative/scorecard.json:jd_keyword_coverage.coverage_result.missing` | **Partial** | Artifact-only in current runs. Not surfaced through Exit. |
| `overfit_score` | **Defines threshold** — `specs/agent_spec.resume_generation.v1.0.0.yaml:anti_overfit_profile.mimicry_max: 0.30`; `overfit_risk_max: 1.0`; `integrations/anti_overfitting.py` referenced in runbook | N/A | **Computes** — legacy orchestrator path only; written as `overfit_report.score/flags/warning/escalate` in `run_report.json` | `apps_rg/config/specs/agent_spec.resume_generation.v1.0.0.yaml:195–198`, `apps_rg/integrations/anti_overfitting.py` (quarantined), artifact: `run_report.json:overfit_report` | **Partial** | Thresholds declared; computation quarantined; not connected to current Exit binding or any exit gate. |
| `provenance_valid` | **Defines expected provenance** — `exit_profile.resume_generation.v1.json:G24` lists 16 required provenance fields; `docx_manifest_v1.yaml` declares `provenance_report` required | **Supports** — provides `evidence_digest` as anchor | **Computes/interprets** — G24 checks `sealed.sovereign_execution_receipt` and `sealed.compilation_hash` chain only; legacy `run_report.json:provenance_report.valid/reason` not produced by current bindings | `apps_rg/config/domain_contract/exit_profile.resume_generation.v1.json:G24`, `apps_rg/runtime/bindings/exit_binding.py:_safe_build_g24_provenance`, `apps_rg/integrations/hitl_bridge.py:90` (commented), artifact: `run_report.json:provenance_report` | **Partial** | G24 enforces receipt + hash chain but not the full 16-field list. Legacy `provenance_report.valid` flag not produced by current bindings. |

### Gap Summary from W0

**apps_rg U0/profile gaps:**
- `required_source_classes` — hardcoded in `c0_binding.py`, not in any profile config.
- `support_target` — `retrieval_profiles.yaml` has `required_evidence_for` but C0 does not read it.
- `briefing_source_type` — no enumerated field distinguishes briefing modes in FEC.
- `company_brief_provenance` — brief schema has fields; C0 does not extract them.

**agentic_core C0 serialization gaps:**
- No run artifact serialization — all FEC retrieval fields are in-memory only.
- File-only path degrades silently — UNKNOWN status with no artifact evidence.
- `PARTIAL` returned by `_compute_support_status()` — not in canonical enum.
- `company_brief_provenance` fields not extracted into FEC.

**apps_rg scoring/Exit interpretation gaps:**
- `support_status` not enforced at Exit — profile declares blocking values; `exit_binding.py` does not read them.
- `support_target_met` not gated.
- G13 (citation_map hard-fail) not connected to Exit evaluation.
- G09 (freshness warn) not evaluated at runtime.
- `jd_keyword_coverage`, `overfit_score`, `provenance_valid` computed only in quarantined/commented-out pipeline.

**Artifact/reporting gaps:**
- No `c0_metrics.json` or equivalent per-run artifact.
- `jd_keyword_coverage`, `overfit_report`, `provenance_report` absent from current pipeline runs.
- `pool_first_hit_rate` — legacy path only; no current definition.

### Acceptance Checks
- [x] Every row cites exact file path and symbol/artifact.
- [x] Artifact-only fields marked artifact-only.
- [x] Missing fields marked Missing or Partial, not inferred.
- [x] No code changes in W0.

**Status: ✅ DONE**

---

## 6. W1 — apps_rg Retrieval Profile

### Goal
Make `apps_rg` explicitly define what evidence a resume run needs.

### Scope
Implement or extend an `apps_rg`-owned retrieval profile with:
- `required_source_classes`
- `optional_source_classes`
- `support_target`
- `briefing_source_type`
- `company_brief_provenance_policy`
- `freshness_profile`
- `citation_requirement`
- `jd_requirement_policy`
- `candidate_fact_policy`
- `minimum_grounding_thresholds`
- `overfit_threshold`

**Target file:** `apps_rg/config/domain_contract/retrieval_profiles.yaml` (extend existing) or new `apps_rg/config/domain_contract/retrieval_requirements_profile.resume_generation.v1.yaml`

### Rules
- This profile defines requirements only. It must not retrieve.
- It must not compute generic C0 metrics.
- It must not modify `agentic_core` with `apps_rg`-specific logic.
- `_NORMATIVE_SOURCE_CLASSES` in `c0_binding.py` must be derivable from this profile (or the profile must make the current hardcoded values explicit and documented).

### Briefing Source Types (explicit taxonomy)
```
UPLOADED_BRIEFING       — user supplied manual_brief_path; pre-built JSON
DELEGATED_APPS_RESEARCH — apps_research delegated via research_via="apps_research"
NATIVE_C0               — no brief; apps_rg C0 retrieves from Chroma
NONE                    — no briefing, no Chroma; file-only path only
```

### Acceptance Checks
- [x] Profile file passes schema validation (YAML lint or JSON schema).
- [x] `apps_rg` can distinguish required JD, candidate resume, master resume, and optional briefing paths.
- [x] All four briefing source types are explicitly named.
- [x] Tests prove profile serialization/validation.
- [x] `agentic_core` untouched.

**Status: ✅ DONE** — Profile at `apps_rg/config/domain_contract/retrieval_requirements_profile.resume_generation.v1.yaml`; loader at `apps_rg/runtime/profiles/retrieval_requirements.py`; `get_normative_source_classes()` resolves from profile.

---

## 7. W2 — Core C0 Metrics Extraction and Enum Alignment

### Goal
Normalize generic retrieval evidence metrics from `FinalEvidenceContract` without app leakage.

### Scope
- Audit and align `support_status` enum across:
  - `agentic_core/runtime/contracts/final_evidence_contract.py` (sentinels)
  - `apps_rg/runtime/bindings/c0_binding.py` (`_compute_support_status` returns `PARTIAL` — fix)
  - `apps_rg/config/domain_contract/resume_c0_minimum_safety_profile.v1.json` (lists `PARTIAL` in rules)
- Implement a generic extraction helper if needed:
  `agentic_core/runtime/c0/evidence_metrics_extractor.py` (or equivalent) that can derive:
  - `retrieval_sources`
  - `support_status`
  - `support_target_met`
  - `evidence_counts`
  - `excluded_evidence_refs`
  - `blocked_source_refs`
  - `confidence_scores` (per-item list when present)
  - `freshness_receipts`
  - `citation_map`
  - `support_score_profile`
  - `final_evidence_digest`

### Canonical support_status Enum
```
PASS             — all required source classes covered
WEAK_WITH_CAVEATS — present but below threshold (replaces WEAK)
CONFLICTED       — internal contradiction detected
EMPTY            — zero normative items
BLOCKED          — ACL or policy block
UNKNOWN          — could not determine (default when Chroma inactive)
```
**`PARTIAL` is not permitted.**

### Rules
- No JD/resume/company-specific logic in `agentic_core`.
- `support_target_met` is computed against the provided app target, not hardcoded.
- Generic extractor returns a typed dict or dataclass; never imports from `apps_rg`.

### Acceptance Checks
- [x] Tests fail if `PARTIAL` appears as `support_status` in FEC or extractor output.
- [x] Tests prove `support_target_met` changes based on supplied target.
- [x] Tests prove `agentic_core` extractor has zero imports from `apps_rg.*`.
- [x] `_compute_support_status` in `c0_binding.py` returns only canonical enum values.
- [x] Existing `agentic_core` tests still pass.

**Status: ✅ DONE** — `evidence_metrics_extractor.py` created in `agentic_core/runtime/c0/`; PARTIAL coerced → WEAK_WITH_CAVEATS; `SUPPORT_STATUS_PASSING_VALUES` bug fixed (PARTIAL incorrectly re-added by prior commit `1134ea2ba0` — removed to restore W2 invariant).

---

## 8. W3 — Durable apps_rg c0_metrics.json Artifact

### Goal
Write retrieval metrics to disk per `apps_rg` run.

### Artifact Path
```
artifacts/apps_rg/runs/<run_id>/c0_metrics.json
```

### Minimum Schema
```json
{
  "schema_version": "c0_metrics.v1",
  "run_id": "<str>",
  "route_id": "<str>",
  "retrieval_mode": "UPLOADED_BRIEFING | DELEGATED_APPS_RESEARCH | NATIVE_C0 | NONE",
  "source_class_coverage": {
    "<source_class>": true | false
  },
  "support_status": "PASS | WEAK_WITH_CAVEATS | CONFLICTED | EMPTY | BLOCKED | UNKNOWN",
  "support_target_met": true | false,
  "evidence_counts": {
    "total": 0,
    "excluded": 0,
    "blocked": 0
  },
  "retrieval_sources": ["<str>"],
  "excluded_evidence_refs": ["<str>"],
  "blocked_source_refs": ["<str>"],
  "freshness_receipts": ["<str>"],
  "citation_map": [["<evidence_id>", "<citation_anchor>"]],
  "support_score_profile": {
    "<source_class>": 0.0
  },
  "final_evidence_digest": "<sha256>",
  "briefing_source_type": "UPLOADED_BRIEFING | DELEGATED_APPS_RESEARCH | NATIVE_C0 | NONE",
  "company_brief_provenance": {
    "source": "<str>",
    "fetched_at": "<iso8601>",
    "freshness_ttl_days": 0
  } | null
}
```

### Rules
- Artifact written for all briefing modes when evidence exists.
- If C0 bypassed by design, write explicit `retrieval_mode` and `N/A` reasons — not silent absence.
- Preserve `final_evidence_digest` for replay/provenance.
- Writer must live in `apps_rg/runtime/bindings/c0_binding.py` or a co-located helper — never in `agentic_core`.
- Schema file at `apps_rg/runtime/schemas/c0_metrics.schema.json`.

### Acceptance Checks
- [x] Tests prove `c0_metrics.json` is created in correct path.
- [x] Tests prove missing evidence creates explicit `EMPTY`/`BLOCKED`/`UNKNOWN` state, not silent absence.
- [x] Tests prove artifact has stable schema (required keys always present).
- [x] Fixture/example artifact committed under `tests/_fixtures/c0_metrics_example.json`.
- [x] `final_evidence_digest` matches `run_metadata.json:prompt_artifact.evidence_digest`.

**Status: ✅ DONE** — Writer at `apps_rg/runtime/bindings/c0_metrics_writer.py`; schema at `apps_rg/runtime/schemas/c0_metrics.schema.json`; `build_c0_metrics()` and `write_c0_metrics()` exported.

---

## 9. W4 — apps_rg Scoring and Exit Consumption

### Goal
Make `apps_rg` scoring/Exit profile consume retrieval evidence cleanly.

### Scope
Wire `apps_rg` Exit binding to consume `c0_metrics.json` or the equivalent underlying FEC contract data:

**apps_rg scoring/Exit owns (resume-domain metrics):**
- `jd_keyword_coverage`
- `must_have_covered` / `must_have_total`
- `missing_keywords`
- `overfit_score`
- `provenance_valid`
- `material_claim_support_rate`
- `unsupported_material_claim_rate`
- `citation_anchor_coverage`

**C0 evidence fields consumed by Exit:**
- `support_status` → gates PA continuation or blocks X3
- `support_target_met` → gates PA continuation
- `citation_map` → feeds G13 hard-fail
- `freshness_receipts` → feeds G09 warn
- `excluded_evidence_refs` → contributes to `unsupported_material_claim_rate`

### Rules
- JD coverage, overfit, provenance_valid remain `apps_rg`-owned; never move to `agentic_core`.
- Use C0 evidence refs to support X1D groundedness and faithfulness.
- Unsupported high-confidence resume claims must block or degrade X1D/X2/X3.
- `UNKNOWN`, `EMPTY`, `BLOCKED`, `CONFLICTED` must not pass Exit.
- `apps_rg` defines thresholds; `agentic_core` Exit applies the configured profile and emits X3.
- G09 (freshness) and G13 (citation) gates must be connected from declared-only state to evaluated state.

### Acceptance Checks
- [x] Tests prove `apps_rg` Exit reads `support_status` from C0 metrics and blocks on `UNKNOWN`/`EMPTY`/`BLOCKED`/`CONFLICTED`.
- [x] Tests prove unsupported claims degrade X1D/X2/X3.
- [x] Tests prove `overfit_score` and `jd_keyword_coverage` remain `apps_rg`-owned.
- [x] Tests prove `agentic_core` Exit has no `apps_rg`-specific literals.
- [x] G09 (freshness warn) connected and evaluated.
- [x] G13 (citation hard-fail) connected and evaluated.

**Status: ✅ DONE** — `_BLOCKING_SUPPORT_STATUSES` and `_evaluate_c0_evidence_gates()` in `exit_binding.py`; inert `InertArtifactCommitCandidate` pattern enforces GAP-001 L4 boundary; all Exit tests green.

---

## 10. W5 — Briefing Path Proof

### Goal
Prove the four briefing modes remain distinct end-to-end.

### Modes
| Mode | `retrieval_mode` value | `briefing_source_type` | Description |
|---|---|---|---|
| Uploaded briefing | `UPLOADED_BRIEFING` | `UPLOADED_BRIEFING` | User supplied `manual_brief_path`; pre-built JSON |
| Delegated apps_research | `DELEGATED_APPS_RESEARCH` | `DELEGATED_APPS_RESEARCH` | `research_via="apps_research"` used |
| Native C0 | `NATIVE_C0` | `NATIVE_C0` | No brief; apps_rg C0 retrieves from Chroma |
| None | `NONE` | `NONE` | No briefing, no Chroma; file-only path |

### Acceptance Checks
- [x] Tests or fixtures prove each mode emits distinct `retrieval_mode` in `c0_metrics.json`.
- [x] `company_brief_provenance` is preserved where present (uploaded or delegated).
- [x] Delegated `apps_research` evidence is treated as evidence input, not `apps_rg`-owned research.
- [x] No-briefing path emits explicit `NONE` absence, not silent success.
- [x] No briefing-mode logic leaks into `agentic_core`.

**Status: ✅ DONE** — `briefing_mode_classifier.py` at `apps_rg/runtime/bindings/`; four modes tested; `agentic_core` boundary clean per AST scan.

---

## 11. W6 — Governance and Anti-Contamination Tests

### Goal
Protect the ownership split permanently.

### Test File
`tests/_apps_contract/test_rg_retrieval_metrics_governance.py`

### Required Test Coverage
1. No JD/resume-specific literals or policies in `agentic_core/runtime/c0/` or `agentic_core/runtime/contracts/`.
2. `apps_rg` U0/profile file defines `required_source_classes`.
3. `agentic_core` C0 extractor has zero `apps_rg` imports.
4. `apps_rg` Exit reads `support_status` and rejects `UNKNOWN`/`EMPTY`/`BLOCKED`/`CONFLICTED`.
5. `support_status` values in `c0_metrics.json` fixture match canonical enum.
6. `UNKNOWN`/`BLOCKED`/`EMPTY`/`CONFLICTED` cannot pass Exit (negative-control test).
7. `c0_metrics.json` is replayable: same input evidence → same `final_evidence_digest`.
8. No direct C0-to-L4 write path introduced.
9. No L6 current-run rescue path introduced.
10. Existing `tests/_apps_contract/` suite still passes without modification.

### Acceptance Checks
- [x] All 10 governance test categories covered.
- [x] All new tests pass.
- [x] All existing `tests/_apps_contract/` tests pass (zero regressions).
- [x] No `apps_rg.*` imports found in `agentic_core/runtime/c0/` by AST scan.
- [x] No new C0-to-L4 write path.
- [x] No L6 rescue path.

**Status: ✅ DONE** — `test_rg_retrieval_metrics_governance.py` 62 tests, 362/362 W1-W6 suite passing. Also added `test_check_no_shadow_spine.py` (20 tests) proving SS-2 does not flag app-owned stage-named bindings (`pa_compose_apps_rg`, `l2_execute_apps_rg`) and does flag core-imported stage chains. Gate `check_no_shadow_spine.py` exits 0, 17 warnings all apps_qna-only (deferred).

---

## 12. W7 — Final Evidence Receipt

### Goal
Produce implementation receipt proving all waves complete and gaps documented.

### Deliverable
Markdown receipt at: `docs/reports/apps_rg/retrieval_metrics_receipt_<ts>.md`

### Receipt Format
```
PASS/FAIL status:      <per wave>
Wave summary:          <table>
Evidence artifacts:    <list of files created/modified>
Test commands:         pytest tests/_apps_contract/test_rg_retrieval_metrics_governance.py -v
Test results:          <pass count / fail count>
c0_metrics.json path:  artifacts/apps_rg/runs/<example_run_id>/c0_metrics.json
Metrics now serialized: <list>
Ownership split proof:  <summary>
Known residual gaps:   <list — non-blocking>
```

### Final Command Results (2026-05-14)

```
pytest W1–W6 suite (287 tests):        287 passed, 0 failed  ✅
pytest shadow-spine regression (20):    20 passed, 0 failed  ✅
python check_no_shadow_spine.py:        exit 0               ✅
```

### Receipt Path
`docs/reports/apps_rg/retrieval_metrics_receipt_20260514.md`

### Acceptance Checks
- [x] Receipt file exists at correct path.
- [x] All wave PASS/FAIL statuses recorded.
- [x] Example `c0_metrics.json` path cited.
- [x] All serialized metrics listed.
- [x] Residual non-blocking gaps explicitly enumerated.

**Status: ✅ DONE**

---

## 13. Definition of Done

| DoD Row | Criterion | Verification |
|---|---|---|
| DoD-1 | `apps_rg` retrieval profile explicitly declares `required_source_classes`, `support_target`, briefing taxonomy | ✅ File exists and passes validation test |
| DoD-2 | `c0_metrics.json` written per run with stable schema | ✅ `tests/_apps_contract/test_rg_retrieval_metrics_governance.py` passes |
| DoD-3 | `support_status` enum aligned — `PARTIAL` eliminated; canonical 6-value set enforced | ✅ Enum gate test fails on any non-canonical value |
| DoD-4 | `apps_rg` Exit reads `support_status`/`citation_map`/`freshness_receipts` from FEC; G09 and G13 gated | ✅ Exit binding tests pass with mock FEC values |
| DoD-5 | Governance scan proves no `apps_rg` literals in `agentic_core` C0 or contracts | ✅ AST import scan test passes |
| DoD-6 | Four briefing modes produce distinct `retrieval_mode` in artifact | ✅ Fixture/parametrized test per mode |
| DoD-7 | Final receipt file produced at `docs/reports/apps_rg/retrieval_metrics_receipt_<ts>.md` | ✅ `docs/reports/apps_rg/retrieval_metrics_receipt_20260514.md` |

### Verification vs Deferral

| Item | Decision |
|---|---|
| Deep native apps_rg company research retrieval | **Deferred** — out of scope per Hard Rule 6 |
| `pool_first_hit_rate` (legacy narrative metric) | **Deferred** — legacy path only; not reintroduced here |
| Real LLM overfit scoring (beyond threshold config) | **Deferred** — threshold profile sufficient for this pass |
| Per-evidence-item ACL verification receipts | **Deferred** — infrastructure gap beyond this plan scope |

---

## 14. Non-Goals

- Do not build deep native `apps_rg` company research retrieval.
- Do not reintroduce `pool_first_hit_rate` or legacy narrative pipeline metrics.
- Do not modify the Chroma ingestion pipeline or embedding strategy.
- Do not change the L2 execution shape or prompt assembly contracts.
- Do not alter `agentic_core` routing or Exit X3 disposition logic.
