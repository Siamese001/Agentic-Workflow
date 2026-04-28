"""Behavioral tests for react_prompt_provenance."""

from __future__ import annotations

import pytest

from agentic_core.react_prompt_provenance import build_prompt_provenance


def test_prompt_provenance_builds_expected_shape():
    provenance = build_prompt_provenance("tmpl-1", "hash-1", ("doc-a", "doc-b"))
    assert provenance.template_id == "tmpl-1"
    assert provenance.sources == ("doc-a", "doc-b")


def test_blank_template_rejected():
    with pytest.raises(ValueError):
        build_prompt_provenance("", "hash-1", tuple())
