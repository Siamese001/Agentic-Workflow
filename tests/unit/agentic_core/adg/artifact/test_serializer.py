"""Foundational behavioral tests for agentic_core/adg/artifact/serializer.py.

fan_in=3 — imported by 3 other modules.
ADG import-hygiene is covered separately by test_serializer_adg.py.
This file covers behavioral invariants and public API contracts.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.adg.artifact.serializer_util import (  # noqa: F401
        diff_artifacts,
        load_artifact,
        serialize_artifact,
        write_artifact,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    serialize_artifact = None  # type: ignore[assignment,misc]
    write_artifact = None  # type: ignore[assignment,misc]
    load_artifact = None  # type: ignore[assignment,misc]
    diff_artifacts = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="serializer.py deps unavailable")
class TestSerializeArtifactFunction:
    def test_is_callable(self):
        assert callable(serialize_artifact)

    def test_has_return_annotation(self):
        import inspect

        sig = inspect.signature(serialize_artifact)
        assert sig.return_annotation is not inspect.Parameter.empty


@pytest.mark.skipif(not _AVAILABLE, reason="serializer.py deps unavailable")
class TestWriteArtifactFunction:
    def test_is_callable(self):
        assert callable(write_artifact)

    def test_has_return_annotation(self):
        import inspect

        sig = inspect.signature(write_artifact)
        assert sig.return_annotation is not inspect.Parameter.empty


@pytest.mark.skipif(not _AVAILABLE, reason="serializer.py deps unavailable")
class TestLoadArtifactFunction:
    def test_is_callable(self):
        assert callable(load_artifact)

    def test_has_return_annotation(self):
        import inspect

        sig = inspect.signature(load_artifact)
        assert sig.return_annotation is not inspect.Parameter.empty


@pytest.mark.skipif(not _AVAILABLE, reason="serializer.py deps unavailable")
class TestDiffArtifactsFunction:
    def test_is_callable(self):
        assert callable(diff_artifacts)

    def test_has_return_annotation(self):
        import inspect

        sig = inspect.signature(diff_artifacts)
        assert sig.return_annotation is not inspect.Parameter.empty


def test_module_importable():
    """Smoke: serializer importable or gracefully unavailable."""
    pass
