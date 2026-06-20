---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\wave-status-completion-enforcement-d4f8e2.md'
original_relative_path: '_archive\\2026-05\\wave-status-completion-enforcement-d4f8e2.md'
source_sha256: bc52aa77c21cbb00c4efbcfe9801ba50ed76fea21605fd50dab8a91f3eace263
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
slug: wave-status-completion-enforcement-d4f8e2
plan_type: infra
dod_exempt: false
---

# Wave Status Completion Enforcement

Implement automated wave status tracking that updates plan sections with ✅ (green check) markers as each wave completes, and syncs to Notion via lifecycle markers.

---

## Context (SCQA)

- **Situation**: The wave lifecycle system (`wave_execution_state.py`, `post_cursor_agent_wave_lifecycle_capture.py`, `wave_lifecycle_writer.py`) captures markers and syncs to Notion. However, the on-disk plan file's Wave Structure table does not automatically update to reflect completed waves.
- **Complication**: Users must manually edit plan files to mark waves complete, creating drift between actual work done and documented state. The Wave Structure table status column (🔲 TODO · 🔄 IN PROGRESS · ✅ DONE) is purely cosmetic without enforcement.
- **Question**: How do we automatically update plan wave status to ✅ DONE when `WAVE_COMPLETE:` markers are emitted, ensuring the on-disk plan reflects actual execution state?
- **Answer**: Extend `post_cursor_agent_wave_lifecycle_capture.py` to not only sync to Notion but also rewrite the plan file's Wave Structure table, flipping status emojis from 🔲/🔄 to ✅ as waves complete.

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| `.cursor/rules/notion-plan-wave-deferral.md` | governing lifecycle marker protocol | ✅ |
| `tools/plan_lifecycle/wave_execution_state.py` | wave state CLI | ✅ |
| `tools/notion/wave_lifecycle_writer.py` | Notion HTTP writer | ✅ |
| `post_cursor_agent_wave_lifecycle_capture.py` | marker capture hook | ✅ |

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Status |
|-------|--------|-------|------------|--------|
| Wave 0 | Baseline | Verify existing lifecycle system | Pre-flight | 🔲 |
| Wave 1 | Parser | Plan file Wave table parser | A | 🔲 |
| Wave 2 | Writer | In-place plan file updater | B | 🔲 |
| Wave 3 | Integration | Hook extension for plan rewrite | C | 🔲 |
| Wave 4 | E2E Test | Full wave complete → ✅ flow | D | 🔲 |

**Total: ~20k tokens across 4 waves**

---

## Out Of Scope

- Notion MCP tool migration (OAuth-hosted variant)
- Backlog Items auto-sync (handled by `post_cursor_agent_deferred_scope_capture.py`)
- Phase-level status tracking (keep at wave granularity)

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| 1.1 | Wave table parser | `tools/windsurf/plan_wave_parser.py`: parse Wave Structure markdown table, extract row status emojis | Markdown table parsing edge cases (multiline cells, emoji width) | ~4k | 🔲 TODO |
| 1.2 | Status flip logic | `tools/windsurf/plan_wave_writer.py`: rewrite specific wave row from 🔲→✅ or 🔄→✅ | Preserving table formatting, column alignment | ~4k | 🔲 TODO |
| 2.1 | File updater | `tools/windsurf/plan_wave_writer.py`: safe read-modify-write with atomic rename | Concurrent edits, Windows file locking | ~3k | 🔲 TODO |
| 3.1 | Hook extension | `post_cursor_agent_wave_lifecycle_capture.py`: call plan writer after Notion sync | Ensure Notion sync succeeds before plan rewrite | ~4k | 🔲 TODO |
| 4.1 | E2E smoke test | Full flow: emit WAVE_COMPLETE → verify plan file has ✅ | Requires temporary test plan file | ~3k | 🔲 TODO |
| 4.2 | Edge case tests | Parser tests: malformed tables, missing wave rows | ~2k | 🔲 TODO |

**Status legend**: 🔲 TODO · 🔄 IN PROGRESS · ✅ DONE · ❌ BLOCKED

---

## Gap Register

**GAP-1: Markdown table parsing complexity**
- Wave Structure tables use GitHub-flavored markdown with emoji cells
- Column alignment markers (`|---|---|`) vary in width
- Multiline cells (wrapped scope descriptions) break naive parsers

**GAP-2: Concurrent modification on Windows**
- Windows file locking prevents atomic rename while file is open
- Plan file may be open in editor during Cursor Agent response

---

## Execution Plan

### Phase 1.1 — Wave Table Parser
**Scope**: Parse plan markdown to extract Wave Structure table rows and their status emojis

**Commands**:
```bash
# Create parser module
python -c "import tools.windsurf.plan_wave_parser"
# Run unit tests
pytest tests/unit/windsurf_scripts/test_plan_wave_parser.py -v
```

**Acceptance**: Parser correctly identifies Wave Structure table, extracts wave numbers and status emojis for all 4 waves

---

### Phase 1.2 — Status Flip Logic  
**Scope**: Generate rewritten markdown with status emoji flipped from 🔲/🔄 to ✅ for completed wave

**Commands**:
```bash
# Test writer module
python -m tools.windsurf.plan_wave_writer --test-rewrite --wave 1
```

**Acceptance**: Writer produces byte-identical table except for target wave's status column

---

### Phase 2.1 — Safe File Updater
**Scope**: Atomic read-modify-write with backup on Windows

**Commands**:
```bash
# Integration test
python -m tools.windsurf.plan_wave_writer --plan wave-status-completion-enforcement-d4f8e2 --wave 1 --dry-run
```

**Acceptance**: Dry-run shows diff; actual run creates `.bak` backup and updates file

---

### Phase 3.1 — Hook Extension
**Scope**: Extend `post_cursor_agent_wave_lifecycle_capture.py` to call plan writer after successful Notion sync

**Commands**:
```bash
# Verify hook wiring
python .cursor/scripts/post_cursor_agent_wave_lifecycle_capture.py --test-mode
```

**Acceptance**: Hook processes markers, writes to Notion, then rewrites plan file

---

### Phase 4.1 — E2E Smoke Test
**Scope**: Full flow verification

**Commands**:
```bash
# Create test plan, run wave 1, verify ✅ appears
python tests/e2e/test_wave_status_auto_update.py
```

**Acceptance**: Test plan Wave 1 status flips to ✅ after WAVE_COMPLETE marker processed

---

## Rules

- Parser must handle emoji width correctly (Python `unicodedata` east_asian_width)
- Writer must preserve all other table content exactly (no reformatting)
- Backup files kept for 7 days, then auto-pruned
- Hook must fail-soft: plan rewrite failure must not block Notion sync

---

## Success Criteria

- [ ] Wave Structure table auto-updates to ✅ when corresponding WAVE_COMPLETE marker emitted
- [ ] Plan file backup created before any modification
- [ ] Parser handles all existing plans in `.cursor/plans/` without error
- [ ] Hook logs plan_rewrite events to `artifacts/cursor/wave_lifecycle_capture.jsonl`

---

## Implementation Commands

```bash
# W0: Baseline verification
python tools/plan_lifecycle/wave_execution_state.py status
python ops_scripts/ci/check_plan_notion_wave_freshness.py

# W1: Parser + Writer development
python -m tools.windsurf.plan_wave_parser --validate-all-plans
python -m tools.windsurf.plan_wave_writer --plan wave-status-completion-enforcement-d4f8e2 --wave 1

# W3: Hook extension
# (Modify post_cursor_agent_wave_lifecycle_capture.py)

# W4: E2E test
pytest tests/e2e/test_wave_status_auto_update.py -v
```

---

## Rollback Strategy

If things go wrong:
1. Restore plan file from `.bak` backup
2. Disable plan rewrite via `WAVE_PLAN_REWRITE_BYPASS=1`
3. Revert hook to prior version

---

## Acceptance Criteria

| Metric | Target | Verification |
|---|---|---|
| Parser accuracy | 100% | All 340+ existing plans parse without error |
| Rewrite safety | Zero data loss | Backup + restore test passes |
| End-to-end latency | <2s | WAVE_COMPLETE marker to ✅ in plan file |

---

## Definition of Done

| # | Criterion | Verification command / evidence | Status |
|---|---|---|---|
| DoD-1 | Wave status auto-updates on WAVE_COMPLETE | `python tests/e2e/test_wave_status_auto_update.py` passes | 🔲 |
| DoD-2 | Parser handles all existing plans | `python -m tools.windsurf.plan_wave_parser --validate-all-plans` exits 0 | 🔲 |
| DoD-3 | ≥15 new unit tests, all green | `pytest tests/unit/windsurf_scripts/test_plan_wave_*.py -v` shows 15+ pass | 🔲 |
| DoD-4 | CI gate green | `python ops_scripts/ci/run_contract_gates.py` exits 0 | 🔲 |
| DoD-5 | Rule + memory writeback | `.cursor/rules/notion-plan-wave-deferral.md` updated with plan rewrite section | 🔲 |

**Verification-vs-Deferral table**:

| Item | Why deferred | Tracked in |
|---|---|---|
| Phase-level status (vs wave-level) | Keep simple; phase tracking adds complexity without clear value | `NEXT_STEP: phase-level status tracking` |
| Real-time plan file watching (editor sync) | Editor-specific, high complexity | `NEXT_STEP: editor-specific file watching` |

---

## Cursor Agent Alignment Checks

- Always-on rules lean; detailed parsing logic in skill/module
- Parser tested against all existing plans before any rewrite
- Fail-soft: plan rewrite errors logged but never block wave execution
