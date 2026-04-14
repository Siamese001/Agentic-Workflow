#!/usr/bin/env python3
# RELOCATED: Moved from apps_shared/reasoning/ to ops_scripts/general/ (P1-B, 2026-03-11).
"""
restore_void_agents.py - Restore functional agents from void_violations

Restores key functional agents that were incorrectly archived as "void violations"
but are actually needed for the system to function properly.

Categories to restore:
1. DAG/Workflow agents -> L3_orchestration/engine/
2. Key orchestration agents -> L3_orchestration/engine/
3. observability agents (unique ones) -> L6_observability/

NOT restored (have active replacements):
- CanonValidatorAgent -> LegacyCanonValidatorAgent
- HierarchyEnforcerAgent -> HierarchyAgent
- MetricsAgent -> MetricsWitnessAgent
- TelemetryAgent -> RuntimeTelemetryAgent

Usage:
    python scripts/restore_void_agents.py --dry-run
    python scripts/restore_void_agents.py
"""

import argparse
import shutil
import sys
from pathlib import Path

from agentic_core.L0_routing.config import (
    AGENTIC_CORE_DIR,
    ARCHIVES_DIR,
)
from tqdm import tqdm


def _resolve_project_root() -> Path:
    for candidate in Path(__file__).resolve().parents:
        if (candidate / ".git").exists():
            return candidate
    return Path(__file__).resolve().parents[2]


PROJECT_ROOT = _resolve_project_root()
VOID_DIR = PROJECT_ROOT / ARCHIVES_DIR / "void_violations"
AGENTIC_CORE = PROJECT_ROOT / AGENTIC_CORE_DIR

# Agents to restore with their target locations
RESTORE_MAP: dict[str, str] = {
    # DAG/Workflow agents -> L3
    "DagEngineAgent.py": "L3_orchestration/engine/",
    "DagExecutorAgent.py": "L3_orchestration/engine/",
    "DagManagerAgent.py": "L3_orchestration/engine/",
    "DAGMutatorAgent.py": "L3_orchestration/engine/",
    "DagRuntimeInspectorAgent.py": "L3_orchestration/engine/",
    "WorkflowOrchestratorAgent.py": "L3_orchestration/engine/",
    "HardenedWorkflowOrchestratorAgent.py": "L3_orchestration/engine/",
    # Orchestration agents -> L3
    "NervousSystemAgent.py": "L3_orchestration/engine/",
    "OrchestrationHandshakeAgent.py": "L3_orchestration/engine/",
    "SelfRecoveringOrchestratorAgent.py": "L3_orchestration/engine/",
    # observability agents -> L6
    "TracingAgent.py": "L6_observability/agents/",
    "AutonomicMonitorAgent.py": "L6_observability/agents/",
    # Safety/validation agents -> L5
    "GenerativeGuardAgent.py": "L5_safety/guardrails/",
    # Architecture/governance -> L5
    "ArchitectureGovernorAgent.py": "L5_safety/validators/",
    "AgentRegistryValidatorAgent.py": "L5_safety/validators/",
    # Bootstrap/core -> L0
    "BootstrapAgent.py": "L0_routing/scripts/",
}

# Agents that have active replacements - DO NOT RESTORE
SKIP_AGENTS = {
    "CanonValidatorAgent.py",  # -> LegacyCanonValidatorAgent
    "HierarchyEnforcerAgent.py",  # -> HierarchyAgent
    "MetricsAgent.py",  # -> MetricsWitnessAgent
    "TelemetryAgent.py",  # -> RuntimeTelemetryAgent
    "PatternEnforcerAgent.py",  # -> CodeStandardsEnforcerAgent
    "HygieneValidatorAgent.py",  # -> HygieneValidatorAgent
    "StateValidatorAgent.py",  # Deprecated
    "StateValidatorDeprecatedAgent.py",
    "GenerativeGuardDeprecatedAgent.py",
    "SystemArchitectDeprecatedAgent.py",
}


def restore_agent(filename: str, target_dir: str, dry_run: bool = False) -> tuple[bool, str]:
    """
    Restore a single agent from void_violations.

    Returns:
        (success, message)
    """
    source = VOID_DIR / filename
    target_path = AGENTIC_CORE / target_dir / filename

    if not source.exists():
        return False, f"Source not found: {source}"

    if target_path.exists():
        return False, f"Already exists: {target_path.relative_to(PROJECT_ROOT)}"

    if dry_run:
        return True, f"Would restore to {target_path.relative_to(PROJECT_ROOT)}"

    try:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(target_path))
        return True, f"Restored to {target_path.relative_to(PROJECT_ROOT)}"
    # guardian: allow-silent-swallow
    except Exception as e:
        return False, f"Error: {e}"


def main():
    parser = argparse.ArgumentParser(description="Restore functional agents from void_violations")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    args = parser.parse_args()

    print("=" * 70)
    print("Void Violations Agent Restoration Script")
    print("=" * 70)

    if args.dry_run:
        print("\n[DRY RUN MODE - No files will be moved]\n")

    restored = 0
    skipped = 0
    errors = 0

    print(f"Restoring {len(RESTORE_MAP)} agents...\n")

    for filename, target_dir in tqdm(sorted(RESTORE_MAP.items()), desc="Processing", unit="item"):
        success, message = restore_agent(filename, target_dir, args.dry_run)

        if success:
            icon = "○" if args.dry_run else "✓"
            print(f"  {icon} {filename} -> {target_dir}")
            restored += 1
        else:
            if "Already exists" in message:
                print(f"  ⊘ SKIP: {filename} (already exists)")
                skipped += 1
            else:
                print(f"  ✗ ERROR: {filename} - {message}")
                errors += 1

    print(f"\n{'=' * 70}")
    print("Summary:")
    print(f"  Restored: {restored}")
    print(f"  Skipped:  {skipped}")
    print(f"  Errors:   {errors}")

    print("\nAgents NOT restored (have active replacements):")
    for agent in sorted(SKIP_AGENTS):
        print(f"  - {agent}")

    if args.dry_run:
        print("\n[DRY RUN COMPLETE - Run without --dry-run to execute]")
    else:
        print("\n✓ RESTORATION COMPLETE")
        print("\nNext step: Regenerate agent_discovery_full.json")

    return 0 if errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
