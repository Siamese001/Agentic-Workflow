# FILE: runtime_utils.py
"""
Unified Runtime Infrastructure (v10_10) — HARDWARE LAYER

This module provides the raw mechanical capabilities required by the
Cognitive Layer. It contains NO business logic, NO policies, and NO prompts.

COMPONENTS:
    1. AsyncModelClient: Low-level HTTP stub for LLM providers.
    2. SandboxedExecution: Process isolation wrapper for tools (Pillar 14).
    3. RetrievalMath: BM25/Fusion algorithms (Pillar 7).
    4. Resilience: Standard Exception hierarchy (Pillar 8).
"""

from __future__ import annotations

import time
import json
import hashlib
import asyncio
from typing import Any, Dict, List, Optional, Union

# =============================================================================
# 1. EXCEPTION HIERARCHY (Pillar 8)
# =============================================================================

class AgenticError(Exception):
    """Root exception for the architecture."""

class ValidationError(AgenticError):
    """Contract violation (Pydantic/Schema mismatch)."""

class ModelClientError(AgenticError):
    """Network/Provider failure (500s, Rate Limits)."""

class ToolExecutionError(AgenticError):
    """Sandbox failure (Runtime error in tool)."""

class SandboxTimeoutError(AgenticError):
    """Execution exceeded time limit."""

class ContextLimitError(AgenticError):
    """Token budget exceeded."""

# =============================================================================
# 2. NETWORK CLIENT (The "Wire")
# =============================================================================

class AsyncModelClient:
    """
    Raw interface to LLM Providers (OpenAI, Anthropic).
    This layer handles retries, timeouts, and raw HTTP.
    It DOES NOT handle Prompt Rendering or Routing Policy.
    """

    async def invoke(
        self, 
        provider: str, 
        model_id: str, 
        prompt_text: str, 
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Simulates the network call.
        In prod, this wraps `openai.AsyncClient` or `anthropic.AsyncClient`.
        """
        # Simulate Network Latency
        await asyncio.sleep(0.1)

        # --- MOCK RESPONSES FOR SIMULATION ---
        # This ensures our "Golden State" tests pass without real API keys.
        
        # 1. Strategy JSON Mock
        if "Strategic Planning Agent" in prompt_text:
            return {
                "content": json.dumps({
                    "branches": [
                        {"branch_id": "b1", "name": "Cloud-First", "rationale": "Scalable", "steps": ["Audit", "Migrate"], "score": 0.9},
                        {"branch_id": "b2", "name": "Hybrid", "rationale": "Secure", "steps": ["VPN", "Sync"], "score": 0.8}
                    ],
                    "selected_branch_id": "b1",
                    "reasoning_trace": "Analyzed complexity vs cost..."
                }),
                "usage": {"input": 100, "output": 50},
                "latency_ms": 450
            }

        # 2. Drafting Mock
        if "Content Drafter" in prompt_text:
            return {
                "content": "This is a drafted section based on the provided evidence. It adheres to the professional tone requested.",
                "usage": {"input": 200, "output": 100},
                "latency_ms": 300
            }

        # 3. Safety Mock
        if "Constitutional Safety Judge" in prompt_text:
            # Trigger block if "Safety Intervention" scenario keywords appear
            if "Ignore rules" in prompt_text or "password" in prompt_text:
                 return {
                    "content": json.dumps({
                        "blocked": True,
                        "findings": [{"rule_id": "no_pii", "violated": True, "confidence": 0.99, "snippet": "password: 12345"}],
                        "policy_version": "v1.0"
                    }),
                    "usage": {"input": 100, "output": 20},
                    "latency_ms": 200
                }
            # Otherwise Pass
            return {
                "content": json.dumps({
                    "blocked": False,
                    "findings": [],
                    "policy_version": "v1.0"
                }),
                "usage": {"input": 100, "output": 20},
                    "latency_ms": 200
            }

        # Fallback
        return {
            "content": f"[Simulated Output from {model_id}]",
            "usage": {"input": 10, "output": 10},
            "latency_ms": 100
        }

# Global Client Singleton
NETWORK = AsyncModelClient()


# =============================================================================
# 3. TOOL SANDBOX (Pillar 14)
# =============================================================================

class SandboxedExecution:
    """
    Hardened execution environment.
    Enforces timeouts and isolation logic.
    """
    
    async def run(
        self, 
        function: callable, 
        args: Dict[str, Any], 
        timeout_sec: int = 30
    ) -> Any:
        """
        Run a function with strict timeout guardrails.
        """
        try:
            return await asyncio.wait_for(self._unsafe_execute(function, args), timeout=timeout_sec)
        except asyncio.TimeoutError:
            raise SandboxTimeoutError(f"Tool execution exceeded {timeout_sec}s limit.")
        except Exception as e:
            raise ToolExecutionError(f"Sandbox runtime error: {str(e)}")

    async def _unsafe_execute(self, function: callable, args: Dict[str, Any]) -> Any:
        """
        The actual execution logic.
        In a real system, this would spin up a Docker container or E2B sandbox.
        """
        # Simulate overhead
        await asyncio.sleep(0.05)
        
        # For simulation, we map "tool_id" strings to logic here
        # assuming 'function' is a placeholder string in this harness.
        
        tool_id = args.get("tool_id", "unknown")
        
        if tool_id == "web_search":
            return "Search Results: Found relevant leadership principles and cloud strategies."
            
        return f"Executed {tool_id} successfully."

# Global Sandbox Singleton
SANDBOX = SandboxedExecution()


# =============================================================================
# 4. RETRIEVAL MATH (Pillar 7)
# =============================================================================

class RetrievalMath:
    """
    Pure logic for ranking and fusion.
    No state, no network.
    """
    
    @staticmethod
    def bm25_score(query: str, doc: str) -> float:
        """Heuristic length/term match scorer."""
        q_terms = set(query.lower().split())
        d_terms = doc.lower().split()
        score = 0.0
        for t in q_terms:
            score += d_terms.count(t)
        return min(score, 10.0) # Cap

    @staticmethod
    def reciprocal_rank_fusion(lists: List[List[Dict[str, Any]]], k: int = 60) -> List[Dict[str, Any]]:
        """
        Fuses multiple ranked lists.
        """
        scores: Dict[str, float] = {}
        docs_map: Dict[str, Dict[str, Any]] = {}
        
        for ranked_list in lists:
            for rank, item in enumerate(ranked_list):
                content = item.get("content", "")
                # Dedupe key
                if content not in docs_map:
                    docs_map[content] = item
                
                # RRF Formula
                scores[content] = scores.get(content, 0.0) + (1.0 / (k + rank + 1))
        
        # Sort by score
        sorted_content = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
        
        # Reconstruct list
        return [docs_map[c] for c in sorted_content]
