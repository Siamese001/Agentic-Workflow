"""Unit tests for agentic_core.runtime.contracts.l3_to_l2_step_contract.

Wave 6.1 (P2 untested-module coverage) — L3->L2 managed-workflow step handoff.
Purely declarative frozen dataclass with all-default fields and an as_dict/
as_json projection. Covers defaults, frozen immutability, tuple-listification
in as_dict, and JSON round-trip completeness (every field present).
"""

from __future__ import annotations

import dataclasses
import json

import pytest

from agentic_core.runtime.contracts.l3_to_l2_step_contract import L3ToL2StepContract


class TestDefaults:
    def test_minimal_construction(self) -> None:
        c = L3ToL2StepContract()
        assert c.node_attempt == 1
        assert c.side_effect_class == "none"
        assert c.allowed_execution_lane == "ENSEMBLE_MODEL"
        assert c.candidate_count == 3
        assert c.pa_is_valid is True
        assert c.schema_version == "W7.a3f7e2"

    def test_tuple_defaults_independent(self) -> None:
        a = L3ToL2StepContract()
        b = L3ToL2StepContract()
        assert a.parent_node_refs == ()
        assert a.tool_allowlist is not b.tool_allowlist or a.tool_allowlist == ()


class TestImmutability:
    def test_frozen(self) -> None:
        c = L3ToL2StepContract()
        with pytest.raises(dataclasses.FrozenInstanceError):
            c.node_id = "x"  # type: ignore[misc]


class TestAsDict:
    def test_lists_tuple_fields(self) -> None:
        c = L3ToL2StepContract(
            parent_node_refs=("p1",),
            dependency_refs=("d1", "d2"),
            authority_order=("S0", "D0"),
        )
        d = c.as_dict()
        assert d["parent_node_refs"] == ["p1"]
        assert d["dependency_refs"] == ["d1", "d2"]
        assert d["authority_order"] == ["S0", "D0"]
        assert all(isinstance(d[k], list) for k in ("parent_node_refs", "dependency_refs"))

    def test_scalar_fields_passthrough(self) -> None:
        c = L3ToL2StepContract(contract_id="ctr-1", node_id="header", node_attempt=2)
        d = c.as_dict()
        assert d["contract_id"] == "ctr-1"
        assert d["node_id"] == "header"
        assert d["node_attempt"] == 2

    def test_as_dict_covers_every_field(self) -> None:
        c = L3ToL2StepContract()
        field_names = {f.name for f in dataclasses.fields(c)}
        # as_dict serialises every declared field
        assert field_names.issubset(set(c.as_dict().keys()))

    def test_pa_failure_fields(self) -> None:
        c = L3ToL2StepContract(pa_is_valid=False, pa_failure_reason="resolver miss")
        d = c.as_dict()
        assert d["pa_is_valid"] is False
        assert d["pa_failure_reason"] == "resolver miss"


class TestAsJson:
    def test_round_trip(self) -> None:
        c = L3ToL2StepContract(contract_id="c1", evidence_refs=("e1",))
        parsed = json.loads(c.as_json())
        assert parsed == c.as_dict()
        assert parsed["contract_id"] == "c1"
        assert parsed["evidence_refs"] == ["e1"]

    def test_compact_separators(self) -> None:
        c = L3ToL2StepContract()
        assert ", " not in c.as_json()  # compact separators (",", ":")
