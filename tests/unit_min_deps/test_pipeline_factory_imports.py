"""GAP-F: build_pipeline_deps() must resolve without ImportError and return correct proposer types."""

from pathlib import Path

import pytest

from agentic_core.L0_routing.config.path_constants import (
    SYSTEM_LEARNING_DIR,
)

PIPELINE_FACTORY_PATH = (
    Path(__file__).parent.parent.parent / SYSTEM_LEARNING_DIR / "pipelines" / "pipeline_factory.py"
)


@pytest.mark.unit_min_deps
class TestPipelineFactoryImports:
    def test_no_healing_backups_import_in_source(self):
        """AST: no import from healing_backups.naming_violations exists in pipeline_factory.py."""
        src = PIPELINE_FACTORY_PATH.read_text(encoding="utf-8", errors="replace")
        assert "healing_backups" not in src, (
            "Stale healing_backups import path still present in pipeline_factory.py"
        )
        assert "naming_violations" not in src, (
            "naming_violations import path still present in pipeline_factory.py"
        )

    def test_canonical_proposer_imports_in_source(self):
        """AST: canonical imports from system_learning.engines.l0/l1/l5 are present."""
        src = PIPELINE_FACTORY_PATH.read_text(encoding="utf-8", errors="replace")
        assert "system_learning.engines.l0_threshold_tuner" in src
        assert "system_learning.engines.l1_model_proposer" in src
        assert "system_learning.engines.l5_policy_proposer" in src

    def test_build_pipeline_deps_no_import_error(self, tmp_path):
        """build_pipeline_deps() must not raise ImportError."""
        from system_learning.pipelines.pipeline_factory import build_pipeline_deps

        # Should not raise ImportError
        deps = build_pipeline_deps(repo_root=tmp_path)
        assert deps is not None

    def test_l0_proposer_is_correct_type(self, tmp_path):
        """The l0_proposer in PipelineDependencies must be an L0ProposerAdapter instance."""
        from system_learning.engines.l0_threshold_tuner import L0ProposerAdapter
        from system_learning.pipelines.pipeline_factory import build_pipeline_deps

        deps = build_pipeline_deps(repo_root=tmp_path)
        assert isinstance(deps.l0_proposer, L0ProposerAdapter), (
            f"Expected L0ProposerAdapter, got {type(deps.l0_proposer)}"
        )

    def test_l1_proposer_is_correct_type(self, tmp_path):
        """The l1_proposer in PipelineDependencies must be an L1ModelProposer instance."""
        from system_learning.engines.l1_model_proposer import L1ModelProposer
        from system_learning.pipelines.pipeline_factory import build_pipeline_deps

        deps = build_pipeline_deps(repo_root=tmp_path)
        assert isinstance(deps.l1_proposer, L1ModelProposer), (
            f"Expected L1ModelProposer, got {type(deps.l1_proposer)}"
        )

    def test_l5_proposer_is_correct_type(self, tmp_path):
        """The l5_proposer in PipelineDependencies must be an L5PolicyProposer instance."""
        from system_learning.engines.l5_policy_proposer import L5PolicyProposer
        from system_learning.pipelines.pipeline_factory import build_pipeline_deps

        deps = build_pipeline_deps(repo_root=tmp_path)
        assert isinstance(deps.l5_proposer, L5PolicyProposer), (
            f"Expected L5PolicyProposer, got {type(deps.l5_proposer)}"
        )

    def test_run_pipeline_completes_after_import_fix(self, tmp_path):
        """Pipeline execution verification: build_pipeline_deps + run_pipeline must not raise ImportError."""
        from system_learning.pipelines.meta_learning_pipeline import run_pipeline
        from system_learning.pipelines.pipeline_factory import (
            build_pipeline_config,
            build_pipeline_deps,
        )

        cfg = build_pipeline_config(proposal_only=True)
        deps = build_pipeline_deps(repo_root=tmp_path)

        # Must not raise ImportError (the primary regression we're guarding against)
        try:
            result = run_pipeline(
                now_utc=1_000_000,
                window_start_utc=999_000,
                window_end_utc=1_000_000,
                cfg=cfg,
                deps=deps,
            )
            # If it returns, result must be a tuple (proposals)
            assert isinstance(result, tuple)
        except ImportError as e:
            pytest.fail(f"run_pipeline raised ImportError after import fix: {e}")
