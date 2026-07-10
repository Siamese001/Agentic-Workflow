"""L7_AUDITABILITY emit verification for integrated_single_action_spine_run.

Tests that the R4 entrypoint produces the four canonical L7 artifacts:
- agentic_core_how_trace.json
- agentic_core_l7_route_family_coverage.json
- agentic_core_spine_proof.json
- integrated_runtime_artifact_manifest.json
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from agentic_core.runtime.entrypoints.integrated_single_action_spine_run import (
    run_integrated_single_action_spine,
)


def _minimal_raw_request() -> dict:
    """Return a minimal valid raw request for R4 pipeline."""
    return {
        "request_id": "test-req-001",
        "trace_root": "test-trace-001",
        "jd_payload": {"title": "Test Role", "description": "Test description"},
        "jd_hash": "abc123",
        "brief_hash": "def456",
        "resume_hash": "ghi789",
    }


@pytest.fixture
def temp_artifact_dir():
    """Provide a temporary directory for artifact emission."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


class TestR4L7Emit:
    """Verify L7_AUDITABILITY artifacts are emitted by R4 deterministic pipeline."""

    def test_l7_artifacts_emitted(self, temp_artifact_dir: Path):
        """All four canonical L7 artifacts must exist after run completion."""
        # Mock the L2 callable to avoid real execution
        mock_l2_result = {"status": "success", "output": "test output"}
        mock_l2_callable = MagicMock(return_value=mock_l2_result)

        # Mock recipe resolver to use our mock callable
        # Note: resolve_l2_recipe is imported inside the function, so we patch the module's __import__
        with patch(
            "agentic_core.runtime.l2_recipe_resolver.resolve_l2_recipe"
        ) as mock_resolve:
            mock_resolve.return_value = mock_l2_callable

            result = run_integrated_single_action_spine(
                raw_request=_minimal_raw_request(),
                app_name="apps_rg",
                artifact_dir=temp_artifact_dir,
                _test_mode=True,  # Required for l2_callable injection
                l2_callable=mock_l2_callable,
            )

        # Verify run completed successfully
        assert result.fault == ""
        assert result.x3_disposition in (
            "ALLOW",
            "DENY",
            "REVIEW",
            "X3A",
            "EXIT_OK",
            "X3D",
        )
        assert result.artifact_dir == temp_artifact_dir

        # Verify all four canonical L7 artifacts exist
        l7_artifacts = [
            "agentic_core_how_trace.json",
            "agentic_core_l7_route_family_coverage.json",
            "agentic_core_spine_proof.json",
            "integrated_runtime_artifact_manifest.json",
        ]

        for filename in l7_artifacts:
            artifact_path = temp_artifact_dir / filename
            assert artifact_path.exists(), f"Missing L7 artifact: {filename}"
            # Verify valid JSON
            content = json.loads(artifact_path.read_text(encoding="utf-8"))
            assert content, f"Empty or invalid JSON in {filename}"

    def test_how_trace_structure(self, temp_artifact_dir: Path):
        """HOW trace must have required schema fields."""
        mock_l2_callable = MagicMock(return_value={"status": "success"})

        with patch(
            "agentic_core.runtime.l2_recipe_resolver.resolve_l2_recipe"
        ) as mock_resolve:
            mock_resolve.return_value = mock_l2_callable

            run_integrated_single_action_spine(
                raw_request=_minimal_raw_request(),
                app_name="apps_rg",
                artifact_dir=temp_artifact_dir,
                _test_mode=True,
                l2_callable=mock_l2_callable,
            )

        how_trace_path = temp_artifact_dir / "agentic_core_how_trace.json"
        assert how_trace_path.exists()

        content = json.loads(how_trace_path.read_text(encoding="utf-8"))["payload"]
        # Required fields per HowTrace schema
        assert "schema_version" in content
        assert "runtime_subject" in content
        assert "evidence_plane" in content
        assert "stages" in content
        assert isinstance(content["stages"], list)

    def test_manifest_has_l7_refs(self, temp_artifact_dir: Path):
        """Manifest must reference L7 artifacts with artifact:// URIs."""
        mock_l2_callable = MagicMock(return_value={"status": "success"})

        with patch(
            "agentic_core.runtime.l2_recipe_resolver.resolve_l2_recipe"
        ) as mock_resolve:
            mock_resolve.return_value = mock_l2_callable

            run_integrated_single_action_spine(
                raw_request=_minimal_raw_request(),
                app_name="apps_rg",
                artifact_dir=temp_artifact_dir,
                _test_mode=True,
                l2_callable=mock_l2_callable,
            )

        manifest_path = temp_artifact_dir / "integrated_runtime_artifact_manifest.json"
        assert manifest_path.exists()

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))["payload"]
        assert "how_trace_ref" in manifest
        assert "how_trace_sha256" in manifest
        assert "l7_route_family_coverage_ref" in manifest
        assert "l7_route_family_coverage_sha256" in manifest
        assert manifest["how_trace_ref"].startswith("artifact://")
        assert manifest["l7_route_family_coverage_ref"].startswith("artifact://")

    def test_spine_proof_has_identity_binding(self, temp_artifact_dir: Path):
        """Spine proof must bind back to identity envelope."""
        mock_l2_callable = MagicMock(return_value={"status": "success"})

        with patch(
            "agentic_core.runtime.l2_recipe_resolver.resolve_l2_recipe"
        ) as mock_resolve:
            mock_resolve.return_value = mock_l2_callable

            result = run_integrated_single_action_spine(
                raw_request=_minimal_raw_request(),
                app_name="apps_rg",
                artifact_dir=temp_artifact_dir,
                _test_mode=True,
                l2_callable=mock_l2_callable,
            )

        spine_path = temp_artifact_dir / "agentic_core_spine_proof.json"
        assert spine_path.exists()

        spine = json.loads(spine_path.read_text(encoding="utf-8"))["payload"]
        assert "run_id" in spine
        assert spine["run_id"] == result.run_id

    def test_execution_witness_reports_real_l2_and_attempt_counts(
        self,
        temp_artifact_dir: Path,
    ) -> None:
        def _l2() -> dict:
            section_dir = temp_artifact_dir / "sections" / "executive_summary"
            section_dir.mkdir(parents=True, exist_ok=True)
            (section_dir / "judge_attempt_ledger.json").write_text(
                json.dumps(
                    {
                        "schema_version": "apps_rg.judge_attempt_ledger.v1",
                        "attempt_count": 2,
                        "attempts": [{"attempt": 1}, {"attempt": 2}],
                    }
                ),
                encoding="utf-8",
            )
            (section_dir / "provider_response.json").write_text(
                json.dumps(
                    {
                        "provider_attempt_spans": [
                            {"attempt_id": "generation-1"},
                            {"attempt_id": "generation-2"},
                        ]
                    }
                ),
                encoding="utf-8",
            )
            return {
                "status": "success",
                "run_dir": str(temp_artifact_dir),
                "runtime_execution_witness": {
                    "generation_provider_attempt_count": 2,
                    "judge_attempt_count": 2,
                    "attempt_evidence_refs": [
                        "sections/executive_summary/provider_response.json",
                        "sections/executive_summary/judge_attempt_ledger.json",
                    ],
                },
            }

        run_integrated_single_action_spine(
            raw_request=_minimal_raw_request(),
            app_name="apps_rg",
            artifact_dir=temp_artifact_dir,
            _test_mode=True,
            l2_callable=_l2,
        )

        terminal = json.loads(
            (temp_artifact_dir / "terminal_ret_packet.json").read_text(encoding="utf-8")
        )["payload"]
        witness = json.loads(
            (temp_artifact_dir / "runtime_execution_witness.json").read_text(
                encoding="utf-8"
            )
        )["payload"]
        manifest = json.loads(
            (temp_artifact_dir / "integrated_runtime_artifact_manifest.json").read_text(
                encoding="utf-8"
            )
        )["payload"]

        assert terminal["no_l2_execution_assertion"] is False
        assert terminal["l2_execution_status"] == "EXECUTED"
        assert witness["c0"]["status"] == "BYPASSED_PRELOADED_CONTEXT"
        assert witness["l2"]["status"] == "PASS"
        assert witness["generation_provider_attempt_count"] == 2
        assert witness["judge_attempt_count"] == 2
        assert manifest["llm_judge_invocation_count"] == 2
