"""Concurrency safety tests for GraphMemoryBridge.

Tests thread safety and race conditions in concurrent access scenarios.
"""

from __future__ import annotations

import pytest

# Check if GraphMemoryBridge is available
try:
    from agentic_core.L4_state.enforcement.graph_memory_bridge import GraphMemoryBridge

    GRAPH_MEMORY_AVAILABLE = True
except ImportError:
    GRAPH_MEMORY_AVAILABLE = False

import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


@pytest.mark.skipif(not GRAPH_MEMORY_AVAILABLE, reason="GraphMemoryBridge not available")
class TestGraphMemoryBridgeConcurrency:
    """Test thread safety of GraphMemoryBridge operations."""

    def test_concurrent_entity_creation(self):
        """Test concurrent entity creation doesn't cause race conditions."""
        bridge = GraphMemoryBridge()
        created_entities = []
        errors = []

        def create_entity(entity_id):
            try:
                entity_name = f"concurrent_entity_{entity_id}"
                success = bridge.create_agent_entity(entity_name, "test_type")
                created_entities.append((entity_id, success))
            except Exception as e:
                errors.append((entity_id, str(e)))

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(create_entity, i) for i in range(50)]
            for future in as_completed(futures):
                future.result()
        assert len(errors) == 0, f"Errors in concurrent execution: {errors}"
        assert len(created_entities) == 50
        assert all((success for _, success in created_entities))
        assert len(bridge._registered_entities) == 50

    def test_concurrent_relation_creation(self):
        """Test concurrent relation creation maintains consistency."""
        bridge = GraphMemoryBridge()
        for i in range(10):
            bridge.create_agent_entity(f"entity_{i}", "test_type")
        created_relations = []
        errors = []

        def create_relation(relation_id):
            try:
                from_entity = f"entity_{relation_id % 10}"
                to_entity = f"entity_{(relation_id + 1) % 10}"
                relation_type = f"relation_{relation_id}"
                success = bridge.create_relation(from_entity, to_entity, relation_type)
                created_relations.append((relation_id, success))
            except Exception as e:
                errors.append((relation_id, str(e)))

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(create_relation, i) for i in range(100)]
            for future in as_completed(futures):
                future.result()
        assert len(errors) == 0, f"Errors in concurrent relation creation: {errors}"
        assert bridge.stats["relations_created"] >= 90

    def test_concurrent_observation_addition(self):
        """Test concurrent observation addition maintains data integrity."""
        bridge = GraphMemoryBridge()
        bridge.create_agent_entity("test_entity", "test_type")
        observations = []
        errors = []

        def add_observation(obs_id):
            try:
                entity_name = "test_entity"
                observation = f"Observation {obs_id} at {time.time()}"
                success = bridge.add_observation(entity_name, observation)
                observations.append((obs_id, success))
            except Exception as e:
                errors.append((obs_id, str(e)))

        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(add_observation, i) for i in range(200)]
            for future in as_completed(futures):
                future.result()
        assert len(errors) == 0, f"Errors in concurrent observation addition: {errors}"
        successful_obs = [obs_id for obs_id, success in observations if success]
        assert len(successful_obs) >= 190

    def test_concurrent_state_isolation(self):
        """Test that multiple bridge instances don't interfere with each other."""
        results = {}

        def create_entities_in_instance(instance_id):
            bridge = GraphMemoryBridge()
            entity_count = 0
            try:
                for i in range(10):
                    entity_name = f"instance_{instance_id}_entity_{i}"
                    if bridge.create_agent_entity(entity_name, "test_type"):
                        entity_count += 1
                results[instance_id] = {
                    "entity_count": entity_count,
                    "stats": bridge.stats.copy(),
                    "registered_count": len(bridge._registered_entities),
                    "validation": bridge.validate_state_isolation(),
                }
            except Exception as e:
                results[instance_id] = {"error": str(e)}

        threads = []
        for instance_id in range(5):
            thread = threading.Thread(target=create_entities_in_instance, args=(instance_id,))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()
        for instance_id, result in results.items():
            assert "error" not in result, f"Instance {instance_id} failed: {result.get('error')}"
            assert result["entity_count"] == 10
            assert result["stats"]["entities_created"] == 10
            assert result["registered_count"] == 10

    def test_concurrent_cleanup_operations(self):
        """Test concurrent cleanup operations don't cause corruption."""
        bridges = [GraphMemoryBridge() for _ in range(10)]
        cleanup_results = []

        def create_and_cleanup(bridge_id):
            bridge = bridges[bridge_id]
            for i in range(5):
                bridge.create_agent_entity(f"cleanup_entity_{bridge_id}_{i}", "test_type")
            pre_cleanup = bridge.validate_state_isolation()
            assert not pre_cleanup["is_clean"]
            bridge.cleanup()
            post_cleanup = bridge.validate_state_isolation()
            cleanup_results.append(
                {
                    "bridge_id": bridge_id,
                    "pre_clean_entities": pre_cleanup["registered_entities_count"],
                    "post_clean_entities": post_cleanup["registered_entities_count"],
                    "is_clean_after": post_cleanup["is_clean"],
                }
            )

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(create_and_cleanup, i) for i in range(10)]
            for future in as_completed(futures):
                future.result()
        for result in cleanup_results:
            assert result["pre_clean_entities"] == 5
            assert result["post_clean_entities"] == 0
            assert result["is_clean_after"] is True

    def test_context_manager_isolation(self):
        """Test that context manager provides proper isolation."""
        context_results = []

        def use_context_manager(instance_id):
            try:
                with GraphMemoryBridge() as bridge:
                    for i in range(3):
                        entity_name = f"context_entity_{instance_id}_{i}"
                        bridge.create_agent_entity(entity_name, "test_type")
                    validation = bridge.validate_state_isolation()
                    assert not validation["is_clean"]
                    assert validation["registered_entities_count"] == 3
                    context_results.append(
                        {
                            "instance_id": instance_id,
                            "entities_created": validation["registered_entities_count"],
                            "stats": bridge.stats.copy(),
                        }
                    )
                final_validation = bridge.validate_state_isolation()
                assert final_validation["is_clean"]
            except Exception as e:
                context_results.append({"instance_id": instance_id, "error": str(e)})

        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(use_context_manager, i) for i in range(6)]
            for future in as_completed(futures):
                future.result()
        for result in context_results:
            assert "error" not in result
            assert result["entities_created"] == 3
            assert result["stats"]["entities_created"] == 3

    def test_high_load_stress_test(self):
        """Stress test with high concurrent load."""
        bridge = GraphMemoryBridge()
        operation_count = 1000
        errors = []
        successful_ops = 0

        def perform_operations(op_id):
            nonlocal successful_ops
            try:
                if op_id % 3 == 0:
                    entity_name = f"stress_entity_{op_id}"
                    success = bridge.create_agent_entity(entity_name, "test_type")
                    if success:
                        successful_ops += 1
                elif op_id % 3 == 1:
                    if op_id > 10:
                        from_entity = f"stress_entity_{op_id - 10}"
                        to_entity = f"stress_entity_{op_id - 5}"
                        bridge.create_relation(from_entity, to_entity, "stress_relation")
                        successful_ops += 1
                elif op_id > 5:
                    entity_name = f"stress_entity_{op_id - 5}"
                    observation = f"Stress observation {op_id}"
                    success = bridge.add_observation(entity_name, observation)
                    if success:
                        successful_ops += 1
            except Exception as e:
                errors.append((op_id, str(e)))

        start_time = time.time()
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(perform_operations, i) for i in range(operation_count)]
            for future in as_completed(futures):
                future.result()
        end_time = time.time()
        assert len(errors) < operation_count * 0.01, f"Too many errors: {len(errors)}/{operation_count}"
        assert successful_ops > operation_count * 0.8, (
            f"Too few successful operations: {successful_ops}/{operation_count}"
        )
        duration = end_time - start_time
        assert duration < 30.0, f"Stress test took too long: {duration:.2f}s"
        final_validation = bridge.validate_state_isolation()
        assert final_validation["registered_entities_count"] > 0
        assert final_validation["stats_totals"] > 0
