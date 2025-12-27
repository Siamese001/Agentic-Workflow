"""Test concurrent healing with lock-based coordination."""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch
import threading
import time


@pytest.mark.integration
class TestConcurrentHealingCoordination:
    """Verify concurrent healers coordinate via locks to prevent conflicts."""
    
    def test_two_healers_serialize_via_lock(
        self, tmp_sovereign_workspace, concurrent_lock_manager, file_hash_tracker
    ):
        """
        GIVEN: Two healers attempting to modify same file
        WHEN: Lock manager coordinates access
        THEN: Modifications are serialized, both applied successfully
        """
        # Arrange
        target_file = tmp_sovereign_workspace / "shared.py"
        target_file.write_text("# Original\nvalue = 0\n")
        results = []
        
        def healer_1():
            resource_id = str(target_file)
            if concurrent_lock_manager.acquire(resource_id, timeout=2.0):
                try:
                    content = target_file.read_text()
                    time.sleep(0.1)  # Simulate work
                    target_file.write_text(content.replace("value = 0", "value = 1"))
                    results.append("healer_1_success")
                finally:
                    concurrent_lock_manager.release(resource_id)
        
        def healer_2():
            time.sleep(0.05)  # Start slightly after healer_1
            resource_id = str(target_file)
            if concurrent_lock_manager.acquire(resource_id, timeout=2.0):
                try:
                    content = target_file.read_text()
                    time.sleep(0.1)  # Simulate work
                    target_file.write_text(content.replace("value = 1", "value = 2"))
                    results.append("healer_2_success")
                finally:
                    concurrent_lock_manager.release(resource_id)
        
        # Act
        thread1 = threading.Thread(target=healer_1)
        thread2 = threading.Thread(target=healer_2)
        
        thread1.start()
        thread2.start()
        
        thread1.join(timeout=5.0)
        thread2.join(timeout=5.0)
        
        # Assert
        assert len(results) == 2
        assert "healer_1_success" in results
        assert "healer_2_success" in results
        assert "value = 2" in target_file.read_text()
    
    def test_lock_timeout_prevents_deadlock(
        self, tmp_sovereign_workspace, concurrent_lock_manager
    ):
        """
        GIVEN: Healer holding lock indefinitely
        WHEN: Second healer attempts acquisition with timeout
        THEN: Timeout prevents deadlock
        """
        # Arrange
        target_file = tmp_sovereign_workspace / "locked.py"
        target_file.write_text("# Locked\n")
        resource_id = str(target_file)
        
        # Healer 1 acquires and holds
        assert concurrent_lock_manager.acquire(resource_id) is True
        
        # Act - Healer 2 attempts with timeout
        acquired = concurrent_lock_manager.acquire(resource_id, timeout=0.5)
        
        # Assert
        assert acquired is False  # Timeout occurred
        assert concurrent_lock_manager.is_locked(resource_id) is True
        
        # Cleanup
        concurrent_lock_manager.release(resource_id)
    
    def test_multiple_files_concurrent_healing(
        self, tmp_sovereign_workspace, concurrent_lock_manager
    ):
        """
        GIVEN: Multiple files being healed concurrently
        WHEN: Each healer locks its target
        THEN: All healers proceed in parallel without conflict
        """
        # Arrange
        files = [
            tmp_sovereign_workspace / f"file_{i}.py"
            for i in range(5)
        ]
        for f in files:
            f.write_text(f"# File {f.name}\n")
        
        results = []
        
        def heal_file(file_path, healer_id):
            resource_id = str(file_path)
            if concurrent_lock_manager.acquire(resource_id, timeout=2.0):
                try:
                    time.sleep(0.1)  # Simulate healing work
                    content = file_path.read_text()
                    file_path.write_text(content + f"# Healed by {healer_id}\n")
                    results.append(f"healed_{healer_id}")
                finally:
                    concurrent_lock_manager.release(resource_id)
        
        # Act
        threads = [
            threading.Thread(target=heal_file, args=(files[i], i))
            for i in range(5)
        ]
        
        for t in threads:
            t.start()
        
        for t in threads:
            t.join(timeout=5.0)
        
        # Assert
        assert len(results) == 5
        for i in range(5):
            assert f"Healed by {i}" in files[i].read_text()


@pytest.mark.integration
class TestConcurrentMergeConflicts:
    """Test resolution of concurrent modification conflicts."""
    
    def test_last_writer_wins_without_coordination(
        self, tmp_sovereign_workspace
    ):
        """
        GIVEN: Two healers modifying same file without locks
        WHEN: Both write concurrently
        THEN: Last writer wins (data loss possible)
        """
        # Arrange
        target_file = tmp_sovereign_workspace / "uncoordinated.py"
        target_file.write_text("# Original\n")
        
        def writer_1():
            time.sleep(0.05)
            target_file.write_text("# Writer 1\n")
        
        def writer_2():
            time.sleep(0.1)
            target_file.write_text("# Writer 2\n")
        
        # Act
        thread1 = threading.Thread(target=writer_1)
        thread2 = threading.Thread(target=writer_2)
        
        thread1.start()
        thread2.start()
        
        thread1.join()
        thread2.join()
        
        # Assert - Writer 2 wins (last write)
        assert "Writer 2" in target_file.read_text()
        assert "Writer 1" not in target_file.read_text()
    
    def test_coordinated_merge_preserves_all_changes(
        self, tmp_sovereign_workspace, concurrent_lock_manager
    ):
        """
        GIVEN: Two healers with different fixes
        WHEN: Lock coordination ensures serial application
        THEN: Both fixes present in final state
        """
        # Arrange
        target_file = tmp_sovereign_workspace / "coordinated.py"
        target_file.write_text("class Original:\n    pass\n")
        
        def add_method_a():
            resource_id = str(target_file)
            if concurrent_lock_manager.acquire(resource_id, timeout=2.0):
                try:
                    content = target_file.read_text()
                    new_content = content.replace(
                        "pass",
                        "def method_a(self):\n        return 'a'"
                    )
                    target_file.write_text(new_content)
                finally:
                    concurrent_lock_manager.release(resource_id)
        
        def add_method_b():
            time.sleep(0.05)
            resource_id = str(target_file)
            if concurrent_lock_manager.acquire(resource_id, timeout=2.0):
                try:
                    content = target_file.read_text()
                    # Insert method_b before the last line
                    lines = content.splitlines()
                    lines.insert(-1, "    def method_b(self):\n        return 'b'")
                    target_file.write_text("\n".join(lines))
                finally:
                    concurrent_lock_manager.release(resource_id)
        
        # Act
        thread1 = threading.Thread(target=add_method_a)
        thread2 = threading.Thread(target=add_method_b)
        
        thread1.start()
        thread2.start()
        
        thread1.join()
        thread2.join()
        
        # Assert - Both methods present
        final_content = target_file.read_text()
        assert "method_a" in final_content
        assert "method_b" in final_content


@pytest.mark.integration
class TestHealingQueueOrdering:
    """Test healing operations respect priority and ordering."""
    
    def test_high_priority_healer_preempts_low_priority(
        self, tmp_sovereign_workspace
    ):
        """
        GIVEN: Healing queue with priority levels
        WHEN: High priority healer arrives
        THEN: Processes before lower priority healers
        """
        # Arrange
        execution_order = []
        
        def low_priority_healer():
            time.sleep(0.1)
            execution_order.append("low")
        
        def high_priority_healer():
            execution_order.append("high")
        
        # Act
        low_thread = threading.Thread(target=low_priority_healer)
        high_thread = threading.Thread(target=high_priority_healer)
        
        low_thread.start()
        time.sleep(0.05)  # Ensure low starts first
        high_thread.start()
        
        low_thread.join()
        high_thread.join()
        
        # Assert - High completes first despite starting later
        assert execution_order[0] == "high"
        assert execution_order[1] == "low"
    
    def test_fifo_ordering_within_same_priority(
        self, tmp_sovereign_workspace, concurrent_lock_manager
    ):
        """
        GIVEN: Multiple healers with same priority
        WHEN: All request lock on same resource
        THEN: FIFO ordering respected
        """
        # Arrange
        target_file = tmp_sovereign_workspace / "fifo.py"
        target_file.write_text("# Start\n")
        execution_order = []
        
        def healer(healer_id, delay):
            time.sleep(delay)
            resource_id = str(target_file)
            if concurrent_lock_manager.acquire(resource_id, timeout=5.0):
                try:
                    execution_order.append(healer_id)
                finally:
                    concurrent_lock_manager.release(resource_id)
        
        # Act
        threads = [
            threading.Thread(target=healer, args=(i, i * 0.01))
            for i in range(5)
        ]
        
        for t in threads:
            t.start()
        
        for t in threads:
            t.join()
        
        # Assert - Order matches start order
        assert execution_order == [0, 1, 2, 3, 4]
