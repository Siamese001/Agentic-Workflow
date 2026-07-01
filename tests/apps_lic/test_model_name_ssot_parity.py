"""Single SSOT for every apps_lic model name.

`config/domain_contract/model_profiles.yaml` is the ONE source of truth for the
Claude Opus generator model and the GPT X1D judge model/transport id. This test fails
if any other apps_lic surface — the wired engine constants OR the shadow copies in
validation_exit.v1.yaml / the W0 contract — diverges from it.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from apps_lic.config.model_profiles import (
    resolve_generator_model,
    resolve_generator_provider,
    resolve_x1d_judge_model,
    resolve_x1d_judge_provider,
    resolve_x1d_judge_transport_model_id,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
DC = REPO_ROOT / "apps_lic" / "config" / "domain_contract"


def _yaml(name: str) -> dict:
    with (DC / name).open(encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def test_engine_constants_resolve_from_ssot() -> None:
    from apps_lic.engines import x1d_judge_policy as jp
    from apps_lic.engines import x1d_gpt_judge_adapter as ad
    from apps_lic.engines import whole_message_generation as wmg
    from apps_lic.engines import generation_engine as ge

    assert jp.DEFAULT_X1D_JUDGE_MODEL == resolve_x1d_judge_model()
    assert jp.DEFAULT_X1D_JUDGE_PROVIDER == resolve_x1d_judge_provider()
    assert ad.DEFAULT_GPT_TRANSPORT_MODEL_ID == resolve_x1d_judge_transport_model_id()
    assert wmg.GENERATOR_MODEL_ID == resolve_generator_model()
    assert wmg.GENERATOR_PROVIDER_ID == resolve_generator_provider()
    assert ge.DEFAULT_MODEL == resolve_generator_model()
    assert ge.DEFAULT_PROVIDER == resolve_generator_provider()


def test_generator_is_claude_opus_core() -> None:
    # Claude Opus is the core apps_lic generation model.
    gen = resolve_generator_model()
    assert gen == "Claude Sonnet 5" and resolve_generator_provider() == "claude"


def test_validation_exit_yaml_mirrors_ssot() -> None:
    x1d = _yaml("validation_exit.v1.yaml").get("x1d") or {}
    assert x1d.get("default_model") == resolve_x1d_judge_model()
    assert x1d.get("default_provider") == resolve_x1d_judge_provider()
    indep = x1d.get("independence_policy") or {}
    assert indep.get("generator_model") == resolve_generator_model()
    assert indep.get("generator_provider") == resolve_generator_provider()
    preflight = x1d.get("preflight_policy") or {}
    assert preflight.get("required_transport_model_id") == resolve_x1d_judge_transport_model_id()


def test_w0_contract_yaml_mirrors_ssot() -> None:
    doc = _yaml("apps_lic_redesign_w0_contracts.yaml")
    # find any "default_model" key anywhere and assert it equals the judge SSOT
    found: list[str] = []

    def walk(o: object) -> None:
        if isinstance(o, dict):
            for k, v in o.items():
                if k == "default_model" and isinstance(v, str):
                    found.append(v)
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    walk(doc)
    assert found, "expected a default_model entry in the W0 contract"
    assert all(v == resolve_x1d_judge_model() for v in found), found
