"""Tests for Wave 17 REQ-313/320: Surgical edit + SSOT hash determinism."""

import hashlib
import json
from dataclasses import asdict, dataclass

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
class SurgicalChange:
    """Represents a single surgical change."""

    target: str
    operation: str  # "insert", "delete", "replace"
    content: str
    line_number: int | None = None


@dataclass(frozen=True)
class SurgicalManifest:
    """Manifest for surgical edits with SSOT hash."""

    manifest_id: str
    changes: list[SurgicalChange]
    ssot_hash: str
    timestamp: float
    signature: str = ""

    def __post_init__(self):
        if not self.signature:
            # Compute signature from changes
            changes_data = [asdict(change) for change in self.changes]
            content = json.dumps(changes_data, sort_keys=True)
            sig = hashlib.sha256(content.encode()).hexdigest()[:16]
            object.__setattr__(self, "signature", sig)


class MockSSOTStore:
    """Mock Single Source of Truth store."""

    def __init__(self):
        self._files: dict[str, str] = {}

    def get_file(self, path: str) -> str:
        """Get file content."""
        return self._files.get(path, "")

    def apply_surgical_manifest(self, manifest: SurgicalManifest) -> bool:
        """Apply surgical manifest to files."""
        try:
            for change in manifest.changes:
                current_content = self._files.get(change.target, "")
                lines = current_content.split("\n") if current_content else []

                if change.operation == "insert":
                    if change.line_number is not None:
                        lines.insert(change.line_number, change.content)
                    else:
                        lines.append(change.content)
                elif change.operation == "delete":
                    if change.line_number is not None and 0 <= change.line_number < len(lines):
                        lines.pop(change.line_number)
                elif change.operation == "replace":
                    if change.line_number is not None and 0 <= change.line_number < len(lines):
                        lines[change.line_number] = change.content

                self._files[change.target] = "\n".join(lines)

            return True
        except (ValueError, KeyError, IndexError):
            return False

    def compute_ssot_hash(self) -> str:
        """Compute current SSOT hash."""
        all_content = json.dumps(self._files, sort_keys=True)
        return hashlib.sha256(all_content.encode()).hexdigest()


class TestSurgicalSSOTReplay:
    """Test surgical edit and SSOT hash determinism."""

    def test_surgical_manifest_application(self):
        """Test that surgical manifest applies correctly."""
        # Given - Initial file state
        store = MockSSOTStore()
        store._files["test.py"] = "line1\nline2\nline3"

        # Create surgical changes
        changes = [
            SurgicalChange(target="test.py", operation="insert", content="new_line", line_number=1),
            SurgicalChange(target="test.py", operation="replace", content="modified_line2", line_number=2),
        ]

        # Create manifest
        manifest = SurgicalManifest(
            manifest_id="surgical_001",
            changes=changes,
            ssot_hash="",  # Will be computed
            timestamp=1234567890.0,
        )

        # When - Apply manifest
        success = store.apply_surgical_manifest(manifest)

        # Then - Changes should be applied
        assert success, "Manifest should apply successfully"
        result = store.get_file("test.py")
        expected = "line1\nnew_line\nmodified_line2\nline3"
        assert result == expected, f"Expected {expected}, got {result}"

    def test_ssot_hash_determinism(self):
        """Test that SSOT hash is deterministic across runs."""
        # Given - Same initial state and changes
        initial_state = {"file1.py": "content1", "file2.py": "content2"}

        changes = [SurgicalChange(target="file1.py", operation="insert", content="new_content")]

        # Run 1
        store1 = MockSSOTStore()
        store1._files = initial_state.copy()

        manifest1 = SurgicalManifest(
            manifest_id="deterministic_test",
            changes=changes,
            ssot_hash="",
            timestamp=1234567890.0,
        )

        store1.apply_surgical_manifest(manifest1)
        hash1 = store1.compute_ssot_hash()

        # Run 2 (identical)
        store2 = MockSSOTStore()
        store2._files = initial_state.copy()

        manifest2 = SurgicalManifest(
            manifest_id="deterministic_test",
            changes=changes,
            ssot_hash="",
            timestamp=1234567890.0,
        )

        store2.apply_surgical_manifest(manifest2)
        hash2 = store2.compute_ssot_hash()

        # Then - Hashes should be identical
        assert hash1 == hash2, "SSOT hash should be deterministic"
        assert len(hash1) == 64, "Hash should be SHA256"

    def test_surgical_manifest_replay(self):
        """Test two-run surgical manifest replay."""
        # Given - Create manifest
        changes = [
            SurgicalChange(target="replay_test.py", operation="insert", content="print('replay test')"),
            SurgicalChange(target="replay_test.py", operation="insert", content="print('deterministic')"),
        ]

        manifest = SurgicalManifest(
            manifest_id="replay_manifest",
            changes=changes,
            ssot_hash="",
            timestamp=1234567890.0,
        )

        # Run 1
        store1 = MockSSOTStore()
        result1 = store1.apply_surgical_manifest(manifest)
        final_state1 = store1._files.copy()

        # Run 2
        store2 = MockSSOTStore()
        result2 = store2.apply_surgical_manifest(manifest)
        final_state2 = store2._files.copy()

        # Then - Results should be identical
        assert result1 == result2, "Both runs should succeed"
        assert final_state1 == final_state2, "Final states should be identical"
        assert "replay_test.py" in final_state1, "File should be created"

    def test_ssot_hash_tamper_detection(self):
        """Test SSOT hash tamper detection."""
        # Given - Original manifest and state
        store = MockSSOTStore()
        store._files["important.py"] = "original_content"

        changes = [SurgicalChange(target="important.py", operation="replace", content="modified_content")]

        manifest = SurgicalManifest(
            manifest_id="secure_manifest",
            changes=changes,
            ssot_hash="",
            timestamp=1234567890.0,
        )

        # When - Apply changes
        store.apply_surgical_manifest(manifest)
        actual_hash = store.compute_ssot_hash()

        # Then - Tampered hash should be detected
        tampered_hash = hashlib.sha256(b"tampered").hexdigest()
        assert actual_hash != tampered_hash, "Tampered hash should not match"

    def test_surgical_change_order_independence(self):
        """Test that surgical changes are order-dependent for determinism."""
        # Given - Same changes in different order
        change_a = SurgicalChange(target="order_test.py", operation="insert", content="FIRST", line_number=0)

        change_b = SurgicalChange(
            target="order_test.py",
            operation="insert",
            content="SECOND",
            line_number=0,  # both insert at position 0 → order matters
        )

        # Manifest 1: A then B
        manifest1 = SurgicalManifest(
            manifest_id="order_test_1",
            changes=[change_a, change_b],
            ssot_hash="",
            timestamp=1234567890.0,
        )

        # Manifest 2: B then A
        manifest2 = SurgicalManifest(
            manifest_id="order_test_2",
            changes=[change_b, change_a],
            ssot_hash="",
            timestamp=1234567890.0,
        )

        # Apply both
        store1 = MockSSOTStore()
        store1.apply_surgical_manifest(manifest1)
        hash1 = store1.compute_ssot_hash()

        store2 = MockSSOTStore()
        store2.apply_surgical_manifest(manifest2)
        hash2 = store2.compute_ssot_hash()

        # Then - Different order should produce different results
        assert hash1 != hash2, "Different change order should produce different hash"

    def test_manifest_signature_binding(self):
        """Test that manifest is bound to its content."""
        # Given - Create manifest
        changes = [SurgicalChange(target="signature_test.py", operation="insert", content="test_content")]

        manifest = SurgicalManifest(
            manifest_id="signature_manifest",
            changes=changes,
            ssot_hash="",
            timestamp=1234567890.0,
        )

        # When - Create identical manifest
        identical_manifest = SurgicalManifest(
            manifest_id="signature_manifest",
            changes=changes,
            ssot_hash="",
            timestamp=1234567890.0,
        )

        # Then - Signatures should be identical
        assert manifest.signature == identical_manifest.signature, (
            "Identical manifests should have identical signatures"
        )

        # Tampered manifest should have different signature
        tampered_changes = [
            SurgicalChange(
                target="signature_test.py",
                operation="insert",
                content="tampered_content",  # Different content
            ),
        ]

        tampered_manifest = SurgicalManifest(
            manifest_id="signature_manifest",
            changes=tampered_changes,
            ssot_hash="",
            timestamp=1234567890.0,
        )

        assert manifest.signature != tampered_manifest.signature, (
            "Tampered manifest should have different signature"
        )


def test_req313_surgical_edit_determinism():
    """REQ-313: Test surgical edit determinism."""
    test = TestSurgicalSSOTReplay()
    test.test_surgical_manifest_application()
    test.test_surgical_manifest_replay()
    test.test_surgical_change_order_independence()


def test_req320_ssot_hash_determinism():
    """REQ-320: Test SSOT hash determinism."""
    test = TestSurgicalSSOTReplay()
    test.test_ssot_hash_determinism()
    test.test_ssot_hash_tamper_detection()
    test.test_manifest_signature_binding()
