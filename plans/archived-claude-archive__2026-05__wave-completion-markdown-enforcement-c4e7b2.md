---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\wave-completion-markdown-enforcement-c4e7b2.md'
original_relative_path: '_archive\\2026-05\\wave-completion-markdown-enforcement-c4e7b2.md'
source_sha256: fb42b85c9a7530b0aca65e2a6da4d3d51db4820cad2223cc229d86985425305a
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: wave-completion-markdown-enforcement-c4e7b2
plan_type: governance
---

# Enforce Plan Markdown Updates At End Of Every Wave

Ensure that every wave completion triggers both an on-disk plan `.md` status update and a Notion Plans DB sync, with CI enforcement to catch violations.

---

## Context (SCQA)

- **Situation** — The infrastructure for plan-wave auto-sync already exists: `post_cursor_agent_wave_lifecycle_capture.py` parses `WAVE_COMPLETE:` markers and calls `_plan_wave_table_updater.py` (updates `.md` tables) + `wave_lifecycle_writer.py` (patches Notion). CI gate NP4 (`check_plan_notion_wave_freshness.py`) detects skew. The wave table updater maps `WAVE_COMPLETE:` → `✅ DONE` in the Wave Structure table.
- **Complication** — Cursor Agent does not always emit the required `WAVE_COMPLETE:` marker at wave boundaries. When this happens, the plan `.md` file stays stale (waves still show `🟢` or no status token), Notion Summary is not appended, and NP4 flags skew after 7 days. The gap is in Cursor Agent behavior discipline, not in tooling.
- **Question** — How do we enforce that Cursor Agent always emits `WAVE_COMPLETE:` (and `WAVE_START:`) markers at wave boundaries so both on-disk and Notion stay synchronized?
- **Answer** — Add an always-on rule requiring markers at wave boundaries, a post-cursor-agent audit hook to detect missing markers when wave-like work is done, and a pre-wave-start gate that checks the prior wave was marked complete before the next wave begins.

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| `.cursor/scripts/post_cursor_agent_wave_lifecycle_capture.py` | Existing marker parser + Notion/disk writer | ✅ Read |
| `tools/windsurf/_plan_wave_table_updater.py` | On-disk `.md` table status update logic | ✅ Read |
| `tools/plan_lifecycle/wave_execution_state.py` | CLI for start/complete/wave-progress | ✅ Read |
| `ops_scripts/ci/check_plan_notion_wave_freshness.py` | NP4 backstop gate | ✅ Read |
| `.cursor/rules/notion-plan-wave-deferral.md` | Existing wave lifecycle rule | ✅ Read |

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Rule + hook + gate | Always-on rule, post-cursor-agent audit hook, pre-wave-start gate | A | ~15K 🟢 |

**Total: ~15K tokens, 1 wave, GREEN**

---

## Out Of Scope

- Modifying existing `_plan_wave_table_updater.py` logic (works correctly when triggered)
- Modifying existing `post_cursor_agent_wave_lifecycle_capture.py` (works correctly when markers present)
- Changing the NP4 backstop gate threshold
- Retroactively fixing plans that are already stale

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| 1.1 | Always-on rule | `.cursor/rules/wave-completion-discipline.md` | Must be concise (§33 budget) | ~3K | 🟢 |
| 1.2 | Post-cursor-agent audit hook | `.cursor/scripts/post_cursor_agent_wave_completion_audit.py` | Detect wave-like work without markers | ~6K | 🟢 |
| 1.3 | Hook registration | `.cursor/hooks.json` | Add new hook entry | ~1K | 🟢 |
| 1.4 | Pre-wave-start gate in `wave_execution_state.py` | `tools/plan_lifecycle/wave_execution_state.py` | Refuse to start W(N+1) if W(N) not marked | ~3K | 🟢 |
| 1.5 | Verification | Run hooks, test with/without markers | — | ~2K | 🟢 |

---

## Gap Register

| Gap ID | Risk | Mitigation |
|---|---|---|
| GAP-1 | False positives in audit (Cursor Agent does wave-like work but plan is T1/no waves) | Audit only fires when active plan is in-progress per `_wave_execution_state.py` |
| GAP-2 | Token budget for always-on rule | Keep rule < 1KB (§33 compliant) |

---

## Execution Plan

### Wave 1 — Rule + Hook + Gate

**Phase 1.1 — Always-on rule**

New file: `.cursor/rules/wave-completion-discipline.md`

Trigger: `always_on` (but minimal, under §33 budget)

Content (enforces):
1. At the end of every wave (when all phases in a wave are done), Cursor Agent MUST emit:
   ```
   WAVE_COMPLETE: plan=<slug-6hex> wave=<N> note="<succinct summary>"
   ```
2. Before starting any wave (first edit of a new wave), Cursor Agent MUST call:
   ```
   python tools/plan_lifecycle/wave_execution_state.py start --plan <slug-6hex>
   ```
   (only needed once per plan, not per wave)
3. When all waves are done, Cursor Agent MUST emit:
   ```
   PLAN_COMPLETE: plan=<slug-6hex> note="<final outcome>"
   ```
4. These markers trigger automatic updates to both the plan `.md` file (Wave Structure table status cells) and Notion Plans DB (Summary column append + Status field).

---

**Phase 1.2 — Post-cursor-agent audit hook**

New file: `.cursor/scripts/post_cursor_agent_wave_completion_audit.py`

Logic:
1. Read `_wave_execution_state` to find the currently-active plan (if any)
2. If no active plan → exit 0 (nothing to enforce)
3. Scan the Cursor Agent response for file-write activity in `agentic_core/` or `apps_*/` or `tests/`
4. If substantial file writes detected (≥3 new/modified files) AND no `WAVE_COMPLETE:` marker in response AND no `WAVE_START:` marker → emit advisory warning to stderr
5. Fail policy: OPEN (exit 0 always). Advisory only.
6. Bypass: `WAVE_COMPLETION_AUDIT_BYPASS=1`

This is a heuristic nudge, not a hard block. The hard enforcement comes from:
- NP4 (Notion skew backstop, 7-day threshold)
- The pre-wave-start gate (Phase 1.4)

---

**Phase 1.3 — Hook registration**

Add to `.cursor/hooks.json`:
```json
{
  "command": "python .cursor/scripts/post_cursor_agent_wave_completion_audit.py",
  "working_directory": ".",
  "show_output": true
}
```

---

**Phase 1.4 — Pre-wave-start gate in wave_execution_state.py**

Modify `tools/plan_lifecycle/wave_execution_state.py` `wave-progress` subcommand:
- Before recording `wave-progress --wave N`, check the lifecycle log for a `WAVE_COMPLETE` entry for wave `N-1` (if N > 1)
- If prior wave has no completion entry, emit a WARNING (not a block) indicating the prior wave was never marked complete
- This creates an advisory "you forgot to close the last wave" signal

---

**Phase 1.5 — Verification**

1. Emit `WAVE_COMPLETE: plan=wave-completion-markdown-enforcement-c4e7b2 wave=1 note="rule, hook, gate added"`
2. Verify `_plan_wave_table_updater` would update Wave 1 status in this plan's `.md`
3. Verify Notion Summary would be appended (via lifecycle log entry)

---

## Rules

- Markers must be bare lines (start of line, regex anchor `^`)
- `note="..."` is strongly recommended but not gated
- Plan `.md` Wave Structure table uses `🟢` or `🔲 TODO` for pending, `🔄 IN PROGRESS` for active, `✅ DONE` for complete
- The hook updates `.md` status cells automatically — Cursor Agent should NOT manually edit the status column

---

## Rollback Strategy

1. Remove hook entry from `hooks.json` → audit stops running
2. Set `WAVE_COMPLETION_AUDIT_BYPASS=1` → audit hook skipped
3. Set `WAVE_TABLE_UPDATE_BYPASS=1` → `.md` updates skipped
4. Set `WAVE_LIFECYCLE_CAPTURE_BYPASS=1` → entire marker capture chain skipped

---

## Acceptance Criteria

| Criterion | Expected | Verification |
|---|---|---|
| Always-on rule exists | `.cursor/rules/wave-completion-discipline.md` present and under 1KB | File size check |
| Audit hook fires on wave work without markers | Advisory warning emitted | Manual test |
| Audit hook silent when markers present | No output | Manual test |
| `.md` table updated on WAVE_COMPLETE marker | Status cell → `✅ DONE` | Lifecycle capture hook test |
| Notion Summary appended on WAVE_COMPLETE marker | `[Wave-Log <ts>] W{N} DONE` in Summary | Lifecycle log entry |
| wave-progress warns on missing prior wave | WARNING emitted when W(N) starts without W(N-1) complete | CLI test |

---

## Definition of Done

| # | Criterion | Verification command / evidence | Status |
|---|---|---|---|
| DoD-1 | Rule file exists and < 1KB | `wc -c .cursor/rules/wave-completion-discipline.md` | 🔲 |
| DoD-2 | Hook registered in hooks.json | `grep wave_completion_audit .cursor/hooks.json` | 🔲 |
| DoD-3 | Hook runs without error | `python .cursor/scripts/post_cursor_agent_wave_completion_audit.py` exits 0 | 🔲 |
| DoD-4 | wave-progress warns on missing prior | `python tools/plan_lifecycle/wave_execution_state.py wave-progress --plan test --wave 2` warns | 🔲 |
| DoD-5 | WAVE_COMPLETE marker emitted for this plan | Present in this response | 🔲 |

---

## Verification-vs-Deferral

| Item | Verified This Plan | Deferred |
|---|---|---|
| Rule content | ✅ | — |
| Hook logic | ✅ | — |
| Retroactive fix of stale plans | — | ✅ (separate maintenance task) |
| NP4 threshold tuning | — | ✅ (if needed based on data) |

---

## Cursor Agent Alignment Checks

- Keep always-on rules lean; place detailed procedures in skills or workflows.
- Retrieve local or scoped evidence before synthesis.
- Reserve deterministic enforcement for hooks or scripts, not template prose.
