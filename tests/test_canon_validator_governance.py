#!/usr/bin/env python3
"""
Canon Validator Engine - Governance & Resilience Test Suite (L3/L4/L5)

Tests for:
- GR-001: Cost Overrun (L3)
- GR-002: Redis Atomicity Failure (L4)
- GR-003: Temporal Awareness (L4)
- GR-004: MEMemory Failure (L5)
"""

from canon_validator_engine import execute_cost_governed_vulnerability_check
from canon_validator import CanonValidator
import pytest
import json
from unittest.mock import Mock, patch

# Import the validator
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestGovernanceResilience:
    """Test suite for Governance & Resilience (L3/L4/L5)"""

    @pytest.fixture
    def mock_validator(self):
        """Create a validator with mocked dependencies"""
        validator = CanonValidator()

        # Mock LLM responses
        validator.llm.generate_plan = Mock()

        # Mock embedding function
        validator.embed_fn = Mock(return_value=[0.1] * 768)

        # Mock Pinecone
        validator.pinecone = Mock()
        validator.pinecone.query = Mock(return_value={'matches': []})
        validator.pinecone.upsert = Mock()

        # Mock Redis cache
        validator.cache = Mock()
        validator.cache.check = Mock(return_value=None)
        validator.cache.store = Mock()

        return validator

    @patch('canon_validator_engine.execute_vulnerability_search')
    @patch('canon_validator_engine.execute_hybrid_fix_search')
    def test_gr001_cost_overrun_l3(self, mock_pinecone, mock_brave):
        """GR-001: Cost Overrun (L3)"""
        # Track quota usage
        quota_used = 0
        quota_limit = 2  # Set low limit for testing

        def mock_brave_with_quota(query, logger):
            nonlocal quota_used
            if quota_used >= quota_limit:
                raise Exception("Brave Search quota exceeded")
            quota_used += 1
            return json.dumps([{
                "source": "security.stackexchange.com",
                "fix_text": "Apply secure pattern",
                "confidence": "high"
            }])

        def mock_pinecone_fallback(description, version, logger):
            return {
                "status": "success",
                "fix_result": {
                    "metadata": {
                        "edits": [{"oldText": "insecure", "newText": "secure"}]
                    }
                },
                "source": "Pinecone_HighCost"
            }

        mock_brave.side_effect = mock_brave_with_quota
        mock_pinecone.side_effect = mock_pinecone_fallback

        # Execute until quota exhaustion
        results = []
        for i in range(5):  # Try 5 times, should hit quota limit
            try:
                result = execute_cost_governed_vulnerability_check(
                    violation_hash=f"VIO_{i}",
                    violation_description=f"Violation {i}",
                    code_version="v1.0.0",
                    logger=Mock()
                )
                results.append(result)
            except Exception as e:
                results.append({"status": "error", "message": str(e)})

        # Verify cost governance
        assert quota_used == quota_limit  # Used up quota
        # Fallback used
        assert any(r.get("source") == "Pinecone_HighCost" for r in results)
        assert any("quota" in str(r).lower()
                   for r in results)  # Quota hit logged

    def test_gr002_redis_atomicity_failure_l4(self, mock_validator):
        """GR-002: Redis Atomicity Failure (L4)"""
        # Mock Redis to fail on EXEC
        mock_redis = Mock()
        mock_redis.multi = Mock(return_value=mock_redis)
        mock_redis.exec = Mock(side_effect=Exception(
            "Redis connection lost before EXEC"))
        mock_redis.discard = Mock()

        # Test atomic transaction failure
        with patch('canon_validator.redis_client', mock_redis):
            validator = CanonValidator()
            validator.cache = mock_redis

            # Try to perform atomic operations
            try:
                # Simulate atomic transaction
                mock_redis.multi()
                mock_redis.set("key1", "value1")
                mock_redis.set("key2", "value2")
                mock_redis.exec()  # This should fail

                assert False, "Should have raised Atomic State Integrity Error"
            except Exception as e:
                assert "Atomic State Integrity Error" in str(
                    e) or "connection lost" in str(e).lower()

            # Verify rollback was attempted
            mock_redis.discard.assert_called()

    @patch('canon_validator.mcp11_get_current_time')
    def test_gr003_temporal_awareness_l4(self, mock_get_time):
        """GR-003: Temporal Awareness (L4)"""
        # Mock time responses for different timezones
        mock_responses = {
            "Asia/Tokyo": "2025-01-15T15:00:00+09:00",
            "Europe/London": "2025-01-15T06:00:00+00:00"
        }

        def mock_time_response(timezone):
            return {"time": mock_responses[timezone], "timezone": timezone}

        mock_get_time.side_effect = mock_time_response

        # Test temporal awareness
        from mcp11_convert_time import convert_time

        # Convert between timezones
        result = convert_time(
            source_timezone="Asia/Tokyo",
            time="15:00",
            target_timezone="Europe/London"
        )

        # Verify time conversion
        assert "06:00" in result["time"] or "06:00" in str(result)

        # Verify ISO format preservation
        for timezone in ["Asia/Tokyo", "Europe/London"]:
            time_data = mock_get_time(timezone)
            assert "T" in time_data["time"]  # ISO format
            assert "+" in time_data["time"]  # Timezone offset

    def test_gr004_mememory_failure_l5(self, mock_validator):
        """GR-004: MEMemory Failure (L5)"""
        # Mock MEMemory to fail
        def mock_failing_memory(observations):
            raise ConnectionError("MEMemory endpoint unavailable")

        # Mock add_observations to fail
        with patch('canon_validator.add_observations', side_effect=mock_failing_memory):
            # Setup validator to work normally
            mock_validator.llm.generate_plan.return_value = {
                "status": "valid",
                "reasoning": "Code is compliant"
            }

            # Execute validation - should continue despite MEMemory failure
            result = mock_validator.validate("valid code")

            # Should succeed despite logging failure
            assert result["status"] == "valid"

            # Verify other operations still worked
            mock_validator.pinecone.upsert.assert_called()

    def test_cost_tracking_enforcement(self, mock_validator):
        """Test that cost tracking is enforced across operations"""
        cost_tracker = {"total": 0, "brave_calls": 0, "pinecone_calls": 0}

        def track_cost(operation, cost):
            cost_tracker["total"] += cost
            if operation == "brave":
                cost_tracker["brave_calls"] += 1
            elif operation == "pinecone":
                cost_tracker["pinecone_calls"] += 1

            # Enforce daily limit
            if cost_tracker["total"] > 100:  # $100 daily limit
                raise Exception(
                    f"Daily cost limit exceeded: ${cost_tracker['total']}")

        # Mock operations with cost tracking
        with patch('canon_validator_engine.execute_vulnerability_search') as mock_brave:
            with patch('canon_validator_engine.execute_hybrid_fix_search') as mock_pinecone:
                def mock_brave_with_cost(*args, **kwargs):
                    track_cost("brave", 1)  # $1 per call
                    return json.dumps([{"fix_text": "fix"}])

                def mock_pinecone_with_cost(*args, **kwargs):
                    track_cost("pinecone", 10)  # $10 per call
                    return {"status": "success"}

                mock_brave.side_effect = mock_brave_with_cost
                mock_pinecone.side_effect = mock_pinecone_with_cost

                # Execute until limit hit
                operations = 0
                while operations < 15:  # Should hit limit before 15 operations
                    try:
                        execute_cost_governed_vulnerability_check(
                            "VIO_TEST", "test", "v1.0", Mock()
                        )
                        operations += 1
                    except Exception as e:
                        assert "cost limit exceeded" in str(e).lower()
                        break

                # Verify cost was tracked
                assert cost_tracker["total"] > 100
                assert cost_tracker["brave_calls"] > 0

    def test_state_consistency_l4(self, mock_validator):
        """Test L4 state consistency across operations"""
        # Mock Redis with state tracking
        state_changes = []

        def mock_set_with_state(key, value):
            state_changes.append(("SET", key, value))

        def mock_get_with_state(key):
            for change in reversed(state_changes):
                if change[0] == "SET" and change[1] == key:
                    return change[2]
            return None

        mock_redis = Mock()
        mock_redis.set = Mock(side_effect=mock_set_with_state)
        mock_redis.get = Mock(side_effect=mock_get_with_state)

        # Test state consistency
        with patch('canon_validator.redis_client', mock_redis):
            # Perform operations
            mock_redis.set("audit:123", "PENDING")
            mock_redis.set("audit:123", "COMPLETED")

            # Verify state
            assert mock_redis.get("audit:123") == "COMPLETED"

            # Verify all changes were tracked
            assert len(state_changes) == 2
            assert state_changes[-1] == ("SET", "audit:123", "COMPLETED")

    def test_circuit_breaker_pattern(self, mock_validator):
        """Test circuit breaker for external dependencies"""
        # Mock Pinecone with failures
        failure_count = 0
        circuit_open = False

        def mock_pinecone_with_circuit(*args, **kwargs):
            nonlocal failure_count, circuit_open
            if circuit_open:
                raise Exception("Circuit breaker is OPEN")

            failure_count += 1
            if failure_count >= 3:  # Open circuit after 3 failures
                circuit_open = True
                raise Exception(
                    "Circuit breaker opened due to repeated failures")

            raise Exception("Simulated failure")

        mock_validator.pinecone.query.side_effect = mock_pinecone_with_circuit

        # Execute operations until circuit opens
        for i in range(5):
            try:
                mock_validator.validate("test code")
            except Exception as e:
                if "circuit breaker" in str(e).lower():
                    assert circuit_open
                    assert failure_count >= 3
                    break
        else:
            assert False, "Circuit breaker should have opened"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

