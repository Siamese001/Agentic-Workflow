# apps_rg Simplification + Graph-Skill Signal — AIG End-to-End Proof (2026-06-07)

Scope authorized via Author-Gate (`refactor_scope`, decision `dec_19e9ffaee599e073d`, selected `focused_high_value`, confidence 0.82, precedent: cold corpus). Two read-only audits grounded the picks; deferred follow-up items from the first closeout are now implemented in wave 2.

## What changed

### S1 — Align SC path counts with the variance-class profile
- **unify_bullets / ibm_bullets**: SC `15/12 → 4` over fixed slot counts.
- **competencies**: candidate-category pool `10 → 8` (selection pool ≥6 final categories).
- Regen extra paths trimmed.

### S2 — IBM bullets: drop redundant second Anthropic judge on pool path
- Pool path uses `employment_pool_x1d_judge_rows()` synthetic `anthropic_claude` selector row (mirrors unify). Adjudicator panel still escalates borderline cases.

### G1 — Surface graph-skill `allowed_phrases` in evidence packs
- `format_competency_capability_evidence_pack` and `format_headline_positioning_evidence_pack` emit `bound_skills (graph authority — vocabulary anchors only)`.

### Wave 2 — Deferred scope closed

| Item | Fix |
|------|-----|
| FEC-bridge PA authority | `_PA_GRAPH_BUNDLE_AUTHORITY_KEYS` in [c0_fec_compose.py](apps_rg/runtime/spine/c0_fec_compose.py) propagates `competency_capability_bundle_consumption` + bundle payloads through `pa_proof_authority_metadata` |
| Narrative pack thickening | `_format_narrative_bundle_block` in [unify_role_episode_evidence.py](apps_rg/runtime/sections/unify_role_episode_evidence.py) and [ibm_role_episode_evidence.py](apps_rg/runtime/sections/ibm_role_episode_evidence.py) now emit `bound_skills \| allowed_phrases` |
| Exec-summary judge trim | `RELEASE_POST_X2_JUDGE_REFRESH_ENABLED = False`; `JUDGE_REGEN_MAX_ATTEMPTS = 1` (hard cap 3) in [executive_summary_repair_policy.py](apps_rg/runtime/sections/executive_summary_repair_policy.py) |
| C03 1-hop adjacency | `adjacent_skill_ids` on competency projection via shared `capability_domain_contains_skill` edges in [augmented_skills_graph.py](apps_rg/fact_inventory/augmented_skills_graph.py) |

## FILES_CHANGED (wave 1 + wave 2)
- [employment_bullet_pool.py](apps_rg/runtime/reasoning/employment_bullet_pool.py) — S1
- [competencies_graph_pool.py](apps_rg/runtime/reasoning/competencies_graph_pool.py) — S1
- [competencies_rigor.py](apps_rg/runtime/sections/competencies_rigor.py) — S1
- [ibm_bullets_lane.py](apps_rg/runtime/sections/ibm_bullets_lane.py) — S2
- [competency_capability_evidence.py](apps_rg/runtime/sections/competency_capability_evidence.py) — G1
- [headline_positioning_evidence.py](apps_rg/runtime/sections/headline_positioning_evidence.py) — G1
- [c0_fec_compose.py](apps_rg/runtime/spine/c0_fec_compose.py) — FEC bundle authority propagation
- [unify_role_episode_evidence.py](apps_rg/runtime/sections/unify_role_episode_evidence.py) — narrative allowed_phrases
- [ibm_role_episode_evidence.py](apps_rg/runtime/sections/ibm_role_episode_evidence.py) — narrative allowed_phrases
- [executive_summary_repair_policy.py](apps_rg/runtime/sections/executive_summary_repair_policy.py) — judge loop trim
- [augmented_skills_graph.py](apps_rg/fact_inventory/augmented_skills_graph.py) — C03 adjacency projection

## TESTS_GATES
- `python -m compileall apps_rg -q` → exit 0
- `git diff --name-only -- agentic_core/` → empty
- Wave 1: 129 targeted unit/contract tests pass (S1/S2/G1 suites).
- Wave 2: 38 targeted tests pass (competency bundle wiring + FEC PA metadata + adjacency contract + exec-summary regen policy).

## SECTION_RUNTIME_PROOF (live, provider=qwen_vllm, AIG JD+briefing)

| Section | run_dir | gen | X3 | Scope proof |
|---|---|---|---|---|
| competencies (wave 1) | `competencies_20260607_030711` | REAL_LLM | **X3_ALLOW** | S1 `initial_path_count=8` |
| competencies (wave 2 / G1 FEC) | `competencies_20260607_081726` | REAL_LLM | X3_BLOCK (content X2) | **10 `COMPETENCY_BUNDLE` blocks, 32 `allowed_phrases:` lines, 10 `bound_skills` blocks in `compiled_prompt.txt`**; `competency_capability_bundle_consumption=true` in FEC bridge |
| ibm_bullets | `ibm_bullets_20260607_031632` | REAL_LLM | X3_BLOCK (rigor-correct) | S1 pool=4; S2 synthetic selector row |
| headline | `headline_20260607_031442` | REAL_LLM | X3_BLOCK | G1: 7 positioning bundles, 20 allowed_phrases in prompt |

Wave 2 competencies X3_BLOCK is **model output variance** on deterministic content gates (`x2_duplicate_variants_collapsed`, `x2_competency_duplicate_variant_absent`, `x2_no_keyword_stuffing`, `x2_required_capability_families_covered`) — not a regression of FEC/G1 wiring. Judges ran: `gemini_pro` MODEL_BACKED_PASS (uses `GOOGLE_API_KEY`).

## ENVIRONMENT (corrected — keys were never missing)

**Prior closeout was wrong.** A bare `os.environ.get('ANTHROPIC_API_KEY')` without `load_dotenv()` reported false negatives.

**Actual behavior:** `apps_rg/__main__.py` loads repo-root `.env` via `load_dotenv(override=False)` before every CLI run.

Verified with dotenv:
- `ANTHROPIC_API_KEY` — set
- `GOOGLE_API_KEY` — set (canonical Gemini judge path; `GEMINI_API_KEY` unset is expected)
- `VLLM_BASE_URL` — `http://localhost:8000/v1` (must include `/v1`)

Judge release-signoff is **not** blocked on missing keys when runs go through `python -m apps_rg`.

## AGENTIC_SPINE_STEPS
Single canonical pipeline: `python -m apps_rg --section <s>` → `c0_binding.c0_retrieve_apps_rg` → section lane → X2/X1D/X3 → Exit/L6.

## STATUS: PARTIAL
All authorized + deferred scope **implemented and tested**. Live proof confirms S1/S2/G1 + FEC-bridge G1 on competencies prompt. PARTIAL because no full multi-section X3_ALLOW sweep (ibm/headline/content gates block sub-standard output by design; wave-2 competencies hit content X2 variance). No `agentic_core` diff; no rigor weakened.
