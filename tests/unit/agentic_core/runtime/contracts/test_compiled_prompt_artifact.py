"""Unit tests for agentic_core.runtime.contracts.compiled_prompt_artifact.

W1 (plan adg-testing-hotspots-wave-plan-a7f3c1) — Core P1 runtime-contract surface.
``compiled_prompt_artifact`` (fan_in=30, L_RUNTIME) is the Prompt-Assembly output
contract consumed by L2 execution. Frozen, slotted dataclasses with an L5
fail-closed certification invariant — exhaustive contract coverage.
"""

from __future__ import annotations

import dataclasses

import pytest

from agentic_core.runtime.contracts.compiled_prompt_artifact import (
    CompiledPromptArtifact,
    PromptBlock,
)
from agentic_core.runtime.contracts.origin import Origin
from agentic_core.runtime.contracts.posture import POSTURE_GENERATION, RuntimePosture


class TestPromptBlock:
    def test_required_fields(self) -> None:
        b = PromptBlock(role="system", content="you are ...")
        assert b.role == "system"
        assert b.content == "you are ..."

    def test_defaults(self) -> None:
        b = PromptBlock(role="user", content="hi")
        assert b.block_index == 0
        assert b.origin == Origin.SYSTEM_INTERNAL

    def test_explicit_origin(self) -> None:
        b = PromptBlock(role="user", content="hi", origin=Origin.USER_INTENT)
        assert b.origin == Origin.USER_INTENT

    def test_frozen(self) -> None:
        b = PromptBlock(role="system", content="x")
        with pytest.raises(dataclasses.FrozenInstanceError):
            b.content = "y"  # type: ignore[misc]

    def test_slots_no_dict(self) -> None:
        assert not hasattr(PromptBlock(role="system", content="x"), "__dict__")


def _valid_artifact(**overrides: object) -> CompiledPromptArtifact:
    base: dict[str, object] = dict(
        request_id="req-1",
        run_id="run-1",
        app_id="apps_rg",
        trace_id="trace-1",
        l5_certification_ref="cert-ref-1",
    )
    base.update(overrides)
    return CompiledPromptArtifact(**base)  # type: ignore[arg-type]


class TestCompiledPromptArtifact:
    def test_valid_construction(self) -> None:
        a = _valid_artifact()
        assert a.request_id == "req-1"
        assert a.app_id == "apps_rg"

    def test_scalar_defaults(self) -> None:
        a = _valid_artifact()
        assert a.system_preamble == ""
        assert a.user_instruction == ""
        assert a.schema_version == "W6.0"
        assert a.target_model == ""
        assert a.target_provider == ""
        assert a.max_tokens == 4096
        assert a.temperature == 0.7
        assert a.top_p == 1.0
        assert a.sandbox_required is False
        assert a.signature == ""
        assert a.replay_key == ""

    def test_collection_defaults_empty(self) -> None:
        a = _valid_artifact()
        assert a.prompt_blocks == ()
        assert a.slot_lineage_map == {}
        assert a.component_hash_map == {}
        assert a.per_input_hash_map == {}
        assert a.allowed_tools == ()
        assert a.allowed_models == ()
        assert a.otel_span_refs == ()
        assert a.audit_refs == ()
        assert a.gate_verdict_refs == ()
        assert a.snapshot_refs == ()

    def test_posture_default_is_generation(self) -> None:
        a = _valid_artifact()
        assert isinstance(a.posture, RuntimePosture)
        assert a.posture == POSTURE_GENERATION

    def test_carries_prompt_blocks(self) -> None:
        blocks = (
            PromptBlock(role="system", content="sys", origin=Origin.SYSTEM_INTERNAL),
            PromptBlock(role="user", content="usr", origin=Origin.USER_INTENT),
        )
        a = _valid_artifact(prompt_blocks=blocks)
        assert a.prompt_blocks == blocks
        assert a.prompt_blocks[1].origin == Origin.USER_INTENT

    def test_missing_cert_ref_raises(self) -> None:
        with pytest.raises(ValueError, match="l5_certification_ref"):
            _valid_artifact(l5_certification_ref="")

    @pytest.mark.parametrize("bad", ["   ", "\t", "\n"])
    def test_blank_cert_ref_raises(self, bad: str) -> None:
        with pytest.raises(ValueError, match="l5_certification_ref"):
            _valid_artifact(l5_certification_ref=bad)

    def test_frozen(self) -> None:
        a = _valid_artifact()
        with pytest.raises(dataclasses.FrozenInstanceError):
            a.target_model = "x"  # type: ignore[misc]

    def test_slots_no_dict(self) -> None:
        assert not hasattr(_valid_artifact(), "__dict__")
