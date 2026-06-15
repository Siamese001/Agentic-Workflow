"""Smoke tests for the canonical code detector utility."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.utils.code_detector_util")


def test_module_imports_clean():
    assert mod is not None


def test_code_detector_class_present():
    assert hasattr(mod, "CodeDetector")
    assert isinstance(mod.CodeDetector, type)


def test_code_detector_exposes_scan_api():
    assert callable(getattr(mod.CodeDetector, "run_full_scan", None))


def test_detection_present():
    assert hasattr(mod, "Detection")
    assert isinstance(mod.Detection, type)
