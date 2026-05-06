# Deferred-Scope Followup — apps_rg + vLLM Items Not Closed in f7d3a9

**Slug**: `apps-rg-vllm-followup-blocked-c4e8b2`
**Status**: In Progress (W1 complete 2026-05-06; W2/W3/W4 still pending)
**Tier**: T2 (cross-cutting)
**Parent**: `apps-rg-vllm-followup-f7d3a9` (Completed 2026-05-06; W4 skipped per user; W2 partial; W6 blocked)

## Goal

Capture the items from parent plan that were **not implemented** in 2026-05-06 session, with explicit reasons and unblock conditions. **Do NOT implement** — this plan is for capture only.

## Wave Structure

| Wave | Focus | Why deferred | Unblock condition |
|---|---|---|---|
| W1 | apps_rg default-path refactor + delete `company_research.json` (Blend360) + `job_description.json` (stub) | ✅ DONE 2026-05-06 (commit `16b027f62d`). `_DEFAULT_JD_PATH` / `_DEFAULT_BRIEF_PATH` redirected to wizard-managed `_interactive_*.json`; all 10 referencing files updated (`apps_rg/__main__.py`, `apps_rg/integrations/company_research_loader.py`, `apps_rg/integrations/preloaded_input_context_manifest.py`, `apps_rg/l2_recipe/steps.py`, `agentic_core/runtime/l2_recipe_resolver.py`, `apps_rg/scripts/narrative_pass.py`, `ops_scripts/apps_rg/narrative_pass.py`, `apps_rg/types/company_research.py`, `tools/calibrate_apps_rg_overfit_threshold.py`, `artifacts/_jd_extract_smoke.py`). Both stale files deleted. 14/14 wizard tests still pass; non-TTY hard-fail preserved. | (closed) |
| W2 | apps_research synthesis cascade — OpenAI + Anthropic tiers | ⏭ SKIPPED again 2026-05-06 — user reaffirmed "apps_research only Gemini". | User authorizes adding cloud cascade tiers beyond Gemini. |
| W3 | Always-on promotion of `apps-rg-interactive-discipline.md` (model_decision → always_on) | §33 always-on token-budget gate FAIL on 2026-05-06: 51,793 / 51,200 bytes (593 bytes over). Promotion would worsen the overage. | Trim some always-on rule (candidates: `scope-containment.md` 8425b, `mcp-serialization.md` 5031b, `adg-canonical-invariants.md` 5073b); re-run `python ops_scripts/ci/check_always_on_token_budget.py`; when PASS with headroom ≥ 3500 bytes, flip frontmatter trigger. |
| W4 | Sibling-app interactive wizards (apps_lic, apps_underwriting_ai, etc. when applicable) | None of the 6 sibling apps surveyed in 2026-05-06 W1 have the same "3 mandatory target inputs + cross-target contamination risk" pattern as apps_rg. apps_lic has 9 optional args (all empty defaults), apps_underwriting_ai uses `--request <file>` or `--demo`, apps_qna/apps_research/apps_rfp use receipts emitter pattern. Force-fitting a wizard would be unused code. | A sibling app grows new mandatory target inputs with cross-target contamination risk. At that point: import `apps_shared.cli.interactive_wizard.run_wizard()`, mirror apps_rg pattern, extend rule scope. |

## Phase-Level Summary

| Phase | Scope (files) | Est. Tokens | Pain Points |
|---|---|---|---|
| W1.P1 | `apps_rg/__main__.py`, `apps_rg/integrations/company_research_loader.py`, `apps_rg/integrations/preloaded_input_context_manifest.py`, `apps_rg/l2_recipe/steps.py`, `apps_rg/types/company_research.py`, `apps_rg/scripts/narrative_pass.py`, `ops_scripts/apps_rg/narrative_pass.py`, `agentic_core/runtime/l2_recipe_resolver.py`, `tools/calibrate_apps_rg_overfit_threshold.py`, `artifacts/_jd_extract_smoke.py` (10+ files) | ~600 | Refactor preserves cross-company guard semantics; delete only after grep confirms zero `company_research.json` / `job_description.json` references remain. |
| W2.P1 | `apps_research/engines/company_brief_engine.py`, `.env.example`, new `apps_research/engines/_openai_synthesize.py`, new `apps_research/engines/_anthropic_synthesize.py` (or inline) | ~800 | Two new SDKs (`openai`, `anthropic`); shared cascade-iteration helper to reduce duplication; env vars `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `OPENAI_MODEL`, `ANTHROPIC_MODEL`. |
| W3.P1 | `.windsurf/rules/apps-rg-interactive-discipline.md` frontmatter (1 line); upstream trimming of one always-on rule (varies) | ~150 (rule flip) + ~200-400 (trim work) | Identify which rule to trim or which procedural detail to move to a skill. Run gate before AND after change. |
| W4.P1 | When activated: `apps_<x>/__main__.py` for the specific app + tests | varies | Each app has different inputs; helper makes per-app wiring cheap (~100 LOC per app). |

## Files In Scope

When activated. Plan is capture-only.

## Non-Goals

- Hook-based enforcement of wizard discipline (rejected during initial design)
- Auto-detection of "user explicitly authorized" vs "Cascade inferred" (NLP-hard)
- Real LLM-judge implementations (separate plan family — see memory `5ba9ca42`)
- C0 FEC producer wiring for grounded apps (separate plan, blocker #4)
- apps_underwriting_ai analyst attestation flip (out-of-scope; requires qualified-owner sign-off)

## Success Criteria

When each wave is activated:
- ✅ Wave gets its own activation plan with `## ADG_GRAPH_LAYER_EVIDENCE` per §22
- ✅ Notion row registered before `wave_execution_state.py start` (per §36)
- ✅ Defense-in-depth preserved (cross-company guard, contamination test, behavioral rule)

## Pattern Source

Same shape as parent `apps-rg-vllm-deferred-followup-f7d3a9`. Same shape as `plan-location.md` / `ssot-folder-enforcement.md` / `mcp-serialization.md` (helper logic + conditional rule + durable test surface).

## Constitutional Cross-Reference

- §6 (Author-Gate for ambiguous decisions)
- §18 (no hidden scope expansion — items captured here, not silently widened)
- §22 (ADG_GRAPH_LAYER_EVIDENCE required when any wave activates)
- §24 (deferred-scope capture — this plan IS the capture artifact)
- §33 (W3 gated on always-on token budget)
- §36 (plan must be registered in Notion before wave starts)

## Notion Registration

- Database: Plans DB (`6aba34d9-4d0b-4f4c-b956-b2bdea541ca9`)
- Status: `Not Started` (option id `503df59f-85d4-4ac0-baae-e457d0354b6f`, gray)
- AI Summary: bullet-style per `notion-plans-taxonomy.md` invariant
- Exists On Disk: true
- Plan File Path: `.windsurf/plans/apps-rg-vllm-followup-blocked-c4e8b2.md`
