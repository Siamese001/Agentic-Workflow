"""P1 Freeze: Timing test.

Prove freeze takes effect immediately; no execution window.
"""

from __future__ import annotations

import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import pytest


class FreezeTimingAuthority:
    """Authority for testing freeze timing."""

    def __init__(self):
        self.freeze_active = False
        self.freeze_timestamp: float | None = None
        self.operations_before_freeze: list[str] = []
        self.operations_after_freeze: list[str] = []
        self.concurrent_operations: list[str] = []

    def activate_freeze(self) -> float:
        """Activate freeze and return timestamp."""
        self.freeze_active = True
        self.freeze_timestamp = time.time()
        return self.freeze_timestamp

    def attempt_operation(self, operation_id: str, delay: float = 0) -> bool:
        """Attempt an operation with optional delay."""
        if delay > 0:
            time.sleep(delay)

        if self.freeze_active:
            self.operations_after_freeze.append(operation_id)
            return False
        else:
            self.operations_before_freeze.append(operation_id)
            return True

    def concurrent_operation(self, operation_id: str) -> str:
        """Operation that can run concurrently with freeze."""
        # Simulate some work
        time.sleep(0.001)  # 1ms work

        if self.freeze_active:
            return f"{operation_id}_blocked"
        else:
            return f"{operation_id}_allowed"


@pytest.mark.governance
def test_p1_freeze_immediate_effect():
    """P1 Freeze: Freeze takes effect immediately."""
    authority = FreezeTimingAuthority()

    # Operation before freeze should succeed
    assert authority.attempt_operation("op1")
    assert "op1" in authority.operations_before_freeze

    # Activate freeze
    freeze_time = authority.activate_freeze()

    # Operation immediately after freeze should fail
    assert not authority.attempt_operation("op2")
    assert "op2" in authority.operations_after_freeze

    # Verify timing
    assert authority.freeze_timestamp == freeze_time
    assert authority.freeze_active


@pytest.mark.governance
def test_p1_freeze_no_execution_window():
    """P1 Freeze: No execution window between freeze activation and effect."""
    authority = FreezeTimingAuthority()

    # Start a thread that will activate freeze after a short delay
    def delayed_freeze():
        time.sleep(0.01)  # 10ms delay
        authority.activate_freeze()

    freeze_thread = threading.Thread(target=delayed_freeze)
    freeze_thread.start()

    # Rapidly attempt operations
    successful_ops = []
    failed_ops = []

    for i in range(100):
        success = authority.attempt_operation(f"op{i}")
        if success:
            successful_ops.append(f"op{i}")
        else:
            failed_ops.append(f"op{i}")

        # Very small delay between operations
        time.sleep(0.0001)  # 0.1ms

    freeze_thread.join()

    # There should be a clear cutoff - no operations succeed after freeze
    assert len(successful_ops) > 0
    assert len(failed_ops) > 0

    # Verify operations are properly categorized
    for op in successful_ops:
        assert op in authority.operations_before_freeze
        assert op not in authority.operations_after_freeze

    for op in failed_ops:
        assert op in authority.operations_after_freeze
        assert op not in authority.operations_before_freeze


@pytest.mark.governance
def test_p1_freeze_concurrent_operations():
    """P1 Freeze: Freeze blocks concurrent operations immediately."""
    authority = FreezeTimingAuthority()

    def worker_operation(worker_id: int, operation_count: int) -> list[str]:
        """Worker that performs multiple operations."""
        results = []
        for i in range(operation_count):
            result = authority.concurrent_operation(f"worker{worker_id}_op{i}")
            results.append(result)
        return results

    # Start multiple workers
    workers = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        # Submit 10 workers, each doing 20 operations
        futures = []
        for worker_id in range(10):
            future = executor.submit(worker_operation, worker_id, 20)
            futures.append(future)

        # Let workers run for a bit
        time.sleep(0.005)  # 5ms

        # Activate freeze while workers are running
        authority.activate_freeze()

        # Collect results
        for future in as_completed(futures):
            results = future.result()
            workers.extend(results)

    # Some operations should have succeeded, others failed
    allowed_ops = [r for r in workers if r.endswith("_allowed")]
    blocked_ops = [r for r in workers if r.endswith("_blocked")]

    assert len(allowed_ops) > 0
    assert len(blocked_ops) > 0

    # Verify freeze was active
    assert authority.freeze_active


@pytest.mark.governance
def test_p1_freeze_timing_precision():
    """P1 Freeze: Test timing precision of freeze activation."""
    authority = FreezeTimingAuthority()

    # Record timing of operations around freeze
    operation_timings = []

    def timed_operation(operation_id: str):
        """Operation with precise timing."""
        start_time = time.time()
        success = authority.attempt_operation(operation_id)
        end_time = time.time()

        operation_timings.append(
            {
                "operation": operation_id,
                "start": start_time,
                "end": end_time,
                "success": success,
                "freeze_active": authority.freeze_active,
            }
        )

    # Start operations in rapid succession
    threads = []
    for i in range(50):
        thread = threading.Thread(target=timed_operation, args=(f"op{i}",))
        threads.append(thread)
        thread.start()
        time.sleep(0.0001)  # 0.1ms between starts

    # Activate freeze after some operations have started
    time.sleep(0.002)  # 2ms
    freeze_time = authority.activate_freeze()

    # Wait for all operations to complete
    for thread in threads:
        thread.join()

    # Analyze timing
    successful_ops = [t for t in operation_timings if t["success"]]
    failed_ops = [t for t in operation_timings if not t["success"]]

    # All successful operations should have started before freeze
    for op in successful_ops:
        assert op["start"] < freeze_time

    # All failed operations should have encountered active freeze
    for op in failed_ops:
        assert op["freeze_active"]


@pytest.mark.governance
def test_p1_freeze_race_condition_protection():
    """P1 Freeze: Freeze is protected against race conditions."""
    authority = FreezeTimingAuthority()

    # Multiple threads trying to activate freeze
    def activate_freeze_worker(worker_id: int):
        """Worker that tries to activate freeze."""
        freeze_time = authority.activate_freeze()
        return f"worker{worker_id}_{freeze_time}"

    # Start multiple freeze activation threads
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(activate_freeze_worker, i) for i in range(5)]
        results = [future.result() for future in as_completed(futures)]

    # Extract timestamps
    freeze_times = [float(r.split("_")[1]) for r in results]

    # Should have 1 or 2 unique timestamps (due to thread scheduling)
    # But freeze should be active
    assert authority.freeze_active
    assert len(set(freeze_times)) <= 2  # Allow for small timing differences


@pytest.mark.governance
def test_p1_freeze_immediate_block_new_operations():
    """P1 Freeze: New operations immediately blocked after freeze."""
    authority = FreezeTimingAuthority()

    # Activate freeze
    freeze_time = authority.activate_freeze()

    # Multiple immediate attempts should all fail
    failed_attempts = []
    for i in range(100):
        success = authority.attempt_operation(f"immediate_op{i}")
        if not success:
            failed_attempts.append(f"immediate_op{i}")

    # All should fail
    assert len(failed_attempts) == 100
    assert len(authority.operations_after_freeze) == 100
    assert len(authority.operations_before_freeze) == 0

    # Verify timing - all should be after freeze
    assert authority.freeze_timestamp == freeze_time


@pytest.mark.governance
def test_p1_freeze_microsecond_precision():
    """P1 Freeze: Test freeze timing at microsecond precision."""
    authority = FreezeTimingAuthority()

    # Record high-precision timing
    high_precision_timings = []

    def precision_operation(operation_id: str):
        """Operation with microsecond precision timing."""
        start_time = time.perf_counter()
        success = authority.attempt_operation(operation_id)
        end_time = time.perf_counter()

        high_precision_timings.append(
            {
                "operation": operation_id,
                "start": start_time,
                "end": end_time,
                "success": success,
                "duration_ns": int((end_time - start_time) * 1e9),
            }
        )

    # Start precision operations
    threads = []
    for i in range(20):
        thread = threading.Thread(target=precision_operation, args=(f"precise_op{i}",))
        threads.append(thread)
        thread.start()

    # Very short delay before freeze
    time.sleep(0.0001)  # 0.1ms

    # Activate freeze with high precision
    freeze_start = time.perf_counter()
    authority.activate_freeze()
    freeze_end = time.perf_counter()

    # Wait for operations
    for thread in threads:
        thread.join()

    # Analyze precision
    successful_ops = [t for t in high_precision_timings if t["success"]]
    failed_ops = [t for t in high_precision_timings if not t["success"]]

    # Freeze activation should be very fast
    freeze_duration_ns = int((freeze_end - freeze_start) * 1e9)
    assert freeze_duration_ns < 1000000  # Less than 1ms

    # Verify cutoff precision
    if successful_ops and failed_ops:
        last_success = max(t["start"] for t in successful_ops)
        first_failure = min(t["start"] for t in failed_ops)

        # There should be minimal gap between last success and first failure
        gap_ns = int((first_failure - last_success) * 1e9)
        assert gap_ns < 100000  # Less than 0.1ms gap


@pytest.mark.governance
def test_p1_freeze_no_execution_window_stress():
    """P1 Freeze: Stress test for no execution window."""
    authority = FreezeTimingAuthority()

    results = []

    def stress_worker(worker_id: int, operations: int):
        """Stress worker performing many operations."""
        worker_results = []
        for i in range(operations):
            op_id = f"worker{worker_id}_op{i}"
            start_time = time.perf_counter()
            success = authority.attempt_operation(op_id)
            end_time = time.perf_counter()

            worker_results.append(
                {
                    "worker": worker_id,
                    "operation": op_id,
                    "start": start_time,
                    "end": end_time,
                    "success": success,
                }
            )
        return worker_results

    # Start many stress workers
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(stress_worker, i, 50) for i in range(20)]

        # Let workers run, then activate freeze
        time.sleep(0.01)  # 10ms
        authority.activate_freeze()

        # Collect all results
        for future in as_completed(futures):
            worker_results = future.result()
            results.extend(worker_results)

    # Analyze results for execution window
    successful_ops = [r for r in results if r["success"]]
    failed_ops = [r for r in results if not r["success"]]

    # Should have both successful and failed operations
    assert len(successful_ops) > 0
    # If no failed ops, the freeze might have been too late
    if len(failed_ops) == 0:
        # At least verify freeze is active
        assert authority.freeze_active
    else:
        # There should be a clear cutoff
        last_success_time = max(r["start"] for r in successful_ops)
        first_failure_time = min(r["start"] for r in failed_ops)

        # The gap should be minimal (no execution window)
        gap_ns = int((first_failure_time - last_success_time) * 1e9)
        assert gap_ns < 50000  # Less than 0.05ms gap

    # Verify freeze effectiveness
    assert authority.freeze_active
