"""W5 — schema_version standardization + signature field tests.

Covers D8 (all 11 contracts carry ``schema_version``) and D9 (all 11
contracts carry ``signature``; HMAC helper round-trips correctly).

Expected to grow to ~20 assertions per plan "+20 tests" DoD.
"""
from __future__ import annotations

import json
import dataclasses
import importlib
import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fields(cls) -> dict[str, dataclasses.Field]:
    return {f.name: f for f in dataclasses.fields(cls)}


# ---------------------------------------------------------------------------
# Contract imports (lazy so CI finds import errors immediately)
# ---------------------------------------------------------------------------

from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest
from agentic_core.runtime.contracts.l1_plan_contract import L1PlanContract
from agentic_core.runtime.contracts.route_contract import RouteContract
from agentic_core.runtime.contracts.final_evidence_contract import FinalEvidenceContract
from agentic_core.runtime.contracts.compiled_prompt_artifact import CompiledPromptArtifact
from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact
from agentic_core.runtime.contracts.x3_disposition import X3Disposition
from agentic_core.runtime.contracts.l3_runtime_orchestration_receipt import L3RuntimeOrchestrationReceipt
from agentic_core.L6_observability.runtime_trace.runtime_exhaust_bundle import RuntimeExhaustBundle
from agentic_core.L4_state.contracts.records import CommitRequest
from agentic_core.runtime.contracts.signature import (
    compute_contract_hmac,
    verify_contract_hmac,
    UNVERIFIED,
)

# All 11 contracts in insertion order for parametric tests
_ALL_CONTRACTS = [
    ValidatedRequest,
    L1PlanContract,
    RouteContract,
    FinalEvidenceContract,
    CompiledPromptArtifact,
    SealedL2Artifact,
    X3Disposition,
    L3RuntimeOrchestrationReceipt,
    RuntimeExhaustBundle,
    CommitRequest,
]

# ---------------------------------------------------------------------------
# D8 — schema_version field present on all contracts
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("cls", _ALL_CONTRACTS)
def test_schema_version_field_exists(cls):
    """Every emit contract must declare a 'schema_version' field."""
    assert "schema_version" in _fields(cls), (
        f"{cls.__name__} missing schema_version field"
    )


@pytest.mark.parametrize("cls", _ALL_CONTRACTS)
def test_schema_version_is_str(cls):
    """schema_version must be typed as str."""
    f = _fields(cls)["schema_version"]
    assert f.type in (str, "str"), (
        f"{cls.__name__}.schema_version must be str, got {f.type!r}"
    )


def test_validated_request_schema_version_default():
    assert _fields(ValidatedRequest)["schema_version"].default == "W6.0"


def test_l1_plan_contract_schema_version_default():
    assert _fields(L1PlanContract)["schema_version"].default == "W6.0"


def test_route_contract_schema_version_default():
    assert _fields(RouteContract)["schema_version"].default == "W6.0"


def test_final_evidence_contract_schema_version_default():
    assert _fields(FinalEvidenceContract)["schema_version"].default == "W6.0"


def test_compiled_prompt_artifact_schema_version_default():
    assert _fields(CompiledPromptArtifact)["schema_version"].default == "W6.0"


def test_sealed_l2_artifact_schema_version_default():
    assert _fields(SealedL2Artifact)["schema_version"].default == "W6.0"


def test_x3_disposition_schema_version_default():
    assert _fields(X3Disposition)["schema_version"].default == "W6.0"


# L3 receipt has L3_RUNTIME_RECEIPT_SCHEMA_VERSION = "1.0"
def test_l3_receipt_schema_version_default():
    from agentic_core.runtime.contracts.l3_runtime_orchestration_receipt import (
        L3_RUNTIME_RECEIPT_SCHEMA_VERSION,
    )
    f = _fields(L3RuntimeOrchestrationReceipt)["schema_version"]
    assert f.default == L3_RUNTIME_RECEIPT_SCHEMA_VERSION


def test_runtime_exhaust_bundle_schema_version_default():
    assert _fields(RuntimeExhaustBundle)["schema_version"].default == "1.0"


def test_commit_request_schema_version_default():
    from agentic_core.L4_state.contracts.records import L4_CONTRACT_SCHEMA_VERSION
    f = _fields(CommitRequest)["schema_version"]
    assert f.default == L4_CONTRACT_SCHEMA_VERSION


# D8 — old field names must NOT appear
def test_plan_version_field_removed():
    assert "plan_version" not in _fields(L1PlanContract)


def test_route_version_field_removed():
    assert "route_version" not in _fields(RouteContract)


def test_contract_version_field_removed_fec():
    assert "contract_version" not in _fields(FinalEvidenceContract)


def test_assembly_version_field_removed():
    assert "assembly_version" not in _fields(CompiledPromptArtifact)


def test_contract_version_field_removed_sealed():
    assert "contract_version" not in _fields(SealedL2Artifact)


def test_disposition_version_field_removed():
    assert "disposition_version" not in _fields(X3Disposition)


# ---------------------------------------------------------------------------
# D9 — signature field present and defaults to empty string
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("cls", _ALL_CONTRACTS)
def test_signature_field_exists(cls):
    """Every emit contract must declare a 'signature' field."""
    assert "signature" in _fields(cls), (
        f"{cls.__name__} missing signature field"
    )


@pytest.mark.parametrize("cls", _ALL_CONTRACTS)
def test_signature_default_empty(cls):
    """signature must default to empty string (unsigned = UNVERIFIED, not INVALID)."""
    f = _fields(cls)["signature"]
    assert f.default == "", (
        f"{cls.__name__}.signature default must be '' (unsigned), got {f.default!r}"
    )


# ---------------------------------------------------------------------------
# D9 — HMAC helper correctness
# ---------------------------------------------------------------------------

_KEY = b"test-key-w5"
_PAYLOAD = b'{"schema_version": "W6.0", "run_id": "r1"}'


def test_compute_hmac_returns_hex_string():
    sig = compute_contract_hmac(_PAYLOAD, key=_KEY)
    assert isinstance(sig, str)
    assert len(sig) == 64  # SHA-256 hex


def test_compute_hmac_no_key_returns_empty():
    sig = compute_contract_hmac(_PAYLOAD, key=None)
    # Without W6_CONTRACT_HMAC_KEY env var set, returns empty string
    import os
    if "W6_CONTRACT_HMAC_KEY" not in os.environ:
        assert sig == ""


def test_verify_hmac_ok():
    sig = compute_contract_hmac(_PAYLOAD, key=_KEY)
    result = verify_contract_hmac(_PAYLOAD, sig, key=_KEY)
    assert result == "OK"


def test_verify_hmac_invalid_on_tamper():
    sig = compute_contract_hmac(_PAYLOAD, key=_KEY)
    tampered = _PAYLOAD + b" "
    result = verify_contract_hmac(tampered, sig, key=_KEY)
    assert result == "INVALID"


def test_verify_hmac_unverified_no_key():
    import os
    if "W6_CONTRACT_HMAC_KEY" not in os.environ:
        result = verify_contract_hmac(_PAYLOAD, "somesig", key=None)
        assert result == UNVERIFIED


def test_verify_hmac_unverified_empty_sig():
    result = verify_contract_hmac(_PAYLOAD, "", key=_KEY)
    assert result == UNVERIFIED


def test_compute_hmac_string_key():
    sig1 = compute_contract_hmac(_PAYLOAD, key=_KEY)
    sig2 = compute_contract_hmac(_PAYLOAD, key=_KEY.decode("utf-8"))
    assert sig1 == sig2


def test_unverified_sentinel_is_string():
    assert isinstance(UNVERIFIED, str)
    assert UNVERIFIED == "UNVERIFIED"
