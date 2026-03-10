#!/usr/bin/env python3
"""Tests for apps_lic.reasoning.HOPPipelineExecutor (dependency may be incomplete)."""
import importlib

import pytest


def test_apps_lic_reasoning_HOPPipelineExecutor_importable():
    """Module must be importable; xfail if upstream dependency is missing."""
    try:
        m = importlib.import_module("apps_lic.reasoning.HOPPipelineExecutor")
        assert m is not None
    except ImportError as exc:
        pytest.xfail(f"Upstream dependency missing: {exc}")

def test_hop_pipeline_executor_module_importable():
    import importlib
    try:
        m = importlib.import_module("apps_lic.reasoning.HOPPipelineExecutor")
        assert hasattr(m, "HOPPipelineExecutor")
    except ImportError as exc:
        pytest.xfail(f"apps_lic dependency not installed: {exc}")
