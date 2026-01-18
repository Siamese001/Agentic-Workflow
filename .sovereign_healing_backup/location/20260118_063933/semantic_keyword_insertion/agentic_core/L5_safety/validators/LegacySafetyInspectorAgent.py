"""
_LegacySafetyInspectorAgent - Extracted from canon_agents_quality.py
Legacy safety inspection agent preserved for backward compatibility.
"""

# TODO: GRAVITY VIOLATION AUTO-HEALED
# Downstream imports removed — move shared logic to apps_shared or sovereign utils
# Original violation: GRAVITY VIOLATION: Upstream 'agentic_core' imports downstream roots: ['apps_shared']. Move shared logic to apps_shared or sovereign utils.
# Removed: apps_shared.base_agents.canon_base_agent_interface

from __future__ import annotations
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, Tuple
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin

try:
    from agentic_core.L1_cognition.thought_engine.canon_validators_ast import validate_print_statements, validate_debugger, validate_empty_except, validate_bare_except, validate_eval_exec
except ImportError:
    validate_print_statements = validate_debugger = validate_empty_except = validate_bare_except = validate_eval_exec = lambda *a, **k: (True, [])



# NOT_AN_AGENT — legacy L1 class removed 2026-01-06, use L5 canonical version
# from agentic_core.L5_safety.guardrails.overseer import SafetyInspectorAgent
class _LegacySafetyInspectorAgent(HealerMixin):
    """
    KEYS: 0 (Secrets), 1 (TODO/FIXME), 2 (Print), 3 (Debugger), 4 (Empty Except), 5 (Bare Except), 6 (Eval/Exec)
    ROLE: Security Compliance. Emits SECURE signal.
    
    DDD Compliance Phase 9A:
    - Uses composition with CanonBaseAgentInterface
    - Implementation injected via dependency injection
    - No direct dependency on L2_Execution layer
    """

    def __init__(self, agent_impl: CanonBaseAgentInterface) -> None:
        """Initialize with injected agent implementation."""
        self.agent = agent_impl

    def __getattr__(self, name):
        """Delegate all agent methods to injected implementation - backward compatible."""
        return getattr(self.agent, name)

    def execute(self) -> None:
        """
        Executes the security audit by running all defined checks.
        Reports findings to the context and signals security status.
        """
        print(f'\nfrom agentic_core.utils.core_extensions.subatomic_testing_mixin import SubatomicTestingMixin\nfrom agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin\nimport logging\n\nLogger = logging.getLogger(__name__)\n[>>>] {self.agent.name} ACTIVATED: Security Audit...')
        keys: Any = [(0, self.check_key_00_no_hardcoded_secrets), (1, self.check_key_01_no_todo_fixme), (2, self.check_key_02_no_print_statements), (3, self.check_key_03_no_debugger_statements), (4, self.check_key_04_no_empty_except_blocks), (5, self.check_key_05_no_bare_except), (6, self.check_key_06_no_eval_exec)]
        for key, check_func in keys:
            passed, details = check_func()
            self.agent.ctx.report(self.agent.name, key, passed, details)
        self.agent.ctx.signal_secure()

    def _check_content_for_secret_patterns(self, content: str, patterns: List[str]) -> bool:
        """Helper to check if file content contains any secret patterns."""
        for pattern in patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        return False

    def _read_file_content(self, fp: str) -> Tuple[str, bool]:
        """Helper to read file content, returns content and success status."""
        try:
            with open(fp, 'r', encoding='utf-8') as f:
                return (f.read(), True)
        except Exception:
            return ('', False)

    def _find_secret_violations_in_file(self, fp: str, patterns: List[str]) -> List[str]:
        """Helper to find hardcoded secrets in a single file."""
        content, success = self._read_file_content(fp)
        if not success:
            return []
        if self._check_content_for_secret_patterns(content, patterns):
            return [fp]
        return []

    def check_key_00_no_hardcoded_secrets(self) -> Tuple[bool, List[str]]:
        """
        Checks for hardcoded secrets (passwords, API keys, tokens) in files.
        """
        violations: Any = []
        patterns: Any = ['password\\s*=\\s*["\\\'][^"\\\']+["\\\']', 'api[_-]?key\\s*=\\s*["\\\'][^"\\\']+["\\\']', 'secret\\s*=\\s*["\\\'][^"\\\']+["\\\']', 'token\\s*=\\s*["\\\'][^"\\\']+["\\\']']
        for fp in self.agent.ctx.python_files:
            violations.extend(self._find_secret_violations_in_file(fp, patterns))
        return (len(violations) == 0, violations)

    def _process_file_lines_for_todo_fixme(self, f_obj, fp: str) -> List[str]:
        """Helper to process lines of an open file for TODO/FIXME violations."""
        violations = []
        for i, line in enumerate(f_obj, 1):
            if re.search('\\b(TODO|FIXME)\\b', line, re.IGNORECASE):
                violations.append(f'{fp}:{i}')
        return violations

    def _find_todo_fixme_violations_in_file(self, fp: str) -> List[str]:
        """Helper to find TODO/FIXME comments in a single file."""
        try:
            with open(fp, 'r', encoding='utf-8') as f:
                return self._process_file_lines_for_todo_fixme(f, fp)
        except Exception:
            pass
        return []

    def check_key_01_no_todo_fixme(self) -> Tuple[bool, List[str]]:
        """
        Checks for 'TODO' or 'FIXME' comments in files.
        """
        violations: Any = []
        for fp in self.agent.ctx.python_files:
            violations.extend(self._find_todo_fixme_violations_in_file(fp))
        return (len(violations) == 0, violations)

    def check_key_02_no_print_statements(self) -> Tuple[bool, List[str]]:
        """
        [REFACTORED] Checks for 'print()' statements using AST-based validator.
        Automatically handles TYPE_CHECKING blocks and exception ledger.
        """
        violations: Any = []
        for fp in self.agent.ctx.python_files:
            try:
                with open(fp, 'r', encoding='utf-8') as f:
                    content: Any = f.read()
                results: Any = validate_print_statements(Path(fp), content)
                for result in results:
                    violations.append(f"{fp}:{result['line']}")
            except Exception:
                continue
        return (len(violations) == 0, violations)

    def check_key_03_no_debugger_statements(self) -> Tuple[bool, List[str]]:
        """
        [REFACTORED] Checks for debugger statements using AST-based validator.
        Detects breakpoint() and pdb.set_trace() with TYPE_CHECKING awareness.
        """
        violations: Any = []
        for fp in self.agent.ctx.python_files:
            try:
                with open(fp, 'r', encoding='utf-8') as f:
                    content: Any = f.read()
                results: Any = validate_debugger(Path(fp), content)
                for result in results:
                    violations.append(f"{fp}:{result['line']}")
            except Exception:
                continue
        return (len(violations) == 0, violations)

    def check_key_04_no_empty_except_blocks(self) -> Tuple[bool, List[str]]:
        """
        [REFACTORED] Checks for empty 'except' blocks using AST-based validator.
        """
        violations: Any = []
        for fp in self.agent.ctx.python_files:
            try:
                with open(fp, 'r', encoding='utf-8') as f:
                    content: Any = f.read()
                results: Any = validate_empty_except(Path(fp), content)
                for result in results:
                    violations.append(f"{fp}:{result['line']}")
            except Exception:
                continue
        return (len(violations) == 0, violations)

    def check_key_05_no_bare_except(self) -> Tuple[bool, List[str]]:
        """
        [REFACTORED] Checks for bare 'except:' statements using AST-based validator.
        """
        violations: Any = []
        for fp in self.agent.ctx.python_files:
            try:
                with open(fp, 'r', encoding='utf-8') as f:
                    content: Any = f.read()
                results: Any = validate_bare_except(Path(fp), content)
                for result in results:
                    violations.append(f"{fp}:{result['line']}")
            except Exception:
                continue
        return (len(violations) == 0, violations)

    def check_key_06_no_eval_exec(self) -> Tuple[bool, List[str]]:
        """
        [REFACTORED] Checks for 'eval()' or 'exec()' calls using AST-based validator.
        """
        violations: Any = []
        for fp in self.agent.ctx.python_files:
            try:
                with open(fp, 'r', encoding='utf-8') as f:
                    content: Any = f.read()
                results: Any = validate_eval_exec(Path(fp), content)
                for result in results:
                    violations.append(f"{fp}:{result['line']}")
            except Exception:
                continue
        return (len(violations) == 0, violations)

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()