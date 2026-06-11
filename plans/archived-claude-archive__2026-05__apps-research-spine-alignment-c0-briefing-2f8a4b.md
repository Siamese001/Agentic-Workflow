---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\apps-research-spine-alignment-c0-briefing-2f8a4b.md'
original_relative_path: '_archive\\2026-05\\apps-research-spine-alignment-c0-briefing-2f8a4b.md'
source_sha256: 4ff530dc55a6e8bae8867b1b42842547f48b989fcf04c14820b2307d667e0329
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: apps-research-spine-alignment-c0-briefing-2f8a4b
plan_type: refactor
---

# apps_research Spine Alignment + C0 Briefing-Grade Retrieval

Align `apps_research` to the canonical agentic_core spine, retire all
hop/DAG terminology from docs and code, and augment C0 with adaptive
briefing-grade depth profiles, JD-as-first-class-input, section-coverage
matrix, source-mix policy, and structured FEC outputs — enabling
role/company/use-case adaptive, evidence-backed briefing packets.

---

## Context (SCQA)

- **Situation** — `apps_research` has a real R3 single-step grounded
  route registered in `route_registry.yaml` and a working `GovernedResearchRun`
  substrate. The spine-handoff module, FEC producer, and cert route registry are
  all wired. However, docs (`TECHNICAL_SPEC.md`, `hop_pipeline.py` comments,
  `governed_research_run.py` field names such as `hop_checkpoints`) still use
  "hop" and inner-DAG terminology. `CompanyBriefEngine` uses flat
  `_FACET_QUERIES`, a `depth` enum of `{shallow, standard, deep}`, and a
  `jd_anchor` file-path shim — not the canonical depth-profile + JD
  first-class-input model. C0 emits no `BriefingCoverageMatrix`,
  `SourcePortfolioSummary`, `ClaimEvidenceMap`, `ContradictionMatrix`,
  `FreshnessReport`, `SectionGapReport`, or `SynthesisGuidanceForPA`.
  Cache profile exists but has no JD-digest participation. Route registry
  uses `apps_research.single_step_v1` not `R3_SIMPLE_GROUNDED_READ`.
  Negative controls cover only `stale_source` and `unsupported_claim`; the
  23 negative controls specified in the prompt do not exist.

- **Complication** — The Zero-Loss Overwrite Objective requires the app to
  produce fully adaptive, evidence-backed briefing packets at Lincoln-style
  depth (COMPANY_BRIEF_DEEP: 18–25 final sources, 30–45 citation anchors,
  adaptive section coverage per intent/JD/sector) and to satisfy all 12
  implementation requirements in the prompt verbatim. The current C0 surface
  is Tavily-facet-based with no coverage gating, no source-mix policy, no
  contradiction detection, no freshness gating, no JD-structured input, and
  no structured PA guidance. The route ID in `route_registry.yaml` does not
  match the canonical `R3_SIMPLE_GROUNDED_READ` name used in the prompt and
  the spine manifest.

- **Question** — How do we align `apps_research` to the canonical spine
  terminology and augment C0 to produce briefing-grade, JD-aware,
  section-adaptive, evidence-gated company briefs?

- **Answer** — Execute a 5-wave plan: (W1) doc/terminology cleanup; (W2)
  domain-contract schema additions; (W3) route-registry + cache-profile
  updates; (W4) C0/PA/L2 engine augmentation; (W5) FEC producer extension,
  test suite (golden path + JD path + negative controls), and deliverable
  report.

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| `apps_research/config/route_registry.yaml` | route_id rename target | ✅ read |
| `apps_research/config/cert_route_registry.yaml` | JD-digest cache participation | ✅ read |
| `apps_research/config/domain_contract/*.yaml` | schema gap inventory | ✅ read |
| `apps_research/engines/company_brief_engine.py` | C0 engine — depth, JD, retrieval | ✅ read |
| `apps_research/engines/research_retrieval_engine.py` | existing retrieval surface | ✅ read |
| `apps_research/integrations/governed_research_run.py` | hop_checkpoints fields | ✅ read |
| `apps_research/integrations/spine_handoff.py` | R3 contract surface | ✅ read |
| `apps_research/config/hop_pipeline.py` | hop terminology source | ✅ read |
| `apps_research/cert/fec_producer.py` | FEC shape to extend | ✅ read |
| `apps_research/spine_manifest.yaml` | claimed_routes | ✅ read |
| `apps_research/tests/` | existing test surface | ✅ read |
| `.cursor/templates/execution-plan-template.md` | plan format | ✅ read |

---

## Wave Structure

| Wave | Metric | Scope | Checkpoint | Tokens |
|------|--------|-------|------------|--------|
| W1 | Terminology clean — zero "hop"/"DAG" references remain in docs/comments | `TECHNICAL_SPEC.md`, `hop_pipeline.py`, `governed_research_run.py`, `spine_manifest.yaml`, `README.md`, `RUNBOOK.md` | A | ~15K 🟢 |
| W2 | Domain-contract schemas added — 9 new YAML files or sections pass schema lint | `domain_contract/` (7 new YAMLs + 2 updated), `app_domain_manifest.yaml` | B | ~20K 🟢 |
| W3 | Route/cache registry updated — route_id = R3_SIMPLE_GROUNDED_READ, JD-digest in cache compat | `route_registry.yaml`, `cert_route_registry.yaml`, `cache_profiles.yaml`, `route_profiles.yaml`, `spine_manifest.yaml` | C | ~10K 🟢 |
| W4 | C0/PA/L2 engine augmented — depth profiles, adaptive coverage, JD input, structured outputs | `company_brief_engine.py`, `research_assembly_engine.py`, `execution_adapter.py`, `query_decomposer.py` | D | ~35K 🟢 |
| W5 | FEC extended + tests pass — 40+ new tests: golden path, JD path, 23 negative controls | `cert/fec_producer.py`, `tests/_apps_contract/test_apps_research_spine_alignment.py` | E | ~30K 🟢 |

**Total: ~110K tokens across 5 waves, all GREEN**

---

## Out Of Scope

- `apps_rg` and `apps_lic` internal changes — this plan only specifies what
  `apps_research` exposes to them (downstream field shapes in FEC /
  `SynthesisGuidanceForPA`).
- Real Tavily API key wiring or live web retrieval — all new C0 code degrades
  gracefully when `TAVILY_API_KEY` is absent (existing pattern preserved).
- L6 shadow-eval ledger additions — existing `eval_harness_outcome` ledger
  is unchanged; new learning candidates are named in docs only.
- `hop_pipeline.py` deletion — the `HopRegistry`/`HopStageSpec` substrate in
  `apps_shared.orchestration` may still be used by other apps; rename
  `hop_pipeline.py` doc-comment purpose only, do not delete the file.
- Real LLM-judge scoring for new rubric dims — new dims land as
  `intentional_failopen_dims` (established pattern from `apps-eval-harness-closeout-b7c9d2`).
- UWG / L4 durable-write path changes.
- `agentic_core` contract type modifications.

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| 1.1 | Retire hop/DAG docs terminology | `TECHNICAL_SPEC.md`, `README.md`, `RUNBOOK.md`, `hop_pipeline.py` header comment | GAP-1: docs contradict spine prompt | ~5K | 🔲 TODO |
| 1.2 | Retire hop/DAG code terminology | `governed_research_run.py` (`hop_checkpoints` comment), `spine_manifest.yaml` notes, `company_brief_engine.py` depth comment | GAP-1 | ~5K | 🔲 TODO |
| 1.3 | Clarify R3/R5/post-R3 in all narrative surfaces | `TECHNICAL_SPEC.md`, `spine_manifest.yaml`, `route_registry.yaml` description field | GAP-2 | ~5K | 🔲 TODO |
| 2.1 | Add depth profiles YAML | `domain_contract/research_depth_profiles.yaml` (new) | GAP-3 | ~5K | 🔲 TODO |
| 2.2 | Add coverage + source-mix + freshness + contradiction + claim-support YAMLs | `domain_contract/briefing_coverage_matrix_schema.yaml`, `source_portfolio_schema.yaml`, `claim_evidence_map_schema.yaml`, `contradiction_matrix_schema.yaml`, `freshness_policy.yaml`, `source_mix_policy.yaml`, `synthesis_guidance_schema.yaml` (all new) | GAP-3, GAP-4 | ~8K | 🔲 TODO |
| 2.3 | Add JD context + claim classification schema | `domain_contract/jd_context_schema.yaml` (new) | GAP-5 | ~4K | 🔲 TODO |
| 2.4 | Update `app_domain_manifest.yaml` + `input_contract.yaml` | reference new schemas, add `jd_ref`/`jd_content_hash` optional inputs | GAP-3, GAP-5 | ~3K | 🔲 TODO |
| 3.1 | Rename route_id to R3_SIMPLE_GROUNDED_READ | `route_registry.yaml`, `cert_route_registry.yaml` | GAP-6 | ~3K | 🔲 TODO |
| 3.2 | Add JD-digest to cache compat + R5 pre-route terminal | `cache_profiles.yaml` (`jd_digest_compat` field), `route_profiles.yaml` (R5 entry), `cert_route_registry.yaml` route description | GAP-6, GAP-7 | ~4K | 🔲 TODO |
| 3.3 | Update `spine_manifest.yaml` claimed_routes | change type from `R3_grounded_read` to `R3_SIMPLE_GROUNDED_READ`, add R5 terminal shape | GAP-6 | ~3K | 🔲 TODO |
| 4.1 | Depth profiles in `CompanyBriefEngine` | `company_brief_engine.py`: replace `{shallow, standard, deep}` with `COMPANY_BRIEF_{LIGHT,STANDARD,DEEP,DOSSIER}`, add profile-driven query fan-out and per-profile fetch counts | GAP-3 | ~10K | 🔲 TODO |
| 4.2 | Adaptive coverage sections in `CompanyBriefEngine` | `company_brief_engine.py`: replace flat `_FACET_QUERIES` with `coverage_family_catalog` dispatch driven by user-intent/role/JD/sector | GAP-3 | ~8K | 🔲 TODO |
| 4.3 | JD as first-class C0 input | `company_brief_engine.py`: replace `jd_anchor` path shim with structured `jd_context` dict carrying all JD fields; add JD-specific query families; add JD claim classification | GAP-5 | ~8K | 🔲 TODO |
| 4.4 | Structured C0 outputs: FinalEvidenceContract bundle | `company_brief_engine.py`, `research_assembly_engine.py`: emit `BriefingCoverageMatrix`, `SourcePortfolioSummary`, `ClaimEvidenceMap`, `ContradictionMatrix`, `FreshnessReport`, `SectionGapReport`, `SynthesisGuidanceForPA` | GAP-3, GAP-4 | ~9K | 🔲 TODO |
| 4.5 | C0-to-PA gate enforcement | `company_brief_engine.py`: add `_evaluate_c0_pa_gate()` — PASS / WEAK_WITH_CAVEATS / FAIL logic per depth profile thresholds; emit sealed degraded packet on FAIL | GAP-4 | ~6K | 🔲 TODO |
| 4.6 | PA integration: consume structured C0 bundle | `research_assembly_engine.py`: ensure PA slot binding includes all 7 C0 output objects + JD ref when present; fence retrieved content + JD as DATA | GAP-3 | ~4K | 🔲 TODO |
| 4.7 | L2 E1-E5 receipt names | `execution_adapter.py`: rename receipt checks to `L2.E{1-5}.research_*`; remove Hop 1/2/3/4 receipt references | GAP-1 | ~4K | 🔲 TODO |
| 5.1 | FEC producer extension | `cert/fec_producer.py`: add briefing-grade fields: depth profile, section coverage, source portfolio, contradiction matrix, freshness, citation coverage, JD fields when present | GAP-8 | ~5K | 🔲 TODO |
| 5.2 | Golden path + JD path tests | `tests/_apps_contract/test_apps_research_spine_alignment.py` (new): 20 tests covering golden path proof bundle, JD path additions, R1A/R1B cache check order, R5 terminal, C0 → PA gate | GAP-8 | ~12K | 🔲 TODO |
| 5.3 | Negative controls | 23 negative controls per prompt §11: missing RouteContract, R3+no-C0, insufficient sources, no authoritative anchor, unresolved contradiction, JD controls (11 JD-specific), plus existing stale_source + unsupported_claim tightened | GAP-8, GAP-9 | ~10K | 🔲 TODO |
| 5.4 | Deliverable report | `apps_research/SPINE_ALIGNMENT_REPORT.md` (new): files changed, tests added, final YES/NO verdict | — | ~3K | 🔲 TODO |

**Status legend**: 🔲 TODO · 🔄 IN PROGRESS · ✅ DONE · ❌ BLOCKED

---

## Gap Register

**GAP-1: Hop/DAG terminology in docs and code**
- `TECHNICAL_SPEC.md`, `hop_pipeline.py` header comment, `governed_research_run.py`
  `hop_checkpoints` docstring, and `README.md` all use "Hop 1/2/3/4",
  "inner DAG", "3-stage inner DAG", "hop pipeline topology".
- `execution_adapter.py` may use hop receipt names.
- Impact: violates CORE TERMINOLOGY RULE; scanners checking for
  "static DAG" / "hop N" terminology would flag apps_research.

**GAP-2: R3 / R5 / post-R3 semantics not documented correctly**
- Current `route_registry.yaml` description says "no retries, branches, or
  joins" but does not clarify R5 = pre-route terminal vs post-R3
  degraded/failure path. Lincoln-style brief conflated with fixed template.
- Impact: implementors cannot distinguish R5 terminal from C0-fail degraded
  packet; adaptive coverage intent is unclear.

**GAP-3: C0 depth profiles and adaptive coverage absent**
- `company_brief_engine.py` has `depth ∈ {shallow, standard, deep}` mapped
  to `max_queries ∈ {3, 6, 10}`. No `COMPANY_BRIEF_{LIGHT,STANDARD,DEEP,DOSSIER}`
  depth profiles. No source-count floors, citation-anchor floors, or adaptive
  coverage family selection.
- `BriefingCoverageMatrix`, `SourcePortfolioSummary`, `ClaimEvidenceMap`,
  `SynthesisGuidanceForPA`, `SectionGapReport` are absent from C0 output.
- Impact: C0 cannot produce Lincoln-style depth; PA has no coverage guidance.

**GAP-4: C0-to-PA gate and structured evidence outputs absent**
- No PASS / WEAK_WITH_CAVEATS / FAIL gate logic. No `ContradictionMatrix`,
  `FreshnessReport`, or `SectionGapReport`. PA receives flat synthesis
  without structured evidence bundle.
- Impact: weak evidence silently passes to PA; no contradiction or freshness
  enforcement.

**GAP-5: JD as first-class C0 input not implemented**
- `jd_anchor` accepts only a file path; no structured `jd_context` with
  content_hash / origin_label / extracted_themes / claim classification.
  No JD-specific query families generated by C0. No downstream
  `apps_rg_fields` / `apps_lic_fields` in `SynthesisGuidanceForPA`.
- `input_contract.yaml` has no `jd_ref` / `jd_content_hash` optional inputs.
- `cache_profiles.yaml` has no JD-digest cache compatibility field.
- Impact: JD path cannot be proven end-to-end; apps_rg / apps_lic cannot
  consume structured JD evidence.

**GAP-6: Route ID mismatch with canonical spine terminology**
- `route_registry.yaml` registers `apps_research.single_step_v1`, not
  `R3_SIMPLE_GROUNDED_READ`. `cert_route_registry.yaml` uses
  `apps_research.company_brief_v1` for the route_id field.
- `spine_manifest.yaml` uses `R3_grounded_read` (underscore-lowercase),
  not `R3_SIMPLE_GROUNDED_READ`.
- Impact: L0 route-decision tests cannot assert `route_id = R3_SIMPLE_GROUNDED_READ`.

**GAP-7: R5 pre-route terminal not in route/cache profiles**
- No `R5_PRE_ROUTE_FALLBACK` entry in `route_profiles.yaml`. Cache
  compatibility does not check JD digest.
- Impact: R5 path cannot be proven distinct from post-R3 degraded packets
  in negative controls.

**GAP-8: FEC producer does not carry briefing-grade evidence fields**
- Current `produce_fec()` returns: `schema_version`, `producer`, `grounded`,
  `retrieval_sources`, `template_ids`, `route_id`, `evidence_sufficiency`.
  Missing: `research_depth_profile`, section coverage, source portfolio,
  contradiction matrix, freshness report, citation coverage, JD fields.
- Impact: Exit cannot validate briefing-grade evidence quality from FEC.

**GAP-9: Negative controls cover only 2 of 23 required scenarios**
- `negative_controls.yaml` covers `stale_source` and `unsupported_claim`.
  21 required negative controls from prompt §11 (including all 11 JD
  negative controls) are absent.
- Impact: acceptance bar cannot be met; `NO, insufficient evidence` verdict.

---

## Execution Plan

### Wave 1 — Terminology Cleanup (Phases 1.1 – 1.3)

**Scope**: Remove all "Hop 1/2/3/4", "inner DAG", "3-stage inner DAG",
"hop pipeline topology", and "static app DAG" language from documentation,
inline comments, and YAML descriptions. Replace with canonical spine stage
names. Clarify R3/R5/post-R3 semantics everywhere they appear.

**Phase 1.1 — Retire hop/DAG from docs**

Files:
- `apps_research/TECHNICAL_SPEC.md` — rewrite to use U0/L1/L0/R3_SIMPLE_GROUNDED_READ/C0/PA/L2 E1-E5 terminology
- `apps_research/README.md` — update architecture section
- `apps_research/RUNBOOK.md` — update flow description
- `apps_research/config/hop_pipeline.py` header docstring — rewrite to clarify this is a legacy substrate shim, not a canonical "hop pipeline"; rename stage comments to use spine terms (`research_retrieval`, `company_brief`, `research_assembly` stage names are fine; the word "HOP pipeline topology" in the module docstring must go)

**Phase 1.2 — Retire hop/DAG from code comments**

Files:
- `apps_research/integrations/governed_research_run.py` — rename
  `hop_checkpoints` field docstring reference from "Inner-DAG HOP
  pipeline" to "apps_research inner pipeline checkpoints (substrate
  R3_SIMPLE_GROUNDED_READ, no L3)"; field name preserved for
  back-compat but inline comment updated
- `apps_research/engines/company_brief_engine.py` — remove comment
  references to "V2 retrieval pipeline" in the context of "hops"; update
  depth comments
- `apps_research/integrations/execution_adapter.py` — audit for any
  "Hop 1/2/3/4" receipt names; rename to `L2.E{1-5}.research_*`

**Phase 1.3 — Clarify R3/R5/post-R3 everywhere**

Files:
- `apps_research/config/route_registry.yaml` — update `description` field to
  declare: "R3_SIMPLE_GROUNDED_READ: SIMPLE=no L3, GROUNDED=C0 required,
  READ=informational output. R5 is a pre-route terminal fallback before C0
  starts. Post-C0 degraded packets are distinct from R5."
- `apps_research/spine_manifest.yaml` — add note clarifying R5 is separate
  from post-R3 degraded; update Lincoln exemplar note
- `apps_research/TECHNICAL_SPEC.md` — add R3 meaning table, R5 vs
  post-R3 clarification, Lincoln = depth exemplar not fixed template

**Acceptance**: `grep -rn "Hop [0-9]\|inner DAG\|static.*DAG\|HOP pipeline topology" apps_research/` returns zero results excluding `hop_pipeline.py` symbol names.

---

### Wave 2 — Domain Contract Schema Additions (Phases 2.1 – 2.4)

**Scope**: Add 8 new YAML files to `apps_research/config/domain_contract/`
and update 2 existing files to reference them. All new files follow the
existing comment header convention (`# apps_research Fort Knox app-domain contract`).

**Phase 2.1 — research_depth_profiles.yaml (new)**

```yaml
# apps_research domain contract — research depth profiles
# Plan: apps-research-spine-alignment-c0-briefing-2f8a4b W2.P1

research_depth_profiles:
  COMPANY_BRIEF_LIGHT:
    purpose: short company context
    final_sources_min: 3
    final_sources_target: 5
    citation_anchors_min: 5
    output_equivalent: "1-2 pages"

  COMPANY_BRIEF_STANDARD:
    purpose: company + role + market + leadership context
    final_sources_min: 8
    final_sources_target: 12
    citation_anchors_min: 12
    output_equivalent: "3-5 pages"

  COMPANY_BRIEF_DEEP:
    purpose: executive-grade recruiter/outreach/interview briefing
    final_sources_min: 18
    final_sources_target: 25
    final_sources_max: 35
    raw_candidates_min: 80
    raw_candidates_target: 150
    raw_candidates_max: 250
    citation_anchors_min: 30
    citation_anchors_target: 45
    output_equivalent: "8-15 pages"

  COMPANY_BRIEF_DOSSIER:
    purpose: high-stakes diligence/account/interview strategy
    final_sources_min: 35
    final_sources_target: 50
    final_sources_max: 60
    citation_anchors_min: 60
    output_equivalent: "15+ pages"

default_profile: COMPANY_BRIEF_DEEP
default_trigger: >-
  Use COMPANY_BRIEF_DEEP unless L1, route policy, user instruction,
  or runtime budget explicitly selects STANDARD or LIGHT.
```

**Phase 2.2 — 7 new schema/policy YAMLs**

Create each at `apps_research/config/domain_contract/<name>.yaml`:

1. `briefing_coverage_matrix_schema.yaml` — `BriefingCoverageMatrix` shape:
   `briefing_profile_id`, `artifact_type`, `user_intent`, `target_company`,
   `target_role_optional`, `downstream_consumer_optional`,
   `jd_context_optional`, `selected_coverage_sections[]` with per-section
   fields: `section_id`, `coverage_family`, `selection_reason`,
   `required_for_this_brief`, `coverage_status`
   (`PASS|WEAK|WEAK_WITH_CAVEATS|EMPTY|CONFLICTED|BLOCKED`),
   `source_count`, `citation_anchor_count`, `source_type_requirements`,
   `strongest_sources`, `gaps`, `caveats`, `omit_if_unsupported`.
   Coverage family catalog: `company_basics`, `role_context`,
   `leadership_and_org`, `market_and_competitive_context`,
   `technology_and_operating_model`, `product_and_customer_context`,
   `financial_and_value_context`, `risk_governance_and_regulatory`,
   `talent_and_hiring_context`, `outreach_or_interview_strategy`.

2. `source_portfolio_schema.yaml` — `SourcePortfolioSummary` shape:
   `total_sources`, `primary_source_count`,
   `company_official_source_count`, `financial_or_investor_source_count`,
   `role_specific_source_count`, `technology_vendor_or_partner_source_count`,
   `regulatory_or_standards_source_count`,
   `industry_context_source_count`,
   `independent_news_or_interview_source_count`,
   `low_authority_source_count`, `freshness_distribution`,
   `source_diversity_score`.

3. `claim_evidence_map_schema.yaml` — `ClaimEvidenceMap` shape per entry:
   `claim_id`, `claim_text`,
   `claim_origin` (`JD_DECLARED|EXTERNAL|INFERRED_FROM_BOTH`),
   `jd_ref`, `external_support_status`
   (`SUPPORTED|UNSUPPORTED|CONTRADICTED|NOT_REQUIRED`),
   `supporting_sources[]`, `contradicting_sources[]`,
   `allowed_output_treatment`
   (`factual_claim|caveated_claim|recruiter_question|omit`),
   `citation_anchors[]`, `freshness_status`.

4. `contradiction_matrix_schema.yaml` — `ContradictionMatrix` shape:
   `contradiction_flags[]`, `source_disagreement_matrix`,
   `preferred_source_reason`, `unresolved_conflict_notes`,
   detection domains per prompt §CONTRADICTION POLICY.

5. `freshness_policy.yaml` — freshness classes:
   `current_claims` (max_age_days: 90),
   `strategy_claims` (max_age_days: 365),
   `historical_architecture` (max_age_days: 1825),
   `evergreen_industry_context` (max_age_days: 730),
   failure behaviors: `stale_but_useful → WEAK_WITH_CAVEATS`,
   `stale_for_current_claim → BLOCKED`, `no_recent_source → WEAK`.

6. `source_mix_policy.yaml` — source mix for COMPANY_BRIEF_DEEP:
   `min_total_sources: 18`, `target_total_sources: 25`,
   `max_total_sources_after_rerank: 35`,
   required source categories with mins per prompt §SOURCE MIX POLICY,
   hard guardrails (must_include_primary_sources, etc.).

7. `synthesis_guidance_schema.yaml` — `SynthesisGuidanceForPA` shape:
   `selected_sections`, `omitted_sections_with_reason[]`,
   `must_include_claims[]`, `must_caveat_claims[]`, `forbidden_claims[]`,
   `open_questions[]`, `confidence_labels`,
   `recruiter_outreach_overlay` (why_this_company, why_this_role, why_now,
   JD_theme_to_company_evidence_map, candidate_positioning_angles,
   likely_pain_points, role_mandate_interpretation,
   executive_stakeholders, open_questions_for_recruiter,
   avoid_overclaiming_notes),
   `jd_usage_guidance` when JD present,
   `apps_rg_downstream_fields` when relevant,
   `apps_lic_downstream_fields` when relevant.

**Phase 2.3 — jd_context_schema.yaml (new)**

`JDContext` shape: `jd_present`, `jd_ref`, `jd_content_hash`,
`jd_origin_label`, `jd_role_title`, `jd_company`, `jd_location`,
`jd_working_model`, `jd_extracted_themes[]`, `jd_required_skills[]`,
`jd_preferred_skills[]`, `jd_responsibility_clusters[]`,
`jd_success_metric_signals[]`, `jd_ambiguities[]`,
`jd_claims_requiring_external_support[]`.
JD claim classification vocab: `JD_DECLARED`, `EXTERNALLY_SUPPORTED`,
`UNSUPPORTED_BUT_RELEVANT`, `CONTRADICTED`.

**Phase 2.4 — Update existing manifests**

- `app_domain_manifest.yaml`: add refs to all 8 new schema files under
  new key `briefing_schema_refs`.
- `input_contract.yaml`: add optional inputs `jd_ref`,
  `jd_content_hash`, `jd_origin_label`, `research_depth_profile`,
  `downstream_consumer`.
- `negative_controls.yaml`: expand from 2 to 25 controls — add the 23
  missing scenarios from prompt §11 (both baseline and JD-specific).

**Acceptance**: `python -c "import yaml; [yaml.safe_load(open(f)) for f in glob('apps_research/config/domain_contract/*.yaml')]"` exits 0. `app_domain_manifest.yaml` references all new schema files.

---

### Wave 3 — Route/Cache Registry Updates (Phases 3.1 – 3.3)

**Scope**: Update route and cache profile files so the canonical
`R3_SIMPLE_GROUNDED_READ` route ID is used consistently, JD digest
participates in cache compatibility, and R5 pre-route terminal shape is
declared.

**Phase 3.1 — Rename route_id to R3_SIMPLE_GROUNDED_READ**

- `apps_research/config/route_registry.yaml`:
  - Change `route_id: apps_research.single_step_v1` →
    `route_id: R3_SIMPLE_GROUNDED_READ`
  - Add `execution_form: SINGLE_STEP`
  - Add `l3_required: false`
  - Add `selected_capability: apps_research.company_brief_v1`
  - Update `description` to use full R3/R5 clarification from Phase 1.3
  - Add comment: `# SIMPLE=no L3, GROUNDED=C0 required, READ=informational output`

- `apps_research/config/cert_route_registry.yaml`:
  - Change `route_id: apps_research.company_brief_v1` in the routes list
    to `route_id: R3_SIMPLE_GROUNDED_READ`
  - Keep `selected_capability: apps_research.company_brief_v1`

- `apps_research/__main__.py`:
  - Update hardcoded `route_id` strings from `apps_research.company_brief_v1`
    to `R3_SIMPLE_GROUNDED_READ` in the `resolve_fec` call context

**Phase 3.2 — JD-digest cache compat + R5 terminal in route profiles**

- `apps_research/config/domain_contract/cache_profiles.yaml`:
  - Add field: `jd_digest_compat_required: true`
  - Add comment explaining: when JD is present in a request, the
    `jd_content_hash` must match (or be compatibility-approved) for
    R1A/R1B cache hits to be valid
  - Add field: `r1b_jd_intent_compat: similarity_threshold_override: 0.88`
    (tighter threshold when JD context differs)

- `apps_research/config/domain_contract/route_profiles.yaml`:
  - Rename existing `default_route_id: research.company_brief.default` to
    `R3_SIMPLE_GROUNDED_READ`
  - Add `R5_PRE_ROUTE_FALLBACK` entry with terminal packet types:
    `CLARIFY_PACKET`, `SAFE_ABSTAIN_PACKET`, `SAFE_FALLBACK_PACKET`,
    `MARK_DEGRADED_PACKET`; `execution_form: TERMINAL_SHORTCIRCUIT`;
    `l3_required: false`; usage triggers per prompt §R5 section
  - Add `R1A_EXACT_CACHE` and `R1B_SEMANTIC_CACHE` entries with
    `execution_form: TERMINAL_SHORTCIRCUIT`

**Phase 3.3 — Update spine_manifest.yaml**

- Change `type: R3_grounded_read` to `type: R3_SIMPLE_GROUNDED_READ`
- Add second claimed_route entry for `type: R5_PRE_ROUTE_FALLBACK`
  with appropriate description
- Add note: "R3_SIMPLE_GROUNDED_READ: SIMPLE=bypass L3, GROUNDED=C0 mandatory,
  READ=informational/briefing. R5 is pre-route terminal before C0 starts.
  Post-R3 degraded/failure packets are distinct from R5."

**Acceptance**: `grep -rn "single_step_v1\|R3_grounded_read" apps_research/config/` returns zero results. `grep -n "R3_SIMPLE_GROUNDED_READ" apps_research/config/route_registry.yaml apps_research/config/cert_route_registry.yaml apps_research/spine_manifest.yaml` returns 3+ matches.

---

### Wave 4 — C0/PA/L2 Engine Augmentation (Phases 4.1 – 4.7)

**Scope**: Augment `company_brief_engine.py` and `research_assembly_engine.py`
to implement the full C0 briefing-grade retrieval standard: depth profiles,
adaptive coverage, JD first-class input, structured outputs, C0-to-PA gate.
Update `execution_adapter.py` for L2 E1-E5 receipt names.

All new code degrades gracefully: when Tavily is absent, empty evidence
bundles are produced; all schemas emit stubs with correct structure but
zero evidence, preserving existing offline-test green behavior.

**Phase 4.1 — Depth profiles in CompanyBriefEngine**

In `company_brief_engine.py`:

- Add `_DEPTH_PROFILES` dict mapping the 4 profile IDs to their
  parameter objects (source floors, query counts, raw candidate counts).
- Add `_resolve_depth_profile(depth: str) -> dict` that maps the profile ID
  to parameters. Map legacy values: `"shallow"` → `COMPANY_BRIEF_LIGHT`,
  `"standard"` → `COMPANY_BRIEF_STANDARD`, `"deep"` → `COMPANY_BRIEF_DEEP`.
- Replace `max_queries = {shallow:3, standard:6, deep:10}` with
  profile-driven `query_count = profile["query_count"]`.
- In `_run_research_v2`, replace hard-coded `top_k=10` / `cutoff=5` with
  profile-driven per-query fetch parameters.
- Thread `research_depth_profile` str through `execute()` signature
  (default: `"COMPANY_BRIEF_DEEP"`).

**Phase 4.2 — Adaptive coverage family selection**

In `company_brief_engine.py`:

- Add `_COVERAGE_FAMILY_CATALOG` — maps each of the 10 family IDs to their
  example section IDs from prompt §ADAPTIVE COVERAGE MATRIX.
- Add `_select_coverage_families(intent: str, role: str | None, jd_context: dict | None, depth_profile: str, sector: str | None) -> list[str]`:
  - Apply selection rules from prompt examples (recruiter outreach → 6 families;
    SVP IT Strategy → 6 families; sales account → 6 families; resume targeting → 5 families).
  - Default to all families when intent is generic.
- Replace flat `_FACET_QUERIES` dispatch with `_build_query_families(company, role, jd_context, selected_families) -> list[tuple[str,str]]`:
  - For each selected family, generate the baseline query templates from
    prompt §QUERY FAMILY REQUIREMENTS.
  - When JD is present, add JD-specific query families (role_mandate_queries,
    jd_theme_queries, jd_skill_to_company_evidence_queries,
    role_pain_point_queries, hiring_signal_queries).
- Emit `selected_coverage_sections` list in C0 output.

**Phase 4.3 — JD as first-class C0 input**

In `company_brief_engine.py`:

- Replace `jd_anchor: Optional[Path]` with `jd_context: dict | None` in
  `execute()`. Accept dict with keys from `JDContext` schema (W2.3).
- Add `_parse_jd_context(raw: Any) -> dict | None`: accepts dict (direct
  structured input), path-str (legacy file path for back-compat, reads
  JSON/YAML, extracts fields), or None.
- Add `_classify_jd_claims(jd_context: dict, retrieved_evidence: dict) -> list[dict]`:
  classify each `jd_claims_requiring_external_support` entry as
  `JD_DECLARED`, `EXTERNALLY_SUPPORTED`, `UNSUPPORTED_BUT_RELEVANT`, or
  `CONTRADICTED` based on what C0 retrieved.
- When `jd_context` present:
  - Bind `jd_content_hash` from dict; if missing, compute from serialized JD text.
  - Pass JD fields to `_select_coverage_families()` and `_build_query_families()`.
  - Produce `jd_usage_guidance` block for `SynthesisGuidanceForPA`.
  - Populate `apps_rg_downstream_fields` and `apps_lic_downstream_fields` stubs.

**Phase 4.4 — Structured C0 output bundle**

In `company_brief_engine.py`, add `_build_c0_bundle(...)` that assembles:

1. `BriefingCoverageMatrix` — per-section status from evidence scan
2. `SourcePortfolioSummary` — count by source type from retrieved docs
3. `ClaimEvidenceMap` — per-claim support status (stub entries for each
   claim extracted from synthesis; JD claims classified via Phase 4.3)
4. `ContradictionMatrix` — conflict entries detected across sources
5. `FreshnessReport` — per-source freshness class evaluation against
   `freshness_policy.yaml` thresholds
6. `SectionGapReport` — sections with `EMPTY` or `WEAK` coverage status
7. `SynthesisGuidanceForPA` — assembled from all of the above, including
   `selected_sections`, `omitted_sections`, guidance overlays

Return as `c0_bundle: dict` from `execute()`.

In `research_assembly_engine.py`, extend `assemble()` to consume `c0_bundle`
and bind all 7 objects into PA prompt slots (fence as DATA not instruction).

**Phase 4.5 — C0-to-PA gate**

In `company_brief_engine.py`, add `_evaluate_c0_pa_gate(c0_bundle, depth_profile) -> str`:

- Returns `"PASS"`, `"WEAK_WITH_CAVEATS"`, or `"FAIL"`.
- PASS thresholds for `COMPANY_BRIEF_DEEP`:
  - `selected_required_sections_coverage >= 85%`
  - `total_final_sources >= 18`
  - `citation_anchor_count >= 30`
  - no unresolved critical contradiction
  - at least one authoritative company/source anchor
  - when JD present: `jd_content_hash` bound + critical JD themes have
    external support or marked as open questions
- WEAK_WITH_CAVEATS thresholds: 60–84% coverage, 10–17 sources.
- FAIL / DEGRADE: coverage < 60%, sources < 10, unresolved critical
  contradiction, company/entity unresolved, etc.
- On FAIL: return `sealed_degraded_or_failure_packet` dict to Exit (not PA).
- On WEAK_WITH_CAVEATS: pass to PA with required caveats in
  `SynthesisGuidanceForPA.must_caveat_claims`.

**Phase 4.6 — PA integration**

In `research_assembly_engine.py` `assemble()` / `_compile_prompt()`:

- Add named slots for all 7 C0 bundle objects in the prompt template.
- Ensure JD text (if present) is fenced as `[DATA: JD content]` — not instruction.
- Ensure retrieved content is fenced as `[DATA: evidence chunk]`.
- Bind `research_depth_profile` + `selected_coverage_sections` in prompt context.
- Emit `CompiledPromptArtifact` with bundle refs (existing type, extended fields).

**Phase 4.7 — L2 E1-E5 receipt names**

In `execution_adapter.py`:

- Audit all receipt/check string literals for "Hop 1/2/3/4" occurrences.
- Replace with:
  - `L2.E1.research_execution_context_bound`
  - `L2.E2.research_evidence_validated`
  - `L2.E3.research_brief_synthesized`
  - `L2.E4.research_local_heal_applied`
  - `L2.E5.research_artifact_sealed`
- Add `l3_required: false` and `route_id: R3_SIMPLE_GROUNDED_READ`
  assertions in E1 context-freeze check.

**Acceptance**: All existing tests in `apps_research/tests/` pass. `python -m apps_research --apps-e2e-live` exits 0.

---

### Wave 5 — FEC Extension, Tests, and Deliverable Report (Phases 5.1 – 5.4)

**Scope**: Extend the FEC producer to carry briefing-grade evidence fields,
write the full test suite (golden path + JD path + 23 negative controls),
and emit the final deliverable report.

**Phase 5.1 — FEC producer extension**

In `apps_research/cert/fec_producer.py`:

Add to `produce_fec()` output dict (all keys fail-soft when absent from `run_context`):

```python
{
    # existing fields preserved ...
    "schema_version": "1.1",                    # bump minor for new fields
    "research_depth_profile": ...,              # str from run_context
    "selected_section_count": ...,              # int
    "covered_section_count": ...,               # int (status = PASS or WEAK*)
    "source_portfolio": ...,                    # SourcePortfolioSummary dict
    "citation_anchor_count": ...,               # int
    "contradiction_count": ...,                 # int
    "freshness_violations": ...,                # list of section_ids
    "unsupported_claim_count": ...,             # int
    "recruiter_outreach_overlay_present": ...,  # bool
    "briefing_schema_valid": ...,               # bool
    # JD fields (omitted / None when no JD) ---
    "jd_present": ...,                          # bool
    "jd_ref": ...,                              # str or None
    "jd_content_hash": ...,                     # str or None
    "jd_parse_receipt": ...,                    # dict or None
    "jd_theme_coverage_count": ...,             # int or None
    "jd_to_company_evidence_map_present": ...,  # bool
    "jd_unsupported_claim_count": ...,          # int or None
    "jd_contradiction_count": ...,              # int or None
}
```

Update `cert/__init__.py` to re-register (no-op if already registered).

**Phase 5.2 — Golden path + JD path tests**

New file: `tests/_apps_contract/test_apps_research_spine_alignment.py`

20 tests:

1. `test_route_id_is_r3_simple_grounded_read` — load `route_registry.yaml`,
   assert `routes[0].route_id == "R3_SIMPLE_GROUNDED_READ"`.
2. `test_cert_route_id_is_r3_simple_grounded_read` — same for
   `cert_route_registry.yaml`.
3. `test_spine_manifest_route_type_r3` — load `spine_manifest.yaml`,
   assert `claimed_routes[0].type == "R3_SIMPLE_GROUNDED_READ"`.
4. `test_r5_terminal_in_route_profiles` — load `route_profiles.yaml`,
   assert `R5_PRE_ROUTE_FALLBACK` entry present with `execution_form =
   TERMINAL_SHORTCIRCUIT` and `l3_required = false`.
5. `test_depth_profile_deep_source_floor` — instantiate engine stub,
   call `_resolve_depth_profile("COMPANY_BRIEF_DEEP")`, assert
   `final_sources_min == 18`, `citation_anchors_min == 30`.
6. `test_depth_profile_default_is_deep` — assert
   `_resolve_depth_profile(None)` returns COMPANY_BRIEF_DEEP parameters.
7. `test_coverage_family_recruiter_outreach_selects_correct_families` —
   call `_select_coverage_families("recruiter outreach", None, None, "COMPANY_BRIEF_DEEP", None)`,
   assert includes `company_basics`, `talent_and_hiring_context`,
   `outreach_or_interview_strategy`.
8. `test_no_l3_required_flag` — load `route_registry.yaml`, assert
   `l3_required == false`.
9. `test_c0_bundle_contains_all_required_outputs` — call engine with
   mocked retrieval, assert `c0_bundle` keys include all 7 required objects.
10. `test_c0_pa_gate_pass_threshold` — inject 18+ sources with 30+
    citation anchors, assert gate returns `"PASS"`.
11. `test_c0_pa_gate_fail_below_floor` — inject 5 sources, assert gate
    returns `"FAIL"` and engine returns `sealed_degraded_or_failure_packet`.
12. `test_c0_pa_gate_weak_with_caveats` — inject 12 sources, assert gate
    returns `"WEAK_WITH_CAVEATS"`.
13. `test_jd_content_hash_bound_when_jd_present` — call engine with JD
    context dict, assert `c0_bundle["jd_context"]["jd_content_hash"]` non-empty.
14. `test_jd_theme_queries_generated` — with JD present, assert query list
    includes at least one JD-theme-derived query string.
15. `test_jd_claim_classified_jd_declared` — JD claim with no external
    support classified as `JD_DECLARED`.
16. `test_apps_rg_downstream_fields_populated_when_jd` — with JD present,
    assert `SynthesisGuidanceForPA["apps_rg_downstream_fields"]` non-empty dict.
17. `test_fec_carries_depth_profile` — run `produce_fec` with
    `run_context["research_depth_profile"] = "COMPANY_BRIEF_DEEP"`, assert
    `fec["research_depth_profile"] == "COMPANY_BRIEF_DEEP"`.
18. `test_fec_carries_jd_content_hash` — run `produce_fec` with JD context,
    assert `fec["jd_present"] == True`, `fec["jd_content_hash"]` non-empty.
19. `test_l2_receipt_names_use_spine_terminology` — scan
    `execution_adapter.py` for strings matching `r"L2\.E[1-5]\.research_"`,
    assert at least 5 distinct receipt names present.
20. `test_no_hop_n_terminology_in_source` — `grep -rn "Hop [1-4]\b"
    apps_research/` returns zero results.

**Phase 5.3 — Negative controls**

In `tests/_apps_contract/test_apps_research_spine_alignment.py` (or a
sibling file `test_apps_research_negative_controls.py`), add 23 negative
control tests matching prompt §11:

Baseline controls (12):
- `test_neg_missing_route_contract` — no RouteContract → gate fails closed
- `test_neg_r3_no_c0_evidence` — R3 selected but FinalEvidenceContract missing → FAIL
- `test_neg_grounding_required_but_fec_missing` — `grounding_required=true`, no FEC → FAIL
- `test_neg_deep_under_10_sources_passes_as_pass` — assert gate DOES NOT return PASS when sources < 10
- `test_neg_deep_no_authoritative_anchor_passes_as_pass` — assert gate DOES NOT return PASS when no company-official source
- `test_neg_deep_critical_contradiction_passes_as_pass` — assert gate DOES NOT return PASS when unresolved critical contradiction
- `test_neg_stale_source_for_current_claim_no_caveat` — stale source for current claim without caveat → BLOCKED freshness status
- `test_neg_financial_metric_no_primary_source` — financial metric claim with no primary/financial source → FAIL claim support
- `test_neg_role_mandate_no_official_source` — role mandate with no official/role source → FAIL claim support
- `test_neg_vendor_claim_treated_as_neutral` — vendor case study not labeled as vendor claim → violation
- `test_neg_fixed_lincoln_sections_used` — assert C0 does NOT force fixed Lincoln section list when intent is generic recruiter
- `test_neg_direct_research_attempts_l3` — assert `l3_required` is never True in direct apps_research route

JD negative controls (11):
- `test_neg_jd_present_no_content_hash` — JD dict without `content_hash` → extract or fail closed
- `test_neg_jd_as_trusted_authority` — JD responsibility presented as verified company strategy without external support → classified `JD_DECLARED` not `EXTERNALLY_SUPPORTED`
- `test_neg_jd_company_conflicts_target_company` — JD company != target company, no resolution → R5 terminal or contradiction flag
- `test_neg_jd_responsibilities_as_verified_strategy` — JD responsibilities without external evidence → `JD_DECLARED`, must not be factual_claim
- `test_neg_jd_prompt_injection_overrides_system` — JD text containing instruction-like content fenced as DATA, does not alter route/policy
- `test_neg_c0_ignores_jd_for_coverage_sections` — when JD present, `selected_coverage_sections` must include role_context family
- `test_neg_c0_no_jd_query_families` — when JD present, query list must include at least one JD-theme query
- `test_neg_pa_receives_jd_without_fencing` — assert PA prompt artifact fences JD content as DATA
- `test_neg_l2_presents_jd_claim_as_factual` — JD-declared claim without external support must not appear as `allowed_output_treatment: factual_claim`
- `test_neg_apps_rg_no_jd_resume_map` — when JD present, FEC `jd_to_company_evidence_map_present` must be True when downstream = apps_rg
- `test_neg_apps_lic_no_jd_outreach_map` — when JD present, FEC must carry apps_lic downstream fields when downstream = apps_lic

Also update `negative_controls.yaml` (domain contract) with the 23 control entries following existing YAML shape.

**Phase 5.4 — Deliverable report**

Create `apps_research/SPINE_ALIGNMENT_REPORT.md`:

```markdown
# apps_research Spine Alignment Report
Plan: apps-research-spine-alignment-c0-briefing-2f8a4b

## Files Changed
...

## Files Created
...

## Tests Added
...

## Commands Run
...

## Passing Evidence
...

## Failing Evidence
...

## Remaining Gaps
...

## Final Verdict
Is apps_research aligned to the canonical agentic_core spine and
C0 briefing-grade retrieval standard?

[YES / NO + reason from acceptance bar]
```

**Acceptance**: `pytest tests/_apps_contract/test_apps_research_spine_alignment.py tests/_apps_contract/test_apps_research_negative_controls.py -v` exits 0. Deliverable report populated with verdict.

---

## Rules

- No L3 usage introduced anywhere in apps_research direct path.
- All new C0 code degrades gracefully when `TAVILY_API_KEY` is absent or
  Tavily is unavailable — preserve offline-green test invariant.
- Existing `apps_research/tests/` tests must remain green throughout.
- New files follow canonical SSOT routing: `check_*.py` → `ops_scripts/ci/`,
  test files → `tests/_apps_contract/`.
- No hop/DAG terminology introduced in new code or comments.
- `jd_anchor` path shim preserved with deprecation warning for back-compat;
  new `jd_context` dict is the preferred path.
- All FEC schema changes use `schema_version: "1.1"` minor bump.
- No `agentic_core` contract type modifications.
- `hop_pipeline.py` file is NOT deleted; only its docstring is updated.

---

## Success Criteria

- [ ] `grep -rn "Hop [1-4]\b\|inner DAG\|static.*DAG\|HOP pipeline topology" apps_research/` returns zero results
- [ ] `apps_research/config/route_registry.yaml` → `route_id: R3_SIMPLE_GROUNDED_READ`
- [ ] `apps_research/config/cert_route_registry.yaml` → `route_id: R3_SIMPLE_GROUNDED_READ`
- [ ] `apps_research/spine_manifest.yaml` → `type: R3_SIMPLE_GROUNDED_READ`
- [ ] 8 new YAML files present in `apps_research/config/domain_contract/`
- [ ] `CompanyBriefEngine` supports 4 canonical depth profiles with correct floors
- [ ] `CompanyBriefEngine` uses adaptive coverage family selection (not fixed Lincoln sections)
- [ ] JD context dict accepted as first-class C0 input with content_hash binding
- [ ] C0 emits all 7 required structured output objects
- [ ] C0-to-PA gate returns PASS/WEAK_WITH_CAVEATS/FAIL per depth-profile thresholds
- [ ] PA fences retrieved content and JD content as DATA
- [ ] L2 E1-E5 receipt names use `L2.E{1-5}.research_*` pattern
- [ ] FEC carries briefing-grade fields (depth profile, section coverage, source portfolio, JD fields)
- [ ] 20 golden/JD path tests pass in `test_apps_research_spine_alignment.py`
- [ ] 23 negative control tests pass in `test_apps_research_negative_controls.py`
- [ ] All existing `apps_research/tests/*.py` tests continue to pass
- [ ] `SPINE_ALIGNMENT_REPORT.md` populated with final YES/NO verdict

---

## Rollback Strategy

1. Each wave is a discrete commit; rollback to prior commit to undo any wave.
2. Wave 1 (docs only) — no runtime behavior; rollback is `git checkout apps_research/{TECHNICAL_SPEC,README,RUNBOOK}.md`.
3. Wave 2 (new YAML files only) — delete new YAML files; update `app_domain_manifest.yaml` refs.
4. Wave 3 (route_id rename) — revert route/cache/spine YAML files; existing `__main__.py` string literals.
5. Wave 4 (engine augmentation) — all new methods are additive or behind
   `if jd_context` / `if depth_profile == "COMPANY_BRIEF_DEEP"` guards;
   revert `company_brief_engine.py` and `research_assembly_engine.py` to
   prior state. Legacy `depth="deep"` path is preserved via mapping in
   `_resolve_depth_profile`.
6. Wave 5 (FEC + tests) — revert `fec_producer.py` to prior version;
   delete new test files. Existing FEC tests in
   `tests/_apps_contract/test_apps_research_fec_producer.py` remain green.

---

## Acceptance Criteria

| Metric | Target | Verification |
|---|---|---|
| Hop/DAG terminology eliminated | 0 occurrences | `grep -rn "Hop [1-4]\|inner DAG" apps_research/` |
| Route ID canonical | `R3_SIMPLE_GROUNDED_READ` in 3 files | grep assertion |
| Depth profiles | 4 profiles in YAML + engine | schema lint + unit test |
| Adaptive coverage | 10 families in catalog | `test_coverage_family_*` |
| C0 structured outputs | 7 bundle objects present | `test_c0_bundle_contains_all_required_outputs` |
| C0-to-PA gate | PASS/FAIL per floor | `test_c0_pa_gate_*` (3 tests) |
| JD first-class input | content_hash bound, query families generated | `test_jd_*` (6 tests) |
| FEC briefing fields | depth_profile + source portfolio + JD fields | `test_fec_carries_*` (2 tests) |
| Golden path tests | 20 pass | pytest exit 0 |
| Negative controls | 23 pass | pytest exit 0 |
| Existing tests | zero regressions | `pytest apps_research/tests/` |
| Final verdict | YES or documented NO | `SPINE_ALIGNMENT_REPORT.md` |

---

## Cursor Agent Alignment Checks

- Wave 1 edits documentation only — no code changes; safe to execute first.
- Wave 2 creates YAML files only — no runtime impact; safe to execute before engine work.
- Wave 4 augments engines additively; legacy `depth ∈ {shallow,standard,deep}` mapped via `_resolve_depth_profile` — no existing caller breaks.
- Negative controls are test-only; they assert failure scenarios without modifying production paths.
- All engine changes degrade gracefully (empty bundles when Tavily absent) — offline CI stays green.
