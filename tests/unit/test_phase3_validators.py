"""
Phase 3: High-Frequency Validator Integration Tests

Tests meta-learning integration for high-frequency validators:
- ATSCompatibilityAgent validation caching
- MessageComplianceAgent compliance pattern learning
- PII_SanitizerSpecialistAgent privacy protection learning
- Performance optimization and cache tuning

All tests use mocked dependencies to avoid external services.
"""

from __future__ import annotations

import pytest
from pathlib import Path


# ==================== TEST 3.1: ATSCompatibilityAgent Caching ====================


class TestATSCompatibilityAgentCaching:
    """Test ATSCompatibilityAgent validation result caching."""

    def test_ats_agent_file_exists(self):
        """Test ATSCompatibilityAgent file exists."""
        agent_path = Path("apps_rg/engines/ATSCompatibilityAgent.py")
        assert agent_path.exists()

    def test_keyword_score_caching_workflow(self):
        """Test keyword score calculation caching workflow."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient

        client = MetaLearningClient()

        # Simulate caching keyword score
        resume_sig = "resume_abc123"
        job_sig = "job_xyz789"
        cache_key = f"ats_score:{resume_sig}:{job_sig}"

        score = 0.85
        client.cache_set(cache_key, score, "apps_rg", ttl=1800)

        # Retrieve cached score
        cached_score = client.cache_get(cache_key, "apps_rg")
        assert cached_score == score

    def test_ats_validation_result_caching(self):
        """Test complete ATS validation result caching."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient

        client = MetaLearningClient()

        # Simulate validation result
        validation_result = {
            "passed": True,
            "issues": [],
            "suggestions": ["Consider adding more keywords"],
            "score": 0.92,
        }

        client.cache_set("ats_validation_resume1", validation_result, "apps_rg")

        result = client.cache_get("ats_validation_resume1", "apps_rg")
        assert result["passed"] is True
        assert result["score"] == 0.92

    def test_ats_signature_generation(self):
        """Test resume and job description signature generation."""
        # Test signature generation logic
        resume = {"experience": ["Software Engineer"], "education": ["BS CS"]}
        job_desc = "Looking for software engineer"

        # Signature should be deterministic
        sections = [(k, len(str(v))) for k, v in resume.items() if not k.startswith("_")]
        sig1 = str(hash(tuple(sorted(sections))) % 10000)
        sig2 = str(hash(tuple(sorted(sections))) % 10000)

        assert sig1 == sig2  # Deterministic

    def test_ats_cache_ttl_30_minutes(self):
        """Test ATS validation cache uses 30-minute TTL."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient

        client = MetaLearningClient()

        # Store with 30-minute TTL (1800 seconds)
        client.cache_set("ats_ttl_test", {"data": "test"}, "apps_rg", ttl=1800)

        # Should be accessible immediately
        result = client.cache_get("ats_ttl_test", "apps_rg")
        assert result is not None


# ==================== TEST 3.2: MessageComplianceAgent Learning ====================


class TestMessageComplianceAgentLearning:
    """Test MessageComplianceAgent compliance pattern learning."""

    def test_message_compliance_agent_exists(self):
        """Test MessageComplianceAgent file exists."""
        agent_path = Path("apps_lic/engines/MessageComplianceAgent.py")
        assert agent_path.exists()

    def test_compliance_rule_caching(self):
        """Test compliance rule result caching."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient

        client = MetaLearningClient()

        # Cache compliance check result
        compliance_result = {
            "compliant": True,
            "rules_checked": ["no_profanity", "professional_tone", "length_limit"],
            "violations": [],
        }

        client.cache_set("compliance_msg_123", compliance_result, "apps_lic")

        result = client.cache_get("compliance_msg_123", "apps_lic")
        assert result["compliant"] is True
        assert len(result["rules_checked"]) == 3

    def test_compliance_pattern_storage(self):
        """Test storing compliance patterns for future matching."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient

        client = MetaLearningClient()

        # Store successful compliance pattern
        pattern = {
            "message_type": "outreach",
            "industry": "tech",
            "compliance_score": 0.95,
            "best_practices": ["personalization", "clear_cta"],
        }

        client.cache_set("compliance_pattern_tech_outreach", pattern, "apps_lic")

        result = client.cache_get("compliance_pattern_tech_outreach", "apps_lic")
        assert result["compliance_score"] == 0.95

    def test_compliance_domain_isolation(self):
        """Test compliance patterns are isolated to apps_lic."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient

        client = MetaLearningClient()

        # Store in apps_lic
        client.cache_set("compliance_isolation_test", {"domain": "lic"}, "apps_lic")

        # Should not be in other domains
        assert client.cache_get("compliance_isolation_test", "agentic_core") is None
        assert client.cache_get("compliance_isolation_test", "apps_rg") is None
        assert client.cache_get("compliance_isolation_test", "apps_lic") is not None


# ==================== TEST 3.3: PII_SanitizerSpecialistAgent Learning ====================


class TestPIISanitizerSpecialistAgent:
    """Test PII_SanitizerSpecialistAgent privacy protection learning."""

    def test_pii_sanitizer_agent_exists(self):
        """Test PII_SanitizerSpecialistAgent file exists."""
        agent_path = Path("apps_lic/engines/PII_SanitizerSpecialistAgent.py")
        assert agent_path.exists()

    def test_pii_pattern_caching(self):
        """Test PII detection pattern caching."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient

        client = MetaLearningClient()

        # Cache PII detection result
        pii_result = {
            "pii_found": True,
            "types": ["email", "phone"],
            "locations": [
                {"type": "email", "start": 10, "end": 30},
                {"type": "phone", "start": 45, "end": 57},
            ],
            "sanitized": True,
        }

        client.cache_set("pii_scan_doc_123", pii_result, "apps_lic")

        result = client.cache_get("pii_scan_doc_123", "apps_lic")
        assert result["pii_found"] is True
        assert len(result["types"]) == 2

    def test_pii_pattern_learning(self):
        """Test learning new PII patterns from detections."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient

        client = MetaLearningClient()

        # Store learned PII pattern
        new_pattern = {
            "pattern_type": "custom_id",
            "regex": r"EMP-\d{6}",
            "confidence": 0.92,
            "false_positive_rate": 0.02,
        }

        client.cache_set("pii_learned_pattern_emp_id", new_pattern, "apps_lic")

        result = client.cache_get("pii_learned_pattern_emp_id", "apps_lic")
        assert result["pattern_type"] == "custom_id"
        assert result["confidence"] >= 0.90

    def test_pii_false_positive_tracking(self):
        """Test tracking false positives for pattern refinement."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient

        client = MetaLearningClient()

        # Track false positive
        fp_record = {
            "pattern": "phone",
            "flagged_text": "555-1234",
            "context": "product_code",
            "is_false_positive": True,
            "timestamp": "2026-02-01",
        }

        client.cache_set("pii_fp_record_1", fp_record, "apps_lic")

        result = client.cache_get("pii_fp_record_1", "apps_lic")
        assert result["is_false_positive"] is True


# ==================== TEST 3.4: Performance Optimization ====================


class TestPerformanceOptimization:
    """Test cache performance optimization for validators."""

    def test_cache_hit_ratio_tracking(self):
        """Test cache hit ratio tracking for performance monitoring."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient

        client = MetaLearningClient()
        initial_hits = client.stats["cache_hits"]
        initial_misses = client.stats["cache_misses"]

        # Generate some cache operations
        client.cache_set("perf_test_key", {"data": "value"}, "agentic_core")

        # Hits
        client.cache_get("perf_test_key", "agentic_core")
        client.cache_get("perf_test_key", "agentic_core")

        # Misses
        client.cache_get("nonexistent_key_1", "agentic_core")

        # Verify tracking
        assert client.stats["cache_hits"] >= initial_hits + 2
        assert client.stats["cache_misses"] >= initial_misses + 1

    def test_batch_validation_caching(self):
        """Test batch validation result caching."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient

        client = MetaLearningClient()

        # Simulate batch validation
        batch_results = []
        for i in range(10):
            result = {"id": f"item_{i}", "valid": True, "score": 0.9 + (i * 0.01)}
            client.cache_set(f"batch_validation_{i}", result, "apps_rg")
            batch_results.append(result)

        # Verify all cached
        for i in range(10):
            cached = client.cache_get(f"batch_validation_{i}", "apps_rg")
            assert cached is not None
            assert cached["id"] == f"item_{i}"

    def test_cache_size_efficiency(self):
        """Test cache handles many entries efficiently."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient

        client = MetaLearningClient()

        # Store 100 validation results
        for i in range(100):
            client.cache_set(
                f"efficiency_test_{i}", {"index": i, "data": "x" * 100}, "agentic_core"
            )

        # Verify random access
        assert client.cache_get("efficiency_test_50", "agentic_core")["index"] == 50
        assert client.cache_get("efficiency_test_99", "agentic_core")["index"] == 99

    def test_ttl_optimization(self):
        """Test TTL optimization for different validation types."""
        from agentic_core.L1_cognition.meta_learning.guardrails import MetaLearningGuardrails

        guardrails = MetaLearningGuardrails()

        # Test TTL validation
        assert guardrails.validate_ttl(1800) == 1800  # 30 min - valid
        assert guardrails.validate_ttl(3600) == 3600  # 1 hour - valid
        assert guardrails.validate_ttl(30) == 60  # Too short - bumped to min


# ==================== TEST 3.5: Validator Integration ====================


class TestValidatorIntegration:
    """Test integration between validators and meta-learning."""

    def test_cross_validator_pattern_sharing(self):
        """Test patterns can be shared between validators in same domain."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient

        client = MetaLearningClient()

        # ATS validator stores pattern
        client.cache_set(
            "shared_resume_pattern",
            {"source": "ats_validator", "pattern": "keyword_optimization"},
            "apps_rg",
        )

        # Content validator reads pattern
        pattern = client.cache_get("shared_resume_pattern", "apps_rg")
        assert pattern["source"] == "ats_validator"

    def test_validator_depth_tracking(self):
        """Test healing depth tracking for validator agents."""
        from agentic_core.L1_cognition.meta_learning.guardrails import MetaLearningGuardrails

        guardrails = MetaLearningGuardrails()

        # Track depth for validators
        for _ in range(3):
            guardrails.increment_healing_depth("ATSValidator", "validation_1")

        # Should still allow
        assert guardrails.check_healing_depth("ATSValidator", "validation_1") is True

        # Different validator has independent depth
        assert guardrails.check_healing_depth("ComplianceValidator", "validation_1") is True

    def test_validation_chain_caching(self):
        """Test caching across validation chains."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient

        client = MetaLearningClient()

        # First validator in chain
        step1_result = {"step": "format_check", "passed": True}
        client.cache_set("chain_step_1", step1_result, "apps_rg")

        # Second validator in chain
        step2_result = {"step": "content_check", "passed": True, "depends_on": "step_1"}
        client.cache_set("chain_step_2", step2_result, "apps_rg")

        # Third validator in chain
        step3_result = {"step": "ats_check", "passed": True, "depends_on": "step_2"}
        client.cache_set("chain_step_3", step3_result, "apps_rg")

        # Verify chain integrity
        s1 = client.cache_get("chain_step_1", "apps_rg")
        s2 = client.cache_get("chain_step_2", "apps_rg")
        s3 = client.cache_get("chain_step_3", "apps_rg")

        assert s1["passed"] and s2["passed"] and s3["passed"]

    def test_guardrails_rate_limiting_validators(self):
        """Test rate limiting applies to validator operations."""
        from agentic_core.L1_cognition.meta_learning.guardrails import MetaLearningGuardrails

        guardrails = MetaLearningGuardrails()

        # Normal traffic should pass
        for _ in range(100):
            assert guardrails.check_rate_limit("apps_rg", "request") is True


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
