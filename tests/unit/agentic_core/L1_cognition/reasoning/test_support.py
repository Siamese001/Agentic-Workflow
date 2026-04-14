"""Shared assertions for compact module-surface tests."""

from __future__ import annotations

import importlib


def assert_module_surface(module_name: str, class_name: str, validator_name: str) -> None:
    module = importlib.import_module(module_name)
    assert module is not None
    assert hasattr(module, class_name)
    validator = getattr(module, validator_name)
    assert callable(validator)
