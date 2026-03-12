"""Unit tests for system_learning.pipelines.approval_gates."""

import pytest

from system_learning.pipelines.approval_gates import (
    ApprovalDecision,
    DefaultRiskClassifier,
    DefaultRuleBasedGate,
)

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300


pytestmark = pytest.mark.unit_min_deps

THRESHOLD = 0.95

# =============================================================================
# Mock Change Package
# =============================================================================


class MockChangePackage:
    """Mock change package for testing."""

    def __init__(self, num_surfaces: int = 1, max_delta: float = 0.0, affects_l5: bool = False):
        self.num_surfaces = num_surfaces
        self.max_delta = max_delta
        self.affects_l5 = affects_l5


# =============================================================================
# Tests
# =============================================================================


class TestDefaultRiskClassifier:
    def test_low_impact_single_surface_small_delta(self):
        """Single surface with small delta is low impact (tier 1)."""
        classifier = DefaultRiskClassifier()
        pkg = MockChangePackage(num_surfaces=1, max_delta=0.03, affects_l5=False)

        risk_tier = classifier.classify(pkg)

        assert risk_tier == 1

    def test_medium_impact_multiple_surfaces(self):
        """Multiple surfaces is medium impact (tier 2)."""
        classifier = DefaultRiskClassifier()
        pkg = MockChangePackage(num_surfaces=2, max_delta=0.03, affects_l5=False)

        risk_tier = classifier.classify(pkg)

        assert risk_tier == 2

    def test_medium_impact_moderate_delta(self):
        """Moderate delta is medium impact (tier 2)."""
        classifier = DefaultRiskClassifier()
        pkg = MockChangePackage(num_surfaces=1, max_delta=0.08, affects_l5=False)

        risk_tier = classifier.classify(pkg)

        assert risk_tier == 2

    def test_high_impact_affects_l5(self):
        """Affecting L5 is high impact (tier 3)."""
        classifier = DefaultRiskClassifier()
        pkg = MockChangePackage(num_surfaces=1, max_delta=0.03, affects_l5=True)

        risk_tier = classifier.classify(pkg)

        assert risk_tier == 3

    def test_high_impact_many_surfaces(self):
        """Many surfaces is high impact (tier 3)."""
        classifier = DefaultRiskClassifier()
        pkg = MockChangePackage(num_surfaces=5, max_delta=0.03, affects_l5=False)

        risk_tier = classifier.classify(pkg)

        assert risk_tier == 3

    def test_critical_impact_l5_large_delta(self):
        """L5 + large delta is critical impact (tier 4)."""
        classifier = DefaultRiskClassifier()
        pkg = MockChangePackage(num_surfaces=1, max_delta=0.15, affects_l5=True)

        risk_tier = classifier.classify(pkg)

        assert risk_tier == 4


class TestDefaultRuleBasedGate:
    def test_high_impact_rejects_by_default(self):
        """High impact changes are REJECTED by default."""
        classifier = DefaultRiskClassifier()
        gate = DefaultRuleBasedGate(classifier, allow_high_impact=False)

        # High impact package
        pkg = MockChangePackage(num_surfaces=5, max_delta=0.03, affects_l5=False)

        decision = gate.decide(pkg, None, None)

        assert decision == ApprovalDecision.REJECT

    def test_low_impact_approves(self):
        """Low impact changes are APPROVED."""
        classifier = DefaultRiskClassifier()
        gate = DefaultRuleBasedGate(classifier, allow_high_impact=False)

        # Low impact package
        pkg = MockChangePackage(num_surfaces=1, max_delta=0.03, affects_l5=False)

        decision = gate.decide(pkg, None, None)

        assert decision == ApprovalDecision.APPROVE

    def test_high_impact_approves_when_allowed(self):
        """High impact changes are APPROVED when allow_high_impact=True."""
        classifier = DefaultRiskClassifier()
        gate = DefaultRuleBasedGate(classifier, allow_high_impact=True)

        # High impact package
        pkg = MockChangePackage(num_surfaces=5, max_delta=0.03, affects_l5=False)

        decision = gate.decide(pkg, None, None)

        assert decision == ApprovalDecision.APPROVE

    def test_medium_impact_approves(self):
        """Medium impact changes are APPROVED (below threshold)."""
        classifier = DefaultRiskClassifier()
        gate = DefaultRuleBasedGate(classifier, high_impact_threshold=THRESHOLD, allow_high_impact=False)

        # Medium impact package (tier 2)
        pkg = MockChangePackage(num_surfaces=2, max_delta=0.03, affects_l5=False)

        decision = gate.decide(pkg, None, None)

        assert decision == ApprovalDecision.APPROVE


class TestDeterminism:
    def test_classifier_deterministic(self):
        """Risk classifier produces identical results."""
        classifier = DefaultRiskClassifier()
        pkg = MockChangePackage(num_surfaces=2, max_delta=0.08, affects_l5=False)

        tier1 = classifier.classify(pkg)
        tier2 = classifier.classify(pkg)
        tier3 = classifier.classify(pkg)

        assert tier1 == tier2 == tier3

    def test_gate_deterministic(self):
        """Approval gate produces identical results."""
        classifier = DefaultRiskClassifier()
        gate = DefaultRuleBasedGate(classifier, allow_high_impact=False)
        pkg = MockChangePackage(num_surfaces=1, max_delta=0.03, affects_l5=False)

        decision1 = gate.decide(pkg, None, None)
        decision2 = gate.decide(pkg, None, None)
        decision3 = gate.decide(pkg, None, None)

        assert decision1 == decision2 == decision3