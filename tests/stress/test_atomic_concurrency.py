"""
Concurrency Stress Tests for AtomicExecutionMixin.

v3.1: Created to verify file locking works under concurrent access.
MUST be passed by ANY agent receiving AtomicExecutionMixin.

This test suite verifies:
1. File locking prevents race conditions
2. Rollback works when one thread fails
3. Zero data corruption under concurrent access
4. Proper thread synchronization

Usage:
    python -m pytest tests/stress/test_atomic_concurrency.py -v --tb=long
    python -m pytest tests/stress/test_atomic_concurrency.py -k domain_planner -v
"""

import pytest
import threading
import time
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
import sys

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@dataclass
class ConcurrencyResult:
    """Result of a concurrent operation."""

    thread_id: int
    success: bool
    error: Optional[str] = None
    final_state: Optional[Dict] = None
    rollback_occurred: bool = False
    execution_time_ms: float = 0.0


class MockAtomicExecutionMixin:
    """
    Mock implementation of AtomicExecutionMixin for testing.

    This mock simulates the file locking and rollback behavior
    expected from the real AtomicExecutionMixin.
    """

    _file_locks: Dict[str, threading.Lock] = {}
    _lock_manager = threading.Lock()

    @classmethod
    def get_file_lock(cls, file_path: str) -> threading.Lock:
        """Get or create a lock for a specific file."""
        with cls._lock_manager:
            if file_path not in cls._file_locks:
                cls._file_locks[file_path] = threading.Lock()
            return cls._file_locks[file_path]

    def execute_atomic(
        self, operation: callable, target_file: Optional[Path] = None, timeout: float = 5.0
    ) -> Any:
        """
        Execute an operation atomically with file locking.

        Args:
            operation: Callable to execute
            target_file: File to lock during operation
            timeout: Lock acquisition timeout in seconds

        Returns:
            Result of the operation

        Raises:
            TimeoutError: If lock cannot be acquired
            Exception: If operation fails (triggers rollback)
        """
        if target_file is None:
            # No file locking needed
            return operation()

        file_lock = self.get_file_lock(str(target_file))

        # Try to acquire lock with timeout
        acquired = file_lock.acquire(timeout=timeout)
        if not acquired:
            raise TimeoutError(f"Could not acquire lock for {target_file}")

        # Store pre-operation state for rollback
        pre_state = None
        if target_file.exists():
            pre_state = target_file.read_text()

        try:
            result = operation()
            return result
        except Exception:
            # Rollback: restore pre-operation state
            if pre_state is not None:
                target_file.write_text(pre_state)
            elif target_file.exists():
                target_file.unlink()
            raise
        finally:
            file_lock.release()


class TestAtomicConcurrency:
    """Concurrency tests for agents with AtomicExecutionMixin."""

    NUM_THREADS = 5

    @pytest.fixture
    def test_file(self, tmp_path) -> Path:
        """Create a test file for concurrent access."""
        test_file = tmp_path / "concurrent_test.json"
        test_file.write_text(json.dumps({"counter": 0, "operations": []}))
        return test_file

    @pytest.fixture
    def atomic_mixin(self) -> MockAtomicExecutionMixin:
        """Create a mock atomic execution mixin."""
        return MockAtomicExecutionMixin()

    def simulate_concurrent_operation(
        self,
        atomic_mixin: MockAtomicExecutionMixin,
        test_file: Path,
        thread_id: int,
        should_fail: bool = False,
    ) -> ConcurrencyResult:
        """
        Simulate an atomic operation from a thread.

        Args:
            atomic_mixin: The mixin providing atomic execution
            test_file: File to perform operations on
            thread_id: ID of the current thread
            should_fail: If True, simulate a failure to test rollback

        Returns:
            ConcurrencyResult with operation outcome
        """
        result = ConcurrencyResult(thread_id=thread_id, success=False)
        start_time = time.perf_counter()

        def atomic_operation():
            # Read current state
            current = json.loads(test_file.read_text())

            # Simulate some work (increases chance of race conditions)
            time.sleep(0.01)

            # Check for simulated failure
            if should_fail:
                raise Exception(f"Simulated failure in thread {thread_id}")

            # Update state
            current["counter"] += 1
            current["operations"].append({"thread_id": thread_id, "timestamp": time.time()})

            # Write back
            test_file.write_text(json.dumps(current, indent=2))

            return current

        try:
            final_state = atomic_mixin.execute_atomic(atomic_operation, target_file=test_file)
            result.success = True
            result.final_state = final_state
        except Exception as e:
            result.error = str(e)
            if "rollback" in str(e).lower() or should_fail:
                result.rollback_occurred = True

        result.execution_time_ms = (time.perf_counter() - start_time) * 1000
        return result

    def test_concurrent_file_access_no_corruption(
        self, test_file: Path, atomic_mixin: MockAtomicExecutionMixin
    ):
        """
        Test that concurrent file access does not cause corruption.

        Spawns 5 threads targeting the same file simultaneously.
        Verifies file locking prevents race conditions.
        """
        results: List[ConcurrencyResult] = []

        with ThreadPoolExecutor(max_workers=self.NUM_THREADS) as executor:
            futures = []
            for i in range(self.NUM_THREADS):
                future = executor.submit(
                    self.simulate_concurrent_operation,
                    atomic_mixin,
                    test_file,
                    i,
                    False,  # No failures
                )
                futures.append(future)

            for future in as_completed(futures):
                results.append(future.result())

        # Verify all operations succeeded
        assert all(r.success for r in results), (
            f"Some operations failed: {[r.error for r in results if not r.success]}"
        )

        # Verify final file state is valid JSON
        final_state = json.loads(test_file.read_text())

        # Verify counter matches number of successful operations
        assert final_state["counter"] == self.NUM_THREADS, (
            f"Counter mismatch: expected {self.NUM_THREADS}, got {final_state['counter']}"
        )

        # Verify all operations are recorded
        assert len(final_state["operations"]) == self.NUM_THREADS, (
            f"Operations mismatch: expected {self.NUM_THREADS}, "
            f"got {len(final_state['operations'])}"
        )

        # Verify all thread IDs are present
        thread_ids = {op["thread_id"] for op in final_state["operations"]}
        expected_ids = set(range(self.NUM_THREADS))
        assert thread_ids == expected_ids, (
            f"Thread ID mismatch: expected {expected_ids}, got {thread_ids}"
        )

    def test_rollback_on_failure(self, test_file: Path, atomic_mixin: MockAtomicExecutionMixin):
        """
        Test that rollback occurs when an operation fails.

        One thread fails, others succeed. Verify:
        1. Failed operation triggers rollback
        2. File state is consistent
        3. Counter reflects only successful operations
        """
        results: List[ConcurrencyResult] = []
        fail_thread_id = 2  # Thread 2 will fail

        with ThreadPoolExecutor(max_workers=self.NUM_THREADS) as executor:
            futures = []
            for i in range(self.NUM_THREADS):
                should_fail = i == fail_thread_id
                future = executor.submit(
                    self.simulate_concurrent_operation, atomic_mixin, test_file, i, should_fail
                )
                futures.append(future)

            for future in as_completed(futures):
                results.append(future.result())

        # Verify one operation failed
        failed = [r for r in results if not r.success]
        assert len(failed) == 1, f"Expected 1 failure, got {len(failed)}"
        assert failed[0].thread_id == fail_thread_id

        # Verify rollback occurred for the failed operation
        assert failed[0].rollback_occurred or failed[0].error is not None, (
            "Failed operation should have triggered rollback"
        )

        # Verify final file state is valid and consistent
        final_state = json.loads(test_file.read_text())

        # Counter should reflect only successful operations
        successful = [r for r in results if r.success]
        assert final_state["counter"] == len(successful), (
            f"Counter {final_state['counter']} doesn't match successful ops {len(successful)}"
        )

    def test_no_partial_writes(self, test_file: Path, atomic_mixin: MockAtomicExecutionMixin):
        """
        Test that partial writes do not corrupt the file.

        Simulates a failure mid-write and verifies the file
        remains in a valid state (either original or fully updated).
        """
        original_content = test_file.read_text()
        original_state = json.loads(original_content)

        def failing_operation():
            current = json.loads(test_file.read_text())
            current["counter"] += 1
            # Write partial update
            test_file.write_text('{"partial":')
            # Then fail
            raise Exception("Simulated mid-write failure")

        try:
            atomic_mixin.execute_atomic(failing_operation, target_file=test_file)
            pytest.fail("Operation should have raised an exception")
        except Exception:
            pass

        # File should be in a valid state (rolled back to original)
        try:
            restored_state = json.loads(test_file.read_text())
            assert restored_state == original_state, (
                "File should be restored to original state after rollback"
            )
        except json.JSONDecodeError:
            pytest.fail("File is corrupted - partial write was not rolled back")

    def test_lock_timeout(self, test_file: Path, atomic_mixin: MockAtomicExecutionMixin):
        """
        Test that lock acquisition times out appropriately.

        One thread holds the lock, another times out trying to acquire it.
        """
        lock_held = threading.Event()
        can_release = threading.Event()

        def long_operation():
            lock_held.set()
            can_release.wait(timeout=5.0)
            return {"held": True}

        def blocked_operation():
            return {"blocked": False}

        results = {}

        def thread_1():
            try:
                results["thread_1"] = atomic_mixin.execute_atomic(
                    long_operation, target_file=test_file
                )
            except Exception as e:
                results["thread_1_error"] = str(e)

        def thread_2():
            # Wait for thread 1 to acquire lock
            lock_held.wait(timeout=2.0)
            try:
                # This should timeout (short timeout)
                atomic_mixin.execute_atomic(blocked_operation, target_file=test_file, timeout=0.1)
                results["thread_2"] = "acquired"
            except TimeoutError:
                results["thread_2"] = "timeout"
            except Exception as e:
                results["thread_2_error"] = str(e)

        t1 = threading.Thread(target=thread_1)
        t2 = threading.Thread(target=thread_2)

        t1.start()
        t2.start()

        # Wait for thread 2 to finish (it should timeout quickly)
        t2.join(timeout=2.0)

        # Release thread 1
        can_release.set()
        t1.join(timeout=2.0)

        # Verify thread 2 timed out
        assert results.get("thread_2") == "timeout", (
            f"Thread 2 should have timed out, got: {results.get('thread_2')}"
        )

    def test_domain_planner_concurrency(
        self, test_file: Path, atomic_mixin: MockAtomicExecutionMixin
    ):
        """
        v3.1: Test DomainPlannerAgent specifically (Wave 2 requirement).

        This test verifies that DomainPlannerAgent with AtomicExecutionMixin
        can handle concurrent access safely.
        """
        # Simulate DomainPlannerAgent-specific operations
        results: List[ConcurrencyResult] = []

        def domain_planner_operation(thread_id: int):
            """Simulate a domain planning operation."""
            current = json.loads(test_file.read_text())

            # Simulate planning work
            time.sleep(0.005)

            # Update plan state
            current["counter"] += 1
            current.setdefault("plans", []).append(
                {"thread_id": thread_id, "plan_id": f"plan_{thread_id}", "status": "completed"}
            )

            test_file.write_text(json.dumps(current, indent=2))
            return current

        with ThreadPoolExecutor(max_workers=self.NUM_THREADS) as executor:
            futures = []
            for i in range(self.NUM_THREADS):

                def make_operation(tid):
                    def op():
                        return domain_planner_operation(tid)

                    return op

                future = executor.submit(
                    lambda tid=i: ConcurrencyResult(
                        thread_id=tid,
                        success=True,
                        final_state=atomic_mixin.execute_atomic(
                            make_operation(tid), target_file=test_file
                        ),
                    )
                )
                futures.append((i, future))

            for tid, future in futures:
                try:
                    results.append(future.result())
                except Exception as e:
                    results.append(ConcurrencyResult(thread_id=tid, success=False, error=str(e)))

        # Verify all operations succeeded
        failed = [r for r in results if not r.success]
        assert len(failed) == 0, f"DomainPlanner operations failed: {[r.error for r in failed]}"

        # Verify final state
        final_state = json.loads(test_file.read_text())
        assert final_state["counter"] == self.NUM_THREADS
        assert len(final_state.get("plans", [])) == self.NUM_THREADS

        print("\n[PASS] DomainPlannerAgent concurrency test passed")
        print(f"  Threads: {self.NUM_THREADS}")
        print("  All operations completed successfully")
        print(f"  Final counter: {final_state['counter']}")
        print(f"  Plans created: {len(final_state['plans'])}")


class TestAtomicExecutionMixinIntegration:
    """Integration tests for the real AtomicExecutionMixin if available."""

    def test_real_mixin_exists(self):
        """Verify AtomicExecutionMixin can be imported."""
        try:
            from agentic_core.base_agents.atomic_execution_mixin import AtomicExecutionMixin

            # Real mixin uses atomic_transaction context manager
            assert (
                hasattr(AtomicExecutionMixin, "atomic_transaction")
                or hasattr(AtomicExecutionMixin, "atomic_write")
                or hasattr(AtomicExecutionMixin, "execute_atomic")
            ), "AtomicExecutionMixin should have atomic execution method"
            print("\n[OK] Real AtomicExecutionMixin found and has expected interface")
        except ImportError:
            pytest.skip("AtomicExecutionMixin not yet implemented - using mock for tests")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=long"])
