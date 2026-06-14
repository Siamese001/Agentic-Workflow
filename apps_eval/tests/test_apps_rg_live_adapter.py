from __future__ import annotations

import json
from pathlib import Path

from apps_eval.adapters.apps_rg import run_apps_rg_live
from apps_eval.contracts import AppOutputSnapshot, EvalRequest
from apps_eval.runner import core as runner


def _complete_payload(tmp_path: Path) -> dict[str, str]:
    brief = tmp_path / "brief.md"
    brief.write_text("enterprise AI platform modernization briefing\n", encoding="utf-8")
    resume = tmp_path / "resume.json"
    resume.write_text('{"candidate_name":"Test Candidate"}\n', encoding="utf-8")
    return {
        "generation_mode": "strategic_tailor",
        "jd": "Lead enterprise AI platform modernization.",
        "manual_brief": str(brief),
        "resume_path": str(resume),
        "target_company": "ExampleCo",
        "target_role": "SVP Engineering",
    }


def test_apps_rg_live_preflight_requires_targeting_inputs(tmp_path: Path) -> None:
    snapshot = run_apps_rg_live(
        "resume_tailor_basic",
        {"target_company": "ExampleCo"},
        tmp_path / "run",
    )

    assert snapshot.x3_disposition == "PRECHECK_FAILED"
    errors = snapshot.output["preflight"]["errors"]
    assert "missing_required_input:target_role" in errors
    assert "missing_required_input:jd" in errors
    assert "apps_rg_live_preflight.json" in snapshot.artifacts


def test_apps_rg_live_preflight_blocks_windows_risky_artifact_root(tmp_path: Path) -> None:
    long_root = tmp_path
    for idx in range(9):
        long_root = long_root / f"very_long_artifact_segment_{idx:02d}"

    snapshot = run_apps_rg_live(
        "resume_tailor_basic",
        _complete_payload(tmp_path),
        long_root,
    )

    assert snapshot.x3_disposition == "PRECHECK_FAILED"
    errors = snapshot.output["preflight"]["errors"]
    assert any(error.startswith("windows_path_budget_exceeded") for error in errors)
    assert not long_root.exists()


def test_apps_rg_live_normalizes_generated_resume(monkeypatch, tmp_path: Path) -> None:
    import agentic_core.runtime.entry.apps_rg_dispatch as dispatch_module

    def fake_dispatch_apps_rg_run(**kwargs: str) -> dict[str, object]:
        artifact_dir = Path(kwargs["artifact_dir"])
        out_dir = artifact_dir / "outputs"
        out_dir.mkdir(parents=True, exist_ok=True)
        generated = {
            "sections": {
                "summary": {"text": "Strategic technology leader for enterprise AI platforms."},
                "experience": [
                    {
                        "title": "SVP Engineering",
                        "bullets": [
                            {
                                "text": "Led modernization programs.",
                                "source_id": "resume:leadership",
                            }
                        ],
                    }
                ],
                "skills": {"categories": [{"name": "AI strategy"}]},
            }
        }
        (out_dir / "generated_resume.json").write_text(
            json.dumps(generated, indent=2),
            encoding="utf-8",
        )
        return {
            "artifact_dir": str(artifact_dir),
            "execution_status": "completed",
            "exit_status": "success",
            "fault": "",
            "outcome_authorized": True,
            "x3_disposition": "X3D",
        }

    monkeypatch.setattr(dispatch_module, "dispatch_apps_rg_run", fake_dispatch_apps_rg_run)

    snapshot = run_apps_rg_live(
        "resume_tailor_basic",
        _complete_payload(tmp_path),
        tmp_path / "run",
    )

    assert snapshot.x3_disposition == "X3D_ALLOW_FINISH"
    assert "resume.md" in snapshot.artifacts
    assert "generated_resume.json" in snapshot.artifacts
    assert snapshot.output["sections"]["executive_summary"].startswith("Strategic technology")
    assert "Led modernization programs" in snapshot.output["sections"]["experience"]
    assert "AI strategy" in snapshot.output["sections"]["skills"]
    assert snapshot.provenance["evidence_refs"] == ["resume:leadership"]
    assert (tmp_path / "run" / "resume.md").is_file()


def test_apps_rg_live_runner_uses_compact_artifact_paths(monkeypatch, tmp_path: Path) -> None:
    captured: list[Path] = []

    def fake_run_apps_rg_live(scenario_id: str, payload: dict[str, object], artifact_dir: Path) -> AppOutputSnapshot:
        captured.append(artifact_dir)
        return AppOutputSnapshot(
            app_id="apps_rg",
            scenario_id=scenario_id,
            x3_disposition="X3D_ALLOW_FINISH",
            output={
                "sections": {
                    "executive_summary": "summary",
                    "experience": "experience",
                    "skills": "skills",
                }
            },
            claims=[
                {
                    "id": "claim",
                    "source_ids": ["resume:leadership"],
                    "supported": True,
                    "text": "claim",
                }
            ],
            artifacts=["resume.md"],
            provenance={"evidence_refs": ["resume:leadership"]},
            side_effects={"product_state_mutated": False, "writes": []},
        )

    monkeypatch.setattr(runner, "run_apps_rg_live", fake_run_apps_rg_live)

    record = runner.run_eval(
        EvalRequest(
            suite_id="apps_rg.dev.resume_generation",
            mode="live_adapter",
            deterministic_only=False,
            out_dir=str(tmp_path),
        )
    )

    assert captured
    assert all("la" in path.parts for path in captured)
    assert all("live_adapter_artifacts" not in path.parts for path in captured)
    assert all(len(path.name) == 8 for path in captured)
    live_snapshots = Path(record.artifact_paths["live_snapshots"])
    assert live_snapshots.is_dir()
    assert len(list(live_snapshots.glob("*.json"))) == len(captured)
