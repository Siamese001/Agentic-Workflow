"""W3C: runtime gate ``contracts`` facade is identity-bound to ``types``."""

from __future__ import annotations

import pytest

from agentic_core.L5_safety.runtime_gates import contracts
from agentic_core.L5_safety.runtime_gates import types as types_impl


@pytest.mark.parametrize(
    "name",
    [
        "SCHEMA_VERSION",
        "DecisionAlias",
        "Disposition",
        "GateContext",
        "GateDecision",
        "GraderType",
        "RegressionSignal",
        "Result",
        "Severity",
    ],
)
def test_contract_exports_match_types_module(name: str) -> None:
    assert getattr(contracts, name) is getattr(types_impl, name)


def test_gate_decision_disposition_semantics_unchanged() -> None:
    d = contracts.GateDecision(
        gate_id="G99",
        disposition=contracts.Disposition.ALLOW,
        result=contracts.Result.PASS,
        severity=contracts.Severity.INFO,
    )
    assert d.disposition is types_impl.Disposition.ALLOW
    assert d.to_verdict()["disposition"] == types_impl.Disposition.ALLOW.value
    assert d.to_verdict()["result"] == types_impl.Result.PASS.value
