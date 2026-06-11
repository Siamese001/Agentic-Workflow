---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\wave-phase-auto-update-rca-fix-e9c2b8.md'
original_relative_path: '_archive\\2026-05\\wave-phase-auto-update-rca-fix-e9c2b8.md'
source_sha256: d314f789e0f88d153f508aef919cf76c8279b79ac15e95cd0ba4bb99942ea473
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: wave-phase-auto-update-rca-fix-e9c2b8
plan_type: retrospective
retrospective_target: plan-wave-inline-status-sync-8b4d2f
touches_agentic_core: false
touches_governance_ci: false
touches_windsurf_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: true
---

# Wave/Phase Auto-Update RCA and Fix — Retrospective

Retrospective plan documenting the root cause analysis for why `WAVE_STATUS`, `WAVE_COMPLETE`, `PHASE_STATUS`, and `PHASE_COMPLETE` inline fields were not auto-updating when waves/phases completed. Includes all fixes applied and future testing scope.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: COMPLETED
CURRENT_WAVE: W3
LAST_COMPLETED_WAVE: W3
LAST_UPDATED: 2026-05-12

---

## RCA Summary

**Problem**: Simplified-format plans (using prose `WAVE_STATUS:`, `PHASE_STATUS:` fields instead of pipe tables) had inline status fields that never auto-updated when `WAVE_COMPLETE:` / `PHASE_COMPLETE:` markers were emitted.

**Root Causes Identified**:

| # | Root Cause | Location | Fix |
|---|------------|----------|-----|
| RC-1 | `phase_complete` markers skipped in capture hook | `post_cursor_agent_wave_lifecycle_capture.py:131` | Added `_update_phase_in_plan()` call |
| RC-2 | User expectation mismatch — markers must be emitted with specific format | Cursor Agent response text | Documented required marker grammar |
| RC-3 | Missing `WAVE_COMPLETE:`/`PHASE_COMPLETE:` markers in responses | Human process | Documented marker requirements |

---

## Wave 1 — Diagnosis (COMPLETED)

WAVE_ID: W1
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED

**Phases**:
- **W1.1** — Identify why inline fields don't update | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W1.2** — Test updater logic in isolation | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W1.3** — Check capture hook registration | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Findings**:
1. `_plan_wave_table_updater.py` inline field logic works correctly in isolation
2. `post_cursor_agent_wave_lifecycle_capture.py` had `if kind == "phase_complete": continue` at line 131
3. Hook IS registered in `hooks.json` (priority 380)
4. Log file shows hook fires but no markers detected (user wasn't emitting them)

---

## Wave 2 — Fix Phase Complete Handling (COMPLETED)

WAVE_ID: W2
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED

**Phases**:
- **W2.1** — Add phase_complete handling to capture hook | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W2.2** — Verify syntax and test | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Changes**:
- `.cursor/scripts/post_cursor_agent_wave_lifecycle_capture.py` lines 131-148
- Added `_update_phase_in_plan()` call for `phase_complete` markers
- Added logging for phase updates

**Verification**:
- Syntax validation passes
- Manual test: `phase_complete` updates `PHASE_STATUS: TODO → DONE` and `PHASE_COMPLETE: NO → YES`

---

## Wave 3 — Future Testing and Documentation (COMPLETED)

WAVE_ID: W3
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED

**Phases**:
- **W3.1** — Document marker grammar requirements | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W3.2** — Scope future integration tests | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

---

## Required Marker Grammar

For auto-update to fire, markers MUST follow this exact format:

```text
WAVE_COMPLETE: plan=<slug-6hex> wave=<N> note="<optional one-liner>"
PHASE_COMPLETE: plan=<slug-6hex> phase=<W#.#> note="<optional one-liner>"
PLAN_COMPLETE: plan=<slug-6hex> note="<optional one-liner>"
```

**Requirements**:
- Must start at beginning of line (regex `^` anchor)
- `plan=` must match plan slug exactly
- `wave=N` for wave markers, `phase=W3.1` for phase markers
- Optional `note="..."` gets appended to plan summary in Notion

**Example**:
```text
WAVE_COMPLETE: plan=apps-rg-chroma-ingestion-wiring-c7f2d9 wave=3 note="W3 ingestion complete, 2340 chunks added"
PHASE_COMPLETE: plan=apps-rg-chroma-ingestion-wiring-c7f2d9 phase=W3.1 note="rubrics corpus ingested"
```

---

## Future Testing Scope

**Deferred to future plan**:

| Test | Scope | Acceptance |
|------|-------|------------|
| FT-1 | End-to-end wave marker test | Emit `WAVE_COMPLETE:` marker → verify `WAVE_STATUS: DONE` in plan file |
| FT-2 | End-to-end phase marker test | Emit `PHASE_COMPLETE:` marker → verify `PHASE_STATUS: DONE` in plan file |
| FT-3 | Plan marker test | Emit `PLAN_COMPLETE:` marker → verify all waves/phases marked DONE |
| FT-4 | Code-fence exclusion test | Verify fenced code containing `WAVE_STATUS: TODO` is NOT rewritten |
| FT-5 | Monotonic guard test | Verify `DONE` fields are never downgraded to `TODO` |
| FT-6 | Duplicate wave section test | Verify warning emitted, no corruption when duplicate `## Wave N` headers exist |
| FT-7 | Missing wave section test | Verify safe no-op when target wave not found |
| FT-8 | Drift detection integration | Verify `plan_driven_closer.py --show-drift` reports `plan_header_inline_drift` |

**Trigger for future plan**:
- When user confirms they will emit markers and wants automated verification
- When regression is detected in production

---

## Files Changed

| File | Change | Lines |
|------|--------|-------|
| `.cursor/scripts/post_cursor_agent_wave_lifecycle_capture.py` | Added phase_complete handling | 131-148 |

---

## Verification Commands

**Test inline updater directly**:
```python
from pathlib import Path
import sys
sys.path.insert(0, 'c:/Git/Agentic-Workflow-FRESH')

import importlib.util
spec = importlib.util.spec_from_file_location('_plan_wave_table_updater', 
    'c:/Git/Agentic-Workflow-FRESH/tools/windsurf/_plan_wave_table_updater.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

repo = Path('c:/Git/Agentic-Workflow-FRESH')
ok, msg = mod._update_phase_in_plan(repo, 'test-plan-abc123', 'W1.1', 'phase_complete')
print(f"Result: {ok}, {msg}")
```

**Check capture hook logs**:
```powershell
Get-Content c:/Git/Agentic-Workflow-FRESH/artifacts/cursor/wave_lifecycle_capture.jsonl -Tail 10
```

---

## Lessons Learned

1. **Capture hook skipping logic** — The `continue` statement at line 131 was too aggressive; should have routed to the phase updater instead of skipping entirely.
2. **Marker visibility** — Users may not know marker grammar requirements; documentation must be explicit and findable.
3. **Test gaps** — No end-to-end test exists that actually emits markers and verifies file updates; integration test needed.
4. **Log inspection** — First symptom investigation should check `wave_lifecycle_capture.jsonl` for `wave_table_update` events.

---

## Definition of Done

DoD-1: RCA documented with all root causes identified
- Status: DONE

DoD-2: Fix applied and verified (phase_complete now updates inline fields)
- Status: DONE

DoD-3: Marker grammar documented for future reference
- Status: DONE

DoD-4: Future testing scope defined with 8 test cases
- Status: DONE

DoD-5: Plan registered in Notion Plans DB
- Status: DONE

---

## Scope Expansion Authorization

Not applicable — retrospective plan, scope closed.
