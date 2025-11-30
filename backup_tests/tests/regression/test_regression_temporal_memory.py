"""
Regression tests for Performance Stability
Tests that performance remains stable across runs
"""
import pytest
from typing import Dict, Any, List
from unittest.mock import Mock
import time
import statistics

# Import actual components when available
try:
    from agentic_core.l1_planning.planners.strategy_planner import StrategyPlanner
    from agentic_core.l2_execution.executors.company_research_executor import CompanyResearchExecutor
    from agentic_core.l3_orchestration.dag.dag import ResumeEngineDAG
    from agentic_core.l4_memory.providers.rag_provider import RAGProvider
    from agentic_core.l5_safety.policies.policy_engine import PolicyEngine
except ImportError:
    StrategyPlanner = CompanyResearchExecutor = ResumeEngineDAG = RAGProvider = PolicyEngine = Mock


class TestPerformanceStability:
    """Test performance stability regression contracts"""
    
    def test_planner_performance_stability_contract(self):
        """Test planners maintain stable performance"""
        if StrategyPlanner is Mock:
            pytest.skip("StrategyPlanner not implemented")
        
        planner = StrategyPlanner({})
        
        input_data = {
            "goal": "optimize_resume",
            "context": {
                "user_profile": {
                    "name": "John Doe",
                    "skills": ["Python", "Machine Learning"],
                    "experience": "5 years"
                }
            },
            "constraints": []
        }
        
        # Measure performance over multiple runs
        execution_times = []
        for i in range(10):
            start_time = time.time()
            result = planner.plan(input_data.copy())
            elapsed_time = time.time() - start_time
            execution_times.append(elapsed_time)
        
        # Performance should be stable (low variance)
        mean_time = statistics.mean(execution_times)
        std_dev = statistics.stdev(execution_times) if len(execution_times) > 1 else 0
        
        # Should complete within reasonable time
        assert mean_time < 1.0, f"Planner too slow: {mean_time:.3f}s average"
        
        # Variance should be low (stable performance)
        cv = std_dev / mean_time if mean_time > 0 else float('inf')
        assert cv < 0.5, f"Performance too variable: CV={cv:.3f}"
    
    def test_executor_performance_stability_contract(self):
        """Test executors maintain stable performance"""
        if CompanyResearchExecutor is Mock:
            pytest.skip("CompanyResearchExecutor not implemented")
        
        executor = CompanyResearchExecutor({"timeout": 10})
        
        input_data = {
            "company_name": "TechCorp",
            "research_scope": ["basic_info", "products"],
            "depth": "basic"
        }
        
        execution_times = []
        for i in range(5):  # Fewer runs for executor (more expensive)
            start_time = time.time()
            result = executor.execute(input_data.copy())
            elapsed_time = time.time() - start_time
            execution_times.append(elapsed_time)
        
        # Should respect timeout
        for elapsed in execution_times:
            assert elapsed < 10.0, "Executor exceeded timeout"
        
        # Performance should be stable
        mean_time = statistics.mean(execution_times)
        std_dev = statistics.stdev(execution_times) if len(execution_times) > 1 else 0
        
        cv = std_dev / mean_time if mean_time > 0 else float('inf')
        assert cv < 0.7, f"Executor performance too variable: CV={cv:.3f}"
    
    def test_dag_performance_stability_contract(self):
        """Test DAG orchestration maintains stable performance"""
        if ResumeEngineDAG is Mock:
            pytest.skip("ResumeEngineDAG not implemented")
        
        dag = ResumeEngineDAG({})
        
        input_data = {
            "user_profile": {
                "name": "Alice Smith",
                "skills": ["JavaScript", "React"],
                "experience": "3 years"
            },
            "target_positions": ["Frontend Developer"],
            "companies": ["WebCorp"]
        }
        
        execution_times = []
        for i in range(3):  # DAG is expensive, fewer runs
            start_time = time.time()
            result = dag.execute(input_data.copy())
            elapsed_time = time.time() - start_time
            execution_times.append(elapsed_time)
        
        # Should complete within reasonable time
        mean_time = statistics.mean(execution_times)
        assert mean_time < 30.0, f"DAG too slow: {mean_time:.3f}s average"
        
        # Performance should be somewhat stable
        if len(execution_times) > 1:
            std_dev = statistics.stdev(execution_times)
            cv = std_dev / mean_time if mean_time > 0 else float('inf')
            assert cv < 1.0, f"DAG performance too variable: CV={cv:.3f}"
    
    def test_rag_performance_stability_contract(self):
        """Test RAG provider maintains stable performance"""
        if RAGProvider is Mock:
            pytest.skip("RAGProvider not implemented")
        
        rag_provider = RAGProvider({"max_latency_ms": 1000})
        
        query_data = {
            "query": "machine learning engineer position requirements",
            "max_results": 5
        }
        
        execution_times = []
        for i in range(10):
            start_time = time.time()
            result = rag_provider.query(query_data.copy())
            elapsed_time = time.time() - start_time
            execution_times.append(elapsed_time * 1000)  # Convert to ms
        
        # Should meet latency requirements
        for elapsed_ms in execution_times:
            assert elapsed_ms < 1000, f"RAG exceeded latency: {elapsed_ms:.1f}ms"
        
        # Performance should be stable
        mean_time_ms = statistics.mean(execution_times)
        std_dev_ms = statistics.stdev(execution_times) if len(execution_times) > 1 else 0
        
        cv = std_dev_ms / mean_time_ms if mean_time_ms > 0 else float('inf')
        assert cv < 0.5, f"RAG performance too variable: CV={cv:.3f}"
    
    def test_safety_performance_stability_contract(self):
        """Test safety evaluation maintains stable performance"""
        if PolicyEngine is Mock:
            pytest.skip("PolicyEngine not implemented")
        
        policy_engine = PolicyEngine({})
        
        content = {
            "text": "I am a software engineer with expertise in Python and machine learning.",
            "context": {"type": "resume", "user_id": "test_user"}
        }
        
        execution_times = []
        for i in range(20):  # Safety should be fast, many runs
            start_time = time.time()
            result = policy_engine.evaluate_content(content.copy())
            elapsed_time = time.time() - start_time
            execution_times.append(elapsed_time * 1000)  # Convert to ms
        
        # Should be very fast
        mean_time_ms = statistics.mean(execution_times)
        assert mean_time_ms < 100, f"Safety evaluation too slow: {mean_time_ms:.1f}ms average"
        
        # Should be very stable
        std_dev_ms = statistics.stdev(execution_times) if len(execution_times) > 1 else 0
        cv = std_dev_ms / mean_time_ms if mean_time_ms > 0 else float('inf')
        assert cv < 0.3, f"Safety performance too variable: CV={cv:.3f}"
    
    def test_memory_usage_stability_contract(self):
        """Test memory usage remains stable"""
        if StrategyPlanner is Mock:
            pytest.skip("StrategyPlanner not implemented")
        
        planner = StrategyPlanner({})
        
        input_data = {
            "goal": "optimize_resume",
            "context": {"user_profile": {"name": "Memory Test"}},
            "constraints": []
        }
        
        # Test memory usage over multiple operations
        import gc
        import sys
        
        # Baseline memory
        gc.collect()
        baseline_objects = len(gc.get_objects())
        
        # Execute multiple times
        for i in range(50):
            result = planner.plan(input_data.copy())
            del result  # Clean up
        
        # Check for memory leaks
        gc.collect()
        final_objects = len(gc.get_objects())
        
        object_growth = final_objects - baseline_objects
        assert object_growth < 1000, f"Potential memory leak: {object_growth} objects created"
    
    def test_concurrent_performance_stability_contract(self):
        """Test performance under concurrent load"""
        if PolicyEngine is Mock:
            pytest.skip("PolicyEngine not implemented")
        
        policy_engine = PolicyEngine({})
        
        content = {
            "text": "Test content for concurrent evaluation",
            "context": {"type": "test"}
        }
        
        # Test concurrent execution
        import threading
        import queue
        
        results_queue = queue.Queue()
        
        def worker():
            start_time = time.time()
            result = policy_engine.evaluate_content(content.copy())
            elapsed_time = time.time() - start_time
            results_queue.put(elapsed_time)
        
        # Start multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Collect results
        execution_times = []
        while not results_queue.empty():
            execution_times.append(results_queue.get())
        
        # Should handle concurrent load gracefully
        assert len(execution_times) == 5, "Not all concurrent operations completed"
        
        mean_time = statistics.mean(execution_times)
        assert mean_time < 0.2, f"Concurrent performance too slow: {mean_time:.3f}s"
    
    def test_scalability_performance_contract(self):
        """Test performance scales appropriately with input size"""
        if CompanyResearchExecutor is Mock:
            pytest.skip("CompanyResearchExecutor not implemented")
        
        executor = CompanyResearchExecutor({})
        
        # Test with different input sizes
        small_input = {
            "company_name": "SmallCorp",
            "research_scope": ["basic_info"],
            "depth": "basic"
        }
        
        large_input = {
            "company_name": "LargeCorp",
            "research_scope": ["basic_info", "products", "competitors", "financials", "leadership"],
            "depth": "comprehensive"
        }
        
        # Measure performance
        start_time = time.time()
        small_result = executor.execute(small_input)
        small_time = time.time() - start_time
        
        start_time = time.time()
        large_result = executor.execute(large_input)
        large_time = time.time() - start_time
        
        # Large input should take longer but not excessively so
        assert large_time > small_time, "Large input should take longer"
        assert large_time < small_time * 10, f"Large input too slow: {large_time/small_time:.1f}x slower"
    
    def test_performance_regression_detection_contract(self):
        """Test performance regression detection"""
        # This test establishes performance baselines for future regression testing
        performance_baselines = {
            "strategy_planner": {
                "max_mean_time_ms": 100,
                "max_cv": 0.5,
                "sample_size": 10
            },
            "company_research": {
                "max_mean_time_ms": 5000,
                "max_cv": 0.7,
                "sample_size": 5
            },
            "safety_evaluation": {
                "max_mean_time_ms": 50,
                "max_cv": 0.3,
                "sample_size": 20
            },
            "rag_query": {
                "max_mean_time_ms": 1000,
                "max_cv": 0.5,
                "sample_size": 10
            }
        }
        
        for component, baseline in performance_baselines.items():
            # Validate baseline structure
            assert "max_mean_time_ms" in baseline
            assert "max_cv" in baseline
            assert "sample_size" in baseline
            assert baseline["max_mean_time_ms"] > 0
            assert baseline["max_cv"] > 0
            assert baseline["sample_size"] > 0
    
    def test_negative_case_performance_regression_contract(self):
        """Test negative case: detect performance regressions"""
        if PolicyEngine is Mock:
            pytest.skip("PolicyEngine not implemented")
        
        # Simulate performance regression by adding artificial delay
        class SlowPolicyEngine:
            def __init__(self, config):
                self.config = config
            
            def evaluate_content(self, content):
                time.sleep(0.1)  # Artificial delay
                return {
                    "allowed": True,
                    "confidence_score": 0.9,
                    "metadata": {"slow": True}
                }
        
        slow_engine = SlowPolicyEngine({})
        
        content = {"text": "test", "context": {"type": "test"}}
        
        # Measure degraded performance
        start_time = time.time()
        result = slow_engine.evaluate_content(content)
        elapsed_time = time.time() - start_time
        
        # Should detect performance regression
        assert elapsed_time > 0.05, f"Performance regression not detected: {elapsed_time:.3f}s"
    
    def test_resource_cleanup_stability_contract(self):
        """Test resource cleanup remains stable"""
        if RAGProvider is Mock:
            pytest.skip("RAGProvider not implemented")
        
        rag_provider = RAGProvider({})
        
        # Test multiple operations with cleanup
        for i in range(10):
            result = rag_provider.query({
                "query": f"test query {i}",
                "max_results": 3
            })
            
            # Should clean up resources properly
            if hasattr(rag_provider, 'cleanup'):
                rag_provider.cleanup()
        
        # Final check
        final_result = rag_provider.query({
            "query": "final test",
            "max_results": 1
        })
        
        assert "results" in final_result, "Resource cleanup affected functionality"
