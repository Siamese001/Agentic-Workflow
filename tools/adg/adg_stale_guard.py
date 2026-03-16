"""
ADG staleness guard — Accelerator #2.

Compares the ADG Redis ingest timestamp against the latest Python file commit
in git history. Raises RuntimeError if ADG is stale so that queries never run
against a stale graph.

Fail-closed: raises RuntimeError on Redis unavailability.
NO filesystem fallback. NO grep.

Usage (CLI):
    python tools/adg/adg_stale_guard.py           # exit 0=fresh, 1=stale
    python tools/adg/adg_stale_guard.py --warn    # warn but always exit 0
    python tools/adg/adg_stale_guard.py --json    # machine-readable JSON output
    python tools/adg/adg_stale_guard.py --files   # list files changed since last ingest
"""

from __future__ import annotations

import datetime
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "adg_stale_guard")
_emit_applies_guardrail("p0", "adg_stale_guard", "p0_governance")
_emit_reads_policy_state("p0", "adg_stale_guard", "policy_binding")
_emit_snapshots_state("p0", "adg_stale_guard", "state_snapshot")
emit_replay_key("p0", "adg_stale_guard")
emit_determinism_digest("p0", "adg_stale_guard")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.adg.adg_redis_query import ADGRedisClient


@dataclass
class StalenessResult:
    is_stale: bool
    ingest_time: float
    last_commit_time: float
    changed_files: list[str] = field(default_factory=list)
    message: str = ""

    @property
    def seconds_stale(self) -> float:
        return max(0.0, self.last_commit_time - self.ingest_time)


class ADGStalenessChecker:
    """Check whether the ADG Redis cache is stale relative to git commit history.

    Staleness = any Python file was committed after the last ADG ingest timestamp.
    """

    def __init__(
        self,
        client: ADGRedisClient | None = None,
        repo_root: Path | None = None,
    ) -> None:
        self._adg = client or ADGRedisClient()
        self._root = repo_root or ROOT

    def _get_ingest_time(self) -> float:
        """Get ADG ingest timestamp from Redis meta hash.

        Raises:
            RuntimeError: if Redis unavailable or 'ingested_at' field is missing.
        """
        meta = self._adg.meta()
        val = meta.get("ingested_at")
        if val is None:
            raise RuntimeError(
                "ADG meta key 'ingested_at' is missing — cache may be corrupt. "
                "Run: python tools/adg/adg_redis_ingest.py --force"
            )
        return float(val)

    def _get_last_python_commit_time(self) -> float:
        """Return Unix timestamp of the most recent commit touching any Python file.

        Returns 0.0 if no Python commits exist.

        Raises:
            RuntimeError: if git command fails or times out.
        """
        try:
            result = subprocess.run(
                ["git", "log", "-1", "--format=%ct", "--", "*.py"],
                cwd=str(self._root),
                capture_output=True,
                encoding="utf-8",
                errors="replace",
                timeout=30,
            )
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(f"git log timed out: {exc}") from exc
        if result.returncode != 0:
            raise RuntimeError(f"git log failed: {result.stderr.strip()}")
        out = result.stdout.strip()
        return float(out) if out else 0.0

    def _get_files_changed_since(self, since_timestamp: float) -> list[str]:
        """Return Python files committed strictly after since_timestamp.

        Raises:
            RuntimeError: if git command fails or times out.
        """
        dt = datetime.datetime.utcfromtimestamp(since_timestamp).strftime("%Y-%m-%d %H:%M:%S")
        try:
            result = subprocess.run(
                [
                    "git",
                    "log",
                    f"--after={dt}",
                    "--name-only",
                    "--format=",
                    "--",
                    "*.py",
                ],
                cwd=str(self._root),
                capture_output=True,
                encoding="utf-8",
                errors="replace",
                timeout=30,
            )
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(f"git log timed out: {exc}") from exc
        if result.returncode != 0:
            raise RuntimeError(f"git log failed: {result.stderr.strip()}")
        return sorted({f for f in result.stdout.splitlines() if f.strip() and f.endswith(".py")})

    def check(self) -> StalenessResult:
        """Check staleness. Raises RuntimeError if Redis is unavailable.

        Returns:
            StalenessResult with is_stale, timestamps, and changed_files.
        """
        ingest_time = self._get_ingest_time()
        last_commit_time = self._get_last_python_commit_time()

        if last_commit_time <= ingest_time:
            return StalenessResult(
                is_stale=False,
                ingest_time=ingest_time,
                last_commit_time=last_commit_time,
                message="ADG is fresh — no Python commits since last ingest.",
            )

        changed = self._get_files_changed_since(ingest_time)
        return StalenessResult(
            is_stale=True,
            ingest_time=ingest_time,
            last_commit_time=last_commit_time,
            changed_files=changed,
            message=(
                f"ADG is STALE — {len(changed)} Python file(s) committed after last ingest. "
                "Run: python tools/adg/adg_redis_ingest.py --force"
            ),
        )

    def assert_fresh(self) -> None:
        """Raise RuntimeError if ADG is stale.

        Intended as a pre-flight guard before any ADG query session.
        """
        result = self.check()
        if result.is_stale:
            raise RuntimeError(result.message)

    def warn_if_stale(self) -> None:
        """Print a warning to stderr if ADG is stale; never raises.

        Use in non-blocking contexts (e.g. pre-commit warn mode, ADGQuerySession
        with warn_only=True). Redis/staleness errors are demoted to warnings.
        """
        try:
            result = self.check()
        except Exception as exc:
            print(
                f"[adg-stale-guard] WARNING: could not check staleness: {exc}",
                file=sys.stderr,
            )
            return
        if result.is_stale:
            print(
                f"[adg-stale-guard] WARNING: {result.message}",
                file=sys.stderr,
            )


def _cli() -> None:
    import argparse
    import json as _json

    parser = argparse.ArgumentParser(
        prog="adg_stale_guard",
        description="Check whether the ADG Redis cache is stale relative to git history.",
    )
    parser.add_argument(
        "--warn",
        action="store_true",
        help="Print warning but exit 0 even if stale (non-blocking mode)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Machine-readable JSON output",
    )
    parser.add_argument(
        "--files",
        action="store_true",
        help="List Python files changed since last ADG ingest",
    )
    parser.add_argument(
        "--fail-if-stale",
        action="store_true",
        dest="fail_if_stale",
        help=(
            "CI-safe strict mode: exit 1 if Redis is UP and graph is STALE, "
            "exit 0 if Redis is DOWN (CI has no Redis). "
            "Stronger than --warn (which never blocks), weaker than strict (which "
            "blocks on Redis-unavailable too)."
        ),
    )
    args = parser.parse_args()

    import redis as _redis

    # --fail-if-stale treats Redis-unavailable the same as --warn (exit 0)
    _redis_down_is_ok = args.warn or args.fail_if_stale

    try:
        adg = ADGRedisClient()
        adg.ping()
    except _redis.ConnectionError as exc:
        if _redis_down_is_ok:
            print(
                f"[adg-stale-guard] WARNING: Redis unavailable — cannot check ADG staleness: {exc}",
                file=sys.stderr,
            )
            sys.exit(0)
        print(f"ERROR: Redis unavailable: {exc}", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as exc:
        if _redis_down_is_ok:
            print(f"[adg-stale-guard] WARNING: {exc}", file=sys.stderr)
            sys.exit(0)
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

    checker = ADGStalenessChecker(client=adg)
    try:
        result = checker.check()
    except RuntimeError as exc:
        if _redis_down_is_ok:
            print(f"[adg-stale-guard] WARNING: {exc}", file=sys.stderr)
            sys.exit(0)
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(
            _json.dumps(
                {
                    "is_stale": result.is_stale,
                    "ingest_time": result.ingest_time,
                    "last_commit_time": result.last_commit_time,
                    "seconds_stale": result.seconds_stale,
                    "changed_files": result.changed_files,
                    "message": result.message,
                },
                indent=2,
            )
        )
        sys.exit(1 if result.is_stale and not args.warn else 0)

    if result.is_stale:
        print(f"STALE: {result.message}")
        if args.files and result.changed_files:
            print(f"\n{len(result.changed_files)} file(s) changed since last ingest:")
            for f in result.changed_files:
                print(f"  {f}")
        print("\nRun: python tools/adg/adg_redis_ingest.py --force")
        # --warn: never block; --fail-if-stale: block on stale (Redis is up)
        sys.exit(0 if args.warn else 1)
    else:
        print(f"FRESH: {result.message}")
        sys.exit(0)


if __name__ == "__main__":
    _cli()
