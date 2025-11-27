"""
Phase 8 Telemetry Thread Safety Stress Tests

Tests telemetry system under extreme thread safety stress:
- High-contention multi-threaded access
- Lock contention and deadlock prevention
- Memory consistency across threads
- Singleton pattern thread safety
- Concurrent configuration changes
- Thread-safe event filtering and retrieval
"""

import threading
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any

from runtime.telemetry_bus import (
    TelemetryBus,
    get_telemetry_bus
)

class TestTelemetryThreadSafety:
    """Test suite for telemetry thread safety under stress conditions."""
    
    def setup_method(self):
        """Setup fresh telemetry bus for each test."""
        # Clear singleton to ensure clean state
        TelemetryBus._instance = None
        self.bus = get_telemetry_bus()
        self.bus.clear()
        self.bus.configure(enabled=True, detail_level="standard")
    
    def test_high_contention_event_recording(self):
        """Test event recording under high thread contention."""
        num_threads = 20
        events_per_thread = 100
        results = []
        errors = []
        
        def high_contention_recording(thread_id):
            try:
                for i in range(events_per_thread):
                    payload = {
                        "workflow_type": "stress_test",
                        "thread_id": thread_id,
                        "iteration": i,
                        "random_data": random.random(),
                        "timestamp": time.time()
                    }
                    
                    # Mix of different event types to increase contention
                    event_name = random.choice(["event_start", "event_progress", "event_end", "event_error"])
                    layer = random.choice(["L1", "L2", "L3", "L4", "L5"])
                    
                    self.bus.record_event(event_name, layer, payload)
                    
                    # Random small delays to increase thread interleaving
                    if random.random() < 0.1:
                        time.sleep(random.uniform(0.0001, 0.001))
                
                results.append(thread_id)
                
            except Exception as e:
                errors.append((thread_id, e))
        
        # Use verbose mode to preserve thread_id field
        self.bus.configure(detail_level="verbose")
        
        # Create high contention scenario
        threads = []
        start_time = time.time()
        
        for i in range(num_threads):
            thread = threading.Thread(target=high_contention_recording, args=(i,))
            threads.append(thread)
        
        # Start all threads simultaneously
        for thread in threads:
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        duration = time.time() - start_time
        
        # Validate results
        assert len(errors) == 0, f"Thread safety errors: {errors}"
        assert len(results) == num_threads
        
        # Validate data integrity
        events = self.bus.get_events()
        expected_events = num_threads * events_per_thread
        assert len(events) == expected_events, f"Expected {expected_events} events, got {len(events)}"
        
        # Validate no layer in any payload
        for event in events:
            assert "layer" not in event.payload
            assert event.layer in ["L1", "L2", "L3", "L4", "L5"]
        
        # Validate thread distribution
        thread_ids = set()
        for event in events:
            if "thread_id" in event.payload:
                thread_ids.add(event.payload["thread_id"])
        
        assert len(thread_ids) == num_threads, f"Events from {len(thread_ids)} threads, expected {num_threads}"
        
        # Performance should be reasonable
        assert duration < 10.0, f"High contention test took too long: {duration}s"
    
    def test_concurrent_configuration_changes(self):
        """Test thread safety during concurrent configuration changes."""
        num_threads = 10
        changes_per_thread = 50
        results = []
        errors = []
        
        def concurrent_config_changes(thread_id):
            try:
                for i in range(changes_per_thread):
                    # Random configuration changes
                    enabled = random.choice([True, False])
                    detail_level = random.choice(["verbose", "standard", "minimal"])
                    
                    self.bus.configure(enabled=enabled, detail_level=detail_level)
                    
                    # Record event to test configuration effect
                    if enabled:
                        payload = {
                            "workflow_type": "config_test",
                            "thread_id": thread_id,
                            "iteration": i,
                            "config_detail": detail_level
                        }
                        self.bus.record_event("config_event", "L3", payload)
                    
                    # Small delay to increase interleaving
                    time.sleep(0.001)
                
                results.append(thread_id)
                
            except Exception as e:
                errors.append((thread_id, e))
        
        # Create concurrent configuration changes
        threads = []
        for i in range(num_threads):
            thread = threading.Thread(target=concurrent_config_changes, args=(i,))
            threads.append(thread)
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Validate no thread safety errors
        assert len(errors) == 0, f"Configuration change errors: {errors}"
        assert len(results) == num_threads
        
        # Validate final state is consistent
        final_config = self.bus._enabled, self.bus._detail_level
        assert isinstance(final_config[0], bool)
        assert final_config[1] in ["verbose", "standard", "minimal"]
    
    def test_concurrent_event_filtering_and_retrieval(self):
        """Test thread safety of concurrent event filtering and retrieval."""
        num_producer_threads = 5
        num_consumer_threads = 5
        events_per_producer = 50
        
        producer_results = []
        consumer_results = []
        errors = []
        
        def event_producer(thread_id):
            try:
                for i in range(events_per_producer):
                    payload = {
                        "workflow_type": random.choice(["outreach", "research", "draft"]),
                        "thread_id": thread_id,
                        "iteration": i,
                        "stage": random.choice(["start", "progress", "end"])
                    }
                    
                    event_name = f"producer_event_{i}"
                    layer = f"L{random.randint(1, 5)}"
                    
                    self.bus.record_event(event_name, layer, payload)
                    time.sleep(0.001)  # Small delay
                
                producer_results.append(thread_id)
                
            except Exception as e:
                errors.append(("producer", thread_id, e))
        
        def event_consumer(thread_id):
            try:
                for i in range(20):  # Multiple retrieval operations
                    # Random filtering operations
                    layer_filter = random.choice([None, "L1", "L2", "L3", "L4", "L5"])
                    name_filter = random.choice([None, "producer_event_10", "producer_event_20"])
                    
                    events = self.bus.get_events(layer=layer_filter, name=name_filter)
                    _ = self.bus.get_errors(layer=layer_filter)
                    _ = self.bus.get_traces()
                    
                    # Validate retrieved data integrity
                    for event in events:
                        assert "layer" not in event.payload
                        assert hasattr(event, 'timestamp')
                        assert hasattr(event, 'name')
                    
                    time.sleep(0.002)  # Small delay
                
                consumer_results.append(thread_id)
                
            except Exception as e:
                errors.append(("consumer", thread_id, e))
        
        # Create producer and consumer threads
        threads = []
        
        # Start producers
        for i in range(num_producer_threads):
            thread = threading.Thread(target=event_producer, args=(f"producer_{i}",))
            threads.append(thread)
        
        # Start consumers
        for i in range(num_consumer_threads):
            thread = threading.Thread(target=event_consumer, args=(f"consumer_{i}",))
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Validate results
        assert len(errors) == 0, f"Consumer/producer errors: {errors}"
        assert len(producer_results) == num_producer_threads
        assert len(consumer_results) == num_consumer_threads
        
        # Validate data integrity
        events = self.bus.get_events()
        expected_events = num_producer_threads * events_per_producer
        assert len(events) == expected_events
    
    def test_singleton_pattern_thread_safety_extreme(self):
        """Test singleton pattern under extreme thread safety stress."""
        num_threads = 50
        instances_per_thread = 10
        all_instances = []
        errors = []
        
        def singleton_stress_test(thread_id):
            try:
                thread_instances = []
                for i in range(instances_per_thread):
                    # Create multiple instances rapidly
                    instance = TelemetryBus()
                    thread_instances.append(id(instance))
                    
                    # Small delay to increase contention
                    time.sleep(0.0001)
                
                all_instances.extend(thread_instances)
                
            except Exception as e:
                errors.append((thread_id, e))
        
        # Create extreme contention for singleton
        threads = []
        for i in range(num_threads):
            thread = threading.Thread(target=singleton_stress_test, args=(i,))
            threads.append(thread)
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Validate singleton pattern integrity
        assert len(errors) == 0, f"Singleton stress errors: {errors}"
        
        # All instances should have the same ID
        unique_instances = set(all_instances)
        assert len(unique_instances) == 1, f"Multiple instances created: {len(unique_instances)}"
    
    def test_deadlock_prevention_under_stress(self):
        """Test that telemetry system prevents deadlocks under stress."""
        num_threads = 10
        operations_per_thread = 100
        results = []
        errors = []
        
        def deadlock_stress_test(thread_id):
            try:
                for i in range(operations_per_thread):
                    # Mix operations that could cause deadlocks
                    operation = random.choice([
                        'record_event', 'record_error', 'record_trace',
                        'get_events', 'get_errors', 'get_traces', 'configure', 'clear'
                    ])
                    
                    if operation == 'record_event':
                        payload = {"thread_id": thread_id, "iteration": i}
                        self.bus.record_event(f"event_{i}", "L3", payload)
                    
                    elif operation == 'record_error':
                        try:
                            raise Exception(f"Test error {i}")
                        except Exception as e:
                            context = {"thread_id": thread_id, "iteration": i}
                            self.bus.record_error(f"error_{i}", "L3", e, context)
                    
                    elif operation == 'record_trace':
                        trace_data = {"thread_id": thread_id, "iteration": i}
                        self.bus.record_trace(trace_data)
                    
                    elif operation == 'get_events':
                        self.bus.get_events()
                    
                    elif operation == 'get_errors':
                        self.bus.get_errors()
                    
                    elif operation == 'get_traces':
                        self.bus.get_traces()
                    
                    elif operation == 'configure':
                        self.bus.configure(enabled=True, detail_level="standard")
                    
                    elif operation == 'clear':
                        # Only clear occasionally to avoid removing all data
                        if random.random() < 0.05:
                            self.bus.clear()
                    
                    # Random small delays
                    if random.random() < 0.1:
                        time.sleep(random.uniform(0.0001, 0.001))
                
                results.append(thread_id)
                
            except Exception as e:
                errors.append((thread_id, e))
        
        # Create deadlock stress scenario
        threads = []
        start_time = time.time()
        
        for i in range(num_threads):
            thread = threading.Thread(target=deadlock_stress_test, args=(i,))
            threads.append(thread)
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        duration = time.time() - start_time
        
        # Validate no deadlocks occurred
        assert len(errors) == 0, f"Deadlock stress errors: {errors}"
        assert len(results) == num_threads
        
        # Should complete in reasonable time (no deadlocks)
        assert duration < 30.0, f"Potential deadlock detected, test took too long: {duration}s"
    
    def test_memory_consistency_across_threads(self):
        """Test memory consistency of telemetry data across threads."""
        num_threads = 8
        events_per_thread = 25
        all_thread_data = {}
        errors = []
        
        def memory_consistency_test(thread_id):
            try:
                thread_events = []
                
                for i in range(events_per_thread):
                    payload = {
                        "thread_id": thread_id,
                        "iteration": i,
                        "unique_data": f"thread_{thread_id}_event_{i}",
                        "timestamp": time.time()
                    }
                    
                    event_name = f"memory_test_{thread_id}_{i}"
                    self.bus.record_event(event_name, "L3", payload)
                    
                    # Store expected data for validation
                    thread_events.append({
                        "name": event_name,
                        "thread_id": thread_id,
                        "iteration": i,
                        "unique_data": payload["unique_data"]
                    })
                
                all_thread_data[thread_id] = thread_events
                
            except Exception as e:
                errors.append((thread_id, e))
        
        # Use verbose mode to preserve thread_id and unique_data fields
        self.bus.configure(detail_level="verbose")
        
        # Create memory consistency test
        threads = []
        for i in range(num_threads):
            thread = threading.Thread(target=memory_consistency_test, args=(i,))
            threads.append(thread)
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Validate no errors
        assert len(errors) == 0, f"Memory consistency errors: {errors}"
        
        # Validate data consistency
        events = self.bus.get_events()
        assert len(events) == num_threads * events_per_thread
        
        # Create lookup for validation
        event_lookup = {}
        for event in events:
            key = event.name
            event_lookup[key] = event
        
        # Validate each thread's data is correctly stored
        for thread_id, expected_events in all_thread_data.items():
            for expected_event in expected_events:
                event_name = expected_event["name"]
                assert event_name in event_lookup, f"Event {event_name} not found"
                
                stored_event = event_lookup[event_name]
                assert stored_event.layer == "L3"
                assert "layer" not in stored_event.payload
                assert stored_event.payload["thread_id"] == thread_id
                assert stored_event.payload["iteration"] == expected_event["iteration"]
                assert stored_event.payload["unique_data"] == expected_event["unique_data"]
    
    def test_thread_pool_executor_stress(self):
        """Test telemetry system with ThreadPoolExecutor stress."""
        num_workers = 15
        tasks_per_worker = 30
        results = []
        errors = []
        
        def thread_pool_task(task_id):
            try:
                for i in range(tasks_per_worker):
                    # Complex payload to stress memory management
                    payload = {
                        "task_id": task_id,
                        "iteration": i,
                        "large_data": "x" * 1000,  # 1KB per event
                        "nested_data": {
                            "level1": {"level2": {"level3": f"data_{i}"}},
                            "array": list(range(100))
                        },
                        "timestamp": time.time()
                    }
                    
                    self.bus.record_event(f"pool_task_{task_id}_{i}", "L3", payload)
                    
                    # Periodic retrieval operations
                    if i % 10 == 0:
                        events = self.bus.get_events()
                        assert len(events) >= 0  # Should not crash
                
                results.append(task_id)
                
            except Exception as e:
                errors.append((task_id, e))
        
        # Use verbose mode to preserve large_data field
        self.bus.configure(detail_level="verbose")
        
        # Use ThreadPoolExecutor for stress testing
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            # Submit tasks
            futures = []
            for i in range(num_workers):
                future = executor.submit(thread_pool_task, i)
                futures.append(future)
            
            # Wait for completion
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    errors.append(("executor", e))
        
        duration = time.time() - start_time
        
        # Validate results
        assert len(errors) == 0, f"Thread pool stress errors: {errors}"
        assert len(results) == num_workers
        
        # Validate data integrity
        events = self.bus.get_events()
        expected_events = num_workers * tasks_per_worker
        assert len(events) == expected_events
        
        # Performance validation
        assert duration < 20.0, f"Thread pool stress took too long: {duration}s"
        
        # Memory efficiency check
        for event in events:
            assert "layer" not in event.payload
            assert len(event.payload["large_data"]) == 1000
