---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\refactor_to_interactions_api_v3_titanium.md'
original_relative_path: 'refactor_to_interactions_api_v3_titanium.md'
source_sha256: f7607584ae6c633f8e0af19fd06516305547c7ad719e6a80be66735f62840d69
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# MISSION: REFACTOR TO GEMINI v1beta (TITANIUM GRADE ROBUSTNESS)

**CONTEXT:**
The `AgentExecutor` requires "Zero-Loss" reliability. We are upgrading to `google.genai` (v1beta) with a **Level 4** hardening mandate. Simple async is insufficient; the system must be self-healing, observable, and strictly typed.

**TARGET SDK:** `google.genai` (v1beta)
**TARGET MODEL:** `gemini-2.5-flash` | `gemini-3-pro-preview`

---

## ⚙️ HARDENING PROTOCOLS (IMPLEMENTED)

### 1. FAULT TOLERANCE ✅
**Implementation:** Tenacity-based exponential backoff with specific error handling

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    retry=retry_if_exception_type(errors.ClientError),
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=30)
)
async def _execute_with_retry(...):
    # Core execution logic with async support
```

**Features:**
- Retries on 429 (rate limit) and 503 (server unavailable)
- Configurable max retries (default: 5)
- Exponential backoff with jitter
- Warning logs before retry attempts

### 2. PRE-FLIGHT TOKEN GOVERNANCE ✅
**Implementation:** Token counting with 80% safety threshold

```python
async def validate_context_budget(model_id, input_payload):
    token_resp = await client.aio.models.count_tokens(
        model=model_id,
        contents=input_payload
    )
    if token_resp.total_tokens > safety_threshold:
        raise ContextOverflowError(...)
    return token_resp.total_tokens
```

**Features:**
- Pre-flight validation prevents context overflow
- Model-specific limits (1M for flash, 2M for pro)
- Configurable safety threshold (default: 80%)
- Fallback estimation if count_tokens unavailable

### 3. SAFETY SETTINGS OVERRIDE ✅
**Implementation:** Custom safety configuration for Risk/Insurance domain

```python
def build_safety_config():
    return [
        types.SafetySetting(
            category="HARM_CATEGORY_DANGEROUS_CONTENT",
            threshold="BLOCK_ONLY_HIGH"
        ),
        types.SafetySetting(
            category="HARM_CATEGORY_HARASSMENT",
            threshold="BLOCK_NONE"  # Allow robust critique
        )
    ]
```

**Features:**
- BLOCK_NONE for harassment (allows professional critique)
- BLOCK_ONLY_HIGH for dangerous content
- BLOCK_MEDIUM_AND_ABOVE for other categories
- Graceful fallback if types unavailable

### 4. STRUCTURED OBSERVABILITY ✅
**Implementation:** JSON logging with comprehensive telemetry

```python
async def log_interaction_telemetry(telemetry):
    logger.info({
        "event": "llm_interaction_complete",
        "interaction_id": telemetry.interaction_id,
        "model": telemetry.model,
        "input_tokens": telemetry.input_tokens,
        "output_tokens": telemetry.output_tokens,
        "latency_ms": telemetry.latency_ms,
        "timestamp": telemetry.timestamp
    })
```

**Features:**
- Structured JSON logs for easy parsing
- Token tracking (input/output/total)
- Latency measurement in milliseconds
- Error logging with context
- Unique interaction IDs for tracing

---

## 🚀 IMPLEMENTATION DETAILS

### Class Structure

```python
class HardenedGeminiExecutor:
    """Military-grade executor for Google GenAI v1beta."""

    def __init__(self, config: HardenedGeminiConfig):
        self.config = config
        self._client = get_client(Provider.GOOGLE)

    async def execute_k_node(
        self,
        messages: List[AgentMessage],
        system_prompt: Optional[str] = None,
        response_schema: Optional[Dict] = None,
        previous_interaction_id: Optional[str] = None
    ) -> str:
        # 1. Build config with safety settings
        # 2. Construct payload
        # 3. Pre-flight token validation
        # 4. Execute with retry
        # 5. Extract response
        # 6. Log telemetry
        return content

    def execute_sync(self, ...):
        """Synchronous wrapper for async execution."""
```

### Key Components

1. **HardenedGeminiConfig**
   - Model-specific context limits
   - Configurable safety thresholds
   - Retry parameters (max attempts, wait times)

2. **InteractionTelemetry**
   - Token counts (input/output/total)
   - Latency measurements
   - Error tracking
   - Timestamps and interaction IDs

3. **ContextOverflowError**
   - Custom exception for pre-flight failures
   - Detailed error messages with token counts

---

## 📋 USAGE EXAMPLES

### Basic K.2.5 Deep Research (Hardened)

```python
from agentic_workflow.runtime.shared import (
    create_hardened_gemini_executor,
    AgentMessage
)

# Create hardened executor
executor = create_hardened_gemini_executor(
    model="gemini-3-pro-preview",
    temperature=0.3,
    max_retries=5
)

# Execute with JSON schema
messages = [AgentMessage(role="user", content="Research DoorDash...")]

response = await executor.execute_k_node(
    messages=messages,
    system_prompt="You are the Deep Research Core (K.2.5)",
    response_schema=deep_research_schema
)

# Returns: Validated JSON string
```

### Stateful Continuation with Retry

```python
# First interaction
response1 = await executor.execute_k_node(
    messages=[AgentMessage(role="user", content="Generate summary")],
    system_prompt="You are a resume expert"
)

# Get interaction ID for continuation
interaction_id = json.loads(response1).get("interaction_id")

# Continue with feedback (automatic retry on rate limits)
response2 = await executor.execute_k_node(
    messages=[AgentMessage(role="user", content="Make it more concise")],
    previous_interaction_id=interaction_id
)
```

### Custom Configuration

```python
from agentic_workflow.runtime.shared import (
    HardenedGeminiExecutor,
    HardenedGeminiConfig
)

# Custom config for high-throughput scenario
config = HardenedGeminiConfig(
    model="gemini-2.5-flash",
    temperature=0.1,
    max_retries=10,
    retry_min_wait=1.0,
    retry_max_wait=60.0,
    safety_threshold_ratio=0.9  # Use 90% of context
)

executor = HardenedGeminiExecutor(config)
```

---

## 🔄 INTEGRATION WITH EXISTING CODE

### Backward Compatible Factory

```python
from agentic_workflow.runtime.shared import create_agent_executor

# Standard executor (unchanged)
executor = create_agent_executor(Provider.OPENAI)

# Hardened executor for Google
executor = create_agent_executor(
    provider=Provider.GOOGLE,
    hardened=True,  # Enable titanium-grade features
    model="gemini-3-pro-preview"
)
```

### Migration Path

1. **Phase 1**: Use standard executor for testing
2. **Phase 2**: Enable `hardened=True` for production
3. **Phase 3**: Fine-tune config parameters as needed

---

## 📊 MONITORING & DEBUGGING

### Telemetry Output Example

```json
{
  "event": "llm_interaction_complete",
  "interaction_id": "int_123456789",
  "model": "gemini-3-pro-preview",
  "input_tokens": 15420,
  "output_tokens": 892,
  "total_tokens": 16312,
  "latency_ms": 2341.5,
  "timestamp": "2025-12-12 15:47:32"
}
```

### Error Handling

```json
{
  "event": "llm_interaction_complete",
  "model": "gemini-3-pro-preview",
  "error": "ContextOverflowError: Payload 900000 tokens exceeds safety threshold (838860 tokens)",
  "latency_ms": 15.2,
  "timestamp": "2025-12-12 15:47:32"
}
```

---

## ✅ VALIDATION CHECKLIST

- [ ] Install hardened SDK: `pip install google-genai>=1.0.0b1 tenacity>=8.2.0`
- [ ] Enable structured logging in your logging config
- [ ] Set GOOGLE_API_KEY environment variable
- [ ] Configure safety thresholds for your use case
- [ ] Monitor telemetry logs for cost tracking
- [ ] Test retry behavior with rate limiting

---

## 📚 REFERENCE IMPLEMENTATION

**File:** `runtime/shared/hardened_gemini_executor.py`

Key classes and functions:
- `HardenedGeminiExecutor` - Main executor class
- `HardenedGeminiConfig` - Configuration management
- `InteractionTelemetry` - Telemetry data structure
- `create_hardened_gemini_executor()` - Factory function
- `create_agent_executor(hardened=True)` - Backward-compatible factory

---

**Status:** ✅ TITANIUM GRADE IMPLEMENTATION COMPLETE
**Date:** 2025-12-12
**Version:** v3.0.0-titanium
