---
slug: relocate-plans-ssot-outside-claude-c1a17d
status: Completed
plan_type: governance_change
dod_exempt: false
---

# Relocate Plans SSOT Out of `.claude/` → repo-root `plans/`

## Context (SCQA)

- **Situation:** Plan markdown lives under `.claude/plans/`. Plans are edited very frequently.
- **Complication:** Claude Code (≥ v2.1.78) enforces a **hardcoded anti-tampering guard over the entire `.claude/` directory**. Editing anything under `.claude/` triggers a "sensitive file" permission prompt that is NOT suppressible by `permissions.allow`, `acceptEdits`, or `bypassPermissions`. Plans are non-sensitive markdown, yet every plan edit prompts. Confirmed via RCA + web (anthropics/claude-code issues #38806, #39523, #50055, #61860).
- **Question:** Where should plans live, and how do we relocate without breaking the plan-governance enforcement chain?
- **Answer:** Move the SSOT to **repo-root `plans/`** (outside `.claude/`, so no guard). **Forward-only**: new plans land in `plans/`; existing `.claude/plans/**` (incl. `_archive/`) remain valid. Every plan-scanning surface accepts BOTH dirs (union) during transition; only the write-target flips to `plans/`.

Claude Code has **no native concept of "plans"** — `.claude/plans/` was purely a repo convention, so nothing in Claude Code requires it. Only `settings.json`, `skills/`, `agents/`, `commands/`, `hooks/` are Claude-native under `.claude/`.

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | P1 | Authority: rules + CLAUDE.md declare `plans/` canonical, `.claude/plans/` legacy-valid | ~6k | Forward-only dual-accept | ✅ DONE | Rules name `plans/<slug>-<6hex>.md` as SSOT |
| W2 | P2 | Enforcement: 6 gates + pre-commit filters + creation default accept both dirs | ~8k | Gates glob a dir | ✅ DONE | Gates scan `plans/` ∪ `.claude/plans/`; new plans write to `plans/` |
| W3 | P3 | Governance hooks accept both dirs | ~5k | Hooks hardcode path | ✅ DONE | Plan hooks recognize `plans/` |
| W4 | P4 | Verify: new plan in `plans/` passes gates; existing plans still pass | ~3k | — | ✅ DONE | Both locations green (compileall exit 0; PLAN-DOD/WAVE-TOP exit 0; new-plan-found=True) |

### Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| P1 | Authority rules | `plan-location.md`, `constitutional.md`, `ssot-folder-enforcement.md`, `plan-registration-enforcement.md`, `claude-config-lookup.md`, `memory-notion-writeback.md`, `CLAUDE.md`, `plan-governance/SKILL.md` | `.claude/` edits prompt (one-time) | ~6k | In Progress |
| P2 | Enforcement gates + config | 6× `check_plan_*.py`, `.pre-commit-config.yaml`, `plan_creation_helper.py` | prompt-free (outside `.claude/`) | ~8k | Not started |
| P3 | Governance hooks | `_plan_registration.py`, `_plan_lifecycle.py`, registration/scope/lifecycle hooks hardcoding `.claude/plans/` | `.claude/` edits prompt | ~5k | Not started |
| P4 | Verification | dummy plan + gate runs | — | ~3k | Not started |

## Design — dual-accept (forward-only)

Canonical for NEW writes: `plans/<slug>-<6hex>.md`. Legacy (still valid, read-only growth): `.claude/plans/**` incl. `_archive/`.

Every scanner that currently does `PLANS_DIR = REPO_ROOT/".claude"/"plans"; PLANS_DIR.glob("*.md")` becomes a union over `[REPO_ROOT/"plans", REPO_ROOT/".claude"/"plans"]`. Slug→path resolvers prefer `plans/` then fall back to `.claude/plans/`. Pre-commit `files:` regexes become `^(plans|\.claude/plans)/.*\.md$`.

## Definition of Done

| # | Criterion | Verify / Defer |
|---|-----------|----------------|
| 1 | `plan-location.md` declares `plans/<slug>-<6hex>.md` canonical; `.claude/plans/` documented legacy-valid | Verify: read rule |
| 2 | `constitutional.md` §31/§36 + `CLAUDE.md` reference `plans/` | Verify: grep |
| 3 | `plan_creation_helper.py` default path → `plans/{slug}.md` | Verify: unit/smoke |
| 4 | 6 `check_plan_*.py` gates scan both dirs | Verify: run each gate, exit 0 |
| 5 | pre-commit `files:` filters match both dirs | Verify: grep regex |
| 6 | A new plan written to `plans/` passes format/wave/DoD gates | Verify: smoke run |
| 7 | An existing `.claude/plans/*.md` still passes (no regression) | Verify: gate run |
| 8 | Governance plan hooks recognize `plans/` | Verify: targeted run |

Verification-vs-Deferral: existing plan file relocation + Notion `Plan File Path` rewrites are DEFERRED (forward-only). Historical `tools/notion/plan_notion_sync_*.py` one-offs are OUT OF SCOPE (they cite closed plans).
