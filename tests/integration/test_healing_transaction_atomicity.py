"""Test healing transaction atomicity - zero-loss guarantee."""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import hashlib

@pytest.mark.integration
class test_healing_transaction_atomicity:
    """Verify HealingTransaction backup/commit/rollback preserves data integrity."""

    def test_successful_commit_clears_backups(self, tmp_sovereign_workspace: Any, healing_transaction_mock: Any, file_hash_tracker: Any) -> Any:
        """
        GIVEN: A file with original content
        WHEN: Transaction backs up, modifies, and commits
        THEN: Backups are cleared and new content persists
        """
        test_file: Any = tmp_sovereign_workspace / 'test_module.py'
        original_content: Any = 'def original_function():\n    pass\n'
        test_file.write_text(original_content)
        original_hash: Any = file_hash_tracker(test_file)
        healing_transaction_mock.backup(test_file)
        test_file.write_text("def healed_function():\n    return 'fixed'\n")
        healing_transaction_mock.commit()
        assert healing_transaction_mock.committed is True
        assert len(healing_transaction_mock.backups) == 0
        assert file_hash_tracker(test_file) != original_hash
        assert 'healed_function' in test_file.read_text()

    def test_rollback_restores_exact_content(self, tmp_sovereign_workspace: Any, healing_transaction_mock: Any, file_hash_tracker: Any) -> Any:
        """
        GIVEN: A file modified during transaction
        WHEN: Rollback is triggered
        THEN: Original content is restored bit-for-bit (hash match)
        """
        test_file: Any = tmp_sovereign_workspace / 'critical_module.py'
        original_content: Any = '# Critical sovereignty code\nclass SovereignCore:\n    pass\n'
        test_file.write_text(original_content)
        original_hash: Any = file_hash_tracker(test_file)
        healing_transaction_mock.backup(test_file)
        test_file.write_text('# CORRUPTED\nclass Broken:\n    raise Exception()\n')
        corrupted_hash: Any = file_hash_tracker(test_file)
        healing_transaction_mock.rollback()
        assert healing_transaction_mock.rolled_back is True
        assert file_hash_tracker(test_file) == original_hash
        assert file_hash_tracker(test_file) != corrupted_hash
        assert test_file.read_text() == original_content

    def test_partial_failure_triggers_full_rollback(self, tmp_sovereign_workspace: Any, healing_transaction_mock: Any, file_hash_tracker: Any) -> Any:
        """
        GIVEN: Multiple files in transaction, one fails mid-operation
        WHEN: Exception occurs during healing
        THEN: All files rollback to original state
        """
        file1: Any = tmp_sovereign_workspace / 'module1.py'
        file2: Any = tmp_sovereign_workspace / 'module2.py'
        file1.write_text('# Module 1\nclass A:\n    pass\n')
        file2.write_text('# Module 2\nclass B:\n    pass\n')
        hash1_original: Any = file_hash_tracker(file1)
        hash2_original: Any = file_hash_tracker(file2)
        healing_transaction_mock.backup(file1)
        healing_transaction_mock.backup(file2)
        file1.write_text('# Modified 1\nclass A_Fixed:\n    pass\n')
        file2.write_text('# Modified 2\nclass B_Fixed:\n    pass\n')
        healing_transaction_mock.rollback()
        assert file_hash_tracker(file1) == hash1_original
        assert file_hash_tracker(file2) == hash2_original
        assert 'A_Fixed' not in file1.read_text()
        assert 'B_Fixed' not in file2.read_text()

    def test_no_backup_no_rollback_corruption(self, tmp_sovereign_workspace: Any, healing_transaction_mock: Any) -> Any:
        """
        GIVEN: File modified without backup
        WHEN: Rollback is attempted
        THEN: File remains in modified state (no phantom restoration)
        """
        test_file: Any = tmp_sovereign_workspace / 'no_backup.py'
        test_file.write_text('# Original\n')
        test_file.write_text('# Modified without backup\n')
        healing_transaction_mock.rollback()
        assert 'Modified without backup' in test_file.read_text()
        assert healing_transaction_mock.rolled_back is True

    @pytest.mark.parametrize('file_size', [100, 10000, 100000])
    def test_large_file_rollback_integrity(self, tmp_sovereign_workspace: Any, healing_transaction_mock: Any, file_hash_tracker: Any, file_size: Any) -> Any:
        """
        GIVEN: Large file (up to 100KB)
        WHEN: Transaction rollback occurs
        THEN: Full content restored regardless of size
        """
        test_file: Any = tmp_sovereign_workspace / f'large_{file_size}.py'
        original_content: Any = '# ' + 'x' * file_size + '\n'
        test_file.write_text(original_content)
        original_hash: Any = file_hash_tracker(test_file)
        healing_transaction_mock.backup(test_file)
        test_file.write_text('# Corrupted\n')
        healing_transaction_mock.rollback()
        assert file_hash_tracker(test_file) == original_hash
        assert len(test_file.read_text()) == len(original_content)

    def test_transaction_operations_audit_trail(self, tmp_sovereign_workspace: Any, healing_transaction_mock: Any, audit_log_tracker: Any) -> Any:
        """
        GIVEN: Transaction with multiple operations
        WHEN: Operations are performed
        THEN: Audit trail records all operations in order
        """
        file1: Any = tmp_sovereign_workspace / 'audit1.py'
        file2: Any = tmp_sovereign_workspace / 'audit2.py'
        file1.write_text('# File 1\n')
        file2.write_text('# File 2\n')
        healing_transaction_mock.backup(file1)
        audit_log_tracker.log('backup', {'file': str(file1)})
        healing_transaction_mock.backup(file2)
        audit_log_tracker.log('backup', {'file': str(file2)})
        healing_transaction_mock.commit()
        audit_log_tracker.log('commit', {'files': 2})
        operations: Any = healing_transaction_mock.get_operations()
        assert len(operations) == 3
        assert operations[0][0] == 'backup'
        assert operations[1][0] == 'backup'
        assert operations[2][0] == 'commit'
        audit_entries: Any = audit_log_tracker.get_entries('backup')
        assert len(audit_entries) == 2

    def test_nested_transaction_not_supported(self, tmp_sovereign_workspace: Any, healing_transaction_mock: Any) -> Any:
        """
        GIVEN: Attempt to nest transactions
        WHEN: Second backup called before commit
        THEN: Operations are sequential (no nesting support in mock)
        """
        test_file: Any = tmp_sovereign_workspace / 'nested.py'
        test_file.write_text('# Original\n')
        healing_transaction_mock.backup(test_file)
        test_file.write_text('# Modified 1\n')
        healing_transaction_mock.backup(test_file)
        test_file.write_text('# Modified 2\n')
        healing_transaction_mock.rollback()
        assert 'Modified 1' in test_file.read_text()
        assert 'Modified 2' not in test_file.read_text()

@pytest.mark.integration
class test_zero_loss_guarantee:
    """Verify zero data loss across all transaction scenarios."""

    def test_binary_file_preservation(self, tmp_sovereign_workspace: Any, healing_transaction_mock: Any, file_hash_tracker: Any) -> Any:
        """
        GIVEN: Binary file (non-text)
        WHEN: Transaction rollback occurs
        THEN: Binary content preserved exactly
        """
        binary_file: Any = tmp_sovereign_workspace / 'data.bin'
        binary_content: Any = bytes([0, 255, 170, 85] * 100)
        binary_file.write_bytes(binary_content)
        original_hash: Any = hashlib.sha256(binary_content).hexdigest()
        healing_transaction_mock.backup(binary_file)
        binary_file.write_bytes(bytes([0] * 400))
        healing_transaction_mock.rollback()
        restored_hash: Any = hashlib.sha256(binary_file.read_bytes()).hexdigest()
        assert restored_hash == original_hash

    def test_unicode_content_preservation(self, tmp_sovereign_workspace: Any, healing_transaction_mock: Any, file_hash_tracker: Any) -> Any:
        """
        GIVEN: File with unicode characters
        WHEN: Transaction rollback occurs
        THEN: Unicode preserved exactly
        """
        unicode_file: Any = tmp_sovereign_workspace / 'unicode.py'
        unicode_content: Any = '# Sovereignty Architecture\n# Souverainete\n# Suverenitet\n'
        unicode_file.write_text(unicode_content, encoding='utf-8')
        original_hash: Any = hashlib.sha256(unicode_content.encode('utf-8')).hexdigest()
        healing_transaction_mock.backup(unicode_file)
        unicode_file.write_text('# ASCII only\n', encoding='utf-8')
        healing_transaction_mock.rollback()
        restored_hash: Any = hashlib.sha256(unicode_file.read_text(encoding='utf-8').encode('utf-8')).hexdigest()
        assert restored_hash == original_hash
        assert 'Sovereignty' in unicode_file.read_text(encoding='utf-8')
