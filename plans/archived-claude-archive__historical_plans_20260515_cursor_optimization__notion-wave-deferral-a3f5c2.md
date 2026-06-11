---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\notion-wave-deferral-a3f5c2.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\notion-wave-deferral-a3f5c2.md'
source_sha256: 31de5d7a4ac22da775b50ffde88b4ee6c3c21661bc4abfe24c4567bde67c14d0
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Notion Plan-Wave Deferral Enforcement

**Slug:** `notion-wave-deferral-a3f5c2`
**Status:** Completed
**Created:** 2026-05-03
**Owner:** Cascade

## Problem

During multi-wave plan execution, Cascade kept pausing mid-wave to call Notion MCP tools. Because remote MCPs are serialized per constitutional §25, each Notion call stalled the turn and forced the user to manually prompt "next wave" repeatedly, fragmenting execution.

## Goal

Deterministically block Notion MCP calls while a multi-wave plan is actively executing so ALL Notion writes batch at plan completion. Keep a well-documented bypass for exceptional mid-plan reads.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | P1–P5 | Single-wave implementation + tests + smoke | ~6k | Session-scoped state via VSCODE_PID matches existing `pre_mcp_gate` convention | Completed | 13/13 unit tests pass; end-to-end smoke: blocked when active, allowed after complete, bypass env respected |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|--------------|-------------|-------------|--------|
| P1 | Shared state helper | `.windsurf/scripts/_wave_execution_state.py` | Session isolation across IDE windows | ~1k | Completed |
| P2 | CLI wrapper | `tools/windsurf/wave_execution_state.py` | — | ~1k | Completed |
| P3 | Hook integration | `.windsurf/scripts/pre_mcp_gate.py` (check_notion_wave_deferral) | Fail-open on helper import failure; bypass env var | ~1k | Completed |
| P4 | Always-on rule | `.windsurf/rules/notion-plan-wave-deferral.md` | Explicit protocol + bypass semantics | ~1k | Completed |
| P5 | Unit + smoke tests | `tests/unit/windsurf_scripts/test_wave_execution_state.py` | Subprocess CLI tests with env-var session pinning | ~2k | Completed |

## Files In Scope

- `@c:\Git\Agentic-Workflow-FRESH\.windsurf\scripts\_wave_execution_state.py`
- `@c:\Git\Agentic-Workflow-FRESH\tools\windsurf\wave_execution_state.py`
- `@c:\Git\Agentic-Workflow-FRESH\.windsurf\scripts\pre_mcp_gate.py`
- `@c:\Git\Agentic-Workflow-FRESH\.windsurf\rules\notion-plan-wave-deferral.md`
- `@c:\Git\Agentic-Workflow-FRESH\tests\unit\windsurf_scripts\test_wave_execution_state.py`

## Verification Evidence

- `python -m pytest tests/unit/windsurf_scripts/test_wave_execution_state.py -v` → 13 passed
- Smoke 1 (active plan → blocked): `pre_mcp_gate.py` returned exit 2 with actionable message naming the active plan and the `complete` command
- Smoke 2 (after `complete` → allowed): same Notion tool call returned exit 0
- Smoke 3 (bypass env): `NOTION_WAVE_DEFERRAL_BYPASS=1` with active plan → exit 0 as designed

## Design Notes

- **Pattern**: single-helper + two-consumers (CLI + hook), same shape as `ssot-folder-enforcement.md` and `plan-location.md`
- **Session isolation**: `VSCODE_PID` env var (fallback `os.getppid()`) → per-IDE-window state file at `artifacts/windsurf/wave_execution_<session>.json`
- **Fail-open guards**: malformed JSON, missing state file, missing helper module → allow (never brick Notion globally)
- **Bypass**: `NOTION_WAVE_DEFERRAL_BYPASS=1` for rare exceptional mid-plan reads

## References

- Constitutional §25 (MCP serialization — remote MCPs one per response)
- `.windsurf/rules/mcp-serialization.md` (remote MCP allowlist)
- `.windsurf/rules/plan-location.md` (plan SSOT + table shape)
- `.windsurf/rules/notion-plan-wave-deferral.md` (this plan's authored rule)

## Gap Register

None — all waves and phases completed.
