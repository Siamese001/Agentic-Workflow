"""Scenario scaffolding and validation helpers for apps_eval."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from apps_eval.registry import load_graders_registry, load_suite

_SCENARIO_ID = re.compile(r"^[a-z0-9][a-z0-9_]{2,80}$")
_DEFAULT_APPS_RG_FIXTURE_ROOT = Path("apps_eval/fixtures/dev/apps_rg")
_SCENARIO_KEYS = {"description", "graders", "scenario_id"}
_EXPECTATION_KEYS = {
    "allow_side_effects",
    "escalation_required",
    "expected_x3",
    "forbidden_terms",
    "grounded_claims_required",
    "length_bounds",
    "required_artifacts",
    "required_output_keys",
    "required_provenance",
    "required_sections",
}
_SNAPSHOT_KEYS = {
    "app_id",
    "artifacts",
    "claims",
    "deterministic_hash",
    "output",
    "provenance",
    "scenario_id",
    "side_effects",
    "x3_disposition",
}


@dataclass(frozen=True)
class ScenarioScaffoldResult:
    scenario_id: str
    fixture_root: str
    files_written: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "scenario_id": self.scenario_id,
            "fixture_root": self.fixture_root,
            "files_written": self.files_written,
        }


def _write_json(path: Path, data: dict[str, Any], overwrite: bool) -> bool:
    if path.exists() and not overwrite:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return True


def _stable_hash(data: dict[str, Any]) -> str:
    snapshot = dict(data)
    snapshot.pop("deterministic_hash", None)
    raw = json.dumps(snapshot, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _load_json_object(path: Path, problems: list[str], scenario_id: str) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        problems.append(f"{scenario_id}: invalid json {path.as_posix()}: {exc}")
        return {}
    if not isinstance(data, dict):
        problems.append(f"{scenario_id}: expected object in {path.as_posix()}")
        return {}
    return data


def _unknown_keys(data: dict[str, Any], allowed: set[str]) -> list[str]:
    return sorted(set(data) - allowed)


def _require_keys(data: dict[str, Any], keys: set[str], label: str, problems: list[str], scenario_id: str) -> None:
    missing = sorted(keys - set(data))
    if missing:
        problems.append(f"{scenario_id}: missing {label} keys {missing}")


def _apps_rg_expectations() -> dict[str, Any]:
    return {
        "allow_side_effects": False,
        "escalation_required": False,
        "expected_x3": "X3D_ALLOW_FINISH",
        "forbidden_terms": ["salary", "age", "photo", "married", "race", "religion"],
        "grounded_claims_required": True,
        "length_bounds": {"max_words": 160, "min_words": 12},
        "required_artifacts": ["resume.md"],
        "required_output_keys": ["sections"],
        "required_provenance": ["resume:leadership"],
        "required_sections": ["executive_summary", "experience", "skills"],
    }


def _apps_rg_snapshot(scenario_id: str) -> dict[str, Any]:
    snapshot = {
        "app_id": "apps_rg",
        "artifacts": ["resume.md"],
        "claims": [
            {
                "id": "rg_claim_1",
                "source_ids": ["resume:leadership"],
                "supported": True,
                "text": "Led modernization programs",
            }
        ],
        "output": {
            "sections": {
                "executive_summary": (
                    "Strategic technology leader aligning platform modernization, governed AI delivery, "
                    "and measurable operating outcomes for enterprise teams."
                ),
                "experience": (
                    "Led cross-functional modernization programs, improved delivery governance, and "
                    "translated evidence-backed achievements into role-relevant resume language."
                ),
                "skills": (
                    "AI strategy, platform modernization, stakeholder leadership, governance, analytics, "
                    "enterprise transformation."
                ),
            }
        },
        "provenance": {"evidence_refs": ["resume:leadership"], "rubric_refs": []},
        "scenario_id": scenario_id,
        "side_effects": {"product_state_mutated": False, "writes": []},
        "x3_disposition": "X3D_ALLOW_FINISH",
    }
    snapshot["deterministic_hash"] = _stable_hash(snapshot)
    return snapshot


def scaffold_apps_rg_scenario(
    scenario_id: str,
    description: str,
    *,
    fixture_root: str | Path = _DEFAULT_APPS_RG_FIXTURE_ROOT,
    overwrite: bool = False,
) -> ScenarioScaffoldResult:
    """Create a small apps_rg dev scenario fixture tree."""

    if not _SCENARIO_ID.fullmatch(scenario_id):
        raise ValueError("scenario_id must be lowercase snake_case, 3-81 characters")
    root = Path(fixture_root) / scenario_id
    if root.exists() and any(root.iterdir()) and not overwrite:
        raise FileExistsError(f"scenario already exists: {root}")

    files: list[str] = []
    writes = {
        root / "scenario.yaml": {
            "description": description,
            "graders": [
                "schema",
                "artifact_presence",
                "x3_disposition",
                "forbidden_content",
                "grounded_claim",
                "provenance",
                "section_structure",
                "length_bounds",
                "side_effect",
                "escalation",
                "determinism",
            ],
            "scenario_id": scenario_id,
        },
        root / "input" / "request.json": {
            "generation_mode": "strategic_tailor",
            "jd": "Lead enterprise AI platform modernization.",
            "target_company": "ExampleCo",
            "target_role": "SVP Engineering",
        },
        root / "expected" / "expectations.json": _apps_rg_expectations(),
        root / "snapshots" / "app_output_snapshot.json": _apps_rg_snapshot(scenario_id),
    }
    for path, data in writes.items():
        if _write_json(path, data, overwrite):
            files.append(path.as_posix())

    artifact = root / "snapshots" / "artifacts" / "resume.md"
    if overwrite or not artifact.exists():
        artifact.parent.mkdir(parents=True, exist_ok=True)
        artifact.write_text(
            "# Resume\n\n"
            "## Executive Summary\n\n"
            f"{writes[root / 'snapshots' / 'app_output_snapshot.json']['output']['sections']['executive_summary']}\n",
            encoding="utf-8",
        )
        files.append(artifact.as_posix())

    return ScenarioScaffoldResult(
        scenario_id=scenario_id,
        fixture_root=root.as_posix(),
        files_written=files,
    )


def validate_suite_fixtures(suite_id: str) -> list[str]:
    """Return fixture contract problems for a suite; empty means valid."""

    suite = load_suite(suite_id)
    problems: list[str] = []
    known_graders = set(load_graders_registry())
    suite_app_id = str(suite["app_id"])
    root = Path(str(suite["fixture_root"]))
    for scenario_id in suite.get("scenarios", []):
        scenario_root = root / scenario_id
        required = [
            scenario_root / "scenario.yaml",
            scenario_root / "input" / "request.json",
            scenario_root / "expected" / "expectations.json",
            scenario_root / "snapshots" / "app_output_snapshot.json",
        ]
        for path in required:
            if not path.is_file():
                problems.append(f"{scenario_id}: missing {path.as_posix()}")
        artifacts = scenario_root / "snapshots" / "artifacts"
        if not artifacts.is_dir():
            problems.append(f"{scenario_id}: missing {artifacts.as_posix()}")
            continue
        scenario_path = scenario_root / "scenario.yaml"
        expected_path = scenario_root / "expected" / "expectations.json"
        snapshot_path = scenario_root / "snapshots" / "app_output_snapshot.json"
        scenario = _load_json_object(scenario_path, problems, scenario_id) if scenario_path.is_file() else {}
        expected = _load_json_object(expected_path, problems, scenario_id) if expected_path.is_file() else {}
        if scenario:
            unknown = _unknown_keys(scenario, _SCENARIO_KEYS)
            if unknown:
                problems.append(f"{scenario_id}: unknown scenario keys {unknown}")
            _require_keys(scenario, _SCENARIO_KEYS, "scenario", problems, scenario_id)
            if scenario.get("scenario_id") != scenario_id:
                problems.append(f"{scenario_id}: scenario_id mismatch in scenario.yaml")
            graders = scenario.get("graders")
            if not isinstance(graders, list) or not all(isinstance(item, str) for item in graders):
                problems.append(f"{scenario_id}: graders must be a list of strings")
            else:
                bad_graders = sorted(set(graders) - known_graders)
                if bad_graders:
                    problems.append(f"{scenario_id}: unknown graders {bad_graders}")
        if expected:
            unknown = _unknown_keys(expected, _EXPECTATION_KEYS)
            if unknown:
                problems.append(f"{scenario_id}: unknown expectation keys {unknown}")
            _require_keys(expected, _EXPECTATION_KEYS, "expectation", problems, scenario_id)
            for key in ("required_artifacts", "required_output_keys", "required_provenance", "required_sections"):
                if not isinstance(expected.get(key), list):
                    problems.append(f"{scenario_id}: {key} must be a list")
            for artifact_name in expected.get("required_artifacts", []):
                if isinstance(artifact_name, str) and not (artifacts / artifact_name).is_file():
                    problems.append(f"{scenario_id}: missing required artifact {artifact_name}")
        if snapshot_path.is_file():
            data = _load_json_object(snapshot_path, problems, scenario_id)
            unknown = _unknown_keys(data, _SNAPSHOT_KEYS)
            if unknown:
                problems.append(f"{scenario_id}: unknown snapshot keys {unknown}")
            _require_keys(data, _SNAPSHOT_KEYS, "snapshot", problems, scenario_id)
            if data.get("scenario_id") != scenario_id:
                problems.append(f"{scenario_id}: scenario_id mismatch in snapshot")
            if data.get("app_id") != suite_app_id:
                problems.append(f"{scenario_id}: app_id mismatch in snapshot")
            output = data.get("output")
            if expected and isinstance(output, dict):
                missing_output = [key for key in expected.get("required_output_keys", []) if key not in output]
                if missing_output:
                    problems.append(f"{scenario_id}: snapshot missing output keys {missing_output}")
                sections = output.get("sections") if isinstance(output.get("sections"), dict) else output
                missing_sections = [key for key in expected.get("required_sections", []) if key not in sections]
                if missing_sections:
                    problems.append(f"{scenario_id}: snapshot missing sections {missing_sections}")
            expected_hash = data.get("deterministic_hash")
            actual_hash = _stable_hash(data)
            if expected_hash != actual_hash:
                problems.append(f"{scenario_id}: deterministic_hash mismatch")
    return problems
