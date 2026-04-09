"""Tests for ADG Prompt Assembly contracts (EvidenceItem, EvidenceBundle, PromptEnvelope, PromptAssemblyStatus)."""

from __future__ import annotations

import json

import pytest

from tools.adg.prompt_assembly.contracts import (
    ContradictionFlag,
    EvidenceBundle,
    EvidenceItem,
    PromptAssemblyStatus,
    PromptEnvelope,
)


# ---------------------------------------------------------------------------
# EvidenceItem
# ---------------------------------------------------------------------------


class TestEvidenceItem:
    def test_default_construction(self) -> None:
        item = EvidenceItem(
            source_artifact="test.sqlite",
            source_type="sqlite",
            snapshot_id="04082026_1914",
        )
        assert item.source_artifact == "test.sqlite"
        assert item.source_type == "sqlite"
        assert item.snapshot_id == "04082026_1914"
        assert item.is_derived is False
        assert item.support_score == 1.0
        assert item.data == {}
        assert item.row_references == []

    def test_derived_flag(self) -> None:
        item = EvidenceItem(
            source_artifact="graph_db",
            source_type="graph_db",
            snapshot_id="",
            is_derived=True,
        )
        assert item.is_derived is True

    def test_to_dict_roundtrip(self) -> None:
        item = EvidenceItem(
            source_artifact="test.json",
            source_type="json_report",
            snapshot_id="ts",
            commit_sha="abc123",
            data={"key": "value"},
        )
        d = item.to_dict()
        assert d["source_artifact"] == "test.json"
        assert d["commit_sha"] == "abc123"
        assert d["data"] == {"key": "value"}
        assert d["is_derived"] is False


# ---------------------------------------------------------------------------
# ContradictionFlag
# ---------------------------------------------------------------------------


class TestContradictionFlag:
    def test_construction(self) -> None:
        cf = ContradictionFlag(
            field_name="node_count",
            source_a="sqlite",
            value_a=65708,
            source_b="report",
            value_b=65682,
            severity="major",
            description="DB vs report mismatch",
        )
        assert cf.severity == "major"
        assert cf.value_a == 65708
        assert cf.value_b == 65682

    def test_to_dict(self) -> None:
        cf = ContradictionFlag(
            field_name="test",
            source_a="a",
            value_a=1,
            source_b="b",
            value_b=2,
        )
        d = cf.to_dict()
        assert d["field_name"] == "test"
        assert d["severity"] == "minor"


# ---------------------------------------------------------------------------
# EvidenceBundle
# ---------------------------------------------------------------------------


class TestEvidenceBundle:
    def test_empty_bundle(self) -> None:
        bundle = EvidenceBundle()
        assert bundle.items == []
        assert bundle.coverage_score == 0.0
        assert bundle.contradiction_status == "none"
        assert bundle.weak_support is False

    def test_bundle_with_contradictions(self) -> None:
        cf = ContradictionFlag(
            field_name="test",
            source_a="a",
            value_a=1,
            source_b="b",
            value_b=2,
            severity="major",
        )
        bundle = EvidenceBundle(
            contradictions=[cf],
            contradiction_status="major",
        )
        d = bundle.to_dict()
        assert d["contradiction_status"] == "major"
        assert len(d["contradictions"]) == 1

    def test_to_dict_compact_form(self) -> None:
        """to_dict uses compact item_count (not full items) — verify count matches."""
        items = [
            EvidenceItem(source_artifact="a.json", source_type="json_report", snapshot_id="ts"),
            EvidenceItem(source_artifact="b.sqlite", source_type="sqlite", snapshot_id="ts"),
        ]
        bundle = EvidenceBundle(items=items, coverage_score=0.8)
        d = bundle.to_dict()
        assert "item_count" in d
        assert d["item_count"] == 2
        assert "items" not in d  # compact form — no raw items in dict

    def test_weak_support_flag(self) -> None:
        bundle = EvidenceBundle(coverage_score=0.3, weak_support=True)
        assert bundle.weak_support is True


# ---------------------------------------------------------------------------
# PromptEnvelope
# ---------------------------------------------------------------------------


class TestPromptEnvelope:
    def test_deterministic_packet_id(self) -> None:
        """Same inputs → same packet_id."""
        env1 = PromptEnvelope(
            packet_type="test",
            replay_metadata={"snapshot_id": "ts1"},
        )
        env2 = PromptEnvelope(
            packet_type="test",
            replay_metadata={"snapshot_id": "ts1"},
        )
        assert env1.packet_id == env2.packet_id
        assert len(env1.packet_id) == 16

    def test_custom_packet_id_preserved(self) -> None:
        """Explicit packet_id is preserved, not overwritten by __post_init__."""
        env = PromptEnvelope(
            packet_type="test",
            packet_id="custom_id_12345678",
            replay_metadata={"snapshot_id": "ts1"},
        )
        assert env.packet_id == "custom_id_12345678"

    def test_different_inputs_different_ids(self) -> None:
        env1 = PromptEnvelope(
            packet_type="test",
            replay_metadata={"snapshot_id": "ts1"},
        )
        env2 = PromptEnvelope(
            packet_type="test",
            replay_metadata={"snapshot_id": "ts2"},
        )
        assert env1.packet_id != env2.packet_id

    def test_to_json(self) -> None:
        env = PromptEnvelope(
            packet_type="executive_summary",
            system_block="system",
            policy_block="policy",
            task_block="task",
        )
        j = env.to_json()
        parsed = json.loads(j)
        assert parsed["packet_type"] == "executive_summary"
        assert parsed["system_block"] == "system"
        assert parsed["schema_version"] == "1.0.0"

    def test_to_dict_includes_status(self) -> None:
        status = PromptAssemblyStatus(
            packet_type="test",
            assembly_result="pass",
        )
        env = PromptEnvelope(
            packet_type="test",
            assembly_status=status,
        )
        d = env.to_dict()
        assert "assembly_status" in d
        assert d["assembly_status"]["assembly_result"] == "pass"

    def test_to_markdown_contains_sections(self) -> None:
        env = PromptEnvelope(
            packet_type="test_packet",
            system_block="You are a test analyst.",
            policy_block="Test policy.",
            task_block="Do the test.",
            must_use_evidence=[{"source_artifact": "test.json", "data": {}}],
            contradiction_flags=[
                {
                    "field_name": "count",
                    "source_a": "db",
                    "value_a": 10,
                    "source_b": "report",
                    "value_b": 12,
                    "severity": "minor",
                }
            ],
        )
        md = env.to_markdown()
        assert "# ADG Packet: test_packet" in md
        assert "## System" in md
        assert "## Policy / Invariants" in md
        assert "## Task" in md
        assert "## Must-Use Evidence" in md
        assert "## Contradiction Flags" in md

    def test_to_markdown_all_sections_rendered(self) -> None:
        """Exercise every conditional section in to_markdown rendering."""
        status = PromptAssemblyStatus(
            packet_type="test",
            assembly_result="partial",
            evidence_contract_status="partial",
            contradiction_status="minor",
            token_budget_status="trimmed",
            overflow_action="narrowed",
        )
        env = PromptEnvelope(
            packet_type="full_test",
            system_block="System instructions.",
            policy_block="Policy rules.",
            task_block="Task description.",
            must_use_evidence=[{"source_artifact": "a.json", "data": {}}],
            optional_evidence=[{"source_artifact": "graph.db", "data": {}}],
            contradiction_flags=[
                {
                    "field_name": "count",
                    "source_a": "db",
                    "value_a": 10,
                    "source_b": "report",
                    "value_b": 20,
                    "severity": "major",
                }
            ],
            abstain_instructions="Abstain if insufficient.",
            refine_instructions="Request narrower scope.",
            output_schema={"type": "object", "properties": {}},
            replay_metadata={"snapshot_ids": ["ts1"]},
            assembly_status=status,
        )
        md = env.to_markdown()
        assert "## System" in md
        assert "## Policy / Invariants" in md
        assert "## Task" in md
        assert "## Must-Use Evidence" in md
        assert "## Optional Evidence (Derived)" in md
        assert "## Contradiction Flags" in md
        assert "## Abstain Instructions" in md
        assert "## Refine Instructions" in md
        assert "## Output Schema" in md
        assert "## Replay Metadata" in md
        assert "## Assembly Status" in md
        assert "partial" in md.lower()

    def test_block_order_in_dict(self) -> None:
        """Verify canonical block ordering in to_dict output."""
        env = PromptEnvelope(packet_type="test")
        d = env.to_dict()
        keys = list(d.keys())
        # system_block before policy_block before task_block
        assert keys.index("system_block") < keys.index("policy_block")
        assert keys.index("policy_block") < keys.index("task_block")
        assert keys.index("task_block") < keys.index("must_use_evidence")
        assert keys.index("must_use_evidence") < keys.index("optional_evidence")
        assert keys.index("optional_evidence") < keys.index("contradiction_flags")


# ---------------------------------------------------------------------------
# PromptAssemblyStatus
# ---------------------------------------------------------------------------


class TestPromptAssemblyStatus:
    def test_default_values(self) -> None:
        status = PromptAssemblyStatus(packet_type="test")
        assert status.evidence_contract_status == "empty"
        assert status.assembly_result == "pass"
        assert status.overflow_action == "none"
        assert status.assembly_timestamp  # auto-set

    def test_custom_timestamp_preserved(self) -> None:
        """Explicit assembly_timestamp is not overwritten by __post_init__."""
        custom_ts = "2026-01-01T00:00:00+00:00"
        status = PromptAssemblyStatus(
            packet_type="test",
            assembly_timestamp=custom_ts,
        )
        assert status.assembly_timestamp == custom_ts

    def test_to_dict(self) -> None:
        status = PromptAssemblyStatus(
            packet_type="ratchet_review",
            evidence_contract_status="complete",
            assembly_result="pass",
        )
        d = status.to_dict()
        assert d["packet_type"] == "ratchet_review"
        assert d["evidence_contract_status"] == "complete"
