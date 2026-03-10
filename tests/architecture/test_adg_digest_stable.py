"""Phase 7.1: ADG Determinism test -- digest is stable across two invocations.

Markers: architecture, determinism
"""

from __future__ import annotations

from pathlib import Path

import pytest

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

REPO_ROOT = Path(__file__).parent.parent.parent


@pytest.mark.architecture
@pytest.mark.determinism
def test_adg_digest_stable_two_runs() -> None:
    """Scanner digest must be identical across two independent invocations."""
    from agentic_core.adg.extraction.static_scanner import ADGStaticScanner

    scanner = ADGStaticScanner(repo_root=REPO_ROOT)
    result_1 = scanner.scan(commit_sha="test-run-1")
    result_2 = scanner.scan(commit_sha="test-run-2")

    assert result_1.digest, "First scan produced empty digest"
    assert result_2.digest, "Second scan produced empty digest"
    assert result_1.digest == result_2.digest, (
        f"Digest mismatch:\n  run1: {result_1.digest}\n  run2: {result_2.digest}\n"
        f"  edges1: {len(result_1.edges)}\n  edges2: {len(result_2.edges)}"
    )


@pytest.mark.architecture
@pytest.mark.determinism
def test_adg_digest_is_sha256_hex() -> None:
    """Digest must be a 64-character lowercase hex string (SHA-256)."""
    from agentic_core.adg.extraction.static_scanner import ADGStaticScanner

    scanner = ADGStaticScanner(repo_root=REPO_ROOT)
    result = scanner.scan(commit_sha="test-digest-format")

    assert len(result.digest) == 64, f"Expected 64-char hex, got: {result.digest!r}"
    assert result.digest == result.digest.lower(), "Digest must be lowercase"
    assert all(c in "0123456789abcdef" for c in result.digest)


@pytest.mark.architecture
@pytest.mark.determinism
def test_adg_edge_list_sorted() -> None:
    """Edge list in ScanResult must be in stable sorted order."""
    from agentic_core.adg.extraction.static_scanner import ADGStaticScanner

    scanner = ADGStaticScanner(repo_root=REPO_ROOT)
    result = scanner.scan(commit_sha="test-sort")

    assert len(result.edges) > 0, "Expected at least one edge from scan"
    for i in range(len(result.edges) - 1):
        a = result.edges[i]
        b = result.edges[i + 1]
        assert a <= b, f"Edge list not sorted at index {i}:\n  [{i}]: {a}\n  [{i + 1}]: {b}"


@pytest.mark.architecture
@pytest.mark.determinism
def test_adg_modules_sorted() -> None:
    """Module list must be in deterministic sorted order."""
    from agentic_core.adg.extraction.static_scanner import ADGStaticScanner

    scanner = ADGStaticScanner(repo_root=REPO_ROOT)
    result = scanner.scan(commit_sha="test-modules-sort")

    assert result.modules == sorted(result.modules), "Module list is not sorted"


@pytest.mark.architecture
@pytest.mark.determinism
def test_adg_canonical_edge_text_stable() -> None:
    """canonical_edge_text() must produce identical output on two calls."""
    from agentic_core.adg.extraction.static_scanner import ADGStaticScanner

    scanner = ADGStaticScanner(repo_root=REPO_ROOT)
    result = scanner.scan(commit_sha="test-text-stable")

    text_1 = result.canonical_edge_text()
    text_2 = result.canonical_edge_text()
    assert text_1 == text_2, "canonical_edge_text() is not idempotent"


@pytest.mark.architecture
@pytest.mark.determinism
def test_adg_scan_files_subset_digest_differs_from_full() -> None:
    """Scanning a subset of files must produce a different digest than full scan."""
    from agentic_core.adg.extraction.static_scanner import ADGStaticScanner

    scanner = ADGStaticScanner(repo_root=REPO_ROOT)
    full_result = scanner.scan(commit_sha="full")
    subset_result = scanner.scan_files(
        ["agentic_core/L2_execution/UniversalWriteGateway.py"],
        commit_sha="subset",
    )
    assert full_result.digest != subset_result.digest, (
        "Subset scan should produce a different digest from full scan"
    )
