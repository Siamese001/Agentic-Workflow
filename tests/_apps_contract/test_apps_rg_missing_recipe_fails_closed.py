"""Test 4: Missing L2 recipe → fail closed.

Proves:
  - app_name with no registered recipe returns fault
  - apps_rg with recipe import blocked returns fault
  - No artifacts produced when recipe missing
"""

from __future__ import annotations

from pathlib import Path
from unittest import mock

import pytest


class TestMissingRecipeFailsClosed:
    """R4 runner fails closed when recipe cannot be resolved."""

    @pytest.fixture()
    def artifact_dir(self, tmp_path):
        d = tmp_path / "artifacts"
        d.mkdir()
        return d

    @pytest.fixture()
    def raw_request(self):
        return {
            "transport": "ui",
            "method": "POST",
            "content_type": "application/json",
            "source_channel": "apps_rg_cli",
            "declared_schema": "apps_rg_jd_v1",
            "body_text": "{}",
            "tenant_id": "default",
            "user_id": "u-test",
            "target_company": "TestCo",
            "target_role": "Engineer",
            "jd_payload": {},
            "jd_hash": "abc",
            "brief_hash": "def",
            "resume_hash": "ghi",
            "policy_hash": "policy_v1",
            "blueprint_hash": "blueprint_v1",
        }

    def test_unknown_app_name_fails_closed(self, raw_request, artifact_dir):
        """app_name='nonexistent_app' → L2_RECIPE_NOT_FOUND fault."""
        from agentic_core.runtime.entrypoints.integrated_r4_deterministic_pipeline_run import (
            run_integrated_r4_deterministic_pipeline,
        )

        result = run_integrated_r4_deterministic_pipeline(
            raw_request=raw_request,
            app_name="nonexistent_app",
            artifact_dir=artifact_dir,
        )

        assert result.fault
        assert "L2_RECIPE_NOT_FOUND" in result.fault
        assert "nonexistent_app" in result.fault

    def test_no_artifacts_on_missing_recipe(self, raw_request, tmp_path):
        """No receipt files written when recipe is missing."""
        from agentic_core.runtime.entrypoints.integrated_r4_deterministic_pipeline_run import (
            run_integrated_r4_deterministic_pipeline,
        )

        art_dir = tmp_path / "run_artifacts"

        result = run_integrated_r4_deterministic_pipeline(
            raw_request=raw_request,
            app_name="nonexistent_app",
            artifact_dir=art_dir,
        )

        assert result.fault
        # Fault returns before mkdir — no files should exist
        if art_dir.exists():
            receipts = list(art_dir.glob("*.json"))
            assert len(receipts) == 0

    def test_recipe_import_failure_fails_closed(self, raw_request, artifact_dir):
        """If apps_rg.l2_recipe cannot be imported, recipe is not registered."""
        from agentic_core.runtime import l2_recipe_resolver

        # Force registry reload with apps_rg blocked
        original_registry = l2_recipe_resolver._RECIPE_REGISTRY
        l2_recipe_resolver._RECIPE_REGISTRY = None

        try:
            with mock.patch.dict("sys.modules", {"apps_rg.l2_recipe": None, "apps_rg.l2_recipe.registry": None}):
                l2_recipe_resolver._RECIPE_REGISTRY = None
                from agentic_core.runtime.entrypoints.integrated_r4_deterministic_pipeline_run import (
                    run_integrated_r4_deterministic_pipeline,
                )
                result = run_integrated_r4_deterministic_pipeline(
                    raw_request=raw_request,
                    app_name="apps_rg",
                    artifact_dir=artifact_dir,
                )
                assert result.fault
                assert "L2_RECIPE_NOT_FOUND" in result.fault
        finally:
            l2_recipe_resolver._RECIPE_REGISTRY = original_registry
