"""Gate-invocation + generation manifest recorders for the ADG pipeline.

Two companion manifests are emitted per ``generate_full_adg.py`` run:

1. **Gate invocation manifest** — which gates ran, with status, duration,
   exit code, blocking mode. Proves no gate was silently skipped.
2. **Generation manifest** — the snapshot handoff contract: exact
   snapshot path, commit SHA, p0 status, runtime proof status, pointer
   to the gate invocation manifest. Consumed by
   ``tools/adg/run_full_adg_audit.py``.

Both are written on every run (including crash paths via ``atexit``) so
partial runs are still auditable.

Design notes:
- ``GateManifestRecorder`` is the single instance held by ``main()``.
- All I/O is best-effort: a manifest failure never blocks the pipeline.
  The wrapper is the fail-closed consumer, not this module.
- Timestamps are ISO-8601 UTC with ``Z`` suffix (matches other ADG
  artifacts under ``artifacts/adg/``).
"""

from __future__ import annotations

import atexit
import hashlib
import json
import os
import sys
import tempfile
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from time import monotonic
from typing import Any, Literal, TypeVar

GateStatus = Literal[
    "invoked",  # started — no terminal status yet
    "pass",  # exit code 0 / validation ok
    "fail",  # non-zero exit / validation error
    "deferred_fail",  # failure deferred via --continue-on-p0 or deferred_failures
    "timed_out",  # subprocess.TimeoutExpired
    "missing_script",  # script file not found (hard_fail in certification)
    "skipped",  # intentionally disabled (e.g., --no-<gate>-check flag)
]

CertificationStatus = Literal["clean", "failed", "diagnostic_only"]


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    """Atomically replace one JSON document without leaving partial output."""
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=path.name + ".",
            suffix=".tmp",
            delete=False,
        ) as handle:
            json.dump(payload, handle, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
            temp_path = Path(handle.name)
        temp_path.replace(path)
    except (OSError, TypeError, ValueError):
        if temp_path is not None:
            try:
                temp_path.unlink(missing_ok=True)
            except OSError:
                pass
        raise


def sqlite_snapshot_sidecars(sqlite_path: Path) -> tuple[Path, ...]:
    """Return SQLite sidecars that sit outside the main-file digest authority."""
    path = Path(sqlite_path)
    candidates = (
        Path(str(path) + "-wal"),
        Path(str(path) + "-shm"),
        Path(str(path) + "-journal"),
    )
    return tuple(candidate for candidate in candidates if candidate.exists())


def seal_sqlite_snapshot(sqlite_path: Path) -> None:
    """Checkpoint a producer-owned SQLite file and reject unsealed sidecars."""
    import sqlite3

    path = Path(sqlite_path).resolve()
    if not path.is_file():
        raise ValueError(f"SQLite snapshot is missing: {path}")
    try:
        con = sqlite3.connect(str(path), timeout=30)
    except sqlite3.Error as exc:
        raise ValueError(f"SQLite snapshot could not be opened for sealing: {path}: {exc}") from exc
    try:
        quick_check = con.execute("PRAGMA quick_check").fetchone()
        if not quick_check or str(quick_check[0]).lower() != "ok":
            raise ValueError(f"SQLite snapshot quick_check failed: {path}: {quick_check!r}")
        checkpoint = con.execute("PRAGMA wal_checkpoint(TRUNCATE)").fetchone()
        if checkpoint and int(checkpoint[0]) != 0:
            raise ValueError(f"SQLite WAL checkpoint remained busy: {path}: {checkpoint!r}")
        mode_row = con.execute("PRAGMA journal_mode=DELETE").fetchone()
        mode = str(mode_row[0]).lower() if mode_row else ""
        if mode != "delete":
            raise ValueError(f"SQLite snapshot did not leave WAL mode: {path}: {mode!r}")
        con.commit()
    except sqlite3.Error as exc:
        raise ValueError(f"SQLite snapshot sealing failed: {path}: {exc}") from exc
    finally:
        con.close()

    sidecars = sqlite_snapshot_sidecars(path)
    if sidecars:
        raise ValueError(
            "SQLite snapshot has unsealed sidecars: " + ", ".join(str(sidecar) for sidecar in sidecars)
        )


@dataclass
class GateRecord:
    """One gate invocation row in the manifest."""

    name: str
    phase: str
    kind: str
    blocking_mode: str
    status: GateStatus
    exit_code: int | None = None
    duration_s: float | None = None
    started_at_utc: str | None = None
    finished_at_utc: str | None = None
    script_rel: str | None = None
    message: str | None = None


@dataclass
class GateManifest:
    timestamp: str
    generator_entrypoint: str
    sqlite_path: str | None
    generation_exit_code: int | None
    certification_status: CertificationStatus
    gates: list[dict[str, Any]] = field(default_factory=list)
    unexpected_skips: list[dict[str, Any]] = field(default_factory=list)
    failed_gates: list[dict[str, Any]] = field(default_factory=list)
    deferred_failures: list[dict[str, Any]] = field(default_factory=list)


class GateManifestRecorder:
    """Records gate invocations for a single generator run.

    Usage (inside ``generate_full_adg.py::main``)::

        recorder = GateManifestRecorder(out_dir, ts)
        recorder.record("mcp_config_drift", "preflight", "python_function",
                        "hard_fail", status="pass", duration_s=0.01)
        # ... post-ADG gates call record_subprocess_gate(...) ...
        recorder.finalize(sqlite_path=..., generation_exit_code=...)
    """

    def __init__(
        self, out_dir: Path, ts: str, generator_entrypoint: str = "tools/generate/generate_full_adg.py"
    ) -> None:
        self._out_dir = Path(out_dir)
        self._ts = ts
        self._entrypoint = generator_entrypoint
        self._records: list[GateRecord] = []
        self._in_flight: dict[str, float] = {}
        self._generation_exit_code: int | None = None
        self._sqlite_path: Path | None = None
        self._finalized = False
        self._atexit_registered = False
        self._register_atexit()

    # ------------------------------------------------------------------
    # Lifecycle helpers
    # ------------------------------------------------------------------
    def _register_atexit(self) -> None:
        if self._atexit_registered:
            return
        atexit.register(self._atexit_flush)
        self._atexit_registered = True

    def _atexit_flush(self) -> None:
        if self._finalized:
            return
        # Emergency flush — we crashed before main() called finalize().
        # Mark any still-in-flight gates as failed.
        for name, started in list(self._in_flight.items()):
            self._records.append(
                GateRecord(
                    name=name,
                    phase="unknown",
                    kind="unknown",
                    blocking_mode="unknown",
                    status="fail",
                    duration_s=monotonic() - started,
                    message="in-flight at process exit — partial record",
                )
            )
        try:
            self._write_manifests(
                certification_status="failed",
                generation_exit_code=self._generation_exit_code,
                sqlite_path=self._sqlite_path,
                best_effort=True,
            )
        except (OSError, TypeError, ValueError):
            # Absolute last-ditch — never raise from atexit.
            pass

    # ------------------------------------------------------------------
    # Recording API
    # ------------------------------------------------------------------
    def record(
        self,
        name: str,
        phase: str,
        kind: str,
        blocking_mode: str,
        *,
        status: GateStatus,
        exit_code: int | None = None,
        duration_s: float | None = None,
        script_rel: str | None = None,
        message: str | None = None,
    ) -> None:
        now = _utcnow_iso()
        rec = GateRecord(
            name=name,
            phase=phase,
            kind=kind,
            blocking_mode=blocking_mode,
            status=status,
            exit_code=exit_code,
            duration_s=duration_s,
            started_at_utc=now,
            finished_at_utc=now,
            script_rel=script_rel,
            message=message,
        )
        self._records.append(rec)

    def start(self, name: str) -> None:
        """Mark a gate as starting; pair with :meth:`finish`."""
        self._in_flight[name] = monotonic()

    def finish(
        self,
        name: str,
        phase: str,
        kind: str,
        blocking_mode: str,
        *,
        status: GateStatus,
        exit_code: int | None = None,
        script_rel: str | None = None,
        message: str | None = None,
    ) -> None:
        started = self._in_flight.pop(name, None)
        duration = (monotonic() - started) if started is not None else None
        self.record(
            name,
            phase,
            kind,
            blocking_mode,
            status=status,
            exit_code=exit_code,
            duration_s=duration,
            script_rel=script_rel,
            message=message,
        )

    def record_validation_gate(
        self,
        name: str,
        *,
        status: GateStatus = "pass",
        message: str | None = None,
        duration_s: float | None = None,
    ) -> None:
        """Convenience for validation/gates.py call sites."""
        self.record(
            name,
            phase="post-commit-validation" if name not in ("p2_ratchet",) else "build",
            kind="validation",
            blocking_mode="hard_fail",
            status=status,
            duration_s=duration_s,
            message=message,
        )

    # ------------------------------------------------------------------
    # Finalization
    # ------------------------------------------------------------------
    def finalize(
        self,
        *,
        sqlite_path: Path | None,
        generation_exit_code: int,
        runtime_proof_status: str = "view_absent",
        runtime_attested_edge_count: int = 0,
        registry_bucket_edge_count: int = 0,
        commit_sha: str | None = None,
        repo_state_hash: str | None = None,
        p0_status: str = "unknown",
    ) -> Path:
        """Write both manifests and return the generation manifest path."""
        self._generation_exit_code = generation_exit_code
        self._sqlite_path = Path(sqlite_path) if sqlite_path else None

        # Classify certification_status.
        had_failure = any(r.status in ("fail", "timed_out", "missing_script") for r in self._records)
        had_deferred = any(r.status == "deferred_fail" for r in self._records)
        runtime_proof_unreadable = runtime_proof_status == "snapshot_unreadable"
        snapshot_authority_incomplete = (
            self._sqlite_path is None
            or bool(sqlite_snapshot_sidecars(self._sqlite_path))
            or not commit_sha
            or not repo_state_hash
        )
        if (
            generation_exit_code != 0
            or had_failure
            or runtime_proof_unreadable
            or snapshot_authority_incomplete
        ):
            status: CertificationStatus = "failed"
        elif had_deferred:
            status = "failed"  # deferred fail still breaks certification
        else:
            status = "clean"

        gate_manifest_path = self._write_manifests(
            certification_status=status,
            generation_exit_code=generation_exit_code,
            sqlite_path=self._sqlite_path,
            runtime_proof_status=runtime_proof_status,
            runtime_attested_edge_count=runtime_attested_edge_count,
            registry_bucket_edge_count=registry_bucket_edge_count,
            commit_sha=commit_sha,
            repo_state_hash=repo_state_hash,
            p0_status=p0_status,
            best_effort=False,
        )
        self._finalized = True
        return gate_manifest_path

    # ------------------------------------------------------------------
    # Writer
    # ------------------------------------------------------------------
    def _write_manifests(
        self,
        *,
        certification_status: CertificationStatus,
        generation_exit_code: int | None,
        sqlite_path: Path | None,
        runtime_proof_status: str = "view_absent",
        runtime_attested_edge_count: int = 0,
        registry_bucket_edge_count: int = 0,
        commit_sha: str | None = None,
        repo_state_hash: str | None = None,
        p0_status: str = "unknown",
        best_effort: bool,
    ) -> Path:
        self._out_dir.mkdir(parents=True, exist_ok=True)

        failed = [asdict(r) for r in self._records if r.status in ("fail", "timed_out", "missing_script")]
        deferred = [asdict(r) for r in self._records if r.status == "deferred_fail"]
        skips = [asdict(r) for r in self._records if r.status == "missing_script"]

        manifest = GateManifest(
            timestamp=_utcnow_iso(),
            generator_entrypoint=self._entrypoint,
            sqlite_path=str(sqlite_path) if sqlite_path else None,
            generation_exit_code=generation_exit_code,
            certification_status=certification_status,
            gates=[asdict(r) for r in self._records],
            unexpected_skips=skips,
            failed_gates=failed,
            deferred_failures=deferred,
        )

        gate_manifest_path = self._out_dir / f"adg_gate_invocation_manifest_{self._ts}.json"
        try:
            _atomic_write_json(gate_manifest_path, asdict(manifest))
        except OSError as e:
            if not best_effort:
                raise
            print(f"[gate_manifest] WARN failed to write gate manifest: {e}", file=sys.stderr)

        # Generation manifest — snapshot handoff contract
        snapshot_sha256: str | None = None
        if sqlite_path is not None and not sqlite_snapshot_sidecars(sqlite_path):
            try:
                digest = hashlib.sha256()
                with sqlite_path.open("rb") as handle:
                    for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                        digest.update(chunk)
                snapshot_sha256 = digest.hexdigest()
            except OSError:
                # Preserve the manifest with an explicit unverifiable digest.
                # The audit wrapper rejects it for certification.
                snapshot_sha256 = None

        gen_manifest = {
            "timestamp": _utcnow_iso(),
            "sqlite_path": str(sqlite_path) if sqlite_path else None,
            "snapshot_path": str(sqlite_path) if sqlite_path else None,
            "snapshot_sha256": snapshot_sha256,
            "commit_sha": commit_sha,
            "repo_state_hash": repo_state_hash,
            "generation_exit_code": generation_exit_code,
            "p0_status": p0_status,
            "gate_manifest_path": str(gate_manifest_path),
            "runtime_proof_status": runtime_proof_status,
            "runtime_attested_edge_count": runtime_attested_edge_count,
            "registry_bucket_edge_count": registry_bucket_edge_count,
            "created_at_utc": _utcnow_iso(),
            "certification_status": certification_status,
        }
        gen_manifest_path = self._out_dir / f"adg_generation_manifest_{self._ts}.json"
        try:
            _atomic_write_json(gen_manifest_path, gen_manifest)
            # Latest-pointer for local dev (CI MUST NOT rely on this — wrapper
            # resolves the timestamped file by mtime + timestamp validation).
            latest = self._out_dir / "adg_generation_manifest_latest.json"
            _atomic_write_json(latest, gen_manifest)
        except OSError as e:
            if not best_effort:
                raise
            print(f"[gate_manifest] WARN failed to write gen manifest: {e}", file=sys.stderr)

        return gate_manifest_path

    # ------------------------------------------------------------------
    # Inspection
    # ------------------------------------------------------------------
    @property
    def records(self) -> list[GateRecord]:
        return list(self._records)


# ---------------------------------------------------------------------------
# Module-level singleton (threaded to validation/gates.py call sites that
# cannot receive an explicit recorder parameter without broad refactors).
# ---------------------------------------------------------------------------
_CURRENT_RECORDER: GateManifestRecorder | None = None


def set_current_recorder(recorder: GateManifestRecorder | None) -> None:
    global _CURRENT_RECORDER
    _CURRENT_RECORDER = recorder


def current_recorder() -> GateManifestRecorder | None:
    return _CURRENT_RECORDER


_T = TypeVar("_T")


def _deferred_gate_names() -> frozenset[str]:
    from tools.generate.integration.deferred_failures import deferred_failure_summary

    return frozenset(str(row["gate_name"]) for row in deferred_failure_summary())


def run_recorded_validation(
    name: str,
    fn: Callable[..., _T],
    /,
    *args: object,
    **kwargs: object,
) -> _T:
    """Invoke a validation gate and record pass/fail/deferred_fail in the manifest.

    ``name`` must match ``tools.generate._required_gates.REQUIRED_GATES`` so
    ``run_full_adg_audit`` cross-check passes in certification mode.
    """
    rec = current_recorder()
    if rec is None:
        return fn(*args, **kwargs)

    from tools.generate.integration.deferred_failures import _resolve_defer_flag

    deferred_before = _deferred_gate_names()
    started = monotonic()
    try:
        result = fn(*args, **kwargs)
    except SystemExit:
        rec.record_validation_gate(
            name,
            status="fail",
            duration_s=monotonic() - started,
        )
        raise

    new_deferred = _deferred_gate_names() - deferred_before
    if new_deferred and _resolve_defer_flag(None):
        rec.record_validation_gate(
            name,
            status="deferred_fail",
            duration_s=monotonic() - started,
            message=", ".join(sorted(new_deferred)[:5]),
        )
    else:
        rec.record_validation_gate(
            name,
            status="pass",
            duration_s=monotonic() - started,
        )
    return result


def record_validation_gate_global(
    name: str,
    *,
    status: GateStatus = "pass",
    message: str | None = None,
) -> None:
    """Call from validation/gates.py — no-ops if no recorder is set."""
    rec = current_recorder()
    if rec is not None:
        rec.record_validation_gate(name, status=status, message=message)


def runtime_proof_from_sqlite(sqlite_path: Path) -> tuple[str, int]:
    """Classify runtime-proof status for a snapshot.

    Returns ``(status, attested_edge_count)`` with status ∈
    ``{attested, view_present_zero_attested, view_absent, snapshot_unreadable}``.

    The exact snapshot is opened through SQLite's read-only immutable URI and
    ``query_only`` guard. A missing, locked, corrupt, or otherwise unreadable
    snapshot is distinct from a valid snapshot that simply lacks the view.
    """
    import sqlite3

    if sqlite_snapshot_sidecars(sqlite_path):
        return "snapshot_unreadable", 0
    try:
        snapshot_uri = Path(sqlite_path).resolve().as_uri() + "?mode=ro&immutable=1"
        con = sqlite3.connect(snapshot_uri, uri=True)
    except (OSError, ValueError, sqlite3.Error):
        return "snapshot_unreadable", 0
    try:
        try:
            con.execute("PRAGMA query_only = ON")
            row = con.execute(
                "SELECT name FROM sqlite_master WHERE type IN ('table','view') AND name='v_runtime_proof'"
            ).fetchone()
        except sqlite3.Error:
            return "snapshot_unreadable", 0
        if row is None:
            return "view_absent", 0
        try:
            attested = con.execute(
                "SELECT COUNT(*) FROM v_runtime_proof WHERE attesting_trace_count >= 1"
            ).fetchone()[0]
        except sqlite3.Error:
            return "snapshot_unreadable", 0
        if attested and attested > 0:
            return "attested", int(attested)
        return "view_present_zero_attested", 0
    finally:
        try:
            con.close()
        except sqlite3.Error:
            pass
