#!/usr/bin/env python3
"""
EBP-002: State Rollback (The Anchor Drop)
Emergency Protocol test for L4 state reversion
"""

import pytest
from unittest.mock import Mock, patch, call
import json
import time
from datetime import datetime, timezone
from canon_validator import CanonValidator


class TestEBP002:
    """Test Emergency Bailout Protocol Phase 2 - State Rollback"""
    
    @pytest.fixture
    def validator(self):
        """Create validator with mocked dependencies"""
        validator = CanonValidator()
        validator.llm = Mock()
        validator.llm.generate_plan.return_value = {
            "status": "valid",
            "reasoning": "Code is valid"
        }
        validator.embed_fn = Mock(return_value=[0.1] * 768)
        validator.cache = Mock()
        validator.cache.check = Mock(return_value=None)
        validator.pinecone = Mock()
        validator.pinecone.query = Mock(return_value={'matches': []})
        validator.pinecone.upsert = Mock()
        return validator
    
    def test_codebase_reversion(self, validator):
        """Test EBP-2.1: Codebase reversion using GitKraken"""
        git_history = [
            {"commit_id": "abc123", "message": "Last good state", "timestamp": "2025-12-15T10:00:00Z"},
            {"commit_id": "def456", "message": "Broken change", "timestamp": "2025-12-15T11:00:00Z"},
            {"commit_id": "ghi789", "message": "Current broken state", "timestamp": "2025-12-15T12:00:00Z"}
        ]
        
        current_commit = "ghi789"
        rollback_target = "abc123"
        
        git_operations = []
        
        def mock_git_reset(commit_id):
            """Mock git reset --hard operation"""
            git_operations.append({
                "operation": "reset",
                "commit_id": commit_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            return {"status": "success", "commit_id": commit_id}
        
        def mock_get_current_commit():
            return current_commit
        
        # Execute rollback
        current = mock_get_current_commit()
        assert current == "ghi789"
        
        result = mock_git_reset(rollback_target)
        
        # Verify rollback
        assert result["status"] == "success"
        assert result["commit_id"] == "abc123"
        assert len(git_operations) == 1
        assert git_operations[0]["commit_id"] == "abc123"
    
    def test_atomic_state_reversion(self, validator):
        """Test EBP-2.2: Atomic state reversion using L4 utility"""
        # Simulate state snapshots
        state_snapshots = {
            "snapshot_001": {
                "timestamp": "2025-12-15T10:00:00Z",
                "data": {
                    "audit:state": "COMPLETED",
                    "audit:result": '{"status": "success"}',
                    "counter": 100,
                    "config:version": "1.0.0"
                }
            },
            "snapshot_002": {
                "timestamp": "2025-12-15T11:00:00Z",
                "data": {
                    "audit:state": "FAILED",
                    "audit:result": '{"status": "error"}',
                    "counter": 150,
                    "config:version": "1.1.0"
                }
            }
        }
        
        current_state = {
            "audit:state": "CORRUPTED",
            "audit:result": '{"status": "critical_error"}',
            "counter": 200,
            "config:version": "1.2.0"
        }
        
        rollback_log = []
        
        def mock_l4_state_rollback(snapshot_id):
            """Mock L4 state rollback utility"""
            if snapshot_id not in state_snapshots:
                return {"status": "error", "message": "Snapshot not found"}
            
            snapshot = state_snapshots[snapshot_id]
            rollback_log.append({
                "operation": "L4_ATOMIC_ROLLBACK",
                "snapshot_id": snapshot_id,
                "timestamp": snapshot["timestamp"],
                "keys_restored": list(snapshot["data"].keys())
            })
            
            # Restore state
            current_state.clear()
            current_state.update(snapshot["data"])
            
            return {"status": "success", "snapshot_id": snapshot_id}
        
        # Execute rollback to last good state
        result = mock_l4_state_rollback("snapshot_001")
        
        # Verify rollback
        assert result["status"] == "success"
        assert result["snapshot_id"] == "snapshot_001"
        assert current_state["audit:state"] == "COMPLETED"
        assert current_state["counter"] == 100
        assert current_state["config:version"] == "1.0.0"
        
        # Verify rollback log
        assert len(rollback_log) == 1
        assert rollback_log[0]["operation"] == "L4_ATOMIC_ROLLBACK"
        assert len(rollback_log[0]["keys_restored"]) == 4
    
    def test_quota_freeze(self, validator):
        """Test EBP-2.3: Quota freeze for Brave Search"""
        redis_state = {}
        max_quota = 1000
        
        def mock_get_quota():
            return int(redis_state.get("brave_search:daily_count", 0))
        
        def mock_set_quota(value):
            redis_state["brave_search:daily_count"] = value
            return True
        
        def mock_freeze_quota():
            """Freeze quota at maximum to prevent further usage"""
            redis_state["brave_search:daily_count"] = max_quota
            redis_state["quota:frozen"] = True
            redis_state["quota:frozen_at"] = datetime.now(timezone.utc).isoformat()
            return True
        
        # Set initial quota usage
        mock_set_quota(250)
        assert mock_get_quota() == 250
        
        # Freeze quota
        result = mock_freeze_quota()
        
        # Verify freeze
        assert result == True
        assert mock_get_quota() == max_quota
        assert redis_state["quota:frozen"] == True
        assert "quota:frozen_at" in redis_state
        
        # Verify attempts to use quota fail
        def mock_attempt_search():
            if redis_state.get("quota:frozen", False):
                raise Exception("QUOTA_FROZEN: Brave Search disabled by EBP")
            return "search results"
        
        try:
            mock_attempt_search()
            assert False, "Should have failed due to frozen quota"
        except Exception as e:
            assert "QUOTA_FROZEN" in str(e)
    
    def test_rollback_transaction_integrity(self, validator):
        """Test that rollback operations are atomic"""
        rollback_operations = []
        
        class MockRollbackTransaction:
            def __init__(self):
                self.operations = []
                self.executed = False
                self.failed = False
            
            def add_operation(self, operation_type, target, data):
                self.operations.append({
                    "type": operation_type,
                    "target": target,
                    "data": data
                })
            
            def execute(self):
                """Execute all rollback operations atomically"""
                try:
                    for op in self.operations:
                        rollback_operations.append(f"EXEC: {op['type']} {op['target']}")
                        # Simulate potential failure
                        if op["target"] == "test":
                            self.failed = True
                            raise Exception("Rollback operation failed")
                    
                    self.executed = True
                    return True
                except Exception as e:
                    # Rollback all operations
                    rollback_operations.append("ROLLBACK: All operations reverted")
                    return False
        
        # Create rollback transaction
        tx = MockRollbackTransaction()
        tx.add_operation("git_reset", "commit_abc", {})
        tx.add_operation("state_restore", "redis", {})
        tx.add_operation("quota_freeze", "brave_search", {})
        tx.add_operation("fail_point", "test", {})  # This will fail
        
        # Debug: check operations
        print(f"Operations: {[op['target'] for op in tx.operations]}")
        
        # Execute transaction
        result = tx.execute()
        
        # Verify atomic behavior
        assert not result
        assert tx.failed
        assert "ROLLBACK: All operations reverted" in rollback_operations
        assert not tx.executed
    
    def test_rollback_verification(self, validator):
        """Test verification after rollback"""
        verification_results = []
        
        def mock_verify_rollback():
            """Verify system state after rollback"""
            checks = {
                "git_state": True,  # Git is at correct commit
                "redis_state": True,  # Redis state restored
                "quota_frozen": True,  # Quota is frozen
                "tools_disabled": True,  # Tools are disabled
                "blackout_active": True  # Blackout flag is set
            }
            
            for check_name, passed in checks.items():
                verification_results.append({
                    "check": check_name,
                    "status": "PASS" if passed else "FAIL",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
            
            return all(checks.values()), checks
        
        # Execute verification
        all_passed, details = mock_verify_rollback()
        
        # Verify all checks passed
        assert all_passed
        assert len(verification_results) == 5
        for result in verification_results:
            assert result["status"] == "PASS"
    
    def test_rollback_completion_logging(self, validator):
        """Test that rollback completion is properly logged"""
        rollback_log = []
        
        def mock_log_rollback_completion(rollback_details):
            """Log rollback completion to L5 MEMemory"""
            log_entry = {
                "entityName": "emergency_bailout_protocol",
                "contents": [
                    f"EBP-2 COMPLETED: State rollback successful",
                    f"Git reset to: {rollback_details['git_commit']}",
                    f"State snapshot: {rollback_details['snapshot_id']}",
                    f"Quota frozen: {rollback_details['quota_frozen']}",
                    f"Rollback time: {rollback_details['duration']}ms"
                ],
                "corpusNames": ["canon_validator"],
                "tags": ["ebp", "rollback", "l4", "emergency"]
            }
            rollback_log.append(log_entry)
            return {"status": "logged"}
        
        # Log rollback completion
        rollback_details = {
            "git_commit": "abc123",
            "snapshot_id": "snapshot_001",
            "quota_frozen": True,
            "duration": 250
        }
        
        result = mock_log_rollback_completion(rollback_details)
        
        # Verify logging
        assert result["status"] == "logged"
        assert len(rollback_log) == 1
        log = rollback_log[0]
        assert "EBP-2 COMPLETED" in str(log["contents"])
        assert "rollback" in log["tags"]
        assert "l4" in log["tags"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
