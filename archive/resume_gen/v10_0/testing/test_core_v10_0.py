# File: test_core_v10_0.py
# Comprehensive tests for core_v10_0.py
# Tests: WorkflowContext, State Management, CacheManager, Cost Tracking

import pytest
import redis
import json
import hashlib
from unittest.mock import Mock, MagicMock, patch, AsyncMock
from datetime import datetime
from typing import Dict, Any

# Import components to test (adjust imports based on actual structure)
try:
    from core_v10_0 import (
        WorkflowContext, MainGraphState, CacheManager, CostTracker,
        ResumeContext, JobContext, MetadataContext,
        CostCeilingExceededError, ModelAPIError, JSONParsingError, FileIOError
    )
    from master_config_v10_0 import CONFIG
except ImportError:
    pytest.skip("core_v10_0 module not available", allow_module_level=True)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_redis():
    """Mock Redis client"""
    redis_mock = MagicMock(spec=redis.Redis)
    redis_mock.get.return_value = None
    redis_mock.set.return_value = True
    redis_mock.setex.return_value = True
    redis_mock.incr.return_value = 1
    return redis_mock


@pytest.fixture
def mock_config():
    """Mock configuration object"""
    config = MagicMock()
    
    # Caching config
    config.caching_config.enable_llm_caching = True
    config.caching_config.cache_ttl_seconds = 3600
    config.caching_config.cache_db = 1
    
    # Cost config
    config.cost_config.cost_ceiling_per_workflow = 5.0
    config.cost_config.cost_ceiling_per_agent = 0.5
    config.cost_config.enable_cost_tracking = True
    config.cost_config.cost_warning_threshold = 4.0
    
    # Performance config
    config.performance_config.enable_async_llm = True
    config.performance_config.max_concurrent_llm_calls = 10
    config.performance_config.llm_timeout_seconds = 30
    
    return config


@pytest.fixture
def workflow_context(mock_redis, mock_config):
    """Create WorkflowContext with mocked dependencies"""
    with patch('core_v10_0.CONFIG', mock_config):
        context = WorkflowContext(mock_config, mock_redis)
        return context


@pytest.fixture
def cache_manager(mock_redis, mock_config):
    """Create CacheManager instance"""
    return CacheManager(mock_redis, mock_config)


@pytest.fixture
def cost_tracker(mock_config):
    """Create CostTracker instance"""
    return CostTracker(mock_config)


# ============================================================================
# WORKFLOWCONTEXT TESTS (ROW 4: Dependency Injection)
# ============================================================================

class TestWorkflowContext:
    """Test WorkflowContext dependency injection"""
    
    def test_context_initialization(self, workflow_context):
        """Test WorkflowContext initializes all dependencies"""
        assert workflow_context.config is not None
        assert workflow_context.redis_client is not None
        assert workflow_context.cache_manager is not None
        assert workflow_context.cost_tracker is not None
    
    def test_get_model_client_returns_client(self, workflow_context):
        """Test get_model_client returns appropriate client"""
        with patch('core_v10_0.AnthropicAsyncClient') as mock_anthropic:
            client = workflow_context.get_model_client("anthropic", "claude-sonnet-4-20250514")
            assert client is not None
    
    def test_get_model_client_caches_instances(self, workflow_context):
        """Test model clients are cached per (provider, model)"""
        with patch('core_v10_0.AnthropicAsyncClient') as mock_anthropic:
            client1 = workflow_context.get_model_client("anthropic", "claude-sonnet-4-20250514")
            client2 = workflow_context.get_model_client("anthropic", "claude-sonnet-4-20250514")
            assert client1 is client2  # Same instance
    
    def test_get_model_client_different_models(self, workflow_context):
        """Test different models return different clients"""
        with patch('core_v10_0.AnthropicAsyncClient') as mock_anthropic, \
             patch('core_v10_0.GeminiAsyncClient') as mock_gemini:
            client1 = workflow_context.get_model_client("anthropic", "claude-sonnet-4-20250514")
            client2 = workflow_context.get_model_client("google", "gemini-2.0-flash-exp")
            assert client1 is not client2


# ============================================================================
# STATE MANAGEMENT TESTS (ROW 4: Modular State)
# ============================================================================

class TestMainGraphState:
    """Test MainGraphState decomposition"""
    
    def test_state_initialization(self):
        """Test MainGraphState initializes with all sub-contexts"""
        state = MainGraphState()
        assert isinstance(state.resume, ResumeContext)
        assert isinstance(state.job, JobContext)
        assert isinstance(state.metadata, MetadataContext)
    
    def test_state_to_dict(self):
        """Test state serialization to dict"""
        state = MainGraphState()
        state.resume.master_resume = {"name": "Test User"}
        state.job.company = "Test Corp"
        state.metadata.workflow_id = "test-123"
        
        state_dict = state.to_dict()
        assert isinstance(state_dict, dict)
        assert state_dict["resume"]["master_resume"]["name"] == "Test User"
        assert state_dict["job"]["company"] == "Test Corp"
        assert state_dict["metadata"]["workflow_id"] == "test-123"
    
    def test_state_from_dict(self):
        """Test state deserialization from dict"""
        state_dict = {
            "resume": {"master_resume": {"name": "Test User"}},
            "job": {"company": "Test Corp"},
            "metadata": {"workflow_id": "test-123"}
        }
        
        state = MainGraphState.from_dict(state_dict)
        assert state.resume.master_resume["name"] == "Test User"
        assert state.job.company == "Test Corp"
        assert state.metadata.workflow_id == "test-123"
    
    def test_state_round_trip(self):
        """Test state serialization/deserialization round trip"""
        original_state = MainGraphState()
        original_state.resume.master_resume = {"skills": ["Python", "AI"]}
        original_state.job.job_title = "Senior Engineer"
        
        state_dict = original_state.to_dict()
        restored_state = MainGraphState.from_dict(state_dict)
        
        assert restored_state.resume.master_resume == original_state.resume.master_resume
        assert restored_state.job.job_title == original_state.job.job_title


# ============================================================================
# CACHE MANAGER TESTS (ROW 5: Caching)
# ============================================================================

class TestCacheManager:
    """Test CacheManager functionality"""
    
    def test_cache_key_generation(self, cache_manager):
        """Test cache key is deterministic and unique"""
        key1 = cache_manager.generate_cache_key(
            provider="anthropic",
            model="claude-sonnet-4-20250514",
            prompt="Test prompt",
            temperature=0.7
        )
        
        key2 = cache_manager.generate_cache_key(
            provider="anthropic",
            model="claude-sonnet-4-20250514",
            prompt="Test prompt",
            temperature=0.7
        )
        
        assert key1 == key2  # Deterministic
        assert len(key1) == 64  # SHA256 hex digest
    
    def test_cache_key_differs_by_prompt(self, cache_manager):
        """Test different prompts produce different cache keys"""
        key1 = cache_manager.generate_cache_key(
            provider="anthropic", model="claude", prompt="Prompt A", temperature=0.7
        )
        key2 = cache_manager.generate_cache_key(
            provider="anthropic", model="claude", prompt="Prompt B", temperature=0.7
        )
        assert key1 != key2
    
    def test_cache_key_differs_by_temperature(self, cache_manager):
        """Test different temperatures produce different cache keys"""
        key1 = cache_manager.generate_cache_key(
            provider="anthropic", model="claude", prompt="Test", temperature=0.7
        )
        key2 = cache_manager.generate_cache_key(
            provider="anthropic", model="claude", prompt="Test", temperature=0.9
        )
        assert key1 != key2
    
    def test_cache_set_and_get(self, cache_manager, mock_redis):
        """Test cache set and retrieve"""
        cache_key = "test_cache_key"
        response_data = {"content": "Cached response"}
        
        mock_redis.get.return_value = json.dumps(response_data).encode('utf-8')
        
        cache_manager.set(cache_key, response_data)
        cached = cache_manager.get(cache_key)
        
        assert cached == response_data
        mock_redis.setex.assert_called_once()
    
    def test_cache_miss(self, cache_manager, mock_redis):
        """Test cache miss returns None"""
        mock_redis.get.return_value = None
        
        result = cache_manager.get("nonexistent_key")
        assert result is None
    
    def test_cache_stats_tracking(self, cache_manager, mock_redis):
        """Test cache hit/miss statistics"""
        # Simulate cache hit
        mock_redis.get.return_value = json.dumps({"cached": True}).encode('utf-8')
        cache_manager.get("key1")
        
        # Simulate cache miss
        mock_redis.get.return_value = None
        cache_manager.get("key2")
        
        stats = cache_manager.get_stats()
        assert stats['hits'] >= 1
        assert stats['misses'] >= 1
        assert 'hit_rate_pct' in stats
    
    def test_cache_disabled(self, mock_redis):
        """Test cache operations when caching is disabled"""
        config = MagicMock()
        config.caching_config.enable_llm_caching = False
        
        cache_manager = CacheManager(mock_redis, config)
        
        # Set should not call Redis
        cache_manager.set("key", {"data": "value"})
        mock_redis.setex.assert_not_called()
        
        # Get should return None
        result = cache_manager.get("key")
        assert result is None


# ============================================================================
# COST TRACKER TESTS (ROW 4: Dependency Injection)
# ============================================================================

class TestCostTracker:
    """Test CostTracker functionality"""
    
    def test_cost_tracking_initialization(self, cost_tracker):
        """Test CostTracker initializes correctly"""
        assert cost_tracker.config is not None
        assert cost_tracker.cost_ceiling_per_workflow > 0
        assert cost_tracker.enable_tracking is True
    
    def test_track_cost(self, cost_tracker):
        """Test tracking cost for workflow"""
        workflow_id = "test-workflow-123"
        cost_tracker.track_cost(workflow_id, agent_name="TestAgent", cost=0.15)
        
        summary = cost_tracker.get_cost_summary(workflow_id)
        assert summary['total_workflow_cost'] == 0.15
        assert summary['agent_costs']['TestAgent'] == 0.15
    
    def test_cost_ceiling_check_pass(self, cost_tracker):
        """Test cost ceiling check passes under limit"""
        workflow_id = "test-workflow-123"
        cost_tracker.track_cost(workflow_id, "Agent1", 1.0)
        
        # Should not raise exception
        cost_tracker.check_cost_ceiling(workflow_id)
    
    def test_cost_ceiling_check_fail(self, cost_tracker):
        """Test cost ceiling check fails over limit"""
        workflow_id = "test-workflow-123"
        cost_tracker.track_cost(workflow_id, "Agent1", 6.0)  # Over 5.0 ceiling
        
        with pytest.raises(CostCeilingExceededError):
            cost_tracker.check_cost_ceiling(workflow_id)
    
    def test_cost_warning_threshold(self, cost_tracker):
        """Test cost warning at threshold"""
        workflow_id = "test-workflow-123"
        cost_tracker.track_cost(workflow_id, "Agent1", 4.5)  # Over 4.0 warning
        
        with patch('core_v10_0.logger') as mock_logger:
            cost_tracker.check_cost_ceiling(workflow_id)
            mock_logger.warning.assert_called()
    
    def test_multiple_agents_cost(self, cost_tracker):
        """Test tracking costs across multiple agents"""
        workflow_id = "test-workflow-123"
        cost_tracker.track_cost(workflow_id, "Agent1", 0.5)
        cost_tracker.track_cost(workflow_id, "Agent2", 0.3)
        cost_tracker.track_cost(workflow_id, "Agent3", 0.2)
        
        summary = cost_tracker.get_cost_summary(workflow_id)
        assert summary['total_workflow_cost'] == 1.0
        assert len(summary['agent_costs']) == 3
    
    def test_cost_tracking_disabled(self):
        """Test cost tracking when disabled"""
        config = MagicMock()
        config.cost_config.enable_cost_tracking = False
        config.cost_config.cost_ceiling_per_workflow = 5.0
        
        tracker = CostTracker(config)
        
        # Should not track anything
        tracker.track_cost("workflow-123", "Agent1", 10.0)
        summary = tracker.get_cost_summary("workflow-123")
        assert summary['total_workflow_cost'] == 0.0


# ============================================================================
# EXCEPTION TESTS (v9.9 Preserved)
# ============================================================================

class TestExceptions:
    """Test custom exception types"""
    
    def test_cost_ceiling_exceeded_error(self):
        """Test CostCeilingExceededError"""
        with pytest.raises(CostCeilingExceededError) as exc_info:
            raise CostCeilingExceededError("Cost limit exceeded")
        assert "Cost limit exceeded" in str(exc_info.value)
    
    def test_model_api_error(self):
        """Test ModelAPIError"""
        with pytest.raises(ModelAPIError) as exc_info:
            raise ModelAPIError("API call failed")
        assert "API call failed" in str(exc_info.value)
    
    def test_json_parsing_error(self):
        """Test JSONParsingError"""
        with pytest.raises(JSONParsingError) as exc_info:
            raise JSONParsingError("Invalid JSON")
        assert "Invalid JSON" in str(exc_info.value)
    
    def test_file_io_error(self):
        """Test FileIOError"""
        with pytest.raises(FileIOError) as exc_info:
            raise FileIOError("File not found")
        assert "File not found" in str(exc_info.value)


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestCoreIntegration:
    """Integration tests for core components"""
    
    def test_workflow_context_full_initialization(self, mock_redis, mock_config):
        """Test complete WorkflowContext initialization"""
        context = WorkflowContext(mock_config, mock_redis)
        
        # Verify all components initialized
        assert context.cache_manager is not None
        assert context.cost_tracker is not None
        assert context.config is not None
        assert context.redis_client is not None
    
    def test_state_with_context_integration(self, workflow_context):
        """Test state management with context"""
        state = MainGraphState()
        state.resume.master_resume = {"name": "John Doe"}
        state.metadata.workflow_id = "workflow-123"
        
        # Simulate cost tracking
        workflow_context.cost_tracker.track_cost(
            state.metadata.workflow_id,
            "TestAgent",
            0.25
        )
        
        summary = workflow_context.cost_tracker.get_cost_summary(
            state.metadata.workflow_id
        )
        assert summary['total_workflow_cost'] == 0.25
    
    def test_cache_and_cost_integration(self, workflow_context):
        """Test cache and cost tracking work together"""
        workflow_id = "test-workflow"
        cache_key = workflow_context.cache_manager.generate_cache_key(
            provider="anthropic",
            model="claude",
            prompt="Test",
            temperature=0.7
        )
        
        # Simulate caching response
        response = {"content": "Cached result"}
        workflow_context.cache_manager.set(cache_key, response)
        
        # Track cost
        workflow_context.cost_tracker.track_cost(workflow_id, "Agent1", 0.1)
        
        # Verify both work
        cached = workflow_context.cache_manager.get(cache_key)
        cost = workflow_context.cost_tracker.get_cost_summary(workflow_id)
        
        assert cached == response
        assert cost['total_workflow_cost'] == 0.1


# ============================================================================
# EDGE CASES AND ERROR CONDITIONS
# ============================================================================

class TestEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_empty_state_serialization(self):
        """Test serializing empty state"""
        state = MainGraphState()
        state_dict = state.to_dict()
        assert isinstance(state_dict, dict)
        
        restored = MainGraphState.from_dict(state_dict)
        assert restored is not None
    
    def test_cache_with_large_response(self, cache_manager, mock_redis):
        """Test caching large response"""
        large_response = {"content": "X" * 100000}  # 100KB response
        cache_key = "large_key"
        
        cache_manager.set(cache_key, large_response)
        mock_redis.setex.assert_called_once()
    
    def test_cost_tracker_zero_cost(self, cost_tracker):
        """Test tracking zero cost"""
        workflow_id = "test-workflow"
        cost_tracker.track_cost(workflow_id, "FreeAgent", 0.0)
        
        summary = cost_tracker.get_cost_summary(workflow_id)
        assert summary['total_workflow_cost'] == 0.0
    
    def test_cache_key_with_special_characters(self, cache_manager):
        """Test cache key generation with special characters"""
        key = cache_manager.generate_cache_key(
            provider="test",
            model="test-model",
            prompt="Special: !@#$%^&*()_+{}[]|\\:;<>?,./~`",
            temperature=0.7
        )
        assert len(key) == 64  # Still valid SHA256
    
    def test_workflow_context_with_none_redis(self, mock_config):
        """Test WorkflowContext handles None redis gracefully"""
        # This should raise or handle gracefully depending on design
        with pytest.raises((TypeError, AttributeError)):
            context = WorkflowContext(mock_config, None)


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
