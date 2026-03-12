"""G-16-28: Approval gates for System Learning governance.

Deterministic approval decision logic for change packages.

Invariants:
  - All gates are deterministic
  - Risk classification is rule-based
  - High impact defaults to REJECT unless explicitly overridden
"""
from __future__ import annotations
from enum import Enum
from typing import Any, Protocol
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

class ApprovalDecision(Enum):
    """Approval decision for change package."""
    APPROVE = 'APPROVE'
    REJECT = 'REJECT'

class ApprovalGate(Protocol):
    """Protocol for approval gate."""

    def decide(self, pkg: Any, rca: Any, snapshot: Any) -> ApprovalDecision:
        """Decide whether to approve change package.

        Parameters
        ----------
        pkg : Any
            Change package to evaluate.
        rca : Any
            RCA report.
        snapshot : Any
            Snapshot.

        Returns
        -------
        ApprovalDecision
            APPROVE or REJECT.
        """
        ...

class RiskTierClassifier(Protocol):
    """Protocol for risk tier classification."""

    def classify(self, pkg: Any) -> int:
        """Classify risk tier of change package.

        Parameters
        ----------
        pkg : Any
            Change package to classify.

        Returns
        -------
        int
            Risk tier (higher = more risky).
        """
        ...

class DefaultRuleBasedGate:
    """Default deterministic rule-based approval gate.

    Rules:
      - High impact (risk tier >= 3): REJECT by default
      - Low impact (risk tier < 3): APPROVE

    High impact criteria:
      - Touches more than K surfaces
      - Delta exceeds threshold
      - Affects L5 (safety-critical)
    """

    # guardian: allow-magic-config
    def __init__(self, risk_classifier: RiskTierClassifier, high_impact_threshold: int=3, allow_high_impact: bool=False):
        """Initialize approval gate.

        Parameters
        ----------
        risk_classifier : RiskTierClassifier
            Risk tier classifier.
        high_impact_threshold : int
            Threshold for high impact (default 3).
        allow_high_impact : bool
            Whether to allow high impact changes (default False).
        """
        self.risk_classifier = risk_classifier
        self.high_impact_threshold = high_impact_threshold
        self.allow_high_impact = allow_high_impact

    def decide(self, pkg: Any, rca: Any, snapshot: Any) -> ApprovalDecision:
        """Decide whether to approve change package.

        Parameters
        ----------
        pkg : Any
            Change package to evaluate.
        rca : Any
            RCA report.
        snapshot : Any
            Snapshot.

        Returns
        -------
        ApprovalDecision
            APPROVE or REJECT.
        """
        risk_tier = self.risk_classifier.classify(pkg)
        if risk_tier >= self.high_impact_threshold:
            if self.allow_high_impact:
                return ApprovalDecision.APPROVE
            return ApprovalDecision.REJECT
        return ApprovalDecision.APPROVE

class DefaultRiskClassifier:
    """Default deterministic risk tier classifier.

    Risk tiers:
      0: No change
      1: Low impact (single surface, small delta)
      2: Medium impact (multiple surfaces, moderate delta)
      3: High impact (many surfaces, large delta, or L5)
      4: Critical impact (L5 + large delta)
    """

    # guardian: allow-magic-config
    def __init__(self, max_surfaces_low: int=1, max_surfaces_medium: int=3, max_delta_low: float=0.05, max_delta_medium: float=0.1):
        """Initialize risk classifier.

        Parameters
        ----------
        max_surfaces_low : int
            Max surfaces for low impact (default 1).
        max_surfaces_medium : int
            Max surfaces for medium impact (default 3).
        max_delta_low : float
            Max delta for low impact (default 0.05).
        max_delta_medium : float
            Max delta for medium impact (default 0.10).
        """
        self.max_surfaces_low = max_surfaces_low
        self.max_surfaces_medium = max_surfaces_medium
        self.max_delta_low = max_delta_low
        self.max_delta_medium = max_delta_medium

    def classify(self, pkg: Any) -> int:
        """Classify risk tier of change package.

        Parameters
        ----------
        pkg : Any
            Change package to classify.

        Returns
        -------
        int
            Risk tier (0-4).
        """
        num_surfaces = getattr(pkg, 'num_surfaces', 1)
        max_delta = getattr(pkg, 'max_delta', 0.0)
        affects_l5 = getattr(pkg, 'affects_l5', False)
        if affects_l5 and max_delta > self.max_delta_medium:
            return 4
        if affects_l5 or num_surfaces > self.max_surfaces_medium or max_delta > self.max_delta_medium:
            return 3
        if num_surfaces > self.max_surfaces_low or max_delta > self.max_delta_low:
            return 2
        return 1
