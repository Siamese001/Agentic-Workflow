"""Unit tests for Phase C.1 — read-only runtime ADG query adapter.

All tests use synthetic ``RuntimeADGNode`` / ``RuntimeADGSnapshot`` fixtures;
no live SQLite file is opened and no ``RuntimeADGQuery`` (static ADG) is imported.

Test plan reference: .windsurf/plans/runtime-cert-c1-query-adapter-7e3f92.md §6
"""

from __future__ import annotations

import json
import sys
from typing import Any

import pytest

from agentic_core.L6_system_learning.snapshot import (
    RuntimeADGNode,
    attributes_to_json,
    create_runtime_adg_snapshot,
)
from tools.runtime_cert.runtime_adg_query_adapter import (
    EVIDENCE_SOURCE_PREFIX,
    NOT_CERTIFIED,
    PHASE_C1_SCHEMA_VERSION,
    VALID_ROUTE_SHAPES,
    PhaseC1Row,
    build_test_snapshot,
    extract_attributes,
    iter_rows_for_trace,
    iter_rows_from_snapshot,
    node_to_row,
)

# ---------------------------------------------------------------------------
# Shared fixture factories
# ---------------------------------------------------------------------------


def _make_node(
    node_id: str = "span-001",
    name: str = "orchestrator.execute",
    kind: str = "orchestrator",
    layer: str = "L3",
    component: str = "apps_research",
    started_at_utc: int = 1_700_000_000_000,
    duration_ms: float = 123.4,
    status: str = "ok",
    attrs: dict[str, Any] | None = None,
) -> RuntimeADGNode:
    return RuntimeADGNode(
        node_id=node_id,
        name=name,
        kind=kind,
        layer=layer,
        component=component,
        started_at_utc=started_at_utc,
        duration_ms=duration_ms,
        status=status,
        attributes_json=attributes_to_json(attrs or {}),
    )


def _make_snapshot(
    nodes: list[RuntimeADGNode],
    trace_id: str = "trace-abc-123",
    started_at_utc: int = 1_700_000_000_000,
    ended_at_utc: int = 1_700_000_001_000,
):
    return create_runtime_adg_snapshot(
        trace_id=trace_id,
        mission="test",
        started_at_utc=started_at_utc,
        ended_at_utc=ended_at_utc,
        nodes=tuple(nodes),
        edges=(),
    )


# ---------------------------------------------------------------------------
# T1 — basic fields
# ---------------------------------------------------------------------------


def test_node_to_row_basic_fields():
    """T1: span_id, span_name, timestamp, evidence_source are correctly mapped."""
    node = _make_node(node_id="span-001", name="tool.search", started_at_utc=1_000_000)
    snapshot = _make_snapshot([node], trace_id="trace-xyz")
    row = node_to_row(node, snapshot_id=snapshot.snapshot_id, trace_id="trace-xyz")

    assert row.span_id == "span-001"
    assert row.span_name == "tool.search"
    assert row.timestamp == 1_000_000
    assert row.evidence_source.startswith(EVIDENCE_SOURCE_PREFIX)
    assert snapshot.snapshot_id in row.evidence_source


# ---------------------------------------------------------------------------
# T2 — attributes parsed
# ---------------------------------------------------------------------------


def test_node_to_row_attrs_parsed():
    """T2: attributes is a dict when attributes_json is valid JSON."""
    node = _make_node(attrs={"contract_name": "ValidatedRequest", "run_id": "r1"})
    snapshot = _make_snapshot([node])
    row = node_to_row(node, snapshot_id=snapshot.snapshot_id, trace_id=snapshot.trace_id)

    assert isinstance(row.attributes, dict)
    assert row.attributes["contract_name"] == "ValidatedRequest"
    assert row.attributes["run_id"] == "r1"


# ---------------------------------------------------------------------------
# T3 — malformed JSON
# ---------------------------------------------------------------------------


def test_node_to_row_attrs_malformed_json():
    """T3: attributes == {} and no exception when attributes_json is malformed."""
    node = RuntimeADGNode(
        node_id="bad-json",
        name="test.span",
        kind="tool",
        layer="L2",
        component="apps_test",
        started_at_utc=0,
        duration_ms=0.0,
        status="ok",
        attributes_json="{not valid json",
    )
    snapshot = _make_snapshot([node])
    row = node_to_row(node, snapshot_id=snapshot.snapshot_id, trace_id=snapshot.trace_id)

    assert row.attributes == {}


# ---------------------------------------------------------------------------
# T4 — parent_span_id extracted
# ---------------------------------------------------------------------------


def test_node_to_row_parent_span_id_extracted():
    """T4: parent_span_id extracted from attributes['parent_span_id']."""
    node = _make_node(attrs={"parent_span_id": "span-000"})
    snapshot = _make_snapshot([node])
    row = node_to_row(node, snapshot_id=snapshot.snapshot_id, trace_id=snapshot.trace_id)
    assert row.parent_span_id == "span-000"


# ---------------------------------------------------------------------------
# T5 — parent_span_id alias
# ---------------------------------------------------------------------------


def test_node_to_row_parent_span_id_alias():
    """T5: parent_span_id populated from attributes['parent_id'] when primary key absent."""
    node = _make_node(attrs={"parent_id": "span-999"})
    snapshot = _make_snapshot([node])
    row = node_to_row(node, snapshot_id=snapshot.snapshot_id, trace_id=snapshot.trace_id)
    assert row.parent_span_id == "span-999"


# ---------------------------------------------------------------------------
# T6 — contract_name is None
# ---------------------------------------------------------------------------


def test_node_to_row_contract_name_is_none():
    """T6: contract_name is None — C.1 never resolves contracts."""
    node = _make_node(attrs={"contract_name": "ValidatedRequest"})
    snapshot = _make_snapshot([node])
    row = node_to_row(node, snapshot_id=snapshot.snapshot_id, trace_id=snapshot.trace_id)
    assert row.contract_name is None


# ---------------------------------------------------------------------------
# T7 — normalized_cert_alias is None
# ---------------------------------------------------------------------------


def test_node_to_row_normalized_cert_alias_is_none():
    """T7: normalized_cert_alias is None — C.1 never resolves aliases."""
    node = _make_node()
    snapshot = _make_snapshot([node])
    row = node_to_row(node, snapshot_id=snapshot.snapshot_id, trace_id=snapshot.trace_id)
    assert row.normalized_cert_alias is None


# ---------------------------------------------------------------------------
# T8 — certification status invariant
# ---------------------------------------------------------------------------


def test_phase_c1_row_rejects_non_not_certified():
    """T8: constructing PhaseC1Row with any non-NOT_CERTIFIED value raises ValueError."""
    with pytest.raises(ValueError, match="NOT_CERTIFIED"):
        PhaseC1Row(
            app_name="apps_research",
            route_shape="R3_grounded_read",
            trace_id="t1",
            span_id="s1",
            parent_span_id=None,
            span_name="test",
            timestamp=0,
            runtime_certification_status="RUNTIME_CERTIFIED",
        )


def test_phase_c1_row_rejects_trace_observed():
    """T8b: TRACE_OBSERVED is also rejected — only NOT_CERTIFIED is allowed."""
    with pytest.raises(ValueError):
        PhaseC1Row(
            app_name="apps_research",
            route_shape="R3_grounded_read",
            trace_id="t1",
            span_id="s1",
            parent_span_id=None,
            span_name="test",
            timestamp=0,
            runtime_certification_status="TRACE_OBSERVED",
        )


# ---------------------------------------------------------------------------
# T9 — iter_rows_from_snapshot yields all nodes
# ---------------------------------------------------------------------------


def test_iter_rows_from_snapshot_yields_all_nodes():
    """T9: a 3-node snapshot yields exactly 3 rows."""
    nodes = [_make_node(node_id=f"span-{i:03d}") for i in range(3)]
    snapshot = _make_snapshot(nodes)
    rows = list(iter_rows_from_snapshot(snapshot))
    assert len(rows) == 3


# ---------------------------------------------------------------------------
# T10 — time filter lower bound
# ---------------------------------------------------------------------------


def test_iter_rows_from_snapshot_time_filter_lower_bound():
    """T10: started_after_ms filters out older nodes."""
    nodes = [
        _make_node(node_id="old", started_at_utc=999),
        _make_node(node_id="new", started_at_utc=2_000),
    ]
    snapshot = _make_snapshot(nodes, started_at_utc=0, ended_at_utc=3_000)
    rows = list(iter_rows_from_snapshot(snapshot, started_after_ms=1_000))
    span_ids = {r.span_id for r in rows}
    assert "new" in span_ids
    assert "old" not in span_ids


# ---------------------------------------------------------------------------
# T11 — time filter upper bound
# ---------------------------------------------------------------------------


def test_iter_rows_from_snapshot_time_filter_upper_bound():
    """T11: ended_before_ms filters out newer nodes."""
    nodes = [
        _make_node(node_id="early", started_at_utc=100),
        _make_node(node_id="late", started_at_utc=5_000),
    ]
    snapshot = _make_snapshot(nodes, started_at_utc=0, ended_at_utc=10_000)
    rows = list(iter_rows_from_snapshot(snapshot, ended_before_ms=1_000))
    span_ids = {r.span_id for r in rows}
    assert "early" in span_ids
    assert "late" not in span_ids


# ---------------------------------------------------------------------------
# T12 — empty snapshot
# ---------------------------------------------------------------------------


def test_iter_rows_from_snapshot_empty_snapshot():
    """T12: zero nodes → zero rows, no exception."""
    snapshot = _make_snapshot([])
    rows = list(iter_rows_from_snapshot(snapshot))
    assert rows == []


# ---------------------------------------------------------------------------
# T13 — trace_id from snapshot level
# ---------------------------------------------------------------------------


def test_iter_rows_for_trace_correct_trace_id():
    """T13: rows carry snapshot.trace_id, not a per-node attribute value."""
    node = _make_node(attrs={"trace_id": "attr-trace-override"})
    snapshot = _make_snapshot([node], trace_id="snapshot-trace-id")
    rows = list(iter_rows_for_trace(snapshot, "snapshot-trace-id"))
    assert len(rows) == 1
    assert rows[0].trace_id == "snapshot-trace-id"


# ---------------------------------------------------------------------------
# T14 — build_test_snapshot roundtrip
# ---------------------------------------------------------------------------


def test_build_test_snapshot_roundtrip():
    """T14: build_test_snapshot returns a valid RuntimeADGSnapshot with correct snapshot_id."""
    snap = build_test_snapshot(
        "trace-roundtrip",
        [{"node_id": "n1", "name": "span.one", "attributes": {"x": 1}}],
    )
    assert snap.trace_id == "trace-roundtrip"
    assert snap.snapshot_id == snap.snapshot_hash
    assert len(snap.snapshot_id) == 64
    assert snap.node_count() == 1


# ---------------------------------------------------------------------------
# T15 — evidence_source includes snapshot_id
# ---------------------------------------------------------------------------


def test_evidence_source_includes_snapshot_id():
    """T15: evidence_source == f'runtime_adg.snapshot.{snapshot.snapshot_id}'."""
    node = _make_node()
    snapshot = _make_snapshot([node])
    row = node_to_row(node, snapshot_id=snapshot.snapshot_id, trace_id=snapshot.trace_id)
    assert row.evidence_source == f"{EVIDENCE_SOURCE_PREFIX}{snapshot.snapshot_id}"


# ---------------------------------------------------------------------------
# T16 — app_name from kwarg
# ---------------------------------------------------------------------------


def test_app_name_from_kwarg():
    """T16: caller-supplied app_name takes precedence over attributes['app_name']."""
    node = _make_node(attrs={"app_name": "apps_other"})
    snapshot = _make_snapshot([node])
    row = node_to_row(
        node,
        snapshot_id=snapshot.snapshot_id,
        trace_id=snapshot.trace_id,
        app_name="apps_research",
    )
    assert row.app_name == "apps_research"


# ---------------------------------------------------------------------------
# T17 — app_name from attrs fallback
# ---------------------------------------------------------------------------


def test_app_name_from_attrs_fallback():
    """T17: attributes['app_name'] is used when kwarg is empty string."""
    node = _make_node(attrs={"app_name": "apps_eval"})
    snapshot = _make_snapshot([node])
    row = node_to_row(
        node,
        snapshot_id=snapshot.snapshot_id,
        trace_id=snapshot.trace_id,
        app_name="",
    )
    assert row.app_name == "apps_eval"


# ---------------------------------------------------------------------------
# T18 — manifest_hash from attrs
# ---------------------------------------------------------------------------


def test_manifest_hash_from_attrs():
    """T18: manifest_hash is extracted from attributes['manifest_hash'] when present."""
    mhash = "a" * 64
    node = _make_node(attrs={"manifest_hash": mhash})
    snapshot = _make_snapshot([node])
    row = node_to_row(node, snapshot_id=snapshot.snapshot_id, trace_id=snapshot.trace_id)
    assert row.manifest_hash == mhash


# ---------------------------------------------------------------------------
# T19 — manifest_hash default empty
# ---------------------------------------------------------------------------


def test_manifest_hash_default_empty():
    """T19: manifest_hash == '' when not in attributes."""
    node = _make_node()
    snapshot = _make_snapshot([node])
    row = node_to_row(node, snapshot_id=snapshot.snapshot_id, trace_id=snapshot.trace_id)
    assert row.manifest_hash == ""


# ---------------------------------------------------------------------------
# T20 — artifact_id and contract_id independent
# ---------------------------------------------------------------------------


def test_artifact_id_and_contract_id_independent():
    """T20: both fields populated independently when attrs contain both keys."""
    node = _make_node(attrs={"artifact_id": "art-1", "contract_id": "con-1"})
    snapshot = _make_snapshot([node])
    row = node_to_row(node, snapshot_id=snapshot.snapshot_id, trace_id=snapshot.trace_id)
    assert row.artifact_id == "art-1"
    assert row.contract_id == "con-1"


# ---------------------------------------------------------------------------
# T21 — source_path from code.filepath
# ---------------------------------------------------------------------------


def test_source_path_from_code_filepath():
    """T21: source_path is populated from attributes['code.filepath']."""
    node = _make_node(attrs={"code.filepath": "apps_research/runner.py"})
    snapshot = _make_snapshot([node])
    row = node_to_row(node, snapshot_id=snapshot.snapshot_id, trace_id=snapshot.trace_id)
    assert row.source_path == "apps_research/runner.py"


# ---------------------------------------------------------------------------
# T22 — source_path alias
# ---------------------------------------------------------------------------


def test_source_path_from_alias():
    """T22: source_path populated from attributes['source_path'] when code.filepath absent."""
    node = _make_node(attrs={"source_path": "apps_eval/evaluator.py"})
    snapshot = _make_snapshot([node])
    row = node_to_row(node, snapshot_id=snapshot.snapshot_id, trace_id=snapshot.trace_id)
    assert row.source_path == "apps_eval/evaluator.py"


# ---------------------------------------------------------------------------
# T23 — to_dict serialisable
# ---------------------------------------------------------------------------


def test_to_dict_serialisable():
    """T23: row.to_dict() passes json.dumps() without raising."""
    node = _make_node(attrs={"foo": "bar", "count": 42})
    snapshot = _make_snapshot([node])
    row = node_to_row(node, snapshot_id=snapshot.snapshot_id, trace_id=snapshot.trace_id)
    serialised = json.dumps(row.to_dict())
    assert isinstance(serialised, str)
    assert "NOT_CERTIFIED" in serialised


# ---------------------------------------------------------------------------
# T24 — to_dict has all 18 fields
# ---------------------------------------------------------------------------


def test_to_dict_has_all_18_fields():
    """T24: row.to_dict() contains all 17 schema fields + schema_version envelope field.

    The 17 schema data fields are enumerated in _SCHEMA_FIELDS.
    The plan refers to '18 fields' counting evidence_source as the 17th data
    field plus schema_version as the envelope field = 18 keys in to_dict().
    """
    _SCHEMA_FIELDS = {
        "app_name", "route_shape", "trace_id", "span_id", "parent_span_id",
        "span_name", "timestamp", "contract_name", "normalized_cert_alias",
        "manifest_hash", "static_runtime_mode", "runtime_certification_status",
        "artifact_id", "contract_id", "source_path", "attributes",
        "evidence_source",
    }
    assert len(_SCHEMA_FIELDS) == 17
    node = _make_node()
    snapshot = _make_snapshot([node])
    row = node_to_row(node, snapshot_id=snapshot.snapshot_id, trace_id=snapshot.trace_id)
    d = row.to_dict()
    missing = _SCHEMA_FIELDS - set(d.keys())
    assert not missing, f"Missing schema fields: {missing}"
    # schema_version is an envelope field (not a schema data field)
    assert "schema_version" in d
    # to_dict() total: 17 data fields + 1 envelope = 18 keys
    assert len(d) == 18


# ---------------------------------------------------------------------------
# T25 — CommitRequest span preserved
# ---------------------------------------------------------------------------


def test_commit_request_span_preserved():
    """T25: CommitRequest spans are yielded by iter_rows_from_snapshot (not suppressed)."""
    nodes = [
        _make_node(node_id="normal", name="orchestrator.execute"),
        _make_node(node_id="commit", name="CommitRequest"),
    ]
    snapshot = _make_snapshot(nodes)
    rows = list(iter_rows_from_snapshot(snapshot))
    span_names = {r.span_name for r in rows}
    assert "CommitRequest" in span_names


# ---------------------------------------------------------------------------
# T26 — malformed time window applies no filter
# ---------------------------------------------------------------------------


def test_malformed_time_window_no_filter():
    """T26: started_after_ms > ended_before_ms logs a warning and yields all nodes."""
    nodes = [
        _make_node(node_id="a", started_at_utc=100),
        _make_node(node_id="b", started_at_utc=200),
    ]
    snapshot = _make_snapshot(nodes, started_at_utc=0, ended_at_utc=1_000)
    # malformed window: start > end
    rows = list(iter_rows_from_snapshot(snapshot, started_after_ms=9999, ended_before_ms=1))
    assert len(rows) == 2


# ---------------------------------------------------------------------------
# T27 — PHASE_C1_SCHEMA_VERSION constant
# ---------------------------------------------------------------------------


def test_phase_c1_schema_version_constant():
    """T27: PHASE_C1_SCHEMA_VERSION == '1.0'."""
    assert PHASE_C1_SCHEMA_VERSION == "1.0"


# ---------------------------------------------------------------------------
# T28 — no live DB import
# ---------------------------------------------------------------------------


def test_no_live_db_import():
    """T28: importing the adapter does not pull in RuntimeADGQuery (static ADG)."""
    # RuntimeADGQuery lives in tools.adg.runtime_query — it must NOT be imported
    # by the adapter at module scope. (It might exist if another test already
    # imported it, but the adapter itself must not be the cause.)
    import tools.runtime_cert.runtime_adg_query_adapter as adapter_mod  # noqa: F401

    # Verify the adapter module does not import RuntimeADGQuery.
    import ast
    import pathlib

    src = pathlib.Path(adapter_mod.__file__).read_text(encoding="utf-8")
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names = []
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module or ""]
            for n in names:
                assert "runtime_query" not in (n or ""), (
                    f"Adapter must not import tools.adg.runtime_query; found: {n!r}"
                )


# ---------------------------------------------------------------------------
# T29 — extract_attributes returns dict
# ---------------------------------------------------------------------------


def test_extract_attributes_returns_dict():
    """T29: extract_attributes always returns a dict, even on bad input."""
    good_node = _make_node(attrs={"k": "v"})
    bad_node = RuntimeADGNode(
        node_id="x", name="y", kind="z", layer="L0", component="c",
        started_at_utc=0, duration_ms=0.0, status="ok",
        attributes_json="not-json",
    )
    empty_node = RuntimeADGNode(
        node_id="x2", name="y2", kind="z", layer="L0", component="c",
        started_at_utc=0, duration_ms=0.0, status="ok",
        attributes_json="",
    )
    assert isinstance(extract_attributes(good_node), dict)
    assert extract_attributes(good_node) == {"k": "v"}
    assert isinstance(extract_attributes(bad_node), dict)
    assert extract_attributes(bad_node) == {}
    assert isinstance(extract_attributes(empty_node), dict)
    assert extract_attributes(empty_node) == {}


# ---------------------------------------------------------------------------
# T30 — B.5 accessor compatibility
# ---------------------------------------------------------------------------


def test_iter_rows_preserves_b5_accessor_compatibility():
    """T30: rows satisfy Phase B.5 defensive accessor functions."""
    from tools.runtime_cert.negative_controls import (
        _row_app_name,
        _row_contract_name,
        _row_source_path,
    )

    node = _make_node(
        attrs={"app_name": "apps_eval", "source_path": "apps_eval/eval.py"},
        component="apps_eval",
    )
    snapshot = _make_snapshot([node])
    row = next(
        iter_rows_from_snapshot(snapshot, app_name="apps_eval", route_shape="formal_exception")
    )
    d = row.to_dict()

    # B.5 accessors must work on C.1 row dicts without raising
    assert _row_app_name(d) == "apps_eval"
    assert _row_contract_name(d) is None  # C.1 leaves contract_name=None
    assert _row_source_path(d) == "apps_eval/eval.py"


# ---------------------------------------------------------------------------
# Additional invariant: runtime_certification_status is always NOT_CERTIFIED
# ---------------------------------------------------------------------------


def test_all_rows_have_not_certified_status():
    """Invariant: every row produced by iter_rows_from_snapshot is NOT_CERTIFIED."""
    nodes = [_make_node(node_id=f"s{i}") for i in range(5)]
    snapshot = _make_snapshot(nodes)
    for row in iter_rows_from_snapshot(snapshot):
        assert row.runtime_certification_status == NOT_CERTIFIED


# ---------------------------------------------------------------------------
# Additional: route_shape from kwarg
# ---------------------------------------------------------------------------


def test_route_shape_from_kwarg():
    """route_shape caller kwarg takes precedence over attributes['route_shape']."""
    node = _make_node(attrs={"route_shape": "formal_exception"})
    snapshot = _make_snapshot([node])
    row = node_to_row(
        node,
        snapshot_id=snapshot.snapshot_id,
        trace_id=snapshot.trace_id,
        route_shape="R3_grounded_read",
    )
    assert row.route_shape == "R3_grounded_read"


# ---------------------------------------------------------------------------
# Additional: artifact_id fallback to contract_id
# ---------------------------------------------------------------------------


def test_artifact_id_falls_back_to_contract_id():
    """When artifact_id absent, artifact_id is populated from contract_id."""
    node = _make_node(attrs={"contract_id": "con-42"})
    snapshot = _make_snapshot([node])
    row = node_to_row(node, snapshot_id=snapshot.snapshot_id, trace_id=snapshot.trace_id)
    assert row.artifact_id == "con-42"
    assert row.contract_id == "con-42"


# ---------------------------------------------------------------------------
# Additional: build_test_snapshot with attributes dict
# ---------------------------------------------------------------------------


def test_build_test_snapshot_with_attributes():
    """build_test_snapshot correctly serialises the attributes dict."""
    snap = build_test_snapshot(
        "trace-attrs",
        [{"node_id": "n1", "name": "span.x", "attributes": {"contract_name": "ValidatedRequest"}}],
    )
    assert snap.node_count() == 1
    attrs = extract_attributes(snap.nodes[0])
    assert attrs.get("contract_name") == "ValidatedRequest"


# ---------------------------------------------------------------------------
# Additional: VALID_ROUTE_SHAPES covers all four values
# ---------------------------------------------------------------------------


def test_valid_route_shapes_coverage():
    """VALID_ROUTE_SHAPES contains all four expected route shape values."""
    expected = {"R3_grounded_read", "R3R4_grounded_write", "build_time_compiler", "formal_exception"}
    assert expected == VALID_ROUTE_SHAPES


# ---------------------------------------------------------------------------
# Additional: iter_rows_for_trace on non-matching trace_id
# ---------------------------------------------------------------------------


def test_iter_rows_for_trace_no_match():
    """iter_rows_for_trace yields nothing when trace_id does not match the snapshot."""
    node = _make_node()
    snapshot = _make_snapshot([node], trace_id="trace-A")
    rows = list(iter_rows_for_trace(snapshot, "trace-B"))
    assert rows == []


# ---------------------------------------------------------------------------
# Additional: to_dict contains schema_version envelope field
# ---------------------------------------------------------------------------


def test_to_dict_contains_schema_version():
    """to_dict() output includes 'schema_version' matching PHASE_C1_SCHEMA_VERSION."""
    node = _make_node()
    snapshot = _make_snapshot([node])
    row = node_to_row(node, snapshot_id=snapshot.snapshot_id, trace_id=snapshot.trace_id)
    d = row.to_dict()
    assert d["schema_version"] == PHASE_C1_SCHEMA_VERSION
