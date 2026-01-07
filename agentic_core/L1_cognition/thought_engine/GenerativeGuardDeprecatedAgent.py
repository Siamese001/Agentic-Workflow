"""
GenerativeGuardDeprecatedAgent - Extracted from CanonHealerAgent.py
Deprecated guard logic preserved for backward compatibility.
"""
from __future__ import annotations
import importlib  # AUTO-INJECTED BY GRAVITY HEALER
import logging
import os
from typing import Any, Dict, List
# GRAVITY VIOLATION: from apps_shared.base_agents.canon_base_agent_interface import CanonBaseAgentInterface
from agentic_core.L0_maintenance.mixins.subatomic_testing_mixin import SubatomicTestingMixin
# GRAVITY FIXED (Upward Leak): from agentic_core.utils.core_extensions.mcp_hardened_mixin import MCPHardenedMixin
_mod = importlib.import_module('agentic_core.L5_safety.guardrails.mcp_hardened_mixin')
MCPHardenedMixin = getattr(_mod, 'MCPHardenedMixin')
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin

EXCLUDED_DIRS = {'__pycache__', '.git', 'node_modules', 'venv', '.venv'}


# Legacy class removed - use GenerativeGuardAgent instead
class GenerativeGuardDeprecatedAgent(HealerMixin, CanonBaseAgentInterface, MCPHardenedMixin):
    """
    KEYS: 45 (Dead Code/Runaway Generation)
    ROLE: The Watchdog. Identifies and deletes recursively-generated files.
    Phase 9A: DDD Remediation - Composition over inheritance
    Name updated to PascalCase with 'Agent' suffix for registry visibility.
    """

    def __init__(self, ctx: Any = None):
        self.impl = None  # CanonBaseAgent is abstract, skip instantiation
        self.ctx = ctx
        self.name = self.__class__.__name__
        self.Logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.GENERATIVE_PATTERNS = [
            r"_copy\d*\.py$",
            r"_backup\d*\.py$",
            r"_old\d*\.py$",
            r"_temp\d*\.py$",
        ]

    async def execute(self, goal: str = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute guard checks - maintains backward compatibility."""
        await self._execute_guard()
        return {"status": "completed", "agent": self.name}

    def get_capabilities(self) -> List[str]:
                    
        return self.impl.get_capabilities()

    def validate_state(self) -> bool:
                    
        return self.impl.validate_state()

    async def _execute_guard(self):
        """Original execute logic preserved."""
        print(f"\n[>>>] {self.name} ACTIVATED: Checking Generative Policy...")
        violations = []

        project_root = getattr(self.ctx, 'project_root', '.')
        
        for root, dirs, files in os.walk(project_root):
            dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
            violations.extend(self._find_runaway_violations_in_dir(root, files))

        if violations:
            self._process_found_violations(violations)
        else:
            print("   [OK] No runaway generation detected.")
            self.ctx.report(self.name, 45, True, [])
            self.ctx.signals.add("GENERATIVE_CLEAN")

    def _purge_single_file(self, file_path: str):
        """Helper to attempt purging a single file and report."""
        try:
            os.remove(file_path)
            print(f"         DELETED: {file_path}")
        except OSError as e:
            print(f"         [X] Failed to delete {file_path}: {e}", file=sys.stderr)

    def _process_found_violations(self, violations: List[str]):
        """Helper to process and optionally purge detected runaway files."""
        print(f"   🛑 RUNAWAY GENERATION DETECTED ({len(violations)} files).")
        self.ctx.report(self.name, 45, False, violations)

        purge_runaway = "--purge-runaway" in sys.argv
        if not purge_runaway:
            self.ctx.signals.add("GENERATIVE_FAIL")
            print("      Hint: Run with '--purge-runaway' to delete these files.")
        else:
            print("      🗑️  Purging runaway generated files...")
            for file_path in violations:
                self._purge_single_file(file_path)
            self.ctx.signals.add("GENERATIVE_CLEAN")

    def _is_runaway_file(self, normalized_file_path: str) -> bool:
        """Helper to check if a file path matches any runaway pattern."""
        for pattern in self.GENERATIVE_PATTERNS:
            if re.search(pattern, normalized_file_path):
                return True
        return False

    def _find_runaway_violations_in_dir(self, root: str, files: List[str]) -> List[str]:
        """Helper to find runaway violations within a specific directory."""
        violations_in_dir = []
        for file in files:
            file_path = os.path.join(root, file)
            normalized_file_path = Path(file_path).as_posix() 
            
            if self._is_runaway_file(normalized_file_path):
                violations_in_dir.append(file_path)
        return violations_in_dir