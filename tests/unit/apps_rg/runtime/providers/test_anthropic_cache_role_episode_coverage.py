from __future__ import annotations

from agentic_core.knowledge.retrieval.anthropic_cache_control import min_cacheable_chars
from apps_rg.runtime.providers.provider_gateway import ProviderProfile
from apps_rg.runtime.providers.section_provider_call import _resolve_anthropic_cache_payload


def test_section_provider_renders_legacy_insurtech_and_ey_self_consistency_payloads(monkeypatch) -> None:
    monkeypatch.setenv("APPS_RG_ANTHROPIC_PROMPT_CACHE", "1")
    model = "claude-sonnet-5"
    long_prompt = "role episode graph evidence " * ((min_cacheable_chars(model) // 28) + 100)

    for section_id in ("insurtech_bullets", "ey_bullets"):
        payload, seed, strategy = _resolve_anthropic_cache_payload(
            {
                "messages": [
                    {"role": "system", "content": "You are an apps_rg section generator."},
                    {"role": "user", "content": long_prompt},
                ],
                "anthropic_workload_kind": "SELF_CONSISTENCY",
            },
            profile=ProviderProfile.EXTERNAL_CLAUDE,
            model=model,
            section_id=section_id,
            run_id="run-1",
        )
        assert payload is not None
        assert seed is not None
        assert strategy == "fallback_system_user_prefix_v3"
        assert seed["section_id"] == section_id
        assert seed["cache_marker_count"] == 1
        assert "cache_control" in str(payload["messages"])
