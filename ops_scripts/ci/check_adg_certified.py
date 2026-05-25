#!/usr/bin/env python3
"""Gate G-ADG-CERTIFIED — aggregate certification gate (rollup-first).

ADR-081: default path reads ``adg_enforcement_report_*.json`` instead of
re-invoking six subprocess gates. Use ``--legacy-subgates`` to restore the
prior subprocess fleet for parity debugging.

Verdict file: ``docs/reports/adg/ADG_CERTIFIED_VERDICT.json``.
"""

from __future__ import annotations

__adg_consumer_mode__ = "proof"

import argparse
import json
import os
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Final

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

ARTIFACT_DIR: Final[Path] = REPO_ROOT / "artifacts" / "adg"
VERDICT_PATH: Final[Path] = (
    REPO_ROOT / "docs" / "reports" / "adg" / "ADG_CERTIFIED_VERDICT.json"
)

SUB_GATES: Final[tuple[tuple[str, str, bool, bool], ...]] = (
    (
        "graph-layer evidence (snapshot)",
        "ops_scripts/ci/check_snapshot_has_mvs.py",
        True,
        False,
    ),
    (
        "runtime proof view well-formed",
        "ops_scripts/ci/check_runtime_proof_view_well_formed.py",
        True,
        True,
    ),
    (
        "OTel GenAI semconv coverage",
        "ops_scripts/ci/check_otel_genai_semconv_coverage.py",
        True,
        True,
    ),
    (
        "consumer mode declared",
        "ops_scripts/ci/check_consumer_mode_declared.py",
        True,
        False,
    ),
    (
        "three-bucket gap thresholds",
        "ops_scripts/ci/check_three_bucket_gap_thresholds.py",
        True,
        True,
    ),
    (
        "ADG snapshot signed (in-toto/SLSA)",
        "ops_scripts/ci/check_adg_snapshot_signed.py",
        True,
        True,
    ),
    (
        "schema graduation readiness",
        "ops_scripts/ci/check_schema_graduation_readiness.py",
        False,
        True,
    ),
)


def _latest_snapshot() -> Path | None:
    if not ARTIFACT_DIR.exists():
        return None
    try:
        from tools.adg.shared_modules.path_resolver import latest_sqlite  # noqa: PLC0415
    except ImportError:
        files = list(ARTIFACT_DIR.glob("adg_indexed_*.sqlite"))
        from datetime import datetime as _dt  # noqa: PLC0415

        def _valid(p: Path) -> bool:
            try:
                _dt.strptime(p.stem.replace("adg_indexed_", ""), "%m%d%Y_%H%M")
                return True
            except ValueError:
                return False

        valid = [p for p in files if _valid(p)]
        return max(valid, key=lambda p: p.stat().st_mtime) if valid else None
    return latest_sqlite()


def _check_triplet_completeness(snapshot: Path) -> dict[str, object]:
    out: dict[str, object] = {
        "label": "triplet completeness (read-time)",
        "ok": True,
        "details": "",
    }
    if not snapshot.exists():
        out["ok"] = False
        out["details"] = f"snapshot missing: {snapshot}"
        return out
    try:
        con = sqlite3.connect(str(snapshot))
        try:
            null_count = con.execute(
                "SELECT COUNT(*) FROM edges WHERE bucket IS NULL "
                "OR resolution_status IS NULL OR authority_status IS NULL"
            ).fetchone()[0]
            total = con.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
        finally:
            con.close()
    except sqlite3.Error as exc:
        out["ok"] = False
        out["details"] = f"sqlite error: {exc}"
        return out

    out["null_triplet_count"] = null_count
    out["total_edges"] = total
    out["ok"] = null_count == 0
    if not out["ok"]:
        out["details"] = (
            f"{null_count} of {total} edges have NULL in "
            f"(bucket, resolution_status, authority_status)"
        )
    else:
        out["details"] = f"all {total} edges have populated triplet"
    return out


def _rollup_verdict(
    *,
    report_path: Path,
    strict: bool,
) -> tuple[bool, list[str], dict[str, object]]:
    from ops_scripts.ci.adg_enforcement_report import _load_json  # noqa: PLC0415

    report = _load_json(report_path)
    blockers: list[str] = []
    p0 = report.get("p0_bug_gates_failed") or []
    if p0:
        blockers.extend(str(x) for x in p0)
    rollup = str(report.get("certified_rollup", "NOT_CERTIFIED"))
    certified = rollup == "CERTIFIED"
    sub_results: list[dict[str, object]] = [
        {
            "label": "enforcement_report rollup",
            "ok": certified,
            "details": f"path={report_path}",
            "contributes_to_certification": True,
            "rollup": report.get("planes"),
        }
    ]
    if strict and not certified:
        return False, blockers, {"sub_gates": sub_results, "rollup_path": str(report_path)}
    return certified, blockers, {"sub_gates": sub_results, "rollup_path": str(report_path)}


def _run_subgate(
    script_relpath: str, *, strict: bool, accepts_strict_flag: bool
) -> dict[str, object]:
    script = REPO_ROOT / script_relpath
    if not script.is_file():
        return {
            "ok": False,
            "exit_code": -1,
            "details": f"script missing: {script_relpath}",
            "stdout_tail": "",
        }
    cmd = [sys.executable, str(script)]
    if strict and accepts_strict_flag:
        cmd.append("--strict")
    env = os.environ.copy()
    if strict:
        env.setdefault("CONSUMER_MODE_GATE_STRICT", "1")
        env.setdefault("RUNTIME_PROOF_VIEW_STRICT", "1")
        env.setdefault("GENAI_SEMCONV_STRICT", "1")
        env.setdefault("THREE_BUCKET_GAP_STRICT", "1")
        env.setdefault("ADG_SIGNATURE_GATE_STRICT", "1")
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            cwd=REPO_ROOT,
            env=env,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "exit_code": -1,
            "details": "subgate timed out (>120s)",
            "stdout_tail": "",
        }

    return {
        "ok": proc.returncode == 0,
        "exit_code": proc.returncode,
        "details": "",
        "stdout_tail": (proc.stdout or "")[-400:],
    }


def _legacy_subgate_verdict(*, strict: bool, snapshot: Path | None) -> tuple[bool, list[str], list[dict[str, object]]]:
    sub_results: list[dict[str, object]] = []
    blockers: list[str] = []
    if snapshot is not None:
        triplet = _check_triplet_completeness(snapshot)
        sub_results.append(triplet)
        if not triplet["ok"]:
            blockers.append(str(triplet["label"]))
    for label, script, contributes, accepts_strict_flag in SUB_GATES:
        result = _run_subgate(script, strict=strict, accepts_strict_flag=accepts_strict_flag)
        result["label"] = label
        result["script"] = script
        result["contributes_to_certification"] = contributes
        sub_results.append(result)
        if contributes and not result["ok"]:
            blockers.append(label)
    return len(blockers) == 0, blockers, sub_results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Non-zero exit on NOT_CERTIFIED.",
    )
    parser.add_argument("--write-verdict", action="store_true")
    parser.add_argument(
        "--rollup",
        action="store_true",
        help="Read adg_enforcement_report (default unless --legacy-subgates).",
    )
    parser.add_argument(
        "--rollup-path",
        type=Path,
        default=None,
        help="Explicit enforcement report JSON path.",
    )
    parser.add_argument(
        "--legacy-subgates",
        action="store_true",
        help="Re-run subprocess sub-gates (pre-ADR-081 behavior).",
    )
    args = parser.parse_args(argv)

    if os.environ.get("ADG_CERTIFIED_BYPASS") == "1":
        print("[adg_certified] bypass active (ADG_CERTIFIED_BYPASS=1)")
        return 0

    env_strict = os.environ.get("ADG_CERTIFIED_STRICT") == "1"
    args.strict = args.strict or env_strict
    use_rollup = args.rollup or os.environ.get("ADG_CERTIFIED_USE_ROLLUP", "1") == "1"
    use_rollup = use_rollup and not args.legacy_subgates

    snapshot = _latest_snapshot()
    started = datetime.now(timezone.utc)
    blockers: list[str] = []
    sub_results: list[dict[str, object]] = []
    rollup_path: str | None = None

    if use_rollup:
        from ops_scripts.ci.adg_enforcement_report import latest_enforcement_report  # noqa: PLC0415

        report_path = args.rollup_path or latest_enforcement_report()
        if report_path is None or not report_path.is_file():
            print("[adg_certified] WARN no enforcement report — falling back to legacy subgates")
            certified, blockers, sub_results = _legacy_subgate_verdict(
                strict=args.strict, snapshot=snapshot
            )
        else:
            certified, blockers, extra = _rollup_verdict(
                report_path=report_path, strict=args.strict
            )
            sub_results = list(extra.get("sub_gates") or [])
            rollup_path = str(extra.get("rollup_path") or report_path)
    else:
        certified, blockers, sub_results = _legacy_subgate_verdict(
            strict=args.strict, snapshot=snapshot
        )

    verdict = "ADG_CERTIFIED" if certified else "ADG_NOT_CERTIFIED"
    report = {
        "gate": "G-ADG-CERTIFIED",
        "tier": "B",
        "verdict": verdict,
        "strict_mode": args.strict,
        "rollup_mode": use_rollup,
        "rollup_path": rollup_path,
        "timestamp": started.isoformat(),
        "snapshot_used": str(snapshot) if snapshot else None,
        "blockers": blockers,
        "sub_gates": sub_results,
    }

    if args.write_verdict or not VERDICT_PATH.exists() or not certified:
        VERDICT_PATH.parent.mkdir(parents=True, exist_ok=True)
        VERDICT_PATH.write_text(
            json.dumps(report, indent=2, default=str), encoding="utf-8"
        )

    print(
        f"[adg_certified] verdict={verdict} blockers={len(blockers)} "
        f"rollup={use_rollup} strict={args.strict}"
    )
    if blockers:
        print(f"[adg_certified] blockers: {', '.join(blockers)}")
    print(f"[adg_certified] verdict written to {VERDICT_PATH}")

    if not certified and args.strict:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
