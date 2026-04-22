"""Behavioral tests for ``agentic_core.L0_routing.enforcement.safety_enforcement_seam``.

Each loader imports a specific L5 enforcement module via ``importlib.import_module``.
Tests verify the exact module path and the returned symbol.
"""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import patch

from agentic_core.L0_routing.enforcement import safety_enforcement_seam as seam


class TestLoaderPaths:
    def test_load_code_deduplication_agent(self) -> None:
        with patch("importlib.import_module") as mock_import:
            mock_import.return_value = SimpleNamespace(CodeDeduplicationAgent="CDA")
            result = seam.load_code_deduplication_agent()
            mock_import.assert_called_with(
                "agentic_core.L5_safety.enforcement.CodeDeduplicationAgent",
            )
            assert result == "CDA"

    def test_load_archival_gatekeeper_returns_module(self) -> None:
        sentinel = object()
        with patch("importlib.import_module", return_value=sentinel) as mock_import:
            assert seam.load_archival_gatekeeper() is sentinel
            mock_import.assert_called_with(
                "agentic_core.L5_safety.enforcement.archival_gatekeeper_gate",
            )

    def test_load_ssot_scanner_returns_module(self) -> None:
        sentinel = object()
        with patch("importlib.import_module", return_value=sentinel) as mock_import:
            assert seam.load_ssot_scanner() is sentinel
            mock_import.assert_called_with(
                "agentic_core.L5_safety.enforcement.ssot_scanner_enforcer",
            )

    def test_load_activation_gate_returns_module(self) -> None:
        sentinel = object()
        with patch("importlib.import_module", return_value=sentinel) as mock_import:
            assert seam.load_activation_gate() is sentinel
            mock_import.assert_called_with(
                "agentic_core.L5_safety.enforcement.activation_gate",
            )


class TestLoaderSurface:
    def test_all_loaders_exist_as_callables(self) -> None:
        names = [
            "load_code_deduplication_agent",
            "load_archival_gatekeeper",
            "load_ssot_scanner",
            "load_activation_gate",
        ]
        for name in names:
            fn = getattr(seam, name, None)
            assert callable(fn), f"{name} must be a public callable"
