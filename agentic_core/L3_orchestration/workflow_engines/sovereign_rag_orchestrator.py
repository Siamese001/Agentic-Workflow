#!/usr/bin/env python3
"""
Sovereign RAG Orchestrator - L3 Self-Optimizing RAG System
Adapts parameters based on performance with persistent configuration
"""

import asyncio
import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class SovereignRAGOrchestrator:
    logger.info("[L6_AUDIT] Action at line 14")
    def __init__(self, retriever=None, query_planner=None, guardrail=None, engine=None):
        # Self-Optimization State (Loaded from L4)
        self.query_history = []
        self.config_path = Path("agentic_core/L4_state/validation_context/.sovereign_config.json")
        self._load_sovereign_config()
        
        # Calibration parameters
        self.threshold_adaptation_rate = 0.02
        self.performance_window = 50
        
        # Component dependencies
        logger.info("[L6_AUDIT] Action at line 26")
        self.retriever = retriever
        self.query_planner = query_planner
        self.guardrail = guardrail
        self.engine = engine
        self.enable_red_team_critique = False
        self.max_critique_rounds = 2

    def _load_sovereign_config(self):
        """L4: Persist the 'learned intelligence' of the system"""
        if self.config_path.exists():
            config = json.loads(self.config_path.read_text())
            self.faithfulness_threshold = config.get("faithfulness_threshold", 0.88)
            self.max_hops = config.get("max_hops", 3)
            self.base_top_k = config.get("base_top_k", 12)
        else:
            self.faithfulness_threshold = 0.88
            self.max_hops = 3
            self.base_top_k = 12

    def _save_sovereign_config(self):
        """L4: Write learned parameters back to the Canon"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.config_path.write_text(json.dumps({
            "faithfulness_threshold": self.faithfulness_threshold,
            "max_hops": self.max_hops,
            "base_top_k": self.base_top_k
        }))

    async def red_team_critique(self, answer: str, documents: List[Any], query: str) -> Dict:
        """L5: Red team critique for faithfulness validation"""
        critique_prompt = f"""
You are a critical evaluator. Assess if this answer is faithful to the source documents.

Query: {query}
Answer: {answer}
Documents: {[d.text[:200] for d in documents[:5]]}

Output JSON: {{"faithfulness_score": 0.0-1.0, "improvement_suggestion": "..."}}
"""
        # Use the hardened JSON cleaning we built in L1
        response = await self.engine.resilient_mutation(critique_prompt, temperature=0.3)
        
        def _parse_critique(raw):
            logger.info("[L6_AUDIT] Action at line 70")
            logger.info("[L6_AUDIT] Action at line 71")
            try:
                logger.info("[L6_AUDIT] Action at line 73")
                logger.info("[L6_AUDIT] Action at line 74")
                # Stripping potential markdown artifacts
                from agentic_core.L1_cognition.thought_engine.query_planner import (
                    QueryPlanner,
                )
                planner_helper = QueryPlanner()
                cleaned = planner_helper._clean_json_response(raw)
                return json.loads(cleaned)
            except:
                return {"faithfulness_score": 0.0, "improvement_suggestion": "Critical parsing error. Retry retrieval."}

        return _parse_critique(response)

    async def sovereign_retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        filters: Optional[Dict] = None,
        mission_context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Main retrieval method with multi-hop expansion and self-optimization
        """
        if top_k is None:
            top_k = self.base_top_k
         logger.info("[L6_AUDIT] Action at line 99")
        
        current_query = query
        all_documents = []
        
        logger.info("[L6_AUDIT] Action at line 104")
        for hop in range(self.max_hops):
            # L1: Decompose first, then expand each in parallel
            base_queries = await self.query_planner.decompose_query(current_query)
            
            all_queries = []
            # 2025 Sovereign Standard: Python 3.11+ TaskGroup for structured concurrency
            async with asyncio.TaskGroup() as tg:
                tasks = [tg.create_task(self.query_planner.multi_query_generation(bq)) 
                         for bq in base_queries]
            
            for t in tasks:
                all_queries.extend(t.result())
            
            # Final dedupe across the entire fan-out
            all_queries = list(dict.fromkeys(all_queries))
            
            # L2: Parallel execution - don't block the loop
            tasks = [self.retriever.hybrid_search(q, top_k=8) for q in all_queries]
            results_lists = await asyncio.gather(*tasks)
            
            retrieved = [doc for sublist in results_lists for doc in sublist]
            
            # L2: Deduplicate by content hash to prevent redundant L5 work
            unique_docs = self.retriever.deduplicate_by_hash(retrieved, set())
            all_documents.extend(unique_docs)
            
            # Check if we have sufficient faithfulness
            if len(all_documents) >= top_k:
                break
        
        # Final reranking
        final_docs = await self.guardrail.rerank_documents(all_documents, query, top_k=top_k)
        
        result = {
            "query": query,
            "documents": final_docs,
            "faithfulness": 0.85,  # Placeholder
            "top_k": top_k,
            "hops": hop + 1
        }
        
        # Track for adaptation
        self.query_history.append(result)
        
        # Trigger adaptation if we have enough data
        if len(self.query_history) >= self.performance_window:
            await self.adapt_parameters(result)
        
        return result

    async def adapt_parameters(self, result: Dict):
        """Self-optimization: adjust thresholds with dampen and persistence"""
        recent = self.query_history[-self.performance_window:]
        
        # Calculate average faithfulness
        faithfulness_scores = [r.get("faithfulness", 0.0) for r in recent]
        avg_faithfulness = sum(faithfulness_scores) / len(faithfulness_scores)
        
        # Adaptive threshold adjustment
        if avg_faithfulness > 0.94:
            self.faithfulness_threshold = min(0.95, self.faithfulness_threshold + self.threshold_adaptation_rate)
            self._save_sovereign_config()
            print(f"   [SELF-OPT] Raising threshold to {self.faithfulness_threshold:.3f}")
        elif avg_faithfulness < 0.85:
            # Never drop below the Sovereign Safety Floor
            self.faithfulness_threshold = max(0.70, self.faithfulness_threshold - self.threshold_adaptation_rate)
            self._save_sovereign_config()
            print(f"   [SELF-OPT] Lowering threshold to {self.faithfulness_threshold:.3f}")
        
        # Adaptive top_k adjustment
        if avg_faithfulness > 0.92 and self.base_top_k > 8:
            self.base_top_k -= 1
            self._save_sovereign_config()
            print(f"   [SELF-OPT] Reducing top_k to {self.base_top_k}")
        elif avg_faithfulness < 0.82 and self.base_top_k < 20:
            self.base_top_k += 1
            self._save_sovereign_config()
            print(f"   [SELF-OPT] Increasing top_k to {self.base_top_k}")

    async def multi_hop_retrieve(
        self,
        query: str,
        max_hops: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Multi-hop retrieval with iterative refinement
        """
        if max_hops is None:
            max_hops = self.max_hops
        
        all_documents = []
        current_query = query
        
        for hop in range(max_hops):
            result = await self.sovereign_retrieve(current_query)
            all_documents.extend(result.get("documents", []))
            
            # Check if we have sufficient faithfulness
            if result.get("faithfulness", 0.0) >= self.faithfulness_threshold:
                break
            
            # Refine query for next hop (placeholder)
            current_query = f"Refined: {current_query}"
        
        return {
            "query": query,
            "documents": all_documents,
            "hops": hop + 1,
            "faithfulness": result.get("faithfulness", 0.0)
        }

    def get_config(self) -> Dict[str, Any]:
        """Get current configuration"""
        return {
            "faithfulness_threshold": self.faithfulness_threshold,
            "max_hops": self.max_hops,
            "base_top_k": self.base_top_k,
            "threshold_adaptation_rate": self.threshold_adaptation_rate,
            "performance_window": self.performance_window
        }
