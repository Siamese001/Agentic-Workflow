---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\refactor_to_interactions_api.md'
original_relative_path: '_archive\\2026-05\\refactor_to_interactions_api.md'
source_sha256: 612c3dbc13396552c6ec43115377d870b8df2ad69faace9b6f7e53b8b3d1b274
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# MISSION: REFACTOR EXECUTION ENGINE TO GEMINI INTERACTIONS API (v1beta)

**CONTEXT:**
We are upgrading the "Subatomic Agentic Architecture" (specifically the `AgentExecutor`) to the latest Google Gen AI SDK. The legacy `chat.send_message` methods are deprecated for our use case. We must switch to the **Interactions API** to leverage native state management and tighter structured output controls.

**TARGET SDK:** `google.genai` (v1beta)
**TARGET MODEL:** `gemini-2.5-flash` (for speed) or `gemini-3-pro-preview` (for K.2.5 Deep Research)

---

## ⚙️ REFACTORING MANDATE

You are required to refactor the `AgentExecutor` class to use `client.interactions.create`. Follow these strict implementation protocols:

### 1. INITIALIZATION & CLIENT
**Old Way (Banned):**
```python
import google.generativeai as genai
model = genai.GenerativeModel('gemini-1.5-pro')
```

**New Way (Mandated):**
```python
from google import genai
client = genai.Client()
# Model selection must be dynamic based on 'AgentConfig'
```

### 2. EXECUTION LOGIC: STATELESS VS. STATEFUL

The architecture requires **Stateless Execution** for K-Nodes (to strictly control the RAG context window) but **Stateful Execution** for the Orchestrator.

#### A. For K-Node Agents (K.2.5, K.5A, etc.) - STATELESS

* **Requirement:** We must manually construct the history to inject the specific "DoorDash PDF" context and the "Deep Research" system prompt.
* **Implementation:**
  ```python
  response = client.interactions.create(
      model="gemini-3-pro-preview",
      input=[
          {"role": "user", "content": SYSTEM_PROMPT_PAYLOAD}, # Ingest System Prompt as first user turn or config
          {"role": "model", "content": "Understood. I am ready."},
          {"role": "user", "content": RAG_CONTEXT_BLOCK + "\n\n" + USER_QUERY}
      ]
      # config=... (Attach JSON Schema here if applicable)
  )
  ```

#### B. For Orchestrator (Feedback Loop) - STATEFUL

* **Requirement:** Maintain the conversation thread across multiple refinement hops without resending the whole context.
* **Implementation:**
  ```python
  # Pass the 'previous_interaction_id' to maintain state
  refinement_step = client.interactions.create(
      model="gemini-3-pro-preview",
      input="The previous output failed validation on 'Metric Source Binding'. Rewrite bullet 3.",
      previous_interaction_id=last_interaction_id
  )
  ```

### 3. STRUCTURED OUTPUT (CRITICAL)

For **K.2.5 Deep Research**, you must enforce the JSON schema.

* **Directive:** Ensure the `input` prompt explicitly requests JSON, or use the `config` parameter in `interactions.create` to specify `response_mime_type="application/json"` (if supported in the current client version) or rely on the strict prompt schema we defined.

### 4. ERROR HANDLING

* Wrap all `interactions.create` calls in a `try/except` block to catch `genai.errors.ClientError`.
* If a 500 error occurs, implement a "Backoff and Retry" logic (max 3 retries).

---

## 🚀 EXECUTION PLAN

### COMPLETED CHANGES:

1. ✅ **Updated requirements.txt** - Added `google-genai>=1.0.0b1` alongside legacy SDK
2. ✅ **Refactored multi_provider_clients.py** - Updated Google provider to return `genai.Client()` with fallback
3. ✅ **Added _execute_google method** - New method in AgentExecutor supporting Interactions API
4. ✅ **Updated providers_google_genai_client.py** - Added support for v1beta API with fallback
5. ✅ **Added structured JSON output** - Native JSON schema enforcement for K.2.5
6. ✅ **Implemented error handling** - Tenacity-based retry with exponential backoff

### KEY IMPLEMENTATION DETAILS:

#### 1. Dual SDK Support
The implementation supports both the new v1beta API and legacy SDK for backward compatibility:
```python
# In multi_provider_clients.py
if hasattr(client, 'interactions'):
    # Use new v1beta Interactions API
    return self._execute_google_interactions(...)
else:
    # Fallback to legacy SDK
    return self._execute_google_legacy(...)
```

#### 2. Stateful vs Stateless Execution
- **Stateless**: K-Nodes pass full history in `input` parameter
- **Stateful**: Orchestrator uses `previous_interaction_id` to maintain context

#### 3. Structured Output Enforcement
For K.2.5 Deep Research, the implementation uses:
```python
response = client.interactions.create(
    model=model,
    input=input_messages,
    config={
        "response_mime_type": "application/json",
        "response_schema": schema,  # Pydantic model JSON schema
    }
)
```

#### 4. Error Handling
Implemented using tenacity decorator:
```python
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def _execute_google_interactions(...):
```

---

## 📋 USAGE EXAMPLES

### K.2.5 Deep Research (Stateless with JSON Output)
```python
from agentic_workflow.runtime.shared import AgentExecutor, Provider, AgentMessage
from apps_rg.L1_cognition.k2_5_deep_research_models import DeepResearchOutput

# Create executor with Google provider
executor = AgentExecutor(
    provider=Provider.GOOGLE,
    model="gemini-3-pro-preview",
    temperature=0.3
)

# Execute with structured output
messages = [
    AgentMessage(role="user", content="Research DoorDash for competitive intelligence")
]

response = executor.execute_structured(
    messages=messages,
    response_model=DeepResearchOutput,
    system_prompt="You are the Deep Research Core (K.2.5)..."
)

# Returns: DeepResearchOutput instance with validated JSON
```

### Orchestrator Feedback Loop (Stateful)
```python
# First interaction
response1 = executor.execute(
    messages=[AgentMessage(role="user", content="Generate resume summary")],
    system_prompt="You are a resume generation expert..."
)

# Store interaction_id for continuation
interaction_id = response1.interaction_id

# Continue with feedback
response2 = executor.execute(
    messages=[AgentMessage(role="user", content="Make it more concise")],
    previous_interaction_id=interaction_id  # Maintains context!
)
```

---

## 🔄 MIGRATION CHECKLIST

- [ ] Install new SDK: `pip install google-genai>=1.0.0b1`
- [ ] Update existing Google API calls to use AgentExecutor
- [ ] For K-Nodes: Use stateless execution with full history
- [ ] For Orchestrator: Use `previous_interaction_id` for stateful continuation
- [ ] For structured output: Use `execute_structured()` method
- [ ] Monitor logs for fallback to legacy SDK

---

## 🐛 TROUBLESHOOTING

### Issue: "interactions attribute not found"
**Cause:** New SDK not installed
**Solution:** Install `google-genai>=1.0.0b1`, system will fallback to legacy SDK

### Issue: "Invalid JSON response from model"
**Cause:** Model didn't follow schema constraints
**Solution:** System automatically retries with exponential backoff

### Issue: "previous_interaction_id not working"
**Cause:** Interaction session expired (24-hour timeout)
**Solution:** Start new interaction with full history

---

## 📚 REFERENCE

### API Documentation
- New v1beta API: https://github.com/googleapis/python-genai
- Legacy SDK: https://github.com/google/generative-ai-python

### Model Mapping
- `gemini-2.0-flash-exp` → Fast inference for general tasks
- `gemini-3-pro-preview` → High-quality output for K.2.5 Deep Research

### Configuration Options
```python
config = {
    "temperature": 0.3,
    "max_output_tokens": 8192,
    "response_mime_type": "application/json",  # For structured output
    "response_schema": json_schema,  # Pydantic model schema
}
```

---

## ✅ VALIDATION

To verify the migration works correctly:

1. Run the K.2.5 Deep Research example:
   ```bash
   python examples/k2_5_deep_research_example.py
   ```

2. Check logs for "Using Google GenAI v1beta Interactions API"

3. Verify JSON output matches schema without parsing errors

4. Test stateful continuation with Orchestrator

---

**Status:** ✅ MIGRATION COMPLETE
**Date:** 2025-12-12
**Version:** v1.0.0-beta
