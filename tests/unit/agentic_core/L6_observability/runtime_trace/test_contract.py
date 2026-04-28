"""Tests for the runtime trace contract loader and validator.

Covers W1.1 of plan ``assurance-p1-gates-ab4758``.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_core.L6_observability.runtime_trace import (
    ContractValidationError,
    load_contract,
    validate_trace,
)
from agentic_core.L6_observability.runtime_trace.contract import (
    RequiredEdge,
    RequiredSpan,
    RuntimeTraceContract,
)


REPO_ROOT = Path(__file__).resolve().parents[5]
CANARY_LIC_PATH = REPO_ROOT / "config" / "runtime_trace" / "contracts" / "canary_lic_v1.yaml"


# ---------------------------------------------------------------------------
# Helpers — minimal valid trace fixture
# ---------------------------------------------------------------------------


def _valid_lic_trace() -> list[dict]:
    """Return a span graph that satisfies canary.lic.v1 fully."""
    base_attrs = {"trace_id": "T1", "route_id": "R1"}
    return [
        {
            "name": "u0.intake",
            "layer": "L0",
            "parent_name": None,
            "attributes": {**base_attrs, "tier": "T2"},
        },
        {
            "name": "l0.route",
            "layer": "L0",
            "parent_name": "u0.intake",
            "attributes": {**base_attrs, "selected_route": "lic.standard"},
        },
        {
            "name": "c0.retrieval",
            "layer": "L1",
            "parent_name": "l0.route",
            "attributes": {**base_attrs, "retrieval_mode": "hybrid", "k": 5},
            "edges": [{"to": "pa.assemble", "kind": "flows_to"}],
        },
        {
            "name": "pa.assemble",
            "layer": "L1",
            "parent_name": "c0.retrieval",
            "attributes": {**base_attrs, "prompt_packet_id": "PP-1"},
        },
        {
            "name": "l2.execute",
            "layer": "L2",
            "parent_name": "pa.assemble",
            "attributes": {**base_attrs, "tool_call_count": 2},
            "edges": [{"to": "uwg.commit", "kind": "writes_to"}],
        },
        {
            "name": "exit.disposition",
            "layer": "L2",
            "parent_name": "l2.execute",
            "attributes": {
                **base_attrs,
                "disposition": "X3.PASS",
                "evidence_packet_id": "EV-1",
            },
        },
        {
            "name": "uwg.commit",
            "layer": "L4",
            "parent_name": "exit.disposition",
            "attributes": {
                **base_attrs,
                "evidence_hash": "abc",
                "actor": "lic-canary",
                "reason": "exit.commit",
                "write": True,
                "uwg": True,
            },
        },
    ]


# ---------------------------------------------------------------------------
# Loader tests
# ---------------------------------------------------------------------------


class TestLoadContract:
    def test_loads_canary_lic_v1(self) -> None:
        contract = load_contract("canary.lic.v1")
        assert contract.contract_id == "canary.lic.v1"
        assert contract.version == 1
        assert len(contract.required_spans) == 7
        assert contract.required_spans[0].name == "u0.intake"
        assert contract.required_spans[0].parent is None
        assert contract.required_spans[-1].name == "uwg.commit"
        assert "direct_l4_write_outside_uwg" in contract.forbidden
        assert "trace_id" in contract.invariant_attributes

    def test_missing_contract_raises_filenotfound(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError, match="runtime_trace_contract_unresolved"):
            load_contract("nonexistent.v1", root=tmp_path)

    def test_malformed_yaml_raises_validation_error(self, tmp_path: Path) -> None:
        bad = tmp_path / "broken_v1.yaml"
        bad.write_text("contract_id: broken.v1\n[ unclosed", encoding="utf-8")
        with pytest.raises(ContractValidationError, match="invalid YAML"):
            load_contract("broken.v1", root=tmp_path)

    def test_top_level_not_mapping_raises(self, tmp_path: Path) -> None:
        bad = tmp_path / "scalar_v1.yaml"
        bad.write_text("just-a-string", encoding="utf-8")
        with pytest.raises(ContractValidationError, match="top-level must be a mapping"):
            load_contract("scalar.v1", root=tmp_path)

    def test_contract_id_mismatch_raises(self, tmp_path: Path) -> None:
        bad = tmp_path / "x_v1.yaml"
        bad.write_text("contract_id: y.v1\nversion: 1\n", encoding="utf-8")
        with pytest.raises(ContractValidationError, match="contract_id mismatch"):
            load_contract("x.v1", root=tmp_path)

    def test_unsupported_version_raises(self, tmp_path: Path) -> None:
        bad = tmp_path / "x_v1.yaml"
        bad.write_text("contract_id: x.v1\nversion: 99\n", encoding="utf-8")
        with pytest.raises(ContractValidationError, match="unsupported version"):
            load_contract("x.v1", root=tmp_path)

    def test_unknown_layer_raises(self, tmp_path: Path) -> None:
        path = tmp_path / "x_v1.yaml"
        path.write_text(
            "contract_id: x.v1\nversion: 1\nrequired_spans:\n"
            "  - name: foo\n    layer: L99\n    parent: null\n",
            encoding="utf-8",
        )
        with pytest.raises(ContractValidationError, match="unknown layer"):
            load_contract("x.v1", root=tmp_path)

    def test_unknown_edge_kind_raises(self, tmp_path: Path) -> None:
        path = tmp_path / "x_v1.yaml"
        path.write_text(
            "contract_id: x.v1\nversion: 1\nrequired_edges:\n"
            "  - from: a\n    to: b\n    kind: bogus\n",
            encoding="utf-8",
        )
        with pytest.raises(ContractValidationError, match="unknown kind"):
            load_contract("x.v1", root=tmp_path)


# ---------------------------------------------------------------------------
# Validator tests — happy path + each violation kind
# ---------------------------------------------------------------------------


class TestValidateTrace:
    def test_valid_trace_passes(self) -> None:
        contract = load_contract("canary.lic.v1")
        result = validate_trace(contract, _valid_lic_trace())
        assert result.ok, f"expected pass; violations={result.violations!r}"
        assert result.contract_id == "canary.lic.v1"
        assert result.spans_seen == 7
        assert result.violations == ()

    def test_missing_span_flagged(self) -> None:
        contract = load_contract("canary.lic.v1")
        spans = [s for s in _valid_lic_trace() if s["name"] != "uwg.commit"]
        result = validate_trace(contract, spans)
        assert not result.ok
        kinds = {v.kind for v in result.violations}
        assert "missing_span" in kinds

    def test_wrong_layer_flagged(self) -> None:
        contract = load_contract("canary.lic.v1")
        spans = _valid_lic_trace()
        for s in spans:
            if s["name"] == "c0.retrieval":
                s["layer"] = "L2"  # wrong
        result = validate_trace(contract, spans)
        assert not result.ok
        assert any(v.kind == "wrong_layer" for v in result.violations)

    def test_wrong_parent_flagged(self) -> None:
        contract = load_contract("canary.lic.v1")
        spans = _valid_lic_trace()
        for s in spans:
            if s["name"] == "pa.assemble":
                s["parent_name"] = "u0.intake"  # skipped C0
        result = validate_trace(contract, spans)
        assert not result.ok
        assert any(v.kind == "wrong_parent" for v in result.violations)

    def test_missing_attribute_flagged(self) -> None:
        contract = load_contract("canary.lic.v1")
        spans = _valid_lic_trace()
        for s in spans:
            if s["name"] == "uwg.commit":
                s["attributes"] = {
                    k: v for k, v in s["attributes"].items() if k != "evidence_hash"
                }
        result = validate_trace(contract, spans)
        assert not result.ok
        assert any(
            v.kind == "missing_attribute" and "evidence_hash" in v.detail
            for v in result.violations
        )

    def test_missing_semantic_edge_flagged(self) -> None:
        contract = load_contract("canary.lic.v1")
        spans = _valid_lic_trace()
        for s in spans:
            if s["name"] == "l2.execute":
                s["edges"] = []  # remove writes_to edge
        result = validate_trace(contract, spans)
        assert not result.ok
        assert any(
            v.kind == "missing_edge" and "writes_to" in v.detail
            for v in result.violations
        )

    def test_cross_layer_skip_flagged(self) -> None:
        # Synthetic mini-contract enabling cross_layer_skip detection.
        contract = RuntimeTraceContract(
            contract_id="t.skip.v1",
            version=1,
            description="",
            required_spans=(
                RequiredSpan(name="root", layer="L0", parent=None),
                RequiredSpan(name="leaf", layer="L3", parent="root"),
            ),
            required_edges=(),
            forbidden=("cross_layer_skip",),
            invariant_attributes=(),
        )
        spans = [
            {"name": "root", "layer": "L0", "parent_name": None, "attributes": {}},
            {"name": "leaf", "layer": "L3", "parent_name": "root", "attributes": {}},
        ]
        result = validate_trace(contract, spans)
        assert not result.ok
        assert any(v.kind == "cross_layer_skip" for v in result.violations)

    def test_direct_l4_write_outside_uwg_flagged(self) -> None:
        contract = load_contract("canary.lic.v1")
        spans = _valid_lic_trace()
        # Inject illegal direct L4 write outside UWG.
        spans.append(
            {
                "name": "l4.bypass.write",
                "layer": "L4",
                "parent_name": "l2.execute",  # NOT a UWG span
                "attributes": {"trace_id": "T1", "route_id": "R1", "write": True},
            }
        )
        result = validate_trace(contract, spans)
        assert not result.ok
        assert any(
            v.kind == "direct_l4_write_outside_uwg" for v in result.violations
        )

    def test_swallowed_exception_flagged(self) -> None:
        contract = RuntimeTraceContract(
            contract_id="t.swallow.v1",
            version=1,
            description="",
            required_spans=(),
            required_edges=(),
            forbidden=("swallowed_exception",),
            invariant_attributes=(),
        )
        spans = [
            {"name": "root", "layer": "L0", "parent_name": None, "attributes": {}},
            {
                "name": "child",
                "layer": "L1",
                "parent_name": "root",
                "attributes": {},
                "status": "error",
            },
        ]
        result = validate_trace(contract, spans)
        assert not result.ok
        assert any(v.kind == "swallowed_exception" for v in result.violations)

    def test_swallowed_exception_with_recover_passes(self) -> None:
        contract = RuntimeTraceContract(
            contract_id="t.swallow.v1",
            version=1,
            description="",
            required_spans=(),
            required_edges=(),
            forbidden=("swallowed_exception",),
            invariant_attributes=(),
        )
        spans = [
            {"name": "root", "layer": "L0", "parent_name": None, "attributes": {}},
            {
                "name": "child",
                "layer": "L1",
                "parent_name": "root",
                "attributes": {},
                "status": "error",
            },
            {
                "name": "recover.retry",
                "layer": "L1",
                "parent_name": "root",
                "attributes": {},
                "status": "ok",
            },
        ]
        result = validate_trace(contract, spans)
        assert result.ok, f"expected pass; violations={result.violations!r}"

    def test_invariant_attribute_drift_flagged(self) -> None:
        contract = load_contract("canary.lic.v1")
        spans = _valid_lic_trace()
        for s in spans:
            if s["name"] == "uwg.commit":
                s["attributes"]["trace_id"] = "T_DIFFERENT"
        result = validate_trace(contract, spans)
        assert not result.ok
        assert any(
            v.kind == "invariant_attribute_drift" for v in result.violations
        )

    def test_missing_trace_id_attribute_flagged(self) -> None:
        contract = RuntimeTraceContract(
            contract_id="t.tid.v1",
            version=1,
            description="",
            required_spans=(),
            required_edges=(),
            forbidden=("missing_trace_id_attribute",),
            invariant_attributes=(),
        )
        spans = [
            {"name": "x", "layer": "L0", "parent_name": None, "attributes": {}},
        ]
        result = validate_trace(contract, spans)
        assert not result.ok
        assert any(
            v.kind == "missing_trace_id_attribute" for v in result.violations
        )

    def test_parent_child_required_edge(self) -> None:
        contract = RuntimeTraceContract(
            contract_id="t.pc.v1",
            version=1,
            description="",
            required_spans=(
                RequiredSpan(name="a", layer="L0", parent=None),
                RequiredSpan(name="b", layer="L1", parent="a"),
            ),
            required_edges=(RequiredEdge(from_span="a", to_span="b", kind="parent_child"),),
            forbidden=(),
            invariant_attributes=(),
        )
        # b's parent is wrong — so parent_child edge from a to b is missing.
        spans = [
            {"name": "a", "layer": "L0", "parent_name": None, "attributes": {}},
            {"name": "b", "layer": "L1", "parent_name": "elsewhere", "attributes": {}},
        ]
        result = validate_trace(contract, spans)
        assert not result.ok
        # Two violations expected: wrong_parent on b, plus missing_edge.
        kinds = {v.kind for v in result.violations}
        assert "missing_edge" in kinds


# ---------------------------------------------------------------------------
# Sanity check on shipped contract file
# ---------------------------------------------------------------------------


class TestShippedContract:
    def test_canary_lic_v1_file_exists(self) -> None:
        assert CANARY_LIC_PATH.is_file(), f"expected {CANARY_LIC_PATH} to exist"

    def test_canary_lic_v1_loads_clean(self) -> None:
        contract = load_contract("canary.lic.v1")
        # Every required_spans entry references a parent that is either None
        # or another required span — graph is internally consistent.
        names = {s.name for s in contract.required_spans}
        for span in contract.required_spans:
            if span.parent is not None:
                assert span.parent in names, (
                    f"contract canary.lic.v1: span {span.name!r} references "
                    f"unknown parent {span.parent!r}"
                )
