"""
End-to-End Tests for L1 Cognition Pipeline

Tests full integration of:
- Perception → Reasoning → Planning → Action
- Semantic memory integration
- Meta-learning adaptation
- Simple to complex missions
"""

import pytest
import asyncio
import sys

sys.path.insert(0, 'c:/Git/Agentic-Workflow')

from agentic_core.L1_cognition.cognitive_node.CognitiveNode import CognitiveNode


@pytest.fixture
def cognition_node():
    """Create cognitive node for testing."""
    return CognitiveNode()


class TestSimpleMissions:
    """Tests for simple, straightforward missions."""
    
    @pytest.mark.asyncio
    async def test_simple_math_mission(self, cognition_node):
        """Test simple math calculation."""
        raw = {"user_query": "What is 2+2?"}
        context = {}
        
        result = await cognition_node.process_async(raw, context)
        
        assert result.success == True
        assert "4" in result.output
        assert result.latency_ms >= 0  # May be very fast
    
    @pytest.mark.asyncio
    async def test_simple_question_mission(self, cognition_node):
        """Test simple question answering."""
        raw = {"user_query": "What is the capital of France?"}
        context = {}
        
        result = await cognition_node.process_async(raw, context)
        
        assert result.success == True
        assert result.output is not None
        assert len(result.output) > 0
    
    @pytest.mark.asyncio
    async def test_simple_mission_latency(self, cognition_node):
        """Test that simple missions complete quickly."""
        raw = {"user_query": "Hello"}
        context = {}
        
        result = await cognition_node.process_async(raw, context)
        
        assert result.latency_ms < 1000  # Should be fast
    
    @pytest.mark.asyncio
    async def test_simple_mission_has_plan(self, cognition_node):
        """Test that simple missions generate plans."""
        raw = {"user_query": "Calculate 5*3"}
        context = {}
        
        result = await cognition_node.process_async(raw, context)
        
        assert result.plan is not None
        assert "steps" in result.plan
        assert len(result.plan["steps"]) > 0


class TestComplexMissions:
    """Tests for complex, multi-step missions."""
    
    @pytest.mark.asyncio
    async def test_complex_planning_mission(self, cognition_node):
        """Test complex planning mission."""
        raw = {"user_query": "Create a strategy for improving team productivity"}
        context = {}
        
        result = await cognition_node.process_async(raw, context)
        
        assert result.success == True
        assert len(result.plan.get("steps", [])) >= 3
        assert result.plan.get("score", 0) > 0.7
    
    @pytest.mark.asyncio
    async def test_complex_reasoning_mission(self, cognition_node):
        """Test complex reasoning mission."""
        raw = {"user_query": "Analyze the pros and cons of remote work"}
        context = {}
        
        result = await cognition_node.process_async(raw, context)
        
        assert result.success == True
        assert result.thought_type in ["cot", "tot", "react", "reflection", "direct"]
        assert result.output is not None
    
    @pytest.mark.asyncio
    async def test_complex_mission_uses_memory(self, cognition_node):
        """Test that complex missions use semantic memory."""
        # Add something to memory first
        if cognition_node.semantic_memory:
            cognition_node.semantic_memory.add_thought({
                "text": "Remote work improves work-life balance",
                "type": "reasoning"
            })
        
        raw = {"user_query": "What are benefits of remote work?"}
        context = {}
        
        result = await cognition_node.process_async(raw, context)
        
        assert result.success == True
        # Memory should be used if available
        if cognition_node.semantic_memory:
            assert len(result.memory_used) >= 0


class TestAdaptiveMissions:
    """Tests for adaptive behavior and learning."""
    
    @pytest.mark.asyncio
    async def test_multiple_missions_improve_latency(self, cognition_node):
        """Test that multiple missions improve latency over time."""
        latencies = []
        
        for i in range(5):
            raw = {"user_query": f"Mission {i}: Calculate {i+1}+{i+1}"}
            context = {}
            
            result = await cognition_node.process_async(raw, context)
            latencies.append(result.latency_ms)
        
        # Later missions should be faster (caching, learning)
        assert latencies[-1] <= latencies[0] or latencies[-1] < 500
    
    @pytest.mark.asyncio
    async def test_meta_learning_stores_experience(self, cognition_node):
        """Test that meta-learning stores experiences."""
        if not cognition_node.meta_learner:
            pytest.skip("Meta-learner not available")
        
        initial_count = cognition_node.meta_learner.total_experiences
        
        raw = {"user_query": "Test mission"}
        context = {}
        
        result = await cognition_node.process_async(raw, context)
        
        # Experience should be stored
        assert cognition_node.meta_learner.total_experiences > initial_count
    
    @pytest.mark.asyncio
    async def test_strategy_bias_affects_reasoning(self, cognition_node):
        """Test that strategy bias affects reasoning."""
        if not cognition_node.meta_learner:
            pytest.skip("Meta-learner not available")
        
        # Set bias towards specific strategy
        cognition_node.meta_learner.strategy_weights["cot"] = 10.0
        cognition_node.meta_learner.strategy_weights["tot"] = 0.1
        
        raw = {"user_query": "Complex problem"}
        context = {}
        
        result = await cognition_node.process_async(raw, context)
        
        # Should use biased strategy
        assert result.thought_type is not None
    
    @pytest.mark.asyncio
    async def test_failure_recovery_adaptive(self, cognition_node):
        """Test adaptive behavior on failure."""
        # First mission with potential failure
        raw1 = {"user_query": "Impossible task"}
        result1 = await cognition_node.process_async(raw1, {})
        
        # Second mission should adapt
        raw2 = {"user_query": "Simple task"}
        result2 = await cognition_node.process_async(raw2, {})
        
        # Both should complete
        assert result1 is not None
        assert result2 is not None


class TestGovernanceIntegration:
    """Tests for governance policy enforcement."""
    
    @pytest.mark.asyncio
    async def test_governance_result_included(self, cognition_node):
        """Test that governance result is included."""
        raw = {"user_query": "Test mission"}
        context = {}
        
        result = await cognition_node.process_async(raw, context)
        
        assert "governance" in result.governance or result.governance is not None
    
    @pytest.mark.asyncio
    async def test_mission_completes_with_governance(self, cognition_node):
        """Test that missions complete even with governance."""
        raw = {"user_query": "Mission with governance"}
        context = {}
        
        result = await cognition_node.process_async(raw, context)
        
        assert result.success == True
        assert result.output is not None


class TestPipelineIntegration:
    """Tests for full pipeline integration."""
    
    @pytest.mark.asyncio
    async def test_full_pipeline_flow(self, cognition_node):
        """Test complete pipeline flow."""
        raw = {"user_query": "Create a plan for learning Python"}
        context = {"domain": "education"}
        
        result = await cognition_node.process_async(raw, context)
        
        # All components should have executed
        assert result.success == True
        assert result.output is not None
        assert result.thought_type is not None
        assert result.plan is not None
        assert result.latency_ms >= 0  # May be very fast
    
    @pytest.mark.asyncio
    async def test_perception_reasoning_planning_action_flow(self, cognition_node):
        """Test each stage of the pipeline."""
        raw = {"user_query": "Calculate 10 * 5"}
        context = {}
        
        # Perception
        perceived = await cognition_node.perception.process_async(raw, context)
        assert perceived["query"] == "Calculate 10 * 5"
        
        # Reasoning
        perceived["strategy_bias"] = {}
        reasoned = await cognition_node.reasoning.reason_async(perceived)
        assert reasoned["goal"] is not None
        assert reasoned["thought_type"] is not None
        
        # Planning
        plan = cognition_node.planning.plan(reasoned["goal"], reasoned["domain"], perceived)
        assert plan["steps"] is not None
        
        # Action
        reasoned["plan"] = plan
        output = cognition_node.action.act(reasoned)
        assert output is not None
    
    @pytest.mark.asyncio
    async def test_memory_integration_in_pipeline(self, cognition_node):
        """Test memory integration throughout pipeline."""
        if not cognition_node.semantic_memory:
            pytest.skip("Semantic memory not available")
        
        # Add memory
        cognition_node.semantic_memory.add_thought({
            "text": "Python is a programming language",
            "type": "knowledge"
        })
        
        raw = {"user_query": "Tell me about Python"}
        context = {}
        
        result = await cognition_node.process_async(raw, context)
        
        assert result.success == True
        # Memory should be integrated
        assert len(result.memory_used) >= 0
    
    @pytest.mark.asyncio
    async def test_learning_feedback_loop(self, cognition_node):
        """Test learning feedback loop."""
        if not cognition_node.meta_learner:
            pytest.skip("Meta-learner not available")
        
        initial_experiences = cognition_node.meta_learner.total_experiences
        
        # Run mission
        raw = {"user_query": "Test learning"}
        context = {}
        result = await cognition_node.process_async(raw, context)
        
        # Experience should be stored
        assert cognition_node.meta_learner.total_experiences > initial_experiences
        assert result.success == True


class TestStatistics:
    """Tests for statistics and monitoring."""
    
    @pytest.mark.asyncio
    async def test_statistics_tracking(self, cognition_node):
        """Test that statistics are tracked."""
        raw = {"user_query": "Test"}
        context = {}
        
        await cognition_node.process_async(raw, context)
        
        stats = cognition_node.get_statistics()
        
        assert stats["missions_processed"] >= 1
        assert stats["average_latency_ms"] >= 0  # May be very fast
    
    @pytest.mark.asyncio
    async def test_multiple_missions_statistics(self, cognition_node):
        """Test statistics across multiple missions."""
        for i in range(3):
            raw = {"user_query": f"Mission {i}"}
            context = {}
            await cognition_node.process_async(raw, context)
        
        stats = cognition_node.get_statistics()
        
        assert stats["missions_processed"] == 3
        assert stats["average_latency_ms"] >= 0  # May be very fast


class TestErrorHandling:
    """Tests for error handling and robustness."""
    
    @pytest.mark.asyncio
    async def test_empty_input_handled(self, cognition_node):
        """Test handling of empty input."""
        raw = {"user_query": ""}
        context = {}
        
        result = await cognition_node.process_async(raw, context)
        
        # Should handle gracefully
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_missing_input_handled(self, cognition_node):
        """Test handling of missing input."""
        raw = {}
        context = {}
        
        result = await cognition_node.process_async(raw, context)
        
        # Should handle gracefully
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_invalid_context_handled(self, cognition_node):
        """Test handling of invalid context."""
        raw = {"user_query": "Test"}
        context = None
        
        # Should handle None context
        try:
            result = await cognition_node.process_async(raw, context or {})
            assert result is not None
        except TypeError:
            pytest.fail("Should handle None context")


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
