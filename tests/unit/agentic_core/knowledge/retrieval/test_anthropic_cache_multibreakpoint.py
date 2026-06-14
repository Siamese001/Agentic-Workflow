"""Multi-breakpoint + workload-aware caching tests (P1 + P2 / W3).

Plan: prompt-cache-anthropic-best-practice-c7a1e9 (W3).

Covers: the renderer emitting a tuple of stability-tier boundary hints; per-tier
marker placement with the volatile tail never marked; the workload-aware
CacheStrategy gate on the per-query/documents tier; the 4-marker cap; and the
DualPassCitationOrchestrator threading cache_strategy + model through.
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from agentic_core.knowledge.retrieval.anthropic_cache_control import (
    CacheStrategy,
    build_messages_payload,
    build_user_content,
    caches_query_tier,
    count_cache_markers,
)
from agentic_core.knowledge.retrieval.anthropic_prompt_renderer import (
    render_anthropic_prompt,
)
from agentic_core.knowledge.retrieval.dual_pass_citation_orchestrator import (
    DualPassCitationOrchestrator,
)

_OPUS = "claude-opus-4-8"


def _fake_envelope(*, system: str, doc: str, abstain: bool = False):
    chunk = SimpleNamespace(content=doc, metadata={"title": "Doc"}, chunk_id="c1", is_must_use=True)
    return SimpleNamespace(
        abstain_recommended=abstain,
        system_blocks=[system] if system else [],
        verified_chunks=[chunk] if doc else [],
        task_spec="Answer the question.",
    )


# --------------------------------------------------------------------------- #
# Renderer — tuple of stability-tier boundary hints (P1)
# --------------------------------------------------------------------------- #


def test_render_emits_system_and_docs_hints():
    env = _fake_envelope(system="S" * 200, doc="D" * 200)
    r = render_anthropic_prompt(env, "the query")
    assert len(r.cache_boundary_hints) == 2
    h0, h1 = r.cache_boundary_hints
    assert 0 < h0 < h1 < len(r.text)
    # Tier 1 = system (no document tag); tier 2 spans the documents.
    assert "<document" not in r.text[:h0]
    assert "<document" in r.text[h0:h1]
    # Volatile tail carries the query, never a document boundary.
    assert "<query>" in r.text[h1:]
    # Back-compat scalar equals the last (documents) hint.
    assert r.cache_boundary_hint == h1


def test_render_docs_only_single_hint():
    env = _fake_envelope(system="", doc="D" * 200)
    r = render_anthropic_prompt(env, "q")
    assert r.cache_boundary_hints == (r.cache_boundary_hint,)
    assert len(r.cache_boundary_hints) == 1


def test_render_system_only_single_hint_scalar_minus_one():
    env = _fake_envelope(system="S" * 200, doc="")
    r = render_anthropic_prompt(env, "q")
    assert len(r.cache_boundary_hints) == 1
    assert r.cache_boundary_hint == -1  # no documents → scalar stays -1


def test_render_abstain_has_empty_hints():
    env = _fake_envelope(system="S" * 200, doc="D" * 200, abstain=True)
    r = render_anthropic_prompt(env, "q")
    assert r.cache_boundary_hints == ()
    assert r.cache_boundary_hint == -1


# --------------------------------------------------------------------------- #
# build_user_content — multi-tier placement
# --------------------------------------------------------------------------- #


def test_two_tiers_marked_tail_never_marked():
    prompt = "S" * 4000 + "D" * 4000 + "Q" * 100  # default floor 3500
    blocks = build_user_content(prompt, cache_boundary_hints=[4000, 8000], cache_query_tier=True)
    assert len(blocks) == 3
    assert "cache_control" in blocks[0]  # system tier
    assert "cache_control" in blocks[1]  # docs tier
    assert "cache_control" not in blocks[2]  # volatile tail


def test_one_shot_suppresses_docs_tier():
    prompt = "S" * 4000 + "D" * 4000 + "Q" * 100
    blocks = build_user_content(prompt, cache_boundary_hints=[4000, 8000], cache_query_tier=False)
    assert "cache_control" in blocks[0]  # stable system tier still cached
    assert "cache_control" not in blocks[1]  # volatile docs tier suppressed
    assert "cache_control" not in blocks[2]


def test_below_floor_tier_not_marked():
    # System tier (1000 chars) is below the 3500 default floor → no marker.
    prompt = "S" * 1000 + "D" * 4000 + "Q" * 100
    blocks = build_user_content(prompt, cache_boundary_hints=[1000, 5000], cache_query_tier=True)
    assert "cache_control" not in blocks[0]  # below floor
    assert "cache_control" in blocks[1]  # above floor


def test_below_model_floor_tier_not_marked_for_opus():
    # 4000-char tiers are below Opus's 16384-char floor → unmarked even when cached.
    prompt = "S" * 4000 + "D" * 4000 + "Q" * 100
    blocks = build_user_content(
        prompt, cache_boundary_hints=[4000, 8000], cache_query_tier=True, model=_OPUS
    )
    assert "cache_control" not in blocks[0]
    assert "cache_control" not in blocks[1]


def test_single_hint_falls_back_to_scalar_split():
    prompt = "S" * 4000 + "Q" * 100
    blocks = build_user_content(prompt, cache_boundary_hints=[4000])
    assert len(blocks) == 2  # scalar prefix + suffix
    assert "cache_control" in blocks[0]
    assert "cache_control" not in blocks[1]


def test_invalid_hints_ignored():
    prompt = "x" * 100
    # All out of range → single uncached block.
    blocks = build_user_content(prompt, cache_boundary_hints=[0, -1, 100, 999])
    assert blocks == [{"type": "text", "text": prompt}]


# --------------------------------------------------------------------------- #
# CacheStrategy + build_messages_payload
# --------------------------------------------------------------------------- #


def test_caches_query_tier_helper():
    assert caches_query_tier(CacheStrategy.ONE_SHOT) is False
    assert caches_query_tier(CacheStrategy.MULTI_TURN) is True
    assert caches_query_tier(CacheStrategy.HOT) is True
    assert caches_query_tier("one_shot") is False
    assert caches_query_tier("multi_turn") is True


def test_payload_one_shot_default_leaves_docs_unmarked():
    prompt = "S" * 4000 + "D" * 4000 + "Q" * 100
    payload = build_messages_payload(prompt, cache_boundary_hints=[4000, 8000])  # default ONE_SHOT
    assert count_cache_markers(payload) == 1  # system tier only


def test_payload_multi_turn_marks_both_tiers():
    prompt = "S" * 4000 + "D" * 4000 + "Q" * 100
    payload = build_messages_payload(
        prompt, cache_boundary_hints=[4000, 8000], cache_strategy=CacheStrategy.MULTI_TURN
    )
    assert count_cache_markers(payload) == 2


def test_marker_cap_drops_to_four():
    # system block (1) + 4 user tiers (HOT marks all) = 5 → capped to 4.
    prompt = "A" * 4000 + "B" * 4000 + "C" * 4000 + "D" * 4000 + "E" * 4000 + "Q" * 100
    payload = build_messages_payload(
        prompt,
        system_prompt="X" * 4000,
        cache_boundary_hints=[4000, 8000, 12000, 16000],
        cache_strategy=CacheStrategy.HOT,
    )
    assert count_cache_markers(payload) == 4


# --------------------------------------------------------------------------- #
# Orchestrator wiring — cache_strategy + model thread through to the payload
# --------------------------------------------------------------------------- #


def _capture_orchestrator(**kw):
    captured: dict = {}

    def pass1(payload):
        captured["payload"] = payload
        raise ValueError("stop after capture")  # short-circuit post-processing

    orch = DualPassCitationOrchestrator(pass1_fn=pass1, **kw)
    return orch, captured


def test_orchestrator_one_shot_marks_only_system_tier():
    orch, captured = _capture_orchestrator(cache_strategy=CacheStrategy.ONE_SHOT)
    env = _fake_envelope(system="S" * 5000, doc="D" * 5000)
    orch.execute(env, "the query")
    assert count_cache_markers(captured["payload"]) == 1  # docs tier suppressed


def test_orchestrator_multi_turn_marks_both_tiers():
    orch, captured = _capture_orchestrator(cache_strategy=CacheStrategy.MULTI_TURN)
    env = _fake_envelope(system="S" * 5000, doc="D" * 5000)
    orch.execute(env, "the query")
    assert count_cache_markers(captured["payload"]) == 2


def test_orchestrator_threads_model_floor():
    # model=opus → 5000-char tiers are below the 16384-char floor → 0 markers.
    orch, captured = _capture_orchestrator(cache_strategy=CacheStrategy.HOT, model=_OPUS)
    env = _fake_envelope(system="S" * 5000, doc="D" * 5000)
    orch.execute(env, "the query")
    assert count_cache_markers(captured["payload"]) == 0


def test_orchestrator_default_is_one_shot():
    orch, captured = _capture_orchestrator()  # no cache_strategy → ONE_SHOT
    env = _fake_envelope(system="S" * 5000, doc="D" * 5000)
    orch.execute(env, "the query")
    assert count_cache_markers(captured["payload"]) == 1
