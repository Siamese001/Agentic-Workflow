from __future__ import annotations

"""
query_planner - L1 Cognition Query Decomposition and Expansion
"""
import json
import logging
import re
from typing import Any

# [SSOT IMPORT] Structure blueprint is the single source of truth

Logger: Any = logging.getLogger(__name__)


class query_planner:
    """
    Sovereign L1 Query Planner – transforms queries for maximum recall/precision
    """

    def __init__(self, engine: SubAtomicEngine | None = None, cache: semantic_cache | None = None):
        self.engine = engine or SubAtomicEngine(gemini_client=None)
        self.cache = cache or semantic_cache()
        self.expansion_temperature = 0.7
        self.reflection_temperature = 0.3

    def _clean_json_response(self, raw_text: str) -> str:
        """
        Hardens the planner against LLMs that insist on markdown formatting.
        """
        cleaned = re.sub("```json|```", "", raw_text).strip()
        match = re.search("(\\[.*\\]|\\{.*\\})", cleaned, re.DOTALL)
        return match.group(1) if match else cleaned

    async def multi_query_generation(self, original_query: str) -> list[str]:
        """
        L1: Generate diverse query variants to maximize vector recall.
        """
        cache_key: Any = f"mq_expand:{hash(original_query)}"
        cached: Any = await self.cache.get(cache_key)
        if cached:
            return cached["queries"]
        prompt: Any = f'\nYou are the Sovereign Multi-Query Generator. \nGenerate 6-8 diverse versions of the query to capture different semantic facets.\n\nQuery: "{original_query}"\n\nVary the phrasing: use technical terms, lay terms, and sub-questions.\nOutput format: {{"queries": ["variant1", "variant2", ...]}}\n'
        response: Any = await self.engine.resilient_mutation(prompt=prompt, temperature=0.8)
        try:
            cleaned: Any = self._clean_json_response(response)
            result: Any = json.loads(cleaned)
            queries: Any = result.get("queries", [])[:8]
            if original_query not in queries:
                queries.insert(0, original_query)
        except Exception as e:
            print(f"   [!] Multi-query parse failure: {e}")
            queries: Any = [original_query]
        await self.cache.set(cache_key, {"queries": queries})
        return queries

    async def decompose_query(self, query: str) -> list[str]:
        """
        L1 Sovereign Query Decomposition - Thread-safe and JSON-hardened.
        """
        cache_key: Any = f"decompose:{hash(query)}"
        cached: Any = await self.cache.get(cache_key)
        if cached:
            return cached["sub_queries"]
        prompt: Any = f'\nYou are the Sovereign Query Decomposer. \nBreak this complex query into 3-5 atomic, independent sub-questions.\n\nQuery: "{query}"\n\nOutput ONLY a JSON object: {{"sub_queries": ["q1", "q2", ...]}}\n'
        response: Any = await self.engine.resilient_mutation(prompt=prompt, temperature=0.5)
        try:
            cleaned: Any = self._clean_json_response(response)
            result: Any = json.loads(cleaned)
            sub_queries: Any = result.get("sub_queries", [])
            sub_queries: Any = list(dict.fromkeys([q.strip() for q in sub_queries if q.strip()]))
            if not sub_queries:
                sub_queries: Any = [query]
        except Exception as e:
            print(f"   [!] Decomposition parse error: {e}")
            sub_queries: Any = [query]
        await self.cache.set(cache_key, {"sub_queries": sub_queries})
        return sub_queries

    async def decompose_and_expand(self, query: str) -> list[str]:
        """
        L1: Decompose query + generate expanded variants (legacy method)
        """
        prompt: Any = '\nYou are a semantic query expansion specialist. Given a user query, generate 5-8 expanded queries that capture:\n- Core intent\n- Specific technical terms\n- Broader context\n- Related concepts\n\nOutput format: {"queries": ["query1", "query2", ...]}\n'
        response: Any = await self.engine.resilient_mutation(
            prompt=prompt,
            temperature=self.expansion_temperature,
            response_format={"type": "json_object"},
        )
        try:
            result: Any = json.loads(self._clean_json_response(response))
            expanded: Any = result.get("queries", [])[:8]
        except Exception as e:
            Logger.error(f"L1 Decomposition failure: {e}")
            expanded: Any = [query]
        return expanded

    async def generate_synthetic_passages(self, query: str) -> list[str]:
        """
        Generate synthetic documentation passages for training
        """
        prompt: Any = f'\nGenerate 2-3 factual, technical passages about the following query topic.\n\nQuery: "{query}"\n\nMake them detailed, factual, and in the style of canon documentation.\nOutput format: {{"passages": ["passage1", "passage2", ...]}}\n'
        response: Any = await self.engine.resilient_mutation(
            prompt=prompt, temperature=0.5, response_format={"type": "json_object"}
        )
        try:
            result: Any = json.loads(self._clean_json_response(response))
            return result.get("passages", [])[:3]
        except Exception as e:
            Logger.error(f"L1 HyDE failure: {e}")
            return []
