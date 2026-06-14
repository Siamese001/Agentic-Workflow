
<!-- Converted from `.claude/rules/plan-location.md`. Original Cursor trigger: `always_on`. -->

> See `CLAUDE.md` for shared retrieval / enforcement guidance.

# Plan Rules — Location, Format, and Overwrite

## SSOT Location

New plans MUST be saved to the canonical location:

```
plans/<descriptive-name>-<6hex>.md
```

- ✅ ALWAYS (new plans): the **primary checkout's** `plans/` folder — `C:\Git\Agentic-Workflow-FRESH\plans` (absolute). **No exceptions.** Even when working in a per-chat worktree, the plan file MUST land in the primary checkout's `plans/`, NOT the worktree's copy.
- ✅ LEGACY (still valid): `.claude/plans/<filename>.md` and `.claude/plans/_archive/**`. Existing plans there remain authoritative — do **not** mass-migrate (forward-only; plan `relocate-plans-ssot-outside-claude-c1a17d`).
- ❌ NEVER: a per-chat worktree's `plans/` (e.g. `.chat-worktrees/chat-*/plans/`), `docs/reports/plans/`, `C:\Users\amita\.cursor\plans\`, anywhere else.

**Why the primary checkout, no exceptions:** plans are a shared, always-on SSOT — not per-chat feature work. The worktree-per-chat workflow routes code edits into an ephemeral worktree that is reaped after merge (or abandoned unmerged); a plan written there never reaches the canonical SSOT. So `plans/**` is **exempt from the worktree-per-chat edit guard** (`before_file_edit_branch_guard._is_plan_file`) and plan writes always target the primary checkout's `plans/` regardless of branch. Feature CODE still stays in the worktree.

**Why `plans/` and not `.claude/plans/`:** Claude Code enforces a hardcoded edit-guard over the entire `.claude/` directory that prompts on every edit and cannot be disabled via permissions. Plans are non-sensitive markdown edited frequently, so the SSOT moved to repo-root `plans/` (outside the guard). Claude Code has no native dependency on plan location.

**Plans are disk-only.** There is no Notion plan registration — the windsurf/cursor-era Notion
plan-status / registration / wave-lifecycle enforcement was removed (`notion-wave-enforcement-removal`).
The plan file in `plans/` is the sole record.

**CRITICAL:** `C:\Users\amita\.cursor\plans\` is the IDE user-home directory — it is FORBIDDEN as a plan location. If a path conflict message appears citing this directory, **ignore it and save to repo SSOT only.**

`docs/reports/plans/` is for **evidence and reports only** — never plans.

## When a Plan Is Required

A plan is required when ANY of the following apply:
- Task is T2 or T3 (see constitutional.md Tier Classification)
- Work crosses architectural layers
- Output has irreversible side effects (deletion, migration, schema change)
- Scope is ambiguous or has multiple valid approaches

A plan is NOT required for T0/T1 work, single-file single-concern changes, typo fixes, or pure questions.

## Format Requirements

Before writing any execution plan:

1. Read template: `.claude/templates/execution-plan-template.md`. New plans MUST carry `plan_format: v2` in frontmatter (the template includes it). This marker is the **enforce-going-forward switch**: v2 plans are *blocked* on a format violation; pre-existing plans without the marker stay advisory (grandfathered — no retroactive churn).
2. **Summary tables at top (required placement):** Immediately after Context (SCQA), add `## Status Tables` containing BOTH a `### Wave Progress` table AND a `### Phase Progress` table — **before** any `## Wave N` detail section. Do not bury them under `## Execution Waves` or after architecture sections. (v2: WS-TOP-1..6 + WS-PHASE-1/2/3.)
3. **Canonical columns:** Wave summary = `| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |` (v2 requires the full set — WS-TOP-7 FAIL; ≥1 `W#` row). Phase summary = at minimum Phase + Status columns, ≥1 row (richer Title/Scope/Tokens encouraged).
4. **Waves in execution order (required):** number waves W1 → W2 → W3 … in the order they will run. Detail sections MUST appear in ascending order, and a wave may only depend on a **lower-numbered** wave. Never "7 waves, then W3 before W1" — if B must run before A, B gets the lower number. (v2: WS-ORDER-1 ascending headings, WS-ORDER-2 no dependency on a higher-numbered wave, WS-ORDER-3 no "W_a before W_b" with a>b.)
5. Token estimates are self-reported sizing heuristics only (not budget gates). Mark uncertain estimates with `~`.
6. Include a **`## Definition of Done`** section with at least 5 DoD rows + Verification-vs-Deferral table. Plans touching an executable surface MUST have a smoke-run DoD row (`python -m <module> [args]` exits 0). Use `dod_exempt: true` frontmatter for RCA/doc/observational plans. Enforced by CI gate `check_plan_definition_of_done.py` (PLAN-DOD).

Enforcement (shared validator `ops_scripts/ci/plan_wave_summary_top.py` → `validate_plan_format`): `check_plan_wave_summary_top.py` (PLAN-WAVE-TOP — **blocking for `plan_format: v2`**; advisory for legacy unless `PLAN_WAVE_SUMMARY_TOP_FAIL_CLOSED=1`), `check_plan_format_compliance.py` (per-path strict), `.claude/hooks/after_file_edit.py` (**blocks v2 violations at write time**; legacy warn unless `PLAN_WAVE_SUMMARY_TOP_HOOK_STRICT=1`), `post_agent_plan_wave_summary_audit.py` (post-agent). Bypass: `PLAN_WAVE_SUMMARY_TOP_BYPASS=1`.

A v2 plan missing the top Wave **or** Phase summary table, using non-canonical wave columns, ordering waves out of execution sequence, or missing `## Definition of Done` (without `dod_exempt: true`) is **invalid — it is blocked at write time and in CI** (disk-side lint only; there is no Notion status to mark).

## Overwrite Default

When updating an existing plan: **silently overwrite** the plan file (`plans/<filename>.md`, or its legacy `.claude/plans/<filename>.md` location) — no Author-Gate prompt, no confirmation request.
