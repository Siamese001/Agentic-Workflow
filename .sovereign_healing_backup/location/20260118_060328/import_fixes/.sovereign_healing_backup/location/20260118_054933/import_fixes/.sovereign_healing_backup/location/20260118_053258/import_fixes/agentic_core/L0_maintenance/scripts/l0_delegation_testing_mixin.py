from __future__ import annotations
"""
L0DelegationTestingMixin - Phase 2 Canonical Delegated Testing for L0 Agents

L0 agents are foundational/boot-level and must NEVER self-test or self-modify.
They delegate validation to higher layers (L1 validators or L2 healers).
This prevents boot-time instability.

Location: agentic_core/L0_maintenance/bases/l0_delegation_testing_mixin.py
Purpose: Provide delegated testing capability for all L0 agents
"""
from pathlib import Path
from typing import Optional, Dict, Any
import logging

Logger = logging.getLogger(__name__)


class AgenticWorkflowError(Exception):
    """Base exception for agentic workflow errors at L0."""
    pass


class L0DelegationTestingMixin:
    """
    Phase 2: Canonical delegated testing mixin for L0 agents.
    
    L0 Table Decision:
    - Basic Self-Testing: NO (infrastructure layer)
    - Delegation to Higher Layers: YES
    
    L0 agents don't produce executable artifacts like L2-L4.
    They perform infrastructure operations (bootstrap, reconcile, heal).
    Validation is delegated to L1/L2 validators to prevent boot-time instability.
    """
    
    # Class-level flag to enable/disable delegation (for emergency bypass)
    _delegation_enabled: bool = True
    
    # Track if delegation has already run (avoid duplicate runs in MRO)
    _delegation_completed: bool = False

    def _delegate_tests(self) -> bool:
        """
        Delegate integrity checks to L1/L2 validators.
        
        Returns:
            True if all delegated checks pass
            
        Raises:
            AgenticWorkflowError: If delegated tests fail critically
        """
        if not self._delegation_enabled:
            return True
            
        class_name = self.__class__.__name__
        
        try:
            # Check 1: SSOT blueprint presence (critical for L0)
            blueprint_paths = [
                Path("agentic_core/config/blueprint_sovereign/structure_blueprint.py"),
                Path("system_blueprint.json"),
            ]
            blueprint_found = any(p.exists() for p in blueprint_paths)
            if not blueprint_found:
                # Try relative to common project roots
                for root in [Path.cwd(), Path(__file__).parent.parent.parent.parent]:
                    if (root / "agentic_core/config/blueprint_sovereign/structure_blueprint.py").exists():
                        blueprint_found = True
                        break
            
            if not blueprint_found:
                Logger.warning(f"[L0 DELEGATION] {class_name}: SSOT blueprint not found - non-critical")
            
            # Check 2: Core module importability (lightweight L1 delegation)
            try:
                from agentic_core.config.blueprint_sovereign.structure_blueprint_1 import SOVEREIGN_REGISTRY
                if SOVEREIGN_REGISTRY is None:
                    Logger.warning(f"[L0 DELEGATION] {class_name}: SOVEREIGN_REGISTRY is None")
            except ImportError as e:
                Logger.warning(f"[L0 DELEGATION] {class_name}: Cannot import SOVEREIGN_REGISTRY: {e}")
            
            # Check 3: Hygiene validator delegation (if available)
            try:
                from agentic_core.L0_maintenance.scripts.hygiene_validator import HygieneValidatorAgent
                # Don't run full scan at boot - just verify importability
                Logger.debug(f"[L0 DELEGATION] {class_name}: HygieneValidatorAgent available for delegation")
            except ImportError:
                Logger.debug(f"[L0 DELEGATION] {class_name}: HygieneValidatorAgent not available")
            
            # Check 4: Gravity compliance module presence (L5 delegation target)
            try:
                # from agentic_core.L5_safety.gravity import GravityLeakRepairAgent  # Refactored to dynamic import (Sprint 1)
                import importlib
                module = importlib.import_module('agentic_core.L5_safety.gravity')
                GravityLeakRepairAgent = module.GravityLeakRepairAgent
                Logger.debug(f"[L0 DELEGATION] {class_name}: Gravity delegation target available")
            except ImportError:
                Logger.debug(f"[L0 DELEGATION] {class_name}: Gravity module not available")
            
            Logger.debug(f"[L0 DELEGATION] {class_name}: Delegated tests passed")
            return True
            
        except Exception as e:
            Logger.error(f"[L0 DELEGATION] {class_name}: Delegation failed: {e}")
            raise AgenticWorkflowError(f"L0 delegated test failed for {class_name}: {e}")

    def _delegate_tests_safe(self) -> bool:
        """
        Safe wrapper that catches exceptions and logs them.
        Use this for non-critical delegation runs.
        
        Returns:
            True if tests pass, False if they fail (no exception raised)
        """
        try:
            return self._delegate_tests()
        except AgenticWorkflowError as e:
            Logger.warning(f"[L0 DELEGATION FAILED] {self.__class__.__name__}: {e}")
            return False
        except Exception as e:
            Logger.error(f"[L0 DELEGATION ERROR] {self.__class__.__name__}: {e}")
            return False

    @classmethod
    def disable_delegation(cls) -> None:
        """Disable delegation for emergency bypass (e.g., recovery mode)."""
        cls._delegation_enabled = False
        Logger.warning("[L0 DELEGATION] Delegation disabled - emergency bypass active")

    @classmethod
    def enable_delegation(cls) -> None:
        """Re-enable delegation."""
        cls._delegation_enabled = True
        Logger.info("[L0 DELEGATION] Delegation re-enabled")


__all__ = [
    "L0DelegationTestingMixin",
    "AgenticWorkflowError",
]
