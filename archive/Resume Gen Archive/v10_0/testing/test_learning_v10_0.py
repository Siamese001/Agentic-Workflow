# File: test_learning_v10_0.py
# Comprehensive tests for run_learning_v10_0.py
# Tests: Async meta-learning, pattern finding, hypothesis generation

import pytest
import asyncio
import json
import os
from unittest.mock import Mock, MagicMock, patch, AsyncMock, mock_open
from datetime import datetime

pytest_plugins = ('pytest_asyncio',)

try:
    from run_learning_v10_0 import (
        LogReaderAgent, AsyncPatternFinderAgent, AsyncHypothesisGeneratorAgent,
        AsyncProposalDrafterAgent, MetaPlannerAgent, AsyncProposalCritiqueAgent,
        run_read_logs, run_find_patterns, run_generate_hypothesis,
        run_draft_proposal, run_critique_proposal, run_write_proposal,
        get_meta_learning_graph_app, run_meta_learning
    )
    from core_v10_0 import WorkflowContext, MetaGraphState
except ImportError:
    pytest.skip("run_learning_v10_0 module not available", allow_module_level=True)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_workflow_context():
    """Mock WorkflowContext for meta-learning"""
    context = MagicMock(spec=WorkflowContext)
    
    # Mock model client
    mock_client = AsyncMock()
    mock_client.chat_completion_async.return_value = {
        "content": {"patterns": [], "hypotheses": [], "proposal": {}}
    }
    context.get_model_client.return_value = mock_client
    
    # Mock cache manager
    context.cache_manager.get_stats.return_value = {
        'hits': 5,
        'misses': 3,
        'hit_rate_pct': 62.5
    }
    
    return context


@pytest.fixture
def sample_feedback_log():
    """Sample feedback log content"""
    return """
{"timestamp": "2025-01-01T10:00:00", "type": "qa_failure", "message": "Bullet count too low"}
{"timestamp": "2025-01-01T10:05:00", "type": "qa_failure", "message": "Bullet count too low"}
{"timestamp": "2025-01-01T10:10:00", "type": "qa_failure", "message": "Missing quantification"}
"""


@pytest.fixture
def sample_preference_log():
    """Sample preference log content"""
    return """
{"timestamp": "2025-01-01T09:00:00", "preference": "action_verbs", "value": "prefer strong action verbs"}
{"timestamp": "2025-01-01T09:30:00", "preference": "quantification", "value": "always quantify achievements"}
"""


@pytest.fixture
def sample_patterns():
    """Sample patterns found in logs"""
    return [
        {
            "id": "pattern_1",
            "description": "Repeated QA failures for bullet count",
            "frequency": 5,
            "severity": "HIGH"
        },
        {
            "id": "pattern_2",
            "description": "Missing quantification in bullets",
            "frequency": 3,
            "severity": "MEDIUM"
        }
    ]


@pytest.fixture
def sample_hypotheses():
    """Sample hypotheses"""
    return [
        {
            "id": "hyp_1",
            "pattern_id": "pattern_1",
            "root_cause": "BulletGeneratorAgent not checking count constraint",
            "confidence": 0.85
        }
    ]


@pytest.fixture
def sample_proposal():
    """Sample change proposal"""
    return {
        "type": "constraint_addition",
        "target": "BulletGeneratorAgent",
        "change": "Add validation for bullet count before returning",
        "expected_impact": "Reduce bullet count failures by 80%"
    }


# ============================================================================
# AGENT TESTS
# ============================================================================

class TestLogReaderAgent:
    """Test LogReaderAgent"""
    
    def test_read_logs_success(
        self, mock_workflow_context, tmp_path, sample_feedback_log, sample_preference_log
    ):
        """Test successful log reading"""
        feedback_file = tmp_path / "feedback.jsonl"
        preference_file = tmp_path / "preference.jsonl"
        
        feedback_file.write_text(sample_feedback_log)
        preference_file.write_text(sample_preference_log)
        
        with patch('run_learning_v10_0.CONFIG') as mock_config:
            mock_config.meta_loop_config.feedback_log_path = str(feedback_file)
            mock_config.meta_loop_config.preference_log_path = str(preference_file)
            
            agent = LogReaderAgent(mock_workflow_context, debug_mode=True)
            logs = agent.run()
            
            assert "feedback_log" in logs
            assert "preference_log" in logs
            assert "bullet count" in logs["feedback_log"]
            assert "action_verbs" in logs["preference_log"]
    
    def test_read_logs_missing_files(self, mock_workflow_context):
        """Test log reading with missing files"""
        with patch('run_learning_v10_0.CONFIG') as mock_config:
            mock_config.meta_loop_config.feedback_log_path = "/nonexistent/feedback.jsonl"
            mock_config.meta_loop_config.preference_log_path = "/nonexistent/preference.jsonl"
            
            agent = LogReaderAgent(mock_workflow_context, debug_mode=True)
            logs = agent.run()
            
            # Should return empty logs, not crash
            assert logs["feedback_log"] == ""
            assert logs["preference_log"] == ""


class TestAsyncPatternFinderAgent:
    """Test AsyncPatternFinderAgent"""
    
    @pytest.mark.asyncio
    async def test_find_patterns_success(
        self, mock_workflow_context, sample_patterns
    ):
        """Test successful pattern finding"""
        mock_client = mock_workflow_context.get_model_client.return_value
        mock_client.chat_completion_async.return_value = {
            "content": {"patterns": sample_patterns}
        }
        
        agent = AsyncPatternFinderAgent(mock_workflow_context, debug_mode=True)
        raw_logs = {
            "feedback_log": "QA failure: bullet count\nQA failure: bullet count",
            "preference_log": ""
        }
        
        patterns = await agent.run_async(raw_logs)
        
        assert len(patterns) == 2
        assert patterns[0]["id"] == "pattern_1"
        mock_client.chat_completion_async.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_find_patterns_empty_logs(self, mock_workflow_context):
        """Test pattern finding with empty logs"""
        agent = AsyncPatternFinderAgent(mock_workflow_context, debug_mode=True)
        raw_logs = {"feedback_log": "", "preference_log": ""}
        
        patterns = await agent.run_async(raw_logs)
        
        assert patterns == []
    
    @pytest.mark.asyncio
    async def test_find_patterns_api_error(self, mock_workflow_context):
        """Test pattern finding with API error"""
        mock_client = mock_workflow_context.get_model_client.return_value
        mock_client.chat_completion_async.side_effect = Exception("API error")
        
        agent = AsyncPatternFinderAgent(mock_workflow_context, debug_mode=True)
        raw_logs = {"feedback_log": "data", "preference_log": "data"}
        
        patterns = await agent.run_async(raw_logs)
        
        assert patterns == []  # Should handle error gracefully


class TestAsyncHypothesisGeneratorAgent:
    """Test AsyncHypothesisGeneratorAgent"""
    
    @pytest.mark.asyncio
    async def test_generate_hypotheses_success(
        self, mock_workflow_context, sample_patterns, sample_hypotheses
    ):
        """Test successful hypothesis generation"""
        mock_client = mock_workflow_context.get_model_client.return_value
        mock_client.chat_completion_async.return_value = {
            "content": {"hypotheses": sample_hypotheses}
        }
        
        agent = AsyncHypothesisGeneratorAgent(mock_workflow_context, debug_mode=True)
        hypotheses = await agent.run_async(sample_patterns, critique=None)
        
        assert len(hypotheses) == 1
        assert hypotheses[0]["id"] == "hyp_1"
        mock_client.chat_completion_async.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_hypotheses_with_critique(
        self, mock_workflow_context, sample_patterns, sample_hypotheses
    ):
        """Test hypothesis generation incorporating critique"""
        mock_client = mock_workflow_context.get_model_client.return_value
        mock_client.chat_completion_async.return_value = {
            "content": {"hypotheses": sample_hypotheses}
        }
        
        critique = {"reason": "Previous hypothesis too vague"}
        
        agent = AsyncHypothesisGeneratorAgent(mock_workflow_context, debug_mode=True)
        hypotheses = await agent.run_async(sample_patterns, critique=critique)
        
        # Should pass critique to LLM
        call_args = mock_client.chat_completion_async.call_args
        assert "critique" in str(call_args)
    
    @pytest.mark.asyncio
    async def test_generate_hypotheses_api_error(
        self, mock_workflow_context, sample_patterns
    ):
        """Test hypothesis generation with API error"""
        mock_client = mock_workflow_context.get_model_client.return_value
        mock_client.chat_completion_async.side_effect = Exception("API error")
        
        agent = AsyncHypothesisGeneratorAgent(mock_workflow_context, debug_mode=True)
        hypotheses = await agent.run_async(sample_patterns, critique=None)
        
        assert hypotheses == []


class TestAsyncProposalDrafterAgent:
    """Test AsyncProposalDrafterAgent"""
    
    @pytest.mark.asyncio
    async def test_draft_proposal_success(
        self, mock_workflow_context, sample_hypotheses, sample_proposal
    ):
        """Test successful proposal drafting"""
        mock_client = mock_workflow_context.get_model_client.return_value
        mock_client.chat_completion_async.return_value = {
            "content": sample_proposal
        }
        
        agent = AsyncProposalDrafterAgent(mock_workflow_context, debug_mode=True)
        proposal = await agent.run_async(sample_hypotheses[0])
        
        assert proposal["type"] == "constraint_addition"
        assert "BulletGeneratorAgent" in proposal["target"]
        mock_client.chat_completion_async.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_draft_proposal_api_error(
        self, mock_workflow_context, sample_hypotheses
    ):
        """Test proposal drafting with API error"""
        mock_client = mock_workflow_context.get_model_client.return_value
        mock_client.chat_completion_async.side_effect = Exception("API error")
        
        agent = AsyncProposalDrafterAgent(mock_workflow_context, debug_mode=True)
        proposal = await agent.run_async(sample_hypotheses[0])
        
        assert proposal == {}


class TestAsyncProposalCritiqueAgent:
    """Test AsyncProposalCritiqueAgent"""
    
    @pytest.mark.asyncio
    async def test_critique_proposal_pass(
        self, mock_workflow_context, sample_proposal, sample_patterns
    ):
        """Test critique passes proposal"""
        mock_client = mock_workflow_context.get_model_client.return_value
        mock_client.chat_completion_async.return_value = {
            "content": {
                "critique_passed": True,
                "reason": "Proposal addresses root cause effectively"
            }
        }
        
        agent = AsyncProposalCritiqueAgent(mock_workflow_context, debug_mode=True)
        critique = await agent.run_async(sample_proposal, sample_patterns)
        
        assert critique["critique_passed"] is True
        mock_client.chat_completion_async.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_critique_proposal_fail(
        self, mock_workflow_context, sample_proposal, sample_patterns
    ):
        """Test critique fails proposal"""
        mock_client = mock_workflow_context.get_model_client.return_value
        mock_client.chat_completion_async.return_value = {
            "content": {
                "critique_passed": False,
                "reason": "Proposal may cause side effects"
            }
        }
        
        agent = AsyncProposalCritiqueAgent(mock_workflow_context, debug_mode=True)
        critique = await agent.run_async(sample_proposal, sample_patterns)
        
        assert critique["critique_passed"] is False
        assert "side effects" in critique["reason"]
    
    @pytest.mark.asyncio
    async def test_critique_proposal_api_error(
        self, mock_workflow_context, sample_proposal, sample_patterns
    ):
        """Test critique with API error"""
        mock_client = mock_workflow_context.get_model_client.return_value
        mock_client.chat_completion_async.side_effect = Exception("API error")
        
        agent = AsyncProposalCritiqueAgent(mock_workflow_context, debug_mode=True)
        critique = await agent.run_async(sample_proposal, sample_patterns)
        
        assert critique["critique_passed"] is False


class TestMetaPlannerAgent:
    """Test MetaPlannerAgent"""
    
    def test_write_proposal_success(self, tmp_path, sample_proposal):
        """Test successful proposal writing"""
        output_file = tmp_path / "proposals.jsonl"
        
        agent = MetaPlannerAgent()
        result = agent.run(sample_proposal, str(output_file))
        
        assert result is True
        assert output_file.exists()
        
        # Verify content
        content = output_file.read_text()
        assert "constraint_addition" in content
    
    def test_write_proposal_io_error(self, sample_proposal):
        """Test proposal writing with IO error"""
        agent = MetaPlannerAgent()
        result = agent.run(sample_proposal, "/nonexistent/dir/proposals.jsonl")
        
        assert result is False


# ============================================================================
# NODE FUNCTION TESTS
# ============================================================================

class TestNodeFunctions:
    """Test LangGraph node functions"""
    
    @pytest.mark.asyncio
    async def test_run_read_logs_node(
        self, mock_workflow_context, tmp_path, sample_feedback_log
    ):
        """Test read logs node"""
        feedback_file = tmp_path / "feedback.jsonl"
        feedback_file.write_text(sample_feedback_log)
        
        with patch('run_learning_v10_0.CONFIG') as mock_config:
            mock_config.meta_loop_config.feedback_log_path = str(feedback_file)
            mock_config.meta_loop_config.preference_log_path = str(tmp_path / "pref.jsonl")
            
            state = MetaGraphState()
            result = await run_read_logs(state, mock_workflow_context)
            
            assert "raw_logs" in result
            assert "feedback_log" in result["raw_logs"]
    
    @pytest.mark.asyncio
    async def test_run_find_patterns_node(
        self, mock_workflow_context, sample_patterns
    ):
        """Test find patterns node"""
        mock_client = mock_workflow_context.get_model_client.return_value
        mock_client.chat_completion_async.return_value = {
            "content": {"patterns": sample_patterns}
        }
        
        state = MetaGraphState()
        state["raw_logs"] = {"feedback_log": "data", "preference_log": "data"}
        
        result = await run_find_patterns(state, mock_workflow_context)
        
        assert "patterns" in result
        assert len(result["patterns"]) == 2
    
    @pytest.mark.asyncio
    async def test_run_generate_hypothesis_node(
        self, mock_workflow_context, sample_patterns, sample_hypotheses
    ):
        """Test generate hypothesis node"""
        mock_client = mock_workflow_context.get_model_client.return_value
        mock_client.chat_completion_async.return_value = {
            "content": {"hypotheses": sample_hypotheses}
        }
        
        state = MetaGraphState()
        state["patterns"] = sample_patterns
        state["replan_count"] = 0
        
        result = await run_generate_hypothesis(state, mock_workflow_context)
        
        assert "hypotheses" in result
        assert result["replan_count"] == 1
    
    @pytest.mark.asyncio
    async def test_run_draft_proposal_node(
        self, mock_workflow_context, sample_hypotheses, sample_proposal
    ):
        """Test draft proposal node"""
        mock_client = mock_workflow_context.get_model_client.return_value
        mock_client.chat_completion_async.return_value = {
            "content": sample_proposal
        }
        
        state = MetaGraphState()
        state["hypotheses"] = sample_hypotheses.copy()
        
        result = await run_draft_proposal(state, mock_workflow_context)
        
        assert "proposal" in result
        assert len(result["hypotheses"]) == 0  # Hypothesis consumed
    
    @pytest.mark.asyncio
    async def test_run_critique_proposal_node(
        self, mock_workflow_context, sample_proposal, sample_patterns
    ):
        """Test critique proposal node"""
        mock_client = mock_workflow_context.get_model_client.return_value
        mock_client.chat_completion_async.return_value = {
            "content": {"critique_passed": True, "reason": "Good"}
        }
        
        state = MetaGraphState()
        state["proposal"] = sample_proposal
        state["patterns"] = sample_patterns
        
        result = await run_critique_proposal(state, mock_workflow_context)
        
        assert "critique" in result
        assert result["critique"]["critique_passed"] is True
    
    @pytest.mark.asyncio
    async def test_run_write_proposal_node(
        self, mock_workflow_context, tmp_path, sample_proposal
    ):
        """Test write proposal node"""
        output_file = tmp_path / "proposals.jsonl"
        
        with patch('run_learning_v10_0.CONFIG') as mock_config:
            mock_config.meta_loop_config.proposed_rules_path = str(output_file)
            
            state = MetaGraphState()
            state["proposal"] = sample_proposal
            
            result = await run_write_proposal(state, mock_workflow_context)
            
            assert output_file.exists()


# ============================================================================
# GRAPH BUILDING TESTS
# ============================================================================

class TestMetaLearningGraph:
    """Test meta-learning graph construction"""
    
    def test_get_meta_learning_graph_app(self, mock_workflow_context):
        """Test graph app creation"""
        mock_checkpointer = MagicMock()
        
        app = get_meta_learning_graph_app(mock_checkpointer, mock_workflow_context)
        
        assert app is not None
        # Graph should have nodes
        assert hasattr(app, 'invoke')


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestMetaLearningIntegration:
    """Integration tests for meta-learning"""
    
    @pytest.mark.asyncio
    async def test_run_meta_learning_full_flow(
        self, mock_workflow_context, tmp_path, sample_feedback_log
    ):
        """Test full meta-learning flow"""
        feedback_file = tmp_path / "feedback.jsonl"
        preference_file = tmp_path / "preference.jsonl"
        output_file = tmp_path / "proposals.jsonl"
        
        feedback_file.write_text(sample_feedback_log)
        preference_file.write_text("")
        
        # Mock all LLM calls
        mock_client = mock_workflow_context.get_model_client.return_value
        
        call_count = [0]
        
        async def mock_chat_completion(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:  # Pattern finder
                return {
                    "content": {
                        "patterns": [
                            {"id": "p1", "description": "Test pattern", "frequency": 5}
                        ]
                    }
                }
            elif call_count[0] == 2:  # Hypothesis generator
                return {
                    "content": {
                        "hypotheses": [
                            {"id": "h1", "root_cause": "Test cause", "confidence": 0.8}
                        ]
                    }
                }
            elif call_count[0] == 3:  # Proposal drafter
                return {
                    "content": {
                        "type": "fix",
                        "target": "Agent",
                        "change": "Add validation"
                    }
                }
            else:  # Critique
                return {
                    "content": {
                        "critique_passed": True,
                        "reason": "Good proposal"
                    }
                }
        
        mock_client.chat_completion_async = AsyncMock(side_effect=mock_chat_completion)
        
        with patch('run_learning_v10_0.setup_logging'), \
             patch('run_learning_v10_0.CONFIG') as mock_config, \
             patch('run_learning_v10_0.redis.Redis'), \
             patch('run_learning_v10_0.WorkflowContext', return_value=mock_workflow_context), \
             patch('run_learning_v10_0.RedisSaver'):
            
            mock_config.meta_loop_config.enable_meta_learning = True
            mock_config.meta_loop_config.feedback_log_path = str(feedback_file)
            mock_config.meta_loop_config.preference_log_path = str(preference_file)
            mock_config.meta_loop_config.proposed_rules_path = str(output_file)
            mock_config.meta_loop_config.max_meta_replan_loops = 3
            mock_config.redis_config.host = "localhost"
            mock_config.redis_config.port = 6379
            mock_config.redis_config.db = 0
            
            await run_meta_learning()
            
            # Should complete without error
            # Verify proposal was written
            assert output_file.exists()
    
    @pytest.mark.asyncio
    async def test_run_meta_learning_disabled(self, mock_workflow_context):
        """Test meta-learning when disabled"""
        with patch('run_learning_v10_0.setup_logging'), \
             patch('run_learning_v10_0.CONFIG') as mock_config:
            
            mock_config.meta_loop_config.enable_meta_learning = False
            
            await run_meta_learning()
            # Should exit early without error


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
