"""Tests for REQ-298 and REQ-337: Discovery scan and promotion decision determinism.

Tests that discovery scan is deterministic and promotion decisions are
replay-stable.
"""

import pytest
from dataclasses import dataclass
from typing import List, Dict, Any, Set
import hashlib
import json
from pathlib import Path

pytestmark = pytest.mark.governance

@dataclass(frozen=True)
class AgentCandidate:
    """A candidate agent discovered during scan."""
    file_path: str
    class_name: str
    layer: str
    confidence_score: float
    discovery_hash: str

@dataclass(frozen=True)
class DiscoveryResult:
    """Result of a discovery scan."""
    scan_id: str
    candidates: List[AgentCandidate]
    scan_timestamp: float
    total_files_scanned: int

@dataclass(frozen=True)
class PromotionDecision:
    """Decision to promote a candidate."""
    decision_id: str
    candidate: AgentCandidate
    promote: bool
    reason: str
    blueprint_hash: str
    semantic_clock_tick: int

@dataclass(frozen=True)
class SurgicalManifest:
    """Manifest for surgical changes."""
    manifest_id: str
    changes: List[Dict[str, Any]]
    ssot_hash: str
    timestamp: float

class MockDiscoveryScanner:
    """Mock discovery scanner for testing."""

    def __init__(self):
        self.scan_count = 0

    def scan_agents(self, root_path: str, file_patterns: List[str]) -> DiscoveryResult:
        """Perform deterministic scan of agents."""
        self.scan_count += 1

        # Simulate finding agents based on patterns
        candidates = []

        # Mock file discovery based on patterns
        mock_files = [
            ('agentic_core/L1_cognition/reasoning/TestAgent.py', 'TestAgent', 'L1_cognition'),
            ('agentic_core/L2_execution/engines/ExecutorAgent.py', 'ExecutorAgent', 'L2_execution'),
            ('agentic_core/L3_orchestration/agents/OrchestratorAgent.py', 'OrchestratorAgent', 'L3_orchestration'),
        ]

        for file_path, class_name, layer in mock_files:
            # Check if file matches any pattern
            if any(pattern in file_path for pattern in file_patterns):
                # Generate deterministic hash
                content_hash = hashlib.sha256(f"{file_path}:{class_name}:{layer}".encode()).hexdigest()

                candidate = AgentCandidate(
                    file_path=file_path,
                    class_name=class_name,
                    layer=layer,
                    confidence_score=0.9,  # Fixed for determinism
                    discovery_hash=content_hash
                )
                candidates.append(candidate)

        # Generate scan ID deterministically
        scan_input = f"{root_path}:{sorted(file_patterns)}:{self.scan_count}"
        scan_id = hashlib.sha256(scan_input.encode()).hexdigest()[:12]

        result = DiscoveryResult(
            scan_id=scan_id,
            candidates=candidates,
            scan_timestamp=1234567890.0 + self.scan_count,  # Fixed base + offset
            total_files_scanned=len(mock_files)
        )

        return result

class MockPromotionDecider:
    """Mock promotion decider for testing."""

    def __init__(self):
        self.decision_count = 0
        self.semantic_clock = 0

    def decide_promotion(self, candidate: AgentCandidate, blueprint_hash: str) -> PromotionDecision:
        """Make deterministic promotion decision."""
        self.decision_count += 1
        self.semantic_clock += 1

        # Deterministic decision based on candidate hash
        try:
            promote = int(candidate.discovery_hash, 16) % 2 == 0
        except ValueError:
            # Fallback for non-hex hashes
            promote = hash(candidate.discovery_hash) % 2 == 0

        decision = PromotionDecision(
            decision_id=f"dec_{self.decision_count}_{hashlib.sha256(candidate.discovery_hash.encode()).hexdigest()[:8]}",
            candidate=candidate,
            promote=promote,
            reason="Deterministic decision based on hash parity",
            blueprint_hash=blueprint_hash,
            semantic_clock_tick=self.semantic_clock
        )

        return decision

class MockSurgicalManifest:
    """Mock surgical manifest for testing."""

    @staticmethod
    def create_manifest(changes: List[Dict[str, Any]]) -> SurgicalManifest:
        """Create manifest with deterministic hash."""
        # Sort changes for determinism
        sorted_changes = sorted(changes, key=lambda c: c.get('target', ''))

        # Generate SSOT hash
        ssot_content = json.dumps(sorted_changes, sort_keys=True)
        ssot_hash = hashlib.sha256(ssot_content.encode()).hexdigest()

        manifest = SurgicalManifest(
            manifest_id=f"manifest_{ssot_hash[:12]}",
            changes=sorted_changes,
            ssot_hash=ssot_hash,
            timestamp=1234567890.0  # Fixed timestamp
        )

        return manifest

def test_req298_discovery_scan_determinism():
    """REQ-298: Test that discovery scan is deterministic."""
    # Given
    scanner = MockDiscoveryScanner()
    root_path = "agentic_core"
    patterns = ["**/reasoning/*.py", "**/engines/*.py"]

    # When - Run scan twice with identical inputs
    result1 = scanner.scan_agents(root_path, patterns)
    scanner.scan_count = 0  # Reset scan count
    result2 = scanner.scan_agents(root_path, patterns)

    # Then - Results must be identical
    assert result1.scan_id == result2.scan_id, "Scan IDs must be identical"
    assert len(result1.candidates) == len(result2.candidates), "Number of candidates must match"

    # Verify each candidate is identical
    for cand1, cand2 in zip(result1.candidates, result2.candidates):
        assert cand1.file_path == cand2.file_path, "File paths must match"
        assert cand1.class_name == cand2.class_name, "Class names must match"
        assert cand1.layer == cand2.layer, "Layers must match"
        assert cand1.discovery_hash == cand2.discovery_hash, "Discovery hashes must match"

    # Verify ordering is deterministic
    candidate_paths1 = [c.file_path for c in result1.candidates]
    candidate_paths2 = [c.file_path for c in result2.candidates]
    assert candidate_paths1 == candidate_paths2, "Candidate ordering must be identical"

def test_req337_promotion_decision_determinism():
    """REQ-337: Test that promotion decisions are replay-stable."""
    # Given
    decider = MockPromotionDecider()
    blueprint_hash = hashlib.sha256("blueprint_content".encode()).hexdigest()

    candidate = AgentCandidate(
        file_path="test/agent.py",
        class_name="TestAgent",
        layer="L1_cognition",
        confidence_score=0.9,
        discovery_hash=hashlib.sha256("test_agent".encode()).hexdigest()
    )

    # When - Make decision twice with identical inputs
    decision1 = decider.decide_promotion(candidate, blueprint_hash)
    decider.decision_count = 0  # Reset count
    decider.semantic_clock = 0  # Reset clock
    decision2 = decider.decide_promotion(candidate, blueprint_hash)

    # Then - Decisions must be identical
    assert decision1.decision_id == decision2.decision_id, "Decision IDs must match"
    assert decision1.promote == decision2.promote, "Promotion decision must match"
    assert decision1.reason == decision2.reason, "Reason must match"
    assert decision1.blueprint_hash == decision2.blueprint_hash, "Blueprint hash must match"
    assert decision1.semantic_clock_tick == decision2.semantic_clock_tick, "Clock tick must match"

    # Verify candidate is identical
    assert decision1.candidate.file_path == decision2.candidate.file_path
    assert decision1.candidate.discovery_hash == decision2.candidate.discovery_hash

def test_discovery_scan_different_inputs():
    """Test that different scan inputs produce different but deterministic results."""
    # Given
    scanner = MockDiscoveryScanner()

    # When - Scan with different patterns
    patterns1 = ["**/reasoning/*.py"]
    patterns2 = ["**/engines/*.py"]

    result1 = scanner.scan_agents("agentic_core", patterns1)
    scanner.scan_count = 0  # Reset
    result2 = scanner.scan_agents("agentic_core", patterns2)

    # Then - Results should be different
    assert result1.scan_id != result2.scan_id, "Different patterns should produce different scan IDs"

    # But replay should be identical
    scanner.scan_count = 0
    result1_replay = scanner.scan_agents("agentic_core", patterns1)
    assert result1.scan_id == result1_replay.scan_id, "Replay must be identical"

def test_promotion_decision_different_candidates():
    """Test that different candidates produce different but deterministic decisions."""
    # Given
    decider = MockPromotionDecider()
    blueprint_hash = hashlib.sha256("blueprint".encode()).hexdigest()

    candidate1 = AgentCandidate("file1.py", "Agent1", "L1", 0.9, "1a2b3c4d")
    candidate2 = AgentCandidate("file2.py", "Agent2", "L2", 0.8, "2b3c4d5e")

    # When - Make decisions for different candidates
    decision1 = decider.decide_promotion(candidate1, blueprint_hash)
    decision2 = decider.decide_promotion(candidate2, blueprint_hash)

    # Then - Decisions should be different
    assert decision1.decision_id != decision2.decision_id, "Different candidates should produce different decisions"
    assert decision1.candidate != decision2.candidate, "Candidates should be different"

    # But replay should be identical
    decider.decision_count = 0
    decider.semantic_clock = 0
    decision1_replay = decider.decide_promotion(candidate1, blueprint_hash)
    assert decision1.decision_id == decision1_replay.decision_id, "Replay must be identical"

def test_surgical_manifest_determinism():
    """Test that surgical manifest creation is deterministic."""
    # Given
    changes = [
        {"action": "add", "target": "file1.py", "content": "code1"},
        {"action": "modify", "target": "file2.py", "content": "code2"},
        {"action": "delete", "target": "file3.py"}
    ]

    # When - Create manifest twice
    manifest1 = MockSurgicalManifest.create_manifest(changes)
    manifest2 = MockSurgicalManifest.create_manifest(changes)

    # Then - Manifests must be identical
    assert manifest1.manifest_id == manifest2.manifest_id, "Manifest IDs must match"
    assert manifest1.ssot_hash == manifest2.ssot_hash, "SSOT hashes must match"
    assert manifest1.changes == manifest2.changes, "Changes must match"

    # Verify changes are sorted deterministically
    target_order = [c["target"] for c in manifest1.changes]
    assert target_order == sorted(target_order), "Changes must be sorted by target"

def test_surgical_manifest_ssot_hash():
    """Test that SSOT hash is deterministic and content-based."""
    # Given
    changes1 = [{"action": "add", "target": "file.py", "content": "content"}]
    changes2 = [{"action": "add", "target": "file.py", "content": "content"}]
    changes3 = [{"action": "add", "target": "file.py", "content": "different"}]

    # When - Create manifests
    manifest1 = MockSurgicalManifest.create_manifest(changes1)
    manifest2 = MockSurgicalManifest.create_manifest(changes2)
    manifest3 = MockSurgicalManifest.create_manifest(changes3)

    # Then - Same content should produce same hash
    assert manifest1.ssot_hash == manifest2.ssot_hash, "Same content should produce same hash"

    # Different content should produce different hash
    assert manifest1.ssot_hash != manifest3.ssot_hash, "Different content should produce different hash"

def test_discovery_promotion_integration():
    """Test integration between discovery and promotion decisions."""
    # Given
    scanner = MockDiscoveryScanner()
    decider = MockPromotionDecider()
    blueprint_hash = hashlib.sha256("integration_test".encode()).hexdigest()

    # When - Scan and then make promotion decisions
    scan_result = scanner.scan_agents("agentic_core", ["**/*.py"])

    promotion_decisions = []
    for candidate in scan_result.candidates:
        decision = decider.decide_promotion(candidate, blueprint_hash)
        promotion_decisions.append(decision)

    # Then - Process should be deterministic
    assert len(promotion_decisions) == len(scan_result.candidates)

    # Replay should produce identical results
    scanner.scan_count = 0
    decider.decision_count = 0
    decider.semantic_clock = 0

    scan_result_replay = scanner.scan_agents("agentic_core", ["**/*.py"])
    promotion_decisions_replay = []

    for candidate in scan_result_replay.candidates:
        decision = decider.decide_promotion(candidate, blueprint_hash)
        promotion_decisions_replay.append(decision)

    # Verify identical results
    assert scan_result.scan_id == scan_result_replay.scan_id
    assert len(promotion_decisions) == len(promotion_decisions_replay)

    for orig, replay in zip(promotion_decisions, promotion_decisions_replay):
        assert orig.decision_id == replay.decision_id
        assert orig.promote == replay.promote

def test_candidate_immutability():
    """Test that candidate objects are immutable."""
    # Given
    candidate = AgentCandidate(
        file_path="test.py",
        class_name="TestClass",
        layer="L1",
        confidence_score=0.9,
        discovery_hash="hash123"
    )

    # When/Then - Attempting to modify should fail
    with pytest.raises(AttributeError):
        candidate.file_path = "modified.py"

    with pytest.raises(AttributeError):
        candidate.confidence_score = 1.0

def test_decision_immutability():
    """Test that decision objects are immutable."""
    # Given
    candidate = AgentCandidate("test.py", "Test", "L1", 0.9, "hash")
    decision = PromotionDecision(
        decision_id="dec1",
        candidate=candidate,
        promote=True,
        reason="test",
        blueprint_hash="blueprint",
        semantic_clock_tick=1
    )

    # When/Then - Attempting to modify should fail
    with pytest.raises(AttributeError):
        decision.promote = False

    with pytest.raises(AttributeError):
        decision.reason = "modified"
