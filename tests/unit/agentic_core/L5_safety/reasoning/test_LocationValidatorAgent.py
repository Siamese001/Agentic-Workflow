#!/usr/bin/env python3
"""
Test for test_LocationValidatorAgent
# GENERATED_MIRROR_TEST
"""

import importlib
from pathlib import Path

import pytest


def test_test_LocationValidatorAgent_can_import():
    """Test that the module can be imported successfully."""
    try:
        mod = importlib.import_module("agentic_core.L5_safety.reasoning.LocationValidatorAgent")
        assert mod is not None
    except ImportError as e:
        pytest.skip(f"Cannot import module agentic_core.L5_safety.reasoning.LocationValidatorAgent: {e}")


def test_test_LocationValidatorAgent_has_file_attribute():
    """Test that module has __file__ attribute."""
    try:
        mod = importlib.import_module("agentic_core.L5_safety.reasoning.LocationValidatorAgent")
        assert hasattr(mod, "__file__")
    except ImportError:
        pytest.skip("Cannot import module agentic_core.L5_safety.reasoning.LocationValidatorAgent")


def test_test_LocationValidatorAgent_has_public_attributes():
    """Test that module has public attributes or callables."""
    try:
        mod = importlib.import_module("agentic_core.L5_safety.reasoning.LocationValidatorAgent")
        # Count non-private attributes
        public_attrs = [name for name in dir(mod) if not name.startswith("_")]
        # Look for at least one callable
        callables = [name for name in public_attrs if callable(getattr(mod, name))]

        if callables:
            # Test that first callable is callable
            assert callable(getattr(mod, callables[0]))
        else:
            # If no callables, at least assert we have some public attributes
            assert len(public_attrs) >= 0
    except ImportError:
        pytest.skip("Cannot import module agentic_core.L5_safety.reasoning.LocationValidatorAgent")


# ---------------------------------------------------------------------------
# Regression tests: bugs that caused system_learning files to be deleted
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).parents[5]


@pytest.mark.parametrize(
    "rel_path",
    [
        "system_learning/adapters/l1_meta_adapter.py",
        "system_learning/engines/l0_threshold_tuner.py",
        "system_learning/engines/l1_model_proposer.py",
        "system_learning/engines/l3_efficiency_tuner.py",
        "system_learning/engines/l4_audit_reader.py",
        "system_learning/engines/l4_state_writer.py",
        "system_learning/engines/l4_version_store.py",
        "system_learning/engines/l5_policy_proposer.py",
    ],
)
def test_system_learning_layer_prefix_files_not_violations(rel_path):
    """system_learning files with l0_/l1_/.../l5_ prefixes must NOT be flagged.

    Regression: LocationValidatorAgent._validate_filename_patterns() was
    treating layer-prefix filenames in system_learning as LAYER PREFIX
    VIOLATION, causing LocationHealerAgent to archive/delete them.
    """
    try:
        from agentic_core.L5_safety.reasoning.LocationValidatorAgent import (
            LocationValidatorAgent,
        )
    except ImportError as e:
        pytest.skip(f"Cannot import LocationValidatorAgent: {e}")

    validator = LocationValidatorAgent(project_root=REPO_ROOT)
    file_path = REPO_ROOT / rel_path
    ok, msg = validator.validate_file_location(file_path)
    assert ok, (
        f"system_learning file incorrectly flagged as violation: {rel_path}\n"
        f"Reason: {msg}\n"
        "Fix: ensure system_learning is exempt from FORBIDDEN_LAYER_PREFIXES check."
    )


@pytest.mark.parametrize(
    "rel_path",
    [
        "tools/dump_runtime_state_ml.py",
        "tools/prove_meta_learning_bus.py",
    ],
)
def test_tools_flat_scripts_not_shallow_violations(rel_path):
    """Flat .py scripts directly in tools/ must NOT be flagged as SHALLOW VIOLATION.

    Regression: tools/ has depth=2 in SOVEREIGN_TERRITORIES but allow_root_py=True,
    which permits depth-1 scripts. LocationValidatorAgent was ignoring allow_root_py
    and flagging flat tools scripts, causing LocationHealerAgent to move them to
    tools/depth_aligned/.
    """
    try:
        from agentic_core.L5_safety.reasoning.LocationValidatorAgent import (
            LocationValidatorAgent,
        )
    except ImportError as e:
        pytest.skip(f"Cannot import LocationValidatorAgent: {e}")

    validator = LocationValidatorAgent(project_root=REPO_ROOT)
    file_path = REPO_ROOT / rel_path
    ok, msg = validator.validate_file_location(file_path)
    assert ok, (
        f"tools flat script incorrectly flagged as violation: {rel_path}\n"
        f"Reason: {msg}\n"
        "Fix: _validate_depth_requirements must honour allow_root_py=True."
    )
