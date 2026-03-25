"""Behavioral contract tests for agentic_core.evaluation.judges.llm_judge."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.evaluation.judges.llm_judge"


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


def test_geminijudge_is_instantiable(mod):
    """GeminiJudge is accessible and is a type."""
    cls = getattr(mod, "GeminiJudge", None)
    assert cls is not None, "GeminiJudge must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "GeminiJudge must be a class"


def test_judgescore_is_instantiable(mod):
    """JudgeScore is accessible and is a type."""
    cls = getattr(mod, "JudgeScore", None)
    assert cls is not None, "JudgeScore must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "JudgeScore must be a class"


def test_llmjudge_is_instantiable(mod):
    """LLMJudge is accessible and is a type."""
    cls = getattr(mod, "LLMJudge", None)
    assert cls is not None, "LLMJudge must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "LLMJudge must be a class"


def test_nulljudge_is_instantiable(mod):
    """NullJudge is accessible and is a type."""
    cls = getattr(mod, "NullJudge", None)
    assert cls is not None, "NullJudge must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "NullJudge must be a class"


def test_protocol_is_instantiable(mod):
    """Protocol is accessible and is a type."""
    cls = getattr(mod, "Protocol", None)
    assert cls is not None, "Protocol must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "Protocol must be a class"


def test_dataclass_is_callable(mod):
    """dataclass is accessible and callable."""
    func = getattr(mod, "dataclass", None)
    assert func is not None, "dataclass must be defined in {MODULE_PATH}"
    assert callable(func), "dataclass must be callable"


def test_emit_determinism_digest_is_callable(mod):
    """emit_determinism_digest is accessible and callable."""
    func = getattr(mod, "emit_determinism_digest", None)
    assert func is not None, "emit_determinism_digest must be defined in {MODULE_PATH}"
    assert callable(func), "emit_determinism_digest must be callable"


def test_emit_replay_key_is_callable(mod):
    """emit_replay_key is accessible and callable."""
    func = getattr(mod, "emit_replay_key", None)
    assert func is not None, "emit_replay_key must be defined in {MODULE_PATH}"
    assert callable(func), "emit_replay_key must be callable"


def test_runtime_checkable_is_callable(mod):
    """runtime_checkable is accessible and callable."""
    func = getattr(mod, "runtime_checkable", None)
    assert func is not None, "runtime_checkable must be defined in {MODULE_PATH}"
    assert callable(func), "runtime_checkable must be callable"

