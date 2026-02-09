#!/usr/bin/env python3
"""
Focused test to ensure L6 observability imports don't raise MRO errors.
This test FAILS if any MRO TypeError occurs during import.
"""

import pytest


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
        "agentic_core.L6_observability.reasoning.TelemetryAgent",
        "agentic_core.L6_observability.reasoning.BenchmarkingAgent",
        "agentic_core.L6_observability.reasoning.StrategicObservationAgent",
        "agentic_core.L6_observability.reasoning.SovereignObservabilityAgent",
        "agentic_core.L6_observability.reasoning.RuntimeTelemetryAgent",
        "agentic_core.L6_observability.reasoning.TracingAgent",
        "agentic_core.L6_observability.reasoning.TrackObservabilityCostAgent",
        "agentic_core.L6_observability.reasoning.PerformanceAnalystAgent",
        "agentic_core.L6_observability.reasoning.MetricsAgent",
        "agentic_core.L6_observability.reasoning.ReportingAgent",
        "agentic_core.L6_observability.reasoning.DeadlockDetectorAgent",
        "agentic_core.L6_observability.reasoning.DebateSynthesisAgent",
        "agentic_core.L6_observability.reasoning.AutonomicMonitorAgent",
        "agentic_core.L6_observability.reasoning.SovereignHealthMonitor",
        "agentic_core.L6_observability.reasoning.ObservabilityProbeExecutor",
        "agentic_core.L6_observability.reasoning.CoordinateObservabilityOperationsAgent",
    ]

    for module_name in modules_to_test:
        try:
            # Import the module
            module = __import__(module_name, fromlist=[""])
            # Try to get the main class (usually the last part of module name)
            class_name = module_name.split(".")[-1]
            cls = getattr(module, class_name, None)
            assert cls is not None, f"Class {class_name} not found in {module_name}"
        except TypeError as e:
            if "method resolution" in str(e):
                pytest.fail(f"MRO error importing {module_name}: {e}")
            else:
                # Other TypeErrors are acceptable for this test
                pass
        except Exception as e:
            # Import/Attribute errors are acceptable - we only care about MRO
            if "method resolution" in str(e):
                pytest.fail(f"MRO error importing {module_name}: {e}")
            # Other errors are fine for this test
