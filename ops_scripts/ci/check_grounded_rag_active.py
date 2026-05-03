"""check_grounded_rag_active — RAG dim activation gate for grounded apps.

Plan: ``.windsurf/plans/apps-core-contract-rectification-a8f3c2.md`` Phase 5.3.

When C0 retrieval is wired, the 5 grounded apps must promote their RAG dims from
tracked-only (weight=0, fail_closed_if_unknown=false) to active
(weight>0, fail_closed_if_unknown=true).  This gate detects the flip point:

- While C0 is NOT wired: advisory pass for apps with RAG dims listed in
  ``intentional_failopen_dims`` — those are correctly deferred.
- Once any app's threshold profile REMOVES a RAG dim from
  ``intentional_failopen_dims``, this gate checks that the corresponding
  rubric dim also has weight>0 and fail_closed_if_unknown=true.

Checks per grounded app:
    RAG_DIM_WEIGHT_ZERO: a RAG dim NOT in intentional_failopen_dims has weight==0.0
    RAG_DIM_FAILOPEN: a RAG dim NOT in intentional_failopen_dims has
                      fail_closed_if_unknown=false
    RAG_DIM_DEFERRED: RAG dim is in intentional_failopen_dims (INFO — expected until C0)

Exit codes:
    0 — always (advisory)

Promotion path to fail-closed:
    Set env ``GROUNDED_RAG_ACTIVE_FAIL_CLOSED=1`` → ERROR findings exit 1.

Usage::

    python ops_scripts/ci/check_grounded_rag_active.py
    python ops_scripts/ci/check_grounded_rag_active.py --app apps_qna

"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

_GROUNDED_APPS: list[str] = [
    "apps_qna",
    "apps_research",
    "apps_rfp",
    "apps_exec",
    "apps_underwriting_ai",
]

_RAG_DIMS: frozenset[str] = frozenset(
    {"context_recall", "context_precision", "answer_relevancy"}
)


@dataclass
class Finding:
    app_id: str
    check_id: str
    severity: str
    message: str
    dim_id: str = ""


@dataclass
class AppResult:
    app_id: str
    findings: list[Finding] = field(default_factory=list)

    @property
    def errors(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == "ERROR"]

    @property
    def warns(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == "WARN"]

    @property
    def infos(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == "INFO"]


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _intentional_failopen_dims_for_app(app_id: str) -> frozenset[str]:
    """Return RAG dims listed in intentional_failopen_dims across threshold profiles.

    The threshold YAML is a top-level list of profile objects.
    """
    threshold_path = REPO_ROOT / app_id / "config" / "domain_contract" / "threshold_profiles.yaml"
    if not threshold_path.exists():
        return frozenset()
    raw = yaml.safe_load(threshold_path.read_text(encoding="utf-8")) or []
    profile_list: list[dict[str, Any]] = raw if isinstance(raw, list) else [raw]
    dims: set[str] = set()
    for profile in profile_list:
        if not isinstance(profile, dict):
            continue
        for dim_id in profile.get("intentional_failopen_dims", []):
            dims.add(str(dim_id))
    return frozenset(dims)


def _rubric_dims_by_id(app_id: str) -> dict[str, dict[str, Any]]:
    """Return rubric score_dimensions keyed by dimension_id.

    The rubric YAML is a top-level list of rubric objects, each containing a
    ``score_dimensions`` list.  Collect dims from all rubric objects.
    """
    rubric_path = REPO_ROOT / app_id / "config" / "domain_contract" / "eval_rubrics.yaml"
    if not rubric_path.exists():
        return {}
    raw = yaml.safe_load(rubric_path.read_text(encoding="utf-8")) or []
    # Top-level may be a list of rubric objects OR a single dict
    rubric_list: list[dict[str, Any]] = raw if isinstance(raw, list) else [raw]
    result: dict[str, dict[str, Any]] = {}
    for rubric in rubric_list:
        if not isinstance(rubric, dict):
            continue
        for dim in rubric.get("score_dimensions", []):
            if not isinstance(dim, dict):
                continue
            dim_id = dim.get("dimension_id") or dim.get("dim_id", "")
            if dim_id:
                result[str(dim_id)] = dim
    return result


def check_app(app_id: str) -> AppResult:
    result = AppResult(app_id=app_id)
    failopen_dims = _intentional_failopen_dims_for_app(app_id)
    rubric_dims = _rubric_dims_by_id(app_id)

    for dim_id in _RAG_DIMS:
        if dim_id not in rubric_dims:
            continue  # dim not declared yet — not an error

        dim = rubric_dims[dim_id]

        if dim_id in failopen_dims:
            result.findings.append(Finding(
                app_id=app_id,
                check_id="RAG_DIM_DEFERRED",
                severity="INFO",
                message=(
                    f"{app_id} {dim_id}: RAG dim is intentionally fail-open "
                    f"(C0 retrieval not yet wired). Expected state until C0 promotion."
                ),
                dim_id=dim_id,
            ))
            continue

        # Dim is NOT in intentional_failopen_dims — must be active
        weight = float(dim.get("weight", 0.0))
        fail_closed = bool(dim.get("fail_closed_if_unknown", False))

        if weight == 0.0:
            result.findings.append(Finding(
                app_id=app_id,
                check_id="RAG_DIM_WEIGHT_ZERO",
                severity="ERROR",
                message=(
                    f"{app_id} {dim_id}: RAG dim removed from intentional_failopen_dims "
                    f"but weight is still 0.0. Set weight>0 to activate."
                ),
                dim_id=dim_id,
            ))

        if not fail_closed:
            result.findings.append(Finding(
                app_id=app_id,
                check_id="RAG_DIM_FAILOPEN",
                severity="ERROR",
                message=(
                    f"{app_id} {dim_id}: RAG dim removed from intentional_failopen_dims "
                    f"but fail_closed_if_unknown is still false. Set to true to enforce."
                ),
                dim_id=dim_id,
            ))

    return result


def run(apps: list[str] | None = None) -> list[AppResult]:
    targets = apps or _GROUNDED_APPS
    return [check_app(app_id) for app_id in targets]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--app", metavar="APP_ID", help="Check a single app only")
    parser.add_argument(
        "--report",
        metavar="PATH",
        default=str(REPO_ROOT / "artifacts" / "ci" / "grounded_rag_active.json"),
        help="Path to write JSON report",
    )
    args = parser.parse_args(argv)

    apps = [args.app] if args.app else None
    results = run(apps)

    total_errors = sum(len(r.errors) for r in results)
    total_warns = sum(len(r.warns) for r in results)
    total_infos = sum(len(r.infos) for r in results)

    for r in results:
        for f in r.findings:
            print(f"[{f.severity}] {f.check_id}: {f.message}")

    print(
        f"\nGrounded RAG activation gate: "
        f"ERROR={total_errors} WARN={total_warns} INFO={total_infos} "
        f"(apps checked: {len(results)})"
    )

    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(
            {
                "grounded_apps": [r.app_id for r in results],
                "total_errors": total_errors,
                "total_warns": total_warns,
                "total_infos": total_infos,
                "findings": [
                    {
                        "app_id": f.app_id,
                        "check_id": f.check_id,
                        "severity": f.severity,
                        "message": f.message,
                        "dim_id": f.dim_id,
                    }
                    for r in results
                    for f in r.findings
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    fail_closed = os.environ.get("GROUNDED_RAG_ACTIVE_FAIL_CLOSED", "0") == "1"
    if fail_closed and total_errors > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
