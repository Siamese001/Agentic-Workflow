"""C0 Governance and Safety Enforcement - Cross-cutting policy plane.

Implements 10C GAP-10C-003:
- G1: Triage Mode Selection (determine governance level)
- G2: Authority Context Binding (attach policy to request)
- G3: Layer Isolation Check (verify no boundary violations)
- G4: Registry Validation (allowed set verification)
- G5: Classify/Shape (route categorization)
- G6: Policy Chokepoint (actual enforcement)
- G7: Sovereign Egress (fail-closed exit)
"""

from .triage_selector import TriageSelector, TriageLevel
from .authority_binder import AuthorityBinder, AuthorityContext
from .isolation_checker import IsolationChecker, BoundaryCheck
from .registry_validator import RegistryValidator, ValidationResult
from .classifier_shaper import ClassifierShaper, RouteCategory
from .policy_chokepoint import PolicyChokepoint, ChokepointDecision
from .sovereign_egress import SovereignEgress, EgressResult

__all__ = [
    "TriageSelector",
    "TriageLevel",
    "AuthorityBinder",
    "AuthorityContext",
    "IsolationChecker",
    "BoundaryCheck",
    "RegistryValidator",
    "ValidationResult",
    "ClassifierShaper",
    "RouteCategory",
    "PolicyChokepoint",
    "ChokepointDecision",
    "SovereignEgress",
    "EgressResult",
]
