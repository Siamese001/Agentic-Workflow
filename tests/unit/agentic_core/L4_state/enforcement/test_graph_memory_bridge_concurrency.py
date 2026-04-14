"""Concurrency safety tests for GraphMemoryBridge.

Tests thread safety and race conditions in concurrent access scenarios.
"""

from __future__ import annotations

import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import pytest

try:
    from agentic_core.L4_state.enforcement.graph_memory_bridge import GraphMemoryBridge
except ImportError:
    pytest.skip("GraphMemoryBridge not available", allow_module_level=True)


class TestGraphMemoryBridgeConcurrency:
    """Test thread safety of GraphMemoryBridge operations."""

    def test_concurrent_entity_creation(self) -> None:
        bridge = GraphMemoryBridge()
        created_entities = []
        errors = []

        def create_entity(entity_id: int) -> None:
            try:
                entity_name = f"concurrent_entity_{entity_id}"
                success = bridge.create_agent_entity(entity_name, "test_type")
                created_entities.append((entity_id, success))
            except Exception as exc:  # pragma: no cover - depends on runtime implementation
                errors.append((entity_id, str(exc)))

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(create_entity, i) for i in range(50)]
            for future in as_completed(futures):
                future.result()
        assert len(errors) == 0, f"Errors in concurrent execution: {errors}"
        assert len(created_entities) == 50
        assert all(success for _, success in created_entities)
        assert len(bridge._registered_entities) == 50

    def test_concurrent_relation_creation(self) -> None:
        bridge = GraphMemoryBridge()
        for i in range(10):
            bridge.create_agent_entity(f"entity_{i}", "test_type")
        created_relations = []
        errors = []

        def create_relation(relation_id: int) -> None:
            try:
                from_entity = f"entity_{relation_id % 10}"
                to_entity = f"entity_{(relation_id + 1) % 10}"
                relation_type = f"relation_{relation_id}"
                success = bridge.create_relation(from_entity, to_entity, relation_type)
                created_relations.append((relation_id, success))
            except Exception as exc:  # pragma: no cover - depends on runtime implementation
                errors.append((relation_id, str(exc)))

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(create_relation, i) for i in range(100)]
            for future in as_completed(futures):
                future.result()
        assert len(errors) == 0, f"Errors in concurrent relation creation: {errors}"
        assert bridge.stats["relations_created"] == 100
        assert len(created_relations) == 100

    def test_concurrent_cleanup_safety(self) -> None:
        bridge = GraphMemoryBridge()
        for i in range(20):
            bridge.create_agent_entity(f"cleanup_entity_{i}", "test_type")
        cleanup_results = []

        def cleanup_bridge() -> None:
            try:
                bridge.cleanup()
                cleanup_results.append(True)
            except Exception:
                cleanup_results.append(False)

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(cleanup_bridge) for _ in range(5)]
            for future in as_completed(futures):
                future.result()
        assert all(cleanup_results)
        assert len(bridge._registered_entities) == 0

    def test_thread_local_isolation(self) -> None:
        results = {}
        errors = []

        def worker(thread_id: int) -> None:
            try:
                bridge = GraphMemoryBridge.create_isolated()
                entity_name = f"thread_entity_{thread_id}"
                bridge.create_agent_entity(entity_name, "thread_type")
                validation = bridge.validate_state_isolation()
                results[thread_id] = {
                    "entity_count": validation["registered_entities_count"],
                    "stats": bridge.stats.copy(),
                }
                bridge.cleanup()
            except Exception as exc:  # pragma: no cover - depends on runtime implementation
                errors.append((thread_id, str(exc)))

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        assert len(errors) == 0, f"Thread isolation errors: {errors}"
        assert len(results) == 10
        for thread_id, result in results.items():
            assert result["entity_count"] == 1
            assert result["stats"]["entities_created"] == 1

    def test_race_condition_prevention(self) -> None:
        bridge = GraphMemoryBridge()
        shared_counter = 0
        counter_lock = threading.Lock()
        errors = []

        def mixed_operations(op_id: int) -> None:
            nonlocal shared_counter
            try:
                with counter_lock:
                    entity_id = shared_counter
                    shared_counter += 1
                entity_name = f"race_entity_{entity_id}"
                bridge.create_agent_entity(entity_name, "race_type")
                if entity_id > 0:
                    prev_entity = f"race_entity_{entity_id - 1}"
                    bridge.create_relation(prev_entity, entity_name, "follows")
                time.sleep(0.001)
            except Exception as exc:  # pragma: no cover - depends on runtime implementation
                errors.append((op_id, str(exc)))

        with ThreadPoolExecutor(max_workers=15) as executor:
            futures = [executor.submit(mixed_operations, i) for i in range(30)]
            for future in as_completed(futures):
                future.result()
        assert len(errors) == 0, f"Race condition errors: {errors}"
        assert len(bridge._registered_entities) == 30

    def test_context_manager_thread_safety(self) -> None:
        context_results = []

        def use_context_manager(instance_id: int) -> None:
            try:
                with GraphMemoryBridge() as bridge:
                    for i in range(3):
                        bridge.create_agent_entity(f"ctx_{instance_id}_{i}", "context_type")
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
            except Exception as exc:  # pragma: no cover - depends on runtime implementation
                context_results.append({"instance_id": instance_id, "error": str(exc)})

        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(use_context_manager, i) for i in range(6)]
            for future in as_completed(futures):
                future.result()
        for result in context_results:
            assert "error" not in result
            assert result["entities_created"] == 3
            assert result["stats"]["entities_created"] == 3

    def test_high_load_stress_test(self) -> None:
        bridge = GraphMemoryBridge()
        operation_count = 1000
        errors = []
        successful_ops = 0

        def perform_operations(op_id: int) -> None:
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
                    if entity_name in bridge._registered_entities:
                        successful_ops += 1
            except Exception as exc:  # pragma: no cover - depends on runtime implementation
                errors.append((op_id, str(exc)))

        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(perform_operations, i) for i in range(operation_count)]
            for future in as_completed(futures):
                future.result()
        assert len(errors) == 0, f"Stress test errors: {errors[:10]}"
        assert successful_ops > operation_count * 0.8
