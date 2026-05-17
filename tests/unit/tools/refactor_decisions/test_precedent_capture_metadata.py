"""precedent_capture_metadata — subprocess fail-soft paths."""

from __future__ import annotations

from unittest.mock import MagicMock

import tools.refactor_decisions.precedent_capture_metadata as pcm


def test_compute_skips_lookup_when_intent_empty(monkeypatch):
    monkeypatch.setattr(pcm, "subprocess", MagicMock())  # should not run
    out = pcm.compute_precedent_capture_metadata(
        "refactor_scope",
        "",
        "tools/foo",
        layer="tools",
        degraded_scope=False,
        sidecar=None,
    )
    assert out["precedent_lookup_ok"] is False
    assert out["precedent_lookup_query_digest"]
    assert out["precedent_top_match_ids_json"] == "[]"


def test_compute_lookup_ok_sets_flag(monkeypatch):
    class Proc:
        returncode = 0
        stdout = '{"verdict":"none","matches":[],"reason":"x"}'

    monkeypatch.setattr(pcm.subprocess, "run", lambda *_a, **_kw: Proc())
    out = pcm.compute_precedent_capture_metadata(
        "refactor_scope",
        "intent-a",
        "tools/foo",
        layer="tools",
        degraded_scope=False,
        sidecar=None,
    )
    assert out["precedent_lookup_ok"] is True
    assert out["precedent_verdict_from_lookup"] == "none"
    assert out["precedent_match_count"] == 0
