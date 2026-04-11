"""Tests for the packet builders.

These tests use no real SQLite or graph DB — they verify that builders
produce valid PromptEnvelopes from adapter outputs (which gracefully
handle missing artifacts).
"""

from __future__ import annotations

import pytest

from tools.adg.prompt_assembly.contracts import (
    EvidenceBundle,
    EvidenceItem,
    PromptAssemblyStatus,
    PromptEnvelope,
)
from tools.adg.prompt_assembly.packets.builders import (
    _BUILDER_NAMES,
    build_determinism_rca,
    build_executive_summary,
    build_graph_path_explanation,
    build_hotspot_investigation,
    build_infrastructure_boundary,
    build_p0_failure,
    build_packet,
    build_ratchet_review,
    build_unknown_unresolved_triage,
)


class TestBuildPacket:
    def test_unknown_type_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown packet type"):
            build_packet("nonexistent")

    def test_all_types_buildable(self) -> None:
        """Every registered type can be built (with missing artifacts → graceful degradation)."""
        for ptype in _BUILDER_NAMES:
            kwargs = {}
            if ptype == "graph_path_explanation":
                kwargs = {"from_node": "a", "to_node": "b"}
            env = build_packet(ptype, sqlite_path=None, graph=None, **kwargs)
            assert isinstance(env, PromptEnvelope)
            assert env.packet_type == ptype
            assert env.schema_version == "1.0.0"
            assert env.packet_id  # non-empty
            assert env.system_block  # non-empty
            assert env.policy_block  # non-empty
            assert env.task_block  # non-empty
            assert env.assembly_status is not None


class TestEnvelopeStructure:
    """Verify structural invariants of assembled envelopes."""

    def _build(self, ptype: str, **kwargs) -> PromptEnvelope:
        if ptype == "graph_path_explanation":
            kwargs.setdefault("from_node", "a")
            kwargs.setdefault("to_node", "b")
        return build_packet(ptype, sqlite_path=None, graph=None, **kwargs)

    def test_contradiction_flags_list(self) -> None:
        for ptype in _BUILDER_NAMES:
            env = self._build(ptype)
            assert isinstance(env.contradiction_flags, list)

    def test_replay_metadata_has_sources(self) -> None:
        for ptype in _BUILDER_NAMES:
            env = self._build(ptype)
            assert "source_artifacts" in env.replay_metadata

    def test_assembly_status_present(self) -> None:
        for ptype in _BUILDER_NAMES:
            env = self._build(ptype)
            status = env.assembly_status
            assert isinstance(status, PromptAssemblyStatus)
            assert status.packet_type == ptype
            assert status.assembly_timestamp

    def test_derived_evidence_tagged(self) -> None:
        """All optional_evidence items from graph_db should carry is_derived."""
        env = self._build("graph_path_explanation")
        for item in env.optional_evidence:
            if item.get("source_type") == "graph_db":
                assert item.get("is_derived") is True

    def test_output_schema_present(self) -> None:
        for ptype in _BUILDER_NAMES:
            env = self._build(ptype)
            assert env.output_schema  # non-empty dict
            assert "type" in env.output_schema

    def test_json_serializable(self) -> None:
        """All envelopes must be JSON-serializable."""
        import json

        for ptype in _BUILDER_NAMES:
            env = self._build(ptype)
            j = env.to_json()
            parsed = json.loads(j)
            assert parsed["packet_type"] == ptype

    def test_markdown_renderable(self) -> None:
        """All envelopes must produce non-empty markdown."""
        for ptype in _BUILDER_NAMES:
            env = self._build(ptype)
            md = env.to_markdown()
            assert f"# ADG Packet: {ptype}" in md


class TestSpecificBuilders:
    def test_determinism_rca(self) -> None:
        env = build_determinism_rca()
        assert env.packet_type == "determinism_rca"
        assert "provenance" in env.task_block.lower() or "digest" in env.task_block.lower()

    def test_p0_failure(self) -> None:
        env = build_p0_failure()
        assert env.packet_type == "p0_failure"
        assert "violation" in env.task_block.lower()

    def test_ratchet_review(self) -> None:
        env = build_ratchet_review()
        assert env.packet_type == "ratchet_review"
        assert "ratchet" in env.task_block.lower() or "ceiling" in env.task_block.lower()

    def test_executive_summary(self) -> None:
        env = build_executive_summary()
        assert env.packet_type == "executive_summary"
        assert "summary" in env.task_block.lower()

    def test_graph_path_with_nodes(self) -> None:
        env = build_graph_path_explanation(from_node="module_a", to_node="module_b")
        assert env.packet_type == "graph_path_explanation"
        assert "module_a" in env.task_block
        assert "module_b" in env.task_block
        assert env.replay_metadata.get("from_node") == "module_a"
        assert env.replay_metadata.get("to_node") == "module_b"


class TestPreShapedBundleHook:
    """Targeted tests for the pre_shaped_bundle parameter added to _assemble()."""

    def _make_item(self, source_artifact: str = "test.json") -> EvidenceItem:
        return EvidenceItem(
            source_artifact=source_artifact,
            source_type="json_report",
            snapshot_id="ts001",
            data={"text_snippet": "test evidence content"},
            support_score=0.85,
        )

    def _make_bundle(self, coverage: float = 0.75, weak: bool = False) -> EvidenceBundle:
        item = self._make_item()
        return EvidenceBundle(
            items=[item],
            coverage_score=coverage,
            contradiction_status="none",
            contradictions=[],
            gaps=[],
            freshness="2026-04-11T09:00:00Z",
            weak_support=weak,
        )

    def test_pre_shaped_bundle_used_directly(self) -> None:
        """When pre_shaped_bundle is supplied, it is used and coverage flows through."""
        from tools.adg.prompt_assembly.packets.builders import _assemble
        from tools.adg.prompt_assembly.packets.registry import get_template

        template = get_template("executive_summary")
        item = self._make_item()
        bundle = self._make_bundle(coverage=0.75)
        env = _assemble(
            template=template,
            must_items=[item],
            opt_items=[],
            task_block="Test task block for C0 bridge",
            pre_shaped_bundle=bundle,
        )
        assert isinstance(env, PromptEnvelope)
        assert env.assembly_status is not None
        assert env.assembly_status.evidence_contract_status == "partial"

    def test_pre_shaped_bundle_coverage_complete(self) -> None:
        """coverage_score >= 0.8 produces evidence_contract_status='complete'."""
        from tools.adg.prompt_assembly.packets.builders import _assemble
        from tools.adg.prompt_assembly.packets.registry import get_template

        template = get_template("executive_summary")
        item = self._make_item()
        bundle = self._make_bundle(coverage=0.90)
        env = _assemble(
            template=template,
            must_items=[item],
            opt_items=[],
            task_block="Test task block",
            pre_shaped_bundle=bundle,
        )
        assert env.assembly_status is not None
        assert env.assembly_status.evidence_contract_status == "complete"
        assert env.assembly_status.assembly_result == "pass"

    def test_pre_shaped_bundle_empty_coverage_fails(self) -> None:
        """coverage_score == 0.0 with pre_shaped_bundle produces assembly_result='fail'."""
        from tools.adg.prompt_assembly.packets.builders import _assemble
        from tools.adg.prompt_assembly.packets.registry import get_template

        template = get_template("executive_summary")
        empty_bundle = EvidenceBundle(
            items=[],
            coverage_score=0.0,
            contradiction_status="none",
            contradictions=[],
            gaps=["no_evidence"],
            freshness="",
            weak_support=True,
        )
        env = _assemble(
            template=template,
            must_items=[],
            opt_items=[],
            task_block="Test task block",
            pre_shaped_bundle=empty_bundle,
        )
        assert env.assembly_status is not None
        assert env.assembly_status.evidence_contract_status == "empty"
        assert env.assembly_status.assembly_result == "fail"

    def test_replay_extras_flow_through_with_pre_shaped_bundle(self) -> None:
        """replay_extras keys survive in replay_metadata when pre_shaped_bundle is used."""
        from tools.adg.prompt_assembly.packets.builders import _assemble
        from tools.adg.prompt_assembly.packets.registry import get_template

        template = get_template("executive_summary")
        item = self._make_item()
        bundle = self._make_bundle(coverage=0.80)
        extras = {
            "retrieval_id": "ret-uuid-001",
            "request_id": "req-uuid-001",
            "evidence_hmac": "abc123deadbeef" * 4,
            "coverage_score": 0.80,
            "abstain_hint": False,
            "confidence_band": "HIGH",
        }
        env = _assemble(
            template=template,
            must_items=[item],
            opt_items=[],
            task_block="Test task block",
            replay_extras=extras,
            pre_shaped_bundle=bundle,
        )
        assert env.replay_metadata["retrieval_id"] == "ret-uuid-001"
        assert env.replay_metadata["request_id"] == "req-uuid-001"
        assert env.replay_metadata["evidence_hmac"] == "abc123deadbeef" * 4
        assert env.replay_metadata["confidence_band"] == "HIGH"
        assert env.replay_metadata["abstain_hint"] is False

    def test_none_pre_shaped_bundle_uses_internal_shaping(self) -> None:
        """With pre_shaped_bundle=None (default), internal shape_evidence() is called unchanged."""
        env = build_executive_summary()
        assert isinstance(env, PromptEnvelope)
        assert env.packet_type == "executive_summary"
        assert env.assembly_status is not None

    def test_existing_builders_unaffected(self) -> None:
        """All 8 existing builders produce valid output unchanged after the parameter addition."""
        for ptype in _BUILDER_NAMES:
            kwargs = {}
            if ptype == "graph_path_explanation":
                kwargs = {"from_node": "x", "to_node": "y"}
            env = build_packet(ptype, sqlite_path=None, graph=None, **kwargs)
            assert isinstance(env, PromptEnvelope)
            assert env.packet_type == ptype
            assert env.assembly_status is not None
            assert "source_artifacts" in env.replay_metadata
