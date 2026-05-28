# Remaining Resume-Rigor Architecture Finish Wave

**Status:** PASS (non-runtime architecture)
**Runtime proof:** DEFERRED — no live Qwen run, no full resume generation. Runtime proof will be performed later with the user.
**agentic_core diff:** empty.

This wave completes the non-runtime architecture so `apps_rg` generates **headline**, **unify_bullets**, and **unify_narrative** from graph-backed proof while preserving base SVP Engineering rigor. It mirrors the already-shipped IBM role-episode and competency-capability patterns.

## Authority model (enforced)

| Source | Role |
|---|---|
| Graph skills + linked source facts + role episode / positioning bundles | content + proof authority |
| Base resume | seniority / technical specificity / scope / voice calibration only |
| Archive resumes | provenance inventory only |
| JD / briefing | targeting only |
| E0 examples | style only |

## PART A — Headline graph-positioning wiring

- Data: [`headline_positioning_bundles.json`](../../../apps_rg/fact_inventory/headline_positioning_bundles.json) — 7 positioning families (`svp_engineering_leadership`, `agentic_ai_platforms`, `distributed_ai_infrastructure`, `runtime_governance`, `enterprise_ai_architecture`, `platform_productization`, `regulated_ai_systems`).
- Registry: [`headline_positioning_registry.py`](../../../apps_rg/runtime/sections/headline_positioning_registry.py)
- Evidence pack (`HEADLINE_POSITIONING_EVIDENCE_PACK`): [`headline_positioning_evidence.py`](../../../apps_rg/runtime/sections/headline_positioning_evidence.py)
- X2 gates: [`headline_positioning_x2.py`](../../../apps_rg/runtime/validators/headline_positioning_x2.py), wired into [`headline_x2.py`](../../../apps_rg/runtime/validators/headline_x2.py)
- C0/PA injection: [`headline_pa.py`](../../../apps_rg/runtime/sections/headline_pa.py)

Fail shapes (e.g. `SVP IT Strategy | Data Modernization | AI Governance`) are demoted by `x2_headline_generic_it_strategy_demote_forbidden`. Pass shapes (e.g. `SVP Engineering | Agentic AI Platforms | Insurance IT Modernization | Runtime Governance`) satisfy seniority + platform/runtime + governance floors.

## PART B — Unify graph gap fill

[`unify_graph_gap_fill.json`](../../../apps_rg/fact_inventory/unify_graph_gap_fill.json) classifies all 20 required architecture-spine signals as `ACTIVE_CONFIRMED`, `ACTIVE_INTERNAL_ONLY`, `DRAFT`, or `SUPPORTING_CONTEXT_ONLY`. Internal-only signals (dependency graph accelerator, architecture visibility, identity controls) carry an `external_claim_policy` that blocks unqualified external claims; `API gateways` remains `DRAFT` with no claim authority.

## PART C — Unify role episode bundles

[`unify_role_episode_bundles.json`](../../../apps_rg/fact_inventory/unify_role_episode_bundles.json) defines the 6 required bundles, all bound to employer `Unify` / `employment_exp_unify_001` / `2023-02 to present`, each with `graph_skill_node_ids`, `linked_source_fact_ids`, and `section_eligibility`. Registry: [`unify_graph_role_episode_registry.py`](../../../apps_rg/runtime/sections/unify_graph_role_episode_registry.py). Metrics restricted to the approved `metric_outcome_id` list; `$14M operating capacity` remains conditional/HOLD.

## PART D / E — Unify bullets + narrative consumption

- Evidence pack (`UNIFY_ROLE_EPISODE_EVIDENCE_PACK`): [`unify_role_episode_evidence.py`](../../../apps_rg/runtime/sections/unify_role_episode_evidence.py)
- X2 gates: [`unify_role_episode_x2.py`](../../../apps_rg/runtime/validators/unify_role_episode_x2.py) wired into [`unify_bullets_x2.py`](../../../apps_rg/runtime/validators/unify_bullets_x2.py) and [`unify_narrative_x2.py`](../../../apps_rg/runtime/validators/unify_narrative_x2.py)
- PA injection: [`unify_bullets_pa.py`](../../../apps_rg/runtime/sections/unify_bullets_pa.py), [`unify_narrative_pa.py`](../../../apps_rg/runtime/sections/unify_narrative_pa.py)

Flat skill-only packets, missing bundle IDs, missing employer/time-window binding, metrics without `metric_outcome_id`, generic consulting language, and base/archive n-gram hydration above threshold all hard-fail.

## PART F — Cross-section signal guards

[`cross_section_signal_guards.py`](../../../apps_rg/runtime/sections/cross_section_signal_guards.py) — shared helpers (`seniority_floor_score`, `technical_specificity_score`, `detect_generic_consulting_phrases`, `detect_jd_only_phrases`, `base_archive_ngram_overlap`, `is_flat_skill_only_graph_packet`) reusing existing vocab from `narrative_quality_x2` / `bullet_ngram_overlap_x2`. No IBM/competencies behavior change.

## Config decision

[`section_retrieval_profile.yaml`](../../../apps_rg/config/domain_contract/section_retrieval_profile.yaml): `graph_expansion_allowed: true` is set **only** alongside `*_bundle_consumption: required` and `graph_expansion_mode: *_bundle_only` for headline, unify_bullets, unify_narrative. Flat-skill / JD-only generation cannot pass.

## Tests & acceptance

| Gate | Result |
|---|---|
| `python -m compileall apps_rg -q` | exit 0 |
| `test_remaining_resume_rigor_finish.py` | 22 passed |
| IBM + competencies regression suites | 165 passed |
| `git diff --name-only agentic_core/` | empty |

### Pre-existing failures (stash-parity confirmed, NOT regressions)

Re-running with all wave changes stashed (`git stash -u`) reproduced these identically:

- `test_headline_x2_fixed_prefix_contract.py::test_valid_canonical_derived_passes` and `::test_mocked_runtime_with_passing_x2_still_not_x3_allow` — pre-existing `x2_headline_no_narrowing_it_labels`.
- `test_section_complexity_budget.py::test_ci_complexity_baseline_gate_passes_on_clean_tree` — baseline drift (incl. `executive_summary:loc_delta=8729` from prior waves).
- `test_section_gate_coverage.py::test_weak_fail_cases_reference_valid_lanes_and_critical_gates` and `::test_all_lane_critical_gates_have_weak_or_dedicated_coverage` — pre-existing coverage-map gaps.

## Non-claims

- No live runtime proof. No full resume generation was run.
- No metric promotion beyond the approved/linked Unify list.
- No agentic_core modification. No IBM/competencies behavior change.
