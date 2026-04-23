"""Tests for to_rich_artifact bridge (phase RH2B.2).

Plan: prompt-reception-followups-a7b3c4.

Post-RH2B.2 SSOT merge: the narrow ``CompiledPromptArtifact`` is now an
alias for the rich L2 variant. ``to_rich_artifact`` retains its signature
as an identity/fill-in helper so callers that still invoke it keep
working.
"""

from __future__ import annotations

from agentic_core.L2_execution.reasoning.compiled_artifact import (
    CompiledPromptArtifact as RichCompiledPromptArtifact,
)
from agentic_core.prompt_governance.contracts.compiled_artifact_types import (
    CompiledPromptArtifact,
    to_rich_artifact,
)


def _make_artifact(
    system_version_hash: str = "svh-1",
    slots_used: list[str] | None = None,
) -> CompiledPromptArtifact:
    return CompiledPromptArtifact(
        trace_id="t-1",
        system_version_hash=system_version_hash,
        final_system_string="S",
        final_user_string="U",
        allowed_tools_schema=[{"name": "tool_a"}],
        tokens=7,
        slots_used=list(slots_used or ["S0", "U0"]),
        signature="deadbeef",
    )


def test_governance_alias_is_rich_class() -> None:
    """The governance-package alias IS the rich L2 class (identity check)."""
    assert CompiledPromptArtifact is RichCompiledPromptArtifact


def test_to_rich_artifact_identity_when_no_overrides() -> None:
    artifact = _make_artifact()
    result = to_rich_artifact(artifact)
    # With no overrides, to_rich_artifact returns the SAME object (identity).
    assert result is artifact


def test_to_rich_artifact_fills_system_version_hash() -> None:
    artifact = _make_artifact(system_version_hash="")
    result = to_rich_artifact(artifact, system_version_hash="svh-new")
    assert result.system_version_hash == "svh-new"
    assert result.trace_id == artifact.trace_id
    assert result.tokens == artifact.tokens
    # Original is untouched (frozen dataclass → replace returns new instance).
    assert artifact.system_version_hash == ""


def test_to_rich_artifact_fills_slots_used() -> None:
    artifact = _make_artifact(slots_used=[])
    result = to_rich_artifact(artifact, slots_used=["S0", "C0", "U0"])
    assert result.slots_used == ["S0", "C0", "U0"]


def test_to_rich_artifact_exposes_prompt_messages() -> None:
    """Sanity: the merged class still supports the PromptMessages IR."""
    artifact = _make_artifact()
    ir = artifact.to_prompt_messages()
    assert ir.to_flat() == ("S", "U")
    assert ir.metadata["trace_id"] == "t-1"
