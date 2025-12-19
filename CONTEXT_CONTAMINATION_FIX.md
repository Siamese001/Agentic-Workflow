# Context Contamination Fix - December 19, 2025

## Problem Diagnosis

The validator was stuck in a hallucination loop:
- Round 1: Model generates code with `import base` (hallucination)
- Round 2: Model sees its own bad code in history, repeats `import base`
- Round 3: Token count explodes (6k → 22k → 30k+), model drowns in failed attempts

## Root Causes

1. **Temperature Too High (1.0)**: Encouraged "creativity" leading to fake imports
2. **Weak Negative Constraints**: Model didn't understand `base`, `context` don't exist
3. **Contaminated History**: Failed attempts with hallucinations stayed in chat history
4. **No History Reset**: By Round 3, 30k+ tokens of bad examples poisoned the context

## Fixes Applied

### 1. Lower Temperature (Line 469)
```python
temperature=0.4,  # Lower temp for literal, deterministic code fixes
```
**Why**: Prevents hallucination of fake imports. Lower temp = more literal, less creative.

### 2. Stronger Negative Constraints (Lines 450-454)
```python
CRITICAL CONSTRAINTS:
1. NEVER use 'import base', 'import context', 'import L3_orchestration', or 'import conversational_repair'
2. These modules DO NOT EXIST in this codebase: base, context, L3_orchestration, conversational_repair
3. ONLY use imports from Python standard library (os, sys, pathlib, etc.) or imports that exist in the provided code
4. If you need a utility, use fully qualified paths like 'from agentic_workflow.runtime.shared import ...'
```
**Why**: Explicitly tells model these modules don't exist, not just "forbidden".

### 3. Chat Session Reset on Round 3 (Lines 479-484)
```python
# CRITICAL: Reset session on Round 3 to clear contaminated history (30k+ tokens)
if round_num >= 3 and chat_key in self.chat_sessions:
    print(f"      🔄 Round {round_num}: Resetting chat session to clear contaminated history", flush=True)
    del self.chat_sessions[chat_key]
    if file_path in self.conversation_history:
        self.conversation_history[file_path] = []
```
**Why**: Clears 30k+ tokens of contaminated history, gives model fresh start.

### 4. Round Number Tracking (Line 443)
```python
async def resilient_mutation(self, agent_name: str, task: str, code: str, file_path: str = None, round_num: int = 1) -> str:
```
**Why**: Enables round-aware logic (reset on Round 3).

## Expected Behavior After Fix

### Before
```
Round 1: import base (6k tokens)
Round 2: import base (22k tokens - sees own mistake)
Round 3: import base (30k tokens - drowning in bad examples)
Round 4: import base (40k tokens - completely stuck)
Round 5: FAILED
```

### After
```
Round 1: import base (6k tokens)
Round 2: import base (12k tokens - still has history)
Round 3: 🔄 RESET → Fresh start with clean history
Round 3: Correct code (8k tokens - no contamination)
Round 4: SUCCESS
```

## Key Improvements

1. **Temperature 0.4**: More deterministic, less hallucination
2. **Explicit "DO NOT EXIST"**: Model understands these aren't just forbidden, they're fake
3. **Round 3 Reset**: Clears contaminated history before it's too late
4. **Stronger Constraints**: Multiple ways to tell model not to hallucinate

## Testing

Run validator with:
```bash
python apps_shared\canon_validator_v2_agentic.py --target . --heal
```

Watch for:
- ✅ Lower token counts (should stay under 15k per round)
- ✅ No repeated `import base` after Round 3 reset
- ✅ "🔄 Resetting chat session" message on Round 3
- ✅ Successful healing within 5 rounds

## Files Modified

- `apps_shared/canon_validator_v2_agentic.py`:
  - Line 443: Added `round_num` parameter
  - Line 447-463: Stronger negative constraints
  - Line 469: Temperature 0.4 (was 1.0)
  - Line 479-484: Round 3 reset logic
  - Line 755: Pass `round_num` to mutation call
