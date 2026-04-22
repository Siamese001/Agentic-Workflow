"""Behavioral tests for ``agentic_core.L0_routing.enforcement.safety_reasoning_seam``.

Each loader imports a specific L5 module via ``importlib.import_module``.
Tests verify the exact module path and the returned symbol.
"""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import patch

from agentic_core.L0_routing.enforcement import safety_reasoning_seam as seam


def _patched_import(attr_name: str, symbol: object):
    """Build a mock for importlib.import_module returning a module with symbol."""
    fake_module = SimpleNamespace(**{attr_name: symbol})
    return fake_module


class TestLoaderPaths:
    def test_load_naming_agent(self) -> None:
        with patch("importlib.import_module") as mock_import:
            mock_import.return_value = _patched_import("NamingAgent", "NA_CLS")
            result = seam.load_naming_agent()
            mock_import.assert_called_with("agentic_core.L5_safety.reasoning.NamingAgent")
            assert result == "NA_CLS"

    def test_load_structure_enforcer_agent(self) -> None:
        with patch("importlib.import_module") as mock_import:
            mock_import.return_value = _patched_import("StructureEnforcerAgent", "SEA")
            result = seam.load_structure_enforcer_agent()
            mock_import.assert_called_with(
                "agentic_core.L5_safety.reasoning.StructureEnforcerAgent",
            )
            assert result == "SEA"

    def test_load_cognitive_disposition_agent(self) -> None:
        with patch("importlib.import_module") as mock_import:
            mock_import.return_value = _patched_import("CognitiveDispositionAgent", "CDA")
            result = seam.load_cognitive_disposition_agent()
            mock_import.assert_called_with(
                "agentic_core.L5_safety.reasoning.CognitiveDispositionAgent",
            )
            assert result == "CDA"

    def test_load_file_classification_agent(self) -> None:
        with patch("importlib.import_module") as mock_import:
            mock_import.return_value = _patched_import("FileClassificationAgent", "FCA")
            result = seam.load_file_classification_agent()
            mock_import.assert_called_with(
                "agentic_core.L5_safety.reasoning.FileClassificationAgent",
            )
            assert result == "FCA"

    def test_load_location_validator_agent(self) -> None:
        with patch("importlib.import_module") as mock_import:
            mock_import.return_value = _patched_import("LocationValidatorAgent", "LVA")
            result = seam.load_location_validator_agent()
            mock_import.assert_called_with(
                "agentic_core.L5_safety.reasoning.location_validator",
            )
            assert result == "LVA"

    def test_load_verification_gate_adapter_returns_module(self) -> None:
        sentinel = object()
        with patch("importlib.import_module", return_value=sentinel) as mock_import:
            result = seam.load_verification_gate_adapter()
            mock_import.assert_called_with(
                "agentic_core.L5_safety.reasoning.verification_gate_adapter",
            )
            assert result is sentinel

    def test_load_human_review_adapter_returns_module(self) -> None:
        sentinel = object()
        with patch("importlib.import_module", return_value=sentinel) as mock_import:
            result = seam.load_human_review_adapter()
            mock_import.assert_called_with(
                "agentic_core.L5_safety.reasoning.human_review_adapter",
            )
            assert result is sentinel

    def test_load_inspector_executor(self) -> None:
        with patch("importlib.import_module") as mock_import:
            mock_import.return_value = _patched_import("InspectorExecutor", "IE")
            result = seam.load_inspector_executor()
            mock_import.assert_called_with(
                "agentic_core.L5_safety.reasoning.InspectorExecutor",
            )
            assert result == "IE"


class TestLoaderSurfaceShape:
    def test_all_loaders_exist_as_callables(self) -> None:
        names = [
            "load_naming_agent",
            "load_structure_enforcer_agent",
            "load_cognitive_disposition_agent",
            "load_file_classification_agent",
            "load_location_validator_agent",
            "load_verification_gate_adapter",
            "load_human_review_adapter",
            "load_inspector_executor",
        ]
        for name in names:
            fn = getattr(seam, name, None)
            assert callable(fn), f"{name} must be a public callable"
