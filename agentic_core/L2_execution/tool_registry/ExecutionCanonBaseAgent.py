import ast
'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
import asyncio
import os
import re
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, Tuple
from dotenv import load_dotenv

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai: Any = None
    types: Any = None
load_dotenv()

class _SubatomicEnginePlaceholder:
    """
    Placeholder for the Subatomic Engine.
    In a full refactor, the actual implementation from apps_shared would be moved here
    or to a new sovereign module within agentic_core.
    """

    def __init__(self, gemini_client: Any):
        self.client = gemini_client

class _fission_managerPlaceholder:
    """
    Placeholder for the Fission Manager.
    """

    def __init__(self):
        pass

class _safety_guardrailPlaceholder:
    """
    Placeholder for the Safety Guardrail.
    """

    def __init__(self):
        pass

def get_subatomic_engine(gemini_client: Any) -> Any:
    """
    Placeholder function to get the Subatomic Engine.
    Replaces the original import from apps_shared.
    """
    return _SubatomicEnginePlaceholder(gemini_client)

def get_fission_manager() -> Any:
    """
    Placeholder function to get the Fission Manager.
    Replaces the original import from apps_shared.
    """
    return _fission_managerPlaceholder()

def get_safety_guardrail() -> Any:
    """
    Placeholder function to get the Safety Guardrail.
    Replaces the original import from apps_shared.
    """
    return _safety_guardrailPlaceholder()

# Alias for backward compatibility
CanonBaseAgent = None  # Will be set after class definition

@dataclass
class CanonBaseAgent(ABC):
    """
    Base class for Canon Validator agents with Subatomic healing capabilities.

    All specialized agents (SystemArchitect, CodeJanitor, StructuralEngineer, HealerAgent)
    inherit from this base and implement their specific validation logic.
    """
    ctx: Any
    name: str = field(init=False)
    role: str = field(init=False)
    _client: Optional[Any] = field(default=None, init=False)
    chat_sessions: Dict[str, Any] = field(default_factory=dict, init=False)
    conversation_history: Dict[str, List[Any]] = field(default_factory=dict, init=False)
    _subatomic_engine: Optional[Any] = field(default=None, init=False)
    _fission_manager: Optional[Any] = field(default=None, init=False)
    _safety_guardrail: Optional[Any] = field(default=None, init=False)
    BANNED_IMPORTS: List[str] = field(default_factory=lambda: ['base', 'context', 'L3_orchestration', 'conversational_repair'], init=False)

    def __post_init__(self):
        """Initialize agent name, role, and external clients."""
        self.name = self.__class__.__name__
        self.role = self._get_role_name()
        api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
        if genai and api_key:
            self._client = genai.Client(api_key=api_key)
            print(f'[OK] {self.name} connected to Gemini 2.5', flush=True)
        else:
            print(f"[!] {self.name}: Gemini client not available (API key: {('found' if api_key else 'missing')})", flush=True)
        if self._client:
            try:
                self._subatomic_engine = get_subatomic_engine(gemini_client=self._client)
                self._fission_manager = get_fission_manager()
                self._safety_guardrail = get_safety_guardrail()
                print(f'   [+] {self.name}: Sub-Atomic Engine initialized', flush=True)
            except Exception as e:
                print(f'   [!]  {self.name}: Failed to initialize Sub-Atomic Engine: {e}', flush=True)

    def _get_role_name(self) -> str:
        """Convert class name to role name (e.g., SystemArchitect -> system_architect)."""
        name = self.__class__.__name__
        return re.sub('(?<!^)(?=[A-Z])', '_', name).lower()

    @abstractmethod
    async def execute(self) -> Any:
        """Execute agent's validation logic. Must be implemented by subclasses."""
        raise NotImplementedError(f'{self.name} must implement execute()')

    @abstractmethod
    def get_validation_keys(self) -> List[int]:
        """Return list of canon keys this agent validates. Must be implemented by subclasses."""
        raise NotImplementedError(f'{self.name} must implement get_validation_keys()')

    def check_negative_constraints(self, code: str) -> Tuple[bool, List[str]]:
        """
        Check if generated code violates negative constraints (banned imports).

        Args:
            code: Generated code to check

        Returns:
            Tuple of (is_valid, list of violations)
        """
        violations: Any = []
        for banned in self.BANNED_IMPORTS:
            regex_pattern: Any = f'(?:import\\s+{re.escape(banned)}|from\\s+{re.escape(banned)}\\s+import|from\\s+{re.escape(banned)}\\.)'
            if re.search(regex_pattern, code):
                violations.append(f'Banned import detected: {banned}')
        return (len(violations) == 0, violations)

    def _reset_chat_session_if_needed(self, chat_key: str, file_path: Optional[str], round_num: int):
        """
        Resets the chat session if round_num is 3 or greater, clearing contaminated history.
        """
        if round_num >= 3 and chat_key in self.chat_sessions:
            print(f'      [~] Round {round_num}: Resetting chat session to clear contaminated history', flush=True)
            del self.chat_sessions[chat_key]
            if file_path in self.conversation_history:
                self.conversation_history[file_path] = []

    def _get_gemini_response_from_session(self, chat_key: str, config: Any, prompt: str, round_num: int, file_path: Optional[str]) -> Any:
        """
        Gets or creates a Gemini chat session and sends a message.
        """
        if chat_key not in self.chat_sessions:
            model_name = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
            self.chat_sessions[chat_key] = self._client.chats.create(model=model_name, config=config)
            print(f"      [NEW] Created new chat session for {(os.path.basename(file_path) if file_path else 'default')}", flush=True)
        else:
            print(f'      [REUSE]  Reusing chat session (Round {round_num})', flush=True)
        chat = self.chat_sessions[chat_key]
        return chat.send_message(prompt)

    def _process_gemini_response(self, response: Any, code: str) -> str:
        """
        Extracts and validates code from the Gemini API response.
        """
        if not (response.candidates and response.candidates[0].content.parts):
            print(f'      [!] Malformed response from Gemini', flush=True)
            return code
        first_part = response.candidates[0].content.parts[0]
        if hasattr(first_part, 'function_call') and first_part.function_call:
            print(f'      [ALERT] CRITICAL: Model called tool despite tools=[] - {first_part.function_call.name}', flush=True)
            return code
        if hasattr(first_part, 'text'):
            generated_code = first_part.text.strip()
            generated_code = self._extract_python_code(generated_code)
            if not self._is_valid_python(generated_code):
                print(f'      [!] Response is not valid Python code - rejecting', flush=True)
                return code
            is_valid, violations = self.check_negative_constraints(generated_code)
            if not is_valid:
                print(f"      [X] Hallucination Detected: {', '.join(violations)}", flush=True)
                return code
            if hasattr(response, 'usage_metadata'):
                total_tokens = response.usage_metadata.total_token_count
                print(f'      [OK] Tokens: {total_tokens}', flush=True)
            return generated_code
        print(f'      [!] Malformed response from Gemini (no text part)', flush=True)
        return code

    def _extract_python_code(self, text: str) -> str:
        """
        Extract pure Python code from LLM response, stripping markdown fences
        and any explanatory text.
        """
        if '```python' in text:
            start = text.find('```python') + 9
            end = text.find('```', start)
            if end != -1:
                code = text[start:end].strip()
                return code
        elif '```' in text:
            start = text.find('```') + 3
            end = text.find('```', start)
            if end != -1:
                code = text[start:end].strip()
                return code
        lines = text.split('\n')
        python_lines = []
        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith('#') or stripped.startswith('"""') or stripped.startswith("'''"):
                if stripped and (not (stripped.startswith('"""') or stripped.startswith("'''"))):
                    continue
                python_lines.append(line)
                continue
            python_lines.append(line)
            python_lines.extend(lines[lines.index(line) + 1:])
            break
        return '\n'.join(python_lines) if python_lines else text

    def _is_valid_python(self, code: str) -> bool:
        """
        Validate that the code is valid Python syntax.
        """
        try:
            ast.parse(code)
            return True
        except SyntaxError:
            return False

    async def resilient_mutation(self, task: str, code: str, file_path: Optional[str]=None, round_num: int=1, previous_failure: Optional[str]=None) -> str:
        """
        Core healing logic using Gemini 2.5 Flash with dynamic prompt loading.

        Args:
            task: Description of the violation to fix
            code: Original code to be fixed
            file_path: Path to the file being fixed
            round_num: Current healing round (1-5)
            previous_failure: Reason for previous failure (for lesson learned)

        Returns:
            Fixed code as string
        """
        if not self._client:
            raise RuntimeError('Gemini client not initialized. Set GOOGLE_API_KEY environment variable.')
        original_line_count: Any = len(code.splitlines())
        chat_key: Any = f'chat_{file_path}' if file_path else 'chat_default'
        if previous_failure and chat_key in self.chat_sessions:
            print(f'      [CLEAN] Clean Slate Protocol: Clearing contaminated history', flush=True)
            del self.chat_sessions[chat_key]
            if file_path in self.conversation_history:
                self.conversation_history[file_path] = []
        lesson_learned: Any = previous_failure if previous_failure else ''
        try:
            project_root: Any = Path(__file__).parent.parent.parent
            if str(project_root) not in sys.path:
                sys.path.insert(0, str(project_root))
            try:
                from archives.legacy_code.prompts.prompt_loader import load_prompt_for_agent
            except ImportError:
                from prompts.prompt_loader import load_prompt_for_agent
            prompt: Any = load_prompt_for_agent(agent_role=self.role, task=task, code=code, original_line_count=original_line_count, lesson_learned=lesson_learned)
        except Exception as e:
            print(f'      [!] Prompt loader failed ({e}), using fallback', flush=True)
            prompt: Any = self._build_fallback_prompt(task, code, original_line_count, lesson_learned)
        try:
            config: Any = types.GenerateContentConfig(temperature=0.2, thinking_config=types.ThinkingConfig(thinking_budget=16000), tools=[])
            self._reset_chat_session_if_needed(chat_key, file_path, round_num)
            response: Any = await asyncio.to_thread(lambda: self._get_gemini_response_from_session(chat_key, config, prompt, round_num, file_path))
            return self._process_gemini_response(response, code)
        except Exception as e:
            print(f'      [X] Gemini API error: {e}', flush=True)
            return code

    def _build_fallback_prompt(self, task: str, code: str, original_line_count: int, lesson_learned: str) -> str:
        """Build fallback prompt if dynamic loading fails."""
        prompt = f"Task: {task}\nSYSTEM: You are an ELITE Level 5 Autonomous Repair Agent.\n\n[X] ZERO-TOLERANCE DELETION RULE:\n- The original file has {original_line_count} lines of code\n- Your output MUST be a COMPLETE, functional file with ALL {original_line_count} lines\n- NEVER truncate files or use placeholders like '# ... rest of code' or '# existing code'\n- If you delete more than 10% of lines ({int(original_line_count * 0.1)} lines) without structural reason, REJECTED\n\n[X] PROHIBITED MODULES (HARD-CODED BLACKLIST):\n- 'base' - DOES NOT EXIST\n- 'context' - DOES NOT EXIST\n- 'L3_orchestration' - DOES NOT EXIST\n- 'conversational_repair' - DOES NOT EXIST\n\n⚡ ELITE ENGINEER RULES:\n1. Fix the specific violation ONLY - surgical precision\n2. NEVER hallucinate imports - verify all imports are real\n3. NEVER delete logic, comments, or docstrings\n4. Return ONLY valid Python code. No markdown blocks.\n5. CRITICAL: Return code as TEXT. Do NOT call any tools or functions.\n"
        if lesson_learned:
            prompt += f'\n\n📚 LESSON LEARNED: {lesson_learned}\n'
        prompt += f'\n{code}'
        return prompt

    async def verify_fix(self, original_code: str, fixed_code: str, violation_key: int) -> Tuple[bool, str]:
        """
        Verify that the fix resolves the violation without introducing new issues.

        Args:
            original_code: Original code before fix
            fixed_code: Fixed code to verify
            violation_key: Canon key that was being fixed

        Returns:
            Tuple of (is_fixed, reason)
        """
        try:
            ast.parse(fixed_code)
        except SyntaxError as e:
            return (False, f'SyntaxError at line {e.lineno}')
        original_lines: Any = len(original_code.splitlines())
        fixed_lines: Any = len(fixed_code.splitlines())
        max_allowed_deletion: Any = int(original_lines * 0.1)
        deletion_count: Any = original_lines - fixed_lines
        if deletion_count > max_allowed_deletion:
            return (False, f'Mass deletion: {deletion_count} lines deleted (max {max_allowed_deletion})')
        expansion_factor: Any = int(os.getenv('CODE_EXPANSION_FACTOR', '4'))
        if fixed_lines > original_lines * expansion_factor:
            return (False, f'Code bloat: {fixed_lines} lines (original {original_lines})')
        is_valid, violations = self.check_negative_constraints(fixed_code)
        if not is_valid:
            return (False, f"Banned imports: {', '.join(violations)}")
        return (True, 'Fix verified')

# Set the alias after class definition
CanonBaseAgent = canon_base_agent
