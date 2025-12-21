#!/usr/bin/env python3
"""
Canon Validator - Orchestration Entry Point
Coordinates L1-L5 components for 50-key canon validation.
VERSION 2.7 - DYNAMIC HEALING ENGINE
(Fixes: Dynamic agent discovery, Iterative healing loop, Enhanced reporting)
"""

import asyncio
import importlib
import inspect
import logging
import os
import sys
import time
import traceback
from pathlib import Path
from typing import Any, Optional

# Add project root to sys.path for imports
# Validator is now at root (Key 0), so parent is the project root
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# --- CRITICAL FIX: IMPORT POLYFILL (agentic_workflow -> agentic_core) ---
# Maps legacy 'agentic_workflow' imports to the new 'agentic_core' package
# to prevent ModuleNotFoundError in agent files.
try:
    import agentic_core
    sys.modules['agentic_workflow'] = agentic_core
    sys.modules['agentic_workflow.agentic_core'] = agentic_core
    # Explicitly shim common submodules to prevent deep import errors
    sys.modules['agentic_workflow.agents'] = agentic_core
    print("   [PATCH] Shimmed 'agentic_workflow' imports to 'agentic_core'")
except ImportError:
    print("   [CRITICAL] Could not import 'agentic_core'. Shim failed.")
    sys.exit(1)

# Hard-Gate: Tri-Brain SDKs are MANDATORY
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError as e:
    print(f"CRITICAL: Missing dependency: {e.name}. Install with: pip install python-dotenv")
    sys.exit(1)

# Dashboard Integration
try:
    from canon_dashboard import CanonDashboard, DashboardMetrics
    from canon_dashboard_web import run_server
    DASHBOARD_AVAILABLE = True
except ImportError:
    DASHBOARD_AVAILABLE = False
    print("[!] Dashboard not available. Install: pip install rich flask flask-cors")

# Import core components from agentic_core
try:
    from agentic_core.L3_orchestration import FissionManager, apply_fission_blueprint
    from agentic_core.L5_safety import SafetyGuardrail, SubAtomicEngine
    from agentic_core.runtime import (
        ALLOWED_ROOT_FOLDERS,
        check_import_waterfall_violations,
        check_single_child_violations,
        enforce_void_compliance,
        generate_ascii_tree,  # [VISUALIZER]
        get_applicable_keys_for_file,
        get_folder_scope_summary,
        validate_file_location,
    )
except ImportError as e:
    print(f"CRITICAL: Core component missing: {e}")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


# ==============================================================================
# [HARDENING] TELEMETRY PROXY: GEMINI SPY
# ==============================================================================
class GeminiSpy:
    """
    [L5 HARDENING] TELEMETRY INTERCEPTOR
    Wraps the SubAtomicEngine to force visibility of all LLM transactions.
    Ensures that 'Agentic Capabilities' are actually resulting in API calls.
    """
    def __init__(self, real_engine):
        self._engine = real_engine

    def __getattr__(self, name):
        # Pass through non-callable attributes immediately
        attr = getattr(self._engine, name)
        if not callable(attr) or name.startswith("_"):
            return attr

        # Intercept method calls (e.g., generate_content, query, chat)
        def wrapper(*args, **kwargs):
            print(f"\n[👀 GEMINI SPY] Agent triggering: {name}")
            # Log prompt preview if available
            if args:
                try:
                    preview = str(args[0])[:120].replace('\n', ' ')
                    print(f"   -> Prompt: {preview}...")
                except: pass
            
            start_t = time.time()
            try:
                result = attr(*args, **kwargs)
                duration = time.time() - start_t
                print(f"[👀 GEMINI SPY] ✅ Success ({duration:.2f}s). Signal received.")
                return result
            except Exception as e:
                print(f"[👀 GEMINI SPY] ❌ FAILURE: {e}")
                raise e
        return wrapper


# ==============================================================================
# L6 PEACEKEEPER: PHYSICAL BOUNDARY ENFORCEMENT
# ==============================================================================

def run_l6_preflight(target_sector: str, project_root: Path) -> bool:
    """
    Integrates Void Compliance into the Master Validation Sweep.
    Ensures the system is self-aware of its physical boundaries before judging code.
    
    Args:
        target_sector: Target directory to validate
        project_root: Project root directory
        
    Returns:
        True if sector is void-compliant, False otherwise
    """
    print(f"\n[*] L6 PRE-FLIGHT: Enforcing Void Compliance on {target_sector}...")
    
    # Cross-reference with IDE Rules
    rules_path = project_root / "windsurfrules.md"
    if rules_path.exists():
        print(f"   [INFO] Synchronization active: windsurfrules.md detected.")
    
    target_path = Path(target_sector).resolve()
    
    # Check 1: Single-Child Antipattern Detection (Ignore project root)
    single_child_violations = []
    if target_path != project_root:
        single_child_violations = check_single_child_violations(target_path if target_path.is_dir() else project_root)
    if single_child_violations:
        print(f"[!] L6 ALERT: Found {len(single_child_violations)} single-child antipatterns:")
        for folder_path, reason in single_child_violations[:3]:
            print(f"   [X] {folder_path.relative_to(project_root)}: {reason}")
        if len(single_child_violations) > 3:
            print(f"   ... and {len(single_child_violations) - 3} more violations")
    
    # Check 2: Import Waterfall Violations (Sovereign -> Apps)
    waterfall_violations = []
    if target_path.is_dir():
        for py_file in target_path.rglob("*.py"):
            violations = check_import_waterfall_violations(py_file, project_root)
            if violations:
                waterfall_violations.extend([(py_file, v) for v in violations])
    
    if waterfall_violations:
        print(f"[!] L6 ALERT: Found {len(waterfall_violations)} import waterfall violations:")
        for file_path, reason in waterfall_violations[:3]:
            print(f"   [X] {file_path.name}: {reason}")
        if len(waterfall_violations) > 3:
            print(f"   ... and {len(waterfall_violations) - 3} more violations")
    
    # Check 3: File Location Validation
    location_violations = []
    if target_path.is_dir():
        for py_file in target_path.rglob("*.py"):
            is_valid, reason = validate_file_location(py_file, project_root)
            if not is_valid:
                location_violations.append((py_file, reason))
    
    if location_violations:
        print(f"[!] L6 ALERT: Found {len(location_violations)} file location violations:")
        for file_path, reason in location_violations[:3]:
            print(f"   [X] {file_path.name}: {reason}")
        if len(location_violations) > 3:
            print(f"   ... and {len(location_violations) - 3} more violations")
    
    # Summary
    total_violations = len(single_child_violations) + len(waterfall_violations) + len(location_violations)
    
    if total_violations == 0:
        print("[OK] L6 PRE-FLIGHT: Sector is Void-Compliant.")
        return True
    else:
        print(f"[!] L6 PRE-FLIGHT: {total_violations} physical structure violations detected.")
        print("    ArchitectureGovernor may auto-flatten or halt based on severity.")
        return False


# ==============================================================================
# L4 ORCHESTRATION: THE RUNNER (Mission Logic)
# ==============================================================================

async def run_mission(target_scope: str = "agentic_core"):
    """
    [L3 ORCHESTRATOR]
    Executes the full Agentic Validation Mission.
    FULLY HARDENED: Instantiates Safety, Engine, and Fission Logic and wires to Context.
    """
    print(f"\n[*] MISSION START: Validating {target_scope}")
    print(f"DEBUG: VERSION 2.7 - DYNAMIC HEALING ENGINE")
    
    # Add project root to sys.path for imports
    # Validator is now at root (Key 0), so parent is the project root
    project_root = Path(__file__).parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    # === DASHBOARD INITIALIZATION ===
    dashboard_metrics = None
    web_thread = None
    
    if DASHBOARD_AVAILABLE:
        dashboard_metrics = DashboardMetrics()
        dashboard = CanonDashboard(dashboard_metrics)
        
        # Start web dashboard in background
        import canon_dashboard_web
        canon_dashboard_web.metrics = dashboard_metrics
        web_thread = threading.Thread(
            target=run_server,
            args=('0.0.0.0', 5000, False),
            daemon=True
        )
        web_thread.start()
        print(f"   [OK] Web Dashboard: http://localhost:5000")
        print(f"   [!] Terminal Dashboard: Disabled (blocks execution)")
    
    # === L6 PEACEKEEPER: MANDATORY PRE-FLIGHT ===
    # Execute void compliance check BEFORE any validation begins
    l6_compliant = run_l6_preflight(target_scope, project_root)
    if not l6_compliant:
        print("\n⚠️  [L6 WARNING] Physical structure violations detected.")
        print("    Proceeding with validation, but auto-healing may be restricted.")

    # --- L5 HARDENING INSTANTIATION ---
    # 1. Initialize Safety Components
    safety_guard = SafetyGuardrail(deletion_limit=110)

    # [HARDENING] VERIFY KEY PRESENCE
    if not os.getenv("GEMINI_API_KEY"):
        print("\n[CRITICAL HARDENING] GEMINI_API_KEY NOT FOUND!")
        print("   -> Agentic capabilities cannot be unleashed without a neural link.")
        print("   -> Execution halted to prevent 'Dry Run' silence.")
        sys.exit(1)

    # [AGENTIC UNLEASH] EXPLICIT CLIENT CONSTRUCTION
    try:
        import google.generativeai as genai
        from google.generativeai.types import HarmCategory, HarmBlockThreshold

        api_key = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=api_key)
        
        # [UNLEASHED CONFIG] Maximum Creativity & Capacity
        generation_config = {
            "temperature": float(os.getenv("GEMINI_TEMPERATURE", "1.0")),   # Transformative fixes
            "top_p": float(os.getenv("GEMINI_TOP_P", "0.99")),
            "top_k": int(os.getenv("GEMINI_TOP_K", "64")),
            "max_output_tokens": int(os.getenv("GEMINI_MAX_TOKENS", "32768")), # Full-file rewrites
        }

        # [NO HANDCUFFS] Disable Safety Filters
        safety_settings = [
            {"category": HarmCategory.HARM_CATEGORY_HARASSMENT, "threshold": HarmBlockThreshold.BLOCK_NONE},
            {"category": HarmCategory.HARM_CATEGORY_HATE_SPEECH, "threshold": HarmBlockThreshold.BLOCK_NONE},
            {"category": HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, "threshold": HarmBlockThreshold.BLOCK_NONE},
            {"category": HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, "threshold": HarmBlockThreshold.BLOCK_NONE},
        ]

        model_name = os.getenv("GEMINI_MODEL")
        if not model_name:
            print("\n[CRITICAL] GEMINI_MODEL not set in .env!")
            print("   -> Add GEMINI_MODEL=gemini-2.5-flash to your .env file")
            sys.exit(1)
        gemini_model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=generation_config,
            safety_settings=safety_settings
        )

        # Initialize Engine with PRE-BUILT client
        _real_engine = SubAtomicEngine(gemini_client=gemini_model)
        # Wrap in Spy for Visibility
        subatomic_engine = GeminiSpy(_real_engine)
        
        print(f"   [OK] AGENTIC UNLEASHED: {model_name} | Temp: {generation_config['temperature']} | Tokens: {generation_config['max_output_tokens']}")
        print(f"   [OK] SAFETY FILTERS: DISABLED (BLOCK_NONE)")
        print(f"   [OK] TELEMETRY: GEMINI SPY ACTIVE")

    except Exception as e:
        print(f"[CRITICAL] Failed to unleash Gemini: {e}")
        sys.exit(1)

    # 2. Initialize Fission Logic with HIGH threshold to validate all files
    # Set to 10000 to effectively disable fission and validate everything
    fission_mgr = FissionManager(line_limit=10000, max_rounds=3)
    
    print(f"   [OK] SafetyGuardrail active (Limit: 110 lines)")
    
    # === INITIALIZE CONTEXT (MOVED UP FOR SAFETY) ===
    # Must exist before CallableReport attempts to use it in closure
    try:
        from agentic_core.L4_state.validation_context import ValidationContext
        ctx = ValidationContext()
        print("   [OK] ValidationContext loaded from agentic_core")
    except ImportError:
        class ValidationContext:
            def __init__(self):
                self.target_scope = None
                self.python_files = []
                self.report = []
                self.results = {}
                self.signals = set()
                self._client = None
        ctx = ValidationContext()
        print("   [!] Using fallback ValidationContext")

    # ===========================================================================
    # [ENHANCEMENT 1] L4 STATE HARDENING: Smart-Report Hybrid
    # ===========================================================================
    class CallableReport(list):
        """Hybrid report: Acts as list for append() AND callable for ctx.report()"""
        def __init__(self, initial_list=None):
            super().__init__(initial_list or [])
            self._current_round = 1

        def __call__(self, agent_name: str, key_num: int, passed: bool, details: str = ""):
            status = "PASS" if passed else "FAIL"
            entry = {
                "agent": agent_name,
                "key": key_num,
                "status": status,
                "msg": str(details),
                "timestamp": __import__('datetime').datetime.now().isoformat(),
                "round": self._current_round
            }
            self.append(entry)
            
            # Forward to dashboard metrics
            if dashboard_metrics and hasattr(ctx, 'python_files'):
                current_file = getattr(ctx, 'current_file_path', None)
                if current_file and not passed:
                    # Extract violation count from details if present
                    violation_count = 1
                    if "violations" in str(details).lower():
                        import re
                        match = re.search(r'(\d+)\s+violations?', str(details), re.IGNORECASE)
                        if match:
                            violation_count = int(match.group(1))
                    dashboard_metrics.record_violation(current_file, key_num, violation_count)

    # Harden Attributes (The "AttributeError" Fix)
    ctx.report = CallableReport(getattr(ctx, 'report', []))
    if not hasattr(ctx, 'results'): ctx.results = {} # Fixes StructuralEngineer
    if not hasattr(ctx, 'get_env'): ctx.get_env = lambda k, d=None: os.getenv(k, d)
    if not hasattr(ctx, 'signals'): ctx.signals = set()
    
    # 3. WIRE COMPONENTS TO CONTEXT (Crucial Fix)
    ctx.engine = subatomic_engine
    ctx.safety = safety_guard
    ctx.fission = fission_mgr
    ctx.dashboard_metrics = dashboard_metrics  # Wire dashboard metrics
    
    ctx.target_scope = target_scope
    
    # === L5 SAFETY: Path Containment ===
    target_path = Path(target_scope).resolve()
    project_root_path = project_root.resolve()
    if not target_path.is_relative_to(project_root_path):
        raise ValueError(f"[SECURITY BLOCK] Target scope '{target_scope}' escapes project root.")
    
    # Discover all Python files in target scope
    discovered_files = [p for p in target_path.rglob("*.py") if p.is_file()]
    
    # === L6 RUNTIME: Void Compliance Enforcement ===
    valid_files, violations = enforce_void_compliance(discovered_files, project_root_path)
    
    if violations:
        print(f"\n⚠️  [VOID COMPLIANCE] {len(violations)} files in forbidden/unknown folders:")
        for file_path, reason in violations[:5]:  # Show first 5
            print(f"   [X] {file_path.name}: {reason}")
        if len(violations) > 5:
            print(f"   ... and {len(violations) - 5} more violations")
    
    ctx.python_files = [str(p) for p in valid_files]
    print(f"   [OK] Context hardened: {len(ctx.python_files)} Python files in {len(ALLOWED_ROOT_FOLDERS)} allowed folders")
    
    # Initialize dashboard session
    if dashboard_metrics:
        dashboard_metrics.start_session(target_scope, len(ctx.python_files))
    
    # Print folder scope summary (ASCII TREE)
    print(f"\n   [SCOPE] Verifying Map vs. Territory...")
    folder_summary = get_folder_scope_summary(project_root_path)
    
    # Print stats
    for folder, count in sorted(folder_summary.items()):
        if count > 0:
            print(f"      • {folder:<20} : {count} files")
            
    # [VISUALIZER] Print the Physical Tree (Max Depth 4 for readability)
    print("\n   [PHYSICS] Current Directory Structure:")
    tree_view = generate_ascii_tree(project_root_path, max_depth=4)
    print(tree_view)
    print("-" * 50)
    
    # ===========================================================================
    # [ENHANCEMENT 2] L1 INTELLIGENCE INJECTION: Dynamic Agent Discovery
    # ===========================================================================
    cleaning_crew = []
    
    def discover_agents():
        """
        [L1 DISCOVERY] Scans the Atomic Layers (L1-L5) and Domains for Agents.
        Targeting:
          - agentic_core/ (The Brain: Strategy, Orchestration, Safety)
          - apps_rg/agents/ (Domain A Specialists)
          - apps_lic/agents/ (Domain B Compliance)
        """
        found_agents = []
        
        # Define scan targets based on ASCII Architecture
        scan_targets = [
            project_root / "agentic_core",   # Recursive scan for L1-L5 agents
            project_root / "apps_rg" / "agents",
            project_root / "apps_lic" / "agents"
        ]

        print(f"   [DISCOVERY] Scanning architectural layers for agents...")
        
        for base_dir in scan_targets:
            if not base_dir.exists(): continue

            for file_path in base_dir.rglob("*.py"):
                if file_path.name.startswith("__") or "__pycache__" in str(file_path):
                    continue
                
                # Convert file path to module path (Robust)
                try:
                    rel_path = file_path.relative_to(project_root)
                except ValueError:
                    continue # Skip files outside project root

                module_name = str(rel_path).replace(os.sep, ".")[:-3]  # Strip .py
                
                # Skip non-agent files
                if "setup" in module_name or "utils" in module_name or "__init__" in module_name:
                    continue

                try:
                    module = importlib.import_module(module_name)
                    # Inspect module for classes that look like Agents
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        # Filter: Must be a class, defined in this module, and have execute/run method
                        if (isinstance(attr, type) and 
                            attr.__module__ == module_name and
                            (attr_name.endswith(('Agent', 'Guardian', 'Architect', 'Engineer', 'Enforcer', 'Sentinel', 'Hunter')) or
                             attr_name in ('SystemArchitect', 'StructuralEngineer', 'HealerAgent', 'HygieneGuardian', 'ArchitectureGovernor', 
                                         'DependencySentinel', 'SecurityEnforcer', 'MemoryArchitect', 'HallucinationHunter')) and
                            (hasattr(attr, 'execute') or hasattr(attr, 'run'))):
                            found_agents.append((module_name, attr_name, attr))
                except Exception as e:
                    print(f"     [!] Failed to inspect {file_path.name}: {e}")
                
        return found_agents

    # Execute Discovery
    # Scans agentic_core (L1-L5) and apps_*/agents
    discovered = discover_agents()
    print(f"   [COMPREHENSIVE MODE] Found {len(discovered)} agents via dynamic discovery")
    print(f"   [CONFIG] Fission Threshold: 10,000 LOC | Healing: Iterative Loop")
    
    for mod_name, cls_name, cls_ref in discovered:
        try:
            # Instantiate with context
            agent_instance = cls_ref(ctx)
            cleaning_crew.append(agent_instance)
            print(f"     [+] Active: {cls_name}")
        except Exception as e:
            print(f"     [!] Failed to instantiate {cls_name}: {e}")

    # --- CRITICAL SAFETY CHECK ---
    if not cleaning_crew:
        print("\n[CRITICAL FAILURE] 0 Agents loaded. Mission Aborted.")
        print("   -> Check if the Import Shim (Diff 1) was applied correctly.")
        return # Halt execution
    # -----------------------------

    # Inject "Surgeon Mode" into ArchitectureGovernor
    surgeon_prompt = """
### SYSTEM_ROLE: ARCHITECTURAL_SURGEON
Your primary directive is ATOMICITY. 
THRESHOLD: 200 Lines.

IF (file_lines > 200) OR (task == "GENERATE_FISSION_BLUEPRINT"):
    1. ABANDON standard healing. 
    2. TRIGGER FISSION_EVENT.
    3. GENERATE JSON ONLY (No Markdown):
    {
      "fission_event": true,
      "original_file": "{{file_path}}",
      "blueprint": {
        "logic_core": {"content": "...", "exports": ["ClassA"]},
        "utils_shared": {"content": "...", "exports": ["helper_v"]}
      }
    }
    4. Ensure 'content' includes imports.
"""
    governor = next((a for a in cleaning_crew if a.__class__.__name__ == 'ArchitectureGovernor'), None)
    if governor:
        # Try updating system prompt via method or attribute
        if hasattr(governor, 'update_system_prompt'):
            governor.update_system_prompt(surgeon_prompt)
        else:
            governor.system_prompt = surgeon_prompt
        print("   [+] L1 Injection: ArchitectureGovernor configured as Surgeon")
    
    # ===========================================================================
    # [ENHANCEMENT 3] L3 ORCHESTRATION: Categorize Agents (Fixes "Too Fast" Bug)
    # ===========================================================================
    atomic_validators = [] # Run PER FILE (takes file_path arg)
    batch_validators = []  # Run ONCE (takes no args)
    monitors = []          # Run ONCE at end

    for agent in cleaning_crew:
        name = agent.__class__.__name__
        if name in ['MemoryArchitect', 'HallucinationHunter']:
            monitors.append(agent)
            continue
            
        # Introspect execute/run method
        method = getattr(agent, 'execute', getattr(agent, 'run', None))
        if method:
            # Check if method takes 'file_path' argument (excluding self)
            # Hardened against methods that might not expose __code__ (e.g. C-extensions or functools.partial)
            try:
                arg_count = method.__code__.co_argcount
                if arg_count > 1:
                    atomic_validators.append(agent)
                else:
                    batch_validators.append(agent)
            except AttributeError:
                # Fallback: Assume Atomic if name implies it, otherwise Batch
                print(f"     [?] Could not introspect {name}. Defaulting to Batch.")
                batch_validators.append(agent)
        else:
            print(f"   [!] Agent {name} has no execute/run method.")

    print(f"   [L3] Orchestration Plan:")
    print(f"        - {len(atomic_validators)} Atomic Agents (Run {len(ctx.python_files)}x)")
    print(f"        - {len(batch_validators)} Batch Agents (Run 1x)")
    print(f"        - {len(monitors)} Monitors (Run 1x)")
    print(f"   [>] Starting Execution Sweep...\n")

    # ===========================================================================
    # PHASE 1: ATOMIC SWEEP (Per-File Validation)
    # ===========================================================================
    for idx, file_path in enumerate(ctx.python_files, 1):
        file_name = os.path.basename(file_path)
        file_path_obj = Path(file_path)
        
        # === L6 RUNTIME: ALL 50 KEYS FOR COMPREHENSIVE VALIDATION ===
        # Enable all 50 canon keys (0-49) for comprehensive validation
        applicable_keys = list(range(0, 50))
        
        # Check LOC for Safety Threshold
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                loc_count = len(f.readlines())
        except: loc_count = 0
        
        print(f"🔍 [{idx}/{len(ctx.python_files)}] {file_name} ({loc_count} LOC) [Keys: {sorted(applicable_keys) if applicable_keys else 'ALL'}]", end='\r')

        # Update dashboard with current file
        if dashboard_metrics:
            dashboard_metrics.session.current_file = file_path
            ctx.current_file_path = file_path  # Store for report callback

        # --- ACTIVE FISSION TRIGGER (Files > 10000 Lines) ---
        # Increased threshold to validate all files comprehensively
        if loc_count > 10000:
            print(f"\n⚠️  [FISSION TRIGGER] {file_name} ({loc_count} lines). Engaging Auto-Fission.")
            
            if governor:
                try:
                    # 1. Force Governor to generate Blueprint
                    print(f"   [>] Generating Blueprint via ArchitectureGovernor...")
                    method = getattr(governor, 'execute', getattr(governor, 'run', None))
                    
                    # Pass file path (Modern) or set context (Legacy)
                    if method:
                        res = await method(file_path) if method.__code__.co_argcount > 1 else await method()
                    else:
                        res = None

                    # [CRITICAL FIX] L2 Parsing Bridge: Convert String to Dict
                    if isinstance(res, str):
                        res = SubAtomicEngine.parse_fission_output(res)

                    # 2. Check for Fission Event in Result
                    if isinstance(res, dict) and res.get("fission_event"):
                        # Use the pre-initialized fission_mgr with 200 limit
                        
                        # 3. Execute Physical Split (L2)
                        success = await apply_fission_blueprint(file_path, res["blueprint"], fission_mgr)
                        
                        if success:
                            ctx.results[file_name] = {"action": "FISSION_COMPLETE", "loc": loc_count}
                            ctx.report("FissionManager", 50, True, f"Split {file_name} into sub-modules")
                            print(f"   [✓] Fission Complete. Skipping standard validation.")
                            continue # Skip to next file
                        else:
                            print(f"   [!] Blueprint Application Failed.")
                except Exception as e:
                    print(f"   [!] Fission Error: {e}")
            
            # If we are here, Fission didn't happen or failed.
            # Mark for manual review but DO NOT CONTINUE (let standard agents try to fix what they can)
            ctx.results[file_name] = {"action": "FISSION_ATTEMPTED_FALLBACK", "loc": loc_count}
            # Remove 'continue' to allow standard validation on large files if fission fails

        # --- ATOMIC AGENT EXECUTION (ITERATIVE HEALING LOOP) ---
        ctx.current_file_applicable_keys = applicable_keys
        MAX_HEALING_ROUNDS = 3
        file_healed = False
        
        print(f"\n   [HEALING] Starting iterative validation for {file_name}")
        
        for round_idx in range(1, MAX_HEALING_ROUNDS + 1):
            violations_this_round = 0
            changes_this_round = 0
            
            # Update round tracking in reports
            ctx.report._current_round = round_idx
            
            print(f"     Round {round_idx}/{MAX_HEALING_ROUNDS}...", end=' ')
            
            for agent in atomic_validators:
                try:
                    method = getattr(agent, 'execute', getattr(agent, 'run', None))
                    if method:
                        # Track if agent made changes (some agents return True/dict when they fix things)
                        result = None
                        try:
                            if method.__code__.co_argcount > 1:
                                result = await method(file_path)
                            else:
                                result = await method()
                        except AttributeError:
                            # Fallback for decorated methods that don't expose __code__
                            # Try calling with file_path first, then without
                            try:
                                result = await method(file_path)
                            except TypeError:
                                result = await method()
                        
                        # Count actual changes/healing actions
                        if result is True or (isinstance(result, dict) and result.get('healed')):
                            changes_this_round += 1
                            file_healed = True
                            
                except Exception as e:
                    ctx.report(agent.__class__.__name__, 0, False, f"Exec Error: {str(e)[:50]}")
                    violations_this_round += 1
            
            # Check for convergence (no new violations in this round)
            # Get current report entries for this file and round
            current_round_reports = [r for r in ctx.report if file_name in str(r) and r.get('round', 1) == round_idx]
            fail_count = len([r for r in current_round_reports if r.get('status') == 'FAIL'])
            
            print(f"Changes: {changes_this_round} | Violations: {fail_count}")
            
            # If no violations and we're past round 1, we've converged
            if fail_count == 0 and round_idx > 1:
                print(f"     [] Converged after {round_idx-1} rounds")
                break
        
        if file_healed:
            print(f"   [HEALING] Complete: {file_name}")
        
        # Update dashboard after file processing
        if dashboard_metrics:
            # Determine if file passed or failed based on report
            file_reports = [r for r in ctx.report if file_name in str(r)]
            file_passed = len([r for r in file_reports if r.get('status') == 'FAIL']) == 0
            dashboard_metrics.update_file_progress(file_path, "passed" if file_passed else "failed")
    
    # ... (rest of the code remains the same)
    # ===========================================================================
    # PHASE 2: BATCH SWEEP (Cross-File / Full Scope Validation)
    # ===========================================================================
    print(f"\n\n🧩 [L4 STATE] Executing Batch Agents ({len(batch_validators)})...")
    for agent in batch_validators:
        print(f"   [>] Running {agent.__class__.__name__}...")
        try:
            method = getattr(agent, 'execute', getattr(agent, 'run', None))
            # Batch agents typically run without args or manage their own scope
            if method:
                await method() 
            print(f"   [✓] {agent.__class__.__name__} completed")
        except Exception as e:
             print(f"   [!] Error in {agent.__class__.__name__}: {e}")
             ctx.report(agent.__class__.__name__, 0, False, f"Batch Error: {str(e)[:50]}")

    # ===========================================================================
    # PHASE 3: MONITORING (Final Pass)
    # ===========================================================================
    print(f"\n🧠 [L4 STATE] Executing Global Monitors (Single Pass)...")
    for monitor in monitors:
        try:
            method = getattr(monitor, 'execute', getattr(monitor, 'run', None))
            if method: await method()
            print(f"   [✓] {monitor.__class__.__name__} completed")
        except Exception: pass

    # ===========================================================================
    # [ENHANCEMENT 6] MISSION DASHBOARD & SUMMARY
    # ===========================================================================
    print("\n" + "="*70)
    print(f"🚀 MISSION COMPLETE: {len(ctx.python_files)} Files Swept")
    
    # Mark session as complete
    if dashboard_metrics:
        dashboard_metrics.session.status = "completed"
        
        # Export dashboard report
        report_path = f"canon_report_{dashboard_metrics.session.session_id}.json"
        dashboard.export_report(report_path)
        print(f"📊 Dashboard Report: {report_path}")
    
    # Fission Stats
    fission_done = sum(1 for v in ctx.results.values() if isinstance(v, dict) and v.get('action') == 'FISSION_COMPLETE')
    fission_pending = sum(1 for v in ctx.results.values() if isinstance(v, dict) and v.get('action') == 'FISSION_REQUIRED_MANUAL')
    
    if fission_done > 0:
        print(f"⚡ FISSION SUCCESS: {fission_done} files split into sub-modules")
    if fission_pending > 0:
        print(f"⚠️  FISSION PENDING: {fission_pending} files require manual blueprint")

    # Violation Summary
    if ctx.report:
        print(f"📊 TOTAL VIOLATIONS: {len(ctx.report)}")
        from collections import Counter
        agent_counts = Counter(item.get('agent', 'Unknown') for item in ctx.report)
        for agent, count in agent_counts.most_common():
            print(f"   - {agent}: {count}")
    
    if dashboard_metrics:
        print(f"\n🌐 Web Dashboard: http://localhost:5000 (still running)")
        print("   Press Ctrl+C to stop...")
    
    print("="*70)


# ==============================================================================
# FACTORY FUNCTIONS
# ==============================================================================

def get_fission_manager(line_limit: int = 800, max_rounds: int = 3) -> FissionManager:
    """
    Factory function to create FissionManager instance.
    
    Args:
        line_limit: Maximum lines before triggering fission
        max_rounds: Maximum healing rounds before exhaustion
        
    Returns:
        FissionManager instance
    """
    return FissionManager(line_limit=line_limit, max_rounds=max_rounds)


def get_safety_guardrail(deletion_limit: int = 110) -> SafetyGuardrail:
    """
    Factory function to create SafetyGuardrail instance.
    
    Args:
        deletion_limit: Maximum lines that can be deleted
        
    Returns:
        SafetyGuardrail instance
    """
    return SafetyGuardrail(deletion_limit=deletion_limit)


def get_subatomic_engine(gemini_client: Optional[Any] = None) -> SubAtomicEngine:
    """
    Factory function to create SubAtomicEngine instance.
    
    Args:
        gemini_client: Optional Gemini client
        
    Returns:
        SubAtomicEngine instance
    """
    return SubAtomicEngine(gemini_client=gemini_client)


# ==============================================================================
# USAGE EXAMPLE
# ==============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Canon Validator One-File Runner")
    parser.add_argument(
        "--target", 
        type=str, 
        default="agentic_core", 
        help="Target folder for validation"
    )
    args = parser.parse_args()
    
    # Global mission timeout: 30 minutes
    MISSION_TIMEOUT = int(os.getenv("MISSION_TIMEOUT_SECONDS", "1800"))

    try:
        async def timed_mission():
            async with asyncio.timeout(MISSION_TIMEOUT):
                await run_mission(args.target)
        asyncio.run(timed_mission())
    except KeyboardInterrupt:
        print("\n[!] Mission interrupted by user")
    except asyncio.TimeoutError:
        print(f"\n[X] Mission timed out after {MISSION_TIMEOUT}s")
    except Exception as e:
        print(f"\n[X] Mission failed: {e}")
        traceback.print_exc()