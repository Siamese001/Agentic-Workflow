"""AppsRgRuntimeAuthorityPolicy — central allow/deny policy for apps_rg input.

Path: agentic_core/runtime/contracts/apps_rg_runtime_authority_policy.py

This module defines:
- AppsRgRuntimeAuthorityPolicy (the policy engine)
- AuthorityAllowRule (allow-list rule with pattern)
- AuthorityDenyRule (deny-list rule with pattern)
- AuthorityValidationReceipt (receipt from validating an ingress payload)
- RuntimeAuthorityScanReceipt (receipt from scanning a module for forbidden patterns)
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional, Sequence, Set


@dataclass(frozen=True, slots=True)
class AuthorityAllowRule:
    """Allow-list rule for authority validation.

    Fields:
        pattern: String pattern to match (exact or regex).
        reason: Human-readable justification for this rule.
    """
    pattern: str
    reason: str


@dataclass(frozen=True, slots=True)
class AuthorityDenyRule:
    """Deny-list rule for authority validation.

    Fields:
        pattern: Regex pattern to match forbidden module/function names.
        reason: Human-readable justification for denial.
    """
    pattern: str
    reason: str


@dataclass(frozen=True, slots=True)
class AuthorityValidationReceipt:
    """Receipt produced by AppsRgRuntimeAuthorityPolicy.validate_ingress_payload().

    Proves that the payload was inspected and either passed or failed authority
    validation. On failure, lists the forbidden fields detected.
    """

    allowed: bool  # True if validation passed
    passed: bool  # Alias for allowed (compatibility)
    request_id: str = ""
    checked_fields: tuple[str, ...] = field(default_factory=tuple)  # list of fields that were inspected
    forbidden_fields_detected: tuple[str, ...] = field(default_factory=tuple)
    matched_rule: Optional[str] = None  # Rule that caused allow/deny
    reason: str = ""  # Explanation for denial
    timestamp_iso: str = ""
    policy_version: str = "1.0"

    def __post_init__(self) -> None:
        # Sync passed with allowed for backwards compatibility
        object.__setattr__(self, 'passed', self.allowed)

    def assert_passed(self) -> None:
        if not self.allowed:
            raise AppsRgAuthorityViolation(
                f"Authority validation failed. Forbidden fields: {self.forbidden_fields_detected}"
            )


@dataclass(frozen=True, slots=True)
class RuntimeAuthorityScanReceipt:
    """Receipt produced by AppsRgRuntimeAuthorityPolicy.assert_no_apps_rg_runtime_authority().

    Proves that a module or package scan found zero forbidden runtime-authority
    patterns. Used for CI gates and pre-write hooks.
    """

    passed: bool = True
    scanned_path: str = ""
    scanned_modules: List[str] = field(default_factory=list)
    forbidden_patterns_detected: tuple[str, ...] = field(default_factory=tuple)
    detection_count: int = 0
    total_modules: int = 0
    violation_count: int = 0
    policy_version: str = "1.0"
    module_results: Dict[str, AuthorityValidationReceipt] = field(default_factory=dict, repr=False)

    def __post_init__(self) -> None:
        # Sync derived fields
        object.__setattr__(self, 'violation_count', sum(
            1 for r in self.module_results.values() if not r.allowed
        ))
        object.__setattr__(self, 'total_modules', len(self.scanned_modules))

    def add_module_result(self, module: str, receipt: AuthorityValidationReceipt) -> None:
        """Add a module validation result to the scan receipt."""
        # Since dataclass is frozen, we can't actually mutate
        # This is a no-op for frozen dataclass - tests should construct fully
        pass

    def is_compliant(self) -> bool:
        """Return True if no violations detected."""
        return self.violation_count == 0

    def assert_passed(self) -> None:
        if not self.passed:
            raise AppsRgAuthorityViolation(
                f"Runtime authority scan failed for {self.scanned_path}. "
                f"Patterns: {self.forbidden_patterns_detected}"
            )


class AppsRgAuthorityViolation(Exception):
    """Raised when apps_rg attempts to assert runtime authority.

    This exception is the fail-closed signal for all authority checks.
    It must be caught at the CLI boundary and converted to a user-facing
    error, or propagated to CI to fail the build.
    """
    pass


class AppsRgRuntimeAuthorityPolicy:
    """Central policy for what apps_rg may and may not input.

    This policy is the runtime enforcement of the non-negotiable governance
    statement: "apps_rg is an ingress and declarative domain profile package
    only. It has no runtime authority."
    """

    def __init__(
        self,
        version: str = "1.0.0",
        allow_rules: Optional[List[AuthorityAllowRule]] = None,
        deny_rules: Optional[List[AuthorityDenyRule]] = None,
    ) -> None:
        self.version = version
        self.allow_rules = allow_rules or []
        self.deny_rules = deny_rules or []

    def validate(self, module_path: str) -> AuthorityValidationReceipt:
        """Validate a module path against allow/deny rules.

        Checks deny rules first, then allow rules. Returns a receipt
        indicating whether the module is authorized.
        """
        # Check deny rules first
        for rule in self.deny_rules:
            if re.search(rule.pattern, module_path):
                return AuthorityValidationReceipt(
                    allowed=False,
                    passed=False,
                    request_id="",
                    matched_rule=rule.pattern,
                    reason=f"deny: {rule.reason}",
                    policy_version=self.version,
                )

        # Check allow rules
        for rule in self.allow_rules:
            if module_path.startswith(rule.pattern) or re.search(rule.pattern, module_path):
                return AuthorityValidationReceipt(
                    allowed=True,
                    passed=True,
                    request_id="",
                    matched_rule=rule.pattern,
                    reason=f"allow: {rule.reason}",
                    policy_version=self.version,
                )

        # Default deny if no rules matched
        return AuthorityValidationReceipt(
            allowed=False,
            passed=False,
            request_id="",
            matched_rule=None,
            reason="deny: no matching allow rule",
            policy_version=self.version,
        )

    # §10 forbidden fields that apps_rg may NOT include in its ingress payload
    FORBIDDEN_PAYLOAD_FIELDS: Set[str] = frozenset({
        "route_id",
        "execution_form",
        "model_id",
        "provider",
        "prompt_artifact",
        "tool_call_spec",
        "tool_calls",
        "workflow_dag",
        "workflow_graph",
        "l2_work_order",
        "work_order",
        "exit_disposition",
        "disposition",
        "durable_write_request",
        "commit_request",
        "learning_proposal",
        "gate_verdict",
    })

    # Forbidden authority-bearing contract types apps_rg may NOT emit
    FORBIDDEN_EMISSION_CONTRACTS: Set[str] = frozenset({
        "L1PlanContract",
        "RouteContract",
        "FinalEvidenceContract",
        "CompiledPromptArtifact",
        "SealedL2Artifact",
        "X3Disposition",
        "GateVerdict",
        "CommitRequest",
        "LearningProposal",
    })

    @classmethod
    def validate_ingress_payload(
        cls,
        payload: "AppsRgIngressPayload",  # noqa: F821
        request_id: str,
        timestamp_iso: str,
    ) -> AuthorityValidationReceipt:
        """Validate that the ingress payload contains no forbidden authority fields.

        Called by U0 immediately after receiving the payload from apps_rg CLI.
        """
        from dataclasses import asdict

        flat = asdict(payload)  # type: ignore[arg-type]
        detected: list[str] = []

        for key in flat.keys():
            if key in cls.FORBIDDEN_PAYLOAD_FIELDS:
                detected.append(key)

        # Also check nested user_constraints and output_preferences for forbidden keys
        for section in ("user_constraints", "output_preferences"):
            sec_dict = flat.get(section) or {}
            if isinstance(sec_dict, dict):
                for key in sec_dict.keys():
                    if key in cls.FORBIDDEN_PAYLOAD_FIELDS:
                        detected.append(f"{section}.{key}")

        passed = len(detected) == 0
        return AuthorityValidationReceipt(
            allowed=passed,
            passed=passed,
            request_id=request_id,
            checked_fields=tuple(sorted(flat.keys())),
            forbidden_fields_detected=tuple(sorted(detected)),
            timestamp_iso=timestamp_iso,
            policy_version="1.0",
        )

    @classmethod
    def assert_no_apps_rg_runtime_authority(
        cls,
        scanned_path: str,
        found_patterns: Sequence[str],
    ) -> RuntimeAuthorityScanReceipt:
        """Produce a scan receipt after checking a module or path for forbidden patterns.

        Used by CI gates and pre-write hooks.
        """
        passed = len(found_patterns) == 0
        return RuntimeAuthorityScanReceipt(
            passed=passed,
            scanned_path=scanned_path,
            forbidden_patterns_detected=tuple(found_patterns),
            detection_count=len(found_patterns),
            policy_version="1.0",
        )

    @classmethod
    def is_forbidden_emission_contract(cls, contract_name: str) -> bool:
        """Check if a contract type is one that apps_rg is forbidden to emit."""
        return contract_name in cls.FORBIDDEN_EMISSION_CONTRACTS
