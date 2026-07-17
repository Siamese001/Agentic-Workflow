from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from ops_scripts.ci.verify_adg_report_mece import load_bundle_report_inputs, main, validate

RUN_ID = "07172026_1200"


def _write_text(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _write_json(path: Path, value: dict) -> Path:
    return _write_text(path, json.dumps(value, indent=2, sort_keys=True) + "\n")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _adapter() -> dict:
    return {
        "sections": {
            "fix_now": {
                "rows": [
                    {"gate_id": "10_infra_wiring", "band": "P0", "rows": 3},
                    {"gate_id": "S4_unused_imports_ratchet", "band": "P3", "rows": 10},
                ]
            },
            "burn_down": {"rows": [{"gate_id": "G_REACH_l0_reachability", "band": "P0", "rows": 100}]},
            "kpi_watchlist": {"rows": [{"gate_id": "D2_role_duplication_warn", "band": "P2", "rows": 7}]},
            "clear": {"rows": [{"gate_id": "1_critical_path_integrity", "band": "P0", "rows": 0}]},
        }
    }


def _summary() -> dict:
    return {
        "gate_mece_summary": {
            "decision_gates": [
                {
                    "move": "Repair graph/report consistency",
                    "why_it_matters": "Report mismatch.",
                    "evidence": "1 mismatch.",
                    "next_step": "Repair before ranking.",
                }
            ]
        },
        "canonical_next_best_actions": {
            "rows": [
                {
                    "action_type": "fix_blocker",
                    "scope": "10_infra_wiring",
                    "move": "Clear infra wiring P0 block",
                },
                {
                    "action_type": "fix_blocker",
                    "scope": "S4_unused_imports_ratchet",
                    "move": "Remove unused-import regression only",
                },
            ]
        },
    }


def _bundle_fixture(tmp_path: Path) -> tuple[Path, dict[str, Path]]:
    artifacts = tmp_path / "artifacts" / "adg"
    adapter_json = _write_json(
        artifacts / f"adg_bcg_adapter_{RUN_ID}.json",
        {**_adapter(), "source": {"run_id": RUN_ID}},
    )
    adapter_md = _write_text(artifacts / f"adg_bcg_adapter_{RUN_ID}.md", "# Adapter\n")
    burndown_md = _write_text(
        artifacts / f"adg_burndown_report_{RUN_ID}.md",
        "# ADG CI Burndown Report\n",
    )
    action_json = _write_json(artifacts / f"adg_action_queue_{RUN_ID}.json", {"rows": []})
    review_json = _write_json(artifacts / f"adg_review_template_{RUN_ID}.json", {"rows": []})
    review_yaml = _write_text(artifacts / f"adg_review_template_{RUN_ID}.yaml", "rows: []\n")
    summary_json = _write_json(
        artifacts / f"adg_bcg_executive_summary_{RUN_ID}.json",
        {**_summary(), "run": {"run_id": RUN_ID}},
    )
    summary_yaml = _write_text(
        artifacts / f"adg_bcg_executive_summary_{RUN_ID}.yaml",
        f"run:\n  run_id: {RUN_ID}\n",
    )
    summary_md = _write_text(
        artifacts / f"adg_bcg_executive_summary_{RUN_ID}.md",
        "Decision gate:\n\nFix now:\n",
    )
    published_paths = [
        adapter_json,
        adapter_md,
        burndown_md,
        review_json,
        review_yaml,
        summary_json,
        summary_yaml,
        summary_md,
    ]
    publication = _write_json(
        artifacts / f"adg_output_publication_{RUN_ID}.json",
        {
            "schema_version": "adg-output-publication/v1",
            "run_id": RUN_ID,
            "mutable_report_aliases_published": False,
            "artifacts": [{"path": str(path.resolve()), "sha256": _sha256(path)} for path in published_paths],
        },
    )
    paths = {
        "adapter_json": adapter_json,
        "adapter_md": adapter_md,
        "burndown_md": burndown_md,
        "action_json": action_json,
        "review_json": review_json,
        "review_yaml": review_yaml,
        "summary_json": summary_json,
        "summary_yaml": summary_yaml,
        "summary_md": summary_md,
        "publication": publication,
    }
    gate_paths = {
        "bcg_gate_adapter": [adapter_json, adapter_md],
        "burndown_report": [burndown_md],
        "action_queue": [action_json],
        "review_template": [review_json, review_yaml],
        "bcg_executive_summary": [summary_json, summary_yaml, summary_md],
        "latest_publication": [publication],
    }
    manifest = {
        "schema_version": "adg-run-output-bundle/v1",
        "run_id": RUN_ID,
        "status": "complete",
        "gates": [
            {
                "key": key,
                "required": True,
                "status": "pass",
                "producer_exit_code": 0,
                "paths": [str(path.resolve()) for path in values],
                "diagnostic": "",
            }
            for key, values in gate_paths.items()
        ],
        "artifacts": [{"path": str(path.resolve()), "sha256": _sha256(path)} for path in paths.values()],
    }
    manifest_path = _write_json(artifacts / "adg_run_output_bundle_latest.json", manifest)
    return manifest_path, paths


def _reseal_fixture_artifact(manifest_path: Path, paths: dict[str, Path], changed: Path) -> None:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for row in manifest["artifacts"]:
        if row["path"] == str(changed.resolve()):
            row["sha256"] = _sha256(changed)
    publication = json.loads(paths["publication"].read_text(encoding="utf-8"))
    for row in publication["artifacts"]:
        if row["path"] == str(changed.resolve()):
            row["sha256"] = _sha256(changed)
    _write_json(paths["publication"], publication)
    for row in manifest["artifacts"]:
        if row["path"] == str(paths["publication"].resolve()):
            row["sha256"] = _sha256(paths["publication"])
    _write_json(manifest_path, manifest)


def test_verify_adg_report_mece_accepts_separated_decision_and_work_sections() -> None:
    errors = validate(_summary(), _adapter(), "Decision gate:\n\nFix now:\n")

    assert errors == []


def test_verify_adg_report_mece_rejects_decision_gate_in_ranked_actions() -> None:
    summary = _summary()
    summary["canonical_next_best_actions"]["rows"].insert(
        0,
        {
            "action_type": "repair_reporting",
            "scope": "mv_graph_vs_report_mismatches",
            "move": "Repair graph/report consistency",
        },
    )

    errors = validate(summary, _adapter(), "Decision gate:\n\nFix now:\n")

    assert any("decision gate" in error for error in errors)


def test_verify_adg_report_mece_rejects_watchlist_work_overlap() -> None:
    adapter = _adapter()
    adapter["sections"]["burn_down"]["rows"].append(
        {"gate_id": "D2_role_duplication_warn", "band": "P2", "rows": 7}
    )

    errors = validate(_summary(), adapter, "Decision gate:\n\nFix now:\n")

    assert any("KPI/watchlist gate" in error for error in errors)


def test_verify_adg_report_mece_rejects_p3_hygiene_before_p0_live_gate() -> None:
    summary = _summary()
    summary["canonical_next_best_actions"]["rows"] = [
        {
            "action_type": "fix_blocker",
            "scope": "S4_unused_imports_ratchet",
            "move": "Remove unused-import regression only",
        },
        {"action_type": "fix_blocker", "scope": "10_infra_wiring", "move": "Clear infra wiring P0 block"},
    ]

    errors = validate(summary, _adapter(), "Decision gate:\n\nFix now:\n")

    assert any("P3 hygiene gate" in error for error in errors)


def test_verify_adg_report_mece_allows_decision_gate_to_block_p0_ranking() -> None:
    summary = _summary()
    summary["canonical_next_best_actions"]["rows"] = [
        {"action_type": "add_tests", "scope": "unknown", "move": "Fund mapped tests for unknown"},
    ]

    errors = validate(summary, _adapter(), "Decision gate:\n\nFix now:\n")

    assert errors == []


def test_verify_adg_report_mece_still_rejects_p3_hygiene_when_decision_gate_exists() -> None:
    summary = _summary()
    summary["canonical_next_best_actions"]["rows"] = [
        {
            "action_type": "fix_blocker",
            "scope": "S4_unused_imports_ratchet",
            "move": "Remove unused-import regression only",
        },
    ]

    errors = validate(summary, _adapter(), "Decision gate:\n\nFix now:\n")

    assert any("P3 hygiene gate" in error for error in errors)


def test_verify_adg_report_mece_rejects_markdown_without_decision_gate() -> None:
    errors = validate(_summary(), _adapter(), "Fix now:\n")

    assert any("missing a Decision gate" in error for error in errors)


def test_bundle_mode_resolves_one_digest_bound_current_run(tmp_path: Path) -> None:
    manifest_path, paths = _bundle_fixture(tmp_path)

    inputs = load_bundle_report_inputs(manifest_path, repo_root=tmp_path)

    assert inputs.run_id == RUN_ID
    assert inputs.summary_json == paths["summary_json"]
    assert inputs.adapter_json == paths["adapter_json"]
    assert inputs.summary_md == paths["summary_md"]
    assert main(["--bundle-manifest", str(manifest_path)]) == 0


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("schema_version", "adg-run-output-bundle/v0", "schema mismatch"),
        ("status", "blocked", "not complete"),
        ("run_id", "07172026_1159", "required gate paths"),
    ],
)
def test_bundle_mode_rejects_unsealed_or_mixed_manifest_metadata(
    tmp_path: Path,
    field: str,
    value: str,
    message: str,
) -> None:
    manifest_path, _ = _bundle_fixture(tmp_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest[field] = value
    _write_json(manifest_path, manifest)

    with pytest.raises(ValueError, match=message):
        load_bundle_report_inputs(manifest_path, repo_root=tmp_path)


def test_bundle_mode_rejects_required_gate_failure(tmp_path: Path) -> None:
    manifest_path, _ = _bundle_fixture(tmp_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["gates"][0]["status"] = "fail"
    _write_json(manifest_path, manifest)

    with pytest.raises(ValueError, match="did not pass cleanly"):
        load_bundle_report_inputs(manifest_path, repo_root=tmp_path)


def test_bundle_mode_rejects_failed_additional_required_gate(tmp_path: Path) -> None:
    manifest_path, paths = _bundle_fixture(tmp_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["gates"].append(
        {
            "key": "certification",
            "required": True,
            "status": "fail",
            "producer_exit_code": 2,
            "paths": [str(paths["action_json"].resolve())],
            "diagnostic": "failed",
        }
    )
    _write_json(manifest_path, manifest)

    with pytest.raises(ValueError, match="certification"):
        load_bundle_report_inputs(manifest_path, repo_root=tmp_path)


def test_bundle_mode_rejects_artifact_digest_tampering(tmp_path: Path) -> None:
    manifest_path, paths = _bundle_fixture(tmp_path)
    paths["summary_md"].write_text("Decision gate:\n\nFix now:\n\ntampered\n", encoding="utf-8")

    with pytest.raises(ValueError, match="artifact digest mismatch"):
        load_bundle_report_inputs(manifest_path, repo_root=tmp_path)


def test_bundle_mode_rejects_gate_path_tampering_even_when_inventoried(tmp_path: Path) -> None:
    manifest_path, paths = _bundle_fixture(tmp_path)
    replacement = paths["adapter_json"].with_name("adg_bcg_adapter_latest.json")
    replacement.write_bytes(paths["adapter_json"].read_bytes())
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    adapter_gate = next(row for row in manifest["gates"] if row["key"] == "bcg_gate_adapter")
    adapter_gate["paths"][0] = str(replacement.resolve())
    manifest["artifacts"].append({"path": str(replacement.resolve()), "sha256": _sha256(replacement)})
    _write_json(manifest_path, manifest)

    with pytest.raises(ValueError, match="required gate paths"):
        load_bundle_report_inputs(manifest_path, repo_root=tmp_path)


def test_bundle_mode_rejects_summary_source_run_mismatch_with_fresh_digests(tmp_path: Path) -> None:
    manifest_path, paths = _bundle_fixture(tmp_path)
    summary = json.loads(paths["summary_json"].read_text(encoding="utf-8"))
    summary["run"]["run_id"] = "07172026_1159"
    _write_json(paths["summary_json"], summary)
    _reseal_fixture_artifact(manifest_path, paths, paths["summary_json"])

    with pytest.raises(ValueError, match="summary run_id"):
        load_bundle_report_inputs(manifest_path, repo_root=tmp_path)


def test_bundle_mode_rejects_adapter_source_run_mismatch_with_fresh_digests(tmp_path: Path) -> None:
    manifest_path, paths = _bundle_fixture(tmp_path)
    adapter = json.loads(paths["adapter_json"].read_text(encoding="utf-8"))
    adapter["source"]["run_id"] = "07172026_1159"
    _write_json(paths["adapter_json"], adapter)
    _reseal_fixture_artifact(manifest_path, paths, paths["adapter_json"])

    with pytest.raises(ValueError, match="adapter source run_id"):
        load_bundle_report_inputs(manifest_path, repo_root=tmp_path)


def test_all_three_explicit_inputs_bypass_bundle_mode(tmp_path: Path) -> None:
    summary_json = _write_json(tmp_path / "summary.json", _summary())
    adapter_json = _write_json(tmp_path / "adapter.json", _adapter())
    summary_md = _write_text(tmp_path / "summary.md", "Decision gate:\n\nFix now:\n")

    assert (
        main(
            [
                "--bundle-manifest",
                str(tmp_path / "missing-bundle.json"),
                "--summary-json",
                str(summary_json),
                "--adapter-json",
                str(adapter_json),
                "--summary-md",
                str(summary_md),
            ]
        )
        == 0
    )


def test_partial_explicit_inputs_still_use_bundle_mode(tmp_path: Path) -> None:
    manifest_path, _ = _bundle_fixture(tmp_path)

    assert (
        main(
            [
                "--bundle-manifest",
                str(manifest_path),
                "--summary-json",
                str(tmp_path / "ignored.json"),
            ]
        )
        == 0
    )
