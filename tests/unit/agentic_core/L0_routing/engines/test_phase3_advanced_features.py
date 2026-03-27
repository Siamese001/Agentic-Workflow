"""
Tests for Phase 3 Advanced Features and Optimization

Comprehensive test suite covering Wave 3.1 (Mixture of Experts), Wave 3.2 (Meta-Learning),
and Wave 3.3 (Production Optimization) implementations.
"""

import pytest
import numpy as np
import time
import threading
from unittest.mock import Mock, patch
from typing import Dict, Any, List

# Import the modules we're testing
from agentic_core.L0_routing.engines.mixture_of_experts import (
    MixtureOfExperts,
    BaseExpert,
    CodeReviewExpert,
    ResumeExpert,
    DataAnalysisExpert,
    GatingNetwork,
    LoadBalancer,
    ExpertSpecialization,
    ExpertPrediction,
    MoEDecision,
    create_default_moe
)

from agentic_core.L0_routing.engines.meta_learning_integration import (
    MetaLearningFramework,
    BaseMetaLearner,
    MAMLMetaLearner,
    ContinualLearner,
    TaskScheduler,
    TaskExample,
    MetaLearningTask,
    AdaptationResult,
    create_few_shot_task,
    create_default_meta_framework
)

from agentic_core.L0_routing.engines.production_optimization import (
    PerformanceOptimizer,
    ModelCompressor,
    QuantizationCompressor,
    PruningCompressor,
    LRUCache,
    DistributedCache,
    OptimizationMetrics,
    CacheEntry,
    CacheStats,
    create_default_optimizer
)

class TestMixtureOfExperts:
    """Test suite for Mixture of Experts implementation"""
    
    @pytest.fixture
    def default_moe(self):
        """Create a default mixture of experts"""
        return create_default_moe()
    
    @pytest.fixture
    def sample_experts(self):
        """Create sample experts for testing"""
        return [
            CodeReviewExpert("code_expert"),
            ResumeExpert("resume_expert"),
            DataAnalysisExpert("data_expert")
        ]
    
    def test_moe_initialization(self, default_moe):
        """Test MoE initialization"""
        assert len(default_moe.experts) == 3
        assert default_moe.gating_network is not None
        assert default_moe.load_balancer is not None
        assert default_moe.max_concurrent_experts == 3
        assert default_moe.prediction_count == 0
    
    def test_expert_specialization(self):
        """Test expert specialization matching"""
        specialization = ExpertSpecialization(
            domain_name="code_review",
            keywords=["code", "review", "python"],
            capability_score=0.9,
            confidence_threshold=0.7
        )
        
        # Test matching
        match_score = specialization.matches_query("Please review my Python code")
        assert match_score > 0.5
        
        # Test non-matching
        match_score = specialization.matches_query("Write my resume")
        assert match_score < 0.5
    
    def test_code_review_expert(self):
        """Test code review expert predictions"""
        expert = CodeReviewExpert("test_expert")
        
        # Test code review query
        prediction = expert.predict("Please review my Python code", {})
        
        assert isinstance(prediction, ExpertPrediction)
        assert prediction.expert_id == "test_expert"
        assert "review" in prediction.agent_name or "python" in prediction.agent_name
        assert 0.0 <= prediction.confidence <= 1.0
        assert prediction.uncertainty >= 0.0
        assert prediction.processing_time >= 0.0
    
    def test_resume_expert(self):
        """Test resume expert predictions"""
        expert = ResumeExpert("test_expert")
        
        # Test resume query
        prediction = expert.predict("Help me write my resume", {})
        
        assert isinstance(prediction, ExpertPrediction)
        assert prediction.expert_id == "test_expert"
        assert "resume" in prediction.agent_name or "career" in prediction.agent_name
        assert 0.0 <= prediction.confidence <= 1.0
    
    def test_data_analysis_expert(self):
        """Test data analysis expert predictions"""
        expert = DataAnalysisExpert("test_expert")
        
        # Test data analysis query
        prediction = expert.predict("Analyze this sales data", {})
        
        assert isinstance(prediction, ExpertPrediction)
        assert prediction.expert_id == "test_expert"
        assert "data" in prediction.agent_name or "analysis" in prediction.agent_name
        assert 0.0 <= prediction.confidence <= 1.0
    
    def test_gating_network(self):
        """Test gating network functionality"""
        gating_network = GatingNetwork(input_dim=50, num_experts=3)
        
        # Test forward pass
        query_embedding = np.random.randn(50)
        expert_features = [{"confidence": 0.8, "reliability": 0.9} for _ in range(3)]
        
        probabilities = gating_network.forward(query_embedding, expert_features)
        
        assert len(probabilities) == 3
        assert all(0.0 <= p <= 1.0 for p in probabilities)
        assert abs(sum(probabilities) - 1.0) < 1e-6  # Should sum to 1
        
        # Test update
        gating_network.update(query_embedding, expert_features, 0, 1.0)
        assert gating_network.training_count == 1
    
    def test_load_balancer(self):
        """Test load balancer functionality"""
        load_balancer = LoadBalancer()
        
        # Register experts
        load_balancer.register_expert("expert1", capacity=1.0)
        load_balancer.register_expert("expert2", capacity=2.0)
        
        # Test load updates
        load_balancer.update_load("expert1", 0.5)
        assert load_balancer.expert_loads["expert1"] == 0.5
        
        # Test weight calculation
        weights = load_balancer.get_load_balance_weights(["expert1", "expert2"])
        assert len(weights) == 2
        assert sum(weights.values()) == 1.0
    
    def test_moe_routing(self, default_moe):
        """Test MoE routing decision"""
        query = "Please review my Python code for bugs"
        context = {"user_id": "test_user"}
        
        decision = default_moe.route(query, context)
        
        assert isinstance(decision, MoEDecision)
        assert decision.selected_expert in default_moe.experts
        assert decision.selected_agent is not None
        assert 0.0 <= decision.confidence <= 1.0
        assert decision.uncertainty >= 0.0
        assert len(decision.gating_scores) == len(default_moe.experts)
        assert len(decision.expert_predictions) == len(default_moe.experts)
        assert decision.load_balancing_applied is True
        assert decision.decision_time >= 0.0
    
    def test_moe_update_outcome(self, default_moe):
        """Test MoE outcome update"""
        query = "Help me write my resume"
        context = {"user_id": "test_user"}
        
        decision = default_moe.route(query, context)
        initial_success_rate = default_moe.get_success_rate()
        
        # Update with successful outcome
        default_moe.update_outcome(decision, success=True)
        
        assert default_moe.prediction_count == 1
        assert default_moe.success_count == 1
        assert default_moe.get_success_rate() == 1.0
    
    def test_moe_performance_tracking(self, default_moe):
        """Test MoE performance tracking"""
        # Make several routing decisions
        queries = [
            "Review my Python code",
            "Write my resume",
            "Analyze sales data",
            "Debug JavaScript function"
        ]
        
        for query in queries:
            decision = default_moe.route(query, {})
            default_moe.update_outcome(decision, success=True)
        
        performance = default_moe.get_expert_performance()
        
        assert len(performance) == 3
        for expert_id, metrics in performance.items():
            assert "domain" in metrics
            assert "reliability" in metrics
            assert "predictions" in metrics
            assert "successes" in metrics
            assert "avg_processing_time" in metrics
            assert "load_factor" in metrics
    
    def test_concurrent_expert_predictions(self, default_moe):
        """Test concurrent expert predictions"""
        query = "Review my complex Python algorithm"
        context = {"complexity": "high"}
        
        start_time = time.time()
        decision = default_moe.route(query, context)
        end_time = time.time()
        
        # Should complete quickly due to concurrency
        assert end_time - start_time < 2.0  # 2 seconds max
        assert len(decision.expert_predictions) == len(default_moe.experts)
    
    def test_moe_shutdown(self, default_moe):
        """Test MoE shutdown"""
        # Should shutdown without errors
        default_moe.shutdown()
        assert True  # If we reach here, shutdown was successful

class TestMetaLearningIntegration:
    """Test suite for Meta-Learning Integration"""
    
    @pytest.fixture
    def default_framework(self):
        """Create default meta-learning framework"""
        return create_default_meta_framework()
    
    @pytest.fixture
    def sample_task_examples(self):
        """Create sample task examples"""
        return [
            TaskExample(
                query="Review my Python code",
                context={"user_id": "user1"},
                target_agent="code_reviewer",
                confidence=0.8,
                success=True
            ),
            TaskExample(
                query="Write my resume",
                context={"user_id": "user2"},
                target_agent="resume_writer",
                confidence=0.9,
                success=True
            ),
            TaskExample(
                query="Analyze sales data",
                context={"user_id": "user3"},
                target_agent="data_analyst",
                confidence=0.7,
                success=False
            ),
            TaskExample(
                query="Debug JavaScript function",
                context={"user_id": "user4"},
                target_agent="code_reviewer",
                confidence=0.6,
                success=True
            )
        ]
    
    def test_framework_initialization(self, default_framework):
        """Test framework initialization"""
        assert len(default_framework.meta_learners) == 2
        assert "maml" in default_framework.meta_learners
        assert "continual" in default_framework.meta_learners
        assert default_framework.task_scheduler is not None
        assert default_framework.adaptation_threshold == 0.1
    
    def test_task_example_creation(self):
        """Test task example creation"""
        example = TaskExample(
            query="Test query",
            context={"test": "context"},
            target_agent="test_agent",
            confidence=0.8,
            success=True
        )
        
        assert example.query == "Test query"
        assert example.target_agent == "test_agent"
        assert example.confidence == 0.8
        assert example.success is True
        assert example.timestamp > 0
    
    def test_meta_learning_task_creation(self, sample_task_examples):
        """Test meta-learning task creation"""
        task = create_few_shot_task(
            task_id="test_task",
            task_name="Test Task",
            examples_data=[
                {"query": e.query, "target_agent": e.target_agent, "confidence": e.confidence}
                for e in sample_task_examples
            ]
        )
        
        assert task.task_id == "test_task"
        assert task.task_name == "Test Task"
        assert task.task_type == "few_shot"
        assert len(task.support_examples) > 0
        assert len(task.query_examples) > 0
        assert len(task.support_examples) + len(task.query_examples) == len(sample_task_examples)
    
    def test_maml_meta_learner(self):
        """Test MAML meta-learner"""
        learner = MAMLMetaLearner("test_maml", adaptation_rate=0.01)
        
        # Create a simple task
        examples = [
            TaskExample("code review", {}, "code_reviewer", 0.8, True),
            TaskExample("resume writing", {}, "resume_writer", 0.9, True)
        ]
        
        task = create_few_shot_task("maml_test", "MAML Test", [
            {"query": e.query, "target_agent": e.target_agent, "confidence": e.confidence}
            for e in examples
        ])
        
        # Test adaptation
        result = learner.adapt(task)
        
        assert isinstance(result, AdaptationResult)
        assert result.task_id == "maml_test"
        assert result.adaptation_type == "MAML"
        assert result.adaptation_time >= 0.0
        assert result.examples_used > 0
        
        # Test prediction
        agent_name, confidence = learner.predict("test query", {})
        assert agent_name is not None
        assert 0.0 <= confidence <= 1.0
    
    def test_continual_learner(self):
        """Test continual learner"""
        learner = ContinualLearner("test_continual", memory_size=100)
        
        # Create tasks
        task1_examples = [
            TaskExample("code review", {}, "code_reviewer", 0.8, True),
            TaskExample("debug code", {}, "code_reviewer", 0.7, True)
        ]
        
        task2_examples = [
            TaskExample("write resume", {}, "resume_writer", 0.9, True),
            TaskExample("cover letter", {}, "resume_writer", 0.8, False)
        ]
        
        task1 = create_few_shot_task("continual_test1", "Continual Test 1", [
            {"query": e.query, "target_agent": e.target_agent, "confidence": e.confidence}
            for e in task1_examples
        ])
        
        task2 = create_few_shot_task("continual_test2", "Continual Test 2", [
            {"query": e.query, "target_agent": e.target_agent, "confidence": e.confidence}
            for e in task2_examples
        ])
        
        # Test adaptation with experience replay
        result1 = learner.adapt(task1)
        assert isinstance(result1, AdaptationResult)
        assert result1.adaptation_type == "continual"
        
        # Second adaptation should use replay buffer
        result2 = learner.adapt(task2)
        assert isinstance(result2, AdaptationResult)
        assert len(learner.replay_buffer) > 0
    
    def test_task_scheduler(self):
        """Test task scheduler"""
        scheduler = TaskScheduler(max_concurrent_tasks=2)
        
        # Create tasks with different priorities
        task1 = create_few_shot_task("task1", "Task 1", [
            {"query": "test", "target_agent": "agent1", "confidence": 0.8}
        ], priority=1.0)
        
        task2 = create_few_shot_task("task2", "Task 2", [
            {"query": "test", "target_agent": "agent2", "confidence": 0.9}
        ], priority=2.0)
        
        task3 = create_few_shot_task("task3", "Task 3", [
            {"query": "test", "target_agent": "agent3", "confidence": 0.7}
        ], priority=0.5)
        
        # Add tasks
        scheduler.add_task(task1)
        scheduler.add_task(task2)
        scheduler.add_task(task3)
        
        # Test task retrieval (should be prioritized)
        next_task = scheduler.get_next_task()
        assert next_task.task_id == "task2"  # Highest priority
        
        # Test task completion
        scheduler.complete_task("task2")
        assert "task2" not in scheduler.active_tasks
        assert "task2" in [t.task_id for t in scheduler.completed_tasks]
        
        # Test statistics
        stats = scheduler.get_task_statistics()
        assert "queue_size" in stats
        assert "active_tasks" in stats
        assert "completed_tasks" in stats
        assert "task_types" in stats
    
    def test_framework_adaptation_request(self, default_framework, sample_task_examples):
        """Test framework adaptation request processing"""
        # Create adaptation task
        task = create_few_shot_task("framework_test", "Framework Test", [
            {"query": e.query, "target_agent": e.target_agent, "confidence": e.confidence}
            for e in sample_task_examples
        ])
        
        # Process adaptation
        results = default_framework.process_adaptation_request(task)
        
        assert len(results) == 2  # Should have results from both learners
        for result in results:
            assert isinstance(result, AdaptationResult)
            assert result.task_id == "framework_test"
    
    def test_framework_best_learner_selection(self, default_framework):
        """Test best learner selection"""
        # Initially should have a best learner
        best_learner = default_framework.get_best_learner()
        assert best_learner in default_framework.meta_learners
        
        # Test prediction with best learner
        agent_name, confidence = default_framework.predict_with_best_learner("test query", {})
        assert agent_name is not None
        assert 0.0 <= confidence <= 1.0
    
    def test_framework_statistics(self, default_framework):
        """Test framework statistics"""
        stats = default_framework.get_framework_statistics()
        
        assert "meta_learners" in stats
        assert "task_scheduler" in stats
        assert "framework_performance" in stats
        
        for learner_name, learner_stats in stats["meta_learners"].items():
            assert "performance_trend" in learner_stats
            assert "adaptations" in learner_stats
            assert "avg_performance" in learner_stats

class TestProductionOptimization:
    """Test suite for Production Optimization"""
    
    @pytest.fixture
    def default_optimizer(self):
        """Create default performance optimizer"""
        return create_default_optimizer()
    
    @pytest.fixture
    def sample_model(self):
        """Create a sample model for optimization"""
        class MockModel:
            def __init__(self):
                self.weights = np.random.randn(100, 50)
                self.bias = np.random.randn(50)
                self.metadata = {"version": "1.0", "type": "test"}
        
        return MockModel()
    
    def test_optimizer_initialization(self, default_optimizer):
        """Test optimizer initialization"""
        assert len(default_optimizer.compressors) == 2
        assert default_optimizer.cache is not None
        assert default_optimizer.optimization_target == "balanced"
        assert len(default_optimizer.compressed_models) == 0
    
    def test_quantization_compressor(self, sample_model):
        """Test quantization compressor"""
        compressor = QuantizationCompressor(bits=8)
        
        compressed_model, metrics = compressor.compress(sample_model)
        
        assert isinstance(metrics, OptimizationMetrics)
        assert metrics.compression_ratio >= 1.0
        assert metrics.latency_improvement >= 0.0
        assert metrics.original_size > 0
        assert metrics.compressed_size > 0
        
        # Test decompression
        decompressed_model = compressor.decompress(compressed_model)
        assert decompressed_model is not None
    
    def test_pruning_compressor(self, sample_model):
        """Test pruning compressor"""
        compressor = PruningCompressor(pruning_ratio=0.3)
        
        compressed_model, metrics = compressor.compress(sample_model)
        
        assert isinstance(metrics, OptimizationMetrics)
        assert metrics.compression_ratio >= 1.0
        assert metrics.latency_improvement >= 0.0
        assert metrics.memory_savings >= 0.0
        
        # Test decompression
        decompressed_model = compressor.decompress(compressed_model)
        assert decompressed_model is not None
    
    def test_lru_cache(self):
        """Test LRU cache functionality"""
        cache = LRUCache(max_size=3, default_ttl=1.0)
        
        # Test basic operations
        assert cache.get("nonexistent") is None
        
        # Test put and get
        assert cache.put("key1", "value1")
        assert cache.get("key1") == "value1"
        
        # Test TTL expiration
        time.sleep(1.1)
        assert cache.get("key1") is None
        
        # Test LRU eviction
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        cache.put("key3", "value3")
        cache.put("key4", "value4")  # Should evict key1
        
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"
        assert cache.get("key4") == "value4"
        
        # Test statistics
        stats = cache.get_stats()
        assert isinstance(stats, CacheStats)
        assert stats.total_requests > 0
        assert stats.cache_hits > 0
        assert stats.cache_misses > 0
        assert 0.0 <= stats.hit_rate <= 1.0
    
    def test_distributed_cache(self):
        """Test distributed cache functionality"""
        nodes = ["node1", "node2", "node3"]
        cache = DistributedCache(nodes, replication_factor=2)
        
        # Test basic operations
        assert cache.put("key1", "value1")
        assert cache.get("key1") == "value1"
        
        # Test replication
        cluster_stats = cache.get_cluster_stats()
        assert len(cluster_stats) == 3
        for node, stats in cluster_stats.items():
            assert isinstance(stats, CacheStats)
    
    def test_model_optimization(self, default_optimizer, sample_model):
        """Test model optimization"""
        results = default_optimizer.optimize_model("test_model", sample_model)
        
        assert len(results) == 2  # Should have results from both compressors
        
        for compressor_name, metrics in results.items():
            assert isinstance(metrics, OptimizationMetrics)
            assert metrics.compression_ratio >= 1.0
            assert metrics.latency_improvement >= 0.0
        
        # Test getting optimized model
        optimized_model = default_optimizer.get_optimized_model("test_model")
        assert optimized_model is not None
    
    def test_prediction_caching(self, default_optimizer):
        """Test prediction caching"""
        cache_key = "test_prediction"
        prediction = {"agent": "test_agent", "confidence": 0.8}
        
        # Test cache miss
        assert default_optimizer.get_cached_prediction(cache_key) is None
        
        # Test cache put and hit
        default_optimizer.cache_prediction(cache_key, prediction)
        cached_prediction = default_optimizer.get_cached_prediction(cache_key)
        assert cached_prediction == prediction
    
    def test_optimization_report(self, default_optimizer, sample_model):
        """Test optimization report generation"""
        # Optimize a model
        default_optimizer.optimize_model("test_model", sample_model)
        
        # Generate report
        report = default_optimizer.get_optimization_report()
        
        assert "optimization_target" in report
        assert "total_optimizations" in report
        assert "compressed_models" in report
        assert "cache_stats" in report
        assert "compressor_performance" in report
        
        for compressor_name, stats in report["compressor_performance"].items():
            assert "avg_compression_ratio" in stats
            assert "avg_latency_improvement" in stats
            assert "optimizations_count" in stats
    
    def test_concurrent_optimization(self, default_optimizer):
        """Test concurrent model optimization"""
        models = [Mock() for _ in range(5)]
        
        # Mock the compress methods
        for compressor in default_optimizer.compressors:
            compressor.compress = Mock(return_value=(Mock(), OptimizationMetrics(
                original_size=1000000,
                compressed_size=500000,
                compression_ratio=2.0,
                original_latency=10.0,
                optimized_latency=5.0,
                latency_improvement=0.5,
                accuracy_before=0.9,
                accuracy_after=0.88,
                accuracy_degradation=0.02,
                memory_usage_before=100,
                memory_usage_after=50,
                memory_savings=0.5
            )))
        
        # Optimize all models concurrently
        start_time = time.time()
        
        for i, model in enumerate(models):
            default_optimizer.optimize_model(f"model_{i}", model)
        
        end_time = time.time()
        
        # Should complete quickly due to concurrency
        assert end_time - start_time < 5.0  # 5 seconds max
        assert len(default_optimizer.compressed_models) == 10  # 5 models × 2 compressors

class TestIntegration:
    """Integration tests for Phase 3 components"""
    
    def test_moe_meta_learning_integration(self):
        """Test integration between MoE and meta-learning"""
        # Create MoE system
        moe = create_default_moe()
        
        # Create meta-learning framework
        framework = create_default_meta_framework()
        
        # Simulate routing decisions and meta-learning
        queries = [
            "Review my Python code",
            "Write my resume",
            "Analyze sales data"
        ]
        
        for query in queries:
            # Get MoE routing decision
            decision = moe.route(query, {})
            
            # Create task example from decision
            example = TaskExample(
                query=query,
                context={},
                target_agent=decision.selected_agent,
                confidence=decision.confidence,
                success=True
            )
            
            # Add to meta-learning
            task = create_few_shot_task(
                task_id=f"task_{len(framework.adaptation_history)}",
                task_name=f"Task for {query}",
                examples_data=[{
                    "query": example.query,
                    "target_agent": example.target_agent,
                    "confidence": example.confidence
                }]
            )
            
            framework.process_adaptation_request(task)
        
        # Verify both systems have learned
        assert moe.prediction_count == 3
        assert len(framework.adaptation_history) == 3
    
    def test_optimization_caching_integration(self):
        """Test integration between optimization and caching"""
        optimizer = create_default_optimizer()
        
        # Create and optimize a model
        class TestModel:
            def __init__(self):
                self.weights = np.random.randn(50, 25)
        
        model = TestModel()
        optimizer.optimize_model("test_model", model)
        
        # Get optimized model and cache prediction
        optimized_model = optimizer.get_optimized_model("test_model")
        cache_key = "prediction_key"
        prediction = {"agent": "optimized_agent", "confidence": 0.9}
        
        optimizer.cache_prediction(cache_key, prediction)
        
        # Verify both work together
        assert optimized_model is not None
        assert optimizer.get_cached_prediction(cache_key) == prediction
        
        # Check cache stats
        cache_stats = optimizer.cache.get_stats()
        assert cache_stats.cache_hits > 0
    
    def test_full_pipeline_integration(self):
        """Test full pipeline integration"""
        # Create all components
        moe = create_default_moe()
        framework = create_default_meta_framework()
        optimizer = create_default_optimizer()
        
        # Simulate full workflow
        query = "Review my machine learning Python code"
        context = {"user_id": "test_user", "complexity": "high"}
        
        # 1. Get routing decision
        decision = moe.route(query, context)
        
        # 2. Cache the decision
        cache_key = f"routing_{hash(query)}"
        optimizer.cache_prediction(cache_key, {
            "agent": decision.selected_agent,
            "confidence": decision.confidence,
            "expert": decision.selected_expert
        })
        
        # 3. Create learning example
        example = TaskExample(
            query=query,
            context=context,
            target_agent=decision.selected_agent,
            confidence=decision.confidence,
            success=True
        )
        
        # 4. Add to meta-learning
        task = create_few_shot_task(
            task_id="integration_task",
            task_name="Integration Test",
            examples_data=[{
                "query": example.query,
                "target_agent": example.target_agent,
                "confidence": example.confidence
            }]
        )
        
        framework.process_adaptation_request(task)
        
        # 5. Update MoE with outcome
        moe.update_outcome(decision, success=True)
        
        # Verify integration worked
        assert decision.selected_agent is not None
        assert optimizer.get_cached_prediction(cache_key) is not None
        assert len(framework.adaptation_history) == 1
        assert moe.get_success_rate() == 1.0

class TestPerformance:
    """Performance tests for Phase 3 components"""
    
    def test_moe_performance(self):
        """Test MoE performance with many requests"""
        moe = create_default_moe()
        
        queries = [
            "Review my Python code",
            "Write my resume",
            "Analyze sales data",
            "Debug JavaScript function",
            "Create data visualization"
        ] * 20  # 100 total requests
        
        start_time = time.time()
        
        for query in queries:
            decision = moe.route(query, {})
            moe.update_outcome(decision, success=True)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should handle 100 requests efficiently
        assert total_time < 10.0  # 10 seconds max
        assert moe.prediction_count == 100
        assert len(moe.decision_history) == 100
    
    def test_meta_learning_performance(self):
        """Test meta-learning performance with many tasks"""
        framework = create_default_meta_framework()
        
        # Create many tasks
        start_time = time.time()
        
        for i in range(50):
            examples = [
                TaskExample(f"query_{i}_{j}", {}, f"agent_{i % 5}", 0.8, True)
                for j in range(4)
            ]
            
            task = create_few_shot_task(
                task_id=f"task_{i}",
                task_name=f"Task {i}",
                examples_data=[{
                    "query": e.query,
                    "target_agent": e.target_agent,
                    "confidence": e.confidence
                } for e in examples]
            )
            
            framework.process_adaptation_request(task)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should handle 50 tasks efficiently
        assert total_time < 15.0  # 15 seconds max
        assert len(framework.adaptation_history) == 100  # 50 tasks × 2 learners
    
    def test_optimization_performance(self):
        """Test optimization performance with many models"""
        optimizer = create_default_optimizer()
        
        # Create many models
        models = []
        for i in range(20):
            class TestModel:
                def __init__(self, size):
                    self.weights = np.random.randn(size, size // 2)
                    self.bias = np.random.randn(size // 2)
            
            models.append(TestModel(50 + i * 10))  # Increasing model sizes
        
        # Optimize all models
        start_time = time.time()
        
        for i, model in enumerate(models):
            optimizer.optimize_model(f"model_{i}", model)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should handle 20 model optimizations efficiently
        assert total_time < 20.0  # 20 seconds max
        assert len(optimizer.compressed_models) == 40  # 20 models × 2 compressors

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
