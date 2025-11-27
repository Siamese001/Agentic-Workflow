"""
Phase 8 Telemetry Async Safety Stress Tests

Tests telemetry system under extreme async safety stress:
- Async/await context safety
- Event loop integration
- Concurrent async operations
- Async telemetry recording
- Coroutine safety and error handling
- Async configuration changes
"""

import asyncio
import time
import random
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any

from runtime.telemetry_bus import TelemetryBus, get_telemetry_bus


class TestTelemetryAsyncSafety:
    """Test suite for telemetry async safety under stress conditions."""
    
    def setup_method(self):
        """Setup fresh telemetry bus for each test."""
        # Clear singleton to ensure clean state
        TelemetryBus._instance = None
        self.bus = get_telemetry_bus()
        self.bus.clear()
        self.bus.configure(enabled=True, detail_level="standard")
    
    def test_async_event_recording_safety(self):
        """Test async event recording safety under high concurrency."""
        num_coroutines = 20
        events_per_coroutine = 50
        results = []
        errors = []
        
        async def async_event_recording(coroutine_id):
            try:
                for i in range(events_per_coroutine):
                    payload = {
                        "workflow_type": "async_test",
                        "coroutine_id": coroutine_id,
                        "iteration": i,
                        "async_data": f"async_{coroutine_id}_{i}",
                        "timestamp": time.time()
                    }
                    
                    event_name = f"async_event_{coroutine_id}_{i}"
                    layer = f"L{random.randint(1, 5)}"
                    
                    # Simulate async work before recording
                    await asyncio.sleep(random.uniform(0.0001, 0.001))
                    
                    # Record event (synchronous operation in async context)
                    self.bus.record_event(event_name, layer, payload)
                    
                    # Random async delays
                    if random.random() < 0.1:
                        await asyncio.sleep(random.uniform(0.001, 0.005))
                
                results.append(coroutine_id)
                
            except Exception as e:
                errors.append((coroutine_id, e))
        
        # Create high-concurrency async scenario
        async def run_async_concurrent():
            tasks = []
            for i in range(num_coroutines):
                task = asyncio.create_task(async_event_recording(i))
                tasks.append(task)
            
            await asyncio.gather(*tasks, return_exceptions=True)
        
        # Execute async concurrent operations
        start_time = time.time()
        asyncio.run(run_async_concurrent())
        duration = time.time() - start_time
        
        # Validate results
        assert len(errors) == 0, f"Async safety errors: {errors}"
        assert len(results) == num_coroutines
        
        # Validate data integrity
        events = self.bus.get_events()
        expected_events = num_coroutines * events_per_coroutine
        assert len(events) == expected_events, f"Expected {expected_events} events, got {len(events)}"
        
        # Validate no layer in any payload
        for event in events:
            assert "layer" not in event.payload
            assert event.layer in ["L1", "L2", "L3", "L4", "L5"]
        
        # Performance should be reasonable
        assert duration < 15.0, f"Async concurrent test took too long: {duration}s"
    
    def test_mixed_sync_async_operations_safety(self):
        """Test safety when mixing synchronous and asynchronous operations."""
        num_sync_threads = 5
        num_async_coroutines = 5
        operations_per_worker = 30
        
        sync_results = []
        async_results = []
        errors = []
        
        def sync_operations(thread_id):
            try:
                for i in range(operations_per_worker):
                    payload = {
                        "worker_type": "sync",
                        "thread_id": thread_id,
                        "iteration": i,
                        "data": f"sync_{thread_id}_{i}"
                    }
                    
                    self.bus.record_event(f"sync_event_{thread_id}_{i}", "L3", payload)
                    time.sleep(0.001)  # Small sync delay
                
                sync_results.append(thread_id)
                
            except Exception as e:
                errors.append(("sync", thread_id, e))
        
        async def async_operations(coroutine_id):
            try:
                for i in range(operations_per_worker):
                    payload = {
                        "worker_type": "async",
                        "coroutine_id": coroutine_id,
                        "iteration": i,
                        "data": f"async_{coroutine_id}_{i}"
                    }
                    
                    await asyncio.sleep(0.001)  # Small async delay
                    self.bus.record_event(f"async_event_{coroutine_id}_{i}", "L3", payload)
                
                async_results.append(coroutine_id)
                
            except Exception as e:
                errors.append(("async", coroutine_id, e))
        
        # Use verbose mode to preserve all test fields
        self.bus.configure(detail_level="verbose")
        
        # Run mixed operations concurrently
        async def run_mixed_operations():
            # Start async coroutines
            async_tasks = []
            for i in range(num_async_coroutines):
                task = asyncio.create_task(async_operations(i))
                async_tasks.append(task)
            
            # Start sync threads in parallel
            with ThreadPoolExecutor(max_workers=num_sync_threads) as executor:
                sync_futures = []
                for i in range(num_sync_threads):
                    future = executor.submit(sync_operations, i)
                    sync_futures.append(future)
                
                # Wait for sync threads to complete
                for future in sync_futures:
                    future.result()
            
            # Wait for async coroutines to complete
            await asyncio.gather(*async_tasks, return_exceptions=True)
        
        # Execute mixed operations
        start_time = time.time()
        asyncio.run(run_mixed_operations())
        _ = time.time() - start_time  # Duration calculated but not needed for validation
        
        # Validate results
        assert len(errors) == 0, f"Mixed operations errors: {errors}"
        assert len(sync_results) == num_sync_threads
        assert len(async_results) == num_async_coroutines
        
        # Validate data integrity
        events = self.bus.get_events()
        expected_events = (num_sync_threads + num_async_coroutines) * operations_per_worker
        assert len(events) == expected_events
        
        # Validate both sync and async events are present
        sync_events = [e for e in events if "sync_event" in e.name and e.payload.get("worker_type") == "sync"]
        async_events = [e for e in events if "async_event" in e.name and e.payload.get("worker_type") == "async"]
        
        # The actual count shows both sync and async operations are running correctly
        assert len(sync_events) == num_sync_threads * operations_per_worker
        assert len(async_events) == num_async_coroutines * operations_per_worker
        
        # Validate total events count
        assert len(events) == len(sync_events) + len(async_events)
        
        # Validate event content integrity
        for sync_event in sync_events:
            assert sync_event.payload["worker_type"] == "sync"
            assert "thread_id" in sync_event.payload
        
        for async_event in async_events:
            assert async_event.payload["worker_type"] == "async"
            assert "coroutine_id" in async_event.payload
    
    def test_async_context_telemetry_safety(self):
        """Test telemetry safety within different async contexts."""
        contexts_tested = []
        errors = []
        
        async def async_context_1():
            try:
                # Test in basic async context
                for i in range(20):
                    payload = {"context": "basic_async", "iteration": i}
                    self.bus.record_event(f"context_1_event_{i}", "L3", payload)
                    await asyncio.sleep(0.001)
                contexts_tested.append("basic_async")
            except Exception as e:
                errors.append(("context_1", e))
        
        async def async_context_2():
            try:
                # Test in async context with gather
                async def sub_task(task_id):
                    payload = {"context": "gather", "task_id": task_id}
                    self.bus.record_event(f"context_2_task_{task_id}", "L3", payload)
                    await asyncio.sleep(0.001)
                
                tasks = [sub_task(i) for i in range(10)]
                await asyncio.gather(*tasks)
                contexts_tested.append("gather")
            except Exception as e:
                errors.append(("context_2", e))
        
        async def async_context_3():
            try:
                # Test in async context with timeout
                async def timeout_task():
                    for i in range(15):
                        payload = {"context": "timeout", "iteration": i}
                        self.bus.record_event(f"context_3_event_{i}", "L3", payload)
                        await asyncio.sleep(0.001)
                
                await asyncio.wait_for(timeout_task(), timeout=1.0)
                contexts_tested.append("timeout")
            except Exception as e:
                errors.append(("context_3", e))
        
        async def async_context_4():
            try:
                # Test in async context with exception handling
                for i in range(25):
                    try:
                        payload = {"context": "exception_handling", "iteration": i}
                        self.bus.record_event(f"context_4_event_{i}", "L3", payload)
                        
                        if i % 10 == 0:
                            raise ValueError(f"Test exception {i}")
                        
                        await asyncio.sleep(0.001)
                    except ValueError:
                        # Record error event
                        test_error = Exception(f"Context error {i}")
                        context = {"context": "exception_handling", "iteration": i}
                        self.bus.record_error(f"context_4_error_{i}", "L3", test_error, context)
                
                contexts_tested.append("exception_handling")
            except Exception as e:
                errors.append(("context_4", e))
        
        # Run all async contexts
        async def run_all_contexts():
            await asyncio.gather(
                async_context_1(),
                async_context_2(),
                async_context_3(),
                async_context_4(),
                return_exceptions=True
            )
        
        asyncio.run(run_all_contexts())
        
        # Validate results
        assert len(errors) == 0, f"Async context errors: {errors}"
        assert len(contexts_tested) == 4
        
        # Validate data integrity
        events = self.bus.get_events()
        errors_list = self.bus.get_errors()
        
        assert len(events) >= 70  # 20 + 10 + 15 + 25
        assert len(errors_list) >= 2  # From exception handling context
        
        # Validate context separation
        context_1_events = [e for e in events if "context_1_event" in e.name]
        context_2_events = [e for e in events if "context_2_task" in e.name]
        context_3_events = [e for e in events if "context_3_event" in e.name]
        context_4_events = [e for e in events if "context_4_event" in e.name]
        
        assert len(context_1_events) == 20
        assert len(context_2_events) == 10
        assert len(context_3_events) == 15
        assert len(context_4_events) == 25
    
    def test_async_configuration_changes_safety(self):
        """Test async safety during concurrent configuration changes."""
        num_config_changers = 8
        changes_per_changer = 20
        results = []
        errors = []
        
        async def async_config_changer(changer_id):
            try:
                for i in range(changes_per_changer):
                    # Async configuration changes
                    enabled = random.choice([True, False])
                    detail_level = random.choice(["verbose", "standard", "minimal"])
                    
                    self.bus.configure(enabled=enabled, detail_level=detail_level)
                    
                    # Record event if enabled
                    if enabled:
                        payload = {
                            "changer_id": changer_id,
                            "iteration": i,
                            "config_detail": detail_level
                        }
                        self.bus.record_event(f"config_event_{changer_id}_{i}", "L3", payload)
                    
                    # Async delay
                    await asyncio.sleep(random.uniform(0.001, 0.003))
                
                results.append(changer_id)
                
            except Exception as e:
                errors.append((changer_id, e))
        
        # Run concurrent async configuration changes
        async def run_async_config_changes():
            tasks = []
            for i in range(num_config_changers):
                task = asyncio.create_task(async_config_changer(i))
                tasks.append(task)
            
            await asyncio.gather(*tasks, return_exceptions=True)
        
        asyncio.run(run_async_config_changes())
        
        # Validate results
        assert len(errors) == 0, f"Async config errors: {errors}"
        assert len(results) == num_config_changers
        
        # Validate final state consistency
        final_enabled = self.bus._enabled
        final_detail = self.bus._detail_level
        assert isinstance(final_enabled, bool)
        assert final_detail in ["verbose", "standard", "minimal"]
    
    def test_async_error_recording_safety(self):
        """Test async safety of error recording operations."""
        num_error_coroutines = 10
        errors_per_coroutine = 15
        results = []
        errors = []
        
        async def async_error_recorder(coroutine_id):
            try:
                for i in range(errors_per_coroutine):
                    # Create different types of errors
                    error_types = [
                        ValueError(f"Value error {coroutine_id}_{i}"),
                        RuntimeError(f"Runtime error {coroutine_id}_{i}"),
                        Exception(f"Generic error {coroutine_id}_{i}")
                    ]
                    
                    test_error = random.choice(error_types)
                    context = {
                        "coroutine_id": coroutine_id,
                        "iteration": i,
                        "async_context": True,
                        "error_type": type(test_error).__name__
                    }
                    
                    # Record error in async context
                    self.bus.record_error(f"async_error_{coroutine_id}_{i}", "L3", test_error, context)
                    
                    # Async delay
                    await asyncio.sleep(random.uniform(0.001, 0.002))
                
                results.append(coroutine_id)
                
            except Exception as e:
                errors.append((coroutine_id, e))
        
        # Use verbose mode to preserve async_context field
        self.bus.configure(detail_level="verbose")
        
        # Run async error recording
        async def run_async_error_recording():
            tasks = []
            for i in range(num_error_coroutines):
                task = asyncio.create_task(async_error_recorder(i))
                tasks.append(task)
            
            await asyncio.gather(*tasks, return_exceptions=True)
        
        asyncio.run(run_async_error_recording())
        
        # Validate results
        assert len(errors) == 0, f"Async error recording errors: {errors}"
        assert len(results) == num_error_coroutines
        
        # Validate error data integrity
        error_events = self.bus.get_errors()
        expected_errors = num_error_coroutines * errors_per_coroutine
        assert len(error_events) == expected_errors
        
        # Validate error structure
        for error_event in error_events:
            assert error_event.layer == "L3"
            assert "layer" not in error_event.context
            assert "async_context" in error_event.context
            assert error_event.context["async_context"] is True
            assert isinstance(error_event.error, Exception)
    
    def test_async_trace_recording_safety(self):
        """Test async safety of trace recording operations."""
        num_trace_coroutines = 6
        traces_per_coroutine = 20
        results = []
        errors = []
        
        async def async_trace_recorder(coroutine_id):
            try:
                for i in range(traces_per_coroutine):
                    # Create complex trace data
                    trace_data = {
                        "coroutine_id": coroutine_id,
                        "iteration": i,
                        "async_trace": True,
                        "trace_sequence": list(range(i, i + 10)),
                        "nested_trace": {
                            "level1": {"level2": f"trace_data_{i}"},
                            "timing": {"start": time.time(), "end": time.time() + 0.1}
                        },
                        "metadata": {
                            "coroutine_type": "async_trace_test",
                            "trace_id": f"async_trace_{coroutine_id}_{i}"
                        }
                    }
                    
                    # Record trace in async context
                    self.bus.record_trace(trace_data)
                    
                    # Async delay
                    await asyncio.sleep(random.uniform(0.001, 0.002))
                
                results.append(coroutine_id)
                
            except Exception as e:
                errors.append((coroutine_id, e))
        
        # Run async trace recording
        async def run_async_trace_recording():
            tasks = []
            for i in range(num_trace_coroutines):
                task = asyncio.create_task(async_trace_recorder(i))
                tasks.append(task)
            
            await asyncio.gather(*tasks, return_exceptions=True)
        
        asyncio.run(run_async_trace_recording())
        
        # Validate results
        assert len(errors) == 0, f"Async trace recording errors: {errors}"
        assert len(results) == num_trace_coroutines
        
        # Validate trace data integrity
        traces = self.bus.get_traces()
        expected_traces = num_trace_coroutines * traces_per_coroutine
        assert len(traces) == expected_traces
        
        # Validate trace structure (traces preserve all data)
        for trace in traces:
            assert "async_trace" in trace.trace
            assert trace.trace["async_trace"] is True
            assert "coroutine_id" in trace.trace
            assert "nested_trace" in trace.trace
            assert "metadata" in trace.trace
    
    def test_async_event_loop_integration_safety(self):
        """Test telemetry safety across different event loop scenarios."""
        loop_scenarios = []
        errors = []
        
        async def scenario_default_loop():
            try:
                # Test in default event loop
                for i in range(15):
                    payload = {"scenario": "default_loop", "iteration": i}
                    self.bus.record_event(f"default_loop_event_{i}", "L3", payload)
                    await asyncio.sleep(0.001)
                loop_scenarios.append("default_loop")
            except Exception as e:
                errors.append(("default_loop", e))
        
        async def scenario_nested_tasks():
            try:
                # Test with nested async tasks
                async def nested_task(task_id):
                    for i in range(5):
                        payload = {"scenario": "nested_tasks", "task_id": task_id, "iteration": i}
                        self.bus.record_event(f"nested_task_{task_id}_{i}", "L3", payload)
                        await asyncio.sleep(0.001)
                
                tasks = [nested_task(i) for i in range(3)]
                await asyncio.gather(*tasks)
                loop_scenarios.append("nested_tasks")
            except Exception as e:
                errors.append(("nested_tasks", e))
        
        async def scenario_with_timeout():
            try:
                # Test with timeout handling
                async def timeout_task():
                    for i in range(10):
                        payload = {"scenario": "with_timeout", "iteration": i}
                        self.bus.record_event(f"timeout_event_{i}", "L3", payload)
                        await asyncio.sleep(0.002)
                
                await asyncio.wait_for(timeout_task(), timeout=1.0)
                loop_scenarios.append("with_timeout")
            except Exception as e:
                errors.append(("with_timeout", e))
        
        # Run all event loop scenarios
        async def run_all_scenarios():
            await asyncio.gather(
                scenario_default_loop(),
                scenario_nested_tasks(),
                scenario_with_timeout(),
                return_exceptions=True
            )
        
        asyncio.run(run_all_scenarios())
        
        # Validate results
        assert len(errors) == 0, f"Event loop scenario errors: {errors}"
        assert len(loop_scenarios) == 3
        
        # Validate data integrity across scenarios
        events = self.bus.get_events()
        assert len(events) >= 30  # 15 + 15 + 10
        
        # Validate scenario separation
        default_events = [e for e in events if "default_loop_event" in e.name]
        nested_events = [e for e in events if "nested_task_" in e.name]
        timeout_events = [e for e in events if "timeout_event" in e.name]
        
        assert len(default_events) == 15
        assert len(nested_events) == 15  # 3 tasks * 5 events each
        assert len(timeout_events) == 10
        
        # Validate no layer in any payload
        for event in events:
            assert "layer" not in event.payload
