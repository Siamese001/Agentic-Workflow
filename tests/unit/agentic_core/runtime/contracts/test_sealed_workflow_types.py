"""Unit tests for agentic_core.runtime.contracts.sealed_workflow_types.

W1 (plan adg-testing-hotspots-wave-plan-a7f3c1) — Core P1 runtime-contract surface.
``sealed_workflow_types`` (fan_in=16, L_RUNTIME) holds the generic, app-agnostic
SealedSectionArtifact + SealedWorkflowPackage contracts L3 assembles for Exit.
Frozen/slots value dataclasses with as_dict/as_json serialization.
"""

from __future__ import annotations

import dataclasses
import json

import pytest

from agentic_core.runtime.contracts.sealed_workflow_types import (
    SealedSectionArtifact,
    SealedWorkflowPackage,
)


class TestSealedSectionArtifact:
    def test_defaults(self) -> None:
        a = SealedSectionArtifact()
        assert a.lane == "ENSEMBLE_MODEL"
        assert a.node_order == 0
        assert a.merge_order == 0
        assert a.gate_result_refs == ()
        assert a.judge_result_refs == ()
        assert a.schema_version == "W5.a3f7e2"

    def test_as_dict_tuples_become_lists(self) -> None:
        a = SealedSectionArtifact(
            artifact_id="art-1",
            gate_result_refs=("g1", "g2"),
            judge_result_refs=("j1",),
        )
        d = a.as_dict()
        assert d["artifact_id"] == "art-1"
        assert d["gate_result_refs"] == ["g1", "g2"]
        assert d["judge_result_refs"] == ["j1"]

    def test_as_json_round_trips(self) -> None:
        a = SealedSectionArtifact(node_id="n1", run_id="r1")
        assert json.loads(a.as_json()) == a.as_dict()

    def test_frozen(self) -> None:
        with pytest.raises(dataclasses.FrozenInstanceError):
            SealedSectionArtifact().node_id = "x"  # type: ignore[misc]

    def test_slots_no_dict(self) -> None:
        assert not hasattr(SealedSectionArtifact(), "__dict__")


class TestSealedWorkflowPackage:
    def test_defaults(self) -> None:
        p = SealedWorkflowPackage()
        assert p.sealed_sections == ()
        assert p.section_count == 0
        assert p.total_candidates_generated == 0
        assert p.schema_version == "W5.a3f7e2"

    def test_carries_sealed_sections(self) -> None:
        sections = (
            SealedSectionArtifact(node_id="headline", node_order=0),
            SealedSectionArtifact(node_id="summary", node_order=1),
        )
        p = SealedWorkflowPackage(sealed_sections=sections, section_count=2)
        assert p.sealed_sections == sections
        assert p.section_count == 2

    def test_as_dict_keys_and_tuple_conversion(self) -> None:
        p = SealedWorkflowPackage(
            package_id="pkg-1",
            section_artifact_refs=("a1", "a2"),
            failed_node_refs=("n3",),
            section_count=2,
        )
        d = p.as_dict()
        assert d["package_id"] == "pkg-1"
        assert d["section_artifact_refs"] == ["a1", "a2"]
        assert d["failed_node_refs"] == ["n3"]
        assert d["section_count"] == 2

    def test_as_json_round_trips(self) -> None:
        p = SealedWorkflowPackage(package_id="pkg-1", run_id="r1")
        assert json.loads(p.as_json()) == p.as_dict()

    def test_frozen(self) -> None:
        with pytest.raises(dataclasses.FrozenInstanceError):
            SealedWorkflowPackage().package_id = "x"  # type: ignore[misc]
