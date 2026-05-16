"""PA → core CPA adapter field preservation."""

from __future__ import annotations

from types import SimpleNamespace

from agentic_core.L0_routing.config.model_registry import QWEN_LOCAL_MODEL_ID

from apps_rg.l2_recipe.pa_to_core_cpa import adapt_apps_rg_cpa_for_l2_envelope


def test_adapt_maps_unspecified_model_to_ssot():
    """Legacy PA manifests must not send ``unspecified`` to vLLM."""
    local_cpa = SimpleNamespace(
        prompt_hash="sha256:abc",
        provider_render_manifest={"model": "unspecified", "max_tokens": 1024},
        messages=[],
        system_prompt="s",
        replay_manifest={},
        slot_lineage_map={},
        component_hash_map=None,
    )
    core = adapt_apps_rg_cpa_for_l2_envelope(
        local_cpa,
        {"request_id": "r1", "run_id": "run1", "trace_root": "tr1"},
    )
    assert core.target_model == QWEN_LOCAL_MODEL_ID


def test_adapt_preserves_temperature_zero():
    """``temperature: 0`` in provider_render_manifest must not collapse to 0.7."""
    local_cpa = SimpleNamespace(
        prompt_hash="sha256:abc",
        provider_render_manifest={
            "model": "m1",
            "max_tokens": 1024,
            "temperature": 0.0,
        },
        messages=[],
        system_prompt="system text",
        replay_manifest={},
        slot_lineage_map={},
        component_hash_map=None,
    )
    core = adapt_apps_rg_cpa_for_l2_envelope(
        local_cpa,
        {"request_id": "r1", "run_id": "run1", "trace_root": "tr1"},
    )
    assert core.temperature == 0.0
    assert core.target_model == "m1"
    assert core.max_tokens == 1024


def test_adapt_caps_top_p() -> None:
    local_cpa = SimpleNamespace(
        prompt_hash="sha256:abc",
        provider_render_manifest={"model": "m1", "max_tokens": 1024, "temperature": 0.05, "top_p": 0.99},
        messages=[],
        system_prompt="s",
        replay_manifest={},
        slot_lineage_map={},
        component_hash_map=None,
    )
    core = adapt_apps_rg_cpa_for_l2_envelope(
        local_cpa,
        {"request_id": "r1", "run_id": "run1", "trace_root": "tr1"},
    )
    assert core.top_p == 0.8
    assert core.temperature == 0.05
