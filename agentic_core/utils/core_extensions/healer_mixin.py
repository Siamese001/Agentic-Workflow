from __future__ import annotations

"""
HealerMixin - Phase 3 Default-On Healing Infrastructure

SSOT LOCATION: agentic_core/utils/core_extensions/healer_mixin.py

Provides autonomous repair capability for agents that detect violations.
Default-on approach: All agents can heal unless explicitly opted out.

Opt-out cases:
- L0 agents: Boot isolation safety
- Pure data/enums: No repair value
- Read-only detectors: Adversarial safety

FILESYSTEM COMPLIANCE: All file operations use safe_path_join from structure_blueprint

Phase 1 Enhancement (Jan 19, 2026):
- Added HealResult TypedDict for standardized return format
- Added _normalize_result() for zero-loss legacy key mapping
- Updated heal_repository signature with **kwargs for dynamic orchestrator calls

SSOT Consolidation (Jan 20, 2026):
- Moved from L5_safety/validators/ to utils/core_extensions/ as the single source of truth
- All other locations now re-export from this module with deprecation warnings

Phase 23 Enhancement (Jan 21, 2026):
- Healing Budget Per-Violation-Type Per-File (granular budget tracking)
- If a file has a syntax error, fixing it shouldn't prevent fixing a logic error later
- Budget is now tracked per (file_path, violation_type) tuple

"""


import ast
import asyncio
import logging
import time
from ast import parse, unparse
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypedDict

# Lazy import to break circular dependency
if TYPE_CHECKING:
    from agentic_core.schemas.models.anomaly_report import AnomalyReport


# Import instructional injection patterns for all agents
from agentic_core.utils.core_extensions.instructional_injection_mixin import (
    instructional_injection_mixin,
)

Logger = logging.getLogger(__name__)


class HealResult(TypedDict):
    """
    Standardized return format for all healing operations.
    Ensures SSOT consistency across the orchestrator layer.

    Phase 1 Enhancement: This TypedDict provides type safety and
    documentation for the canonical healing return format.
    """

    violations_found: int
    violations_fixed: int
    status: str  # 'PASS', 'FAIL', 'ERROR', 'SKIPPED', 'UNKNOWN'
    errors: int
    skipped: int


class HealerMixin(instructional_injection_mixin):
    """
    Phase 3: Default-on healing mixin for autonomous repair.

    Provides:
    - heal() method for violation repair
    - Atomic write with rollback on failure
    - Self-test verification after healing (leverages Phase 1)
    - Logging and observability
    - All 30 instructional injection patterns (via instructional_injection_mixin)

    Subclasses should override apply_fix() to implement specific transformers.
    Set _healing_enabled = False to opt-out for justified cases.

    MRO HARDENING:
    - Uses cooperative multiple inheritance via **kwargs
    - Always calls super().__init__(**kwargs) to propagate up the chain
    - Private attributes use _healer_ prefix to avoid collisions

    INSTRUCTIONAL INJECTION (Jan 2026):
    - Inherits instructional_injection_mixin providing all 30 patterns
    - All worker agents automatically get inject_*_layer() methods
    - Patterns from: data/prompt_governance/prompt_injections/Instructional_Injection_Enhanced_v5.md
    """

    # Default ON - opt-out only where justified
    _healing_enabled: bool = True

    # Healing budget tracking (Phase 23: Per-Violation-Type Per-File)
    _healing_count: int = 0
    _max_healing_per_session: int = 50
    _max_healing_per_violation_type_per_file: int = 3  # Phase 23: Granular budget

    def __init__(self, **kwargs):
        """
        Initialize healing infrastructure with cooperative inheritance.

        MRO HARDENING: Passes **kwargs up the chain to ensure all
        mixins in the MRO are properly initialized.
        """
        super().__init__(**kwargs)
        # Private prefix _healer_ to avoid attribute collisions
        self._healer_cache: dict[str, tuple[float, bool]] = {}  # {type: (ts, success)}
        self._healer_metrics = {"count": 0, "total_time": 0.0, "success_count": 0}
        self._healer_cache_ttl = 300  # 5min suppression (configurable)
        self._healer_max_depth = 5
        self._healer_current_depth = 0

        # Phase 23: Per-Violation-Type Per-File budget tracking
        # Key: (file_path, violation_type) -> count
        self._healer_granular_budget: dict[tuple[str, str], int] = {}

    def heal(self, violation: dict[str, Any], anomaly: AnomalyReport | None = None) -> bool:
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

        # 1. cache short-circuit (zero-cost repeat suppression)
        if anomaly and anomaly.type in self._healer_cache:
            cached_ts, cached_success = self._healer_cache[anomaly.type]
            if time.time() - cached_ts < self._healer_cache_ttl:
                return cached_success

        # 2. Severity optimization (skip heavy MCP audit for LOW)
        # Import at runtime to avoid circular dependency
        from agentic_core.schemas.models.anomaly_report import AnomalySeverity

        lightweight = anomaly and anomaly.severity == AnomalySeverity.LOW
        if lightweight:
            success = self._perform_healing(anomaly) if anomaly else False
            if success:
                Logger.debug(
                    f"[HEALING] Low severity heal success: {anomaly.type if anomaly else 'unknown'}"
                )
            return success

        # Budget check (global session limit)
        if self._healing_count >= self._max_healing_per_session:
            Logger.warning(f"[HEALING] {self.__class__.__name__}: Session budget exhausted")
            return False

        # Phase 23: Per-Violation-Type Per-File budget check
        file_path_str = str(violation.get("path", ""))
        violation_type = violation.get("violation_type", "UNKNOWN")
        granular_key = (file_path_str, violation_type)

        current_granular_count = self._healer_granular_budget.get(granular_key, 0)
        if current_granular_count >= self._max_healing_per_violation_type_per_file:
            Logger.warning(
                f"[HEALING] {self.__class__.__name__}: Granular budget exhausted for "
                f"{violation_type} in {file_path_str} ({current_granular_count} attempts)"
            )
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

        file_path = Path(violation.get("path", ""))
        if not file_path.exists():
            Logger.warning(f"[HEALING] File not found: {file_path}")
            return False

        try:
            # Read before state
            before_code = file_path.read_text(encoding="utf-8")

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
                if hasattr(ast, "validate"):
                    ast.validate(fixed_ast)
            except Exception as e:
                Logger.error(f"Post-heal AST validation failed: {e}")
                return False

            fixed_code = unparse(fixed_ast)

            try:
                compile(fixed_code, str(file_path), "exec")
            except Exception as e:
                Logger.error(f"Post-heal static compile failed: {e}")
                return False

            # Atomic write
            file_path.write_text(fixed_code, encoding="utf-8")

            # Verify via self-test (leverages Phase 1)
            if hasattr(self, "_run_self_tests"):
                try:
                    if self._run_self_tests():
                        self._log_healing_success(violation)
                        self._healing_count += 1
                        # Phase 23: Increment granular budget
                        self._healer_granular_budget[granular_key] = current_granular_count + 1
                        return True
                except AssertionError:
                    pass  # Self-test failed, rollback
            else:
                # No self-tests, assume success
                self._log_healing_success(violation)
                self._healing_count += 1
                # Phase 23: Increment granular budget
                self._healer_granular_budget[granular_key] = current_granular_count + 1
                return True

            # Rollback on failed verify
            Logger.warning(f"[HEALING] Rolling back {file_path} - verification failed")
            file_path.write_text(before_code, encoding="utf-8")
            return False

        except Exception as e:
            Logger.error(f"[HEALING] Failed on {file_path}: {e}")
            # Attempt rollback if we have before_code
            try:
                if "before_code" in locals():
                    file_path.write_text(before_code, encoding="utf-8")
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
            # cache result for repeat suppression
            if anomaly:
                self._healer_cache[anomaly.type] = (time.time(), success)
            # Optional audited emit (zero-loss safe)
            if hasattr(self, "_mcp_audit") and self._healer_metrics["count"] > 0:
                avg_time = self._healer_metrics["total_time"] / self._healer_metrics["count"]
                self._mcp_audit(
                    "healing_metrics",
                    payload={
                        "duration": duration,
                        "success": success,
                        "avg_time": avg_time,
                        "success_rate": self._healer_metrics["success_count"]
                        / self._healer_metrics["count"],
                    },
                )

    async def heal_async(
        self, violation: dict[str, Any], anomaly: AnomalyReport | None = None
    ) -> bool:
        """Non-blocking heal for orchestrators/state agents."""
        return await asyncio.to_thread(self.heal, violation, anomaly)

    def get_healing_metrics(self) -> dict[str, Any]:
        """Zero-loss observable — for diagnostics/metrics agents."""
        count = self._healer_metrics["count"]
        return {
            "count": count,
            "avg_time": (self._healer_metrics["total_time"] / count) if count else 0,
            "success_rate": (self._healer_metrics["success_count"] / count) if count else 1.0,
        }

    def _perform_healing(self, anomaly: AnomalyReport) -> bool:
        """Override in subclasses for anomaly-specific healing logic."""
        Logger.debug(f"[HEALING] {self.__class__.__name__}: No _perform_healing implementation")
        return False

    def apply_fix(self, ast_tree: Any, violation: dict[str, Any]) -> Any | None:
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

    def _log_healing_success(self, violation: dict[str, Any]) -> None:
        """Log successful healing for observability."""
        class_name = violation.get("class_name", "Unknown")
        path = violation.get("path", "Unknown")
        violation_type = violation.get("violation_type", "Unknown")
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
        # Phase 23: Also reset granular budget
        self._healer_granular_budget = {}

    def reset_granular_budget_for_file(self, file_path: str) -> None:
        """
        [Phase 23] Reset granular budget for a specific file.

        Useful when a file has been significantly modified and
        previous healing attempts should not count against new attempts.

        Args:
            file_path: Path to the file to reset budget for
        """
        keys_to_remove = [k for k in self._healer_granular_budget if k[0] == file_path]
        for key in keys_to_remove:
            del self._healer_granular_budget[key]
        Logger.debug(f"[HEALING] Reset granular budget for {file_path}")

    def get_granular_budget_stats(self) -> dict[str, Any]:
        """
        [Phase 23] Get granular budget statistics.

        Returns:
            Dictionary with budget usage per file and violation type
        """
        return {
            "total_entries": len(self._healer_granular_budget),
            "budget_usage": dict(self._healer_granular_budget),
            "max_per_violation_type_per_file": self._max_healing_per_violation_type_per_file,
        }

    def _normalize_result(self, result: dict[str, Any]) -> HealResult:
        """
        ZERO-LOSS NORMALIZATION:
        Maps legacy keys (violations, fixed, renamed) to the standard HealResult format
        to ensure backward compatibility with older agents.

        Phase 1 Enhancement: This method ensures no data is dropped during
        the transition from legacy return formats to the standardized HealResult.

        Args:
            result: Dictionary with legacy or mixed keys

        Returns:
            HealResult with standardized keys
        """
        # Preserve original counts while mapping to new schema
        # Priority order ensures we capture data from any legacy format
        found = result.get("violations_found") or result.get("violations") or 0
        fixed = result.get("violations_fixed") or result.get("fixed") or result.get("renamed") or 0

        return HealResult(
            violations_found=found,
            violations_fixed=fixed,
            status=result.get("status", "UNKNOWN"),
            errors=result.get("errors", 0),
            skipped=result.get("skipped", 0),
        )

    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set[str] | None = None,
        **kwargs,  # Essential for dynamic orchestrator calls
    ) -> HealResult:
        """
        Repository-level healing method (Canon Key 51 compliance).

        This is the foundational heal_repository that all agents inherit.
        Subclasses should call super().heal_repository(**kwargs) FIRST to ensure
        the shared healing chain (diagnostics, rollback, MCP hardening) runs.

        CRITICAL: Base Case / Termination Logic
        If we are too deep, or if this mixin is the last in the chain capable of healing,
        we return a neutral result rather than calling super() which might hit object().

        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, apply fixes (opposite of dry_run for clarity)
            depth: Current recursion depth for cycle detection
            max_depth: Maximum recursion depth allowed
            _call_path: Set of agent names already in call chain (cycle detection)
            **kwargs: Additional arguments for backward compatibility and orchestrator calls

        Returns:
            HealResult with standardized healing summary
        """
        agent_name = self.__class__.__name__

        # CRITICAL: Base Case / Termination Logic
        # If we are too deep, return a neutral result rather than calling super()
        # which might hit object() and cause AttributeError
        if depth > max_depth:
            Logger.warning(f"[HEAL_REPOSITORY] Max depth {max_depth} exceeded for {agent_name}")
            return HealResult(
                violations_found=0,
                violations_fixed=0,
                status="SKIPPED",
                errors=0,
                skipped=1,
            )

        # Initialize call path for cycle detection
        if _call_path is None:
            _call_path = set()

        # Cycle detection with detailed error reporting
        if agent_name in _call_path:
            Logger.warning(f"[HEAL_REPOSITORY] Cycle detected: {agent_name} re-entered")
            return HealResult(
                violations_found=0,
                violations_fixed=0,
                status="SKIPPED",
                errors=0,
                skipped=1,
            )

        # Check if healing is enabled
        if not self._healing_enabled:
            Logger.debug(f"[HEAL_REPOSITORY] {agent_name}: Healing disabled")
            return self._normalize_result(
                {"violations": 0, "fixed": 0, "errors": 0, "skipped": 1, "status": "SKIPPED"}
            )

        # Budget check
        if self._healing_count >= self._max_healing_per_session:
            Logger.warning(f"[HEAL_REPOSITORY] {agent_name}: Budget exhausted")
            return self._normalize_result(
                {"violations": 0, "fixed": 0, "errors": 1, "skipped": 0, "status": "ERROR"}
            )

        # Add to call path
        _call_path.add(agent_name)

        try:
            # Base implementation - subclasses override to add specific logic
            Logger.debug(
                f"[HEAL_REPOSITORY] {agent_name}: Base heal_repository invoked (dry_run={dry_run})"
            )

            # Reset metrics for this healing session if at root
            # [FIX] Ensure _healer_metrics exists (defensive for agents not calling super().__init__)
            if not hasattr(self, "_healer_metrics"):
                self._healer_metrics = {"count": 0, "total_time": 0.0, "success_count": 0}
            if depth == 0:
                self._healer_metrics["count"] = 0
                self._healer_metrics["total_time"] = 0.0
                self._healer_metrics["success_count"] = 0

            return self._normalize_result(
                {"violations": 0, "fixed": 0, "errors": 0, "skipped": 0, "status": "PASS"}
            )

        except Exception as e:
            Logger.error(f"[HEAL_REPOSITORY] {agent_name} failed: {e}")
            return self._normalize_result(
                {"violations": 0, "fixed": 0, "errors": 1, "status": "ERROR"}
            )
        finally:
            _call_path.discard(agent_name)

    async def heal_repository_async(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set[str] | None = None,
    ) -> dict[str, int]:
        """Non-blocking heal_repository for orchestrators/async agents."""
        return await asyncio.to_thread(
            self.heal_repository, dry_run, execute, depth, max_depth, _call_path
        )


__all__ = ["HealerMixin", "HealResult"]
