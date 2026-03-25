"""Behavioral contract tests for agentic_core.adg.identity.__init__."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.adg.identity.__init__"


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


def test_identitykind_is_instantiable(mod):
    """IdentityKind is accessible and is a type."""
    cls = getattr(mod, "IdentityKind", None)
    assert cls is not None, "IdentityKind must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "IdentityKind must be a class"


def test_identitynormalizer_is_instantiable(mod):
    """IdentityNormalizer is accessible and is a type."""
    cls = getattr(mod, "IdentityNormalizer", None)
    assert cls is not None, "IdentityNormalizer must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "IdentityNormalizer must be a class"


def test_identityrecord_is_instantiable(mod):
    """IdentityRecord is accessible and is a type."""
    cls = getattr(mod, "IdentityRecord", None)
    assert cls is not None, "IdentityRecord must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "IdentityRecord must be a class"


def test_normalize_identity_is_callable(mod):
    """normalize_identity is accessible and callable."""
    func = getattr(mod, "normalize_identity", None)
    assert func is not None, "normalize_identity must be defined in {MODULE_PATH}"
    assert callable(func), "normalize_identity must be callable"

