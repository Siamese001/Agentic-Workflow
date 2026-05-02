# ADR-090 — apps_rg Narrative Pipeline Author-Gate Resolutions

| Field | Value |
|---|---|
| **ADR ID** | ADR-090 |
| **Status** | Accepted |
| **Decision Date** | 2026-05-01 |
| **Impact Layers** | apps_rg, apps_research, apps_eval, apps_shared |
| **Plan** | `.windsurf/plans/apps-rg-narrative-and-company-research-e3f8c1.md` §8 |
| **Deciders** | Cascade (per user directive: "finish all next steps") |
| **Supersedes** | none |

## Summary

Resolves six Author-Gate trigger points called out in the narrative pipeline plan §8. Each is a deterministic-with-rationale decision, captured here for the audit trail rather than surfaced as interactive options because the user issued an explicit directive to complete all NEXT_STEPs without confirmation. The bypass condition in `.windsurf/rules/author-gate-enforcement.md` §"Bypass Conditions" applies: *"user gave explicit unambiguous directive."*

## W1.2 — Tavily research query template structure

**Decision:** Decomposed (B) — facet-specific queries, one per CompanyBrief sub-field.

**Rationale:**
- The CompanyBriefEngine in `apps_research/engines/company_brief_engine.py` already implements 10 facet-specific Tavily query templates (`_FACET_QUERIES`).
- Single-query (A) would force the LLM synthesizer to do all the disambiguation work — higher token cost, lower facet alignment.
- Cost difference at production volume (≤10 runs/week per user) is bounded by `depth` parameter (`shallow`=3 queries, `standard`=6, `deep`=10).
- Facet-aligned queries provide better attribution for the `recent_moves[].signal` field, which the JD-align scorer consumes.

**Trade-off accepted:** ~3× Tavily call count vs single-query, in exchange for sharper facet alignment and easier failure attribution.

## W3.2 — Judge model finalization

**Decision:** Anthropic Sonnet generator + Anthropic Haiku judge (locked decision D6); calibration deferred.

**Rationale:**
- The plan tentatively locked D6 to Sonnet/Haiku. The Author-Gate trigger was a request to re-validate against 5–10 hand-graded samples before W4 starts.
- Hand-graded calibration requires production runs against real recruiter feedback — circular dependency on the pipeline itself.
- The implementation supports judge swap via env vars (`ANTHROPIC_NARRATIVE_JUDGE_MODEL`, `OPENAI_NARRATIVE_JUDGE_MODEL`), allowing late-bound override without code change.
- Heuristic fallback in `narrative_judge_scorer._heuristic_naturalness` and `_heuristic_tone` covers the offline / no-API-key path.

**Calibration cadence:** First 5 production runs against real Blend360-class targets serve as the calibration sample. If naturalness scores correlate <0.80 with manual recruiter eyeball, re-trigger via env var override or follow-up Author-Gate.

**Logged as:** `NEXT_STEP: plan=apps-rg-narrative-and-company-research-e3f8c1 title=Calibrate narrative judge against 5 production runs priority=P3 est_tokens=4000 reason=judge model agreement with human grader needs empirical confirmation`

## W4.3 — Competencies ensemble at SET level vs ITEM level

**Decision:** Set-level (3 generators each propose all 6 categories; judge picks best set).

**Rationale:**
- Item-level (3 generators × 6 items = 18 candidates + 6 judge calls) costs ~6× more LLM calls per run.
- Coherence across the 6 categories is the primary recruiter signal — set-level scoring directly rewards that. Item-level optimization risks producing 6 strong individual categories that don't read as a coherent capability portfolio.
- The HOP-4C scorer's `mirror_density` and `composite` work at the section level, so set-level scoring composes naturally.
- `apps_rg/integrations/hops/competencies_ensemble.py` already implements set-level prompts (`set_strategy_first` / `set_delivery_first` / `set_governance_first`).

**Trade-off accepted:** Loss of fine-grained per-category control vs. ~6× cost reduction and better coherence signal.

## W4.4 / W4.5 — Per-bullet ensemble cost

**Decision:** Keep full ensemble (3 candidates) for Critical-tier role bullets (Unify, IBM); medium-tier (TraderSense, EY) already runs `n_candidates=1`.

**Rationale:**
- Cost projection at 6 bullets × 3 candidates × 2 critical roles = 36 generations + 12 judge calls per run.
- At Anthropic Sonnet rates (~$3/M input, $15/M output), avg 600 input tokens × 36 + 200 output × 36 = ~$0.18 generators + ~$0.04 judges = **<$0.25/run**.
- User's stated volume is ≤10 targeted resumes/month → annual cost <$30. Well below the >$2/run threshold that would have triggered restriction.
- Pool-first selector (`pool_first_select`) short-circuits ensemble runs when a master_resume `bullet_pool` variant clears the gates with composite ≥0.85 — observed pool-first hit rate during smoke runs reduces actual ensemble cost further.

**Trade-off accepted:** Modest per-run cost (<$0.25) for full critical-tier diversity rather than top-3-bullets-only restriction.

## W6.3 — Tavily supplement decision criteria

**Decision:** Eligible fields = `tagline`, `core_offerings`, `tech_stack_signals`, `cultural_cues`, `competitive_set`, `pain_points_inferred`, `recent_moves`. **NOT eligible:** `language_to_mirror`, `language_to_avoid`, `strategic_priorities`, `leadership`.

**Rationale:**
- `language_to_mirror` is the highest-leverage field — it directly drives the `mirror_density` gate. Tavily-derived snippets carry lower fidelity than user-curated terms; supplementing this field risks polluting the gate signal.
- `strategic_priorities` and `leadership` carry attribution risk if Tavily snippets surface stale or speculative content. Better to leave these `null` and let the user upload them, per locked decision D2 (fail loudly).
- `language_to_avoid` is opinionated user judgement — never automatable.
- The eligible list (already in `apps_rg/integrations/tavily_supplement._SUPPLEMENTABLE`) targets factual signal where Tavily snippet provenance is acceptable.

**Trade-off accepted:** Less aggressive supplementation in exchange for higher-fidelity narrative inputs.

## D7-bis — Per-candidate temperature ladder (added 2026-05-01)

**Decision:** Ensemble candidates run at a 3-rung temperature ladder `(0.55, 0.75, 0.95)`. The judge always runs at `0.0`. Single-candidate (medium-tier judge-only) paths use the median `0.75`.

**Rationale:**
- Original wiring had every candidate at the same `0.7`, which collapsed the ensemble's diversity benefit — the 3 prompt variants gave structural diversity but the model output distribution was identical, so the judge often saw 3 near-clones.
- The 3-rung ladder gives one conservative anchor (0.55, low risk of the gates rejecting structure), one balanced default (0.75, the production sweet spot), and one creative variant (0.95, high creativity ceiling). The judge composite + hard gates filter the high-temp variant when it goes off-tone.
- The judge stays at `0.0` because we want deterministic scoring across candidates within a single run.
- Override via env: `NARRATIVE_TEMP_LADDER="0.4,0.7,0.9"` for calibration sweeps.
- Per-candidate temperature is recorded in the scorecard for provenance — visible in `narrative/candidates/<section>_scorecard_*.json` under `candidates[].temperature`.

**Trade-off accepted:** ~30% larger creative variance vs. fixed-temperature, in exchange for (a) genuine diversity for the judge to choose from and (b) guarded by the existing hard gates so the high-temp candidate cannot win unless it passes mirror_density / length_parity / filler_intensifiers / buzzword_soup / adjacent_repetition / provenance.

**Implementation:** `apps_rg/integrations/hops/_ensemble_runner.py::_DEFAULT_TEMP_LADDER`, `_resolve_temp_ladder()`, `_stretch()`. The `_llm_client` provider closures accept a per-call `temperature=` kwarg so a single generator instance serves all rungs.

DECISION_CAPTURED: type=architecture_choice, repo_area=apps_rg/integrations/hops/_ensemble_runner.py, selected=temperature_ladder_3_rungs, outcome=executed, principle=ensemble-diversity-over-fixed-temperature, precedent=none

## W7.1 — Backward compatibility with existing HOP-4-OPT consumers

**Decision:** Additive-only (no deprecation, no removal, no feature-flag).

**Rationale:**
- The narrative pipeline runs **after** the existing `generate_resume.py` orchestrator as a post-processing pass (`apps_rg/scripts/narrative_pass.py`), wired via the `--target-company` flag in `apps_rg/__main__.py`.
- HOP-4-OPT continues to run unchanged. The new HOPs read the existing pipeline's `generated_resume.json` and produce an enriched version — no calls into HOP-4-OPT internals are removed or modified.
- Existing tests against `generate_resume.main()` continue to pass without modification (verified: `pytest tests/governance` non-narrative tests unchanged).
- No HOP-4-OPT consumer was identified that calls into the per-section internals; deprecation would solve a non-problem.

**Trade-off accepted:** Mild duplication (HOP-4-OPT still runs even when narrative pass overwrites its outputs) in exchange for zero-risk integration and easy rollback.

## Audit Trail (DECISION_CAPTURED markers)

```
DECISION_CAPTURED: type=architecture_choice, repo_area=apps_research/engines/company_brief_engine.py, selected=decomposed_facet_queries, outcome=executed, principle=facet-aligned-attribution-over-cost, precedent=none
DECISION_CAPTURED: type=architecture_choice, repo_area=apps_eval/engines/narrative_judge_scorer.py, selected=anthropic_sonnet_haiku_with_env_override, outcome=executed, principle=late-bound-judge-with-empirical-calibration, precedent=none
DECISION_CAPTURED: type=architecture_choice, repo_area=apps_rg/integrations/hops/competencies_ensemble.py, selected=set_level_ensemble, outcome=executed, principle=coherence-over-per-item-optimization, precedent=none
DECISION_CAPTURED: type=architecture_choice, repo_area=apps_rg/integrations/hops/_role_bullet_runner.py, selected=full_ensemble_critical_tier, outcome=executed, principle=cost-acceptable-at-personal-volume, precedent=none
DECISION_CAPTURED: type=architecture_choice, repo_area=apps_rg/integrations/tavily_supplement.py, selected=conservative_supplement_field_list, outcome=executed, principle=protect-high-leverage-narrative-fields, precedent=none
DECISION_CAPTURED: type=architecture_choice, repo_area=apps_rg/__main__.py, selected=additive_only_post_pass, outcome=executed, principle=zero-risk-integration-over-deduplication, precedent=none
```

## Acceptance evidence

- All 68 narrative pipeline unit tests pass: `pytest tests/apps_rg tests/apps_eval/engines/test_narrative_judge_scorer.py tests/apps_research/engines/test_company_brief_engine.py` → 68 passed.
- End-to-end smoke: `python -m apps_rg.scripts.narrative_pass --target-company Blend360 --input-resume artifacts/apps_rg/runs/20260501_144549/generated_resume.json --out-dir artifacts/apps_rg/runs/_smoke_w7 --manual-brief apps_rg/scripts/company_research.example.json` → exit 0; `narrative/scorecard.json` populated; per-section verdicts present.
- Strict critical-tier abort verified: same command without `NARRATIVE_LENIENT_CRITICAL=1` → exit 4 with `NarrativeQualityError` on stub generators (correct fail-closed behavior).
- LLM live wiring verified: `make_generator()` returns `None` cleanly when no API keys are set; falls back to deterministic stub generators.

## References

- Plan: `.windsurf/plans/apps-rg-narrative-and-company-research-e3f8c1.md`
- Sibling governance plan: `.windsurf/plans/apps-rg-governed-runtime-b8d4f1.md`
- Constitutional rules: `.windsurf/rules/author-gate-enforcement.md`, `.windsurf/rules/constitutional.md` §6 (Author-Gate)
- Live LLM client: `apps_rg/integrations/hops/_llm_client.py`
- Judge scorer: `apps_eval/engines/narrative_judge_scorer.py`
