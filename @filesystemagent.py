#!/usr/bin/env python3
"""
Sovereign direct agent launcher — @agentname.py
Canon Key 51 compliance - Direct agent invocation, no runner scripts.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Map: lowercase stem → getter import
AGENT_MAP = {
    "namingagent": "from agentic_core.utils.core_extensions.NamingAgent import get_naming_agent",
    "hierarchyagent": "from agentic_core.L5_safety.validators.HierarchyAgent import HierarchyAgent",
    "locationagent": "from agentic_core.L5_safety.validators.LocationAgent import LocationAgent",
    "filesystemagent": "from agentic_core.L5_safety.validators.FilesystemAgent import FilesystemAgent",
    "governanceagent": "from agentic_core.L5_safety.validators.GovernanceAgent import get_governance_agent",
    "guardianagent": "from agentic_core.L5_safety.validators.AutonomyGuardianAgent import AutonomyGuardianAgent",
    "hop1": "from apps_lic.engines.outreach_engine.hop_agents.HOP1ProfileAnalysisAgent import HOP1ProfileAnalysisAgent",
    "hop2": "from apps_lic.engines.outreach_engine.HOP2ResearchAgent import HOP2ResearchAgent",
    "hop3": "from apps_lic.engines.outreach_engine.hop_agents.HOP3SenderGroundingAgent import HOP3SenderGroundingAgent",
    "hop4": "from apps_lic.engines.outreach_engine.hop_agents.HOP4RoutingAgent import HOP4RoutingAgent",
    "hop5": "from apps_lic.engines.outreach_engine.HOP5GenerationAgent import HOP5GenerationAgent",
    "hop6": "from apps_lic.engines.outreach_engine.HOP6ValidationAgent import HOP6ValidationAgent",
    "hop7": "from apps_lic.engines.outreach_engine.hop_agents.HOP7GateDecisionAgent import HOP7GateDecisionAgent",
    "hop8": "from apps_lic.engines.outreach_engine.HOP8QAReportAgent import HOP8QAReportAgent",
}

def main() -> None:
    invoked = Path(sys.argv[0]).stem.lower().lstrip("@")
    if invoked not in AGENT_MAP:
        print(f"[!] Unknown agent: {invoked}")
        print("\nCompliant agents:")
        for k in sorted(AGENT_MAP):
            print(f"  @{k}.py")
        sys.exit(1)

    parser = argparse.ArgumentParser(description=f"Direct invocation of {invoked}")
    parser.add_argument("--execute", action="store_true", help="Execute healing (default: dry-run)")
    parser.add_argument("--depth", type=int, default=0, help="Recursion depth (default: 0)")
    parser.add_argument("--max-depth", type=int, default=3, help="Max recursion depth (default: 3)")
    args = parser.parse_args()

    code = AGENT_MAP[invoked]
    ns = {}
    exec(code, globals(), ns)
    
    # Get the class or getter function
    agent_cls_or_getter = list(ns.values())[-1]
    
    # Instantiate agent
    project_root = Path(".").resolve()
    if callable(agent_cls_or_getter) and agent_cls_or_getter.__name__.startswith("get_"):
        # It's a getter function
        agent = agent_cls_or_getter(project_root)
    else:
        # It's a class
        agent = agent_cls_or_getter(project_root)
    
    print(f"[{agent.__class__.__name__}] Direct sovereign run")
    print(f"  Mode: {'EXECUTE' if args.execute else 'DRY-RUN'}")
    print(f"  Depth: {args.depth}/{args.max_depth}\n")

    result = agent.heal_repository(
        dry_run=not args.execute,
        execute=args.execute,
        depth=args.depth,
        max_depth=args.max_depth,
    )
    
    print(f"\n[RESULT] {result}")

if __name__ == "__main__":
    main()
