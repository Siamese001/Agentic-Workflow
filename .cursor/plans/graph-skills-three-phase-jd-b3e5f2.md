# Graph Skills — Three-Phase JD Quality Enhancements

**Plan ID**: graph-skills-three-phase-jd-b3e5f2  
**Created**: 2026-05-27  
**Status**: In Progress  
**Notion DB**: Plans (`6aba34d9-4d0b-4f4c-b956-b2bdea541ca9`)

---

## Context (SCQA)

**Situation**: apps_rg graph skills surface career evidence from three career tracks:
- Phase 1 — Actuarial / Risk / Derivatives (2002–2010), `track_actuarial_risk_derivatives`
- Phase 2 — Data / Cloud / ML / GTM (2010–2022), `track_data_tech_cloud_ml`
- Phase 3 — GenAI / Agentic (2022–present), `track_genai_agentic`

`DEFAULT_TRACK_WEIGHTS` starts at (0.10 / 0.25 / 0.65).

**Complication**: JDs that require all three career phases simultaneously (regulated AI governance, insurance tech transformation with AI, banking platform AI with risk rigor) starve Phase 1 evidence. Even with max JD keyword boost (+0.08), Phase 1 only reaches ~18% pre-normalization, then compresses back down. No "three-phase hit" detection sentinel exists — gates, PA templates, and X1D judges cannot branch on the three-era career posture. The `EXECUTIVE_CAPABILITY_FRAMES` list has zero Phase 1 entries beyond `basel`. `SEMANTIC_VARIANT_MAP` has only 4 entries (all Phase 3/InsurTech). Hybrid boost only runs on `executive_summary`.

**Question**: What specific code changes will ensure higher-quality resume outputs for JDs that trigger all three career phases?

**Answer**: 10 targeted enhancements across 6 files, sequenced in 4 waves by blast radius, with Waves 1–2 implemented in this plan.

---

## Status Tables

### Wave Progress

| Wave | Focus | Files | Status |
|------|-------|-------|--------|
| 1 (Wave A) | Sentinel + JD keyword coverage + exec frames + SEMANTIC_VARIANT_MAP | `graph_selection_rationale.py`, `track_weighted_graph_expansion.py`, `c03_graph_ref_policy.py`, `graph_skills_utilization_scorer.py` | Complete |
| 2 (Wave B) | THREE_PHASE_GENERALIST profile + binding diversity + hybrid boost | `track_weighted_graph_expansion.py`, `c03_graph_ref_policy.py`, `graph_skills_hybrid_boost.py` | Complete |
| 3 (Wave C) | X1D rubric career-phase diversity marker | X1D rubric modules | Deferred |
| 4 (Wave D) | Cross-section career-phase floor gate | `cross_section_x2.py` | Deferred |

---

## Wave 1 — Sentinel + Coverage Additions

**Enhancements**: #1, #4, #5, #6, #9 from canvas analysis

### Scope

| # | Enhancement | File | Change |
|---|-------------|------|--------|
| 1 | `three_phase_jd_detected` sentinel | `graph_selection_rationale.py` | Add `all_three_tracks_hit` check in `emit_graph_selection_rationale`; expose in returned dict |
| 4 | Phase 1 executive capability frames | `c03_graph_ref_policy.py` | Add `actuarial_risk`, `ccar_stress`, `derivatives_risk` to `EXECUTIVE_CAPABILITY_FRAMES` |
| 5 | Phase 1 JD keyword expansion | `graph_selection_rationale.py`, `track_weighted_graph_expansion.py` | Add stress testing, IFRS 17, Solvency II, model risk, quantitative risk, reserving, economic capital, embedded value |
| 6 | SEMANTIC_VARIANT_MAP expansions | `graph_skills_utilization_scorer.py` | Add Phase 1 variants (actuarial modeling, capital risk) and Phase 2 variants (enterprise data platform, cloud data) |
| 9 | Phase 2 JD keyword coverage | `graph_selection_rationale.py`, `track_weighted_graph_expansion.py` | Add watson, apptio, finops, solution engineering, cloud marketplace, ibm consulting |

### Definition of Done
- `extract_jd_keyword_hits()` returns hits for "stress testing", "IFRS 17", "Solvency II" test inputs
- `emit_graph_selection_rationale()` dict includes `three_phase_jd_detected: true` when all 3 tracks hit
- `EXECUTIVE_CAPABILITY_FRAMES` contains `actuarial_risk`, `ccar_stress`, `derivatives_risk` entries
- `SEMANTIC_VARIANT_MAP` has ≥3 Phase 1 and ≥2 Phase 2 variant entries
- No test regressions

---

## Wave 2 — Profile + Compression + Hybrid Boost

**Enhancements**: #2, #3, #7 from canvas analysis

### Scope

| # | Enhancement | File | Change |
|---|-------------|------|--------|
| 2 | `THREE_PHASE_GENERALIST` role family profile | `track_weighted_graph_expansion.py` | Add entry with balanced weights (0.27/0.38/0.35); add detection path in `infer_projection_role_family_key` |
| 3 | Phase-diversity pass in exec summary compression | `c03_graph_ref_policy.py` | When `three_phase_jd_detected=True` (signaled via `pillar_hints` check), guarantee ≥1 Phase 1 skill in kept set |
| 7 | Hybrid boost extended to narratives for three-phase JDs | `graph_skills_hybrid_boost.py` | Add `hybrid_sections_for_jd(three_phase: bool)` helper; update `HYBRID_SECTIONS_DEFAULT` for three-phase awareness |

### Definition of Done
- `ROLE_FAMILY_TRACK_WEIGHTS["THREE_PHASE_GENERALIST"]` weights within ±0.05 of equal across all three tracks
- `compress_binding_for_executive_summary` outputs at least one Phase 1 skill when P1 candidates in input skill set
- `HYBRID_SECTIONS_DEFAULT` remains `("executive_summary",)`; new `hybrid_sections_for_jd(True)` returns `executive_summary` + narratives
- No test regressions

---

## Deferred Scope

### DEFERRED_SCOPE: Wave 3 — X1D Rubric Career-Phase Diversity Marker
Adding `career_phase` marker group to `FAMILY_MARKER_GROUPS["executive_summary"]` requires Wave 1 sentinel to be stable across multiple production runs. Deferring to avoid rubric threshold regression before evidence accumulates.

### DEFERRED_SCOPE: Wave 4 — Cross-Section Career-Phase Floor Gate  
`cross_section_x2.py` phase-floor gate requires sentinel stable + Wave 2 profile proven clean on 3+ three-phase JD targets. High blast radius — gates the aggregation preflight.

---

## Immutable Constraints

- JD text remains targeting-only (`jd_used_as_proof=false`) — no relaxation
- `assert_hybrid_fact_ids_in_resolver_pool` / NEG-3 law: hybrid boost cannot widen the resolver pool
- No `pytest.mark.skip` without `strict=True`
- No bare `except Exception` without guardian tag
- `FORBIDDEN_RELAXATION_MARKERS` in X1D rubric contract: no threshold relaxation

---

## Files Changed

| File | Wave | Enhancement |
|------|------|-------------|
| [graph_selection_rationale.py](apps_rg/runtime/graph_selection_rationale.py) | 1 | #1, #5, #9 |
| [track_weighted_graph_expansion.py](apps_rg/fact_inventory/track_weighted_graph_expansion.py) | 1+2 | #5, #9, #2 |
| [c03_graph_ref_policy.py](apps_rg/runtime/c0/c03_graph_ref_policy.py) | 1+2 | #4, #3 |
| [graph_skills_utilization_scorer.py](apps_rg/runtime/graph_skills_utilization_scorer.py) | 1 | #6 |
| [graph_skills_hybrid_boost.py](apps_rg/runtime/graph_skills_hybrid_boost.py) | 2 | #7 |
