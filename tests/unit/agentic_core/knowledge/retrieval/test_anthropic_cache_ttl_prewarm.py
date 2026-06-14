"""Per-tier TTL + pre-warming tests (P6 / W4).

Plan: prompt-cache-anthropic-best-practice-c7a1e9 (W4).

Covers: stable tiers at 1h / volatile docs tier at 5m; the max_tokens=0 pre-warm
payload (marks the stable block, never the placeholder); the needs_rewarm
predicate; and the orchestrator defaulting stable tiers to 1h.
"""

from __future__ import annotations

from types import SimpleNamespace

from agentic_core.knowledge.retrieval.anthropic_cache_control import (
    CACHE_TTL_1H,
    CACHE_TTL_5M,
    CacheStrategy,
    build_messages_payload,
    build_prewarm_payload,
    build_user_content,
    needs_rewarm,
    ttl_seconds,
)
from agentic_core.knowledge.retrieval.dual_pass_citation_orchestrator import (
    DualPassCitationOrchestrator,
)

_EPHEMERAL_5M = {"type": "ephemeral"}
_EPHEMERAL_1H = {"type": "ephemeral", "ttl": "1h"}


# --------------------------------------------------------------------------- #
# Per-tier TTL
# --------------------------------------------------------------------------- #


def test_stable_ttl_routes_per_tier():
    prompt = "S" * 4000 + "D" * 4000 + "Q" * 100
    blocks = build_user_content(
        prompt, cache_boundary_hints=[4000, 8000], cache_query_tier=True,
        ttl=CACHE_TTL_5M, stable_ttl=CACHE_TTL_1H,
    )
    assert blocks[0]["cache_control"] == _EPHEMERAL_1H  # stable system tier → 1h
    assert blocks[1]["cache_control"] == _EPHEMERAL_5M  # volatile docs tier → 5m
    assert "cache_control" not in blocks[2]  # tail


def test_stable_ttl_none_uses_ttl_everywhere():
    prompt = "S" * 4000 + "D" * 4000 + "Q" * 100
    blocks = build_user_content(
        prompt, cache_boundary_hints=[4000, 8000], cache_query_tier=True, ttl=CACHE_TTL_5M
    )  # stable_ttl defaults to None → 5m everywhere (back-compat)
    assert blocks[0]["cache_control"] == _EPHEMERAL_5M
    assert blocks[1]["cache_control"] == _EPHEMERAL_5M


def test_payload_system_block_uses_stable_ttl():
    prompt = "S" * 4000 + "D" * 4000 + "Q" * 100
    payload = build_messages_payload(
        prompt,
        system_prompt="X" * 4000,
        cache_boundary_hints=[4000, 8000],
        cache_strategy=CacheStrategy.MULTI_TURN,
        ttl=CACHE_TTL_5M,
        stable_ttl=CACHE_TTL_1H,
    )
    assert payload["system"][0]["cache_control"] == _EPHEMERAL_1H  # separate system block → 1h
    user = payload["messages"][0]["content"]
    assert user[0]["cache_control"] == _EPHEMERAL_1H  # stable system tier → 1h
    assert user[1]["cache_control"] == _EPHEMERAL_5M  # docs tier → 5m


# --------------------------------------------------------------------------- #
# Pre-warming (max_tokens=0)
# --------------------------------------------------------------------------- #


def test_prewarm_marks_system_not_placeholder():
    payload = build_prewarm_payload(system_prompt="S" * 4000)
    assert payload["max_tokens"] == 0
    assert payload["system"][0]["cache_control"] == _EPHEMERAL_1H  # default 1h
    placeholder = payload["messages"][0]["content"][-1]
    assert "cache_control" not in placeholder  # placeholder never marked
    assert placeholder["text"] == "warmup"


def test_prewarm_marks_stable_user_prefix_not_placeholder():
    payload = build_prewarm_payload(stable_user_prefix="P" * 4000, system_prompt="")
    content = payload["messages"][0]["content"]
    assert content[0]["cache_control"] == _EPHEMERAL_1H  # stable prefix marked
    assert "cache_control" not in content[1]  # placeholder unmarked
    assert "system" not in payload  # no system block


def test_prewarm_below_floor_not_marked():
    payload = build_prewarm_payload(system_prompt="S" * 100)  # below 3500 default floor
    assert payload["max_tokens"] == 0
    assert "cache_control" not in payload["system"][0]


def test_prewarm_respects_5m_ttl_override():
    payload = build_prewarm_payload(system_prompt="S" * 4000, ttl=CACHE_TTL_5M)
    assert payload["system"][0]["cache_control"] == _EPHEMERAL_5M


# --------------------------------------------------------------------------- #
# ttl_seconds / needs_rewarm
# --------------------------------------------------------------------------- #


def test_ttl_seconds():
    assert ttl_seconds(CACHE_TTL_5M) == 300
    assert ttl_seconds(CACHE_TTL_1H) == 3600
    assert ttl_seconds("nonsense") == 300


def test_needs_rewarm():
    assert needs_rewarm(100, CACHE_TTL_5M) is False  # within window
    assert needs_rewarm(400, CACHE_TTL_5M) is True  # gap exceeds 5m
    assert needs_rewarm(3000, CACHE_TTL_1H) is False
    assert needs_rewarm(4000, CACHE_TTL_1H) is True
    assert needs_rewarm(4000) is True  # default ttl=1h


# --------------------------------------------------------------------------- #
# Orchestrator — stable tiers default to 1h, docs stays 5m
# --------------------------------------------------------------------------- #


def _fake_envelope(*, system: str, doc: str):
    chunk = SimpleNamespace(content=doc, metadata={"title": "Doc"}, chunk_id="c1", is_must_use=True)
    return SimpleNamespace(
        abstain_recommended=False,
        system_blocks=[system],
        verified_chunks=[chunk],
        task_spec="Answer the question.",
    )


def test_orchestrator_defaults_stable_tier_to_1h():
    captured: dict = {}

    def pass1(payload):
        captured["payload"] = payload
        raise ValueError("stop after capture")

    orch = DualPassCitationOrchestrator(pass1_fn=pass1, cache_strategy=CacheStrategy.MULTI_TURN)
    orch.execute(_fake_envelope(system="S" * 5000, doc="D" * 5000), "the query")
    content = captured["payload"]["messages"][0]["content"]
    assert content[0]["cache_control"] == _EPHEMERAL_1H  # stable system tier → 1h (default)
    assert content[1]["cache_control"] == _EPHEMERAL_5M  # volatile docs tier → 5m
