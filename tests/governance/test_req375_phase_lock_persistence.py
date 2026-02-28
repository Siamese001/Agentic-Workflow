"""Tests for REQ-375: Phase lock persistence.

Tests that phase lock state survives process restart and is properly
persisted in L4 storage.
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
import time

pytestmark = pytest.mark.governance

# Import the modules we're testing
import sys
sys.path.append(str(Path(__file__).parent.parent.parent / "agentic_core" / "L4_state" / "enforcement"))

try:
    from phase_lock_store import PhaseLockStore, PhaseLockRecord, PhaseLockValidator
except ImportError:
    pytest.skip("phase_lock_store module not available", allow_module_level=True)

class TestPhaseLockPersistence:
    """Test phase lock persistence functionality."""

    def setup_method(self):
        """Set up test environment."""
        # Create temporary directory for test storage
        self.temp_dir = Path(tempfile.mkdtemp())
        self.store = PhaseLockStore(self.temp_dir)
        self.validator = PhaseLockValidator(self.store)

    def teardown_method(self):
        """Clean up test environment."""
        # Remove temporary directory
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_req375_phase_lock_persistence(self):
        """REQ-375: Test that phase lock persists across store instances."""
        # Given - Create a phase lock
        phase = 5
        metadata = {"reason": "test", "author": "test_suite"}
        signature = "test_signature"

        lock1 = self.store.lock_phase(phase, metadata, signature)

        # When - Create new store instance (simulating process restart)
        store2 = PhaseLockStore(self.temp_dir)

        # Then - Lock should be persisted
        assert store2.is_locked(phase), "Phase lock should persist across instances"

        lock2 = store2.get_lock_record(phase)
        assert lock2 is not None, "Lock record should be available"
        assert lock2.phase == phase, "Phase should match"
        assert lock2.locked is True, "Lock should be active"
        assert lock2.metadata == metadata, "Metadata should persist"
        assert lock2.signature == signature, "Signature should persist"

    def test_phase_lock_unlock_persistence(self):
        """Test that unlock operation persists."""
        # Given - Lock a phase
        phase = 3
        self.store.lock_phase(phase, {"test": "data"}, "sig")

        # When - Unlock the phase
        unlock_success = self.store.unlock_phase(phase, "unlock_sig")
        assert unlock_success is True, "Unlock should succeed"

        # Then - Create new instance and verify unlock persisted
        store2 = PhaseLockStore(self.temp_dir)
        assert not store2.is_locked(phase), "Phase should remain unlocked"

        lock_record = store2.get_lock_record(phase)
        assert lock_record is not None, "Lock record should still exist"
        assert lock_record.locked is False, "Lock should be inactive"

    def test_phase_lock_replay_integrity(self):
        """Test replay integrity verification."""
        # Given - Create a phase lock
        phase = 7
        metadata = {"test": "replay"}
        lock = self.store.lock_phase(phase, metadata, "test_sig")

        # When - Verify replay integrity
        integrity_valid = self.store.verify_replay_integrity(phase)

        # Then - Integrity should be valid
        assert integrity_valid is True, "Replay integrity should be valid"

        # Verify digest is computed correctly
        replay_data = f"{phase}:{lock.timestamp}:{metadata}"
        import hashlib
        expected_digest = hashlib.sha256(replay_data.encode()).hexdigest()
        assert lock.replay_digest == expected_digest, "Replay digest should match"

    def test_phase_lock_sequence_validation(self):
        """Test phase sequence validation."""
        # Given - Lock phases in sequence
        self.store.lock_phase(1, {}, "sig1")
        self.store.lock_phase(2, {}, "sig2")
        self.store.lock_phase(3, {}, "sig3")

        # When - Validate sequence for current phase
        sequence_valid = self.validator.validate_phase_sequence(3)

        # Then - Sequence should be valid
        assert sequence_valid is True, "Phase sequence should be valid"

        # Phase 4 is also valid since all previous phases are locked
        assert self.validator.validate_phase_sequence(4) is True, \
            "Phase 4 validation should pass when phases 1-3 are locked"

        # But invalid if phases are missing (fresh validator with empty store)
        import tempfile
        with tempfile.TemporaryDirectory() as fresh_dir:
            from pathlib import Path as _Path
            from phase_lock_store import PhaseLockValidator, PhaseLockStore as FreshStore
            fresh_store = FreshStore(_Path(fresh_dir))
            fresh_validator = PhaseLockValidator(fresh_store)
            with pytest.raises(RuntimeError, match="Phase 1 must be locked"):
                fresh_validator.validate_phase_sequence(5)

    def test_phase_lock_dependency_validation(self):
        """Test phase dependency validation."""
        # Given - Lock dependency phases
        self.store.lock_phase(2, {}, "sig2")
        self.store.lock_phase(5, {}, "sig5")

        # When - Validate dependencies
        deps_valid = self.validator.validate_dependencies(7, [2, 5])

        # Then - Dependencies should be valid
        assert deps_valid is True, "Dependencies should be valid"

        # But invalid if dependency missing
        with pytest.raises(RuntimeError, match="Phase 3 must be locked"):
            self.validator.validate_dependencies(8, [2, 3, 5])

    def test_multiple_phase_locks_persistence(self):
        """Test persistence of multiple phase locks."""
        # Given - Lock multiple phases
        phases = [1, 3, 5, 7]
        locks = {}

        for phase in phases:
            metadata = {"phase": phase}
            lock = self.store.lock_phase(phase, metadata, f"sig{phase}")
            locks[phase] = lock

        # When - Create new store instance
        store2 = PhaseLockStore(self.temp_dir)

        # Then - All locks should be persisted
        for phase in phases:
            assert store2.is_locked(phase), f"Phase {phase} should be locked"

            restored_lock = store2.get_lock_record(phase)
            assert restored_lock.phase == phase
            assert restored_lock.metadata == {"phase": phase}

        # Verify all locked phases can be retrieved
        all_locked = store2.get_all_locked_phases()
        assert len(all_locked) == len(phases), "All locked phases should be retrieved"

        for phase in phases:
            assert phase in all_locked, f"Phase {phase} should be in locked phases"

    def test_phase_lock_timestamp_persistence(self):
        """Test that timestamps are persisted correctly."""
        # Given - Lock a phase with known timestamp
        phase = 4
        before_lock = time.time()
        lock = self.store.lock_phase(phase, {"test": "timestamp"}, "timestamp_sig")
        after_lock = time.time()

        # When - Create new store instance
        store2 = PhaseLockStore(self.temp_dir)

        # Then - Timestamp should be persisted and reasonable
        restored_lock = store2.get_lock_record(phase)
        assert restored_lock is not None, "Lock should exist"
        assert before_lock <= restored_lock.timestamp <= after_lock, "Timestamp should be reasonable"

    def test_phase_lock_clear_all(self):
        """Test clearing all phase locks."""
        # Given - Lock multiple phases
        for phase in [1, 2, 3]:
            self.store.lock_phase(phase, {}, "sig")

        assert len(self.store.get_all_locked_phases()) == 3, "Should have 3 locked phases"

        # When - Clear all locks
        self.store.clear_all_locks()

        # Then - No locks should remain
        assert len(self.store.get_all_locked_phases()) == 0, "No phases should be locked"

        # Verify persistence of clear
        store2 = PhaseLockStore(self.temp_dir)
        assert len(store2.get_all_locked_phases()) == 0, "Clear should persist"

    def test_phase_lock_unlock_permissions(self):
        """Test unlock permission validation."""
        # Given - Lock a phase
        phase = 6
        self.store.lock_phase(phase, {}, "lock_sig")

        # When - Try to unlock without signature
        with pytest.raises(RuntimeError, match="Signature required"):
            self.validator.validate_unlock_permissions(phase, "")

        # When - Try to unlock with signature
        permission_valid = self.validator.validate_unlock_permissions(phase, "unlock_sig")
        assert permission_valid is True, "Unlock should be permitted with signature"

        # Given - Lock a higher phase
        self.store.lock_phase(8, {}, "higher_sig")

        # When - Try to unlock lower phase
        with pytest.raises(RuntimeError, match="Cannot unlock phase 6 while phase 8 is locked"):
            self.validator.validate_unlock_permissions(phase, "unlock_sig")

    def test_phase_lock_storage_file_creation(self):
        """Test that storage files are created correctly."""
        # Given - Store should create files on first lock
        storage_file = self.temp_dir / "phase_locks.json"

        # When - Lock a phase
        self.store.lock_phase(1, {"test": "file"}, "test_sig")

        # Then - Storage file should exist
        assert storage_file.exists(), "Storage file should be created"

        # Verify file content is valid JSON
        with open(storage_file, 'r') as f:
            data = json.load(f)

        assert "1" in data, "Phase 1 should be in stored data"
        assert data["1"]["phase"] == 1, "Phase should be stored"
        assert data["1"]["locked"] is True, "Lock status should be stored"

    def test_phase_lock_missing_storage_handling(self):
        """Test handling of missing storage file."""
        # Given - Remove storage file if it exists
        storage_file = self.temp_dir / "phase_locks.json"
        if storage_file.exists():
            storage_file.unlink()

        # When - Create store with missing storage
        store = PhaseLockStore(self.temp_dir)

        # Then - Store should initialize correctly
        assert not store.is_locked(1), "No phases should be locked initially"
        assert len(store.get_all_locked_phases()) == 0, "Should have no locked phases"

        # And should be able to lock phases
        lock = store.lock_phase(1, {}, "test_sig")
        assert lock is not None, "Should be able to lock after missing storage init"

    def test_phase_lock_corrupted_storage_handling(self):
        """Test handling of corrupted storage file."""
        # Given - Create corrupted JSON file
        storage_file = self.temp_dir / "phase_locks.json"
        with open(storage_file, 'w') as f:
            f.write("invalid json content")

        # When - Create store with corrupted storage
        store = PhaseLockStore(self.temp_dir)

        # Then - Store should handle corruption gracefully
        assert not store.is_locked(1), "Should handle corruption gracefully"

        # And should be able to recover
        lock = store.lock_phase(1, {"recovery": "test"}, "recovery_sig")
        assert lock is not None, "Should recover and allow locking"
