"""Smoke tests for optimized_vllm_client — wave 31."""

import pytest

mod = pytest.importorskip("agentic_core.L3_orchestration.inference.qwen_vllm.engines.optimized_vllm_client")


def test_module_imports_clean():
    assert mod is not None


def test_module_has_public_surface():
    public = [k for k in dir(mod) if not k.startswith("_")]
    assert len(public) > 0
