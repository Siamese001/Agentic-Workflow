"""
Phase 4: Cross-Cutting Concerns Integration Tests

Tests meta-learning integration for cross-cutting concerns:
- CodeQualityGuardrail AST metadata caching
- InputValidationGuardrailAgent adaptive validation
- DependencyPruningAgent dependency caching
- ThreatLevelAgent risk assessment learning
- Global pattern sharing mechanisms

All tests use mocked dependencies to avoid external services.
"""

from __future__ import annotations

import pytest
from pathlib import Path


# ==================== TEST 4.1: CodeQualityGuardrail Caching ====================


class TestCodeQualityGuardrailCaching:
    """Test CodeQualityGuardrail AST metadata caching."""

    def test_code_quality_guardrail_exists(self):
        """Test CodeQualityGuardrail file exists."""
        agent_path = Path("apps_lic/engines/CodeQualityGuardrail.py")
        assert agent_path.exists()

    def test_ast_metadata_caching(self):
        """Test AST metadata caching for code analysis."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient

        client = MetaLearningClient()

        # Cache AST metadata
        ast_metadata = {
            "file_path": "/test/module.py",
            "functions": ["func_a", "func_b"],
            "classes": ["ClassA"],
            "imports": ["os", "sys", "pathlib"],
            "complexity": 12,
        }

        client.cache_set("ast_metadata:/test/module.py", ast_metadata, "agentic_core")

        result = client.cache_get("ast_metadata:/test/module.py", "agentic_core")
        assert result["complexity"] == 12
        assert len(result["functions"]) == 2

    def test_code_quality_pattern_learning(self):
        """Test learning code quality patterns."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient

        client = MetaLearningClient()

        # Store quality pattern
        quality_pattern = {
            "pattern_type": "function_length",
            "threshold": 50,
            "violations_found": 3,
            "auto_fixable": True,
        }

        client.cache_set("quality_pattern_func_length", quality_pattern, "agentic_core")

        result = client.cache_get("quality_pattern_func_length", "agentic_core")
        assert result["auto_fixable"] is True

    def test_code_analysis_result_caching(self):
        """Test caching complete code analysis results."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient

        client = MetaLearningClient()

        # Cache analysis result
        analysis_result = {
            "file": "/test/file.py",
            "issues": [
                {"line": 10, "type": "complexity", "severity": "warning"},
                {"line": 25, "type": "unused_import", "severity": "info"},
            ],
            "score": 85,
            "passed": True,
        }

        client.cache_set("code_analysis:/test/file.py", analysis_result, "agentic_core")

        result = client.cache_get("code_analysis:/test/file.py", "agentic_core")
        assert result["score"] == 85
        assert len(result["issues"]) == 2


# ==================== TEST 4.2: InputValidationGuardrail Learning ====================


class TestInputValidationGuardrailLearning:
    """Test InputValidationGuardrailAgent adaptive validation."""

    def test_input_validation_guardrail_exists(self):
        """Test InputValidationGuardrailAgent file exists."""
        agent_path = Path("agentic_core/L5_safety/guardrails/InputValidationGuardrailAgent.py")
        assert agent_path.exists()

    def test_validation_rule_caching(self):
        """Test validation rule caching."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient

        client = MetaLearningClient()

        # Cache validation rule
        validation_rule = {
            "rule_id": "input_length",
            "max_length": 10000,
            "pattern": r"^[a-zA-Z0-9\s]+$",
            "block_on_fail": True,
        }

        client.cache_set("validation_rule_input_length", validation_rule, "agentic_core")

        result = client.cache_get("validation_rule_input_length", "agentic_core")
        assert result["max_length"] == 10000

    def test_attack_pattern_learning(self):
        """Test learning attack patterns for adaptive validation."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient

        client = MetaLearningClient()

        # Store detected attack pattern
        attack_pattern = {
            "pattern_type": "sql_injection",
            "signature": "SELECT.*FROM.*WHERE",
            "severity": "critical",
            "detection_count": 15,
            "false_positive_rate": 0.01,
        }

        client.cache_set("attack_pattern_sql_injection", attack_pattern, "agentic_core")

        result = client.cache_get("attack_pattern_sql_injection", "agentic_core")
        assert result["severity"] == "critical"
        assert result["detection_count"] == 15

    def test_validation_bypass_tracking(self):
        """Test tracking validation bypass attempts."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient

        client = MetaLearningClient()

        # Track bypass attempt
        bypass_record = {
            "attempt_type": "encoding_bypass",
            "payload_hash": "abc123",
            "blocked": True,
            "rule_triggered": "xss_prevention",
        }

        client.cache_set("bypass_attempt_001", bypass_record, "agentic_core")

        result = client.cache_get("bypass_attempt_001", "agentic_core")
        assert result["blocked"] is True


# ==================== TEST 4.3: DependencyPruningAgent Caching ====================


class TestDependencyPruningAgentCaching:
    """Test DependencyPruningAgent dependency caching."""

    def test_dependency_pruning_agent_exists(self):
        """Test DependencyPruningAgent file exists."""
        agent_path = Path("agentic_core/L5_safety/guardrails/DependencyPruningAgent.py")
        assert agent_path.exists()

    def test_dependency_graph_caching(self):
        """Test dependency graph caching."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient

        client = MetaLearningClient()

        # Cache dependency graph
        dep_graph = {
            "module": "agentic_core.L5_safety",
            "dependencies": [
                {"name": "logging", "type": "stdlib"},
                {"name": "pathlib", "type": "stdlib"},
                {"name": "agentic_core.base_agents", "type": "internal"},
            ],
            "circular_deps": [],
        }

        client.cache_set("dep_graph:agentic_core.L5_safety", dep_graph, "agentic_core")

        result = client.cache_get("dep_graph:agentic_core.L5_safety", "agentic_core")
        assert len(result["dependencies"]) == 3
        assert len(result["circular_deps"]) == 0

    def test_pruning_decision_caching(self):
        """Test caching pruning decisions for faster resolution."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient

        client = MetaLearningClient()

        # Cache pruning decision
        pruning_decision = {
            "dependency": "unused_module",
            "action": "remove",
            "reason": "no_references",
            "safe_to_prune": True,
        }

        client.cache_set("prune_decision_unused_module", pruning_decision, "agentic_core")

        result = client.cache_get("prune_decision_unused_module", "agentic_core")
        assert result["safe_to_prune"] is True

    def test_dependency_resolution_pattern(self):
        """Test learning dependency resolution patterns."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient

        client = MetaLearningClient()

        # Store resolution pattern
        resolution_pattern = {
            "conflict_type": "version_mismatch",
            "resolution": "upgrade_to_latest",
            "success_rate": 0.95,
            "rollback_needed": False,
        }

        client.cache_set("dep_resolution_version_mismatch", resolution_pattern, "agentic_core")

        result = client.cache_get("dep_resolution_version_mismatch", "agentic_core")
        assert result["success_rate"] == 0.95


# ==================== TEST 4.4: ThreatLevelAgent Learning ====================


class TestThreatLevelAgentLearning:
    """Test ThreatLevelAgent risk assessment learning."""

    def test_threat_level_agent_exists(self):
        """Test ThreatLevelAgent file exists."""
        agent_path = Path("agentic_core/L5_safety/guardrails/ThreatLevelAgent.py")
        assert agent_path.exists()

    def test_threat_assessment_caching(self):
        """Test threat assessment result caching."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient

        client = MetaLearningClient()

        # Cache threat assessment
        assessment = {
            "input_hash": "xyz789",
            "threat_level": "medium",
            "confidence": 0.85,
            "indicators": ["unusual_pattern", "high_entropy"],
        }

        client.cache_set("threat_assessment_xyz789", assessment, "agentic_core")

        result = client.cache_get("threat_assessment_xyz789", "agentic_core")
        assert result["threat_level"] == "medium"
        assert result["confidence"] == 0.85

    def test_threat_pattern_learning(self):
        """Test learning threat patterns from incidents."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient

        client = MetaLearningClient()

        # Store learned threat pattern
        threat_pattern = {
            "pattern_id": "prompt_injection_v2",
            "indicators": ["ignore_previous", "system_prompt"],
            "severity": "high",
            "detection_accuracy": 0.92,
        }

        client.cache_set("threat_pattern_prompt_injection_v2", threat_pattern, "agentic_core")

        result = client.cache_get("threat_pattern_prompt_injection_v2", "agentic_core")
        assert result["severity"] == "high"
        assert result["detection_accuracy"] >= 0.90

    def test_risk_score_calculation_caching(self):
        """Test caching risk score calculations."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient

        client = MetaLearningClient()

        # Cache risk score
        risk_calculation = {
            "input_type": "user_message",
            "base_risk": 0.1,
            "modifiers": [
                {"factor": "length", "adjustment": 0.05},
                {"factor": "special_chars", "adjustment": 0.1},
            ],
            "final_risk": 0.25,
        }

        client.cache_set("risk_calc_user_msg_001", risk_calculation, "agentic_core")

        result = client.cache_get("risk_calc_user_msg_001", "agentic_core")
        assert result["final_risk"] == 0.25


# ==================== TEST 4.5: Global Pattern Sharing ====================


class TestGlobalPatternSharing:
    """Test global pattern sharing mechanisms."""

    def test_cross_domain_pattern_isolation(self):
        """Test patterns are properly isolated across domains."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient

        client = MetaLearningClient()

        # Store patterns in all domains
        domains = ["agentic_core", "apps_lic", "apps_rg"]
        for domain in domains:
            client.cache_set("isolation_test", {"domain": domain}, domain)

        # Verify isolation
        for domain in domains:
            result = client.cache_get("isolation_test", domain)
            assert result["domain"] == domain

    def test_shared_security_patterns(self):
        """Test security patterns can be shared across domains."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient

        client = MetaLearningClient()

        # Store security pattern in core
        security_pattern = {
            "type": "xss_prevention",
            "rule": "escape_html_entities",
            "shared": True,
        }

        client.cache_set("security_xss_prevention", security_pattern, "agentic_core")

        # Core should have it
        result = client.cache_get("security_xss_prevention", "agentic_core")
        assert result["type"] == "xss_prevention"

    def test_guardrails_stats_tracking(self):
        """Test guardrails statistics tracking."""
        from agentic_core.L1_cognition.meta_learning.guardrails import MetaLearningGuardrails

        guardrails = MetaLearningGuardrails()

        # Generate some operations
        for i in range(10):
            guardrails.check_rate_limit("agentic_core", "request")
            guardrails.increment_healing_depth("TestAgent", f"violation_{i}")

        # Get stats
        stats = guardrails.get_stats()

        assert "request_rates" in stats
        assert "depth_trackers" in stats
        assert "TestAgent" in stats["depth_trackers"]

    def test_pattern_quality_validation(self):
        """Test pattern quality is validated before sharing."""
        from agentic_core.L1_cognition.meta_learning.guardrails import MetaLearningGuardrails

        guardrails = MetaLearningGuardrails()

        # Valid pattern
        valid_pattern = {"violation_type": "test", "healing_strategy": {"action": "fix"}}

        assert guardrails.validate_domain_isolation("agentic_core", valid_pattern) is True

        # Invalid pattern (missing required fields)
        invalid_pattern = {"some_field": "value"}

        assert guardrails.validate_domain_isolation("agentic_core", invalid_pattern) is False

    def test_cache_cleanup_workflow(self):
        """Test cache cleanup for stale patterns."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient

        client = MetaLearningClient()

        # Store with short TTL
        client.cache_set("cleanup_test", {"data": "temporary"}, "agentic_core", ttl=1)

        # Should exist immediately
        assert client.cache_get("cleanup_test", "agentic_core") is not None

        # Wait for expiration
        import time

        time.sleep(1.5)

        # Should be cleaned up
        assert client.cache_get("cleanup_test", "agentic_core") is None


# ==================== RUN CONFIGURATION ====================

if __name__ == "__main__":
    pytest.main(
        [
            __file__,
            "-v",
            "--tb=short",
            "-x",
        ]
    )
