# RCA: Plan Status "In Progress" vs "Not Started"

## Problem Statement
A plan in the Notion Plans DB is marked **"In Progress"** (green) when it should be **"Not Started"** (gray).

---

## Root Cause Analysis

### Status State Machine (Canonical)

```
Not Started (gray) ──► In Progress (green) ──► Completed (blue)
       ▲                    │
       │                    ├──► Waiting (orange) ──►┘
       │                    │      (blocked)
       │                    │
       └── Lower Priority ◄─┘
           (yellow, paused)
```

**Status Flip Triggers:**

| Current Status | Trigger | New Status | Mechanism |
|---|---|---|---|
| **Not Started** | `WAVE_START` marker | **In Progress** | `_wave_lifecycle_helpers.py:272` |
| **Not Started** | `wave_execution_state.py start --plan <slug>` | **In Progress** | Direct HTTP or hook capture |
| **Waiting** | `WAVE_START` marker | **In Progress** | Same as above |
| **In Progress** | `PLAN_COMPLETE` marker | **Completed** | `_wave_lifecycle_helpers.py:287` |

### The Flip Logic

In `tools/notion/_wave_lifecycle_helpers.py`:

```python
_FLIPPABLE_TO_IN_PROGRESS: frozenset[str] = frozenset({
    STATUS_NOT_STARTED,  # "Not Started"
    STATUS_WAITING       # "Waiting"
})

def patch_for_marker(marker, current_status):
    if marker.kind == "wave_start":
        if current_status in _FLIPPABLE_TO_IN_PROGRESS:
            # THIS IS THE FLIP
            props.update(_status_property(STATUS_IN_PROGRESS))
```

**Any `wave_start` marker will flip "Not Started" → "In Progress" automatically.**

---

## Likely Causes (Check These)

### Cause 1: `wave_execution_state.py start` was called prematurely

**Evidence to check:**
```bash
# Look for the START log line
grep "wave-exec.*START plan=<your-slug>" artifacts/windsurf/wave_lifecycle_capture.jsonl
```

**How it happens:**
1. Plan file created
2. Plan registered in Notion (correctly as "Not Started")
3. Someone runs: `python tools/windsurf/wave_execution_state.py start --plan <slug>`
4. This calls `_notion_sync(plan, "wave_start", wave=1)`
5. Status flips to "In Progress"

**Fix:** Don't call `start` until you're actually beginning Wave 1 work.

---

### Cause 2: `WAVE_START` marker was emitted in chat

**Evidence to check:**
```bash
# Look for WAVE_START marker in response logs
grep "WAVE_START.*plan=<your-slug>" artifacts/windsurf/wave_lifecycle_capture.jsonl
```

**How it happens:**
1. Cursor Agent emits: `WAVE_START: plan=<slug> wave=1` in response
2. `post_cursor_agent_wave_lifecycle_capture.py` parses marker
3. Calls `patch_for_marker(marker, current_status="Not Started")`
4. Status flips to "In Progress"

**Fix:** Only emit `WAVE_START` when actually starting work. For plan creation/registration only, use `PLAN_CREATED` marker instead.

---

### Cause 3: Plan created with wrong initial status

**Evidence to check:**
```python
# In the Notion page history, check the initial API-post-page payload
# If it had: "Status": {"select": {"name": "In Progress"}}
# Instead of: "Status": {"select": {"name": "Not Started"}}
```

**How it happens:**
1. Cursor Agent creates plan via `API-post-page`
2. Mistakenly sets `Status` to "In Progress" instead of "Not Started"
3. **This is a bug** — new plans should always be "Not Started"

**Fix:** Manually flip status in Notion UI, or patch via API.

---

### Cause 4: Retrospective plan completed in same turn, then `start` called

**Evidence to check:**
- Plan created and marked "Completed" in same Cursor Agent turn
- Then `wave_execution_state.py start` called on next turn

**How it happens:**
1. Plan created and all work completed immediately (retrospective plan)
2. Notion status = "Completed" (correct)
3. Later, someone calls `start` (mistakenly)
4. `_cmd_start` has guard: `if current_status == "Completed": skip` 
5. **Wait — this should be protected!**

**Check:** Verify the guard is actually working:
```bash
grep "NOTION_SYNC SKIPPED.*status_already_completed" artifacts/windsurf/wave_lifecycle_capture.jsonl
```

If this guard **fired**, the status wouldn't flip. If the status flipped anyway, check if the `current_status` lookup returned `None` (API failure) and the guard didn't trigger.

---

## Diagnostic Commands

### 1. Check current Notion status
```bash
# Requires NOTION_TOKEN
python -c "
from tools.notion._wave_lifecycle_helpers import _current_notion_status
import os
os.environ['NOTION_TOKEN'] = 'your_token_here'
print(_current_notion_status('your-plan-slug'))
"
```

### 2. Check wave lifecycle log
```bash
cat artifacts/windsurf/wave_lifecycle_capture.jsonl | jq 'select(.slug == "your-plan-slug")'
```

### 3. Check if `start` command was run
```bash
grep "wave-exec.*START plan=your-plan-slug" artifacts/windsurf/wave_lifecycle_capture.jsonl
```

### 4. Check for WAVE_START markers
```bash
grep "WAVE_START.*plan=your-plan-slug" artifacts/windsurf/wave_lifecycle_capture.jsonl
```

---

## Prevention Measures

| Measure | Implementation | Status |
|---|---|---|
| **Guard in `start`** | `_cmd_start` checks if status == "Completed" and skips | ✅ EXISTS |
| **Guard in `patch_for_marker`** | Never flip Completed → In Progress | ✅ EXISTS |
| **Pre-flight check** | `pre_user_prompt_plan_registration_surface.py` surfaces pending registrations | ✅ EXISTS |
| **Plan creation discipline** | New plans MUST use "Not Started" | 🔲 ADD TO TEMPLATE |
| **Lint gate** | CI gate checks no "In Progress" plans without wave logs | 🔲 COULD ADD |

---

## Fix Options

### Option A: Manual Notion UI Fix (Immediate)
1. Open the plan in Notion
2. Change Status from "In Progress" → "Not Started"
3. **Risk:** If `start` command or `WAVE_START` marker fires again, it will flip back

### Option B: Prevent Re-flip (Correct)
1. Identify what triggered the flip (`start` command or `WAVE_START` marker)
2. Remove/avoid that trigger
3. Manually reset status in Notion

### Option C: API Patch (Scripted)
```python
# Patch status back to Not Started
python -c "
import os
from tools.notion._wave_lifecycle_helpers import _notion_patch_status_and_waiting_for

os.environ['NOTION_TOKEN'] = 'your_token'
result = _notion_patch_status_and_waiting_for(
    'your-plan-slug',
    'Not Started',  # Reset to correct status
    None,  # No Waiting For
    os.environ['NOTION_TOKEN']
)
print(result)
"
```

---

## Which Plan Is Affected?

The user didn't specify which plan has the wrong status. To proceed with a fix, I need:

1. **Plan slug** (e.g., `fix-rules-notion-drift-c4e7b2`)
2. **Expected status** ("Not Started")
3. **Current status** ("In Progress")

Then I can:
- Check the lifecycle logs
- Identify the trigger
- Apply the correct fix
- Verify the outcome
