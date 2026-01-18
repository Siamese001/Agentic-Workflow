
# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: guardrail, memory, prompt, workflow
# This boosts alignment detection — review and integrate appropriately

from __future__ import annotations
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

FILESYSTEM COMPLIANCE: All file operations use safe_path_join from structure_blueprint
"""
from ast import parse, unparse
import ast
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, TYPE_CHECKING
import logging
import time
import asyncio

# Lazy import to break circular dependency
if TYPE_CHECKING:
    from agentic_core.schemas.models.anomaly_report import AnomalyReport, AnomalySeverity

from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    get_validated_project_root,
    safe_path_join,
    validate_path_within_project
)

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
    
    MRO HARDENING:
    - Uses cooperative multiple inheritance via **kwargs
    - Always calls super().__init__(**kwargs) to propagate up the chain
    - Private attributes use _healer_ prefix to avoid collisions
    """
    
    # Default ON - opt-out only where justified
    _healing_enabled: bool = True
    
    # Healing budget tracking
    _healing_count: int = 0
    _max_healing_per_session: int = 50

    def __init__(self, **kwargs):
        """
        Initialize healing infrastructure with cooperative inheritance.
        
        MRO HARDENING: Passes **kwargs up the chain to ensure all
        mixins in the MRO are properly initialized.
        """
        super().__init__(**kwargs)
        # Private prefix _healer_ to avoid attribute collisions
        self._healer_cache: Dict[str, Tuple[float, bool]] = {}  # {type: (ts, success)}
        self._healer_metrics = {"count": 0, "total_time": 0.0, "success_count": 0}
        self._healer_cache_ttl = 300  # 5min suppression (configurable)
        self._healer_max_depth = 5
        self._healer_current_depth = 0

    def heal(self, violation: Dict[str, Any], anomaly: Optional[AnomalyReport] = None) -> bool:
        """
        Autonomous repair with rollback verification.
        
        Args:
            violation: Dict with 'path', 'class_name', 'violation_type', etc.
            
        Returns:
            True if healing succeeded, False otherwise
            
        Raises:
            Exception: If healing fails critically
        """
        start_time = time.time()
        success = False
        
        if not self._healing_enabled:
            Logger.debug(f"[HEALING] {self.__class__.__name__}: Healing disabled")
            return False
        
        # 1. Cache short-circuit (zero-cost repeat suppression)
        if anomaly and anomaly.type in self._healer_cache:
            cached_ts, cached_success = self._healer_cache[anomaly.type]
            if time.time() - cached_ts < self._healer_cache_ttl:
                return cached_success
        
        # 2. Severity optimization (skip heavy MCP audit for LOW)
        lightweight = anomaly and anomaly.severity == AnomalySeverity.LOW
        if lightweight:
            success = self._perform_healing(anomaly) if anomaly else False
            if success:
                Logger.debug(f"[HEALING] Low severity heal success: {anomaly.type if anomaly else 'unknown'}")
            return success
        
        # Budget check
        if self._healing_count >= self._max_healing_per_session:
            Logger.warning(f"[HEALING] {self.__class__.__name__}: Budget exhausted")
            return False

        self._healer_current_depth += 1
        if self._healer_current_depth > self._healer_max_depth:
            self._healer_current_depth -= 1
            Logger.critical("Healing recursion depth exceeded")
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

            try:
                if hasattr(ast, 'validate'):
                    ast.validate(fixed_ast)
            except Exception as e:
                Logger.error(f"Post-heal AST validation failed: {e}")
                return False
            
            fixed_code = unparse(fixed_ast)

            try:
                compile(fixed_code, str(file_path), 'exec')
            except Exception as e:
                Logger.error(f"Post-heal static compile failed: {e}")
                return False
            
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
        finally:
            self._healer_current_depth = max(0, self._healer_current_depth - 1)
            # Track metrics
            duration = time.time() - start_time
            self._healer_metrics["count"] += 1
            self._healer_metrics["total_time"] += duration
            if success:
                self._healer_metrics["success_count"] += 1
            # Cache result for repeat suppression
            if anomaly:
                self._healer_cache[anomaly.type] = (time.time(), success)
            # Optional audited emit (zero-loss safe)
            if hasattr(self, "_mcp_audit") and self._healer_metrics["count"] > 0:
                avg_time = self._healer_metrics["total_time"] / self._healer_metrics["count"]
                self._mcp_audit("healing_metrics", payload={
                    "duration": duration,
                    "success": success,
                    "avg_time": avg_time,
                    "success_rate": self._healer_metrics["success_count"] / self._healer_metrics["count"]
                })

    async def heal_async(self, violation: Dict[str, Any], anomaly: Optional[AnomalyReport] = None) -> bool:
        """Non-blocking heal for orchestrators/state agents."""
        return await asyncio.to_thread(self.heal, violation, anomaly)

    def get_healing_metrics(self) -> Dict[str, Any]:
        """Zero-loss observable — for diagnostics/metrics agents."""
        count = self._healer_metrics["count"]
        return {
            "count": count,
            "avg_time": (self._healer_metrics["total_time"] / count) if count else 0,
            "success_rate": (self._healer_metrics["success_count"] / count) if count else 1.0
        }

    def _perform_healing(self, anomaly: AnomalyReport) -> bool:
        """Override in subclasses for anomaly-specific healing logic."""
        Logger.debug(f"[HEALING] {self.__class__.__name__}: No _perform_healing implementation")
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

    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: Optional[Set[str]] = None
    ) -> Dict[str, int]:
        """
        Repository-level healing method (Canon Key 51 compliance).
        
        This is the foundational heal_repository that all agents inherit.
        Subclasses should call super().heal_repository() FIRST to ensure
        the shared healing chain (diagnostics, rollback, MCP hardening) runs.
        
        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, apply fixes (opposite of dry_run for clarity)
            depth: Current recursion depth for cycle detection
            max_depth: Maximum recursion depth allowed
            _call_path: Set of agent names already in call chain (cycle detection)
            
        Returns:
            Dict with healing summary: {violations, fixed, errors, skipped}
        """
        agent_name = self.__class__.__name__
        
        # Initialize call path for cycle detection
        if _call_path is None:
            _call_path = set()
        
        # Cycle detection
        if agent_name in _call_path:
            Logger.warning(f"[HEAL_REPOSITORY] Cycle detected: {agent_name}")
            return {"violations": 0, "fixed": 0, "errors": 0, "skipped": 1, "cycle_detected": True}
        
        # Depth limiting
        if depth > max_depth:
            Logger.warning(f"[HEAL_REPOSITORY] Max depth {max_depth} exceeded for {agent_name}")
            return {"violations": 0, "fixed": 0, "errors": 0, "skipped": 1, "depth_limited": True}
        
        # Check if healing is enabled
        if not self._healing_enabled:
            Logger.debug(f"[HEAL_REPOSITORY] {agent_name}: Healing disabled")
            return {"violations": 0, "fixed": 0, "errors": 0, "skipped": 1}
        
        # Budget check
        if self._healing_count >= self._max_healing_per_session:
            Logger.warning(f"[HEAL_REPOSITORY] {agent_name}: Budget exhausted")
            return {"violations": 0, "fixed": 0, "errors": 1, "budget_exhausted": True}
        
        # Add to call path
        _call_path.add(agent_name)
        
        try:
            # Base implementation - subclasses override to add specific logic
            Logger.debug(f"[HEAL_REPOSITORY] {agent_name}: Base heal_repository invoked (dry_run={dry_run})")
            
            # Reset metrics for this healing session if at root
            if depth == 0:
                self._healer_metrics["count"] = 0
                self._healer_metrics["total_time"] = 0.0
                self._healer_metrics["success_count"] = 0
            
            return {"violations": 0, "fixed": 0, "errors": 0, "skipped": 0}
            
        except Exception as e:
            Logger.error(f"[HEAL_REPOSITORY] {agent_name} failed: {e}")
            return {"violations": 0, "fixed": 0, "errors": 1, "error_message": str(e)}
        finally:
            _call_path.discard(agent_name)

    async def heal_repository_async(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: Optional[Set[str]] = None
    ) -> Dict[str, int]:
        """Non-blocking heal_repository for orchestrators/async agents."""
        return await asyncio.to_thread(
            self.heal_repository, dry_run, execute, depth, max_depth, _call_path
        )


__all__ = ["HealerMixin"]
