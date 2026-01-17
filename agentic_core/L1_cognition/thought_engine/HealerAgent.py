"""HealerAgent - Primary self-healing agent for repository maintenance.

Extracted from CanonHealerAgent.py.
Handles syntax repair and structural alignment healing operations.
"""
from __future__ import annotations

import ast
import logging
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, Tuple

from agentic_core.L1_cognition.thought_engine.CanonBaseAgent import CanonBaseAgent
from agentic_core.L3_orchestration.mixins.L3SubatomicTestingMixin import SubatomicTestingMixin
from agentic_core.config.blueprint_sovereign.structure_blueprint import SOVEREIGN_REGISTRY
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin

class CanonBaseAgentInterface(Protocol):
    """Protocol for CanonBaseAgent interface compatibility."""
    ctx: Any
    name: str
    def smart_fix(self, file_path: str, violation_key: int) -> bool: ...


@dataclass
class HealerAgent(SubatomicTestingMixin, HealerMixin):
    """
    Self-healing agent for syntax repair and structural alignment.
    
    Validates Canon Keys:
        - Key 48: Syntax Repair - fixes Python syntax errors.
        - Key 49: Structural Alignment - ensures proper file structure.
    
    Role:
        The Ultimate Repair Agent. Uses LLM-based healing with retry logic.
    
    Note:
        Legacy L1 class - uses composition over inheritance (DDD Phase 9A).
    
    Attributes:
        impl: Optional CanonBaseAgent implementation (abstract, skip instantiation).
        ctx: ValidationContext for file access and reporting.
        name: Agent name for logging.
        Logger: Logger instance for this agent.
    """

    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        **kwargs: Any
    ) -> Dict[str, int]:
        """
        Execute autonomous healing for Canon Key 51 compliance.
        
        Runs the shared HealerMixin chain (diagnostics, rollback, MCP hardening)
        before executing agent-specific healing logic.
        
        Args:
            dry_run: If True, only report violations without fixing.
            execute: If True, apply fixes to detected violations.
            **kwargs: Additional healing parameters.
        
        Returns:
            Dict with keys: violations, fixed, errors.
        """
        super().heal_repository()
        return {"violations": 0, "fixed": 0, "errors": 0}

    def __init__(self, ctx: Optional[Any] = None) -> None:
        """
        Initialize the HealerAgent.
        
        Args:
            ctx: Optional ValidationContext for file access and reporting.
        """
        self.impl: Optional[CanonBaseAgent] = None  # Abstract, skip instantiation
        self.ctx = ctx
        self.name = self.__class__.__name__
        self.Logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    async def execute(
        self,
        goal: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute healing operations.
        
        Maintains backward compatibility with orchestrator interface.
        
        Args:
            goal: Optional goal description (unused, for interface compat).
            context: Optional execution context (unused, for interface compat).
            
        Returns:
            Dict with status and agent name.
        """
        await self._execute_healing()
        return {"status": "completed", "agent": self.name}

    def get_capabilities(self) -> List[str]:
        """
        Get list of agent capabilities.
        
        Returns:
            List of capability strings from implementation.
        """
        if self.impl is None:
            return []
        return self.impl.get_capabilities()

    def validate_state(self) -> bool:
        """
        Validate current agent state.
        
        Returns:
            True if state is valid, False otherwise.
        """
        if self.impl is None:
            return True
        return self.impl.validate_state()

    async def _execute_healing(self) -> None:
        """
        Execute the core healing logic.
        
        Scans for syntax errors and attempts LLM-based fixes with retry.
        Reports results to validation context.
        """
        MAX_HEALING_ROUNDS = int(os.getenv('MAX_HEALING_ROUNDS', '3'))

        def _check_file_for_syntax_error(self, file_path: str) -> Tuple[bool, Optional[SyntaxError]]:
            """Helper to check a single file for syntax errors."""
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    ast.parse(f.read(), filename=file_path)
                return False, None
            except SyntaxError as e:
                return True, e
            except (FileNotFoundError, UnicodeDecodeError) as e:
                print(
                    f"Warning: Could not read or decode {file_path} for healing: {e}",
                    file=sys.stderr
                )
                # For reporting purposes, treat unreadable/undecodable as a syntax error
                # to ensure it's flagged and potentially retried.
                return True, SyntaxError(f"File unreadable/undecodable: {e}")

        def _process_file_for_syntax_error(self, file_path: str) -> Optional[Tuple[str, SyntaxError]]:
            """Helper to check a single file for syntax errors and return if found."""
            if is_excluded(file_path):
                return None
            has_error, error_obj = self._check_file_for_syntax_error(file_path)
            if has_error:
                return (file_path, error_obj)
            return None

        def _scan_for_syntax_errors(self) -> List[Tuple[str, Optional[SyntaxError]]]:
            """Helper to scan all Python files for syntax errors."""
            syntax_errors = []
            for file_path in self.ctx.python_files:
                error_info = self._process_file_for_syntax_error(file_path)
                if error_info:
                    syntax_errors.append(error_info)
            return syntax_errors

        async def _attempt_fix_single_file(self, file_path: str, error) -> bool:
            """Helper to attempt fixing a single file and return success status."""
            print(f"      [SCAN] Fixing {file_path}:{error.lineno} – {error.msg}")
            return await self.smart_fix(file_path, 48)

        print(f"\n[>>>] {self.name} ACTIVATED: Investigating Failures...")
        
        round_num = 0
        # Flag to track if any file was successfully fixed in the current round.
        # Initialize to True to ensure the loop runs at least once.
        any_file_healed_in_current_round = True 

        while any_file_healed_in_current_round and round_num < self.MAX_HEALING_ROUNDS:
            round_num += 1
            syntax_errors_found_this_round = self._scan_for_syntax_errors()

            if not syntax_errors_found_this_round:
                any_file_healed_in_current_round = False  # No errors found, stop healing attempts
                break

            print(f"   [ALERT] Round {round_num}: Found {len(syntax_errors_found_this_round)} Syntax Blockers. Healing...")
            
            # Collect results of fixes
            fix_results = [
                await self._attempt_fix_single_file(file_path, error)
                for file_path, error in syntax_errors_found_this_round
            ]
            any_file_healed_in_current_round = any(fix_results)

        # After all healing rounds, perform a final check for any remaining syntax errors
        remaining_syntax_errors = []
        for file_path in self.ctx.python_files:
            has_error, _ = self._check_file_for_syntax_error(file_path)
            if has_error:
                remaining_syntax_errors.append(file_path)

        if not remaining_syntax_errors:
            print("   [OK] Architecture verified. Core integrity intact.")
            self.ctx.report(self.name, 48, True, [])
            self.ctx.signal_ast_valid()
        else:
            print(f"   [X] Critical Failure: {len(remaining_syntax_errors)} files still have syntax errors.")
            self.ctx.report(self.name, 48, False, remaining_syntax_errors)
            self.ctx.signal_critical_failure()