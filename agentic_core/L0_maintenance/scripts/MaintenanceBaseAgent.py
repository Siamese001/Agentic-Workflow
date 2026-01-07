"""MaintenanceBaseAgent — L0 Base with Subatomic Delegation Framework (Jan 01, 2026)

L0 Maintenance agents handle bootstrapping, filesystem reconciliation, and healing.
Subatomic CRITIQUE hop includes:
- NO basic self-testing (L0 = infrastructure, not Artifact production)
- YES delegation to TestSovereigntyAgent on healing failures

Table Decision (L0 Maintenance):
- Basic Self-Testing: NO
- Delegation to TestSovereigntyAgent: YES (on healing failure)
"""
from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.utils.core_extensions.timeout_decorator import timeout
from agentic_core.utils.core_extensions.redis_cache_mixin import RedisCacheMixin
from agentic_core.utils.core_extensions.pinecone_vector_mixin import PineconeVectorMixin

# [PHASE 2] L0 Delegated Testing Mixin
from agentic_core.L0_maintenance.bases.l0_delegation_testing_mixin import L0DelegationTestingMixin


class L0SovereignSeverity(Enum):
    """Sovereign event Severity levels for L0 delegation."""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class L0DelegationMixin(MCPHardenedMixin):
    """Mixin providing L0 delegation-only capabilities.
    
    L0 Table Decision:
    - Basic Self-Testing: NO (infrastructure layer)
    - Delegation to TestSovereigntyAgent: YES (on healing failure)
    
    L0 agents don't produce executable artifacts like L2-L4.
    They perform infrastructure operations (bootstrap, reconcile, heal).
    On failure, delegate to TestSovereigntyAgent for validation.
    """

    async def delegate_on_failure(self, operation: str, error: str, context: Dict) -> Dict:
        """L0 CRITIQUE: Delegate to TestSovereigntyAgent on operation failure.
        
        Args:
            operation: The maintenance operation that failed
            error: Error message from the failure
            context: Execution context with Task info
            
        Returns:
            Dict with specialist validation result
        """
        self._emit_l0_event(L0SovereignSeverity.WARNING, "L0_OPERATION_FAILED", {
            "operation": operation,
            "error": error[:200]
        })
        
        # Delegate to TestSovereigntyAgent for validation
        ValidationResult = await self._delegate_to_specialist(operation, error, context)
        
        if ValidationResult["passed"]:
            self._emit_l0_event(L0SovereignSeverity.INFO, "L0_SPECIALIST_VALIDATED", {
                "operation": operation,
                "Recommendation": "retry_safe"
            })
        else:
            self._emit_l0_event(L0SovereignSeverity.ERROR, "L0_SPECIALIST_REJECTED", {
                "operation": operation,
                "reason": ValidationResult.get("error", "unknown")
            })
        
        return ValidationResult

    async def validate_healing_result(self, healed_code: str, original_code: str, context: Dict) -> Dict:
        """Validate healing result by delegating to TestSovereigntyAgent.
        
        L0 healing agents should call this after producing healed code
        to get specialist validation before committing.
        
        Args:
            healed_code: The healed/fixed code
            original_code: Original code before healing
            context: Healing context with Violation info
            
        Returns:
            Dict with validation result
        """
        self._emit_l0_event(L0SovereignSeverity.INFO, "L0_HEALING_VALIDATION_REQUESTED", {
            "original_lines": len(original_code.splitlines()),
            "healed_lines": len(healed_code.splitlines())
        })
        
        # Delegate to specialist for comprehensive testing
        result = await self._delegate_healing_to_specialist(healed_code, context)
        
        if result["passed"]:
            self._emit_l0_event(L0SovereignSeverity.INFO, "L0_HEALING_VALIDATED", {
                "tests_passed": len(result.get("tests", []))
            })
        else:
            self._emit_l0_event(L0SovereignSeverity.ERROR, "L0_HEALING_REJECTED", {
                "reason": result.get("error", "validation_failed")
            })
        
        return result

    async def _delegate_to_specialist(self, operation: str, error: str, context: Dict) -> Dict:
        """Delegate failure analysis to TestSovereigntyAgent."""
        try:
#             from agentic_core.L5_safety.validators.TestSovereigntyAgent import TestSovereigntyAgent  # Refactored to dynamic import (Sprint 1)
def _get_test_sovereignty_agent():
    """Lazy load TestSovereigntyAgent to avoid L0 → L5 dependency."""
    import importlib
    module = importlib.import_module('agentic_core.L5_safety.validators.TestSovereigntyAgent')
    return module.TestSovereigntyAgent
            
            specialist = TestSovereigntyAgent()
            result = await specialist.execute({
                "type": "basic",
                "context": {
                    "layer": "L0",
                    "operation": operation,
                    "error": error
                }
            })
            return result
        except ImportError:
            return {"passed": False, "error": "TestSovereigntyAgent not available", "tests": []}
        except Exception as e:
            return {"passed": False, "error": str(e), "tests": []}

    async def _delegate_healing_to_specialist(self, healed_code: str, context: Dict) -> Dict:
        """Delegate healed code validation to TestSovereigntyAgent."""
        try:
#             from agentic_core.L5_safety.validators.TestSovereigntyAgent import TestSovereigntyAgent  # Refactored to dynamic import (Sprint 1)
            
            specialist = TestSovereigntyAgent()
            result = await specialist.execute({
                "Artifact": healed_code,
                "type": "python_code_integration",
                "coverage_target": 95
            })
            return result
        except ImportError:
            return {"passed": False, "error": "TestSovereigntyAgent not available", "tests": []}
        except Exception as e:
            return {"passed": False, "error": str(e), "tests": []}

    def _emit_l0_event(self, Severity: L0SovereignSeverity, event_type: str, payload: Optional[Dict] = None) -> None:
        """Emit L0 delegation event for observability."""
        self.log_info(f"SUBATOMIC L0 {Severity.value} | {event_type}")
        if payload:
            self.log_info(f"Payload: {payload}")


@dataclass
class MaintenanceBaseAgent(SovereignBaseAgent, L0DelegationMixin, L0DelegationTestingMixin, RedisCacheMixin, PineconeVectorMixin):
    """Base class for L0 Maintenance agents with delegation-only testing.
    
    HARDENED: Now with Redis caching + Pinecone vector support.
    
    NOTE: _healing_enabled = False for L0 boot isolation safety.
    
    L0 Table Decision:
    - Basic Self-Testing: NO (infrastructure layer, no Artifact production)
    - Delegation to TestSovereigntyAgent: YES (on healing/operation failure)
    
    L0 agents handle:
    - Bootstrapping
    - Filesystem reconciliation
    - Healing orchestration
    - Infrastructure maintenance
    
    They don't produce executable artifacts like L2-L4, so no self-testing.
    On failure, delegate to TestSovereigntyAgent for validation.
    """

    # [PHASE 3] L0 boot isolation safety - healing disabled
    _healing_enabled: bool = False
    
    # [PHASE 2] Redis/Pinecone integration
    _cache_prefix: str = "l0_maintenance"
    _namespace: str = "l0_patterns"

    async def maintain(self, Task: Dict) -> Dict:
        """Execute maintenance logic. Override in subclasses."""
        raise NotImplementedError(f"{self.name} must implement maintain()")

    async def execute_with_delegation(self, Task: Dict) -> Dict:
        """Execute with L0 delegation on failure.
        
        Subclasses should call this to get automatic delegation
        to TestSovereigntyAgent on operation failures.
        """
        try:
            # INIT/THINK/ACT
            result = await self.maintain(Task)
            
            # If healing was performed, validate with specialist
            if result.get("healed_code"):
                validation = await self.validate_healing_result(
                    healed_code=result["healed_code"],
                    original_code=result.get("original_code", ""),
                    context=Task
                )
                result["validation"] = validation
                if not validation["passed"]:
                    result["validation_failed"] = True
            
            return result
            
        except Exception as e:
            # On failure, delegate for analysis
            delegation_result = await self.delegate_on_failure(
                operation=Task.get("operation", "unknown"),
                error=str(e),
                context=Task
            )
            return {
                "success": False,
                "error": str(e),
                "delegation_result": delegation_result
            }

    @timeout(300)
    def heal_repository(self, dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: Optional[set] = None) -> Dict[str, int]:
        """L0 maintenance base agent - invoke shared healing chain."""
        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            super().heal_repository(dry_run=dry_run, execute=execute, depth=depth, max_depth=max_depth, _call_path=_call_path)
            self.log_info("L0 maintenance - healing chain invoked")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)
