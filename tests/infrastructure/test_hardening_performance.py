"""Infrastructure Hardening Performance & Stress Tests

Comprehensive performance validation and stress testing for all five infrastructure hardening opportunities.
"""

import asyncio
import time
import unittest
from datetime import datetime

from infrastructure.hardening.adaptive_optimizer import AdaptiveOptimizer
from infrastructure.hardening.cross_layer_coherence import CrossLayerCoherenceManager
from infrastructure.hardening.distributed_state_manager import DistributedStateManager
from infrastructure.hardening.implementation_plan import LayerType, QueryRequest, QueryStatus
from infrastructure.hardening.security_framework import (
    DataClassification,
    SecurityContext,
    SecurityGateway,
)
from infrastructure.hardening.unified_query_router import UnifiedQueryRouter


class TestInfrastructurePerformance(unittest.TestCase):
    """Performance tests for infrastructure components."""

    def setUp(self):
        self.router = UnifiedQueryRouter()
        self.coherence_manager = CrossLayerCoherenceManager()
        self.optimizer = AdaptiveOptimizer()
        self.state_manager = DistributedStateManager()
        self.security_gateway = SecurityGateway()

    def test_query_router_performance(self):
        """Test query router performance under load."""
        # Setup multiple instances
        self.router.add_layer_instances(
            LayerType.REDIS_EXACT_MATCH, [(f"redis_{i}", f"redis://localhost:637{i}", 1) for i in range(1, 6)]
        )

        self.router.add_layer_instances(
            LayerType.SEMANTIC_CACHE, [(f"semantic_{i}", f"http://localhost:800{i}", 1) for i in range(1, 6)]
        )

        # Performance test
        query_count = 100
        start_time = time.time()

        async def run_queries():
            tasks = []
            for i in range(query_count):
                request = QueryRequest(
                    query_id=f"perf_test_{i}",
                    user_query=f"Performance test query {i}",
                    timestamp=datetime.now(),
                    priority=1,
                )

                task = self.router.route_query(
                    request, [LayerType.REDIS_EXACT_MATCH, LayerType.SEMANTIC_CACHE]
                )
                tasks.append(task)

            results = await asyncio.gather(*tasks)
            return results

        results = asyncio.run(run_queries())
        end_time = time.time()

        # Performance metrics
        total_time = end_time - start_time
        queries_per_second = query_count / total_time
        success_rate = sum(
            1 for result_group in results for result in result_group if result.status == QueryStatus.COMPLETED
        ) / (query_count * 2)

        # Assertions
        self.assertGreater(queries_per_second, 50)  # At least 50 QPS
        self.assertGreater(success_rate, 0.9)  # At least 90% success rate
        self.assertLess(total_time, 5.0)  # Complete within 5 seconds

        print(f"Query Router Performance: {queries_per_second:.2f} QPS, {success_rate:.2%} success rate")

    def test_cache_coherence_performance(self):
        """Test cache coherence performance."""
        entry_count = 1000
        batch_size = 100

        # Performance test for cache operations
        start_time = time.time()

        # Add entries in batches
        for batch_start in range(0, entry_count, batch_size):
            batch_end = min(batch_start + batch_size, entry_count)

            async def add_batch():
                tasks = []
                for i in range(batch_start, batch_end):
                    task = self.coherence_manager.add_cache_entry(
                        LayerType.REDIS_EXACT_MATCH,
                        f"perf_key_{i}",
                        {"data": f"performance_data_{i}", "index": i},
                        f"v1.{i % 10}.0",
                        3600,
                    )
                    tasks.append(task)

                return await asyncio.gather(*tasks)

            asyncio.run(add_batch())

        add_time = time.time() - start_time

        # Test retrieval performance
        start_time = time.time()

        async def retrieve_all():
            tasks = []
            for i in range(entry_count):
                task = self.coherence_manager.get_cache_entry(LayerType.REDIS_EXACT_MATCH, f"perf_key_{i}")
                tasks.append(task)

            return await asyncio.gather(*tasks)

        entries = asyncio.run(retrieve_all())
        retrieve_time = time.time() - start_time

        # Performance metrics
        add_ops_per_second = entry_count / add_time
        retrieve_ops_per_second = entry_count / retrieve_time
        hit_rate = sum(1 for entry in entries if entry is not None) / entry_count

        # Assertions
        self.assertGreater(add_ops_per_second, 100)  # At least 100 ops/sec for adds
        self.assertGreater(retrieve_ops_per_second, 200)  # At least 200 ops/sec for retrieves
        self.assertEqual(hit_rate, 1.0)  # All entries should be found

        print(
            f"Cache Coherence Performance: {add_ops_per_second:.2f} adds/sec, {retrieve_ops_per_second:.2f} retrieves/sec"
        )

    def test_optimizer_performance(self):
        """Test adaptive optimizer performance."""
        # Add performance data
        data_points = 500

        start_time = time.time()

        for i in range(data_points):
            from infrastructure.hardening.adaptive_optimizer import LayerResponse

            response = LayerResponse(
                layer_type=LayerType.REDIS_EXACT_MATCH,
                status=QueryStatus.COMPLETED,
                data=f"test_response_{i}",
                processing_time_ms=50 + (i % 100),
                cost_estimate=0.001 + (i % 10) * 0.0001,
                cache_hit=i % 2 == 0,
            )

            asyncio.run(self.optimizer.add_performance_data(LayerType.REDIS_EXACT_MATCH, response))

        data_add_time = time.time() - start_time

        # Test optimization cycle
        start_time = time.time()

        asyncio.run(self.optimizer._train_models())

        training_time = time.time() - start_time

        # Performance metrics
        data_points_per_second = data_points / data_add_time

        # Assertions
        self.assertGreater(data_points_per_second, 100)  # At least 100 data points/sec
        self.assertLess(training_time, 2.0)  # Training should complete within 2 seconds

        # Verify optimization status
        status = self.optimizer.get_optimization_status()
        self.assertIsNotNone(status)

        print(
            f"Optimizer Performance: {data_points_per_second:.2f} data points/sec, training: {training_time:.3f}s"
        )

    def test_state_management_performance(self):
        """Test distributed state management performance."""
        state_count = 100

        start_time = time.time()

        # Store multiple states
        async def store_states():
            tasks = []
            for i in range(state_count):
                state_data = {
                    "state_id": i,
                    "data": f"state_data_{i}",
                    "timestamp": datetime.now().isoformat(),
                }

                task = self.state_manager.store_layer_state(LayerType.RAG_RETRIEVAL, state_data)
                tasks.append(task)

            return await asyncio.gather(*tasks)

        snapshot_ids = asyncio.run(store_states())
        store_time = time.time() - start_time

        # Retrieve states
        start_time = time.time()

        async def retrieve_states():
            tasks = []
            for snapshot_id in snapshot_ids:
                task = self.state_manager.retrieve_layer_state(LayerType.RAG_RETRIEVAL, snapshot_id)
                tasks.append(task)

            return await asyncio.gather(*tasks)

        retrieved_states = asyncio.run(retrieve_states())
        retrieve_time = time.time() - start_time

        # Performance metrics
        store_ops_per_second = state_count / max(store_time, 0.001)  # Prevent division by zero
        retrieve_ops_per_second = state_count / max(retrieve_time, 0.001)  # Prevent division by zero
        success_rate = sum(1 for state in retrieved_states if state is not None) / state_count

        # Assertions
        self.assertGreater(store_ops_per_second, 50)  # At least 50 stores/sec
        self.assertGreater(retrieve_ops_per_second, 100)  # At least 100 retrieves/sec
        self.assertEqual(success_rate, 1.0)  # All states should be retrieved

        print(
            f"State Management Performance: {store_ops_per_second:.2f} stores/sec, {retrieve_ops_per_second:.2f} retrieves/sec"
        )

    def test_security_performance(self):
        """Test security framework performance."""
        operation_count = 500

        # Setup users
        for i in range(10):
            self.security_gateway.access_controller.assign_user_role(f"user_{i}", "user")

        start_time = time.time()

        # Test authentication performance
        async def test_auth():
            tasks = []
            for i in range(operation_count):
                user_id = f"user_{i % 10}"
                security_context = SecurityContext(
                    user_id=user_id,
                    roles=["user"],
                    data_classification=self.security_gateway.data_classifier.classify_text(f"Test data {i}"),
                    compliance_requirements=[],
                    access_permissions={"ip_address": "127.0.0.1", "user_agent": "perf_test"},
                )

                request = QueryRequest(
                    query_id=f"auth_test_{i}",
                    user_query=f"Authentication test {i}",
                    timestamp=datetime.now(),
                    priority=1,
                )

                task = self.security_gateway.authenticate_request(request, security_context)
                tasks.append(task)

            return await asyncio.gather(*tasks)

        auth_results = asyncio.run(test_auth())
        auth_time = time.time() - start_time

        # Test data filtering performance
        start_time = time.time()

        async def test_filtering():
            tasks = []
            for i in range(operation_count):
                test_data = {
                    "message": f"Test message {i}",
                    "email": f"user{i}@example.com" if i % 10 == 0 else "public_data",
                    "index": i,
                }

                security_context = SecurityContext(
                    user_id=f"user_{i % 10}",
                    roles=["user"],
                    data_classification=DataClassification.INTERNAL,
                    compliance_requirements=[],
                    access_permissions={"ip_address": "127.0.0.1", "user_agent": "perf_test"},
                )

                task = self.security_gateway.filter_response_data(
                    LayerType.REDIS_EXACT_MATCH, test_data, security_context
                )
                tasks.append(task)

            return await asyncio.gather(*tasks)

        filtered_results = asyncio.run(test_filtering())
        filtering_time = time.time() - start_time

        # Performance metrics
        auth_ops_per_second = operation_count / auth_time
        filtering_ops_per_second = operation_count / filtering_time
        auth_success_rate = sum(auth_results) / len(auth_results)

        # Assertions
        self.assertGreater(auth_ops_per_second, 100)  # At least 100 auth ops/sec
        self.assertGreater(filtering_ops_per_second, 200)  # At least 200 filtering ops/sec
        self.assertGreater(auth_success_rate, 0.9)  # At least 90% auth success

        # Verify data masking worked
        masked_count = sum(
            1 for result in filtered_results if isinstance(result, dict) and "***" in str(result)
        )
        self.assertGreater(masked_count, operation_count // 20)  # At least 5% should be masked

        print(
            f"Security Performance: {auth_ops_per_second:.2f} auth/sec, {filtering_ops_per_second:.2f} filtering/sec"
        )


class TestInfrastructureStress(unittest.TestCase):
    """Stress tests for infrastructure components."""

    def setUp(self):
        self.router = UnifiedQueryRouter()
        self.coherence_manager = CrossLayerCoherenceManager()
        self.optimizer = AdaptiveOptimizer()
        self.state_manager = DistributedStateManager()
        self.security_gateway = SecurityGateway()

    def test_high_concurrency_queries(self):
        """Test system under high query concurrency."""
        # Setup router with multiple instances
        self.router.add_layer_instances(
            LayerType.REDIS_EXACT_MATCH,
            [(f"redis_{i}", f"redis://localhost:637{i}", 1) for i in range(1, 11)],
        )

        # High concurrency test
        concurrent_queries = 1000
        batch_size = 50

        start_time = time.time()

        async def run_concurrent_queries():
            all_results = []

            for batch_start in range(0, concurrent_queries, batch_size):
                batch_end = min(batch_start + batch_size, concurrent_queries)

                tasks = []
                for i in range(batch_start, batch_end):
                    request = QueryRequest(
                        query_id=f"stress_test_{i}",
                        user_query=f"Stress test query {i}",
                        timestamp=datetime.now(),
                        priority=1,
                    )

                    task = self.router.route_query(request, [LayerType.REDIS_EXACT_MATCH])
                    tasks.append(task)

                batch_results = await asyncio.gather(*tasks)
                all_results.extend(batch_results)

            return all_results

        results = asyncio.run(run_concurrent_queries())
        end_time = time.time()

        # Stress test metrics
        total_time = end_time - start_time
        queries_per_second = concurrent_queries / total_time
        success_rate = sum(1 for result in results if result[0].status == QueryStatus.COMPLETED) / len(
            results
        )

        # Assertions
        self.assertGreater(queries_per_second, 100)  # At least 100 QPS under stress
        self.assertGreater(
            success_rate, 0.1
        )  # At least 10% success rate under extreme stress (circuit breaker will activate)
        self.assertLess(total_time, 15.0)  # Complete within 15 seconds

        print(f"High Concurrency Test: {queries_per_second:.2f} QPS, {success_rate:.2%} success rate")

    def test_memory_usage_stress(self):
        """Test memory usage under high load."""
        import sys

        # Get initial memory usage
        initial_memory = sys.getsizeof(self.coherence_manager.layer_caches)

        # Add large cache entries
        large_entry_count = 100
        large_data_size = 10000  # 10KB per entry

        start_time = time.time()

        for i in range(large_entry_count):
            large_data = "x" * large_data_size
            asyncio.run(
                self.coherence_manager.add_cache_entry(
                    LayerType.SEMANTIC_CACHE,
                    f"memory_stress_key_{i}",
                    {"large_data": large_data, "index": i, "metadata": f"metadata_{i}" * 100},
                    f"v1.{i}.0",
                    3600,
                )
            )

        add_time = time.time() - start_time

        # Check memory usage
        final_memory = sys.getsizeof(self.coherence_manager.layer_caches)
        memory_increase = final_memory - initial_memory

        # Test retrieval under memory pressure
        start_time = time.time()

        async def retrieve_under_pressure():
            tasks = []
            for i in range(large_entry_count):
                task = self.coherence_manager.get_cache_entry(
                    LayerType.SEMANTIC_CACHE, f"memory_stress_key_{i}"
                )
                tasks.append(task)

            return await asyncio.gather(*tasks)

        entries = asyncio.run(retrieve_under_pressure())
        retrieve_time = time.time() - start_time

        # Stress test metrics
        add_ops_per_second = large_entry_count / add_time
        retrieve_ops_per_second = large_entry_count / max(retrieve_time, 0.001)  # Prevent division by zero
        hit_rate = sum(1 for entry in entries if entry is not None) / large_entry_count

        # Assertions
        self.assertGreater(add_ops_per_second, 20)  # At least 20 ops/sec with large data
        self.assertGreater(retrieve_ops_per_second, 50)  # At least 50 retrieves/sec
        self.assertEqual(hit_rate, 1.0)  # All entries should be found

        # Memory should be reasonable (allow 3x overhead)
        expected_memory = large_data_size * large_entry_count * 2  # Approximate
        self.assertLess(memory_increase, expected_memory * 3)

        print(
            f"Memory Stress Test: {add_ops_per_second:.2f} adds/sec, {retrieve_ops_per_second:.2f} retrieves/sec"
        )
        print(f"Memory increase: {memory_increase / 1024:.2f}KB for {large_entry_count} large entries")

    def test_circuit_breaker_stress(self):
        """Test circuit breaker under failure conditions."""
        # Setup router
        self.router.add_layer_instances(
            LayerType.RAG_RETRIEVAL, [(f"rag_{i}", f"http://localhost:800{i}", 1) for i in range(1, 6)]
        )

        circuit_breaker = self.router.circuit_breakers[LayerType.RAG_RETRIEVAL]

        # Stress test with failures
        failure_count = 0
        stress_operations = 100

        start_time = time.time()

        for i in range(stress_operations):
            try:
                asyncio.run(
                    circuit_breaker.call(lambda: (_ for _ in ()).throw(Exception(f"Stress failure {i}")))
                )
            except Exception:
                failure_count += 1

        stress_time = time.time() - start_time

        # Circuit should be open
        self.assertEqual(circuit_breaker.state.value, "open")

        # Test fail-fast behavior
        start_time = time.time()

        fail_fast_count = 0
        for i in range(20):
            try:
                asyncio.run(circuit_breaker.call(lambda: "test"))
            except Exception:
                fail_fast_count += 1

        fail_fast_time = time.time() - start_time

        # Assertions
        self.assertEqual(fail_fast_count, 20)  # All should fail fast
        self.assertLess(fail_fast_time, 1.0)  # Should complete quickly
        self.assertGreater(failure_count, circuit_breaker.config.failure_threshold)

        print(f"Circuit Breaker Stress: {failure_count} failures in {stress_time:.3f}s")
        print(f"Fail-fast: {fail_fast_count} operations in {fail_fast_time:.3f}s")

    def test_security_under_load(self):
        """Test security framework under high load."""
        # Setup many users
        user_count = 100
        for i in range(user_count):
            self.security_gateway.access_controller.assign_user_role(f"load_user_{i}", "user")

        # High load security test
        security_operations = 1000

        start_time = time.time()

        async def security_load_test():
            tasks = []
            for i in range(security_operations):
                user_id = f"load_user_{i % user_count}"
                security_context = SecurityContext(
                    user_id=user_id,
                    roles=["user"],
                    data_classification=DataClassification.INTERNAL,
                    compliance_requirements=[],
                    access_permissions={"ip_address": "127.0.0.1", "user_agent": "load_test"},
                )

                request = QueryRequest(
                    query_id=f"load_test_{i}",
                    user_query=f"Security load test {i}",
                    timestamp=datetime.now(),
                    priority=1,
                )

                task = self.security_gateway.authenticate_request(request, security_context)
                tasks.append(task)

            return await asyncio.gather(*tasks)

        auth_results = asyncio.run(security_load_test())
        load_time = time.time() - start_time

        # Load test metrics
        ops_per_second = security_operations / load_time
        success_rate = sum(auth_results) / len(auth_results)

        # Assertions
        self.assertGreater(ops_per_second, 200)  # At least 200 security ops/sec
        self.assertGreater(success_rate, 0.9)  # At least 90% success rate

        # Verify audit log performance
        audit_summary = self.security_gateway.audit_logger.get_audit_summary()
        self.assertEqual(audit_summary["total_entries"], security_operations)

        print(f"Security Load Test: {ops_per_second:.2f} ops/sec, {success_rate:.2%} success rate")
        print(f"Audit entries: {audit_summary['total_entries']}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
