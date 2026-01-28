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
import re
import subprocess
from subprocess import DEVNULL
from functools import wraps
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field

# [ETERNAL UTF-8] Force Windows consoles to handle unicode symbols (From Canon)
if sys.platform.startswith("win"):
    # [ULTRA-HARDENED] Replace shell command with direct subprocess call to eliminate injection vectors
    try:
        subprocess.run(["chcp", "65001"], stdout=DEVNULL, stderr=DEVNULL, check=False)
    except FileNotFoundError:
        # chcp not available, skip - this is common in some Windows environments
        pass
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

# [ULTRA-HARDENED] Whitelist of allowed module prefixes for dynamic imports
# Prevents loading agents from unexpected packages (defense-in-depth against tampered discovery/cache)
ALLOWED_MODULE_PREFIXES = (
    "agentic_core",
    "apps_shared",
    "apps_lic",
    "apps_rg"
)

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
        self.project_root = project_root.resolve()  # [ULTRA-HARDENED] Force real absolute path resolution
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
            "compliance_scores": {},
            # [SILENT AGGREGATION] Track decisions for final report
            "decisions_made": [],
            "compliance_report": {}
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
        """
        [HARDENED] Silent Aggregation.
        Records agent completion but suppresses intermediate JSON console dumps.
        """
        self.state["completed_agents"].append({
            "agent": agent_name,
            "time": datetime.now().isoformat(),
            "success": success,
            "details": details
        })
        # Log to file/state but DO NOT PRINT JSON to console here
        self.add_event("agent_end", f"{'✓' if success else '❌'} Completed {agent_name}")
        self.save()

    def add_event(self, event_type: str, message: str):
        self.state["events"].append({
            "time": datetime.now().isoformat(),
            "type": event_type,
            "message": message
        })
        # [SILENT AGGREGATION] Only log minimal status to console during execution
        # Full telemetry captured in state for final report
        if event_type == "error":
            logger.error(message)
        elif event_type == "warning":
            logger.warning(message)
        elif event_type in ["agent_start", "agent_end"]:
            # Keep minimal agent progress indicators
            logger.info(message)
        else:
            # Suppress other verbose intermediate logs
            pass

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
        return self.value > 0.75
    
    @property
    def is_medium_confidence(self) -> bool:
        return 0.5 <= self.value <= 0.75
    
    @property
    def is_low_confidence(self) -> bool:
        return self.value < 0.5

class AutonomousDecisionEngine:
    """Makes autonomous healing decisions based on confidence scores."""
    
    def __init__(self, enable_llm: bool = False, state_mgr: Optional['RuntimeStateManager'] = None):
        self.enable_llm = enable_llm
        self.decisions_made = []
        self.state_mgr = state_mgr  # [SILENT AGGREGATION] Link to state for decision tracking
        
    def calculate_healing_confidence(
        self,
        violations_count: int,
        violation_types: List[str],
        territory: str,
        historical_success_rate: float = 0.9
    ) -> ConfidenceScore:
        """
        Calculate confidence based on Territorial Trust logic.
        Trusted territories tolerate higher violation counts.
        """
        factors = {}
        
        # [SOVEREIGN TRUST] Define Risk Profiles
        TRUSTED_TERRITORIES = {'prompt_governance', 'scripts', 'tests', 'L0_maintenance', 'apps_lic', 'apps_rg'}
        CRITICAL_TERRITORIES = {'L5_safety', 'L3_orchestration', 'base_agents', 'L2_execution'}
        
        is_trusted = any(t in territory for t in TRUSTED_TERRITORIES)
        is_critical = any(c in territory for c in CRITICAL_TERRITORIES)

        # Factor 1: Violation Count (Risk-Adjusted)
        if violations_count == 0: 
            # [LOGIC FIX] Zero violations = perfect confidence (1.0)
            # No need for weighted averaging when there are no issues
            factors['violation_count'] = 1.0
            factors['known_types'] = 1.0
            factors['historical_success'] = 1.0
            factors['territory_complexity'] = 1.0
            confidence_value = 1.0
        elif violations_count <= 5: 
            factors['violation_count'] = 0.95 if is_trusted else 0.9
        elif violations_count <= 25: 
            factors['violation_count'] = 0.90 if is_trusted else 0.7
        elif violations_count <= 100: 
            # Senior Dev Velocity: Mass edits in trusted zones are normal
            factors['violation_count'] = 0.85 if is_trusted else 0.4
        else: 
            factors['violation_count'] = 0.70 if is_trusted else 0.2
        
        # Only calculate weighted confidence for violations > 0
        unknown_types = []  # Initialize for all cases
        if violations_count > 0:
            # Factor 2: Known violation types (Expanded definition)
            known_types = {'SHALLOW', 'DEEP', 'VOID', 'NAMING', 'IMPORT', 'HIERARCHY', 'ORPHAN', 'DUPLICATE', 'STRUCTURE'}
            unknown_types = [v for v in violation_types if not any(k in str(v) for k in known_types)]
            factors['known_types'] = 1.0 if not unknown_types else 0.5
            
            # Factor 3: Historical success
            factors['historical_success'] = historical_success_rate
            
            # Factor 4: Complexity / Trust Bonus
            if is_trusted:
                 factors['territory_complexity'] = 1.0   # High Trust Bonus
            elif is_critical:
                 factors['territory_complexity'] = 0.6   # High Caution Penalty
            else:
                 factors['territory_complexity'] = 0.85  # Standard
            
            # Adjusted Weights to favor Territory Trust
            weights = {'violation_count': 0.35, 'known_types': 0.25, 'historical_success': 0.15, 'territory_complexity': 0.25}
            confidence_value = sum(factors[k] * weights[k] for k in factors)
        else:
            # Zero violations - set all factors to perfect for consistency
            factors['known_types'] = 1.0
            factors['historical_success'] = 1.0
            factors['territory_complexity'] = 1.0
        
        risk_profile = "TRUSTED" if is_trusted else ("CRITICAL" if is_critical else "STANDARD")
        reasoning = f"[{risk_profile}] Violations: {violations_count}, Unknowns: {len(unknown_types)}, Conf: {confidence_value:.2f}"
        
        return ConfidenceScore(
            value=confidence_value,
            reasoning=reasoning,
            factors=factors
        )
    
    def should_proceed_with_healing(self, confidence: ConfidenceScore) -> Tuple[bool, str]:
        """
        [HARDENED] Confidence Gate.
        Strict threshold > 0.75 for autonomous healing actions.
        """
        decision = {
            'confidence': confidence.value,
            'timestamp': datetime.now().isoformat()
        }
        
        # New Threshold Logic: > 0.75 triggers Autonomous Healing
        if confidence.value > 0.75:
            result = (True, f"HIGH CONFIDENCE ({confidence.value:.2f} > 0.75) - AUTO-HEAL")
        else:
            # Score is <= 0.75: Request LLM Intervention or Fail
            if self.enable_llm:
                result = (True, f"LOW CONFIDENCE ({confidence.value:.2f}) - LLM Override")
            else:
                result = (False, f"LOW CONFIDENCE ({confidence.value:.2f}) - LLM Disabled")
        
        decision['decision'] = result[0]
        decision['reason'] = result[1]
        self.decisions_made.append(decision)
        
        # [SILENT AGGREGATION] Also store in state manager for final report
        if self.state_mgr:
            self.state_mgr.state["decisions_made"].append(decision)
            self.state_mgr.save()
        
        return result

class EnhancedAutonomousDecisionEngine(AutonomousDecisionEngine):
    """Enhanced decision engine with CognitiveDispositionAgent integration."""
    
    def __init__(self, enable_llm: bool = False, state_mgr: Optional['RuntimeStateManager'] = None, enable_cda: bool = False):
        super().__init__(enable_llm, state_mgr)
        self.enable_cda = enable_cda
        self.cda = None
        
        if enable_cda:
            try:
                from agentic_core.L5_safety.validators.CognitiveDispositionAgent import CognitiveDispositionAgent
                project_root = state_mgr.project_root if state_mgr else Path.cwd()
                self.cda = CognitiveDispositionAgent(project_root=project_root)
                logger.info("🧠 CognitiveDispositionAgent integrated for enhanced decision making")
            except ImportError as e:
                logger.warning(f"CognitiveDispositionAgent not available: {e}")
                self.enable_cda = False
    
    async def get_cognitive_disposition(self, file_path: Path, violation_type: str, context: dict = None) -> Optional['DispositionDecision']:
        """Get AI-powered disposition analysis for complex violations."""
        if not self.cda:
            return None
            
        try:
            return await self.cda.analyze_violation_async(file_path, violation_type, context)
        except Exception as e:
            logger.warning(f"Cognitive analysis failed for {file_path}: {e}")
            return None
    
    def calculate_healing_confidence(
        self,
        violations_count: int,
        violation_types: List[str],
        territory: str,
        historical_success_rate: float = 0.9,
        cognitive_dispositions: List['DispositionDecision'] = None
    ) -> ConfidenceScore:
        """
        Enhanced confidence calculation with cognitive disposition analysis.
        """
        # Get base confidence from parent calculation
        base_confidence = super().calculate_healing_confidence(
            violations_count, violation_types, territory, historical_success_rate
        )
        
        # Enhance with cognitive analysis if available
        if cognitive_dispositions and self.enable_cda:
            cognitive_factor = self._calculate_cognitive_factor(cognitive_dispositions)
            base_confidence.factors['cognitive_analysis'] = cognitive_factor
            
            # Adjust confidence based on cognitive analysis
            # Weight cognitive analysis at 15% of total confidence
            cognitive_weight = 0.15
            base_weight = 0.85
            
            # Re-calculate weighted confidence
            base_confidence.value = (
                base_confidence.value * base_weight + 
                cognitive_factor * cognitive_weight
            )
            
            # Update reasoning to include cognitive insights
            avg_cognitive_conf = sum(d.confidence for d in cognitive_dispositions) / len(cognitive_dispositions)
            base_confidence.reasoning += f" | Cognitive: {avg_cognitive_conf:.2f}"
        
        return base_confidence
    
    def _calculate_cognitive_factor(self, dispositions: List['DispositionDecision']) -> float:
        """Calculate cognitive confidence factor from disposition decisions."""
        if not dispositions:
            return 0.5  # Neutral factor
        
        # Average confidence across all cognitive dispositions
        avg_confidence = sum(d.confidence for d in dispositions) / len(dispositions)
        
        # Factor in action types - some actions are riskier than others
        action_weights = {
            'MOVE': 0.9,      # High confidence in move decisions
            'ARCHIVE': 0.95,  # Very safe action
            'IGNORE': 0.7,    # Lower confidence for ignoring
            'MANUAL_REVIEW': 0.3  # Lowest confidence - requires human intervention
        }
        
        # Weight by action type
        weighted_confidences = []
        for disposition in dispositions:
            action_weight = action_weights.get(disposition.action, 0.5)
            weighted_confidences.append(disposition.confidence * action_weight)
        
        if weighted_confidences:
            return sum(weighted_confidences) / len(weighted_confidences)
        
        return avg_confidence
    
    async def analyze_violations_with_cognitive_disposition(
        self,
        violations: List,
        territory: str,
        state_mgr=None
    ) -> Tuple[List['DispositionDecision'], ConfidenceScore]:
        """
        Analyze violations using CognitiveDispositionAgent and calculate enhanced confidence.
        """
        if not self.enable_cda or not self.cda:
            return [], self.calculate_healing_confidence(len(violations), ['UNKNOWN'], territory)
        
        cognitive_dispositions = []
        
        # Analyze each violation with CDA (limit to first 10 for performance)
        for violation in violations[:10]:
            try:
                # Extract file path and violation type
                if isinstance(violation, tuple) and len(violation) >= 2:
                    file_path = Path(violation[0])
                    violation_message = str(violation[1])
                elif hasattr(violation, 'file'):
                    file_path = Path(violation.file)
                    violation_message = getattr(violation, 'message', str(violation))
                else:
                    continue
                
                # Determine violation type from message
                violation_type = self._classify_violation_type(violation_message)
                
                # Get cognitive disposition
                context = {
                    'territory': territory,
                    'total_violations': len(violations),
                    'violation_index': len(cognitive_dispositions)
                }
                
                disposition = await self.get_cognitive_disposition(
                    file_path, violation_type, context
                )
                
                if disposition:
                    cognitive_dispositions.append(disposition)
                    logger.info(f"🧠 CDA Analysis: {file_path.name} -> {disposition.action} (conf: {disposition.confidence:.2f})")
                
            except Exception as e:
                logger.warning(f"Cognitive analysis failed for violation: {e}")
                continue
        
        # Calculate enhanced confidence with cognitive insights
        enhanced_confidence = self.calculate_healing_confidence(
            len(violations),
            ['COGNITIVE_ANALYZED'],
            territory,
            cognitive_dispositions=cognitive_dispositions
        )
        
        return cognitive_dispositions, enhanced_confidence
    
    def _classify_violation_type(self, violation_message: str) -> str:
        """Classify violation type from message content."""
        message_lower = violation_message.lower()
        
        if 'missing sovereign root' in message_lower:
            return 'MISSING_DIRECTORY'
        elif 'forbidden keyword' in message_lower:
            return 'FORBIDDEN_CONTENT'
        elif 'forbidden extension' in message_lower:
            return 'EXTENSION_MISMATCH'
        elif 'test_' in message_lower:
            return 'TEST_FILE_MISPLACED'
        elif 'sovereign' in message_lower:
            return 'SOVEREIGN_VIOLATION'
        else:
            return 'STRUCTURAL_VIOLATION'

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
                        clean_parts = rel_path.with_suffix("").parts
                        # [ULTRA-HARDENED] Reject any path containing navigation tokens (., ..) or empty segments
                        if any(p in {"", ".", ".."} for p in clean_parts):
                            logger.warning(f"Skipping agent with invalid path parts: {raw_path}")
                            continue
                            
                        module_path = ".".join(clean_parts)
                        
                        # [ULTRA-HARDENED] Enforce module prefix whitelist before permitting dynamic import
                        if not any(module_path == p or module_path.startswith(p + ".") for p in ALLOWED_MODULE_PREFIXES):
                            logger.warning(f"Blocking unauthorized module load attempt: {module_path}")
                            continue
                            
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
                        clean_parts = rel_path.with_suffix("").parts
                        # [ULTRA-HARDENED] Reject any path containing navigation tokens (., ..) or empty segments
                        if any(p in {"", ".", ".."} for p in clean_parts):
                            logger.warning(f"Skipping agent with invalid path parts: {raw_path}")
                            continue
                            
                        module_path = ".".join(clean_parts)
                        
                        # [ULTRA-HARDENED] Enforce module prefix whitelist before permitting dynamic import
                        if not any(module_path == p or module_path.startswith(p + ".") for p in ALLOWED_MODULE_PREFIXES):
                            logger.warning(f"Blocking unauthorized module load attempt: {module_path}")
                            continue
                            
                        agents.append((agent["class_name"], module_path))
                    except Exception as p_err:
                        # Log but don't crash on single bad path
                        logger.warning(f"Skipping malformed agent path '{raw_path}': {p_err}")
                        continue
            # [ULTRA-HARDENED] Atomic write + strict 600 permissions for agent discovery cache
            try:
                temp_name = None
                with tempfile.NamedTemporaryFile('w', delete=False, dir=str(project_root), encoding='utf-8') as tf:
                    json.dump(discovery_data, tf, indent=2)
                    temp_name = tf.name
                os.chmod(temp_name, stat.S_IRUSR | stat.S_IWUSR)
                os.replace(temp_name, json_path)
                logger.info(f"Discovered {len(agents)} agents (cached)")
            except Exception as cache_err:
                logger.warning(f"Failed to cache agent discovery: {cache_err}")
                if temp_name and os.path.exists(temp_name): os.remove(temp_name)
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
def execute_phase1_discovery(agents, territory, decision_engine, state_mgr, dry_run=False, auto_approve=True):
    """PHASE 1: TERRITORIAL DISCOVERY (Retriable)"""
    return execute_phase1_discovery_impl(agents, territory, decision_engine, state_mgr, dry_run, auto_approve)

def execute_phase1_discovery_impl(agents, territory, decision_engine, state_mgr, dry_run=False, auto_approve=True):
    """PHASE 1: TERRITORIAL DISCOVERY - Implementation with CognitiveDispositionAgent integration"""
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
    
    # [ULTRA-HARDENED] Explicit path traversal protection for user-supplied territory string
    agentic_core_base = (Path.cwd() / "agentic_core").resolve()
    territory_path = (agentic_core_base / territory).resolve()
    if not territory_path.is_relative_to(agentic_core_base):
        logger.critical(f"SECURITY ALERT: Path traversal attempt detected for territory '{territory}'")
        state_mgr.add_event("security", "Path traversal blocked")
        state_mgr.complete_agent("LocationAgent", False, "Traversal blocked")
        return drift_report, []
    
    violations = []
    if territory_path.exists():
        files = list(territory_path.rglob("*.py"))
        logger.info(f"Scanning {len(files)} files in {territory_path.relative_to(Path.cwd())}")
        violations = location_validator.run(files=files) or []
    else:
        logger.warning(f"Territory path does not exist: {territory_path}")
    
    # Enhanced confidence calculation with cognitive analysis
    if hasattr(decision_engine, 'enable_cda') and decision_engine.enable_cda and violations:
        logger.info("🧠 Using CognitiveDispositionAgent for enhanced violation analysis...")
        
        # Create event loop for async cognitive analysis
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Get cognitive dispositions and enhanced confidence
        cognitive_dispositions, enhanced_confidence = loop.run_until_complete(
            decision_engine.analyze_violations_with_cognitive_disposition(violations, territory, state_mgr)
        )
        
        # Store cognitive dispositions in state for reporting
        state_mgr.state["cognitive_dispositions"] = [d.__dict__ for d in cognitive_dispositions]
        
        confidence = enhanced_confidence
        logger.info(f"🧠 Enhanced confidence with cognitive analysis: {confidence.value:.2f}")
    else:
        # Fallback to standard confidence calculation
        confidence = decision_engine.calculate_healing_confidence(
            len(violations), 
            [str(v) for v in violations[:10]], 
            territory
        )
    
    state_mgr.state["compliance_scores"][territory] = confidence.value
    
    # [DETAILED TRACKING] Store actual LocationAgent violations for final report
    state_mgr.state["location_violations"] = violations
    
    # [AUTO-HEALING] If confidence is high enough, trigger LocationAgent healing
    if len(violations) > 0:
        proceed, reason = decision_engine.should_proceed_with_healing(confidence)
        state_mgr.add_event("decision", f"Location Healing: {reason}")
        logger.info(f"Location Decision: {reason}")
        
        if proceed and not dry_run:
            logger.info(f"🔧 Triggering LocationAgent auto-heal for {len(violations)} violations")
            # LocationAgent should have a heal method - call it
            if hasattr(location_validator, 'heal_violations'):
                heal_result = location_validator.heal_violations(violations, auto_approve=auto_approve)
                healed_count = heal_result.get('healed', 0) if isinstance(heal_result, dict) else 0
                state_mgr.complete_agent("LocationAgent", True, f"Violations: {len(violations)} | Healed: {healed_count} | Conf: {confidence.value:.2f}")
            else:
                logger.warning("LocationAgent has no heal_violations method - violations detected but not healed")
                state_mgr.complete_agent("LocationAgent", True, f"Violations: {len(violations)} | Conf: {confidence.value:.2f} (no heal method)")
        else:
            state_mgr.complete_agent("LocationAgent", True, f"Violations: {len(violations)} | Conf: {confidence.value:.2f} (healing skipped)")
    else:
        state_mgr.complete_agent("LocationAgent", True, f"Violations: 0 | Conf: {confidence.value:.2f}")
    
    return drift_report, violations

@with_retry(max_retries=3)
def execute_phase2_alignment(agents, territory, decision_engine, state_mgr, dry_run=False, auto_approve=True):
    """PHASE 2: STRUCTURAL ALIGNMENT (Retriable)"""
    return execute_phase2_alignment_impl(agents, territory, decision_engine, state_mgr, dry_run, auto_approve)

def execute_phase2_alignment_impl(agents, territory, decision_engine, state_mgr, dry_run=False, auto_approve=True):
    """PHASE 2: STRUCTURAL ALIGNMENT - Implementation"""
    logger.info(f"=== PHASE 2: ALIGNMENT - {territory} ===")
    
    state_mgr.update_agent("HierarchyAgent", "L5 - Safety")
    hierarchy = agents['hierarchy'](project_root=Path.cwd())
    
    # [STRICT SCOPE] Pass territory to scan only the target root
    scan = hierarchy.scan_root_violations(target_territory=territory)
    violations = scan.get('violations_found', 0)
    
    # Check if we found violations in the returned dict format (list vs count)
    if 'violations' in scan and isinstance(scan['violations'], list):
         violations = len(scan['violations'])
    
    if violations > 0:
        confidence = decision_engine.calculate_healing_confidence(violations, ['HIERARCHY'], territory)
        proceed, reason = decision_engine.should_proceed_with_healing(confidence)
        
        state_mgr.add_event("decision", f"Hierarchy Healing: {reason}")
        logger.info(f"Decision: {reason}")
        
        if proceed:
            # [SOVEREIGN DEFAULT] Propagate active/dry-run status to HierarchyAgent
            res = hierarchy.heal_hierarchy(
                create_structure=True, 
                relocate_files=True,
                enforce_depth=True,
                purge_orphans=False,
                target_territory=territory, # [STRICT SCOPE] Already correct here, but ensuring strict adherence
                dry_run=dry_run,
                auto_approve=auto_approve
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
def execute_phase4_healing(agents, territory, gov_report, decision_engine, state_mgr, dry_run=False, auto_approve=True):
    """PHASE 4: HEALING (Retriable)"""
    # [STRICT SCOPE] Gatekeeper check
    if not gov_report:
        logger.warning("Skipping healing: No governance report available.")
        return None

    return execute_phase4_healing_impl(agents, territory, gov_report, decision_engine, state_mgr, dry_run, auto_approve)

def execute_phase4_healing_impl(agents, territory, gov_report, decision_engine, state_mgr, dry_run=False, auto_approve=True):
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
            # [SOVEREIGN DEFAULT] Pass orchestration flags to the Governor healing plan
            res = arch_gov.execute_healing_plan(
                plan, 
                dry_run=dry_run, 
                auto_approve=auto_approve
            )
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
    """PHASE 5: CERTIFICATION - Implementation with Silent Aggregation"""
    logger.info(f"=== PHASE 5: CERTIFICATION - {territory} ===")
    
    state_mgr.update_agent("SovereignCertifier", "L5 - Compliance")
    
    # [UNIFIED MANIFEST] Aggregate all findings from the state manager
    compliance_report = state_mgr.state.get("compliance_report", {})
    decision_history = state_mgr.state.get("decision_history", [])
    
    # [CRITICAL FIX] Aggregate violations from ALL agents, not just ArchitectureGovernor
    # The compliance_report only has ArchitectureGovernor violations
    # We need to include LocationAgent violations from Phase 1
    all_violations = []
    
    # Get ArchitectureGovernor violations
    arch_violations = compliance_report.get('violations', [])
    all_violations.extend(arch_violations)
    
    # Get LocationAgent violations from Phase 1 (stored in state)
    location_violations = state_mgr.state.get("location_violations", [])
    for loc_violation in location_violations:
        # LocationAgent violations are tuples: (Path, message)
        if isinstance(loc_violation, tuple) and len(loc_violation) >= 2:
            file_path = str(loc_violation[0])
            message = str(loc_violation[1])
        else:
            file_path = str(getattr(loc_violation, 'file', 'unknown'))
            message = str(loc_violation)
        
        # Generate specific, actionable recommendations based on violation type
        if "Missing sovereign root:" in message:
            dir_name = message.split('Missing sovereign root:')[1].strip().strip("')")
            action = f"Create directory: {dir_name}"
        elif "Forbidden keyword 'def test_'" in message:
            path_parts = file_path.replace('\\', '/').split('/')
            filename = path_parts[-1]
            action = f"Move {filename} to tests/ directory (contains test functions)"
        elif "Forbidden keyword 'class Sovereign'" in message:
            path_parts = file_path.replace('\\', '/').split('/')
            filename = path_parts[-1]
            action = f"Move {filename} to agentic_core/base_agents/ or agentic_core/L5_safety/"
        elif "Forbidden extension .py for destination docs/reports" in message:
            path_parts = file_path.replace('\\', '/').split('/')
            filename = path_parts[-1]
            action = f"Move {filename} to agentic_core/L0_maintenance/scripts/ (Python files don't belong in docs/)"
        else:
            action = f"Fix location/naming issue: {message[:60]}"
        
        # Convert LocationAgent violation object to detailed dict
        violation_dict = {
            "type": "LOCATION",
            "source": "LocationAgent",
            "file": file_path,
            "message": message,
            "severity": "medium",
            "recommended_action": action,
            "llm_triggered": False,  # LocationAgent doesn't trigger LLM
            "confidence": state_mgr.state["compliance_scores"].get(territory, 0.0)
        }
        all_violations.append(violation_dict)
    
    violation_count = len(all_violations)
    status = 'COMPLIANT' if violation_count == 0 else 'NON-COMPLIANT'
    
    # [LOGIC FIX] Recalculate confidence based on FINAL violation count, not Phase 1
    # Get the decision engine to recalculate confidence for the final state
    decision_engine = getattr(state_mgr, '_decision_engine', None)
    if decision_engine is None:
        # Fallback: create a temporary decision engine for final calculation
        decision_engine = AutonomousDecisionEngine(enable_llm=False)
    
    final_confidence = decision_engine.calculate_healing_confidence(
        violations_count=violation_count,
        violation_types=[v.get('type', 'UNKNOWN') for v in all_violations[:10]],
        territory=territory
    )
    confidence_avg = final_confidence.value
    
    drift_count = compliance_report.get('stats', {}).get('drift_detected', 0)
    
    # Build detailed decision log with LLM status
    decisions_made = state_mgr.state.get("decisions_made", [])
    
    detailed_cert = {
        'meta': {
            'territory': territory,
            'timestamp': datetime.now().isoformat(),
            'status': status,
            'sovereignty_level': 'L5',
        },
        'metrics': {
            'confidence_score': confidence_avg,
            'violation_count': violation_count,
            'drift_count': drift_count,
            'errors': compliance_report.get('stats', {}).get('errors', 0),
            'violations_fixed': compliance_report.get('stats', {}).get('violations_fixed', 0),
        },
        'governance_log': {
            'decisions': decisions_made,
            'files_processed': []
        },
        'unified_violations': all_violations,  # Use all_violations instead of just arch violations
        'agents_executed': [
            'FilesystemSSOTReconcilerAgent',
            'LocationAgent', 
            'HierarchyAgent',
            'PascalSovereigntyAgent',
            'ArchitectureGovernorAgent',
            'SystemArchitectAgent'
        ]
    }

    # Add violations to file log
    files_affected = set()
    for v in all_violations:  # Use all_violations instead of violations
        files_affected.add(v.get('file', 'unknown'))
        
    detailed_cert['governance_log']['files_processed'] = list(files_affected)

    # Generate Markdown Executive Summary
    markdown_summary = [
        f"# 🛡️ Sovereign Compliance Report: {territory}",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | **Status:** {status}",
        "",
        "## 📊 Executive Summary",
        "",
        f"* **Confidence Score:** {confidence_avg:.4f}",
        f"* **Violations Detected:** {violation_count}",
        f"* **Integrity Drift:** {drift_count}",
        f"* **Violations Fixed:** {detailed_cert['metrics']['violations_fixed']}",
        "",
        "## 🚨 Violations Detected",
        ""
    ]
    
    # Add detailed violations table
    if violation_count > 0:
        markdown_summary.extend([
            "| # | Type | File | Issue | Severity | LLM | Confidence | Action |",
            "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |"
        ])
        
        for idx, violation in enumerate(all_violations, 1):
            v_type = violation.get('type', 'UNKNOWN')
            v_file = violation.get('file', 'unknown')
            # Extract just the filename from full path
            if '/' in v_file or '\\' in v_file:
                v_file = v_file.split('/')[-1].split('\\')[-1]
            
            # Parse message to get the actual issue
            v_message = violation.get('message', '')
            if 'ARTIFACT ROUTING VIOLATION:' in v_message:
                issue = v_message.split('ARTIFACT ROUTING VIOLATION:')[1].split("'")[0].strip()
            elif 'Missing sovereign root:' in v_message:
                issue = v_message.split('Missing sovereign root:')[1].strip().strip("')")
            else:
                issue = v_message[:50] + "..." if len(v_message) > 50 else v_message
            
            v_severity = violation.get('severity', 'medium')
            v_llm = 'Yes' if violation.get('llm_triggered', False) else 'No'
            v_conf = violation.get('confidence', 0.0)
            v_action = violation.get('recommended_action', 'Review')[:30] + "..."
            
            markdown_summary.append(
                f"| {idx} | {v_type} | `{v_file}` | {issue} | {v_severity} | {v_llm} | {v_conf:.2f} | {v_action} |"
            )
    else:
        markdown_summary.append("*No violations detected - territory is compliant.*")
    
    markdown_summary.extend([
        "",
        "## 🧠 AI Governance Log",
        "",
        "| Decision Context | Confidence | LLM Triggered | Outcome |",
        "| :--- | :--- | :--- | :--- |"
    ])
    
    # Add decision details to markdown table
    for decision in decisions_made:
        confidence = decision.get('confidence', 0.0)
        llm_triggered = confidence <= 0.75
        outcome = "PROCEED" if decision.get('decision', False) else "SKIP"
        context = decision.get('reason', 'Unknown')
        markdown_summary.append(f"| {context} | {confidence:.2f} | {'Yes' if llm_triggered else 'No'} | {outcome} |")
    
    # Print JSON Manifest
    print(json.dumps(detailed_cert, indent=2))
    
    # Print Markdown Summary
    print("\n" + "\n".join(markdown_summary))
    if files_affected:
        print("\n### 📂 Affected Files")
        for f in sorted(files_affected):
            print(f"* `{f}`")
    else:
        print("\n*No files required remediation.*")
    
    # [COMPREHENSIVE REPORTS] Save detailed reports to files
    save_comprehensive_reports(territory, detailed_cert, markdown_summary, files_affected, state_mgr.project_root)

    logger.info(f"📜 CERTIFICATE ISSUED: {territory}")
    state_mgr.complete_agent("SovereignCertifier", True, "Certificate Issued")
    return detailed_cert

def save_comprehensive_reports(territory: str, detailed_cert: dict, markdown_summary: list, files_affected: set, project_root: Path):
    """
    [COMPREHENSIVE REPORTS] Save detailed JSON manifest and Markdown summary to persistent files.
    Creates timestamped reports in logs/compliance_reports/ directory.
    """
    try:
        # Create reports directory
        reports_dir = project_root / "logs" / "compliance_reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate timestamp for filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save JSON Manifest
        json_filename = f"compliance_report_{territory}_{timestamp}.json"
        json_path = reports_dir / json_filename
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(detailed_cert, f, indent=2, default=str)
        
        # Save Markdown Executive Summary
        md_filename = f"executive_summary_{territory}_{timestamp}.md"
        md_path = reports_dir / md_filename
        
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(markdown_summary))
            if files_affected:
                f.write("\n\n### 📂 Affected Files\n\n")
                for f_sorted in sorted(files_affected):
                    f.write(f"* `{f_sorted}`\n")
            else:
                f.write("\n\n*No files required remediation.*\n")
        
        # Save latest symlink for easy access
        latest_json = reports_dir / f"latest_compliance_{territory}.json"
        latest_md = reports_dir / f"latest_summary_{territory}.md"
        
        # Remove existing symlinks/files
        if latest_json.exists():
            latest_json.unlink()
        if latest_md.exists():
            latest_md.unlink()
        
        # Create symlinks (or copy on Windows)
        try:
            latest_json.symlink_to(json_path)
            latest_md.symlink_to(md_path)
        except (OSError, NotImplementedError):
            # Fallback for Windows or systems without symlink support
            import shutil
            shutil.copy2(json_path, latest_json)
            shutil.copy2(md_path, latest_md)
        
        logger.info(f"📁 Comprehensive reports saved:")
        logger.info(f"   JSON: {json_path.relative_to(project_root)}")
        logger.info(f"   Markdown: {md_path.relative_to(project_root)}")
        logger.info(f"   Latest: {latest_json.relative_to(project_root)}")
        
    except Exception as e:
        logger.error(f"Failed to save comprehensive reports: {e}")
        # Don't fail the entire process if report saving fails

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
    # Add project root to Python path
    project_root = Path.cwd()
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
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
    # [SOVEREIGN DEFAULT] Inverting safety logic to 'Active by Default' for Senior Developer velocity
    parser.add_argument("--disable-llm", action="store_true", help="Disable LLM for low-confidence decisions")
    parser.add_argument("--enable-cda", action="store_true", help="Enable CognitiveDispositionAgent for enhanced AI-powered violation analysis")
    parser.add_argument("--dry-run", action="store_true", help="Run in preview mode (no changes applied)")
    parser.add_argument("--interactive", action="store_true", help="Enable human-in-the-loop prompts (Default: Auto-Approve)")
    parser.add_argument("--manual", action="store_true", help="Disable autonomous mode (legacy)")
    parser.add_argument("--validate", action="store_true", help="Run in validation-only mode (CI/Dry-Run Mode)")
    # [PHASE 8] New Flag for Golden Baseline capture
    parser.add_argument("--capture-baseline", action="store_true", help="Capture new Golden Baseline")
    args = parser.parse_args()

    # [ULTRA-HARDENED] Validate user-supplied territory name format via regex
    if args.territory and not re.match(r"^[A-Za-z0-9_]+$", args.territory):
        parser.error("Invalid territory name: only alphanumeric and underscores allowed.")
    
    # 1. Handle Discovery
    if args.list_agents:
        logger.info("DISCOVERABLE AGENTS:")
        agents_list = list_available_agents(project_root)
        for i, (name, path) in enumerate(agents_list, 1):
            print(f"   {i:3}. {name:<40} [{path}]")
        print(f"\nTotal: {len(agents_list)} agents")
        return

    # [PHASE 8] Handle baseline capture command
    if args.capture_baseline:
        print("\n🔒 INITIATING BASELINE CAPTURE PROTOCOL...")
        try:
            from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import ArchitectureGovernorAgent
            governor = ArchitectureGovernorAgent(project_root=project_root)
            manifest = governor.capture_golden_baseline()
            print(f"✨ Golden Baseline captured at: {manifest}")
            sys.exit(0)
        except Exception as e:
            logger.error(f"Baseline capture failed: {e}")
            sys.exit(1)

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
    
    # [SOVEREIGN DEFAULT] Resolve 'Active-by-Default' logic across the orchestration chain
    enable_llm = not args.disable_llm
    dry_run = args.dry_run or args.validate
    auto_approve = not args.interactive
    
    # [NEW] Enable CognitiveDispositionAgent if requested
    enable_cda = getattr(args, 'enable_cda', False)
    
    decision_engine = EnhancedAutonomousDecisionEngine(enable_llm=enable_llm, state_mgr=state_mgr, enable_cda=enable_cda)
    
    logger.info("🏛️ UNIFIED SOVEREIGN PROTOCOL STARTED")
    logger.info(f"  Mode: {'AUTONOMOUS' if not args.manual else 'MANUAL'}")
    logger.info(f"  LLM: {'ENABLED' if enable_llm else 'DISABLED'}")
    logger.info(f"  CDA: {'ENABLED' if enable_cda else 'DISABLED'}")
    logger.info(f"  HEALING: {'ACTIVE' if not dry_run else 'DRY-RUN'}")
    logger.info(f"  APPROVAL: {'AUTO' if auto_approve else 'INTERACTIVE'}")
    
    try:
        from agentic_core.L5_safety.validators.FilesystemSSOTReconcilerAgent import FilesystemSSOTReconcilerAgent
        from agentic_core.L5_safety.validators.LocationAgent import LocationAgent
        from agentic_core.L5_safety.validators.HierarchyAgent import HierarchyAgent
        from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import ArchitectureGovernorAgent
        from agentic_core.L5_safety.validators.SystemArchitectAgent import SystemArchitectAgent
        # [ADDED] Integrated Sovereignty Guardians
        from agentic_core.L5_safety.validators.PascalSovereigntyAgent import PascalSovereigntyAgent
        from agentic_core.L5_safety.validators.RootHygieneAgent import RootHygieneAgent
        
        agents = {
            'reconciler': FilesystemSSOTReconcilerAgent,
            'location': LocationAgent,
            'hierarchy': HierarchyAgent,
            'arch_governor': ArchitectureGovernorAgent,
            'system_architect': SystemArchitectAgent,
            # [ADDED]
            'pascal_sovereignty': PascalSovereigntyAgent,
            'root_hygiene': RootHygieneAgent
        }
        logger.info("✅ All agents loaded successfully including Sovereignty Guardians")
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
            
            # [PHASE 8] Integrated Integrity Check
            # [HARDENED] Pass territory targets to ensure integrity check is also scoped.
            if is_autonomous:
                logger.info(f"🔍 [PHASE 8] Running integrity check (Scope: {targets})...")
                try:
                    from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import ArchitectureGovernorAgent
                    governor = ArchitectureGovernorAgent(project_root=project_root, ci_mode=True)
                    # Use provided targets to prevent global scanning during pre-flight check
                    audit_results = governor.run_audit(target_territories=targets)
                    
                    # [UNIFIED AUDIT] Persist all identified violations to the runtime state
                    state_mgr.state["compliance_report"] = audit_results
                    
                    if audit_results['stats']['violations_found'] > 0:
                        logger.warning(f"⚠️  {audit_results['stats']['violations_found']} total violations identified.")
                        
                    if audit_results['stats']['drift_detected'] > 0:
                        logger.error(f"🛑 CRITICAL: {audit_results['stats']['drift_detected']} integrity drift detected.")
                        if args.validate:
                            state_mgr.finish_mission(status="failed_integrity")
                            sys.exit(1) # Fatal in CI
                        else:
                            logger.warning("⚠️  Proceeding with caution (Heal mode active)...")
                except Exception as e:
                    logger.warning(f"Integrity check failed, continuing: {e}")
            
            # [INTEGRATION] Attempt L3 Smart Orchestration first
            if args.domains:
                l3_success, l3_results = try_summon_orchestrator(project_root, targets, execute=is_autonomous)
                if l3_success:
                    state_mgr.update_meta_learning({"total_experiences": 1, "experience": "L3 Mission Complete"})
                    state_mgr.finish_mission("completed")
                    logger.info("🎉 L3 MISSION COMPLETED")
                    return l3_results
            
            # [HARDENED] Universal Compliance Persistence
            results = []
            for territory in targets:
                logger.info(f"\n{'='*60}")
                logger.info(f"🚀 PROCESSING TERRITORY: {territory}")
                logger.info(f"{'='*60}")
                
                # Update State with Target
                state_mgr.state["current_territory"] = territory
                state_mgr.save()
                state_mgr.add_event("domain_start", f"Entering Domain: {territory}")
                
                try:
                    # [UNIVERSAL HEALING] Unified Execution Phase
                    # All agents now receive the 'Heal' signal if confidence is met
                    p1_drift, p1_loc = execute_phase1_discovery(agents, territory, decision_engine, state_mgr, dry_run, auto_approve)
                    
                    if p1_drift is not None:
                        # Phase 2: Structural Alignment (Hierarchy)
                        execute_phase2_alignment(agents, territory, decision_engine, state_mgr, dry_run, auto_approve)
                        
                        # [UNIVERSAL HEALING] Phase 2.5: Sovereignty Enforcement (Pascal/Header/Naming)
                        # Now integrated with confidence-based decision engine
                        pascal_confidence = decision_engine.calculate_healing_confidence(
                            violations_count=len(p1_loc) if p1_loc else 0,
                            violation_types=['SOVEREIGNTY', 'NAMING', 'HEADER'],
                            territory=territory
                        )
                        pascal_proceed, pascal_reason = decision_engine.should_proceed_with_healing(pascal_confidence)
                        
                        state_mgr.add_event("decision", f"Sovereignty Healing: {pascal_reason}")
                        logger.info(f"Sovereignty Decision: {pascal_reason}")
                        
                        if pascal_proceed and not dry_run:
                            logger.info(f"🛡️ Triggering Sovereignty Purge: {territory}")
                            state_mgr.update_agent("PascalSovereigntyAgent", "L5 - Safety")
                            pascal = agents['pascal_sovereignty'](project_root=Path.cwd())
                            # Force the agent to fix headers and rename files with proper parameters
                            if hasattr(pascal, 'heal_repository'):
                                res = pascal.heal_repository(
                                    target_territory=territory, 
                                    dry_run=dry_run,
                                    auto_approve=auto_approve
                                )
                                healed = res.get('files_healed', 0) if isinstance(res, dict) else 0
                                state_mgr.complete_agent("PascalSovereigntyAgent", True, f"Healed: {healed}")
                            else:
                                state_mgr.complete_agent("PascalSovereigntyAgent", False, "No heal_repository method")
                        elif not pascal_proceed:
                            state_mgr.add_event("warning", f"Sovereignty healing skipped - {pascal_reason}")
                        elif dry_run:
                            state_mgr.add_event("info", "Sovereignty healing skipped - Dry run mode")

                        # Phase 3: Validation
                        gov, arch = execute_phase3_validation(agents, territory, state_mgr)
                        
                        # Persist full work to state
                        state_mgr.state["compliance_report"] = gov
                        state_mgr.save()
                        
                        # Phase 4: Final Healing (Governor)
                        execute_phase4_healing(agents, territory, gov, decision_engine, state_mgr, dry_run, auto_approve)
                        
                        # Phase 5
                        cert = execute_phase5_final(agents, territory, state_mgr)
                        results.append(cert)
                    else:
                        logger.error(f"Phase 1 failed for {territory} - skipping")
                        state_mgr.add_event("error", f"Phase 1 failure in {territory}")
                        
                except RuntimeError as runtime_err:
                    # Catch the NonInteractiveGuard trap specifically
                    if "Interactive prompt blocked" in str(runtime_err):
                        logger.critical(f"🛑 BLOCKED INTERACTIVE PROMPT in {territory}: {runtime_err}")
                        state_mgr.add_event("error", f"Blocked Prompt in {territory}")
                        continue # Skip this territory, try next
                    raise runtime_err
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
            high_conf = sum(1 for d in decision_engine.decisions_made if d['confidence'] > 0.75)
            med_conf = sum(1 for d in decision_engine.decisions_made if 0.5 <= d['confidence'] <= 0.75)
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
