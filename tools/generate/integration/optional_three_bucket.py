"""Optional three-bucket enrichment — off the default ``generate_full_adg`` hot path.

ADR-079: static ADG + MVs are the product; runtime/registry reconciliation and
gap reports are **audit-only** and run when explicitly requested.

Enable (any truthy env or CLI ``--three-bucket``):

* ``ADG_THREE_BUCKET=1`` — runtime view + registry lift + gap/audit reports
* ``ADG_RUNTIME_VIEW=1`` — only ``build_runtime_view``
* ``ADG_REGISTRY_LIFT=1`` — only registry bucket lift
* ``ADG_THREE_BUCKET_REPORTS=1`` — only gap JSON/MD + authority audit
* ``ADG_THREE_BUCKET_SIGN=1`` — in-toto signing (implies full audit bundle)

Contract gates (``check_three_bucket_gap_thresholds``, ``check_adg_certified``)
remain in ``run_contract_gates.py``; use ``tools/adg/run_three_bucket_audit.py``
to refresh reports before those gates.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from tools.generate.core.helpers import _env_flag


@dataclass
class ThreeBucketRunResult:
    """Paths and counters from an optional three-bucket pass."""

    runtime_rows_written: int = 0
    registry_edges_inserted: int = 0
    report_paths: dict[str, Path] = field(default_factory=dict)
    signed: bool = False
    skipped_reason: str | None = None


def three_bucket_master_enabled() -> bool:
    return _env_flag("ADG_THREE_BUCKET", default=False)


def runtime_view_enabled() -> bool:
    return three_bucket_master_enabled() or _env_flag("ADG_RUNTIME_VIEW", default=False)


def registry_lift_enabled() -> bool:
    return three_bucket_master_enabled() or _env_flag("ADG_REGISTRY_LIFT", default=False)


def three_bucket_reports_enabled() -> bool:
    return three_bucket_master_enabled() or _env_flag("ADG_THREE_BUCKET_REPORTS", default=False)


def three_bucket_sign_enabled() -> bool:
    return _env_flag("ADG_THREE_BUCKET_SIGN", default=False)


def any_three_bucket_stage_enabled() -> bool:
    return (
        runtime_view_enabled()
        or registry_lift_enabled()
        or three_bucket_reports_enabled()
        or three_bucket_sign_enabled()
    )


def run_optional_three_bucket_enrichment(
    sqlite_path: Path,
    *,
    sqlite_error_type: type[BaseException] = sqlite3.Error,
) -> ThreeBucketRunResult:
    """Run enabled optional stages against an existing ADG snapshot."""
    result = ThreeBucketRunResult()
    if not any_three_bucket_stage_enabled():
        result.skipped_reason = "disabled (set ADG_THREE_BUCKET=1 or --three-bucket)"
        print(f"[ADG] three-bucket audit: SKIPPED — {result.skipped_reason}")
        return result

    print("[ADG] three-bucket audit: ENABLED (off hot path by default; ADR-079)")

    sqlite_path = Path(sqlite_path).resolve()
    if not sqlite_path.exists():
        result.skipped_reason = f"static snapshot missing: {sqlite_path}"
        print(f"[ADG] three-bucket audit: SKIPPED — {result.skipped_reason}")
        return result

    import sqlite3 as _sqlite3

    try:
        _probe = _sqlite3.connect(str(sqlite_path))
        try:
            for _tbl in ("nodes", "edges"):
                _row = _probe.execute(
                    "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
                    (_tbl,),
                ).fetchone()
                if not _row:
                    result.skipped_reason = f"canonical table missing: {_tbl}"
                    print(f"[ADG] three-bucket audit: SKIPPED — {result.skipped_reason}")
                    return result
        finally:
            _probe.close()
    except _sqlite3.Error as exc:
        result.skipped_reason = f"sqlite probe failed: {exc}"
        print(f"[ADG] three-bucket audit: SKIPPED — {result.skipped_reason}")
        return result

    if runtime_view_enabled():
        try:
            from tools.otel.runtime_view_builder import build_runtime_view  # noqa: PLC0415

            rv_stats = build_runtime_view(sqlite_path, fail_soft=True)
            result.runtime_rows_written = rv_stats.rows_written
            print(
                f"[ADG] runtime_view_builder: snapshots={rv_stats.snapshots_read} "
                f"rows_written={rv_stats.rows_written} error={rv_stats.error or 'none'}"
            )
        except Exception as exc:  # guardian: allow-broad-exception -- optional audit stage
            print(f"[WARN] runtime_view_builder failed (continuing): {exc}")

    if registry_lift_enabled():
        try:
            from tools.adg.registry_bucket_lift import lift as registry_lift  # noqa: PLC0415

            reg_stats = registry_lift(static_snapshot=sqlite_path, dry_run=False)
            result.registry_edges_inserted = reg_stats.edges_inserted
            print(
                f"[ADG] registry-bucket lift: resolved={reg_stats.edges_resolved} "
                f"inserted={reg_stats.edges_inserted}"
            )
        except (ImportError, OSError, sqlite_error_type, FileNotFoundError) as exc:
            print(f"[ADG] registry-bucket lift: SKIPPED ({type(exc).__name__}: {exc})")

    if three_bucket_reports_enabled():
        try:
            from tools.generate.integration.three_bucket_reports import emit_three_bucket_reports

            result.report_paths = emit_three_bucket_reports(sqlite_path)
        except Exception as exc:  # guardian: allow-broad-exception -- optional audit stage
            print(f"[WARN] three-bucket reports failed (continuing): {exc}")

    if three_bucket_sign_enabled():
        try:
            from tools.adg.sign_snapshot import sign_snapshot  # noqa: PLC0415

            sig_stats = sign_snapshot(snapshot=sqlite_path)
            result.signed = sig_stats.verified
            print(
                f"[ADG] in-toto sign: verified={sig_stats.verified} "
                f"envelope={sig_stats.envelope_path}"
            )
        except Exception as exc:  # guardian: allow-broad-exception -- optional audit stage
            print(f"[WARN] in-toto sign failed (continuing): {exc}")

    return result


def format_mode_banner() -> str:
    """Short banner fragment for startup logging."""
    if not any_three_bucket_stage_enabled():
        return "three_bucket=OFF"
    parts: list[str] = []
    if runtime_view_enabled():
        parts.append("runtime")
    if registry_lift_enabled():
        parts.append("registry")
    if three_bucket_reports_enabled():
        parts.append("reports")
    if three_bucket_sign_enabled():
        parts.append("sign")
    return f"three_bucket=AUDIT[{','.join(parts)}]"
