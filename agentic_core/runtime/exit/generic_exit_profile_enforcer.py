"""Generic Exit profile enforcer — evaluates Exit gates for X3 disposition.

This engine is app-agnostic. It consumes:
- SealedL2Artifact (completed L2 work with receipts)
- Exit profile (app-specific gate configuration from app profile)
- GateMeshResult (optional, for conditional gates like G25)

Universal spine laws (hardcoded in generic engine):
- Exit emits exactly ONE X3
- UNKNOWN is never PASS (material UNKNOWN blocks allow)
- NOT_APPLICABLE requires explicit reason
- Durable write path: Exit X3C -> CommitRequest -> UWG -> L4
- No app code emits X3 (only core Exit)

App-specific policy (from app profiles, not hardcoded here):
- Required gates list (G21, G22, G23, G24, G26, G28, etc.)
- Conditional gates configuration (G25, G27)
- G27 read-only draft policy
- App-specific gate verdict thresholds

Reference: W5B P1 apps_lic Exit migration plan
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Sequence, Protocol

logger = logging.getLogger(__name__)


class GateVerdict(str, Enum):
    """Canonical gate verdicts."""
    
    PASS = "PASS"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class X3Decision(str, Enum):
    """Canonical X3 disposition decisions."""
    
    ALLOW = "ALLOW"
    BLOCK = "BLOCK"
    ESCALATE = "ESCALATE"
    DEFER = "DEFER"


@dataclass(frozen=True)
class ExitProfileSpec:
    """App-provided Exit profile specification.
    
    This is app-specific policy passed from app profile. Generic engine
    does NOT hardcode any app-specific gate IDs here.
    """
    
    # App identification (for logging/telemetry only)
    app_id: str
    
    # Required gates that must PASS for ALLOW
    required_gates: Sequence[str] = field(default_factory=tuple)
    
    # Conditional gate configurations
    conditional_gates: Mapping[str, "ConditionalGateConfig"] = field(default_factory=dict)
    
    # G27 configuration for read-only draft handling
    g27_config: "G27Config" | None = None
    
    # App-specific gate verdict thresholds
    gate_thresholds: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ConditionalGateConfig:
    """Configuration for a conditional gate (like G25, G27)."""
    
    gate_id: str
    condition_field: str  # Field in GateMeshResult to check
    condition_value: Any  # Value that triggers gate evaluation
    verdict_on_trigger: GateVerdict  # Verdict when condition met
    verdict_on_skip: GateVerdict  # Verdict when condition not met


@dataclass(frozen=True)
class G27Config:
    """G27 read-only draft configuration."""
    
    enabled: bool = True
    read_only_draft_field: str = "read_only_draft"
    required_reason_on_not_applicable: bool = True


@dataclass(frozen=True)
class GateMeshResult:
    """Result from GateMesh evaluation."""
    
    gate_id: str
    verdict: GateVerdict
    reason: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class X3Disposition:
    """Exit X3 disposition result."""
    
    decision: X3Decision
    reason: str
    gate_receipts: Mapping[str, GateVerdict]
    required_gates_passed: bool
    material_unknown_present: bool
    not_applicable_with_reason: bool
    app_id: str


class ExitProfileEnforcer:
    """Generic Exit profile enforcer — app-agnostic gate evaluator.
    
    Universal spine laws enforced here (not in app bindings):
    1. Exit emits exactly ONE X3
    2. UNKNOWN is never PASS (material UNKNOWN blocks allow)
    3. NOT_APPLICABLE requires reason
    4. Only core Exit emits X3
    """
    
    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def evaluate_exit(
        self,
        l2_artifact: "SealedL2Artifact",
        profile_spec: ExitProfileSpec,
        gate_mesh_results: Mapping[str, GateMeshResult] | None = None,
    ) -> X3Disposition:
        """Evaluate Exit gates using app profile.
        
        Args:
            l2_artifact: Sealed L2 artifact with completed work
            profile_spec: App-specific Exit profile specification
            gate_mesh_results: Optional GateMesh results for conditional gates
            
        Returns:
            X3Disposition with decision and gate receipts
        """
        self.logger.debug(
            "Exit evaluating app=%s with %d required gates",
            profile_spec.app_id,
            len(profile_spec.required_gates)
        )
        
        gate_receipts: dict[str, GateVerdict] = {}
        required_gates_passed = True
        material_unknown_present = False
        not_applicable_with_reason = True  # Assume valid until proven otherwise
        
        # Evaluate required gates
        for gate_id in profile_spec.required_gates:
            verdict = self._evaluate_required_gate(
                gate_id, l2_artifact, gate_mesh_results
            )
            gate_receipts[gate_id] = verdict
            
            # Universal spine law: UNKNOWN is never PASS
            if verdict == GateVerdict.UNKNOWN:
                material_unknown_present = True
                required_gates_passed = False
            
            # FAIL also blocks
            if verdict == GateVerdict.FAIL:
                required_gates_passed = False
            
            # NOT_APPLICABLE requires reason
            if verdict == GateVerdict.NOT_APPLICABLE:
                if not self._has_not_applicable_reason(gate_id, gate_mesh_results):
                    not_applicable_with_reason = False
        
        # Evaluate conditional gates (G25, G27)
        for gate_id, config in profile_spec.conditional_gates.items():
            verdict = self._evaluate_conditional_gate(
                config, l2_artifact, gate_mesh_results
            )
            gate_receipts[gate_id] = verdict
            
            if verdict == GateVerdict.UNKNOWN:
                material_unknown_present = True
            
            if verdict == GateVerdict.NOT_APPLICABLE:
                if not self._has_not_applicable_reason(gate_id, gate_mesh_results):
                    not_applicable_with_reason = False
        
        # Determine X3 decision
        decision = self._determine_x3_decision(
            required_gates_passed,
            material_unknown_present,
            not_applicable_with_reason,
        )
        
        reason = self._build_decision_reason(
            decision,
            gate_receipts,
            required_gates_passed,
            material_unknown_present,
        )
        
        return X3Disposition(
            decision=decision,
            reason=reason,
            gate_receipts=gate_receipts,
            required_gates_passed=required_gates_passed,
            material_unknown_present=material_unknown_present,
            not_applicable_with_reason=not_applicable_with_reason,
            app_id=profile_spec.app_id,
        )
    
    def _evaluate_required_gate(
        self,
        gate_id: str,
        l2_artifact: "SealedL2Artifact",
        gate_mesh_results: Mapping[str, GateMeshResult] | None,
    ) -> GateVerdict:
        """Evaluate a required gate."""
        # Check if we have a GateMesh result for this gate
        if gate_mesh_results and gate_id in gate_mesh_results:
            return gate_mesh_results[gate_id].verdict
        
        # No GateMesh result: evaluate from artifact
        # For W5B P1, default to PASS if artifact has required receipts
        # Apps can override via profile
        self.logger.debug("No GateMesh result for %s, evaluating from artifact", gate_id)
        
        # Universal spine law: missing required gate fails closed
        return GateVerdict.UNKNOWN
    
    def _evaluate_conditional_gate(
        self,
        config: ConditionalGateConfig,
        l2_artifact: "SealedL2Artifact",
        gate_mesh_results: Mapping[str, GateMeshResult] | None,
    ) -> GateVerdict:
        """Evaluate a conditional gate (G25, G27)."""
        # Check if condition is triggered
        condition_met = self._check_condition(
            config.condition_field,
            config.condition_value,
            l2_artifact,
            gate_mesh_results,
        )
        
        if condition_met:
            # Condition triggered: evaluate the gate
            if gate_mesh_results and config.gate_id in gate_mesh_results:
                return gate_mesh_results[config.gate_id].verdict
            return config.verdict_on_trigger
        else:
            # Condition not met: skip with configured verdict
            return config.verdict_on_skip
    
    def _check_condition(
        self,
        field: str,
        value: Any,
        l2_artifact: "SealedL2Artifact",
        gate_mesh_results: Mapping[str, GateMeshResult] | None,
    ) -> bool:
        """Check if conditional gate condition is met."""
        # Check GateMesh results first
        if gate_mesh_results:
            for result in gate_mesh_results.values():
                if result.metadata.get(field) == value:
                    return True
        
        # Check L2 artifact
        if hasattr(l2_artifact, field):
            return getattr(l2_artifact, field) == value
        
        if hasattr(l2_artifact, 'metadata') and isinstance(l2_artifact.metadata, dict):
            return l2_artifact.metadata.get(field) == value
        
        return False
    
    def _has_not_applicable_reason(
        self,
        gate_id: str,
        gate_mesh_results: Mapping[str, GateMeshResult] | None,
    ) -> bool:
        """Check if NOT_APPLICABLE gate has required reason."""
        if not gate_mesh_results:
            return False
        
        if gate_id not in gate_mesh_results:
            return False
        
        result = gate_mesh_results[gate_id]
        return result.verdict == GateVerdict.NOT_APPLICABLE and result.reason is not None
    
    def _determine_x3_decision(
        self,
        required_gates_passed: bool,
        material_unknown_present: bool,
        not_applicable_with_reason: bool,
    ) -> X3Decision:
        """Determine X3 decision based on gate evaluation."""
        # Universal spine law: material UNKNOWN blocks allow
        if material_unknown_present:
            return X3Decision.BLOCK
        
        # Required gates must all pass
        if not required_gates_passed:
            return X3Decision.BLOCK
        
        # NOT_APPLICABLE must have reason
        if not not_applicable_with_reason:
            return X3Decision.ESCALATE
        
        # All checks passed: ALLOW
        return X3Decision.ALLOW
    
    def _build_decision_reason(
        self,
        decision: X3Decision,
        gate_receipts: Mapping[str, GateVerdict],
        required_gates_passed: bool,
        material_unknown_present: bool,
    ) -> str:
        """Build human-readable decision reason."""
        if decision == X3Decision.ALLOW:
            return f"All {len(gate_receipts)} gates satisfied"
        
        if material_unknown_present:
            unknown_gates = [
                gid for gid, v in gate_receipts.items() if v == GateVerdict.UNKNOWN
            ]
            return f"Material UNKNOWN present in gates: {unknown_gates}"
        
        if not required_gates_passed:
            failed_gates = [
                gid for gid, v in gate_receipts.items() if v == GateVerdict.FAIL
            ]
            return f"Required gates failed: {failed_gates}"
        
        return "Exit evaluation completed"


# Placeholder for SealedL2Artifact (would be imported from contracts module)
class SealedL2Artifact:
    """Placeholder for SealedL2Artifact type."""
    pass


# Singleton instance for use by thin adapter bindings
_generic_exit_enforcer: ExitProfileEnforcer | None = None


def get_generic_exit_enforcer() -> ExitProfileEnforcer:
    """Get or create singleton generic Exit enforcer instance."""
    global _generic_exit_enforcer
    if _generic_exit_enforcer is None:
        _generic_exit_enforcer = ExitProfileEnforcer()
    return _generic_exit_enforcer


__all__ = [
    "ExitProfileEnforcer",
    "ExitProfileSpec",
    "ConditionalGateConfig",
    "G27Config",
    "GateMeshResult",
    "X3Disposition",
    "GateVerdict",
    "X3Decision",
    "get_generic_exit_enforcer",
]
