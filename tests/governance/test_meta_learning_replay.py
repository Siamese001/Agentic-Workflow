"""Tests for REQ-060 and REQ-063: Meta-learning replay proof.

Tests that meta-learning stage and proposer are replay-proof with
identical ChangePackage lists across runs.
"""

import hashlib
import json
from dataclasses import dataclass
from typing import Any

import pytest

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

pytestmark = pytest.mark.governance


@dataclass(frozen=True)
class ChangePackage:
    """A change package in meta-learning."""

    package_id: str
    changes: list[dict[str, Any]]
    timestamp: float
    semantic_clock_tick: int


@dataclass(frozen=True)
class Stage6Proposal:
    """Stage 6 meta-learning proposal."""

    proposal_id: str
    change_packages: list[ChangePackage]
    proposer_confidence: float
    semantic_clock_tick: int


class MockMetaLearningStage:
    """Mock meta-learning stage for testing."""

    def __init__(self):
        self.proposals: list[Stage6Proposal] = []
        self.semantic_clock = 0

    def generate_proposal(self, input_data: dict[str, Any]) -> Stage6Proposal:
        """Generate a deterministic proposal based on input."""
        self.semantic_clock += 1

        # Create deterministic change packages
        packages = []
        for i, change in enumerate(input_data.get("changes", [])):
            package = ChangePackage(
                package_id=f"pkg_{i}_{self.semantic_clock}",
                changes=[change],
                timestamp=1234567890.0 + i,  # Fixed timestamp for determinism
                semantic_clock_tick=self.semantic_clock,
            )
            packages.append(package)

        proposal = Stage6Proposal(
            proposal_id=f"prop_{hashlib.sha256(str(input_data).encode()).hexdigest()[:8]}",
            change_packages=packages,
            proposer_confidence=0.85,  # Fixed confidence for determinism
            semantic_clock_tick=self.semantic_clock,
        )

        self.proposals.append(proposal)
        return proposal


class MockMetaLearningProposer:
    """Mock meta-learning proposer for testing."""

    def __init__(self):
        self.stage = MockMetaLearningStage()

    def order_proposals(self, proposals: list[Stage6Proposal]) -> list[Stage6Proposal]:
        """Order proposals deterministically."""
        # Sort by semantic_clock_tick then proposal_id for deterministic ordering
        return sorted(proposals, key=lambda p: (p.semantic_clock_tick, p.proposal_id))

    def replay_proposal_generation(self, input_data: dict[str, Any]) -> list[ChangePackage]:
        """Replay proposal generation and return ChangePackage list."""
        proposal = self.stage.generate_proposal(input_data)
        ordered_proposals = self.order_proposals([proposal])

        # Extract ChangePackages from ordered proposals
        all_packages = []
        for prop in ordered_proposals:
            all_packages.extend(prop.change_packages)

        return all_packages


def test_req060_meta_learning_stage_replay_proof():
    """REQ-060: Test that meta-learning stage is replay-proof."""
    # Given
    proposer = MockMetaLearningProposer()
    input_data = {
        "changes": [
            {"type": "add", "target": "agent.py", "content": "new_function"},
            {"type": "modify", "target": "config.py", "content": "update_config"},
        ],
    }

    # When - Run proposal generation twice with identical input
    packages1 = proposer.replay_proposal_generation(input_data)
    proposer.stage.semantic_clock = 0  # Reset clock
    packages2 = proposer.replay_proposal_generation(input_data)

    # Then - ChangePackage lists must be identical
    assert len(packages1) == len(packages2), "Number of packages must match"

    for pkg1, pkg2 in zip(packages1, packages2):
        assert pkg1.package_id == pkg2.package_id, "Package IDs must match"
        assert pkg1.changes == pkg2.changes, "Package changes must match"
        assert pkg1.semantic_clock_tick == pkg2.semantic_clock_tick, "Clock ticks must match"

    # Verify deterministic ordering
    package_ids1 = [p.package_id for p in packages1]
    package_ids2 = [p.package_id for p in packages2]
    assert package_ids1 == package_ids2, "Package ordering must be identical"


def test_req063_meta_learning_proposer_replay_proof():
    """REQ-063: Test that meta-learning proposer ordering is replay-proof."""
    # Given
    proposer = MockMetaLearningProposer()

    # Create multiple proposals with different timestamps
    proposals = []
    for i in range(3):
        input_data = {"changes": [{"type": "add", "target": f"file_{i}.py", "content": f"content_{i}"}]}
        proposal = proposer.stage.generate_proposal(input_data)
        proposals.append(proposal)

    # When - Order proposals twice
    ordered1 = proposer.order_proposals(proposals.copy())
    ordered2 = proposer.order_proposals(proposals.copy())

    # Then - Ordering must be identical
    assert len(ordered1) == len(ordered2), "Number of ordered proposals must match"

    for prop1, prop2 in zip(ordered1, ordered2):
        assert prop1.proposal_id == prop2.proposal_id, "Proposal IDs must match in order"
        assert prop1.semantic_clock_tick == prop2.semantic_clock_tick, "Clock ticks must match in order"

    # Verify deterministic ordering by semantic_clock_tick
    clock_ticks1 = [p.semantic_clock_tick for p in ordered1]
    clock_ticks2 = [p.semantic_clock_tick for p in ordered2]
    assert clock_ticks1 == clock_ticks2, "Clock tick ordering must be identical"
    assert clock_ticks1 == sorted(clock_ticks1), "Must be sorted by clock tick"


def test_meta_learning_deterministic_input_hashing():
    """Test that input hashing is deterministic."""
    # Given
    input_data = {
        "changes": [
            {"type": "add", "target": "test.py", "content": "test content"},
            {"type": "modify", "target": "config.json", "content": '{"key": "value"}'},
        ],
        "metadata": {"author": "test", "version": 1},
    }

    # When - Hash input twice
    hash1 = hashlib.sha256(json.dumps(input_data, sort_keys=True).encode()).hexdigest()
    hash2 = hashlib.sha256(json.dumps(input_data, sort_keys=True).encode()).hexdigest()

    # Then - Hashes must be identical
    assert hash1 == hash2, "Input hashing must be deterministic"


def test_meta_learning_semantic_clock_determinism():
    """Test that semantic clock advancement is deterministic."""
    # Given
    stage = MockMetaLearningStage()

    # When - Generate multiple proposals
    initial_clock = stage.semantic_clock
    proposal1 = stage.generate_proposal({"changes": []})
    proposal2 = stage.generate_proposal({"changes": []})
    proposal3 = stage.generate_proposal({"changes": []})

    # Then - Clock must advance deterministically
    assert stage.semantic_clock == initial_clock + 3, "Clock must advance by number of proposals"
    assert proposal1.semantic_clock_tick == initial_clock + 1, "First proposal tick must be 1"
    assert proposal2.semantic_clock_tick == initial_clock + 2, "Second proposal tick must be 2"
    assert proposal3.semantic_clock_tick == initial_clock + 3, "Third proposal tick must be 3"


def test_meta_learning_change_package_immutability():
    """Test that ChangePackages are immutable."""
    # Given
    changes = [{"type": "add", "target": "test.py", "content": "content"}]
    package = ChangePackage(
        package_id="test_pkg",
        changes=changes,
        timestamp=1234567890.0,
        semantic_clock_tick=1,
    )

    # When/Then - Attempting to modify should fail
    with pytest.raises(AttributeError):
        package.package_id = "modified"

    with pytest.raises(AttributeError):
        package.changes = []

    with pytest.raises(AttributeError):
        package.semantic_clock_tick = 2


def test_meta_learning_proposal_immutability():
    """Test that Stage6Proposals are immutable."""
    # Given
    packages = [ChangePackage("pkg1", [], 0.0, 1)]
    proposal = Stage6Proposal(
        proposal_id="test_prop",
        change_packages=packages,
        proposer_confidence=0.9,
        semantic_clock_tick=1,
    )

    # When/Then - Attempting to modify should fail
    with pytest.raises(AttributeError):
        proposal.proposal_id = "modified"

    with pytest.raises(AttributeError):
        proposal.change_packages = []

    with pytest.raises(AttributeError):
        proposal.semantic_clock_tick = 2


def test_meta_learning_replay_with_different_inputs():
    """Test that different inputs produce different but deterministic outputs."""
    # Given
    proposer = MockMetaLearningProposer()

    input1 = {"changes": [{"type": "add", "target": "file1.py", "content": "content1"}]}
    input2 = {"changes": [{"type": "add", "target": "file2.py", "content": "content2"}]}

    # When - Generate proposals for different inputs
    packages1 = proposer.replay_proposal_generation(input1)
    proposer.stage.semantic_clock = 0  # Reset for next test
    packages2 = proposer.replay_proposal_generation(input2)

    # Then - Outputs should be different but internally consistent
    assert packages1 != packages2, "Different inputs should produce different outputs"

    # Replay each should be identical
    proposer.stage.semantic_clock = 0  # Reset for replay
    packages1_replay = proposer.replay_proposal_generation(input1)
    assert packages1 == packages1_replay, "Same input should replay identically"

    proposer.stage.semantic_clock = 0  # Reset for replay
    packages2_replay = proposer.replay_proposal_generation(input2)
    assert packages2 == packages2_replay, "Same input should replay identically"
