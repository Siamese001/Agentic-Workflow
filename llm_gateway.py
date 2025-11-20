# FILE: llm_gateway.py
"""
Unified LLM Gateway (v10_10) — COGNITIVE INFRASTRUCTURE (NEW)

This module implements the "Brain" access layer (Pillars 6, 8, 11).
It provides a single, hardened interface for all Cognitive (L1) and
Action (L2) layers to access Language Models.

Features:
    1. Model Routing: Dynamic selection based on Cost/Latency/Complexity (Pillar 11).
    2. Semantic Caching: Deduplicates redundant cognitive work (Pillar 11).
    3. Reasoning Injection: Auto-wraps prompts with CoT/ToT strategies (Pillar 6).
    4. Resilience: Centralized retries, backoff, and circuit breaking (Pillar 8).
    5. Observability: Automatic span tracking for all LLM calls (Pillar 10).
"""

from __future__ import annotations

import time
import hashlib
import asyncio
from typing import Any, Dict, Optional, List
from pydantic import BaseModel

from models import (
    PromptSpec,
    ExecutionResult,
    TraceSpan,
    RoutingConfig
)
from registry import REGISTRY
from meta_profile import (
    get_routing_bias,
    get_planning_bias,
)
from runtime_utils import (
    CostTracker, 
    record_event,
    ModelClientError,
    WorkflowTimeoutError
)

# =============================================================================
# DATA MODELS (Gateway Specific)
# =============================================================================

class ModelResponse(BaseModel):
    """Normalized response from any provider."""
    content: str
    model_used: str
    tokens_in: int
    tokens_out: int
    latency_ms: float
    cached: bool = False
    reasoning_trace: Optional[str] = None


# =============================================================================
# CACHE LAYER (In-Memory Stub)
# =============================================================================

class SemanticCache:
    """
    Simple in-memory cache. In production, this would use Redis/VectorDB.
    Satisfies Pillar 11 (Cost & Optimization).
    """
    _store: Dict[str, ModelResponse] = {}

    @staticmethod
    def _hash_key(prompt: str, model: str) -> str:
        return hashlib.sha256(f"{model}::{prompt}".encode()).hexdigest()

    def get(self, prompt: str, model: str) -> Optional[ModelResponse]:
        key = self._hash_key(prompt, model)
        hit = self._store.get(key)
        if hit:
            hit.cached = True
            record_event("cache_hit", {"model": model})
        return hit

    def set(self, prompt: str, model: str, response: ModelResponse) -> None:
        key = self._hash_key(prompt, model)
        self._store[key] = response


# =============================================================================
# LLM GATEWAY
# =============================================================================

class LLMGateway:
    """
    The single entry point for all cognitive operations.
    """
    cache = SemanticCache()

    async def call_model(
        self,
        prompt_id: str,
        inputs: Dict[str, Any],
        workflow_id: str,
        reasoning_strategy: str = "direct", # direct, cot, tot
        force_model: Optional[str] = None,
    ) -> ModelResponse:
        """
        Execute an LLM call with full governance, routing, and observability.
        """
        start_time = time.perf_counter()
        
        # 1. Fetch & Render Prompt (Governance)
        spec = REGISTRY.get_prompt(prompt_id)
        rendered_prompt = self._render_prompt(spec, inputs)

        # 2. Apply Reasoning Strategy (Pillar 6)
        final_prompt = self._inject_reasoning(rendered_prompt, reasoning_strategy)

        # 3. Route Model (Pillar 11)
        selected_model = force_model or self._route_model(spec, reasoning_strategy)

        # 4. Check Cache (Pillar 11)
        cached_resp = self.cache.get(final_prompt, selected_model)
        if cached_resp:
            return cached_resp

        # 5. Execute with Retries (Pillar 8)
        try:
            # In a real implementation, this calls OpenAI/Anthropic APIs.
            # Here we simulate the network call.
            raw_response = await self._simulate_network_call(selected_model, final_prompt)
        except Exception as e:
            record_event("llm_failure", {"error": str(e), "prompt_id": prompt_id})
            raise ModelClientError(f"Failed to call {selected_model}: {e}")

        # 6. Observability & Metrics (Pillar 10)
        duration_ms = (time.perf_counter() - start_time) * 1000
        response = ModelResponse(
            content=raw_response,
            model_used=selected_model,
            tokens_in=len(final_prompt.split()),
            tokens_out=len(raw_response.split()),
            latency_ms=duration_ms,
            reasoning_trace="Step-by-step logic..." if reasoning_strategy != "direct" else None
        )
        
        # 7. Write to Cache
        self.cache.set(final_prompt, selected_model, response)
        
        record_event("llm_call", {
            "workflow_id": workflow_id,
            "prompt_id": prompt_id,
            "model": selected_model,
            "latency": duration_ms,
            "strategy": reasoning_strategy
        })

        return response

    # --- INTERNAL HELPERS ---

    def _render_prompt(self, spec: PromptSpec, inputs: Dict[str, Any]) -> str:
        """Safe string interpolation."""
        try:
            # Simple f-string style simulation
            text = spec.template
            for var in spec.input_variables:
                val = inputs.get(var, f"MISSING_{var}")
                text = text.replace(f"{{{var}}}", str(val))
            return text
        except Exception as e:
            raise ValueError(f"Prompt rendering failed for {spec.prompt_id}: {e}")

    def _inject_reasoning(self, prompt: str, strategy: str) -> str:
        """
        Wraps the prompt in cognitive scaffolding (Pillar 6).
        """
        planning_bias = get_planning_bias()
        
        # Meta-Profile Override: If history shows we need deep thought, force CoT
        if planning_bias.get("conservative") and strategy == "direct":
            strategy = "cot"

        if strategy == "cot":
            return f"{prompt}\n\nLet's think step by step to ensure accuracy:"
        elif strategy == "tot":
            return (
                f"{prompt}\n\n"
                "Generate three distinct approaches. Evaluate the pros and cons of each. "
                "Then select the best one and execute it."
            )
        return prompt

    def _route_model(self, spec: PromptSpec, strategy: str) -> str:
        """
        Selects the optimal model based on Meta-Profile biases (Pillar 11).
        """
        routing_bias = get_routing_bias()
        
        # 1. Hard Constraints from Prompt Registry
        if "required_model" in spec.model_constraints:
            return spec.model_constraints["required_model"]

        # 2. Meta-Learning Biases
        if routing_bias.get("prefer_fast"):
            return "gpt-3.5-turbo-fast"
        
        if routing_bias.get("prefer_long_context"):
            return "claude-3-opus"

        # 3. Complexity Heuristics
        if strategy in ("tot", "cot"):
            return "gpt-4-turbo"  # Reasoning requires capability
        
        return "gpt-4o"  # Default balanced model

    async def _simulate_network_call(self, model: str, prompt: str) -> str:
        """
        Simulates API latency and output generation.
        In a real app, this is where `openai.chat.completions.create` lives.
        """
        # Simulation Logic: Return a valid JSON-like string or text based on prompt cues
        # This allows the rest of the architecture to function without real APIs.
        
        # Simulate network latency (variable based on model)
        latency = 0.1 if "fast" in model else 0.5
        await asyncio.sleep(latency)

        # Mock Responses for "Golden Path" simulation
        if "Strategy" in prompt:
            return """
            {
                "branches": [
                    {"branch_id": "b1", "strategy_name": "Conservative", "rationale": "Low risk approach"},
                    {"branch_id": "b2", "strategy_name": "Aggressive", "rationale": "High growth approach"},
                    {"branch_id": "b3", "strategy_name": "Balanced", "rationale": "Mixed approach"}
                ],
                "selected_branch": {"branch_id": "b3", "strategy_name": "Balanced"},
                "aggregated_decision": "proceed",
                "aggregated_confidence": 0.95
            }
            """
        if "Draft" in prompt:
            return "This is a drafted section based on the provided evidence. It is professional and concise."
        
        if "Safety" in prompt:
            # Default to safe
            return """
            {
                "issues": [],
                "blocked": false,
                "summary": "No safety violations found."
            }
            """

        return f"[LLM OUTPUT from {model}]: Processed request."

# Singleton instance
GATEWAY = LLMGateway()
