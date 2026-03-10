"""Wave 3 tests — healer re-entry gate + airlock enforcement."""

from __future__ import annotations

from unittest.mock import patch

import pytest

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

pytestmark = pytest.mark.unit_min_deps

_VALID_CONTEXT = {"namespace": "ns1", "max_k": 5, "version": "v1"}


def _make_assembler():
    from agentic_core.prompt_governance.core.prompt_assembler import PromptAssembler

    with patch(
        "agentic_core.prompt_governance.core.prompt_assembler.PromptAssembler._load_templates",
        return_value=None,
    ):
        return PromptAssembler()


# ---------------------------------------------------------------------------
# validate_healer_reentry
# ---------------------------------------------------------------------------


def test_healer_reentry_valid_passes():
    from agentic_core.prompt_governance.security.validators.output_schema_validator import (
        validate_healer_reentry,
    )

    ok, code = validate_healer_reentry({"healing_proposal": True, "reentry_gate": True})
    assert ok is True
    assert code is None


def test_healer_reentry_missing_gate_fails():
    from agentic_core.prompt_governance.security.validators.output_schema_validator import (
        validate_healer_reentry,
    )

    ok, code = validate_healer_reentry({"healing_proposal": True})
    assert ok is False
    assert code == "HEALER_REENTRY_VIOLATION"


def test_healer_reentry_gate_false_fails():
    from agentic_core.prompt_governance.security.validators.output_schema_validator import (
        validate_healer_reentry,
    )

    ok, code = validate_healer_reentry({"healing_proposal": True, "reentry_gate": False})
    assert ok is False
    assert code == "HEALER_REENTRY_VIOLATION"


def test_healer_reentry_no_healing_proposal_passes():
    from agentic_core.prompt_governance.security.validators.output_schema_validator import (
        validate_healer_reentry,
    )

    ok, code = validate_healer_reentry({"other": "data"})
    assert ok is True
    assert code is None


def test_healer_reentry_mutation_marker_fails():
    from agentic_core.prompt_governance.security.validators.output_schema_validator import (
        validate_healer_reentry,
    )

    ok, code = validate_healer_reentry(
        {"healing_proposal": True, "reentry_gate": True, "action": "durable_write"}
    )
    assert ok is False
    assert code == "HEALER_REENTRY_VIOLATION"


def test_healer_reentry_error_code_is_uppercase():
    from agentic_core.prompt_governance.security.validators import output_schema_validator as osv

    assert osv.HEALER_REENTRY_VIOLATION == osv.HEALER_REENTRY_VIOLATION.upper()


def test_healer_reentry_non_dict_fails():
    from agentic_core.prompt_governance.security.validators.output_schema_validator import (
        validate_healer_reentry,
    )

    ok, code = validate_healer_reentry("not a dict")  # type: ignore[arg-type]
    assert ok is False
    assert code == "HEALER_REENTRY_VIOLATION"


# ---------------------------------------------------------------------------
# Airlock enforcement in assembler
# ---------------------------------------------------------------------------


def test_airlock_violation_raised_on_u0_bypass_flag():
    from agentic_core.prompt_governance.contracts.slot_contracts import AirlockViolationError

    a = _make_assembler()
    with pytest.raises(AirlockViolationError, match="AIRLOCK_VIOLATION"):
        a.assemble(
            role="Agent",
            objective="Test",
            context_data=_VALID_CONTEXT,
            injections=[],
            metadata={"_u0_bypass": True},
        )


def test_airlock_not_raised_without_bypass_flag():
    a = _make_assembler()
    text = a.assemble(
        role="Agent",
        objective="Test",
        context_data=_VALID_CONTEXT,
        injections=[],
        metadata={"other": "data"},
    )
    assert isinstance(text, str)


# ---------------------------------------------------------------------------
# Healer directive injection in assembler
# ---------------------------------------------------------------------------


def test_healer_directive_injected_in_d0_when_healing_proposal():
    a = _make_assembler()
    text = a.assemble(
        role="Agent",
        objective="Test",
        context_data=_VALID_CONTEXT,
        injections=[],
        metadata={"healing_proposal": True, "reentry_gate": True},
    )
    assert "<HEALER_DIRECTIVE>" in text


def test_healer_directive_not_injected_without_healing_flag():
    from agentic_core.prompt_governance.core.invariant_registry import ITERATIVE_FEEDBACK_DIRECTIVE

    a = _make_assembler()
    text = a.assemble(
        role="Agent",
        objective="Test",
        context_data=_VALID_CONTEXT,
        injections=[],
    )
    assert ITERATIVE_FEEDBACK_DIRECTIVE not in text


def test_assembler_rejects_healing_proposal_without_reentry_gate():
    from agentic_core.prompt_governance.core.prompt_assembler import SecurityIntegrityError

    a = _make_assembler()
    with pytest.raises(SecurityIntegrityError, match="HEALER_REENTRY_VIOLATION"):
        a.assemble(
            role="Agent",
            objective="Test",
            context_data=_VALID_CONTEXT,
            injections=[],
            metadata={"healing_proposal": True},
        )
