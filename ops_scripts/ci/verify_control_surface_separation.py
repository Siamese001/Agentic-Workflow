"""Verifier — control_surface separation between healing and llm_as_judge.

Per operator directive 2026-05-01 14:15 UTC-04:00. Read-only verifier
that reports violations but does not mutate any file.

Fails (exit 2) when ANY of the following is true:

  1. Any JSON artifact under ``artifacts/certification/`` declares
     ``control_surface = "healing"``. Healing evidence MUST live under
     ``artifacts/healing/`` instead.
  2. Any JSON artifact under ``artifacts/certification/integrated_runtime/
     consensus_jury/`` (panel-attestation directory) lacks top-level
     ``control_surface = "llm_as_judge"``.
  3. Any juror record inside a panel attestation lacks
     ``control_surface = "llm_as_judge"``.
  4. Any JSON artifact under ``artifacts/healing/`` falsely claims
     ``control_surface = "llm_as_judge"`` (reverse-direction spoof).

Exit codes:
  - 0  : PASS (no violations)
  - 2  : FAIL (violations found — report printed)
  - 3  : HARNESS_ERROR (unexpected exception)

Output artifact:
  ``artifacts/certification/control_surface_separation_report.json``
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.certification.safety.rtc_req_056_panel import (
    CONSENSUS_JURY_ARTIFACT_SUBDIR,
    CONTROL_SURFACE as JUDGE_CONTROL_SURFACE,
    PANEL_ATTESTATION_FILENAME,
)

ARTIFACTS_CERTIFICATION = REPO_ROOT / "artifacts" / "certification"
ARTIFACTS_HEALING = REPO_ROOT / "artifacts" / "healing"
PANEL_DIR = (
    ARTIFACTS_CERTIFICATION
    / "integrated_runtime"
    / CONSENSUS_JURY_ARTIFACT_SUBDIR
)
REPORT_PATH = ARTIFACTS_CERTIFICATION / "control_surface_separation_report.json"

HEALING_SURFACE = "healing"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_load(path: Path) -> dict[str, Any] | None:
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def _scan_tree(root: Path) -> list[Path]:
    """Recursively list all .json files under root. Returns [] if absent."""
    if not root.exists():
        return []
    return sorted(p for p in root.rglob("*.json") if p.is_file())


def _find_violations() -> tuple[list[dict[str, Any]], dict[str, int]]:
    violations: list[dict[str, Any]] = []
    counts = {
        "healing_in_certification_tree": 0,
        "panel_missing_control_surface": 0,
        "panel_juror_missing_control_surface": 0,
        "judge_surface_in_healing_tree": 0,
    }

    # Rule 1: artifacts under certification/ declaring control_surface=healing
    for p in _scan_tree(ARTIFACTS_CERTIFICATION):
        doc = _safe_load(p)
        if doc is None:
            continue
        surface = doc.get("control_surface")
        if surface == HEALING_SURFACE:
            counts["healing_in_certification_tree"] += 1
            violations.append({
                "rule": "healing_in_certification_tree",
                "path": str(p.relative_to(REPO_ROOT)),
                "observed_control_surface": surface,
                "expected": JUDGE_CONTROL_SURFACE,
            })

    # Rule 2 + 3: panel attestations in consensus_jury/ must stamp the
    # judge surface at top-level AND per-juror.
    for p in _scan_tree(PANEL_DIR):
        if p.name != PANEL_ATTESTATION_FILENAME:
            continue
        doc = _safe_load(p)
        if doc is None:
            continue
        top = doc.get("control_surface")
        if top != JUDGE_CONTROL_SURFACE:
            counts["panel_missing_control_surface"] += 1
            violations.append({
                "rule": "panel_missing_control_surface",
                "path": str(p.relative_to(REPO_ROOT)),
                "observed_control_surface": top,
                "expected": JUDGE_CONTROL_SURFACE,
            })
        jurors = doc.get("jurors") or []
        if isinstance(jurors, list):
            for i, j in enumerate(jurors):
                if not isinstance(j, dict):
                    continue
                js = j.get("control_surface")
                if js != JUDGE_CONTROL_SURFACE:
                    counts["panel_juror_missing_control_surface"] += 1
                    violations.append({
                        "rule": "panel_juror_missing_control_surface",
                        "path": str(p.relative_to(REPO_ROOT)),
                        "juror_index": i,
                        "juror_id": j.get("juror_id"),
                        "observed_control_surface": js,
                        "expected": JUDGE_CONTROL_SURFACE,
                    })

    # Rule 4: healing tree must NOT claim the judge surface (reverse spoof)
    for p in _scan_tree(ARTIFACTS_HEALING):
        doc = _safe_load(p)
        if doc is None:
            continue
        surface = doc.get("control_surface")
        if surface == JUDGE_CONTROL_SURFACE:
            counts["judge_surface_in_healing_tree"] += 1
            violations.append({
                "rule": "judge_surface_in_healing_tree",
                "path": str(p.relative_to(REPO_ROOT)),
                "observed_control_surface": surface,
                "expected": HEALING_SURFACE,
            })

    return violations, counts


def main() -> int:
    try:
        violations, counts = _find_violations()
    except Exception as exc:  # noqa: BLE001 — harness catch-all
        print(f"[verify_control_surface] HARNESS_ERROR: {exc}", file=sys.stderr)
        return 3

    status = "PASS" if not violations else "FAIL"
    report = {
        "verifier": "verify_control_surface_separation",
        "executed_at_utc": _utc_now(),
        "status": status,
        "counts": counts,
        "violation_count": len(violations),
        "violations": violations,
        "roots_scanned": {
            "certification": str(ARTIFACTS_CERTIFICATION.relative_to(REPO_ROOT)),
            "healing": str(ARTIFACTS_HEALING.relative_to(REPO_ROOT)),
            "panel_dir": str(PANEL_DIR.relative_to(REPO_ROOT)),
        },
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(
        f"[verify_control_surface] {status} "
        f"violations={len(violations)} "
        f"counts={counts}"
    )
    for v in violations[:10]:
        print(
            f"[verify_control_surface]   {v['rule']}: "
            f"{v['path']} (observed={v['observed_control_surface']!r} "
            f"expected={v['expected']!r})"
        )
    if len(violations) > 10:
        print(f"[verify_control_surface]   ... {len(violations) - 10} more")
    print(f"[verify_control_surface] wrote: {REPORT_PATH.relative_to(REPO_ROOT)}")
    return 0 if status == "PASS" else 2


if __name__ == "__main__":
    sys.exit(main())
