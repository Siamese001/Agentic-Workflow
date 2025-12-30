#!/usr/bin/env python3
import sys
# Canon Validator - Orchestration Entry Point
# Coordinates L1-L5 components for 50-key canon validation.
# VERSION 2.9 - SOVEREIGN HARDENING (Fixes: Boot Hangs, NoneType Crashes, Syntax Loops)
# (Fixes: Dynamic agent discovery, Iterative healing loop, Enhanced reporting)

import os
import shutil
import uuid

# [REENTRY GUARD] Prevent repeated full boot on convergence retries
# NAMING FIXED: _MISSION_EXECUTED → _mission_executed
_mission_executed = False

# [ETERNAL UTF-8] Force Windows consoles to handle unicode symbols (≠, 🚨)
if sys.platform.startswith("win"):
    os.system("chcp 65001 >nul")
    sys.stdout.reconfigure(encoding='utf-8')

import asyncio
import importlib
import inspect
import logging
import re
import time
import traceback
from pathlib import Path
from typing import Any, Optional, List, Dict, Tuple

# [DECOMPOSITION] Migrating static agent imports to L5 ComplianceOrchestrator
# RATIONALE: Redundant global imports at L6 cause boot bloat. Orchestrator now owns agent discovery.
try:
    from agentic_core.L5_safety.validators.compliance_orchestrator import compliance_orchestrator as ComplianceOrchestrator
    ORCHESTRATOR_AVAILABLE = True
    print("   [OK] Sovereign Compliance Orchestrator loaded")
except ImportError as e:
    print(f"   [!] Sovereign Orchestrator unavailable: {e}")
    print("   [FALLBACK] Running in legacy mode — limited functionality")
    ORCHESTRATOR_AVAILABLE = False

# [BOOTSTRAP] Dynamic bootstrap agent discovery
try:
    from agentic_core.L0_maintenance.scripts.BootstrapAgent import BootstrapAgent
    BOOTSTRAP_AVAILABLE = True
except ImportError:
    print("   [!] BootstrapAgent unavailable — skipping boot verification")
    BOOTSTRAP_AVAILABLE = False

from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    FORBIDDEN_ROOT_FOLDERS,
    CORE_SUBFOLDER_MAP,
    APPS_RG_SUBFOLDER_MAP,
    APPS_LIC_SUBFOLDER_MAP,
    APPS_SHARED_SUBFOLDER_MAP,
    TESTS_SUBFOLDER_MAP,
    CANON_SIGNALS,
    FORBIDDEN_PATTERNS,
    CANON_KEY_TO_FOLDER_MAP,  # [CRITICAL FIX] Required for final key coverage report
    ROOT_PROTECTED_FILES,
    SOVEREIGN_EXCLUDED_FOLDERS, # [SSOT] The single source of truth for ignored folders
    MCP_CAPABILITIES, # [SSOT] Capability status
    DISCOVERY_EXCLUDED_TERRITORIES, # [SSOT] Discovery scan exclusions
    MISSION_CONFIG, # [SSOT] Global mission toggles
    GRAVITY_SURGERY_ENABLED, # [SSOT] Master toggle
    HEALING_CONFIG, # [SSOT] Healing budget parameters
    AGENT_RESILIENCE_CONFIG, # [SSOT] Retry and backoff config
    SCOPE_SUMMARY_EXCLUSIONS, # [SSOT] Folders hidden from scope summary
)
from agentic_core.config.blueprint_sovereign.sovereign_env import get_env

# [SUB-ATOMIC SIZE POLICY] Enforce meaningful module granularity
# RATIONALE: Restore min/max bounds to prevent "Code Dust" (Key 13/49)
# These values ensure modules are small enough to be sub-atomic but large enough to be meaningful.
MAX_LINES_PER_FILE = 800   # Upper limit – triggers fission if exceeded
MIN_LINES_PER_FILE = 80    # Lower limit – prevents tiny dust files
DUST_THRESHOLD     = 40    # Reject splits producing files smaller than this

# [SOVEREIGN REPAIR] THE GRAVITY ANCHOR
# 1. Resolve Absolute Project Root by looking for the .env 'Soul' of the project
current_file_path = Path(__file__).resolve()
project_root = None

# We crawl up the tree until we find the .env file that defines the root
for parent in current_file_path.parents:
    if (parent / ".env").exists():
        project_root = parent
        break

if not project_root:
    print(f"\n[!] [L6 ERROR] CRITICAL GRAVITY LOSS: Could not locate .env root from {current_file_path}")
    # sys.exit(1)  # Commented out to allow pytest collection
    project_root = Path.cwd()  # Fallback to current directory

# [SOVEREIGN ANCHOR] Force project root into sys.path for Discovery
project_root_str = str(project_root)
if project_root_str not in sys.path:
    sys.path.insert(0, project_root_str)

# 2. Re-establish Neural Link to Resurrected Territories
# NAMING FIXED: SOVEREIGN_PATHS → sovereign_paths
sovereign_paths = [
    project_root / "agentic_core" / "runtime" / "shared_runtime",
    project_root / "apps_shared" / "utils"
]

for p in sovereign_paths:
    p_str = str(p)
    if p.exists() and p_str not in sys.path:
        sys.path.insert(0, p_str)

# [FIX] Guard against re-execution on import - only print once
# NAMING FIXED: _INIT_COMPLETE → _init_complete
_init_complete = getattr(sys.modules.get(__name__), '_init_complete', False)
if not _init_complete and __name__ == "__main__":
    print(f"   [OK] Sovereign Neural Link Active at Root: {project_root_str}")

    # [ETERNAL INDEX] Territory bootstrap removed - handled by PineconeSovereignAgent on demand
    
    _init_complete = True

# [PHASE 12] TELEMETRY: Delegated to L4/L5 TracingAgent
# RATIONALE: All OTEL/Mock setup is now managed by the sovereign conductor.
if ORCHESTRATOR_AVAILABLE:
    try:
        from agentic_core.L5_safety.validators.compliance_orchestrator import compliance_orchestrator
        orchestrator = compliance_orchestrator(Path.cwd())
        if hasattr(orchestrator, 'tracing') and orchestrator.tracing:
            tracer = orchestrator.tracing.get_tracer()
        else:
            # Orchestrator exists but no tracing configured
            class MockSpan:
                def __enter__(self): return self
                def __exit__(self, *args): pass
                def set_attribute(self, *args): pass
                def end(self): pass

            class MockTracer:
                def start_as_current_span(self, name): return MockSpan()
                def start_span(self, name): return MockSpan()
            
            tracer = MockTracer()
    except Exception as e:
        # Emergency L6 Fallback (Zero-Dependency)
        class MockSpan:
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def set_attribute(self, *args): pass
            def end(self): pass

        class MockTracer:
            def start_as_current_span(self, name): return MockSpan()
            def start_span(self, name): return MockSpan()
        
        tracer = MockTracer()
        if __name__ == "__main__":
            print(f"   [!] TracingAgent setup failed: {e}")
else:
    # Emergency L6 Fallback (Zero-Dependency)
    class MockSpan:
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def set_attribute(self, *args): pass
        def end(self): pass

    class MockTracer:
        def start_as_current_span(self, name): return MockSpan()
        def start_span(self, name): return MockSpan()
    
    tracer = MockTracer()

if __name__ == "__main__":
    # [PHASE 1] Bootstrap: Verify Environment and Neural Links
    if BOOTSTRAP_AVAILABLE:
        bootstrap = BootstrapAgent(project_root)
        bootstrap.run_bootstrap()
    else:
        print("   [WARNING] Boot verification skipped (agent missing)")

    # [HARDENING] Remove auto-mutation of legacy imports on every run
    print("\n[INFO] Legacy import reconciliation skipped (run manually if needed)")
    print("-" * 70)

def _get_optimized_order(default_list: List[Tuple[str, List[str]]], project_root: Path) -> List[Tuple[str, List[str]]]:
    """
    [CANON KEY 3] Dynamic Re-prioritization
    Re-orders the agent execution list based on MetaLearningAgent telemetry.
    """
    memory_path = project_root / "agentic_core" / "runtime" / "mission_memory.json"
    if not memory_path.exists():
        return default_list

    try:
        memory = json.loads(memory_path.read_text(encoding="utf-8"))
        priority_names = memory.get("next_priority_order", [])
        if not priority_names:
            return default_list

        # Map class names to their full tuple definitions
        default_map = {item[1][0]: item for item in default_list}
        optimized_list = []

        # 1. Insert agents in prioritized order
        for name in priority_names:
            if name in default_map:
                optimized_list.append(default_map.pop(name))

        # 2. Append remaining agents (Constitutional Baseline)
        optimized_list.extend(default_map.values())
        
        return optimized_list
    except Exception as e:
        print(f"    [!] Mission Memory Load Failure: {e}")
        return default_list

# ===========================================================================
# [PHASES] NAMING, GRAVITY, AND REGISTRY SYNC
# ===========================================================================
if __name__ == "__main__":
    print(f"\n[PHASE 0] Naming Law Amplification: ARMED")
    print(f"[PHASE -1] Gravity Surgery: ARMED")
    print(f"[PHASE +1] Sovereign Registry Sync: SCHEDULED")
    print("-" * 70)

# [ETERNAL SSOT] Initialize sovereign environment loader
env = get_env(project_root)
if __name__ == "__main__":
    print(f"   [OK] SovereignEnv loaded — Model: {env.GEMINI_MODEL} | Embedding Dim: {env.EMBEDDING_DIMENSION}")

# [GRAVITY SSOT] Dynamically derived authority order
# NAMING FIXED: GRAVITY_LAYERS → gravity_layers
gravity_layers = SOVEREIGN_REGISTRY["agentic_core"]["subfolders"]

def get_layer_rank(path_str: str) -> int:
    """Lower index = higher authority. Order pulled directly from SSOT."""
    for i, layer in enumerate(gravity_layers):
        if layer in path_str:
            return i
    return -1

# [SSOT MAPPING] Direct access — no intermediate duplicate map needed
def get_legal_l2_for_l1(root: str, l1_name: str) -> List[str]:
    """Pull valid L2 folders directly from imported SSOT maps."""
    if root == "agentic_core":
        return CORE_SUBFOLDER_MAP.get(l1_name, [])
    elif root == "apps_rg":
        return APPS_RG_SUBFOLDER_MAP.get(l1_name, [])
    elif root == "apps_lic":
        return APPS_LIC_SUBFOLDER_MAP.get(l1_name, [])
    elif root == "apps_shared":
        return APPS_SHARED_SUBFOLDER_MAP.get(l1_name, [])
    return []

# [HARDENING] NEURAL LINK INITIALIZATION
if __name__ == "__main__":
    print("   [OK] Environment loading complete (handled in neural link verification)")

# Dashboard removed - was causing port 5000 conflicts
# NAMING FIXED: DASHBOARD_AVAILABLE → dashboard_available
dashboard_available = False

# [GRAVITY FIX] DYNAMIC IMPORT SYSTEM
# Utils layer cannot import from L1-L5 directly - use dynamic loading
def dynamic_import(module_path, class_name):
    """Dynamically import classes to avoid gravity violations."""
    try:
        module = __import__(module_path, fromlist=[class_name])
        return getattr(module, class_name)
    except ImportError:
        return None
