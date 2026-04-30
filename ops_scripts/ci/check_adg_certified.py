#!/usr/bin/env python3
"""Gate G-ADG-CERTIFIED — the aggregate certification gate.

ADG consumer mode: ``proof`` — this gate's verdict is the final word on
whether a snapshot is CERTIFIED. It runs every sub-gate that contributes
to the three-bucket authority model's correctness invariants and returns
a single ``ADG_CERTIFIED`` / ``ADG_NOT_CERTIFIED`` verdict with structured
per-gate breakdown.

Sub-gates aggregated:

  1. **graph-layer evidence** — `check_graph_layer_evidence.py` /
     `check_snapshot_has_mvs.py` ensure mv_*/v_p* views populated.
  2. **runtime proof view well-formed** — `check_runtime_proof_view_well_formed.py`
     asserts every AUTHORITATIVE_RUNTIME row has a real trace_id.
  3. **OTel GenAI semconv coverage** — `check_otel_genai_semconv_coverage.py`
     asserts ≥80% of agent/workflow/tool span emitters use the
     standardized ``gen_ai.*`` attributes.
  4. **consumer mode declared** — `check_consumer_mode_declared.py`
     asserts every ADG consumer file declares its mode.
  5. **triplet completeness** — every edges row has non-null
     (bucket, resolution_status, authority_status) post-backfill (the W7
     graduation assertion in `ArtifactPaths.py` enforces this at write
     time; this gate verifies it at read time as defense in depth).

Verdict logic:

  * ALL sub-gates exit 0 in strict mode -> ADG_CERTIFIED.
  * ANY sub-gate exit non-zero in strict mode -> ADG_NOT_CERTIFIED with
    the failing gate reported.
  * Advisory-mode gates that report violations but exit 0 -> reported
    as `coverage<threshold` in the report; do NOT block certification
    until they are graduated to strict.

Plan: ``.windsurf/plans/three-bucket-otel-view-5db409.md`` (W7).

USAGE
=====

::

    # Default: advisory mode — runs every sub-gate but does not block.
    python ops_scripts/ci/check_adg_certified.py

    # Strict: any sub-gate failure produces a non-zero exit and a
    # NOT_CERTIFIED verdict.
    python ops_scripts/ci/check_adg_certified.py --strict

    # CI-friendly: write the verdict file unconditionally.
    python ops_scripts/ci/check_adg_certified.py --write-verdict

Verdict file: ``docs/reports/adg/ADG_CERTIFIED_VERDICT.json``.
"""

from __future__ import annotations

# This gate aggregates other gates; it produces a proof-level certification.
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


# Sub-gate registry: (label, script_relpath, contributes_to_certification, accepts_strict_flag)
SUB_GATES: Final[tuple[tuple[str, str, bool, bool], ...]] = (
    (
        "graph-layer evidence (snapshot)",
        "ops_scripts/ci/check_snapshot_has_mvs.py",
        True,
        False,  # Existing gate has no --strict arg
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
        True,  # W3 of three-bucket-gap-remediation-069806: migration complete (100%).
        True,
    ),
    (
        "consumer mode declared",
        "ops_scripts/ci/check_consumer_mode_declared.py",
        True,
        False,  # Activated via env var, not flag
    ),
    (
        "three-bucket gap thresholds",
        "ops_scripts/ci/check_three_bucket_gap_thresholds.py",
        True,  # W5 of three-bucket-gap-remediation-069806.
        True,
    ),
    (
        "ADG snapshot signed (in-toto/SLSA)",
        "ops_scripts/ci/check_adg_snapshot_signed.py",
        True,  # W6 of three-bucket-gap-remediation-069806.
        True,
    ),
    (
        "schema graduation readiness",
        "ops_scripts/ci/check_schema_graduation_readiness.py",
        False,  # W7 — advisory until 4-week green window closes.
        True,
    ),
)


def _latest_snapshot() -> Path | None:
    """Resolve the latest valid ADG snapshot.

    Delegates to the canonical ``tools.adg.shared_modules.path_resolver.latest_sqlite``
    which validates ``%m%d%Y_%H%M`` timestamps and picks by mtime. This rejects
    the legacy sentinel ``adg_indexed_99999999_9999.sqlite`` (month 99 is
    invalid) — without this delegation, the previous naive
    ``sorted(glob())[-1]`` would shadow the real snapshot with any sentinel
    that test code or archiver cleanup left behind.

    Regression precedent (2026-04-30): a sentinel was shadowing the real
    snapshot and this gate falsely reported ``ADG_NOT_CERTIFIED`` via a
    "triplet completeness" blocker, despite the real snapshot having all
    762,238 edges properly triplet-attested.
    """
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
    """Defense-in-depth: read-time check that all edges have non-null triplet."""
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


def _run_subgate(
    script_relpath: str, *, strict: bool, accepts_strict_flag: bool
) -> dict[str, object]:
    """Invoke a sub-gate as a subprocess and capture its result.

    Sub-gates that accept ``--strict`` get the flag when ``strict=True``.
    Sub-gates that activate via env var (e.g. ``CONSUMER_MODE_GATE_STRICT``)
    are not given the flag — those env vars are set in the inherited env
    when ``strict`` is passed.
    """
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
        # Activate strict mode for env-flag-based gates.
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Run every sub-gate in strict mode; non-zero exits produce NOT_CERTIFIED.",
    )
    parser.add_argument(
        "--write-verdict",
        action="store_true",
        help="Always write the verdict file (default: only on certification change).",
    )
    args = parser.parse_args(argv)

    # W6 P6.1 completion-audit (2026-04-30): env-var surface matches the
    # rest of the 3B-tier gates.
    # - ADG_CERTIFIED_BYPASS=1 : skip the gate entirely (logs a one-line
    #   notice, exits 0). Mirrors APPS_SPINE_DELEGATION_GATE_BYPASS,
    #   THREE_BUCKET_GAP_BYPASS, etc.
    # - ADG_CERTIFIED_STRICT=1 : treat the run as strict even without the
    #   --strict CLI flag. The CLI flag wins when both are set in the
    #   "advisory" direction (CLI can only INCREASE strictness, not
    #   decrease it — same semantics as THREE_BUCKET_GAP_STRICT).
    if os.environ.get("ADG_CERTIFIED_BYPASS") == "1":
        print("[adg_certified] bypass active (ADG_CERTIFIED_BYPASS=1)")
        return 0
    env_strict = os.environ.get("ADG_CERTIFIED_STRICT") == "1"
    args.strict = args.strict or env_strict

    snapshot = _latest_snapshot()
    started = datetime.now(timezone.utc)

    sub_results: list[dict[str, object]] = []
    blockers: list[str] = []

    # Defense-in-depth triplet completeness — runs only when a snapshot exists.
    if snapshot is not None:
        triplet = _check_triplet_completeness(snapshot)
        sub_results.append(triplet)
        if not triplet["ok"]:
            blockers.append(str(triplet["label"]))

    for label, script, contributes, accepts_strict_flag in SUB_GATES:
        result = _run_subgate(
            script, strict=args.strict, accepts_strict_flag=accepts_strict_flag
        )
        result["label"] = label
        result["script"] = script
        result["contributes_to_certification"] = contributes
        sub_results.append(result)
        if contributes and not result["ok"]:
            blockers.append(label)

    certified = len(blockers) == 0
    verdict = "ADG_CERTIFIED" if certified else "ADG_NOT_CERTIFIED"

    report = {
        "gate": "G-ADG-CERTIFIED",
        "tier": "B",
        "verdict": verdict,
        "strict_mode": args.strict,
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
        f"sub_gates_run={len(sub_results)} strict={args.strict}"
    )
    if blockers:
        print(f"[adg_certified] blockers: {', '.join(blockers)}")
        for r in sub_results:
            if r.get("contributes_to_certification") and not r["ok"]:
                print(f"  ✗ {r['label']}: {r.get('details') or r.get('stdout_tail', '')[:200]}")
    print(f"[adg_certified] verdict written to {VERDICT_PATH}")

    if not certified and args.strict:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
