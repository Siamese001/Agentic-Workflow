"""Unit tests for agentic_core.L3_orchestration.managed_workflow_runner.

Wave 6.1 (plan adg-testing-hotspots-wave-plan-a7f3c1) — P2 untested-module
coverage. Validates the pure / constructible surface only:
``ManagedWorkflowRunnerError`` message + reason attribute, the frozen
``_ResolvedNode`` dataclass, the pure ``_topological_sort`` (ordering,
cycle fail-closed, optional/node_type passthrough), ``_compute_digest``
(determinism + missing-file empty string), ``_load_manifest_yaml`` (parse +
non-dict coercion), and ``_StageReceiptWriter`` (None-dir no-op + write).
No live L2 executor, no models, no mocks.
"""
from __future__ import annotations

import dataclasses
import hashlib

import pytest

from agentic_core.L3_orchestration.managed_workflow_runner import (
    ManagedWorkflowRunnerError,
    _ResolvedNode,
    _StageReceiptWriter,
    _compute_digest,
    _load_manifest_yaml,
    _topological_sort,
)


class TestRunnerError:
    def test_reason_attribute(self) -> None:
        err = ManagedWorkflowRunnerError("bad thing")
        assert err.reason == "bad thing"

    def test_message_format(self) -> None:
        err = ManagedWorkflowRunnerError("bad thing")
        assert str(err) == "ManagedWorkflowRunnerError: bad thing"

    def test_is_exception(self) -> None:
        with pytest.raises(ManagedWorkflowRunnerError):
            raise ManagedWorkflowRunnerError("x")


class TestResolvedNode:
    def test_construction_fields(self) -> None:
        node = _ResolvedNode(
            node_id="a",
            node_type="section",
            depends_on=("b", "c"),
            optional=True,
            node_order=3,
        )
        assert node.node_id == "a"
        assert node.node_type == "section"
        assert node.depends_on == ("b", "c")
        assert node.optional is True
        assert node.node_order == 3

    def test_frozen(self) -> None:
        node = _ResolvedNode("a", "t", (), False, 0)
        with pytest.raises(dataclasses.FrozenInstanceError):
            node.node_id = "z"  # type: ignore[misc]


class TestTopologicalSort:
    def test_linear_chain_order(self) -> None:
        nodes = [
            {"node_id": "c", "depends_on": ["b"]},
            {"node_id": "b", "depends_on": ["a"]},
            {"node_id": "a"},
        ]
        ordered = _topological_sort(nodes)
        ids = [n.node_id for n in ordered]
        assert ids.index("a") < ids.index("b") < ids.index("c")

    def test_node_order_is_sequential(self) -> None:
        nodes = [{"node_id": "a"}, {"node_id": "b", "depends_on": ["a"]}]
        ordered = _topological_sort(nodes)
        assert [n.node_order for n in ordered] == [0, 1]

    def test_optional_and_node_type_passthrough(self) -> None:
        nodes = [{"node_id": "a", "node_type": "render", "optional": True}]
        ordered = _topological_sort(nodes)
        assert ordered[0].node_type == "render"
        assert ordered[0].optional is True
        assert ordered[0].depends_on == ()

    def test_missing_optional_defaults_false(self) -> None:
        ordered = _topological_sort([{"node_id": "a"}])
        assert ordered[0].optional is False
        assert ordered[0].node_type == ""

    def test_cycle_fails_closed(self) -> None:
        nodes = [
            {"node_id": "a", "depends_on": ["b"]},
            {"node_id": "b", "depends_on": ["a"]},
        ]
        with pytest.raises(ManagedWorkflowRunnerError) as ei:
            _topological_sort(nodes)
        assert "Cycle detected" in str(ei.value)

    def test_empty_returns_empty(self) -> None:
        assert _topological_sort([]) == []

    def test_independent_nodes_all_order_zero_indegree(self) -> None:
        nodes = [{"node_id": "a"}, {"node_id": "b"}, {"node_id": "c"}]
        ordered = _topological_sort(nodes)
        assert {n.node_id for n in ordered} == {"a", "b", "c"}
        assert len(ordered) == 3


class TestComputeDigest:
    def test_matches_sha256(self, tmp_path) -> None:
        f = tmp_path / "m.yaml"
        f.write_bytes(b"hello-bytes")
        assert _compute_digest(f) == hashlib.sha256(b"hello-bytes").hexdigest()

    def test_determinism(self, tmp_path) -> None:
        f = tmp_path / "m.yaml"
        f.write_bytes(b"abc")
        assert _compute_digest(f) == _compute_digest(f)

    def test_missing_file_returns_empty(self, tmp_path) -> None:
        assert _compute_digest(tmp_path / "nope.yaml") == ""


class TestLoadManifestYaml:
    def test_parses_dict(self, tmp_path) -> None:
        f = tmp_path / "m.yaml"
        f.write_text("nodes:\n  - node_id: a\n", encoding="utf-8")
        data = _load_manifest_yaml(f)
        assert data["nodes"][0]["node_id"] == "a"

    def test_non_dict_coerced_to_empty(self, tmp_path) -> None:
        f = tmp_path / "m.yaml"
        f.write_text("- just\n- a\n- list\n", encoding="utf-8")
        assert _load_manifest_yaml(f) == {}

    def test_empty_file_returns_empty_dict(self, tmp_path) -> None:
        f = tmp_path / "m.yaml"
        f.write_text("", encoding="utf-8")
        assert _load_manifest_yaml(f) == {}

    def test_missing_file_raises(self, tmp_path) -> None:
        with pytest.raises(ManagedWorkflowRunnerError):
            _load_manifest_yaml(tmp_path / "absent.yaml")


class TestStageReceiptWriter:
    def test_none_dir_is_noop(self) -> None:
        writer = _StageReceiptWriter(None)
        assert writer.write("x.json", {"k": "v"}) is None

    def test_writes_json_and_creates_dir(self, tmp_path) -> None:
        target_dir = tmp_path / "sub" / "receipts"
        writer = _StageReceiptWriter(target_dir)
        out = writer.write("01.json", {"k": "v", "n": 1})
        assert out is not None
        assert out.exists()
        assert '"k": "v"' in out.read_text(encoding="utf-8")

    def test_default_str_serialization(self, tmp_path) -> None:
        writer = _StageReceiptWriter(tmp_path)
        # Path is not natively JSON serializable; default=str handles it.
        out = writer.write("02.json", {"p": tmp_path})
        assert out is not None
        assert out.exists()
