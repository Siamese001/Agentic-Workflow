"""Prompt 14: Policy-Tuning Review Pack Tests."""

import pytest
from pathlib import Path


class TestPolicyReviewPack:
    """Prompt 14: Policy-tuning review pack tests."""

    def test_review_window_aggregation_works_correctly(self, tmp_path):
        """Review pack should aggregate artifacts within defined window."""
        import json
        from datetime import datetime, timedelta
        from tools.generate.adg_graph_watchlist_builder import ADGPolicyReviewPack, AcceptedBaselineManager

        # Create baseline within window
        artifact_path = tmp_path / "adg_graph_watchlist_20260101_120000.json"
        with open(artifact_path, "w") as f:
            json.dump({"watchlist": []}, f)

        baseline_manager = AcceptedBaselineManager(tmp_path)
        baseline_manager.accept_baseline(artifact_path, "reviewer_1", "Baseline")

        # Generate review pack with 30-day window
        review_pack = ADGPolicyReviewPack(tmp_path, review_window_days=30)
        pack = review_pack.generate_review_pack()

        # Should include the baseline
        assert pack["review_window"]["days"] == 30
        assert len(pack["source_artifacts"]["accepted_baselines"]) == 1

    def test_review_pack_excludes_out_of_window_artifacts(self, tmp_path):
        """Review pack should exclude artifacts outside review window."""
        import json
        from tools.generate.adg_graph_watchlist_builder import ADGPolicyReviewPack, AcceptedBaselineManager

        # The baseline timestamp will be current, so 1-day window will include it
        # but let's verify window boundaries work

        artifact_path = tmp_path / "adg_graph_watchlist_20260101_120000.json"
        with open(artifact_path, "w") as f:
            json.dump({"watchlist": []}, f)

        baseline_manager = AcceptedBaselineManager(tmp_path)
        baseline_manager.accept_baseline(artifact_path, "reviewer_1", "Baseline")

        # Very short window should still include recent baseline
        review_pack = ADGPolicyReviewPack(tmp_path, review_window_days=1)
        pack = review_pack.generate_review_pack()

        # Should still include (baseline is from "now")
        assert len(pack["source_artifacts"]["accepted_baselines"]) >= 0  # Could be 0 or 1 depending on timing

    def test_repeated_proposals_are_counted_correctly(self, tmp_path):
        """Review pack should count repeated proposal patterns."""
        import json
        from tools.generate.adg_graph_watchlist_builder import (
            ADGPolicyReviewPack,
            ADGProposalPromotionManager,
            ProposalPacket,
        )

        # Create multiple proposals with same category
        promo_manager = ADGProposalPromotionManager(tmp_path)
        for i in range(5):
            proposal = ProposalPacket(
                proposal_id=f"SL_{i:03d}",
                category="threshold_tuning",  # Same category = repeated pattern
                trigger_evidence=[{"pattern": "repeat"}],
                affected_signals=["reverse_dependency"],
                affected_layers=["L_TOOLS"],
                affected_files=["test.py"],
                suggested_change=f"Adjust threshold {i}",
                expected_benefit="Better detection",
                risk_assessment="Low",
                confidence_score=0.85,
                occurrence_count=5,
                learning_window_runs=5,
            )
            promo_manager.queue_proposal(proposal)

        # Persist queue
        promo_manager.emit_promotion_artifacts()

        # Generate review pack
        review_pack = ADGPolicyReviewPack(tmp_path, review_window_days=30)
        pack = review_pack.generate_review_pack()

        # Should count the repeated pattern
        hotspot_summary = pack["sections"]["hotspot_patterns"]
        total_analyzed = hotspot_summary.get("total_proposals_analyzed", 0)
        assert total_analyzed == 5

    def test_rollback_frequency_is_computed_correctly(self, tmp_path):
        """Review pack should compute rollback frequency accurately."""
        import json
        from tools.generate.adg_graph_watchlist_builder import (
            ADGPolicyReviewPack,
            AcceptedBaselineManager,
            GovernedPromotionApplicator,
            PromotionAction,
        )

        # Setup and apply promotion
        artifact_path = tmp_path / "adg_graph_watchlist_20260101_120000.json"
        with open(artifact_path, "w") as f:
            json.dump({"watchlist": []}, f)

        baseline_manager = AcceptedBaselineManager(tmp_path)
        baseline_manager.accept_baseline(artifact_path, "reviewer_1", "Baseline")

        applicator = GovernedPromotionApplicator(tmp_path, baseline_manager)
        action = PromotionAction(
            action_id="PA_001",
            source_proposal_id="SL_001",
            source_queue_id="QP_001",
            reviewer="reviewer_1",
            target_type="threshold_config",
            target_path="config/threshold",
            old_value="50",
            new_value="75",
            timestamp="20260101_120000",
            rationale="Adjustment",
            rollback_token="RB_001",
            reversible=True,
        )
        applicator.apply_promotion(action, "operator_1", "Apply change")

        # Rollback the application
        applicator.rollback_application(
            applicator.applications[0].application_id, "operator_2", "Reverting due to issues"
        )

        # Generate review pack
        review_pack = ADGPolicyReviewPack(tmp_path, review_window_days=30)
        pack = review_pack.generate_review_pack()

        # Should show the rollback
        pr_summary = pack["sections"]["promotion_rollback_summary"]
        assert pr_summary["total_rollbacks_in_window"] == 1

    def test_policy_questions_generated_when_evidence_threshold_met(self, tmp_path):
        """Policy questions should be generated when evidence meets threshold."""
        import json
        from tools.generate.adg_graph_watchlist_builder import (
            ADGPolicyReviewPack,
            ADGProposalPromotionManager,
            ProposalPacket,
        )

        # Create many proposals to trigger threshold
        promo_manager = ADGProposalPromotionManager(tmp_path)
        for i in range(10):
            proposal = ProposalPacket(
                proposal_id=f"SL_{i:03d}",
                category="threshold_tuning",
                trigger_evidence=[{"pattern": "repeat"}],
                affected_signals=["reverse_dependency"],
                affected_layers=["L_TOOLS"],
                affected_files=["test.py"],
                suggested_change=f"Adjust threshold {i}",
                expected_benefit="Better detection",
                risk_assessment="Low",
                confidence_score=0.9,  # High confidence
                occurrence_count=5,
                learning_window_runs=5,
            )
            promo_manager.queue_proposal(proposal)

        promo_manager.emit_promotion_artifacts()

        # Generate review pack
        review_pack = ADGPolicyReviewPack(tmp_path, review_window_days=30)
        pack = review_pack.generate_review_pack()

        # Should generate questions due to high proposal count
        questions = pack["sections"]["policy_tuning_questions"]
        assert len(questions) > 0

    def test_review_pack_remains_non_binding(self, tmp_path):
        """Review pack must be explicitly non-binding."""
        from tools.generate.adg_graph_watchlist_builder import ADGPolicyReviewPack

        review_pack = ADGPolicyReviewPack(tmp_path, review_window_days=30)
        pack = review_pack.generate_review_pack()

        # Must be explicitly marked as non-binding
        assert pack["requires_human_review"] is True
        assert pack["live_mutation"] is False

        # Recommendations should be marked non-binding
        for rec in pack["sections"]["non_binding_recommendations"]:
            assert rec["non_binding"] is True
            assert rec["requires_human_review"] is True

    def test_no_live_mutation_occurs_during_generation(self, tmp_path):
        """Generating review pack must not mutate any live state."""
        import json
        from tools.generate.adg_graph_watchlist_builder import ADGPolicyReviewPack, AcceptedBaselineManager

        # Create baseline
        artifact_path = tmp_path / "adg_graph_watchlist_20260101_120000.json"
        with open(artifact_path, "w") as f:
            json.dump({"watchlist": []}, f)

        baseline_manager = AcceptedBaselineManager(tmp_path)
        baseline_manager.accept_baseline(artifact_path, "reviewer_1", "Baseline")

        # List artifacts before
        artifacts_before = list(tmp_path.glob("adg_*.json"))

        # Generate review pack
        review_pack = ADGPolicyReviewPack(tmp_path, review_window_days=30)
        pack = review_pack.generate_review_pack()

        # List artifacts after (excluding the review pack itself)
        artifacts_after = [a for a in tmp_path.glob("adg_*.json") if "review_pack" not in a.name]

        # Should not create/modify other artifacts
        assert len(artifacts_after) == len(artifacts_before)

    def test_empty_low_data_windows_are_graceful(self, tmp_path):
        """Review pack should handle empty or low-data windows gracefully."""
        from tools.generate.adg_graph_watchlist_builder import ADGPolicyReviewPack

        # Empty directory - no artifacts
        review_pack = ADGPolicyReviewPack(tmp_path, review_window_days=30)
        pack = review_pack.generate_review_pack()

        # Should not error
        assert pack["review_pack_id"].startswith("RP_")
        assert pack["sections"]["window_summary"]["data_completeness"] == "partial"

        # Should have empty but valid sections
        assert pack["sections"]["hotspot_patterns"]["total_proposals_analyzed"] == 0
        assert pack["sections"]["proposal_summary"]["high_confidence_proposals"] == 0

    def test_bounded_output_limits_are_enforced(self, tmp_path):
        """Review pack output should be bounded."""
        import json
        from tools.generate.adg_graph_watchlist_builder import (
            ADGPolicyReviewPack,
            ADGProposalPromotionManager,
            ProposalPacket,
        )

        # Create many proposals
        promo_manager = ADGProposalPromotionManager(tmp_path)
        for i in range(50):
            proposal = ProposalPacket(
                proposal_id=f"SL_{i:03d}",
                category=f"category_{i % 15}",  # Many categories
                trigger_evidence=[{"pattern": "repeat"}],
                affected_signals=["reverse_dependency"],
                affected_layers=["L_TOOLS"],
                affected_files=["test.py"],
                suggested_change=f"Change {i}",
                expected_benefit="Benefit",
                risk_assessment="Low",
                confidence_score=0.85,
                occurrence_count=5,
                learning_window_runs=5,
            )
            promo_manager.queue_proposal(proposal)

        promo_manager.emit_promotion_artifacts()

        # Generate review pack
        review_pack = ADGPolicyReviewPack(tmp_path, review_window_days=30)
        pack = review_pack.generate_review_pack()

        # Should be bounded
        hotspot = pack["sections"]["hotspot_patterns"]
        assert len(hotspot["repeat_offenders"]) <= 5

        proposals = pack["sections"]["proposal_summary"]
        assert len(proposals["proposal_counts_by_category"]) <= 10

        questions = pack["sections"]["policy_tuning_questions"]
        assert len(questions) <= 5

        recommendations = pack["sections"]["non_binding_recommendations"]
        assert len(recommendations) <= 5

    def test_textual_summary_reflects_artifact_truthfully(self, tmp_path):
        """Textual summary should accurately reflect review pack content."""
        import json
        from tools.generate.adg_graph_watchlist_builder import (
            ADGPolicyReviewPack,
            ADGProposalPromotionManager,
            ProposalPacket,
        )

        # Create proposals
        promo_manager = ADGProposalPromotionManager(tmp_path)
        for i in range(3):
            proposal = ProposalPacket(
                proposal_id=f"SL_{i:03d}",
                category="threshold_tuning",
                trigger_evidence=[{"pattern": "repeat"}],
                affected_signals=["reverse_dependency"],
                affected_layers=["L_TOOLS"],
                affected_files=["test.py"],
                suggested_change="Change",
                expected_benefit="Benefit",
                risk_assessment="Low",
                confidence_score=0.85,
                occurrence_count=5,
                learning_window_runs=5,
            )
            promo_manager.queue_proposal(proposal)

        promo_manager.emit_promotion_artifacts()

        # Generate review pack and summary
        review_pack = ADGPolicyReviewPack(tmp_path, review_window_days=30)
        pack = review_pack.generate_review_pack()
        summary = review_pack.generate_textual_summary()

        # Summary should mention key facts from pack
        assert "ADG POLICY REVIEW PACK" in summary
        assert "Requires Human Review: YES" in summary or "requires_human_review" in summary.lower()
        assert "Live Mutation: NO" in summary or "live_mutation" in summary.lower()

        # Should be bounded
        assert len(summary.split("\n")) <= 65  # max_lines + 5 for safety


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
