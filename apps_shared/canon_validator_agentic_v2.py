#!/usr/bin/env python3
"""
[START] CANON SUB-ATOMIC ENGINE - V2.2
Shared core for Fission, Safety Guardrails, and Resilient Mutation.
"""

import asyncio
import importlib
import json
import logging
import random
import shutil
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
    from google.api_core.exceptions import ResourceExhausted, InternalServerError, DeadlineExceeded
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
        """Execute resilient mutation with exponential backoff retry."""
        if not self._client:
            raise RuntimeError("Gemini client not initialized")
        
        # Build prompt
        if fission_active:
            prompt = f"ATOMIC FISSION: Split {file_path} into 3 sub-modules. Return ONLY a JSON map.\n\nCODE:\n{code}"
        else:
            prompt = f"HEAL: Fix violations in {file_path}.\n\nTASK: {task}\n\nCODE:\n{code}"
        
        config = self.get_safe_config(is_fission=fission_active)
        chat_key = f"chat_{file_path}"
        
        if chat_key not in self.chat_sessions:
            model_name = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
            self.chat_sessions[chat_key] = self._client.chats.create(model=model_name, config=config)
            logger.info(f"   [NEW] Created chat session for {os.path.basename(file_path)}")
        
        # === RETRY WITH EXPONENTIAL BACKOFF (Max 3 attempts) ===
        max_retries = 3
        response = None
        
        for attempt in range(1, max_retries + 1):
            try:
                response = await asyncio.to_thread(self.chat_sessions[chat_key].send_message, prompt)
                break  # Success
            except (ResourceExhausted, InternalServerError, DeadlineExceeded) as e:
                if attempt == max_retries:
                    logger.error(f"   [X] Gemini Error (Final): {e}")
                    return code
                wait = (2 ** attempt) + random.uniform(0, 1)
                logger.warning(f"   [!] Gemini Transient Error ({attempt}/{max_retries}): {e}. Retrying in {wait:.1f}s")
                await asyncio.sleep(wait)
            except Exception as e:
                logger.error(f"   [X] Gemini Fatal Error: {e}")
                return code

        # Extract response
        if response and response.candidates and response.candidates[0].content.parts:
            output = response.candidates[0].content.parts[0].text.strip()
            # Truncation guard
            if not fission_active and "..." in output and len(output) < (len(code) * 0.8):
                logger.warning("   [X] TRUNCATION DETECTED. Rejecting mutation.")
                return code
            return output
        
        logger.warning("   [!] Malformed response from Gemini")
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
                logger.warning(f"   [!] Skipping invalid module entry: {module_name}")
                continue
                
            module_content = module_data.get('content', '').strip()
            if not module_content:
                logger.warning(f"   [!] Empty content for module {module_name}")
                continue
            
            # Create sub-module file
            module_file = os.path.join(submodule_dir, f"{module_name}.py")
            with open(module_file, 'w', encoding='utf-8', errors='ignore') as f:
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
        
        # Safe __all__ generation
        all_exports = [e for _, exports in created_modules for e in exports]
        if all_exports:
            router_content += f"\n__all__ = [" + ", ".join(f'"{e}"' for e in all_exports) + "]\n"
        else:
            router_content += "\n# No public exports defined\n__all__ = []\n"
        
        # Backup & Write
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{file_path}.fission_backup_{timestamp}"
        
        # Atomic backup: copy to temp then move
        shutil.copy2(file_path, f"{backup_path}.tmp")
        os.replace(f"{backup_path}.tmp", backup_path)
        
        with open(file_path, 'w', encoding='utf-8', errors='ignore') as f:
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
    [L3 ORCHESTRATOR]
    Executes the full Agentic Validation Mission.
    FULLY HARDENED: Instantiates Safety, Engine, and Fission Logic and wires to Context.
    """
    print(f"\n[*] MISSION START: Validating {target_scope}")
    print(f"DEBUG: VERSION 2.5 - GOLDEN MASTER (CAP: 24,576)")
    
    # Add project root to sys.path for imports
    project_root = Path(__file__).parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    # --- L5 HARDENING INSTANTIATION ---
    # 1. Initialize Safety Components
    safety_guard = SafetyGuardrail(deletion_limit=110)
    subatomic_engine = SubAtomicEngine() # Uses environment keys
    # 2. Initialize Fission Logic with CORRECT 200 line threshold
    fission_mgr = FissionManager(line_limit=200, max_rounds=3)
    
    print(f"   [OK] SubAtomicEngine active (Model: {os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')})")
    print(f"   [OK] SafetyGuardrail active (Limit: 110 lines)")
    
    # ===========================================================================
    # [ENHANCEMENT 1] L4 STATE HARDENING: Smart-Report Hybrid
    # ===========================================================================
    class CallableReport(list):
        """Hybrid report: Acts as list for append() AND callable for ctx.report()"""
        def __call__(self, agent_name: str, key_num: int, passed: bool, details: str = ""):
            status = "PASS" if passed else "FAIL"
            self.append({
                "agent": agent_name,
                "key": key_num,
                "status": status,
                "msg": str(details)
            })

    # Initialize Context
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
    
    # Harden Attributes (The "AttributeError" Fix)
    ctx.report = CallableReport(getattr(ctx, 'report', []))
    if not hasattr(ctx, 'results'): ctx.results = {} # Fixes StructuralEngineer
    if not hasattr(ctx, 'get_env'): ctx.get_env = lambda k, d=None: os.getenv(k, d)
    if not hasattr(ctx, 'signals'): ctx.signals = set()
    
    # 3. WIRE COMPONENTS TO CONTEXT (Crucial Fix)
    ctx.engine = subatomic_engine
    ctx.safety = safety_guard
    ctx.fission = fission_mgr
    
    ctx.target_scope = target_scope
    
    # === L5 SAFETY: Path Containment ===
    target_path = Path(target_scope).resolve()
    project_root_path = project_root.resolve()
    if not target_path.is_relative_to(project_root_path):
        raise ValueError(f"[SECURITY BLOCK] Target scope '{target_scope}' escapes project root.")
    
    ctx.python_files = [str(p) for p in target_path.rglob("*.py") if p.is_file()]
    print(f"   [OK] Context hardened: {len(ctx.python_files)} Python files in safe scope '{target_path}'")
    
    # ===========================================================================
    # [ENHANCEMENT 2] L1 INTELLIGENCE INJECTION: Agent Loading & Surgeon Prompt
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
        except Exception as e:
            print(f"   [!] Load Error {class_name}: {e}")

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
    # [ENHANCEMENT 3] L3 ORCHESTRATION: Separation of Concerns
    # ===========================================================================
    file_validators = [a for a in cleaning_crew if a.__class__.__name__ not in ['MemoryArchitect', 'HallucinationHunter']]
    mission_monitors = [a for a in cleaning_crew if a.__class__.__name__ in ['MemoryArchitect', 'HallucinationHunter']]
    
    print(f"   [L3] Orchestration: {len(file_validators)} validators, {len(mission_monitors)} monitors")
    print(f"   [>] Starting Linear Execution Sweep...\n")

    # ===========================================================================
    # [ENHANCEMENT 4 & 5] L2 EXECUTION & L5 SAFETY: The Atomic Sweep
    # ===========================================================================
    for idx, file_path in enumerate(ctx.python_files, 1):
        file_name = os.path.basename(file_path)
        
        # Check LOC for Safety Threshold
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                loc_count = len(f.readlines())
        except: loc_count = 0
        
        print(f"🔍 [{idx}/{len(ctx.python_files)}] {file_name} ({loc_count} LOC)", end='\r')

        # --- ACTIVE FISSION TRIGGER (Files > 200 Lines) ---
        if loc_count > 200:
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
            
            # If fission failed or no governor, mark as manual req and skip healing to save budget
            ctx.results[file_name] = {"action": "FISSION_REQUIRED_MANUAL", "loc": loc_count}
            continue

        # --- STANDARD VALIDATION (Files < 200 Lines) ---
        print(f"\n", end='') # New line for clean logging
        for agent in file_validators:
            try:
                method = getattr(agent, 'execute', getattr(agent, 'run', None))
                if method:
                    # Introspection to handle arguments safely
                    if method.__code__.co_argcount > 1:
                        await method(file_path)
                    else:
                        await method()
            except Exception as e:
                ctx.report(agent.__class__.__name__, 0, False, f"Exec Error: {str(e)[:50]}")
    
    # ===========================================================================
    # [ENHANCEMENT 3] GLOBAL MONITORING (Run ONCE at End)
    # ===========================================================================
    print(f"\n\n🧠 [L4 STATE] Executing Global Monitors (Single Pass)...")
    for monitor in mission_monitors:
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
        import traceback
        traceback.print_exc()
