---
plan_id: notion-supersession-auto-retire-b4e7a1
slug: notion-supersession-auto-retire
created: 2026-06-08
status: Not Started
plan_type: governance_hook_addition
dod_exempt: false
supersedes: []
---

# Notion Supersession Auto-Retire (with comment)

> Make the manual move we just did — flip a superseded predecessor plan to `Retired`
> **and post an explanatory Notion comment** — happen automatically when a superseding
> plan declares the relationship and goes active. Closes the RCA gap: no hook exists
> today that performs cross-plan supersession retirement.

## Context (SCQA)

- **Situation.** Plan `apps-lic-redesign-refactor-plan-v2-consolidated` (Notion-only,
  `Not Started`) was operationally superseded once `apps-lic-30-profile-gap-remediation-a9f3c2`
  went `In Progress`. It had to be retired **by hand**, with the note written manually.
- **Complication.** RCA (this session) found: (1) **no hook** performs cross-plan
  supersession retirement; (2) the only written rule (`notion-plans-taxonomy.md` supersession
  invariant) is **agent-behavioral**, gated on a `## Supersedes` table that the child plan
  never contained; (3) Notion-only / cross-worktree / cross-session plans are invisible to the
  marker-driven lifecycle chain; (4) **no Notion comment writer** exists in governance scripts.
- **Question.** What is the smallest deterministic mechanism that auto-retires a declared
  predecessor — with a comment — and a sweep that catches the cases a live hook structurally
  cannot see?
- **Answer.** A canonical machine-readable `## Supersedes` signal + a fail-soft post-agent hook
  that patches `Status→Retired`, appends the Summary note, and posts a Notion comment + a CI
  sweep gate that flags any declared-but-unretired predecessor. Reuse `plan_driven_closer.py`'s
  Notion HTTP machinery; add only a comment writer.

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| W0 | P0.1, P0.2 | `## Supersedes` signal grammar + template/rule/skill docs | ~6k | Taxonomy rule editable; template is SSOT | Not Started | Grammar documented in template + `notion-plans-taxonomy.md` + `plan-governance` skill |
| W1 | P1.1, P1.2 | Core lib: slug→page_id resolve, predecessor status check, patch-to-Retired, **new comment writer** | ~14k | `plan_driven_closer._notion_request` reusable; Notion token in env | Not Started | Unit tests (mocked Notion) green: retire payload + comment payload shape correct |
| W2 | P2.1, P2.2 | Live hook `post_agent_plan_supersession_retire.py` + Stop-dispatch wiring | ~12k | Stop→`after_agent_governance_dispatch.py` is the dispatch seam | Not Started | Dry-run on synthetic pair logs intended retire+comment; smoke-run exits 0 |
| W3 | P3.1 | CI sweep gate `check_plan_supersession_consistency.py` (catches cross-session misses) | ~8k | `run_contract_gates.py` is the gate registry | Not Started | Sweep flags any `## Supersedes` predecessor still non-terminal |
| W4 | P4.1, P4.2 | Backfill sweep + live E2E proof on throwaway pair | ~9k | Can create/delete a disposable Notion pair | Not Started | Live `--execute` flips predecessor→Retired + posts comment, verified via API read |

### Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| P0.1 | Define `## Supersedes` grammar | `.codex/templates/execution-plan-template.md` | Must be both human-readable + machine-parseable | ~3k | Not Started |
| P0.2 | Doc the trigger | `.codex/rules/notion-plans-taxonomy.md`, `.codex/skills/plan-governance/SKILL.md` | Keep invariant wording aligned with new hook | ~3k | Not Started |
| P1.1 | Resolver + status guard | `.codex/governance/scripts/_plan_supersession.py` (new) | Slug→page_id for Notion-only rows; terminal-status guard | ~7k | Not Started |
| P1.2 | Notion comment writer | `_plan_supersession.py`, reuse `plan_driven_closer._notion_request` | No existing `/v1/comments` writer; idempotent comment de-dup | ~7k | Not Started |
| P2.1 | Post-agent hook | `.codex/governance/scripts/post_agent_plan_supersession_retire.py` (new) | Fail-soft; never block turn | ~7k | Not Started |
| P2.2 | Dispatch wiring + flags | `.codex/hooks/after_agent_governance_dispatch.py` (or `post_agent_dispatch.py`) | Dry-run default, `--execute`, bypass env | ~5k | Not Started |
| P3.1 | CI sweep gate | `ops_scripts/ci/check_plan_supersession_consistency.py` (new), `run_contract_gates.py` | Cross-worktree plan discovery | ~8k | Not Started |
| P4.1 | Backfill sweep | (run only) | Existing plans may declare informal supersession | ~4k | Not Started |
| P4.2 | Live E2E proof | throwaway Notion pair | Cleanup of disposable rows | ~5k | Not Started |

## Gap Register

| ID | Priority | Gap (from RCA) | Required Outcome |
|---|---:|---|---|
| S1 | P0 | No hook performs cross-plan supersession retirement | Post-agent hook patches predecessor `Status→Retired` |
| S2 | P0 | No Notion comment writer in governance scripts | Add `post_supersession_comment()` via `/v1/comments` |
| S3 | P0 | Trigger (`## Supersedes`) is undocumented + unparsed | Canonical grammar in template/rule/skill + parser |
| S4 | P1 | Notion-only / cross-session plans invisible to live hook | CI sweep gate re-derives from all plan files + Notion |
| S5 | P1 | Risk of double-retire / duplicate comments | Idempotency: skip terminal predecessors + existing supersession comment |

## Design (reference, not yet implemented)

**Signal.** Superseding plan body carries:
```markdown
## Supersedes
| Predecessor slug | Reason |
|---|---|
| apps-lic-redesign-refactor-plan-v2-consolidated | design implemented in worktree; tracking moved here |
```
plus optional frontmatter `supersedes: [<slug>, ...]` for fast parsing.

**Live hook** `post_agent_plan_supersession_retire.py` (Stop dispatch chain), per agent response:
1. Detect a plan going active — `WAVE_START:`/`PLAN_CREATED: ... status=In Progress` marker, or a changed plan file whose registered Notion status is `In Progress`.
2. Parse its `## Supersedes` table / `supersedes:` frontmatter → predecessor slugs.
3. Resolve each predecessor → Notion page_id (reuse `_plan_registration` slug index / `fetch_all_open_rows`).
4. If predecessor status ∉ `get_terminal_statuses()` → **patch** `Status→Retired` + append dated Summary note **and** `post_supersession_comment()` linking the successor.
5. **Idempotent + fail-soft:** skip already-`Retired`/`Completed`/`Archived`; skip if a supersession comment already exists; never raise into the turn. Dry-run default; `--execute` to write; `PLAN_SUPERSESSION_RETIRE_BYPASS=1` to disable.

**Reuse:** `plan_driven_closer.py` (`_notion_request`, `fetch_all_open_rows`, `patch_row_done` shape, JSONL `_log`), `_notion_canonical.py` (`get_terminal_statuses`, `validate_status_for_write`, status-id map). **Net-new:** `post_supersession_comment()` (`POST /v1/comments`).

**Backstop sweep** `check_plan_supersession_consistency.py`: scan every plan file (all worktrees in scope) for `## Supersedes`; for each predecessor still non-terminal in Notion, report ERROR — catches the cross-session/cross-worktree cases the live hook structurally cannot observe.

## ADG_HOTSPOT_REPORT

Greenfield governance addition — no existing hotspot is refactored. New files land in
`.codex/governance/scripts/` (hook layer) and `ops_scripts/ci/` (gate layer); zero `agentic_core/`
spine edits, so layer multipliers (L0/L5 ×2.0 etc.) do not apply. Blast radius is confined to the
Stop-dispatch chain and the Plans Notion DB. No `## Supersedes` predecessor → hook is a no-op.

## ADG_GRAPH_LAYER_EVIDENCE

Net-new scripts have no inbound ADG edges yet (not in the current snapshot). The only structural
coupling is **outbound, by reuse**: the new lib imports helpers from `plan_driven_closer.py` and
`_notion_canonical.py` (governance-script layer, not spine). No materialized-view hotspot, semantic
edge, or P-view is mutated; this plan adds a leaf consumer at the governance edge. Full MV/P-view
evidence is N/A for a greenfield leaf and is deferred to the W1 implementation PR's ADG regen.

## Definition of Done

| # | Criterion | Verify by |
|---|---|---|
| 1 | `## Supersedes` grammar documented in template + `notion-plans-taxonomy.md` + `plan-governance` skill | Read the three files; grammar identical |
| 2 | Core lib unit tests green with mocked `_notion_request` — Retire payload + comment payload shapes asserted | `python -m pytest tests/unit/governance/test_plan_supersession.py -q` |
| 3 | Hook registered in Stop dispatch and runs fail-soft (never non-zero into the turn) | Inspect `after_agent_governance_dispatch.py`; dry-run a malformed payload → exit 0 |
| 4 | **Smoke-run:** hook executes on a sample response and exits 0 | `python .codex/governance/scripts/post_agent_plan_supersession_retire.py --dry-run < sample_response.json` → exit 0 |
| 5 | **Live E2E:** `--execute` on a throwaway predecessor/successor pair flips predecessor→`Retired` AND posts a comment | `API-retrieve-a-page` shows `Retired`; `API-get-comments` shows the supersession comment |
| 6 | Idempotency: re-run on already-`Retired` predecessor makes no second patch and no duplicate comment | Re-run `--execute`; JSONL log shows `skipped=terminal`/`skipped=comment_exists` |
| 7 | CI sweep gate wired into `run_contract_gates.py` and runs clean (or lists known misses) | `python ops_scripts/ci/check_plan_supersession_consistency.py` → exit 0/advisory |

### Verification vs Deferral

| Item | Verified in-plan | Deferred |
|---|---|---|
| Retire-payload + comment-payload shape | ✅ W1 unit tests | — |
| Live patch + comment land in Notion | ✅ W4 E2E | — |
| Idempotency / fail-soft | ✅ W2 + W4 | — |
| Cross-worktree predecessor discovery | ✅ W3 sweep | Multi-repo (non-worktree) plan stores → deferred |
| Auto-detecting *informal* supersession (no `## Supersedes`) | — | Deferred — out of scope; declaration is required by design |

## Non-Goals

- Inferring supersession without an explicit `## Supersedes` declaration (RCA root cause #5: that
  needs human judgment — the hook intentionally requires the signal).
- Retiring `Completed`/`Archived` predecessors (terminal; left untouched).
- Any `agentic_core/` spine change.

## Supersedes

_None — net-new plan._
