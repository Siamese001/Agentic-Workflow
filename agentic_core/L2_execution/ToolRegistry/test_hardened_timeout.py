import unittest
import time
import concurrent.futures
from unittest.mock import patch, MagicMock
from agentic_core.L2_execution.ToolRegistry.query_runtime import run_hardened_query

class TestHardenedTimeout(unittest.TestCase):

    def test_timeout_break_logic(self):
        """CRITICAL: Ensures the main thread breaks even if the worker is in a sleep loop."""
        def permanent_sleep(sql):
            time.sleep(100)
            return "should never return"

        with patch('agentic_core.L2_execution.ToolRegistry.query_runtime.execute_sql', side_effect=permanent_sleep):
            start = time.time()
            # Set a very short timeout to trigger the logic quickly
            with self.assertRaises((concurrent.futures.TimeoutError, TimeoutError)):
                run_hardened_query("SELECT hang", timeout_seconds=1)
            
            elapsed = time.time() - start
            # Verify we broke out within ~1.5 seconds (allowing for small overhead)
            self.assertLess(elapsed, 2.0, "The query failed to break the polling loop within the timeout.")

    def test_future_cleanup_on_failure(self):
        """Verify the system remains stable when a query fails mid-execution."""
        def crash_immediately(sql):
            raise ConnectionError("DB Dead")

        with patch('agentic_core.L2_execution.ToolRegistry.query_runtime.execute_sql', side_effect=crash_immediately):
            with self.assertRaises(ConnectionError):
                run_hardened_query("SELECT fail")

    def test_rapid_re_entry_stability(self):
        """Ensure terminal UI handles sequential sub-second timeouts without corruption."""
        with patch('agentic_core.L2_execution.ToolRegistry.query_runtime.execute_sql', side_effect=lambda x: time.sleep(2)):
            for _ in range(3):
                with self.assertRaises((concurrent.futures.TimeoutError, TimeoutError)):
                    run_hardened_query("SELECT slow", timeout_seconds=0.1)

    def test_successful_execution_retrieval(self):
        """Verify data is returned correctly when the thread finishes before timeout."""
        with patch('agentic_core.L2_execution.ToolRegistry.query_runtime.execute_sql', return_value="success"):
            result = run_hardened_query("SELECT valid", timeout_seconds=5)
            self.assertEqual(result, "success")

    def test_wait_pattern_robustness(self):
        """Verify concurrent.futures.wait pattern handles edge cases correctly."""
        def slow_but_successful(sql):
            time.sleep(0.2)
            return [{"id": sql}]

        with patch('agentic_core.L2_execution.ToolRegistry.query_runtime.execute_sql', side_effect=slow_but_successful):
            result = run_hardened_query("SELECT wait_test", timeout_seconds=1)
            self.assertEqual(result, [{"id": "SELECT wait_test"}])

    def test_multiple_timeout_types_caught(self):
        """Ensure both concurrent.futures.TimeoutError and built-in TimeoutError are caught."""
        def raise_concurrent_timeout(sql):
            raise concurrent.futures.TimeoutError("Concurrent timeout")

        with patch('agentic_core.L2_execution.ToolRegistry.query_runtime.execute_sql', side_effect=raise_concurrent_timeout):
            with self.assertRaises((concurrent.futures.TimeoutError, TimeoutError)):
                run_hardened_query("SELECT concurrent_timeout")

if __name__ == '__main__':
    # 100% pass mandatory
    unittest.main()
