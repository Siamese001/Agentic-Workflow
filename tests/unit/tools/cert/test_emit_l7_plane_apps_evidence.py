"""L7_AUDITABILITY regression test for Fort Knox apps_* L7 artifact binding.

Verifies that emit_l7_plane_evidence.py correctly collects L7 artifacts
from apps_* governed_run output directories and includes them in the
chain evidence for RTC-REQ certification.
"""
from __future__ import annotations

import json
from pathlib import Path
from unittest import mock

import pytest

from tools.cert.emit_l7_plane_evidence import (
    _collect_apps_chain_artifacts,
    build_all_chain_evidence,
    collect_chain_artifacts,
    APPS_L7_CHAINS,
)


class TestAppsL7ArtifactCollection:
    """Verify apps_* L7 artifacts are collected for Fort Knox certification."""

    def test_collect_apps_chain_artifacts_missing_dir(self, tmp_path: Path):
        """Should return _missing=True when runs directory doesn't exist."""
        result = _collect_apps_chain_artifacts("nonexistent_app")
        assert result.get("_missing") is True

    def test_collect_apps_chain_artifacts_empty_dir(self, tmp_path: Path, monkeypatch):
        """Should return _missing=True when no run directories exist."""
        monkeypatch.chdir(tmp_path)
        
        # Create empty artifacts/apps_test/runs directory
        runs_dir = tmp_path / "artifacts" / "apps_test" / "runs"
        runs_dir.mkdir(parents=True)
        
        # Need to mock REPO_ROOT to point to tmp_path
        with mock.patch("tools.cert.emit_l7_plane_evidence.REPO_ROOT", tmp_path):
            result = _collect_apps_chain_artifacts("apps_test")
        
        assert result.get("_missing") is True

    def test_collect_apps_chain_artifacts_with_l7_files(self, tmp_path: Path, monkeypatch):
        """Should collect L7 artifacts from latest run directory."""
        monkeypatch.chdir(tmp_path)
        
        # Create run directories with L7 artifacts
        runs_dir = tmp_path / "artifacts" / "apps_eval" / "runs"
        
        # Older run
        old_run = runs_dir / "20260101-120000"
        old_run.mkdir(parents=True)
        (old_run / "l2_execution_receipt.json").write_text('{"old": true}')
        
        # Newer run (should be selected)
        new_run = runs_dir / "20260102-120000"
        new_run.mkdir(parents=True)
        (new_run / "agentic_core_how_trace.json").write_text('{"trace": "test"}')
        (new_run / "agentic_core_l7_route_family_coverage.json").write_text('{"coverage": "test"}')
        (new_run / "integrated_runtime_artifact_manifest.json").write_text('{"manifest": "test"}')
        
        with mock.patch("tools.cert.emit_l7_plane_evidence.REPO_ROOT", tmp_path):
            result = _collect_apps_chain_artifacts("apps_eval")
        
        assert result.get("_missing") is None
        assert "agentic_core_how_trace.json" in result
        assert "agentic_core_l7_route_family_coverage.json" in result
        assert "integrated_runtime_artifact_manifest.json" in result
        # Should NOT include old run's file
        assert "l2_execution_receipt.json" not in result

    def test_apps_chains_included_in_build_all(self, tmp_path: Path, monkeypatch):
        """APPS_L7_CHAINS must be included in build_all_chain_evidence output."""
        monkeypatch.chdir(tmp_path)
        
        # Create mock chain dirs for certified chains
        chains_dir = tmp_path / "artifacts" / "certification" / "integrated_runtime"
        for chain in ["latest", "r1a_latest"]:
            chain_dir = chains_dir / chain
            chain_dir.mkdir(parents=True)
            (chain_dir / "agentic_core_how_trace.json").write_text('{"trace": true}')
        
        # Create apps_eval run dir with L7 artifacts
        apps_runs = tmp_path / "artifacts" / "apps_eval" / "runs"
        run_dir = apps_runs / "20260102-120000"
        run_dir.mkdir(parents=True)
        (run_dir / "agentic_core_how_trace.json").write_text('{"apps_trace": true}')
        
        with mock.patch("tools.cert.emit_l7_plane_evidence.REPO_ROOT", tmp_path):
            with mock.patch("tools.cert.emit_l7_plane_evidence.CHAINS_DIR", chains_dir):
                result = build_all_chain_evidence()
        
        # Should include both certified chains and apps_* chains
        assert "latest" in result
        assert "r1a_latest" in result
        assert "apps_eval" in result
        
    def test_apps_l7_chains_constant_defined(self):
        """APPS_L7_CHAINS must be defined and contain expected apps."""
        assert isinstance(APPS_L7_CHAINS, list)
        assert "apps_eval" in APPS_L7_CHAINS

    def test_collect_chain_artifacts_finds_all_l7_targets(self, tmp_path: Path):
        """collect_chain_artifacts must find all expected L7 artifact types."""
        chain_dir = tmp_path / "test_chain"
        chain_dir.mkdir()
        
        # Create all expected L7 artifacts
        l7_artifacts = [
            "agentic_core_how_trace.json",
            "agentic_core_l7_route_family_coverage.json",
            "integrated_runtime_artifact_manifest.json",
            "agentic_core_spine_proof.json",
            "runtime_identity_envelope.json",
            "route_contract.json",
        ]
        
        for artifact in l7_artifacts:
            (chain_dir / artifact).write_text(f'{{"{artifact}": true}}')
        
        result = collect_chain_artifacts(chain_dir)
        
        for artifact in l7_artifacts:
            assert artifact in result, f"Missing {artifact}"
            # Verify it's a sha256 hash (64 hex chars)
            assert len(result[artifact]) == 64
            assert all(c in "0123456789abcdef" for c in result[artifact])
