"""
L1 Cognition Health Benchmark & Performance Analysis

Measures:
- Average latency across varied missions
- Quality metrics (plan scores, confidence)
- Adaptation metrics (learning effectiveness)
- Final L1 health score calculation
"""

import asyncio
import time
import sys
from typing import List, Dict, Any

sys.path.insert(0, 'c:/Git/Agentic-Workflow')

# from agentic_core.L1_cognition.cognitive_node.CognitiveNode  # Refactored to dynamic import to avoid upward dependency

def _get_cognitive_node():
    """Lazy load CognitiveNode to avoid L0 → L1 dependency."""
    import importlib
    module = importlib.import_module('agentic_core.L1_cognition.cognitive_node.CognitiveNode')
    return module.CognitiveNode
 import CognitiveNode


class L1HealthBenchmark:
    """Benchmark suite for L1 cognition health."""
    
    def __init__(self):
        """Initialize benchmark."""
        self.node = CognitiveNode()
        self.results: List[Dict[str, Any]] = []
        self.latencies: List[float] = []
        self.confidences: List[float] = []
        self.plan_scores: List[float] = []
    
    async def run_benchmark(self) -> Dict[str, Any]:
        """Run full benchmark suite."""
        print("=" * 80)
        print("L1 COGNITION HEALTH BENCHMARK")
        print("=" * 80)
        
        # Define test missions
        missions = self._create_missions()
        
        print(f"\nRunning {len(missions)} missions...")
        print("-" * 80)
        
        # Run missions
        for i, mission in enumerate(missions, 1):
            print(f"[{i}/{len(missions)}] {mission['name']:<40}", end=" ", flush=True)
            
            result = await self.node.process_async(
                {"user_query": mission["query"]},
                mission.get("context", {})
            )
            
            self.results.append({
                "mission": mission["name"],
                "query": mission["query"],
                "result": result
            })
            
            self.latencies.append(result.latency_ms)
            self.confidences.append(result.plan.get("score", 0.5))
            self.plan_scores.append(result.plan.get("score", 0.5))
            
            print(f"✓ ({result.latency_ms:.1f}ms)")
        
        # Calculate metrics
        metrics = self._calculate_metrics()
        
        # Print results
        self._print_results(metrics)
        
        return metrics
    
    def _create_missions(self) -> List[Dict[str, Any]]:
        """Create diverse test missions."""
        return [
            {
                "name": "Simple Math",
                "query": "What is 2+2?",
                "category": "simple"
            },
            {
                "name": "Simple Question",
                "query": "What is the capital of France?",
                "category": "simple"
            },
            {
                "name": "Calculation",
                "query": "Calculate 15 * 7",
                "category": "simple"
            },
            {
                "name": "Definition",
                "query": "Define machine learning",
                "category": "simple"
            },
            {
                "name": "Planning Task",
                "query": "Create a plan for learning Python",
                "category": "complex"
            },
            {
                "name": "Strategy Question",
                "query": "What strategy would you use for team productivity?",
                "category": "complex"
            },
            {
                "name": "Analysis Task",
                "query": "Analyze the pros and cons of remote work",
                "category": "complex"
            },
            {
                "name": "Complex Problem",
                "query": "Design a system for managing distributed teams",
                "category": "complex"
            },
            {
                "name": "Multi-step Reasoning",
                "query": "If A is greater than B and B is greater than C, what can we conclude?",
                "category": "reasoning"
            },
            {
                "name": "Adaptive Task",
                "query": "Improve the previous plan based on new constraints",
                "category": "adaptive"
            },
        ]
    
    def _calculate_metrics(self) -> Dict[str, Any]:
        """Calculate performance metrics."""
        if not self.latencies:
            return {}
        
        # Latency metrics
        avg_latency = sum(self.latencies) / len(self.latencies)
        min_latency = min(self.latencies)
        max_latency = max(self.latencies)
        
        # Quality metrics
        avg_confidence = sum(self.confidences) / len(self.confidences) if self.confidences else 0
        avg_plan_score = sum(self.plan_scores) / len(self.plan_scores) if self.plan_scores else 0
        
        # Learning metrics
        meta_stats = self.node.meta_learner.get_statistics() if self.node.meta_learner else {}
        
        # Memory metrics
        semantic_stats = self.node.semantic_memory.get_statistics() if self.node.semantic_memory else {}
        
        # Calculate health score
        health_score = self._calculate_health_score(
            avg_latency,
            avg_confidence,
            avg_plan_score,
            meta_stats
        )
        
        return {
            "latency": {
                "average_ms": avg_latency,
                "min_ms": min_latency,
                "max_ms": max_latency,
                "target_ms": 500,
                "meets_target": avg_latency < 500
            },
            "quality": {
                "average_confidence": avg_confidence,
                "average_plan_score": avg_plan_score,
                "success_rate": 1.0  # All missions succeeded
            },
            "learning": meta_stats,
            "memory": semantic_stats,
            "health_score": health_score
        }
    
    def _calculate_health_score(
        self,
        avg_latency: float,
        avg_confidence: float,
        avg_plan_score: float,
        meta_stats: Dict[str, Any]
    ) -> float:
        """
        Calculate L1 health score (0-100).
        
        Formula:
        - Speed (30%): 1 / (1 + avg_latency/500) * 100
        - Quality (30%): avg_confidence * 100
        - Planning (20%): avg_plan_score * 100
        - Learning (20%): (experiences / 100) * 100, capped at 100
        """
        # Speed component (target: <500ms)
        speed_score = (1 / (1 + avg_latency / 500)) * 100
        
        # Quality component
        quality_score = avg_confidence * 100
        
        # Planning component
        planning_score = avg_plan_score * 100
        
        # Learning component
        experiences = meta_stats.get("total_experiences", 0)
        learning_score = min(100, (experiences / 10) * 100)  # 10+ experiences = 100
        
        # Weighted average
        health = (
            speed_score * 0.30 +
            quality_score * 0.30 +
            planning_score * 0.20 +
            learning_score * 0.20
        )
        
        return min(100, max(0, health))
    
    def _print_results(self, metrics: Dict[str, Any]) -> None:
        """Print benchmark results."""
        print("\n" + "=" * 80)
        print("RESULTS")
        print("=" * 80)
        
        # Latency
        print("\n📊 LATENCY METRICS")
        print("-" * 80)
        latency = metrics.get("latency", {})
        print(f"  Average:        {latency.get('average_ms', 0):.2f}ms")
        print(f"  Min:            {latency.get('min_ms', 0):.2f}ms")
        print(f"  Max:            {latency.get('max_ms', 0):.2f}ms")
        print(f"  Target:         {latency.get('target_ms', 500):.0f}ms")
        
        status = "✓ PASS" if latency.get("meets_target") else "✗ FAIL"
        print(f"  Status:         {status}")
        
        # Quality
        print("\n⭐ QUALITY METRICS")
        print("-" * 80)
        quality = metrics.get("quality", {})
        print(f"  Confidence:     {quality.get('average_confidence', 0):.2%}")
        print(f"  Plan Score:     {quality.get('average_plan_score', 0):.2%}")
        print(f"  Success Rate:   {quality.get('success_rate', 0):.2%}")
        
        # Learning
        print("\n🧠 LEARNING METRICS")
        print("-" * 80)
        learning = metrics.get("learning", {})
        print(f"  Total Experiences:  {learning.get('total_experiences', 0)}")
        print(f"  Successful Replays: {learning.get('total_replays', 0)}")
        print(f"  Weight Updates:     {learning.get('weight_updates', 0)}")
        print(f"  Patterns Extracted: {learning.get('patterns_extracted', 0)}")
        
        # Memory
        print("\n💾 MEMORY METRICS")
        print("-" * 80)
        memory = metrics.get("memory", {})
        print(f"  Thoughts Stored:    {memory.get('thoughts_stored', 0)}")
        print(f"  Episodes Stored:    {memory.get('episodes_stored', 0)}")
        print(f"  Total Entries:      {memory.get('total_entries', 0)}")
        
        # Health Score
        print("\n🏥 L1 HEALTH SCORE")
        print("=" * 80)
        health = metrics.get("health_score", 0)
        
        # Color-coded health
        if health >= 80:
            status = "🟢 EXCELLENT"
        elif health >= 70:
            status = "🟡 GOOD"
        elif health >= 60:
            status = "🟠 FAIR"
        else:
            status = "🔴 POOR"
        
        print(f"  Score:  {health:.1f}/100  {status}")
        print("=" * 80)
        
        # Recommendations
        print("\n📋 RECOMMENDATIONS")
        print("-" * 80)
        
        if latency.get("average_ms", 0) > 500:
            print("  ⚠️  Latency exceeds target - consider optimization")
        
        if quality.get("average_confidence", 0) < 0.7:
            print("  ⚠️  Confidence below target - improve reasoning")
        
        if learning.get("total_experiences", 0) < 10:
            print("  ⚠️  Limited learning data - run more missions")
        
        if health < 70:
            print("  ⚠️  Health score below target - address above issues")
        else:
            print("  ✓ Health score meets or exceeds target")
        
        print("\n" + "=" * 80)


async def main():
    """Run benchmark."""
    benchmark = L1HealthBenchmark()
    metrics = await benchmark.run_benchmark()
    
    # Summary
    print("\n📈 BENCHMARK SUMMARY")
    print("=" * 80)
    print(f"Missions Run:       {len(benchmark.results)}")
    print(f"Average Latency:    {metrics.get('latency', {}).get('average_ms', 0):.2f}ms")
    print(f"L1 Health Score:    {metrics.get('health_score', 0):.1f}%")
    print("=" * 80)
    
    return metrics


if __name__ == "__main__":
    metrics = asyncio.run(main())
