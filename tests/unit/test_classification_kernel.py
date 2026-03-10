#!/usr/bin/env python3
"""Tests for agentic_core.L5_safety.core_kernel.classification_kernel."""
import importlib

import pytest


def test_agentic_core_L5_safety_core_kernel_classification_kernel_importable():
    """Module must be importable without error."""
    m = importlib.import_module("agentic_core.L5_safety.core_kernel.classification_kernel")
    assert m is not None

def test_classification_kernel_has_enums():
    import importlib
    m = importlib.import_module("agentic_core.L5_safety.core_kernel.classification_kernel")
    # Must expose FileType or ExecutionMode enum
    assert hasattr(m, "FileType") or hasattr(m, "ExecutionMode"), (
        "classification_kernel must expose FileType or ExecutionMode"
    )

def test_file_type_enum_members():
    import importlib
    m = importlib.import_module("agentic_core.L5_safety.core_kernel.classification_kernel")
    ft = m.FileType
    members = list(ft)
    assert len(members) > 0, "FileType enum must have members"
