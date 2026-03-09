"""Negative-first tests for Phase 2 prompt governance contracts + enforcement.

All tests are deterministic and minimal.
Tests fail if enforcement is removed.
"""

from __future__ import annotations

import ast
import copy
from pathlib import Path
from unittest.mock import patch

import pytest

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
)

pytestmark = pytest.mark.unit_min_deps

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _repo_root() -> Path:
    """Walk up from this file until pytest.ini is found (repo root sentinel)."""
    p = Path(__file__).resolve()
    for parent in p.parents:
        if (parent / "pytest.ini").exists():
            return parent
    raise RuntimeError("Could not locate repo root (pytest.ini not found)")


CONTRACTS_PATH = _repo_root() / AGENTIC_CORE_DIR / "prompt_governance" / "contracts" / "context_contracts.py"

_VALID_RETRIEVAL = {"namespace": "ns1", "max_k": 5, "version": "v1"}
_VALID_CITATION = {
    "source_doc_id": "doc1",
    "offset_start": 0,
    "offset_end": 10,
    "timestamp": "2026-01-01T00:00:00Z",
}


def _vcc(payload):
    """Import fresh each call to avoid _invariant_validated caching issues."""
    from agentic_core.prompt_governance.security.validators.output_schema_validator import (
        validate_context_contract,
    )

    return validate_context_contract(payload)


# ---------------------------------------------------------------------------
# validate_context_contract — citations
# ---------------------------------------------------------------------------


def test_citations_missing_required_fields_returns_false_and_empty_normalized():
    ok, code, normalized = _vcc({"citations": [{"source_doc_id": "x"}]})
    assert ok is False
    assert code == "MISSING_CITATION_FIELDS"
    assert normalized == {}


def test_citations_valid_passes():
    ok, code, normalized = _vcc({"citations": [_VALID_CITATION]})
    assert ok is True
    assert code is None
    assert "citations" in normalized


# ---------------------------------------------------------------------------
# validate_context_contract — retrieval_metadata
# ---------------------------------------------------------------------------


def test_retrieval_missing_version_returns_incomplete():
    ok, code, normalized = _vcc({"retrieval_metadata": {"namespace": "ns", "max_k": 3}})
    assert ok is False
    assert code == "INCOMPLETE_RETRIEVAL_METADATA"
    assert normalized == {}


def test_retrieval_missing_namespace_returns_incomplete():
    ok, code, normalized = _vcc({"retrieval_metadata": {"max_k": 3, "version": "v1"}})
    assert ok is False
    assert code == "INCOMPLETE_RETRIEVAL_METADATA"
    assert normalized == {}


def test_retrieval_max_k_zero_returns_constraint_error():
    ok, code, normalized = _vcc({"retrieval_metadata": {"namespace": "ns", "max_k": 0, "version": "v1"}})
    assert ok is False
    assert code == "INVALID_RETRIEVAL_FIELD_CONSTRAINT"
    assert normalized == {}


def test_retrieval_max_k_negative_returns_constraint_error():
    ok, code, normalized = _vcc({"retrieval_metadata": {"namespace": "ns", "max_k": -1, "version": "v1"}})
    assert ok is False
    assert code == "INVALID_RETRIEVAL_FIELD_CONSTRAINT"
    assert normalized == {}


def test_retrieval_empty_namespace_returns_constraint_error():
    ok, code, normalized = _vcc({"retrieval_metadata": {"namespace": "", "max_k": 5, "version": "v1"}})
    assert ok is False
    assert code == "INVALID_RETRIEVAL_FIELD_CONSTRAINT"
    assert normalized == {}


def test_retrieval_empty_version_returns_constraint_error():
    ok, code, normalized = _vcc({"retrieval_metadata": {"namespace": "ns", "max_k": 5, "version": ""}})
    assert ok is False
    assert code == "INVALID_RETRIEVAL_FIELD_CONSTRAINT"
    assert normalized == {}


# ---------------------------------------------------------------------------
# validate_context_contract — forbidden verbs (scoped to retrieval_metadata)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("verb", ["write", "modify", "update", "delete"])
def test_retrieval_contains_forbidden_verb_key_fails(verb):
    rm = dict(_VALID_RETRIEVAL)
    rm[verb] = "some_value"
    ok, code, normalized = _vcc({"retrieval_metadata": rm})
    assert ok is False
    assert code == "MUTATION_VERB_IN_RETRIEVAL"
    assert normalized == {}


def test_forbidden_verb_outside_retrieval_metadata_does_not_trigger():
    """Forbidden verbs are scoped: top-level key 'write' must NOT fail when no retrieval_metadata."""
    ok, code, normalized = _vcc({"write": "something"})
    assert ok is True
    assert code is None


# ---------------------------------------------------------------------------
# validate_context_contract — normalization
# ---------------------------------------------------------------------------


def test_drops_unknown_retrieval_keys_in_normalized():
    rm = dict(_VALID_RETRIEVAL)
    rm["extra_key"] = "should_be_dropped"
    ok, code, normalized = _vcc({"retrieval_metadata": rm})
    assert ok is True
    assert code is None
    assert set(normalized["retrieval_metadata"].keys()) == {"namespace", "max_k", "version"}


def test_normalized_is_not_same_object_as_payload():
    payload = {"retrieval_metadata": dict(_VALID_RETRIEVAL)}
    ok, code, normalized = _vcc(payload)
    assert ok is True
    assert normalized is not payload


def test_does_not_mutate_input_payload():
    payload = {"retrieval_metadata": dict(_VALID_RETRIEVAL), "other": "data"}
    original = copy.deepcopy(payload)
    _vcc(payload)
    assert payload == original


# ---------------------------------------------------------------------------
# validate_context_contract — error codes are uppercase strings
# ---------------------------------------------------------------------------


def test_error_codes_are_uppercase_strings():
    from agentic_core.prompt_governance.security.validators import output_schema_validator as osv

    codes = [
        osv.MISSING_CITATION_FIELDS,
        osv.INCOMPLETE_RETRIEVAL_METADATA,
        osv.MUTATION_VERB_IN_RETRIEVAL,
        osv.INVALID_RETRIEVAL_FIELD_CONSTRAINT,
    ]
    for code in codes:
        assert isinstance(code, str)
        assert code == code.upper()


# ---------------------------------------------------------------------------
# contracts — no pydantic import
# ---------------------------------------------------------------------------


def test_context_contracts_has_no_pydantic_import():
    source = CONTRACTS_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert "pydantic" not in alias.name, (
                        f"pydantic import found in context_contracts.py: {alias.name}"
                    )
            else:
                assert node.module is None or "pydantic" not in node.module, (
                    f"pydantic import found in context_contracts.py: {node.module}"
                )


# ---------------------------------------------------------------------------
# invariant registry
# ---------------------------------------------------------------------------


def test_validate_invariant_registry_succeeds():
    from agentic_core.prompt_governance.core.invariant_registry import validate_invariant_registry

    validate_invariant_registry()  # must not raise


def test_invariant_registry_called_on_first_use_via_validate_context_contract():
    """Spy: validate_against_schema must be called (via validate_invariant_registry) on first use."""
    import agentic_core.prompt_governance.security.validators.output_schema_validator as osv

    # Reset the module-level flag so first-use fires
    original = osv._invariant_validated
    osv._invariant_validated = False
    try:
        call_log = []

        real_vas = osv.validate_against_schema

        def spy_vas(obj, schema):
            call_log.append((obj, schema))
            return real_vas(obj, schema)

        with patch.object(osv, "validate_against_schema", side_effect=spy_vas):
            # Call validate_context_contract — should trigger validate_invariant_registry
            osv.validate_context_contract({"other": "data"})

        assert len(call_log) >= 1, "validate_against_schema was not called on first use"
    finally:
        osv._invariant_validated = original


# ---------------------------------------------------------------------------
# assembler — single enforcement path
# ---------------------------------------------------------------------------


def test_assembler_rejects_non_dict_context_data_with_invalid_context_type():
    from agentic_core.prompt_governance.core.prompt_assembler import (
        PromptAssembler,
        SecurityIntegrityError,
    )

    with patch(
        "agentic_core.prompt_governance.core.prompt_assembler.PromptAssembler._load_templates",
        return_value=None,
    ):
        assembler = PromptAssembler()
    with pytest.raises(SecurityIntegrityError, match="INVALID_CONTEXT_TYPE"):
        assembler.assemble(
            role="Agent",
            objective="Test",
            context_data="not a dict",
            injections=[],
        )


def test_assembler_cannot_bypass_validator_monkeypatch():
    """Meta-test: if validate_context_contract raises, assembler must propagate it."""
    from agentic_core.prompt_governance.core import prompt_assembler as pa
    from agentic_core.prompt_governance.core.prompt_assembler import (
        PromptAssembler,
        SecurityIntegrityError,
    )

    def _always_fail(payload):
        return (False, "MUTATION_VERB_IN_RETRIEVAL", {})

    with patch(
        "agentic_core.prompt_governance.core.prompt_assembler.PromptAssembler._load_templates",
        return_value=None,
    ):
        assembler = PromptAssembler()

    with patch.object(pa, "validate_context_contract", side_effect=_always_fail):
        with pytest.raises(SecurityIntegrityError, match="MUTATION_VERB_IN_RETRIEVAL"):
            assembler.assemble(
                role="Agent",
                objective="Test",
                context_data={"retrieval_metadata": _VALID_RETRIEVAL},
                injections=[],
            )


# ---------------------------------------------------------------------------
# Wave 3 — Capability wiring closure
# ---------------------------------------------------------------------------

_VALID_TELEMETRY = {"hit_rate": 0.9, "recall_estimate": 0.85, "empty_result_signal": False}


# telemetry_envelope validation
def test_telemetry_envelope_valid_passes():
    ok, code, normalized = _vcc({"telemetry_envelope": _VALID_TELEMETRY})
    assert ok is True
    assert code is None
    assert normalized["telemetry_envelope"] == _VALID_TELEMETRY


def test_telemetry_envelope_missing_hit_rate_fails():
    te = {"recall_estimate": 0.5, "empty_result_signal": True}
    ok, code, normalized = _vcc({"telemetry_envelope": te})
    assert ok is False
    assert code == "INVALID_TELEMETRY_ENVELOPE"
    assert normalized == {}


def test_telemetry_envelope_wrong_type_for_empty_result_signal_fails():
    te = {"hit_rate": 0.9, "recall_estimate": 0.5, "empty_result_signal": "yes"}
    ok, code, normalized = _vcc({"telemetry_envelope": te})
    assert ok is False
    assert code == "INVALID_TELEMETRY_ENVELOPE"
    assert normalized == {}


def test_telemetry_envelope_error_code_is_uppercase():
    from agentic_core.prompt_governance.security.validators import output_schema_validator as osv

    assert osv.INVALID_TELEMETRY_ENVELOPE == osv.INVALID_TELEMETRY_ENVELOPE.upper()


# iterative feedback directive
def test_iterative_feedback_directive_exists_and_is_non_empty():
    from agentic_core.prompt_governance.core.invariant_registry import ITERATIVE_FEEDBACK_DIRECTIVE

    assert isinstance(ITERATIVE_FEEDBACK_DIRECTIVE, str)
    assert len(ITERATIVE_FEEDBACK_DIRECTIVE) > 0


def test_iterative_feedback_directive_contains_no_mutation_authority():
    from agentic_core.prompt_governance.core.invariant_registry import ITERATIVE_FEEDBACK_DIRECTIVE

    lower = ITERATIVE_FEEDBACK_DIRECTIVE.lower()
    assert "no mutation" in lower or "read-only" in lower or "no authority" in lower


# structured field pass-through: all three contract sections in one payload
def test_full_structured_payload_passes_validator():
    payload = {
        "retrieval_metadata": _VALID_RETRIEVAL,
        "citations": [_VALID_CITATION],
        "telemetry_envelope": _VALID_TELEMETRY,
        "other": "data",
    }
    ok, code, normalized = _vcc(payload)
    assert ok is True
    assert code is None
    assert "retrieval_metadata" in normalized
    assert "citations" in normalized
    assert "telemetry_envelope" in normalized
    assert normalized["other"] == "data"


def test_full_structured_payload_normalized_is_copy():
    payload = {
        "retrieval_metadata": _VALID_RETRIEVAL,
        "citations": [_VALID_CITATION],
        "telemetry_envelope": _VALID_TELEMETRY,
    }
    ok, code, normalized = _vcc(payload)
    assert ok is True
    assert normalized is not payload
    assert normalized["retrieval_metadata"] is not payload["retrieval_metadata"]
