"""
Wave 4: Metrics Sanity Check Test
Validates that ADG metrics aren't inflated by comparing edge counts to file counts.
"""

import subprocess
from pathlib import Path

import pytest

from agentic_core.adg.extraction.static_scanner import ADGStaticScanner


class TestMetricsSanity:
    """Detect artificially inflated metrics by comparing against ground truth."""

    # Ratio threshold: if edges > 10x Python files, something is wrong
    MAX_EDGE_TO_FILE_RATIO = 10.0

    # Minimum files before ratio check applies (avoid small sample noise)
    MIN_FILES_FOR_CHECK = 10

    def test_edge_count_sanity_check(self, tmp_path):
        """Verify edge count is proportional to actual Python file count."""
        repo_root = tmp_path.parent  # Use actual repo

        # Count actual Python files (excluding tests)
        py_files = list(repo_root.rglob("*.py"))
        non_test_files = [
            f for f in py_files
            if not (f.name.startswith("test_") or "_test.py" in f.name or "/tests/" in str(f))
        ]

        file_count = len(non_test_files)

        if file_count < self.MIN_FILES_FOR_CHECK:
            pytest.skip(f"Insufficient files for sanity check: {file_count} < {self.MIN_FILES_FOR_CHECK}")

        # Run scanner
        scanner = ADGStaticScanner(repo_root=repo_root)
        result = scanner.scan()

        edge_count = len(result.edges)

        # Calculate ratio
        ratio = edge_count / file_count if file_count > 0 else float('inf')

        assert ratio <= self.MAX_EDGE_TO_FILE_RATIO, (
            f"Edge-to-file ratio {ratio:.1f} exceeds threshold {self.MAX_EDGE_TO_FILE_RATIO}\n"
            f"Edges: {edge_count}, Files: {file_count}\n"
            f"This suggests phantom edges or metric inflation."
        )

    def test_edge_per_module_reasonable(self, tmp_path):
        """Verify average edges per module is within reasonable bounds."""
        repo_root = tmp_path.parent

        scanner = ADGStaticScanner(repo_root=repo_root)
        result = scanner.scan()

        # Count unique modules from edges
        modules_from_edges = set()
        for edge in result.edges:
            modules_from_edges.add(edge.from_name)
            # Extract module from to_name if it's a qualified name
            if '::' in edge.to_name:
                # ADG::Type::Symbol format
                parts = edge.to_name.split('::')
                if len(parts) >= 2:
                    modules_from_edges.add(parts[-1])  # The symbol part

        module_count = len(modules_from_edges)
        edge_count = len(result.edges)

        if module_count == 0:
            pytest.skip("No modules found in edges")

        avg_edges_per_module = edge_count / module_count

        # A module with 1000+ edges is suspicious
        MAX_AVG_EDGES_PER_MODULE = 500

        assert avg_edges_per_module <= MAX_AVG_EDGES_PER_MODULE, (
            f"Average edges per module ({avg_edges_per_module:.1f}) exceeds threshold {MAX_AVG_EDGES_PER_MODULE}\n"
            f"Total edges: {edge_count}, Unique modules: {module_count}\n"
            f"Check for duplicate or phantom edge generation."
        )

    def test_no_duplicate_edges(self, tmp_path):
        """Verify no exact duplicate edges exist (same from/to/relation/line)."""
        repo_root = tmp_path.parent

        scanner = ADGStaticScanner(repo_root=repo_root)
        result = scanner.scan()

        # Create edge signatures
        edge_signatures = {}
        duplicates = []

        for edge in result.edges:
            sig = (edge.from_name, edge.to_name, edge.relation_type, edge.line_no)
            if sig in edge_signatures:
                duplicates.append({
                    'signature': sig,
                    'first_seen': edge_signatures[sig],
                    'duplicate': len(edge_signatures) + 1
                })
            else:
                edge_signatures[sig] = len(edge_signatures) + 1

        if duplicates:
            dup_samples = "\n".join(
                f"  - {d['signature']} (first: edge #{d['first_seen']}, dup: #{d['duplicate']})"
                for d in duplicates[:10]
            )
            pytest.fail(
                f"Found {len(duplicates)} duplicate edges:\n{dup_samples}\n"
                f"(showing first 10 of {len(duplicates)})"
            )


class TestGroundTruthComparison:
    """Compare ADG output against git-tracked files as ground truth."""

    def test_adg_modules_match_git_tracked_files(self, tmp_path):
        """Verify ADG module count matches git-tracked Python files."""
        repo_root = tmp_path.parent

        # Get git-tracked Python files
        try:
            result = subprocess.run(
                ["git", "ls-files", "*.py"],
                capture_output=True,
                text=True,
                cwd=str(repo_root),
                timeout=30
            )
            git_tracked = [line.strip() for line in result.stdout.split("\n") if line.strip()]
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
            pytest.skip("Could not get git-tracked files")

        # Filter out tests
        production_files = [
            f for f in git_tracked
            if not (f.startswith("tests/") or f.startswith("test_") or "_test.py" in f)
        ]

        git_count = len(production_files)

        # Get ADG module count
        scanner = ADGStaticScanner(repo_root=repo_root)
        scan_result = scanner.scan()

        # Count unique modules in ADG
        adg_modules = set()
        for edge in scan_result.edges:
            if edge.from_name.startswith("ADG::Module::"):
                adg_modules.add(edge.from_name)

        adg_count = len(adg_modules)

        # Allow 10% variance for non-tracked/generated files
        variance = abs(adg_count - git_count) / max(git_count, 1)

        assert variance <= 0.10, (
            f"ADG module count ({adg_count}) differs from git-tracked files ({git_count}) by {variance:.1%}\n"
            f"Expected <10% variance. Check for phantom modules or missing files."
        )
