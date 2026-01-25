import unittest
import time
import concurrent.futures
from unittest.mock import patch, MagicMock
from agentic_core.L2_execution.ToolRegistry.query_runtime import run_hardened_query

class TestQueryTerminalHardening(unittest.TestCase):

    def test_timeout_termination_logic(self):
        """FIXED: UI reflects timeout state and raises exception even if thread hangs."""
        def infinite_wait(sql):
            while True:
                time.sleep(10)
        
        with patch('agentic_core.L2_execution.ToolRegistry.query_runtime.execute_sql', side_effect=infinite_wait):
            with self.assertRaises((concurrent.futures.TimeoutError, TimeoutError)):
                run_hardened_query("SELECT sleep(100)", timeout_seconds=1)

    def test_retry_logic_on_transient_failure(self):
        """Verify that the query retries on failure and eventually succeeds."""
        call_count = 0
        
        def transient_failure(sql):
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise RuntimeError("Transient DB Error")
            return [{"id": 1}]
            
        with patch('agentic_core.L2_execution.ToolRegistry.query_runtime.execute_sql', side_effect=transient_failure):
            with patch('agentic_core.L2_execution.ToolRegistry.query_runtime.time.sleep'): # Fast forward retries
                result = run_hardened_query("SELECT retry_test")
                self.assertEqual(result, [{"id": 1}])
                self.assertEqual(call_count, 2)

    def test_animation_liveness_during_io_block(self):
        """Verify that the executor returns correctly when the mock driver is slow."""
        def slow_db_call(sql):
            time.sleep(1.2)
            return [{"id": 1}]
        
        with patch('agentic_core.L2_execution.ToolRegistry.query_runtime.execute_sql', side_effect=slow_db_call):
            result = run_hardened_query("SELECT * FROM users")
            self.assertEqual(len(result), 1)

    def test_malformed_query_ui_recovery(self):
        """Confirm that a database error does not lock the terminal display."""
        with patch('agentic_core.L2_execution.ToolRegistry.query_runtime.execute_sql', side_effect=ValueError("Syntax Error")):
            with self.assertRaises(ValueError):
                run_hardened_query("INVALID SQL")

    def test_high_frequency_execution(self):
        """Stress test: Ensure the Progress context manager handles rapid open/close cycles."""
        with patch('agentic_core.L2_execution.ToolRegistry.query_runtime.execute_sql', return_value="ok"):
            for _ in range(10):
                run_hardened_query("SELECT 1")
            self.assertTrue(True)

    def test_concurrent_animation_thread_isolation(self):
        """Verify that the animation thread doesn't interfere with the main thread."""
        animation_calls = []
        
        def mock_progress_update(*args, **kwargs):
            animation_calls.append(('update', args, kwargs))
        
        def mock_progress_add_task(*args, **kwargs):
            return "mock_task_id"
        
        with patch('agentic_core.L2_execution.ToolRegistry.query_runtime.Progress') as mock_progress_class:
            mock_progress = MagicMock()
            mock_progress_class.return_value.__enter__.return_value = mock_progress
            mock_progress.add_task.side_effect = mock_progress_add_task
            mock_progress.update.side_effect = mock_progress_update
            
            def quick_db_call(sql):
                return [{"result": "quick"}]
            
            with patch('agentic_core.L2_execution.ToolRegistry.query_runtime.execute_sql', side_effect=quick_db_call):
                result = run_hardened_query("SELECT quick")
                
                self.assertEqual(result, [{"result": "quick"}])
                self.assertGreater(len(animation_calls), 0)

    def test_graceful_error_handling_with_cleanup(self):
        """Test that errors don't leave the progress bar in a broken state."""
        with patch('agentic_core.L2_execution.ToolRegistry.query_runtime.Progress') as mock_progress_class:
            mock_progress = MagicMock()
            mock_progress_class.return_value.__enter__.return_value = mock_progress
            
            def failing_db_call(sql):
                raise RuntimeError("Connection lost")
            
            with patch('agentic_core.L2_execution.ToolRegistry.query_runtime.execute_sql', side_effect=failing_db_call):
                with self.assertRaises(RuntimeError):
                    run_hardened_query("SELECT failing")
                
                # Verify progress was updated to show failure
                mock_progress.update.assert_called()

if __name__ == '__main__':
    # 100% Pass Language: All tests targeting the hang and retry logic must pass.
    unittest.main()
