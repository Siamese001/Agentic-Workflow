#!/usr/bin/env python3
"""
Unified Sovereign Compliance Protocol (v4.0)
Merges SSOT Compliance Protocol (Autonomous Decision Engine) with Canon Validator (Observability & Discovery).

PRIMARY FEATURES:
- Autonomous Confidence-Based Healing (SSOT)
- Real-time Runtime State & Dashboard Integration (Canon)
- Multi-Domain Orchestration (Canon)
- Hybrid Agent Discovery (Canon)
- Comprehensive Audit Trail (SSOT)
"""

import sys
import os
import json
import logging
import argparse
import traceback
import importlib.util
import tempfile
import time
import builtins
import atexit  # [HARDENED] For guaranteed state cleanup
import stat  # [HARDENED] For permission bits
from functools import wraps
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field

# [ETERNAL UTF-8] Force Windows consoles to handle unicode symbols (From Canon)
if sys.platform.startswith("win"):
    os.system("chcp 65001 >nul")
    sys.stdout.reconfigure(encoding='utf-8')

# ============================================================================
# CONFIGURATION & CONSTANTS
# ============================================================================

# Directory Constants
AGENTIC_CORE_DIR = "agentic_core"
APPS_SHARED_DIR = "apps_shared"
APPS_LIC_DIR = "apps_lic"
APPS_RG_DIR = "apps_rg"
SCRIPTS_DIR = "scripts"
AGENT_DISCOVERY_JSON = "agent_discovery_full.json"
RUNTIME_STATE_FILE = "runtime_state.json"

# Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [SOVEREIGN] - %(levelname)s - %(message)s'
)
logger = logging.getLogger("UnifiedSovereign")

# ============================================================================
# HARDENING UTILITIES (NEW)
# ============================================================================

class NonInteractiveGuard:
    """
    [HARDENED] Global overrides to prevent terminal prompts from hanging CI/CD.
    Now includes Resource Exhaustion Protection against infinite prompt loops.
    """
    def __init__(self, active: bool = True, max_blocked_prompts: int = 10):
        self.active = active
        self.max_blocked_prompts = max_blocked_prompts
        self.blocked_count = 0
        self.original_input = builtins.input

    def __enter__(self):
        if self.active:
            builtins.input = self._trap_input
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        builtins.input = self.original_input

    def _trap_input(self, prompt=None):
        self.blocked_count += 1
        logger.warning(f"BLOCKED PROMPT ({self.blocked_count}/{self.max_blocked_prompts}): Agent attempted input('{prompt}')")
        
        # [HARDENED] Resource Exhaustion Protection
        if self.blocked_count > self.max_blocked_prompts:
            logger.critical("Infinite prompt loop detected - killing process capability")
            raise RecursionError("Interactive prompt limit exceeded (Infinite Loop Protection)")
            
        raise RuntimeError(f"Interactive prompt blocked in autonomous mode: {prompt}")

def with_retry(max_retries=3, delay=1.0):
    """
    [HARDENED] Decorator for transient failure resilience with exponential backoff.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    # Don't retry on security guard or exhaustion errors
                    if isinstance(e, RuntimeError) and "prompt" in str(e):
                        raise e
                    if isinstance(e, RecursionError):
                        raise e
                    
                    wait_time = delay * (2 ** attempt)
                    logger.warning(f"Retry {attempt + 1}/{max_retries} for {func.__name__} failed: {e}. Waiting {wait_time}s")
                    time.sleep(wait_time)
            logger.error(f"All retries failed for {func.__name__}")
            raise last_exception
        return wrapper
    return decorator

# ============================================================================
# RUNTIME STATE MANAGEMENT (From Canon Validator)
# ============================================================================

class RuntimeStateManager:
    """Manages live state for dashboard observability."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.state = {
            "status": "idle",
            "start_time": None,
            "end_time": None,
            "current_agent": None,
            "current_layer": None,
            "agents_order": [],
            "completed_agents": [],
            "events": [],
            # [INTEGRATION] Ported from Canon Validator
            "meta_learning": {
                "enabled": False,
                "total_experiences": 0,
                "patterns_extracted": 0,
                "strategy_weights": {"cot": 1.0, "tot": 1.0, "react": 1.0},
                "recent_experiences": []
            },
            "compliance_scores": {}
        }
        # [HARDENED] Register exit handler to prevent 'zombie' running states
        atexit.register(self._emergency_cleanup)

    def start_mission(self, mission_type: str, agents_order: List[str]):
        self.state["status"] = "running"
        self.state["start_time"] = datetime.now().isoformat()
        self.state["agents_order"] = agents_order
        self.add_event("info", f"Mission started: {mission_type}")
        self.save()

    def update_agent(self, agent_name: str, layer: str):
        self.state["current_agent"] = agent_name
        self.state["current_layer"] = layer
        self.add_event("agent_start", f"→ Executing {agent_name} ({layer})")
        self.save()

    def complete_agent(self, agent_name: str, success: bool, details: str = ""):
        self.state["completed_agents"].append({
            "agent": agent_name,
            "time": datetime.now().isoformat(),
            "success": success,
            "details": details
        })
        self.add_event("agent_end", f"{'✓' if success else '❌'} Completed {agent_name}")
        self.save()

    def add_event(self, event_type: str, message: str):
        self.state["events"].append({
            "time": datetime.now().isoformat(),
            "type": event_type,
            "message": message
        })
        # Mirror to logger
        if event_type == "error":
            logger.error(message)
        elif event_type == "warning":
            logger.warning(message)
        else:
            logger.info(message)

    def finish_mission(self, status="completed"):
        self.state["status"] = status
        self.state["end_time"] = datetime.now().isoformat()
        self.state["current_agent"] = None
        self.save()

    def save(self):
        """
        [HARDENED] Atomic Write Pattern with Permission Lockdown.
        Writes to temp file, sets 600 permissions, then renames.
        """
        try:
            state_path = self.project_root / RUNTIME_STATE_FILE
            temp_dir = state_path.parent
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            # Create temp file
            with tempfile.NamedTemporaryFile('w', dir=str(temp_dir), delete=False, encoding='utf-8') as tf:
                json.dump(self.state, tf, indent=2, default=str)
                temp_name = tf.name
            
            # [HARDENED] Set strict permissions (Owner Read/Write only) before moving
            # This prevents other users on shared CI runners from reading potential sensitive logs
            os.chmod(temp_name, stat.S_IRUSR | stat.S_IWUSR)
            
            # Atomic replacement
            os.replace(temp_name, state_path)
            
        except Exception as e:
            logger.error(f"Failed to save runtime state (Atomic Write Failed): {e}")
            try:
                if 'temp_name' in locals() and os.path.exists(temp_name):
                    os.remove(temp_name)
            except: pass

    def _emergency_cleanup(self):
        """Ensure state is finalized even on unhandled exit."""
        if self.state["status"] == "running":
            self.finish_mission("terminated")

    def update_meta_learning(self, experience_data: Dict[str, Any]):
        """[INTEGRATION] Updates cognitive metrics for dashboard."""
        ml = self.state["meta_learning"]
        ml["enabled"] = True
        
        if "total_experiences" in experience_data:
            ml["total_experiences"] = experience_data["total_experiences"]
        
        if "strategy_weights" in experience_data:
            ml["strategy_weights"] = experience_data["strategy_weights"]
            
        if "experience" in experience_data:
            ml["recent_experiences"].insert(0, experience_data["experience"])
            ml["recent_experiences"] = ml["recent_experiences"][:5] # Keep last 5
            
        self.save()

# ============================================================================
# AUTONOMOUS DECISION ENGINE (From SSOT Protocol)
# ============================================================================

@dataclass
class ConfidenceScore:
    """Confidence score for autonomous healing decisions."""
    value: float  # 0.0 to 1.0
    reasoning: str
    factors: Dict[str, float] = field(default_factory=dict)
    
    @property
    def is_high_confidence(self) -> bool:
        return self.value >= 0.8
    
    @property
    def is_medium_confidence(self) -> bool:
        return 0.5 <= self.value < 0.8
    
    @property
    def is_low_confidence(self) -> bool:
        return self.value < 0.5

class AutonomousDecisionEngine:
    """Makes autonomous healing decisions based on confidence scores."""
    
    def __init__(self, enable_llm: bool = False):
        self.enable_llm = enable_llm
        self.decisions_made = []
        
    def calculate_healing_confidence(
        self,
        violations_count: int,
        violation_types: List[str],
        territory: str,
        historical_success_rate: float = 0.9
    ) -> ConfidenceScore:
        factors = {}
        
        # Factor 1: Violation count
        if violations_count == 0: factors['violation_count'] = 1.0
        elif violations_count <= 5: factors['violation_count'] = 0.9
        elif violations_count <= 10: factors['violation_count'] = 0.7
        elif violations_count <= 50: factors['violation_count'] = 0.5
        else: factors['violation_count'] = 0.3
        
        # Factor 2: Known violation types
        known_types = {'SHALLOW', 'DEEP', 'VOID', 'NAMING', 'IMPORT', 'HIERARCHY'}
        unknown_types = [v for v in violation_types if not any(k in str(v) for k in known_types)]
        factors['known_types'] = 1.0 if not unknown_types else 0.6
        
        # Factor 3: Historical success
        factors['historical_success'] = historical_success_rate
        
        # Factor 4: Complexity
        complex_territories = {'L5_safety', 'L3_orchestration', 'base_agents'}
        factors['territory_complexity'] = 0.7 if territory in complex_territories else 0.9
        
        weights = {'violation_count': 0.4, 'known_types': 0.2, 'historical_success': 0.2, 'territory_complexity': 0.2}
        confidence_value = sum(factors[k] * weights[k] for k in factors)
        
        reasoning = f"Violations: {violations_count}, Unknowns: {len(unknown_types)}, Historical: {historical_success_rate:.1%}"
        
        return ConfidenceScore(
            value=confidence_value,
            reasoning=reasoning,
            factors=factors
        )
    
    def should_proceed_with_healing(self, confidence: ConfidenceScore) -> Tuple[bool, str]:
        decision = {
            'confidence': confidence.value,
            'timestamp': datetime.now().isoformat()
        }
        
        if confidence.is_high_confidence:
            result = (True, f"HIGH CONFIDENCE ({confidence.value:.2f})")
        elif confidence.is_medium_confidence:
            result = (True, f"MEDIUM CONFIDENCE ({confidence.value:.2f})")
        else:
            if self.enable_llm:
                result = (True, f"LOW CONFIDENCE ({confidence.value:.2f}) - LLM Override")
            else:
                result = (False, f"LOW CONFIDENCE ({confidence.value:.2f}) - LLM Disabled")
        
        decision['decision'] = result[0]
        decision['reason'] = result[1]
        self.decisions_made.append(decision)
        
        return result

# ============================================================================
# AGENT DISCOVERY (From Canon Validator)
# ============================================================================

def list_available_agents(project_root: Path, dedupe: bool = True) -> List[Tuple[str, str]]:
    """Hybrid agent discovery: prefer cached JSON, fallback to live scan."""
    agents = []
    json_path = project_root / AGENT_DISCOVERY_JSON

    # Try Cache
    if json_path.exists():
        try:
            data = json.loads(json_path.read_text(encoding="utf-8"))
            for agent in data:
                if agent.get("class_name"):
                    # [HARDENED] Use pathlib for robust cross-platform path resolution
                    try:
                        raw_path = agent.get("path", "")
                        # Handle absolute or relative paths gracefully
                        if os.path.isabs(raw_path):
                            full_path = Path(raw_path)
                            rel_path = full_path.relative_to(project_root)
                        else:
                            rel_path = Path(raw_path)
                            
                        # Convert path parts to module dot notation
                        module_path = ".".join(rel_path.with_suffix("").parts)
                        agents.append((agent["class_name"], module_path))
                    except Exception as p_err:
                        # Log but don't crash on single bad path
                        logger.warning(f"Skipping malformed agent path '{raw_path}': {p_err}")
                        continue
            logger.info(f"Loaded {len(agents)} agents from cache")
        except Exception as e:
            logger.warning(f"Cache load failed: {e}")

    # Try Live Scan if empty
    if not agents:
        try:
            from agentic_core.utils.discovery.Full_Agent_discovery import discover_all_agents
            logger.info("Running live agent discovery...")
            discovery_data = discover_all_agents(project_root)
            for agent in discovery_data:
                if agent.get("class_name"):
                    # [HARDENED] Use pathlib for robust cross-platform path resolution
                    try:
                        raw_path = agent.get("path", "")
                        # Handle absolute or relative paths gracefully
                        if os.path.isabs(raw_path):
                            full_path = Path(raw_path)
                            rel_path = full_path.relative_to(project_root)
                        else:
                            rel_path = Path(raw_path)
                            
                        # Convert path parts to module dot notation
                        module_path = ".".join(rel_path.with_suffix("").parts)
                        agents.append((agent["class_name"], module_path))
                    except Exception as p_err:
                        # Log but don't crash on single bad path
                        logger.warning(f"Skipping malformed agent path '{raw_path}': {p_err}")
                        continue
            # Cache results
            json_path.write_text(json.dumps(discovery_data, indent=2), encoding="utf-8")
            logger.info(f"Discovered {len(agents)} agents (cached)")
        except ImportError:
            logger.warning("Live discovery unavailable - Full_Agent_discovery not found")
        except Exception as e:
            logger.error(f"Live discovery failed: {e}")

    if dedupe:
        agents = sorted(set(agents), key=lambda x: x[0])
    return agents

# ============================================================================
# EXECUTION PHASES (SSOT Logic + Canon Observability)
# ============================================================================

@with_retry(max_retries=3)
def execute_phase1_discovery(agents, territory, decision_engine, state_mgr):
    """PHASE 1: TERRITORIAL DISCOVERY (Retriable)"""
    return execute_phase1_discovery_impl(agents, territory, decision_engine, state_mgr)

def execute_phase1_discovery_impl(agents, territory, decision_engine, state_mgr):
    """PHASE 1: TERRITORIAL DISCOVERY - Implementation"""
    logger.info(f"=== PHASE 1: DISCOVERY - {territory} ===")
    
    state_mgr.update_agent("FilesystemSSOTReconcilerAgent", "L0 - Maintenance")
    
    reconciler = agents['reconciler'](project_root=Path.cwd())
    drift_report = reconciler.detect_root_drift()
    
    if drift_report is None:
        state_mgr.complete_agent("FilesystemSSOTReconcilerAgent", False, "Returned None")
        return None, None
        
    violations_count = len(drift_report.get('violations', []))
    state_mgr.complete_agent("FilesystemSSOTReconcilerAgent", True, f"Drift violations: {violations_count}")

    # Location Validation
    state_mgr.update_agent("LocationAgent", "L5 - Safety")
    location_validator = agents['location'](project_root=Path.cwd())
    
    territory_path = Path.cwd() / "agentic_core" / territory
    violations = []
    if territory_path.exists():
        files = list(territory_path.rglob("*.py"))
        logger.info(f"Scanning {len(files)} files in {territory}")
        violations = location_validator.run(files=files) or []
    else:
        logger.warning(f"Territory path does not exist: {territory_path}")
    
    confidence = decision_engine.calculate_healing_confidence(
        len(violations), 
        [str(v) for v in violations[:10]], 
        territory
    )
    state_mgr.state["compliance_scores"][territory] = confidence.value
    state_mgr.complete_agent("LocationAgent", True, f"Violations: {len(violations)} | Conf: {confidence.value:.2f}")
    
    return drift_report, violations

@with_retry(max_retries=3)
def execute_phase2_alignment(agents, territory, decision_engine, state_mgr):
    """PHASE 2: STRUCTURAL ALIGNMENT (Retriable)"""
    return execute_phase2_alignment_impl(agents, territory, decision_engine, state_mgr)

def execute_phase2_alignment_impl(agents, territory, decision_engine, state_mgr):
    """PHASE 2: STRUCTURAL ALIGNMENT - Implementation"""
    logger.info(f"=== PHASE 2: ALIGNMENT - {territory} ===")
    
    state_mgr.update_agent("HierarchyAgent", "L5 - Safety")
    hierarchy = agents['hierarchy'](project_root=Path.cwd())
    
    scan = hierarchy.scan_root_violations()
    violations = scan.get('violations_found', 0)
    
    if violations > 0:
        confidence = decision_engine.calculate_healing_confidence(violations, ['HIERARCHY'], territory)
        proceed, reason = decision_engine.should_proceed_with_healing(confidence)
        
        state_mgr.add_event("decision", f"Hierarchy Healing: {reason}")
        logger.info(f"Decision: {reason}")
        
        if proceed:
            res = hierarchy.heal_hierarchy(
                create_structure=True, 
                relocate_files=True,
                enforce_depth=True,
                purge_orphans=False
            )
            healed = res.get('total_healed', 0)
            state_mgr.complete_agent("HierarchyAgent", True, f"Healed: {healed}")
            return res
        else:
            state_mgr.complete_agent("HierarchyAgent", False, "Skipped - Low Confidence")
    else:
        state_mgr.complete_agent("HierarchyAgent", True, "No violations found")
    
    return None

@with_retry(max_retries=3)
def execute_phase3_validation(agents, territory, state_mgr):
    """PHASE 3: ARCHITECTURAL VALIDATION (Retriable)"""
    return execute_phase3_validation_impl(agents, territory, state_mgr)

def execute_phase3_validation_impl(agents, territory, state_mgr):
    """PHASE 3: ARCHITECTURAL VALIDATION - Implementation"""
    logger.info(f"=== PHASE 3: VALIDATION - {territory} ===")
    
    state_mgr.update_agent("ArchitectureGovernorAgent", "L5 - Safety")
    arch_gov = agents['arch_governor'](project_root=Path.cwd())
    gov_report = arch_gov.comprehensive_territory_audit(
        target_territories=[territory],
        check_layer_boundaries=True,
        check_naming_conventions=True
    )
    
    if gov_report is None:
        state_mgr.complete_agent("ArchitectureGovernorAgent", False, "Returned None")
        return None, None
    
    violations = len(gov_report.get('layer_violations', [])) + len(gov_report.get('naming_violations', []))
    state_mgr.complete_agent("ArchitectureGovernorAgent", True, f"Violations: {violations}")
    
    state_mgr.update_agent("SystemArchitectAgent", "L5 - Safety")
    sys_arch = agents['system_architect'](project_root=Path.cwd())
    arch_report = sys_arch.validate_core_architecture(f"agentic_core/{territory}")
    
    if arch_report is None:
        state_mgr.complete_agent("SystemArchitectAgent", False, "Returned None")
        return gov_report, None
    
    if not arch_report.get('imports_valid', True):
        circular = arch_report.get('circular_dependencies', [])
        state_mgr.add_event("error", f"Circular dependencies detected: {circular}")
        state_mgr.complete_agent("SystemArchitectAgent", False, "Circular Dependencies")
        return gov_report, arch_report
        
    state_mgr.complete_agent("SystemArchitectAgent", True, "Architecture Valid")
    return gov_report, arch_report

@with_retry(max_retries=3)
def execute_phase4_healing(agents, territory, gov_report, decision_engine, state_mgr):
    """PHASE 4: HEALING (Retriable)"""
    return execute_phase4_healing_impl(agents, territory, gov_report, decision_engine, state_mgr)

def execute_phase4_healing_impl(agents, territory, gov_report, decision_engine, state_mgr):
    """PHASE 4: HEALING - Implementation"""
    logger.info(f"=== PHASE 4: HEALING - {territory} ===")
    
    if gov_report is None:
        logger.warning("No governance report - skipping healing")
        return None
    
    arch_gov = agents['arch_governor'](project_root=Path.cwd())
    plan = arch_gov.generate_healing_plan(gov_report)
    
    if plan is None:
        logger.warning("No healing plan generated")
        return None
    
    if plan.get('requires_healing', False):
        fixes = len(plan.get('naming_fixes', []))
        confidence = decision_engine.calculate_healing_confidence(fixes, ['NAMING'], territory)
        proceed, reason = decision_engine.should_proceed_with_healing(confidence)
        
        state_mgr.add_event("decision", f"Arch Healing: {reason}")
        logger.info(f"Decision: {reason}")
        
        if proceed:
            state_mgr.update_agent("ArchitectureGovernorAgent", "HEALING MODE")
            res = arch_gov.execute_healing_plan(plan)
            success = res.get('success', False)
            state_mgr.complete_agent("ArchitectureGovernorAgent", success, f"Healed: {success}")
            return res
        else:
            state_mgr.add_event("warning", "Healing skipped - Low confidence")
            
    return None

@with_retry(max_retries=3)
def execute_phase5_final(agents, territory, state_mgr):
    """PHASE 5: CERTIFICATION (Retriable)"""
    return execute_phase5_final_impl(agents, territory, state_mgr)

def execute_phase5_final_impl(agents, territory, state_mgr):
    """PHASE 5: CERTIFICATION - Implementation"""
    logger.info(f"=== PHASE 5: CERTIFICATION - {territory} ===")
    
    state_mgr.update_agent("SovereignCertifier", "L5 - Compliance")
    
    cert = {
        'territory': territory,
        'timestamp': datetime.now().isoformat(),
        'status': 'COMPLIANT',
        'confidence_score': state_mgr.state["compliance_scores"].get(territory, 0.0),
        'agents_executed': [
            'FilesystemSSOTReconcilerAgent',
            'LocationAgent',
            'HierarchyAgent',
            'ArchitectureGovernorAgent',
            'SystemArchitectAgent'
        ]
    }
    
    logger.info(f"📜 CERTIFICATE ISSUED: {territory}")
    print(json.dumps(cert, indent=2))
    state_mgr.complete_agent("SovereignCertifier", True, "Certificate Issued")
    return cert

# ============================================================================
# L3 ORCHESTRATION INTEGRATION
# ============================================================================

def try_summon_orchestrator(project_root: Path, targets: List[str], execute: bool):
    """
    [INTEGRATION] Attempts to load L3 Orchestrator for smart execution.
    Returns: (success: bool, results: List|None)
    """
    try:
        # Dynamic import to avoid hard dependency on L3 (Graceful Degradation)
        from agentic_core.L3_orchestration.ConsolidatedOrchestratorAgent import get_consolidated_orchestrator
        from agentic_core.L5_safety.validators.FilesystemSSOTReconcilerAgent import FilesystemSSOTReconcilerAgent
        from agentic_core.L5_safety.validators.LocationAgent import LocationAgent
        from agentic_core.L5_safety.validators.HierarchyAgent import HierarchyAgent
        from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import ArchitectureGovernorAgent
        from agentic_core.L5_safety.validators.SystemArchitectAgent import SystemArchitectAgent
        
        orchestrator = get_consolidated_orchestrator(project_root)
        logger.info("🧠 L3 ORCHESTRATOR SUMMONED: Delegating command.")
        
        # Assemble Roster for L3
        active_roster = [
            ("LocationAgent", LocationAgent(project_root)),
            ("HierarchyAgent", HierarchyAgent(project_root)),
            ("ArchitectureGovernorAgent", ArchitectureGovernorAgent(project_root))
        ]
        
        mission_context = {
            "dry_run": not execute,
            "execute": execute,
            "domains": targets,
            "scan_mode": "leveraged"
        }
        
        # Execute via L3
        mission_results = orchestrator.run_mission(active_roster, mission_context)
        return True, mission_results
        
    except ImportError:
        logger.warning("L3 Orchestrator not found. Falling back to L5 iteration.")
        return False, None
    except Exception as e:
        logger.error(f"L3 Orchestration failed: {e}. Falling back to L5 iteration.")
        return False, None

# ============================================================================
# MAIN ORCHESTRATOR
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Unified Sovereign Compliance Protocol v4.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single territory scan (autonomous)
  python execute_ssot.py --territory prompt_governance
  
  # Multi-domain sweep
  python execute_ssot.py --domains
  
  # With LLM assistance
  python execute_ssot.py --territory L5_safety --enable-llm
  
  # List all discoverable agents
  python execute_ssot.py --list-agents
  
  # Run specific agent directly
  python execute_ssot.py --agent NamingAgent
        """
    )
    parser.add_argument("--territory", type=str, help="Specific territory to scan")
    parser.add_argument("--domains", action="store_true", help="Scan all major domains (Multi-Domain Mode)")
    parser.add_argument("--agent", type=str, help="Run specific agent directly")
    parser.add_argument("--list-agents", action="store_true", help="List discoverable agents")
    parser.add_argument("--enable-llm", action="store_true", help="Enable LLM for low-confidence decisions")
    parser.add_argument("--manual", action="store_true", help="Disable autonomous mode (legacy)")
    args = parser.parse_args()

    project_root = Path.cwd()
    
    # 1. Handle Discovery
    if args.list_agents:
        logger.info("DISCOVERABLE AGENTS:")
        agents_list = list_available_agents(project_root)
        for i, (name, path) in enumerate(agents_list, 1):
            print(f"   {i:3}. {name:<40} [{path}]")
        print(f"\nTotal: {len(agents_list)} agents")
        return

    # 2. Handle Direct Agent Invocation (Developer Mode)
    if args.agent:
        logger.info(f"DIRECT AGENT EXECUTION: {args.agent}")
        try:
            found = [x for x in list_available_agents(project_root) if args.agent.lower() in x[0].lower()]
            if not found:
                logger.error(f"Agent {args.agent} not found.")
                logger.info("Use --list-agents to see available agents")
                return
            
            name, path = found[0]
            logger.info(f"Found: {name} at {path}")
            
            module = importlib.import_module(path)
            
            # Try instantiation strategies
            agent = None
            if hasattr(module, f"get_{name.lower()}"):
                agent = getattr(module, f"get_{name.lower()}")(project_root)
            elif hasattr(module, name):
                agent_cls = getattr(module, name)
                agent = agent_cls(project_root=project_root)
            else:
                logger.error(f"Could not instantiate {name}")
                return
                
            logger.info(f"Running {name}...")
            
            # Prefer standard methods
            if hasattr(agent, "run"):
                result = agent.run()
            elif hasattr(agent, "scan_root_violations"):
                result = agent.scan_root_violations()
            elif hasattr(agent, "heal_repository"):
                result = agent.heal_repository(dry_run=True)
            else:
                result = "Agent instantiated but no standard run method found."
            
            logger.info(f"Result: {result}")
            
        except Exception as e:
            logger.error(f"Failed to run agent: {e}")
            traceback.print_exc()
        return

    # 3. Initialize Sovereign State & Agents
    state_mgr = RuntimeStateManager(project_root)
    decision_engine = AutonomousDecisionEngine(enable_llm=args.enable_llm)
    
    logger.info("🏛️ UNIFIED SOVEREIGN PROTOCOL STARTED")
    logger.info(f"  Mode: {'AUTONOMOUS' if not args.manual else 'MANUAL'}")
    logger.info(f"  LLM: {'ENABLED' if args.enable_llm else 'DISABLED'}")
    
    try:
        from agentic_core.L5_safety.validators.FilesystemSSOTReconcilerAgent import FilesystemSSOTReconcilerAgent
        from agentic_core.L5_safety.validators.LocationAgent import LocationAgent
        from agentic_core.L5_safety.validators.HierarchyAgent import HierarchyAgent
        from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import ArchitectureGovernorAgent
        from agentic_core.L5_safety.validators.SystemArchitectAgent import SystemArchitectAgent
        
        agents = {
            'reconciler': FilesystemSSOTReconcilerAgent,
            'location': LocationAgent,
            'hierarchy': HierarchyAgent,
            'arch_governor': ArchitectureGovernorAgent,
            'system_architect': SystemArchitectAgent
        }
        logger.info("✅ All agents loaded successfully")
    except ImportError as e:
        logger.critical(f"Failed to load Sovereign Agents: {e}")
        sys.exit(1)

    # 4. Determine Targets
    targets = []
    mission_mode = ""
    if args.territory:
        targets = [args.territory]
        mission_mode = f"Territory Scan: {args.territory}"
    elif args.domains:
        # Multi-domain sweep
        targets = ["prompt_governance", "L5_safety", "L3_orchestration", "L2_execution", "L0_maintenance"]
        mission_mode = "Multi-Domain Sweep (L3 Attempt)"
    else:
        targets = ["prompt_governance"]  # Default safe target
        mission_mode = "Default Scan"

    # 5. Execute Mission
    # [HARDENED] Wrap entire autonomous execution in NonInteractiveGuard
    is_autonomous = not args.manual
    
    try:
        with NonInteractiveGuard(active=is_autonomous):
            state_mgr.start_mission(f"Unified Protocol: {mission_mode}", [f"{t}" for t in targets])
            
            # [INTEGRATION] Attempt L3 Smart Orchestration first
            if args.domains:
                l3_success, l3_results = try_summon_orchestrator(project_root, targets, execute=is_autonomous)
                if l3_success:
                    state_mgr.update_meta_learning({"total_experiences": 1, "experience": "L3 Mission Complete"})
                    state_mgr.finish_mission("completed")
                    logger.info("🎉 L3 MISSION COMPLETED")
                    return l3_results
            
            # Fallback to standard L5 Iteration (The original loop)
            results = []
            for territory in targets:
                logger.info(f"\n{'='*60}")
                logger.info(f"🚀 PROCESSING TERRITORY: {territory}")
                logger.info(f"{'='*60}")
                state_mgr.add_event("domain_start", f"Entering Domain: {territory}")
                
                try:
                    # Phase 1
                    p1_drift, p1_loc = execute_phase1_discovery(agents, territory, decision_engine, state_mgr)
                    
                    if p1_drift is not None:
                        # Phase 2
                        execute_phase2_alignment(agents, territory, decision_engine, state_mgr)
                        # Phase 3
                        gov, arch = execute_phase3_validation(agents, territory, state_mgr)
                        # Phase 4
                        execute_phase4_healing(agents, territory, gov, decision_engine, state_mgr)
                        # Phase 5
                        cert = execute_phase5_final(agents, territory, state_mgr)
                        results.append(cert)
                    else:
                        logger.error(f"Phase 1 failed for {territory} - skipping")
                        state_mgr.add_event("error", f"Phase 1 failure in {territory}")
                        
                except RuntimeError as re:
                    # Catch the NonInteractiveGuard trap specifically
                    if "Interactive prompt blocked" in str(re):
                        logger.critical(f"🛑 BLOCKED INTERACTIVE PROMPT in {territory}: {re}")
                        state_mgr.add_event("error", f"Blocked Prompt in {territory}")
                        continue # Skip this territory, try next
                    raise re
                except Exception as e:
                    logger.error(f"❌ Protocol crashed on {territory}: {e}")
                    traceback.print_exc()
                    state_mgr.add_event("error", f"Crash in {territory}: {str(e)[:200]}")
                    if is_autonomous:
                        continue
                    else:
                        state_mgr.finish_mission(status="error")
                        sys.exit(1)
                        
            # Only mark completed if we got here
            state_mgr.finish_mission(status="completed")
            
            # Final Summary
            logger.info(f"\n{'='*60}")
            logger.info("🎉 UNIFIED PROTOCOL COMPLETED")
            logger.info(f"{'='*60}")
            logger.info(f"Territories processed: {len(results)}/{len(targets)}")
            logger.info(f"Decisions made: {len(decision_engine.decisions_made)}")
            
            # Decision breakdown
            high_conf = sum(1 for d in decision_engine.decisions_made if d['confidence'] >= 0.8)
            med_conf = sum(1 for d in decision_engine.decisions_made if 0.5 <= d['confidence'] < 0.8)
            low_conf = sum(1 for d in decision_engine.decisions_made if d['confidence'] < 0.5)
            logger.info(f"  High confidence: {high_conf}, Medium: {med_conf}, Low: {low_conf}")
            
            return results

    except Exception as fatal_e:
        # Catch-all for top-level crashes (e.g., initialization failure)
        logger.critical(f"🔥 FATAL PROTOCOL ERROR: {fatal_e}")
        traceback.print_exc()
        state_mgr.finish_mission(status="fatal_error")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
        sys.exit(0)
    except KeyboardInterrupt:
        logger.warning("⏸️ Protocol interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.critical(f"💥 Protocol failed: {e}")
        traceback.print_exc()
        sys.exit(1)
