---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\apps-rg-vllm-followup-blocked-c4e8b2.md'
original_relative_path: 'apps-rg-vllm-followup-blocked-c4e8b2.md'
source_sha256: 56cc2e85d4d619bcd74d8420502b41b886b9ad71ca62a9734345f92e43b6a646
recovered_status: SURVIVED_IN_CURRENT
last_commit: '153652b9eb3'
last_commit_date: '2026-06-07 06:37:48 -0400'
created_date: '2026-05-06'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Deferred-Scope Followup — apps_rg + vLLM Items Not Closed in f7d3a9

**Slug**: `apps-rg-vllm-followup-blocked-c4e8b2`
**Status**: In Progress (W1 ✅, W3 ✅ 2026-05-06; W2 skipped; W4 deferred)
**Tier**: T2 (cross-cutting)
**Parent**: `apps-rg-vllm-followup-f7d3a9` (Completed 2026-05-06; W4 skipped per user; W2 partial; W6 blocked)

## Goal

Capture the items from parent plan that were **not implemented** in 2026-05-06 session, with explicit reasons and unblock conditions. **Do NOT implement** — this plan is for capture only.

## Wave Structure

| Wave | Focus | Why deferred | Unblock condition |
|---|---|---|---|
| W1 | apps_rg default-path refactor + delete `company_research.json` (Blend360) + `job_description.json` (stub) | ✅ DONE 2026-05-06 (commit `16b027f62d`). `_DEFAULT_JD_PATH` / `_DEFAULT_BRIEF_PATH` redirected to wizard-managed `_interactive_*.json`; all 10 referencing files updated (`apps_rg/__main__.py`, `apps_rg/integrations/company_research_loader.py`, `apps_rg/integrations/preloaded_input_context_manifest.py`, `apps_rg/l2_recipe/steps.py`, `agentic_core/runtime/l2_recipe_resolver.py`, `apps_rg/scripts/narrative_pass.py`, `ops_scripts/apps_rg/narrative_pass.py`, `apps_rg/types/company_research.py`, `tools/calibrate_apps_rg_overfit_threshold.py`, `artifacts/_jd_extract_smoke.py`). Both stale files deleted. 14/14 wizard tests still pass; non-TTY hard-fail preserved. | (closed) |
| W2 | apps_research synthesis cascade — OpenAI + Anthropic tiers | ⏭ SKIPPED again 2026-05-06 — user reaffirmed "apps_research only Gemini". | User authorizes adding cloud cascade tiers beyond Gemini. |
| W3 | Always-on promotion of `apps-rg-interactive-discipline.md` (model_decision → always_on) | ✅ DONE 2026-05-06. Rule trimmed 7,123 → 4,701 bytes (2,422b saved via table conversions + prose compression). Promoted to `trigger: always_on`. Gate passes: 49,625 / 51,200 bytes (1,575b headroom). | (closed) |
| W4 | Sibling-app interactive wizards — **apps_lic scoped in dedicated plan** | ⏸ DEFERRED to dedicated plan `app-wizard-lic-scope-capture-f8d3e1.md`. User identified apps_lic as needing wizard; scoped but not designed. Other apps (apps_underwriting_ai, apps_qna, apps_rfp, apps_research, apps_exec) still lack the "mandatory target inputs + cross-contamination risk" pattern. | User activates `app-wizard-lic-scope-capture-f8d3e1.md` for design + implementation. |

## Phase-Level Summary

| Phase | Scope (files) | Est. Tokens | Pain Points |
|---|---|---|---|
| W1.P1 | `apps_rg/__main__.py`, `apps_rg/integrations/company_research_loader.py`, `apps_rg/integrations/preloaded_input_context_manifest.py`, `apps_rg/l2_recipe/steps.py`, `apps_rg/types/company_research.py`, `apps_rg/scripts/narrative_pass.py`, `ops_scripts/apps_rg/narrative_pass.py`, `agentic_core/runtime/l2_recipe_resolver.py`, `tools/calibrate_apps_rg_overfit_threshold.py`, `artifacts/_jd_extract_smoke.py` (10+ files) | ~600 | Refactor preserves cross-company guard semantics; delete only after grep confirms zero `company_research.json` / `job_description.json` references remain. |
| W2.P1 | `apps_research/engines/company_brief_engine.py`, `.env.example`, new `apps_research/engines/_openai_synthesize.py`, new `apps_research/engines/_anthropic_synthesize.py` (or inline) | ~800 | Two new SDKs (`openai`, `anthropic`); shared cascade-iteration helper to reduce duplication; env vars `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `OPENAI_MODEL`, `ANTHROPIC_MODEL`. |
| W3.P1 | `.windsurf/rules/apps-rg-interactive-discipline.md` frontmatter (1 line); upstream trimming of one always-on rule (varies) | ~150 (rule flip) + ~200-400 (trim work) | Identify which rule to trim or which procedural detail to move to a skill. Run gate before AND after change. |
| W4.P1 | apps_lic wizard — deferred to `app-wizard-lic-scope-capture-f8d3e1.md` | ~2,500 total across 8 phases | Design TBD by user; 3 gaps identified (input classification, target identity field, manifest interaction). |

## Files In Scope

When activated. Plan is capture-only.

## Non-Goals

- Hook-based enforcement of wizard discipline (rejected during initial design)
- Auto-detection of "user explicitly authorized" vs "Cursor Agent inferred" (NLP-hard)
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
