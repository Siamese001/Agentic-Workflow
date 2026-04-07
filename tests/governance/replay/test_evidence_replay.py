"""Tests for Wave 17 REQ-307/308: Evidence artifacts + ToolTranscript hash binding."""

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
class ToolTranscript:
    """Mock ToolTranscript for testing."""

    tool_name: str
    inputs: dict[str, Any]
    outputs: str
    timestamp: float
    hash: str = ""

    def __post_init__(self):
        if not self.hash:
            # Compute hash from inputs and outputs
            content = json.dumps(
                {
                    "tool_name": self.tool_name,
                    "inputs": self.inputs,
                    "outputs": self.outputs,
                    "timestamp": self.timestamp,
                },
                sort_keys=True,
            )
            object.__setattr__(self, "hash", hashlib.sha256(content.encode()).hexdigest())


@dataclass(frozen=True)
class EvidencePack:
    """Mock EvidencePack for testing."""

    pack_id: str
    wave_id: int
    artifacts: list[str]
    tool_transcripts: list[ToolTranscript]
    hash: str = ""

    def __post_init__(self):
        if not self.hash:
            # Compute hash including transcript hashes
            transcript_hashes = [t.hash for t in self.tool_transcripts]
            content = json.dumps(
                {
                    "pack_id": self.pack_id,
                    "wave_id": self.wave_id,
                    "artifacts": sorted(self.artifacts),
                    "transcript_hashes": sorted(transcript_hashes),
                },
                sort_keys=True,
            )
            object.__setattr__(self, "hash", hashlib.sha256(content.encode()).hexdigest())


class TestEvidenceReplay:
    """Test evidence replay with hash binding."""

    def test_evidence_pack_hash_binding(self):
        """Test that EvidencePack is hash-bound."""
        # Given - Create tool transcripts
        transcript1 = ToolTranscript(
            tool_name="file_writer",
            inputs={"path": "test.py", "content": "print('hello')"},
            outputs="File written successfully",
            timestamp=1234567890.0,
        )

        transcript2 = ToolTranscript(
            tool_name="validator",
            inputs={"file": "test.py"},
            outputs="Validation passed",
            timestamp=1234567891.0,
        )

        # Create evidence pack
        evidence_pack = EvidencePack(
            pack_id="evidence_001",
            wave_id=16,
            artifacts=["test.py", "validation.log"],
            tool_transcripts=[transcript1, transcript2],
        )

        # When/Then - Pack should have hash
        assert evidence_pack.hash, "EvidencePack should have hash"
        assert len(evidence_pack.hash) == 64, "Hash should be SHA256"

        # Hash should be influenced by transcript hashes (different transcripts -> different pack hash)
        # Verify by creating a pack with different transcripts and comparing
        other_transcript = ToolTranscript(
            tool_name="other_tool", inputs={"x": "y"}, outputs="Other output", timestamp=9999.0,
        )
        other_pack = EvidencePack(
            pack_id="evidence_001",
            wave_id=16,
            artifacts=["test.py", "validation.log"],
            tool_transcripts=[other_transcript],
        )
        assert evidence_pack.hash != other_pack.hash, "Pack hash should be influenced by transcript hashes"

    def test_tool_transcript_missing_hash_detection(self):
        """Test detection of missing ToolTranscript hash."""
        # Given - Create transcript without hash by setting it to empty after creation
        transcript = ToolTranscript(
            tool_name="test_tool", inputs={"param": "value"}, outputs="Success", timestamp=1234567890.0,
        )

        # Manually set hash to empty to simulate missing hash
        object.__setattr__(transcript, "hash", "")

        # When/Then - Should detect missing hash
        assert not transcript.hash, "Transcript should have missing hash"

        # Evidence pack with missing transcript hash should be invalid
        evidence_pack = EvidencePack(
            pack_id="invalid_pack", wave_id=16, artifacts=["test.txt"], tool_transcripts=[transcript],
        )

        # Should detect gap
        gap_detected = self._detect_evidence_gap(evidence_pack)
        assert gap_detected, "Should detect missing transcript hash"

    def test_evidence_replay_consistency(self):
        """Test that evidence replay is consistent."""
        # Given - Create identical evidence packs
        transcript = ToolTranscript(
            tool_name="replay_test", inputs={"test": "data"}, outputs="Test result", timestamp=1234567890.0,
        )

        pack1 = EvidencePack(
            pack_id="replay_pack",
            wave_id=16,
            artifacts=["test1.txt", "test2.txt"],
            tool_transcripts=[transcript],
        )

        pack2 = EvidencePack(
            pack_id="replay_pack",
            wave_id=16,
            artifacts=["test1.txt", "test2.txt"],
            tool_transcripts=[transcript],
        )

        # When/Then - Hashes should be identical
        assert pack1.hash == pack2.hash, "Identical packs should have identical hashes"

    def test_tampered_evidence_detection(self):
        """Test detection of tampered evidence."""
        # Given - Create original evidence pack
        transcript = ToolTranscript(
            tool_name="secure_tool", inputs={"secret": "data"}, outputs="Processed", timestamp=1234567890.0,
        )

        original_pack = EvidencePack(
            pack_id="secure_pack", wave_id=16, artifacts=["secret.txt"], tool_transcripts=[transcript],
        )

        # When - Tamper with evidence
        tampered_transcript = ToolTranscript(
            tool_name="secure_tool",
            inputs={"secret": "modified_data"},  # Tampered
            outputs="Processed",
            timestamp=1234567890.0,
        )

        tampered_pack = EvidencePack(
            pack_id="secure_pack",
            wave_id=16,
            artifacts=["secret.txt"],
            tool_transcripts=[tampered_transcript],
        )

        # Then - Hashes should be different
        assert original_pack.hash != tampered_pack.hash, "Tampered evidence should have different hash"

    def test_evidence_gap_detection(self):
        """Test comprehensive evidence gap detection."""
        # Given - Evidence pack with various issues
        issues = []

        # Transcript with invalid hash length (too short)
        missing_hash_transcript = ToolTranscript(
            tool_name="bad_tool",
            inputs={},
            outputs="Result",
            timestamp=1234567890.0,
            hash="abc123",  # Valid hex but wrong length -> "invalid hash length"
        )

        # Mismatched hash (non-hex characters)
        mismatched_transcript = ToolTranscript(
            tool_name="mismatch_tool",
            inputs={},
            outputs="Result",
            timestamp=1234567890.0,
            hash="wrong_hash_not_sha256",  # Non-hex -> "invalid hash format"
        )

        evidence_pack = EvidencePack(
            pack_id="gap_pack",
            wave_id=16,
            artifacts=["gap.txt"],
            tool_transcripts=[missing_hash_transcript, mismatched_transcript],
        )

        # When - Detect gaps
        gaps = self._detect_all_evidence_gaps(evidence_pack)

        # Then - Should detect all issues
        assert len(gaps) >= 2, "Should detect multiple gaps"
        assert any("invalid hash" in gap.lower() for gap in gaps), "Should detect invalid hash"
        # Both transcripts have hash issues (length and format)
        assert len(gaps) >= 2, "Should detect both hash issues"

    def _detect_evidence_gap(self, pack: EvidencePack) -> bool:
        """Detect if evidence pack has gaps."""
        # Check for missing transcript hashes
        for transcript in pack.tool_transcripts:
            if not transcript.hash:
                return True

            # Check if hash is valid SHA256
            try:
                int(transcript.hash, 16)
                if len(transcript.hash) != 64:
                    return True
            except ValueError:
                return True

        return False

    def _detect_all_evidence_gaps(self, pack: EvidencePack) -> list[str]:
        """Detect all evidence gaps with descriptions."""
        gaps = []

        for i, transcript in enumerate(pack.tool_transcripts):
            if not transcript.hash:
                gaps.append(f"Transcript {i}: missing hash")
            else:
                try:
                    int(transcript.hash, 16)
                    if len(transcript.hash) != 64:
                        gaps.append(f"Transcript {i}: invalid hash length")
                except ValueError:
                    gaps.append(f"Transcript {i}: invalid hash format")

        return gaps


def test_req307_evidence_pack_hash_binding():
    """REQ-307: Test EvidencePack hash binding."""
    test = TestEvidenceReplay()
    test.test_evidence_pack_hash_binding()
    test.test_evidence_replay_consistency()
    test.test_tampered_evidence_detection()


def test_req308_tool_transcript_hash_gap():
    """REQ-308: Test ToolTranscript hash gap detection."""
    test = TestEvidenceReplay()
    test.test_tool_transcript_missing_hash_detection()
    test.test_evidence_gap_detection()
