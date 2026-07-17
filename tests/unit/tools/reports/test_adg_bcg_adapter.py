from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from tools.reports.adg_bcg_adapter import (
    build_bcg_brief,
    build_bcg_gate_adapter,
    build_deprecation_deletion_plan,
    build_report_bcg_findings,
    emit_bcg_gate_adapter,
    has_bcg_findings,
    render_bcg_brief_md,
    render_bcg_gate_adapter_md,
)


def _valid_gate_results(snapshot: Path) -> dict:
    return {
        "timestamp": "2026-07-17T12:00:00+00:00",
        "snapshot": snapshot.name,
        "snapshot_path": str(snapshot),
        "snapshot_sha256": hashlib.sha256(snapshot.read_bytes()).hexdigest(),
        "total_gates": 1,
        "overall_exit_code": 0,
        "gates": [
            {
                "gate_id": "G1_test",
                "band": "P0",
                "enforcement": "block",
                "classification": "pass",
                "status": "pass",
                "exit_code": 0,
                "violation_count": 0,
            }
        ],
    }


def _write_adapter_inputs(tmp_path: Path) -> tuple[Path, Path, Path]:
    snapshot = tmp_path / "adg_indexed_07172026_0700.sqlite"
    snapshot.write_bytes(b"sqlite-snapshot")
    gate_results = tmp_path / "adg_gate_results_20260717_120000.json"
    gate_results.write_text(json.dumps(_valid_gate_results(snapshot)), encoding="utf-8")
    burndown = tmp_path / "adg_burndown_table_07172026_0700.json"
    burndown.write_text(
        json.dumps(
            {
                "schema_version": "2.2",
                "summary": {},
                "provenance": {
                    "sqlite_source_path": str(snapshot),
                    "sqlite_source_sha256": hashlib.sha256(snapshot.read_bytes()).hexdigest(),
                },
            }
        ),
        encoding="utf-8",
    )
    return snapshot, gate_results, burndown


def test_emitter_fails_closed_when_gate_results_missing(tmp_path: Path) -> None:
    rc, path = emit_bcg_gate_adapter(
        adg_artifacts_dir=tmp_path,
        ts="07172026_0700",
        gate_results_path=tmp_path / "missing.json",
        burndown_path=tmp_path / "missing-burndown.json",
        docs_dir=tmp_path / "docs",
    )

    assert rc == 2
    assert path is None


def test_emitter_rejects_mixed_snapshot_and_empty_gate_rows(tmp_path: Path) -> None:
    snapshot, gate_results, burndown = _write_adapter_inputs(tmp_path)
    other_snapshot = tmp_path / "adg_indexed_other.sqlite"
    other_snapshot.write_bytes(b"other")

    rc, path = emit_bcg_gate_adapter(
        adg_artifacts_dir=tmp_path,
        ts="07172026_0700",
        gate_results_path=gate_results,
        burndown_path=burndown,
        expected_snapshot_path=other_snapshot,
        docs_dir=tmp_path / "docs",
    )
    assert (rc, path) == (2, None)

    malformed = _valid_gate_results(snapshot)
    malformed["gates"] = [{}]
    gate_results.write_text(json.dumps(malformed), encoding="utf-8")
    rc, path = emit_bcg_gate_adapter(
        adg_artifacts_dir=tmp_path,
        ts="07172026_0700",
        gate_results_path=gate_results,
        burndown_path=burndown,
        expected_snapshot_path=snapshot,
        docs_dir=tmp_path / "docs",
    )
    assert (rc, path) == (2, None)


@pytest.mark.parametrize("fallback_status", ["error", "unknown"])
def test_emitter_accepts_bound_error_evidence_without_negative_totals(
    tmp_path: Path, fallback_status: str
) -> None:
    snapshot, gate_results, burndown = _write_adapter_inputs(tmp_path)
    payload = _valid_gate_results(snapshot)
    payload["overall_exit_code"] = 1
    payload["gates"][0].update(
        {
            "classification": "error",
            "status": fallback_status,
            "exit_code": -1,
            "violation_count": -1,
        }
    )
    gate_results.write_text(json.dumps(payload), encoding="utf-8")

    rc, path = emit_bcg_gate_adapter(
        adg_artifacts_dir=tmp_path,
        ts="07172026_0700",
        gate_results_path=gate_results,
        burndown_path=burndown,
        expected_snapshot_path=snapshot,
        docs_dir=tmp_path / "docs",
    )

    assert rc == 0
    assert path is not None
    adapter = json.loads(path.read_text(encoding="utf-8"))
    row = adapter["sections"]["fix_now"]["rows"][0]
    assert row["sub"] == "error"
    assert row["rows"] == 0
    assert row["evidence_status"] == "error"
    assert adapter["source"]["snapshot_sha256"]


def test_emitter_rejects_unknown_status_without_error_classification_or_nonzero_exit(
    tmp_path: Path,
) -> None:
    snapshot, gate_results, burndown = _write_adapter_inputs(tmp_path)
    payload = _valid_gate_results(snapshot)
    payload["gates"][0]["status"] = "unknown"
    gate_results.write_text(json.dumps(payload), encoding="utf-8")

    rc, path = emit_bcg_gate_adapter(
        adg_artifacts_dir=tmp_path,
        ts="07172026_0700",
        gate_results_path=gate_results,
        burndown_path=burndown,
        expected_snapshot_path=snapshot,
        docs_dir=tmp_path / "docs",
    )

    assert (rc, path) == (2, None)


@pytest.mark.parametrize(
    ("updates", "overall_exit_code"),
    [
        ({"classification": "pass", "status": "fail", "exit_code": 0}, 0),
        ({"classification": "pass", "status": "pass", "exit_code": 1}, 0),
        ({"classification": "blocked", "status": "pass", "exit_code": 1}, 1),
        ({"classification": "error", "status": "error", "exit_code": 0}, 1),
        ({"violation_count": "0"}, 0),
        ({"exit_code": True}, 0),
    ],
)
def test_emitter_rejects_contradictory_or_non_strict_gate_rows(
    tmp_path: Path,
    updates: dict[str, object],
    overall_exit_code: int,
) -> None:
    snapshot, gate_results, burndown = _write_adapter_inputs(tmp_path)
    payload = _valid_gate_results(snapshot)
    payload["overall_exit_code"] = overall_exit_code
    payload["gates"][0].update(updates)
    gate_results.write_text(json.dumps(payload), encoding="utf-8")

    assert emit_bcg_gate_adapter(
        adg_artifacts_dir=tmp_path,
        ts="07172026_0700",
        gate_results_path=gate_results,
        burndown_path=burndown,
        expected_snapshot_path=snapshot,
        docs_dir=tmp_path / "docs",
    ) == (2, None)


def test_emitter_rejects_nonzero_overall_when_all_gate_rows_pass(tmp_path: Path) -> None:
    snapshot, gate_results, burndown = _write_adapter_inputs(tmp_path)
    payload = _valid_gate_results(snapshot)
    payload.update(
        {
            "overall_exit_code": 1,
            "snapshot_changed_during_run": False,
            "fleet_registry_valid": True,
        }
    )
    gate_results.write_text(json.dumps(payload), encoding="utf-8")

    assert emit_bcg_gate_adapter(
        adg_artifacts_dir=tmp_path,
        ts="07172026_0700",
        gate_results_path=gate_results,
        burndown_path=burndown,
        expected_snapshot_path=snapshot,
        docs_dir=tmp_path / "docs",
    ) == (2, None)


@pytest.mark.parametrize(
    ("integrity_field", "integrity_value", "failure_name"),
    [
        ("snapshot_changed_during_run", True, "snapshot_changed_during_run"),
        ("fleet_registry_valid", False, "fleet_registry_invalid"),
    ],
)
def test_emitter_surfaces_dispatcher_integrity_failure_as_synthetic_fix(
    tmp_path: Path,
    integrity_field: str,
    integrity_value: bool,
    failure_name: str,
) -> None:
    snapshot, gate_results, burndown = _write_adapter_inputs(tmp_path)
    payload = _valid_gate_results(snapshot)
    payload["overall_exit_code"] = 1
    payload[integrity_field] = integrity_value
    gate_results.write_text(json.dumps(payload), encoding="utf-8")

    rc, path = emit_bcg_gate_adapter(
        adg_artifacts_dir=tmp_path,
        ts="07172026_0700",
        gate_results_path=gate_results,
        burndown_path=burndown,
        expected_snapshot_path=snapshot,
        docs_dir=tmp_path / "docs",
    )

    assert rc == 0
    assert path is not None
    adapter = json.loads(path.read_text(encoding="utf-8"))
    integrity = next(
        row for row in adapter["sections"]["fix_now"]["rows"] if row["gate_id"] == "run_integrity"
    )
    assert integrity["verdict"] == "FIX"
    assert integrity["sub"] == "error"
    assert integrity["evidence_status"] == "error"
    assert integrity["raw_gate"]["integrity_failures"] == [failure_name]


def test_emitter_can_skip_latest_and_docs_publication(tmp_path: Path) -> None:
    snapshot, gate_results, burndown = _write_adapter_inputs(tmp_path)
    docs = tmp_path / "docs"

    rc, path = emit_bcg_gate_adapter(
        adg_artifacts_dir=tmp_path,
        ts="07172026_0700",
        gate_results_path=gate_results,
        burndown_path=burndown,
        expected_snapshot_path=snapshot,
        docs_dir=docs,
        publish_latest=False,
    )

    assert rc == 0
    assert path == tmp_path / "adg_bcg_adapter_07172026_0700.json"
    assert path.is_file()
    assert path.with_suffix(".md").is_file()
    assert not (tmp_path / "adg_bcg_adapter_latest.json").exists()
    assert not (tmp_path / "adg_bcg_adapter_latest.md").exists()
    assert not docs.exists()


def test_render_bcg_brief_md_uses_shared_business_and_technical_style() -> None:
    brief = build_bcg_brief(
        title="BCG Sample Brief",
        status="PASS",
        status_label="Source status",
        secondary_statuses={"Decision status": "BLOCKED"},
        business_read="Fix the blocker first, then clean the waste.",
        technical_read=["FIX gates: 1", "TRACK gates: 2"],
        decision_gates=[
            {
                "move": "Repair graph/report consistency",
                "why_it_matters": "Ranking is not trustworthy yet.",
                "evidence": "1 mismatch.",
                "next_step": "Repair consistency before ranking work.",
            }
        ],
        priority_rule="Blockers before backlog.",
        priority_rows=[
            {
                "priority": 1,
                "move": "Fix blocker",
                "why_it_matters": "Keeps the run credible.",
                "evidence": "1 red gate.",
                "next_step": "Fix the blocker now.",
                "business_reason": "Keeps the run credible.",
                "technical_reason": "1 red gate.",
                "why_this_rank": "Blocks green.",
                "decision": "now",
                "decision_options": [{"label": "Fix", "description": "Remove the direct dependency."}],
                "done_condition": "The gate is green.",
            }
        ],
        why_this_order=["Confirmed waste first.", "Noise comes after evidence is clean."],
        next_step="Fix blocker",
    )

    md = render_bcg_brief_md(brief)

    assert "Maintain SVP engineer-level repo standards" in md
    assert "### BCG Sample Brief" in md
    assert "- **Source status:** PASS" in md
    assert "- **Decision status:** BLOCKED" in md
    assert "- **Status:** PASS" not in md
    assert "- **Business read:** Fix the blocker first, then clean the waste." in md
    assert "Decision gate:" in md
    assert (
        "| Repair graph/report consistency | Ranking is not trustworthy yet. | 1 mismatch. | Repair consistency before ranking work. |"
        in md
    )
    assert "Fix now:" in md
    assert "| Priority | Move | Why it matters | Evidence | Next step |" in md
    assert "Business reason" not in md
    assert "Technical reason" not in md
    assert "Why this order" not in md
    assert "fix_blocker" not in md
    row = brief["priority_rows"][0]
    assert row["decision_options"]
    assert row["done_condition"] == "The gate is green."


def test_deprecation_deletion_plan_brief_prioritizes_dead_code_before_noise() -> None:
    plan = build_deprecation_deletion_plan(
        {
            "status": "PASS",
            "summary": {
                "total_dead_imports": 0,
                "total_dead_code_candidates": 2,
                "total_unresolved_imports": 17,
                "first_party_low_confidence_ratio": 2.5,
                "inferred_symbol_ratio": 9.0,
            },
            "dead_code_candidates": {
                "dead_code_hotspots": [
                    ("ADG::Module::legacy_path", 4),
                    ("ADG::Module::stale_path", 2),
                ]
            },
            "unresolved_imports": {"unresolved_hotspots": [("ADG::Module::tests/foo.py", 7)]},
            "low_confidence_zones": {"first_party_low_confidence_ratio": 2.5},
            "inferred_symbols": {"inferred_symbol_ratio": 9.0},
        },
        None,
        None,
    )

    assert plan["summary"]["cleanup_candidate_count"] == 0
    assert plan["priority_rows"][0]["scope"] == "ADG::Module::legacy_path"
    assert plan["priority_rows"][0]["decision"] == "delete_after_deprecation"
    assert plan["brief"]["title"] == "BCG Deletion Brief"
    assert plan["brief"]["status"] == "DELETION_CANDIDATES"
    assert plan["brief"]["status_label"] == "Deletion status"
    assert "Confirmed dead code first" in plan["brief"]["priority_rule"]


def test_deprecation_deletion_plan_labels_no_delete_status_not_source_pass() -> None:
    plan = build_deprecation_deletion_plan(
        {
            "status": "PASS",
            "summary": {
                "total_dead_imports": 0,
                "total_dead_code_candidates": 0,
                "total_unresolved_imports": 17,
            },
            "dead_code_candidates": {"dead_code_hotspots": []},
            "unresolved_imports": {"unresolved_hotspots": [("ADG::Module::tests/foo.py", 7)]},
        },
        None,
        None,
    )

    md = render_bcg_brief_md(plan["brief"])

    assert "- **Deletion status:** NO_DELETIONS_APPROVED" in md
    assert "- **Source report status:** PASS" in md
    assert "- **Status:** PASS" not in md


def test_build_report_bcg_findings_emits_required_management_story() -> None:
    findings = build_report_bcg_findings(
        report_kind="adg_test_report",
        title="BCG Test Brief",
        status="BLOCKED",
        status_label="Decision status",
        business_read="Fix the blocker before funding cleanup.",
        technical_read=["FIX gates: 1", "TRACK gates: 2"],
        priority_rule="Blockers before backlog.",
        priority_rows=[
            {
                "priority": 1,
                "move": "Fix blocker",
                "why_it_matters": "The run is not decision-grade while blocked.",
                "evidence": "1 red gate.",
                "next_step": "Fix and rerun ADG.",
            }
        ],
        why_this_order=["Blockers stop the line."],
        next_step="Fix and rerun ADG.",
    )

    assert findings["schema_version"] == "1.0"
    assert findings["report_kind"] == "adg_test_report"
    assert findings["brief"]["title"] == "BCG Test Brief"
    assert findings["business_read"] == "Fix the blocker before funding cleanup."
    assert findings["priority_rows"][0]["move"] == "Fix blocker"
    assert has_bcg_findings({"bcg_findings": findings}) is True
    assert has_bcg_findings({"brief": findings["brief"]}) is True
    assert has_bcg_findings({"not_bcg": {}}) is False


def test_bcg_gate_adapter_separates_kpi_from_burndown() -> None:
    adapter = build_bcg_gate_adapter(
        {
            "timestamp": "run",
            "gates": [
                {
                    "gate_id": "C2_l5_bypass_pview",
                    "band": "P0",
                    "enforcement": "block",
                    "classification": "blocked",
                    "violation_count": 2,
                },
                {
                    "gate_id": "G_REACH_l0_reachability",
                    "band": "P0",
                    "enforcement": "ratchet",
                    "classification": "pass",
                    "violation_count": 2800,
                    "baseline_count": 2800,
                },
                {
                    "gate_id": "S4_unused_imports_ratchet",
                    "band": "P3",
                    "enforcement": "ratchet",
                    "classification": "pass",
                    "violation_count": 10750,
                    "baseline_count": 10750,
                },
                {
                    "gate_id": "D2_role_duplication_warn",
                    "band": "P2",
                    "enforcement": "warn",
                    "classification": "pass",
                    "violation_count": 4,
                },
                {
                    "gate_id": "13_core_imports_apps",
                    "band": "P0",
                    "enforcement": "block",
                    "classification": "blocked",
                    "violation_count": 3,
                },
            ],
        }
    )

    assert adapter["artifact_kind"] == "adg_bcg_gate_adapter"
    assert adapter["sections"]["fix_now"]["gate_count"] == 2
    assert adapter["sections"]["burn_down"]["gate_count"] == 1
    assert adapter["sections"]["kpi_watchlist"]["gate_count"] == 2
    assert adapter["summary"]["priority_queue_gate_count"] == 3
    assert adapter["summary"]["report_only_gate_count"] == 2
    assert {row["gate_id"] for row in adapter["sections"]["kpi_watchlist"]["rows"]} == {
        "S4_unused_imports_ratchet",
        "D2_role_duplication_warn",
    }
    assert adapter["sections"]["fix_now"]["rows"][0]["materiality"] == "core_app_boundary"
    md = render_bcg_gate_adapter_md(adapter)
    assert "## KPI / watchlist" in md
    assert "`S4_unused_imports_ratchet`" in md
