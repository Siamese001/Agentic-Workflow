"""
Guardian Heal Orchestrator — L3 orchestration for guardian→dispatcher→healer pipeline.

Replaces the legacy execute_ssot pipeline with a clean, deterministic
three-stage execution model:

    1. **Guardians** — Scan-only detection (no mutations)
    2. **Dispatcher** — Phase-ordered interpretation of guardian results
    3. **Healers** — Dry-run or apply remediation per check_id

Modes:
    --scan       Run guardians only, emit aggregate JSON (default)
    --dry-run    Run guardians + dispatcher + healers in dry-run mode
    --apply      Run guardians + dispatcher + healers in apply mode (sandbox-gated)

CLI:
    python -m agentic_core.L3_orchestration.scripts.guardian_heal_orchestrator --scan
    python -m agentic_core.L3_orchestration.scripts.guardian_heal_orchestrator --dry-run
    python -m agentic_core.L3_orchestration.scripts.guardian_heal_orchestrator --apply --repo-root /path/to/sandbox
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
from agentic_core.L0_routing.utils.project_root_util import get_validated_project_root
from agentic_core.L2_execution.tools import write_gateway as _wg
from agentic_core.L5_safety.config.structure_blueprint_config import REPORTS_DIR
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)

TOOL_ID = "guardian_heal_orchestrator"


def _run_guardians(
    repo_root: Path, timestamp: str, correlation_id: str | None = None, write_artifacts_dir: str | None = None
) -> dict:
    """Run all enabled guardians and return aggregate result as dict."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_run_guardians", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_run_guardians", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "_run_guardians")
    from agentic_core.L0_routing.scripts.run_all_guardians import run_all_guardians

    result = run_all_guardians(
        repo_root=repo_root,
        write_artifacts_dir=write_artifacts_dir,
        timestamp=timestamp,
        correlation_id=correlation_id,
    )
    return json.loads(result.to_json())


def _run_dispatcher(
    guardian_aggregate: dict,
    write_artifacts_dir: Path,
    created_utc: str,
    *,
    apply: bool = False,
    repo_root: Path | None = None,
    allow_repo_mutation: bool = False,
) -> dict:
    """Run the remediation dispatcher on guardian aggregate.

    Writes aggregate to a temp file for dispatcher consumption, then
    invokes the dispatcher and returns the CombinedHealResult as dict.
    """
    import tempfile

    from agentic_core.L2_execution.scripts.remediation_dispatcher import run_dispatcher

    assert_no_persistent_write("L0", "json.dump")
    tmp_dir = write_artifacts_dir or Path(tempfile.gettempdir())
    agg_path = tmp_dir / f"_guardian_agg_{created_utc}.json"
    _wg.write_json(agg_path, guardian_aggregate)
    try:
        result = run_dispatcher(
            guardian_result_path=agg_path,
            write_artifacts_dir=write_artifacts_dir,
            created_utc=created_utc,
            apply=apply,
            repo_root=repo_root,
            allow_repo_mutation=allow_repo_mutation,
        )
        return result.to_dict()
    finally:
        _wg.remove_file(agg_path)


def run_pipeline(
    mode: str = "scan",
    repo_root: Path | None = None,
    write_artifacts_dir: str | None = None,
    timestamp: str | None = None,
    correlation_id: str | None = None,
    allow_repo_mutation: bool = False,
) -> dict:
    """Execute the L0 pipeline in the specified mode.

    Args:
        mode: One of "scan", "dry-run", "apply".
        repo_root: Project root (defaults to SSOT get_validated_project_root).
        write_artifacts_dir: Repo-relative dir for artifacts.
        timestamp: Injectable ISO-8601 timestamp.
        correlation_id: Trace correlation ID.
        allow_repo_mutation: Allow apply mode on non-sandbox repos.

    Returns:
        Pipeline result dict with keys: mode, guardian_result, heal_result (if applicable).
    """
    if repo_root is None:
        repo_root = get_validated_project_root()
    if timestamp is None:
        timestamp = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    guardian_artifacts_dir = write_artifacts_dir
    if write_artifacts_dir is not None:
        try:
            Path(write_artifacts_dir).resolve().relative_to(repo_root.resolve())
        except ValueError:
            guardian_artifacts_dir = None
    guardian_aggregate = _run_guardians(
        repo_root=repo_root,
        timestamp=timestamp,
        correlation_id=correlation_id,
        write_artifacts_dir=guardian_artifacts_dir,
    )
    pipeline_result: dict = {
        "tool_id": TOOL_ID,
        "mode": mode,
        "timestamp": timestamp,
        "guardian_result": guardian_aggregate,
    }
    if mode == "scan":
        return pipeline_result
    heal_dir = (
        Path(write_artifacts_dir) if write_artifacts_dir else repo_root / "docs" / REPORTS_DIR / "plans"
    )
    heal_result = _run_dispatcher(
        guardian_aggregate=guardian_aggregate,
        write_artifacts_dir=heal_dir,
        created_utc=timestamp,
        apply=mode == "apply",
        repo_root=repo_root if mode == "apply" else None,
        allow_repo_mutation=allow_repo_mutation,
    )
    pipeline_result["heal_result"] = heal_result
    return pipeline_result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="L0 Thin Router — Guardian→Dispatcher→Healer pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Modes:\n  --scan       Run guardians only, emit aggregate JSON (default)\n  --dry-run    Run guardians + dispatcher + healers in dry-run mode\n  --apply      Run full pipeline with apply-mode healers (sandbox-gated)\n",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--scan", action="store_true", default=True, help="Scan-only mode (default)")
    group.add_argument("--dry-run", action="store_true", help="Dry-run mode")
    group.add_argument("--apply", action="store_true", help="Apply mode (sandbox-gated)")
    parser.add_argument("--repo-root", default=None, help="Project root path")
    parser.add_argument("--write-artifacts", default=None, help="Artifact output directory")
    parser.add_argument("--timestamp", default=None, help="Injectable ISO-8601 timestamp")
    parser.add_argument("--correlation-id", default=None, help="Trace correlation ID")
    parser.add_argument("--allow-repo-mutation", action="store_true", help="Allow apply on non-sandbox")
    parser.add_argument(
        "--format", choices=["json", "summary"], default="json", help="Output format (default: json)"
    )
    args = parser.parse_args()
    if args.apply:
        mode = "apply"
    elif args.dry_run:
        mode = "dry-run"
    else:
        mode = "scan"
    try:
        result = run_pipeline(
            mode=mode,
            repo_root=Path(args.repo_root) if args.repo_root else None,
            write_artifacts_dir=args.write_artifacts,
            timestamp=args.timestamp,
            correlation_id=args.correlation_id,
            allow_repo_mutation=args.allow_repo_mutation,
        )
    # guardian: allow-silent-swallow
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    guardian = result.get("guardian_result", {})
    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(f"L0 Pipeline | Mode: {result['mode']} | Status: {guardian.get('status', '?')}")
        print(f"Guardian Summary: {guardian.get('summary', 'N/A')}")
        for check in guardian.get("checks", []):
            print(f"  [{check.get('status', '?')}] {check.get('check_id', '?')}: {check.get('details', '')}")
        if "heal_result" in result:
            heal = result["heal_result"]
            print(f"\nHealer Summary: {len(heal.get('results', []))} check(s) processed")
            for hr in heal.get("results", []):
                print(f"  [{hr.get('status', '?')}] {hr.get('check_id', '?')}: {hr.get('notes', '')}")
    if guardian.get("status") == "ERROR":
        return 2
    if mode != "scan" and guardian.get("status") == "FAIL":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
