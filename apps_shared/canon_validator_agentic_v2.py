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
# L4 ORCHESTRATION: THE RUNNER (Mission Logic)
# ==============================================================================

async def run_mission(target_scope: str = "agentic_core"):
    """Executes the full 50-key agentic validation mission."""
    print(f"\n[*] MISSION START: Validating {target_scope}")
    print(f"DEBUG: VERSION 2.2 - BUDGET HARDENED (CAP: 24,576)")
    
    # 1. Initialize & Harden Context (L4 State)
    try:
        from agentic_core.L4_state.validation_context import ValidationContext
        ctx = ValidationContext()
    except ImportError:
        class ValidationContext:
            def __init__(self):
                self.python_files = []
                self.report = []
                self.results = {}
                self.signals = set()
        ctx = ValidationContext()

    # 🛡️ SMART-REPORT HYBRID: Fixes "list object not callable" and "missing report"
    class CallableReport(list):
        def __call__(self, agent_name, key_num, passed, details=""):
            status = "PASS" if passed else "FAIL"
            self.append({"agent": agent_name, "key": key_num, "status": status, "msg": str(details)})

    ctx.report = CallableReport(getattr(ctx, 'report', []))
    if not hasattr(ctx, 'results'): ctx.results = {} 
    if not hasattr(ctx, 'get_env'): ctx.get_env = lambda k, d=None: os.getenv(k, d)
    
    ctx.target_scope = target_scope
    ctx.python_files = [str(p) for p in Path(target_scope).rglob("*.py") if p.suffix == ".py"]

    # 2. Load Agents
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

    # 3. L3 ORCHESTRATION: Separate Logic from Monitoring
    # This prevents the "Silent Loop" hang
    validators = [a for a in cleaning_crew if a.__class__.__name__ not in ['MemoryArchitect', 'HallucinationHunter']]
    monitors = [a for a in cleaning_crew if a.__class__.__name__ in ['MemoryArchitect', 'HallucinationHunter']]

    print(f"   [>] Found {len(ctx.python_files)} files. Starting Agentic Sweep...")

    # --- THE ATOMIC SWEEP (Per File) ---
    for file_path in ctx.python_files:
        file_name = os.path.basename(file_path)
        print(f"🔍 [SWEEP] {file_name}")
        
        for agent in validators:
            try:
                # Dynamically find the execution method
                method = getattr(agent, 'execute', getattr(agent, 'run', None))
                if method:
                    # If the agent takes a file argument, pass it; otherwise just run
                    await method() if method.__code__.co_argcount == 1 else await method(file_path)
            except Exception as e:
                ctx.report.append({"agent": agent.__class__.__name__, "msg": f"Error on {file_name}: {e}"})

    # --- THE MONITORING PASS (Final State Check) ---
    print("\n🧠 [L4 STATE] Finalizing Memory & Hallucination Pass...")
    for monitor in monitors:
        try:
            method = getattr(monitor, 'execute', getattr(monitor, 'run', None))
            if method: await method()
        except Exception: pass

    # 📊 MISSION SUMMARY
    print("\n" + "="*50)
    print(f"🚀 MISSION COMPLETE: {len(ctx.python_files)} Files Swept")
    print(f"📊 TOTAL VIOLATIONS DETECTED: {len(ctx.report)}")
    print("="*50)


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
