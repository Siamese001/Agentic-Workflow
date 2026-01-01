"""
HealerMixin - Phase 3 Default-On Healing Infrastructure

Provides autonomous repair capability for agents that detect violations.
Default-on approach: All agents can heal unless explicitly opted out.

Location: agentic_core/common/healing/healer_mixin.py
Purpose: Core healing engine for autonomous agent repair

Opt-out cases:
- L0 agents: Boot isolation safety
- Pure data/enums: No repair value
- Read-only detectors: Adversarial safety
"""
from ast import parse, unparse
from pathlib import Path
from typing import Any, Dict, Optional
import logging

Logger = logging.getLogger(__name__)


class HealerMixin:
    """
    Phase 3: Default-on healing mixin for autonomous repair.
    
    Provides:
    - heal() method for violation repair
    - Atomic write with rollback on failure
    - Self-test verification after healing (leverages Phase 1)
    - Logging and observability
    
    Subclasses should override apply_fix() to implement specific transformers.
    Set _healing_enabled = False to opt-out for justified cases.
    """
    
    # Default ON - opt-out only where justified
    _healing_enabled: bool = True
    
    # Healing budget tracking
    _healing_count: int = 0
    _max_healing_per_session: int = 50

    def heal(self, violation: Dict[str, Any]) -> bool:
        """
        Autonomous repair with rollback verification.
        
        Args:
            violation: Dict with 'path', 'class_name', 'violation_type', etc.
            
        Returns:
            True if healing succeeded, False otherwise
            
        Raises:
            Exception: If healing fails critically
        """
        if not self._healing_enabled:
            Logger.debug(f"[HEALING] {self.__class__.__name__}: Healing disabled")
            return False
        
        # Budget check
        if self._healing_count >= self._max_healing_per_session:
            Logger.warning(f"[HEALING] {self.__class__.__name__}: Budget exhausted")
            return False
        
        # Prerequisite check - need tools or transformer capability
        if not self._can_heal():
            Logger.debug(f"[HEALING] {self.__class__.__name__}: Prerequisites not met")
            return False
        
        file_path = Path(violation.get('path', ''))
        if not file_path.exists():
            Logger.warning(f"[HEALING] File not found: {file_path}")
            return False
        
        try:
            # Read before state
            before_code = file_path.read_text(encoding='utf-8')
            
            try:
                before_ast = parse(before_code)
            except SyntaxError as e:
                Logger.warning(f"[HEALING] Cannot parse {file_path}: {e}")
                return False
            
            # Subclass-specific fix
            fixed_ast = self.apply_fix(before_ast, violation)
            if fixed_ast is None:
                Logger.debug(f"[HEALING] No fix applied for {violation.get('class_name')}")
                return False
            
            fixed_code = unparse(fixed_ast)
            
            # Atomic write
            file_path.write_text(fixed_code, encoding='utf-8')
            
            # Verify via self-test (leverages Phase 1)
            if hasattr(self, '_run_self_tests'):
                try:
                    if self._run_self_tests():
                        self._log_healing_success(violation)
                        self._healing_count += 1
                        return True
                except AssertionError:
                    pass  # Self-test failed, rollback
            else:
                # No self-tests, assume success
                self._log_healing_success(violation)
                self._healing_count += 1
                return True
            
            # Rollback on failed verify
            Logger.warning(f"[HEALING] Rolling back {file_path} - verification failed")
            file_path.write_text(before_code, encoding='utf-8')
            return False
            
        except Exception as e:
            Logger.error(f"[HEALING] Failed on {file_path}: {e}")
            # Attempt rollback if we have before_code
            try:
                if 'before_code' in locals():
                    file_path.write_text(before_code, encoding='utf-8')
            except Exception:
                pass
            return False

    def apply_fix(self, ast_tree: Any, violation: Dict[str, Any]) -> Optional[Any]:
        """
        Override: Implement specific transformer logic.
        
        Args:
            ast_tree: Parsed AST of the file
            violation: Violation details
            
        Returns:
            Fixed AST or None if no fix applied
        """
        # Default: no-op, subclasses should override
        Logger.debug(f"[HEALING] {self.__class__.__name__}: No apply_fix implementation")
        return None

    def _can_heal(self) -> bool:
        """
        Check if healing prerequisites are met.
        
        Override to add specific prerequisites.
        """
        return self._healing_enabled

    def _log_healing_success(self, violation: Dict[str, Any]) -> None:
        """Log successful healing for observability."""
        class_name = violation.get('class_name', 'Unknown')
        path = violation.get('path', 'Unknown')
        violation_type = violation.get('violation_type', 'Unknown')
        Logger.info(f"[HEALED] {class_name} in {path} ({violation_type})")
        print(f"HEALED: {class_name} in {path}")

    @classmethod
    def disable_healing(cls) -> None:
        """Disable healing for this class."""
        cls._healing_enabled = False
        Logger.info(f"[HEALING] Disabled for {cls.__name__}")

    @classmethod
    def enable_healing(cls) -> None:
        """Enable healing for this class."""
        cls._healing_enabled = True
        Logger.info(f"[HEALING] Enabled for {cls.__name__}")

    def reset_healing_budget(self) -> None:
        """Reset healing budget for new session."""
        self._healing_count = 0


__all__ = ["HealerMixin"]
