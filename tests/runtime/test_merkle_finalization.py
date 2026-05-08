"""W5 — Merkle Finalization Tests.

Validates merkle tree depth, completeness, and consistency.
Per plan: RTC-REQ-031, 122, 124.

W5 implementation per runtime-cert-hardened-w0-deferred-scope.md
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import pytest

# Verifier paths
ROOT_VERIFIER = Path("ops_scripts/ci/verify_merkle_root.py")
CONSISTENCY_VERIFIER = Path("ops_scripts/ci/verify_merkle_consistency.py")


def run_verifier(verifier: Path, env: dict[str, str] | None = None) -> tuple[int, str, str]:
    """Run a verifier script."""
    result = subprocess.run(
        [sys.executable, str(verifier)],
        capture_output=True,
        text=True,
        timeout=60,
        env={**dict(subprocess.os.environ), **(env or {})},
    )
    return result.returncode, result.stdout, result.stderr


def create_valid_merkle_tree(path: Path) -> None:
    """Create a valid merkle tree with depth >= 3."""
    # Create a 3-level tree
    tree = {
        "root_hash": "abc123",
        "root": {
            "name": "root",
            "hash": "abc123",
            "children": [
                {
                    "name": "level1_a",
                    "hash": "def456",
                    "children": [
                        {"name": "canonical_csv", "hash": "aaa111", "data": "csv_hash"},
                        {"name": "matrix_loader", "hash": "bbb222", "data": "loader_hash"},
                    ],
                },
                {
                    "name": "level1_b",
                    "hash": "ghi789",
                    "children": [
                        {"name": "proof_depth_ladder", "hash": "ccc333", "data": "ladder_hash"},
                        {"name": "acceptance_validator", "hash": "ddd444", "data": "validator_hash"},
                    ],
                },
            ],
        },
    }
    
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(tree, f, indent=2)


def create_shallow_tree(path: Path) -> None:
    """Create a shallow tree (depth < 3)."""
    tree = {
        "root_hash": "shallow123",
        "root": {
            "name": "root",
            "hash": "shallow123",
            "children": [
                {"name": "artifact1", "hash": "a1", "data": "data1"},
                {"name": "artifact2", "hash": "a2", "data": "data2"},
            ],
        },
    }
    
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(tree, f, indent=2)


def create_tree_with_duplicates(path: Path) -> None:
    """Create a tree with duplicate artifacts."""
    tree = {
        "root_hash": "dup123",
        "root": {
            "name": "root",
            "hash": "dup123",
            "children": [
                {
                    "name": "branch1",
                    "hash": "b1",
                    "children": [
                        {"name": "duplicate_artifact", "hash": "d1", "data": "data1"},
                    ],
                },
                {
                    "name": "branch2",
                    "hash": "b2",
                    "children": [
                        {"name": "duplicate_artifact", "hash": "d2", "data": "data2"},
                    ],
                },
            ],
        },
    }
    
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(tree, f, indent=2)


def create_tree_with_hollow_nodes(path: Path) -> None:
    """Create a tree with hollow intermediate nodes."""
    tree = {
        "root_hash": "hollow123",
        "root": {
            "name": "root",
            "hash": "hollow123",
            "children": [
                {
                    # Hollow node - has children but no name or hash
                    "children": [
                        {"name": "artifact1", "hash": "a1", "data": "data1"},
                    ],
                },
            ],
        },
    }
    
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(tree, f, indent=2)


class TestMerkleRootVerifier:
    """Tests for merkle root verifier (RTC-REQ-031, 122)."""

    def test_verifier_exists(self) -> None:
        """Merkle root verifier script exists."""
        assert ROOT_VERIFIER.exists(), f"Verifier not found: {ROOT_VERIFIER}"

    def test_verifier_runnable(self) -> None:
        """Verifier runs without crashing."""
        if not ROOT_VERIFIER.exists():
            pytest.skip("Verifier not implemented yet")
        
        exit_code, stdout, stderr = run_verifier(ROOT_VERIFIER)
        # Expected outcomes: 0=VALID, 1=EMPTY, 2=DEPTH, 3=INCOMPLETE
        assert exit_code in {0, 1, 2, 3}, f"Unexpected exit code: {exit_code}"

    def test_valid_tree_passes(self) -> None:
        """Valid tree with depth >= 3 passes verification."""
        if not ROOT_VERIFIER.exists():
            pytest.skip("Verifier not implemented yet")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tree_path = Path(tmpdir) / "merkle_tree.json"
            create_valid_merkle_tree(tree_path)
            
            exit_code, stdout, stderr = run_verifier(
                ROOT_VERIFIER,
                {"MERKLE_TREE_PATH": str(tree_path)},
            )
            
            assert exit_code == 0, f"Valid tree should pass: {stdout}{stderr}"
            assert "MERKLE VALID" in stdout or "MERKLE_VALID" in stdout

    def test_shallow_tree_fails(self) -> None:
        """Shallow tree (depth < 3) fails with exit code 2."""
        if not ROOT_VERIFIER.exists():
            pytest.skip("Verifier not implemented yet")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tree_path = Path(tmpdir) / "merkle_tree.json"
            create_shallow_tree(tree_path)
            
            exit_code, stdout, stderr = run_verifier(
                ROOT_VERIFIER,
                {"MERKLE_TREE_PATH": str(tree_path)},
            )
            
            assert exit_code == 2, f"Shallow tree should fail with code 2: {stdout}{stderr}"
            assert "DEPTH" in stdout or "DEPTH" in stderr

    def test_missing_tree_fails(self) -> None:
        """Missing tree fails with exit code 1."""
        if not ROOT_VERIFIER.exists():
            pytest.skip("Verifier not implemented yet")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            nonexistent_path = Path(tmpdir) / "nonexistent.json"
            
            exit_code, stdout, stderr = run_verifier(
                ROOT_VERIFIER,
                {"MERKLE_TREE_PATH": str(nonexistent_path)},
            )
            
            assert exit_code == 1, f"Missing tree should fail with code 1: {stdout}{stderr}"

    def test_emits_evidence(self) -> None:
        """Verifier emits evidence artifact."""
        if not ROOT_VERIFIER.exists():
            pytest.skip("Verifier not implemented yet")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tree_path = Path(tmpdir) / "merkle_tree.json"
            create_valid_merkle_tree(tree_path)
            
            run_verifier(ROOT_VERIFIER, {"MERKLE_TREE_PATH": str(tree_path)})
            
            # Evidence should be created
            evidence_path = Path("artifacts/certification/evidence/merkle_root_verifier.json")
            assert evidence_path.exists() or "Evidence written" in str(run_verifier(ROOT_VERIFIER, {"MERKLE_TREE_PATH": str(tree_path)}))


class TestMerkleConsistencyVerifier:
    """Tests for merkle consistency verifier (RTC-REQ-124)."""

    def test_verifier_exists(self) -> None:
        """Merkle consistency verifier script exists."""
        assert CONSISTENCY_VERIFIER.exists(), f"Verifier not found: {CONSISTENCY_VERIFIER}"

    def test_verifier_runnable(self) -> None:
        """Verifier runs without crashing."""
        if not CONSISTENCY_VERIFIER.exists():
            pytest.skip("Verifier not implemented yet")
        
        exit_code, stdout, stderr = run_verifier(CONSISTENCY_VERIFIER)
        # Expected: 0=CONSISTENT, 1=DUP, 2=HOLLOW, 3=HASH, 4=MISSING
        assert exit_code in {0, 1, 2, 3, 4}, f"Unexpected exit code: {exit_code}"

    def test_valid_tree_consistent(self) -> None:
        """Valid tree passes consistency check."""
        if not CONSISTENCY_VERIFIER.exists():
            pytest.skip("Verifier not implemented yet")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tree_path = Path(tmpdir) / "merkle_tree.json"
            create_valid_merkle_tree(tree_path)
            
            exit_code, stdout, stderr = run_verifier(
                CONSISTENCY_VERIFIER,
                {"MERKLE_TREE_PATH": str(tree_path)},
            )
            
            assert exit_code == 0, f"Valid tree should be consistent: {stdout}{stderr}"

    def test_duplicate_artifacts_detected(self) -> None:
        """Duplicate artifacts detected with exit code 1."""
        if not CONSISTENCY_VERIFIER.exists():
            pytest.skip("Verifier not implemented yet")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tree_path = Path(tmpdir) / "merkle_tree.json"
            create_tree_with_duplicates(tree_path)
            
            exit_code, stdout, stderr = run_verifier(
                CONSISTENCY_VERIFIER,
                {"MERKLE_TREE_PATH": str(tree_path)},
            )
            
            assert exit_code == 1, f"Duplicates should fail with code 1: {stdout}{stderr}"
            assert "DUPLICATE" in stdout or "DUPLICATE" in stderr

    def test_hollow_nodes_detected(self) -> None:
        """Hollow nodes detected with exit code 2."""
        if not CONSISTENCY_VERIFIER.exists():
            pytest.skip("Verifier not implemented yet")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tree_path = Path(tmpdir) / "merkle_tree.json"
            create_tree_with_hollow_nodes(tree_path)
            
            exit_code, stdout, stderr = run_verifier(
                CONSISTENCY_VERIFIER,
                {"MERKLE_TREE_PATH": str(tree_path)},
            )
            
            assert exit_code == 2, f"Hollow nodes should fail with code 2: {stdout}{stderr}"
            assert "HOLLOW" in stdout or "HOLLOW" in stderr


class TestMerkleEvidence:
    """Tests for merkle evidence artifacts."""

    def test_evidence_schema(self) -> None:
        """Evidence has proper schema."""
        # Run verifiers to generate evidence
        if ROOT_VERIFIER.exists():
            run_verifier(ROOT_VERIFIER)
        
        evidence_path = Path("artifacts/certification/evidence/merkle_root_verifier.json")
        if evidence_path.exists():
            with open(evidence_path, "r", encoding="utf-8") as f:
                evidence = json.load(f)
            
            assert "verifier" in evidence
            assert "timestamp" in evidence
            assert "result" in evidence


class TestMerkleDepthRequirement:
    """RTC-REQ-122: Merkle tree depth >= 3."""

    def test_depth_validation(self) -> None:
        """Tree depth must be at least 3."""
        if not ROOT_VERIFIER.exists():
            pytest.skip("Verifier not implemented yet")
        
        # Valid tree has depth 3
        with tempfile.TemporaryDirectory() as tmpdir:
            tree_path = Path(tmpdir) / "merkle_tree.json"
            create_valid_merkle_tree(tree_path)
            
            exit_code, stdout, stderr = run_verifier(
                ROOT_VERIFIER,
                {"MERKLE_TREE_PATH": str(tree_path)},
            )
            
            assert exit_code == 0
            assert "Depth: 3" in stdout or "depth: 3" in str(stdout)


class TestMerkleCompleteness:
    """RTC-REQ-031: Merkle root non-empty and complete."""

    def test_root_hash_required(self) -> None:
        """Root hash must be present."""
        if not ROOT_VERIFIER.exists():
            pytest.skip("Verifier not implemented yet")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tree_path = Path(tmpdir) / "merkle_tree.json"
            
            # Tree without root_hash
            tree = {
                "root": {
                    "name": "root",
                    "children": [],
                },
            }
            tree_path.parent.mkdir(parents=True, exist_ok=True)
            with open(tree_path, "w", encoding="utf-8") as f:
                json.dump(tree, f)
            
            exit_code, stdout, stderr = run_verifier(
                ROOT_VERIFIER,
                {"MERKLE_TREE_PATH": str(tree_path)},
            )
            
            # Should fail due to missing root hash
            assert exit_code != 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
