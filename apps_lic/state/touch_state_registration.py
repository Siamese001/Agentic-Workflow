"""Touch State Registration for apps_lic.

Wave 1, Phase 3 of apps-lic-infra-prerequisites-unblock-p2p3

This module handles app-domain registration of touch state contracts,
enabling UWG integration for apps_lic multi-touch sequences.

App: apps_lic
Layer: App-specific state management

Dependencies:
    - UWG app_domain_registration (agentic_core/L4_state/uwg/app_domain_registration.py)
    - Touch state writer (agentic_core/L4_state/uwg/touch_state_writer.py)
    - Touch state schema (agentic_core/L4_state/schemas/apps_lic_touch_state.sql)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from agentic_core.L4_state.uwg.touch_state_writer import (
    TOUCH_STATE_WRITE_CLASS,
    TOUCH_STATE_SEVERITY,
    get_touch_state_write_class_severity,
)


# -----------------------------------------------------------------------------
# Touch State Contract Bundle
# -----------------------------------------------------------------------------

@dataclass(frozen=True)
class TouchStateContractSpec:
    """Specification for touch state contract registration.
    
    This is the app-domain contract that tells UWG how to handle
    apps_lic touch state writes.
    
    Fields
    ------
    app_id : str
        Always "apps_lic"
    write_class : str
        The UWG write class for touch state
    severity : WriteClassSeverity
        DURABLE (touch state must persist)
    schema_version : str
        Version of the touch state schema
    schema_path : str
        Path to the SQL schema file (relative to repo root)
    """
    
    app_id: str = "apps_lic"
    write_class: str = TOUCH_STATE_WRITE_CLASS
    severity: Any = TOUCH_STATE_SEVERITY  # WriteClassSeverity type
    schema_version: str = "1.0.0"
    schema_path: str = "agentic_core/L4_state/schemas/apps_lic_touch_state.sql"


# -----------------------------------------------------------------------------
# Registration
# -----------------------------------------------------------------------------

def build_touch_state_contract() -> dict[str, Any]:
    """Build the touch state contract bundle for UWG registration.
    
    This function creates the contract structure expected by
    app_domain_registration.register_bundle().
    
    Returns
    -------
    dict[str, Any]
        Contract bundle ready for UWG registration
    """
    write_class, severity = get_touch_state_write_class_severity()
    
    return {
        "contract": {
            "app_id": "apps_lic",
            "contract_type": "touch_state",
            "version": "1.0.0",
            "status": "active",
        },
        "write_classes": [
            {
                "write_class": write_class,
                "severity": severity.value,
                "description": "Multi-touch sequence state persistence",
                "tables": ["apps_lic_touch_state", "apps_lic_touch_state_transitions"],
            }
        ],
        "input_contract": None,  # Touch state is output-only from UWG perspective
        "output_schema": {
            "schema_type": "touch_state",
            "schema_version": "1.0.0",
            "schema_path": "agentic_core/L4_state/schemas/apps_lic_touch_state.sql",
            "primary_table": "apps_lic_touch_state",
        },
        "eval_rubrics": [],
        "threshold_profiles": [],
        "grader_rosters": [],
        "retrieval_profiles": [],
        "prompt_profiles": [],
        "capability_profiles": [],
        "route_profiles": [],
        "orchestration_profiles": [],
        "fixtures": [],
        "negative_controls": [],
    }


def register_touch_state_contract(
    gateway: Optional[Any] = None,
    store: Optional[Any] = None,
) -> Any:
    """Register apps_lic touch state contract with UWG.
    
    This function should be called during apps_lic spine initialization
    to register the touch state write class with UWG.
    
    Parameters
    ----------
    gateway : Optional[DurableWriteGateway]
        UWG instance. If None, uses process-global gateway.
    store : Optional[InMemoryAppDomainStore]
        In-memory store. If None, uses process-global store.
    
    Returns
    -------
    RegistrationReceipt
        Receipt from UWG registration
    
    Example
    -------
    >>> from apps_lic.state.touch_state_registration import register_touch_state_contract
    >>> receipt = register_touch_state_contract()
    >>> print(f"Touch state registered: {receipt.bundle_digest}")
    """
    from agentic_core.L4_state.uwg.app_domain_registration import (
        register_bundle,
        AppDomainContractBundle,
    )
    
    contract_dict = build_touch_state_contract()
    bundle = AppDomainContractBundle(**contract_dict)
    
    return register_bundle(bundle, gateway=gateway, store=store)


# -----------------------------------------------------------------------------
# Spine Integration
# -----------------------------------------------------------------------------

class TouchStateSpineIntegration:
    """Integration point for apps_lic spine initialization.
    
    This class provides the standard spine integration pattern for
    touch state registration.
    """
    
    @staticmethod
    def initialize(
        gateway: Optional[Any] = None,
        store: Optional[Any] = None,
    ) -> dict[str, Any]:
        """Initialize touch state for apps_lic spine.
        
        This method should be called during apps_lic spine startup,
        after UWG is initialized but before any touch operations.
        
        Parameters
        ----------
        gateway : Optional[DurableWriteGateway]
            UWG instance
        store : Optional[InMemoryAppDomainStore]
            In-memory store
        
        Returns
        -------
        dict[str, Any]
            {
                "status": "success|error",
                "receipt": RegistrationReceipt|None,
                "error": str|None,
            }
        """
        try:
            receipt = register_touch_state_contract(gateway=gateway, store=store)
            return {
                "status": "success",
                "receipt": receipt,
                "error": None,
            }
        except Exception as e:  # guardian: allow-broad-exception -- P2 burndown: fail-soft optional boundary
            return {
                "status": "error",
                "receipt": None,
                "error": str(e),
            }
    
    @staticmethod
    def is_registered(store: Optional[Any] = None) -> bool:
        """Check if touch state contract is already registered.
        
        Parameters
        ----------
        store : Optional[InMemoryAppDomainStore]
            In-memory store to check
        
        Returns
        -------
        bool
            True if touch state write class is registered
        """
        if store is None:
            from agentic_core.L4_state.uwg.app_domain_loader import get_store
            store = get_store()
        
        # Check if our write class is known
        try:
            return store.has_write_class(TOUCH_STATE_WRITE_CLASS)
        except AttributeError:
            # Store doesn't support write class lookup
            return False


# -----------------------------------------------------------------------------
# Convenience Entry Point
# -----------------------------------------------------------------------------

def initialize_touch_state() -> bool:
    """One-shot initialization of touch state for apps_lic.
    
    This is the primary entry point for apps_lic spine initialization.
    It registers the touch state contract with UWG and returns success status.
    
    Returns
    -------
    bool
        True if initialization succeeded
    
    Example
    -------
    >>> from apps_lic.state.touch_state_registration import initialize_touch_state
    >>> if initialize_touch_state():
    ...     print("Touch state ready")
    ... else:
    ...     print("Touch state initialization failed")
    """
    result = TouchStateSpineIntegration.initialize()
    return result["status"] == "success"


# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = [
    "TouchStateContractSpec",
    "build_touch_state_contract",
    "register_touch_state_contract",
    "TouchStateSpineIntegration",
    "initialize_touch_state",
]
