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
import importlib

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

# Color-coded terminal output for progress visibility
try:
    from agentic_core.utils.terminal_colors import (
        phase_header, tier_summary, mission_header, mission_summary,
        agent_status, progress_bar, log_status, Colors, heartbeat
    )
    COLORS_AVAILABLE = True
except ImportError:
    COLORS_AVAILABLE = False
    def phase_header(*args, **kwargs): return f"\n[PHASE] {args[0] if args else ''}"
    def tier_summary(*args, **kwargs): return ""
    def mission_header(*args, **kwargs): return "\n[MISSION START]"
    def mission_summary(*args, **kwargs): return "\n[MISSION COMPLETE]"
    def agent_status(*args, **kwargs): return f"  {args[0] if args else ''}"
    def progress_bar(*args, **kwargs): return ""
    def log_status(level, msg, **kwargs): print(f"[{level.upper()}] {msg}")
    def heartbeat(i): return "."
    class Colors:
        RESET = BRIGHT_GREEN = BRIGHT_RED = BRIGHT_YELLOW = BRIGHT_CYAN = DIM = ""

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
    from scripts.full_agent_discovery import discover_all_agents
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
    "status": "idle",  # idle | running | completed | error
    "start_time": None,
    "end_time": None,
    "current_agent": None,
    "current_layer": None,
    "agents_order": [],
    "total_agents": 0,
    "completed_agents": [],
    "events": [],
    
    # Meta-Learning Metrics (Phase 1.1)
    "meta_learning": {
        "enabled": False,
        "total_experiences": 0,
        "patterns_extracted": 0,
        "strategy_weights": {
            "cot": 1.0,
            "tot": 1.0,
            "react": 1.0,
            "reflection": 1.0
        },
        "recent_experiences": [],  # Last 10 experiences
        "pattern_history": []  # Pattern extraction timeline
    },
    
    # Redis Metrics (Phase 1.1)
    "redis": {
        "connected": False,
        "operations": {
            "get": 0,
            "set": 0,
            "delete": 0,
            "total": 0
        },
        "cache_hits": 0,
        "cache_misses": 0,
        "hit_rate": 0.0,
        "recent_operations": []  # Last 20 operations
    },
    
    # Pinecone Metrics (Phase 1.1)
    "pinecone": {
        "connected": False,
        "operations": {
            "upsert": 0,
            "query": 0,
            "delete": 0,
            "total": 0
        },
        "vectors_stored": 0,
        "avg_similarity": 0.0,
        "recent_queries": []  # Last 10 queries with results
    },
    
    # Agent Execution Timeline (Phase 1.1)
    "execution_timeline": []  # [{agent, layer, start, end, duration, success}]
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

def _update_meta_learning_state(experience_data: dict):
    """Update runtime state with new meta-learning experience."""
    ml = _runtime_state["meta_learning"]
    ml["enabled"] = True
    ml["total_experiences"] = experience_data.get("total_experiences", ml["total_experiences"])
    ml["patterns_extracted"] = experience_data.get("patterns_extracted", ml["patterns_extracted"])
    
    if "strategy_weights" in experience_data:
        ml["strategy_weights"] = experience_data["strategy_weights"]
    
    if "experience" in experience_data:
        ml["recent_experiences"].insert(0, experience_data["experience"])
        ml["recent_experiences"] = ml["recent_experiences"][:10]  # Keep last 10
    
    if "pattern" in experience_data:
        ml["pattern_history"].append({
            "pattern": experience_data["pattern"],
            "timestamp": datetime.now().isoformat()
        })

def _update_redis_state(operation: str, key: str, hit: bool = None):
    """Update runtime state with Redis operation."""
    redis = _runtime_state["redis"]
    redis["connected"] = True
    
    if operation in redis["operations"]:
        redis["operations"][operation] += 1
    redis["operations"]["total"] += 1
    
    if hit is not None:
        if hit:
            redis["cache_hits"] += 1
        else:
            redis["cache_misses"] += 1
        
        total = redis["cache_hits"] + redis["cache_misses"]
        redis["hit_rate"] = redis["cache_hits"] / total if total > 0 else 0.0
    
    redis["recent_operations"].insert(0, {
        "operation": operation,
        "key": key,
        "hit": hit,
        "timestamp": datetime.now().isoformat()
    })
    redis["recent_operations"] = redis["recent_operations"][:20]  # Keep last 20

def _update_pinecone_state(operation: str, metadata: dict = None):
    """Update runtime state with Pinecone operation."""
    pc = _runtime_state["pinecone"]
    pc["connected"] = True
    
    if operation in pc["operations"]:
        pc["operations"][operation] += 1
    pc["operations"]["total"] += 1
    
    if metadata:
        if "vectors_count" in metadata:
            pc["vectors_stored"] += metadata["vectors_count"]
        
        if "similarity" in metadata:
            # Running average of similarity scores
            total_queries = pc["operations"]["query"]
            if total_queries > 0:
                pc["avg_similarity"] = (
                    (pc["avg_similarity"] * (total_queries - 1) + metadata["similarity"]) / total_queries
                )
        
        if operation == "query":
            pc["recent_queries"].insert(0, {
                "results": metadata.get("results", []),
                "top_k": metadata.get("top_k", 0),
                "avg_score": metadata.get("similarity", 0),
                "timestamp": datetime.now().isoformat()
            })
            pc["recent_queries"] = pc["recent_queries"][:10]  # Keep last 10

def _update_agent_execution(agent_name: str, layer: str, start_time: float, end_time: float, success: bool):
    """Update execution timeline with agent completion."""
    _runtime_state["execution_timeline"].append({
        "agent": agent_name,
        "layer": layer,
        "start": start_time,
        "end": end_time,
        "duration": end_time - start_time,
        "success": success
    })

# Agent layer mapping for UI display
AGENT_LAYERS = {
    # L5 Safety & Governance
    "NamingAgent": "L5 – Safety & Governance",
    "AutonomyGuardian": "L5 – Safety & Governance",
    "LocationAgent": "L5 – Safety & Governance",
    "HierarchyAgent": "L5 – Safety & Governance",
    "StructuralHealerAgent": "L5 – Safety & Governance",
    "ComplianceOrchestratorAgent": "L5 – Safety & Governance",
    "AutonomyGuardianAgent": "L5 – Safety & Governance",
    
    # L2 Execution (Future Activation)
    "ImportAgent": "L2 – Execution & Tools",
    "StructuralEngineerAgent": "L2 – Execution & Tools",
    
    # L1 Cognition (Future Activation)
    "GovernanceAgent": "L1 – Cognition & Intelligence",
    "DocumentationAgent": "L1 – Cognition & Intelligence",
    
    # L4 State & Memory (Phase 5 Activation)
    "CheckpointManagerAgent": "L4 – State & Memory",
    
    # L6 Observability & Metrics (Phase 5 Activation)
    "PerformanceAnalystAgent": "L6 – Observability & Metrics",
    
    # L0 Maintenance (Future Activation)
    "BootstrapAgent": "L0 – Maintenance & Infrastructure",
    "FilesystemSSOTReconcilerAgent": "L0 – Maintenance & Infrastructure",
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
        """
        STRICT SSOT DISCOVERY: Always runs live AST scan.
        No caching, no stale artifacts. Guaranteed fresh truth.
        """
        if discover_all_agents is None:
            print("   [CRITICAL] SSOT Discovery Module missing!")
            return []

        print("   [SSOT] Executing Strict Live AST Discovery...")
        try:
            discovery_data = discover_all_agents(project_root)
            agents = process_discovery_data(discovery_data)
            print(f"   [OK] SSOT Verified: {len(agents)} agents discovered")
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
            # [PHASE 3] UNIFIED ORCHESTRATION - Strategy Pattern
            # The 5-tier logic is now encapsulated in HealingStrategy
            from agentic_core.L3_orchestration.unified_orchestrator import UnifiedOrchestratorAgent
            from agentic_core.L3_orchestration.strategies.healing_strategy import HealingStrategy
            from agentic_core.L4_state.ValidationContext.CheckpointManagerAgent import get_checkpoint_manager
            
            # Helper to safely load Performance Analyst (L6)
            def get_performance_analyst_safe(root):
                try:
                    import importlib.util
                    spec = importlib.util.find_spec("agentic_core.L6_observability.agents.PerformanceAnalystAgentSimple")
                    if spec:
                        perf_module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(perf_module)
                        return perf_module.get_performance_analyst(root)
                except: pass
                return None

            # [UNIFIED ENGINE] Create orchestrator with HealingStrategy
            strategy = HealingStrategy(project_root=project_root)
            orchestrator = UnifiedOrchestratorAgent(
                strategy=strategy,
                project_root=project_root,
                name="SovereignHealOrchestrator"
            )
            
            checkpoint_manager = get_checkpoint_manager(project_root)
            performance_analyst = get_performance_analyst_safe(project_root)
            
            # Build mission context
            mission_context = {
                "dry_run": not execute_heal,
                "execute": execute_heal,
                "checkpoint_manager": checkpoint_manager,
                "performance_analyst": performance_analyst,
                "scan_mode": "unified_sovereign_sweep"
            }
            
            # Get tier info for runtime state
            tiers = strategy.get_tiers()
            all_agent_names = []
            for tier_agents in tiers.values():
                all_agent_names.extend(tier_agents)
            
            # Check for Gemini activation
            gemini_active = False
            try:
                from agentic_core.L5_safety.validators.AutonomyGuardianAgent import get_autonomy_guardian
                guardian = get_autonomy_guardian(project_root)
                gemini_active = hasattr(guardian, 'gemini_embedder') and guardian.gemini_embedder is not None
            except: pass
            
            # Initialize runtime state for dashboard
            _runtime_state.update({
                "status": "healing",
                "start_time": datetime.now().isoformat(),
                "agents_order": all_agent_names,
                "total_agents": len(all_agent_names),
                "completed_agents": [],
                "events": [],
                "execution_timeline": []
            })
            _add_event("info", f"Heal mode started ({mode_str}) - Unified Engine")
            _add_event("meta", f"Meta-learning {'ACTIVE' if gemini_active else 'INACTIVE'}")
            _save_runtime_state(project_root)

            # --- UNIFIED MISSION EXECUTION ---
            print(mission_header("SOVEREIGN HEAL (UNIFIED)", execute=execute_heal))
            
            mission_start = datetime.now()
            results = orchestrator.run_mission(mission_context)
            mission_end = datetime.now()
            
            # Update runtime state with execution timeline from results
            for i, agent_result in enumerate(results.get("agent_results", [])):
                _runtime_state["execution_timeline"].append({
                    "agent": agent_result.get("agent_name", f"agent_{i}"),
                    "status": agent_result.get("status", "UNKNOWN"),
                    "fixes": agent_result.get("violations_fixed", 0),
                    "violations": agent_result.get("violations_found", 0),
                    "duration_ms": agent_result.get("execution_time_ms", 0)
                })
            _save_runtime_state(project_root)
            
            # Map MissionResult to reporting format
            total_fixes = results.get("total_fixed", 0)
            total_violations = results.get("total_violations", 0)
            agents_run = len(results.get("agent_results", []))
            
            consolidated_results = [{
                "domain": "Sovereign Repository",
                "agents_run": agents_run,
                "total_fixed": total_fixes,
                "total_violations": total_violations,
                "compliance_score": 100 if (total_fixes + total_violations) == 0 else int((1 - total_violations / max(total_fixes + total_violations, 1)) * 100)
            }]
            
            # Log abort info if mission was aborted
            if results.get("aborted"):
                _add_event("warning", f"Mission aborted: {results.get('abort_reason', 'Unknown')}")
                log_status("warning", f"Mission aborted: {results.get('abort_reason', 'Unknown')}")
            
            # Finalize runtime state
            _runtime_state["status"] = "idle"
            _runtime_state["current_agent"] = None
            _runtime_state["current_layer"] = None
            _add_event("info", f"Heal mode completed — Unified Engine ({results.get('status', 'UNKNOWN')})")
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
    # Calculate totals for mission_summary
    total_agents = sum(r.get("agents_run", 0) for r in results)
    total_fixed = sum(r.get("total_fixed", 0) for r in results)
    total_violations = sum(r.get("total_violations", 0) for r in results)
    total_errors = sum(r.get("total_errors", 0) for r in results)
    
    success = total_violations == 0
    print(mission_summary(total_agents, total_fixed, total_violations, total_errors, 0, success))
    
    print("\n" + "="*60)
    print(f"{Colors.BRIGHT_CYAN if COLORS_AVAILABLE else ''}FINAL CONSOLIDATED SOVEREIGN HEALTH REPORT{Colors.RESET if COLORS_AVAILABLE else ''}")
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
