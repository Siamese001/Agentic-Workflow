# FILE: 10_10/main_v10_10.py
"""
Main Runtime Entrypoint for Agentic Workflow v10_10
===================================================

This script wires together:

    L1 — Planning
    L2 — Execution + Cognition
    L3 — DAG + Self-Correction
    L4 — State Adapter
    L5 — Safety Gateway

It loads job/resume inputs, builds plans, runs the DAG, and prints
the final state patch or saves it to a file.

This file:
    • Contains NO LLM logic (only L2 does).
    • Contains NO orchestration logic (L3).
    • Contains NO state mutation (L4).
    • Contains NO safety decisions (L5).

It is a pure runtime coordinator + CLI wrapper.

Usage:
    python 10_10/main_v10_10.py \
        --job job_input.json \
        --resume master_resume.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from models import (
    JobInput,
    ResumeInput,
    WorkflowConfig,
    ExecutionContext,
)
from routing import RoutingPolicy
from registry import build_default_prompt_registry
from runtime_utils import PredictiveCacheManager, SandboxConfig
from l1 import build_workflow_plan_bundle
from l3 import run_dag
from observability import start_span, end_span, record_event


# =============================================================================
# Helper: load JSON input
# =============================================================================

def _load_json(path: str | Path) -> dict:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


# =============================================================================
# Main Workflow Runner
# =============================================================================

def run_workflow(
    job_path: str,
    resume_path: str,
    config: WorkflowConfig | None = None,
    dump_patch_to: str | None = None,
) -> dict:
    """
    High-level function:
        1. Load inputs
        2. Build L1 plans
        3. Execute DAG (L3)
        4. Return L4 patch
    """

    span = start_span("main_v10_10.run_workflow", ctx={"job_path": job_path})

    try:
        job_data = _load_json(job_path)
        resume_data = _load_json(resume_path)

        job = JobInput.model_validate(job_data)
        resume = ResumeInput.model_validate(resume_data)
        config = config or WorkflowConfig()

        # Build dependency components
        routing_policy = RoutingPolicy()
        prompt_registry = build_default_prompt_registry()
        sandbox = SandboxConfig()

        # Optional predictive cache
        cache_manager = PredictiveCacheManager(max_entries=1024)

        # Execution context
        ctx = ExecutionContext(
            job=job,
            resume=resume,
            config=config,
            routing_policy=routing_policy,
            sandbox_config=sandbox,
            prompt_registry=prompt_registry,
            cache_manager=cache_manager,
            meta_profile_snapshot=None,  # future: persistent meta-learning
        )

        # L1 — Build Plans
        plans = build_workflow_plan_bundle(
            job=job,
            resume=resume,
            config=config,
            meta_profile=None,
            routing_policy=routing_policy,
            prompt_registry=prompt_registry,
        )

        # L3 — Run the DAG with correction loop
        dag_result = run_dag(ctx, plans, max_retries=2)

        patch = dag_result.final_state_patch

        if dump_patch_to:
            outfile = Path(dump_patch_to)
            outfile.parent.mkdir(parents=True, exist_ok=True)
            outfile.write_text(json.dumps(patch, indent=2), encoding="utf-8")
            record_event("main.patch_written", {"path": str(outfile)})

        return patch

    finally:
        end_span(span)


# =============================================================================
# CLI Entrypoint
# =============================================================================

def _cli():
    parser = argparse.ArgumentParser(description="Run Agentic Workflow v10_10")
    parser.add_argument("--job", required=True, help="Path to job_input.json")
    parser.add_argument("--resume", required=True, help="Path to resume_input.json")
    parser.add_argument("--dump", required=False, help="Where to write final state patch (JSON)")

    args = parser.parse_args()

    patch = run_workflow(
        job_path=args.job,
        resume_path=args.resume,
        config=WorkflowConfig(),
        dump_patch_to=args.dump,
    )

    print(json.dumps(patch, indent=2))


if __name__ == "__main__":
    try:
        _cli()
    except Exception as e:
        print(f"Workflow failed: {e}", file=sys.stderr)
        sys.exit(1)
