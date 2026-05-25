"""Tests for deprecated RootCustomsAgent shim (delegates to root_customs_util)."""

from __future__ import annotations

import warnings
from unittest.mock import patch

import pytest

from agentic_core.L0_routing.reasoning.RootCustomsAgent import RootCustomsAgent


def _agent() -> RootCustomsAgent:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        return RootCustomsAgent(dry_run=True)


class TestRootCustomsAgentDeprecation:
    def test_class_emits_deprecation_warning(self):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            RootCustomsAgent()
        assert any(issubclass(w.category, DeprecationWarning) for w in caught)


class TestRootCustomsAgentDelegation:
    def test_run_inspection_delegates(self):
        with patch(
            "agentic_core.L0_routing.reasoning.RootCustomsAgent._run_inspection",
            return_value={"total_files": 0},
        ) as mock_run:
            result = _agent().run_inspection()
        mock_run.assert_called_once()
        assert result["total_files"] == 0

    def test_scan_root_directory_delegates(self):
        with patch(
            "agentic_core.L0_routing.reasoning.RootCustomsAgent.scan_root_directory",
            return_value=[],
        ) as mock_scan:
            files = _agent().scan_root_directory()
        mock_scan.assert_called_once()
        assert files == []

    def test_heal_repository_not_implemented(self):
        with pytest.raises(NotImplementedError):
            _agent().heal_repository()
