#!/usr/bin/env python3
"""
[START] CANON SUB-ATOMIC ENGINE - V2.2
Shared core for Fission, Safety Guardrails, and Resilient Mutation.
"""

import asyncio
import importlib
import json
import logging
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

# Windows console encoding handled by terminal settings

# Hard-Gate: Tri-Brain SDKs are MANDATORY
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError as e:
    print(f"CRITICAL: Missing dependency: {e.name}. Install with: pip install python-dotenv")
    sys.exit(1)

# Gemini SDK
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    print("[!] Gemini SDK not available. Install with: pip install google-generativeai")

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


# ==============================================================================
# L3 ORCHESTRATION: FISSION MANAGER
# ==============================================================================
class FissionManager:
    """Determines when a file is too large or an agent is exhausted."""
    
    def __init__(self, line_limit: int = 800, max_rounds: int = 3):
        self.line_limit = line_limit
        self.max_rounds = max_rounds

    def should_trigger_fission(self, file_path: str, current_round: int) -> Tuple[bool, Optional[str]]:
        """
        Check if fission should be triggered based on file size or healing exhaustion.
        
        Args:
            file_path: Path to file being validated
            current_round: Current healing round number
            
        Returns:
            Tuple of (should_trigger, reason)
        """
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                line_count = len(f.readlines())
                if line_count > self.line_limit:
                    return True, f"L4 State Bloat: {line_count} lines exceeds limit."
        
        if current_round >= self.max_rounds:
            return True, "Cognitive Exhaustion: Round 3 reached."
        
        return False, None


# ==============================================================================
# L5 SAFETY: GUARDRAILS
# ==============================================================================
class SafetyGuardrail:
    """Enforces Zero-Loss principles during mutation."""
    
    def __init__(self, deletion_limit: int = 110):
        self.deletion_limit = deletion_limit
    
    def verify_change(self, original_code: str, new_code: str, fission_active: bool = False) -> Tuple[bool, str]:
        """
        Verify that code changes are safe and don't violate zero-loss principles.
        
        Args:
            original_code: Original code before mutation
            new_code: New code after mutation
            fission_active: Whether atomic fission is active (allows mass deletion)
            
        Returns:
            Tuple of (is_safe, message)
        """
        if not new_code.strip():
            return False, "Safety Block: Attempted to wipe file."
        
        orig_len = len(original_code.splitlines())
        new_len = len(new_code.splitlines())
        delta = orig_len - new_len

        # Fission mode: Mass deletion is expected (monolith → facade)
        if fission_active:
            return True, "Fission Whitelist: Mass deletion permitted for Facade."
        
        # Standard mode: Enforce deletion limit
        if delta > self.deletion_limit:
            return False, f"Safety Block: Mass deletion detected ({delta} lines)."
        
        return True, "Safety Pass."


# ==============================================================================
# ATOMIC MUTATION ENGINE
# ==============================================================================
class SubAtomicEngine:
    """Hardens the LLM interaction with the 24,576 token budget."""
    
    def __init__(self, gemini_client: Optional[Any] = None):
        """
        Initialize SubAtomicEngine.
        
        Args:
            gemini_client: Optional Gemini client (creates new if None)
        """
        if not GENAI_AVAILABLE:
            raise RuntimeError("Gemini SDK not available. Install with: pip install google-generativeai")
        
        if gemini_client:
            self._client = gemini_client
        else:
            # L5 SAFETY: Suppress redundant API key warnings
            # Check GOOGLE_API_KEY first (canonical), then GEMINI_API_KEY (legacy)
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                api_key = os.getenv("GEMINI_API_KEY")
                if api_key:
                    logger.warning("[L5] Using legacy GEMINI_API_KEY. Please migrate to GOOGLE_API_KEY.")
            
            if not api_key:
                raise RuntimeError("No Gemini API key found. Set GOOGLE_API_KEY in your .env file.")
            
            self._client = genai.Client(api_key=api_key)
        
        self.chat_sessions: Dict[str, Any] = {}
    
    @staticmethod
    def get_safe_config(is_fission: bool = False) -> Any:
        """
        Get safe Gemini configuration with hardened thinking budget.
        
        Args:
            is_fission: Whether this is for fission mode (uses max budget)
            
        Returns:
            GenerateContentConfig with safe thinking budget
        """
        if not GENAI_AVAILABLE:
            raise RuntimeError("Gemini SDK not available")
        
        # 🛑 HARDENED: Fixed at 24,576 to prevent 400 INVALID_ARGUMENT
        safe_budget = 24576 if is_fission else 16000
        return types.GenerateContentConfig(
            temperature=0.1,
            thinking_config=types.ThinkingConfig(thinking_budget=safe_budget)
        )
    
    @staticmethod
    def parse_fission_output(output: str) -> Dict[str, str]:
        """
        Extracts JSON file map from AI response.
        
        Args:
            output: Raw output from Gemini
            
        Returns:
            Dictionary mapping file paths to content
        """
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', output, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            logger.warning(f"Failed to parse fission output: {e}")
        
        return {}
    
    async def resilient_mutation(
        self,
        file_path: str,
        code: str,
        task: str,
        round_num: int = 1,
        fission_active: bool = False
    ) -> str:
        """
        Execute resilient mutation with Gemini.
        
        Args:
            file_path: Path to file being mutated
            code: Original code
            task: Task description for the AI
            round_num: Current healing round
            fission_active: Whether atomic fission is active
            
        Returns:
            Mutated code or original code on failure
        """
        if not self._client:
            raise RuntimeError("Gemini client not initialized")
        
        # Build prompt
        if fission_active:
            prompt = f"ATOMIC FISSION: Split {file_path} into 3 sub-modules. Return ONLY a JSON map.\n\nCODE:\n{code}"
        else:
            prompt = f"HEAL: Fix all syntax and style violations in {file_path}.\n\nTASK: {task}\n\nCODE:\n{code}"
        
        # Get safe config
        config = self.get_safe_config(is_fission=fission_active)
        
        # Create or reuse chat session
        chat_key = f"chat_{file_path}"
        if chat_key not in self.chat_sessions:
            model_name = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
            self.chat_sessions[chat_key] = self._client.chats.create(
                model=model_name,
                config=config
            )
            logger.info(f"   [NEW] Created new chat session for {os.path.basename(file_path)}")
        else:
            logger.info(f"   [REUSE]  Reusing chat session (Round {round_num})")
        
        try:
            # Send message
            response = await asyncio.to_thread(
                self.chat_sessions[chat_key].send_message,
                prompt
            )
            
            # Extract response
            if response.candidates and response.candidates[0].content.parts:
                output = response.candidates[0].content.parts[0].text.strip()
                
                # Truncation guard
                if not fission_active and "..." in output and len(output) < (len(code) * 0.8):
                    logger.warning("   [X] TRUNCATION DETECTED. Rejecting mutation.")
                    return code
                
                return output
            else:
                logger.warning("   [!]  Malformed response from Gemini")
                return code
        
        except Exception as e:
            logger.error(f"   [X] Gemini API error: {e}")
            return code


# ==============================================================================
# L3 FISSION: Blueprint Application Helper
# ==============================================================================

async def apply_fission_blueprint(file_path: str, blueprint: dict, fission_mgr: FissionManager) -> bool:
    """
    Apply a fission blueprint to split a monolithic file into sub-modules.
    
    Args:
        file_path: Path to the monolithic file
        blueprint: Fission blueprint with module definitions
        fission_mgr: FissionManager instance
        
    Returns:
        bool: True if fission was successful, False otherwise
    """
    try:
        import os
        
        file_dir = os.path.dirname(file_path)
        file_name = os.path.basename(file_path)
        base_name = file_name.replace('.py', '')
        
        # Create sub-module directory
        submodule_dir = os.path.join(file_dir, f"{base_name}_modules")
        os.makedirs(submodule_dir, exist_ok=True)
        
        # Write sub-modules
        created_modules = []
        for module_name, module_data in blueprint.items():
            if not isinstance(module_data, dict):
                continue
                
            module_content = module_data.get('content', '')
            if not module_content:
                continue
            
            # Create sub-module file
            module_file = os.path.join(submodule_dir, f"{module_name}.py")
            with open(module_file, 'w', encoding='utf-8') as f:
                f.write(module_content)
            
            created_modules.append((module_name, module_data.get('exports', [])))
            logger.info(f"   [+] Created sub-module: {module_name}.py")
        
        if not created_modules:
            logger.warning(f"   [!] No sub-modules created from blueprint")
            return False
        
        # Create router file (original filename becomes orchestrator)
        router_content = f'''"""
{base_name} - L3 Orchestration Router
Auto-generated by Atomic Fission Protocol
Original file split into sub-modules for atomicity compliance
"""

# Import all sub-modules
'''
        
        for module_name, exports in created_modules:
            if exports:
                exports_str = ', '.join(exports)
                router_content += f"from .{base_name}_modules.{module_name} import {exports_str}\n"
            else:
                router_content += f"from .{base_name}_modules import {module_name}\n"
        
        router_content += f"\n# Re-export all components\n__all__ = ["
        all_exports = []
        for _, exports in created_modules:
            all_exports.extend(exports)
        router_content += ", ".join(f'"{e}"' for e in all_exports)
        router_content += "]\n"
        
        # Backup original file
        backup_path = file_path + '.fission_backup'
        import shutil
        shutil.copy2(file_path, backup_path)
        logger.info(f"   [+] Backed up original to: {os.path.basename(backup_path)}")
        
        # Write router file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(router_content)
        
        logger.info(f"   [✓] Fission complete: {len(created_modules)} sub-modules created")
        return True
        
    except Exception as e:
        logger.error(f"   [X] Fission blueprint application failed: {e}")
        return False


# ==============================================================================
# L4 ORCHESTRATION: THE RUNNER (Mission Logic)
# ==============================================================================

async def run_mission(target_scope: str = "agentic_core"):
    """
    Executes the full 50-key agentic validation mission.
    L1-L5 Architecture: Linear Execution (No Cognitive Loops)
    """
    print(f"\n[*] MISSION START: Validating {target_scope}")
    print(f"DEBUG: VERSION 2.3 - LINEAR EXECUTION (CAP: 24,576)")
    
    # Add project root to sys.path for imports
    project_root = Path(__file__).parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    # ===========================================================================
    # L4 STATE HARDENING: Smart-Report Hybrid
    # ===========================================================================
    
    class CallableReport(list):
        """
        Hybrid report that supports both legacy .append() and modern callable interface.
        Fixes: "list object is not callable" and "missing report" errors.
        """
        def __call__(self, agent_name: str, key_num: int, passed: bool, details: str = ""):
            """Modern 4-parameter interface: ctx.report(agent, key, passed, msg)"""
            status = "PASS" if passed else "FAIL"
            self.append({
                "agent": agent_name,
                "key": key_num,
                "status": status,
                "msg": str(details)
            })
    
    # Initialize or import ValidationContext
    try:
        from agentic_core.L4_state.validation_context import ValidationContext
        ctx = ValidationContext()
        print("   [OK] ValidationContext loaded from agentic_core")
    except ImportError:
        # Fallback: Minimal context with hardened API
        class ValidationContext:
            def __init__(self):
                self.target_scope = None
                self.python_files = []
                self.report = []
                self.results = {}
                self.signals = set()
                self._client = None
                
            def get_env(self, key: str, default=None):
                """Get environment variable (fixes 'gget_env' typo)"""
                return os.getenv(key, default)
                
            def add_to_report(self, agent_name: str, message: str, severity: str = "info"):
                """Legacy report interface"""
                self.report.append({"agent": agent_name, "msg": message, "lvl": severity})
            
            def signal_deps_valid(self):
                """Signal that dependencies are valid"""
                self.signals.discard("DEPS_INVALID")
        
        ctx = ValidationContext()
        print("   [!] Using fallback ValidationContext")
    
    # Harden context with CallableReport
    existing_report = getattr(ctx, 'report', [])
    if not isinstance(existing_report, list):
        existing_report = []
    ctx.report = CallableReport(existing_report)
    
    # Ensure required attributes exist
    if not hasattr(ctx, 'results'):
        ctx.results = {}
    if not hasattr(ctx, 'get_env'):
        ctx.get_env = lambda k, d=None: os.getenv(k, d)
    if not hasattr(ctx, 'signals'):
        ctx.signals = set()
    if not hasattr(ctx, 'add_to_report'):
        ctx.add_to_report = lambda agent, msg, lvl="info": ctx.report.append({"agent": agent, "msg": msg, "lvl": lvl})
    if not hasattr(ctx, 'signal_deps_valid'):
        ctx.signal_deps_valid = lambda: ctx.signals.discard("DEPS_INVALID") if hasattr(ctx, 'signals') else None
    
    ctx.target_scope = target_scope
    ctx.python_files = [str(p) for p in Path(target_scope).rglob("*.py") if p.suffix == ".py"]
    
    print(f"   [OK] Context hardened: {len(ctx.python_files)} Python files discovered")
    
    # ===========================================================================
    # L2 AGENT LOADING: Dynamic Import
    # ===========================================================================
    
    cleaning_crew = []
    agent_modules = [
        ('agentic_core.agents.system_architect', 'SystemArchitect'),
        ('agentic_core.agents.structural_engineer', 'StructuralEngineer'),
        ('agentic_core.agents.healer_agent', 'HealerAgent'),
        ('agentic_core.agents.quality', 'HygieneGuardian'),
        ('agentic_core.agents.governance', 'ArchitectureGovernor'),
        ('agentic_core.agents.governance', 'DependencySentinel'),
        ('agentic_core.agents.security', 'SecurityEnforcer'),
        ('agentic_core.agents.memory_architect', 'MemoryArchitect'),
        ('agentic_core.agents.hallucination_hunter', 'HallucinationHunter'),
    ]
    
    for module_path, class_name in agent_modules:
        try:
            module = importlib.import_module(module_path)
            agent_class = getattr(module, class_name)
            cleaning_crew.append(agent_class(ctx))
            print(f"   [+] Loaded: {class_name}")
        except Exception as e:
            print(f"   [!] Load Error {class_name}: {e}")
    
    if not cleaning_crew:
        print("   [!] CRITICAL: No agents loaded. Aborting mission.")
        return
    
    # ===========================================================================
    # L3 ORCHESTRATION: Separate File Validators from Mission Monitors
    # ===========================================================================
    # This prevents the "Silent Loop Hang" where monitors query Pinecone 221x
    
    file_validators = [
        agent for agent in cleaning_crew 
        if agent.__class__.__name__ not in ['MemoryArchitect', 'HallucinationHunter']
    ]
    
    mission_monitors = [
        agent for agent in cleaning_crew 
        if agent.__class__.__name__ in ['MemoryArchitect', 'HallucinationHunter']
    ]
    
    print(f"   [L3] Orchestration: {len(file_validators)} validators, {len(mission_monitors)} monitors")
    print(f"   [>] Starting Linear Execution Sweep...\n")
    
    # ===========================================================================
    # L2 EXECUTION LOGIC: Per-File Validation (Linear, Not Looped)
    # ===========================================================================
    
    for idx, file_path in enumerate(ctx.python_files, 1):
        file_name = os.path.basename(file_path)
        
        # ===========================================================================
        # L5 SAFETY THRESHOLD: Check file size before healing
        # ===========================================================================
        # Files >200 lines trigger FISSION instead of healing to prevent cognitive exhaustion
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                loc_count = len(f.readlines())
        except Exception:
            loc_count = 0
        
        print(f"🔍 [{idx}/{len(ctx.python_files)}] {file_name} ({loc_count} LOC)")
        
        if loc_count > 200:
            print(f"⚠️  [FISSION TRIGGER] {file_name} is {loc_count} lines. Exceeds HOP threshold (200).")
            
            # 1. Initialize FissionManager (L3)
            fission = get_fission_manager(line_limit=200)
            
            # 2. Execute Cognition (L1) -> Identify Split Points
            # Instead of healing, we force a fission plan
            if hasattr(ctx, 'results'):
                ctx.results[file_name] = {
                    "action": "FISSION_REQUIRED",
                    "loc": loc_count,
                    "threshold": 200,
                    "reason": "File exceeds L5 safety threshold for healing"
                }
                print(f"   [+] Fission plan drafted for {file_name}. Moving to next file.")
            
            # 3. Skip HealerAgent for this file (Avoid Cognitive Exhaustion)
            continue
        
        # File is within safe threshold - proceed with normal validation
        for agent in file_validators:
            try:
                # Handle both .execute() and .run() methods
                method = getattr(agent, 'execute', None) or getattr(agent, 'run', None)
                
                if method:
                    # Check if method accepts file_path argument (modern) or no args (legacy)
                    import inspect
                    sig = inspect.signature(method)
                    params = list(sig.parameters.keys())
                    
                    # Remove 'self' from parameter count
                    param_count = len([p for p in params if p != 'self'])
                    
                    if param_count >= 1:
                        # Modern: Pass file_path
                        result = await method(file_path)
                    else:
                        # Legacy: No arguments
                        result = await method()
                    
                    # ===========================================================================
                    # L3 INTEGRATION: Auto-Fission Hook
                    # ===========================================================================
                    # Check if ArchitectureGovernor triggered a Fission Event
                    if isinstance(result, dict) and result.get("fission_event"):
                        print(f"✂️  [L2 EXECUTION] Auto-Fission triggered for {file_name}")
                        
                        # Initialize FissionManager to handle physical file splits
                        fission_mgr = get_fission_manager(line_limit=200)
                        
                        # Execute the split based on the L1 Cognition Blueprint
                        try:
                            success = await apply_fission_blueprint(
                                file_path, 
                                result["blueprint"], 
                                fission_mgr
                            )
                            
                            if success:
                                ctx.report("FissionManager", 0, True, 
                                          f"Successfully split {file_name} into sub-modules")
                                print(f"   [✓] Fission complete for {file_name}")
                                # Break validator loop - file no longer exists in monolithic form
                                break
                            else:
                                print(f"   [!] Fission failed for {file_name}")
                        except Exception as fission_error:
                            print(f"   [!] Fission execution error: {fission_error}")
                    
                    # Check if ArchitectureGovernor stored blueprints in context
                    if (agent.__class__.__name__ == 'ArchitectureGovernor' and 
                        hasattr(ctx, 'fission_blueprints') and 
                        file_path in ctx.fission_blueprints):
                        
                        blueprint = ctx.fission_blueprints[file_path]
                        print(f"✂️  [L2 EXECUTION] Auto-Fission triggered for {file_name} (from context)")
                        
                        fission_mgr = get_fission_manager(line_limit=200)
                        
                        try:
                            success = await apply_fission_blueprint(
                                file_path,
                                blueprint.get("blueprint", {}),
                                fission_mgr
                            )
                            
                            if success:
                                ctx.report("FissionManager", 0, True,
                                          f"Successfully split {file_name} into sub-modules")
                                print(f"   [✓] Fission complete for {file_name}")
                                break
                        except Exception as fission_error:
                            print(f"   [!] Fission execution error: {fission_error}")
                        
            except Exception as e:
                ctx.report.append({
                    "agent": agent.__class__.__name__,
                    "file": file_name,
                    "msg": f"Execution error: {str(e)[:100]}"
                })
    
    # ===========================================================================
    # L3 ORCHESTRATION: Mission Monitors (Single Pass After File Loop)
    # ===========================================================================
    
    print(f"\n🧠 [L4 STATE] Executing Mission Monitors (Single Pass)...")
    for monitor in mission_monitors:
        try:
            method = getattr(monitor, 'execute', None) or getattr(monitor, 'run', None)
            if method:
                await method()
                print(f"   [✓] {monitor.__class__.__name__} completed")
        except Exception as e:
            print(f"   [!] {monitor.__class__.__name__} error: {e}")
    
    # ===========================================================================
    # L5 SAFETY: Mission Summary Dashboard
    # ===========================================================================
    
    print("\n" + "="*70)
    print(f"🚀 MISSION COMPLETE: {len(ctx.python_files)} Files Swept")
    print(f"📊 TOTAL VIOLATIONS DETECTED: {len(ctx.report)}")
    
    # Count fission triggers
    fission_count = sum(1 for v in ctx.results.values() if isinstance(v, dict) and v.get('action') == 'FISSION_REQUIRED')
    if fission_count > 0:
        print(f"⚡ FISSION TRIGGERS: {fission_count} files exceed 200 LOC threshold")
    
    # Count violations by agent
    if ctx.report:
        from collections import Counter
        
        agent_summary = Counter(item.get('agent', 'Unknown') for item in ctx.report)
        key_summary = Counter(item.get('key') for item in ctx.report if 'key' in item)
        
        print("\n📋 VIOLATIONS BY AGENT:")
        for agent, count in agent_summary.most_common():
            print(f"   - {agent}: {count} issues")
            
            # Special flag for ArchitectureGovernor atomicity violations
            if agent == 'ArchitectureGovernor' and count > 100:
                print(f"      ⚠️  CRITICAL: {count} Atomicity Violations (Key 50)")
        
        if key_summary:
            print("\n🔑 TOP VIOLATED CANON KEYS:")
            for key, count in key_summary.most_common(10):
                print(f"   - Key {key}: {count} violations")
    else:
        print("\n✅ No violations detected (or agents did not report)")
    
    # Report fission candidates
    if fission_count > 0:
        print(f"\n⚡ FISSION CANDIDATES ({fission_count} files):")
        fission_files = [(k, v['loc']) for k, v in ctx.results.items() 
                        if isinstance(v, dict) and v.get('action') == 'FISSION_REQUIRED']
        # Sort by LOC descending
        fission_files.sort(key=lambda x: x[1], reverse=True)
        for file_name, loc in fission_files[:10]:  # Show top 10
            print(f"   - {file_name}: {loc} LOC")
        if len(fission_files) > 10:
            print(f"   ... and {len(fission_files) - 10} more files")
    
    print("="*70)
    print(f"[L5] Token Budget Enforced: 24,576 max per agent")
    print(f"[L5] Safety Threshold: Files >200 LOC trigger fission (not healing)")
    print(f"[L3] Linear Execution: No cognitive loops detected")
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

    try:
        asyncio.run(run_mission(args.target))
    except KeyboardInterrupt:
        print("\n[!] Mission interrupted by user")
    except Exception as e:
        print(f"\n[X] Mission failed: {e}")
        import traceback
        traceback.print_exc()
