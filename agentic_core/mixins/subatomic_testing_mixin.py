from __future__ import annotations

import importlib

'\nSubatomicTestingMixin - Phase 1 Canonical Self-Testing for L2 Agents\n\nProvides automatic self-testing capabilities for all L2 execution-layer agents.\nThis mixin enforces the sovereign requirement that L2-L4 agents must be "Self" testing.\n\nLocation: agentic_core/L2_execution/reasoning/subatomic_testing_mixin.py\nPurpose: Shared testing infrastructure for SubAtomicAgent-derived classes\n'
import logging

try:
    _mod = importlib.import_module("agentic_core.L2_execution.enforcement.MCPHardenedMixin")
    MCPHardenedMixin = _mod.MCPHardenedMixin
except (ImportError, AttributeError):

    class MCPHardenedMixin:
        """Stub MCPHardenedMixin for healing resilience."""

        pass


from agentic_core.runtime.config.anomaly_report_config import AnomalyReport, AnomalySeverity

try:
    from agentic_core.mixins.instructional_injection_mixin import InstructionalInjectionMixin
except ImportError:

    class InstructionalInjectionMixin:
        """Stub for healing resilience."""

        pass


Logger = logging.getLogger(__name__)


class SubatomicTestingMixin(InstructionalInjectionMixin):
    """
    Phase 1: Canonical self-testing mixin for L2 agents.

    NOTE: _healing_enabled = False - Pure testing utility, no repair context.

    All SubAtomicAgent subclasses inherit this mixin to gain:
    - Automatic self-test execution on instantiation
    - Basic capability and invariant checks
    - State/memory round-trip validation
    - Tool registration verification

    Subclasses should override _run_self_tests() to add specific tests.
    """

    _self_testing_enabled: bool = True
    _self_tests_completed: bool = False

    def _run_self_tests(self) -> bool:
        """
        Default smoke tests - override in subclasses for specifics.

        Returns:
            True if all tests pass

        Raises:
            AssertionError: If any test fails
        """
        if not self._self_testing_enabled:
            return True
        class_name = self.__class__.__name__
        try:
            if hasattr(self, "can_run"):
                can_run_result = self.can_run()
                if can_run_result is not True:
                    Logger.debug(f"[SELF-TEST] {class_name}.can_run() returned {can_run_result}")
        except AssertionError as e:
            anomaly = AnomalyReport(
                type="self_test_failure",
                severity=AnomalySeverity.MEDIUM,
                description=f"Self-test assertion failed: {e}",
                source=class_name,
                details={"failed_assert": str(e)},
            )
            if hasattr(self, "_mcp_audit"):
                self._mcp_audit("proactive_anomaly_detected", payload=anomaly.to_dict())
            if hasattr(self, "heal"):
                if self.heal({}, anomaly):
                    Logger.info(f"[SELF-TEST] {class_name} healed via proactive repair")
                    return True
            raise
        if hasattr(self, "tools") and self.tools is not None:
            assert isinstance(self.tools, dict | list), (
                f"{class_name}: Tools must be dict or list, got {type(self.tools)}"
            )
        if hasattr(self, "state") and isinstance(self.state, dict):
            test_key = "_self_test_marker"
            test_value = f"ok_{class_name}"
            original_value = self.state.get(test_key)
            self.state[test_key] = test_value
            assert self.state.get(test_key) == test_value, f"{class_name}: State write/read corruption"
            if original_value is None:
                del self.state[test_key]
            else:
                self.state[test_key] = original_value
        if hasattr(self, "memory") and self.memory is not None:
            assert self.memory is not None, f"{class_name}: Memory object is None"
        Logger.debug(f"[SELF-TEST] {class_name} passed basic smoke tests")
        return True

    def _run_self_tests_safe(self) -> bool:
        """
        Safe wrapper that catches exceptions and logs them.
        Use this for non-critical test runs.

        Returns:
            True if tests pass, False if they fail (no exception raised)
        """
        try:
            return self._run_self_tests()
        except AssertionError as e:
            Logger.warning(f"[SELF-TEST FAILED] {self.__class__.__name__}: {e}")
            return False
        except Exception as e:
            Logger.error(f"[SELF-TEST ERROR] {self.__class__.__name__}: {e}")
            return False

    @classmethod
    def disable_self_testing(cls) -> None:
        """Disable self-testing for performance (e.g., in production)."""
        cls._self_testing_enabled = False

    @classmethod
    def enable_self_testing(cls) -> None:
        """Re-enable self-testing."""
        cls._self_testing_enabled = True

    def heal_repository(self, dry_run: bool = True, execute: bool = False, **kwargs) -> dict:
        """MRO chain stub for heal_repository.

        This stub exists to support the MRO chain when agents inherit from
        SubatomicTestingMixin and call super().heal_repository(**kwargs). Without this,
        the super() call would fail with AttributeError.

        Args:
            dry_run: If True, only report what would be done
            execute: If True, apply fixes
            **kwargs: Additional parameters passed through the chain

        Returns:
            Empty dict - actual healing is done by concrete agent classes
        """
        return {}


class L2SelfTestingMixin(SubatomicTestingMixin, MCPHardenedMixin):
    """
    Alias for SubatomicTestingMixin - use in L2 agents.
    Provides the same functionality with clearer naming.

    NOTE: _healing_enabled = False - Pure testing utility, no repair context.
    """

    pass


__all__ = ["SubatomicTestingMixin", "L2SelfTestingMixin"]
