from __future__ import annotations

__version__ = "11.10"
import asyncio
import json
import os
import sys
from typing import Any


def load_mission_input(filename: str = "mission_input.json") -> dict[str, Any]:
    """Loads the mission input JSON file."""
    # guardian: allow-path-string
    if not os.path.exists(filename):
        print(f"FATAL: {filename} not found. Please create it.")
        sys.exit(1)
    try:
        with open(filename) as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"FATAL: Error decoding {filename}: {e}")
        sys.exit(1)


def create_orchestrator() -> WorkflowOrchestrator:
    """Create orchestrator instance"""
    return WorkflowOrchestrator()


async def main():
    """Main execution"""
    print("\n" + "=" * 80)
    print(f"LIC v{__version__} - LinkedIn Outreach Orchestrator (Dual-Loop Agentic)")
    print("=" * 80)
    print("\nLoading mission from mission_input.json...")
    input_data = load_mission_input()
    sender_profile = input_data.get("sender_profile", {})
    recipient_profile = input_data.get("recipient_profile", {})
    job_description = input_data.get("job_description", {})
    if not all([sender_profile, recipient_profile, job_description]):
        print(
            "FATAL: mission_input.json is missing one or more required top-level keys: 'sender_profile', 'recipient_profile', 'job_description'",
        )
        sys.exit(1)
    mission = OutreachMission(
        mission_id=str(uuid4()),
        sender_profile=sender_profile,
        recipient_profile=recipient_profile,
        job_description=job_description,
        connection_status=recipient_profile.get("connection_status", "not_connected"),
        prior_message_count=recipient_profile.get("prior_message_count", 0),
    )
    print(f"\n{'=' * 80}")
    print("LIC v11.10 - Workflow Execution")
    print(f"{'=' * 80}\n")
    print(f"Mission ID: {mission.mission_id}")
    print(f"Sender: {mission.sender_profile.get('name', 'N/A')}")
    print(f"Recipient: {mission.recipient_profile.get('name', 'N/A')}")
    print(
        f"Job: {mission.job_description.get('title', 'N/A')} at {mission.job_description.get('company', 'N/A')}",
    )
    orchestrator = create_orchestrator()
    result = await orchestrator.execute_workflow(mission)
    print(f"\n{'=' * 80}")
    print("WORKFLOW RESULTS")
    print(f"{'=' * 80}\n")
    print(f"Status: {result['status']}")
    if result["status"] == "success":
        print(f"Production Ready: {result['production_ready']}")
        print(f"Workflow Time: {result['workflow_time']:.2f}s")
        print(f"\nGenerated Message ({result['word_count']} words):")
        print("-" * 80)
        print(result["message"])
        print("-" * 80)
        print("\nQA Summary:")
        print(f"  Critical: {result['qa_summary']['critical_issues']}")
        print(f"  High: {result['qa_summary']['high_issues']}")
        print(f"  Medium: {result['qa_summary']['errors']}")
        print(f"  Warnings: {result['qa_summary']['warnings']}")
        print(result["qa_report"])
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")
    return result


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
