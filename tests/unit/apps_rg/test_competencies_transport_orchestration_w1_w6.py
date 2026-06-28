"""Unit + contract tests for the competencies transport/orchestration finish fix (W1–W6).

Covers the plan acceptance criteria WITHOUT touching the network:

* W1 — centralized timeout policy (operator-set budgets are honored up to a bounded ceiling;
  invalid env falls back safely).
* W2 — streamed Anthropic transport records progress/timing metadata; a slow-then-stalled call
  surfaces last-progress on timeout; a successful call still returns ``REAL_LLM``.
* W3 — the Claude pool selector resolves its own timeout env and writes an honest
  lifecycle receipt.
* W4 — per-path progress receipt is written BEFORE the first path completes and updated per path.
* W5/W6 — closeout mode is explicit/auditable and NEVER weakens the competencies contract (still 8
  final categories, graph-only proof authority, unchanged min selection score, X2/X3 unaffected).
"""
from __future__ import annotations

import json
import types

import pytest

from apps_rg.runtime.providers import external_provider as ep
from apps_rg.runtime.providers.external_provider import (
    DEFAULT_EXTERNAL_PROVIDER_TIMEOUT_SECONDS,
    ExternalProvider,
    external_provider_timeout_max_s,
    resolve_external_section_timeout_s,
)
from apps_rg.runtime.providers.provider_gateway import ProviderProfile


# --------------------------------------------------------------------------------------------------
# W1 — timeout resolver
# --------------------------------------------------------------------------------------------------
def test_w1_resolver_honors_budget_within_ceiling(monkeypatch):
    monkeypatch.delenv("APPS_RG_EXTERNAL_PROVIDER_TIMEOUT_MAX_SECONDS", raising=False)
    assert resolve_external_section_timeout_s(180) == 180.0


def test_w1_resolver_bounded_by_ceiling(monkeypatch):
    monkeypatch.delenv("APPS_RG_EXTERNAL_PROVIDER_TIMEOUT_MAX_SECONDS", raising=False)
    assert resolve_external_section_timeout_s(99999) == 300.0  # default ceiling


def test_w1_resolver_invalid_falls_back_to_default(monkeypatch):
    monkeypatch.delenv("APPS_RG_EXTERNAL_PROVIDER_TIMEOUT_MAX_SECONDS", raising=False)
    assert resolve_external_section_timeout_s("not-a-number") == DEFAULT_EXTERNAL_PROVIDER_TIMEOUT_SECONDS
    assert resolve_external_section_timeout_s(0) == DEFAULT_EXTERNAL_PROVIDER_TIMEOUT_SECONDS
    assert resolve_external_section_timeout_s(None) == DEFAULT_EXTERNAL_PROVIDER_TIMEOUT_SECONDS


def test_w1_ceiling_env_override(monkeypatch):
    monkeypatch.setenv("APPS_RG_EXTERNAL_PROVIDER_TIMEOUT_MAX_SECONDS", "180")
    assert external_provider_timeout_max_s() == 180.0
    assert resolve_external_section_timeout_s(170) == 170.0
    assert resolve_external_section_timeout_s(250) == 180.0

    # Hard upper bound protects against a hostile/typo value turning into an extended hang.
    monkeypatch.setenv("APPS_RG_EXTERNAL_PROVIDER_TIMEOUT_MAX_SECONDS", "999999")
    assert external_provider_timeout_max_s() == 300.0


def test_w1_ceiling_malformed_falls_back(monkeypatch):
    monkeypatch.setenv("APPS_RG_EXTERNAL_PROVIDER_TIMEOUT_MAX_SECONDS", "garbage")
    assert external_provider_timeout_max_s() == 300.0


def test_w1_competencies_chat_timeout_caps_extended_budget(monkeypatch):
    from apps_rg.runtime.providers.competencies_live_provider_gate import (
        competencies_provider_chat_timeout_s,
    )

    monkeypatch.delenv("APPS_RG_EXTERNAL_PROVIDER_TIMEOUT_MAX_SECONDS", raising=False)
    monkeypatch.setenv("APPS_RG_COMPETENCIES_CHAT_TIMEOUT_SECONDS", "1000")
    assert competencies_provider_chat_timeout_s() == 300

    monkeypatch.delenv("APPS_RG_COMPETENCIES_CHAT_TIMEOUT_SECONDS", raising=False)
    assert competencies_provider_chat_timeout_s() == 120  # default for normal runs stays bounded


def test_competencies_output_budget_covers_structured_candidate_json():
    from apps_rg.runtime.sections.competencies_lane_defaults import (
        COMPETENCIES_MAX_OUTPUT_TOKENS,
    )

    assert COMPETENCIES_MAX_OUTPUT_TOKENS >= 6000


# --------------------------------------------------------------------------------------------------
# W2 — transport timing metadata + last-progress on timeout
# --------------------------------------------------------------------------------------------------
class _FakeSSEResponse:
    def __init__(self, lines):
        self._lines = lines

    def __enter__(self):
        return iter(self._lines)

    def __exit__(self, *exc):
        return False


def test_w2_stream_transport_records_timing_and_progress(monkeypatch):
    lines = [
        b'data: {"type":"message_start","message":{"model":"claude-x","usage":{"input_tokens":5}}}\n',
        b'data: {"type":"content_block_delta","delta":{"type":"text_delta","text":"{\\"competencies\\":[]}"}}\n',
        b'data: {"type":"message_delta","usage":{"output_tokens":7}}\n',
        b'data: {"type":"message_stop"}\n',
    ]
    monkeypatch.setattr(ep.urllib.request, "urlopen", lambda req, timeout=None: _FakeSSEResponse(lines))

    prov = ExternalProvider(
        provider_profile=ProviderProfile.EXTERNAL_CLAUDE,
        environ={"ANTHROPIC_API_KEY": "k"},
    )
    sink: dict = {}
    out = prov._anthropic_messages_transport(
        {"prompt": "hi", "model": "m", "max_tokens": 50, "temperature": 0.0, "progress_sink": sink}
    )
    timing = out["transport_timing"]
    assert timing["chunk_count"] == 4
    assert timing["read_iterations"] == 4
    assert timing["raw_output_chars"] > 0
    assert timing["first_byte_after_s"] is not None
    assert timing["completed_after_s"] is not None
    # The caller-owned sink is populated in place so a timeout could read it.
    assert sink["completed"] is True
    assert sink["raw_output_chars"] > 0
    assert sink["chunk_count"] == 4


def test_w2_generate_success_returns_real_llm_and_surfaces_timing():
    def fake_transport(req):
        return {"text": '{"competencies":[]}', "model": "claude-x", "transport_timing": {"chunk_count": 3}}

    prov = ExternalProvider(
        provider_profile=ProviderProfile.EXTERNAL_CLAUDE,
        environ={"ANTHROPIC_API_KEY": "k"},
        transport=fake_transport,
    )
    compiled = types.SimpleNamespace(prompt_blocks=(), system_preamble="sys", user_instruction="hi")
    res = prov.generate(compiled, token_budget=100, temperature=0.0, timeout_seconds=1000)
    assert res.runtime_generation_status == "REAL_LLM"
    assert res.provider_response["transport_timing"] == {"chunk_count": 3}
    assert res.provider_response["effective_timeout_seconds"] == 300.0


def test_w2_generate_timeout_surfaces_last_progress():
    def stalling_transport(req):
        sink = req.get("progress_sink")
        if isinstance(sink, dict):
            sink.update({"last_progress_after_s": 5.0, "raw_output_chars": 42, "chunk_count": 3})
        raise TimeoutError("simulated mid-stream stall")

    prov = ExternalProvider(
        provider_profile=ProviderProfile.EXTERNAL_CLAUDE,
        environ={"ANTHROPIC_API_KEY": "k"},
        transport=stalling_transport,
    )
    compiled = types.SimpleNamespace(prompt_blocks=(), system_preamble="sys", user_instruction="hi")
    res = prov.generate(compiled, token_budget=100, temperature=0.0, timeout_seconds=30)
    assert res.runtime_generation_status == "BLOCKED"
    assert "chars_received=42" in (res.exact_provider_error or "")
    assert res.provider_response["transport_progress"]["raw_output_chars"] == 42


# --------------------------------------------------------------------------------------------------
# W3 — selector timeout + honest receipt
# --------------------------------------------------------------------------------------------------
def test_w3_selector_timeout_env_resolved(monkeypatch):
    import apps_rg.runtime.judges.bullet_pool_claude_selector as sel

    monkeypatch.delenv("APPS_RG_EXTERNAL_PROVIDER_TIMEOUT_MAX_SECONDS", raising=False)
    monkeypatch.delenv("APPS_RG_POOL_SELECTOR_TIMEOUT_SECONDS", raising=False)
    assert sel.pool_selector_timeout_s() == 90.0

    monkeypatch.setenv("APPS_RG_POOL_SELECTOR_TIMEOUT_SECONDS", "180")
    assert sel.pool_selector_timeout_s() == 180.0

    monkeypatch.setenv("APPS_RG_POOL_SELECTOR_TIMEOUT_SECONDS", "5")  # below floor
    assert sel.pool_selector_timeout_s() == 30.0


def test_w3_selector_timing_receipt_written(tmp_path):
    import apps_rg.runtime.judges.bullet_pool_claude_selector as sel

    sel._write_selector_timing_receipt(tmp_path, {"phase": "error", "outcome": "selector_timeout"})
    path = tmp_path / sel.SELECTOR_TIMING_RECEIPT_FILENAME
    assert path.is_file()
    doc = json.loads(path.read_text(encoding="utf-8"))
    assert doc["outcome"] == "selector_timeout"


def test_w3_no_hardcoded_60s_selector_timeout():
    """Regression guard: the literal urlopen(..., timeout=60) must be gone."""
    import inspect

    import apps_rg.runtime.judges.bullet_pool_claude_selector as sel

    src = inspect.getsource(sel._call_anthropic_pool_selector)
    assert "timeout=60)" not in src
    assert "timeout=timeout_s" in src


# --------------------------------------------------------------------------------------------------
# W4 — per-path progress receipts
# --------------------------------------------------------------------------------------------------
def test_w4_progress_receipt_written_before_first_path_completes(tmp_path, monkeypatch):
    import apps_rg.runtime.reasoning.bullet_lane_self_consistency as scmod
    from apps_rg.runtime.providers.provider_contract import ProviderResult

    seen_started_row = {"ok": False}

    def fake_call(profile, payload, *, artifact_dir=None, run_id=None, temperature_override=None, token_budget=None):
        # At the moment the provider is invoked, a "started" row (completed_at=None) must already
        # be on disk — proving the board is flushed BEFORE the path completes.
        prog = json.loads((artifact_dir / scmod.PROGRESS_RECEIPT_FILENAME).read_text(encoding="utf-8"))
        if any(r["completed_at"] is None for r in prog["paths"]):
            seen_started_row["ok"] = True
        return ProviderResult(
            provider_requested="external_claude",
            provider_attempted=True,
            provider_available=False,
            exact_provider_error="simulated provider stall",
            runtime_generation_status="BLOCKED",
            model="m",
            raw_model_output="",
            provider_response=None,
        )

    monkeypatch.setattr(scmod, "call_section_model_provider", fake_call)

    paths, _last = scmod.run_provider_self_consistency_paths(
        section_lane="competencies",
        provider_payload={"messages": [{"role": "user", "content": "x"}]},
        parse_model_json=lambda raw: (None, "unused"),
        artifact_dir=tmp_path,
        run_id="run-1",
        temperature_bounds=(0.30, 0.50),
        base_temperature=0.4,
        path_count=2,
    )

    assert seen_started_row["ok"], "progress board was not flushed before the first path completed"
    doc = json.loads((tmp_path / scmod.PROGRESS_RECEIPT_FILENAME).read_text(encoding="utf-8"))
    assert doc["path_count"] == 2
    assert doc["paths_completed"] == 2
    for row in doc["paths"]:
        assert row["completed_at"] is not None
        assert row["runtime_generation_status"] == "BLOCKED"
        assert row["parse_ok"] is False
        assert row["provider_error"] == "simulated provider stall"


def test_competencies_self_consistency_payload_gets_path_diversity_framing(
    tmp_path,
    monkeypatch,
):
    import apps_rg.runtime.reasoning.bullet_lane_self_consistency as scmod
    from apps_rg.runtime.providers.provider_contract import ProviderResult

    seen_contents: list[str] = []

    def fake_call(profile, payload, *, artifact_dir=None, run_id=None, temperature_override=None, token_budget=None):
        seen_contents.append(str((payload.get("messages") or [{}])[-1].get("content") or ""))
        return ProviderResult(
            provider_requested="external_claude",
            provider_attempted=True,
            provider_available=True,
            exact_provider_error=None,
            runtime_generation_status="REAL_LLM",
            model="m",
            raw_model_output='{"competencies":[],"claim_ledger":[]}',
            provider_response={},
        )

    monkeypatch.setattr(scmod, "call_section_model_provider", fake_call)

    paths, _last = scmod.run_provider_self_consistency_paths(
        section_lane="competencies",
        provider_payload={"messages": [{"role": "user", "content": "base"}]},
        parse_model_json=lambda raw: (json.loads(raw), ""),
        artifact_dir=tmp_path,
        run_id="run-1",
        temperature_bounds=(0.30, 0.50),
        base_temperature=0.4,
        path_count=2,
    )

    assert len(paths) == 2
    assert len(seen_contents) == 2
    assert "COMPETENCIES_PATH_DIVERSITY (path_index=0" in seen_contents[0]
    assert "COMPETENCIES_PATH_DIVERSITY (path_index=1" in seen_contents[1]
    assert "agentic platform architecture" in seen_contents[0]
    assert "runtime governance and gates" in seen_contents[1]


# --------------------------------------------------------------------------------------------------
# W5/W6 — closeout mode is auditable and does NOT weaken the competencies contract
# --------------------------------------------------------------------------------------------------
def test_w6_closeout_mode_flag(monkeypatch):
    from apps_rg.runtime.reasoning import competencies_graph_pool as cgp

    monkeypatch.delenv("APPS_RG_E2E_CLOSEOUT_MODE", raising=False)
    assert cgp.e2e_closeout_mode_active() is False
    monkeypatch.setenv("APPS_RG_E2E_CLOSEOUT_MODE", "1")
    assert cgp.e2e_closeout_mode_active() is True


def test_w6_closeout_caps_regen_but_explicit_env_wins(monkeypatch):
    from apps_rg.runtime.reasoning import competencies_graph_pool as cgp

    monkeypatch.delenv("APPS_RG_COMPETENCIES_MAX_REGEN_ROUNDS", raising=False)
    monkeypatch.delenv("APPS_RG_EMPLOYMENT_BULLET_MAX_REGEN_ROUNDS", raising=False)
    monkeypatch.setenv("APPS_RG_E2E_CLOSEOUT_MODE", "1")
    assert cgp.max_competencies_regen_rounds() == 1  # closeout default cap

    monkeypatch.setenv("APPS_RG_COMPETENCIES_MAX_REGEN_ROUNDS", "0")
    assert cgp.max_competencies_regen_rounds() == 0  # explicit env overrides closeout default


def test_w6_strict_default_regen_unchanged(monkeypatch):
    from apps_rg.runtime.reasoning import competencies_graph_pool as cgp

    monkeypatch.delenv("APPS_RG_E2E_CLOSEOUT_MODE", raising=False)
    monkeypatch.delenv("APPS_RG_COMPETENCIES_MAX_REGEN_ROUNDS", raising=False)
    monkeypatch.delenv("APPS_RG_EMPLOYMENT_BULLET_MAX_REGEN_ROUNDS", raising=False)
    assert cgp.max_competencies_regen_rounds() == 2  # product default unchanged when no closeout


def test_w6_closeout_does_not_weaken_contract(monkeypatch):
    """Closeout keeps 8 categories + graph authority + unchanged score floor."""
    from apps_rg.runtime.reasoning import competencies_graph_pool as cgp

    monkeypatch.delenv("APPS_RG_COMPETENCIES_MIN_SELECTION_SCORE", raising=False)
    monkeypatch.delenv("APPS_RG_EMPLOYMENT_BULLET_MIN_SELECTION_SCORE", raising=False)
    monkeypatch.setenv("APPS_RG_E2E_CLOSEOUT_MODE", "1")
    assert cgp.COMPETENCIES_FINAL_CATEGORY_COUNT == 8
    assert cgp.COMPETENCIES_CANDIDATE_CATEGORY_COUNT == 8
    # The selection score floor is NOT lowered by closeout mode.
    assert cgp.min_competencies_selection_score() == cgp.DEFAULT_COMPETENCIES_MIN_SELECTION_SCORE


def test_graph_authority_preserved_in_selection_prompt():
    """The competencies selector prompt must keep graph/fact-only proof authority — never base resume."""
    from apps_rg.runtime.judges.bullet_pool_claude_selector import (
        _competencies_graph_selection_prompt,
    )

    prompt = _competencies_graph_selection_prompt(
        pool_text="POOL",
        targeting_context={"jd_text": "j", "briefing": "b", "skills_graph_ref": "ref"},
        min_score_threshold=0.72,
        selector_name="openai_chatgpt",
    )
    assert "augmented_skills_graph" in prompt
    assert "selected_fact_plan" in prompt
    # JD/briefing are targeting-only and base-resume skills are explicitly not proof.
    assert "base-resume" in prompt
    assert "targeting" in prompt.lower()
    assert "openai_chatgpt" in prompt


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(pytest.main([__file__, "-q"]))
