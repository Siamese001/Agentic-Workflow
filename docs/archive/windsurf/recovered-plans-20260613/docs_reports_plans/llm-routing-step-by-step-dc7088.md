# LLM Routing: Step-by-Step Implementation with Exact File and Line Targets

Implement LLM routing hardening with exact file targets, method signatures, and line-level changes grounded in the actual repo code.

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Repo Reality Baseline

| File | Key fact for this plan |
|------|----------------------|
| `SovereignLLMGateway.generate()` | Accepts `provider`, `model`, `temperature=0.7` — **default is stochastic** |
| `FissionManagerAgent.execute_fission()` | Calls `self.llm_generate(provider="google", model=os.getenv("GEMINI_PRO_MODEL"))` — hardcoded env lookup, temp=0.2 |
| `CognitiveDispositionAgent.analyze_violation_async()` | Calls `self.llm_generate(provider="google", generation_config={"temperature": 0.1})` — no model, uses flash default |
| `StructuredEngineAgent.generate_plan()` | Calls `self.llm_generate(provider="google", model=os.getenv("GEMINI_MODEL"))` — flash, no temp |
| `BulletGenerationTask.execute()` | Calls `self.call_llm(prompt)` — method does not exist anywhere |
| `MCPOperationMixin` | Has `mcp_llm_route()`, `safe_mcp_call()` — no `call_llm()` |
| `DefaultHealingProviderInvoker.invoke_qwen_vllm()` | Returns stub `InvocationRecord` — **no real LLM call** |
| `DefaultHealingProviderInvoker.invoke_gemini()` | Returns stub `InvocationRecord` — **no real LLM call** |
| `ReplayBundle.active_config_hashes` | dict field exists, no healing config hash today |
| `FAILURE_CLASS_PRIORS` | Already in `healing_tier_router.py` — objective rubric for classification |

---

## Step 0 — Agent Classification Scan Script

**New file:** `ops_scripts/general/scan_agent_reasoning_class.py`

Run AST scan across all agent files. For each agent, compute score from:

```
Signal                                      Weight
-------                                     ------
heal method cyclomatic complexity > 8         +2
cross-agent imports in heal method body       +2
failure_type literal in {test_failure,        +2
  runtime_error, unknown}
blast_radius_estimate > 0.5 at call site      +1
retry_count referenced in heal logic          +1
direct llm_generate() call                    +3  (already confirmed LLM needed)
```

Score >= 3 → `STRATEGIC` or `ORCHESTRATOR`
Score 1-2 → `LIGHT`
Score 0 → `DETERMINISTIC`

Output: `artifacts/discovery/agent_reasoning_classification.json`

Format:
```json
{
  "schema_version": 1,
  "classification_hash": "<sha256 of sorted classifications>",
  "agents": [
    {
      "path": "agentic_core/L3_orchestration/reasoning/FissionManagerAgent.py",
      "class": "FissionManagerAgent",
      "score": 5,
      "signals": ["direct_llm_generate", "cross_agent_imports"],
      "assigned_class": "ORCHESTRATOR"
    }
  ]
}
```

Known pre-classified (score already determined from code reading):
- `FissionManagerAgent` → `ORCHESTRATOR` (direct `llm_generate`, complex fission logic)
- `CognitiveDispositionAgent` → `STRATEGIC` (direct `llm_generate`, architectural triage)
- `StructuredEngineAgent` → `STRATEGIC` (direct `llm_generate`, planning)
- `BulletGenerationTask` (apps_rg) → `LIGHT` (fast generation, Qwen tier)
- `MessageGenerationTask` (apps_rg) → `STRATEGIC` (quality content, Gemini tier)

---

## Step 1 — Add `ReasoningClass` Enum

**New file:** `agentic_core/config/reasoning_class.py`

```python
from enum import Enum

class ReasoningClass(Enum):
    DETERMINISTIC = 0  # No LLM — deterministic rules only
    LIGHT = 1          # Qwen vLLM, temp=0 — fast/cheap
    STRATEGIC = 2      # Gemini-2.5-pro, temp=0 — quality reasoning
    ORCHESTRATOR = 3   # Gemini-2.5-pro, temp=0, higher token budget
    HEALER = 4         # Only valid inside @standard_heal seam

# Maps ReasoningClass → (provider, model_env_var, default_model, temperature)
REASONING_CLASS_POLICY: dict[ReasoningClass, dict] = {
    ReasoningClass.LIGHT: {
        "provider": "qwen_vllm",
        "model_env": "QWEN_MODEL",
        "model_default": "qwen2.5-coder-32b-instruct",
        "temperature": 0.0,
        "token_budget": 2048,
    },
    ReasoningClass.STRATEGIC: {
        "provider": "google",
        "model_env": "GEMINI_PRO_MODEL",
        "model_default": "gemini-2.5-pro",
        "temperature": 0.0,
        "token_budget": 8192,
    },
    ReasoningClass.ORCHESTRATOR: {
        "provider": "google",
        "model_env": "GEMINI_PRO_MODEL",
        "model_default": "gemini-2.5-pro",
        "temperature": 0.0,
        "token_budget": 16384,
    },
}
```

No model literals in agents — all resolved through `REASONING_CLASS_POLICY`.

---

## Step 2 — Add `AGENT_REASONING_CLASS` and `ALLOW_STOCHASTIC` to `SovereignBaseAgent`

**File:** `agentic_core/base_agents/SovereignBaseAgent.py`

Add two class-level attributes after the `@dataclass` decorator (before `project_root`):

```python
# [LLM ROUTING] Per-agent reasoning class — default deterministic
AGENT_REASONING_CLASS: ReasoningClass = ReasoningClass.DETERMINISTIC
# Must be False unless L5-certified. Stochastic output breaks replay.
ALLOW_STOCHASTIC: bool = False
```

Import at top of file:
```python
from agentic_core.config.reasoning_class import ReasoningClass
```

---

## Step 3 — Add `route_generation()` to `SovereignLLMGateway`

**File:** `agentic_core/L2_execution/enforcement/SovereignLLMGateway.py`

Add new method after `generate()` (line ~408):

```python
async def route_generation(
    self,
    prompt: str,
    reasoning_class: ReasoningClass,
    trace_id: str,
    *,
    token_budget_limit: int = 0,
) -> dict:
    """Production generation path. Separate from healing path.

    Enforces:
    - temperature=0.0 unless agent declares ALLOW_STOCHASTIC=True
    - Model selection from REASONING_CLASS_POLICY only (no caller override)
    - Token budget enforcement via existing §Wave1.8 gate
    - trace_id required
    """
    from agentic_core.config.reasoning_class import REASONING_CLASS_POLICY, ReasoningClass

    if reasoning_class == ReasoningClass.DETERMINISTIC:
        raise ValueError("DETERMINISTIC agents must not call route_generation()")
    if reasoning_class == ReasoningClass.HEALER:
        raise ValueError("HEALER class must use dispatch_healing(), not route_generation()")

    policy = REASONING_CLASS_POLICY[reasoning_class]
    model = os.getenv(policy["model_env"], policy["model_default"])
    budget = token_budget_limit or policy["token_budget"]

    return await self.generate(
        prompt,
        provider=policy["provider"],
        model=model,
        temperature=policy["temperature"],   # Always 0.0 — no caller override
        token_budget_limit=budget,
        trace_id=trace_id,
    )
```

Add import at top of method scope:
```python
from agentic_core.config.reasoning_class import REASONING_CLASS_POLICY, ReasoningClass
```

**Critical constraint:** `route_generation()` does NOT call `dispatch_healing()`. These are separate paths.

---

## Step 4 — Implement `call_llm()` in `MCPOperationMixin`

**File:** `agentic_core/mixins/mcp_operation_mixin.py`

Add after `mcp_archive_op()` (line ~129):

```python
async def call_llm(
    self,
    prompt: str,
    *,
    reasoning_class: ReasoningClass | None = None,
    trace_id: str | None = None,
) -> str:
    """Route to SovereignLLMGateway.route_generation().

    Production generation path for apps_rg engines and non-healing agents.
    Does NOT call dispatch_healing() — that is the healing path only.

    Args:
        prompt: The prompt to send.
        reasoning_class: Override the agent's AGENT_REASONING_CLASS.
        trace_id: Correlation ID. Auto-generated from CIDRegistry if None.
    """
    from agentic_core.config.reasoning_class import ReasoningClass
    from agentic_core.L2_execution.enforcement.SovereignLLMGateway import get_llm_gateway

    cls = reasoning_class or getattr(self, "AGENT_REASONING_CLASS", ReasoningClass.LIGHT)
    if trace_id is None:
        from agentic_core.L0_routing.enforcement.traceability_contracts import generate_trace_id
        trace_id = generate_trace_id()

    gateway = get_llm_gateway()
    result = await gateway.route_generation(prompt, cls, trace_id)
    return result.get("content", "")
```

Add import at top of file:
```python
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from agentic_core.config.reasoning_class import ReasoningClass
```

---

## Step 5 — Wire Real Provider Calls in `DefaultHealingProviderInvoker`

**File:** `agentic_core/L2_execution/healers/healing_tier_dispatcher.py`

Both `invoke_qwen_vllm()` and `invoke_gemini()` currently return stubs with no LLM call.

Replace stub body of `invoke_qwen_vllm()`:
```python
def invoke_qwen_vllm(self, healing_input, decision, config, *, agent_name=""):
    """Wire to SovereignLLMGateway for Qwen vLLM healing calls."""
    import asyncio
    from agentic_core.L2_execution.enforcement.SovereignLLMGateway import get_llm_gateway

    gateway = get_llm_gateway()
    prompt = self._build_healing_prompt(healing_input)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        gateway.generate(
            prompt,
            provider="qwen_vllm",
            model=config.model_qwen_vllm_id,
            temperature=0.0,
            trace_id=healing_input.trace_id,
        )
    )
    return InvocationRecord(
        tier=HealingTier.QWEN_VLLM,
        model_id=config.model_qwen_vllm_id,
        agent_name=agent_name,
        trace_id=healing_input.trace_id,
        heal_confidence=decision.heal_confidence,
        method_called="invoke_qwen_vllm",
    )
```

Replace stub body of `invoke_gemini()`:
```python
def invoke_gemini(self, healing_input, decision, config, *, agent_name=""):
    """Wire to SovereignLLMGateway for Gemini 2.5 Pro healing calls."""
    import asyncio
    from agentic_core.L2_execution.enforcement.SovereignLLMGateway import get_llm_gateway

    gateway = get_llm_gateway()
    prompt = self._build_healing_prompt(healing_input)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        gateway.generate(
            prompt,
            provider="google",
            model=config.model_gemini_2_5_pro_id,
            temperature=0.0,
            trace_id=healing_input.trace_id,
        )
    )
    return InvocationRecord(
        tier=HealingTier.GEMINI_2_5_PRO,
        model_id=config.model_gemini_2_5_pro_id,
        agent_name=agent_name,
        trace_id=healing_input.trace_id,
        heal_confidence=decision.heal_confidence,
        method_called="invoke_gemini",
    )

def _build_healing_prompt(self, healing_input: HealingInput) -> str:
    """Build structured healing prompt from failure context."""
    return (
        f"HEALING REQUEST\n"
        f"failure_type: {healing_input.failure_type}\n"
        f"error_signature: {healing_input.error_signature}\n"
        f"blast_radius: {healing_input.blast_radius_estimate}\n"
        f"retry_count: {healing_input.retry_count}\n"
        f"context_refs: {list(healing_input.violation_metadata_refs)}\n"
        f"Provide a minimal, deterministic fix."
    )
```

---

## Step 6 — Migrate 3 Direct `llm_generate()` Callers

### 6a. `FissionManagerAgent` — L3

**File:** `agentic_core/L3_orchestration/reasoning/FissionManagerAgent.py`

- Add class attribute: `AGENT_REASONING_CLASS = ReasoningClass.ORCHESTRATOR`
- Replace `execute_fission()` lines 49-53:

```python
# Before
response = await self.llm_generate(
    prompt,
    provider="google",
    model=os.getenv("GEMINI_PRO_MODEL", "gemini-2.5-pro"),
    generation_config={"response_mime_type": "application/json", "temperature": 0.2},
)

# After
from agentic_core.L0_routing.enforcement.traceability_contracts import generate_trace_id
response = await self.llm_gateway.route_generation(
    prompt,
    ReasoningClass.ORCHESTRATOR,
    trace_id=generate_trace_id(),
)
```

- Remove `import os` from this file if no longer used.

### 6b. `CognitiveDispositionAgent` — L5

**File:** `agentic_core/L5_safety/reasoning/CognitiveDispositionAgent.py`

- Add class attribute: `AGENT_REASONING_CLASS = ReasoningClass.STRATEGIC`
- Replace `analyze_violation_async()` lines 103-107:

```python
# Before
response = await self.llm_generate(
    prompt,
    provider="google",
    generation_config={"response_mime_type": "application/json", "temperature": 0.1},
)

# After
from agentic_core.L0_routing.enforcement.traceability_contracts import generate_trace_id
response = await self.llm_gateway.route_generation(
    prompt,
    ReasoningClass.STRATEGIC,
    trace_id=generate_trace_id(),
)
```

### 6c. `StructuredEngineAgent` — L2

**File:** `agentic_core/L2_execution/reasoning/StructuredEngineAgent.py`

- Add class attribute: `AGENT_REASONING_CLASS = ReasoningClass.STRATEGIC`
- Replace `generate_plan()` lines 40-44:

```python
# Before
await self.llm_generate(
    prompt,
    provider="google",
    model=os.getenv("GEMINI_MODEL", "gemini-3-flash-preview"),
)

# After
from agentic_core.L0_routing.enforcement.traceability_contracts import generate_trace_id
await self.llm_gateway.route_generation(
    prompt,
    ReasoningClass.STRATEGIC,
    trace_id=generate_trace_id(),
)
```

- Remove `import os` if no longer used.

---

## Step 7 — Configure `apps_rg` Engine Classifications

**File:** `apps_rg/engines/bullet_generation_task.py`

Add class attribute (after class docstring):
```python
from agentic_core.config.reasoning_class import ReasoningClass
AGENT_REASONING_CLASS = ReasoningClass.LIGHT
```

`call_llm(prompt)` at line 43 now resolves to `MCPOperationMixin.call_llm()` implemented in Step 4.

**File:** `apps_rg/engines/message_generation_task.py` (if exists, else nearest equivalent)

Add:
```python
from agentic_core.config.reasoning_class import ReasoningClass
AGENT_REASONING_CLASS = ReasoningClass.STRATEGIC
```

---

## Step 8 — Wire `HealingTierConfig` Hash into `ReplayBundle`

**File:** `agentic_core/L2_execution/healers/healing_tier_config.py`

Add `content_hash()` method to `HealingTierConfig`:

```python
def content_hash(self) -> str:
    """Deterministic hash for ReplayBundle.active_config_hashes."""
    import hashlib, json
    doc = {
        "heal_confidence_x": self.heal_confidence_x,
        "heal_confidence_y": self.heal_confidence_y,
        "max_heal_retries": self.max_heal_retries,
        "model_qwen_vllm_id": self.model_qwen_vllm_id,
        "model_gemini_2_5_pro_id": self.model_gemini_2_5_pro_id,
    }
    return hashlib.sha256(
        json.dumps(doc, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
```

**File:** `agentic_core/L4_state/types/replay_bundle_types.py`

`active_config_hashes` already accepts arbitrary string keys. Callers should now include:
```python
active_config_hashes={
    "healing_config": healing_tier_config.content_hash(),
    ...existing keys...
}
```

No change to `ReplayBundle` dataclass itself — its `canonical_bytes()` already sorts keys.

---

## Step 9 — AST-Based CI Guard

**New file:** `ops_scripts/ci/check_llm_routing_compliance.py`

AST scans (not grep). Checks:

```python
CHECKS = [
    # 1. All *Agent.py files must have AGENT_REASONING_CLASS attribute (ClassDef AST)
    check_agent_has_reasoning_class,

    # 2. No string literals matching model names in agent files
    # Banned patterns: "gemini-*", "qwen*", "gpt-*", "claude-*"
    check_no_model_string_literals,

    # 3. No calls to .llm_generate() outside of LLMProviderMixin
    # AST: Check Call nodes for Attribute name == "llm_generate" in agent files
    check_no_direct_llm_generate_in_agents,

    # 4. No temperature= keyword argument outside SovereignLLMGateway
    # AST: Check keyword.arg == "temperature" in Call nodes outside gateway file
    check_no_temperature_kwarg_outside_gateway,

    # 5. No os.getenv("GEMINI_*") or os.getenv("QWEN_*") in agent files
    # Model env lookups must be in REASONING_CLASS_POLICY only
    check_no_model_env_lookup_in_agents,

    # 6. No httpx / aiohttp / requests imports in agent files
    check_no_raw_http_in_agents,
]
```

Exit code 1 if any check fails. Added to `.github/workflows/guardian-tests.yml`.

---

## Step 10 — Mark `llm_generate()` Deprecated

**File:** `agentic_core/mixins/llm_provider_mixin.py`

Add deprecation warning to `llm_generate()`:

```python
import warnings

async def llm_generate(self, prompt, model=None, provider="openai", **kwargs):
    warnings.warn(
        "llm_generate() is deprecated. Use self.llm_gateway.route_generation() "
        "or self.call_llm() with AGENT_REASONING_CLASS instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return await self.llm_gateway.generate(prompt, model=model, provider=provider, **kwargs)
```

---

## Execution Sequence

```
Step 0  → Run scan: produces agent_reasoning_classification.json
Step 1  → Create reasoning_class.py (no agent changes yet)
Step 2  → Add AGENT_REASONING_CLASS to SovereignBaseAgent (default=DETERMINISTIC)
Step 3  → Add route_generation() to SovereignLLMGateway
Step 4  → Add call_llm() to MCPOperationMixin (fixes silent apps_rg breakage)
Step 9  → Deploy CI guard (now prevents any model drift during Steps 5-10)
Step 5  → Wire real providers in DefaultHealingProviderInvoker
Step 6  → Migrate 3 direct llm_generate() callers
Step 7  → Configure apps_rg engine classifications
Step 8  → Add content_hash() to HealingTierConfig, wire into ReplayBundle
Step 10 → Deprecate llm_generate()
```

---

## Files Changed

| Step | File | Action |
|------|------|--------|
| 0 | `ops_scripts/general/scan_agent_reasoning_class.py` | NEW |
| 1 | `agentic_core/config/reasoning_class.py` | NEW |
| 2 | `agentic_core/base_agents/SovereignBaseAgent.py` | ADD 3 lines |
| 3 | `agentic_core/L2_execution/enforcement/SovereignLLMGateway.py` | ADD method |
| 4 | `agentic_core/mixins/mcp_operation_mixin.py` | ADD method |
| 5 | `agentic_core/L2_execution/healers/healing_tier_dispatcher.py` | REPLACE 2 stub methods |
| 6a | `agentic_core/L3_orchestration/reasoning/FissionManagerAgent.py` | REPLACE 5 lines |
| 6b | `agentic_core/L5_safety/reasoning/CognitiveDispositionAgent.py` | REPLACE 4 lines |
| 6c | `agentic_core/L2_execution/reasoning/StructuredEngineAgent.py` | REPLACE 4 lines |
| 7 | `apps_rg/engines/bullet_generation_task.py` | ADD 2 lines |
| 8 | `agentic_core/L2_execution/healers/healing_tier_config.py` | ADD method |
| 9 | `ops_scripts/ci/check_llm_routing_compliance.py` | NEW |
| 10 | `agentic_core/mixins/llm_provider_mixin.py` | ADD deprecation warning |
| **Total** | | **13 files, ~3 new** |

---

## Hardening Gates

| Gate | Enforced by |
|------|-------------|
| No model literals in agents | Step 9 CI (AST) |
| No temperature outside gateway | Step 9 CI (AST) |
| All agents have ReasoningClass | Step 9 CI (AST) |
| Healing path cannot be called from generation agents | Step 3 ValueError guard |
| DETERMINISTIC agents cannot call route_generation() | Step 3 ValueError guard |
| Production calls are deterministic by default | Step 3 temperature=0.0 |
| apps_rg engines routed through gateway | Step 4 call_llm() |
| Healing stubs wired to real providers | Step 5 |
| Config hash in ReplayBundle | Step 8 content_hash() |

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

