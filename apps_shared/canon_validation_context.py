"""
Canon Validator Validation Context
Blackboard pattern for shared state across validation agents.
"""

import asyncio
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from apps_shared.canon_service_manager import ServiceManager
from apps_shared.canon_utils import get_python_files

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None


@dataclass
class ValidationContext:
    """Hardened Shared memory with Fission & Truncation Guard."""
    results: Dict[int, Any] = field(default_factory=dict)
    signals: Set[str] = field(default_factory=set)
    modified_files: Set[str] = field(default_factory=set)
    python_files: List[str] = field(default_factory=list)
    refactor_plans: Dict[str, Any] = field(default_factory=dict)
    intelligence_enabled: bool = field(default=False)
    _client: Any = field(default=None)
    target_scope: str = field(default=".")
    services: ServiceManager = field(default_factory=ServiceManager)
    
    healing_attempts: Dict[str, int] = field(default_factory=dict)
    healing_history: Dict[str, List[str]] = field(default_factory=dict)
    max_healing_per_file: int = field(default_factory=lambda: int(os.getenv('MAX_HEALING_PER_FILE', '8')))
    global_healing_budget: int = field(default_factory=lambda: int(os.getenv('GLOBAL_HEALING_BUDGET', '50')))
    healing_budget_used: int = 0
    
    thought_signatures: Dict[str, str] = field(default_factory=dict)
    conversation_history: Dict[str, List[Any]] = field(default_factory=dict)
    chat_sessions: Dict[str, Any] = field(default_factory=dict)
    
    # L5 Hardening: Truncation & Fission State
    fission_active: bool = False
    last_fission_map: Dict[str, str] = field(default_factory=dict)
    
    def __post_init__(self):
        print("\n🔧 Initializing Validation Context...", flush=True)
        
        try:
            if self.target_scope and self.target_scope != ".":
                self.python_files = get_python_files(self.target_scope)
            else:
                self.python_files = get_python_files(".")
        except Exception as e:
            print(f"   ⚠️  File scanning failed: {e}", flush=True)
            self.python_files = []
        
        print("\n🤖 Initializing Gemini Client...", flush=True)
        if genai and os.getenv("GOOGLE_API_KEY"):
            try:
                self.intelligence_enabled = True
                self._client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
                print("   ✅ Gemini Connected - HEALING MODE ACTIVE", flush=True)
            except Exception as e:
                print(f"   ⚠️  Gemini initialization failed: {e}", flush=True)
                self.intelligence_enabled = False
        else:
            self.intelligence_enabled = False
            print("   ⚠️  Healing disabled: No API key configured", flush=True)
        
        print("\n✅ Validation Context Ready\n", flush=True)
    
    def can_attempt_healing(self, file_path: str) -> bool:
        """Check if we can attempt healing on this file."""
        if self.healing_budget_used >= self.global_healing_budget:
            return False
        if self.healing_attempts.get(file_path, 0) >= self.max_healing_per_file:
            return False
        return True
    
    def record_healing_attempt(self, file_path: str, success: bool):
        """Record a healing attempt and update counters."""
        if file_path not in self.healing_attempts:
            self.healing_attempts[file_path] = 0
        self.healing_attempts[file_path] += 1
        self.healing_budget_used += 1
        
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"   Healing attempt {self.healing_attempts[file_path]} for {file_path}: {status}")
        print(f"   Healing budget: {self.healing_budget_used}/{self.global_healing_budget}")
    
    def convert_to_genai_types(self, raw_history):
        """Converts old list-of-dicts history into strict Google GenAI Content objects."""
        formatted = []
        for entry in raw_history:
            parts = []
            for p in entry.get('parts', []):
                parts.append(types.Part(text=p.get('text')))
            formatted.append(types.Content(role=entry['role'], parts=parts))
        return formatted
    
    async def resilient_mutation(self, agent_name: str, task: str, code: str, file_path: str = None, round_num: int = 1, previous_failure: str = None) -> str:
        """ELITE L1 Cognition with Truncation Guard and Fission Awareness."""
        original_line_count = len(code.splitlines())
        
        # L3 Orchestration: Check if we need to pivot to FISSION
        if original_line_count > 800 or round_num >= 3:
            self.fission_active = True
            task = f"ATOMIC FISSION: The file {file_path} is too large ({original_line_count} lines). Split it into _core.py, _signals.py, and a Facade. Return ONLY a JSON map with keys: 'core', 'signals', 'facade' mapping to their respective code."
        
        chat_key = f"chat_{file_path}" if file_path else "chat_default"
        if previous_failure and chat_key in self.chat_sessions:
            print(f"      🧹 Clean Slate Protocol: Clearing contaminated history", flush=True)
            del self.chat_sessions[chat_key]
            if file_path in self.conversation_history:
                self.conversation_history[file_path] = []
        
        lesson_learned = previous_failure if previous_failure else ""
        
        prompt = f"""Task: {task}
SYSTEM: You are an ELITE Level 5 Autonomous Repair Agent.

🚫 ZERO-TOLERANCE DELETION RULE:
- The original file has {original_line_count} lines of code
- Your output MUST be a COMPLETE, functional file with ALL {original_line_count} lines
- NEVER truncate files or use placeholders like '# ... rest of code' or '# existing code'
- If you delete more than 10% of lines ({int(original_line_count * 0.1)} lines) without structural reason, REJECTED
- Every mutation must be COMPLETE and FUNCTIONAL
- Preserve ALL sections exactly as-is unless directly fixing the violation

🚫 PROHIBITED MODULES (HARD-CODED BLACKLIST):
- 'base' - DOES NOT EXIST
- 'context' - DOES NOT EXIST  
- 'L3_orchestration' - DOES NOT EXIST
- 'conversational_repair' - DOES NOT EXIST
- These are HALLUCINATIONS. Do not import them under any circumstances.
- ONLY use: Python stdlib (os, sys, pathlib, etc.) OR 'from agentic_workflow.runtime.shared import ...'

⚡ ELITE ENGINEER RULES:
1. Fix the specific violation ONLY - surgical precision
2. NEVER hallucinate imports - verify all imports are real
3. NEVER delete logic, comments, or docstrings
4. Return ONLY valid Python code. No markdown blocks.
5. CRITICAL: Return code as TEXT. Do NOT call any tools or functions.
"""
        if lesson_learned:
            prompt += f"\n\n📚 LESSON LEARNED: {lesson_learned}\n"
        prompt += f"\n{code}"
        
        try:
            config = types.GenerateContentConfig(
                temperature=0.1,  # Maximum determinism for L1 Cognition
                thinking_config=types.ThinkingConfig(thinking_budget=50000),  # 50k Budget for deep reasoning
                tools=[]
            )
            
            chat_key = f"chat_{file_path}" if file_path else "chat_default"
            
            if round_num >= 3 and chat_key in self.chat_sessions:
                print(f"      🔄 Round {round_num}: Resetting chat session to clear contaminated history", flush=True)
                del self.chat_sessions[chat_key]
                if file_path in self.conversation_history:
                    self.conversation_history[file_path] = []
            
            def get_gemini_response():
                if chat_key not in self.chat_sessions:
                    self.chat_sessions[chat_key] = self._client.chats.create(
                        model=os.getenv('GEMINI_MODEL', 'gemini-2.5-flash'),
                        config=config
                    )
                    print(f"      🆕 Created new chat session for {os.path.basename(file_path) if file_path else 'default'}", flush=True)
                else:
                    print(f"      ♻️  Reusing chat session (Round {round_num})", flush=True)
                
                chat = self.chat_sessions[chat_key]
                return chat.send_message(prompt)
            
            response = await asyncio.to_thread(get_gemini_response)
            
            if response.candidates and response.candidates[0].content.parts:
                first_part = response.candidates[0].content.parts[0]
                if hasattr(first_part, 'function_call') and first_part.function_call:
                    tool_name = first_part.function_call.name
                    tool_args = dict(first_part.function_call.args) if first_part.function_call.args else {}
                    print(f"🔍 DEBUG: Model called tool '{tool_name}' with args: {tool_args}", flush=True)
                    print(f"   🚨 CRITICAL: Tools should be disabled! Clearing session.", flush=True)
                    if chat_key in self.chat_sessions:
                        del self.chat_sessions[chat_key]
                    return code
            
            raw_output = response.text.strip() if response.text else code
            
            # L5 SAFETY: Truncation Guard
            if not self.fission_active and "..." in raw_output and len(raw_output) < (len(code) * 0.8):
                print(f"      🚫 TRUNCATION DETECTED: L1 attempted to skip code. Rejecting.", flush=True)
                return code
            
            # L5 Fission: Handle atomic fission response
            if self.fission_active:
                try:
                    import json
                    self.last_fission_map = json.loads(raw_output)
                    print(f"      ⚛️  FISSION COMPLETE: Generated {len(self.last_fission_map)} modules", flush=True)
                    return "FISSION_COMPLETE"
                except json.JSONDecodeError:
                    print("      ❌ Fission Error: L1 failed to produce valid JSON.", flush=True)
                    self.fission_active = False
                    return code
            
            if hasattr(response, 'usage_metadata'):
                print(f"      ✅ Tokens: {response.usage_metadata.total_token_count}", flush=True)
            
            if file_path:
                if file_path not in self.conversation_history:
                    self.conversation_history[file_path] = []
                self.conversation_history[file_path].append({
                    "round": len(self.conversation_history[file_path]) + 1,
                    "prompt_length": len(prompt),
                    "response_length": len(raw_output)
                })
            
            return raw_output
            
        except Exception as e:
            if "maximum_remote_calls" in str(e):
                print("🚨 SDK Error: Check Pydantic field names in GenerateContentConfig.")
            elif "thought_signature" in str(e):
                print("🚨 Signature Error: History corruption detected. Resetting session.")
                if file_path and file_path in self.conversation_history:
                    self.conversation_history[file_path] = []
            else:
                print(f"🚨 Mutation Error ({agent_name}): {str(e)}")
            return code
    
    async def read_file(self, file_path: str) -> str:
        """Read file content."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except:
            return ""
    
    async def write_file(self, file_path: str, content: str):
        """Write content to file."""
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            print(f"   ❌ Failed to write {file_path}: {e}")
    
    def report(self, agent: str, key: int, passed: bool, details: Any):
        """Report validation result to blackboard."""
        status = "PASS" if passed else "FAIL"
        print(f"   [{agent}] Key {key}: {status}")
        self.results[key] = {"passed": passed, "details": details}
    
    def signal_critical_failure(self):
        self.signals.add("CRITICAL_FAIL")
        print("   🚨 SIGNAL: CRITICAL_FAIL asserted on Blackboard.")
    
    def signal_ast_valid(self):
        self.signals.add("AST_VALID")
        print("   ✅ SIGNAL: AST_VALID asserted on Blackboard.")
    
    def signal_deps_valid(self):
        self.signals.add("DEPS_VALID")
        print("   ✅ SIGNAL: DEPS_VALID asserted on Blackboard.")
    
    def signal_secure(self):
        self.signals.add("SECURE")
        print("   ✅ SIGNAL: SECURE asserted on Blackboard.")
