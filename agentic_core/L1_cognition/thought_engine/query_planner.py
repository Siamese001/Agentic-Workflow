#!/usr/bin/env python3
"""
logger.info("[L6_AUDIT] Action at line 3")
QueryPlanner - L1 Cognition Query Decomposition and Expansion
"""

import asyncio
import json
import logging
import re
from typing import Dict, List, Optional

from agentic_core.L4_state.validation_context.semantic_cache_sovereign import (
    SemanticCache,
)
from agentic_core.L5_safety.guardrails.subatomic_engine import SubAtomicEngine

logger = logging.getLogger(__name__)
 logger.info("[L6_AUDIT] Action at line 19")

logger.info("[L6_AUDIT] Action at line 21")
class QueryPlanner:
    """
    Sovereign L1 Query Planner – transforms queries for maximum recall/precision
    """
    def __init__(self, engine: Optional[SubAtomicEngine] = None, cache: Optional[SemanticCache] = None):
        self.engine = engine or SubAtomicEngine(gemini_client=None)
        self.cache = cache or SemanticCache()
        self.expansion_temperature = 0.7
        self.reflection_temperature = 0.3
 logger.info("[L6_AUDIT] Action at line 31")

    def _clean_json_response(self, raw_text: str) -> str:
        """
        Hardens the planner against LLMs that insist on markdown formatting.
        """
        cleaned = re.sub(r"```json|```", "", raw_text).strip()
        match = re.search(r"(\[.*\]|\{.*\})", cleaned, re.DOTALL)
        return match.group(1) if match else cleaned

    async def multi_query_generation(self, original_query: str) -> List[str]:
        """
        L1: Generate diverse query variants to maximize vector recall.
        """
        cache_key = f"mq_expand:{hash(original_query)}"
        cached = await self.cache.get(cache_key)
        if cached:
            return cached["queries"]

        prompt = f"""
You are the Sovereign Multi-Query Generator. 
Generate 6-8 diverse versions of the query to capture different semantic facets.

Query: "{original_query}"

Vary the phrasing: use technical terms, lay terms, and sub-questions.
Output format: {{"queries": ["variant1", "variant2", ...]}}
"""
        response = await self.engine.resilient_mutation(prompt=prompt, temperature=0.8)
        
        try:
            # Using the hardened cleaner from our previous iteration
            cleaned = self._clean_json_response(response)
            result = json.loads(cleaned)
            queries = result.get("queries", [])[:8]
            
            # Ensure original is always at the pole position
            if original_query not in queries:
                queries.insert(0, original_query)
        except Exception as e:
            print(f"   [!] Multi-query parse failure: {e}")
            queries = [original_query]

        await self.cache.set(cache_key, {"queries": queries})
        return queries

    async def decompose_query(self, query: str) -> List[str]:
        """
        L1 Sovereign Query Decomposition - Thread-safe and JSON-hardened.
        """
        cache_key = f"decompose:{hash(query)}"
        cached = await self.cache.get(cache_key)
        if cached:
            return cached["sub_queries"]

        prompt = f"""
You are the Sovereign Query Decomposer. 
Break this complex query into 3-5 atomic, independent sub-questions.

Query: "{query}"

Output ONLY a JSON object: {{"sub_queries": ["q1", "q2", ...]}}
"""
        response = await self.engine.resilient_mutation(prompt=prompt, temperature=0.5)
        
        try:
            # Hardened cleaning (reusing our L1 sovereign helper)
            cleaned = self._clean_json_response(response)
            result = json.loads(cleaned)
            sub_queries = result.get("sub_queries", [])
            
            # Sanitize and dedupe
            sub_queries = list(dict.fromkeys([q.strip() for q in sub_queries if q.strip()]))
            if not sub_queries:
                sub_queries = [query]
        except Exception as e:
            print(f"   [!] Decomposition parse error: {e}")
            sub_queries = [query]

        await self.cache.set(cache_key, {"sub_queries": sub_queries})
        return sub_queries

    async def decompose_and_expand(self, query: str) -> List[str]:
        """
        L1: Decompose query + generate expanded variants (legacy method)
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
