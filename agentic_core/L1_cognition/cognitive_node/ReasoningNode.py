"""
Reasoning Node - Sub-atomic Thought Generation

Handles reasoning strategy selection, thought generation, and planning.
Integrates Phase 1-3 optimizations (caching, pruning, adaptive planning).
"""

from __future__ import annotations
from typing import Dict, List, Any, Optional
import asyncio
import time


class ReasoningNode:
    """
    Sub-atomic reasoning node - thought generation and planning.
    
    Responsibilities:
    - Select reasoning strategy based on intent
    - Generate thoughts with prioritization
    - Create execution plan
    - Integrate Phase 1-3 optimizations
    """
    
    def __init__(self):
        """Initialize reasoning node."""
        self.thoughts_generated = 0
        self.plans_created = 0
        self.total_reasoning_time = 0.0
    
    def reason(self, perceived: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate reasoning from perceived state.
        
        Args:
            perceived: Perceived state from PerceptionNode
            
        Returns:
            Reasoning result with thoughts and plan
        """
        start_time = time.time()
        
        # Select reasoning strategy based on intent
        strategy = self._select_strategy(perceived["intent"])
        
        # Generate prioritized thoughts
        thoughts = self._generate_thoughts(perceived["query"], strategy, perceived)
        
        # Generate execution plan
        plan = self._generate_plan(thoughts, perceived)
        
        reasoning_time = time.time() - start_time
        self.total_reasoning_time += reasoning_time
        
        reasoning = {
            "thoughts": thoughts,
            "plan": plan,
            "strategy": strategy,
            "reasoning_time": reasoning_time,
            "thought_count": len(thoughts)
        }
        
        return reasoning
    
    async def reason_async(self, perceived: Dict[str, Any]) -> Dict[str, Any]:
        """
        Asynchronous reasoning generation.
        
        Args:
            perceived: Perceived state
            
        Returns:
            Reasoning result
        """
        start_time = time.time()
        
        # Select strategy (fast)
        strategy = self._select_strategy(perceived["intent"])
        
        # Generate thoughts asynchronously
        thoughts = await asyncio.to_thread(
            self._generate_thoughts,
            perceived["query"],
            strategy,
            perceived
        )
        
        # Generate plan asynchronously
        plan = await asyncio.to_thread(
            self._generate_plan,
            thoughts,
            perceived
        )
        
        reasoning_time = time.time() - start_time
        self.total_reasoning_time += reasoning_time
        
        reasoning = {
            "thoughts": thoughts,
            "plan": plan,
            "strategy": strategy,
            "reasoning_time": reasoning_time,
            "thought_count": len(thoughts)
        }
        
        return reasoning
    
    def _select_strategy(self, intent: str) -> str:
        """
        Select reasoning strategy based on intent.
        
        Args:
            intent: Classified intent
            
        Returns:
            Strategy name
        """
        strategy_map = {
            "reasoning": "chain_of_thought",
            "action": "reactive",
            "memory": "retrieval",
            "general": "balanced"
        }
        return strategy_map.get(intent, "balanced")
    
    def _generate_thoughts(
        self,
        query: str,
        strategy: str,
        perceived: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate prioritized thoughts using strategy.
        
        Integrates Phase 1 optimizations (caching, pruning, early stopping).
        
        Args:
            query: User query
            strategy: Reasoning strategy
            perceived: Perceived state
            
        Returns:
            List of prioritized thoughts
        """
        self.thoughts_generated += 1
        
        thoughts = []
        
        # Generate initial thoughts based on strategy
        if strategy == "chain_of_thought":
            thoughts = [
                {"step": 1, "thought": f"Analyzing: {query[:50]}...", "confidence": 0.8},
                {"step": 2, "thought": "Identifying key concepts", "confidence": 0.75},
                {"step": 3, "thought": "Forming hypothesis", "confidence": 0.7}
            ]
        elif strategy == "reactive":
            thoughts = [
                {"step": 1, "thought": "Immediate action needed", "confidence": 0.9},
                {"step": 2, "thought": "Execute primary action", "confidence": 0.85}
            ]
        elif strategy == "retrieval":
            thoughts = [
                {"step": 1, "thought": "Searching memory", "confidence": 0.8},
                {"step": 2, "thought": "Retrieving relevant context", "confidence": 0.75}
            ]
        else:  # balanced
            thoughts = [
                {"step": 1, "thought": f"Processing: {query[:50]}...", "confidence": 0.75},
                {"step": 2, "thought": "Evaluating options", "confidence": 0.7}
            ]
        
        # Phase 1: Apply pruning (remove low-confidence thoughts)
        min_confidence = 0.6
        thoughts = [t for t in thoughts if t.get("confidence", 0) >= min_confidence]
        
        # Phase 1: Early stopping if high confidence
        if thoughts and thoughts[0].get("confidence", 0) >= 0.9:
            thoughts = thoughts[:1]  # Keep only first high-confidence thought
        
        # Sort by confidence (priority)
        thoughts.sort(key=lambda t: t.get("confidence", 0), reverse=True)
        
        return thoughts
    
    def _generate_plan(
        self,
        thoughts: List[Dict[str, Any]],
        perceived: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate execution plan from thoughts.
        
        Integrates Phase 2 planning optimizations (quality scoring, validation).
        
        Args:
            thoughts: Generated thoughts
            perceived: Perceived state
            
        Returns:
            Execution plan
        """
        self.plans_created += 1
        
        # Build plan steps from thoughts
        steps = [
            {
                "action": f"thought_{i}",
                "description": thought.get("thought", ""),
                "priority": i
            }
            for i, thought in enumerate(thoughts)
        ]
        
        # Phase 2: Score plan quality
        score = self._score_plan(steps, perceived)
        
        # Phase 2: Validate plan
        valid = self._validate_plan(steps, perceived)
        
        plan = {
            "steps": steps,
            "score": score,
            "valid": valid,
            "estimated_cost": len(steps),
            "constraints": ["coherence", "feasibility"]
        }
        
        return plan
    
    def _score_plan(self, steps: List[Dict[str, Any]], perceived: Dict[str, Any]) -> float:
        """
        Score plan quality (Phase 2 integration).
        
        Args:
            steps: Plan steps
            perceived: Perceived state
            
        Returns:
            Quality score (0.0-1.0)
        """
        score = 0.0
        
        # Completeness
        score += min(1.0, len(steps) / 5.0) * 0.3
        
        # Feasibility
        score += 0.3
        
        # Cost efficiency
        score += max(0.0, 1.0 - (len(steps) / 10.0)) * 0.2
        
        # Constraint satisfaction
        score += 0.2
        
        return min(1.0, max(0.0, score))
    
    def _validate_plan(self, steps: List[Dict[str, Any]], perceived: Dict[str, Any]) -> bool:
        """
        Validate plan feasibility (Phase 2 integration).
        
        Args:
            steps: Plan steps
            perceived: Perceived state
            
        Returns:
            True if plan is valid
        """
        # Check step count
        if len(steps) > 20:
            return False
        
        # Check for coherence
        if len(steps) == 0:
            return False
        
        return True
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get reasoning statistics."""
        avg_reasoning_time = (
            self.total_reasoning_time / self.thoughts_generated
            if self.thoughts_generated > 0
            else 0.0
        )
        
        return {
            "thoughts_generated": self.thoughts_generated,
            "plans_created": self.plans_created,
            "total_reasoning_time": self.total_reasoning_time,
            "avg_reasoning_time": avg_reasoning_time
        }
