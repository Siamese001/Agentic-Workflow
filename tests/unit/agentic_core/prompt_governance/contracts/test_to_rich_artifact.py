"""Tests for to_rich_artifact bridge (phase RH2B.2).

Plan: prompt-reception-followups-a7b3c4.
"""

from __future__ import annotations

from agentic_core.prompt_governance.contracts.compiled_artifact_types import (
    CompiledPromptArtifact as NarrowCompiledPromptArtifact,
)
from agentic_core.prompt_governance.contracts.compiled_artifact_types import (
    to_rich_artifact,
)


def _make_narrow() -> NarrowCompiledPromptArtifact:
    return NarrowCompiledPromptArtifact(
        trace_id="t-1",
        final_system_string="S",
        final_user_string="U",
        allowed_tools_schema=({"name": "tool_a"},),
        token_estimate=7,
        signature="deadbeef",
    )


def test_to_rich_artifact_field_map() -> None:
    narrow = _make_narrow()
    rich = to_rich_artifact(
        narrow,
        system_version_hash="svh-1",
        slots_used=["S0", "U0"],
    )
    assert rich.trace_id == "t-1"
    assert rich.system_version_hash == "svh-1"
    assert rich.final_system_string == "S"
    assert rich.final_user_string == "U"
    assert rich.allowed_tools_schema == [{"name": "tool_a"}]
    assert rich.tokens == 7
    assert rich.slots_used == ["S0", "U0"]
    assert rich.signature == "deadbeef"


def test_to_rich_artifact_defaults() -> None:
    narrow = _make_narrow()
    rich = to_rich_artifact(narrow)
    assert rich.system_version_hash == ""
    assert rich.slots_used == []


def test_to_rich_artifact_exposes_prompt_messages() -> None:
    """The rich form upgraded from narrow supports the PromptMessages IR."""
    narrow = _make_narrow()
    rich = to_rich_artifact(narrow, slots_used=["U0"])
    ir = rich.to_prompt_messages()
    assert ir.to_flat() == ("S", "U")
    assert ir.metadata["trace_id"] == "t-1"
