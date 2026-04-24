"""P3 Trend Runner — watch-only trend tracking and promotion-candidate detection.

Runs all P3-severity watch gates, accumulates trend history, and surfaces
promotion candidates when violations accumulate near critical paths.

P3 gates:
    - adg_fanin_triage_gate (fan-in growth)

Outputs:
    - Per-gate TrendResult with promotion_candidate flag
    - Consolidated trend summary artifact in artifacts/ci_gates/

Exit codes:
    0 — trend runner completed (P3 gates are watch-only, never block)
    2 — runner-level error (import failure, etc.)
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _bootstrap_repo_root() -> Path:
    repo_root = Path(__file__).resolve().parents[3]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    return repo_root


REPO_ROOT = _bootstrap_repo_root()
CI_ARTIFACTS_DIR = REPO_ROOT / "artifacts" / "ci_gates"
CI_RATCHET_DIR = REPO_ROOT / "artifacts" / "adg" / "ci_ratchets"

_IMPORTS_OK = False
_IMPORT_ERROR = ""

try:
    from ops_scripts.ci.adg_gates.gate_policy import TrendResult

    _IMPORTS_OK = True
except Exception as _exc:  # review: runner must record import-side-effect failures instead of crashing
    _IMPORT_ERROR = f"{type(_exc).__name__}: {_exc}"


def _load_trend(gate_key: str) -> TrendResult:
    """Load TrendResult from persisted JSON."""
    trend_file = CI_RATCHET_DIR / f"{gate_key}_trend.json"
    if not trend_file.exists():
        return TrendResult()
    try:
        data: dict[str, Any] = json.loads(trend_file.read_text(encoding="utf-8"))
        return TrendResult.from_dict(data)
    except (OSError, json.JSONDecodeError, ValueError):
        return TrendResult()


def _save_trend(gate_key: str, trend: TrendResult) -> None:
    """Save TrendResult to JSON atomically."""
    import os
    import tempfile

    CI_RATCHET_DIR.mkdir(parents=True, exist_ok=True)
    trend_file = CI_RATCHET_DIR / f"{gate_key}_trend.json"
    content = json.dumps(trend.to_dict(), indent=2) + "\n"
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=CI_RATCHET_DIR,
            prefix=f".{gate_key}_",
            suffix=".tmp",
            delete=False,
        ) as fh:
            fh.write(content)
            fh.flush()
            os.fsync(fh.fileno())
            tmp_path = Path(fh.name)
        if sys.platform == "win32" and trend_file.exists():
            trend_file.unlink()
        if tmp_path is None:
            raise OSError("Failed to create temporary trend file")
        tmp_path.replace(trend_file)
    except OSError:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except OSError:
                pass
        raise


def _run_fanin_trend(modified_files: list[str]) -> tuple[TrendResult, int, list[str], bool]:
    """Run fan-in triage gate and return (trend, gross, hotspot_modules, near_critical)."""
    try:
        from ops_scripts.ci.adg_fanin_triage_gate import run_fanin_gate  # type: ignore[import]

        result = run_fanin_gate(modified_files=modified_files)
        gross = result.get("violation_count", 0)
        hotspots: list[str] = result.get("hotspot_modules", [])
        near_critical: bool = result.get("near_critical_path", False)
        return _load_trend("fanin_triage"), gross, hotspots, near_critical
    except Exception as exc:
        print(
            f"[p3_trend_runner] WARNING: fanin triage unavailable: {type(exc).__name__}: {exc}",
            file=sys.stderr,
        )
        return _load_trend("fanin_triage"), 0, [], False


def run_p3_trend(
    modified_files: list[str] | None = None,
    emit_artifacts: bool = True,
) -> int:
    """Run all P3 trend gates.

    Args:
        modified_files: Changed files for context (informational for P3).
        emit_artifacts: Write trend artifacts to artifacts/ci_gates/.

    Returns:
        0 always (P3 gates are watch-only).
        2 on import-level error.
    """
    if not _IMPORTS_OK:
        print(f"[p3_trend_runner] ERROR: imports failed — {_IMPORT_ERROR}", file=sys.stderr)
        return 2

    ts = datetime.now(timezone.utc).isoformat()
    promotion_candidates: list[dict[str, Any]] = []

    # --- Fan-in gate ---
    trend, gross, hotspots, near_critical_gate = _run_fanin_trend(modified_files or [])
    trend.update(current_gross=gross, current_hotspots=hotspots)
    near_critical = near_critical_gate or any("agent" in m or "routing" in m for m in hotspots)
    trend.evaluate_promotion(near_critical_path=near_critical)
    _save_trend("fanin_triage", trend)

    if trend.promotion_candidate:
        promotion_candidates.append(
            {
                "gate": "fanin_triage",
                "reason": trend.promotion_reason,
                "consecutive_increases": trend.consecutive_increases,
                "hotspot_modules": trend.hotspot_modules,
            }
        )
        print(
            f"[p3_trend_runner] PROMOTION CANDIDATE: fanin_triage — {trend.promotion_reason}",
            file=sys.stderr,
        )
    else:
        print(
            f"[p3_trend_runner] fanin_triage: gross={gross}, "
            f"consecutive_increases={trend.consecutive_increases} — watch only",
        )

    if emit_artifacts:
        CI_ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
        summary: dict[str, Any] = {
            "timestamp": ts,
            "promotion_candidates": promotion_candidates,
            "gates": {
                "fanin_triage": trend.to_dict(),
            },
        }
        fname_ts = ts.replace(":", "").replace(".", "_")
        out = CI_ARTIFACTS_DIR / f"p3_trend_summary_{fname_ts}.json"
        tmp_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                "w",
                encoding="utf-8",
                dir=CI_ARTIFACTS_DIR,
                prefix=".p3_trend_summary_",
                suffix=".tmp",
                delete=False,
            ) as fh:
                fh.write(json.dumps(summary, indent=2) + "\n")
                fh.flush()
                os.fsync(fh.fileno())
                tmp_path = Path(fh.name)
            if sys.platform == "win32" and out.exists():
                out.unlink()
            if tmp_path is None:
                raise OSError("Failed to create temporary trend summary file")
            tmp_path.replace(out)
            print(f"[p3_trend_runner] Trend artifact: {out}")
        except OSError as exc:
            if tmp_path is not None:
                try:
                    tmp_path.unlink()
                except OSError:
                    pass
            print(f"[p3_trend_runner] WARNING: could not persist trend artifact: {exc}", file=sys.stderr)

    return 0


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="P3 trend runner (watch-only)")
    parser.add_argument("--modified-files", nargs="*", default=[], help="Changed files")
    parser.add_argument("--no-artifacts", action="store_true", help="Suppress artifact writes")
    args = parser.parse_args()

    return run_p3_trend(
        modified_files=args.modified_files,
        emit_artifacts=not args.no_artifacts,
    )


if __name__ == "__main__":
    sys.exit(main())
