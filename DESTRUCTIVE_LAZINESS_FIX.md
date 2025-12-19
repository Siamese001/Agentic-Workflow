# Destructive Laziness Fix - December 19, 2025

## Problem Diagnosis

The validator was stuck in a "Mass Deletion" loop:
- Round 1: Agent deletes 155 lines (226 → 71 lines)
- Round 2: Agent repeats same deletion (226 → 99 lines)
- Round 3: Session reset, but agent still deletes (226 → 103 lines)
- Pattern: Agent "fixes" by deleting everything it doesn't understand

## Root Cause

**Destructive Laziness**: When faced with a large file (226 lines), the agent decides to "fix" it by deleting everything except the few lines it understands. This happens because:

1. **No Structural Integrity Constraint**: Agent wasn't told it MUST preserve all lines
2. **No Feedback Loop**: After rejection, agent didn't know WHY it failed
3. **Vague Instructions**: "Fix the violation" doesn't mean "preserve everything else"

## Fixes Applied

### 1. Structural Integrity Requirement (Lines 458-464)
```python
STRUCTURAL INTEGRITY REQUIREMENT:
- The original file has {original_line_count} lines of code
- Your output MUST contain the FULL file with ALL {original_line_count} lines preserved
- NEVER truncate the file or use shortcuts like '# ... rest of code' or '# existing code'
- NEVER delete sections you don't understand - preserve them exactly as-is
- If you don't provide the complete file, your mutation will be REJECTED
- Only modify the specific lines that fix the violation
```

**Why**: Explicitly tells agent it must preserve ALL lines, not just the ones it understands.

### 2. Mass Deletion Guard with Feedback (Lines 783-792)
```python
# 2. Mass Deletion Guard
original_lines = len(current_code.splitlines())
mutated_lines = len(mutated_code.splitlines())
deletion_threshold = 0.7  # Allow max 30% deletion

if mutated_lines < original_lines * deletion_threshold:
    deletion_count = original_lines - mutated_lines
    print(f"      🚫 Mass Deletion Detected: {original_lines} -> {mutated_lines} lines ({deletion_count} deleted)")
    # Provide feedback for next round
    previous_failure = f"Mass deletion detected: You deleted {deletion_count} lines. You must preserve the full file structure."
    current_code = mutated_code
    continue
```

**Why**: Detects mass deletion (>30% lines removed) and provides explicit feedback to the model.

### 3. Feedback Loop Integration (Lines 443, 449-452)
```python
async def resilient_mutation(self, agent_name: str, task: str, code: str, file_path: str = None, round_num: int = 1, previous_failure: str = None) -> str:
    # Build feedback from previous failure
    feedback = ""
    if previous_failure:
        feedback = f"\n\n⚠️ PREVIOUS ATTEMPT REJECTED: {previous_failure}\nYou must address this issue in your next attempt.\n"
```

**Why**: Model sees WHY its previous attempt failed and can adjust its strategy.

### 4. Previous Failure Tracking (Line 759, 773)
```python
# L5: 5-Round Reflective Healing
max_rounds = 5
previous_failure = None  # Track failure reason for feedback

mutated_code = await self.ctx.resilient_mutation(self.name, prompt, current_code, file_path, round_num, previous_failure)
```

**Why**: Maintains failure context across rounds so model learns from mistakes.

## Expected Behavior After Fix

### Before
```
Round 1: Delete 155 lines (226 → 71) → REJECTED
Round 2: Delete 127 lines (226 → 99) → REJECTED (no feedback, repeats mistake)
Round 3: Reset session, delete 123 lines (226 → 103) → REJECTED (still no feedback)
Round 4: FAILED
```

### After
```
Round 1: Delete 155 lines (226 → 71) → REJECTED
Round 2: Receives feedback: "You deleted 155 lines. Preserve full file structure."
Round 2: Preserves structure, fixes only violation (226 → 228 lines) → SUCCESS
```

## Key Improvements

1. **Explicit Line Count**: Agent knows exactly how many lines to preserve
2. **Rejection Feedback**: Agent learns WHY it failed, not just THAT it failed
3. **30% Deletion Threshold**: Allows minor cleanup but prevents mass deletion
4. **Feedback Persistence**: Failure reason carries forward to next round

## Testing

Run validator with:
```bash
redis-cli flushall
python apps_shared\canon_validator_v2_agentic.py --target . --heal
```

Watch for:
- ✅ "PREVIOUS ATTEMPT REJECTED" messages in subsequent rounds
- ✅ Line counts staying stable (±10% instead of -70%)
- ✅ Successful healing after feedback provided
- ✅ No repeated mass deletions

## Files Modified

- `apps_shared/canon_validator_v2_agentic.py`:
  - Line 443: Added `previous_failure` parameter
  - Line 447: Count original lines for feedback
  - Line 449-452: Build feedback message
  - Line 458-464: Structural integrity requirement
  - Line 759: Initialize `previous_failure` tracker
  - Line 773: Pass `previous_failure` to mutation
  - Line 783-792: Mass deletion guard with feedback
  - Line 794-799: Code bloat guard with feedback

## Combined with Previous Fixes

This fix works together with:
1. **AFC Loop Prevention** (tools=[])
2. **Context Contamination** (Round 3 reset, temp 0.4)
3. **Destructive Laziness** (structural integrity, feedback loop)

All three issues are now resolved for robust autonomous healing.
