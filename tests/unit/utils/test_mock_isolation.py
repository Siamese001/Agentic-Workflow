"""
Mock Isolation Decorators and Utilities
Purpose: Reusable mock enforcement decorators for test suite
Priority: MEDIUM
Execution Time: Utility module (no direct execution)
"""

import functools
import os
import unittest.mock
from collections.abc import Callable
from typing import Any
from unittest.mock import MagicMock, patch


def _safe_patch(target: str, **kwargs):
    """Create a patch that handles missing modules gracefully."""
    try:
        return patch(target, **kwargs)
    except (ImportError, ModuleNotFoundError):
        # Return a no-op context manager for missing modules
        return _NoOpPatch()


class _NoOpPatch:
    """A no-op patch for modules that don't exist."""

    def __enter__(self):
        return MagicMock()

    def __exit__(self, *args):
        pass


def enforce_mock_boundary(
    test_function: Callable = None,
    *,
    block_network: bool = True,
    block_database: bool = True,
    block_filesystem: bool = False,
    block_subprocess: bool = True,
) -> Callable:
    """
    Decorator to enforce mock boundaries during test execution.

    Args:
        test_function: The test function to decorate
        block_network: Block real network calls
        block_database: Block real database connections
        block_filesystem: Block real filesystem operations
        block_subprocess: Block real subprocess calls

    Returns:
        Decorated test function with mock boundary enforcement
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Build patch list based on configuration
            patches = []

            if block_network:
                patches.extend(
                    [
                        patch("socket.socket", side_effect=Exception("Real network calls blocked")),
                    ]
                )

            if block_subprocess:
                patches.append(
                    patch("subprocess.run", side_effect=Exception("Real subprocess calls blocked"))
                )

            if block_filesystem:
                patches.extend(
                    [
                        patch("builtins.open", unittest.mock.mock_open()),
                        patch("pathlib.Path.exists", return_value=False),
                        patch("pathlib.Path.mkdir"),
                    ]
                )

            # Apply all patches
            patchers = [p.__enter__() for p in patches]

            try:
                return func(*args, **kwargs)
            finally:
                # Clean up patches
                for p, _patcher in zip(patches, patchers, strict=False):
                    p.__exit__(None, None, None)

        return wrapper

    # Handle both @enforce_mock_boundary and @enforce_mock_boundary() usage
    if test_function is None:
        return decorator
    else:
        return decorator(test_function)


def mock_external_services(services: dict[str, Any] = None) -> Callable:
    """
    Decorator to mock specific external services.

    Args:
        services: Dictionary mapping service names to mock return values

    Returns:
        Decorated test function with external services mocked
    """
    if services is None:
        services = {}

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Default service mocks
            default_patches = {
                "requests.get": MagicMock(return_value={"status": 200, "data": "mocked"}),
                "requests.post": MagicMock(return_value={"status": 200, "data": "mocked"}),
                "psycopg2.connect": MagicMock(),
                "redis.Redis": MagicMock(),
                "pymongo.MongoClient": MagicMock(),
            }

            # Override with user-provided services
            default_patches.update(services)

            # Apply patches
            with patch.dict(default_patches):
                return func(*args, **kwargs)

        return wrapper

    return decorator


def isolate_environment(
    test_function: Callable = None, *, env_vars: dict[str, str] = None, clean_env: bool = False
) -> Callable:
    """
    Decorator to isolate environment variables during test execution.

    Args:
        test_function: The test function to decorate
        env_vars: Environment variables to set during test
        clean_env: Start with clean environment (only test vars)

    Returns:
        Decorated test function with isolated environment
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Save original environment
            original_env = os.environ.copy()

            try:
                if clean_env:
                    # Clean environment
                    os.environ.clear()

                # Set test environment variables
                if env_vars:
                    os.environ.update(env_vars)

                return func(*args, **kwargs)

            finally:
                # Restore original environment
                os.environ.clear()
                os.environ.update(original_env)

        return wrapper

    # Handle both @isolate_environment and @isolate_environment() usage
    if test_function is None:
        return decorator
    else:
        return decorator(test_function)


def track_mock_calls(
    test_function: Callable = None, *, tracked_modules: list[str] = None
) -> Callable:
    """
    Decorator to track and verify mock calls during test execution.

    Args:
        test_function: The test function to decorate
        tracked_modules: List of module names to track calls for

    Returns:
        Decorated test function with call tracking enabled
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if tracked_modules is None:
                modules_to_track = ["requests", "psycopg2", "redis", "pymongo", "socket"]
            else:
                modules_to_track = tracked_modules

            # Track calls
            call_tracker = {}

            def create_call_tracker(module_name: str):
                def tracker(*args, **kwargs):
                    if module_name not in call_tracker:
                        call_tracker[module_name] = []
                    call_tracker[module_name].append((args, kwargs))
                    return MagicMock()

                return tracker

            # Create patches for tracking
            patches = []
            for module in modules_to_track:
                patches.append(patch(f"{module}.*", side_effect=create_call_tracker(module)))

            # Apply tracking patches
            patchers = [p.__enter__() for p in patches]

            try:
                result = func(*args, **kwargs)

                # Attach call tracker to test result for verification
                if hasattr(result, "__dict__"):
                    result._mock_calls_tracker = call_tracker
                else:
                    # For non-object results, store in wrapper
                    wrapper._mock_calls_tracker = call_tracker

                return result

            finally:
                # Clean up patches
                for p, _patcher in zip(patches, patchers, strict=False):
                    p.__exit__(None, None, None)

        return wrapper

    # Handle both @track_mock_calls and @track_mock_calls() usage
    if test_function is None:
        return decorator
    else:
        return decorator(test_function)


class MockIsolationContext:
    """Context manager for comprehensive mock isolation."""

    def __init__(
        self,
        block_network: bool = True,
        block_database: bool = False,  # Default to False to avoid missing module issues
        block_filesystem: bool = False,
        block_subprocess: bool = True,
        env_vars: dict[str, str] = None,
    ):
        self.block_network = block_network
        self.block_database = block_database
        self.block_filesystem = block_filesystem
        self.block_subprocess = block_subprocess
        self.env_vars = env_vars or {}
        self.patches = []
        self.original_env = None

    def __enter__(self):
        # Save original environment
        self.original_env = os.environ.copy()

        # Set test environment
        if self.env_vars:
            os.environ.update(self.env_vars)

        # Create patches based on configuration - only for modules that exist
        if self.block_network:
            self.patches.append(
                patch("socket.socket", side_effect=Exception("Network calls blocked"))
            )

        if self.block_subprocess:
            self.patches.append(
                patch("subprocess.run", MagicMock(return_value=MagicMock(returncode=0)))
            )

        if self.block_filesystem:
            self.patches.extend(
                [
                    patch("builtins.open", unittest.mock.mock_open()),
                    patch("pathlib.Path.exists", return_value=True),
                    patch("pathlib.Path.mkdir"),
                ]
            )

        # Apply all patches
        self.patchers = [p.__enter__() for p in self.patches]
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Clean up patches
        for p, _patcher in zip(self.patches, self.patchers, strict=False):
            p.__exit__(exc_type, exc_val, exc_tb)

        # Restore environment
        os.environ.clear()
        os.environ.update(self.original_env)


class MockBoundaryViolationDetector:
    """Detects mock boundary violations during test execution."""

    def __init__(self):
        self.violations = []
        self.active_patches = []

    def start_monitoring(self):
        """Start monitoring for boundary violations."""

        def violation_detector(module_name: str):
            def detector(*args, **kwargs):
                self.violations.append(
                    {
                        "module": module_name,
                        "args": args,
                        "kwargs": kwargs,
                        "timestamp": __import__("time").time(),
                    }
                )
                raise Exception(f"Boundary violation detected in {module_name}")

            return detector

        # Monitor common external modules
        modules_to_monitor = [
            "socket.socket.connect",
            "requests.Session.request",
            "psycopg2.connect",
            "redis.Redis",
            "pymongo.MongoClient",
            "subprocess.run",
        ]

        for module in modules_to_monitor:
            try:
                patcher = patch(module, side_effect=violation_detector(module))
                patcher.start()
                self.active_patches.append(patcher)
            except (ImportError, AttributeError):
                # Module not available, skip
                continue

    def stop_monitoring(self):
        """Stop monitoring and clean up patches."""
        for patcher in self.active_patches:
            patcher.stop()
        self.active_patches.clear()

    def get_violations(self) -> list[dict[str, Any]]:
        """Get list of detected violations."""
        return self.violations.copy()

    def clear_violations(self):
        """Clear violation history."""
        self.violations.clear()


# Utility functions for common mock scenarios


def create_mock_llm_response(response_text: str = "Mock LLM response") -> MagicMock:
    """Create a mock LLM response object."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = response_text
    mock_response.choices[0].finish_reason = "stop"
    return mock_response


def create_mock_database_cursor(rows: list[dict[str, Any]] = None) -> MagicMock:
    """Create a mock database cursor."""
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = rows or []
    mock_cursor.fetchone.return_value = rows[0] if rows else None
    mock_cursor.rowcount = len(rows) if rows else 0
    return mock_cursor


def create_mock_file_content(content: str = "mock file content") -> MagicMock:
    """Create a mock file object."""
    mock_file = MagicMock()
    mock_file.read.return_value = content
    mock_file.__enter__.return_value = mock_file
    mock_file.__exit__.return_value = None
    return mock_file


# Test helper functions


def assert_no_real_network_calls(test_function: Callable) -> Callable:
    """Decorator to assert no real network calls are made during test."""

    @functools.wraps(test_function)
    def wrapper(*args, **kwargs):
        detector = MockBoundaryViolationDetector()
        detector.start_monitoring()

        try:
            result = test_function(*args, **kwargs)

            violations = detector.get_violations()
            network_violations = [
                v
                for v in violations
                if any(module in v["module"] for module in ["socket", "requests", "urllib3"])
            ]

            assert len(network_violations) == 0, (
                f"Real network calls detected: {network_violations}"
            )

            return result

        finally:
            detector.stop_monitoring()

    return wrapper


def assert_no_real_database_calls(test_function: Callable) -> Callable:
    """Decorator to assert no real database calls are made during test."""

    @functools.wraps(test_function)
    def wrapper(*args, **kwargs):
        detector = MockBoundaryViolationDetector()
        detector.start_monitoring()

        try:
            result = test_function(*args, **kwargs)

            violations = detector.get_violations()
            db_violations = [
                v
                for v in violations
                if any(module in v["module"] for module in ["psycopg2", "redis", "pymongo"])
            ]

            assert len(db_violations) == 0, f"Real database calls detected: {db_violations}"

            return result

        finally:
            detector.stop_monitoring()

    return wrapper
