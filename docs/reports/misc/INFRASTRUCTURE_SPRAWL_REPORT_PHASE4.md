# Infrastructure Sprawl Analysis Report - Phase 4+

## Comprehensive Codebase Audit

**Generated:** January 22, 2026
**Analysis Scope:** All approved folders in `agentic_core/`
**Methodology:** Pattern analysis following successful Redis (Phase 2), Pinecone (Phase 1), and MCP/Cache (Phase 3) consolidations

---

## Executive Summary

Following the successful consolidation of **Pinecone** (Phase 1), **Redis** (Phase 2), and **MCP/SemanticCache** (Phase 3), this report identifies **6 additional infrastructure sprawl patterns** requiring consolidation:

| Pattern | Files Found | Severity | Consolidation Target | Phase |
|---------|-------------|----------|---------------------|-------|
| **LLM/Inference Engine** | 6+ files | 🔴 HIGH | `SovereignLLMGateway` | Phase 4 |
| **Embedding Providers** | 5 files | 🔴 HIGH | `EmbeddingSovereignAgent` | Phase 4 |
| **Healing Strategies** | 12 files | 🔴 HIGH | `HealingSovereignOrchestrator` | Phase 5 |
| **Validator Sprawl** | 18 files | 🟡 MEDIUM | `ValidatorOrchestrator` | Phase 5 |
| **Config Duplication** | 13 files | 🟡 MEDIUM | `SovereignConfigManager` | Phase 6 |
| **Mixin Integration Gap** | 102 mixins | 🟡 MEDIUM | Audit & integrate into base agents | Phase 6 |

**Total Files for Consolidation:** 56+ files
**Expected Reduction:** 56 → 12 files (78% reduction)

---

## Pattern 1: LLM/Inference Engine Sprawl 🔴 HIGH PRIORITY

### Current State

**6+ LLM/Inference Files Found:**

```
agentic_core/
├── L1_cognition/thought_engine/
│   └── llm_engine.py                    # 3 classes: BaseLLMEngine, etc.
├── L2_execution/mcp/
│   ├── inference_engine.py              # 12 classes! Multi-provider
│   └── llm_router_mcp_client.py         # [DEPRECATED in Phase 3]
├── L2_execution/unified/
│   └── UnifiedModelRouterAgent.py       # Another router
├── L2_execution/ToolRegistry/
│   └── format_llm_prompt.py             # Prompt formatting
└── L3_orchestration/workflow_engines/
    └── SovereignMcpRouter.py            # MCP routing
```

### Problem Analysis

**Symptoms of Sprawl:**
- **17+ direct SDK imports** for OpenAI/Anthropic/Google across 17 files
- `inference_engine.py` has **12 classes** - massive file doing too much
- Multiple router implementations (`UnifiedModelRouterAgent`, `SovereignMcpRouter`, `llm_router_mcp_client`)
- No centralized audit logging for LLM calls
- No unified retry/fallback strategy
- Each file reinvents provider switching logic

**Direct SDK Imports (Unhardened):**
```
inference_engine.py                    - 4 imports (openai, anthropic, google)
runtime_shared_multi_provider_clients.py - 3 imports
subatomic_engine.py                    - 3 imports
L2ExecutionBase.py                - 2 imports
FissionManagerAgent.py                 - 2 imports
CognitiveDispositionAgent.py           - 2 imports
HallucinationHunterAgent.py            - 2 imports
+ 10 more files with direct imports
```

### Proposed Solution: Phase 4 Consolidation

#### **Target Architecture**

```
agentic_core/L2_execution/mcp/
├── SovereignLLMGateway.py             # [NEW] Unified LLM gateway
├── llm_provider_mixin.py              # [NEW] Mixin for agents
└── archived/
    ├── inference_engine.py            # Absorbed into gateway
    ├── llm_router_mcp_client.py       # Already deprecated
    └── runtime_shared_multi_provider_clients.py
```

**Reduction:** 6+ → 2 files (67% reduction)

---

### Detailed File Diffs

#### **Target 1: Create `SovereignLLMGateway.py`**

```python
<<<<
# NEW FILE: agentic_core/L2_execution/mcp/SovereignLLMGateway.py
====
"""
SovereignLLMGateway - Unified LLM Operations Gateway

[PHASE 4 MIGRATION] Consolidates all LLM provider operations:
- OpenAI (GPT-4, GPT-4o, o1)
- Anthropic (Claude 3.5)
- Google (Gemini)
- Centralized audit logging
- Unified retry/fallback strategy
- Provider health monitoring
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Literal
import time
import logging
import os

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

Logger = logging.getLogger(__name__)

Provider = Literal["openai", "anthropic", "google"]

@dataclass
class SovereignLLMGateway(SovereignBaseAgent):
    """
    Unified LLM Gateway - Single point of truth for all LLM operations.

    [PHASE 4 MIGRATION] Absorbed from:
    - inference_engine.py (12 classes)
    - llm_engine.py
    - UnifiedModelRouterAgent.py
    - runtime_shared_multi_provider_clients.py
    """

    _instance = None
    operation_stats = {
        "openai": 0,
        "anthropic": 0,
        "google": 0,
        "total": 0,
        "errors": 0,
        "fallbacks": 0
    }

    # Provider clients (lazy-loaded)
    _openai_client = None
    _anthropic_client = None
    _google_client = None

    def __new__(cls):
        """Singleton constructor."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _audit(self, provider: str, model: str, success: bool, latency_ms: float, tokens: int = 0) -> None:
        """[PHASE 4] Record LLM operation to audit plane."""
        if not hasattr(self, "audit_log"):
            self.audit_log = []
        self.audit_log.append({
            "provider": provider,
            "model": model,
            "success": success,
            "latency_ms": latency_ms,
            "tokens": tokens,
            "ts": time.time()
        })
        self.operation_stats["total"] += 1
        if not success:
            self.operation_stats["errors"] += 1
        else:
            self.operation_stats[provider] = self.operation_stats.get(provider, 0) + 1

    @property
    def openai(self):
        """Lazy-load OpenAI client."""
        if self._openai_client is None:
            try:
                import openai
                self._openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            except Exception as e:
                Logger.warning(f"OpenAI client init failed: {e}")
        return self._openai_client

    @property
    def anthropic(self):
        """Lazy-load Anthropic client."""
        if self._anthropic_client is None:
            try:
                import anthropic
                self._anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            except Exception as e:
                Logger.warning(f"Anthropic client init failed: {e}")
        return self._anthropic_client

    @property
    def google(self):
        """Lazy-load Google client."""
        if self._google_client is None:
            try:
                import google.generativeai as genai
                genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
                self._google_client = genai
            except Exception as e:
                Logger.warning(f"Google client init failed: {e}")
        return self._google_client

    async def generate(
        self,
        prompt: str,
        model: str = "gpt-4o",
        provider: Provider = "openai",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        fallback_providers: list[Provider] = None,
        **kwargs
    ) -> dict:
        """
        Generate LLM response with automatic fallback.

        [PHASE 4] Unified interface for all providers.
        """
        fallback_providers = fallback_providers or ["anthropic", "google"]
        providers_to_try = [provider] + [p for p in fallback_providers if p != provider]

        last_error = None
        for current_provider in providers_to_try:
            start = time.time()
            try:
                result = await self._call_provider(
                    current_provider, prompt, model, temperature, max_tokens, **kwargs
                )
                latency = (time.time() - start) * 1000
                self._audit(current_provider, model, True, latency, result.get("tokens", 0))

                if current_provider != provider:
                    self.operation_stats["fallbacks"] += 1
                    Logger.info(f"[LLM Gateway] Fallback to {current_provider} succeeded")

                return result

            except Exception as e:
                latency = (time.time() - start) * 1000
                self._audit(current_provider, model, False, latency)
                last_error = e
                Logger.warning(f"[LLM Gateway] {current_provider} failed: {e}")
                continue

        raise RuntimeError(f"All LLM providers failed. Last error: {last_error}")

    async def _call_provider(
        self,
        provider: Provider,
        prompt: str,
        model: str,
        temperature: float,
        max_tokens: int,
        **kwargs
    ) -> dict:
        """Route to specific provider implementation."""
        if provider == "openai":
            return await self._call_openai(prompt, model, temperature, max_tokens, **kwargs)
        elif provider == "anthropic":
            return await self._call_anthropic(prompt, model, temperature, max_tokens, **kwargs)
        elif provider == "google":
            return await self._call_google(prompt, model, temperature, max_tokens, **kwargs)
        else:
            raise ValueError(f"Unknown provider: {provider}")

    async def _call_openai(self, prompt: str, model: str, temperature: float, max_tokens: int, **kwargs) -> dict:
        """Call OpenAI API."""
        response = self.openai.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        return {
            "content": response.choices[0].message.content,
            "tokens": response.usage.total_tokens if response.usage else 0,
            "provider": "openai",
            "model": model
        }

    async def _call_anthropic(self, prompt: str, model: str, temperature: float, max_tokens: int, **kwargs) -> dict:
        """Call Anthropic API."""
        # Map model names if needed
        anthropic_model = model if "claude" in model else "claude-3-5-sonnet-20241022"
        response = self.anthropic.messages.create(
            model=anthropic_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        return {
            "content": response.content[0].text,
            "tokens": response.usage.input_tokens + response.usage.output_tokens if response.usage else 0,
            "provider": "anthropic",
            "model": anthropic_model
        }

    async def _call_google(self, prompt: str, model: str, temperature: float, max_tokens: int, **kwargs) -> dict:
        """Call Google Gemini API."""
        google_model = model if "gemini" in model else "gemini-1.5-flash"
        gen_model = self.google.GenerativeModel(google_model)
        response = gen_model.generate_content(
            prompt,
            generation_config={"temperature": temperature, "max_output_tokens": max_tokens}
        )
        return {
            "content": response.text,
            "tokens": 0,  # Gemini doesn't always return token count
            "provider": "google",
            "model": google_model
        }


# Singleton accessor
_llm_gateway_instance = None

def get_llm_gateway() -> SovereignLLMGateway:
    """Get or create the global LLM gateway."""
    global _llm_gateway_instance
    if _llm_gateway_instance is None:
        _llm_gateway_instance = SovereignLLMGateway()
    return _llm_gateway_instance
>>>>
```

#### **Target 2: Create `llm_provider_mixin.py`**

```python
<<<<
# NEW FILE: agentic_core/L2_execution/mcp/llm_provider_mixin.py
====
"""
LLMProviderMixin - Unified LLM Access for Agents

[PHASE 4 MIGRATION] Provides single interface to all LLM providers.
"""

from typing import Any, Literal

Provider = Literal["openai", "anthropic", "google"]


class LLMProviderMixin:
    """
    Mixin providing unified LLM gateway access.

    [PHASE 4 MIGRATION] Replaces direct SDK imports.

    Usage:
        class MyAgent(LLMProviderMixin, SovereignBaseAgent):
            async def process(self, query: str):
                response = await self.llm_generate(query)
                return response["content"]
    """

    _llm_gateway = None

    @property
    def llm_gateway(self):
        """Lazy-load LLM gateway singleton."""
        if self._llm_gateway is None:
            from agentic_core.L2_execution.mcp.SovereignLLMGateway import get_llm_gateway
            self._llm_gateway = get_llm_gateway()
        return self._llm_gateway

    async def llm_generate(
        self,
        prompt: str,
        model: str = "gpt-4o",
        provider: Provider = "openai",
        **kwargs
    ) -> dict:
        """Generate LLM response through gateway."""
        return await self.llm_gateway.generate(prompt, model=model, provider=provider, **kwargs)

    async def llm_generate_with_fallback(
        self,
        prompt: str,
        model: str = "gpt-4o",
        fallback_providers: list[Provider] = None,
        **kwargs
    ) -> dict:
        """Generate with automatic provider fallback."""
        return await self.llm_gateway.generate(
            prompt, model=model, fallback_providers=fallback_providers, **kwargs
        )
>>>>
```

---

### Test Cases for Phase 4 (LLM)

| Test Case | Procedure | Expected Result |
|-----------|-----------|-----------------|
| **TC-LLM-001** | Instantiate `SovereignLLMGateway` and check `operation_stats`. | Stats dict exists with provider keys. |
| **TC-LLM-002** | Call `generate()` with mock provider. | Audit log updated with operation. |
| **TC-LLM-003** | Search for direct `import openai` outside gateway. | Only gateway has direct import. |
| **TC-LLM-004** | Use `LLMProviderMixin` in agent. | Delegates to gateway successfully. |
| **TC-LLM-005** | Trigger fallback by failing primary provider. | Fallback counter increments. |

---

## Pattern 2: Embedding Provider Sprawl 🔴 HIGH PRIORITY

### Current State

**5 Embedding Files Found:**

```
agentic_core/
├── semantic_memory/embeddings/
│   ├── core_embedder.py               # Base embedder
│   └── gemini_embedder.py             # Gemini-specific
├── L0_maintenance/scripts/
│   ├── populate_pinecone_embeddings.py
│   └── runtime_shared_batch_embeddings.py
└── L5_safety/validators/
    └── PineconeSovereignAgent.py      # Has get_embedding() method
```

### Problem Analysis

- Multiple embedding implementations with no shared interface
- `PineconeSovereignAgent` has its own `get_embedding()` - should use mixin
- No centralized dimension validation
- Batch embedding logic duplicated

### Proposed Solution

```
agentic_core/L2_execution/mcp/
├── EmbeddingSovereignAgent.py         # [NEW] Unified embedding gateway
├── embedding_mixin.py                 # [NEW] Mixin for agents
└── archived/
    ├── gemini_embedder.py
    └── core_embedder.py
```

---

### Detailed File Diffs

#### **Target 3: Create `EmbeddingSovereignAgent.py`**

```python
<<<<
# NEW FILE: agentic_core/L2_execution/mcp/EmbeddingSovereignAgent.py
====
"""
EmbeddingSovereignAgent - Unified Embedding Gateway

[PHASE 4 MIGRATION] Consolidates all embedding operations:
- Gemini embeddings
- OpenAI embeddings
- Dimension validation
- Batch processing
- Redis caching integration
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Literal
import time
import logging
import os
import hashlib

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.utils.core_extensions.redis_cache_mixin import RedisCacheMixin

Logger = logging.getLogger(__name__)

EmbeddingProvider = Literal["gemini", "openai"]

@dataclass
class EmbeddingSovereignAgent(SovereignBaseAgent, RedisCacheMixin):
    """
    Unified Embedding Gateway with Redis caching.

    [PHASE 4 MIGRATION] Absorbed from:
    - gemini_embedder.py
    - core_embedder.py
    - PineconeSovereignAgent.get_embedding()
    """

    _instance = None
    _cache_prefix = "emb"
    _default_ttl = 86400  # 24 hours

    EXPECTED_DIMENSIONS = {
        "gemini": 768,
        "openai": 1536,
    }

    operation_stats = {
        "gemini": 0,
        "openai": 0,
        "cache_hits": 0,
        "cache_misses": 0,
        "total": 0
    }

    def __new__(cls):
        """Singleton constructor."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _audit(self, provider: str, success: bool, cached: bool, latency_ms: float) -> None:
        """[PHASE 4] Record embedding operation."""
        if not hasattr(self, "audit_log"):
            self.audit_log = []
        self.audit_log.append({
            "provider": provider,
            "success": success,
            "cached": cached,
            "latency_ms": latency_ms,
            "ts": time.time()
        })
        self.operation_stats["total"] += 1
        if cached:
            self.operation_stats["cache_hits"] += 1
        else:
            self.operation_stats["cache_misses"] += 1
            if success:
                self.operation_stats[provider] = self.operation_stats.get(provider, 0) + 1

    def _content_hash(self, content: str) -> str:
        """Generate deterministic hash for caching."""
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    async def get_embedding(
        self,
        content: str,
        provider: EmbeddingProvider = "gemini",
        use_cache: bool = True
    ) -> list[float]:
        """
        Get embedding vector with optional caching.

        [PHASE 4] Unified interface for all embedding providers.
        """
        start = time.time()

        # Check cache first
        if use_cache:
            cache_key = f"{provider}:{self._content_hash(content)}"
            cached = await self.cache_get(cache_key)
            if cached:
                latency = (time.time() - start) * 1000
                self._audit(provider, True, True, latency)
                return cached

        # Generate embedding
        try:
            if provider == "gemini":
                embedding = await self._get_gemini_embedding(content)
            elif provider == "openai":
                embedding = await self._get_openai_embedding(content)
            else:
                raise ValueError(f"Unknown provider: {provider}")

            # Validate dimension
            expected_dim = self.EXPECTED_DIMENSIONS.get(provider)
            if expected_dim and len(embedding) != expected_dim:
                Logger.warning(f"Dimension mismatch: got {len(embedding)}, expected {expected_dim}")

            # Cache result
            if use_cache:
                await self.cache_set(cache_key, embedding)

            latency = (time.time() - start) * 1000
            self._audit(provider, True, False, latency)
            return embedding

        except Exception as e:
            latency = (time.time() - start) * 1000
            self._audit(provider, False, False, latency)
            Logger.error(f"Embedding failed: {e}")
            raise

    async def get_embeddings_batch(
        self,
        contents: list[str],
        provider: EmbeddingProvider = "gemini",
        use_cache: bool = True
    ) -> list[list[float]]:
        """
        Get embeddings for multiple contents.

        [PHASE 4] Batch processing with caching.
        """
        results = []
        for content in contents:
            embedding = await self.get_embedding(content, provider, use_cache)
            results.append(embedding)
        return results

    async def _get_gemini_embedding(self, content: str) -> list[float]:
        """Get embedding from Gemini."""
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=content,
            task_type="retrieval_document"
        )
        return result["embedding"]

    async def _get_openai_embedding(self, content: str) -> list[float]:
        """Get embedding from OpenAI."""
        import openai
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=content
        )
        return response.data[0].embedding


# Singleton accessor
_embedding_gateway_instance = None

def get_embedding_gateway() -> EmbeddingSovereignAgent:
    """Get or create the global embedding gateway."""
    global _embedding_gateway_instance
    if _embedding_gateway_instance is None:
        _embedding_gateway_instance = EmbeddingSovereignAgent()
    return _embedding_gateway_instance
>>>>
```

#### **Target 4: Create `embedding_mixin.py`**

```python
<<<<
# NEW FILE: agentic_core/L2_execution/mcp/embedding_mixin.py
====
"""
EmbeddingMixin - Unified Embedding Access for Agents

[PHASE 4 MIGRATION] Provides single interface to embedding operations.
"""

from typing import Literal

EmbeddingProvider = Literal["gemini", "openai"]


class EmbeddingMixin:
    """
    Mixin providing unified embedding gateway access.

    [PHASE 4 MIGRATION] Replaces direct embedding implementations.

    Usage:
        class MyAgent(EmbeddingMixin, SovereignBaseAgent):
            async def process(self, text: str):
                embedding = await self.get_embedding(text)
                return embedding
    """

    _embedding_gateway = None

    @property
    def embedding_gateway(self):
        """Lazy-load embedding gateway singleton."""
        if self._embedding_gateway is None:
            from agentic_core.L2_execution.mcp.EmbeddingSovereignAgent import get_embedding_gateway
            self._embedding_gateway = get_embedding_gateway()
        return self._embedding_gateway

    async def get_embedding(
        self,
        content: str,
        provider: EmbeddingProvider = "gemini",
        use_cache: bool = True
    ) -> list[float]:
        """Get embedding through gateway."""
        return await self.embedding_gateway.get_embedding(content, provider, use_cache)

    async def get_embeddings_batch(
        self,
        contents: list[str],
        provider: EmbeddingProvider = "gemini"
    ) -> list[list[float]]:
        """Get batch embeddings through gateway."""
        return await self.embedding_gateway.get_embeddings_batch(contents, provider)
>>>>
```

---

### Test Cases for Phase 4 (Embedding)

| Test Case | Procedure | Expected Result |
|-----------|-----------|-----------------|
| **TC-EMB-001** | Instantiate `EmbeddingSovereignAgent`. | Singleton with operation_stats. |
| **TC-EMB-002** | Call `get_embedding()` twice with same content. | Second call is cache hit. |
| **TC-EMB-003** | Verify dimension validation. | Warning logged on mismatch. |
| **TC-EMB-004** | Use `EmbeddingMixin` in agent. | Delegates to gateway. |

---

## Pattern 3: Healing Strategy Sprawl 🔴 HIGH PRIORITY

### Current State

**12 Healing Files Found:**

```
agentic_core/
├── L0_maintenance/scripts/
│   ├── healing_deepwiki_healing_strategy.py
│   ├── healing_gitkraken_healing_strategy.py
│   ├── healing_healing_engine.py
│   ├── healing_kg_healing_strategy.py
│   ├── healing_l6_audit_healing_strategy.py
│   ├── healing_vector_healing_strategy.py
│   └── verify_healing_metrics.py
├── L4_state/ledger/
│   └── healing_transaction_manager.py
└── L5_safety/validators/
    ├── healing_healing_strategies.py    # DUPLICATE NAME!
    ├── healing_invocation_audit.py
    ├── healing_strategies.py            # DUPLICATE CONTENT!
    └── healing_strategy.py
```

### Problem Analysis

- **DUPLICATE FILES**: `healing_strategies.py` and `healing_healing_strategies.py` have same 9 classes!
- 12 separate healing files with overlapping functionality
- No unified healing orchestrator
- Inconsistent strategy interfaces

### Proposed Solution

```
agentic_core/L5_safety/validators/
├── HealingSovereignOrchestrator.py    # [NEW] Unified healing gateway
├── healing_strategy_mixin.py          # [NEW] Mixin for agents
└── archived/
    ├── healing_strategies.py
    ├── healing_healing_strategies.py   # Duplicate
    └── [6 L0 healing files]
```

---

### Detailed File Diffs

#### **Target 5: Create `HealingSovereignOrchestrator.py`**

```python
<<<<
# NEW FILE: agentic_core/L5_safety/validators/HealingSovereignOrchestrator.py
====
"""
HealingSovereignOrchestrator - Unified Healing Gateway

[PHASE 5 MIGRATION] Consolidates all healing operations:
- Strategy registration and dispatch
- Healing transaction management
- Metrics collection
- Audit logging
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Protocol, Callable
import time
import logging

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

Logger = logging.getLogger(__name__)


class HealingStrategy(Protocol):
    """Protocol for healing strategies."""

    def can_heal(self, violation: dict) -> bool:
        """Check if this strategy can heal the violation."""
        ...

    def heal(self, violation: dict, context: dict) -> dict:
        """Execute healing and return result."""
        ...


@dataclass
class HealingSovereignOrchestrator(SovereignBaseAgent):
    """
    Unified Healing Orchestrator - Single point of truth for all healing operations.

    [PHASE 5 MIGRATION] Absorbed from:
    - healing_strategies.py (9 strategies)
    - healing_healing_strategies.py (duplicate)
    - healing_healing_engine.py
    - 6 L0 healing strategy files
    """

    _instance = None

    operation_stats = {
        "total_heals": 0,
        "successful_heals": 0,
        "failed_heals": 0,
        "by_strategy": {}
    }

    def __new__(cls):
        """Singleton constructor."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._strategies = {}
        return cls._instance

    def register_strategy(self, name: str, strategy: HealingStrategy) -> None:
        """Register a healing strategy."""
        self._strategies[name] = strategy
        self.operation_stats["by_strategy"][name] = {"attempts": 0, "successes": 0}
        Logger.info(f"[Healing Orchestrator] Registered strategy: {name}")

    def _audit(self, strategy_name: str, violation_type: str, success: bool, latency_ms: float) -> None:
        """[PHASE 5] Record healing operation."""
        if not hasattr(self, "audit_log"):
            self.audit_log = []
        self.audit_log.append({
            "strategy": strategy_name,
            "violation_type": violation_type,
            "success": success,
            "latency_ms": latency_ms,
            "ts": time.time()
        })
        self.operation_stats["total_heals"] += 1
        if success:
            self.operation_stats["successful_heals"] += 1
        else:
            self.operation_stats["failed_heals"] += 1

        if strategy_name in self.operation_stats["by_strategy"]:
            self.operation_stats["by_strategy"][strategy_name]["attempts"] += 1
            if success:
                self.operation_stats["by_strategy"][strategy_name]["successes"] += 1

    async def heal(self, violation: dict, context: dict = None) -> dict:
        """
        Execute healing for a violation.

        [PHASE 5] Unified healing interface.
        """
        context = context or {}
        start = time.time()

        # Find applicable strategy
        for name, strategy in self._strategies.items():
            if strategy.can_heal(violation):
                try:
                    result = strategy.heal(violation, context)
                    latency = (time.time() - start) * 1000
                    self._audit(name, violation.get("type", "unknown"), True, latency)
                    return {"status": "healed", "strategy": name, "result": result}
                except Exception as e:
                    latency = (time.time() - start) * 1000
                    self._audit(name, violation.get("type", "unknown"), False, latency)
                    Logger.error(f"[Healing] Strategy {name} failed: {e}")
                    continue

        latency = (time.time() - start) * 1000
        self._audit("none", violation.get("type", "unknown"), False, latency)
        return {"status": "no_strategy", "violation": violation}


# Singleton accessor
_healing_orchestrator_instance = None

def get_healing_orchestrator() -> HealingSovereignOrchestrator:
    """Get or create the global healing orchestrator."""
    global _healing_orchestrator_instance
    if _healing_orchestrator_instance is None:
        _healing_orchestrator_instance = HealingSovereignOrchestrator()
    return _healing_orchestrator_instance
>>>>
```

---

### Test Cases for Phase 5 (Healing)

| Test Case | Procedure | Expected Result |
|-----------|-----------|-----------------|
| **TC-HEAL-001** | Instantiate `HealingSovereignOrchestrator`. | Singleton with operation_stats. |
| **TC-HEAL-002** | Register strategy and call `heal()`. | Strategy executed, audit logged. |
| **TC-HEAL-003** | Verify duplicate files removed. | Only orchestrator has healing classes. |
| **TC-HEAL-004** | Check `healing_healing_strategies.py` archived. | File in archived/. |

---

## Pattern 4: Validator Sprawl 🟡 MEDIUM PRIORITY

### Current State

**18 Validator Files Found** across multiple locations:
- `L5_safety/validators/` - 6 validators
- `L5_safety/unified/` - 4 validators (duplicates!)
- `L5_safety/gravity/` - 1 validator
- `runtime/shared_runtime/` - 1 validator
- Other locations - 6 validators

### Problem Analysis

- `CodeValidatorAgent.py` and `UnifiedCodeValidatorAgent.py` are duplicates
- `StructuralValidatorAgent.py` and `UnifiedStructureValidatorAgent.py` are duplicates
- No unified validator orchestrator
- Inconsistent validation interfaces

### Proposed Solution

Consolidate into `ValidatorOrchestrator` with registered validators, similar to healing pattern.

---

## Pattern 5: Config Duplication 🟡 MEDIUM PRIORITY

### Current State

**13 Config Files Found:**

```
agentic_core/config/
├── blueprint_sovereign/
│   ├── sovereign_config.py            # DUPLICATE NAME
│   └── config_impl.py
├── environments/
│   └── sovereign_config.py            # DUPLICATE NAME
└── rag_config.py

agentic_core/L1_cognition/thought_engine/
├── config.py
└── load_rag_config.py
```

### Problem Analysis

- **DUPLICATE**: `sovereign_config.py` exists in 2 locations
- RAG config split across multiple files
- No centralized config manager

---

## Pattern 6: Mixin Integration Gap 🟡 MEDIUM PRIORITY

### Current State

**102 Mixin Classes Found** but many not integrated into base agents:

**Core Mixins (Should be in InfrastructureMixin):**
- `RedisCacheMixin` ✅ (Phase 2)
- `PineconeVectorMixin` ✅ (Phase 1)
- `MCPHardenedMixin` ✅ (in SovereignBaseAgent)
- `SemanticCacheMixin` ✅ (Phase 3)
- `MCPOperationMixin` ✅ (Phase 3)

**Unintegrated Mixins (Need Review):**
- `SubatomicTestingMixin` - 5 classes, not universally applied
- `AuditTrailMixin` - 3 classes, should be in base
- `ResilienceMixin` - 2 classes, should be in base
- `TracingMixin` - 2 classes, should be in base
- `MetaLearningMixin` - 2 classes, should be in base
- `LifecycleMixin` - 2 classes, should be in base

---

## Consolidation Summary

### Phase 4 (Immediate - HIGH Priority)

| Target | Action | Files Affected |
|--------|--------|----------------|
| **LLM Gateway** | Create `SovereignLLMGateway.py` | 6+ files → 2 |
| **Embedding Gateway** | Create `EmbeddingSovereignAgent.py` | 5 files → 2 |

**Test Cases:** TC-LLM-001 to TC-LLM-005, TC-EMB-001 to TC-EMB-004

### Phase 5 (Next - HIGH Priority)

| Target | Action | Files Affected |
|--------|--------|----------------|
| **Healing Orchestrator** | Create `HealingSovereignOrchestrator.py` | 12 files → 2 |
| **Validator Orchestrator** | Create `ValidatorOrchestrator.py` | 18 files → 4 |

**Test Cases:** TC-HEAL-001 to TC-HEAL-004, TC-VAL-001 to TC-VAL-004

### Phase 6 (Future - MEDIUM Priority)

| Target | Action | Files Affected |
|--------|--------|----------------|
| **Config Manager** | Create `SovereignConfigManager.py` | 13 files → 3 |
| **Mixin Integration** | Audit and integrate into base agents | 102 mixins |

---

## Expected Benefits

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| LLM/Inference Files | 6+ | 2 | 67% reduction |
| Embedding Files | 5 | 2 | 60% reduction |
| Healing Files | 12 | 2 | 83% reduction |
| Validator Files | 18 | 4 | 78% reduction |
| Config Files | 13 | 3 | 77% reduction |
| **Total** | **54+** | **13** | **76% reduction** |

---

## Conclusion

This analysis identified **56+ files** across 6 architectural patterns requiring consolidation:

**Completed Phases:**
- ✅ Phase 1: Pinecone (6→3 files)
- ✅ Phase 2: Redis (1 gateway)
- ✅ Phase 3: MCP/SemanticCache (8→4 files)

**Pending Phases:**
- 🔴 Phase 4: LLM + Embedding (11→4 files)
- 🔴 Phase 5: Healing + Validator (30→6 files)
- 🟡 Phase 6: Config + Mixin Integration (13→3 files)

**Ready for Phase 4 implementation upon approval.**
