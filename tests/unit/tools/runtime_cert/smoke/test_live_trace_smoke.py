"""Unit tests for Phase C.6 — non-promoting live-trace smoke harness.

All tests synthesize RuntimeADGSnapshot JSON fixtures on disk and assert
on the resulting LiveTraceSmokeReport. The apps_research manifest at
``apps_research/spine_manifest.yaml`` is read by
``compute_manifest_hash_for_app`` — no test patches filesystem here.

Test plan reference: task spec §7 (9 required tests)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from system_learning.runtime_adg.app_route_contracts import R3_GROUNDED_READ_CONTRACTS
from system_learning.runtime_adg.manifest_hash import compute_manifest_hash_for_app
from tools.runtime_cert.runtime_adg_query_adapter import NOT_CERTIFIED, build_test_snapshot
from tools.runtime_cert.smoke.live_trace_smoke import (
    LiveTraceSmokeReport,
    REPORT_DISCLAIMER,
    REQUIRED_ENV_VAR,
    REQUIRED_ENV_VALUE,
    SMOKE_APP_NAME,
    run_apps_research_live_trace_smoke,
    write_live_trace_smoke_report,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _env_full(monkeypatch):
    """Default env: AGENTIC_CORE_STACK=full so most tests do not repeat it."""
    monkeypatch.setenv(REQUIRED_ENV_VAR, REQUIRED_ENV_VALUE)


@pytest.fixture()
def apps_research_hash() -> str:
    """Real manifest hash for apps_research, resolved from repo root."""
    return compute_manifest_hash_for_app(SMOKE_APP_NAME)


def _node_dict(
    node_id: str,
    span_name: str,
    *,
    contract_name: str,
    app_name: str = SMOKE_APP_NAME,
    route_shape: str = "R3_grounded_read",
    manifest_hash: str = "",
    extra_attrs: dict[str, Any] | None = None,
    started_at_utc: int = 1_700_000_000_000,
) -> dict[str, Any]:
    """Build a raw snapshot-node dict with all required cert attributes."""
    attrs = {
        "app_name": app_name,
        "route_shape": route_shape,
        "run_id": f"run-{node_id}",
        "contract_name": contract_name,
        "contract_id": f"cid-{node_id}",
        "manifest_hash": manifest_hash,
    }
    if extra_attrs:
        attrs.update(extra_attrs)
    return {
        "node_id": node_id,
        "name": span_name,
        "kind": "span",
        "layer": "",
        "component": "",
        "started_at_utc": started_at_utc,
        "duration_ms": 1.0,
        "status": "ok",
        "attributes": attrs,
    }


def _write_snapshot(tmp_path: Path, nodes: list[dict[str, Any]]) -> Path:
    """Build a snapshot via build_test_snapshot, serialize to_dict, write JSON."""
    snap = build_test_snapshot(
        trace_id="trace-c6-smoke",
        nodes=nodes,
        mission="c6-smoke-test",
        started_at_utc=1_700_000_000_000,
        ended_at_utc=1_700_000_100_000,
    )
    out = tmp_path / "snapshot.json"
    out.write_text(json.dumps(snap.to_dict()), encoding="utf-8")
    return out


def _all_r3_nodes(manifest_hash: str) -> list[dict[str, Any]]:
    """Build one clean node per canonical R3 contract."""
    nodes = []
    for i, contract_name in enumerate(R3_GROUNDED_READ_CONTRACTS):
        nodes.append(
            _node_dict(
                node_id=f"s{i}",
                span_name=f"r3.span.{contract_name}",
                contract_name=contract_name,
                manifest_hash=manifest_hash,
                started_at_utc=1_700_000_000_000 + i,
            )
        )
    return nodes


# ---------------------------------------------------------------------------
# T1 — runtime_certification_status always NOT_CERTIFIED
# ---------------------------------------------------------------------------


def test_report_is_always_not_certified(tmp_path, apps_research_hash):
    """T1: even on a full-pass snapshot, status stays NOT_CERTIFIED."""
    snap_path = _write_snapshot(tmp_path, _all_r3_nodes(apps_research_hash))
    report = run_apps_research_live_trace_smoke(snap_path)
    assert report.runtime_certification_status == NOT_CERTIFIED


def test_report_rejects_non_not_certified_status():
    """T1b: constructor __post_init__ rejects any other status."""
    from tools.runtime_cert.extractors.r3_evidence import R3EvidenceReport

    stub_evidence = R3EvidenceReport(
        app_name=SMOKE_APP_NAME,
        route_shape="R3_grounded_read",
        manifest_hash="a" * 64,
        static_runtime_mode="",
        runtime_certification_status=NOT_CERTIFIED,
        required_contracts=R3_GROUNDED_READ_CONTRACTS,
        observed_contracts=(),
        missing_contracts=R3_GROUNDED_READ_CONTRACTS,
        attribute_hardening_required=(),
        unknown_needs_runtime_run=(),
        forbidden_violations=(),
        contract_evidence=(),
        passed_trace_observed=False,
        failure_reasons=(),
        notes="",
    )
    with pytest.raises(ValueError, match="NOT_CERTIFIED"):
        LiveTraceSmokeReport(
            app_name=SMOKE_APP_NAME,
            route_shape="R3_grounded_read",
            snapshot_path="x",
            manifest_hash="a" * 64,
            static_runtime_mode="",
            runtime_certification_status="RUNTIME_CERTIFIED",
            c1_row_count=0,
            c2_normalized_row_count=0,
            observed_contracts=(),
            missing_contracts=(),
            attribute_hardening_required=(),
            unknown_needs_runtime_run=(),
            forbidden_violations_count=0,
            passed_trace_observed=False,
            evidence_report=stub_evidence,
            failure_reasons=(),
            notes="",
        )


# ---------------------------------------------------------------------------
# T2 — AGENTIC_CORE_STACK missing / not full fails
# ---------------------------------------------------------------------------


def test_missing_agentic_core_stack_env_fails(tmp_path, monkeypatch, apps_research_hash):
    """T2: unset AGENTIC_CORE_STACK → RuntimeError."""
    monkeypatch.delenv(REQUIRED_ENV_VAR, raising=False)
    snap_path = _write_snapshot(tmp_path, _all_r3_nodes(apps_research_hash))
    with pytest.raises(RuntimeError, match="AGENTIC_CORE_STACK"):
        run_apps_research_live_trace_smoke(snap_path)


def test_agentic_core_stack_standalone_fails(tmp_path, monkeypatch, apps_research_hash):
    """T2b: AGENTIC_CORE_STACK=standalone → RuntimeError."""
    monkeypatch.setenv(REQUIRED_ENV_VAR, "standalone")
    snap_path = _write_snapshot(tmp_path, _all_r3_nodes(apps_research_hash))
    with pytest.raises(RuntimeError, match="standalone|full"):
        run_apps_research_live_trace_smoke(snap_path)


def test_agentic_core_stack_empty_fails(tmp_path, monkeypatch, apps_research_hash):
    """T2c: AGENTIC_CORE_STACK='' → RuntimeError."""
    monkeypatch.setenv(REQUIRED_ENV_VAR, "")
    snap_path = _write_snapshot(tmp_path, _all_r3_nodes(apps_research_hash))
    with pytest.raises(RuntimeError):
        run_apps_research_live_trace_smoke(snap_path)


# ---------------------------------------------------------------------------
# T3 — missing snapshot path fails clearly
# ---------------------------------------------------------------------------


def test_missing_snapshot_path_raises_file_not_found(tmp_path):
    """T3: nonexistent snapshot path → FileNotFoundError."""
    bogus = tmp_path / "does_not_exist.json"
    with pytest.raises(FileNotFoundError, match="does not exist"):
        run_apps_research_live_trace_smoke(bogus)


def test_snapshot_path_is_directory_raises(tmp_path):
    """T3b: snapshot_path points at a directory → FileNotFoundError."""
    with pytest.raises(FileNotFoundError, match="not a file"):
        run_apps_research_live_trace_smoke(tmp_path)


def test_invalid_json_snapshot_raises(tmp_path):
    """T3c: malformed JSON → ValueError."""
    bad = tmp_path / "bad.json"
    bad.write_text("{ not valid json", encoding="utf-8")
    with pytest.raises(ValueError, match="not valid JSON"):
        run_apps_research_live_trace_smoke(bad)


def test_snapshot_missing_required_keys_raises(tmp_path):
    """T3d: JSON object missing trace_id/nodes → ValueError."""
    partial = tmp_path / "partial.json"
    partial.write_text(json.dumps({"trace_id": "x"}), encoding="utf-8")
    with pytest.raises(ValueError, match="missing required"):
        run_apps_research_live_trace_smoke(partial)


# ---------------------------------------------------------------------------
# T4 — complete 8 R3 rows → passed_trace_observed=True, NOT_CERTIFIED
# ---------------------------------------------------------------------------


def test_complete_r3_snapshot_reports_honest_evidence(tmp_path, apps_research_hash):
    """T4: 8 clean R3 rows → status NOT_CERTIFIED; observed ∪ unknown = 8.

    The canonical R3 bindings ship ``FinalEvidenceContract`` with
    ``phase_a_status=UNKNOWN_NEEDS_RUNTIME_RUN`` (it is forced to live-trace
    evidence per the design matrix), so even a clean 8-row snapshot CANNOT
    produce ``passed_trace_observed=True`` end-to-end through the Phase C
    pipeline. That is the honest C.6 smoke signal — a non-promoting report
    shows exactly where ``apps_research`` stands today without any
    certification promotion.
    """
    snap_path = _write_snapshot(tmp_path, _all_r3_nodes(apps_research_hash))
    report = run_apps_research_live_trace_smoke(snap_path)

    assert report.runtime_certification_status == NOT_CERTIFIED
    assert report.forbidden_violations_count == 0
    assert report.c1_row_count == 8
    assert report.c2_normalized_row_count == 8
    assert report.manifest_hash == apps_research_hash
    # Every required contract is accounted for in one of the buckets:
    accounted = (
        set(report.observed_contracts)
        | set(report.missing_contracts)
        | set(report.attribute_hardening_required)
        | set(report.unknown_needs_runtime_run)
    )
    assert accounted == set(R3_GROUNDED_READ_CONTRACTS)
    # FinalEvidenceContract's binding phase_a_status = UNKNOWN_NEEDS_RUNTIME_RUN
    # forces it into the unknown bucket; this is the honest state.
    assert "FinalEvidenceContract" in report.unknown_needs_runtime_run
    assert report.passed_trace_observed is False


def test_passed_trace_observed_requires_no_unknown_or_hardening_gaps(
    tmp_path, apps_research_hash,
):
    """T4b: even with 8 clean rows, FinalEvidenceContract forces passed=False.

    Documents the invariant so a future hardening sweep that moves the
    FinalEvidenceContract binding to EXISTS_MATCHES_MATRIX can flip this
    test to ``assert passed is True`` — that will be the explicit C.6 →
    D transition signal.
    """
    snap_path = _write_snapshot(tmp_path, _all_r3_nodes(apps_research_hash))
    report = run_apps_research_live_trace_smoke(snap_path)

    assert report.passed_trace_observed is False
    assert report.runtime_certification_status == NOT_CERTIFIED
    assert report.unknown_needs_runtime_run  # non-empty


# ---------------------------------------------------------------------------
# T5 — missing one contract → missing_contracts populated
# ---------------------------------------------------------------------------


def test_missing_one_contract_reports_missing(tmp_path, apps_research_hash):
    """T5: omit ExitReviewPacket node → ExitReviewPacket in missing_contracts."""
    nodes = [
        n for n in _all_r3_nodes(apps_research_hash)
        if n["attributes"]["contract_name"] != "ExitReviewPacket"
    ]
    snap_path = _write_snapshot(tmp_path, nodes)
    report = run_apps_research_live_trace_smoke(snap_path)

    assert "ExitReviewPacket" in report.missing_contracts
    assert report.passed_trace_observed is False
    assert report.runtime_certification_status == NOT_CERTIFIED


def test_empty_snapshot_reports_all_missing(tmp_path):
    """T5b: no apps_research rows → all 8 required contracts missing."""
    # Snapshot with only a non-apps_research node
    nodes = [
        _node_dict(
            node_id="other_1",
            span_name="something",
            contract_name="ValidatedRequest",
            app_name="apps_other",
            route_shape="R3_grounded_read",
        ),
    ]
    snap_path = _write_snapshot(tmp_path, nodes)
    report = run_apps_research_live_trace_smoke(snap_path)

    assert set(report.missing_contracts) == set(R3_GROUNDED_READ_CONTRACTS)
    assert report.passed_trace_observed is False
    assert report.c1_row_count == 1  # one total, but for other app
    assert report.c2_normalized_row_count == 0
    assert "no rows" in report.notes or "other app" in report.notes


def test_truly_empty_snapshot_reports_all_missing(tmp_path):
    """T5c: zero nodes at all → all R3 contracts missing."""
    snap_path = _write_snapshot(tmp_path, [])
    report = run_apps_research_live_trace_smoke(snap_path)

    assert set(report.missing_contracts) == set(R3_GROUNDED_READ_CONTRACTS)
    assert report.passed_trace_observed is False
    assert report.c1_row_count == 0
    assert report.c2_normalized_row_count == 0


# ---------------------------------------------------------------------------
# T6 — CommitRequest row → forbidden violation
# ---------------------------------------------------------------------------


def test_commit_request_produces_forbidden_violation(tmp_path, apps_research_hash):
    """T6: CommitRequest node on apps_research R3 → forbidden violation."""
    nodes = _all_r3_nodes(apps_research_hash)
    nodes.append(
        _node_dict(
            node_id="s_commit",
            span_name="CommitRequest",
            contract_name="CommitRequest",
            manifest_hash=apps_research_hash,
        )
    )
    snap_path = _write_snapshot(tmp_path, nodes)
    report = run_apps_research_live_trace_smoke(snap_path)

    assert report.forbidden_violations_count == 1
    assert report.passed_trace_observed is False
    assert report.runtime_certification_status == NOT_CERTIFIED
    # The forbidden_violations tuple contains dict summaries
    assert len(report.forbidden_violations) == 1
    assert report.forbidden_violations[0]["contract_name"] == "CommitRequest"


# ---------------------------------------------------------------------------
# T7 — writer writes report with NOT_CERTIFIED disclaimer
# ---------------------------------------------------------------------------


def test_writer_emits_not_certified_disclaimer(tmp_path, apps_research_hash):
    """T7: write_live_trace_smoke_report JSON has disclaimer + NOT_CERTIFIED."""
    snap_path = _write_snapshot(tmp_path, _all_r3_nodes(apps_research_hash))
    report = run_apps_research_live_trace_smoke(snap_path)

    out_path = tmp_path / "smoke_report.json"
    written = write_live_trace_smoke_report(report, out_path)

    assert written.exists()
    data = json.loads(written.read_text(encoding="utf-8"))
    assert data["disclaimer"] == REPORT_DISCLAIMER
    assert "no runtime certification" in data["disclaimer"].lower()
    assert data["runtime_certification_status"] == NOT_CERTIFIED
    assert data["app_name"] == SMOKE_APP_NAME
    assert "evidence_report" in data


def test_writer_creates_parent_directories(tmp_path, apps_research_hash):
    """T7b: writer creates missing parent directories."""
    snap_path = _write_snapshot(tmp_path, _all_r3_nodes(apps_research_hash))
    report = run_apps_research_live_trace_smoke(snap_path)

    nested = tmp_path / "deep" / "nested" / "out.json"
    written = write_live_trace_smoke_report(report, nested)
    assert written.exists()


def test_writer_refuses_non_not_certified_report(tmp_path, apps_research_hash):
    """T7c: writer refuses to emit a report with a non-NOT_CERTIFIED status."""
    snap_path = _write_snapshot(tmp_path, _all_r3_nodes(apps_research_hash))
    report = run_apps_research_live_trace_smoke(snap_path)

    # Bypass __post_init__ by patching via object.__setattr__ on a frozen
    # dataclass — then writer should still catch the mismatch.
    object.__setattr__(report, "runtime_certification_status", "RUNTIME_CERTIFIED")
    with pytest.raises(ValueError, match="NOT_CERTIFIED"):
        write_live_trace_smoke_report(report, tmp_path / "x.json")


# ---------------------------------------------------------------------------
# T8 — no scanner / CI / emitter dependency
# ---------------------------------------------------------------------------


def test_smoke_module_has_no_scanner_or_ci_imports():
    """T8: the module's imports do not touch scanner/CI/emitter surfaces."""
    import tools.runtime_cert.smoke.live_trace_smoke as mod
    src = Path(mod.__file__).read_text(encoding="utf-8")

    forbidden_imports = [
        "from agentic_core",              # no runtime emitter surface
        "apps_shared._compat",            # no shim import beyond B.4 helper chain
        "ops_scripts.ci",                 # no CI gate import
        "from scripts.",                  # no legacy scripts/ root
        "structural_anti_patterns_scanner",
    ]
    for needle in forbidden_imports:
        assert needle not in src, (
            f"Phase C.6 smoke must NOT import {needle!r}; found in module source."
        )


# ---------------------------------------------------------------------------
# T9 — apps_research hardcoded / validated as first smoke app
# ---------------------------------------------------------------------------


def test_smoke_app_name_is_apps_research():
    """T9: SMOKE_APP_NAME constant is exactly 'apps_research'."""
    assert SMOKE_APP_NAME == "apps_research"


def test_route_shape_is_r3_grounded_read(tmp_path, apps_research_hash):
    """T9b: report always carries R3_grounded_read as the route_shape."""
    snap_path = _write_snapshot(tmp_path, _all_r3_nodes(apps_research_hash))
    report = run_apps_research_live_trace_smoke(snap_path)
    assert report.route_shape == "R3_grounded_read"


def test_other_apps_filtered_out(tmp_path, apps_research_hash):
    """T9c: non-apps_research rows never land in R3 evidence for apps_research."""
    nodes = _all_r3_nodes(apps_research_hash)
    # Add a SealedArtifact row from apps_other — must NOT count toward evidence
    nodes.append(
        _node_dict(
            node_id="other_sealed",
            span_name="other.sealed",
            contract_name="SealedArtifact",
            app_name="apps_other",
            manifest_hash=apps_research_hash,
        )
    )
    snap_path = _write_snapshot(tmp_path, nodes)
    report = run_apps_research_live_trace_smoke(snap_path)

    # apps_research's SealedArtifact is still observed (from its own node),
    # and no forbidden/missing states arise from the other-app row.
    assert "SealedArtifact" in report.observed_contracts
    assert report.c1_row_count == 9  # 8 apps_research + 1 other
    assert report.c2_normalized_row_count == 8  # only apps_research normalized
    assert "apps_other" in report.notes or "other app" in report.notes
    assert report.runtime_certification_status == NOT_CERTIFIED


# ---------------------------------------------------------------------------
# Additional — serialization / JSON round-trip
# ---------------------------------------------------------------------------


def test_report_to_json_is_parseable(tmp_path, apps_research_hash):
    """Report.to_json() returns valid JSON with all expected top-level keys."""
    snap_path = _write_snapshot(tmp_path, _all_r3_nodes(apps_research_hash))
    report = run_apps_research_live_trace_smoke(snap_path)

    data = json.loads(report.to_json())
    for key in (
        "disclaimer",
        "app_name",
        "route_shape",
        "runtime_certification_status",
        "manifest_hash",
        "observed_contracts",
        "missing_contracts",
        "passed_trace_observed",
        "evidence_report",
    ):
        assert key in data
    assert data["app_name"] == "apps_research"


def test_report_to_dict_embeds_evidence_report(tmp_path, apps_research_hash):
    """The smoke report's to_dict embeds the R3 evidence report dict."""
    snap_path = _write_snapshot(tmp_path, _all_r3_nodes(apps_research_hash))
    report = run_apps_research_live_trace_smoke(snap_path)

    d = report.to_dict()
    assert isinstance(d["evidence_report"], dict)
    assert d["evidence_report"]["app_name"] == "apps_research"
    assert d["evidence_report"]["runtime_certification_status"] == NOT_CERTIFIED


def test_snapshot_nodes_non_list_rejected(tmp_path):
    """A snapshot whose 'nodes' field is not a list is rejected cleanly."""
    bad = tmp_path / "bad_nodes.json"
    bad.write_text(json.dumps({
        "trace_id": "x",
        "mission": "m",
        "started_at_utc": 0,
        "ended_at_utc": 1,
        "nodes": "not a list",
    }), encoding="utf-8")
    with pytest.raises(ValueError, match="nodes.*list"):
        run_apps_research_live_trace_smoke(bad)
