#!/usr/bin/env python3
"""
Test suite for FileClassificationAgent.
"""

import textwrap
from pathlib import Path

import pytest


def test_fileclassificationagent_basic_functionality():
    """Test basic functionality of FileClassificationAgent."""
    # TODO: Implement actual test based on module functionality
    assert True  # Placeholder


def test_fileclassificationagent_edge_cases():
    """Test edge cases for FileClassificationAgent."""
    # TODO: Test edge cases and boundary conditions
    assert True  # Placeholder


def test_fileclassificationagent_error_scenarios():
    """Test error scenarios for FileClassificationAgent."""
    # TODO: Test error handling and failure modes
    assert True  # Placeholder


# ---------------------------------------------------------------------------
# Semantic duplicate detection tests (RCA: IBlackboardLeaseVerifier duplication)
# ---------------------------------------------------------------------------


@pytest.fixture
def fca_instance(tmp_path):
    """Create a minimal FileClassificationAgent scoped to tmp_path."""
    from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
        FileClassificationAgent,
    )

    return FileClassificationAgent(
        project_root=tmp_path,
        dry_run=True,
        validate_only=True,
    )


def _write(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content), encoding="utf-8")
    return path


class TestSemanticDuplicateDetection:
    """Tests for _detect_semantic_duplicates — the fix for the
    IBlackboardLeaseVerifier / IBlackboardLeaseVerifierProtocol duplication."""

    def test_detects_pascal_vs_snake_same_class(self, fca_instance, tmp_path):
        """Two files in same dir with normalised-equivalent primary class → flagged."""
        d = tmp_path / "interfaces"
        f1 = _write(
            d / "IFooProtocol.py",
            """\
            from typing import Protocol
            class IFoo(Protocol):
                def bar(self) -> None: ...
            """,
        )
        f2 = _write(
            d / "IFoo.py",
            """\
            from typing import Protocol
            class foo(Protocol):
                def bar(self) -> None: ...
            """,
        )
        violations = fca_instance._detect_semantic_duplicates([f1, f2])
        assert len(violations) == 1
        assert violations[0]["type"] == "SEMANTIC_DUPLICATE"

    def test_no_false_positive_different_classes(self, fca_instance, tmp_path):
        """Two files in same dir with genuinely different primary classes → NOT flagged."""
        d = tmp_path / "interfaces"
        f1 = _write(
            d / "IAlpha.py",
            """\
            from typing import Protocol
            class IAlpha(Protocol):
                def run(self) -> None: ...
            """,
        )
        f2 = _write(
            d / "IBeta.py",
            """\
            from typing import Protocol
            class IBeta(Protocol):
                def run(self) -> None: ...
            """,
        )
        violations = fca_instance._detect_semantic_duplicates([f1, f2])
        assert len(violations) == 0

    def test_no_false_positive_different_directories(self, fca_instance, tmp_path):
        """Same class name in different directories → NOT flagged (cross-dir is
        handled by the existing exact-filename duplicate detector)."""
        d1 = tmp_path / "interfaces"
        d2 = tmp_path / "types"
        f1 = _write(
            d1 / "IFooProtocol.py",
            """\
            from typing import Protocol
            class IFoo(Protocol):
                def bar(self) -> None: ...
            """,
        )
        f2 = _write(
            d2 / "IFoo.py",
            """\
            from typing import Protocol
            class IFoo(Protocol):
                def bar(self) -> None: ...
            """,
        )
        violations = fca_instance._detect_semantic_duplicates([f1, f2])
        assert len(violations) == 0

    def test_canonical_prefers_more_importers(self, fca_instance, tmp_path):
        """The file referenced by more other files wins canonical status."""
        d = tmp_path / "interfaces"
        canonical = _write(
            d / "IBarProtocol.py",
            """\
            from typing import Protocol
            class IBar(Protocol):
                def baz(self) -> None: ...
            """,
        )
        duplicate = _write(
            d / "IBar.py",
            """\
            from typing import Protocol
            class bar(Protocol):
                def baz(self) -> None: ...
            """,
        )
        # A consumer that imports only the canonical
        consumer = _write(
            tmp_path / "consumer.py",
            """\
            from interfaces.IBarProtocol import IBar
            """,
        )
        violations = fca_instance._detect_semantic_duplicates([canonical, duplicate, consumer])
        assert len(violations) == 1
        v = violations[0]
        assert v["canonical_path"] == str(canonical)
        assert v["duplicate_path"] == str(duplicate)

    def test_blackboard_regression(self, tmp_path, fca_instance):
        """Regression: the exact scenario that created the original duplication."""
        d = tmp_path / "interfaces"
        protocol = _write(
            d / "IBlackboardLeaseVerifierProtocol.py",
            """\
            from typing import Protocol
            class IBlackboardLeaseVerifier(Protocol):
                def verify(self) -> bool: ...
            """,
        )
        bad_copy = _write(
            d / "IBlackboardLeaseVerifier.py",
            """\
            from typing import Protocol
            class blackboard_lease_verifier(Protocol):
                def verify(self) -> bool: ...
            """,
        )
        violations = fca_instance._detect_semantic_duplicates([protocol, bad_copy])
        assert len(violations) == 1
        assert violations[0]["type"] == "SEMANTIC_DUPLICATE"
        # The Protocol version should win (more importers or shorter name)

    def test_skips_test_files(self, fca_instance, tmp_path):
        """Test files (test_*.py) should be excluded from semantic duplicate detection."""
        d = tmp_path / "interfaces"
        f1 = _write(
            d / "IFoo.py",
            """\
            class IFoo:
                pass
            """,
        )
        f2 = _write(
            d / "test_IFoo.py",
            """\
            class IFoo:
                pass
            """,
        )
        violations = fca_instance._detect_semantic_duplicates([f1, f2])
        assert len(violations) == 0
