# apps_rg Interactive Wizard + Cursor Agent Discipline Rule

**Slug**: `apps-rg-interactive-wizard-a3e7c1`
**Status**: Completed (2026-05-06)
**Tier**: T2 (cross-cutting: code + behavioral rule)

## Goal

Close the loop on cross-company contamination risk in `apps_rg` by adding (1) an in-app interactive wizard that prompts the user for the 3 mandatory inputs (company, JD title+description, briefing document) when stdin is a TTY and any input is missing, and (2) a Cursor Agent behavioral rule preventing Cursor Agent from auto-filling those flags from inferred context.

## Context (RCA)

User invoked `python -m apps_rg` with no args. Cursor Agent auto-supplied `--target-company "Brown & Brown" --target-role "SVP IT Strategy" --jd apps_rg/scripts/jd_brown_brown_svp_it_strategy.json` based on a JD file committed earlier in the same session and Brown & Brown context from prior C0 brief synthesis testing. The cross-company contamination guard caught the mismatch (stale `company_research.json` was Blend360-targeted) — but only because the stale brief happened to be for a different company. Had both stale files matched the same wrong prior company, the resume would have shipped silently.

User RCA: *"this is not working — always mandatory interactive to prompt three items — can mention what it loaded but cannot auto run"*. Inspection of `apps_rg/__main__.py` revealed strict CLI-arg-driven entry with `parser.error()` hard-fail on missing args, plus a misleading docstring at line 240 falsely claiming `_build_raw_request may have prompted interactively`. No interactive code existed.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status |
|---|---|---|---|---|
| W1 | P1.1, P1.2 | Code-side: TTY-only `_interactive_wizard()` + helper `_read_multiline_or_file()`; fix misleading line-240 docstring | ~600 | ✅ DONE |
| W2 | P2.1 | Behavioral rule `apps-rg-interactive-discipline.md` (model_decision trigger; no always-on cost; no hook) | ~400 | ✅ DONE |
| W3 | P3.1 | Smoke tests (10 surface invariants + non-TTY hard-fail preservation) | ~150 | ✅ DONE |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| P1.1 | Interactive wizard | `apps_rg/__main__.py` | Multiline paste in pwsh; `END` sentinel discipline; preserve non-TTY hard-fail | ~400 | ✅ |
| P1.2 | Docstring debt | `apps_rg/__main__.py:240` | Comment lied for months; updated to describe new wizard | ~50 | ✅ |
| P2.1 | Conditional rule | `.cursor/rules/apps-rg-interactive-discipline.md` | Trigger scope; explicit-override path; defense-in-depth layering | ~400 | ✅ |
| P3.1 | Smoke verification | `test_apps_rg_rule_smoke.py` (transient) | Frontmatter, surface, SSOT location, incident traceability | ~150 | ✅ |

## Files

**Created**:
- `apps_rg/__main__.py` — added `_interactive_wizard(args)` (~110 LOC), `_read_multiline_or_file()` helper, `_WIZARD_JD_PATH` / `_WIZARD_BRIEF_PATH` constants
- `.cursor/rules/apps-rg-interactive-discipline.md` — 97 LOC conditional rule (trigger: `model_decision`)

**Modified**:
- `apps_rg/__main__.py` — fixed misleading line-240 docstring; called wizard after argparse before parser.error

**Commits**:
- `d613a5c18a` — apps_rg interactive wizard for 3 mandatory inputs
- `eb0f8ad2ee` — rules: apps-rg-interactive-discipline (conditional, model_decision)

## Defense-in-Depth (4 layers)

| Layer | Mechanism | Where |
|---|---|---|
| 1. Wizard | TTY-only prompt for 3 inputs | `apps_rg/__main__.py::_interactive_wizard` |
| 2. Cross-company guard | `_assert_artifact_matches_company()` | `apps_rg/__main__.py` |
| 3. Test guard | Cross-company contamination test | `tests/_apps_contract/test_apps_rg_cross_company_contamination_guard.py` |
| 4. Behavioral rule | Pre-emptive Cursor Agent discipline | `.cursor/rules/apps-rg-interactive-discipline.md` |

## Non-Goals

- Hook-based enforcement (heuristic too fragile for single-app concern; conditional rule is sufficient)
- Always-on rule (would consume §33 token budget for app-specific concern)
- Sibling apps (`apps_underwriting_ai`, `apps_qna`, `apps_rfp`, `apps_research`, `apps_lic`, `apps_exec`) — extend rule scope only when those apps adopt similar wizards

## Success Criteria

- ✅ `python -m apps_rg` with no args + TTY stdin prompts for company → JD title+description → briefing
- ✅ `'' | python -m apps_rg` (non-TTY) preserves `parser.error()` hard-fail (CI-safe)
- ✅ Wizard writes to `_interactive_jd.json` / `_interactive_brief.json` (not stale default files)
- ✅ Cross-company guard validates wizard outputs with freshly-typed company name
- ✅ Conditional rule auto-loads when Cursor Agent about to invoke `python -m apps_rg`
- ✅ 10/10 smoke tests pass (frontmatter, surface, SSOT, incident traceability, etc.)
- ✅ Zero §33 always-on token budget impact

## Pattern Source

Same shape as `plan-location.md`, `ssot-folder-enforcement.md`, `mcp-serialization.md`: pure helper logic + conditional rule + bypass env var (none needed here — wizard's TTY check is the bypass) + durable test surface.

## Constitutional Cross-Reference

- §6 (Author-Gate for ambiguous decisions — "which company is this resume for?" is canonical ambiguous decision)
- §18 (no hidden scope expansion)
- §33 (two-tier compliance — rule kept conditional, not always-on)

## ADG Graph Layer Evidence

Not applicable — this is a single-app behavioral hardening, not a refactoring touching cross-layer dependencies. No `mv_*` / semantic edges / P-views queried; ADG would not surface a hotspot here because the issue is interaction-discipline, not structural.

## Notion Registration

- Database: Plans DB (`6aba34d9-4d0b-4f4c-b956-b2bdea541ca9`)
- Status: `Completed` (option id `3a59faae-e327-4258-a4d3-82c835ff830d`)
- AI Summary: bullet-style per `notion-plans-taxonomy.md` invariant (mandatory for Status ∈ {Live, Draft, Completed})
- Exists On Disk: true
- Plan File Path: `.cursor/plans/apps-rg-interactive-wizard-a3e7c1.md`
