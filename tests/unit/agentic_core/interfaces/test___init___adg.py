"""Behavioral contract tests for agentic_core.interfaces.__init__."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.interfaces.__init__"


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


def test_detectionrequest_is_instantiable(mod):
    """DetectionRequest is accessible and is a type."""
    cls = getattr(mod, "DetectionRequest", None)
    assert cls is not None, "DetectionRequest must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "DetectionRequest must be a class"


def test_detectionresult_is_instantiable(mod):
    """DetectionResult is accessible and is a type."""
    cls = getattr(mod, "DetectionResult", None)
    assert cls is not None, "DetectionResult must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "DetectionResult must be a class"


def test_detectionsignalprotocol_is_instantiable(mod):
    """DetectionSignalProtocol is accessible and is a type."""
    cls = getattr(mod, "DetectionSignalProtocol", None)
    assert cls is not None, "DetectionSignalProtocol must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "DetectionSignalProtocol must be a class"


def test_humanreviewprotocol_is_instantiable(mod):
    """HumanReviewProtocol is accessible and is a type."""
    cls = getattr(mod, "HumanReviewProtocol", None)
    assert cls is not None, "HumanReviewProtocol must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "HumanReviewProtocol must be a class"


def test_ihealerprotocol_is_instantiable(mod):
    """IHealerProtocol is accessible and is a type."""
    cls = getattr(mod, "IHealerProtocol", None)
    assert cls is not None, "IHealerProtocol must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "IHealerProtocol must be a class"


def test_imemorystoreprotocol_is_instantiable(mod):
    """IMemoryStoreProtocol is accessible and is a type."""
    cls = getattr(mod, "IMemoryStoreProtocol", None)
    assert cls is not None, "IMemoryStoreProtocol must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "IMemoryStoreProtocol must be a class"


def test_iorchestratorprotocol_is_instantiable(mod):
    """IOrchestratorProtocol is accessible and is a type."""
    cls = getattr(mod, "IOrchestratorProtocol", None)
    assert cls is not None, "IOrchestratorProtocol must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "IOrchestratorProtocol must be a class"


def test_learningcontext_is_instantiable(mod):
    """LearningContext is accessible and is a type."""
    cls = getattr(mod, "LearningContext", None)
    assert cls is not None, "LearningContext must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "LearningContext must be a class"

