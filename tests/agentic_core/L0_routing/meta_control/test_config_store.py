"""Tests for ConfigStore types + on-disk store -- Wave 7.0.17."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agentic_core.L0_routing.meta_control.config_store import (
    _version_path,
    apply_change_package_readonly,
    load_current,
    write_next_version,
)
from agentic_core.L0_routing.meta_control.config_store_types import (
    build_config_delta,
    build_config_snapshot,
    canonical_json,
    stable_sha256,
    validate_component_allowed,
)
from agentic_core.L0_routing.types.v15_p2_types import SemanticClockSnapshot
from agentic_core.L7_meta_learning.types.meta_learning_types import (
    build_meta_learning_approval,
    build_meta_learning_change_package,
    build_meta_learning_decision,
    build_meta_learning_evaluation,
    build_meta_learning_proposal,
)

_CLOCK = SemanticClockSnapshot(tick=1, vector_clock=(("L0", 1),))


class TestCanonicalJsonDeterminism:
    def test_same_dict_different_key_order(self) -> None:
        d1 = {"z": 1, "a": 2, "m": {"b": 3, "a": 4}}
        d2 = {"a": 2, "m": {"a": 4, "b": 3}, "z": 1}
        assert canonical_json(d1) == canonical_json(d2)

    def test_stable_sha256_matches(self) -> None:
        text = canonical_json({"x": 1})
        assert stable_sha256(text) == stable_sha256(text)


class TestVersionIncrement:
    def test_sequential_versions(self, tmp_path: Path) -> None:
        s1 = write_next_version(
            tmp_path,
            "apps_rg",
            "routing_thresholds",
            {"threshold": 0.5},
            _CLOCK,
        )
        assert s1.config_version == 1
        assert _version_path(tmp_path, "apps_rg", "routing_thresholds", 1).exists()
        s2 = write_next_version(
            tmp_path,
            "apps_rg",
            "routing_thresholds",
            {"threshold": 0.7},
            _CLOCK,
        )
        assert s2.config_version == 2
        assert _version_path(tmp_path, "apps_rg", "routing_thresholds", 2).exists()
        assert s1.trace_id != s2.trace_id


class TestAtomicWriteConsistency:
    def test_current_matches_last_version(self, tmp_path: Path) -> None:
        payload = {"key": "value", "nested": {"a": 1}}
        write_next_version(tmp_path, "apps_rg", "routing_thresholds", payload, _CLOCK)
        current = load_current(tmp_path, "apps_rg", "routing_thresholds")
        vf = _version_path(tmp_path, "apps_rg", "routing_thresholds", 1)
        assert current == json.loads(vf.read_text(encoding="utf-8"))
        write_next_version(tmp_path, "apps_rg", "routing_thresholds", {"key": "updated"}, _CLOCK)
        current2 = load_current(tmp_path, "apps_rg", "routing_thresholds")
        vf2 = _version_path(tmp_path, "apps_rg", "routing_thresholds", 2)
        assert current2 == json.loads(vf2.read_text(encoding="utf-8"))


def _build_change_package(
    *,
    target_component: str = "routing_thresholds",
    change_spec: dict | None = None,
):
    spec = change_spec if change_spec is not None else {"threshold": 0.05}
    proposal = build_meta_learning_proposal(
        semantic_clock=_CLOCK,
        proposer="test",
        target_component=target_component,
        before={"threshold": 0.5},
        after=spec,
        metric_name="accuracy",
        baseline=0.80,
        candidate=0.85,
        evidence_hash="abc123",
    )
    evaluation = build_meta_learning_evaluation(
        proposal=proposal,
        evaluator="bench",
        dataset_id="ds",
        baseline=0.80,
        candidate=0.85,
        evidence_hash="eval_hash",
    )
    approval = build_meta_learning_approval(
        evaluation=evaluation,
        approver="reviewer",
        decision="APPROVE",
        rationale="OK",
    )
    decision = build_meta_learning_decision(
        proposal=proposal,
        evaluation=evaluation,
        approval=approval,
        semantic_clock=_CLOCK,
        policy_config_hash=None,
    )
    return build_meta_learning_change_package(
        proposal=proposal,
        evaluation=evaluation,
        approval=approval,
        decision=decision,
        target_component=target_component,
        change_spec=spec,
        semantic_clock=_CLOCK,
        policy_config_hash=None,
    )


class TestApplyChangePackageReadonly:
    def test_does_not_create_files(self, tmp_path: Path) -> None:
        store = tmp_path / "store"
        store.mkdir()
        before = set(store.rglob("*"))
        pkg = _build_change_package()
        delta = apply_change_package_readonly(store, pkg, _CLOCK)
        after = set(store.rglob("*"))
        assert before == after, "apply_change_package_readonly must not create files"
        assert delta.artifact_type == "META_CONTROL_CONFIG_DELTA"
        assert delta.from_version == 0
        assert delta.to_version == 1


class TestFailClosed:
    def test_invalid_component_raises(self) -> None:
        with pytest.raises(ValueError, match="COMPONENT_NOT_MUTABLE"):
            validate_component_allowed("guardian_contract")

    def test_load_current_invalid_component(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="COMPONENT_NOT_MUTABLE"):
            load_current(tmp_path, "apps_rg", "guardian_contract")

    def test_write_next_version_empty_app_id(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="APP_ID_EMPTY"):
            write_next_version(tmp_path, "", "routing_thresholds", {}, _CLOCK)

    def test_load_current_returns_empty_on_missing(self, tmp_path: Path) -> None:
        assert load_current(tmp_path, "apps_rg", "routing_thresholds") == {}


class TestSnapshotDeterminism:
    def test_identical_inputs_produce_identical_trace(self) -> None:
        s1 = build_config_snapshot(
            app_id="apps_rg",
            target_component="routing_thresholds",
            config_version=1,
            payload={"threshold": 0.5},
            semantic_clock=_CLOCK,
        )
        s2 = build_config_snapshot(
            app_id="apps_rg",
            target_component="routing_thresholds",
            config_version=1,
            payload={"threshold": 0.5},
            semantic_clock=_CLOCK,
        )
        assert s1.trace_id == s2.trace_id
        assert s1.to_json() == s2.to_json()


class TestDeltaVersionGap:
    def test_version_gap_rejected(self) -> None:
        with pytest.raises(ValueError, match="VERSION_GAP"):
            build_config_delta(
                app_id="apps_rg",
                target_component="routing_thresholds",
                from_version=1,
                to_version=3,
                change_spec={"threshold": 0.05},
                semantic_clock=_CLOCK,
            )
