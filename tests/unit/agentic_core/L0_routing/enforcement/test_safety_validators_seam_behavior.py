"""Behavioral tests for ``agentic_core.L0_routing.enforcement.safety_validators_seam``.

Each loader imports a specific L5 validators module via ``importlib.import_module``.
Tests verify the exact module path and the returned symbol.
"""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import patch

from agentic_core.L0_routing.enforcement import safety_validators_seam as seam


class TestLoaderPaths:
    def test_load_hygiene_guardian(self) -> None:
        with patch("importlib.import_module") as mock_import:
            mock_import.return_value = SimpleNamespace(HygieneGuardianAgent="HGA")
            result = seam.load_hygiene_guardian()
            mock_import.assert_called_with(
                "agentic_core.L5_safety.validators.HygieneGuardianAgent",
            )
            assert result == "HGA"

    def test_load_autonomy_guardian(self) -> None:
        with patch("importlib.import_module") as mock_import:
            mock_import.return_value = SimpleNamespace(AutonomyGuardianAgent="AGA")
            result = seam.load_autonomy_guardian()
            mock_import.assert_called_with(
                "agentic_core.L5_safety.validators.AutonomyGuardianAgent",
            )
            assert result == "AGA"

    def test_load_healing_strategy_returns_module(self) -> None:
        sentinel = object()
        with patch("importlib.import_module", return_value=sentinel) as mock_import:
            assert seam.load_healing_strategy() is sentinel
            mock_import.assert_called_with(
                "agentic_core.L5_safety.validators.healing_strategy",
            )

    def test_load_canonical_truth_validator_returns_module(self) -> None:
        sentinel = object()
        with patch("importlib.import_module", return_value=sentinel) as mock_import:
            assert seam.load_canonical_truth_validator() is sentinel
            mock_import.assert_called_with(
                "agentic_core.L5_safety.validators.canonical_truth_validator",
            )

    def test_load_cognitive_disposition_agent(self) -> None:
        with patch("importlib.import_module") as mock_import:
            mock_import.return_value = SimpleNamespace(CognitiveDispositionAgent="CDA")
            result = seam.load_cognitive_disposition_agent()
            mock_import.assert_called_with(
                "agentic_core.L5_safety.validators.CognitiveDispositionAgent",
            )
            assert result == "CDA"

    def test_load_dashboard_ssot_definitions_returns_module(self) -> None:
        sentinel = object()
        with patch("importlib.import_module", return_value=sentinel) as mock_import:
            assert seam.load_dashboard_ssot_definitions() is sentinel
            mock_import.assert_called_with(
                "agentic_core.L5_safety.validators.dashboard_ssot_definitions_config",
            )


class TestLoaderSurface:
    def test_all_loaders_exist_as_callables(self) -> None:
        names = [
            "load_hygiene_guardian",
            "load_autonomy_guardian",
            "load_healing_strategy",
            "load_canonical_truth_validator",
            "load_cognitive_disposition_agent",
            "load_dashboard_ssot_definitions",
        ]
        for name in names:
            fn = getattr(seam, name, None)
            assert callable(fn), f"{name} must be a public callable"
