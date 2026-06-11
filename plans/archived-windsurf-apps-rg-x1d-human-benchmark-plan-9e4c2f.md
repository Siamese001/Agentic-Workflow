---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\apps-rg-x1d-human-benchmark-plan-9e4c2f.md'
original_relative_path: 'apps-rg-x1d-human-benchmark-plan-9e4c2f.md'
source_sha256: e841373d06db610624f375d4c856db21fa6e6421a2bd99991e949f418b0a8d27
recovered_status: LOST_RECOVERED
last_commit: '56872a6db68'
last_commit_date: '2026-05-13 17:19:32 -0400'
created_date: '2026-05-13'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: apps-rg-x1d-human-benchmark-plan-9e4c2f
plan_type: doc
touches_agentic_core: false
touches_governance_ci: false
touches_windsurf_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: true
---

# apps_rg X1D Human Benchmark Plan for Judge Calibration

Defines structure, schema, coverage targets, and calibration method for future offline human benchmarks
that will eventually calibrate X1D LLM-as-judge panels for apps_rg — without blocking runtime or
requiring any implementation work now.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: TODO
CURRENT_WAVE: W0
LAST_COMPLETED_WAVE: NONE
LAST_UPDATED: 2026-05-13

---

## Context (SCQA)

- **Situation** — apps_rg runs generated resume sections through the full agentic spine. Qwen vLLM generates section artifacts. X1D evaluates subjective quality using LLM-as-judge panels. All X1D judges are currently `UNCALIBRATED` and advisory-only.
- **Complication** — Offline human benchmarks are the only defensible path to promoting judges from advisory to trusted. Without a plan, ad-hoc benchmark collection risks PII exposure, inconsistent schema, unclear section coverage, and uncontrolled public-dataset misuse.
- **Question** — How do we define the benchmark structure, schema, section coverage, calibration method, and data sourcing approach so future implementation is unblocked and well-scoped?
- **Answer** — Emit a plan-only artifact that records all decisions without touching runtime, gates, or requiring human scoring now.

---

## Hard Boundaries (Non-Negotiable)

| Constraint | Reason |
|---|---|
| Do NOT block runtime on benchmark availability | Runtime must be operational today |
| Do NOT implement benchmark collection now | No implementation work in this plan |
| Do NOT require human scoring now | Human effort is a future phase |
| Do NOT add benchmark logic into `agentic_core` | Core is app-agnostic |
| Do NOT rename canonical G01–G29 gates | Gate naming is frozen |
| Keep benchmarks offline / L6-style / future-run only | No current-run mutation |
| X1D judges remain `UNCALIBRATED` / advisory until promoted | Promotion requires Spearman rho ≥ 0.80 via UWG |
| Downloaded public datasets are bootstrap seed only — NOT final calibration proof | Legal + quality discipline |

---

## Wave Overview

**Waves**: 1 total (W1 — Plan Structure Emission)
**Total Estimate**: ~3K tokens
**Current**: W0 (pre-flight)
**Execution Stance**: This is a **no-work-now plan**. W1 consists of emitting this document and the three supporting artifact files listed in §9. No datasets are downloaded. No human labels are collected. No runtime gates are modified. No judges are promoted.

**Wave Manifest**:
- **W1** — Emit plan artifacts to `artifacts/apps_rg/plans/` | ~3K tokens | STATUS: TODO

---

## Wave 1 — Plan Artifact Emission

WAVE_ID: W1
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

**Authorization**: NOT_REQUIRED — No shared surface modifications; doc/artifact output only.

**Phases**:
- **W1.1** — Write `human_benchmark_plan.md` to `artifacts/apps_rg/plans/` | ~1K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W1.2** — Write `human_benchmark_schema.json` to `artifacts/apps_rg/plans/` | ~1K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W1.3** — Write `public_dataset_sourcing_notes.md` to `artifacts/apps_rg/plans/` | ~1K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- Three artifact files exist on disk at the canonical paths
- No runtime files are modified
- No tests are modified or added
- No CI gates are modified

---

## §1 — Section Coverage by Benchmark Priority

### P0 — Human Benchmark Required (Future)

These sections have high subjective quality variance; uncalibrated judge failure on these sections
MUST NOT produce an autonomous quality PASS.

| Section ID | Judge Concern |
|---|---|
| `headline` | Positioning strength, differentiation, seniority signal |
| `executive_summary` | Executive presence, credibility, JD fit |
| `unify_narrative` | Story coherence, evidence fidelity across roles |
| `unify_bullets` | Impact metrics, JD relevance, seniority signal |
| `competencies` | JD match, no keyword stuffing, executive relevance |

### P1 — Human Benchmark Desired (Future)

Lower variance but still subjective; advisory calibration adds value.

| Section ID | Judge Concern |
|---|---|
| `ibm_narrative` | Story coherence, executive relevance |
| `ibm_bullets` | Impact, specificity, metric quality |
| `insurtech_narrative` | Story coherence, executive relevance |
| `insurtech_bullets` | Impact, specificity, metric quality |
| `ey_narrative` | Story coherence, executive relevance |
| `ey_bullets` | Impact, specificity, metric quality |

### No Human Benchmark Needed

These sections are deterministic, copy-verbatim, or structurally validated — no subjective
LLM-as-judge calibration is warranted.

| Section ID | Reason |
|---|---|
| `header` | Deterministic — name/title copy |
| `contact_info` | Deterministic — data field copy |
| `dates` | Deterministic — date range copy |
| `company_names` | Deterministic — verbatim copy |
| `education` | Deterministic — credential copy |
| `certifications` | Deterministic — credential copy |
| `early_career` | Deterministic — copy-verbatim per spec |

---

## §2 — Benchmark Types

| Type | Purpose | When Used |
|---|---|---|
| **Downloaded public resume/JD datasets** | Bootstrap seed examples; JD matching tests; schema validation | Available now if safe existing script; never final calibration proof |
| **Generated section variants from Qwen** | Weak/medium/strong candidate samples for scoring panels | Future W1–W3 collection phase |
| **Human-scored samples** | Ground-truth labels for Spearman rho calibration | Deferred; future phase; requires reviewer workflow |
| **Negative controls** | Bad/generic/unsupported output samples; test judge detection | Future W1–W3 collection phase |
| **Drift holdout set** | Reserved unseen samples for future monitoring only | Created at collection time; never used for calibration |

**Key invariant**: Downloaded public datasets provide bootstrap schema familiarity and weak-label seeds.
They are explicitly NOT sufficient as human calibration proof. Judge promotion requires human-scored
samples with Spearman rho ≥ 0.80.

---

## §3 — Data Sourcing Plan

### 3.1 Public Resume / JD Datasets (Bootstrap Only)

- **Purpose**: schema testing, negative-control seeds, JD matching examples
- **Candidate sources**: ResumeNet, Kaggle resume datasets, O*NET JD data, LinkedIn public job postings
- **License discipline**: record license type per dataset; CC-BY or public domain only
- **PII discipline**: strip or pseudonymize all real person identifiers before storage
- **What they prove**: nothing about X1D judge calibration; bootstraps schema and weak labels only
- **What they do NOT prove**: judge quality, Spearman rho, or promotion readiness

### 3.2 Synthetic Generated Variants (Candidate Samples)

- **Source**: run apps_rg against a range of JDs and prompts; capture `generated_section_text` per section
- **Tiers**: weak (under-prompted), medium (standard), strong (few-shot enhanced)
- **Storage**: `artifacts/apps_rg/benchmarks/<section_id>/<benchmark_id>.json` (future)
- **No current requirement**: collection deferred to future W1 benchmark wave

### 3.3 Private / Project-Specific Examples (Higher Calibration Quality)

- **Source**: real-world resume-JD pairs (PII-scrubbed); Amit-approved samples
- **Purpose**: higher-quality calibration than public datasets
- **Timing**: deferred; requires explicit data-preparation session
- **PII gate**: reviewer must confirm `pii_status=cleared` before storage

### 3.4 Human Labels (Deferred — Future Phase)

- **Assigned reviewers**: at least 2 independent reviewers per sample for agreement scoring
- **Reviewer roles**: `hiring_manager`, `executive_recruiter`, `domain_expert`
- **Inter-rater reliability**: target Cohen's kappa ≥ 0.65 before treating labels as ground truth
- **Timing**: deferred; no current obligation on Amit to score samples

---

## §4 — Benchmark Artifact Schema

Schema version: `1.0`
Canonical future path: `artifacts/apps_rg/benchmarks/<section_id>/<benchmark_id>.json`

```json
{
  "schema_version": "1.0",
  "benchmark_id": "<uuid>",
  "section_id": "<e.g. headline>",
  "section_tier": "<P0|P1|none>",
  "source_resume_ref": "<anonymized ref or null>",
  "jd_ref": "<jd dataset ref or null>",
  "generated_section_text": "<text produced by Qwen>",
  "base_section_text": "<original source text, optional>",
  "c0_evidence_refs": ["<ref1>", "<ref2>"],
  "human_scores": {
    "<dimension_id>": {
      "score": "<1-5 int or null>",
      "reviewer_role": "<hiring_manager|executive_recruiter|domain_expert|null>",
      "reviewer_confidence": "<high|medium|low|null>",
      "reason_codes": ["<code1>", "<code2>"]
    }
  },
  "human_notes": "<free-text notes, optional>",
  "created_at": "<ISO8601>",
  "dataset_origin": "<generated|public_resume_dataset|private>",
  "license_notes": "<CC-BY 4.0, ODbL, N/A-generated, etc.>",
  "pii_status": "<cleared|pending_review|contains_pii>"
}
```

**Schema invariants**:
- `pii_status` MUST be `cleared` before any sample is used for judge calibration
- `human_scores` is optional at creation; populated during future human-labeling phase
- `dataset_origin=generated` samples require no license note
- `dataset_origin=public_resume_dataset` samples MUST carry `license_notes`

---

## §5 — Human Scoring Dimensions per Section

All dimensions are scored on a 1–5 integer scale:
`1=poor, 2=below_average, 3=acceptable, 4=good, 5=excellent`

### headline

| Dimension | What it measures |
|---|---|
| `clarity` | Is the headline immediately understandable? |
| `positioning_strength` | Does it convey a strong value proposition? |
| `differentiation` | Does it stand out vs generic titles? |
| `seniority_signal` | Does it convey appropriate executive level? |
| `jd_fit` | Does it align with the target JD? |
| `overall` | Holistic quality assessment |

### executive_summary

| Dimension | What it measures |
|---|---|
| `executive_presence` | Does it sound like a senior executive? |
| `credibility` | Are claims specific and believable? |
| `specificity` | Are achievements quantified and concrete? |
| `jd_relevance` | Does it connect to what the JD demands? |
| `differentiation` | Does it distinguish from generic summaries? |
| `overall` | Holistic quality assessment |

### narratives (`ibm_narrative`, `insurtech_narrative`, `ey_narrative`, `unify_narrative`)

| Dimension | What it measures |
|---|---|
| `story_coherence` | Is the narrative arc logical and engaging? |
| `executive_relevance` | Is the content appropriate for executive audience? |
| `evidence_fidelity` | Are factual claims traceable to source resume? |
| `clarity` | Is the prose readable and precise? |
| `overall` | Holistic quality assessment |

### bullets (`ibm_bullets`, `insurtech_bullets`, `ey_bullets`, `unify_bullets`)

| Dimension | What it measures |
|---|---|
| `impact` | Does each bullet communicate meaningful impact? |
| `specificity` | Are claims concrete rather than generic? |
| `metric_quality` | Are quantified metrics present and credible? |
| `jd_relevance` | Do bullets reflect JD priorities? |
| `seniority_signal` | Do bullets reflect executive-level contributions? |
| `overall` | Holistic quality assessment |

### competencies

| Dimension | What it measures |
|---|---|
| `jd_match` | Do competencies reflect the JD's key demands? |
| `executive_relevance` | Are competencies appropriate for executive level? |
| `clarity` | Are competency labels crisp and unambiguous? |
| `no_keyword_stuffing` | Does it avoid padding / generic filler? |
| `overall` | Holistic quality assessment |

---

## §6 — Calibration Method

### Process

1. **Collect samples**: generate `n` samples per section from Qwen across weak/medium/strong tiers
2. **Collect human scores**: 2+ independent reviewers score each sample on section dimensions
3. **Confirm inter-rater reliability**: Cohen's kappa ≥ 0.65 per dimension before using as ground truth
4. **Run judge panel**: send the same samples through X1D judge; record judge scores per dimension
5. **Compute Spearman rho**: compare human ranking vs judge ranking per dimension
6. **Promotion gate**: Spearman rho ≥ 0.80 on all P0 dimensions required for promotion

### Promotion Policy

| Judge state | Spearman rho | Operational behavior |
|---|---|---|
| `UNCALIBRATED` | Not yet measured | Advisory only; fail may trigger retry/HITL |
| `CALIBRATED_PROVISIONAL` | ≥ 0.80 on ≥ 80% dims | Trusted advisory; may suppress retry |
| `CALIBRATED_PROMOTED` | ≥ 0.80 on all tracked dims | Trusted; eligible for autonomous PASS on P1 |
| `CALIBRATED_TRUSTED` | ≥ 0.80 sustained over 2 eval cycles | Eligible for autonomous PASS on P0 |

**Promotion is offline only.** Promotion decisions go through L6 proposal and UWG review.
No judge is promoted via current-run mutation.

**P0 constraint**: P0 sections (`headline`, `executive_summary`, `unify_narrative`, `unify_bullets`,
`competencies`) CANNOT receive an autonomous quality PASS from uncalibrated judge scores alone.
Deterministic X1 gates can still hard-fail P0 sections independently.

---

## §7 — Sample Targets by Future Wave

These are future-phase targets. No collection is required now.

### Future W1 (First Collection Wave)

| Section | Target n | Sample types |
|---|---|---|
| `executive_summary` | 20 | generated (weak/medium/strong) + negative controls |
| `headline` | 20 | generated (weak/medium/strong) + negative controls |
| `competencies` | 20 | generated (weak/medium/strong) + negative controls |

### Future W2

| Section | Target n | Sample types |
|---|---|---|
| `unify_narrative` | 15 | generated (weak/medium/strong) + negative controls |
| `unify_bullets` | 15 | generated (weak/medium/strong) + negative controls |

### Future W3

| Section | Target n each | Sample types |
|---|---|---|
| `ibm_narrative` | 10 | generated + negative controls |
| `ibm_bullets` | 10 | generated + negative controls |
| `insurtech_narrative` | 10 | generated + negative controls |
| `insurtech_bullets` | 10 | generated + negative controls |
| `ey_narrative` | 10 | generated + negative controls |
| `ey_bullets` | 10 | generated + negative controls |

**Total future target**: 170 samples (60 P0, 30 P0-unify, 60 P1, 20 negative controls across all)

---

## §8 — Current Runtime Policy While Benchmarks Are Missing

This policy is already in effect and requires no changes now.

| Condition | Current behavior |
|---|---|
| Deterministic X1 gates | Can enforce hard failures regardless of judge state |
| X1D LLM judges | Can run; scores are recorded |
| All judge `calibration_status` | Defaults to `UNCALIBRATED` |
| Uncalibrated judge PASS | Advisory only — does NOT produce autonomous quality PASS on P0 |
| Uncalibrated judge FAIL | May trigger retry and/or HITL escalation |
| P0 sections | Cannot receive autonomous quality PASS from uncalibrated judge alone |
| Judge promotion | Blocked until Spearman rho ≥ 0.80 via future benchmark collection + UWG |

**No runtime gate changes are required by this plan.**

---

## §9 — Plan Artifact File Outputs

These files are to be created in future W1 of this plan. Their paths and purposes are defined here.

| File | Path | Purpose |
|---|---|---|
| `human_benchmark_plan.md` | `artifacts/apps_rg/plans/human_benchmark_plan.md` | This plan in consumable artifact form; includes section coverage, schema reference, calibration method |
| `human_benchmark_schema.json` | `artifacts/apps_rg/plans/human_benchmark_schema.json` | Machine-readable `BenchmarkSample` schema v1.0 (JSON Schema draft-07) |
| `public_dataset_sourcing_notes.md` | `artifacts/apps_rg/plans/public_dataset_sourcing_notes.md` | License notes, candidate public datasets, PII-strip procedure, bootstrap-only disclaimer |

All files land under `artifacts/apps_rg/plans/` — NOT in `agentic_core`, NOT in `apps_rg/` source.

---

## §10 — No-Work-Now Execution Stance

This plan is **structure-and-future-tasks only**. The following actions are explicitly deferred:

| Action | Deferred to |
|---|---|
| Downloading public datasets | Future W1 — requires explicit session + safe existing script |
| Human sample labeling | Future W1–W3 human-scoring phase |
| Modifying X1D runtime gates | Not required — current policy already correct |
| Promoting any judge | Future — requires Spearman rho ≥ 0.80 + UWG |
| Writing benchmark collection code | Future plan (apps-rg-x1d-benchmark-collection-*) |
| Wiring calibration_status into gate enforcement | Future plan after first calibration cycle |

---

## Out Of Scope

- Implementing benchmark collection pipelines
- Downloading any public dataset now
- Human labeling sessions
- Modifying any X1D or G01–G29 gate
- Promoting any judge from UNCALIBRATED
- Adding benchmark logic to `agentic_core`
- Changes to `apps_rg/__main__.py` or any engine
- Any runtime behavior change

---

## Gap Register

**GAP-1: Reviewer workflow not defined**
- Human scoring requires a structured reviewer UX (form, spreadsheet, or dedicated tool)
- Impact: Low now; blocks future W1 human-labeling phase
- Deferred to the benchmark-collection plan

**GAP-2: Public dataset PII-strip tooling not confirmed**
- A safe existing script may or may not exist at `ops_scripts/apps_rg/`
- Impact: Low now; must be confirmed before any public dataset ingestion
- Deferred to future W1

**GAP-3: `calibration_status` field on judge profile not yet formalized in schema**
- Current: implied by advisory-only behavior
- Impact: Low now; should be formalized when first calibration cycle begins
- Deferred to future calibration plan

**GAP-4: Drift holdout split strategy not defined**
- Holdout samples must be reserved at collection time and never used for initial calibration
- Impact: Zero now; must be decided before first collection wave
- Deferred to benchmark-collection plan

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| W1.1 | human_benchmark_plan.md artifact | `artifacts/apps_rg/plans/human_benchmark_plan.md` | None | ~1K | TODO |
| W1.2 | human_benchmark_schema.json artifact | `artifacts/apps_rg/plans/human_benchmark_schema.json` | None | ~1K | TODO |
| W1.3 | public_dataset_sourcing_notes.md artifact | `artifacts/apps_rg/plans/public_dataset_sourcing_notes.md` | None | ~1K | TODO |

---

## Definition of Done

DoD-1: Three artifact files exist at their canonical paths under `artifacts/apps_rg/plans/`
- Evidence: `ls artifacts/apps_rg/plans/` shows all three files
- Status: TODO

DoD-2: No runtime files modified
- Evidence: `git diff --name-only` shows zero changes to `apps_rg/`, `agentic_core/`, `ops_scripts/ci/`
- Status: TODO

DoD-3: No tests added, modified, or broken
- Evidence: `pytest tests/_apps_contract/` passes at same count as baseline
- Status: TODO

DoD-4: Plan registered in Notion Plans DB with Status=Not Started
- Evidence: Notion page ID recorded below
- Status: DONE (posted this session)

DoD-5: Section coverage, schema, calibration method, and runtime policy documented
- Evidence: §1–§10 in this plan are complete and internally consistent
- Status: DONE (this document)

---

## Notion Registration

PLAN_CREATED: apps-rg-x1d-human-benchmark-plan-9e4c2f
Notion page ID: 35f27693-f55c-8177-8899-e4575c61d209
