"""Canonical judge contract hash parity across provider transport wiring."""

from __future__ import annotations

import inspect

from apps_rg.runtime.judges.executive_summary_x1d import (
    _call_anthropic,
    _call_gemini,
    _call_openai,
    build_x1d_judge_system_prompt,
)
from apps_rg.runtime.judges.executive_summary_judge_packet import (
    judge_contract_hash,
    render_judge_prompt_from_packet,
)
from apps_rg.runtime.sections.executive_summary_x1d_judge_contract import (
    build_brown_brown_six_sentence_packet,
)


def test_canonical_contract_hash_in_rendered_prompt() -> None:
    packet = build_brown_brown_six_sentence_packet()
    expected = judge_contract_hash(packet)
    prompt = render_judge_prompt_from_packet(packet)
    assert f"JUDGE_CONTRACT_HASH: {expected}" in prompt


def test_all_providers_use_shared_system_prompt_builder() -> None:
    canonical_system = build_x1d_judge_system_prompt(compact=True)
    assert "score_scale" in canonical_system
    for fn in (_call_openai, _call_anthropic, _call_gemini):
        src = inspect.getsource(fn)
        assert "build_x1d_judge_system_prompt" in src or "JUDGE_SCORE_SCHEMA" in src
