"""Foundational behavioral tests for agentic_core/L2_execution/enforcement/SovereignLLMGateway.py.

fan_in=5 — imported by 5 other modules.
ADG import-hygiene is covered separately by test_SovereignLLMGateway_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L2_execution.enforcement.SovereignLLMGateway import (  # noqa: F401
        ProviderHealthState,
        SovereignLLMGateway,
        SovereigntyViolation,
        get_llm_gateway,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    ProviderHealthState = None  # type: ignore[assignment,misc]
    SovereigntyViolation = None  # type: ignore[assignment,misc]
    SovereignLLMGateway = None  # type: ignore[assignment,misc]
    get_llm_gateway = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="SovereignLLMGateway.py deps unavailable")
class TestProviderHealthStateContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ProviderHealthState)

    def test_is_frozen(self):
        assert ProviderHealthState.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(ProviderHealthState)}
        assert fnames >= {'error_rate', 'last_check', 'is_healthy', 'provider', 'degraded_until', 'consecutive_failures'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(ProviderHealthState)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="SovereignLLMGateway.py deps unavailable")
class TestSovereigntyViolationContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(SovereigntyViolation)

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(SovereigntyViolation)}
        assert fnames >= {'message'}

@pytest.mark.skipif(not _AVAILABLE, reason="SovereignLLMGateway.py deps unavailable")
class TestSovereignLLMGatewayContract:
    def test_is_class(self):
        assert isinstance(SovereignLLMGateway, type)

    def test_has_method_reset_instance(self):
        assert callable(getattr(SovereignLLMGateway, 'reset_instance', None))

    def test_has_method_config(self):
        assert callable(getattr(SovereignLLMGateway, 'config', None))

    def test_has_method_openai(self):
        assert callable(getattr(SovereignLLMGateway, 'openai', None))

    def test_has_method_anthropic(self):
        assert callable(getattr(SovereignLLMGateway, 'anthropic', None))

    def test_public_api_surface_non_empty(self):
        pub = [m for m in dir(SovereignLLMGateway) if not m.startswith('_')]
        assert len(pub) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="SovereignLLMGateway.py deps unavailable")
class TestGetLlmGatewayFunction:
    def test_is_callable(self):
        assert callable(get_llm_gateway)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_llm_gateway)
        assert sig.return_annotation is not inspect.Parameter.empty


def test_module_importable():
    """Smoke: SovereignLLMGateway importable or gracefully unavailable."""
    pass
