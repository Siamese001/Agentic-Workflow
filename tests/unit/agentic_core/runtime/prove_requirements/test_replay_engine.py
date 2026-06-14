"""Unit tests for agentic_core.runtime.prove_requirements.replay_engine.

Wave 6.1 — Core P2 untested-module coverage.
The replay engine projects an OTEL-like trace down to its deterministic fields
(uuid/clock stripped), digests that projection, and compares two replay runs.
Tests cover the field tables, name-path walking, projection shape, digest
determinism vs sensitivity, and the run_replay_pair / artifact-writing drivers
against in-memory fake scenario objects.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from agentic_core.runtime.prove_requirements.replay_engine import (
    DETERMINISTIC_FIELDS,
    NONDETERMINISTIC_FIELDS,
    deterministic_projection,
    replay_digest,
    run_full_replay_suite,
    run_replay_pair,
    write_replay_artifacts,
    write_replay_comparison,
)


def _trace(scenario: str = "s1", *, trace_id: str = "T", clock: int = 0) -> Dict[str, Any]:
    """Two-span trace: root → child. trace_id/clock vary across replays."""
    return {
        "scenario": scenario,
        "span_count": 2,
        "spans": [
            {
                "span_id": "sp-root",
                "parent_span_id": "",
                "name": "root",
                "route_id": "R1",
                "status": "OK",
                "trace_id": trace_id,
                "start_unix_ns": clock,
            },
            {
                "span_id": "sp-child",
                "parent_span_id": "sp-root",
                "name": "child",
                "gate_id": "G1",
                "status": "PASS",
                "trace_id": trace_id,
                "start_unix_ns": clock + 5,
            },
        ],
    }


class _FakeScenario:
    """Minimal object exposing to_dict(), like the harness scenario result."""

    def __init__(self, trace: Dict[str, Any]) -> None:
        self._trace = trace

    def to_dict(self) -> Dict[str, Any]:
        return self._trace


class TestFieldTables:
    def test_deterministic_and_nondeterministic_disjoint(self) -> None:
        assert set(DETERMINISTIC_FIELDS).isdisjoint(set(NONDETERMINISTIC_FIELDS))

    def test_clock_and_uuid_fields_are_nondeterministic(self) -> None:
        for f in ("trace_id", "span_id", "run_id", "start_unix_ns", "latency_ms"):
            assert f in NONDETERMINISTIC_FIELDS

    def test_hash_fields_are_deterministic(self) -> None:
        for f in ("policy_hash", "blueprint_hash", "replay_key", "contract_digest"):
            assert f in DETERMINISTIC_FIELDS


class TestProjection:
    def test_projection_shape(self) -> None:
        proj = deterministic_projection(_trace())
        assert proj["scenario"] == "s1"
        assert proj["span_count"] == 2
        assert len(proj["spans"]) == 2
        # Each projected span has path + fields, fields keyed by DETERMINISTIC_FIELDS.
        for sp in proj["spans"]:
            assert set(sp.keys()) == {"path", "fields"}
            assert set(sp["fields"].keys()) == set(DETERMINISTIC_FIELDS)

    def test_name_path_walks_to_root(self) -> None:
        proj = deterministic_projection(_trace())
        paths = [tuple(sp["path"]) for sp in proj["spans"]]
        assert ("root",) in paths
        assert ("root", "child") in paths

    def test_nondeterministic_fields_excluded(self) -> None:
        proj = deterministic_projection(_trace())
        for sp in proj["spans"]:
            assert "trace_id" not in sp["fields"]
            assert "start_unix_ns" not in sp["fields"]

    def test_projection_ignores_clock_and_trace_id(self) -> None:
        a = deterministic_projection(_trace(trace_id="T1", clock=0))
        b = deterministic_projection(_trace(trace_id="T2", clock=999))
        assert a == b


class TestDigest:
    def test_digest_is_hex_sha256(self) -> None:
        d = replay_digest(_trace())
        assert len(d) == 64
        assert all(c in "0123456789abcdef" for c in d)

    def test_digest_stable_across_clock_and_uuid(self) -> None:
        assert replay_digest(_trace(trace_id="A", clock=1)) == replay_digest(
            _trace(trace_id="B", clock=2)
        )

    def test_digest_sensitive_to_deterministic_field(self) -> None:
        base = _trace()
        changed = _trace()
        changed["spans"][1]["gate_id"] = "G2"
        assert replay_digest(base) != replay_digest(changed)


class TestRunReplayPair:
    def test_match_when_only_clock_differs(self) -> None:
        calls = {"n": 0}

        def fn() -> _FakeScenario:
            calls["n"] += 1
            return _FakeScenario(_trace(trace_id=f"T{calls['n']}", clock=calls["n"] * 10))

        result = run_replay_pair("s1", fn)
        assert result["deterministic_match"] is True
        assert result["span_diffs"] == []
        assert result["deterministic_digest_run_1"] == result["deterministic_digest_run_2"]

    def test_mismatch_reports_span_field_drift(self) -> None:
        calls = {"n": 0}

        def fn() -> _FakeScenario:
            calls["n"] += 1
            t = _trace()
            if calls["n"] == 2:
                t["spans"][1]["gate_id"] = "DRIFT"
            return _FakeScenario(t)

        result = run_replay_pair("s1", fn)
        assert result["deterministic_match"] is False
        assert any(d["issue"] == "span_field_drift" for d in result["span_diffs"])


class TestArtifactWriting:
    def test_write_replay_artifacts(self, tmp_path: Path) -> None:
        result = run_replay_pair("s1", lambda: _FakeScenario(_trace()))
        paths = write_replay_artifacts(tmp_path, "s1", result)
        assert Path(paths["run_1"]).exists()
        assert Path(paths["run_2"]).exists()
        assert json.loads(Path(paths["run_1"]).read_text())["scenario"] == "s1"

    def test_write_replay_comparison(self, tmp_path: Path) -> None:
        result = run_replay_pair("s1", lambda: _FakeScenario(_trace()))
        out = write_replay_comparison(tmp_path, [result])
        summary = json.loads(out.read_text())
        assert summary["all_scenarios_match"] is True
        assert summary["scenarios"][0]["scenario"] == "s1"

    def test_run_full_replay_suite(self, tmp_path: Path) -> None:
        fns = [("s1", lambda: _FakeScenario(_trace("s1")))]
        summary = run_full_replay_suite(fns, tmp_path)
        assert summary["all_scenarios_match"] is True
        assert summary["per_scenario_match"] == {"s1": True}
        assert "s1" in summary["per_scenario_digests"]
        assert Path(summary["comparison_path"]).exists()
