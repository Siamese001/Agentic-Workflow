from __future__ import annotations

import json
from datetime import datetime as real_datetime, timezone
from pathlib import Path

from ops_scripts.ci import check_ci_waiver_expiry as waiver_audit
from ops_scripts.ci.classify_ci_lanes import classify
from ops_scripts.ci.write_ci_disposition import main as write_disposition
from tools.eval.run_capability_regression import run


def test_classify_ci_lanes_matches_globs_and_substrings() -> None:
    config = {
        "workflows": {
            "contract-gates": {
                "lanes": {
                    "pytest-config": {"match": ["pyproject.toml", ".github/workflows/**"]},
                    "eval-smoke": {"match": ["tools/eval/**", "tests/**/eval*"]},
                    "terminal-cleanup": {"match": ["ops_scripts/**"]},
                }
            }
        }
    }
    changed = [
        "pyproject.toml",
        "tools/eval/run_capability_regression.py",
        "tests/unit/tools/eval/test_eval_harness_promotion_gate.py",
    ]

    payload = classify("contract-gates", changed, config)

    assert payload["any"] is True
    assert payload["selected_lanes"] == ["pytest-config", "eval-smoke"]
    assert payload["lane_hits"]["terminal-cleanup"] is False


def test_write_ci_disposition_json(tmp_path: Path) -> None:
    out = tmp_path / "ci_disposition.json"
    rc = write_disposition(
        [
            "--workflow",
            "contract-gates",
            "--lane",
            "contract-summary",
            "--status",
            "FAIL_BLOCKING",
            "--reason",
            "one lane failed",
            "--evidence-artifact",
            "contract-gates-123",
            "--selected-lanes-text",
            "pytest-config,eval-smoke",
            "--changed-files-text",
            "pyproject.toml\ntools/eval/run_capability_regression.py",
            "--out",
            str(out),
        ]
    )

    assert rc == 0
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["workflow"] == "contract-gates"
    assert payload["lane"] == "contract-summary"
    assert payload["status"] == "FAIL_BLOCKING"
    assert payload["blocking"] is True
    assert payload["selected_lanes"] == ["pytest-config", "eval-smoke"]
    assert payload["changed_files"] == [
        "pyproject.toml",
        "tools/eval/run_capability_regression.py",
    ]


def test_smoke_mode_limits_trials_per_dimension(tmp_path: Path) -> None:
    rubrics_path = tmp_path / "rubrics.json"
    golden_root = tmp_path / "golden"
    out_smoke = tmp_path / "smoke.json"
    out_full = tmp_path / "full.json"

    rubrics_path.write_text(
        json.dumps(
            {
                "dimensions": {
                    "faithfulness": {
                        "pass_threshold": 4.0,
                        "warn_threshold": 3.0,
                        "unknown_budget": 0.2,
                    }
                },
                "governance_dimensions": {},
                "security_dimensions": {},
                "eval_taxonomy": {
                    "capability": {"min_pass_rate_target": 0.8},
                    "regression": {"min_pass_rate_target": 0.95},
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    dim_dir = golden_root / "rag" / "faithfulness"
    dim_dir.mkdir(parents=True, exist_ok=True)
    _write_item(dim_dir / "example_0001.json", gold_score=5, gold_outcome="scored")
    _write_item(dim_dir / "seed-001.json", gold_score=None, gold_outcome="pending")
    _write_item(dim_dir / "seed-002.json", gold_score=1, gold_outcome="scored")

    smoke_rc = run(rubrics_path, "capability", out_smoke, golden_root, smoke=True, smoke_limit=2)
    smoke_report = json.loads(out_smoke.read_text(encoding="utf-8"))
    assert smoke_rc == 0
    assert smoke_report["mode"] == "smoke"
    assert smoke_report["smoke_limit"] == 2
    assert smoke_report["results"][0]["trials"] == 1
    assert smoke_report["breached"] is False

    full_rc = run(rubrics_path, "capability", out_full, golden_root, smoke=False)
    full_report = json.loads(out_full.read_text(encoding="utf-8"))
    assert full_rc == 1
    assert full_report["mode"] == "full"
    assert full_report["results"][0]["trials"] == 2
    assert full_report["breached"] is True


def test_ci_waiver_expiry_passes_and_fails_with_frozen_date(
    tmp_path: Path, monkeypatch
) -> None:
    waiver_file = tmp_path / "ci_waivers.yaml"
    waiver_file.write_text(
        "waivers:\n"
        "  - workflow: contract-gates\n"
        "    lane: ci-waiver-expiry\n"
        "    reason: temporary exception\n"
        "    owner: platform\n"
        "    expires_on: 2026-06-20\n",
        encoding="utf-8",
    )

    class FrozenDatetime:
        @staticmethod
        def now(tz: timezone) -> real_datetime:
            return real_datetime(2026, 6, 19, tzinfo=tz)

        @staticmethod
        def strptime(value: str, fmt: str) -> real_datetime:
            return real_datetime.strptime(value, fmt)

    monkeypatch.setattr(waiver_audit, "WAIVER_FILE", waiver_file)
    monkeypatch.setattr(waiver_audit, "datetime", FrozenDatetime)
    assert waiver_audit.main([]) == 0

    waiver_file.write_text(
        "waivers:\n"
        "  - workflow: contract-gates\n"
        "    lane: ci-waiver-expiry\n"
        "    reason: temporary exception\n"
        "    owner: platform\n"
        "    expires_on: 2026-06-18\n",
        encoding="utf-8",
    )

    assert waiver_audit.main([]) == 1


def _write_item(path: Path, *, gold_score: int | None, gold_outcome: str) -> None:
    path.write_text(
        json.dumps(
            {
                "item_id": path.stem,
                "rubric_id": "faithfulness",
                "query": "q",
                "context": "c",
                "answer": "a",
                "human_labels": [],
                "gold_score": gold_score,
                "gold_outcome": gold_outcome,
                "created_at": "2026-04-23T00:00:00Z",
                "license": "internal",
            },
            indent=2,
        ),
        encoding="utf-8",
    )
