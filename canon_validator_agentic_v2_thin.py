#!/usr/bin/env python3
# Canon Validator - Thin Wrapper Entry Point
# Coordinates L1-L5 components for 50-key canon validation.
# VERSION 3.2 - FULL REPO SCAN (All folders, all 20 keys, all agents)
# RATIONALE: All logic extracted to SSOT-compliant modules. This file is entry point only.

import sys
import os
import asyncio
import argparse
import traceback
from pathlib import Path

# [ETERNAL UTF-8] Force Windows consoles to handle unicode symbols
if sys.platform.startswith("win"):
    os.system("chcp 65001 >nul")
    sys.stdout.reconfigure(encoding='utf-8')

# [REENTRY GUARD] Prevent repeated full boot on convergence retries
_mission_executed = False

# [SOVEREIGN REPAIR] THE GRAVITY ANCHOR
# Resolve Absolute Project Root by looking for the .env 'Soul' of the project
current_file_path = Path(__file__).resolve()
project_root = None

for parent in current_file_path.parents:
    if (parent / ".env").exists():
        project_root = parent
        break

if not project_root:
    print(f"\n[!] [L6 ERROR] CRITICAL GRAVITY LOSS: Could not locate .env root from {current_file_path}")
    project_root = Path.cwd()

# [SOVEREIGN ANCHOR] Force project root into sys.path for Discovery
project_root_str = str(project_root)
if project_root_str not in sys.path:
    sys.path.insert(0, project_root_str)

# Re-establish Neural Link to Resurrected Territories
sovereign_paths = [
    project_root / "agentic_core" / "runtime" / "shared_runtime",
    project_root / "apps_shared" / "utils"
]

for p in sovereign_paths:
    p_str = str(p)
    if p.exists() and p_str not in sys.path:
        sys.path.insert(0, p_str)


def main():
    """Main entry point for the Canon Validator."""
    global _mission_executed
    
    parser = argparse.ArgumentParser(description="Canon Validator One-File Runner (Thin Wrapper)")
    parser.add_argument(
        "--target", 
        type=str, 
        default=".",  # [FULL REPO] Scan entire repo by default
        help="Target folder for validation (default: entire repo)"
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset sovereign state before validation"
    )
    parser.add_argument(
        "--heal",
        action="store_true",
        help="Run autonomous domain healing (dry-run by default)"
    )
    parser.add_argument(
        "--execute-heal",
        action="store_true",
        help="Execute heal changes (use with --heal)"
    )
    args = parser.parse_args()
    
    # Global mission timeout: 30 minutes
    MISSION_TIMEOUT = int(os.getenv("MISSION_TIMEOUT_SECONDS", "1800"))
    
    print(f"\n[*] Canon Validator v3.2 - Full Repo Scan (Thin Wrapper)")
    print(f"   [OK] Sovereign Neural Link Active at Root: {project_root_str}")
    
    # Handle reset if requested
    if args.reset:
        print("\n[*] SOVEREIGN STATE RESET ACTIVATED")
        try:
            from agentic_core.L0_maintenance.reset_sovereign_state import purge_volatile_state
            purge_volatile_state()
            print("   [OK] Volatile state purged - SSL fixes will take effect on clean slate")
        except Exception as e:
            print(f"   [!] Reset failed: {e}")
    
    # Handle autonomous healing mode (Canon Key 51 - Agent Autonomy Law)
    if args.heal:
        print("\n[*] SOVEREIGN HEAL MODE - Autonomous Domain Healing")
        print("   [LAW] Canon Key 51: All healing via agent.heal_repository() — no external scripts")
        
        execute_heal = args.execute_heal
        mode_str = "EXECUTE" if execute_heal else "DRY-RUN"
        print(f"   [MODE] {mode_str}")
        
        try:
            # Import autonomous agents
            from agentic_core.utils.core_extensions.NamingAgent import get_naming_agent
            from agentic_core.L5_safety.validators.AutonomyGuardianAgent import get_autonomy_guardian
            
            # All healing goes through agents directly — no scripts (Canon Key 51)
            agents = [
                ("NamingAgent", get_naming_agent(project_root)),
                ("AutonomyGuardian", get_autonomy_guardian(project_root)),
                # Add other autonomous agents as they become available:
                # ("LocationAgent", get_location_agent(project_root)),
                # ("UniquenessAgent", get_uniqueness_agent(project_root)),
            ]
            
            total_summary = {"agents_run": 0, "total_renamed": 0, "total_errors": 0}
            
            for agent_name, agent in agents:
                print(f"\n   [AGENT] {agent_name}.heal_repository()")
                try:
                    result = agent.heal_repository(
                        dry_run=not execute_heal,
                        execute=execute_heal,
                        depth=0,
                        max_depth=3,
                        _call_path=None,  # Clean start for each agent
                    )
                    total_summary["agents_run"] += 1
                    total_summary["total_renamed"] += result.get("renamed", 0)
                    total_summary["total_errors"] += result.get("errors", 0)
                except Exception as e:
                    print(f"   [!] {agent_name} failed: {e}")
                    total_summary["total_errors"] += 1
            
            print(f"\n[SOVEREIGN HEAL COMPLETE]")
            print(f"   Agents run: {total_summary['agents_run']}")
            print(f"   Total renamed: {total_summary['total_renamed']}")
            print(f"   Total errors: {total_summary['total_errors']}")
            
        except Exception as e:
            print(f"   [!] Heal mode failed: {e}")
            traceback.print_exc()
        
        return  # Exit after heal mode
    
    try:
        async def timed_mission():
            async with asyncio.timeout(MISSION_TIMEOUT):
                global _mission_executed
                if _mission_executed:
                    print("[INFO] Mission re-entry detected — skipping duplicate boot sequence")
                    return
                _mission_executed = True
                
                # Import and run the mission controller
                from agentic_core.L3_orchestration.workflow_engines.mission_controller import MissionController
                
                controller = MissionController(project_root)
                await controller.run_mission(args.target)
        
        asyncio.run(timed_mission())
        
    except KeyboardInterrupt:
        print("\n[!] Mission interrupted by user")
    except asyncio.TimeoutError:
        print(f"\n[X] Mission timed out after {MISSION_TIMEOUT}s")
    except Exception as e:
        print(f"\n[X] Mission failed: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()
