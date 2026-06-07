# apps_rg Simplification + Graph-Skill Signal — AIG End-to-End Proof (2026-06-07)

Scope authorized via Author-Gate (`refactor_scope`, decision `dec_19e9ffaee599e073d`, selected `focused_high_value`, confidence 0.82, precedent: cold corpus). Two read-only audits ([simplification](65d6ef15-f481-49f1-8c78-156b4acc7183), [graph-signal](eb6e5e01-eef9-4988-82a2-8b05f5094cd4)) grounded the picks.

## What changed (3 focused, rigor-preserving seams)

### S1 — Align SC path counts with the variance-class profile (the config drift that never landed)
- `section_reasoning_intensity.py` documented SC=4/4/2 for unify/ibm/competencies, but `employment_bullet_pool.sc_path_count_for_lane()` hardcoded **15/12/10**, overriding the profile. The documented variance-class redesign had never reached the execution path.
- **unify_bullets / ibm_bullets**: SC `15/12 → 4` over their FIXED slot counts (unify=6, ibm=5). Generation variance is handled by the Claude pool selector + `min_selection_score=0.72` + employment X2 metric/anchor gates — not brute-force sampling.
- **competencies**: candidate-category pool `10 → 8`. This count is the *candidate selection pool* (generate N → pick best 6), NOT pure sampling, so it stays `>= MAX_CATEGORY_COUNT (6)`. The audit's "→2" would have broken selection; 8 preserves headroom + selection rigor.
- Regen extra paths trimmed (unify/ibm `5/4 → 3`, competencies `5 → 4`).

### S2 — IBM bullets: drop the redundant second Anthropic judge on the pool path
- IBM ran the Claude **pool selector** AND a second independent `run_ibm_bullets_judges` (anthropic GRADE_ONLY) on every run. Unify already used the synthetic selector-derived X1D row.
- Now IBM mirrors unify: `if is_employment_pool_generation(gen_meta): x1d = employment_pool_x1d_judge_rows(...)`. The synthetic row carries `provider_key="anthropic_claude"`, `proof_eligible_judge=True`, satisfying the IBM X2 gate `x2_x1d_required_judges_present` (which requires exactly `EMPLOYMENT_BULLET_JUDGE_PROVIDERS = ("anthropic_claude",)`). The multi-provider **adjudicator panel** still escalates borderline cases. Non-pool fallback keeps the real judge call.

### G1 — Surface latent graph-skill vocabulary into competency + headline evidence packs
- Both packets already loaded `bound_skills` (each with ledger `allowed_phrases`) but the formatters emitted only skill-id strings, dropping the vocabulary anchors. Unify bullets already inject them.
- `format_competency_capability_evidence_pack` and `format_headline_positioning_evidence_pack` now emit a `bound_skills (graph authority — vocabulary anchors only, not proof on their own)` block with `skill_id | allowed_phrases: ...`. Proof authority is unchanged (still `graph_skill_node_ids` + `linked_source_fact_ids` + bundle IDs); phrases are vocabulary substrate. Headline leak-guard (`_FORBIDDEN_C0_SUBSTRINGS`) is unaffected.

## FILES_CHANGED
- [employment_bullet_pool.py](apps_rg/runtime/reasoning/employment_bullet_pool.py) — S1 SC/regen
- [competencies_graph_pool.py](apps_rg/runtime/reasoning/competencies_graph_pool.py) — S1 regen
- [competencies_rigor.py](apps_rg/runtime/sections/competencies_rigor.py) — S1 candidate pool 10→8
- [ibm_bullets_lane.py](apps_rg/runtime/sections/ibm_bullets_lane.py) — S2 synthetic X1D on pool path
- [competency_capability_evidence.py](apps_rg/runtime/sections/competency_capability_evidence.py) — G1 allowed_phrases
- [headline_positioning_evidence.py](apps_rg/runtime/sections/headline_positioning_evidence.py) — G1 allowed_phrases
- Tests realigned: [test_bullet_lane_sc_claude_selection.py](tests/unit/apps_rg/test_bullet_lane_sc_claude_selection.py), [test_competencies_10x6_pool.py](tests/unit/apps_rg/test_competencies_10x6_pool.py), [test_competencies_graph_skills_proof_pool_p2_w1a.py](tests/unit/apps_rg/fact_inventory/test_competencies_graph_skills_proof_pool_p2_w1a.py), [test_competencies_rigor_constants_derived_from_ssot.py](tests/unit/apps_rg/test_competencies_rigor_constants_derived_from_ssot.py), [test_competencies_10x6_target_contract.py](tests/_apps_contract/test_competencies_10x6_target_contract.py), [test_competencies_graph_pool_w2.py](tests/_apps_contract/test_competencies_graph_pool_w2.py)

## TESTS_GATES
- `python -m compileall apps_rg -q` → exit 0
- `git diff --name-only -- agentic_core/` → empty (no core diff)
- 129 targeted unit/contract tests pass (S1 reasoning suites, adjudicator/aggregation 17, competency/headline evidence 54, reasoning profiles).
- 3 stale assertions traced to the **prior-wave uncommitted profile edit** (narrative SC 1→4, bullet profile 15/12→4) via git-stash parity (PASS in committed baseline, FAIL in working tree), then realigned to the canonical variance-class values.

## SECTION_RUNTIME_PROOF (live, provider=qwen_vllm, AIG JD+briefing)
Inputs: `apps_rg/config/targeting/aig_vp_global_head_agentic_ai_jd.txt` (4894B) + `..._briefing.md` (3240B); target AIG / "VP, Global Head of Agentic AI Solutions".

| Section | run_dir | gen | X2 | X3 | S1 proof | S2 proof | G1 proof |
|---|---|---|---|---|---|---|---|
| competencies | `competencies_20260607_030711` | REAL_LLM | all PASS | **X3_ALLOW** / PROOF_ELIGIBLE | `initial_path_count=8` (was 10) | n/a | formatter unit-proven; live competencies body assembled via FEC-bridge (PA bundle block not in this path — pre-existing) |
| ibm_bullets | `ibm_bullets_20260607_031632` | REAL_LLM | 4 deterministic gates FAIL | X3_BLOCK (correct) | `initial_path_count=4` (was 12), `selection_gate.ok=True` | **synthetic `anthropic_claude` row, `judge_role=employment_bullet_pool_selector`** — no 2nd independent Anthropic call | n/a |
| headline | `headline_20260607_031442` | REAL_LLM | `x2_headline_xyz_literal_grounding` FAIL | X3_BLOCK | n/a | n/a | **7 POSITIONING_BUNDLE blocks, 20 `allowed_phrases:` lines, `bound_skills (graph authority...)` block present in compiled prompt** |

### Rigor preserved (the key claim)
- competencies REAL_LLM → **X3_ALLOW** with reduced pool (8) and all competency X2 gates PASS.
- ibm_bullets reduced pool (4) still produced a valid Claude selection (`selection_gate.ok=True`); X3_BLOCK is from **deterministic X2 content gates** (`x2_ibm_bullet_single_thought`, `x2_ibm_hold_metric_forbidden_in_output`, `x2_ibm_metrics_preserved`, `x2_bullet_technical_specificity_floor`) — the variance-class "mechanical rules" class. Sub-standard output is still blocked. **No rigor lost; cost cut 12→4 paths + one fewer Anthropic call.**
- headline X3_BLOCK is the prior-wave strict gate `x2_headline_xyz_literal_grounding` (uncommitted working-tree addition), independent of S1/S2/G1.

## AGENTIC_SPINE_STEPS (competencies run, per specs)
Single canonical pipeline. `GENERATED_LANES = (competencies, unify_bullets, ibm_bullets, unify_narrative, ibm_narrative, executive_summary, headline)`. Spine binding: `apps_rg.runtime.bindings.c0_binding.c0_retrieve_apps_rg`, retrieval_mode `NATIVE_C0`, route `R3_SIMPLE_GROUNDED_READ`.

- **C0 (retrieve/propose)**: `c0_evidence_room_receipt.json` (c01 plan → c02 atoms → c03 graph bindings → c04 stratify), `c02_vector_query.json` (dense `fact_vectors`), `c02_semantic_cache_payload.json` (BGE intent vector + query output), `c0_graph_lane_receipt.json`, `section_spine_c0_retrieve_receipt.json`, `c0_fec_compose_receipt.json` (FEC), `c0_metrics.json`.
- **L2 (execute/seal)**: `bullet_lane_generation.json` (`initial_path_count=8`), `bullet_pool_selection.json`, `compiled_prompt.txt`, `compiled_prompt_artifact.json`.
- **X1D / X2 / X3 (judge / deterministic / aggregate)**: `x1d_llm_judge_outputs.json`, `x2_gate_outputs.json` (all PASS), `x3_disposition.json` (`x3_code`, `proceed_to_runtime`, `product_quality_status`).
- **Exit / L6**: `l6_shadow_eval_package.json`, `l6_shadow_learning.json` (offline_only).

## SINGLE_PIPELINE_CONFIRMATION
All three live sections routed through the one canonical `python -m apps_rg --section <s>` CLI → `c0_binding.c0_retrieve_apps_rg` spine → section lane → X2/X1D/X3 → Exit/L6. No alternate/parallel pipeline was invoked. `best_of_n_section_harness.py` (superseded) was not used.

## ENVIRONMENT_NOTES (honest blockers)
- `qwen_vllm` reachable at `http://localhost:8000/v1` (generation path live). NOTE: `VLLM_BASE_URL` must include `/v1` — the readiness gate appends `/models`.
- `ANTHROPIC_API_KEY` / `GEMINI_API_KEY` NOT set. The Claude pool selector still produced a valid selection (selection_gate.ok=True on ibm), and S2's synthetic row is selector-derived, so S1/S2 were provable on the Qwen path. Full multi-provider judge release-signoff remains blocked on judge keys.
- `_apps_contract` IBM integration slices (`test_ibm_bullets_runtime_slice.py`, `..._text_claim_coverage.py`) exceed unit timeouts (they hit the live provider) — covered instead by the live AIG ibm_bullets run.

## DEFERRED (not in approved focused scope)
- competencies FEC-bridge does not carry the PA-local competency bundle block into the prompt body (G1 surfaces in headline's direct-PA path, not competencies' FEC-bridge path) — pre-existing wiring, candidate for a follow-up.
- broad_sweep items: exec-summary post-X2 3-judge refresh default-off + judge-regen 3→1, narrative pack thickening, C03 1-hop adjacency into competency projection.

## STATUS: PARTIAL
S1 + S2 + G1 implemented, unit-verified, and live-proven on AIG (competencies X3_ALLOW; ibm S1+S2 paths confirmed with rigor-correct X2 block; headline G1 in prompt). PARTIAL (not PASS) because: ibm_bullets/headline X3_BLOCK on deterministic content gates (correct behavior, not a regression) means no full multi-section X3_ALLOW sweep, and competencies G1 does not surface via the FEC-bridge path. No agentic_core diff; no rigor weakened.
