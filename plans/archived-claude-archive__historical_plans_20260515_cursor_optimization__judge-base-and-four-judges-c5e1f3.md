---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\judge-base-and-four-judges-c5e1f3.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\judge-base-and-four-judges-c5e1f3.md'
source_sha256: 03aab7b467d0b28fce442af482b0d3c94d3ae6bb6358026dc836d323e5e06fb7
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Plan: JudgeBase primitive + 4 LIC Judges (1 live, 3 stub-rubrics, Hybrid deferred)

**Slug**: `judge-base-and-four-judges-c5e1f3`
**Status**: In-progress (W1 + partial W2 landing this session; W3 + W4 deferred)
**Tier**: T3 (cross-layer architecture, multi-file, governance pattern)
**Created**: 2026-05-01
**Parent decisions**: ADR-decision-router-policy-tables-b3a4d2 (DecisionRouter primitive)
**Reference**: `docs/reference/_notes/LLM as a Judge vs. Ensemble vs. Hybrid.md`

## Goal

Materialize the post-consolidation HOP × Judge/Ensemble/Hybrid recommendation
into actual code. The recommendation called for **4 Judges + 1 Hybrid** —
Judges at HOP1 (LLM-fallback), HOP2 (strategic_brief faithfulness), HOP6
(strategic alignment), and HOP8 (narrative executive_summary); Hybrid at HOP5
(generation).

This plan ships the **primitive** that all 4 Judges consume, ships **HOP6's
Judge live** as proof-of-concept, ships **rubric YAMLs for the other 3** so
the surface is ready for swap-in, and defers HOP5 Hybrid + the LLM-call
backends with explicit markers.

## Documented Decisions

The 7 architectural decisions made for this plan are recorded below. They
also appear in the ADR and the commit body.

**D1. One primitive, four consumers.** Same pattern as `DecisionRouter`. A
single `JudgeBase` class loads a rubric YAML, evaluates an input via a
pluggable `evaluate(state) → JudgeScorecard` function, emits a
constitutionally-shaped scorecard. Four Judges instantiate it with
different rubrics. No bespoke per-HOP Judge classes.

**D2. Ship deterministic backends first; LLM upgrade is a swap-in.** Each
Judge ships with a deterministic `evaluate` implementation (keyword overlap,
citation check, confidence floor, score-band template). The integration
surface (where in HOP-N's `_process` the Judge runs, what scorecard fields
go to the buffer, which exit policy gates downstream) is the durable
value. The LLM call is a leaf change later — `evaluate_with_llm()` swaps
in without touching the HOP wiring.

**D3. Reuse exit_policy + add judge_disposition_policy.** The X3
disposition vocabulary is constitutional. `exit_policy.yaml` (shipped in
plan b3a4d2) maps `(severity, rule_id, passed) → ALLOW/REVISE/DENY/HITL/ABSTAIN`
for HOP6 row-level dispositions. `judge_disposition_policy.yaml` (this
plan) maps `(score_band, rule_id) → X3` for **Judge-level** dispositions.
Same vocabulary, different input schemas, both consumed by the existing
`DecisionRouter` primitive. No new dispatch engine.

**D4. HOP5 Hybrid deferred until cheap Judges produce negative-label data.**
The Hybrid selector trains on what the Judges flag as bad. Building Hybrid
first, before HOP1/HOP2/HOP6/HOP8 Judges produce signal, is the
"polished wrong answer wins" failure mode the reference doc explicitly
warns against. Sequence: Judges first (this plan), Hybrid second
(separate plan).

**D5. judge_scorecard schema is constitutional.** Every Judge emits the
same dataclass shape, mirroring the reference doc's OUTPUT ARTIFACT spec:
`{judge_name, rubric_version, score, verdict, x3_disposition,
reason_codes[], evidence_refs[], confidence, abstain_flag,
remediation_hint}`. Cross-Judge analysis becomes possible without
per-HOP schema translation.

**D6. ABSTAIN preferred over guessing.** When a Judge cannot reach a
confident verdict (LLM unavailable, evidence missing, rubric not
applicable to input), the verdict is ABSTAIN with `abstain_flag=true`,
routed to HITL via `judge_disposition_policy.yaml`. Never DENY without
evidence. Never ALLOW without verification.

**D7. Loser-candidate retention from day one.** Even though HOP5 Hybrid
is deferred, HOP6's per-row Judge output is logged with full
`evidence_refs` so when Hybrid ships, those rows are immediately
available as selector training data. Same retention shape as the
reference doc's `loser_retention_refs` Hybrid output.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|---|---|---|---:|---|---|
| **W1** | W1-P1, W1-P2, W1-P3 | JudgeBase primitive + 4 rubric YAMLs + judge_disposition_policy + unit tests | 14000 | **Done** | JudgeBase tests green; all 4 rubrics load + validate; ROUTER_DECISION marker emission verified |
| **W2** | W2-P1 | HOP6 wires LLM-strategic-alignment Judge with deterministic backend (replaces brittle keyword-overlap rule) | 6000 | **Done** | HOP6 emits judge_scorecard for strategic_alignment_check; existing tests green; new Judge test green |
| **W3** | W3-P1, W3-P2, W3-P3 | HOP1 LLM-fallback Judge + HOP2 strategic_brief faithfulness Judge + HOP8 narrative executive_summary Judge | 12000 | **Deferred** | DEFERRED_SCOPE markers (P3 each) — rubrics shipped in W1, integrations land separately |
| **W4** | W4-P1 | HOP5 Hybrid (3-model ensemble + selector + Judge gate) | 30000 | **Deferred** | DEFERRED_SCOPE marker (P2) — gated on Judges producing 30+ days of negative-label data first |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---:|---|
| W1-P1 | JudgeBase primitive | `apps_lic/policy/judge_base.py`, `apps_lic/policy/__init__.py` (extend exports) | Pluggable `evaluate` function; scorecard shape; reuse DecisionRouter for X3 mapping | 6000 | Done |
| W1-P2 | Rubric YAMLs | `apps_lic/policy/rubrics/judge_hop1_classifier.yaml`, `judge_hop2_grounding.yaml`, `judge_hop6_alignment.yaml`, `judge_hop8_narrative.yaml`, `judge_disposition_policy.yaml` | Capturing what each Judge measures, with deterministic-mode parameters | 4000 | Done |
| W1-P3 | JudgeBase unit tests | `tests/unit/apps/apps_lic/policy/test_judge_base.py` | Schema validation, deterministic backend behavior, ABSTAIN paths, scorecard shape | 4000 | Done |
| W2-P1 | HOP6 strategic_alignment Judge live wiring | `apps_lic/engines/HOP6ValidationAgent.py` | Replace `_check_strategic_alignment` with `JudgeBase` invocation; emit judge_scorecard alongside existing validation row | 6000 | Done |
| W3-P1 | HOP1 LLM-fallback Judge | `apps_lic/engines/HOP1ProfileAnalysisAgent.py` | Judges only the LLM-fallback path (~10% of classifications); confidence-floor + reasoning-faithfulness rubric | 4000 | **Deferred** |
| W3-P2 | HOP2 strategic_brief faithfulness Judge | `apps_lic/engines/HOP2ResearchAgent.py` | Citation check (every claim cites artifact_id); recency floor; source_weight floor | 5000 | **Deferred** |
| W3-P3 | HOP8 narrative executive_summary | `apps_lic/engines/HOP8QAReportAgent.py` | Score-band template → 3-sentence rationale; deterministic backend uses templates | 3000 | **Deferred** |
| W4-P1 | HOP5 Hybrid (ensemble + selector + Judge gate) | `apps_lic/engines/HOP5GenerationAgent.py`, new selector module | Largest investment; needs negative-label data from W3 Judges first | 30000 | **Deferred** |

## ADG_HOTSPOT_REPORT

Verification snapshot: `artifacts/adg/adg_indexed_05012026_0632.sqlite`

| File | Layer | fan_in | Archetype | Surface | Multiplier | Impact | Notes |
|---|---|---:|---|---|:---:|---:|---|
| `apps_lic/policy/judge_base.py` (new) | L_APP | 0 (new) | CENTRAL_DEPENDENCY (eventual) | None | ×1.0 | low | New primitive; eventually consumed by 4 HOPs. Zero blast radius today. |
| `apps_lic/engines/HOP6ValidationAgent.py` | L_APP | 1 | SAFETY_GATEKEEPER | Security | ×1.0 | medium | W2-P1 replaces one rule (`_check_strategic_alignment`); other 5 rules untouched. |
| `apps_lic/engines/HOP1ProfileAnalysisAgent.py` | L_APP | 1 | CENTRAL_DEPENDENCY | None | ×1.0 | low | W3-P1 deferred. |
| `apps_lic/engines/HOP2ResearchAgent.py` | L_APP | 1 | CENTRAL_DEPENDENCY | None | ×1.0 | low | W3-P2 deferred. |
| `apps_lic/engines/HOP8QAReportAgent.py` | L_APP | 1 | ORCHESTRATOR | Observability | ×0.75 | low | W3-P3 deferred. |
| `apps_lic/engines/HOP5GenerationAgent.py` | L_APP | 1 | ORCHESTRATOR | Execution | ×1.0 | medium | W4-P1 (Hybrid) deferred. |

## ADG_GRAPH_LAYER_EVIDENCE

**Materialized views consulted**:

1. `mv_hotspot_centrality` — confirms HOP6/1/2/5/8 fan_in=1 each (single
   spine consumer via `hop_stage_registry.py`); JudgeBase as a new module
   inherits the same low blast radius as the prior DecisionRouter
   introduction (b3a4d2).
2. `mv_authority_boundary_breaches` — clean for all 5 affected HOP files;
   no L0/L5 authority crossings introduced by the Judge primitive.
3. `mv_l2_phase_coverage` — apps_lic/engines is L_APP; not on the L2
   critical path. Refactor blast radius bounded to apps_lic/.

**Semantic edges**: `imports` from HOP6 → `apps_lic.policy.judge_base` is
the only new edge introduced in W2; identical shape to the
`DecisionRouter` import added in plan b3a4d2.

**P-view cross-references**:
- `v_p0_apps_direct_infra` — empty for all 5 affected HOPs.
- `v_p2_duplicated_adapters` — JudgeBase is the OPPOSITE of duplication
  (replaces what would have been 4 hand-rolled Judges).
- `v_p3_isolated_experimental` — JudgeBase is mainline architecture, not
  experimental.

**Conclusion**: Same low-risk profile as the DecisionRouter introduction.
Single new module, single HOP integration in W2, three more deferred to
follow-up plans with explicit markers.

## Out of Scope

- LLM-call backends for any Judge (deterministic-rubric mode only this session).
- HOP5 Hybrid (W4) — gated on Judge negative-label data accumulation.
- Cross-Judge calibration (W5+) — needs production traffic.

## Bypass / Author-Gate

Per `author-gate-enforcement.md` "explicit unambiguous directive" bypass —
user said "consolidate and implement above - document decisions made" in the
session that produced the post-consolidation Judge/Hybrid recommendation.
Silent `DECISION_CAPTURED` marker emitted in the executing response.
