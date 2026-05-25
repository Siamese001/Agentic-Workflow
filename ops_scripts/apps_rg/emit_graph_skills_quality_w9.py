#!/usr/bin/env python3
"""W9: graph-skills operator guide on disk + fixture digest contract."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

PLAN_ID = "graph-skills-quality-enhancement-c4e8a1"
GUIDE = REPO / "docs" / "apps_rg" / "graph_skills_quality_operator_guide.md"
REPORTS = REPO / "docs" / "reports" / "apps_rg"
W9_JSON = REPORTS / "graph_skills_quality_w9_operator_guide.json"
RECEIPT_W9 = REPORTS / "graph_skills_quality_w9_receipt.json"
PYTEST_TARGET = "tests/unit/apps_rg/test_graph_skills_operator_guide_w9.py"

FIXTURE_PINS: dict[str, str] = {
    "apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt": (
        "3701dd5b1d6e0c92db394d6bf1879574e4ad638094d9b453f6d35e264e8e573f"
    ),
    "apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md": (
        "97b306a10498240fd676e9ce2d9d3fd00139d6f441d0401224e223456a95c78b"
    ),
    "apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing_exec.md": (
        "74bd4674f23f17236abf3e5a3837e7fd422d6691e2f7e1dc234653f11a6da1f6"
    ),
}

REQUIRED_GUIDE_MARKERS: tuple[str, ...] = (
    "python -m apps_rg --section",
    "Canonical whole-resume CLI",
    "Brown fixture identity",
    "3701dd5b1d6e0c92db394d6bf1879574e4ad638094d9b453f6d35e264e8e573f",
    "briefing_exec.md",
    "briefing.md",
    "Forbidden as product proof",
    "CONTRACT_TEST_PROOF",
    "REAL_LLM_RUNTIME_PROOF",
    "emit_graph_skills_quality_w9.py",
    "augmented_skills_graph",
    "NEG-6",
    "graph_skills_utilization_receipt.json",
    "lane_registry.py",
)


def _git_commit() -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO,
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        )
        return out.stdout.strip()
    except (subprocess.SubprocessError, OSError):
        return "unknown"


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def _run_pytest() -> tuple[bool, str]:
    env = {**dict(__import__("os").environ), "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"}
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", PYTEST_TARGET, "-q", "-o", "addopts="],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
        env=env,
    )
    tail = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode == 0, tail[-2000:]


def _validate_guide() -> tuple[bool, list[str]]:
    failures: list[str] = []
    if not GUIDE.is_file():
        return False, ["guide_missing"]
    text = GUIDE.read_text(encoding="utf-8")
    for marker in REQUIRED_GUIDE_MARKERS:
        if marker not in text:
            failures.append(f"missing_marker:{marker}")
    return not failures, failures


def _validate_fixture_digests() -> tuple[bool, list[dict[str, str]]]:
    rows: list[dict[str, str]] = []
    failures: list[str] = []
    for rel, pinned in FIXTURE_PINS.items():
        path = REPO / Path(rel)
        if not path.is_file():
            failures.append(f"missing_fixture:{rel}")
            rows.append({"path": rel, "pinned": pinned, "actual": "", "pass": False})
            continue
        actual = _sha256_file(path)
        ok = actual == pinned
        rows.append({"path": rel, "pinned": pinned, "actual": actual, "pass": ok})
        if not ok:
            failures.append(f"digest_mismatch:{rel}")
    return not failures, rows


def main() -> int:
    REPORTS.mkdir(parents=True, exist_ok=True)
    pytest_ok, pytest_tail = _run_pytest()
    guide_ok, guide_failures = _validate_guide()
    digest_ok, digest_rows = _validate_fixture_digests()
    aggregate_pass = guide_ok and digest_ok and pytest_ok

    doc = {
        "plan_id": PLAN_ID,
        "wave": "W9",
        "gate_id": "G-W9",
        "proof_class": "CONTRACT_TEST_PROOF",
        "operator_guide_path": str(GUIDE.relative_to(REPO)).replace("\\", "/"),
        "guide_present": GUIDE.is_file(),
        "guide_markers_pass": guide_ok,
        "guide_failures": guide_failures,
        "fixture_digests": digest_rows,
        "fixture_digests_pass": digest_ok,
        "contract_test_pass": pytest_ok,
        "aggregate_pass": aggregate_pass,
        "git_commit": _git_commit(),
        "emitted_at": datetime.now(timezone.utc).isoformat(),
    }
    W9_JSON.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")

    status = "PASS" if aggregate_pass else "FAIL"
    receipt = {
        "plan_id": PLAN_ID,
        "wave": "W9",
        "status": status,
        "proof_classes": {"contract": "PASS" if aggregate_pass else "FAIL"},
        "artifacts": {
            "operator_guide": doc["operator_guide_path"],
            "w9_json": str(W9_JSON.relative_to(REPO)).replace("\\", "/"),
        },
        "pytest_tail": pytest_tail,
        "git_commit": doc["git_commit"],
        "emitted_at": doc["emitted_at"],
    }
    RECEIPT_W9.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")

    print(f"STATUS: {status}")
    print(f"GUIDE: {GUIDE}")
    print(f"JSON: {W9_JSON}")
    return 0 if aggregate_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
