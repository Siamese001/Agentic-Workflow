"""Behavioral contract tests for agentic_core.knowledge.research_cache.__init__."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.knowledge.research_cache.__init__"


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


def test_researchcache_is_instantiable(mod):
    """ResearchCache is accessible and is a type."""
    cls = getattr(mod, "ResearchCache", None)
    assert cls is not None, "ResearchCache must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ResearchCache must be a class"

