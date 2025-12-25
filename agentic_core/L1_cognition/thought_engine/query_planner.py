#!/usr/bin/env python3
"""
QueryPlanner - L1 Cognition Query Decomposition and Expansion
"""

import asyncio
import json
import re
import logging
from typing import List, Dict, Optional

from agentic_core.L5_safety.guardrails.subatomic_engine import SubAtomicEngine
from agentic_core.L4_state.validation_context.semantic_cache_sovereign import SemanticCache

logger = logging.getLogger(__name__)

class QueryPlanner:
    """
    Sovereign L1 Query Planner – transforms queries for maximum recall/precision
    """
    def __init__(self, engine: Optional[SubAtomicEngine] = None, cache: Optional[SemanticCache] = None):
        self.engine = engine or SubAtomicEngine(gemini_client=None)
        self.cache = cache or SemanticCache()
        self.expansion_temperature = 0.7
        self.reflection_temperature = 0.3

    def _clean_json_response(self, raw_text: str) -> str:
        """
        Hardens the planner against LLMs that insist on markdown formatting.
        """
        cleaned = re.sub(r"```json|```", "", raw_text).strip()
        match = re.search(r"(\[.*\]|\{.*\})", cleaned, re.DOTALL)
        return match.group(1) if match else cleaned

    async def decompose_and_expand(self, query: str) -> List[str]:
        """
        L1: Decompose query + generate expanded variants
        """
        prompt = f"""
You are a semantic query expansion specialist. Given a user query, generate 5-8 expanded queries that capture:
- Core intent
- Specific technical terms
- Broader context
- Related concepts

Output format: {{"queries": ["query1", "query2", ...]}}
"""

        response = await self.engine.resilient_mutation(
            prompt=prompt,
            temperature=self.expansion_temperature,
            response_format={"type": "json_object"}
        )

        try:
            result = json.loads(self._clean_json_response(response))
            expanded = result.get("queries", [])[:8]
        except Exception as e:
            logger.error(f"L1 Decomposition failure: {e}")
            expanded = [query]  # Fallback
        
        return expanded

    async def generate_synthetic_passages(self, query: str) -> List[str]:
        """
        Generate synthetic documentation passages for training
        """
        prompt = f"""
Generate 2-3 factual, technical passages about the following query topic.

Query: "{query}"

Make them detailed, factual, and in the style of canon documentation.
Output format: {{"passages": ["passage1", "passage2", ...]}}
"""

        response = await self.engine.resilient_mutation(
            prompt=prompt,
            temperature=0.5,
            response_format={"type": "json_object"}
        )

        try:
            result = json.loads(self._clean_json_response(response))
            return result.get("passages", [])[:3]
        except Exception as e:
            logger.error(f"L1 HyDE failure: {e}")
            return []
