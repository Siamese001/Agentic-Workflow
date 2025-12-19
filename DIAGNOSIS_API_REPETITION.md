# 🔍 Diagnosis: API Call Repetition Issue

**Date**: December 19, 2025  
**File**: `apps_shared/canon_validator_v2_agentic.py`  
**Issue**: Gemini API calls repeating in 5-round loop without convergence

---

## Root Causes Identified

### 1. **Fresh Chat Session Every Call** ❌
**Problem**: Creating new chat session on each API call
```python
# BEFORE (Line 458-463):
def get_gemini_response():
    chat = self._client.chats.create(  # ← NEW session every time!
        model=os.getenv('GEMINI_MODEL', 'gemini-2.5-flash'),
        history=history,
        config=config
    )
    return chat.send_message(prompt)
```

**Impact**: Model has no memory between rounds. Each round starts fresh, causing repetitive behavior.

---

### 2. **Automatic Function Calling Loop** ❌
**Problem**: `automatic_function_calling` enabled with tools
```python
# BEFORE (Line 446-450):
config = types.GenerateContentConfig(
    temperature=1.0,
    automatic_function_calling=types.AutomaticFunctionCallingConfig(
        maximum_remote_calls=20  # ← Enables tool calling
    ),
```

**Impact**: Model tries to call tools (filesystem, etc.) but never receives function responses, so it keeps repeating the same tool call waiting for a response.

---

### 3. **History Format Mismatch** ❌
**Problem**: Storing history as plain dicts, not SDK types
```python
# BEFORE (Line 488-491):
self.conversation_history[file_path].append({
    "role": "user",
    "parts": [{"text": prompt}]  # ← Plain dict, not types.Content
})
```

**Impact**: When passed to `chats.create()`, history isn't properly reconstructed, so model doesn't see previous context.

---

## Solutions Implemented ✅

### 1. **Persistent Chat Sessions**
```python
# AFTER (Line 449-466):
chat_key = f"chat_{file_path}" if file_path else "chat_default"

def get_gemini_response():
    if chat_key not in self.chat_sessions:
        # Create ONCE and reuse
        self.chat_sessions[chat_key] = self._client.chats.create(
            model=os.getenv('GEMINI_MODEL', 'gemini-2.5-flash'),
            config=config
        )
        print(f"      🆕 Created new chat session")
    else:
        print(f"      ♻️  Reusing chat session (Round {round_num})")
    
    chat = self.chat_sessions[chat_key]  # ← REUSE existing session
    return chat.send_message(prompt)
```

**Benefit**: Model maintains full conversation context across all 5 rounds.

---

### 2. **Disabled Automatic Function Calling**
```python
# AFTER (Line 440-447):
config = types.GenerateContentConfig(
    temperature=0.7,  # Lower temp for deterministic fixes
    thinking_config=types.ThinkingConfig(
        thinking_budget=16000
    )
    # NO automatic_function_calling - prevents tool loop
)
```

**Added to prompt (Line 435)**:
```
6. DO NOT use tools or function calls - return code directly as text.
```

**Benefit**: Model returns code directly as text, no tool-calling loops.

---

### 3. **Simplified History Tracking**
```python
# AFTER (Line 487-495):
# Track conversation history for debugging (chat session handles actual history)
if file_path:
    if file_path not in self.conversation_history:
        self.conversation_history[file_path] = []
    self.conversation_history[file_path].append({
        "round": len(self.conversation_history[file_path]) // 2 + 1,
        "prompt_length": len(prompt),
        "response_length": len(fixed_code)
    })
```

**Benefit**: Chat session SDK handles history internally. We just track metadata for debugging.

---

### 4. **Added chat_sessions Storage**
```python
# ValidationContext dataclass (Line 369):
chat_sessions: Dict[str, Any] = field(default_factory=dict)
```

**Benefit**: Persistent storage for chat sessions across all healing rounds.

---

## Expected Behavior After Fix

### Before Fix ❌
```
Round 1: API call → Model returns code
Round 2: API call → Model returns SAME code (no memory)
Round 3: API call → Model returns SAME code (no memory)
Round 4: API call → Model returns SAME code (no memory)
Round 5: API call → Model returns SAME code (no memory)
Result: FAILED (no convergence)
```

### After Fix ✅
```
Round 1: API call → Model returns code (session created)
Round 2: Reuse session → Model sees Round 1, improves code
Round 3: Reuse session → Model sees Rounds 1-2, further improves
Round 4: Reuse session → Model sees Rounds 1-3, converges
Round 5: (Not needed - success in Round 4)
Result: SUCCESS (convergence achieved)
```

---

## Debug Output

The fix adds debug output to track session reuse:

```
[Round 1/5] Healing Key 42 → file.py
      🆕 Created new chat session for file.py
      ✅ Tokens: 1234

[Round 2/5] Healing Key 42 → file.py
      ♻️  Reusing chat session (Round 2)
      ✅ Tokens: 987
```

If tool calling is detected (shouldn't happen now):
```
🔍 DEBUG: Model is calling a tool: write_file
   ⚠️  Tool calling should be disabled - clearing session and retrying
```

---

## Testing

Run the validator with healing enabled:
```bash
python apps_shared\canon_validator_v2_agentic.py --target . --heal
```

Expected improvements:
- ✅ No more repetitive API calls
- ✅ Model learns from previous rounds
- ✅ Faster convergence (2-3 rounds instead of 5)
- ✅ Higher success rate on complex violations

---

## Technical Details

### Chat Session Lifecycle
1. **First call**: Create new session, store in `ctx.chat_sessions[chat_key]`
2. **Subsequent calls**: Retrieve existing session from `ctx.chat_sessions[chat_key]`
3. **Session persists**: Across all 5 rounds for the same file
4. **Auto-cleanup**: Session cleared if tool-calling detected (error recovery)

### Key Differences from Before
| Aspect | Before | After |
|--------|--------|-------|
| Session | New every call | Persistent per file |
| Memory | None | Full conversation history |
| Tool Calling | Enabled | Disabled |
| Temperature | 1.0 (creative) | 0.7 (deterministic) |
| History Format | Plain dicts | SDK-managed |

---

## Related Files Modified

1. `apps_shared/canon_validator_v2_agentic.py`:
   - Line 369: Added `chat_sessions` field
   - Line 423-497: Rewrote `resilient_mutation()` method
   - Line 435: Added "no tools" instruction to prompt
   - Line 440-447: Disabled automatic function calling
   - Line 449-466: Implemented persistent chat sessions

---

## Success Metrics

Monitor these to verify the fix:
- **Convergence Rate**: % of violations fixed within 5 rounds (should increase)
- **Average Rounds**: Average rounds to success (should decrease from 5 to 2-3)
- **Token Efficiency**: Total tokens per fix (should decrease with fewer retries)
- **Session Reuse**: Count of "♻️ Reusing chat session" messages (should be 4 per file)
