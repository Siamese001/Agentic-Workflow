from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_eval.scenarios import scaffold_apps_rg_scenario, validate_suite_fixtures


def test_scaffold_apps_rg_scenario_writes_contract_tree(tmp_path: Path) -> None:
    result = scaffold_apps_rg_scenario(
        "resume_tailor_new_case",
        "Checks a new resume tailoring behavior.",
        fixture_root=tmp_path,
    )

    root = Path(result.fixture_root)
    assert root == tmp_path / "resume_tailor_new_case"
    assert (root / "scenario.yaml").is_file()
    assert (root / "input" / "request.json").is_file()
    assert (root / "expected" / "expectations.json").is_file()
    assert (root / "snapshots" / "app_output_snapshot.json").is_file()
    assert (root / "snapshots" / "artifacts" / "resume.md").is_file()

    scenario = json.loads((root / "scenario.yaml").read_text(encoding="utf-8"))
    snapshot = json.loads((root / "snapshots" / "app_output_snapshot.json").read_text(encoding="utf-8"))
    assert scenario["scenario_id"] == "resume_tailor_new_case"
    assert snapshot["scenario_id"] == "resume_tailor_new_case"
    assert snapshot["deterministic_hash"]


def test_scaffold_apps_rg_scenario_rejects_unsafe_id(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        scaffold_apps_rg_scenario("Resume Tailor", "bad id", fixture_root=tmp_path)


def test_scaffold_apps_rg_scenario_refuses_overwrite(tmp_path: Path) -> None:
    scaffold_apps_rg_scenario("resume_tailor_new_case", "first", fixture_root=tmp_path)

    with pytest.raises(FileExistsError):
        scaffold_apps_rg_scenario("resume_tailor_new_case", "second", fixture_root=tmp_path)


def test_validate_suite_fixtures_accepts_current_apps_rg_dev_suite() -> None:
    assert validate_suite_fixtures("apps_rg.dev.resume_generation") == []


def test_validate_suite_fixtures_flags_bad_snapshot_hash(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    scaffold_apps_rg_scenario("resume_tailor_new_case", "new case", fixture_root=tmp_path)
    snapshot = tmp_path / "resume_tailor_new_case" / "snapshots" / "app_output_snapshot.json"
    data = json.loads(snapshot.read_text(encoding="utf-8"))
    data["output"]["sections"]["skills"] = "changed without hash update"
    snapshot.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")

    import apps_eval.scenarios as scenarios

    monkeypatch.setattr(
        scenarios,
        "load_suite",
        lambda suite_id: {
            "suite_id": suite_id,
            "app_id": "apps_rg",
            "fixture_root": str(tmp_path),
            "scenarios": ["resume_tailor_new_case"],
        },
    )
    problems = validate_suite_fixtures("apps_rg.dev.resume_generation")

    assert "resume_tailor_new_case: deterministic_hash mismatch" in problems
