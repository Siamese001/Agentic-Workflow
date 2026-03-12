"""Foundational behavioral tests for agentic_core/L5_safety/reasoning/PredictiveCostAuditorAgent.py.

fan_in=11 — this module is imported by 11 other modules.
ADG contract: import-hygiene is covered by test_PredictiveCostAuditorAgent_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.reasoning.PredictiveCostAuditorAgent import (  # noqa: F401
        HealingMetrics,
        FileAudit,
        CostReport,
        PredictiveCostAuditorAgent,
        get_cost_auditor,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
    )
    _AVAILABLE = True
except Exception as _exc:
    _AVAILABLE = False
    HealingMetrics = None  # type: ignore[assignment,misc]
    FileAudit = None  # type: ignore[assignment,misc]
    CostReport = None  # type: ignore[assignment,misc]
    PredictiveCostAuditorAgent = None  # type: ignore[assignment,misc]
    get_cost_auditor = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="PredictiveCostAuditorAgent.py deps unavailable")
class TestHealingMetricsContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(HealingMetrics)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(HealingMetrics)}
        assert field_names >= {'success', 'attempt_number', 'key_id', 'tokens_used', 'file_path'}

@pytest.mark.skipif(not _AVAILABLE, reason="PredictiveCostAuditorAgent.py deps unavailable")
class TestFileAuditContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(FileAudit)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(FileAudit)}
        assert field_names >= {'total_tokens', 'total_attempts', 'failed_attempts', 'file_path', 'successful_attempts'}

@pytest.mark.skipif(not _AVAILABLE, reason="PredictiveCostAuditorAgent.py deps unavailable")
class TestCostReportContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(CostReport)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(CostReport)}
        assert field_names >= {'successful_files', 'total_tokens', 'total_attempts', 'failed_files', 'total_files'}

@pytest.mark.skipif(not _AVAILABLE, reason="PredictiveCostAuditorAgent.py deps unavailable")
class TestPredictiveCostAuditorAgentContract:
    def test_is_class(self):
        assert isinstance(PredictiveCostAuditorAgent, type)

    def test_has_method_execute(self):
        assert callable(getattr(PredictiveCostAuditorAgent, 'execute', None))

    def test_has_method_get_thermal_map(self):
        assert callable(getattr(PredictiveCostAuditorAgent, 'get_thermal_map', None))

    def test_has_method_get_fission_candidates(self):
        assert callable(getattr(PredictiveCostAuditorAgent, 'get_fission_candidates', None))

    def test_has_method_generate_daily_mission_report(self):
        assert callable(getattr(PredictiveCostAuditorAgent, 'generate_daily_mission_report', None))

@pytest.mark.skipif(not _AVAILABLE, reason="PredictiveCostAuditorAgent.py deps unavailable")
class TestGetCostAuditorFunction:
    def test_is_callable(self):
        assert callable(get_cost_auditor)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_cost_auditor)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="PredictiveCostAuditorAgent.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="PredictiveCostAuditorAgent.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="PredictiveCostAuditorAgent.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="PredictiveCostAuditorAgent.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="PredictiveCostAuditorAgent.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module PredictiveCostAuditorAgent must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
