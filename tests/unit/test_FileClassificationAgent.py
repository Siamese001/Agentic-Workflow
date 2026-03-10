#!/usr/bin/env python3
"""Tests for agentic_core.L5_safety.reasoning.FileClassificationAgent."""
import importlib

import pytest


def test_agentic_core_L5_safety_reasoning_FileClassificationAgent_importable():
    """Module must be importable without error."""
    m = importlib.import_module("agentic_core.L5_safety.reasoning.FileClassificationAgent")
    assert m is not None

def test_file_classification_agent_is_class():
    import importlib
    m = importlib.import_module("agentic_core.L5_safety.reasoning.FileClassificationAgent")
    assert hasattr(m, "FileClassificationAgent")
    assert isinstance(m.FileClassificationAgent, type)
