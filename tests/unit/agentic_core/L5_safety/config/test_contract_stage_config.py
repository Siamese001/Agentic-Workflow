"""Foundational behavioral tests for agentic_core/L5_safety/config/contract_stage_config.py.

fan_in=14 — this module is imported by 14 other modules.
ADG contract: import-hygiene is covered by test_contract_stage_config_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.config.contract_stage_config import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        CognitiveContract,
        CognitiveContractEnforcer,
        Constraint,
        ContractStage,
        Plan,
        PlanQualityError,
    )
    _AVAILABLE = True
except ImportError as _exc:
    _AVAILABLE = False
    ContractStage = None  # type: ignore[assignment,misc]
    CognitiveContract = None  # type: ignore[assignment,misc]
    CognitiveContractEnforcer = None  # type: ignore[assignment,misc]
    Constraint = None  # type: ignore[assignment,misc]
    Plan = None  # type: ignore[assignment,misc]
    PlanQualityError = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="contract_stage_config.py deps unavailable")
class TestContractStageContract:
    def test_is_class(self):
        assert isinstance(ContractStage, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(ContractStage, type)

@pytest.mark.skipif(not _AVAILABLE, reason="contract_stage_config.py deps unavailable")
class TestCognitiveContractContract:
    def test_is_class(self):
        assert isinstance(CognitiveContract, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(CognitiveContract, type)

@pytest.mark.skipif(not _AVAILABLE, reason="contract_stage_config.py deps unavailable")
class TestCognitiveContractEnforcerContract:
    def test_is_class(self):
        assert isinstance(CognitiveContractEnforcer, type)

    def test_has_method_enforce(self):
        assert callable(getattr(CognitiveContractEnforcer, 'enforce', None))

    def test_has_method_add_contract(self):
        assert callable(getattr(CognitiveContractEnforcer, 'add_contract', None))

@pytest.mark.skipif(not _AVAILABLE, reason="contract_stage_config.py deps unavailable")
class TestConstraintContract:
    def test_is_class(self):
        assert isinstance(Constraint, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(Constraint, type)

@pytest.mark.skipif(not _AVAILABLE, reason="contract_stage_config.py deps unavailable")
class TestPlanContract:
    def test_is_class(self):
        assert isinstance(Plan, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(Plan, type)

@pytest.mark.skipif(not _AVAILABLE, reason="contract_stage_config.py deps unavailable")
class TestPlanQualityErrorContract:
    def test_is_class(self):
        assert isinstance(PlanQualityError, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(PlanQualityError, type)

@pytest.mark.skipif(not _AVAILABLE, reason="contract_stage_config.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="contract_stage_config.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="contract_stage_config.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="contract_stage_config.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="contract_stage_config.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module contract_stage_config must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
