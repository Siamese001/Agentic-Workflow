# apps_rg → Narrative + Company Research Architecture

**Slug:** `apps-rg-narrative-and-company-research-e3f8c1`
**Status:** Planned (not started)
**Owner:** TBD
**Created:** 2026-05-01
**Triggering audit:** Send-to-Blend360 readiness assessment on 2026-05-01 surfaced 10 HOP-quality gaps. Top three (no exec summary, JD-keyword undercoverage, generic phrasing) are blocking. The architectural design discussion that produced this plan ran in the same Cursor Agent conversation post-15:35 UTC-04:00.
**Author-Gate decision:** `architecture_choice` — locked through 7 sub-decisions captured below in §3.
**Bar to clear:** A single `python -m apps_rg --target-company <X>` invocation produces a recruiter-ready DOCX with: (a) executive summary aligned to a verified company brief, (b) headline aligned to JD + company language, (c) competencies/bullets respecting length parity (±15% of master_resume baseline) and anti-overfitting bounds (mirror density 8–18%, no buzzword soup), (d) all per-section gates pass strict OR pipeline aborts (critical-tier) or degrades with warning (medium-tier).

> **Self-reported token estimates** are sizing heuristics, not budget gates. 1M context window applies (per `.windsurf/rules/plan-location.md` history note).

---

## 1. Background

`python -m apps_rg` on 2026-05-01 (run `20260501_144549`) produced a structurally complete `generated_resume.json` (43 KB) with `final_quality_score: 1.0`, `ats_valid: true`, full provenance pass. **But it was not recruiter-ready** for the Blend360 SVP, Agentic Transformation role. The DOCX exporter (`apps_rg/outputs/docx_exporter.py`, landed alongside this plan) closes the formatting gap, but **content gaps remain in the HOP pipeline itself**:

1. **No Executive Summary section exists** — schema has zero `summary`/`headline`/`executive_summary` field. Top-of-page-1 narrative anchor is absent.
2. **JD keyword coverage = 24/40 hit, 16/40 miss.** "Consulting" appears 0 times in resume body despite being central to Blend360's identity.
3. **Generic phrasing slipped through HOP-4-OPT** ("leading AWS", "enabled measurable", "leading cloud and data platform providers").
4. **No company intelligence layer** — pipeline consumes JD only, not target-company strategic context. Bullets are JD-aligned but not company-aligned.
5. **No per-section length parity enforcement** — the LLM rewrites can drift from master_resume baselines, breaking ATS-friendly formatting.
6. **No anti-overfitting discipline** — current rubric rewards keyword density without bounds; modern ATS filters and human reviewers penalize keyword-stuffed copy.

This plan introduces:

- A **Company Intelligence Layer** as a peer to the JD intelligence layer, sourced via 4 input modes (manual upload, apps_research cross-app generation, internal invocation, Tavily supplement).
- **8 per-section HOPs** (4A–4H), each tiered by criticality with appropriate generation pattern (Ensemble+Judge / Judge-only / Deterministic).
- A **strengthened judge rubric** with 6 HARD gates (provenance, length parity, buzzword soup, mirror density bounds, adjacent-bullet repetition, filler intensifiers) + 4 SOFT dimensions (JD coverage, company coverage, tone, naturalness).
- **Pool-first selection** for per-bullet sections, falling through to LLM regeneration only when no `bullet_pool` variant clears the hard gates.
- **Tier-based fail-closed semantics** — critical-tier section failures abort pipeline; medium-tier failures degrade with `run_report.json` flag.

This plan does NOT touch governance plumbing (the apps_rg-governed-runtime-b8d4f1 plan covers that orthogonally). This plan is about **content quality**; b8d4f1 is about **runtime certification**. They can land independently and in either order.

---

## 2. The send-to-Blend360 acceptance flow (target end-state)

```
$ python -m apps_rg --target-company "Blend360" \
                    --research-via apps_research \
                    --jd apps_rg/scripts/job_description.json

[HOP-0.5-ARCHETYPE]   strategic_advisory  (matches Blend360 archetype)
[HOP-0.6-CO-RESEARCH] Loaded company brief from apps_research run abc123 ✓
[HOP-1]               Master resume loaded (5 roles, 23 source bullets)
[HOP-2.5-JD-FACETS]   24 JD facets extracted
[HOP-2.6-CO-FACETS]   17 company facets extracted from brief
[HOP-2.7-JD-ALIGN]    Bullet alignment computed (JD: 0.50, Co: 0.35, Lang: 0.15)
[HOP-3-K9]            Quantification verified (19/23 bullets carry $/% metrics)

[HOP-4A-HEADLINE]     Ensemble (3) + Judge → ACCEPT  (winner: candidate-B, score 0.91)
[HOP-4B-EXEC-SUMMARY] Ensemble (3) + Judge → ACCEPT  (winner: candidate-A, score 0.88)
[HOP-4C-COMPETENCIES] Ensemble (3) + Judge → ACCEPT  (winner: set-2, score 0.86)
[HOP-4D-UNIFY]        6 bullets, Ensemble+Judge per-bullet → 5 ACCEPT, 1 REGEN→ACCEPT
[HOP-4E-IBM]          6 bullets, Ensemble+Judge per-bullet → 6 ACCEPT
[HOP-4F-TRADERSENSE]  4 bullets, Pool-first (3 hits) + Judge → ACCEPT
[HOP-4G-EY]           4 bullets, Pool-first (3 hits) + Judge → ACCEPT
[HOP-4H-EARLY-CAREER] Deterministic compress to 1 line ("Earlier Career: 2002-2009 — Actuarial & Quantitative roles")

[HOP-4.5-DIVERSITY]   No adjacent-bullet duplicates ✓
[HOP-4-RANK]          Bullets reranked by alignment within each role
[HOP-4.7-MARQUEE]     3 selected outcomes pulled to top callout
[HOP-5-ATS]           ATS-valid ✓

→ Wrote artifacts/apps_rg/runs/20260502_103000/
    ├── generated_resume.json
    ├── Amit_Ayer_Resume_Blend360_SVP_Agentic_Transformation.docx
    ├── company_research.json (provenance copy)
    ├── narrative/
    │   ├── candidates/
    │   │   ├── headline_a.json, headline_b.json, headline_c.json
    │   │   ├── exec_summary_a.json, ..._b.json, ..._c.json
    │   │   └── competencies_set1.json, ..._set2.json, ..._set3.json
    │   └── scorecard.json (judge scores for all candidates, all sections)
    └── run_report.json (now includes per-section gate verdicts)
```

If `HOP-0.6-CO-RESEARCH` finds no brief: pipeline raises `CompanyBriefMissingError` and exits non-zero. **No JD-only fallback.** Default behavior with no flags = fail.

---

## 3. Locked Architectural Decisions

| # | Decision | Locked Value | Source |
|---|---|---|---|
| D1 | Input modes for company brief | Mode 1: manual upload at `apps_rg/scripts/company_research.json`. Mode 2: apps_research generates via `--mode company`. Mode 3: cross-app invocation via `apps_rg --research-via apps_research`. Mode 4: Tavily supplement only (fills `null` + stale fields, never produces from scratch). | User decision 2026-05-01 §1+§2 |
| D2 | Behavior with no brief | **Fail loudly** — `CompanyBriefMissingError`, no JD-only fallback | User decision 2026-05-01 §1 |
| D3 | Tavily auto-fetch | **Opt-in** via `--auto-research-tavily`, supplements existing brief; never produces from scratch | User decision 2026-05-01 §2 |
| D4 | Tavily supplement scope | Refresh fields where `value is null` OR `fetched_at` older than `freshness_ttl_days` | Cursor Agent recommendation (1c), accepted by silence-as-confirmation in user §1+§2 lock |
| D5 | Cross-app composition trigger | **Explicit** — must pass `--research-via apps_research`. No surprise auto-invocation. | Cursor Agent recommendation (2b), accepted by user "fine with above" |
| D6 | Judge model diversity | Same provider, different model — **Anthropic Sonnet generator + Anthropic Haiku judge** (single auth, solid diversity, cheaper than cross-provider) | Cursor Agent recommendation (3a), accepted by user "fine with above" |
| D7 | Generation pattern per section | Ensemble+Judge for Critical (Headline, Exec Summary, Competencies, Unify, IBM); Judge-only for Medium (TraderSense, EY); Deterministic for Skip (Early Career) | User decision 2026-05-01 §"most critical are exec summary, headline, unify, competencies, IBM, all other" |
| D8 | Per-section fail-closed | **Tier-based** — Critical-tier section failure aborts pipeline; Medium-tier failure degrades with `run_report.json` flag | Cursor Agent recommendation (c), accepted by user "fine with above" |
| D9 | Length parity | HARD gate, ±15% tolerance per bullet/section vs `master_resume.json` baseline. Headline 10–14 words, Exec Summary 80–120 words across 3–4 sentences. | User decision 2026-05-01 |
| D10 | Anti-overfitting | HARD gates: mirror density 8%–18%, max 3 buzzwords from list per bullet, no adjacent-bullet keyword repetition | User decision 2026-05-01 |
| D11 | Pool-first selection | For per-bullet sections, try `bullet_pool` variants first; fall through to LLM only when no pool variant clears hard gates with composite ≥ 0.85 | Cursor Agent recommendation, follows naturally from D9 |
| D12 | Always surface 3 candidates | Write all ensemble candidates to `narrative/candidates/` for human override; default = judge's pick | Cursor Agent recommendation (a), accepted by user "fine with above" |

---

## 4. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|------------:|-------------|--------|------------------|
| W1 — apps_research `company` mode | 1.1, 1.2, 1.3 | Add `--mode company` to apps_research; build `CompanyBriefEngine`; emit governed `company_research.json` | ~25k | apps_research's existing `BaseResearchEngine` + `governed_research_run.py` accept a new mode without architectural rework; Tavily MCP available for primary research | Planned | `python -m apps_research --topic "Blend360" --mode company --jd-anchor <path>` produces a schema-valid `company_research.json` under `artifacts/apps_research/runs/<ts>/`; round-trips against `apps_rg/schemas/company_research.schema.json` |
| W2 — apps_rg input layer | 2.1, 2.2, 2.3, 2.4 | HOP-0.6-COMPANY-RESEARCH (4-mode loader); HOP-2.6-COMPANY-FACETS extractor; cross-app facade in `apps_shared`; `CompanyBriefMissingError` fail-loud gate | ~22k | apps_shared/adapters/ pattern is clean to extend; schema validation library (pydantic) handles freshness checks | Planned | `python -m apps_rg` with no flags AND no brief on disk raises `CompanyBriefMissingError` non-zero; with `--research-via apps_research --target-company <X>` invokes apps_research and consumes its output; with manual brief on disk loads it; with `--auto-research-tavily` supplements `null`/stale fields |
| W3 — Judge rubric + length budgets | 3.1, 3.2, 3.3 | New rubric `apps_eval/config/rubrics/narrative_judge.yaml`; length-budget extractor that reads `master_resume.json`; rubric scorer with 6 HARD gates + 4 SOFT dimensions | ~20k | `apps_eval/engines/llm_judge_engine.py` accepts new rubric; pydantic schema for `LengthBudget` is straightforward | Planned | Rubric loads cleanly; HARD gate failures produce `RubricHardGateFailure` with cited dimension; SOFT composite is computed correctly; length budgets match master_resume per-bullet word counts ±15% |
| W4 — Critical-tier per-section HOPs | 4.1, 4.2, 4.3, 4.4, 4.5 | HOP-4A Headline, HOP-4B Exec Summary, HOP-4C Competencies, HOP-4D Unify bullets, HOP-4E IBM bullets — all Ensemble+Judge with 3 prompt variations | ~50k | Anthropic API supports parallel calls via httpx async; SovereignLLMGateway can dispatch 3 concurrent generations per HOP without rate-limit issues at single-user scale | Planned | Each Critical HOP produces 3 candidates + 1 judge scorecard per run; winner shipped, runners-up archived to `narrative/candidates/`; on critical-tier judge fail-closed, pipeline aborts with `NarrativeQualityError` |
| W5 — Medium-tier per-section HOPs + pool-first | 5.1, 5.2, 5.3 | HOP-4F TraderSense, HOP-4G EY (Judge-only); pool-first selector that tries `bullet_pool` variants before LLM regen | ~25k | `bullet_pool` is well-formed in master_resume.json (verified via current run output); pool variants typically have 2–4 phrasings per slot | Planned | Medium HOPs produce 1 candidate + 1 judge scorecard; pool-first hits ≥40% on TraderSense+EY (8 bullets total → ≥3 pool hits expected); on medium-tier judge fail-closed, section degrades with `run_report.json` flag, pipeline continues |
| W6 — Deterministic Early-Career + Marquee + Tavily Supplement | 6.1, 6.2, 6.3 | HOP-4H Early Career (1-line deterministic); HOP-4.7-MARQUEE selected outcomes callout; Tavily supplement adapter | ~18k | `master_resume.json` has chronology metadata sufficient for 1-line compression; Tavily MCP serialization (constitutional §25) doesn't bottleneck since this is a non-critical-path supplement | Planned | Early Career compresses to deterministic 1-liner; Marquee section pulls top 3–4 quantified bullets across all roles; Tavily supplement fills null/stale fields with provenance trail; supplement is fail-soft (never aborts pipeline) |
| W7 — Wiring + DOCX integration + Acceptance | 7.1, 7.2, 7.3, 7.4 | Wire all 8 per-section HOPs into `generate_resume.py` orchestrator; update DOCX exporter to render headline + exec summary; update `run_report.json` schema; acceptance run against Blend360 JD | ~15k | All upstream waves complete; existing pipeline orchestrator accepts new HOP registration without architectural surgery | Planned | `python -m apps_rg --target-company "Blend360"` produces FULLY-targeted DOCX with all 8 sections; run_report shows per-section gate verdicts; manual eyeball of Blend360 DOCX shows it would not be filtered as keyword-stuffed |

**Total estimated scope:** ~175k tokens, ~3500–5000 LoC, ~20–30 files touched, ~6–9 working sessions.

---

## 5. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---:|---|
| P1.1 | Define `CompanyBrief` Pydantic schema + JSON Schema export | `apps_rg/schemas/company_research.schema.json` (NEW); `apps_rg/types/company_research.py` (NEW) | Schema must capture overview/strategic_priorities/customer_profile/tech_stack/cultural_cues/leadership/competitive_set/pain_points/recent_moves/language_to_mirror/language_to_avoid; freshness_ttl_days field | ~6k | Planned |
| P1.2 | Build `CompanyBriefEngine` for apps_research `company` mode | `apps_research/engines/company_brief_engine.py` (NEW); `apps_research/config/specs/company_mode.yaml` (NEW) | Tavily research query templating; cross-reference Tavily extract on official site + LinkedIn; JD-anchor weighting logic | ~12k | Planned |
| P1.3 | Wire `company` mode into `governed_research_run.py` + ingress | `apps_research/integrations/governed_research_run.py` (modify); `apps_research/integrations/research_ingress_runner.py` (modify); `apps_research/__main__.py` (modify CLI) | Existing 4 modes (`brief`, `comparison`, `trend`, `position`) are factory-dispatched; need 5th branch without breaking existing tests | ~7k | Planned |
| P2.1 | HOP-0.6-COMPANY-RESEARCH 4-mode loader | `apps_rg/integrations/company_research_loader.py` (NEW) | Mode priority logic; cross-app invocation via apps_shared facade; freshness validation; `CompanyBriefMissingError` semantics | ~8k | Planned |
| P2.2 | Cross-app facade for apps_research invocation | `apps_shared/adapters/research_facade.py` (NEW or modify) | Sync wait for apps_research run completion; route artifact path back; error propagation | ~4k | Planned |
| P2.3 | HOP-2.6-COMPANY-FACETS extractor | `apps_rg/integrations/company_facet_extractor.py` (NEW) | Extract facet vectors (verticals, buyer_archetypes, tech_stack, engagement_model, ownership_signal, differentiation); produce alignment_weights | ~6k | Planned |
| P2.4 | Modify HOP-2.7-JD-ALIGN to consume company facets | `apps_rg/integrations/jd_align.py` (modify) | New scoring formula `w_jd × jd_match + w_co × co_match + w_lang × lang_score` with default weights 0.50/0.35/0.15; backwards compatibility with existing tests that mock JD-only | ~4k | Planned |
| P3.1 | Length budget extractor | `apps_rg/integrations/length_budget.py` (NEW) | Read `master_resume.json` per-role per-bullet word counts; emit per-bullet budget with ±15% tolerance; per-section budget for non-bullet sections (headline, exec summary, competencies) | ~5k | Planned |
| P3.2 | Judge rubric + scorer | `apps_eval/config/rubrics/narrative_judge.yaml` (NEW); `apps_eval/engines/narrative_judge_scorer.py` (NEW or extend existing) | 6 HARD gates evaluated in order; SOFT composite weighting; rubric calibration sample for human-vs-judge agreement (per `judge-calibration-cadence.md`) | ~10k | Planned |
| P3.3 | Anti-overfitting detector module | `apps_rg/integrations/anti_overfitting.py` (NEW) | Mirror density calculation; buzzword soup detector with configurable list; adjacent-bullet repetition check | ~5k | Planned |
| P4.1 | HOP-4A-HEADLINE Ensemble+Judge | `apps_rg/integrations/hops/headline_ensemble.py` (NEW) | 3 prompt variations (lead-with-archetype/marquee/pain-point); 12-word target; aggressive filler-intensifier filter | ~10k | Planned |
| P4.2 | HOP-4B-EXEC-SUMMARY Ensemble+Judge | `apps_rg/integrations/hops/exec_summary_ensemble.py` (NEW) | 3 prompt variations with structural diversity; 80–120 word budget; 3–4 sentence count enforcement; provenance traces every claim | ~12k | Planned |
| P4.3 | HOP-4C-COMPETENCIES Ensemble+Judge (set-level) | `apps_rg/integrations/hops/competencies_ensemble.py` (NEW) | Set-level scoring (coherent 6 categories, no overlap, JD+company language coverage); category-name mirroring company terminology | ~10k | Planned |
| P4.4 | HOP-4D-UNIFY Per-Bullet Ensemble+Judge | `apps_rg/integrations/hops/unify_ensemble.py` (NEW) | Per-bullet ensemble for 6 Unify bullets; pool-first attempt before LLM regen; per-bullet length parity ±15% of source | ~10k | Planned |
| P4.5 | HOP-4E-IBM Per-Bullet Ensemble+Judge | `apps_rg/integrations/hops/ibm_ensemble.py` (NEW) | Mirror Unify pattern with role-specific JD-emphasis (scale, financial services, regulatory) | ~8k | Planned |
| P5.1 | Pool-first selector primitive | `apps_rg/integrations/pool_first_selector.py` (NEW) | For each bullet slot: filter pool by length + hard gates → score remaining → return top if composite ≥ 0.85 else None | ~6k | Planned |
| P5.2 | HOP-4F-TRADERSENSE Judge-only | `apps_rg/integrations/hops/tradersense_judge.py` (NEW) | Pool-first → fall-through to single-LLM regen + judge; chronology compression hint in prompt | ~5k | Planned |
| P5.3 | HOP-4G-EY Judge-only | `apps_rg/integrations/hops/ey_judge.py` (NEW) | Mirror TraderSense pattern with role-specific framing (regulatory advisory, model validation) | ~5k | Planned |
| P6.1 | HOP-4H-EARLY-CAREER deterministic | `apps_rg/integrations/hops/early_career_compress.py` (NEW) | Pure template fill from chronology metadata; no LLM; output exactly 1 line ≤25 words | ~3k | Planned |
| P6.2 | HOP-4.7-MARQUEE selected outcomes | `apps_rg/integrations/hops/marquee.py` (NEW) | Pull top 3–4 quantified bullets across all roles; format as section above Professional Experience; deduplicate against bullet content | ~6k | Planned |
| P6.3 | Tavily supplement adapter | `apps_rg/integrations/tavily_supplement.py` (NEW) | Identify null + stale fields; targeted Tavily research per field; provenance log; fail-soft (never aborts) | ~6k | Planned |
| P7.1 | Wire 8 per-section HOPs into orchestrator | `apps_rg/scripts/generate_resume.py` (modify) | Replace existing HOP-4-OPT bulk-rewrite with section-tier dispatch; preserve existing HOP-3-K9, HOP-4.5-DIVERSITY, HOP-4-RANK, HOP-5-ATS | ~6k | Planned |
| P7.2 | Update DOCX exporter for headline + exec summary | `apps_rg/outputs/docx_exporter.py` (modify) | New top-of-resume sections; preserve existing layout; honor `headline` + `executive_summary` fields if present | ~3k | Planned |
| P7.3 | Update `run_report.json` schema | `apps_rg/types/run_report.py` (NEW or modify) | Add `per_section_verdicts`, `gate_failures`, `degraded_sections`, `narrative_candidates_path` | ~3k | Planned |
| P7.4 | Acceptance run + governance test removal | tests + verification commit | Run apps_rg against Blend360; manual eyeball of DOCX; remove xfail markers from any tests in apps-rg-governed-runtime-b8d4f1 that this plan unblocks (separate plan but acceptance test belongs here) | ~3k | Planned |

---

## 6. Cross-App Contract — apps_research `company` mode

### 6.1 New mode declaration

```yaml
# apps_research/config/specs/company_mode.yaml (NEW)
mode: company
description: |
  Company intelligence research producing a structured CompanyBrief
  conforming to apps_rg/schemas/company_research.schema.json. Used
  by apps_rg HOP-0.6-COMPANY-RESEARCH for narrative generation.
required_inputs:
  - topic: str            # Company name (e.g., "Blend360")
optional_inputs:
  - jd_anchor: Path       # Path to job_description.json for facet weighting
  - depth: str            # "shallow" | "standard" | "deep" (default: standard)
output_schema: apps_rg/schemas/company_research.schema.json
governance:
  inherits: governed_research_run
  emit_artifacts:
    - route_contract
    - final_evidence_contract
    - sealed_l2_artifact
    - exit_review_packet
```

### 6.2 CompanyBrief schema (full)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "CompanyBrief",
  "type": "object",
  "required": ["company", "fetched_at", "source", "freshness_ttl_days", "overview", "strategic_priorities", "customer_profile", "language_to_mirror"],
  "properties": {
    "company": {"type": "string"},
    "fetched_at": {"type": "string", "format": "date-time"},
    "source": {"enum": ["user_uploaded", "tavily_research", "apps_research", "manual"]},
    "freshness_ttl_days": {"type": "integer", "default": 30},
    "overview": {
      "type": "object",
      "required": ["tagline", "core_offerings"],
      "properties": {
        "tagline": {"type": "string"},
        "founded": {"type": "integer"},
        "size_band": {"type": "string"},
        "ownership": {"type": "string"},
        "headquarters": {"type": "string"},
        "core_offerings": {"type": "array", "items": {"type": "string"}}
      }
    },
    "strategic_priorities": {"type": "array", "items": {"type": "string"}, "minItems": 2},
    "customer_profile": {
      "type": "object",
      "properties": {
        "verticals": {"type": "array", "items": {"type": "string"}},
        "buyer_titles": {"type": "array", "items": {"type": "string"}},
        "typical_engagement_size": {"type": "string"}
      }
    },
    "tech_stack_signals": {"type": "array", "items": {"type": "string"}},
    "cultural_cues": {"type": "array", "items": {"type": "string"}},
    "leadership": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": {"type": "string"},
          "title": {"type": "string"},
          "background": {"type": "string"}
        }
      }
    },
    "competitive_set": {"type": "array", "items": {"type": "string"}},
    "pain_points_inferred": {"type": "array", "items": {"type": "string"}},
    "recent_moves": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "date": {"type": "string"},
          "event": {"type": "string"},
          "signal": {"type": "string"}
        }
      }
    },
    "language_to_mirror": {"type": "array", "items": {"type": "string"}, "minItems": 3},
    "language_to_avoid": {"type": "array", "items": {"type": "string"}}
  }
}
```

### 6.3 Cross-app facade signature

```python
# apps_shared/adapters/research_facade.py (NEW)
from pathlib import Path
from apps_research.integrations.governed_research_run import GovernedResearchRun
from apps_rg.types.company_research import CompanyBrief

def fetch_company_brief(
    *,
    company: str,
    jd_path: Path | None = None,
    depth: str = "standard",
    cache_max_age_days: int = 30,
) -> CompanyBrief:
    """Synchronous invocation of apps_research --mode company.

    Returns a validated CompanyBrief or raises CompanyBriefMissingError.
    Honors cache: returns existing artifact under
    artifacts/apps_research/runs/<ts>/company_research.json
    if found and within cache_max_age_days.
    """
    ...
```

---

## 7. Judge Rubric — `apps_eval/config/rubrics/narrative_judge.yaml`

```yaml
rubric_id: narrative_judge_v1
applies_to:
  - hop_4a_headline
  - hop_4b_exec_summary
  - hop_4c_competencies
  - hop_4d_unify
  - hop_4e_ibm
  - hop_4f_tradersense
  - hop_4g_ey

hard_gates:
  - gate_id: provenance
    description: Every factual claim traces to master_resume.json
    failure_mode: instant_reject
  - gate_id: length_parity
    description: Word count within budget ±15% (per-bullet) OR within section budget
    failure_mode: instant_reject
  - gate_id: buzzword_soup
    description: At most 3 buzzwords from configured list per bullet
    failure_mode: instant_reject
    config:
      buzzwords: [AI, transformation, agentic, enterprise, Fortune, strategic, C-suite, cloud, digital, innovation]
      max_count: 3
  - gate_id: mirror_density
    description: Combined JD+company mirror term density between 8% and 18%
    failure_mode: instant_reject
    config:
      min: 0.08
      max: 0.18
  - gate_id: adjacent_repetition
    description: No two consecutive bullets in the same role lead with the same mirror term
    failure_mode: instant_reject
  - gate_id: filler_intensifiers
    description: No instances of forbidden filler words/phrases
    failure_mode: instant_reject
    config:
      forbidden: [leading, world-class, cutting-edge, mission-critical, next-generation, best-in-class, leverage, synergy, enabled, unified, robust, comprehensive, holistic]

soft_dimensions:
  - dimension_id: jd_facet_coverage
    weight: 0.25
    min_score: 0.60
  - dimension_id: company_facet_coverage
    weight: 0.20
    min_score: 0.50
  - dimension_id: tone_executive_register
    weight: 0.20
    min_score: 0.80
    judge_prompt: |
      Score 0.0–1.0 on whether this reads as prose written by a senior
      executive describing past work. Penalize: corporate-speak, jargon
      without substance, breathless framing, ATS-bait phrasing.
  - dimension_id: naturalness
    weight: 0.35
    min_score: 0.80
    judge_prompt: |
      Score 0.0–1.0 on whether a human reader would NOT detect this as
      AI-generated or auto-targeted. Penalize: keyword stuffing,
      template-rigid structure, verbatim JD language.

composite_threshold: 0.85
```

---

## 8. Author-Gate Trigger Points

Each is an `architecture_choice` decision that must surface an Author-Gate packet before the implementing developer proceeds:

1. **W1.2 — Tavily research query template structure.** Two paths: (A) one big "research this company" query; (B) decomposed 5–7 facet-specific queries (one per CompanyBrief sub-field). Trade-offs: (A) lower cost, lower precision; (B) higher cost, sharper facet alignment. Author-Gate.
2. **W3.2 — Judge model finalization.** Locked tentatively as Anthropic Sonnet generator + Haiku judge (D6). But before W4 starts, calibrate against 5–10 hand-graded samples to confirm Haiku scores correlate ≥0.80 with human grader. If not, escalate to Sonnet judge or cross-provider GPT-4o-mini.
3. **W4.3 — Competencies ensemble at SET level vs ITEM level.** Tentative: set-level (3 generators each propose all 6 categories; judge picks best set). Alternative: item-level (3 generators per item, 18 total candidates). Author-Gate before P4.3 starts.
4. **W4.4/W4.5 — Per-bullet ensemble cost.** 6 bullets × 3 candidates × 2 roles = 36 generations + 12 judge calls per run. If cost exceeds projection (>$2/run), Author-Gate to decide: keep ensemble for top-3 ranked bullets only OR keep full ensemble.
5. **W6.3 — Tavily supplement decision criteria.** Which fields are eligible for supplement; should `language_to_mirror` ever be supplemented (it's high-leverage but Tavily-derived may be lower fidelity than user-uploaded). Author-Gate.
6. **W7.1 — Backward compatibility with existing HOP-4-OPT consumers.** Existing tests/runs may call HOP-4-OPT directly. Author-Gate to decide: deprecation path vs hard removal vs feature-flag.

---

## 9. Acceptance Gate

After P7.4 completes:

### 9.1 Functional acceptance

- `python -m apps_rg --target-company "Blend360" --research-via apps_research` runs end-to-end and produces all 8 sections.
- `python -m apps_rg` with no flags AND no brief on disk fails with `CompanyBriefMissingError` and non-zero exit.
- Generated DOCX contains: headline, executive summary, competencies (6 items), professional experience (Unify, IBM, TraderSense, EY), Earlier Career one-liner, education, certifications.
- All sections respect length parity ±15%.
- Mirror density on every bullet falls within [8%, 18%].
- Zero filler intensifiers in the final output (verified by post-hoc scan).
- JD keyword coverage improves to ≥34/40 (vs 24/40 baseline).
- "consulting" appears at least 3 times in the resume body for Blend360 target.

### 9.2 Quality acceptance (manual eyeball)

- A human reader scanning the top 8 lines understands the candidate's positioning thesis.
- No bullet reads as ATS-stuffed (per anti-overfitting gate; verified visually).
- Tone is consistent across sections (no LLM voice drift).
- Runner-up candidates for headline/exec summary/competencies are inspectable in `narrative/candidates/`.

### 9.3 Governance acceptance (separate plan)

- This plan does NOT certify the run as `FULLY_PROVEN` per the audit standard. That work belongs to `apps-rg-governed-runtime-b8d4f1.md`. Both can land independently; both must land for FULLY_PROVEN.

---

## 10. Gap Register

| ID | Item | Severity | Note |
|---|---|:---:|---|
| G1 | apps_research's existing 4 modes may have implicit assumptions broken by adding mode 5 | Medium | W1.3 must verify all existing modes still pass tests after factory-dispatch extension |
| G2 | `master_resume.json` may have insufficient `bullet_pool` variants for some slots | Medium | Pool-first selector falls through to LLM regen gracefully, but if pool is sparse, costs rise. Mitigate by measuring pool-hit rate during W5.1 calibration |
| G3 | Anthropic Haiku may not have sufficient discriminating power for naturalness rubric | High | Author-Gate at W3.2 with calibration sample |
| G4 | Tavily research depth is non-deterministic; supplement may produce different fields across runs | Medium | Mitigate via `freshness_ttl_days` and explicit field-level cache; accept that supplement is fail-soft and best-effort |
| G5 | InsurTech vs TraderSense naming inconsistency surfaced by user 2026-05-01 §"InsurTech" | Low | Schema says TraderSense; user may have meant a different role. Verify against `master_resume.json` early in W4.4 (Unify) since IBM is positioned correctly already. May require master_resume.json update. |
| G6 | Cross-app facade adds dependency from apps_rg → apps_research that didn't exist before | Medium | apps_shared/adapters/ pattern is the right place; verify no circular dependency emerges during W2.2 |
| G7 | `judge-calibration-cadence.md` rule mandates periodic human calibration | Low | For personal use, "spot-check N runs" is sufficient; for team/multi-user, formal calibration log needed (out of scope for this plan) |
| G8 | Constitutional §29 (closed-loop router enforcement) does not directly apply but may be relevant if HOP-4.x ensemble selection is treated as a "router decision" | Low | Author-Gate at W4.1 to decide whether to emit `ROUTER_DECISION` markers for ensemble selections (would tie into existing intelligence-ledger family pattern) |

---

## 11. Companion Artifacts

### Schemas
- `apps_rg/schemas/company_research.schema.json`
- `apps_rg/schemas/length_budget.schema.json` (NEW, derived from master_resume per-bullet word counts)

### New modules (apps_rg)
- `apps_rg/integrations/company_research_loader.py`
- `apps_rg/integrations/company_facet_extractor.py`
- `apps_rg/integrations/length_budget.py`
- `apps_rg/integrations/anti_overfitting.py`
- `apps_rg/integrations/pool_first_selector.py`
- `apps_rg/integrations/tavily_supplement.py`
- `apps_rg/integrations/hops/headline_ensemble.py`
- `apps_rg/integrations/hops/exec_summary_ensemble.py`
- `apps_rg/integrations/hops/competencies_ensemble.py`
- `apps_rg/integrations/hops/unify_ensemble.py`
- `apps_rg/integrations/hops/ibm_ensemble.py`
- `apps_rg/integrations/hops/tradersense_judge.py`
- `apps_rg/integrations/hops/ey_judge.py`
- `apps_rg/integrations/hops/early_career_compress.py`
- `apps_rg/integrations/hops/marquee.py`
- `apps_rg/types/company_research.py`
- `apps_rg/types/run_report.py`

### New modules (apps_research)
- `apps_research/engines/company_brief_engine.py`
- `apps_research/config/specs/company_mode.yaml`

### New modules (apps_eval)
- `apps_eval/config/rubrics/narrative_judge.yaml`
- `apps_eval/engines/narrative_judge_scorer.py` (or extend existing `llm_judge_engine.py`)

### New modules (apps_shared)
- `apps_shared/adapters/research_facade.py`

### Modified files
- `apps_research/integrations/governed_research_run.py`
- `apps_research/integrations/research_ingress_runner.py`
- `apps_research/__main__.py`
- `apps_rg/scripts/generate_resume.py`
- `apps_rg/outputs/docx_exporter.py`

### Tests (mirroring module structure under tests/)
- `tests/apps_rg/integrations/test_company_research_loader.py`
- `tests/apps_rg/integrations/test_anti_overfitting.py`
- `tests/apps_rg/integrations/test_length_budget.py`
- `tests/apps_rg/integrations/hops/test_headline_ensemble.py` … (one per HOP)
- `tests/apps_research/engines/test_company_brief_engine.py`
- `tests/apps_eval/engines/test_narrative_judge_scorer.py`
- `tests/integration/test_apps_rg_blend360_acceptance.py` (W7.4 acceptance run)

---

## 12. What this plan does NOT do

- **Does NOT close the governance gap** — that's `apps-rg-governed-runtime-b8d4f1.md`. The two plans are orthogonal and can land in either order.
- **Does NOT introduce ensemble for HOP-4-OPT** generally — ensemble is scoped to HOP-4A through HOP-4E only. Future work that wants ensemble elsewhere requires a new Author-Gate.
- **Does NOT fix `Early Career Roles` rendering as a fake company** — per user direction (2026-05-01 §"ignore early career"), this is collapsed to a deterministic 1-liner; the underlying schema bug remains for future cleanup.
- **Does NOT add a cover-letter HOP** — out of scope; tracked separately as item #10 from the 2026-05-01 send-readiness assessment.
- **Does NOT change the existing R3 governed-runtime path** — runtime certification work remains in b8d4f1.
- **Does NOT alter the DOCX exporter's structural layout** beyond adding headline + exec summary fields (it already handles the rest of the schema).

---

## 13. RTC-REQ Cross-References (for future cert matrix alignment)

Per the runtime_certification_requirements_100_percent_hardened.csv discussion 2026-05-01 §"convert structured data to word document":

This plan does not directly satisfy any RTC-REQ — those are governance receipts, not content quality. However, the per-section gate verdicts and `narrative/candidates/` archive provide the audit trail that future certification work (if applied to this content path) would consume. Specifically:

- `narrative/scorecard.json` could become input to a future `narrative_certification_receipt` (analogous to `x3_disposition_receipt.json` in the runtime cert path).
- The per-section gate fail-closed behavior aligns with RTC-REQ-011 ("proof harnesses MUST NOT stamp/synthesize artifacts") — every gate verdict is produced by the actual judge run, not stamped post-hoc.

Cross-reference is informational; this plan does not block on, nor commit to, RTC-REQ alignment.
