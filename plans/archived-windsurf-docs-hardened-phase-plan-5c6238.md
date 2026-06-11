---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\hardened-phase-plan-5c6238.md'
original_relative_path: 'hardened-phase-plan-5c6238.md'
source_sha256: b81f36d2f04a2a996fef18fd2095a4b9a9869e8014cb7b9253821737d729214b
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-26'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Hardened Phase Plan: Routing Sovereignty + Embedding Integrity + ExecutionMode Governance (v3)

Converge the repo to the target-state mapping by establishing formal agent reasoning policy (RULE_ONLY vs TIER_ROUTED), sealing the generation choke point with ExecutionMode enforcement, then embedding dimension/loader, with every phase carrying a determinism proof and negative control toggle — based on verified gaps at commit `8333412146c5019266b24c7a0b4476162ec2e862`.

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


## Baseline (commit `8333412146c5019266b24c7a0b4476162ec2e862`, branch `embeddings`)

**Critical discovery:** `healing_provider_adapters.py` already contains `QwenInvokerAdapter` + `GeminiInvokerAdapter` with real HTTP calls (`temperature=0.1` at line 94 — must become 0.0 in Phase F). G4 fix = wire dispatcher to use them, not rewrite.

**`ReplayBundle.active_config_hashes`** is `dict[str, str]` (verified `replay_bundle.py:54`) — embedding + policy hashes slot in directly, no schema change.

**Verified gaps:**

| Gap | File | Line | Gap |
|----|------|------|-----|
| G1 | `agentic_core/L1_cognition/types/memory_types.py` | 16 | `EMBEDDING_DIMENSION=1536` (need 3072) |
| G2 | `system_learning/engines/` | — | Loader missing (builder/CLI exist) |
| G3 | `agentic_core/config/reasoning_class.py` | — | File does not exist |
| G4 | `healing_tier_dispatcher.py` | 101–158 | `DefaultHealingProviderInvoker` stubs |
| G5 | `SovereignLLMGateway.py` | 142 | `route_generation()` missing |
| G6 | `mcp_operation_mixin.py` | — | `call_llm()` missing |
| G10 | 32+ agent/engine files | — | 129 temperature violations, model literals |

---

## Execution Order (10 phases total)

```
Phase 0   →  Phase 0b  →  Phase 0c  →  Phase 0d  →  Phase A   →  Phase B   →  Phase C   →  Phase D   →  Phase E   →  Phase F
Policy+      Agent        Enforce      CI bound     G5+G6        CI guard     G3 enum     migrate      G1+G2       G4 wire
ExecMode     Scan         choke        to inv       choke pt     seals        policy      callers      embed       adapters
registry     inventory    points       artifact
```

**Governance-first sequencing:** Phases 0–0d establish ExecutionMode policy and enforcement before any LLM routing is wired.

---

## Determinism + Negative Control Contract (every phase)

Every phase MUST include two additional test functions — not comments:

1. **Determinism proof:** Run acceptance command twice; assert `sha256` of stable artifact (fingerprint, replay_hash, count) is identical.
2. **Negative control:** `@pytest.mark.xfail(strict=True)` that tampers one invariant, asserts hard-fail, restores, asserts pass.

**Replay key surface** — populate into `ReplayBundle.active_config_hashes`:
```python
{
    "embedding_model":  EMBEDDING_MODEL_ID,
    "seed_pack_hash":   SEED_PACK_HASH,
    "reasoning_policy": sha256(json(REASONING_CLASS_POLICY, sort_keys=True)),
    "healing_config":   sha256(json(HealingTierConfig.defaults(), sort_keys=True)),
}
```

| Phase | Determinism Proof | Negative Control |
|-------|-------------------|------------------|
| 0 | `sha256(json(AGENT_EXECUTION_REGISTRY))` stable across restarts | Unregistered agent defaults to RULE_ONLY; override → TIER_ROUTED works |
| 0b | Inventory JSON digest identical on two runs | Inject fake literal via env var → XFAIL exit-0; restore → PASS |
| 0c | RULE_ONLY agent blocked from `call_llm()` | TIER_ROUTED agent can call `call_llm()` and routes via gateway |
| 0d | CI fails on RULE_ONLY agent with model literal | Temporary allowlist removal deadline enforced |
| A | Two `route_generation()` calls → same audit fingerprint | Pass `temperature=0.3` → normalized to 0.0 or raises |
| B | CI script output identical across two runs | `--self-test`: synthetic violating file detected, exit non-zero |
| C | `sha256(json(POLICY))` stable across restarts | Literal `"gemini-2.5-pro"` in `model_id` → `PolicyLiteralError` |
| D | Migrated callers produce same fingerprint | Restore `llm_generate()` call → CI guard catches it |
| E | Dry-run loader emits identical JSON both runs | Flip one byte of `embeddings.f32` → `MatrixHashMismatchError` |
| F | Composite invoker routes identically per tier | `StubHealingProviderInvoker` in prod config → `ProductionInvokerError` |

---

## Phase 0 — Agent Reasoning Policy + ExecutionMode Classification

**Why first:** Establishes the governance rule "high reasoning → TIER_ROUTED (Qwen/Gemini); low reasoning → RULE_ONLY deterministic" before any routing code is written.

### 0.1 ExecutionMode enum + policy surface

**Target:** NEW `agentic_core/config/execution_mode.py`

```python
class ExecutionMode(str, Enum):
    RULE_ONLY           = "rule_only"            # Deterministic healing only, no LLM generation
    TIER_ROUTED         = "tier_routed"          # LLM generation via route_generation(), healing via tier router
    DIRECT_LLM_ALLOWED  = "direct_llm_allowed"   # Legacy/migration mode (temporary)

@dataclass(frozen=True)
class AgentExecutionPolicy:
    reasoning_class: ReasoningClass   # from Phase C
    execution_mode:  ExecutionMode
    rationale:       str              # Why this classification

DEFAULT_EXECUTION_MODE: Final[ExecutionMode] = ExecutionMode.RULE_ONLY
```

**Invariant:** Any agent not in the registry defaults to `RULE_ONLY` (fail-safe deterministic).

### 0.2 AGENT_EXECUTION_REGISTRY SSOT

**Target:** NEW `agentic_core/config/agent_execution_registry.py`

```python
AGENT_EXECUTION_REGISTRY: Final[dict[str, AgentExecutionPolicy]] = {
    # High reasoning intensity → TIER_ROUTED
    "FissionManagerAgent":        AgentExecutionPolicy(ReasoningClass.ORCHESTRATOR, ExecutionMode.TIER_ROUTED, "Multi-step coordination"),
    "CognitiveDispositionAgent":  AgentExecutionPolicy(ReasoningClass.STRATEGIC,    ExecutionMode.TIER_ROUTED, "Strategic reasoning"),
    "StructuredEngineAgent":      AgentExecutionPolicy(ReasoningClass.LIGHT,        ExecutionMode.TIER_ROUTED, "Structured output generation"),

    # Lower reasoning intensity → RULE_ONLY (deterministic healing)
    "ArchitectureGovernanceHealer": AgentExecutionPolicy(ReasoningClass.DETERMINISTIC, ExecutionMode.RULE_ONLY, "Rule-based healing"),
    "DriftDetectionHealer":         AgentExecutionPolicy(ReasoningClass.DETERMINISTIC, ExecutionMode.RULE_ONLY, "Deterministic drift detection"),
    # ... (populate from Phase 0b inventory scan)
}

def get_agent_execution_policy(agent_class_name: str) -> AgentExecutionPolicy:
    """Returns policy for agent, defaulting to RULE_ONLY if unregistered."""
    return AGENT_EXECUTION_REGISTRY.get(
        agent_class_name,
        AgentExecutionPolicy(ReasoningClass.DETERMINISTIC, DEFAULT_EXECUTION_MODE, "Unregistered agent")
    )
```

**Determinism proof:** `sha256(json(AGENT_EXECUTION_REGISTRY, sort_keys=True))` stable across two Python restarts.

**Negative control:**
```python
@pytest.mark.xfail(strict=True)
def test_unregistered_agent_defaults_to_rule_only():
    policy = get_agent_execution_policy("FakeUnregisteredAgent")
    assert policy.execution_mode == ExecutionMode.RULE_ONLY
    # If default changes, this PASSES → CI catches regression
```

**Acceptance test (one command):**
```
python -m pytest tests/agentic_core/config/test_execution_mode.py tests/agentic_core/config/test_agent_execution_registry.py -xvv
```

---

## Phase 0b — Repo-wide Agent Scan + Inventory Artifact

**Target:** NEW `ops_scripts/ci/scan_agent_reasoning_inventory.py`

**Deliverables:**

1. **Deterministic scanner** that inventories all agents (using `classification_kernel.py` SSOT) and detects:
   - Model string literals (AST scan for string nodes matching `"gpt-"|"gemini-"|"claude-"`)
   - Provider SDK imports (`import openai`, `from anthropic import`, `import google.generativeai`)
   - Calls to `call_llm()`, `gateway.generate()`, `llm_generate()`, direct provider invocation

2. **Output artifact:** `artifacts/windsurf/agent_reasoning_inventory.json` (or CSV) with schema:
   ```json
   {
     "scan_timestamp": "2026-02-25T10:55:00Z",
     "commit_hash": "8333412146c5019266b24c7a0b4476162ec2e862",
     "agents": [
       {
         "agent_name": "FissionManagerAgent",
         "file_path": "agentic_core/L3_orchestration/reasoning/FissionManagerAgent.py",
         "detected_violations": ["model_literal: line 45", "provider_import: line 3"],
         "recommended_reasoning_class": "ORCHESTRATOR",
         "recommended_execution_mode": "TIER_ROUTED"
       },
       ...
     ]
   }
   ```

3. **Deterministic output:** Two runs produce identical `sha256(json(inventory, sort_keys=True))`.

**Negative control:**
```bash
# Set env var to inject fake literal finding
export INJECT_FAKE_LITERAL_AGENT="TestAgent"
python ops_scripts/ci/scan_agent_reasoning_inventory.py --xfail-mode
# Expect: exit 0 (XFAIL), inventory contains fake entry

unset INJECT_FAKE_LITERAL_AGENT
python ops_scripts/ci/scan_agent_reasoning_inventory.py
# Expect: exit 0 (PASS), inventory clean
```

**Acceptance test (one command):**
```
python -m pytest tests/ops_scripts/test_scan_agent_reasoning_inventory.py -xvv && python ops_scripts/ci/scan_agent_reasoning_inventory.py --verify-determinism
```

---

## Phase 0c — Enforcement Wiring (ExecutionMode Choke Points)

**Requirements:**

### 0c.1 `call_llm()` ExecutionMode assertion

**Target:** `agentic_core/mixins/mcp_operation_mixin.py` (Phase A adds `call_llm()`, this phase hardens it)

**Add before gateway call:**
```python
async def call_llm(self, prompt: str, *, trace_id: str | None = None) -> str:
    from agentic_core.config.agent_execution_registry import get_agent_execution_policy
    from agentic_core.config.execution_mode import ExecutionMode

    agent_class_name = self.__class__.__name__
    policy = get_agent_execution_policy(agent_class_name)

    if policy.execution_mode == ExecutionMode.RULE_ONLY:
        raise ExecutionModeViolationError(
            f"{agent_class_name} is RULE_ONLY but attempted call_llm(). "
            f"Use deterministic healing only."
        )

    # ... existing route_generation() call
```

### 0c.2 `route_generation()` used for all generation

**Already enforced by Phase A** — `call_llm()` is the sole seam, routes to `route_generation()`.

### 0c.3 Healing escalation remains single choke point

**Already enforced** — `FailureSignal → route_healing_tier()` selects LOCAL/QWEN/GEMINI. Agents never choose tiers.

**Acceptance tests:**
```python
def test_rule_only_agent_blocked_from_call_llm():
    agent = RuleOnlyTestAgent()  # registered as RULE_ONLY
    with pytest.raises(ExecutionModeViolationError):
        await agent.call_llm("test prompt")

def test_tier_routed_agent_can_call_llm():
    agent = TierRoutedTestAgent()  # registered as TIER_ROUTED
    result = await agent.call_llm("test prompt")  # Should succeed, route via gateway
    assert result  # No exception raised
```

**Acceptance test (one command):**
```
python -m pytest tests/agentic_core/mixins/test_mcp_operation_mixin.py -xvv -k "execution_mode or rule_only or tier_routed"
```

---

## Phase 0d — CI Guardrails Bound to Inventory

**Target:** NEW `ops_scripts/ci/check_execution_mode_compliance.py`

**Requirements:**

1. **Load inventory artifact** from Phase 0b (`artifacts/windsurf/agent_reasoning_inventory.json`).

2. **CI fails if any RULE_ONLY agent has:**
   - Model string literals
   - Provider SDK imports (`openai`, `anthropic`, `google.generativeai`)
   - `call_llm()` usage

3. **CI fails if any agent uses model literals outside approved files:**
   - Allowlist: `agentic_core/config/reasoning_class.py`, `ops_scripts/ci/`, `tests/`, `data/sdks_mcps/`, `healing_provider_adapters.py`

4. **Temporary allowlist for migration period:**
   - **IF** a temporary allowlist is needed, it MUST:
     - Be defined in `ops_scripts/ci/execution_mode_allowlist.json` with schema:
       ```json
       {
         "allowlist": [
           {"agent": "LegacyAgent", "reason": "Migration in progress", "deadline": "2026-03-15"}
         ]
       }
       ```
     - Expire on deadline (CI hard-fails after deadline)
     - Be explicitly approved in Phase 0d acceptance
   - **OTHERWISE:** No allowlist, fail hard immediately.

**Negative control:**
```python
@pytest.mark.xfail(strict=True)
def test_rule_only_agent_with_model_literal_fails_ci():
    # Inject a RULE_ONLY agent with model literal into inventory
    # CI check must detect and fail
    pass
```

**Acceptance test (one command):**
```
python -m pytest tests/ops_scripts/test_check_execution_mode_compliance.py -xvv && python ops_scripts/ci/check_execution_mode_compliance.py
```

---

## Phase A — `route_generation()` + `call_llm()` (G5 + G6)

### A.1 `SovereignLLMGateway.route_generation()`

**Target:** `agentic_core/L2_execution/enforcement/SovereignLLMGateway.py`
**Insert after:** `generate()` (~line 155). Local import of `ReasoningClass` inside method body to avoid circular dep.

```python
async def route_generation(
    self,
    prompt: str,
    reasoning_class: Any,   # ReasoningClass, local-imported
    trace_id: str,
    *,
    token_cap: TokenCapArtifact | None = None,
) -> dict:
    """Single production generation seam. temperature=0.0 always."""
    from agentic_core.config.reasoning_class import REASONING_CLASS_POLICY
    policy = REASONING_CLASS_POLICY[reasoning_class]
    return await self.generate(
        prompt,
        model=policy.model_id,
        provider=policy.provider,
        temperature=0.0,     # HARD ZERO
        max_tokens=policy.max_tokens,
        trace_id=trace_id,
        token_cap=token_cap,
    )
```

Audit fingerprint stored in returned dict: `sha256(provider + model + "0.0" + prompt[:64])`.

### A.2 `MCPOperationMixin.call_llm()`

**Target:** `agentic_core/mixins/mcp_operation_mixin.py`
**Insert after:** `mcp_llm_route()` (line 118)

```python
async def call_llm(self, prompt: str, *, trace_id: str | None = None) -> str:
    """Sole production generation seam. No provider SDK. No embedding. No bypass.

    Note: Phase 0c will add ExecutionMode.RULE_ONLY enforcement here.
    """
    from agentic_core.config.reasoning_class import DEFAULT_REASONING_CLASS
    from agentic_core.L2_execution.enforcement.SovereignLLMGateway import get_llm_gateway
    cls = getattr(self, "AGENT_REASONING_CLASS", DEFAULT_REASONING_CLASS)
    result = await get_llm_gateway().route_generation(
        prompt, cls, trace_id or str(uuid.uuid4())
    )
    return result.get("content", "")
```

**Acceptance test (one command):**
```
python -m pytest tests/agentic_core/L2_execution/enforcement/test_sovereign_llm_gateway.py tests/agentic_core/mixins/test_mcp_operation_mixin.py -xvv -k "route_generation or call_llm"
```

---

## Phase B — AST CI Guard (G10)

**Target:** NEW `ops_scripts/ci/check_llm_routing_compliance.py`
Follows `check_anti_patterns.py` + `check_tooling_apps_boundary.py` (both use `ast.parse`, verified in `ops_scripts/ci/`).

**5 checks — all `ast.parse`, zero regex:**

```
CHECK_01: No model string literals in agent/engine files
  Allowlist: ops_scripts/ci/, tests/, agentic_core/config/reasoning_class.py,
             data/sdks_mcps/, healing_provider_adapters.py

CHECK_02: No temperature kwarg set to nonzero float outside SovereignLLMGateway.py
  Note: healing_provider_adapters.py temperature=0.1 is Phase F scope;
        add it to allowlist with TODO marker until Phase F seals it

CHECK_03: No direct import of openai/anthropic/google.generativeai in agent files
  Allowlist: data/sdks_mcps/, healing_provider_adapters.py

CHECK_04: No raw httpx/requests client in agent/engine files

CHECK_05: Every class inheriting SovereignBaseAgent must define AGENT_REASONING_CLASS
  (AST class-body scan, not runtime)
```

**`--self-test` flag:** Ships `tests/fixtures/llm_compliance/` with one synthetic violating file per check. Script must detect all 5 and exit non-zero.

**Acceptance test (one command):**
```
python -m pytest -xvv tests/ops_scripts/test_llm_routing_compliance.py && python ops_scripts/ci/check_llm_routing_compliance.py --self-test
```

---

## Phase C — `ReasoningClass` Enum + Policy SSOT (G3)

**Target:** NEW `agentic_core/config/reasoning_class.py`

```python
class ReasoningClass(str, Enum):
    DETERMINISTIC = "deterministic"   # no LLM call
    LIGHT         = "light"           # fast structured
    STRATEGIC     = "strategic"       # multi-step
    ORCHESTRATOR  = "orchestrator"    # coordination
    HEALER        = "healer"          # healing path only

@dataclass(frozen=True)
class ReasoningPolicy:
    provider:   str   # "openai" | "google" | "anthropic"
    model_id:   str   # os.getenv() result at module load — never a bare literal
    max_tokens: int
    # temperature is NOT a field — always 0.0

REASONING_CLASS_POLICY: Final[dict[ReasoningClass, ReasoningPolicy]] = {
    ReasoningClass.LIGHT:        ReasoningPolicy("google", os.getenv("GEMINI_FLASH_MODEL", ""), 2048),
    ReasoningClass.STRATEGIC:    ReasoningPolicy("google", os.getenv("GEMINI_PRO_MODEL",   ""), 4096),
    ReasoningClass.ORCHESTRATOR: ReasoningPolicy("google", os.getenv("GEMINI_PRO_MODEL",   ""), 8192),
    ReasoningClass.HEALER:       ReasoningPolicy("google", os.getenv("GEMINI_PRO_MODEL",   ""), 4096),
    ReasoningClass.DETERMINISTIC:ReasoningPolicy("",       "",                                  0),
}
DEFAULT_REASONING_CLASS: Final[ReasoningClass] = ReasoningClass.LIGHT
```

**Invariants:**
- `model_id` is `os.getenv(...)` at module load — never a bare string like `"gemini-2.5-pro"`
- `temperature` absent from `ReasoningPolicy` — CHECK_02 enforces this
- `REASONING_CLASS_POLICY` is `Final` — no runtime mutation
- `model_id=""` valid for test seam — gateway raises at call time, not import time

**SovereignBaseAgent addition** (`SovereignBaseAgent.py`):
```python
AGENT_REASONING_CLASS: ClassVar[ReasoningClass] = DEFAULT_REASONING_CLASS
```

**Acceptance test (one command):**
```
python -m pytest tests/agentic_core/config/test_reasoning_class.py -xvv
```

Required tests: default=LIGHT, all providers non-empty string, `temperature` not in policy fields, `sha256(json(POLICY))` stable across two Python invocations, negative control: bare `"gemini-2.5-pro"` literal in `model_id` → `PolicyLiteralError`.

---

## Phase D — Migrate 3 Direct `llm_generate()` Callers to ExecutionMode/ReasoningClass Compliance

**Prerequisite:** Phase B CI guard active and exit-0 before this phase starts.

**Migration target:** ReasoningClass + ExecutionMode compliance (from Phase 0 registry). No direct model strings outside gateway policy surface.

| File | Current | After |
|------|---------|-------|
| `agentic_core/L3_orchestration/reasoning/FissionManagerAgent.py` | `self.llm_generate(prompt, provider="google", model=os.getenv(...))` | `await self.call_llm(prompt)` + `AGENT_REASONING_CLASS = ReasoningClass.ORCHESTRATOR` + Registry: `ExecutionMode.TIER_ROUTED` |
| `agentic_core/L5_safety/reasoning/CognitiveDispositionAgent.py` | `self.llm_generate(..., generation_config={"temperature": 0.1})` | `await self.call_llm(prompt)` + `AGENT_REASONING_CLASS = ReasoningClass.STRATEGIC` + Registry: `ExecutionMode.TIER_ROUTED` |
| `agentic_core/L2_execution/reasoning/StructuredEngineAgent.py` | `self.llm_generate(prompt, provider="google", model=os.getenv(...))` | `await self.call_llm(prompt)` + `AGENT_REASONING_CLASS = ReasoningClass.LIGHT` + Registry: `ExecutionMode.TIER_ROUTED` |

**Post-migration gates:**
1. `python ops_scripts/ci/check_llm_routing_compliance.py` exits 0
2. `python ops_scripts/ci/check_execution_mode_compliance.py` exits 0 (Phase 0d)
3. All 3 agents registered in `AGENT_EXECUTION_REGISTRY` with `ExecutionMode.TIER_ROUTED`

**Acceptance test (one command):**
```
python -m pytest tests/agentic_core/L3_orchestration/reasoning/ tests/agentic_core/L5_safety/reasoning/ tests/agentic_core/L2_execution/reasoning/ -xvv -k "FissionManager or CognitiveDisposition or StructuredEngine" && python ops_scripts/ci/check_llm_routing_compliance.py && python ops_scripts/ci/check_execution_mode_compliance.py
```

---

## Phase E — Embedding Dimension + Startup Invariant + Seed Loader (G1 + G2)

### E.1 Fix constants — `agentic_core/L1_cognition/types/memory_types.py` line 16

```python
# BEFORE
EMBEDDING_DIMENSION: Final[int] = 1536  # OpenAI ada-002 dimension

# AFTER (4 new SSOT pins)
EMBEDDING_DIMENSION:  Final[int] = 3072
EMBEDDING_MODEL_ID:   Final[str] = "text-embedding-3-large"
SEED_PACK_HASH:        Final[str] = "5d94b5b12ec92312d0240be9984ff92b9478f74ed6f1335511a202c5351520d9"
SEED_PACK_NAMESPACE:   Final[str] = "healing_contexts"
```

### E.2 Startup integrity invariant

**Target:** Locate `EmbeddingSovereignAgent` class via AST scan before editing (may be in `agentic_core/L1_cognition/` not `L2_execution/`). Add to `__init__`:

```python
from agentic_core.L1_cognition.types.memory_types import EMBEDDING_MODEL_ID, EMBEDDING_DIMENSION
if self.model != EMBEDDING_MODEL_ID:
    raise EmbeddingModelMismatchError(
        f"model={self.model!r} != required {EMBEDDING_MODEL_ID!r}"
    )
# Also verify manifest at load time:
if manifest["dimensions"] != EMBEDDING_DIMENSION:
    raise EmbeddingDimensionMismatchError(
        f"manifest.dimensions={manifest['dimensions']} != {EMBEDDING_DIMENSION}"
    )
```

### E.3 Seed pack loader — NEW `system_learning/engines/seed_pack_loader.py`

Checks in order (all hard-fail before any Pinecone upsert):
1. `manifest["seed_index_version_hash"] == SEED_PACK_HASH`
2. `manifest["dimensions"] == EMBEDDING_DIMENSION`
3. `sha256(read(embeddings.f32)) == manifest["matrix_hash"]`
4. Target namespace must equal `SEED_PACK_NAMESPACE` — raises on cross-namespace attempt
5. Row iteration: deterministic sorted order by integer index from `row_index.jsonl`

`--dry-run`: emits `{"vector_count": N, "matrix_hash": "..."}` — identical JSON on two runs.

### E.4 Wire into ReplayBundle

When building a bundle after any embedding-augmented decision, caller must include:
```python
active_config_hashes={
    "embedding_model":  EMBEDDING_MODEL_ID,
    "seed_pack_hash":   SEED_PACK_HASH,
    # ... other policy hashes
}
```

**Acceptance test (one command):**
```
python -m pytest tests/unit_min_deps/system_learning/test_seed_embedding_pack_b0.py tests/agentic_core/L1_cognition/types/test_memory_types.py -xvv -k "dimension or model_id or hash or mismatch or dry_run"
```

---

## Phase F — Wire Real Provider Adapters (G4)

**Real adapters exist in `healing_provider_adapters.py`.** Two changes required:

### F.1 `CompositeHealingInvoker` in `healing_tier_dispatcher.py`

Add a `CompositeHealingInvoker` class and a `build_production_invoker()` factory:

```python
class CompositeHealingInvoker:
    """Routes to the correct real adapter based on tier."""
    def __init__(self, qwen, gemini, local):
        self._qwen = qwen
        self._gemini = gemini
        self._local = local

    def invoke_qwen_vllm(self, healing_input, decision, config, *, agent_name=""):
        return self._qwen.invoke_qwen_vllm(healing_input, decision, config, agent_name=agent_name)

    def invoke_gemini(self, healing_input, decision, config, *, agent_name=""):
        return self._gemini.invoke_gemini(healing_input, decision, config, agent_name=agent_name)

    def invoke_local(self, healing_input, decision, config, *, agent_name=""):
        return self._local.invoke_local(healing_input, decision, config, agent_name=agent_name)

def build_production_invoker() -> HealingProviderInvoker:
    from agentic_core.L2_execution.healers.healing_provider_adapters import (
        QwenInvokerAdapter, GeminiInvokerAdapter, LocalAgentAdapter,
    )
    return CompositeHealingInvoker(
        qwen=QwenInvokerAdapter(base_url=os.getenv("QWEN_VLLM_URL", "")),
        gemini=GeminiInvokerAdapter(api_key=os.getenv("GEMINI_API_KEY", "")),
        local=LocalAgentAdapter(),
    )
```

`DefaultHealingProviderInvoker` renamed to `StubHealingProviderInvoker` — tests only. Production default becomes `build_production_invoker()`.

### F.2 Fix `temperature=0.1` in `healing_provider_adapters.py`

**Target:** `healing_provider_adapters.py` line 94 (`QwenInvokerAdapter`) and equivalent in `GeminiInvokerAdapter`:
```python
# BEFORE
temperature=0.1,
# AFTER
temperature=0.0,
```

After this fix, CHECK_02 allowlist entry for `healing_provider_adapters.py` is removed from Phase B.

**Tests use fake invoker seam — no network calls in test suite.**

**Acceptance test (one command):**
```
python -m pytest tests/agentic_core/L2_execution/healers/test_healing_tier_dispatcher.py -xvv -k "composite or real_adapter or production_invoker"
```

---

## Convergence Definition (13 hard gates, all must pass)

**ExecutionMode Governance (Phases 0–0d):**
1. `AGENT_EXECUTION_REGISTRY` exists with deterministic serialization (`sha256` stable)
2. Unregistered agents default to `ExecutionMode.RULE_ONLY` (tested)
3. `artifacts/windsurf/agent_reasoning_inventory.json` exists with deterministic digest
4. `call_llm()` blocks `RULE_ONLY` agents (tested with `ExecutionModeViolationError`)
5. `python ops_scripts/ci/check_execution_mode_compliance.py` exits 0

**LLM Routing Sovereignty (Phases A–D):**
6. `python ops_scripts/ci/check_llm_routing_compliance.py` exits 0
7. `python -m pytest -q --color=no` full suite exits 0
8. No model string literals in agent/engine files (CI CHECK_01 enforced)
9. No nonzero temperature outside gateway (CI CHECK_02 enforced — all allowlist entries removed by Phase F)
10. All generation routes through `route_generation()` via `call_llm()`

**Embedding + Healing (Phases E–F):**
11. `DefaultHealingProviderInvoker` replaced; `CompositeHealingInvoker` uses real adapters (tested with fakes)
12. `EMBEDDING_DIMENSION == 3072`, `EMBEDDING_MODEL_ID` pinned, startup raises on mismatch
13. Seed loader verifies `matrix_hash + dimensions + namespace` before any upsert

**All phases:** Determinism proof + negative control test (all `strict=True` xfail, all passing)

---

## Files Changed (20 total)

| Phase | File | Type | Change |
|-------|------|------|--------|
| 0 | `agentic_core/config/execution_mode.py` | **NEW** | ExecutionMode enum + AgentExecutionPolicy |
| 0 | `agentic_core/config/agent_execution_registry.py` | **NEW** | AGENT_EXECUTION_REGISTRY SSOT + get_agent_execution_policy() |
| 0b | `ops_scripts/ci/scan_agent_reasoning_inventory.py` | **NEW** | Deterministic agent scanner (AST-based) |
| 0b | `artifacts/windsurf/agent_reasoning_inventory.json` | **NEW** | Inventory artifact (generated) |
| 0c | `agentic_core/mixins/mcp_operation_mixin.py` | Modified | Add ExecutionMode.RULE_ONLY enforcement to `call_llm()` |
| 0d | `ops_scripts/ci/check_execution_mode_compliance.py` | **NEW** | CI guard bound to inventory artifact |
| 0d | `ops_scripts/ci/execution_mode_allowlist.json` | **NEW** (optional) | Temporary migration allowlist with deadlines |
| A | `agentic_core/L2_execution/enforcement/SovereignLLMGateway.py` | Modified | Add `route_generation()` |
| A | `agentic_core/mixins/mcp_operation_mixin.py` | Modified | Add `call_llm()` (Phase 0c hardens it) |
| B | `ops_scripts/ci/check_llm_routing_compliance.py` | **NEW** | AST CI guard (5 checks + `--self-test`) |
| C | `agentic_core/config/reasoning_class.py` | **NEW** | Enum + Final policy SSOT |
| C | `agentic_core/base_agents/SovereignBaseAgent.py` | Modified | Add `AGENT_REASONING_CLASS: ClassVar` default |
| D | `agentic_core/L3_orchestration/reasoning/FissionManagerAgent.py` | Modified | Migrate caller + register in AGENT_EXECUTION_REGISTRY |
| D | `agentic_core/L5_safety/reasoning/CognitiveDispositionAgent.py` | Modified | Migrate caller + register in AGENT_EXECUTION_REGISTRY |
| D | `agentic_core/L2_execution/reasoning/StructuredEngineAgent.py` | Modified | Migrate caller + register in AGENT_EXECUTION_REGISTRY |
| E | `agentic_core/L1_cognition/types/memory_types.py` | Modified | 4 SSOT pins |
| E | `EmbeddingSovereignAgent.py` (locate via AST) | Modified | Startup model + dimension invariant |
| E | `system_learning/engines/seed_pack_loader.py` | **NEW** | Loader with 5-step integrity checks |
| F | `agentic_core/L2_execution/healers/healing_tier_dispatcher.py` | Modified | `CompositeHealingInvoker` + factory |
| F | `agentic_core/L2_execution/healers/healing_provider_adapters.py` | Modified | `temperature=0.1` → `0.0` |

---

## Explicitly Out of Scope

- Success-rate materializer — optimization, not sovereignty blocker
- Embedding recall as confidence augmentation — future phase after F completes
- apps_lic spine adapter — no violation found in Phase 0 inspection
- MetaLearningClientMixin in engines — already clean, no change needed
- `agentic_process_mapping.md` — target state, not modified

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

