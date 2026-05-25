"""Targeting publish helpers for executive_summary."""

from __future__ import annotations

import json
from pathlib import Path

from apps_rg.runtime.targeting_context_authority import (
    GenerationMaterialContext,
    material_targeting_digest,
)
from apps_rg.runtime.sections.executive_summary_targeting_publish import (
    audit_judge_packet_targeting_digests,
    parity_allows_judge_regen,
    resolve_judge_packet_for_parity,
)


def test_resolve_judge_packet_prefers_post_x2(tmp_path: Path) -> None:
    initial = {"targeting_context": {"jd_text": "a", "briefing": "b"}}
    post = {"targeting_context": {"jd_text": "a", "briefing": "post"}}
    (tmp_path / "executive_summary_judge_packet.json").write_text(
        json.dumps(initial), encoding="utf-8"
    )
    (tmp_path / "executive_summary_judge_packet_post_x2.json").write_text(
        json.dumps(post), encoding="utf-8"
    )
    resolved = resolve_judge_packet_for_parity(tmp_path, fallback=initial)
    assert resolved["targeting_context"]["briefing"] == "post"


def test_parity_allows_judge_regen() -> None:
    ok, _ = parity_allows_judge_regen({"targeting_context_parity": {"parity_match": True}})
    assert ok is True
    bad, reason = parity_allows_judge_regen({"targeting_context_parity": {"parity_match": False}})
    assert bad is False
    assert "false" in reason


def test_audit_judge_packets_match_generation(tmp_path: Path) -> None:
    jd, br = "jd-x", "br-x"
    digest = material_targeting_digest(jd, br)
    gen = GenerationMaterialContext(jd, br, digest)
    packet = {"targeting_context": {"jd_text": jd, "briefing": br}}
    (tmp_path / "executive_summary_judge_packet.json").write_text(
        json.dumps(packet), encoding="utf-8"
    )
    audit = audit_judge_packet_targeting_digests(tmp_path, generation_material=gen)
    assert audit["all_packets_match_generation"] is True
