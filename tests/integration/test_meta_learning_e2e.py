"""
Meta-Learning E2E and Integration Tests

End-to-end tests for the complete meta-learning system:
- Full healing workflow with pattern recall and storage
- Cross-component integration
- Domain isolation verification
- Production-like scenarios

All tests validate the complete system integration.
"""

from __future__ import annotations

import time
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch


# ==================== E2E TEST 1: Complete Healing Workflow ====================

class TestCompleteHealingWorkflow:
    """End-to-end tests for complete healing workflows."""

    def test_gravity_violation_heal_cycle(self):
        """Test complete gravity violation healing cycle."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient
        from agentic_core.L1_cognition.meta_learning.guardrails import MetaLearningGuardrails
        
        client = MetaLearningClient()
        guardrails = MetaLearningGuardrails()
        
        # Step 1: Detect violation
        violation = {
            "type": "gravity_violation",
            "path": "/agentic_core/L5_safety/test_file.py",
            "import_statement": "from agentic_core.L0_maintenance import util",
            "file_layer": "L5",
            "import_layer": "L0"
        }
        
        # Step 2: Sanitize violation data
        sanitized = guardrails.sanitize_violation_data(violation)
        assert "type" in sanitized
        assert "path" in sanitized
        
        # Step 3: Check healing depth
        violation_id = f"v_{hash(str(sanitized)) % 10000}"
        assert guardrails.check_healing_depth("GravityAgent", violation_id) is True
        guardrails.increment_healing_depth("GravityAgent", violation_id)
        
        # Step 4: Check for cached pattern
        cache_key = f"gravity_heal:{sanitized['type']}:{sanitized['path'].replace('/', '_')}"
        cached_pattern = client.cache_get(cache_key, "agentic_core")
        
        # Step 5: Execute healing (simulated)
        healing_result = {
            "status": "fixed",
            "fix_type": "RELOCATE",
            "new_import": "from apps_shared.utils import util",
            "violations_fixed": 1
        }
        
        # Step 6: Store successful pattern
        client.cache_set(cache_key, healing_result, "agentic_core", ttl=3600)
        
        # Step 7: Reset depth on success
        guardrails.reset_healing_depth("GravityAgent", violation_id)
        
        # Step 8: Verify pattern stored
        stored = client.cache_get(cache_key, "agentic_core")
        assert stored["status"] == "fixed"
        
        # Step 9: Verify depth reset
        assert guardrails.check_healing_depth("GravityAgent", violation_id) is True

    def test_validation_caching_workflow(self):
        """Test complete validation result caching workflow."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient
        
        client = MetaLearningClient()
        
        # Step 1: Create validation input
        resume = {"experience": ["Software Engineer"], "skills": ["Python", "SQL"]}
        job_desc = "Looking for software engineer with Python skills"
        
        # Step 2: Generate cache key
        resume_sig = str(hash(str(resume)) % 10000)
        job_sig = str(hash(job_desc[:100]) % 10000)
        cache_key = f"validation:{resume_sig}:{job_sig}"
        
        # Step 3: Check cache first
        cached = client.cache_get(cache_key, "apps_rg")
        
        if cached is None:
            # Step 4: Perform validation (simulated)
            validation_result = {
                "passed": True,
                "score": 0.85,
                "issues": [],
                "timestamp": time.time()
            }
            
            # Step 5: Cache result
            client.cache_set(cache_key, validation_result, "apps_rg", ttl=1800)
        
        # Step 6: Verify cached
        result = client.cache_get(cache_key, "apps_rg")
        assert result is not None
        assert result["passed"] is True

    def test_multi_domain_healing_workflow(self):
        """Test healing workflow across multiple domains."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient
        from agentic_core.L1_cognition.meta_learning.guardrails import MetaLearningGuardrails
        
        client = MetaLearningClient()
        guardrails = MetaLearningGuardrails()
        
        domains = ["agentic_core", "apps_lic", "apps_rg"]
        
        for domain in domains:
            # Step 1: Create domain-specific violation
            violation = {
                "type": f"{domain}_violation",
                "path": f"/{domain}/module.py",
                "severity": "medium"
            }
            
            # Step 2: Sanitize
            sanitized = guardrails.sanitize_violation_data(violation)
            
            # Step 3: Check depth
            vid = f"v_{domain}"
            assert guardrails.check_healing_depth(f"Agent_{domain}", vid) is True
            guardrails.increment_healing_depth(f"Agent_{domain}", vid)
            
            # Step 4: Store healing result
            result = {"status": "fixed", "domain": domain}
            client.cache_set(f"heal_{domain}", result, domain)
            
            # Step 5: Reset depth
            guardrails.reset_healing_depth(f"Agent_{domain}", vid)
        
        # Verify domain isolation
        for domain in domains:
            result = client.cache_get(f"heal_{domain}", domain)
            assert result["domain"] == domain
            
            # Should not exist in other domains
            for other in domains:
                if other != domain:
                    cross = client.cache_get(f"heal_{domain}", other)
                    assert cross is None


# ==================== E2E TEST 2: Pattern Learning Cycle ====================

class TestPatternLearningCycle:
    """Test complete pattern learning and recall cycles."""

    def test_learn_and_recall_pattern(self):
        """Test learning a pattern and recalling it for similar violations."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient
        
        client = MetaLearningClient()
        
        # Step 1: First violation - no pattern exists
        violation1 = {
            "type": "import_violation",
            "pattern": "circular_dependency",
            "files": ["a.py", "b.py"]
        }
        
        # Step 2: Heal and store pattern
        healing1 = {
            "status": "fixed",
            "strategy": "extract_interface",
            "success": True
        }
        
        pattern_key = "pattern:import_violation:circular_dependency"
        client.cache_set(pattern_key, healing1, "agentic_core")
        
        # Step 3: Similar violation occurs
        violation2 = {
            "type": "import_violation",
            "pattern": "circular_dependency",
            "files": ["c.py", "d.py"]
        }
        
        # Step 4: Recall pattern
        recalled = client.cache_get(pattern_key, "agentic_core")
        
        # Step 5: Apply recalled pattern
        assert recalled is not None
        assert recalled["strategy"] == "extract_interface"

    def test_pattern_quality_evolution(self):
        """Test pattern quality improves with successful uses."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient
        
        client = MetaLearningClient()
        
        # Initial pattern
        pattern = {
            "strategy": "relocate",
            "success_count": 1,
            "failure_count": 0,
            "quality_score": 1.0
        }
        
        client.cache_set("evolving_pattern", pattern, "agentic_core")
        
        # Simulate successful uses
        for i in range(5):
            current = client.cache_get("evolving_pattern", "agentic_core")
            current["success_count"] += 1
            current["quality_score"] = current["success_count"] / (current["success_count"] + current["failure_count"])
            client.cache_set("evolving_pattern", current, "agentic_core")
        
        # Verify evolution
        final = client.cache_get("evolving_pattern", "agentic_core")
        assert final["success_count"] == 6
        assert final["quality_score"] == 1.0


# ==================== E2E TEST 3: System Integration ====================

class TestSystemIntegration:
    """Test integration between all system components."""

    def test_client_guardrails_integration(self):
        """Test MetaLearningClient and Guardrails work together."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient
        from agentic_core.L1_cognition.meta_learning.guardrails import MetaLearningGuardrails
        
        client = MetaLearningClient()
        guardrails = MetaLearningGuardrails()
        
        # Validate key before using client
        test_key = "integration_test_key"
        assert guardrails.validate_cache_key(test_key) is True
        
        # Validate value before storing
        test_value = {"data": "integration_test"}
        assert guardrails.validate_cache_value(test_value) is True
        
        # Store with validated TTL
        ttl = guardrails.validate_ttl(3600)
        client.cache_set(test_key, test_value, "agentic_core", ttl=ttl)
        
        # Verify stored
        result = client.cache_get(test_key, "agentic_core")
        assert result == test_value

    def test_mixin_client_integration(self):
        """Test MetaLearningClientMixin integrates with client."""
        from agentic_core.base_agents.meta_learning_client_mixin import MetaLearningClientMixin
        
        class TestAgent(MetaLearningClientMixin):
            pass
        
        agent = TestAgent()
        
        # Domain detection works
        domain = agent._get_ml_domain()
        assert domain in ["agentic_core", "apps_lic", "apps_rg"]

    def test_cache_strategy_manager_integration(self):
        """Test CacheStrategyManager integrates correctly."""
        from agentic_core.L1_cognition.meta_learning.CacheStrategyManager import (
            CacheStrategyManager,
            DomainConfig,
        )
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient
        
        csm = CacheStrategyManager()
        client = MetaLearningClient()
        
        # Configure domain
        csm.domain_configs["integration_domain"] = DomainConfig(
            domain="integration_domain",
            ttl_seconds=1800
        )
        
        # Use TTL from strategy manager
        ttl = csm.get_ttl("integration_domain")
        client.cache_set("csm_test", {"data": "value"}, "agentic_core", ttl=ttl)
        
        # Verify
        result = client.cache_get("csm_test", "agentic_core")
        assert result is not None

    def test_all_components_healthy(self):
        """Test all components initialize and operate correctly."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import (
            MetaLearningClient,
            get_meta_learning_client,
        )
        from agentic_core.L1_cognition.meta_learning.guardrails import (
            MetaLearningGuardrails,
            get_guardrails,
        )
        from agentic_core.L1_cognition.meta_learning.CacheStrategyManager import (
            CacheStrategyManager,
            get_cache_strategy_manager,
        )
        from agentic_core.base_agents.meta_learning_client_mixin import MetaLearningClientMixin
        
        # All singletons accessible
        client = get_meta_learning_client()
        guardrails = get_guardrails()
        csm = get_cache_strategy_manager()
        
        assert client is not None
        assert guardrails is not None
        assert csm is not None
        
        # Mixin available
        assert hasattr(MetaLearningClientMixin, 'ml_cache_get')


# ==================== E2E TEST 4: Error Recovery ====================

class TestErrorRecovery:
    """Test system recovery from errors."""

    def test_recovery_from_invalid_key(self):
        """Test system handles invalid cache keys gracefully."""
        from agentic_core.L1_cognition.meta_learning.guardrails import MetaLearningGuardrails
        
        guardrails = MetaLearningGuardrails()
        
        invalid_keys = ["", None, "../etc/passwd", "key with spaces"]
        
        for key in invalid_keys:
            result = guardrails.validate_cache_key(key)
            assert result is False

    def test_recovery_from_oversized_value(self):
        """Test system handles oversized values gracefully."""
        from agentic_core.L1_cognition.meta_learning.guardrails import MetaLearningGuardrails
        
        guardrails = MetaLearningGuardrails()
        
        # Create oversized value (> 100KB)
        large_value = {"data": "x" * (101 * 1024)}
        
        result = guardrails.validate_cache_value(large_value)
        assert result is False

    def test_recovery_from_depth_limit(self):
        """Test system handles depth limit correctly."""
        from agentic_core.L1_cognition.meta_learning.guardrails import MetaLearningGuardrails
        
        guardrails = MetaLearningGuardrails()
        
        # Hit depth limit
        for i in range(5):
            guardrails.increment_healing_depth("RecoveryAgent", "deep_v")
        
        # Should be blocked
        assert guardrails.check_healing_depth("RecoveryAgent", "deep_v") is False
        
        # Reset should restore
        guardrails.reset_healing_depth("RecoveryAgent", "deep_v")
        assert guardrails.check_healing_depth("RecoveryAgent", "deep_v") is True

    def test_ttl_expiration_recovery(self):
        """Test system handles expired entries correctly."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient
        
        client = MetaLearningClient()
        
        # Store with very short TTL
        client.cache_set("expire_test", {"data": "temp"}, "agentic_core", ttl=1)
        
        # Should exist
        assert client.cache_get("expire_test", "agentic_core") is not None
        
        # Wait for expiration
        time.sleep(1.5)
        
        # Should gracefully return None
        result = client.cache_get("expire_test", "agentic_core")
        assert result is None


# ==================== E2E TEST 5: Performance Benchmarks ====================

class TestPerformanceBenchmarks:
    """Test performance meets requirements."""

    def test_cache_write_performance(self):
        """Test cache write operations meet performance targets."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient
        
        client = MetaLearningClient()
        
        start = time.time()
        
        for i in range(100):
            client.cache_set(f"perf_write_{i}", {"i": i, "data": "x" * 100}, "agentic_core")
        
        elapsed = time.time() - start
        
        # Should complete 100 writes in < 2 seconds
        assert elapsed < 2.0

    def test_cache_read_performance(self):
        """Test cache read operations meet performance targets."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient
        
        client = MetaLearningClient()
        
        # Setup
        for i in range(100):
            client.cache_set(f"perf_read_{i}", {"i": i}, "agentic_core")
        
        start = time.time()
        
        for i in range(100):
            client.cache_get(f"perf_read_{i}", "agentic_core")
        
        elapsed = time.time() - start
        
        # Should complete 100 reads in < 1 second
        assert elapsed < 1.0

    def test_guardrails_validation_performance(self):
        """Test guardrails validation meets performance targets."""
        from agentic_core.L1_cognition.meta_learning.guardrails import MetaLearningGuardrails
        
        guardrails = MetaLearningGuardrails()
        
        start = time.time()
        
        for i in range(1000):
            guardrails.validate_cache_key(f"perf_key_{i}")
            guardrails.validate_ttl(3600)
            guardrails.check_rate_limit("perf_domain", "request")
        
        elapsed = time.time() - start
        
        # Should complete 3000 validations in < 2 seconds
        assert elapsed < 2.0

    def test_concurrent_operations_performance(self):
        """Test concurrent operations meet performance targets."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient
        
        client = MetaLearningClient()
        
        domains = ["agentic_core", "apps_lic", "apps_rg"]
        
        start = time.time()
        
        # Concurrent-like operations across domains
        for i in range(50):
            for domain in domains:
                client.cache_set(f"concurrent_{i}", {"domain": domain}, domain)
                client.cache_get(f"concurrent_{i}", domain)
        
        elapsed = time.time() - start
        
        # Should complete 300 operations in < 3 seconds
        assert elapsed < 3.0


# ==================== E2E TEST 6: Production Scenarios ====================

class TestProductionScenarios:
    """Test production-like scenarios."""

    def test_healing_loop_prevention(self):
        """Test healing loop is prevented in production scenario."""
        from agentic_core.L1_cognition.meta_learning.guardrails import MetaLearningGuardrails
        
        guardrails = MetaLearningGuardrails()
        
        # Simulate recursive healing attempts
        heals_attempted = 0
        max_attempts = 10
        
        for i in range(max_attempts):
            if guardrails.check_healing_depth("LoopAgent", "recurring_violation"):
                guardrails.increment_healing_depth("LoopAgent", "recurring_violation")
                heals_attempted += 1
            else:
                break
        
        # Should have stopped at 5 (max depth)
        assert heals_attempted == 5

    def test_cache_under_memory_pressure(self):
        """Test cache behavior under simulated memory pressure."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient
        
        client = MetaLearningClient()
        
        # Store many entries
        for i in range(200):
            client.cache_set(f"pressure_key_{i}", {"data": "x" * 500}, "agentic_core")
        
        # Should still function
        result = client.cache_get("pressure_key_100", "agentic_core")
        assert result is not None

    def test_domain_specific_workflows(self):
        """Test domain-specific workflows work correctly."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient
        
        client = MetaLearningClient()
        
        # LIC workflow - outreach compliance
        lic_data = {
            "type": "outreach_message",
            "compliance_score": 0.95,
            "approved": True
        }
        client.cache_set("lic_outreach_1", lic_data, "apps_lic")
        
        # RG workflow - resume validation  
        rg_data = {
            "type": "resume_validation",
            "ats_score": 0.88,
            "passed": True
        }
        client.cache_set("rg_resume_1", rg_data, "apps_rg")
        
        # Core workflow - structural validation
        core_data = {
            "type": "structure_check",
            "violations": 0,
            "healthy": True
        }
        client.cache_set("core_structure_1", core_data, "agentic_core")
        
        # Verify isolation
        assert client.cache_get("lic_outreach_1", "apps_lic")["type"] == "outreach_message"
        assert client.cache_get("rg_resume_1", "apps_rg")["type"] == "resume_validation"
        assert client.cache_get("core_structure_1", "agentic_core")["type"] == "structure_check"


# ==================== RUN CONFIGURATION ====================

if __name__ == "__main__":
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-x",
    ])
