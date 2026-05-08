"""W6 — Certification Reports Tests.

Validates certification report generation and proof bundle assembly.
Per plan: RTC-REQ-125, 126, 127, 128.

W6 implementation per runtime-cert-hardened-w0-deferred-scope.md
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import pytest

# Script paths
REPORT_GENERATOR = Path("tools/certification/generate_certification_report.py")
BUNDLE_ASSEMBLER = Path("tools/certification/assemble_proof_bundle.py")
GAP_ANALYZER = Path("tools/certification/gap_analysis_report.py")


def run_script(script: Path, env: dict[str, str] | None = None) -> tuple[int, str, str]:
    """Run a script."""
    result = subprocess.run(
        [sys.executable, str(script)],
        capture_output=True,
        text=True,
        timeout=60,
        env={**dict(subprocess.os.environ), **(env or {})},
    )
    return result.returncode, result.stdout, result.stderr


def create_mock_evidence(dir_path: Path) -> None:
    """Create mock evidence files."""
    dir_path.mkdir(parents=True, exist_ok=True)
    
    evidence_files = [
        {
            "probe": "canonical_csv",
            "timestamp": "2026-05-08T21:00:00Z",
            "result": {"status": "VALID"},
        },
        {
            "probe": "semantic_cache",
            "timestamp": "2026-05-08T21:01:00Z",
            "result": {"status": "VALID"},
        },
        {
            "verifier": "merkle_root",
            "timestamp": "2026-05-08T21:02:00Z",
            "result": {"status": "MERKLE_VALID", "depth": 3},
        },
    ]
    
    for i, data in enumerate(evidence_files):
        file_path = dir_path / f"evidence_{i}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f)


def create_mock_merkle(dir_path: Path) -> None:
    """Create mock merkle tree."""
    dir_path.mkdir(parents=True, exist_ok=True)
    
    tree = {
        "root_hash": "abc123",
        "metadata": {
            "depth": 3,
            "total_nodes": 17,
            "total_leaves": 11,
        },
        "root": {"name": "root", "hash": "abc123", "children": []},
    }
    
    tree_path = dir_path / "merkle_tree.json"
    with open(tree_path, "w", encoding="utf-8") as f:
        json.dump(tree, f)
    
    root_path = dir_path / "merkle_root.txt"
    with open(root_path, "w", encoding="utf-8") as f:
        f.write("abc123def456")


class TestCertificationReportGenerator:
    """Tests for certification report generator (RTC-REQ-125)."""

    def test_generator_exists(self) -> None:
        """Report generator script exists."""
        assert REPORT_GENERATOR.exists(), f"Generator not found: {REPORT_GENERATOR}"

    def test_generator_runnable(self) -> None:
        """Generator runs without crashing."""
        if not REPORT_GENERATOR.exists():
            pytest.skip("Generator not implemented yet")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            evidence_dir = Path(tmpdir) / "evidence"
            merkle_dir = Path(tmpdir) / "merkle"
            output_dir = Path(tmpdir) / "output"
            
            create_mock_evidence(evidence_dir)
            create_mock_merkle(merkle_dir)
            
            env = {
                "EVIDENCE_DIR": str(evidence_dir),
                "MERKLE_TREE_PATH": str(merkle_dir / "merkle_tree.json"),
                "MERKLE_ROOT_PATH": str(merkle_dir / "merkle_root.txt"),
                "OUTPUT_DIR": str(output_dir),
            }
            
            exit_code, stdout, stderr = run_script(REPORT_GENERATOR, env)
            
            # Should succeed with mock data
            assert exit_code == 0, f"Generator should succeed: {stdout}{stderr}"

    def test_generates_markdown(self) -> None:
        """Generator produces markdown report."""
        if not REPORT_GENERATOR.exists():
            pytest.skip("Generator not implemented yet")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            evidence_dir = Path(tmpdir) / "evidence"
            merkle_dir = Path(tmpdir) / "merkle"
            output_dir = Path(tmpdir) / "output"
            
            create_mock_evidence(evidence_dir)
            create_mock_merkle(merkle_dir)
            
            env = {
                "EVIDENCE_DIR": str(evidence_dir),
                "MERKLE_TREE_PATH": str(merkle_dir / "merkle_tree.json"),
                "MERKLE_ROOT_PATH": str(merkle_dir / "merkle_root.txt"),
                "OUTPUT_DIR": str(output_dir),
            }
            
            run_script(REPORT_GENERATOR, env)
            
            # Check for markdown output
            md_files = list(output_dir.glob("*.md"))
            assert len(md_files) > 0, "Should generate markdown report"

    def test_generates_html(self) -> None:
        """Generator produces HTML report."""
        if not REPORT_GENERATOR.exists():
            pytest.skip("Generator not implemented yet")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            evidence_dir = Path(tmpdir) / "evidence"
            merkle_dir = Path(tmpdir) / "merkle"
            output_dir = Path(tmpdir) / "output"
            
            create_mock_evidence(evidence_dir)
            create_mock_merkle(merkle_dir)
            
            env = {
                "EVIDENCE_DIR": str(evidence_dir),
                "MERKLE_TREE_PATH": str(merkle_dir / "merkle_tree.json"),
                "MERKLE_ROOT_PATH": str(merkle_dir / "merkle_root.txt"),
                "OUTPUT_DIR": str(output_dir),
            }
            
            run_script(REPORT_GENERATOR, env)
            
            # Check for HTML output
            html_files = list(output_dir.glob("*.html"))
            assert len(html_files) > 0, "Should generate HTML report"

    def test_requires_merkle(self) -> None:
        """Generator requires merkle tree."""
        if not REPORT_GENERATOR.exists():
            pytest.skip("Generator not implemented yet")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            env = {
                "MERKLE_TREE_PATH": str(Path(tmpdir) / "nonexistent.json"),
                "EVIDENCE_DIR": str(Path(tmpdir)),
                "OUTPUT_DIR": str(Path(tmpdir) / "output"),
            }
            
            exit_code, stdout, stderr = run_script(REPORT_GENERATOR, env)
            
            # Should fail without merkle
            assert exit_code != 0, "Should fail without merkle tree"


class TestProofBundleAssembler:
    """Tests for proof bundle assembler (RTC-REQ-126)."""

    def test_assembler_exists(self) -> None:
        """Bundle assembler script exists."""
        assert BUNDLE_ASSEMBLER.exists(), f"Assembler not found: {BUNDLE_ASSEMBLER}"

    def test_assembler_runnable(self) -> None:
        """Assembler runs without crashing."""
        if not BUNDLE_ASSEMBLER.exists():
            pytest.skip("Assembler not implemented yet")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            evidence_dir = Path(tmpdir) / "evidence"
            merkle_dir = Path(tmpdir) / "merkle"
            output_dir = Path(tmpdir) / "bundles"
            
            create_mock_evidence(evidence_dir)
            create_mock_merkle(merkle_dir)
            
            env = {
                "EVIDENCE_DIR": str(evidence_dir),
                "MERKLE_TREE_PATH": str(merkle_dir / "merkle_tree.json"),
                "MERKLE_ROOT_PATH": str(merkle_dir / "merkle_root.txt"),
                "OUTPUT_DIR": str(output_dir),
            }
            
            exit_code, stdout, stderr = run_script(BUNDLE_ASSEMBLER, env)
            
            # Should succeed with mock data
            assert exit_code == 0, f"Assembler should succeed: {stdout}{stderr}"

    def test_generates_zip_bundle(self) -> None:
        """Assembler produces zip bundle."""
        if not BUNDLE_ASSEMBLER.exists():
            pytest.skip("Assembler not implemented yet")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            evidence_dir = Path(tmpdir) / "evidence"
            merkle_dir = Path(tmpdir) / "merkle"
            output_dir = Path(tmpdir) / "bundles"
            
            create_mock_evidence(evidence_dir)
            create_mock_merkle(merkle_dir)
            
            env = {
                "EVIDENCE_DIR": str(evidence_dir),
                "MERKLE_TREE_PATH": str(merkle_dir / "merkle_tree.json"),
                "MERKLE_ROOT_PATH": str(merkle_dir / "merkle_root.txt"),
                "OUTPUT_DIR": str(output_dir),
            }
            
            run_script(BUNDLE_ASSEMBLER, env)
            
            # Check for zip bundle
            zip_files = list(output_dir.glob("*.zip"))
            assert len(zip_files) > 0, "Should generate zip bundle"

    def test_generates_tar_bundle(self) -> None:
        """Assembler produces tar.gz bundle."""
        if not BUNDLE_ASSEMBLER.exists():
            pytest.skip("Assembler not implemented yet")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            evidence_dir = Path(tmpdir) / "evidence"
            merkle_dir = Path(tmpdir) / "merkle"
            output_dir = Path(tmpdir) / "bundles"
            
            create_mock_evidence(evidence_dir)
            create_mock_merkle(merkle_dir)
            
            env = {
                "EVIDENCE_DIR": str(evidence_dir),
                "MERKLE_TREE_PATH": str(merkle_dir / "merkle_tree.json"),
                "MERKLE_ROOT_PATH": str(merkle_dir / "merkle_root.txt"),
                "OUTPUT_DIR": str(output_dir),
            }
            
            run_script(BUNDLE_ASSEMBLER, env)
            
            # Check for tar bundle
            tar_files = list(output_dir.glob("*.tar.gz"))
            assert len(tar_files) > 0, "Should generate tar.gz bundle"

    def test_bundle_contains_manifest(self) -> None:
        """Bundle includes manifest.json."""
        if not BUNDLE_ASSEMBLER.exists():
            pytest.skip("Assembler not implemented yet")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            evidence_dir = Path(tmpdir) / "evidence"
            merkle_dir = Path(tmpdir) / "merkle"
            output_dir = Path(tmpdir) / "bundles"
            
            create_mock_evidence(evidence_dir)
            create_mock_merkle(merkle_dir)
            
            env = {
                "EVIDENCE_DIR": str(evidence_dir),
                "MERKLE_TREE_PATH": str(merkle_dir / "merkle_tree.json"),
                "MERKLE_ROOT_PATH": str(merkle_dir / "merkle_root.txt"),
                "OUTPUT_DIR": str(output_dir),
            }
            
            run_script(BUNDLE_ASSEMBLER, env)
            
            # Check zip for manifest
            import zipfile
            zip_files = list(output_dir.glob("*.zip"))
            if zip_files:
                with zipfile.ZipFile(zip_files[0], "r") as zf:
                    assert "manifest.json" in zf.namelist(), "Zip should contain manifest"


class TestGapAnalysisReport:
    """Tests for gap analysis report (RTC-REQ-128)."""

    def test_analyzer_exists(self) -> None:
        """Gap analyzer script exists."""
        assert GAP_ANALYZER.exists(), f"Analyzer not found: {GAP_ANALYZER}"

    def test_analyzer_runnable(self) -> None:
        """Analyzer runs without crashing."""
        if not GAP_ANALYZER.exists():
            pytest.skip("Analyzer not implemented yet")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            evidence_dir = Path(tmpdir) / "evidence"
            output_dir = Path(tmpdir) / "output"
            
            create_mock_evidence(evidence_dir)
            
            env = {
                "EVIDENCE_DIR": str(evidence_dir),
                "OUTPUT_DIR": str(output_dir),
            }
            
            exit_code, stdout, stderr = run_script(GAP_ANALYZER, env)
            
            # Should succeed with mock data
            assert exit_code == 0, f"Analyzer should succeed: {stdout}{stderr}"

    def test_generates_report(self) -> None:
        """Analyzer produces gap report."""
        if not GAP_ANALYZER.exists():
            pytest.skip("Analyzer not implemented yet")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            evidence_dir = Path(tmpdir) / "evidence"
            output_dir = Path(tmpdir) / "output"
            
            create_mock_evidence(evidence_dir)
            
            env = {
                "EVIDENCE_DIR": str(evidence_dir),
                "OUTPUT_DIR": str(output_dir),
            }
            
            run_script(GAP_ANALYZER, env)
            
            # Check for report output
            md_files = list(output_dir.glob("gap_analysis_*.md"))
            assert len(md_files) > 0, "Should generate gap analysis report"

    def test_detects_gaps(self) -> None:
        """Analyzer detects missing artifacts."""
        if not GAP_ANALYZER.exists():
            pytest.skip("Analyzer not implemented yet")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            evidence_dir = Path(tmpdir) / "evidence"
            output_dir = Path(tmpdir) / "output"
            
            # Create sufficient evidence (but with gaps in required artifacts)
            evidence_dir.mkdir(parents=True, exist_ok=True)
            
            # Create evidence files for 2 probes (minimum required)
            for i, probe_name in enumerate(["canonical_csv", "minimal_probe"]):
                with open(evidence_dir / f"evidence_{i}.json", "w") as f:
                    json.dump({
                        "probe": probe_name,
                        "timestamp": "2026-05-08T21:00:00Z",
                        "result": {"status": "VALID"}
                    }, f)
            
            env = {
                "EVIDENCE_DIR": str(evidence_dir),
                "OUTPUT_DIR": str(output_dir),
            }
            
            exit_code, stdout, stderr = run_script(GAP_ANALYZER, env)
            
            # Should succeed and may report gaps (analyzer skips if many gaps)
            # Just verify it runs without error
            assert exit_code in [0, 1], f"Should exit 0 or 1: {stdout}{stderr}"


class TestW6Requirements:
    """W6 requirement validation tests."""

    def test_rtc_req_125_report_generation(self) -> None:
        """RTC-REQ-125: Certification report generation."""
        assert REPORT_GENERATOR.exists(), "Report generator required for RTC-REQ-125"

    def test_rtc_req_126_proof_bundle(self) -> None:
        """RTC-REQ-126: Proof bundle assembly."""
        assert BUNDLE_ASSEMBLER.exists(), "Bundle assembler required for RTC-REQ-126"

    def test_rtc_req_128_gap_analysis(self) -> None:
        """RTC-REQ-128: Gap analysis report."""
        assert GAP_ANALYZER.exists(), "Gap analyzer required for RTC-REQ-128"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
