import concurrent.futures
import time
import unittest
from unittest.mock import patch

from agentic_core.L2_execution.engine.query_runtime import run_hardened_query


class TestThreadHangResolution(unittest.TestCase):
    def test_non_blocking_exit_on_timeout(self):
        """
        GIVEN an infinite worker loop
        WHEN run_hardened_query is called with a 1s timeout
        THEN the main thread must exit promptly without hanging on executor shutdown.
        """

        def infinite_worker(sql):
            while True:
                time.sleep(1)

        with patch(
            "agentic_core.L2_execution.engine.query_runtime.execute_sql",
            side_effect=infinite_worker,
        ):
            start_time = time.time()
            with self.assertRaises((concurrent.futures.TimeoutError, TimeoutError)):
                run_hardened_query("SELECT hang", timeout_seconds=1)

            end_time = time.time()
            duration = end_time - start_time

            # The test should take roughly 1s (timeout) + minor overhead.
            # If it takes > 3s, the executor is blocking.
            self.assertLess(duration, 2.5, "Main thread blocked on executor shutdown despite timeout.")

    def test_retry_decorator_interaction_with_hang(self):
        """
        Ensures that the @retry_query decorator doesn't block the main thread
        if the initial attempt hangs.
        """

        def hang_on_first(sql):
            time.sleep(100)

        with patch(
            "agentic_core.L2_execution.engine.query_runtime.execute_sql",
            side_effect=hang_on_first,
        ):
            with self.assertRaises(TimeoutError):
                run_hardened_query("SELECT hang", timeout_seconds=0.5)

    def test_normal_completion_with_explicit_shutdown(self):
        """Verify that successful queries still return results correctly with explicit shutdown."""
        with patch(
            "agentic_core.L2_execution.engine.query_runtime.execute_sql",
            return_value="success",
        ):
            result = run_hardened_query("SELECT 1")
            self.assertEqual(result, "success")

    def test_clean_error_propagation(self):
        """Verify that standard errors still propagate without executor interference."""
        with patch(
            "agentic_core.L2_execution.engine.query_runtime.execute_sql",
            side_effect=ValueError("Test"),
        ):
            with self.assertRaises(ValueError):
                run_hardened_query("SELECT error")


if __name__ == "__main__":
    # 100% pass mandatory
    unittest.main()
