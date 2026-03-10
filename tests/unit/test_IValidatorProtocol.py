#!/usr/bin/env python3
"""Tests for agentic_core.interfaces.IValidatorProtocol."""
import importlib

import pytest


def test_agentic_core_interfaces_IValidatorProtocol_importable():
    """Module must be importable without error."""
    m = importlib.import_module("agentic_core.interfaces.IValidatorProtocol")
    assert m is not None

def test_ivalidator_protocol_exports_validator_protocol():
    import importlib
    m = importlib.import_module("agentic_core.interfaces.IValidatorProtocol")
    assert hasattr(m, "ValidatorProtocol"), "module must export ValidatorProtocol"

def test_ivalidator_protocol_has_validate():
    import importlib
    m = importlib.import_module("agentic_core.interfaces.IValidatorProtocol")
    cls = m.ValidatorProtocol
    assert hasattr(cls, "validate"), "ValidatorProtocol must declare validate()"
