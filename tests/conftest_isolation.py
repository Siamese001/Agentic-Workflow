"""Test isolation framework for ensuring clean test execution.

Provides base classes and utilities for test isolation to prevent
cross-test contamination and ensure reliable test results.
"""

from __future__ import annotations

import os
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

import pytest

# Global state tracking for isolation validation
_global_state_snapshots: list[dict[str, Any]] = []


def capture_global_state() -> dict[str, Any]:
    """Capture current global state for isolation validation."""
    return {
        "cwd": str(Path.cwd()),
        "env": dict(os.environ),
        "path": sys.path[:],  # Copy to avoid mutation
        "sys_modules": list(sys.modules.keys()),
    }


def restore_global_state(state: dict[str, Any]) -> None:
    """Restore global state from a snapshot."""
    # Restore working directory
    os.chdir(state["cwd"])

    # Restore environment variables
    os.environ.clear()
    os.environ.update(state["env"])

    # Restore sys.path
    sys.path[:] = state["path"]


def reset_global_state() -> None:
    """Reset global state to clean defaults."""
    # Clear any added sys.path entries
    original_cwd = Path.cwd()

    # Reset to original working directory if possible
    try:
        os.chdir(original_cwd)
    except OSError:
        pass  # Directory may not exist anymore

    # Clear environment variables that might have been added
    test_vars = [k for k in os.environ.keys() if k.startswith("TEST_")]
    for var in test_vars:
        os.environ.pop(var, None)


class IsolatedTest:
    """Base class for tests requiring complete isolation."""

    @pytest.fixture(autouse=True)
    def isolated_test_environment(self):
        """Setup isolated test environment for each test method."""
        # Store original state
        self.original_cwd = Path.cwd()
        self.original_env = os.environ.copy()
        self.original_path = sys.path[:]

        # Create isolated temp directory
        self.temp_dir = Path(tempfile.mkdtemp(prefix="test_isolation_"))
        os.chdir(self.temp_dir)

        # Reset any global state
        reset_global_state()

        # Capture initial state for validation
        self.initial_state = capture_global_state()

        yield

        # Cleanup after test
        self._cleanup_isolated_environment()

    def _cleanup_isolated_environment(self):
        """Cleanup isolated test environment."""
        try:
            # Restore original state
            os.chdir(self.original_cwd)
            os.environ.clear()
            os.environ.update(self.original_env)
            sys.path[:] = self.original_path

            # Clean up temp directory
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir, ignore_errors=True)

        except Exception as e:  # guardian: allow-log-and-swallow -- teardown/cleanup context -- swallow is conventional in resource-release paths
            # Log cleanup error but don't fail test
            print(f"Warning: Test cleanup error: {e}")

    def validate_isolation(self) -> bool:
        """Validate that test isolation was maintained."""
        current_state = capture_global_state()

        # Check working directory
        if current_state["cwd"] != self.initial_state["cwd"]:
            return False

        # Check environment variables (allow test-specific additions)
        env_diff = set(current_state["env"].keys()) - set(self.initial_state["env"].keys())
        test_vars = [k for k in env_diff if not k.startswith("TEST_")]
        if test_vars:
            return False

        return True


class StateValidator:
    """Utilities for validating state isolation across tests."""

    @staticmethod
    def validate_no_state_leak(test_instances: list[Any]) -> dict[str, Any]:
        """Validate that multiple test instances don't share state."""
        results = []
        all_entities: list[tuple[int, str]] = []

        for i, instance in enumerate(test_instances):
            if hasattr(instance, "validate_state_isolation"):
                validation = instance.validate_state_isolation()
                registered_entities = validation.get("registered_entities") or []
                for entity in registered_entities:
                    all_entities.append((i, entity))
                results.append(
                    {
                        "instance_index": i,
                        "is_clean": validation["is_clean"],
                        "registered_entities": validation["registered_entities_count"],
                        "stats_totals": validation["stats_totals"],
                    }
                )
            else:
                results.append(
                    {
                        "instance_index": i,
                        "is_clean": None,
                        "error": "No validation method available",
                    }
                )

        entity_counts: dict[str, set[int]] = {}
        for idx, entity in all_entities:
            entity_counts.setdefault(entity, set()).add(idx)

        leaky_indices = {idx for entity, owners in entity_counts.items() if len(owners) > 1 for idx in owners}

        return {
            "total_instances": len(test_instances),
            "clean_instances": sum(1 for r in results if r.get("is_clean") is True),
            "leaky_instances": len(leaky_indices),
            "results": results,
        }

    @staticmethod
    def validate_global_state_integrity() -> dict[str, Any]:
        """Validate that global state hasn't been corrupted."""
        current = capture_global_state()

        # Check for suspicious changes
        suspicious_paths = [p for p in current["path"] if "test" in p.lower()]
        suspicious_env = [k for k in current["env"].keys() if "test" in k.lower()]

        return {
            "sys_path_clean": len(suspicious_paths) == 0,
            "environment_clean": len(suspicious_env) == 0,
            "suspicious_paths": suspicious_paths,
            "suspicious_env_vars": suspicious_env,
            "total_modules": len(current["sys_modules"]),
        }


# Pytest fixtures for easy use
@pytest.fixture
def temp_directory():
    """Provide a temporary directory that gets cleaned up automatically."""
    temp_dir = Path(tempfile.mkdtemp(prefix="pytest_temp_"))
    yield temp_dir
    if temp_dir.exists():
        shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def isolated_cwd():
    """Provide an isolated current working directory."""
    original_cwd = Path.cwd()
    temp_dir = Path(tempfile.mkdtemp(prefix="pytest_cwd_"))
    os.chdir(temp_dir)
    yield temp_dir
    os.chdir(original_cwd)
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def clean_env():
    """Provide a clean environment with minimal test variables."""
    original_env = os.environ.copy()

    # Keep essential variables but remove test additions
    essential_vars = [
        "PATH",
        "HOME",
        "USER",
        "TEMP",
        "TMP",
        "USERNAME",
        "COMPUTERNAME",
        "SYSTEMROOT",
        "WINDIR",
    ]

    clean_env = {k: v for k, v in original_env.items() if k in essential_vars}
    if "HOME" not in clean_env and "USERPROFILE" not in clean_env:
        fallback_home = original_env.get("USERPROFILE") or original_env.get("HOME") or str(Path.home())
        clean_env["USERPROFILE"] = fallback_home
    os.environ.clear()
    os.environ.update(clean_env)

    yield

    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)
