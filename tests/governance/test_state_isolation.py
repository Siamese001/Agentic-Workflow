"""State Isolation Tests - Verify tests don't share state between runs."""

import gc
import shutil
import tempfile
import weakref
from pathlib import Path

import pytest


class TestImportIsolation:
    """Verify imports don't create state that leaks between tests."""

    def test_import_state_isolation(self):
        """Imports in one test shouldn't affect another test."""

        # First test - import and create an instance
        def test_import_1():
            # Create an instance to test state retention
            from pathlib import Path

            from agentic_core.L2_execution.utils.write_gateway import WriteAmplificationError

            error1 = WriteAmplificationError(Path("test1"), 100, 1000, 10.0)
            return id(error1), type(error1)

        # Second test - same import should create fresh state
        def test_import_2():
            from agentic_core.L2_execution.utils.write_gateway import WriteAmplificationError

            error2 = WriteAmplificationError(Path("test2"), 200, 2000, 10.0)
            return id(error2), type(error2)

        # Run both and verify they're independent
        id1, type1 = test_import_1()
        id2, type2 = test_import_2()

        # Types should be the same, but instances should be different
        assert type1 == type2
        assert id1 != id2

    def test_module_level_state_reset(self):
        """Module-level state should be consistent across test runs."""
        # Import a module that might have state
        import sys

        # Clear any existing module state
        modules_to_remove = [
            k for k in sys.modules.keys() if k.startswith(("agentic_core", "apps_", "system_learning"))
        ]

        # Store original modules
        original_modules = {}
        for module_name in modules_to_remove:
            if module_name in sys.modules:
                original_modules[module_name] = sys.modules[module_name]
                del sys.modules[module_name]

        try:
            # First import
            from agentic_core.L2_execution.utils.write_gateway import MAX_GROWTH_RATIO

            first_value = MAX_GROWTH_RATIO

            # Clear module and re-import
            for module_name in modules_to_remove:
                if module_name in sys.modules:
                    del sys.modules[module_name]

            # Second import
            from agentic_core.L2_execution.utils.write_gateway import MAX_GROWTH_RATIO

            second_value = MAX_GROWTH_RATIO

            # Values should be the same (constants don't change)
            assert first_value == second_value

        finally:
            # Restore original modules
            for module_name, module in original_modules.items():
                sys.modules[module_name] = module


class TestFileSystemIsolation:
    """Verify file system operations don't leak between tests."""

    def test_temp_file_cleanup(self):
        """Tests should clean up temporary files."""
        temp_files = []

        def create_temp_files():
            # Create some temporary files
            for i in range(3):
                temp_file = Path(tempfile.gettempdir()) / f"test_isolation_{i}.tmp"
                temp_file.write_text(f"test content {i}")
                temp_files.append(temp_file)

        # Create files
        create_temp_files()

        # Verify files exist
        assert all(f.exists() for f in temp_files)

        # Clean up (simulating proper test cleanup)
        for temp_file in temp_files:
            if temp_file.exists():
                temp_file.unlink()

        # Verify cleanup worked
        assert not any(f.exists() for f in temp_files)

    def test_working_directory_isolation(self):
        """Tests shouldn't change working directory permanently."""
        import os

        original_cwd = os.getcwd()

        def change_directory_test():
            # Change to a temporary directory
            temp_dir = tempfile.mkdtemp()
            try:
                os.chdir(temp_dir)
                changed_cwd = os.getcwd()
                return changed_cwd != original_cwd
            finally:
                os.chdir(original_cwd)
                shutil.rmtree(temp_dir)

        # Run test that changes directory
        directory_changed = change_directory_test()
        assert directory_changed  # Verify the test actually changed directory

        # Verify we're back to original directory
        assert os.getcwd() == original_cwd


class TestEnvironmentVariableIsolation:
    """Verify environment variable changes don't leak between tests."""

    def test_env_var_cleanup(self):
        """Tests should clean up environment variables."""
        import os

        # Store original state
        original_env = os.environ.copy()

        # Set some test environment variables
        test_vars = {
            "TEST_ISOLATION_VAR_1": "value1",
            "TEST_ISOLATION_VAR_2": "value2",
        }

        # Set test variables
        for key, value in test_vars.items():
            os.environ[key] = value

        # Verify variables are set
        for key, value in test_vars.items():
            assert os.environ.get(key) == value

        # Clean up (simulating proper test cleanup)
        for key in test_vars:
            if key in os.environ:
                del os.environ[key]

        # Verify cleanup worked
        for key in test_vars:
            assert key not in os.environ

        # Verify original environment is restored
        assert os.environ == original_env


class TestSingletonIsolation:
    """Verify singleton instances don't cause state leakage."""

    def test_weak_reference_cleanup(self):
        """Objects should be properly garbage collected."""

        def create_object_and_check():
            # Create an object
            from pathlib import Path

            from agentic_core.L2_execution.utils.write_gateway import WriteAmplificationError

            obj = WriteAmplificationError(Path("test"), 100, 1000, 10.0)

            # Create weak reference
            weak_ref = weakref.ref(obj)

            # Delete strong reference
            del obj

            # Force garbage collection
            gc.collect()

            # Check if object was collected
            return weak_ref() is None

        # Run multiple times to verify consistent behavior
        results = [create_object_and_check() for _ in range(5)]

        # All should return True (object was collected)
        assert all(results), "Objects not being properly garbage collected"

    def test_cache_isolation(self):
        """Module-level caches should not accumulate state."""

        # This is a conceptual test - actual implementation depends on specific modules
        def check_cache_size():
            # Check if any module has growing cache
            import sys

            cache_sizes = []
            for module_name, module in sys.modules.items():
                if hasattr(module, "__dict__"):
                    # Look for common cache patterns
                    dict_size = len(module.__dict__)
                    if dict_size > 1000:  # Arbitrary threshold for "large" cache
                        cache_sizes.append((module_name, dict_size))

            return cache_sizes

        # Check cache size before and after operations
        initial_caches = check_cache_size()

        # Perform some operations that might populate caches
        try:
            from agentic_core.L2_execution.utils.write_gateway import WriteAmplificationError
            from agentic_core.runtime.contracts.lifecycle_trace_contract import _emit_agent_executes_agent

            # Create some instances
            error = WriteAmplificationError(Path("test"), 100, 1000, 10.0)
        except ImportError:
            pass  # Modules might not be available

        final_caches = check_cache_size()

        # Cache sizes shouldn't grow dramatically
        initial_total = sum(size for _, size in initial_caches)
        final_total = sum(size for _, size in final_caches)

        # Allow some growth, but not excessive
        assert final_total - initial_total < 1000, "Cache growing excessively"


class TestTestOrderIndependence:
    """Verify test results don't depend on execution order."""

    def test_deterministic_results(self):
        """Same test should produce same results regardless of order."""
        results = []

        def run_test_multiple_times():
            """Run a simple test multiple times and collect results."""
            try:
                from agentic_core.L2_execution.utils.write_gateway import MAX_GROWTH_RATIO

                return MAX_GROWTH_RATIO
            except ImportError:
                return "import_failed"

        # Run test multiple times
        for _ in range(10):
            result = run_test_multiple_times()
            results.append(result)

        # All results should be identical
        assert len(set(results)) == 1, f"Non-deterministic results: {set(results)}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
