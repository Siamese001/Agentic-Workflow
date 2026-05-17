# =============================================================================
# QUARANTINED — LEGACY CODE — DO NOT USE
# =============================================================================
# This file is QUARANTINED as of W4 (2026-05-05) per apps_lic spine acceptance.
#
# REASON:
#   This legacy workflow runner is replaced by the governed R3R4 managed workflow
#   (apps_lic_static and apps_lic_managed recipes via lic_l2_recipe_registry).
#
# UNREACHABLE FROM:
#   - apps_lic/__main__.py (governed spine entrypoint)
#   - L0 routing (R4_STATIC_RECIPE, R3R4_MANAGED_WORKFLOW route families)
#   - R4 recipe resolution (static DAG)
#   - R3R4 recipe resolution (managed DAG)
#   - Active step adapters (STEP_ADAPTERS registry)
#
# ACTIVE PATH:
#   apps_lic/integrations/lic_l2_recipe_registry.py → resolve_recipe()
#   apps_lic/integrations/lic_l2_step_adapters.py → STEP_ADAPTERS
#   apps_lic/config/apps_lic_static_dag.yaml (R4)
#   apps_lic/config/apps_lic_managed_dag.yaml (R3R4)
#
# PRESERVATION:
#   File retained per W4 hard rules (no deletion without explicit approval).
#   Not imported by any active code path. Safe to ignore for spine operation.
#
# STATUS: QUARANTINED — W4 apps_lic spine acceptance complete
# =============================================================================

from __future__ import annotations

__version__ = "12.1"

import asyncio
import json
import os
import sys
from importlib import import_module
from pathlib import Path
from typing import TYPE_CHECKING, Any
from uuid import uuid4
from tqdm import tqdm

if TYPE_CHECKING:
    from apps_lic.types.lic_models_types import OutreachMission

DEFAULT_INPUT_FILE = "mission_input_LIC.json"


def _resolve_input_path(filename: str = DEFAULT_INPUT_FILE) -> Path:
    candidate = Path(filename).expanduser()
    if candidate.is_absolute():
        return candidate
    cwd_candidate = Path.cwd() / candidate
    if cwd_candidate.exists():
        return cwd_candidate
    return Path(__file__).resolve().parent / candidate


def load_mission_input(filename: str = DEFAULT_INPUT_FILE) -> dict[str, Any]:
    """
    Loads the mission input JSON file.

    Args:
        filename: Path to mission input JSON file

    Returns:
        Dictionary containing mission parameters

    Raises:
        SystemExit: If file not found or invalid JSON
    """
    input_path = _resolve_input_path(filename)
    if not input_path.exists():
        print(f"FATAL: {input_path.name} not found. Please create it.")
        # guardian: allow-path-string
        print(f"\nExpected location: {input_path}")
        print("\nThe file should contain:")
        print("- sender_profile: Your profile information")
        print("- recipient_profile: Target recipient information")
        print("- job_description: Job details for context")
        sys.exit(1)
    try:
        with input_path.open(encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"FATAL: Error decoding {input_path.name}: {e}")
        print(f"Line {e.lineno}, column {e.colno}: {e.msg}")
        sys.exit(1)
    except OSError as e:
        print(f"FATAL: Could not read {input_path}: {e}")
        sys.exit(1)


def validate_mission_input(input_data: dict[str, Any]) -> bool:
    """
    Validate that mission input contains all required fields.

    Args:
        input_data: Loaded mission input dictionary

    Returns:
        True if valid, False otherwise
    """
    required_keys = ["sender_profile", "recipient_profile", "job_description"]
    missing_keys = [key for key in required_keys if key not in input_data]
    if missing_keys:
        print(f"FATAL: mission_input_LIC.json is missing required keys: {', '.join(missing_keys)}")
        return False
    sender_required = ["name", "title", "company"]
    sender_missing = [key for key in sender_required if key not in input_data["sender_profile"]]
    if sender_missing:
        print(f"FATAL: sender_profile missing required fields: {', '.join(sender_missing)}")
        return False
    recipient_required = ["name", "title", "company"]
    recipient_missing = [key for key in recipient_required if key not in input_data["recipient_profile"]]
    if recipient_missing:
        print(f"FATAL: recipient_profile missing required fields: {', '.join(recipient_missing)}")
        return False
    job_required = ["title", "company"]
    job_missing = [key for key in job_required if key not in input_data["job_description"]]
    if job_missing:
        print(f"FATAL: job_description missing required fields: {', '.join(job_missing)}")
        return False
    return True


def create_orchestrator():
    """
    Create orchestrator instance.

    This import is done lazily to avoid loading all dependencies
    until we've validated the mission input.

    Returns:
        WorkflowOrchestrator instance
    """
    candidates = [
        ("apps_lic.reasoning.enterprise_campaign_orchestrator", "EnterpriseLicOrchestrator"),
    ]
    errors: list[str] = []
    for module_name, class_name in tqdm(candidates, desc="Processing", unit="item"):
        try:
            module = import_module(module_name)
            cls = getattr(module, class_name)
            instance = cls()
            if not hasattr(instance, "execute_workflow"):
                errors.append(f"{module_name}.{class_name} does not expose execute_workflow()")
                continue
            return instance
        except (ImportError, AttributeError, TypeError) as exc:
            errors.append(f"{module_name}.{class_name}: {type(exc).__name__}: {exc}")

    print("FATAL: No compatible workflow orchestrator is available.")
    print("Checked:")
    for error in errors:
        print(f"- {error}")
    sys.exit(1)


def _build_mission(input_data: dict[str, Any]):
    from apps_lic.types.lic_models_types import OutreachMission

    sender_profile = input_data.get("sender_profile", {})
    recipient_profile = input_data.get("recipient_profile", {})
    job_description = input_data.get("job_description", {})

    return OutreachMission(
        mission_id=str(uuid4()),
        sender_profile=sender_profile,
        recipient_profile=recipient_profile,
        job_description=job_description,
        connection_status=recipient_profile.get("connection_status", "not_connected"),
        prior_message_count=int(recipient_profile.get("prior_message_count", 0) or 0),
    )


def print_header():
    """Print workflow execution header"""
    print("\n" + "=" * 80)
    print(f"LIC v{__version__} - LinkedIn Outreach Orchestrator")
    print("Strategic Alignment Engine with Live API Integration")
    print("=" * 80)


def print_mission_summary(mission: OutreachMission):
    """Print mission details"""
    print(f"\n{'=' * 80}")
    print("MISSION DETAILS")
    print(f"{'=' * 80}\n")
    print(f"Mission ID:   {mission.mission_id}")
    print(
        f"Sender:       {mission.sender_profile.get('name', 'N/A')} - {mission.sender_profile.get('title', 'N/A')}",
    )
    print(f"Company:      {mission.sender_profile.get('company', 'N/A')}")
    print(
        f"\nRecipient:    {mission.recipient_profile.get('name', 'N/A')} - {mission.recipient_profile.get('title', 'N/A')}",
    )
    print(f"Company:      {mission.recipient_profile.get('company', 'N/A')}")
    print(f"Status:       {mission.connection_status}")
    print(f"\nTarget Role:  {mission.job_description.get('title', 'N/A')}")
    print(f"Company:      {mission.job_description.get('company', 'N/A')}")
    print(f"Location:     {mission.job_description.get('location', 'N/A')}")


def print_results(result: dict[str, Any]):
    """Print workflow execution results"""
    print(f"\n{'=' * 80}")
    print("WORKFLOW RESULTS")
    print(f"{'=' * 80}\n")
    print(f"Status: {result['status'].upper()}")
    if result["status"] == "success":
        print(f"Production Ready: {('✓ YES' if result['production_ready'] else '✗ NO')}")
        print(f"Workflow Time: {result['workflow_time']:.2f}s")
        print(f"Route: {result.get('route', 'N/A')}")
        print(f"Archetype: {result.get('archetype', 'N/A')}")
        print("\nQA Summary:")
        qa = result["qa_summary"]
        print(f"  Critical Issues: {qa['critical_issues']}")
        print(f"  High Issues:     {qa['high_issues']}")
        print(f"  Medium Issues:   {qa['errors']}")
        print(f"  Warnings:        {qa['warnings']}")
        if result["production_ready"]:
            print(f"\n{'=' * 80}")
            print(f"GENERATED MESSAGE ({result['word_count']} words)")
            print(f"{'=' * 80}\n")
            print(result["message"])
            print(f"\n{'=' * 80}")
        else:
            print("\n⚠️  Message generated but failed QA validation")
            print("Review QA report for details:")
            print(result.get("qa_report", "No QA report available"))
    else:
        print(f"\n❌ ERROR: {result.get('error', 'Unknown error')}")
        if "error_details" in result:
            print(f"\nDetails: {result['error_details']}")


async def main():
    """
    Main execution function.

    Workflow:
    1. Load and validate mission input
    2. Create orchestrator
    3. Execute workflow
    4. Display results

    Returns:
        Workflow result dictionary
    """
    print_header()
    print("\n📁 Loading mission from mission_input_LIC.json...")
    input_data = load_mission_input()
    if not validate_mission_input(input_data):
        sys.exit(1)
    print("✓ Mission input validated")
    mission = _build_mission(input_data)
    print_mission_summary(mission)
    print("\n🤖 Initializing workflow orchestrator...")
    try:
        orchestrator = create_orchestrator()
        print("✓ Orchestrator initialized")
    except (ImportError, AttributeError, TypeError, RuntimeError) as e:
        print(f"❌ Failed to initialize orchestrator: {type(e).__name__}: {e}")
        sys.exit(1)
    print(f"\n{'=' * 80}")
    print("EXECUTING WORKFLOW")
    print(f"{'=' * 80}\n")
    print("⏳ Running agentic workflow (this may take 1-3 minutes)...\n")
    try:
        workflow_result = await orchestrator.execute_workflow(mission)
    except KeyboardInterrupt:
        print("\n\n⚠️  Workflow interrupted by user")
        sys.exit(130)
    except Exception as e:  # guardian: allow-broad-catch -- outer boundary for third-party orchestrator errors; re-raised via traceback + nonzero exit
        print(f"\n\n❌ Workflow failed with exception: {type(e).__name__}: {e}")
        import traceback

        print("\nStack trace:")
        traceback.print_exc()
        sys.exit(1)
    print_results(workflow_result)
    output_file = f"output_{mission.mission_id[:8]}.json"
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(workflow_result, f, indent=2, default=str)
        print(f"\n💾 Full results saved to: {output_file}")
    except OSError as e:
        print(f"\n⚠️  Could not save results to file: {e}")
    return workflow_result


if __name__ == "__main__":
    # Entry point for command-line execution.
    # Usage: python -m apps_lic  (or: python apps_lic/tools/run_workflow_lic.py)
    # Environment variables: GOOGLE_API_KEY (canonical for Gemini/Google AI); GEMINI_API_KEY is deprecated alias.
    # Optional: GOOGLE_CSE_ID for search.
    missing_env_vars: list[str] = []
    if not (
        os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    ):
        missing_env_vars = ["GOOGLE_API_KEY"]
    # Required files: mission_input_LIC.json; optional: master_resume.json, sender_knowledge_base.json, manual_rag_input.json.
    if missing_env_vars:
        print(f"\n⚠️  WARNING: Missing environment variables: {', '.join(missing_env_vars)}")
        print("\nSome features may not work without these variables.")
        print("Set them with: export VARIABLE_NAME='value'")
        print("\nContinuing anyway...")
    try:
        cli_result = asyncio.run(main())
        if cli_result.get("status") == "success" and cli_result.get("production_ready"):
            sys.exit(0)
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as e:  # guardian: allow-broad-catch -- __main__ last-resort boundary; prints type+message and exits nonzero
        print(f"\n❌ Fatal error: {type(e).__name__}: {e}")
        sys.exit(1)
