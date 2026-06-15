---
plan_format: v2
status: approved
owner: chat/20260615-085637-88d0e979
created: 2026-06-15
approved: 2026-06-15
north_star_relation: precursor
dod_exempt: false
---

# apps_rg Config SSOT Consolidation — One Lane-Policy Source, No Re-Drift

## Context (SCQA)

- **Situation.** apps_rg generates each resume lane on external Claude and judges it with a
  cross-provider panel. The *generator* model already has a single SSOT —
  `apps_rg/config/provider_profiles.yaml` (`external_claude_generator.default_model` +
  `model_by_section`), resolved by
  [`resolve_section_generation_model`](apps_rg/runtime/section_model_limits.py:75) (landed 2026-06-14).
- **Complication.** Model + reasoning config is still scattered across **three competing homes**:
  the home `~/env/.env` (autoloaded at `import apps_rg`), `agentic_core` model config, and the judge
  profiles. The `.env` already caused a **multi-day model-drift incident** — an import-time env pin
  (`APPS_RG_EXTERNAL_CLAUDE_MODEL=sonnet`) silently overrode the YAML for *every* lane. A 40-variable
  audit (this chat) found only **~11 vars legitimately belong in `.env`** (secrets + machine/operator
  toggles); the rest are dead, restate an in-code default, or are competing SSOTs. Because E2E
  certification is only valid against *what actually ran*, this drift class silently invalidates an
  11/11 board on the next run.
- **Question.** How do we make **per-lane model + reasoning intensity single-sourced** so E2E cannot
  re-drift, without violating the `agentic_core`/apps boundary law?
- **Answer.** Extend `provider_profiles.yaml` into the **one apps_rg lane-policy SSOT** (generator
  model + judge model tier + reasoning intensity, per lane), resolved through the **existing**
  `resolve_section_generation_model` seam (plus two sibling resolvers); strip `.env` to secrets +
  machine/operator toggles; migrate the genuine value-overrides into committed config; and add a
  **runtime model-SSOT drift gate** (the assertion specced at
  [typed-edge-role-facet-guardrails:512](plans/typed-edge-role-facet-guardrails-a6f3d2.md)) so the
  invariant is enforced, not just documented. "One SSOT" = **one per ownership domain**: core-owned
  model IDs stay in `agentic_core` committed config; apps_rg lane policy lives in `provider_profiles.yaml`.

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | P1 | `.env` safe prune (Tier D: dead + value==default) | ~15k | `.env` is untracked; `.bak` is the only undo | DONE | `.bak` written; only Tier-D vars removed; `python -m apps_rg --section competencies` byte-identical model/limits resolution |
| W2 | P2 | Extend `provider_profiles.yaml` -> lane-policy SSOT (model + reasoning + judge-model tiers) | ~25k | YAML stays app-owned; code keeps fail-soft literal fallback | DONE (2 commits) | YAML carries per-lane `reasoning_by_section` + `judge_models`; schema documented |
| W3 | P3 | Extend resolvers to read new YAML keys; thread reasoning into generation request | ~40k | resolver pattern in `section_model_limits.py` is the template | DONE (judge-repoint; reasoning kept in existing code SSOT) | `resolve_section_reasoning_intensity()` + judge-model YAML read live; generation `provider_request.json` carries per-lane model + reasoning |
| W4 | P4 | Migrate Tier-C overrides to committed config; delete from `.env` | ~35k | core model IDs are core-owned (legit in core config) | in_progress (anthropic judge migrated 3fbed7f072; core models + HIVE_MIND gated) | 6 Tier-C vars live in committed SSOT + a test each; removed from `.env`; no behavior change |
| W5 | P5 | Model-SSOT drift gate (static literal ban + runtime/offline-replay assertion) | ~40k | offline replay harness can read `provider_request.json` | in_progress (concurrent: feat/apps-rg-model-ssot-gate) | `check_apps_rg_model_ssot.py` wired into `run_contract_gates.py`; fails on a planted hardcoded literal AND on a model mismatch |
| W6 | P6 | E2E validation (2 live ship lanes) + docs + memory writeback | ~30k | Anthropic + Brown lanes are the live ship targets | TODO | 2 live lanes carry resolved per-lane model+reasoning in `provider_request.json`; apps_rg docs + memory updated |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| P1 | `.env` safe prune | DONE |
| P2 | YAML lane-policy SSOT schema | DONE |
| P3 | Resolver extension + generation threading | DONE (judge-repoint; reasoning_by_section reverted 94c2bbc5bf — existing code SSOT adopted) |
| P4 | Tier-C migration to committed config | in_progress (1/6: anthropic judge done) |
| P5 | Model-SSOT drift gate | TODO |
| P6 | E2E validation + docs | TODO |

## Execution Coordination (updated 2026-06-15)

> **Resumed — single owner = worktree `feat/apps-rg-lane-policy-ssot`** (`C:\Git\Agentic-Workflow-FRESH-lanepolicy`,
> cut from current origin/main `3702d47997`; the original chat worktree was reaped). W1 shipped; plan approved.
>
> **W2 DONE — 2 commits on `feat/apps-rg-lane-policy-ssot`:** `8b2a1366fe` (reasoning_by_section +
> `resolve_section_reasoning_intensity()` + 5 tests) and `8740c1a4d0` (judge_models SSOT-of-record +
> parity test pinning `section_judge_profile.py` profile_defaults[0] == YAML, 3 tests). 8/8 pass.
> Both YAML blocks are inert SSOT (not yet consumed by the live paths) — guarded by tests.
>
> **W3 seam-location finding:** ADG fan-in on `section_model_limits` (snapshot `06142026_1721`) returns only
> 3 TEST importers — import edges are symbol-specific and the snapshot predates the resolver's broad
> consumption, so the live modular-lane generation dispatch is NOT resolvable on this snapshot. W3 must
> first regen the ADG **or** do a scoped grep (`DEGRADED_FALLBACK`) to find the live generation seam, then
> thread `resolve_section_reasoning_intensity()` + reconcile the `reasoning_by_section` values to the seam's
> current params. NOTE `apps_rg/integrations/hops/_llm_client.py` is the LEGACY narrative-ensemble path
> (own hardcoded models/temperature) — a separate drift surface, NOT the SSOT seam.
>
> **Remaining:** W3 (thread reasoning into the located seam; repoint `section_judge_profile.py` profile_defaults
> at the YAML `judge_models`, fail-soft to the code tuple); W4 Tier-C migration (re-verify W1 `.env` prune first);
> W6 E2E. **W5 stays on `feat/apps-rg-model-ssot-gate`** (uncommitted there) — do NOT duplicate; build on it once
> it lands.
>
> **Update (W3 partial + W4 gating, 2026-06-15 — commits `8b2a1366fe`, `8740c1a4d0`, `61a45e1088`):**
> W3 **judge-repoint DONE** (`61a45e1088`: resolver reads YAML `judge_models`, fail-soft to code tuple,
> env still wins; one regression RCA'd + fixed; **the 10 other judge-sweep failures are PRE-EXISTING on
> origin/main `3702d47997`**, isolated via stash — NOT ours). The REMAINING waves hit gates that need a
> decision, not blind execution:
> - **(a) W3 reasoning-threading — multi-site + behavior-sensitive.** Generation temp/max_tokens are
>   scattered (`role_episode_lane.MAX_OUTPUT_TOKENS=900`, `ExternalProvider.generate` default temp 0.7,
>   the `generate_bullet_lane_with_sc_and_claude` helper). Behavior-neutral threading needs a per-lane
>   value-map + live/replay validation (changing temp alters generation → risks the 11/11 board). The
>   `reasoning_by_section` placeholders (0.1/0.3/0.2) must be reconciled to the real current values first.
> - **(b) W4 core-model migrations** (`OPENAI_MODEL`=gpt-5.5 vs core default gpt-4o; `GOOGLE_AI_MODEL`):
>   baking these into `agentic_core` committed defaults is a CORE change — broad blast radius (all apps,
>   CI) + boundary receipt + Core-Addition author-gate required.
> - **(c) W4 anthropic enhanced judge:** `.env`=claude-sonnet-4-6 vs code/YAML=claude-opus-4-6. Runtime is
>   already sonnet via env, so the honest migration sets the SSOT to sonnet + updates profile_defaults +
>   parity test — but opus-vs-sonnet canonical is an architecture choice.
> - **(d) W4 `HIVE_MIND_STRICT_MODE`:** removal is NOT behavior-neutral — `semantic_cache_manager`
>   defaults true while `apps_shared/config/environment_config` field defaults false; reconcile first.
> - **(e) CRITICAL — per-lane reasoning ALREADY has a consumed code SSOT (premise was wrong).**
>   `apps_rg/runtime/reasoning/section_reasoning_intensity.py` (`section_reasoning_profile(lane)` →
>   `default_temperature_for_section`) sets per-lane temperature, consumed via `lane_temperature` →
>   `provider.generate(temperature=...)` across `section_lane_executor` / `canonical_dispatch` /
>   `section_cli_runners`. **Real current temps:** headline 0.15, executive_summary 0.42, competencies
>   0.38, unify/ibm_bullets 0.38, unify/ibm_narrative 0.39, default 0.32. **The W2 `reasoning_by_section`
>   (provider_profiles.yaml) + `resolve_section_reasoning_intensity()` (commit `8b2a1366fe`) is a
>   REDUNDANT, unconsumed duplicate with WRONG placeholder values (0.1/0.3/0.2)** — threading it would
>   have shifted every lane's temperature (board regression). **Consolidation decision needed:**
>   (A) adopt the existing code SSOT, revert the W2 reasoning_by_section duplication; or (B) migrate the
>   per-lane temperature into provider_profiles.yaml + make `section_reasoning_intensity.py` read it
>   (behavior-neutral at the real values), leaving the Qwen-era ToT/SC/reflexion knobs in code. The W2
>   `judge_models` slice (`8740c1a4d0`) + the judge-repoint (`61a45e1088`) are UNAFFECTED — valid
>   separate consolidations.
>
> **DELIVERED to origin/main (2026-06-15)** via `deliver_worktree.py --mode push` (rebased on
> origin/main, retest 22/22, pushed HEAD→main). Net commits on main: `9f1225e1c6` (judge_models SSOT),
> `c56438e87a` (judge-repoint), `3f861dee5e` (reasoning revert), `75c39889dc` (anthropic judge → sonnet).
> Worktree `feat/apps-rg-lane-policy-ssot` reaped (junctions removed first; primary cache verified intact).
> **REMAINING (separate gated effort): W4 core-model migrations (`OPENAI_MODEL`, `OPENAI_TEMPERATURE`,
> `GOOGLE_AI_MODEL`, `GOOGLE_AI_PRO_MODEL`) + `HIVE_MIND_STRICT_MODE` — all agentic_core-touching →
> boundary receipt + Core-Addition author-gate required; and W6 E2E validation.**

## Wave W1 — `.env` safe prune (zero runtime risk)

Back up `C:\Users\amita\env\.env` -> `.env.bak`, then delete only the two zero-risk classes from the
40-var audit:

- **DEAD (7, no consumer found):** `APPS_RG_QWEN_TIMEOUT_SECONDS`, `APPS_RG_VLLM_AUTO_START`,
  `APPS_RG_PARALLEL_PHASE1_LANES`, `APPS_RG_PHASE1_MAX_PARALLEL`, `FIGMA_TOKEN`, `FIGMA_TEAM_ID`, `DEBUG`.
- **REDUNDANT_DEFAULT (value == verified in-code default):** `OPENAI_MAX_TOKENS`,
  `GOOGLE_AI_MAX_OUTPUT_TOKENS`, the `==`-default judge token/effort vars, `APPS_RG_SECTION_MAX_MODEL_LEN`
  (=32768, verified at [section_model_limits.py:23](apps_rg/runtime/section_model_limits.py:23)),
  `APPS_RG_EXEC_SUMMARY_MAX_OUTPUT_TOKENS`/`_REGEN` (=4096, verified), `REDIS_HOST/PORT/URL`,
  `ADG_REDIS_URL`, `VLLM_*`/`QWEN_VLLM_MODEL` block, `SEMANTIC_CACHE_D2_ENABLED`,
  `HIVE_MIND_TRACE_SAMPLING_RATE`/`PROMOTION_THRESHOLD`, `PYTHONUNBUFFERED`, `LOG_LEVEL`,
  `APPS_RG_PROVIDER_PROFILE`, `APPS_RG_MODULAR_LANE_PROVIDER`.

**Keep:** 9 secrets, `VECTOR_DB_DEVICE=cuda`, `APPS_RG_L2_PROVIDER_MODE=live_allowed`, and the 6 Tier-C
overrides (until W4 migrates them). Removal-safety is definitional: dead = no reader; redundant = value
already equals the default the code would use. Verify with one `--section competencies` resolution
spot-check (model + ctx unchanged).

## Wave W2 — Extend `provider_profiles.yaml` into the lane-policy SSOT

Under `profiles.external_claude_generator`, add two app-owned blocks (additive; no key renames):

```yaml
external_claude_generator:
  default_model: claude-sonnet-4-6          # existing
  model_by_section: { ... }                 # existing (per-lane generator model)
  reasoning_by_section:                     # NEW — per-lane generation reasoning intensity
    default:            { temperature: 0.2, max_output_tokens: 4096 }
    executive_summary:  { temperature: 0.1, max_output_tokens: 4096 }
    headline:           { temperature: 0.3, max_output_tokens: 1024 }
    # ...one row per canonical lane (12 from section_judge_policy._SECTION_POLICIES)
judge_models:                               # NEW — replaces hardcoded profile_defaults + APPS_RG_*_JUDGE_MODEL_* env
  enhanced: { gemini_pro: gemini-3.1-pro-preview, openai_chatgpt: gpt-5.5, anthropic_claude: claude-opus-4-6 }
  standard: { gemini_pro: gemini-2.5-pro,        openai_chatgpt: gpt-5.5, anthropic_claude: claude-sonnet-4-6 }
```

Canonical lane list (SSOT) is
[`section_judge_policy._SECTION_POLICIES`](apps_rg/runtime/section_judge_policy.py:68) — 11 active
lanes + `final_aggregate_resume`. The section->judge-**tier** matrix **stays in code** (structural, not
`.env`-drift-prone); only judge **model-per-tier** moves to YAML.

## Wave W3 — Extend resolvers; thread reasoning into the generation request

- Add `resolve_section_reasoning_intensity(section_id)` to
  [section_model_limits.py](apps_rg/runtime/section_model_limits.py) mirroring the existing fail-soft
  `_ssot_model_by_section()` pattern (YAML read -> `default` -> literal fallback).
- Point [section_judge_profile.py](apps_rg/runtime/judges/section_judge_profile.py) `profile_defaults`
  at the YAML `judge_models` block (keep code tuple as fail-soft fallback only).
- Thread the resolved reasoning intensity into the generation provider request alongside the model
  (the model is already threaded). **Confirm the exact request param name at implementation** (the
  generation dispatch path — `apps_rg/integrations/hops/_llm_client.py` / section generation seam).

## Wave W4 — Migrate Tier-C overrides to committed config, then delete from `.env`

The 6 active divergences (deleting before migrating WOULD change behavior — migrate first, test, then
remove from `.env`):

| Var | Target committed SSOT | Boundary note |
|---|---|---|
| `OPENAI_MODEL`, `OPENAI_TEMPERATURE` | `agentic_core` model/reasoning config | core-owned model IDs — legit in core |
| `GOOGLE_AI_MODEL`, `GOOGLE_AI_PRO_MODEL` | `agentic_core/config/google_ai_env.py` / `model_registry` | core-owned |
| `APPS_RG_ANTHROPIC_JUDGE_MODEL_ENHANCED` (sonnet, cost downgrade) | `provider_profiles.yaml judge_models.enhanced.anthropic_claude` | app-owned |
| `HIVE_MIND_STRICT_MODE=false` | `apps_shared/config/environment_config.py` field default | shared |

Each migration ships with a unit test pinning the committed default == the value being removed.

## Wave W5 — Model-SSOT drift gate (the durable moat)

`ops_scripts/ci/check_apps_rg_model_ssot.py`, wired into
[run_contract_gates.py](ops_scripts/ci/run_contract_gates.py):

1. **Static:** no hardcoded `claude-*` / `gpt-*` / `gemini-*` literal in apps_rg generation/judge paths
   outside the YAML SSOT + the named fail-soft fallbacks.
2. **Runtime/offline-replay:** every lane's `provider_request.json` model + reasoning == the resolver
   output for that lane (the intended-vs-actual check that the env-pin bug evaded). Reuse
   `tools/apps_rg/replay_section_gates.py` so it costs ~$0.

## Wave W6 — E2E validation + docs + memory

Run the 2 live ship lanes (Anthropic + Brown) — or offline replay where sufficient — confirm
`provider_request.json` carries resolved per-lane model + reasoning. Update apps_rg docs and the
`apps-rg-model-ssot-env-pin-rootcause` memory; mark `apps-rg-stale-qwen-token-budget` superseded
(the 32768/4096 bump is now the in-code default).

## Definition of Done

| # | Criterion | Verification |
|---|-----------|--------------|
| 1 | `.env` contains only secrets + machine/operator toggles + (pre-W4) Tier-C overrides | Manual diff vs `.env.bak`; var count drops ~40->~17 |
| 2 | Per-lane generator model + reasoning + judge model all resolve from `provider_profiles.yaml` | `resolve_section_generation_model` / `resolve_section_reasoning_intensity` unit tests |
| 3 | 6 Tier-C overrides live in committed config with a pinning test each; removed from `.env` | `pytest tests/unit/apps_rg/ -k ssot` green |
| 4 | `check_apps_rg_model_ssot.py` fails on a planted hardcoded literal AND on a model mismatch | Negative-control test in the gate's own test file |
| 5 | Gate wired into `run_contract_gates.py` and passes on a clean tree | `python ops_scripts/ci/run_contract_gates.py` |
| 6 | No `agentic_core` boundary violation introduced | `/core-boundary-audit` clean |
| 7 (smoke) | Pipeline still runs end-to-end | `python -m apps_rg --section competencies` exits 0 with resolved model+reasoning in `provider_request.json` |

### Verification vs Deferral

| Item | This plan | Deferred |
|---|---|---|
| `.env` prune + Tier-C migration + drift gate | yes | — |
| Per-lane reasoning intensity as first-class config | yes | — |
| Moving the section->judge-**tier** matrix into YAML | — | yes (structural, not drift-prone; stays in code) |
| Consolidating `agentic_core` core model registry beyond the 4 Tier-C vars | — | yes (separate core effort) |
| 11/11 lane convergence (`executive_summary`/`headline`) | — | yes (typed-edge plan; this is its precursor) |

## ADG_HOTSPOT_REPORT

Scope is config + resolver seams, not a graph-blast refactor. Touched modules and fan-in:
`section_model_limits.py` (imported by ~15 section lanes + the X2 validator — high fan-in, change is
additive/fail-soft), `section_judge_profile.py` (judge resolution), `provider_profiles.yaml` (data
SSOT, no importers). Archetype: **CENTRAL_DEPENDENCY** (resolver) — mitigated by keeping all changes
additive with literal fail-soft fallbacks so the foundational import never breaks.

## ADG_GRAPH_LAYER_EVIDENCE

Deferred to implementation start (W2/W3): before editing `section_model_limits.py`, query
`adg_edge_fanin` on it to confirm the consumer set (expected ~15 lanes) and that no consumer reads a
to-be-renamed symbol — the change is purely additive (new functions + new YAML keys), so blast radius
is bounded to new call sites. MVs (`mv_graph_reverse_dependency_hotspots`) consulted at W3 to confirm
the resolver is the chokepoint and threading reasoning there covers all lanes.
