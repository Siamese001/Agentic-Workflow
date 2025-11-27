"""
Phase 9 Concurrency and Resilience Interaction Tests

Tests real concurrent execution scenarios with budget limits, async cancellation,
and the interaction between concurrency control and resilience mechanisms.
"""

import pytest
import asyncio
import threading
import time
from typing import Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

from runtime.execution_budget_manager import (
    ExecutionBudgetManager,
    BudgetLimits,
    get_budget_manager
)


class TestConcurrencyBudgetInteraction:
    """Test concurrency and resilience interaction with budget limits."""
    
    def setup_method(self):
        """Setup fresh budget manager for each test."""
        # Clear singleton to ensure clean state
        ExecutionBudgetManager._instance = None
        self.budget_manager = get_budget_manager()
        self.budget_manager.reset_usage()
        
        # Configure specific limits for concurrency testing
        self.concurrency_limits = BudgetLimits(
            max_parallel=3,  # Low parallel limit for testing
            max_tokens=10000,
            max_requests=50,
            max_depth=5,
            executor_timeout=1.0
        )
        self.budget_manager.configure(self.concurrency_limits)
    
    def test_concurrent_slot_enforcement_under_real_load(self):
        """Test concurrent slot enforcement with actual concurrent execution."""
        results = []
        errors = []
        
        # Use a barrier to synchronize worker start times
        barrier = threading.Barrier(10)  # 10 workers
        
        def worker(worker_id):
            try:
                # Wait for all workers to be ready
                barrier.wait(timeout=1.0)
                
                # Try to acquire a slot
                acquired = self.budget_manager.acquire_concurrent_slot(timeout=0.1)
                if acquired:
                    # Hold slot longer to create real contention
                    time.sleep(0.2)
                    
                    # Record some resource usage
                    self.budget_manager.record_tokens(f"worker_{worker_id}", 100)
                    self.budget_manager.record_request()
                    
                    # Release slot
                    self.budget_manager.release_concurrent_slot()
                    
                    results.append({
                        'worker_id': worker_id,
                        'success': True,
                        'acquired': True
                    })
                else:
                    results.append({
                        'worker_id': worker_id,
                        'success': False,
                        'acquired': False,
                        'reason': 'slot_timeout'
                    })
            except Exception as e:
                errors.append((worker_id, e))
        
        # Run more workers than parallel limit
        threads = []
        for i in range(10):  # 10 workers, but only 3 slots
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Verify no crashes
        assert len(errors) == 0
        assert len(results) == 10
        
        # With barrier synchronization and longer hold time, 
        # only 3 should succeed due to parallel limit
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        
        assert len(successful) <= 3  # Can't exceed parallel limit
        assert len(failed) >= 7      # At least 7 should fail
        
        # Final state should be clean
        usage = self.budget_manager.current_usage()
        assert usage['active_concurrent'] == 0
    
    def test_concurrent_depth_tracking_isolation(self):
        """Test depth tracking isolation under concurrent execution."""
        results = []
        errors = []
        
        def worker(worker_id):
            try:
                # Each worker tries to increment depth multiple times
                depth_acquired = 0
                
                for i in range(3):  # Try 3 depth levels per worker
                    if self.budget_manager.increment_depth(f"worker_{worker_id}"):
                        depth_acquired += 1
                        time.sleep(0.01)  # Simulate work
                        
                        # Decrement after work
                        self.budget_manager.decrement_depth(f"worker_{worker_id}")
                    else:
                        break  # Stop if depth limit exceeded
                
                results.append({
                    'worker_id': worker_id,
                    'depth_acquired': depth_acquired
                })
            except Exception as e:
                errors.append((worker_id, e))
        
        # Run multiple workers
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Verify no crashes and depth tracking works
        assert len(errors) == 0
        assert len(results) == 5
        
        # Final depth should be 0 (all properly decremented)
        usage = self.budget_manager.current_usage()
        assert usage['current_depth'] == 0
    
    def test_concurrent_token_budget_competition(self):
        """Test token budget competition under concurrent execution."""
        results = []
        errors = []
        
        def worker(worker_id):
            try:
                tokens_used = 0
                requests_made = 0
                
                # Each worker tries to use tokens
                for i in range(10):
                    # Check budget first
                    if self.budget_manager.check_budget(f"worker_{worker_id}"):
                        # Use tokens and record request
                        self.budget_manager.record_tokens(f"worker_{worker_id}", 50)
                        self.budget_manager.record_request()
                        
                        tokens_used += 50
                        requests_made += 1
                        
                        time.sleep(0.001)  # Simulate work
                    else:
                        break  # Stop when budget exceeded
                
                results.append({
                    'worker_id': worker_id,
                    'tokens_used': tokens_used,
                    'requests_made': requests_made
                })
            except Exception as e:
                errors.append((worker_id, e))
        
        # Run multiple workers competing for token budget
        threads = []
        for i in range(8):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Verify no crashes and budget enforcement works
        assert len(errors) == 0
        assert len(results) == 8
        
        # Total tokens used should not exceed limit
        total_tokens = sum(r['tokens_used'] for r in results)
        assert total_tokens <= 10000  # Our token limit
        
        # Total requests should not exceed limit
        total_requests = sum(r['requests_made'] for r in results)
        assert total_requests <= 50  # Our request limit
    
    def test_async_context_concurrent_execution(self):
        """Test concurrent execution in async context."""
        async def async_worker(worker_id):
            try:
                # Try to acquire slot
                acquired = self.budget_manager.acquire_concurrent_slot(timeout=0.2)
                if acquired:
                    # Simulate async work
                    await asyncio.sleep(0.05)
                    
                    # Use resources
                    self.budget_manager.record_tokens(f"async_worker_{worker_id}", 75)
                    self.budget_manager.record_request()
                    
                    # Release slot
                    self.budget_manager.release_concurrent_slot()
                    
                    return {
                        'worker_id': worker_id,
                        'success': True,
                        'acquired': True
                    }
                else:
                    return {
                        'worker_id': worker_id,
                        'success': False,
                        'acquired': False,
                        'reason': 'slot_timeout'
                    }
            except Exception as e:
                return {
                    'worker_id': worker_id,
                    'success': False,
                    'error': str(e)
                }
        
        async def run_async_test():
            # Run multiple async workers concurrently
            tasks = [async_worker(i) for i in range(8)]  # More workers than slots
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions
            successful_results = []
            exceptions = []
            
            for result in results:
                if isinstance(result, Exception):
                    exceptions.append(result)
                else:
                    successful_results.append(result)
            
            return successful_results, exceptions
        
        # Run the async test
        results, exceptions = asyncio.run(run_async_test())
        
        # Verify no exceptions
        assert len(exceptions) == 0
        assert len(results) == 8
        
        # Some should succeed, some should fail due to slot limits
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        
        assert len(successful) <= 3  # Can't exceed parallel limit
        assert len(failed) >= 5      # At least 5 should fail
        
        # Final state should be clean
        usage = self.budget_manager.current_usage()
        assert usage['active_concurrent'] == 0
    
    def test_concurrent_execution_with_cancellation(self):
        """Test concurrent execution with cancellation scenarios."""
        results = []
        errors = []
        
        def worker(worker_id):
            try:
                # Try to acquire slot
                acquired = self.budget_manager.acquire_concurrent_slot(timeout=0.1)
                if acquired:
                    # Simulate work that might be cancelled
                    for i in range(10):
                        time.sleep(0.01)
                        
                        # Simulate cancellation check
                        if i == 5 and worker_id % 3 == 0:  # Cancel some workers
                            self.budget_manager.release_concurrent_slot()
                            results.append({
                                'worker_id': worker_id,
                                'success': False,
                                'cancelled': True,
                                'iterations_completed': i
                            })
                            return
                    
                    # Complete normally if not cancelled
                    self.budget_manager.record_tokens(f"worker_{worker_id}", 25)
                    self.budget_manager.release_concurrent_slot()
                    
                    results.append({
                        'worker_id': worker_id,
                        'success': True,
                        'cancelled': False,
                        'iterations_completed': 10
                    })
                else:
                    results.append({
                        'worker_id': worker_id,
                        'success': False,
                        'cancelled': False,
                        'reason': 'slot_timeout'
                    })
            except Exception as e:
                errors.append((worker_id, e))
        
        # Run workers
        threads = []
        for i in range(9):  # More workers than slots
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Verify no crashes
        assert len(errors) == 0
        assert len(results) == 9
        
        # Some should be cancelled, some should complete
        cancelled = [r for r in results if r.get('cancelled')]
        completed = [r for r in results if r['success'] and not r.get('cancelled')]
        
        assert len(cancelled) > 0
        assert len(completed) > 0
        
        # Final state should be clean
        usage = self.budget_manager.current_usage()
        assert usage['active_concurrent'] == 0
    
    def test_thread_pool_executor_integration(self):
        """Test integration with ThreadPoolExecutor for realistic concurrent scenarios."""
        results = []
        
        # Use a barrier to synchronize all tasks
        barrier = threading.Barrier(12)
        
        def worker_task(worker_id):
            """Worker task for ThreadPoolExecutor."""
            try:
                # Wait for all tasks to be ready
                barrier.wait(timeout=1.0)
                
                # Acquire slot
                if self.budget_manager.acquire_concurrent_slot(timeout=0.1):
                    # Simulate CPU-bound work with longer duration
                    total = 0
                    for i in range(100000):
                        total += i
                    
                    # Hold slot longer to create contention
                    time.sleep(0.2)
                    
                    # Use resources
                    self.budget_manager.record_tokens(f"pool_worker_{worker_id}", 30)
                    self.budget_manager.record_request()
                    
                    # Release slot
                    self.budget_manager.release_concurrent_slot()
                    
                    return {
                        'worker_id': worker_id,
                        'success': True,
                        'result': total
                    }
                else:
                    return {
                        'worker_id': worker_id,
                        'success': False,
                        'reason': 'slot_timeout'
                    }
            except Exception as e:
                return {
                    'worker_id': worker_id,
                    'success': False,
                    'error': str(e)
                }
        
        # Use ThreadPoolExecutor for realistic concurrent execution
        with ThreadPoolExecutor(max_workers=8) as executor:
            # Submit more tasks than parallel slots
            futures = [executor.submit(worker_task, i) for i in range(12)]
            
            # Collect results as they complete
            for future in as_completed(futures):
                try:
                    result = future.result(timeout=5.0)  # Longer timeout for barrier sync
                    results.append(result)
                except Exception as e:
                    results.append({
                        'success': False,
                        'error': f"Future error: {e}"
                    })
        
        # Verify results
        assert len(results) == 12
        
        # With barrier synchronization and longer hold time,
        # only 3 should succeed due to slot limits
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        
        assert len(successful) <= 3  # Can't exceed parallel limit
        assert len(failed) >= 9      # At least 9 should fail
        
        # Final state should be clean
        usage = self.budget_manager.current_usage()
        assert usage['active_concurrent'] == 0
    
    def test_concurrent_execution_stress_load(self):
        """Test system behavior under high concurrent load stress."""
        results = []
        errors = []
        
        def stress_worker(worker_id):
            try:
                operations_completed = 0
                
                # Each worker performs multiple operations
                for cycle in range(5):
                    # Try to acquire slot
                    if self.budget_manager.acquire_concurrent_slot(timeout=0.05):
                        # Quick work
                        time.sleep(0.001)
                        
                        # Use minimal resources
                        self.budget_manager.record_tokens(f"stress_worker_{worker_id}", 10)
                        
                        # Release slot
                        self.budget_manager.release_concurrent_slot()
                        
                        operations_completed += 1
                    else:
                        # Failed to acquire slot, skip this cycle
                        continue
                
                results.append({
                    'worker_id': worker_id,
                    'operations_completed': operations_completed
                })
            except Exception as e:
                errors.append((worker_id, e))
        
        # High stress: many workers, many cycles
        threads = []
        for i in range(20):  # 20 workers competing for 3 slots
            thread = threading.Thread(target=stress_worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Verify system stability under stress
        assert len(errors) == 0
        assert len(results) == 20
        
        # Should have completed some operations despite high contention
        total_operations = sum(r['operations_completed'] for r in results)
        assert total_operations > 0
        
        # Final state should be clean
        usage = self.budget_manager.current_usage()
        assert usage['active_concurrent'] == 0
        
        # Token usage should be within limits
        assert usage['tokens_used'] <= 10000
    
    
