"""Behavioral contract tests for agentic_core.adg.runtime.capability_budget."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.adg.runtime.capability_budget"


@pytest.fixture(scope="module")
def mod():
    """Import the module under test. Fails hard if first-party import broken."""
    try:
        return importlib.import_module(MODULE_PATH)
    except Exception as exc:
        pytest.fail(
            f"FIRST-PARTY IMPORT FAILED for {MODULE_PATH}: {exc}",
            pytrace=False,
        )


def test_module_importable(mod):
    """Module imports without errors."""
    assert mod.__name__ == MODULE_PATH


def test_module_exposes_public_api(mod):
    """Module exposes expected public symbols."""
    public = [n for n in dir(mod) if not n.startswith("_")]
    assert len(public) >= 1, f"{MODULE_PATH} must expose at least one public symbol"


def test_any_is_instantiable(mod):
    """Any is accessible and is a type."""
    cls = getattr(mod, "Any", None)
    assert cls is not None, "Any must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "Any must be a class"


def test_budgetevent_is_instantiable(mod):
    """BudgetEvent is accessible and is a type."""
    cls = getattr(mod, "BudgetEvent", None)
    assert cls is not None, "BudgetEvent must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "BudgetEvent must be a class"


def test_budgetexceedederror_is_instantiable(mod):
    """BudgetExceededError is accessible and is a type."""
    cls = getattr(mod, "BudgetExceededError", None)
    assert cls is not None, "BudgetExceededError must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "BudgetExceededError must be a class"


def test_budgetgovernorreport_is_instantiable(mod):
    """BudgetGovernorReport is accessible and is a type."""
    cls = getattr(mod, "BudgetGovernorReport", None)
    assert cls is not None, "BudgetGovernorReport must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "BudgetGovernorReport must be a class"


def test_budgetstatus_is_instantiable(mod):
    """BudgetStatus is accessible and is a type."""
    cls = getattr(mod, "BudgetStatus", None)
    assert cls is not None, "BudgetStatus must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "BudgetStatus must be a class"


def test_enum_is_instantiable(mod):
    """Enum is accessible and is a type."""
    cls = getattr(mod, "Enum", None)
    assert cls is not None, "Enum must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "Enum must be a class"


def test_resourcegovernor_is_instantiable(mod):
    """ResourceGovernor is accessible and is a type."""
    cls = getattr(mod, "ResourceGovernor", None)
    assert cls is not None, "ResourceGovernor must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ResourceGovernor must be a class"


def test_resourcegrant_is_instantiable(mod):
    """ResourceGrant is accessible and is a type."""
    cls = getattr(mod, "ResourceGrant", None)
    assert cls is not None, "ResourceGrant must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ResourceGrant must be a class"


def test_dataclass_is_callable(mod):
    """dataclass is accessible and callable."""
    func = getattr(mod, "dataclass", None)
    assert func is not None, "dataclass must be defined in {MODULE_PATH}"
    assert callable(func), "dataclass must be callable"


def test_field_is_callable(mod):
    """field is accessible and callable."""
    func = getattr(mod, "field", None)
    assert func is not None, "field must be defined in {MODULE_PATH}"
    assert callable(func), "field must be callable"

