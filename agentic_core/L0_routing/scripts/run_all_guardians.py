"""
Aggregation Runner — Discovers and runs all Guardian scripts deterministically.

Produces a combined_guardian_result.json with:
- Global status (FAIL if any FAIL, ERROR if any ERROR)
- Per-guardian results in deterministic sorted order
- Artifact index referencing all per-guardian outputs

CLI:
    python -m agentic_core.L0_routing.scripts.run_all_guardians \\
        --write-artifacts docs/reports/verification/guardian \\
        --strict
"""

from __future__ import annotations

import argparse
import importlib
import sys
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.types.guardian_contract import (
    AGGREGATE_GUARDIAN_ID,
    CONTRACT_VERSION,
    ArtifactClass,
    ArtifactType,
    CheckStatus,
    GuardianResult,
    GuardianStatus,
    maybe_sign_result,
    normalize_repo_path,
    write_guardian_result,
)
from agentic_core.L0_routing.types.guardian_registry import (
    GuardianSpec,
    get_guardian_specs,
)
from agentic_core.L5_safety.config.structure_blueprint import (
    get_validated_project_root,
)


def _run_single_guardian(
    spec: GuardianSpec,
    repo_root: Path,
    artifact_dir: str | None,
    timestamp: str | None,
    correlation_id: str | None,
) -> GuardianResult:
    """Import and execute a single guardian, returning its result."""
    mod = importlib.import_module(spec.entrypoint_module)
    func = getattr(mod, spec.entrypoint_fn)
    result: GuardianResult = func(
        repo_root=repo_root,
        write_artifacts_dir=artifact_dir,
        timestamp=timestamp,
    )
    if correlation_id is not None:
        result.correlation_id = correlation_id
    return result


def run_all_guardians(
    repo_root: Path | None = None,
    write_artifacts_dir: str | None = None,
    timestamp: str | None = None,
    correlation_id: str | None = None,
    include_disabled: bool = False,
) -> GuardianResult:
    """
    Execute all registered guardians in deterministic order and aggregate.

    Args:
        include_disabled: If True, run ALL guardians (including disabled_by_default).
                          Default False = enabled-only.

    Returns a combined GuardianResult with:
    - guardian_id = "combined"
    - Global status promotion (ERROR > FAIL > PASS)
    - Per-guardian check entries
    - Combined metrics
    - Artifact references
    """
    if repo_root is None:
        repo_root = get_validated_project_root()

    combined = GuardianResult(
        guardian_id=AGGREGATE_GUARDIAN_ID,
        version=CONTRACT_VERSION,
        timestamp=timestamp,
        correlation_id=correlation_id,
        artifact_class=ArtifactClass.AGGREGATE,
    )

    per_guardian_results: list[dict[str, Any]] = []
    guardian_index: dict[str, dict[str, Any]] = {}  # Phase 4: artifact index
    total_checks = 0
    total_failed = 0
    total_error = 0

    # Get guardians from SSOT registry (already sorted by guardian_id)
    guardian_specs = get_guardian_specs(enabled_only=not include_disabled)

    for spec in guardian_specs:
        gid = spec.guardian_id
        try:
            result = _run_single_guardian(
                spec,
                repo_root,
                write_artifacts_dir,
                timestamp,
                correlation_id,
            )
            # Add a roll-up check for this guardian
            combined.add_check(
                check_id=f"guardian_{gid}",
                status=(CheckStatus.FAIL if result.status != GuardianStatus.PASS.value else CheckStatus.PASS),
                details=result.summary,
                evidence={
                    "guardian_id": gid,
                    "status": result.status,
                    "check_count": len(result.checks),
                    "checks": [c.to_dict() for c in result.checks],
                },
            )

            # Promote global status
            if result.status == GuardianStatus.ERROR.value:
                combined.status = GuardianStatus.ERROR.value
                total_error += 1
            elif result.status == GuardianStatus.FAIL.value:
                if combined.status != GuardianStatus.ERROR.value:
                    combined.status = GuardianStatus.FAIL.value
                total_failed += 1

            total_checks += len(result.checks)

            # Collect remediation hints
            combined.remediation_hints.extend(result.remediation_hints)

            # Collect artifact references
            for artifact in result.artifacts:
                combined.artifacts.append(artifact)

            per_guardian_results.append(
                {
                    "guardian_id": gid,
                    "status": result.status,
                    "checks": len(result.checks),
                },
            )

            # Phase 4: build artifact index for L6 ingestion
            guardian_index[gid] = {
                "status": result.status,
                "artifacts": [normalize_repo_path(a.path) for a in result.artifacts],
            }

        # guardian: allow-silent-swallow
        except Exception as exc:
            combined.add_check(
                check_id=f"guardian_{gid}",
                status=CheckStatus.FAIL,
                details=f"Guardian {gid} crashed: {exc}",
            )
            combined.status = GuardianStatus.ERROR.value
            total_error += 1
            per_guardian_results.append(
                {
                    "guardian_id": gid,
                    "status": "ERROR",
                    "error": str(exc),
                },
            )
            guardian_index[gid] = {
                "status": "ERROR",
                "artifacts": [],
            }

    # Finalize
    guardian_count = len(guardian_specs)
    passed_count = guardian_count - total_failed - total_error
    combined.metrics = {
        "guardian_count": guardian_count,
        "guardians_passed": passed_count,
        "guardians_failed": total_failed,
        "guardians_error": total_error,
        "total_checks": total_checks,
        "per_guardian": per_guardian_results,
    }
    combined.index = guardian_index

    if combined.status == GuardianStatus.PASS.value:
        combined.summary = f"All {guardian_count} guardians passed ({total_checks} checks)"
    elif combined.status == GuardianStatus.ERROR.value:
        combined.summary = f"{total_error} guardian(s) errored, {total_failed} failed out of {guardian_count}"
    else:
        combined.summary = (
            f"{total_failed} guardian(s) failed out of {guardian_count} ({total_checks} checks)"
        )

    # --- V15 signing (before serialization) ---
    maybe_sign_result(combined, commit_hash="HEAD")

    # Write combined artifact
    if write_artifacts_dir:
        artifact_dir_path = repo_root / write_artifacts_dir
        out = write_guardian_result(combined, artifact_dir_path, "combined_guardian_result.json")
        combined.add_artifact(
            ArtifactType.JSON,
            normalize_repo_path(out.relative_to(repo_root)),
            "Combined guardian aggregation result",
        )

    return combined


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description="Run All Guardians (Aggregated)")
    parser.add_argument(
        "--write-artifacts",
        default=None,
        help="Repo-relative directory to write result JSON",
    )
    parser.add_argument(
        "--format",
        choices=["json", "text"],
        default="json",
    )
    parser.add_argument(
        "--json",
        dest="format",
        action="store_const",
        const="json",
        help="Shorthand for --format json",
    )
    parser.add_argument("--strict", action="store_true")
    parser.add_argument(
        "--include-disabled",
        action="store_true",
        default=False,
        help="Include disabled-by-default guardians in aggregation",
    )
    parser.add_argument("--timestamp", default=None)
    parser.add_argument("--correlation-id", default=None)
    args = parser.parse_args()

    result = run_all_guardians(
        write_artifacts_dir=args.write_artifacts,
        timestamp=args.timestamp,
        correlation_id=args.correlation_id,
        include_disabled=args.include_disabled,
    )

    if args.format == "json":
        print(result.to_json())
    else:
        print(f"Guardian Aggregator | Status: {result.status}")
        print(f"Summary: {result.summary}")
        for check in result.checks:
            status_icon = "PASS" if check.status == CheckStatus.PASS.value else "FAIL"
            print(f"  [{status_icon}] {check.check_id}: {check.details}")

    if args.strict and result.status != GuardianStatus.PASS.value:
        return 1
    return 0


# =============================================================================
# §Wave7.0.7 — L0 Render-Only Integration Seam (no apply, no mutation)
# =============================================================================


def render_meta_learning_change_package(
    package: Any,
    *,
    as_json: bool = True,
) -> str:
    """Render a MetaLearningChangePackageArtifact as a deterministic string.

    This is a **pure function**: it does NOT call apply_meta_learning_proposal(),
    does NOT mutate any config, and does NOT write any files.

    Parameters
    ----------
    package : MetaLearningChangePackageArtifact
        The change package to render.
    as_json : bool
        If True, return canonical JSON string of package.to_dict().
        If False, return a stable, minimal single-line summary.

    Returns
    -------
    str
        Deterministic string representation.
    """
    import json as _json

    if as_json:
        return _json.dumps(package.to_dict(), sort_keys=True, separators=(",", ":"))

    return (
        f"CHANGE_PACKAGE target={package.target_component}"
        f" decision_trace={package.decision_trace_id[:12]}"
        f" trace={package.trace_id[:12]}"
        f" spec_keys={sorted(package.change_spec.keys())}"
    )


if __name__ == "__main__":
    sys.exit(main())
