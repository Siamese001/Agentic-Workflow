#!/usr/bin/env python3
"""
Canon Validator Engine - Integration Test Suite

Tests the complete workflow across all layers (L1-L5) with real interactions
between components.
"""

from canon_validator_engine import execute_cost_governed_vulnerability_check
from canon_validator import CanonValidator
import pytest
import json
import time
import tempfile
import os
from unittest.mock import Mock, patch

# Import the validator
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestCanonValidatorIntegration:
    """Integration tests for the complete Canon Validator workflow"""

    @pytest.fixture
    def temp_workspace(self):
        """Create a temporary workspace for integration tests"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            test_file = os.path.join(tmpdir, "test.py")
            with open(test_file, "w") as f:
                f.write("""
import os

def vulnerable_function():
    os.system("ls -la")
    return True
""")

            yield {
                "dir": tmpdir,
                "test_file": test_file
            }

    def test_full_validation_workflow(self, mock_validator_with_all_dependencies, sample_violating_code):
        """Test the complete validation workflow from violation to repair"""
        validator = mock_validator_with_all_dependencies

        # Setup LLM responses for full workflow
        validator.llm.generate_plan.side_effect = [
            {"status": "rejected", "reasoning": "Uses os.system() - security risk"},
            {"code": "import subprocess\n\ndef safe_function():\n    subprocess.run(['ls', '-la'])"}
        ]

        # Execute full workflow
        result = validator.validate(sample_violating_code, auto_repair=True)

        # Verify complete flow
        assert result["status"] == "repaired"
        assert "subprocess" in result["repaired_code"]

        # Verify all components were used
        assert validator.embed_fn.called  # L1: Embedding
        assert validator.cache.check.called  # L1: Cache check
        assert validator.pinecone.query.called  # L3: Context retrieval
        assert validator.llm.generate_plan.call_count == 2  # L5: LLM validation + repair
        assert validator.pinecone.upsert.called  # L5: Meta-learning

    def test_design_compliance_end_to_end(self, temp_workspace):
        """Test design compliance check from file detection to repair"""
        # Create a file with hardcoded colors
        css_file = os.path.join(temp_workspace["dir"], "styles.css")
        with open(css_file, "w") as f:
            f.write("""
.button {
    background-color: #FF0000;
    color: #FFFFFF;
}
""")

        # Mock MCP tools
        mock_tools = {
            'read_text_file': Mock(return_value=".button { background-color: #FF0000; }"),
            'get_variable_defs': Mock(return_value=json.dumps([
                {"name": "primary-red", "value": "#FF0000",
                    "replacement": "tokens.color-primary"}
            ])),
            'search_records': Mock(return_value=json.dumps([{
                "metadata": {"replacement_snippet": "tokens.color-primary"}
            }])),
            'edit_file': Mock(return_value={"status": "success"}),
            'string_set': Mock()
        }

        # Execute design compliance
        validator = CanonValidator()
        result = validator.validate_design_compliance(
            file_path=css_file,
            component_id="button-component",
            tools=mock_tools
        )

        # Verify end-to-end flow
        assert result["status"] == "repaired"
        assert "tokens.color-primary" in result["message"]

        # Verify tool sequence
        mock_tools['read_text_file'].assert_called_once()
        mock_tools['get_variable_defs'].assert_called_once()
        mock_tools['search_records'].assert_called_once()
        mock_tools['edit_file'].assert_called_once()

    def test_cost_governed_rag_fallback_chain(self):
        """Test the complete RAG fallback chain with cost governance"""
        # Track call sequence and costs
        call_sequence = []
        total_cost = 0

        def mock_brave_search(query, logger):
            nonlocal call_sequence, total_cost
            call_sequence.append("brave_search")
            total_cost += 1

            # Return insufficient context on first call
            if len(call_sequence) == 1:
                return json.dumps([{
                    "source": "generic.com",
                    "fix_text": "Not specific enough",
                    "confidence": "low"
                }])
            else:
                return json.dumps([{
                    "source": "security.stackexchange.com",
                    "fix_text": "Apply proper input validation",
                    "confidence": "high",
                    "edits": [{"oldText": "eval(", "newText": "validate_input("}]
                }])

        def mock_pinecone_search(description, version, logger):
            nonlocal call_sequence, total_cost
            call_sequence.append("pinecone_search")
            total_cost += 10

            return {
                "status": "success",
                "fix_result": {
                    "metadata": {
                        "edits": [{"oldText": "eval(", "newText": "safe_eval("}]
                    }
                },
                "source": "Pinecone_HighCost"
            }

        # Test with quota exhaustion
        quota_limit = 2
        brave_calls = 0

        def brave_with_quota(query, logger):
            nonlocal brave_calls
            brave_calls += 1
            if brave_calls > quota_limit:
                raise Exception("Brave Search quota exceeded")
            return mock_brave_search(query, logger)

        # Execute multiple times to test fallback
        results = []
        for i in range(5):
            try:
                with patch('canon_validator_engine.execute_vulnerability_search', side_effect=brave_with_quota), \
                        patch('canon_validator_engine.execute_hybrid_fix_search', side_effect=mock_pinecone_search):

                    result = execute_cost_governed_vulnerability_check(
                        violation_hash=f"VIO_{i}",
                        violation_description=f"Test violation {i}",
                        code_version="v1.0.0",
                        logger=Mock()
                    )
                    results.append(result)
            except Exception as e:
                results.append({"status": "error", "message": str(e)})

        # Verify cost governance worked
        assert brave_calls == quota_limit + 1  # One call over limit
        assert any(r.get("source") == "Pinecone_HighCost" for r in results)
        assert total_cost > 0

    def test_atomic_transaction_rollback(self):
        """Test atomic transaction with rollback on failure"""
        # Mock Redis with transaction support
        transaction_state = []

        class MockRedisTransaction:
            def __init__(self):
                self.operations = []

            def multi(self):
                transaction_state.append("MULTI")
                return self

            def set(self, key, value):
                self.operations.append(("SET", key, value))
                return self

            def exec(self):
                transaction_state.append("EXEC")
                # Simulate failure
                if "FAIL" in self.operations[-1][1]:
                    transaction_state.append("ROLLBACK")
                    raise Exception("Transaction failed")
                return "OK"

            def discard(self):
                transaction_state.append("DISCARD")
                return self

        mock_redis = MockRedisTransaction()

        # Test successful transaction
        try:
            mock_redis.multi()
            mock_redis.set("audit:123", "PENDING")
            mock_redis.set("audit:123", "COMPLETED")
            mock_redis.exec()
            assert "ROLLBACK" not in transaction_state
        except:
            assert False, "Transaction should have succeeded"

        # Reset and test failed transaction
        transaction_state.clear()
        try:
            mock_redis.multi()
            mock_redis.set("audit:456", "PENDING")
            mock_redis.set("audit:456", "FAIL")
            mock_redis.exec()
            assert False, "Should have raised exception"
        except Exception:
            assert "ROLLBACK" in transaction_state

    def test_cross_layer_error_propagation(self, mock_validator_with_all_dependencies):
        """Test error handling across all layers"""
        validator = mock_validator_with_all_dependencies

        # Test L1 failure (embedding)
        validator.embed_fn.side_effect = Exception("Embedding service down")
        result = validator.validate("test code")
        assert result["status"] == "error"
        assert "embedding" in result["message"].lower()

        # Reset and test L3 failure (Pinecone)
        validator.embed_fn.side_effect = None
        validator.pinecone.query.side_effect = Exception(
            "Pinecone unavailable")
        validator.llm.generate_plan.return_value = {
            "status": "valid", "reasoning": "OK"}

        result = validator.validate("test code")
        # Should continue despite Pinecone failure
        assert result["status"] == "valid"

        # Test L5 failure (MEMemory)
        with patch('canon_validator.add_observations', side_effect=Exception("MEMemory down")):
            result = validator.validate("test code")
            # Should continue despite logging failure
            assert result["status"] == "valid"

    def test_concurrent_workflows_isolation(self):
        """Test multiple concurrent workflows don't interfere"""
        import concurrent.futures

        results = []
        errors = []

        def validate_workflow(workflow_id):
            try:
                # Create isolated validator for each workflow
                validator = CanonValidator()
                validator.llm = Mock()
                validator.llm.generate_plan = Mock(return_value={
                    "status": "valid",
                    "reasoning": f"Valid for workflow {workflow_id}"
                })
                validator.embed_fn = Mock(return_value=[0.1] * 768)
                validator.cache = Mock()
                validator.cache.check = Mock(return_value=None)
                validator.pinecone = Mock()
                validator.pinecone.query = Mock(return_value={'matches': []})
                validator.pinecone.upsert = Mock()

                result = validator.validate(f"code_{workflow_id}")
                results.append((workflow_id, result))
            except Exception as e:
                errors.append((workflow_id, e))

        # Run 20 concurrent workflows
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(validate_workflow, i)
                for i in range(20)
            ]
            concurrent.futures.wait(futures)

        # Verify isolation
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 20

        for workflow_id, result in results:
            assert result["status"] == "valid"
            assert str(workflow_id) in result["reasoning"]

    def test_performance_under_load(self, mock_validator_with_all_dependencies):
        """Test system performance under load"""
        validator = mock_validator_with_all_dependencies
        validator.llm.generate_plan.return_value = {
            "status": "valid",
            "reasoning": "Performance test"
        }

        # Measure performance
        start_time = time.time()
        batch_size = 100

        for i in range(batch_size):
            result = validator.validate(f"performance_test_code_{i}")
            assert result["status"] == "valid"

        total_time = time.time() - start_time
        avg_time = total_time / batch_size

        # Performance assertions
        assert avg_time < 0.1, f"Average validation time too high: {avg_time}s"
        assert total_time < 10, f"Total batch time too high: {total_time}s"

        # Verify cache would improve performance
        assert validator.cache.check.call_count == batch_size

    def test_end_to_end_security_scenario(self):
        """Test complete security scenario from detection to mitigation"""
        # Simulate a security vulnerability
        vulnerable_code = """
import pickle
import os

def load_user_data(data):
    # Dangerous deserialization
    return pickle.loads(data)

def execute_command(cmd):
    # Command injection
    os.system(cmd)
"""

        # Mock security-aware responses
        security_responses = [
            {
                "status": "rejected",
                "reasoning": "CRITICAL: Dangerous deserialization + command injection",
                "violations": ["pickle.loads", "os.system"],
                "severity": "CRITICAL"
            },
            {
                "code": """
import json
import subprocess
from typing import Optional, Dict, Any

def load_user_data safely(data: str) -> Optional[Dict[str, Any]]:
    \"\"\"Safely load user data using JSON.\"\"\"
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        return None

def execute_command safely(cmd: str) -> Optional[str]:
    \"\"\"Execute command safely using subprocess.\"\"\"
    try:
        result = subprocess.run(cmd.split(), capture_output=True, text=True)
        return result.stdout
    except Exception:
        return None
"""
            }
        ]

        # Create validator with security context
        validator = CanonValidator()
        validator.llm = Mock()
        validator.llm.generate_plan.side_effect = security_responses
        validator.embed_fn = Mock(return_value=[0.1] * 768)
        validator.cache = Mock()
        validator.cache.check = Mock(return_value=None)
        validator.pinecone = Mock()
        validator.pinecone.query = Mock(return_value={'matches': []})
        validator.pinecone.upsert = Mock()

        # Execute security scenario
        result = validator.validate(vulnerable_code, auto_repair=True)

        # Verify security response
        assert result["status"] == "repaired"
        assert "json.loads" in result["repaired_code"]
        assert "subprocess.run" in result["repaired_code"]
        assert "pickle.loads" not in result["repaired_code"]
        assert "os.system" not in result["repaired_code"]

        # Verify security was logged
        assert validator.pinecone.upsert.called


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

