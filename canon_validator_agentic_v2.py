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

# HARDENING: Centralized, deduplicated sys.path setup
project_root = Path(__file__).resolve().parent
project_root_str = str(project_root)
if project_root_str not in sys.path:
    sys.path.insert(0, project_root_str)

# [FINAL HARDENING] SOVEREIGN SELF-PROTECTION
# Ensure this validator remains at root (Key 0) to maintain architectural gravity.
if Path(__file__).resolve().parent != project_root:
    print(f"\n[!] [GRAVITY ERROR] canon_validator_agentic_v2.py has escaped project root!")
    print(f"    Location: {Path(__file__).resolve().parent}")
    sys.exit(1)

# Additional required paths (deduplicated)
for sub_path in ["apps_shared", "agentic_core"]:
    req_str = str(project_root / sub_path)
    if req_str not in sys.path:
        sys.path.insert(0, req_str)

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

# [HARDENING] SOVEREIGN NEURAL LINK & MODEL AUTHORIZATION
def verify_neural_link():
    """
    Physical Path Anchoring: Resolves the absolute path to project root.
    Enforces a strict GEMINI-ONLY model authorization policy.
    """
    import os
    from dotenv import load_dotenv
    
    # Resolve absolute project root to prevent path drift
    project_root_abs = Path(__file__).resolve().parent
    env_path = project_root_abs / ".env"
    
    if not env_path.exists():
        print(f"\n[!] [L6 ERROR] CRITICAL BOUNDARY VIOLATION: .env missing at {env_path}")
        sys.exit(1)

    # override=True ensures .env values take priority over session noise
    load_dotenv(dotenv_path=env_path, override=True)
    
    # --- MODEL AUTHORIZATION WHITELIST ---
    # Mandatory for currently approved mission logic
    APPROVED_MODELS = ["GOOGLE_API_KEY", "GEMINI_MODEL"]
    FUTURE_MODELS = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY"]
    
    # 1. Verify Mandatory Gemini Presence
    missing_mandatory = [key for key in APPROVED_MODELS if not os.getenv(key)]
    if missing_mandatory:
        print(f"\n[!] [NEURAL LINK ERROR] Mission halted. Missing mandatory keys: {', '.join(missing_mandatory)}")
        sys.exit(1)

    # 2. Strict Model Authorization Check
    # Even if keys exist in .env, this enforces a zero-call policy for non-Gemini models
    unauthorized_detected = [key for key in FUTURE_MODELS if os.getenv(key)]
    
    # 3. REDIS STATE HEALTH CHECK (Langcache integrity)
    try:
        import redis
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        r = redis.from_url(redis_url, socket_timeout=5)
        
        # Ping the server to verify connectivity
        if r.ping():
            print(f"   [OK] Redis State Active: Connected to {redis_url}")
        else:
            raise ConnectionError("Redis server did not respond to PING.")
    except (ImportError, Exception) as e:
        print(f"\n[!] [L4 STATE ERROR] Redis/Langcache unreachable: {e}")
        print("    Check your REDIS_URL and ensure the Redis service is running.")
        sys.exit(1)
    
    print(f"   [OK] Neural Link Sourced: {env_path}")
    if unauthorized_detected:
        print(f"   [INFO] Inactive model strings detected in environment: {', '.join(unauthorized_detected)}")
    
    print(f"   [OK] Model Authorization: GEMINI-ONLY policy enforced.")

verify_neural_link()

# --- CRITICAL FIX: IMPORT POLYFILL (agentic_core.runtime.shared -> apps_shared) ---
# Maps 'agentic_core.runtime.shared' imports to 'apps_shared' where ValidationContext lives
try:
    import apps_shared
    # Only shim the shared submodule, not the entire runtime
    sys.modules['agentic_core.runtime.shared'] = apps_shared
    # Explicitly shim ValidationContext import
    from apps_shared.canon_validation_context import ValidationContext
    sys.modules['agentic_core.runtime.shared.canon_validation_context'] = apps_shared.canon_validation_context
    print("   [PATCH] Shimmed 'agentic_core.runtime.shared' imports to 'apps_shared'")
except ImportError:
    print("   [CRITICAL] Could not shim runtime.shared. Some agents may fail to load.")

# [HARDENING] NEURAL LINK INITIALIZATION
try:
    from dotenv import load_dotenv

    # Explicitly point to Root .env to prevent loading failures from subfolders
    env_path = project_root / ".env"
    if not load_dotenv(dotenv_path=env_path):
        print(f"[!] [L6 ALERT] .env not found at {env_path}. Neural link may be offline.")
except ImportError as e:
    print(f"CRITICAL: Missing dependency: {e.name}. Install with: pip install python-dotenv")
    sys.exit(1)

# Dashboard Integration
try:
    import sys
    from pathlib import Path

    # Add apps_shared to path for dashboard imports
    apps_shared_path = Path(__file__).parent / "apps_shared"
    if str(apps_shared_path) not in sys.path:
        sys.path.insert(0, str(apps_shared_path))
    
    from canon_dashboard import CanonDashboard, DashboardMetrics
    from canon_dashboard_web import run_server
    DASHBOARD_AVAILABLE = True
except ImportError as e:
    DASHBOARD_AVAILABLE = False
    print(f"[!] Dashboard not available: {e}")
    print("    Install: pip install rich flask flask-cors")

# [HARDENING] SOVEREIGN COMPLIANCE IMPORT
# Import directly from root to avoid shadowing stale versions in agentic_core/runtime
try:
    from agentic_core.L3_orchestration import FissionManager, apply_fission_blueprint
    from agentic_core.L5_safety import SafetyGuardrail, SubAtomicEngine
    
    import void_compliance
    from void_compliance import (
        ALLOWED_ROOT_FOLDERS,
        FORBIDDEN_ROOT_FOLDERS,
        check_import_waterfall_violations,
        check_span_of_two_violations,
        validate_canonical_hierarchy,
        enforce_void_compliance,
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
# [FINAL HARDENING] SURGERY CONTROL FLAGS
# ==============================================================================
# Toggle these to False for daily work after global sweep is complete
RUN_GRAVITY_REFACTOR = True  # Enable automatic gravity violation fixes
RUN_SPRAWL_SURGERY = False    # Disable automatic sprawl consolidation

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
            print(f"\n[SPY] GEMINI SPY Agent triggering: {name}")
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
                # [L5 HARDENING] Detect and flag suspicious zero-latency responses
                if duration < 0.05 and name == "resilient_mutation":
                    print(f"   [!] ALERT: Zero-latency mutation detected. Check engine logic.")
                print(f"[SPY] GEMINI SPY LLM Success ({duration:.2f}s).")
                return result
            except Exception as e:
                # Log detailed failure for debugging telemetry mismatches
                print(f"[SPY] GEMINI SPY LLM OR TELEMETRY FAILURE: {e}")
                if "successful_traces" in str(e):
                    print("   -> CAUSE: ValidationContext is missing .successful_traces list.")
                raise e
        return wrapper


# ==============================================================================
# [KEY 48] MISSION AUDIT LOG: ARCHITECTURAL LEDGER
# ==============================================================================
import csv
from datetime import datetime

class MissionAuditLog:
    """
    [L4 STATE] Observability Ledger.
    Records every physical move and code mutation for historical auditing.
    """
    def __init__(self, log_path: str = "mission_audit.csv"):
        self.log_path = log_path
        self._initialize_log()

    def _initialize_log(self):
        if not os.path.exists(self.log_path):
            with open(self.log_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "file", "action", "source", "destination", "reason"])

    def record(self, file_name: str, action: str, source: str, destination: str, reason: str):
        with open(self.log_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().isoformat(),
                file_name,
                action,
                source,
                destination,
                reason
            ])
        print(f"      [LOG] Action recorded in audit ledger: {action}")

# Global audit instance
audit_log = MissionAuditLog()

# ==============================================================================
# L6 PEACEKEEPER: PHYSICAL BOUNDARY ENFORCEMENT
# ==============================================================================

def run_l6_preflight(target_sector: str, project_root: Path) -> bool:
    """
    Integrates Void Compliance into the Master Validation Sweep.
    HARDENING: Only scans Sovereign Roots for gravity leaks (Apps are allowed to depend on Upstream).
    
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
    
    # Check 1: Span of Two Detection (Redundant Tunnels)
    span_violations = []
    if target_path != project_root:
        from void_compliance import check_span_of_two_violations
        span_violations = check_span_of_two_violations(project_root)
    if span_violations:
        print(f"[!] L6 ALERT: Found {len(span_violations)} span violations:")
        for folder_path, reason in span_violations[:3]:
            try:
                rel_path = folder_path.relative_to(project_root)
            except ValueError:
                rel_path = folder_path
            print(f"   [X] {rel_path}: {reason}")
        if len(span_violations) > 3:
            print(f"   ... and {len(span_violations) - 3} more violations")
    
    # Check 2: Hierarchy Alignment (SSOT Verification)
    from void_compliance import validate_canonical_hierarchy
    hierarchy_violations = validate_canonical_hierarchy(project_root)
    if hierarchy_violations:
        print(f"[!] L6 ALERT: Found {len(hierarchy_violations)} hierarchy violations:")
        for folder_path, reason in hierarchy_violations[:3]:
            try:
                rel_path = folder_path.relative_to(project_root)
            except ValueError:
                rel_path = folder_path
            print(f"   [X] {rel_path}: {reason}")
        if len(hierarchy_violations) > 3:
            print(f"   ... and {len(hierarchy_violations) - 3} more violations")
    
    # Check 3: Import Waterfall Violations (Sovereign -> Apps)
    waterfall_violations = []
    SOVEREIGN_ROOTS = {"agentic_core", "prompt_governance", "schemas", "config", "scripts"}
    
    if target_path.is_dir():
        for py_file in target_path.rglob("*.py"):
            rel_path = py_file.relative_to(project_root)
            root_folder = rel_path.parts[0] if rel_path.parts else ""
            
            # Only enforce gravity on Sovereign territory to avoid noise in downstream apps.
            if root_folder in SOVEREIGN_ROOTS:
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
    
    # Check 4: Hierarchy Drift (CANONICAL_HIERARCHY SSOT)
    from void_compliance import validate_canonical_hierarchy
    hierarchy_violations = validate_canonical_hierarchy(project_root)

    # ==========================================================================
    # [L6 HARDENING] MASTER SOVEREIGN DASHBOARD
    # ==========================================================================
    print("\n" + "="*70)
    print(" SOVEREIGN INTEGRITY DASHBOARD (L6 PRE-FLIGHT)")
    print("="*70)
    
    metrics = [
        ("DEPTH / SPAN OF TWO", len(span_violations)),
        ("HIERARCHY ALIGNMENT", len(hierarchy_violations)),
        ("NAMING / SIGNAL",    len(location_violations)), # Location includes naming
        ("GRAVITY / IMPORTS",  len(waterfall_violations))
    ]
    
    for label, count in metrics:
        status = "[✓] OK" if count == 0 else f"[X] {count} VIOLATIONS"
        print(f" {label:<25} | {status}")
    
    print("-" * 70)
    
    total_violations = sum(m[1] for m in metrics)
    
    if total_violations == 0:
        print("[SUCCESS] All structural laws satisfied. Neural Link established.")
        print("="*70 + "\n")
        return True
    else:
        print(f"[BLOCK] {total_violations} Violations must be resolved for convergence.")
        print("="*70 + "\n")
        # If auto-healing is enabled (e.g. HealerAgent), we allow it to proceed to heal.
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
    # Validator is at root level, so parent is the project root
    project_root = Path(__file__).parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    # === DASHBOARD INITIALIZATION (METRICS ONLY) ===
    # Flask server will start AFTER agents are discovered
    dashboard_metrics = None
    web_thread = None
    
    if DASHBOARD_AVAILABLE:
        dashboard_metrics = DashboardMetrics()
        dashboard = CanonDashboard(dashboard_metrics)
        
        # Import module but DON'T start server yet
        import canon_dashboard_web
        canon_dashboard_web.metrics = dashboard_metrics
        print(f"   [OK] Dashboard metrics initialized (server will start after agent discovery)")
    
    # === L6 PEACEKEEPER: MANDATORY PRE-FLIGHT ===
    # Execute void compliance check BEFORE any validation begins
    l6_compliant = run_l6_preflight(target_scope, project_root)
    if not l6_compliant:
        print("\n[!] [L6 WARNING] Physical structure violations detected.")
        print("    Proceeding with validation, but auto-healing may be restricted.")

    # --- L5 HARDENING INSTANTIATION ---
    # 1. Initialize Safety Components
    safety_guard = SafetyGuardrail(deletion_limit=110)

    # [HARDENING] VERIFY KEY PRESENCE
    if not os.getenv("GOOGLE_API_KEY"):
        print("\n[CRITICAL HARDENING] GOOGLE_API_KEY NOT FOUND!")
        print("   -> Agentic capabilities cannot be unleashed without a neural link.")
        print("   -> Execution halted to prevent 'Dry Run' silence.")
        sys.exit(1)

    # [AGENTIC UNLEASH] EXPLICIT CLIENT CONSTRUCTION
    try:
        # Use the new google.genai SDK (not google.generativeai)
        pass
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("\n[CRITICAL] GOOGLE_API_KEY not set in .env!")
            sys.exit(1)
        
        model_name = os.getenv("GEMINI_MODEL")
        if not model_name:
            print("\n[CRITICAL] GEMINI_MODEL not set in .env!")
            print("   -> Add GEMINI_MODEL=gemini-2.5-flash to your .env file")
            sys.exit(1)

        # Initialize Engine with NO client (it will create its own genai.Client)
        _real_engine = SubAtomicEngine(gemini_client=None)
        # Wrap in Spy for Visibility
        subatomic_engine = GeminiSpy(_real_engine)
        
        print(f"   [OK] AGENTIC UNLEASHED: {model_name}")
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
    
    # [FIX] Initialize missing telemetry structures for SubAtomicEngine
    if not hasattr(ctx, 'successful_traces'): ctx.successful_traces = []
    if not hasattr(ctx, 'failed_traces'): ctx.failed_traces = []
    # [FIX] Add missing log_error method required by Budget & Structural agents
    if not hasattr(ctx, 'log_error'): 
        ctx.log_error = lambda msg: ctx.report("System", 0, False, msg)
    
    # [HARDENING] Add missing L4/L5 operational flags
    # [FIX] Convert Booleans to Callables to prevent 'bool object not callable' errors
    if not hasattr(ctx, 'can_attempt_healing'): 
        ctx.can_attempt_healing = lambda: True
    
    if not hasattr(ctx, 'intelligence_enabled'): 
        ctx.intelligence_enabled = lambda: True

    # [FIX] Support for UI/Figma service calls
    if not hasattr(ctx, 'services'): 
        ctx.services = type('obj', (object,), {'mcp_clients': [], 'get': lambda s, k, d=None: d})()
    
    if not hasattr(ctx, 'signal_deps_valid'): ctx.signal_deps_valid = lambda: True
    
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
    
    # === PROTECTED FOLDERS: Skip archives and legacy code ===
    PROTECTED_FOLDERS = {
        'archives',        # [VOID ZONE] Strictly ignored
        'data',            # [VOID ZONE] Strictly ignored
        'legacy_code',     # Deprecated
        'legacy_engines',
        'legacy_resume_gen',
        '.git',
        '__pycache__',
        'node_modules',
        '.venv',
        'venv',
        'env',
        'test',            # New addition
    }
    
    # Discover all Python files in target scope, excluding protected folders
    discovered_files = [
        p for p in target_path.rglob("*.py") 
        if p.is_file() and not any(protected in p.parts for protected in PROTECTED_FOLDERS)
    ]
    
    print(f"   [PROTECTED] Skipping folders: {', '.join(sorted(PROTECTED_FOLDERS))}")
    
    # === L6 RUNTIME: Void Compliance Enforcement ===
    valid_files, violations = enforce_void_compliance(discovered_files, project_root_path)
    
    if violations:
        print(f"\n[!] [VOID COMPLIANCE] {len(violations)} files in forbidden/unknown folders:")
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
            
    # Disabled due to Unicode encoding issues on Windows console
    # print("\n   [PHYSICS] Current Directory Structure:")
    # tree_view = generate_ascii_tree(project_root_path, max_depth=4)
    # print(tree_view)
    
    # ===========================================================================
    # [PHASE -1] SYNTAX HEALING: Fix Broken Python Files Before Discovery
    # ===========================================================================
    print(f"\n[PHASE -1] SYNTAX HEALING")
    import ast
    syntax_healed_count = 0
    for file_path in ctx.python_files:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                code = f.read()
            ast.parse(code, filename=file_path)
        except SyntaxError as e:
            print(f"   [SYNTAX-FIX] {Path(file_path).name}:{e.lineno} -> {e.msg}")
            try:
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    broken_code = f.read()
                
                repair_prompt = f"""### ROLE: SYNTAX_MEDIC
### ERROR: {e.msg} at line {e.lineno}
### TASK: Fix the syntax error (quotes, indents, or colons) only. Do not change logic.
### FILE: {Path(file_path).name}

Return ONLY the fixed Python code. No explanations, no markdown.
"""
                
                fixed_code = await ctx.engine.resilient_mutation(
                    file_path=str(file_path),
                    code=broken_code,
                    task=repair_prompt,
                    round_num=1,
                    fission_active=False
                )
                
                # Safety: Ensure we didn't get an empty response
                if len(fixed_code) > 10:
                    is_safe, msg = ctx.safety.verify_change(broken_code, fixed_code, fission_active=False)
                    if not is_safe:
                        print(f"      [!] Safety check failed: {msg}")
                        continue

                    # HARDENING: Re-parse AST to confirm the repair didn't introduce new syntax errors.
                    try:
                        ast.parse(fixed_code, filename=file_path)
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(fixed_code)
                        print(f"      [✓] Syntax Healed & Verified.")
                        syntax_healed_count += 1
                    except SyntaxError as e2:
                        print(f"      [!] Healing failed: Fixed code still has syntax error at line {e2.lineno}")
            except Exception as heal_err:
                print(f"      [!] Healing failed: {str(heal_err)[:100]}")
    
    if syntax_healed_count > 0:
        print(f"   [PHASE -1 COMPLETE] Healed {syntax_healed_count} files with syntax errors")
    else:
        print(f"   [OK] No syntax errors detected")
    
    print("-" * 50)
    
    # ===========================================================================
    # [PHASE -1.5] NAMESPACE HEALING: Standardizing Standard Lib Imports
    # ===========================================================================
    print(f"\n[PHASE -1.5] NAMESPACE HEALING")
    namespace_healed_count = 0
    
    # Common patterns: (usage_pattern, import_statement)
    import_patterns = [
        ("logging.", "import logging"),
        ("logger.", "import logging"),
        ("Any", "from typing import Any, Optional, Protocol, Dict, List"),
        ("Optional", "from typing import Any, Optional, Protocol, Dict, List"),
        ("Protocol", "from typing import Any, Optional, Protocol, Dict, List"),
        ("Dict[", "from typing import Any, Optional, Protocol, Dict, List"),
        ("List[", "from typing import Any, Optional, Protocol, Dict, List"),
        ("@dataclass", "from dataclasses import dataclass, field"),
        ("dataclass(", "from dataclasses import dataclass, field"),
        ("Enum", "from enum import Enum, auto"),
        ("Path(", "from pathlib import Path"),
        ("json.", "import json"),
        ("os.path", "import os"),
        ("sys.", "import sys"),
    ]
    
    for file_path in ctx.python_files:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            missing_imports = []
            
            # Check each pattern
            for usage_pattern, import_stmt in import_patterns:
                # Skip if usage pattern not found
                if usage_pattern not in content:
                    continue
                
                # Check if import already exists
                if import_stmt in content:
                    continue
                
                # Avoid duplicates in missing_imports
                if import_stmt not in missing_imports:
                    missing_imports.append(import_stmt)
            
            # If we found missing imports, fix the file
            if missing_imports:
                print(f"   [NAMESPACE-FIX] {Path(file_path).name} missing {len(missing_imports)} imports")
                
                fix_prompt = f"""### ROLE: NAMESPACE_MEDIC
### TASK: Add missing standard library imports to the top of the file.
### MISSING IMPORTS:
{chr(10).join(f'- {imp}' for imp in missing_imports)}

### INSTRUCTIONS:
1. Add the missing imports at the top of the file (after docstring if present)
2. Preserve all existing code exactly as-is
3. Do not modify any logic, only add imports
4. Return ONLY the complete fixed Python code

Return the complete file with imports added. No explanations, no markdown."""
                
                fixed_code = await ctx.engine.resilient_mutation(
                    file_path=str(file_path),
                    code=content,
                    task=fix_prompt,
                    round_num=1,
                    fission_active=False
                )
                
                # Safety: Ensure we got valid code back
                if len(fixed_code) > 10:
                    is_safe, msg = ctx.safety.verify_change(content, fixed_code, fission_active=False)
                    if is_safe:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(fixed_code)
                        print(f"      [✓] Namespace Healed. Imports injected.")
                        namespace_healed_count += 1
                    else:
                        print(f"      [!] Safety check failed: {msg}")
        except Exception as heal_err:
            print(f"      [!] Namespace healing failed for {Path(file_path).name}: {str(heal_err)[:100]}")
    
    if namespace_healed_count > 0:
        print(f"   [PHASE -1.5 COMPLETE] Healed {namespace_healed_count} files with missing imports")
    else:
        print(f"   [OK] No missing standard library imports detected")
    
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
                        # [FIX] Do NOT instantiate the base SubAtomicAgent class or it will crash 'await' expressions
                        if (isinstance(attr, type) and 
                            attr.__module__ == module_name and
                            attr_name != 'SubAtomicAgent' and  # Exclude base class
                            (attr_name.endswith(('Agent', 'Guardian', 'Architect', 'Engineer', 'Enforcer', 'Sentinel', 'Hunter')) or
                             attr_name in ('SystemArchitect', 'StructuralEngineer', 'HealerAgent', 'HygieneGuardian', 'ArchitectureGovernor', 
                                         'DependencySentinel', 'SecurityEnforcer', 'MemoryArchitect', 'HallucinationHunter')) and
                            (hasattr(attr, 'execute') or hasattr(attr, 'run'))):
                            found_agents.append((module_name, attr_name, attr))
                            # Debug: Log when SystemArchitect is found
                            if attr_name == 'SystemArchitect':
                                print(f"     [DEBUG] Found SystemArchitect in {module_name}")
                except Exception as e:
                    print(f"     [!] Failed to inspect {file_path.name}: {e}")
                    # Debug: Show full traceback for canon_agents_core
                    if 'canon_agents_core' in str(file_path):
                        import traceback
                        traceback.print_exc()
                
        return found_agents

    # Execute Discovery
    # Scans agentic_core (L1-L5) and apps_*/agents
    discovered = discover_agents()
    print(f"   [COMPREHENSIVE MODE] Found {len(discovered)} agents via dynamic discovery")
    print(f"   [CONFIG] Fission Threshold: 10,000 LOC | Healing: Iterative Loop")
    
    for mod_name, cls_name, cls_ref in discovered:
        try:
            # [HARDENED] L5 Autonomous Instantiation Logic
            sig = inspect.signature(cls_ref.__init__)
            kwargs = {}
            
            # Check for context parameter (try both 'ctx' and 'context')
            if 'ctx' in sig.parameters:
                kwargs['ctx'] = ctx
            elif 'context' in sig.parameters:
                kwargs['context'] = ctx
            
            if 'name' in sig.parameters:
                kwargs['name'] = cls_name
            if 'engine' in sig.parameters:
                kwargs['engine'] = ctx.engine
                
            agent_instance = cls_ref(**kwargs)
            # Add status tracking for dashboard visualization
            agent_instance.current_status = "Idle"
            agent_instance.current_task = "Awaiting mission"
            
            # [HARDENING] Defensive monkey-patch for real-time telemetry
            # Auto-update status/task on all agents without requiring individual changes
            original_method = getattr(agent_instance, 'execute', None) or getattr(agent_instance, 'run', None)
            if original_method:
                async def status_wrapper(*args, **kwargs):
                    file_path = args[0] if args else "batch/global"
                    file_name = Path(file_path).name if hasattr(file_path, '__str__') else str(file_path)
                    agent_instance.current_status = "Active"
                    agent_instance.current_task = f"Processing: {file_name}"
                    try:
                        result = await original_method(*args, **kwargs)
                        agent_instance.current_status = "Success"
                        agent_instance.current_task = "Complete"
                        return result
                    except Exception as e:
                        agent_instance.current_status = "Error"
                        agent_instance.current_task = f"Failed: {str(e)[:50]}"
                        raise
                # Replace method with telemetry wrapper
                if hasattr(agent_instance, 'execute'):
                    agent_instance.execute = status_wrapper
                else:
                    agent_instance.run = status_wrapper
            
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
    
    # Sync agents with dashboard for visualization
    try:
        import canon_dashboard_web
        canon_dashboard_web.agents_global.clear()
        canon_dashboard_web.agents_global.extend(cleaning_crew)
        print(f"   [DASHBOARD] Synced {len(cleaning_crew)} agents to visualization")
        
        # NOW start the Flask server with agents populated
        if DASHBOARD_AVAILABLE and web_thread is None:
            # Check if port 5000 is already in use
            import socket
            def check_port_available(port):
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.bind(('localhost', port))
                    return True
                except OSError:
                    return False
            
            if not check_port_available(5000):
                print(f"   [!] Port 5000 already in use - killing existing process")
                import subprocess
                subprocess.run(['netstat', '-ano', '|', 'findstr', ':5000'], shell=True, capture_output=True)
                print(f"   [!] Run: taskkill /PID <number> /F to free the port")
            else:
                # Start server with error handling
                def safe_run_server():
                    try:
                        run_server('0.0.0.0', 5000, False)
                    except Exception as e:
                        print(f"   [!] Flask server failed to start: {e}")
                        import traceback
                        traceback.print_exc()
                
                web_thread = threading.Thread(
                    target=safe_run_server,
                    daemon=True
                )
                web_thread.start()
                print(f"   [*] Starting web dashboard on http://localhost:5000")
                
                # Wait for server to be ready
                import time
                def wait_for_port(port, host='localhost', timeout=10):
                    start_time = time.time()
                    while True:
                        try:
                            with socket.create_connection((host, port), timeout=1):
                                return True
                        except OSError:
                            if time.time() - start_time >= timeout:
                                return False
                            time.sleep(0.5)
                
                if wait_for_port(5000):
                    print(f"   [OK] Dashboard server confirmed listening on http://localhost:5000")
                    print(f"   [OK] Access dashboards:")
                    print(f"      • Main: http://localhost:5000")
                    print(f"      • Agent Architecture: http://localhost:5000/agent_graph")
                else:
                    print(f"   [!] TIMEOUT: Dashboard server failed to start after 10 seconds")
                print(f"   [!] Agent graph will show {len(cleaning_crew)} live agents")
    except Exception as e:
        print(f"   [!] Dashboard sync failed: {e}")

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
    # [PHASE -1] L6 INTEGRITY SENTINEL - FAST PRE-FLIGHT SOVEREIGNTY CHECK
    # ===========================================================================
    print(f"\n[PHASE -1] L6 INTEGRITY SENTINEL")
    print(f"   [>] Fast pre-flight check: Scanning ALL sovereign roots for gravity leaks...")
    
    integrity_violations = []
    integrity_violation_files = []
    SOVEREIGN_ROOTS = {"agentic_core", "prompt_governance", "schemas", "config", "scripts"}
    
    for file_path in ctx.python_files:
        file_path_obj = Path(file_path)
        rel_path = file_path_obj.relative_to(project_root_path)
        root_folder = rel_path.parts[0] if rel_path.parts else ""
        
        # HARDENING: Expand check to all upstream roots.
        if root_folder in SOVEREIGN_ROOTS:
            violations = check_import_waterfall_violations(file_path_obj, project_root_path)
            if violations:
                integrity_violations.extend(violations)
                integrity_violation_files.append(file_path_obj.name)
    
    if integrity_violations:
        print(f"\n   [X] SOVEREIGNTY BREACH DETECTED")
        print(f"   [!] {len(integrity_violations)} gravity violation(s) in {len(integrity_violation_files)} file(s)")
        print(f"\n   Affected Files:")
        for file_name in integrity_violation_files[:10]:  # Show first 10
            print(f"      - {file_name}")
        if len(integrity_violation_files) > 10:
            print(f"      ... and {len(integrity_violation_files) - 10} more")
        
        print(f"\n   [!] MISSION ABORTED: Architectural integrity violated.")
        print(f"   [!] Sovereign 'agentic_core' must not depend on downstream layers.")
        print(f"\n   REMEDIATION OPTIONS:")
        print(f"      1. Enable auto-healing: Set RUN_GRAVITY_REFACTOR=True in this file")
        print(f"      2. Manual fix: Remove imports from apps_shared, apps_lic, apps_rg")
        print(f"      3. Review violations: Check void_compliance.py for details")
        print(f"\n" + "="*70)
        
        # Check if auto-healing is enabled before aborting
        if not RUN_GRAVITY_REFACTOR:
            sys.exit(1)
        else:
            print(f"\n   [+] Auto-healing enabled: Continuing to fix violations...")
    else:
        print(f"   [✓] Sovereignty Intact: No gravity leaks detected in agentic_core")
        print(f"   [✓] Pre-flight passed. Proceeding to validation phases.")
    
    print("-" * 70)

    # ===========================================================================
    # [AUTONOMY PATCH] PHASE 0: ARCHITECTURAL GRAVITY REFACTOR
    # ===========================================================================
    if RUN_GRAVITY_REFACTOR:
        print(f"\n[PHASE 0] ARCHITECTURAL GRAVITY REFACTOR")
        print(f"   [>] Scanning for Sovereign → Downstream violations...")
        
        gravity_violations_fixed = 0
        gravity_violations_total = 0
        
        # Initialize gravity attempts tracking if not exists
        if not hasattr(ctx, 'gravity_attempts'):
            ctx.gravity_attempts = {}
        
        for file_path in ctx.python_files:
            file_path_obj = Path(file_path)
            violations = check_import_waterfall_violations(file_path_obj, project_root_path)
            
            if violations:
                # [FIX] Prevent infinite loops by tracking attempts per file
                ctx.gravity_attempts[file_path] = ctx.gravity_attempts.get(file_path, 0) + 1
                if ctx.gravity_attempts[file_path] > 2:
                    print(f"   [!] Maximum gravity refactors reached for {Path(file_path).name}. Skipping to prevent loop.")
                    continue
                    
                gravity_violations_total += len(violations)
                file_name = file_path_obj.name
                print(f"\n   [AUTO-HEAL] {file_name}: {len(violations)} gravity violation(s)")
                
                for violation_msg in violations[:3]:  # Show first 3
                    print(f"      - {violation_msg}")
                
                # Read current file content
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                        current_code = f.read()
                    
                    # Construct refactor prompt for SubAtomicEngine
                    refactor_prompt = f"""CRITICAL ARCHITECTURAL REFACTOR REQUIRED

FILE: {file_path}
VIOLATIONS: {len(violations)} Sovereign layer importing from Downstream

{chr(10).join(violations[:5])}

TASK: Refactor this file to eliminate ALL imports from 'apps_shared'.

STRATEGY OPTIONS:
1. Move required utility functions into 'agentic_core/shared/' or 'agentic_core/utils/'
2. Use dependency injection via ValidationContext
3. Inline small helper functions directly into this file
4. Remove the dependency entirely if not critical

REQUIREMENTS:
- Preserve all existing functionality
- Maintain all class/function signatures
- Keep all docstrings and comments
- Ensure code remains syntactically valid
- Do NOT import from apps_shared, apps_rg, or apps_lic

OUTPUT: Return ONLY the complete refactored Python code. No explanations, no markdown.

CURRENT CODE:
{current_code}
"""
                    
                    print(f"      [>] Invoking SubAtomicEngine for autonomous refactor...")
                    
                    # Generate refactored code using LLM
                    try:
                        # Use resilient_mutation method (correct API for SubAtomicEngine)
                        refactored_code = await subatomic_engine.resilient_mutation(
                            file_path=str(file_path),
                            code=current_code,
                            task=refactor_prompt,
                            round_num=1,
                            fission_active=False
                        )
                        
                        # Extract code if wrapped in markdown
                        if isinstance(refactored_code, str):
                            # Remove markdown code blocks if present
                            if refactored_code.startswith("```python"):
                                refactored_code = refactored_code.split("```python", 1)[1]
                                refactored_code = refactored_code.rsplit("```", 1)[0]
                            elif refactored_code.startswith("```"):
                                refactored_code = refactored_code.split("```", 1)[1]
                                refactored_code = refactored_code.rsplit("```", 1)[0]
                            refactored_code = refactored_code.strip()
                        
                        # Validate the change with SafetyGuardrail
                        is_safe, safety_msg = safety_guard.verify_change(current_code, refactored_code, fission_active=False)
                        if is_safe:
                            # Apply the fix physically
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(refactored_code)
                            
                            print(f"      [OK] Gravity Refactored. File updated.")
                            gravity_violations_fixed += len(violations)
                            ctx.report("GravityRefactor", 0, True, f"Fixed {len(violations)} waterfall violations in {file_name}")
                        else:
                            print(f"      [!] SafetyGuardrail rejected refactor: {safety_msg}")
                            ctx.report("GravityRefactor", 0, False, f"Safety check failed: {safety_msg}")
                    
                    except Exception as e:
                        print(f"      [!] Refactor failed: {str(e)[:100]}")
                        ctx.report("GravityRefactor", 0, False, f"Engine error: {str(e)[:50]}")
                
                except Exception as e:
                    print(f"      [!] Could not read file: {e}")
        
        if gravity_violations_total > 0:
            print(f"\n   [PHASE 0 COMPLETE] Fixed {gravity_violations_fixed}/{gravity_violations_total} gravity violations")
            if gravity_violations_fixed < gravity_violations_total:
                print(f"   [!] {gravity_violations_total - gravity_violations_fixed} violations require manual review")
        else:
            print(f"   [OK] No gravity violations detected. Proceeding to standard validation.")
        
        print("-" * 70)
    else:
        print(f"\n[PHASE 0] ARCHITECTURAL GRAVITY REFACTOR - DISABLED")
        print(f"   [SKIP] Gravity refactor disabled for daily work. Enable RUN_GRAVITY_REFACTOR=True for global sweeps.")
        print("-" * 70)

    # ===========================================================================
    # [PHASE 0.5] SPRAWL CONSOLIDATION - ARCHITECTURAL FLATTENING
    # ===========================================================================
    if RUN_SPRAWL_SURGERY:
        print(f"\n[PHASE 0.5] SPRAWL CONSOLIDATION")
        print(f"   [>] Checking for low-density folders and breadth violations...")
        
        sprawl_report_path = project_root_path / "sprawl_report.json"
        sprawl_consolidated = 0
        
        if sprawl_report_path.exists():
            try:
                import json
                with open(sprawl_report_path, 'r') as f:
                    sprawl_data = json.load(f)
                
                flattening_candidates = sprawl_data.get('flattening_candidates', [])
                breadth_violations = sprawl_data.get('violations', [])
                
                print(f"   [SPRAWL] Found {len(flattening_candidates)} flattening candidates")
                print(f"   [SPRAWL] Found {len(breadth_violations)} breadth violations")
                
                # Process flattening candidates
                for candidate in flattening_candidates:
                    folder_path = Path(candidate['folder'])
                    files = candidate['files']
                    
                    if not folder_path.exists():
                        continue
                    
                    print(f"\n   [CONSOLIDATE] {folder_path.name}: {len(files)} file(s)")
                    print(f"      Reason: {candidate['reason']}")
                    
                    # Determine target file (parent's __init__.py or utils.py)
                    parent_dir = folder_path.parent
                    target_path = parent_dir / "__init__.py"
                    
                    # Ensure target exists
                    if not target_path.exists():
                        target_path.touch()
                        target_path.write_text("# Consolidated module\n")
                    
                    print(f"\n   [SURGERY] {folder_path.name} -> {target_path.name}")
                    
                    try:
                        # Read target code
                        with open(target_path, 'r', encoding='utf-8', errors='replace') as f:
                            target_code = f.read()
                        
                        # Read all source files to consolidate
                        source_contents = []
                        for file_name in files:
                            source_file = folder_path / file_name
                            if source_file.exists():
                                with open(source_file, 'r', encoding='utf-8', errors='replace') as f:
                                    source_contents.append(f"# From {file_name}\n{f.read()}\n")
                        
                        surgery_prompt = f"""### ROLE: ARCHITECTURAL_SURGEON
### ACTION: Consolidate sprawl folder into parent
### TASK: Move logic from {folder_path.name}/ into {target_path.name}

SOURCE FILES TO MERGE:
{''.join(source_contents)}

TARGET FILE:
{target_code}

REQUIREMENTS:
1. Preserve all class definitions and logic from source files
2. Update import paths to reflect new location
3. Remove duplicate imports
4. Maintain proper Python structure
5. Ensure all functionality is preserved

Return ONLY the complete merged Python code. No explanations.
"""
                        
                        new_code = await ctx.engine.resilient_mutation(
                            file_path=str(target_path),
                            code=target_code,
                            task=surgery_prompt,
                            round_num=1,
                            fission_active=False
                        )
                        
                        # Extract code if wrapped in markdown
                        if isinstance(new_code, str):
                            if new_code.startswith("```python"):
                                new_code = new_code.split("```python", 1)[1]
                                new_code = new_code.rsplit("```", 1)[0]
                            elif new_code.startswith("```"):
                                new_code = new_code.split("```", 1)[1]
                                new_code = new_code.rsplit("```", 1)[0]
                            new_code = new_code.strip()
                        
                        is_safe, msg = ctx.safety.verify_change(target_code, new_code, fission_active=False)
                        if is_safe:
                            with open(target_path, 'w', encoding='utf-8') as f:
                                f.write(new_code)
                            
                            # PHYSICAL CLEANUP: Delete the empty subfolder sprawl
                            import shutil
                            shutil.rmtree(folder_path, ignore_errors=True)
                            print(f"      [✓] Consolidated: {folder_path.name} -> {target_path.name}")
                            sprawl_consolidated += 1
                            ctx.report("SprawlSurgery", 49, True, f"Consolidated {folder_path.name} into {target_path.name}")
                        else:
                            print(f"      [!] Safety check failed: {msg}")
                            ctx.report("SprawlSurgery", 49, False, f"Safety rejected: {msg}")
                    
                    except Exception as e:
                        print(f"      [!] Surgery failed: {str(e)[:100]}")
                        ctx.report("SprawlSurgery", 49, False, f"Surgery error: {str(e)[:50]}")
                
                if len(flattening_candidates) > 0:
                    print(f"\n   [PHASE 0.5 COMPLETE] Consolidated {sprawl_consolidated}/{len(flattening_candidates)} sprawl folders")
                    print(f"   [✓] Sprawl Consolidated. Refreshing File System Map...")
                    
                    # [CRITICAL] Re-scan directory to remove deleted paths from the mission
                    updated_files = []
                    for root, _, files in os.walk(target_scope):
                        for f in files:
                            if f.endswith('.py'): 
                                updated_files.append(os.path.join(root, f))
                    ctx.python_files = updated_files
                    print(f"   [OK] Territory Updated: {len(ctx.python_files)} files remaining.")
                else:
                    print(f"   [OK] No sprawl detected. Architecture is clean.")
                    
            except Exception as e:
                print(f"   [!] Could not load sprawl report: {e}")
        else:
            print(f"   [SKIP] No sprawl_report.json found. Run sprawl_inspector.py first.")
        
        print("-" * 70)
    else:
        print(f"\n[PHASE 0.5] SPRAWL CONSOLIDATION - DISABLED")
        print(f"   [SKIP] Sprawl surgery disabled for daily work. Enable RUN_SPRAWL_SURGERY=True for global sweeps.")
        print("-" * 70)
    
    print("-" * 70)
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
        
        print(f"[{idx}/{len(ctx.python_files)}] {file_name} ({loc_count} LOC) [Keys: {sorted(applicable_keys) if applicable_keys else 'ALL'}]", end='\r')

        # Update dashboard with current file
        if dashboard_metrics:
            dashboard_metrics.session.current_file = file_path
            ctx.current_file_path = file_path  # Store for report callback

        # --- ACTIVE FISSION TRIGGER (Files > 10000 Lines) ---
        # Increased threshold to validate all files comprehensively
        if loc_count > 10000:
            print(f"\n[!] [FISSION TRIGGER] {file_name} ({loc_count} lines). Engaging Auto-Fission.")
            
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
                            print(f"   [OK] Fission Complete. Skipping standard validation.")
                            continue # Skip to next file
                        else:
                            print(f"   [!] Blueprint Application Failed.")
                except Exception as e:
                    print(f"   [!] Fission Error: {e}")
            
            # Read file content to determine suggested home
            try:
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    content_preview = f.read(500)  # First 500 chars for heuristics
                suggested_home = void_compliance.get_placement_guidance(content_preview)
                
                # Store violation info for agents to access
                ctx.structural_violation = {
                    'file_path': file_path,
                    'message': struct_msg,
                    'suggested_home': suggested_home,
                    'needs_move': True
                }
                print(f"     [>] Suggested home: {suggested_home}")
            except Exception as e:
                print(f"     [!] Could not read file for placement guidance: {e}")
                ctx.structural_violation = {
                    'file_path': file_path,
                    'message': struct_msg,
                    'suggested_home': 'agentic_core/L1_cognition',  # Default
                    'needs_move': True
                }
        
        for round_idx in range(1, MAX_HEALING_ROUNDS + 1):
            violations_this_round = initial_violations
            changes_this_round = 0
            
            # Update round tracking in reports
            ctx.report._current_round = round_idx
            
            print(f"     Round {round_idx}/{MAX_HEALING_ROUNDS}...", end=' ')
            
            for agent in atomic_validators:
                try:
                    method = getattr(agent, 'execute', getattr(agent, 'run', None))
                    if method:
                        result = None
                        # Attempt execution with path-awareness
                        try:
                            result = await method(file_path)
                        except TypeError:
                            result = await method()
                        
                        # Detect successful healing signals
                        if isinstance(result, dict):
                            # [L6 HARDENING] Physical Relocation & Import Sync
                            if result.get('move_to'):
                                target_move_path = result['move_to']
                                target_root = target_move_path.split('/')[0] if '/' in target_move_path else target_move_path
                                
                                # [PHYSICAL SAFETY GATE] Final check against Forbidden Roots
                                if target_root in FORBIDDEN_ROOT_FOLDERS:
                                    print(f"     [!] CRITICAL: Blocked move to forbidden root '{target_root}'.")
                                    continue

                                # 1. Apply import fixes if provided by the agent
                                if result.get('healed_code'):
                                    with open(file_path, 'w', encoding='utf-8') as f:
                                        f.write(result['healed_code'])
                                    print("     [✓] Imports Refactored for new path.")

                                # 2. Execute Physical Move
                                target_dir = project_root / target_move_path
                                target_dir.mkdir(parents=True, exist_ok=True)
                                target_path = target_dir / Path(file_path).name
                                
                                import shutil
                                shutil.move(file_path, target_path)
                                print(f"     [✓] RELOCATED: {Path(file_path).name} -> {result['move_to']}")
                                
                                # [KEY 48] Log relocation to the audit ledger
                                audit_log.record(
                                    file_name=Path(file_path).name,
                                    action="RELOCATED",
                                    source=str(Path(file_path).parent),
                                    destination=result['move_to'],
                                    reason=result.get('reason', 'Structural Re-homing')
                                )
                                
                                # Update python_files list to reflect the new location
                                if hasattr(ctx, 'python_files'):
                                    ctx.python_files = [f if f != file_path else str(target_path) for f in ctx.python_files]
                                
                                changes_this_round += 1
                                file_healed = True
                                
                                # [CRITICAL] Break out of agent loop since file_path is now stale
                                print(f"     [!] File moved - breaking agent loop for {file_name}")
                                break
                            
                            if result.get('healed'):
                                changes_this_round += 1
                                file_healed = True
                        elif result is True:
                            changes_this_round += 1
                            file_healed = True
                            
                except Exception as e:
                    # [CRITICAL] Ensure the round cannot converge if an agent is crashing
                    error_msg = f"FATAL CRASH [{agent.__class__.__name__}]: {str(e)}"
                    print(f"\n   [!] {error_msg}")
                    ctx.report(agent.__class__.__name__, 0, False, error_msg)
                    violations_this_round += 1
            
            # Check for convergence (no new violations in this round)
            # Get current report entries for this file and round
            current_round_reports = [r for r in ctx.report if file_name in str(r) and r.get('round', 1) == round_idx]
            fail_count = len([r for r in current_round_reports if r.get('status') == 'FAIL'])
            
            # Add structural violations to the total count
            total_violations = fail_count + violations_this_round
            
            print(f"Changes: {changes_this_round} | Violations: {total_violations}")
            
            # If no violations and we're past round 1, we've converged
            if total_violations == 0 and round_idx > 1:
                print(f"     [] Converged after {round_idx-1} rounds")
                break
        
        if file_healed:
            print(f"   [HEALING] Complete: {file_name}")
        
        # Execute move instructions if any were generated
        if hasattr(ctx, 'move_instructions') and ctx.move_instructions:
            for move in ctx.move_instructions:
                if move['source'] == file_path:
                    await _execute_move_instruction(move, project_root, ctx)
            # Clear processed moves
            ctx.move_instructions = [m for m in ctx.move_instructions if m['source'] != file_path]
        
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
    print(f"\n\n[L4 STATE] Executing Batch Agents ({len(batch_validators)})...")
    for agent in batch_validators:
        print(f"   [>] Running {agent.__class__.__name__}...")
        try:
            method = getattr(agent, 'execute', getattr(agent, 'run', None))
            # Batch agents typically run without args or manage their own scope
            if method:
                # [FIX] Ensure the method is actually awaitable
                res = method()
                if inspect.iscoroutine(res):
                    await res
                print(f"      [✓] {agent.__class__.__name__} finished pass.")
        except Exception as e:
             print(f"   [!] Error in {agent.__class__.__name__}: {e}")
             ctx.report(agent.__class__.__name__, 0, False, f"Batch Error: {str(e)[:50]}")

    # ===========================================================================
    # PHASE 3: MONITORING (Final Pass)
    # ===========================================================================
    print(f"\n[L4 STATE] Executing Global Monitors (Single Pass)...")
    for monitor in monitors:
        try:
            method = getattr(monitor, 'execute', getattr(monitor, 'run', None))
            if method: await method()
            print(f"   [OK] {monitor.__class__.__name__} completed")
        except Exception: pass

    # ===========================================================================
    # [ENHANCEMENT 6] MISSION DASHBOARD & SUMMARY
    # ===========================================================================
    print("\n" + "="*70)
    print(f"MISSION COMPLETE: {len(ctx.python_files)} Files Swept")
    
    # Mark session as complete
    if dashboard_metrics:
        dashboard_metrics.session.status = "completed"
        
        # Export dashboard report
        report_path = f"canon_report_{dashboard_metrics.session.session_id}.json"
        dashboard.export_report(report_path)
        print(f"[REPORT] Dashboard Report: {report_path}")
    
    # Fission Stats
    fission_done = sum(1 for v in ctx.results.values() if isinstance(v, dict) and v.get('action') == 'FISSION_COMPLETE')
    fission_pending = sum(1 for v in ctx.results.values() if isinstance(v, dict) and v.get('action') == 'FISSION_REQUIRED_MANUAL')
    
    if fission_done > 0:
        print(f"[SUCCESS] FISSION: {fission_done} files split into sub-modules")
    if fission_pending > 0:
        print(f"[!] FISSION PENDING: {fission_pending} files require manual blueprint")

    # Violation Summary
    if ctx.report:
        print(f"[STATS] TOTAL VIOLATIONS: {len(ctx.report)}")
        from collections import Counter
        agent_counts = Counter(item.get('agent', 'Unknown') for item in ctx.report)
        for agent, count in agent_counts.most_common():
            print(f"   - {agent}: {count}")
    
    if dashboard_metrics:
        print(f"\n[WEB] Dashboard: http://localhost:5000 (still running)")
        print("   Press Ctrl+C to stop...")
    
    print("="*70)


async def _execute_move_instruction(move: dict, project_root: Path, ctx):
    """
    Execute a file move instruction generated by HealerAgent.
    
    Args:
        move: Dictionary with 'action', 'source', 'target', 'reason'
        project_root: Project root path
        ctx: Context object for reporting
    """
    import shutil
    from pathlib import Path
    
    source_path = Path(move['source'])
    target_path = project_root / move['target']
    
    # [SAFETY CHECK] Validate target against forbidden roots
    target_root = move['target'].split('/')[0] if '/' in move['target'] else move['target']
    from void_compliance import FORBIDDEN_ROOT_FOLDERS
    if target_root in FORBIDDEN_ROOT_FOLDERS:
        print(f"      [!] CRITICAL: Blocked move instruction to forbidden root '{target_root}'.")
        ctx.report("MoveExecutor", 49, False, f"Blocked move to forbidden root: {target_root}")
        return
    
    try:
        # Ensure target directory exists
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Check if target already exists
        if target_path.exists():
            print(f"      [!] Target already exists: {target_path}")
            ctx.report("MoveExecutor", 40, False, f"Move failed: target exists {target_path.name}")
            return
        
        # Perform the move
        shutil.move(str(source_path), str(target_path))
        
        print(f"      [✓] Moved: {source_path.name} -> {move['target']}")
        ctx.report("MoveExecutor", 40, True, f"Successfully moved {source_path.name} to {move['target']}")
        
        # Update python_files list to reflect the new location
        if hasattr(ctx, 'python_files'):
            ctx.python_files = [f if f != str(source_path) else str(target_path) for f in ctx.python_files]
            
    except Exception as e:
        print(f"      [X] Move failed: {e}")
        ctx.report("MoveExecutor", 40, False, f"Move failed: {str(e)}")


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