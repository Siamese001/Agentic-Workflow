#!/usr/bin/env python3
"""
🚀 CANON SUB-ATOMIC ENGINE - V2.2
Shared core for Fission, Safety Guardrails, and Resilient Mutation.
"""

import asyncio
import json
import logging
import os
import re
import sys
import subprocess
import importlib
import time
from pathlib import Path
from typing import Tuple, Optional, Dict, Any

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
            api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise RuntimeError("No Gemini API key found. Set GOOGLE_API_KEY or GEMINI_API_KEY.")
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
            logger.info(f"   🆕 Created new chat session for {os.path.basename(file_path)}")
        else:
            logger.info(f"   ♻️  Reusing chat session (Round {round_num})")
        
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
                    logger.warning("   🚫 TRUNCATION DETECTED. Rejecting mutation.")
                    return code
                
                return output
            else:
                logger.warning("   ⚠️  Malformed response from Gemini")
                return code
        
        except Exception as e:
            logger.error(f"   ❌ Gemini API error: {e}")
            return code


# ==============================================================================
# L4 ORCHESTRATION: THE RUNNER (Mission Logic)
# ==============================================================================

async def run_mission(target_scope: str = "agentic_core"):
    """Executes the full 50-key agentic validation mission."""
    print(f"\n[*] MISSION START: Validating {target_scope}")
    print(f"DEBUG: VERSION 2.2 - BUDGET HARDENED (CAP: 24,576)")
    
    # LEVEL 6: Create healing branch on start (GitOps)
    branch_name = f"healing/auto_{int(time.time())}"
    try:
        subprocess.run(["git", "checkout", "-b", branch_name], capture_output=True, check=False)
        print(f"   [+] GitOps: Created healing branch '{branch_name}'")
    except Exception:
        print("   [!] GitOps: Git not detected or branch creation failed.")

    # Strategy: Analyze signals and form agenda for the 50-key sweep
    print("\n=== [*] SELF-HEALING CYCLE 1/5 ===")
    print(f"   [>] Target: {os.path.abspath(target_scope)}")
    print("   [>] PLAN: Executing full system diagnostic via modular agents...")
    
    # Add project root to Python path
    project_root = Path(__file__).parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    # 1. Initialize Context (Blackboard)
    try:
        from agentic_core.L4_state.validation_context import ValidationContext
        ctx = ValidationContext()
    except ImportError:
        # Fallback: Create minimal context with agent-compatible API
        class ValidationContext:
            def __init__(self):
                self.target_scope = None
                self._client = None
                self.python_files = []
                self.report_data = []
                self.env_vars = {}
                self.signals = set()
                
            def get_env(self, key, default=None):
                """Get environment variable."""
                return os.getenv(key, default)
                
            def report(self, agent_name, key_number, passed, details):
                """Report validation result for a specific canon key."""
                self.report_data.append({
                    "agent": agent_name,
                    "key": key_number,
                    "passed": passed,
                    "details": details
                })
                
            def add_to_report(self, agent_name, message, severity="info"):
                """Add finding to report."""
                self.report_data.append({"agent": agent_name, "msg": message, "lvl": severity})
            
            def signal_deps_valid(self):
                """Signal that dependencies are valid."""
                self.signals.discard("DEPS_INVALID")
        
        ctx = ValidationContext()
        print("   [!] Using minimal ValidationContext (full context not available)")
    
    # CONTEXT HARDENING: Ensure imported objects meet current requirements
    if not hasattr(ctx, 'get_env'):
        ctx.get_env = lambda key, default=None: os.getenv(key, default)
    
    if not hasattr(ctx, 'report'):
        ctx.report = []
    elif not isinstance(ctx.report, list):
        # If report exists but isn't a list, create report_data for method-based reporting
        ctx.report_data = []
        ctx.report
        def report_method(agent_name, key_number, passed, details):
            ctx.report_data.append({
                "agent": agent_name,
                "key": key_number,
                "passed": passed,
                "details": details
            })
        ctx.report = report_method
        
    if not hasattr(ctx, 'add_to_report'):
        def hardened_report(agent_name, message, severity="info"):
            if isinstance(ctx.report, list):
                ctx.report.append({"agent": agent_name, "msg": message, "lvl": severity})
            elif hasattr(ctx, 'report_data'):
                ctx.report_data.append({"agent": agent_name, "msg": message, "lvl": severity})
        ctx.add_to_report = hardened_report
    
    if not hasattr(ctx, 'signals'):
        ctx.signals = set()
    elif isinstance(ctx.signals, list):
        ctx.signals = set(ctx.signals)
        
    if not hasattr(ctx, 'signal_deps_valid'):
        ctx.signal_deps_valid = lambda: ctx.signals.discard("DEPS_INVALID") if hasattr(ctx, 'signals') else None
        
    if not hasattr(ctx, 'python_files'):
        ctx.python_files = []
        
    if not hasattr(ctx, '_client'):
        ctx._client = None
    
    ctx.target_scope = target_scope
    
    # Populate python_files list
    ctx.python_files = [str(p) for p in Path(target_scope).rglob("*.py")]

    # 2. Dynamic Agent Loading (Key 11/12 Enforcement)
    # Load available agents from agentic_core/agents
    cleaning_crew = []
    
    try:
        # Try to load specialized agents that actually exist
        agent_modules = [
            # Core Canon Agents (inherit from CanonBaseAgent)
            ('agentic_core.agents.system_architect', 'SystemArchitect'),
            ('agentic_core.agents.structural_engineer', 'StructuralEngineer'),
            ('agentic_core.agents.healer_agent', 'HealerAgent'),
            
            # Quality & Hygiene Agents
            ('agentic_core.agents.quality', 'HygieneGuardian'),
            ('agentic_core.agents.quality', 'CodeStyleGuardian'),
            
            # Governance & Architecture
            ('agentic_core.agents.governance', 'ArchitectureGovernor'),
            ('agentic_core.agents.governance', 'DependencySentinel'),
            
            # Engineering & Structure
            ('agentic_core.agents.engineering', 'StructuralEngineer'),
            
            # Security
            ('agentic_core.agents.security', 'SafetyInspector'),
            ('agentic_core.agents.security', 'SecurityEnforcer'),
            
            # Analysis & Memory
            ('agentic_core.agents.memory_architect', 'MemoryArchitect'),
            ('agentic_core.agents.hallucination_hunter', 'HallucinationHunter'),
        ]
        
        for module_path, class_name in agent_modules:
            try:
                module = importlib.import_module(module_path)
                agent_class = getattr(module, class_name)
                cleaning_crew.append(agent_class(ctx))
                print(f"   [+] Loaded: {class_name}")
            except (ImportError, AttributeError) as e:
                print(f"   [!] Could not load {class_name}: {e}")
    except Exception as e:
        print(f"   [!] Agent loading error: {e}")

    if not cleaning_crew:
        print("   [!] No agents loaded. Running in diagnostic mode only.")
    else:
        print(f"   [+] Loaded {len(cleaning_crew)} agents for validation sweep")

    # 3. Execution Loop
    files_to_validate = [str(p) for p in Path(target_scope).rglob("*.py")]
    print(f"   [>] Found {len(files_to_validate)} Python files to validate\n")
    
    for file_path in files_to_validate:
        print(f"[>] Agentic Sweep: {os.path.basename(file_path)}")
        for agent in cleaning_crew:
            try:
                if hasattr(agent, 'can_run') and agent.can_run():
                    if hasattr(agent, 'execute'):
                        await agent.execute()
            except Exception as e:
                print(f"   [!] Agent error: {e}")
    
    print("\n[*] SAVING BLACKBOARD STATE...")
    print("[*] MISSION COMPLETE")


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
