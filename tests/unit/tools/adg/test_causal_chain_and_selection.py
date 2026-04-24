"""Tests for tools.adg.causal_chain, tools.adg.select_tests, and
agentic_core.L6_observability.adg_span_annotator.

All share the fixture DB builder from test_runtime_query.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from unittest.mock import patch

import pytest

from tests.unit.tools.adg.test_runtime_query import _build_fixture_db
from tools.adg.causal_chain import CausalChain
from tools.adg.runtime_query import RuntimeADGQuery
from tools.adg.select_tests import _is_test_file, select_tests_for


@pytest.fixture()
def fixture_q(tmp_path: Path):
    db = tmp_path / "adg_indexed_fixture.sqlite"
    _build_fixture_db(db)
    # Augment for select_tests: add a test file node importing n_central.
    conn = sqlite3.connect(str(db))
    try:
        conn.execute(
            "INSERT INTO nodes (id, adg_name, layer, resolved_path) VALUES (?, ?, ?, ?)",
            ("n_test_1", "tests.unit.test_central", "L_TESTS", "tests/unit/test_central.py"),
        )
        conn.execute(
            "INSERT INTO edges (src_id, tgt_id, relation_type) VALUES (?, ?, 'imports')",
            ("n_test_1", "n_central"),
        )
        # Add semantic writes_to for span annotator.
        conn.execute(
            "INSERT INTO nodes (id, adg_name, layer, resolved_path) VALUES (?, ?, ?, ?)",
            ("n_uwg", "agentic_core.L4_state.write_gateway", "L4", "agentic_core/L4_state/write_gateway.py"),
        )
        conn.execute(
            "INSERT INTO edges (src_id, tgt_id, relation_type) VALUES (?, ?, 'writes_to')",
            ("n_central", "n_uwg"),
        )
        conn.execute(
            "INSERT INTO edges (src_id, tgt_id, relation_type) VALUES (?, ?, 'reads_from')",
            ("n_central", "n_uwg"),
        )
        conn.commit()
    finally:
        conn.close()
    return RuntimeADGQuery(sqlite_path=db)


# ---------- CausalChain ----------


def test_causal_explain_node_known(fixture_q):
    cc = CausalChain(query=fixture_q)
    r = cc.explain_node("n_central", max_callers=3)
    assert r.resolved["node_id"] == "n_central"
    assert r.blast_radius["archetype"] == "CENTRAL_DEPENDENCY"
    assert len(r.upstream_callers) == 3
    assert "archetype=CENTRAL_DEPENDENCY" in r.summary


def test_causal_explain_node_unknown(fixture_q):
    cc = CausalChain(query=fixture_q)
    r = cc.explain_node("does.not.exist")
    assert r.blast_radius["error"] == "node_not_found"
    assert "not found" in r.summary


def test_causal_explain_node_detects_swallow(fixture_q):
    cc = CausalChain(query=fixture_q)
    r = cc.explain_node("n_failing")
    # From the fixture: n_swallow has broad_exception_catch reaching n_failing.
    assert len(r.swallow_sites) >= 1
    assert "swallow site" in r.summary


def test_causal_explain_node_no_snapshot():
    with patch("tools.adg.causal_chain.get_default_query", return_value=None):
        cc = CausalChain(query=None)
        r = cc.explain_node("anything")
    assert r.snapshot_id is None
    assert "unavailable" in r.summary


def test_causal_explain_span_stub(fixture_q):
    cc = CausalChain(query=fixture_q)
    r = cc.explain_span("trace-xyz")
    assert r["trace_id"] == "trace-xyz"
    assert "guidance" in r


def test_causal_report_to_dict_is_json_safe(fixture_q):
    import json as _json

    cc = CausalChain(query=fixture_q)
    r = cc.explain_node("n_central")
    payload = _json.dumps(r.to_dict(), default=str)
    assert "CENTRAL_DEPENDENCY" in payload


# ---------- select_tests ----------


def test_is_test_file_recognition():
    assert _is_test_file("tests/unit/test_foo.py") is True
    assert _is_test_file("tests/integration/test_bar.py") is True
    assert _is_test_file("tests\\unit\\test_win.py") is True
    assert _is_test_file("apps_shared/util.py") is False
    assert _is_test_file(None) is False
    assert _is_test_file("") is False


def test_select_tests_for_changed_file(fixture_q):
    with patch("tools.adg.select_tests.get_default_query", return_value=fixture_q):
        tests = select_tests_for(["agentic_core/L0_routing/router.py"])
    assert "tests/unit/test_central.py" in tests


def test_select_tests_for_unknown_file(fixture_q):
    with patch("tools.adg.select_tests.get_default_query", return_value=fixture_q):
        tests = select_tests_for(["unknown/path.py"])
    assert tests == []


def test_select_tests_for_no_snapshot():
    with patch("tools.adg.select_tests.get_default_query", return_value=None):
        tests = select_tests_for(["any/file.py"])
    assert tests == []


# ---------- adg_span_annotator ----------


def test_annotate_span_adds_static_attrs(fixture_q):
    from agentic_core.L6_observability.adg_span_annotator import (
        ADG_ATTR_PREFIX,
        annotate_span,
    )

    span = {"code.adg_name": "n_central", "duration_ms": 42}
    enriched = annotate_span(span, query=fixture_q)
    assert enriched["duration_ms"] == 42  # untouched
    assert enriched[ADG_ATTR_PREFIX + "node_resolved"] is True
    assert enriched[ADG_ATTR_PREFIX + "archetype"] == "CENTRAL_DEPENDENCY"
    # writes_to appears in the CSV and has a count.
    assert "agentic_core.L4_state.write_gateway" in enriched[ADG_ATTR_PREFIX + "writes_to"]
    assert enriched[ADG_ATTR_PREFIX + "writes_to:count"] == 1


def test_annotate_span_is_non_mutating(fixture_q):
    from agentic_core.L6_observability.adg_span_annotator import annotate_span

    span = {"code.adg_name": "n_central"}
    enriched = annotate_span(span, query=fixture_q)
    assert span == {"code.adg_name": "n_central"}  # pristine
    assert len(enriched) > 1


def test_annotate_span_unknown_node(fixture_q):
    from agentic_core.L6_observability.adg_span_annotator import (
        ADG_ATTR_PREFIX,
        annotate_span,
    )

    enriched = annotate_span({"code.adg_name": "does.not.exist"}, query=fixture_q)
    assert enriched[ADG_ATTR_PREFIX + "node_resolved"] is False


def test_annotate_span_no_snapshot():
    from agentic_core.L6_observability.adg_span_annotator import annotate_span

    span = {"code.adg_name": "n_central"}
    with patch(
        "agentic_core.L6_observability.adg_span_annotator.get_default_query",
        return_value=None,
    ):
        out = annotate_span(span, query=None)
    # No snapshot → unchanged copy.
    assert out == span


def test_drift_report_detects_missing_and_unexpected(fixture_q):
    from agentic_core.L6_observability.adg_span_annotator import drift_report

    with patch(
        "agentic_core.L6_observability.adg_span_annotator.get_default_query",
        return_value=fixture_q,
    ):
        span = {
            "code.adg_name": "n_central",
            "observed.writes": ["unexpected.module"],
        }
        report = drift_report(span, target_identifier="n_central")
    assert "agentic_core.L4_state.write_gateway" in report["writes"]["missing"]
    assert "unexpected.module" in report["writes"]["unexpected"]


def test_drift_report_perfect_match(fixture_q):
    from agentic_core.L6_observability.adg_span_annotator import drift_report

    with patch(
        "agentic_core.L6_observability.adg_span_annotator.get_default_query",
        return_value=fixture_q,
    ):
        span = {
            "code.adg_name": "n_central",
            "observed.writes": ["agentic_core.L4_state.write_gateway"],
            "observed.reads": ["agentic_core.L4_state.write_gateway"],
        }
        report = drift_report(span, target_identifier="n_central")
    assert report["writes"]["missing"] == []
    assert report["writes"]["unexpected"] == []
    assert report["reads"]["missing"] == []
