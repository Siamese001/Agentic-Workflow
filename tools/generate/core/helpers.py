"""Core helper functions for ADG generation."""

from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

_OVERRIDES_FILE = Path(__file__).resolve().parents[1] / "adg_layer_overrides.yaml"


def _infer_layer(path: str) -> str:
    """Infer layer label from file path using YAML overrides."""
    import fnmatch

    import yaml

    overrides_file = _OVERRIDES_FILE
    if overrides_file.exists():
        try:
            with open(overrides_file, encoding="utf-8") as f:
                config = yaml.safe_load(f)
                overrides = config.get("overrides", {})
                default_layer = config.get("default_layer", "L_UNKNOWN")

                for pattern, layer in overrides.items():
                    if fnmatch.fnmatch(path, pattern):
                        return layer

                return default_layer
        except (ValueError, TypeError, RuntimeError) as e:
            print(f"[ADG] Warning: Failed to load layer overrides: {e}")

    for layer in ("L0", "L1", "L2", "L3", "L4", "L5", "L6"):
        if f"/{layer}_" in path or f"\\{layer}_" in path or f"/{layer}/" in path:
            return layer
    for prefix in (
        "apps_eval",
        "apps_exec",
        "apps_lic",
        "apps_research",
        "apps_rfp",
        "apps_rg",
        "apps_shared",
    ):
        if path.startswith(prefix) or f"/{prefix}" in path:
            return "L_APP"
    return "L_UNKNOWN"


def _generate_timestamp() -> str:
    """Generate timestamp in US Eastern time format MMDDYYYY_HHMM."""
    est = timezone(timedelta(hours=-4))  # EDT (UTC-4); DST active Mar-Nov in US Eastern
    now_est = datetime.now(est)
    return now_est.strftime("%m%d%Y_%H%M")  # e.g., 03132026_0512


def _verify_artifacts(adg_artifacts_dir: Path, ts: str, no_zip: bool, no_reports: bool) -> None:
    """Verify that requested artifacts were created."""
    if not no_zip:
        zip_path = adg_artifacts_dir / f"adg_run_{ts}.zip"
        if not zip_path.exists():
            print(f"[ERROR] Zip archive not found: {zip_path}")
            sys.exit(1)
        print(f"[ADG] Zip archive verification: {zip_path.name} exists")

    if not no_reports:
        report_files = [
            f"layer_coverage_report_{ts}.json",
            f"edge_density_report_{ts}.json",
            f"provenance_report_{ts}.json",
            f"replay_determinism_report_{ts}.json",
            f"boundary_report_{ts}.json",
            f"mutation_integrity_report_{ts}.json",
            f"test_surface_coverage_{ts}.json",
            f"closure_validation_report_{ts}.json",
        ]
        missing_reports = [rf for rf in report_files if not (adg_artifacts_dir / rf).exists()]
        if missing_reports:
            print(f"\n[ERROR] ADG generation incomplete: {len(missing_reports)} report(s) missing")
            print(f"[ERROR] Missing: {', '.join(missing_reports)}")
            print("[ERROR] This is a critical failure for full ADG generation")
            sys.exit(1)
        print(f"[ADG] Reports verification: {len(report_files)} reports exist")

    print("[ADG] Full ADG generation verification: all artifacts present")
