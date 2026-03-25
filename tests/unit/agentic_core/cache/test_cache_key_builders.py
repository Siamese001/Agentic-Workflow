"""Behavioral contract tests for agentic_core.cache.cache_key_builders."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.cache.cache_key_builders"


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


def test_build_agent_performance_key_is_callable(mod):
    """build_agent_performance_key is accessible and callable."""
    func = getattr(mod, "build_agent_performance_key", None)
    assert func is not None, "build_agent_performance_key must be defined in {MODULE_PATH}"
    assert callable(func), "build_agent_performance_key must be callable"


def test_build_cap_registry_key_is_callable(mod):
    """build_cap_registry_key is accessible and callable."""
    func = getattr(mod, "build_cap_registry_key", None)
    assert func is not None, "build_cap_registry_key must be defined in {MODULE_PATH}"
    assert callable(func), "build_cap_registry_key must be callable"


def test_build_compiled_prompt_key_is_callable(mod):
    """build_compiled_prompt_key is accessible and callable."""
    func = getattr(mod, "build_compiled_prompt_key", None)
    assert func is not None, "build_compiled_prompt_key must be defined in {MODULE_PATH}"
    assert callable(func), "build_compiled_prompt_key must be callable"


def test_build_lease_key_is_callable(mod):
    """build_lease_key is accessible and callable."""
    func = getattr(mod, "build_lease_key", None)
    assert func is not None, "build_lease_key must be defined in {MODULE_PATH}"
    assert callable(func), "build_lease_key must be callable"


def test_build_novelty_cluster_key_is_callable(mod):
    """build_novelty_cluster_key is accessible and callable."""
    func = getattr(mod, "build_novelty_cluster_key", None)
    assert func is not None, "build_novelty_cluster_key must be defined in {MODULE_PATH}"
    assert callable(func), "build_novelty_cluster_key must be callable"


def test_build_orch_plan_key_is_callable(mod):
    """build_orch_plan_key is accessible and callable."""
    func = getattr(mod, "build_orch_plan_key", None)
    assert func is not None, "build_orch_plan_key must be defined in {MODULE_PATH}"
    assert callable(func), "build_orch_plan_key must be callable"


def test_build_rag_admission_key_is_callable(mod):
    """build_rag_admission_key is accessible and callable."""
    func = getattr(mod, "build_rag_admission_key", None)
    assert func is not None, "build_rag_admission_key must be defined in {MODULE_PATH}"
    assert callable(func), "build_rag_admission_key must be callable"


def test_build_rag_topk_key_is_callable(mod):
    """build_rag_topk_key is accessible and callable."""
    func = getattr(mod, "build_rag_topk_key", None)
    assert func is not None, "build_rag_topk_key must be defined in {MODULE_PATH}"
    assert callable(func), "build_rag_topk_key must be callable"

