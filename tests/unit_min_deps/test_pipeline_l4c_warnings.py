"""GAP-D: L4C write helpers must emit logger.warning on failure, never silent pass."""

import ast
import logging
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

META_PIPELINE_PATH = (
    Path(__file__).parent.parent.parent / "system_learning" / "pipelines" / "meta_learning_pipeline.py"
)


@pytest.mark.unit_min_deps
class TestPipelineL4cWarnings:
    def _count_silent_pass_in_l4_helpers(self):
        """AST: count bare 'except Exception: pass' blocks inside the three L4C helpers."""
        src = META_PIPELINE_PATH.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(src)

        helper_names = {
            "_analyze_shadow_drift_and_write",
            "_generate_policy_recommendation_and_write",
            "_create_proposal_and_write",
        }
        silent_count = 0

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name in helper_names:
                for child in ast.walk(node):
                    if isinstance(child, ast.ExceptHandler):
                        # Check if the handler body is a single bare Pass
                        if len(child.body) == 1 and isinstance(child.body[0], ast.Pass):
                            silent_count += 1
        return silent_count

    def test_no_silent_pass_in_l4c_helpers_ast(self):
        """AST: zero bare 'except … pass' blocks remain in the three L4C helper functions."""
        count = self._count_silent_pass_in_l4_helpers()
        assert count == 0, f"{count} silent 'except ... pass' block(s) still present in L4C helpers"

    def test_shadow_drift_helper_warns_on_exception(self, caplog):
        """_analyze_shadow_drift_and_write emits logger.warning when L4 write raises."""
        from system_learning.pipelines.meta_learning_pipeline import (
            _analyze_shadow_drift_and_write,
            _shadow_telemetry_batch,
        )

        # Inject a fake shadow record so the function doesn't short-circuit
        fake_record = MagicMock()
        _shadow_telemetry_batch.append(fake_record)

        mock_analyzer = MagicMock()
        drift_summary = MagicMock()
        drift_summary.to_canonical_json.return_value = "{}"
        mock_analyzer.analyze_batch.return_value = drift_summary

        mock_writer = MagicMock()
        mock_writer.write_l4c_shadow_drift.side_effect = RuntimeError("disk full")

        with patch(
            "system_learning.pipelines.meta_learning_pipeline._shadow_drift_analyzer",
            mock_analyzer,
        ):
            with caplog.at_level(logging.WARNING, logger="system_learning.pipelines.meta_learning_pipeline"):
                result = _analyze_shadow_drift_and_write(
                    profile_id="prof1", now_utc=1_000_000, l4_writer=mock_writer
                )

        _shadow_telemetry_batch.clear()

        assert result is drift_summary  # pipeline continues
        warning_texts = [r.message for r in caplog.records if r.levelno == logging.WARNING]
        assert any("shadow_drift" in w or "L4C" in w for w in warning_texts), (
            "Expected L4C shadow_drift warning not emitted"
        )

    def test_policy_recommendation_helper_warns_on_exception(self, caplog):
        """_generate_policy_recommendation_and_write emits logger.warning when L4 write raises."""
        from system_learning.pipelines.meta_learning_pipeline import (
            _generate_policy_recommendation_and_write,
        )

        mock_engine = MagicMock()
        recommendation = MagicMock()
        recommendation.to_canonical_json.return_value = "{}"
        mock_engine.generate_recommendation.return_value = recommendation

        mock_writer = MagicMock()
        mock_writer.write_l4c_policy_recommendation.side_effect = RuntimeError("write error")

        drift_summary = MagicMock()
        active_profile = MagicMock()

        with patch(
            "system_learning.pipelines.meta_learning_pipeline._policy_recommendation_engine",
            mock_engine,
        ):
            with caplog.at_level(logging.WARNING, logger="system_learning.pipelines.meta_learning_pipeline"):
                result = _generate_policy_recommendation_and_write(
                    drift_summary=drift_summary,
                    active_profile=active_profile,
                    now_utc=1_000_000,
                    l4_writer=mock_writer,
                )

        assert result is recommendation  # pipeline continues
        warning_texts = [r.message for r in caplog.records if r.levelno == logging.WARNING]
        assert any("policy_recommendation" in w or "L4C" in w for w in warning_texts), (
            "Expected L4C policy_recommendation warning not emitted"
        )

    def test_create_proposal_helper_warns_on_exception(self, caplog):
        """_create_proposal_and_write emits logger.warning when L4 write raises."""
        from system_learning.pipelines.meta_learning_pipeline import (
            _create_proposal_and_write,
        )

        mock_manager = MagicMock()
        proposal = MagicMock()
        proposal.to_canonical_json.return_value = "{}"
        mock_manager.create_proposal.return_value = proposal

        mock_writer = MagicMock()
        mock_writer.write_l4c_retrieval_profile_proposal.side_effect = RuntimeError("no space")

        policy_rec = MagicMock()
        active_profile = MagicMock()

        with patch(
            "system_learning.pipelines.meta_learning_pipeline._proposal_manager",
            mock_manager,
        ):
            with caplog.at_level(logging.WARNING, logger="system_learning.pipelines.meta_learning_pipeline"):
                result = _create_proposal_and_write(
                    policy_recommendation=policy_rec,
                    active_profile=active_profile,
                    now_utc=1_000_000,
                    l4_writer=mock_writer,
                )

        assert result is proposal  # pipeline continues
        warning_texts = [r.message for r in caplog.records if r.levelno == logging.WARNING]
        assert any("proposal" in w or "L4C" in w for w in warning_texts), (
            "Expected L4C retrieval_profile_proposal warning not emitted"
        )

    def test_pipeline_continues_after_l4c_failure(self, caplog):
        """L4C write failure must not propagate — pipeline returns normally."""
        from system_learning.pipelines.meta_learning_pipeline import (
            _create_proposal_and_write,
        )

        mock_manager = MagicMock()
        proposal = MagicMock()
        proposal.to_canonical_json.return_value = "{}"
        mock_manager.create_proposal.return_value = proposal

        # Writer raises on every call
        mock_writer = MagicMock()
        mock_writer.write_l4c_retrieval_profile_proposal.side_effect = OSError("io error")

        with patch(
            "system_learning.pipelines.meta_learning_pipeline._proposal_manager",
            mock_manager,
        ):
            # Must not raise
            result = _create_proposal_and_write(
                policy_recommendation=MagicMock(),
                active_profile=MagicMock(),
                now_utc=1_000_000,
                l4_writer=mock_writer,
            )

        assert result is proposal

    def test_none_drift_summary_short_circuits_policy_helper(self):
        """Passing None drift_summary to _generate_policy_recommendation_and_write returns None."""
        from system_learning.pipelines.meta_learning_pipeline import (
            _generate_policy_recommendation_and_write,
        )

        result = _generate_policy_recommendation_and_write(
            drift_summary=None,
            active_profile=MagicMock(),
            now_utc=1_000_000,
            l4_writer=MagicMock(),
        )
        assert result is None

    def test_none_policy_rec_short_circuits_proposal_helper(self):
        """Passing None policy_recommendation to _create_proposal_and_write returns None."""
        from system_learning.pipelines.meta_learning_pipeline import (
            _create_proposal_and_write,
        )

        result = _create_proposal_and_write(
            policy_recommendation=None,
            active_profile=MagicMock(),
            now_utc=1_000_000,
            l4_writer=MagicMock(),
        )
        assert result is None
