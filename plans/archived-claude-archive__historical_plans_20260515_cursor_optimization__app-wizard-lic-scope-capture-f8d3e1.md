---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\app-wizard-lic-scope-capture-f8d3e1.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\app-wizard-lic-scope-capture-f8d3e1.md'
source_sha256: 795eaf25ff59aa774a7fa41c24a8860fa0c241f774c0c3b84936d05b787c1f89
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: app-wizard-lic-scope-capture-f8d3e1
plan_type: tracker
---

# W4 Scope Capture — apps_lic Interactive Wizard

**Capture-only plan** — User will design later. This document scopes the work for implementing an interactive wizard in `apps_lic` similar to `apps_rg`'s pattern.

---

## Context (SCQA)

**Situation**: `apps_lic` currently has 9 optional CLI args (`--recipient-class`, `--channel`, `--outreach-mode`, `--manifest-id`, `--manifest-hash`, `--policy-hash`, `--blueprint-hash`, `--request-id`, `--artifact-dir`), all with empty-string defaults. Unlike `apps_rg`, there are no mandatory target inputs that risk cross-company contamination. The wizard pattern from `apps_rg` (commit `d613a5c18a`) established:
- TTY-only `_interactive_wizard()` prompting for 3 mandatory items
- `_interactive_*.json` file writes
- `_assert_artifact_matches_company()` cross-company guard
- `apps-rg-interactive-discipline.md` always-on rule (promoted W3)

**Complication**: `apps_lic` generates professional outreach drafts. Target recipient/context selection carries similar contamination risk if wrong inputs are auto-selected. The existing 9 optional args may need wizard-managed defaults to prevent stale/outdated context from silently poisoning outreach generation.

**Question**: How do we extend the `apps_rg` wizard pattern to `apps_lic` while accounting for its different input model (9 optional args vs 3 mandatory)?

**Answer**: Implement a TTY wizard for `apps_lic` that prompts for the high-leverage inputs (recipient_class, channel, outreach_mode, manifest selection) when stdin is a TTY and critical inputs are missing. Write to `apps_lic/scripts/_interactive_*.json` and add cross-contamination guard.

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| `apps_rg/__main__.py` | Reference wizard implementation (`_interactive_wizard`, `_assert_artifact_matches_company`) | ✅ |
| `apps_rg/scripts/_interactive_*.json` | Output file pattern to mirror | ✅ |
| `apps_lic/__main__.py` | Target for wizard integration (lines 168-210 arg parser) | ✅ |
| `apps-rg-interactive-discipline.md` | Rule to extend scope to apps_lic | ✅ |
| ADG blast radius | Files to update when wizard lands | 🔲 (run at design time) |

---

## Wave Structure

| Wave | Focus | Status |
|---|---|---|
| W1 | Design — mandatory vs optional input classification; wizard UX flow | ⏸ DEFERRED |
| W2 | Implementation — `_interactive_wizard()` in `apps_lic/__main__.py`, `_interactive_*.json` I/O | ⏸ DEFERRED |
| W3 | Guard — cross-contamination validation; discipline rule scope extension | ⏸ DEFERRED |
| W4 | Test — wizard contract tests; contamination guard tests | ⏸ DEFERRED |

**Status**: ⏸ CAPTURE-ONLY — User will design later

---

## Out Of Scope (Until Activated)

- Real implementation of wizard UI
- Cross-company guard logic
- File deletion (no stale files identified yet in `apps_lic/scripts/`)
- Sibling apps beyond apps_lic (apps_qna, apps_rfp, etc.)
- Recipe resolver changes
- Exit eval hook wiring

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| W1.P1 | Input classification | Design doc — which 9 args are wizard-eligible | User intent ambiguity | ~200 | ⏸ DEFERRED |
| W1.P2 | Wizard UX flow | Prompt sequence, validation rules | Overlap with existing manifests | ~300 | ⏸ DEFERRED |
| W2.P1 | `_interactive_wizard()` implementation | `apps_lic/__main__.py` lines 168-210+ | Refactoring parser default handling | ~600 | ⏸ DEFERRED |
| W2.P2 | `_interactive_*.json` persistence | New file I/O in `apps_lic/scripts/` | Directory create, JSON schema | ~300 | ⏸ DEFERRED |
| W3.P1 | Cross-contamination guard | `_assert_artifact_matches_target()` helper | What field defines "target"? | ~400 | ⏸ DEFERRED |
| W3.P2 | Discipline rule scope extension | `apps-rg-interactive-discipline.md` → `apps-lic-interactive-discipline.md` or combined | Rule naming, trigger scope | ~200 | ⏸ DEFERRED |
| W4.P1 | Wizard contract tests | `tests/_apps_contract/test_apps_lic_wizard_contract.py` | Mock TTY, file system isolation | ~400 | ⏸ DEFERRED |
| W4.P2 | Contamination guard tests | `tests/_apps_contract/test_apps_lic_cross_target_contamination_guard.py` | Artifact spoofing, negative cases | ~300 | ⏸ DEFERRED |

**Status legend**: ⏸ DEFERRED · 🔲 TODO · 🔄 IN PROGRESS · ✅ DONE

---

## Gap Register

**GAP-1: Input classification ambiguity**
- `apps_lic` has 9 optional args vs `apps_rg`'s 3 mandatory
- Unclear which args rise to "wizard mandatory" vs "stay optional with empty default"
- **Impact**: Wizard scope undefined; can't implement without design decision

**GAP-2: Target identity field undefined**
- `apps_rg` uses `company` field for cross-company guard
- `apps_lic` has no clear "company" or "recipient identity" field in current args
- **Impact**: Cross-contamination guard needs a target identity to validate against

**GAP-3: Manifest vs wizard interaction**
- `apps_lic` uses `--manifest-id` + `--manifest-hash` for preloaded context
- Wizard may overlap or conflict with manifest loading
- **Impact**: UX flow must resolve manifest vs interactive prompt precedence

---

## Preliminary Rules (Draft)

1. **Mandatory inputs TBD** — User will classify which of the 9 args become wizard-managed
2. **TTTY-only wizard** — Same pattern as apps_rg: `_interactive_wizard(args)` fires when stdin is TTY
3. **`_interactive_*.json` output** — Write to `apps_lic/scripts/_interactive_{recipient,context,manifest}.json`
4. **Cross-target guard** — Validate that loaded artifacts match the intended recipient/target
5. **Cascade discipline** — Extend or duplicate always-on rule to cover `apps_lic`

---

## Success Criteria (When Activated)

- [ ] Wizard prompts for classified mandatory inputs when TTY and missing
- [ ] `_interactive_*.json` files written and read as defaults
- [ ] Cross-target contamination guard prevents stale artifact poisoning
- [ ] Discipline rule blocks Cascade from pre-filling target flags
- [ ] All tests pass; no regressions in non-wizard paths

---

## Constitutional Cross-Reference

- §18 (no hidden scope expansion — captured here, not silently widened)
- §22 (ADG_GRAPH_LAYER_EVIDENCE required when activated)
- §24 (deferred-scope capture — this plan IS the capture artifact)
- §33 (always-on token budget — rule extension must fit)
- §36 (plan must be registered in Notion before activation)

---

## Sibling App Queue

| App | Status | Trigger Condition |
|---|---|---|
| apps_lic | ⏸ CAPTURED THIS PLAN | User activates W4 design |
| apps_qna | ⏸ NOT STARTED | Grows mandatory target inputs |
| apps_rfp | ⏸ NOT STARTED | Grows mandatory target inputs |
| apps_research | ⏸ NOT STARTED | Grows mandatory target inputs |
| apps_underwriting_ai | ⏸ NOT STARTED | Grows mandatory target inputs |
| apps_exec | ⏸ NOT STARTED | Grows mandatory target inputs |

---

## Parent Plan Reference

- Parent: `apps-rg-vllm-followup-blocked-c4e8b2.md` — W4 deferred until sibling app needs wizard
- This plan: Spun out for `apps_lic` wizard scope capture per user direction

---

## Notion Registration

- Database: Plans DB (`6aba34d9-4d0b-4f4c-b956-b2bdea541ca9`)
- Status: `Not Started` (option id `503df59f-85d4-4ac0-baae-e457d0354b6f`, gray)
- AI Summary: Scope capture for apps_lic interactive wizard — 8 deferred phases, 3 gaps identified, activation blocked on user design decision
- Exists On Disk: true
- Plan File Path: `.windsurf/plans/app-wizard-lic-scope-capture-f8d3e1.md`
