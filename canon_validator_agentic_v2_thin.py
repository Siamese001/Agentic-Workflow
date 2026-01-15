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
from datetime import datetime

from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    AGENT_DISCOVERY_JSON,
    AGENT_DISCOVERY_MANIFEST_JSON,
    AGENTIC_CORE_DIR,
    SCRIPTS_DIR,
    TESTS_DIR,
    DASHBOARD_DIR,
    L0_MAINTENANCE_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
    L6_OBSERVABILITY_DIR,
    get_validated_project_root,
)

# Define missing directory constants
APPS_SHARED_DIR = "apps_shared"
APPS_LIC_DIR = "apps_lic"
APPS_RG_DIR = "apps_rg"

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not required

# ----------------------------------------------------------------------
# NEW: Hybrid Interactive Discovery (Cached JSON ↔ Live Scan)
# ----------------------------------------------------------------------
try:
    from agentic_core.utils.discovery.Full_Agent_discovery import discover_all_agents
except ImportError:
    discover_all_agents = None

# [ETERNAL UTF-8] Force Windows consoles to handle unicode symbols
if sys.platform.startswith("win"):
    os.system("chcp 65001 >nul")
    sys.stdout.reconfigure(encoding='utf-8')

# [REENTRY GUARD] Prevent repeated full boot on convergence retries
_mission_executed = False

# ----------------------------------------------------------------------
# RUNTIME STATE MANAGEMENT - For Dashboard Live Observability
# ----------------------------------------------------------------------
import json as _json

RUNTIME_STATE_FILE = "runtime_state.json"
_runtime_state = {
    "status": "idle",
    "start_time": None,
    "current_agent": None,
    "current_layer": None,
    "agents_order": [],
    "total_agents": 0,
    "completed_agents": [],
    "events": [],
    "meta_learning": {"gemini_active": False, "note": ""}
}

def _save_runtime_state(project_root_path: Path):
    """Persist runtime state to JSON for dashboard polling."""
    try:
        state_path = project_root_path / RUNTIME_STATE_FILE
        state_path.write_text(_json.dumps(_runtime_state, indent=2, default=str), encoding="utf-8")
    except Exception:
        pass  # Non-critical

def _add_event(event_type: str, message: str):
    """Add timestamped event to runtime state."""
    _runtime_state["events"].append({
        "time": datetime.now().isoformat(),
        "type": event_type,
        "message": message
    })

# Agent layer mapping for UI display
AGENT_LAYERS = {
    "NamingAgent": "L5 – Safety & Governance",
    "AutonomyGuardian": "L5 – Safety & Governance",
    "LocationAgent": "L5 – Safety & Governance",
    "HierarchyAgent": "L5 – Safety & Governance",
    "StructuralHealerAgent": "L5 – Safety & Governance",
    "ComplianceOrchestratorAgent": "L5 – Safety & Governance",
    "AutonomyGuardianAgent": "L5 – Safety & Governance",
}

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
    project_root / AGENTIC_CORE_DIR / "runtime" / "shared_runtime",
    project_root / APPS_SHARED_DIR / "utils"
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
    parser.add_argument(
        "--agent",
        type=str,
        help="Run a specific agent directly (e.g., 'naming', 'location', 'hierarchy', 'filesystem', 'governance', 'guardian')"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Execute changes (use with --agent, same as --execute-heal)"
    )
    parser.add_argument(
        "--list-agents",
        action="store_true",
        help="List all discoverable agents"
    )
    parser.add_argument(
        "--yes", "-y",
        action="store_true",
        help="Automatic yes to all prompts (non-interactive mode)"
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Run autonomy compliance report"
    )
    parser.add_argument(
        "--method",
        type=str,
        default="heal_repository",
        help="Agent method to invoke (default: heal_repository)"
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
    
    # Helper to process discovery data → agent tuples
    def process_discovery_data(data):
        processed = []
        for agent in data:
            class_name = agent.get("class_name", "")
            if not class_name:
                continue
            path = agent.get("path", "").replace("\\", "/")
            module_path = path.replace("/", ".").replace(".py", "")
            processed.append((class_name, module_path))
        return processed

    # Replace the entire original list_available_agents with this new version
    def list_available_agents(dedupe: bool = True) -> list:
        """Hybrid agent discovery: prefer cached JSON with user prompt to fallback/refresh via live scan."""
        import json
        
        agents = []
        json_path = project_root / AGENT_DISCOVERY_JSON

        # Case 1: Cached JSON exists → use it automatically
        if json_path.exists():
            try:
                data = json.loads(json_path.read_text(encoding="utf-8"))
                agents = process_discovery_data(data)
                print(f"   [OK] Loaded {len(agents)} agents from cache")
            except Exception as e:
                print(f"   [!] Cache corrupt: {e}, falling back to live scan")

        # Case 2: No cache or user requested refresh → try live scan
        if not agents:  # Either no cache, corrupt, or user chose refresh
            if discover_all_agents is None:
                print("   [!] Live discovery module not available (Full_Agent_discovery.py missing/wrong path)")
                if json_path.exists():
                    print("   [FALLBACK] Forcing load from (possibly outdated) cache")
                    try:
                        data = json.loads(json_path.read_text(encoding="utf-8"))
                        agents = process_discovery_data(data)
                    except Exception:
                        pass
                if not agents:
                    print("   [ERROR] No agent list available — aborting discovery")
                    return []
            else:
                # Auto-run live scan if cache doesn't exist or is corrupt
                run_live = True
                if not json_path.exists():
                    print(f"\n[*] No cached discovery file found, running live scan...")
                    
                    if not run_live:
                        print("   [ABORT] Cannot proceed without agent list")
                        return []

                print("   [RUNNING] Live AST discovery via Full_Agent_discovery.discover_all_agents()...")
                try:
                    discovery_data = discover_all_agents(project_root)  # ← adjust arg type if needed (Path/str)
                    agents = process_discovery_data(discovery_data)
                    print(f"   [OK] Discovered {len(agents)} agents (fresh)")

                    # Auto-save cache for next run
                    try:
                        json_path.write_text(json.dumps(discovery_data, indent=2), encoding="utf-8")
                        print(f"   [CACHE] Saved fresh discovery to {json_path}")
                    except Exception as e:
                        print(f"   [!] Could not save cache: {e}")
                except Exception as e:
                    print(f"   [!] Live discovery failed: {e}")
                    traceback.print_exc()
                    return []

        if dedupe:
            agents = sorted(set(agents), key=lambda x: (x[0], x[1]))
        else:
            agents = sorted(agents, key=lambda x: (x[0], x[1]))

        return agents
    
    # Handle --list-agents
    if args.list_agents:
        print("\n[*] DISCOVERABLE AGENTS (from agent_discovery_full.json):\n")
        all_agents = list_available_agents()
        for i, (class_name, module_path) in enumerate(all_agents, 1):
            print(f"   {i:3}. {class_name:<45} [{module_path}]")
        print(f"\n   Total: {len(all_agents)} agents")
        print("\n   Usage: python canon_validator_agentic_v2_thin.py --agent <name> [--execute]")
        print("   Example: python canon_validator_agentic_v2_thin.py --agent NamingAgent --execute")
        return
    
    # Handle --report (compliance report shortcut)
    if args.report:
        print("\n[*] Running Autonomy Compliance Report...")
        try:
            # Import Guardian and Targets Config
            from agentic_core.config.autonomy_targets import get_target
            from agentic_core.L5_safety.validators.AutonomyGuardianAgent import get_autonomy_guardian
            guardian = get_autonomy_guardian(project_root)
            # Pass extra config if needed to inject targets during JSON generation
            print("   [TARGETS] Exceptions config loaded from agentic_core/config/autonomy_targets.py")
            guardian.generate_compliance_report(context={"target_resolver": get_target})
        except Exception as e:
            print(f"   [!] Report failed: {e}")
            traceback.print_exc()
        return
    
    # Handle single agent invocation via dynamic discovery
    if args.agent:
        print(f"\n[*] AGENT MODE - Direct invocation of {args.agent.upper()}")
        
        execute = args.execute or args.execute_heal
        mode_str = "EXECUTE" if execute else "DRY-RUN"
        print(f"   [MODE] {mode_str}")
        
        # AST-based agent discovery - find class by name
        def discover_agent(agent_name: str) -> tuple:
            """Discover agent by searching for matching class name via AST."""
            # Normalize search term
            search_term = agent_name.lower().replace("-", "").replace("_", "")
            
            # Search through all discovered agents
            all_agents = list_available_agents()
            
            # Exact match first
            for class_name, module_path in all_agents:
                if class_name.lower() == search_term or class_name.lower() == search_term + "agent":
                    return (module_path, class_name)
            
            # Partial match (prefix)
            for class_name, module_path in all_agents:
                class_normalized = class_name.lower().replace("_", "")
                if class_normalized.startswith(search_term) or search_term in class_normalized:
                    return (module_path, class_name)
            
            return None
        
        discovery_result = discover_agent(args.agent)
        if not discovery_result:
            print(f"   [!] Agent not found: {args.agent}")
            print("   Available agents (use any unique prefix):")
            for class_name, _ in list_available_agents()[:30]:  # Show first 30
                print(f"      - {class_name}")
            print(f"   ... and more. Use --list-agents for full list.")
            sys.exit(1)
        
        module_path, agent_name = discovery_result
        print(f"   [DISCOVERED] {module_path}.{agent_name}")
        
        try:
            module = __import__(module_path, fromlist=[agent_name])
            
            # Try getter function first, then class
            getter_name = f"get_{agent_name.lower()}" if not agent_name.startswith("get_") else agent_name
            if hasattr(module, getter_name):
                agent = getattr(module, getter_name)(project_root)
            elif hasattr(module, agent_name):
                agent_cls = getattr(module, agent_name)
                agent = agent_cls(project_root)
            else:
                # Find any class ending with Agent
                for attr_name in dir(module):
                    if attr_name.endswith("Agent") and not attr_name.startswith("_"):
                        agent_cls = getattr(module, attr_name)
                        if callable(agent_cls):
                            agent = agent_cls(project_root)
                            break
                else:
                    raise AttributeError(f"No Agent class found in {module_path}")
            
            # Invoke specified method (default: heal_repository)
            method_name = args.method
            if not hasattr(agent, method_name):
                print(f"   [!] Method '{method_name}' not found on {agent.__class__.__name__}")
                print(f"   Available methods: {[m for m in dir(agent) if not m.startswith('_') and callable(getattr(agent, m))]}")
                sys.exit(1)
            
            print(f"   [AGENT] {agent.__class__.__name__}.{method_name}()\n")
            
            method = getattr(agent, method_name)
            if method_name == "heal_repository":
                result = method(
                    dry_run=not execute,
                    execute=execute,
                    depth=0,
                    max_depth=3,
                )
                print(f"\n[AGENT COMPLETE]")
                print(f"   Renamed: {result.get('renamed', 0)}")
                print(f"   Errors: {result.get('errors', 0)}")
            elif method_name == "generate_compliance_report":
                method()
            elif method_name == "run":
                result = method()
                print(f"\n[AGENT COMPLETE]")
                print(f"   Result: {result}")
            else:
                result = method()
                print(f"\n[AGENT COMPLETE]")
                if result:
                    print(f"   Result: {result}")
            
        except Exception as e:
            print(f"   [!] Agent invocation failed: {e}")
            traceback.print_exc()
            sys.exit(1)
        
        return  # Exit after agent mode
    
    # Handle autonomous healing mode
    if args.heal:
        print("\n[*] SOVEREIGN HEAL MODE - Autonomous Domain Healing")
        print("   [LAW] All healing via agent.heal_repository() — no external scripts")
        
        execute_heal = getattr(args, 'execute_heal', False)
        mode_str = "EXECUTE" if execute_heal else "DRY-RUN"
        print(f"   [MODE] {mode_str}")
        
        try:
            # Import autonomous agents
            from agentic_core.utils.core_extensions.NamingAgent import get_naming_agent
            from agentic_core.L5_safety.validators.AutonomyGuardianAgent import get_autonomy_guardian
            
            # Phase 4.2: Repository-wide Sovereign Sweep across all aligned domains
            domains = [AGENTIC_CORE_DIR, APPS_LIC_DIR, APPS_RG_DIR, SCRIPTS_DIR]
            consolidated_results = []
            
            # Track Gemini embedder status
            gemini_active = False
            try:
                guardian = get_autonomy_guardian(project_root)
                gemini_active = guardian.gemini_embedder is not None
            except:
                pass
            
            # Build agent list for runtime state
            agents_template = [
                ("NamingAgent", get_naming_agent),
                ("AutonomyGuardian", get_autonomy_guardian),
            ]
            
            # Calculate full execution order for progress tracking
            full_order = []
            for domain in domains:
                domain_path = project_root / domain
                if domain_path.exists():
                    for agent_name, _ in agents_template:
                        full_order.append(f"{agent_name} → {domain}")
            
            # Initialize runtime state for dashboard
            _runtime_state.update({
                "status": "healing",
                "start_time": datetime.now().isoformat(),
                "current_agent": None,
                "current_layer": None,
                "agents_order": full_order,
                "total_agents": len(full_order),
                "completed_agents": [],
                "events": [],
                "meta_learning": {
                    "gemini_active": gemini_active,
                    "note": "Experiences embedded on success" if gemini_active else "Logging only"
                }
            })
            _add_event("info", f"Heal mode started ({mode_str})")
            _add_event("meta", f"Meta-learning {'ACTIVE' if gemini_active else 'INACTIVE'}")
            _save_runtime_state(project_root)
            
            for domain in domains:
                print(f"\n[SOVEREIGN SWEEP] Targeting Domain: {domain}")
                
                # Check if domain exists
                domain_path = project_root / domain
                if not domain_path.exists():
                    print(f"   [SKIP] Domain not found: {domain}")
                    _add_event("info", f"Skipped domain (not found): {domain}")
                    _save_runtime_state(project_root)
                    continue
                
                # Log domain start
                _add_event("info", f"Starting domain sweep: {domain}")
                _save_runtime_state(project_root)
                
                # All healing goes through agents directly — no scripts
                agents = [
                    ("NamingAgent", get_naming_agent(project_root)),
                    ("AutonomyGuardian", get_autonomy_guardian(project_root)),
                ]
                
                domain_summary = {
                    "domain": domain,
                    "agents_run": 0, 
                    "total_renamed": 0, 
                    "total_errors": 0,
                    "total_scanned": 0,
                    "total_fixed": 0,
                    "total_violations": 0
                }
                
                for agent_name, agent in agents:
                    print(f"\n   [AGENT] {agent_name}.heal_repository()")
                    
                    # Update runtime state - agent starting
                    layer = AGENT_LAYERS.get(agent_name, "Unknown")
                    _runtime_state["current_agent"] = agent_name
                    _runtime_state["current_layer"] = layer
                    _add_event("agent_start", f"→ Running {agent_name} ({layer}) on {domain}")
                    _save_runtime_state(project_root)
                    
                    try:
                        result = agent.heal_repository(
                            dry_run=not execute_heal,
                            execute=execute_heal,
                            depth=0,
                            max_depth=3,
                            _call_path=None,  # Clean start for each agent
                        )
                        domain_summary["agents_run"] += 1
                        renamed = result.get("renamed", 0)
                        errors = result.get("errors", 0)
                        fixed = result.get("fixed", 0)
                        violations = result.get("violations", 0)
                        scanned = result.get("scanned", 0)
                        
                        domain_summary["total_renamed"] += renamed
                        domain_summary["total_errors"] += errors
                        domain_summary["total_fixed"] += fixed
                        domain_summary["total_violations"] += violations
                        domain_summary["total_scanned"] += scanned
                        
                        # Build detailed completion message
                        details = []
                        if scanned: details.append(f"scanned: {scanned}")
                        if renamed: details.append(f"renamed: {renamed}")
                        details.append(f"fixed: {fixed}")
                        details.append(f"violations: {violations}")
                        detail_str = " | ".join(details)
                        
                        _add_event("agent_end", f"✓ {agent_name}: {detail_str}")
                        _runtime_state["completed_agents"].append(f"{agent_name} → {domain}")
                        _save_runtime_state(project_root)
                        
                    except Exception as e:
                        print(f"   [!] {agent_name} failed: {e}")
                        domain_summary["total_errors"] += 1
                        _add_event("error", f"✗ {agent_name} failed on {domain}: {str(e)[:200]}...")
                        _runtime_state["completed_agents"].append(f"{agent_name} → {domain}")
                        _save_runtime_state(project_root)
                
                # Calculate domain compliance score
                total_checks = domain_summary["total_violations"] + domain_summary["total_fixed"]
                domain_summary["compliance_score"] = 100 if total_checks == 0 else int((1 - domain_summary["total_violations"] / max(total_checks, 1)) * 100)
                
                # Domain sweep complete
                _add_event("info", f"Domain sweep completed: {domain}")
                _save_runtime_state(project_root)
                
                consolidated_results.append(domain_summary)
                
                # Phase 4.3: Log health snapshot to L4 (if available)
                try:
                    from agentic_core.L6_observability.metrics.SovereignHealthMonitor import SovereignHealthMonitor
                    guardian = get_autonomy_guardian(project_root)
                    if hasattr(guardian, 'redis') and guardian.redis:
                        monitor = SovereignHealthMonitor(guardian.redis)
                        monitor.log_snapshot(
                            domain=domain,
                            score=domain_summary["compliance_score"],
                            fixes=domain_summary["total_fixed"]
                        )
                except Exception:
                    pass  # Health monitoring is optional
            
            # Finalize runtime state
            _runtime_state["status"] = "idle"
            _runtime_state["current_agent"] = None
            _runtime_state["current_layer"] = None
            _add_event("info", "Heal mode completed — full sweep finished")
            _save_runtime_state(project_root)
            
            # Phase 4.5: Autonomous Executive Summary
            report_consolidated_summary(consolidated_results, gemini_active)
            
        except Exception as e:
            print(f"   [!] Heal mode failed: {e}")
            traceback.print_exc()
            _add_event("error", f"Heal mode failed: {str(e)[:300]}...")
            _runtime_state["status"] = "error"
            _save_runtime_state(project_root)
        
        return  # Exit after heal mode


def report_consolidated_summary(results, gemini_active):
    """Phase 4.5: Generates the Consolidated Sovereign Health Report."""
    print("\n" + "="*60)
    print("FINAL CONSOLIDATED SOVEREIGN HEALTH REPORT")
    print("="*60)
    
    # Aggregate cross-domain metrics
    total_summary = {
        "agents_run": 0,
        "total_renamed": 0,
        "total_errors": 0,
        "total_fixed": 0,
        "total_violations": 0
    }
    
    print("\nDomain-by-Domain Health:")
    for res in results:
        domain = res.get("domain", "unknown")
        compliance = res.get("compliance_score", 0)
        fixed = res.get("total_fixed", 0)
        violations = res.get("total_violations", 0)
        
        # Aggregate totals
        total_summary["agents_run"] += res.get("agents_run", 0)
        total_summary["total_renamed"] += res.get("total_renamed", 0)
        total_summary["total_errors"] += res.get("total_errors", 0)
        total_summary["total_fixed"] += fixed
        total_summary["total_violations"] += violations
        
        status = "✅" if compliance == 100 else "⚠️" if compliance >= 80 else "❌"
        print(f"  {status} {domain:20} Compliance: {compliance}%  Fixed: {fixed}  Violations: {violations}")
    
    # Calculate overall compliance
    total_checks = total_summary["total_violations"] + total_summary["total_fixed"]
    overall_compliance = 100 if total_checks == 0 else int((1 - total_summary["total_violations"] / max(total_checks, 1)) * 100)
    
    print("\n" + "="*60)
    print("OVERALL SOVEREIGN HEALTH")
    print("="*60)
    print(f"  Domains Scanned: {len(results)}")
    print(f"  Overall Compliance: {overall_compliance}%")
    print(f"  Total Fixed: {total_summary['total_fixed']}")
    print(f"  Total Violations: {total_summary['total_violations']}")
    print(f"  Total Errors: {total_summary['total_errors']}")
    
    # Display Meta-Learning memory growth
    if gemini_active:
        print(f"\n  Meta-Learning: ACTIVE (Gemini 768D)")
        print(f"  L4 Memory: Historical snapshots persisted")
    else:
        print(f"\n  Meta-Learning: LOGGING ONLY (Set GOOGLE_API_KEY to activate)")
    
    print("="*60)


if __name__ == "__main__":
    main()
