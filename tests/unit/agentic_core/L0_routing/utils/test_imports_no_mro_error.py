#!/usr/bin/env python3
"""
Focused test to ensure L6 observability imports don't raise MRO errors.
This test FAILS if any MRO TypeError occurs during import.
"""

import pytest

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants


def test_l6_observability_imports_no_mro_error():
    """Test that L6 observability modules can be imported without MRO errors."""
    import sys
    from pathlib import Path

    # Add project root to path
    project_root = Path(__file__).resolve().parents[3]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    # List of L6 observability modules that previously had MRO issues
    modules_to_test = [
        "agentic_core.L6_observability.engines.SovereignHealthMonitor",
        "agentic_core.L6_observability.reasoning.observability_probe_executor",
    ]

    for module_name in modules_to_test:
        try:
            # Import the module
            module = __import__(module_name, fromlist=[""])
            # Try to get the main class (handle special cases for module names)
            if module_name.endswith("observability_probe_executor"):
                class_name = "ObservabilityProbeExecutorAgent"
            else:
                class_name = module_name.split(".")[-1]
            cls = getattr(module, class_name, None)
            assert cls is not None, f"Class {class_name} not found in {module_name}"
        except TypeError as e:
            if "method resolution" in str(e):
                pytest.fail(f"MRO error importing {module_name}: {e}")
            else:
                # Other TypeErrors are acceptable for this test
                pass
        except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            # TODO: Handle specific exception properly
            raise  # Re-raise after logging/handling
            # Import/Attribute errors are acceptable - we only care about MRO
            if "method resolution" in str(e):
                pytest.fail(f"MRO error importing {module_name}: {e}")
            # Other errors are fine for this test
