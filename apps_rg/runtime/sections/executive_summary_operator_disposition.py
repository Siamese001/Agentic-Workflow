"""Operator-facing success tiers for executive_summary (draft vs certified).

Deterministic X2 product quality is separate from unanimous X1D certification.
This module drives CLI process exit for ``--section executive_summary`` only.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

PRODUCT_QUALITY_PASS = "PASS"
RUNTIME_REAL_LLM = "REAL_LLM"
X3_ALLOW = "X3_ALLOW"

_BLOCKED_RUNTIME = frozenset(
    {
        "BLOCKED",
        "OFFLINE_CONTRACT_STUB",
    }
)


@dataclass(frozen=True)
class ExecutiveSummaryOperatorDisposition:
    draft_ready: bool
    certified: bool
    disposition_tier: str
    process_exit_code: int
    expected_nonzero_exit: bool
    runtime_generation_status: str
    product_quality_status: str
    x3_code: str


def _load_runtime_generation_status(
    artifact_dir: Path | None,
    manifest_loaded: dict[str, Any],
) -> str:
    if isinstance(manifest_loaded.get("runtime_generation_status"), str):
        rgs = manifest_loaded["runtime_generation_status"].strip()
        if rgs:
            return rgs
    if artifact_dir is not None and (artifact_dir / "l2_output.json").is_file():
        import json

        try:
            l2 = json.loads((artifact_dir / "l2_output.json").read_text(encoding="utf-8"))
            if isinstance(l2, dict):
                rgs_l2 = str(l2.get("runtime_generation_status") or "").strip()
                if rgs_l2:
                    return rgs_l2
        except (OSError, json.JSONDecodeError, TypeError):  # guardian: allow-silent-swallow -- optional l2_output read; fall back to unknown status
            pass
    return "unknown"


def compute_executive_summary_operator_disposition(
    *,
    artifact_dir: Path | None,
    x3_loaded: dict[str, Any],
    manifest_loaded: dict[str, Any] | None = None,
    cli_path_pass: bool = True,
    fault: str = "",
) -> ExecutiveSummaryOperatorDisposition:
    """Derive operator tiers from persisted lane artifacts (no new gates)."""
    manifest_loaded = manifest_loaded or {}
    rgs = _load_runtime_generation_status(artifact_dir, manifest_loaded)
    pq = str(x3_loaded.get("product_quality_status") or PRODUCT_QUALITY_PASS).strip() or "UNKNOWN"
    x3_code = str(x3_loaded.get("x3_code") or "").strip()
    x3_pass = bool(x3_loaded.get("pass"))

    generation_ok = rgs == RUNTIME_REAL_LLM and not fault and rgs not in _BLOCKED_RUNTIME
    draft_ready = bool(
        cli_path_pass
        and generation_ok
        and pq == PRODUCT_QUALITY_PASS
    )
    certified = bool(x3_code == X3_ALLOW and x3_pass)

    if not cli_path_pass or not generation_ok:
        tier = "failed"
    elif certified:
        tier = "certified"
    elif draft_ready:
        tier = "draft"
    else:
        tier = "failed"

    if fault == "temperature_range":
        exit_code = 2
    elif draft_ready:
        exit_code = 0
    else:
        from apps_rg.runtime.cli_exit_codes import exit_code_for_executive_summary_artifact

        exit_code = exit_code_for_executive_summary_artifact(
            artifact_dir if artifact_dir is not None else Path("."),
            fault=fault,
            x3_code=x3_code,
        )
        if exit_code == 0 and not certified:
            exit_code = 1

    return ExecutiveSummaryOperatorDisposition(
        draft_ready=draft_ready,
        certified=certified,
        disposition_tier=tier,
        process_exit_code=exit_code,
        expected_nonzero_exit=exit_code != 0,
        runtime_generation_status=rgs,
        product_quality_status=pq,
        x3_code=x3_code,
    )


def resolve_from_artifact_dir(
    artifact_dir: Path,
    *,
    cli_path_pass: bool = True,
    fault: str = "",
) -> ExecutiveSummaryOperatorDisposition:
    import json

    manifest_loaded: dict[str, Any] = {}
    x3_loaded: dict[str, Any] = {}
    if artifact_dir.is_dir():
        for name, target in (("run_manifest.json", manifest_loaded), ("x3_disposition.json", x3_loaded)):
            path = artifact_dir / name
            if path.is_file():
                try:
                    raw = json.loads(path.read_text(encoding="utf-8"))
                    if isinstance(raw, dict):
                        if name.startswith("run_manifest"):
                            manifest_loaded = raw
                        else:
                            x3_loaded = raw
                except (OSError, json.JSONDecodeError, TypeError):  # guardian: allow-silent-swallow -- optional manifest/x3 read; empty dict defaults
                    pass
    return compute_executive_summary_operator_disposition(
        artifact_dir=artifact_dir,
        x3_loaded=x3_loaded,
        manifest_loaded=manifest_loaded,
        cli_path_pass=cli_path_pass,
        fault=fault,
    )


__all__ = [
    "ExecutiveSummaryOperatorDisposition",
    "compute_executive_summary_operator_disposition",
    "resolve_from_artifact_dir",
]
