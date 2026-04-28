"""Core helper functions for ADG generation."""

from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from tqdm import tqdm


def _env_flag(name: str, *, default: bool = False) -> bool:
    """Parse a boolean environment flag with a single consistent contract.

    Truthy values:   "1", "true", "yes" (case-insensitive, whitespace-trimmed)
    Falsy values:    anything else (including unset, empty, "0", "false", "no")

    W2.2 (plan adg-pipeline-simplification-e2e-9b4c27): centralises three
    previously-inline parsers (`ADG_ENABLE_DETERMINISM_PROBE`,
    `ADG_SKIP_REDIS`, `ADG_SKIP_GIT`) into one testable helper.
    """
    raw = os.environ.get(name, "").strip().lower()
    if not raw:
        return default
    if raw in ("1", "true", "yes"):
        return True
    if raw in ("0", "false", "no"):
        return False
    return default


def _discover_repo_root(start: Path) -> Path:
    """Best-effort repository root discovery for direct script and package execution."""
    for candidate in (start, *start.parents):
        if (candidate / "agentic_core").exists() or (candidate / ".git").exists():
            return candidate
        if candidate.name == "tools" and (candidate / "generate").exists():
            return candidate.parent
    return start.parents[3] if len(start.parents) > 3 else start.parent


ROOT = _discover_repo_root(Path(__file__).resolve().parent)

_OVERRIDES_FILE = Path(__file__).resolve().parents[1] / "adg_layer_overrides.yaml"


def _infer_layer(path: str) -> str:
    """Infer layer label from file path using YAML overrides."""
    import fnmatch

    import yaml

    overrides_file = _OVERRIDES_FILE
    if overrides_file.exists():
        try:
            with open(overrides_file, encoding="utf-8") as f:
                config = yaml.safe_load(f) or {}
                if not isinstance(config, dict):
                    raise ValueError("adg_layer_overrides.yaml must contain a mapping at the document root")
                overrides = config.get("overrides", {})
                default_layer = config.get("default_layer", "L_UNKNOWN")
                if not isinstance(overrides, dict):
                    raise ValueError("'overrides' must be a mapping of glob -> layer")

                for pattern, layer in overrides.items():
                    if fnmatch.fnmatch(path, pattern):
                        return layer

                return default_layer
        except (ValueError, TypeError, RuntimeError) as e:
            print(f"[ADG] Warning: Failed to load layer overrides: {e}")

    for layer in ("L0", "L1", "L2", "L3", "L4", "L5", "L6"):
        if f"/{layer}_" in path or f"\\{layer}_" in path or f"/{layer}/" in path:
            return layer
    for prefix in tqdm(
        (
            "apps_eval",
            "apps_exec",
            "apps_lic",
            "apps_research",
            "apps_rfp",
            "apps_rg",
            "apps_shared",
        ),
        desc="Processing",
        unit="item",
    ):
        if path.startswith(prefix) or f"/{prefix}" in path:
            return "L_APP"
    return "L_UNKNOWN"


def _generate_timestamp() -> str:
    """Generate timestamp in US Eastern time format MMDDYYYY_HHMM."""
    try:
        eastern = ZoneInfo("America/New_York")
    except ZoneInfoNotFoundError:
        eastern = timezone(timedelta(hours=-4))
    now_est = datetime.now(eastern)
    return now_est.strftime("%m%d%Y_%H%M")  # e.g., 03132026_0512


def _artifact_locations(adg_artifacts_dir: Path, ts: str, name: str) -> list[Path]:
    """Return all plausible locations an artifact may exist post-pipeline.

    Plan NEXT_STEP `adg-pipeline-artifact-packaging`: ``_verify_artifacts``
    runs AFTER ``_archive_old_artifacts``, which (with ``keep_runs=1``)
    can move the freshly-created run files into
    ``_archive/<YYYY-MM>/`` and gzip the zip into ``<name>.gz``. The
    verifier therefore must check the root, the timestamped archive
    month-dir, AND the gzipped variants.
    """
    candidates: list[Path] = [adg_artifacts_dir / name]
    # Compressed variant for zip artifacts (archiver gzips zip files).
    candidates.append(adg_artifacts_dir / f"{name}.gz")
    # Archive month directory derived from the run's timestamp (MMDDYYYY_HHMM).
    try:
        dt = datetime.strptime(ts, "%m%d%Y_%H%M")
        archive_month = adg_artifacts_dir / "_archive" / dt.strftime("%Y-%m")
        candidates.append(archive_month / name)
        candidates.append(archive_month / f"{name}.gz")
    except ValueError:  # guardian: allow-broad-exception -- ts format degraded; root-level check still applies
        pass
    return candidates


def _artifact_present(adg_artifacts_dir: Path, ts: str, name: str) -> Path | None:
    """Return the first existing path for ``name`` across all candidate locations."""
    for candidate in _artifact_locations(adg_artifacts_dir, ts, name):
        if candidate.exists():
            return candidate
    return None


def _verify_artifacts(adg_artifacts_dir: Path, ts: str, no_zip: bool, no_reports: bool) -> None:
    """Verify that requested artifacts were created.

    Plan adg-fail-aggregating-gate-chain-9d4e1f W2.3: artifact-verification
    failures route through ``record_or_exit`` so the run can still drain
    its deferred-failure registry and emit the aggregated summary table
    before exiting non-zero. Default behaviour (env var unset) is
    unchanged: missing artifact = immediate ``sys.exit(1)``.

    Plan NEXT_STEP `adg-pipeline-artifact-packaging`: also accept artifacts
    that have been moved into the archive month-dir or gzipped by the
    archive step (which runs BEFORE this verifier in the pipeline).
    """
    from tools.generate.integration.deferred_failures import record_or_exit  # noqa: PLC0415

    if not no_zip:
        zip_name = f"adg_run_{ts}.zip"
        found_zip = _artifact_present(adg_artifacts_dir, ts, zip_name)
        if found_zip is None:
            print(
                f"[ERROR] Zip archive not found: {zip_name} "
                f"(checked root + _archive month dir + .gz variants)"
            )
            record_or_exit(
                "verify_artifacts.zip",
                1,
                message=f"missing {zip_name}",
            )
        else:
            try:
                rel = found_zip.relative_to(adg_artifacts_dir)
            except ValueError:
                rel = found_zip
            print(f"[ADG] Zip archive verification: {rel.as_posix()} exists")

    if not no_reports:
        report_files = [
            f"layer_coverage_report_{ts}.json",
            f"edge_density_report_{ts}.json",
            f"provenance_report_{ts}.json",
            f"closure_validation_report_{ts}.json",
        ]
        missing_reports = [
            rf for rf in report_files if _artifact_present(adg_artifacts_dir, ts, rf) is None
        ]
        if missing_reports:
            print(f"\n[ERROR] ADG generation incomplete: {len(missing_reports)} report(s) missing")
            print(f"[ERROR] Missing: {', '.join(missing_reports)}")
            print(
                "[ERROR] Checked: artifacts/adg/, artifacts/adg/_archive/<YYYY-MM>/, and .gz variants. "
                "This is a critical failure for full ADG generation."
            )
            record_or_exit(
                "verify_artifacts.reports",
                1,
                message=f"{len(missing_reports)} missing: {', '.join(missing_reports)}"[:160],
            )
        else:
            print(f"[ADG] Reports verification: {len(report_files)} reports exist")

    print("[ADG] Full ADG generation verification: all artifacts present")
