"""Tests for apps_shared.proof.scenario_base — deterministic IDs."""

from __future__ import annotations

from pathlib import Path

from apps_shared.proof.scenario_base import ScenarioContext, ScenarioSpec


def _spec(scenario_id: str = "test_scn_v1") -> ScenarioSpec:
    return ScenarioSpec(
        app_id="apps_test",
        scenario_id=scenario_id,
        intake_body="{}",
        grounding_required=False,
        task_spec="t",
        query_spec="q",
        expected_layers=("U0",),
    )


def test_seed_default_is_scenario_id(tmp_path: Path):
    spec = _spec()
    ctx = ScenarioContext(spec=spec, export_root=tmp_path, adg_snapshot=tmp_path)
    assert ctx.seed == "test_scn_v1"


def test_same_seed_produces_same_ids(tmp_path: Path):
    spec = _spec()
    a = ScenarioContext(spec=spec, export_root=tmp_path, adg_snapshot=tmp_path)
    b = ScenarioContext(spec=spec, export_root=tmp_path, adg_snapshot=tmp_path)
    assert a.run_id == b.run_id
    assert a.session_id == b.session_id
    assert a.request_id_hint == b.request_id_hint
    assert a.trace_root == b.trace_root


def test_different_seed_produces_different_ids(tmp_path: Path):
    a = ScenarioContext(spec=_spec("a_v1"), export_root=tmp_path, adg_snapshot=tmp_path)
    b = ScenarioContext(spec=_spec("b_v1"), export_root=tmp_path, adg_snapshot=tmp_path)
    assert a.run_id != b.run_id
    assert a.trace_root != b.trace_root


def test_explicit_seed_overrides_default(tmp_path: Path):
    spec = _spec()
    a = ScenarioContext(spec=spec, export_root=tmp_path, adg_snapshot=tmp_path)
    b = ScenarioContext(spec=spec, export_root=tmp_path, adg_snapshot=tmp_path, seed="custom")
    assert a.run_id != b.run_id


def test_span_ids_deterministic_across_runs(tmp_path: Path):
    spec = _spec()
    a = ScenarioContext(spec=spec, export_root=tmp_path, adg_snapshot=tmp_path)
    b = ScenarioContext(spec=spec, export_root=tmp_path, adg_snapshot=tmp_path)
    span_a = a.emit_span(
        layer="U0", name="x", parent_span_id=None, status="PASS", started_at="t", ended_at="t"
    )
    span_b = b.emit_span(
        layer="U0", name="x", parent_span_id=None, status="PASS", started_at="t", ended_at="t"
    )
    assert span_a.span_id == span_b.span_id


def test_span_counter_increments(tmp_path: Path):
    ctx = ScenarioContext(spec=_spec(), export_root=tmp_path, adg_snapshot=tmp_path)
    s1 = ctx.emit_span(layer="U0", name="x", parent_span_id=None, status="PASS", started_at="t", ended_at="t")
    s2 = ctx.emit_span(
        layer="L1", name="y", parent_span_id=s1.span_id, status="PASS", started_at="t", ended_at="t"
    )
    assert s1.span_id != s2.span_id  # counter changes hash input
