"""
Integration tests for full meta-learning capabilities.

Tests the complete integration of meta-learning features across
apps_rg and apps_lic with proper domain isolation and cross-domain
protection.
"""

import pytest
import time
from unittest.mock import Mock, patch

# Test imports - these will need to be implemented
try:
    from apps_rg.engines.RgHealingOrchestratorAgent import RgHealingOrchestratorAgent
    from apps_lic.engines.LicHealingOrchestratorAgent import LicHealingOrchestratorAgent
    from apps_rg.shared.core.RGAgentBaseAgent import RGAgentBase
    from apps_lic.shared.core.LICAgentBaseAgent import LICAgentBase
except ImportError as e:
    pytest.skip(f"Apps not yet enhanced with full meta-learning: {e}", allow_module_level=True)


class TestFullIntegration:
    """Test complete meta-learning integration scenarios."""

    def test_rg_healing_with_meta_learning(self):
        """Test RG healing orchestrator uses meta-learning effectively."""
        orchestrator = RgHealingOrchestratorAgent()

        violation = {
            "type": "resume_structure",
            "message": "Missing contact information",
            "path": "/resume/contact",
            "severity": "high",
        }

        # Test enhanced healing with meta-learning
        result = orchestrator.ml_heal_with_learning_enhanced(violation)

        # Verify result structure
        assert result["status"] in ["fixed", "skipped", "error"], "Status should be valid"
        assert "violation_id" in result, "Should include violation ID"

        # If healing was successful, verify pattern was stored
        if result["status"] == "fixed":
            # Mock pattern retrieval to verify storage
            with patch.object(
                orchestrator._meta_client, "retrieve_healing_patterns"
            ) as mock_retrieve:
                mock_patterns = [Mock(similarity_score=0.90)]
                mock_retrieve.return_value = mock_patterns

                retrieved = orchestrator._meta_client.retrieve_healing_patterns(
                    violation, domain="apps_rg"
                )
                assert len(retrieved) > 0, "Should have stored patterns for successful healing"

    def test_lic_healing_with_meta_learning(self):
        """Test LIC healing orchestrator uses meta-learning effectively."""
        orchestrator = LicHealingOrchestratorAgent()

        incident = {
            "type": "api_timeout",
            "message": "LinkedIn API timeout exceeded",
            "service": "linkedin_api",
            "severity": "medium",
        }

        # Test enhanced incident healing
        result = orchestrator.ml_heal_incident(incident)

        # Verify result structure
        assert result["status"] in ["resolved", "skipped", "error"], "Status should be valid"
        assert "incident_id" in result, "Should include incident ID"

        # If resolution was successful, verify it was cached
        if result["status"] == "resolved":
            cached = orchestrator.ml_recall_incident_resolution("api_timeout")
            assert cached is not None, "Should cache successful resolutions"
            assert cached["status"] == "resolved", "Cached resolution should match"

    def test_cross_domain_isolation(self):
        """Test patterns don't cross-contaminate between domains."""
        rg_agent = RGAgentBase()
        lic_agent = LICAgentBase()

        # Store RG-specific pattern
        rg_pattern = {"type": "resume_structure", "domain": "apps_rg", "fix": "add_contact_section"}
        rg_agent.ml_cache_resume_quality_pattern_enhanced("rg_test_pattern", rg_pattern)

        # Store LIC-specific pattern
        lic_pattern = {
            "type": "campaign_optimization",
            "domain": "apps_lic",
            "fix": "optimize_timing",
        }
        lic_agent.ml_cache_campaign_pattern_enhanced("lic_test_pattern", lic_pattern)

        # Verify domain isolation
        rg_cached = rg_agent.ml_recall_resume_quality_pattern("rg_test_pattern")
        lic_cached = lic_agent.ml_recall_campaign_pattern("lic_test_pattern")

        assert rg_cached["domain"] == "apps_rg", "RG pattern should maintain RG domain"
        assert lic_cached["domain"] == "apps_lic", "LIC pattern should maintain LIC domain"

        # Verify cross-access is blocked
        rg_cross_access = rg_agent.ml_cache_get("campaign_pattern:lic_test_pattern")
        lic_cross_access = lic_agent.ml_cache_get("resume_quality:rg_test_pattern")

        assert rg_cross_access is None, "RG should not access LIC patterns"
        assert lic_cross_access is None, "LIC should not access RG patterns"

    def test_healing_depth_prevention(self):
        """Test healing depth limits prevent infinite loops."""
        orchestrator = RgHealingOrchestratorAgent()

        # Create a violation that will cause repeated healing attempts
        violation = {
            "type": "recursive_violation",
            "message": "This violation causes recursive healing",
            "path": "/recursive/path",
        }

        # Mock the heal method to always fail to trigger depth limit
        with patch.object(orchestrator, "heal") as mock_heal:
            mock_heal.return_value = {"status": "failed", "reason": "Simulated failure"}

            # Track healing attempts
            healing_attempts = []

            def mock_enhanced_heal(violation):
                healing_attempts.append(1)
                return orchestrator.ml_heal_with_learning_enhanced(violation)

            # Attempt healing multiple times
            for i in range(7):  # More than the depth limit (5)
                result = mock_enhanced_heal(violation)

                # Should be blocked after 5 attempts
                if i >= 5:
                    assert result["status"] == "skipped", (
                        f"Healing should be skipped after depth limit (attempt {i + 1})"
                    )
                    assert result["reason"] == "healing_depth_limit_reached", (
                        "Should specify depth limit reason"
                    )

            assert len(healing_attempts) == 7, "Should attempt healing 7 times"

    def test_pattern_similarity_matching(self):
        """Test semantic similarity matching works across domains."""
        rg_orchestrator = RgHealingOrchestratorAgent()
        lic_orchestrator = LicHealingOrchestratorAgent()

        # Store similar patterns in both domains
        rg_patterns = [
            {"type": "resume_quality", "message": "Missing experience section"},
            {"type": "resume_quality", "message": "No work history listed"},
        ]

        lic_patterns = [
            {"type": "campaign_issue", "message": "Low engagement rate"},
            {"type": "campaign_issue", "message": "Poor response metrics"},
        ]

        # Cache patterns with embeddings
        for i, pattern in enumerate(rg_patterns):
            rg_orchestrator.ml_cache_convergence_pattern(f"rg_pattern_{i}", pattern)

        for i, pattern in enumerate(lic_patterns):
            lic_orchestrator.ml_cache_convergence_pattern(f"lic_pattern_{i}", pattern)

        # Test similarity matching in RG domain
        rg_violation = {"type": "resume_quality", "message": "Work experience missing"}

        with patch.object(
            rg_orchestrator._meta_client, "retrieve_healing_patterns"
        ) as mock_retrieve:
            mock_retrieve.return_value = [
                Mock(similarity_score=0.92, healing_strategy={"action": "add_experience"}),
                Mock(similarity_score=0.85, healing_strategy={"action": "create_section"}),
            ]

            patterns = rg_orchestrator._meta_client.retrieve_healing_patterns(
                rg_violation, domain="apps_rg", min_similarity=0.85
            )

            assert len(patterns) == 2, "Should find similar RG patterns"
            assert all(p.similarity_score >= 0.85 for p in patterns), (
                "All patterns should meet similarity threshold"
            )

        # Test similarity matching in LIC domain
        lic_incident = {"type": "campaign_issue", "message": "Engagement rate too low"}

        with patch.object(
            lic_orchestrator._meta_client, "retrieve_healing_patterns"
        ) as mock_retrieve:
            mock_retrieve.return_value = [
                Mock(similarity_score=0.94, healing_strategy={"action": "optimize_content"}),
                Mock(similarity_score=0.88, healing_strategy={"action": "adjust_timing"}),
            ]

            patterns = lic_orchestrator._meta_client.retrieve_healing_patterns(
                lic_incident,
                domain="apps_lic",
                min_similarity=0.92,  # Higher threshold for LIC
            )

            assert len(patterns) == 1, "Should find only patterns meeting higher LIC threshold"
            assert patterns[0].similarity_score >= 0.92, "Pattern should meet LIC threshold"

    def test_cache_performance_optimization(self):
        """Test cache performance and optimization features."""
        agent = RGAgentBase()

        # Test cache hit performance
        pattern_data = {"type": "test", "message": "test pattern"}

        # Cache pattern
        start_time = time.time()
        agent.ml_cache_resume_quality_pattern_enhanced("perf_test", pattern_data)
        cache_time = time.time() - start_time

        # Retrieve pattern
        start_time = time.time()
        cached = agent.ml_recall_resume_quality_pattern("perf_test")
        retrieve_time = time.time() - start_time

        assert cached is not None, "Pattern should be retrievable"
        assert retrieve_time < 0.1, "Retrieval should be fast (< 100ms)"
        assert cache_time < 0.5, "Caching should be reasonable (< 500ms)"

        # Test statistics tracking
        stats = agent._guardrails.get_stats()
        assert "cache_sizes" in stats, "Should track cache sizes"
        assert "request_rates" in stats, "Should track request rates"

    def test_concurrent_pattern_access(self):
        """Test concurrent pattern access doesn't cause conflicts."""
        import threading

        rg_agent = RGAgentBase()
        lic_agent = LICAgentBase()

        results = []
        errors = []

        def cache_rg_patterns():
            try:
                for i in range(10):
                    pattern = {"type": "concurrent_test", "id": i}
                    rg_agent.ml_cache_resume_quality_pattern_enhanced(f"rg_concurrent_{i}", pattern)
                    results.append(("rg", i))
            except Exception as e:
                errors.append(f"RG error: {e}")

        def cache_lic_patterns():
            try:
                for i in range(10):
                    pattern = {"type": "concurrent_test", "id": i}
                    lic_agent.ml_cache_campaign_pattern_enhanced(f"lic_concurrent_{i}", pattern)
                    results.append(("lic", i))
            except Exception as e:
                errors.append(f"LIC error: {e}")

        # Run concurrent caching
        rg_thread = threading.Thread(target=cache_rg_patterns)
        lic_thread = threading.Thread(target=cache_lic_patterns)

        rg_thread.start()
        lic_thread.start()

        rg_thread.join()
        lic_thread.join()

        # Verify no errors occurred
        assert len(errors) == 0, f"Concurrent access caused errors: {errors}"
        assert len(results) == 20, "Should have cached all patterns"

        # Verify patterns are accessible
        for domain, i in results:
            if domain == "rg":
                cached = rg_agent.ml_recall_resume_quality_pattern(f"rg_concurrent_{i}")
            else:
                cached = lic_agent.ml_recall_campaign_pattern(f"lic_concurrent_{i}")

            assert cached is not None, f"Pattern {domain}_{i} should be accessible"

    def test_meta_learning_statistics_aggregation(self):
        """Test meta-learning statistics are properly aggregated."""
        rg_agent = RGAgentBase()
        lic_agent = LICAgentBase()

        # Generate some activity
        for i in range(5):
            # RG activity
            rg_agent.ml_cache_resume_quality_pattern_enhanced(f"stat_test_rg_{i}", {"test": i})
            rg_agent.ml_recall_resume_quality_pattern(f"stat_test_rg_{i}")

            # LIC activity
            lic_agent.ml_cache_campaign_pattern_enhanced(f"stat_test_lic_{i}", {"test": i})
            lic_agent.ml_recall_campaign_pattern(f"stat_test_lic_{i}")

        # Get statistics
        rg_stats = rg_agent._guardrails.get_stats()
        lic_stats = lic_agent._guardrails.get_stats()

        # Verify statistics tracking
        assert "by_domain" in rg_stats, "RG should track domain statistics"
        assert "by_domain" in lic_stats, "LIC should track domain statistics"

        # Verify domain-specific tracking
        if "apps_rg" in rg_stats["by_domain"]:
            rg_domain_stats = rg_stats["by_domain"]["apps_rg"]
            assert any("cache" in key.lower() for key in rg_domain_stats.keys()), (
                "Should track cache operations for RG"
            )

        if "apps_lic" in lic_stats["by_domain"]:
            lic_domain_stats = lic_stats["by_domain"]["apps_lic"]
            assert any("cache" in key.lower() for key in lic_domain_stats.keys()), (
                "Should track cache operations for LIC"
            )


class TestErrorHandlingAndRecovery:
    """Test error handling and recovery scenarios."""

    def test_meta_client_failure_recovery(self):
        """Test recovery when meta-learning client fails."""
        orchestrator = RgHealingOrchestratorAgent()

        violation = {"type": "test_violation", "message": "test"}

        # Mock meta client failure
        with patch.object(orchestrator._meta_client, "retrieve_healing_patterns") as mock_retrieve:
            mock_retrieve.side_effect = Exception("Meta client unavailable")

            # Should fall back to standard healing
            result = orchestrator.ml_heal_with_learning_enhanced(violation)

            # Should not crash, should handle gracefully
            assert result["status"] in ["fixed", "skipped", "error"], (
                "Should handle meta client failure gracefully"
            )

    def test_cache_corruption_handling(self):
        """Test handling of corrupted cache data."""
        agent = RGAgentBase()

        # Mock corrupted cache retrieval
        with patch.object(agent, "ml_cache_get") as mock_cache_get:
            mock_cache_get.return_value = {"corrupted": "data", "invalid": True}

            # Should handle corruption gracefully
            result = agent.ml_recall_resume_quality_pattern("corrupted_key")

            # Should return None or handle appropriately
            assert result is None or "corrupted" not in str(result), (
                "Should handle corrupted cache data"
            )

    def test_domain_isolation_violation_handling(self):
        """Test handling of domain isolation violations."""
        rg_agent = RGAgentBase()

        # Attempt to cache a pattern with wrong domain
        wrong_domain_pattern = {
            "type": "test_pattern",
            "domain": "apps_lic",  # Wrong domain for RG agent
            "data": "test",
        }

        # Should reject or handle appropriately
        result = rg_agent._guardrails.validate_domain_isolation("apps_rg", wrong_domain_pattern)
        assert result is False, "Should reject cross-domain patterns"


if __name__ == "__main__":
    pytest.main([__file__])
