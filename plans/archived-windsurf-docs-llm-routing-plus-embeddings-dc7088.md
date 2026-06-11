---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\llm-routing-plus-embeddings-dc7088.md'
original_relative_path: 'llm-routing-plus-embeddings-dc7088.md'
source_sha256: 93255317cfd5d6f9aa9c46bc9ae0c9165819736402a6c2c11b1a062362cff3e2
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-26'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# LLM Routing + Embedding-Augmented Point-in-Time Adaptation: Full Merged Plan

Implement hardened LLM routing (generation vs healing split, deterministic by default) AND wire the 100K healing_contexts seed pack into all layers so agents adapt at the moment of decision instead of after-the-fact.

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


## Critical Gap Analysis (from repo code review)

### Embedding Gaps
| Issue | Location | Impact |
|-------|----------|--------|
| `EMBEDDING_DIMENSION = 1536` (ada-002) | `memory_types.py:16` | **Mismatch** — seed pack is 3072 (text-embedding-3-large) |
| No `SeedLoader` exists | Anywhere | Seed pack **never loaded** into Pinecone |
| `ml_enhanced_heal()` defined but **zero agents call it** | `meta_learning_client_mixin.py:478` | Mixin is dead code for all agents |
| `BaseRGEngine` does NOT inherit `MetaLearningClientMixin` | `base_rg_engine.py` | apps_rg engines have no embedding retrieval |
| `apps_lic` has no meta-learning wiring | All of apps_lic | Complete blind spot |
| No pre-call embedding lookup in `@standard_heal` | `decorators_util.py` | Healing bypasses pattern memory entirely |
| No pre-call embedding lookup in `dispatch_healing()` | `healing_tier_dispatcher.py` | Tier routing ignores historical patterns |

### LLM Routing Gaps
| Issue | Location | Impact |
|-------|----------|--------|
| `call_llm()` does not exist | `mcp_operation_mixin.py` | `BulletGenerationTask` silently broken |
| `invoke_qwen_vllm()` / `invoke_gemini()` are stubs | `healing_tier_dispatcher.py` | No actual LLM calls for healing |
| `temperature=0.7` default | `SovereignLLMGateway.generate()` | Stochastic by default — breaks replay |
| No `ReasoningClass` enum | Anywhere | Binary HIGH/LOW only |
| `_HISTORICAL_SUCCESS_RATES` is in-memory only | `healing_tier_router.py` | Resets on process restart, L4 never consulted |

---

## The Core Objective: Point-in-Time Adaptation

Before any LLM call or healing decision, check:
```
1. Embed the current violation/intent → 3072-dim vector
2. Query Pinecone healing_contexts namespace (100K pre-loaded patterns)
3. If similarity >= threshold → apply recalled strategy directly (no LLM call)
4. If no match → proceed to LLM tier routing
5. After successful heal → store new pattern back to Pinecone + update L4
```

This eliminates the "find mistake → additional cycle to correct" loop.

---

## Phase 0 — Fix Dimension Mismatch (BLOCKER)

**File:** `agentic_core/L1_cognition/types/memory_types.py`

Line 16 must change:
```python
# Before (ada-002)
EMBEDDING_DIMENSION: Final[int] = 1536

# After (text-embedding-3-large matching seed pack)
EMBEDDING_DIMENSION: Final[int] = 3072
EMBEDDING_MODEL: Final[str] = "text-embedding-3-large"
```

**File:** `agentic_core/L2_execution/reasoning/EmbeddingSovereignAgent.py`

Verify/update model used for embedding calls matches `text-embedding-3-large`.

---

## Phase 1 — Seed Pack Loader

**New file:** `system_learning/engines/seed_pack_loader.py`

Loads `C:\AgenticEmbeddings\seed_packs\healing_contexts\<hash>\` into Pinecone:

```python
SEED_PACK_PATH = Path(
    r"C:\AgenticEmbeddings\seed_packs\healing_contexts"
    r"\5d94b5b12ec92312d0240be9984ff92b9478f74ed6f1335511a202c5351520d9"
)
SEED_MANIFEST = SEED_PACK_PATH / "seed_manifest.json"
ROW_INDEX = SEED_PACK_PATH / "row_index.jsonl"
EMBEDDINGS_FILE = SEED_PACK_PATH / "embeddings.f32"

# Manifest verified values:
# - vector_count: 100,000
# - dimensions: 3072
# - namespace: "healing_contexts"
# - matrix_hash: "0cb16404980544407a48815dd7ffd174d39e99399fccd34d138c760311281fbb"
# - embedding_model_version: "text-embedding-3-large"

def load_seed_pack_to_pinecone(pinecone_index, *, batch_size=100, dry_run=False):
    """Load seed embeddings into Pinecone healing_contexts namespace.

    - Reads embeddings.f32 as float32 matrix (100000 x 3072)
    - Reads row_index.jsonl for metadata per row
    - Verifies matrix_hash before loading
    - Upserts in batches of batch_size
    - Idempotent: skips rows already present
    """
```

**New file:** `ops_scripts/ci/verify_seed_pack_loaded.py`

CI check: Assert Pinecone `healing_contexts` namespace has >= 99000 vectors.

---

## Phase 2 — Add `ReasoningClass` Enum

**New file:** `agentic_core/config/reasoning_class.py`

```python
class ReasoningClass(Enum):
    DETERMINISTIC = 0  # No LLM, no embedding lookup
    LIGHT = 1          # Qwen vLLM, temp=0, embedding pre-flight
    STRATEGIC = 2      # Gemini-2.5-pro, temp=0, embedding pre-flight
    ORCHESTRATOR = 3   # Gemini-2.5-pro, temp=0, higher budget
    HEALER = 4         # dispatch_healing() path only

REASONING_CLASS_POLICY = {
    ReasoningClass.LIGHT:       {"provider": "qwen_vllm", "model_env": "QWEN_MODEL",       "model_default": "qwen2.5-coder-32b-instruct", "temperature": 0.0, "token_budget": 2048},
    ReasoningClass.STRATEGIC:   {"provider": "google",    "model_env": "GEMINI_PRO_MODEL",  "model_default": "gemini-2.5-pro",             "temperature": 0.0, "token_budget": 8192},
    ReasoningClass.ORCHESTRATOR:{"provider": "google",    "model_env": "GEMINI_PRO_MODEL",  "model_default": "gemini-2.5-pro",             "temperature": 0.0, "token_budget": 16384},
}
```

---

## Phase 3 — Embedding Pre-Flight in `@standard_heal` Seam

**File:** `agentic_core/utils/decorators_util.py`

Inside `standard_heal` wrapper, BEFORE calling `decide_heal_escalation()`, add:

```python
# Step A: Attempt embedding recall BEFORE LLM escalation decision
_recalled = None
_ml_mixin = args[0] if args else None  # self
if hasattr(_ml_mixin, "ml_recall_healing_pattern"):
    _recalled = _ml_mixin.ml_recall_healing_pattern(violation_dict)
    if _recalled:
        # Pattern found — apply directly, skip LLM escalation
        Logger.info(f"[standard_heal] Embedding recall hit — skipping LLM for {agent_name}")
        return _build_heal_result_from_pattern(_recalled)
```

This is the **highest-value change**: prevents LLM calls for violations seen before.

---

## Phase 4 — Embedding Pre-Flight in `dispatch_healing()`

**File:** `agentic_core/L2_execution/healers/healing_tier_dispatcher.py`

In `dispatch_healing()`, after routing decision, before invocation:

```python
# Embedding recall: attempt pattern match before LLM provider call
if decision.tier != HealingTier.LOCAL_AGENT:
    from agentic_core.L1_cognition.engines.memory_embedder import get_healing_memory_embedder
    from agentic_core.L1_cognition.engines.meta_client import get_meta_learning_client

    embedder = get_healing_memory_embedder()
    client = get_meta_learning_client()
    violation_dict = {
        "type": healing_input.failure_type,
        "path": "",
        "message": healing_input.error_signature,
        "domain": "agentic_core",
    }
    recalled = client.retrieve_healing_patterns(violation_dict, "agentic_core", top_k=1)
    if recalled and recalled[0].get("similarity_score", 0) >= 0.85:
        # Cache hit — return synthetic InvocationRecord, skip LLM
        Logger.info(f"[dispatch_healing] Embedding recall hit for {healing_input.failure_type}")
        return decision, InvocationRecord(
            tier=decision.tier,
            model_id="embedding_recall",
            agent_name=agent_name,
            trace_id=healing_input.trace_id,
            heal_confidence=decision.heal_confidence,
            method_called="embedding_recall",
        )
```

---

## Phase 5 — Wire Real Provider Calls in Stubs

**File:** `agentic_core/L2_execution/healers/healing_tier_dispatcher.py`

Replace stub bodies in `DefaultHealingProviderInvoker`:

```python
def invoke_qwen_vllm(self, healing_input, decision, config, *, agent_name=""):
    import asyncio
    from agentic_core.L2_execution.enforcement.SovereignLLMGateway import get_llm_gateway
    gateway = get_llm_gateway()
    prompt = self._build_healing_prompt(healing_input)
    asyncio.get_event_loop().run_until_complete(
        gateway.generate(prompt, provider="qwen_vllm",
                        model=config.model_qwen_vllm_id,
                        temperature=0.0, trace_id=healing_input.trace_id)
    )
    return InvocationRecord(tier=HealingTier.QWEN_VLLM,
                           model_id=config.model_qwen_vllm_id,
                           agent_name=agent_name, trace_id=healing_input.trace_id,
                           heal_confidence=decision.heal_confidence,
                           method_called="invoke_qwen_vllm")

def invoke_gemini(self, healing_input, decision, config, *, agent_name=""):
    import asyncio
    from agentic_core.L2_execution.enforcement.SovereignLLMGateway import get_llm_gateway
    gateway = get_llm_gateway()
    prompt = self._build_healing_prompt(healing_input)
    asyncio.get_event_loop().run_until_complete(
        gateway.generate(prompt, provider="google",
                        model=config.model_gemini_2_5_pro_id,
                        temperature=0.0, trace_id=healing_input.trace_id)
    )
    return InvocationRecord(tier=HealingTier.GEMINI_2_5_PRO,
                           model_id=config.model_gemini_2_5_pro_id,
                           agent_name=agent_name, trace_id=healing_input.trace_id,
                           heal_confidence=decision.heal_confidence,
                           method_called="invoke_gemini")

def _build_healing_prompt(self, healing_input: HealingInput) -> str:
    return (
        f"HEALING REQUEST\nfailure_type: {healing_input.failure_type}\n"
        f"error_signature: {healing_input.error_signature}\n"
        f"blast_radius: {healing_input.blast_radius_estimate}\n"
        f"retry_count: {healing_input.retry_count}\n"
        f"Provide a minimal, deterministic fix."
    )
```

---

## Phase 6 — Wire `ml_enhanced_heal()` into `heal_repository()` Pattern

**File:** `agentic_core/mixins/healing_mixin.py` (or `SovereignBaseAgent.py`)

The `ml_enhanced_heal()` method exists but zero agents call it. Add a base implementation that wraps `heal_repository()`:

```python
def heal_repository(self, *args, **kwargs) -> dict:
    """Override: wrap with ml_enhanced_heal for embedding-augmented healing."""
    violation = {"type": "heal_repository", "path": str(getattr(self, "project_root", "")),
                 "domain": self._get_ml_domain() if hasattr(self, "_get_ml_domain") else "agentic_core"}
    return self.ml_enhanced_heal(
        violation,
        super().heal_repository,
        *args, **kwargs,
    )
```

This activates the **recall → execute → store** loop for every `heal_repository()` call system-wide.

---

## Phase 7 — Fix `apps_rg` BaseRGEngine: Add MetaLearningClientMixin

**File:** `apps_rg/engines/base_rg_engine.py`

`BaseRGEngine` inherits `MCPHardenedMixin` + `HealerMixin` but NOT `MetaLearningClientMixin`.

```python
# Before
class BaseRGEngine(MCPHardenedMixin, HealerMixin, ABC):

# After
from agentic_core.mixins.meta_learning_client_mixin import MetaLearningClientMixin

class BaseRGEngine(MCPHardenedMixin, HealerMixin, MetaLearningClientMixin, ABC):
    _ml_domain = "apps_rg"
```

Also add `AGENT_REASONING_CLASS` + `call_llm()` from LLM routing plan:

```python
from agentic_core.config.reasoning_class import ReasoningClass
AGENT_REASONING_CLASS: ReasoningClass = ReasoningClass.LIGHT  # override per engine
```

---

## Phase 8 — Wire apps_lic Active Spine Path

**File:** `apps_lic/engines/lic_spine_adapter.py` (active LIC path)

Add meta-learning pre-flight to `ExecutionOrchestrator.execute()` via a `_HopObserver` seam:

```python
# After AirlockAssembler.assemble(), before PathRouter.select_path():
# Query embedding recall for similar past executions
recalled_path = self._recall_execution_pattern(payload)
if recalled_path:
    # Use recalled path without full routing re-computation
    return recalled_path
```

New `LicMetaLearningBridge`:
- Domain: `apps_lic`
- Namespace: `healing_contexts` (shared) + `apps_lic` isolation
- `similarity_threshold`: 0.92 (existing domain config)

---

## Phase 9 — Add `route_generation()` to Gateway

**File:** `agentic_core/L2_execution/enforcement/SovereignLLMGateway.py`

```python
async def route_generation(
    self, prompt: str, reasoning_class: ReasoningClass,
    trace_id: str, *, token_budget_limit: int = 0,
) -> dict:
    """Production generation path. Separate from healing/dispatch_healing()."""
    from agentic_core.config.reasoning_class import REASONING_CLASS_POLICY, ReasoningClass
    if reasoning_class in (ReasoningClass.DETERMINISTIC, ReasoningClass.HEALER):
        raise ValueError(f"Cannot call route_generation() with {reasoning_class}")
    policy = REASONING_CLASS_POLICY[reasoning_class]
    return await self.generate(
        prompt,
        provider=policy["provider"],
        model=os.getenv(policy["model_env"], policy["model_default"]),
        temperature=policy["temperature"],  # Always 0.0
        token_budget_limit=token_budget_limit or policy["token_budget"],
        trace_id=trace_id,
    )
```

---

## Phase 10 — Implement `call_llm()` in `MCPOperationMixin`

**File:** `agentic_core/mixins/mcp_operation_mixin.py`

```python
async def call_llm(
    self, prompt: str, *,
    reasoning_class=None, trace_id: str | None = None,
) -> str:
    """Production generation + embedding pre-flight. NOT healing path."""
    from agentic_core.config.reasoning_class import ReasoningClass
    from agentic_core.L2_execution.enforcement.SovereignLLMGateway import get_llm_gateway
    from agentic_core.L0_routing.enforcement.traceability_contracts import generate_trace_id

    # Embedding pre-flight: check pattern memory before LLM call
    if hasattr(self, "ml_recall_healing_pattern"):
        violation = {"type": "generation", "path": prompt[:200], "domain": "apps_rg"}
        recalled = self.ml_recall_healing_pattern(violation)
        if recalled:
            return recalled.get("content", recalled.get("output", ""))

    cls = reasoning_class or getattr(self, "AGENT_REASONING_CLASS", ReasoningClass.LIGHT)
    result = await get_llm_gateway().route_generation(
        prompt, cls, trace_id or generate_trace_id()
    )
    return result.get("content", "")
```

---

## Phase 11 — Migrate 3 Direct `llm_generate()` Callers

| Agent | File | Change |
|-------|------|--------|
| `FissionManagerAgent` | `L3_orchestration/reasoning/FissionManagerAgent.py` line 49 | `llm_generate(provider="google", model=os.getenv("GEMINI_PRO_MODEL"))` → `llm_gateway.route_generation(prompt, ReasoningClass.ORCHESTRATOR, trace_id)` |
| `CognitiveDispositionAgent` | `L5_safety/reasoning/CognitiveDispositionAgent.py` line 103 | `llm_generate(provider="google", generation_config={"temperature": 0.1})` → `llm_gateway.route_generation(prompt, ReasoningClass.STRATEGIC, trace_id)` |
| `StructuredEngineAgent` | `L2_execution/reasoning/StructuredEngineAgent.py` line 40 | `llm_generate(provider="google", model=os.getenv("GEMINI_MODEL"))` → `llm_gateway.route_generation(prompt, ReasoningClass.STRATEGIC, trace_id)` |

---

## Phase 12 — Update `_HISTORICAL_SUCCESS_RATES` to Read from L4/Pinecone

**File:** `agentic_core/L2_execution/healers/healing_tier_router.py`

`get_historical_success_rate()` currently returns from an in-memory dict that resets on restart.

Replace with L4-backed lookup:
```python
def get_historical_success_rate(error_signature: str) -> float:
    """Live lookup from MetaLearningClient instead of in-memory dict."""
    try:
        from agentic_core.L1_cognition.engines.meta_client import get_meta_learning_client
        client = get_meta_learning_client()
        cached = client.cache_get(f"success_rate:{error_signature}", "healing_router")
        if cached is not None:
            return float(cached)
    except Exception:
        pass
    return _NEUTRAL_PRIOR
```

This makes tier routing thresholds adapt over time based on real Pinecone data.

---

## Phase 13 — AST-Based CI Guard

**New file:** `ops_scripts/ci/check_llm_routing_compliance.py`

AST checks:
1. All `*Agent.py` and `*Engine.py` declare `AGENT_REASONING_CLASS`
2. No model string literals in agent/engine files
3. No `temperature=` kwargs outside gateway
4. No `os.getenv("GEMINI_*")` or `os.getenv("QWEN_*")` in agent files
5. No `httpx`/`aiohttp`/`requests` imports in agent files

---

## Execution Sequence

```
Phase 0  → Fix EMBEDDING_DIMENSION mismatch (1536 → 3072) — BLOCKER
Phase 1  → Load seed pack: 100K vectors → Pinecone healing_contexts
Phase 2  → ReasoningClass enum + REASONING_CLASS_POLICY
Phase 3  → Embedding pre-flight in @standard_heal
Phase 4  → Embedding pre-flight in dispatch_healing()
Phase 5  → Wire real provider stubs (Qwen + Gemini)
Phase 6  → Activate ml_enhanced_heal() in heal_repository() base
Phase 7  → BaseRGEngine: add MetaLearningClientMixin
Phase 8  → apps_lic spine: embedding recall seam
Phase 9  → route_generation() in SovereignLLMGateway
Phase 10 → call_llm() in MCPOperationMixin
Phase 11 → Migrate 3 direct llm_generate() callers
Phase 12 → Historical success rates from L4/Pinecone
Phase 13 → AST CI guard
```

---

## Files Changed

| Phase | File | N | Type |
|-------|------|---|------|
| 0 | `L1_cognition/types/memory_types.py` | 1 | MODIFY |
| 0 | `L2_execution/reasoning/EmbeddingSovereignAgent.py` | 1 | VERIFY |
| 1 | `system_learning/engines/seed_pack_loader.py` | 1 | NEW |
| 1 | `ops_scripts/ci/verify_seed_pack_loaded.py` | 1 | NEW |
| 2 | `agentic_core/config/reasoning_class.py` | 1 | NEW |
| 3 | `agentic_core/utils/decorators_util.py` | 1 | MODIFY |
| 4 | `healing_tier_dispatcher.py` | 1 | MODIFY |
| 5 | `healing_tier_dispatcher.py` | — | same file |
| 6 | `agentic_core/mixins/healing_mixin.py` | 1 | MODIFY |
| 7 | `apps_rg/engines/base_rg_engine.py` | 1 | MODIFY |
| 8 | `apps_lic/engines/lic_spine_adapter.py` | 1 | MODIFY |
| 9 | `SovereignLLMGateway.py` | 1 | MODIFY |
| 10 | `mcp_operation_mixin.py` | 1 | MODIFY |
| 11 | 3 agent files | 3 | MODIFY |
| 12 | `healing_tier_router.py` | 1 | MODIFY |
| 13 | `ops_scripts/ci/check_llm_routing_compliance.py` | 1 | NEW |
| 2 | `SovereignBaseAgent.py` | 1 | MODIFY |
| **Total** | | **18 files** | |

---

## Success Criteria

1. Seed pack loaded: Pinecone `healing_contexts` namespace has 100K vectors at 3072 dims
2. Embedding recall fires BEFORE every LLM call in `@standard_heal` and `dispatch_healing()`
3. apps_rg engines get embedding memory via `MetaLearningClientMixin`
4. apps_lic has embedding recall seam in active spine path
5. Production generation separated from healing path
6. All LLM calls deterministic by default (temp=0)
7. Historical success rates adapt from Pinecone, not reset on restart
8. CI blocks model literals, temp kwargs, provider imports in agents

---

## Point-in-Time Adaptation Loop (End State)

```
Violation occurs
      ↓
Embed violation (3072-dim, text-embedding-3-large)
      ↓
Query Pinecone healing_contexts (100K vectors)
      ↓
similarity >= 0.85?
   YES → apply recalled strategy → update success rate → done (no LLM call)
   NO  → compute heal_confidence via FAILURE_CLASS_PRIORS
             ↓
         confidence >= 0.75 → LOCAL_AGENT
         confidence 0.40-0.75 → Qwen vLLM (temp=0)
         confidence < 0.40 → Gemini 2.5 Pro (temp=0)
             ↓
         store successful result → Pinecone + Redis
             ↓
         next similar violation → cache hit (no LLM call)
```

## Gap Register

| Gap | Priority | Impact | Status |
|------|----------|--------|---------|
| [Gap 1] | High | Critical | Open |
| [Gap 2] | Medium | Moderate | In Progress |

---

## Execution Plan

1. **Phase 1**: Analysis and Planning
2. **Phase 2**: Implementation
3. **Phase 3**: Testing and Validation
4. **Phase 4**: Documentation and Cleanup

---

