"""UWG Stage U3: CHECK CATALOG RULES - RBAC, blast radius, diff validation.

10C-REQ-124: Verify RBAC blast radius structure constraints before-after diff
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .uwg_clerk import WriteRequest


@dataclass
class BlastRadius:
    """Blast radius analysis for a proposed change."""
    file_count: int = 0
    downstream_dependencies: list[str] = field(default_factory=list)
    layer_crossings: list[str] = field(default_factory=list)
    risk_score: float = 0.0  # 0.0-1.0


@dataclass
class DiffValidation:
    """Before-after diff validation result."""
    before_hash: str = ""
    after_hash: str = ""
    structural_change: bool = False
    breaking_change: bool = False


@dataclass
class CatalogRuleResult:
    """Result of catalog rule checking."""
    rbac_allowed: bool
    blast_radius_acceptable: bool
    diff_valid: bool
    structure_valid: bool
    rejection_reason: str = ""
    blast_radius: BlastRadius | None = None
    diff_validation: DiffValidation | None = None


class UWGCatalogChecker:
    """UWG Stage U3: Check catalog rules.

    10C-REQ-124: Verify RBAC blast radius structure constraints
    perform before-after diff validation of knowledge base.
    """

    def __init__(self) -> None:
        self._rbac_rules: dict[str, list[str]] = {}  # actor_id -> allowed_paths
        self._blast_radius_threshold: float = 0.5
        self._structure_rules: list[str] = []

    def check(self, request: WriteRequest, before_state: bytes | None = None) -> CatalogRuleResult:
        """Check all catalog rules for a write request."""
        rbac_ok = self._check_rbac(request)
        blast = self._analyze_blast_radius(request)
        blast_ok = blast.risk_score <= self._blast_radius_threshold
        diff = self._validate_diff(request, before_state)
        diff_ok = not diff.breaking_change
        struct_ok = self._check_structure(request)

        all_ok = all([rbac_ok, blast_ok, diff_ok, struct_ok])

        if not all_ok:
            reasons = []
            if not rbac_ok:
                reasons.append("rbac_denied")
            if not blast_ok:
                reasons.append(f"blast_radius_too_high:{blast.risk_score:.2f}")
            if not diff_ok:
                reasons.append("breaking_change_detected")
            if not struct_ok:
                reasons.append("structure_constraint_violated")

            return CatalogRuleResult(
                rbac_allowed=rbac_ok,
                blast_radius_acceptable=blast_ok,
                diff_valid=diff_ok,
                structure_valid=struct_ok,
                rejection_reason=";".join(reasons),
                blast_radius=blast,
                diff_validation=diff,
            )

        return CatalogRuleResult(
            rbac_allowed=True,
            blast_radius_acceptable=True,
            diff_valid=True,
            structure_valid=True,
            blast_radius=blast,
            diff_validation=diff,
        )

    def _check_rbac(self, request: WriteRequest) -> bool:
        """Check RBAC rules for actor."""
        if request.actor_id not in self._rbac_rules:
            return True  # Allow if no specific rules

        allowed_paths = self._rbac_rules[request.actor_id]
        path = Path(request.path)

        for allowed in allowed_paths:
            if path.match(allowed) or str(path).startswith(allowed):
                return True
        return False

    def _analyze_blast_radius(self, request: WriteRequest) -> BlastRadius:
        """Analyze blast radius of proposed change."""
        # Stub - actual implementation uses ADG impact analysis
        return BlastRadius(
            file_count=1,
            downstream_dependencies=[],
            layer_crossings=[],
            risk_score=0.1,  # Low risk default
        )

    def _validate_diff(self, request: WriteRequest, before_state: bytes | None) -> DiffValidation:
        """Validate before-after diff."""
        if before_state is None or request.data is None:
            return DiffValidation(structural_change=False, breaking_change=False)

        before_hash = hash(before_state) % (10**10)
        after_hash = hash(request.data) % (10**10)

        # Simple heuristic: size change > 50% is structural
        size_diff = abs(len(request.data) - len(before_state))
        structural = size_diff > len(before_state) * 0.5 if before_state else False

        return DiffValidation(
            before_hash=str(before_hash),
            after_hash=str(after_hash),
            structural_change=structural,
            breaking_change=structural,  # Conservative: structural = breaking
        )

    def _check_structure(self, request: WriteRequest) -> bool:
        """Check structure constraints."""
        # Stub - actual implementation checks layer gravity, etc.
        return True

    def set_blast_radius_threshold(self, threshold: float) -> None:
        """Set blast radius threshold (0.0-1.0)."""
        self._blast_radius_threshold = max(0.0, min(1.0, threshold))

    def register_rbac(self, actor_id: str, allowed_paths: list[str]) -> None:
        """Register RBAC rule for actor."""
        self._rbac_rules[actor_id] = allowed_paths
