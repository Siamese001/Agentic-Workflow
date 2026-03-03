"""Guardian tests for G-1-1 (§1.7) — V15 Artifact Typing Migration.

Validates:
1. ResultArtifact: validator accepts dataclass, dict, rejects missing fields.
2. HealingPlan: validator accepts dataclass, dict, rejects missing fields.
3. IncidentArtifact + StaleWriteIncident: same pattern.
4. Bridge adapters: round-trip identity for dict input, lossless for dataclass.
5. Structural: TD module exists and exports expected names.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from agentic_core.L0_routing.types.artifact_validate_compat_types import (
    make_healing_plan_from_dataclass,
    make_result_artifact_from_dataclass,
    to_healing_plan_dict,
    to_incident_artifact_dict,
    to_result_artifact_dict,
    to_stale_write_incident_dict,
    validate_healing_plan,
    validate_incident_artifact,
    validate_result_artifact,
    validate_stale_write_incident,
)
from agentic_core.L0_routing.types.routing_artifact_types import (
    HealingPlan,
    IncidentArtifact,
    ResultArtifact,
    SeverityEnum,
    StaleWriteIncident,
)

# =====================================================================
# Fixtures
# =====================================================================


@pytest.fixture()
def result_artifact_dc():
    """Create a valid ResultArtifact frozen dataclass."""
    return ResultArtifact(
        trace_id="trace-r1",
        execution_outcome="success",
        final_state_hash="abc123",
        artifact_class="RESULT",
        emitting_layer="L2",
    )


@pytest.fixture()
def result_artifact_dict():
    """Create a valid ResultArtifact as plain dict."""
    return {
        "trace_id": "trace-r1",
        "execution_outcome": "success",
        "final_state_hash": "abc123",
        "artifact_class": "RESULT",
        "emitting_layer": "L2",
    }


@pytest.fixture()
def healing_plan_dc():
    """Create a valid HealingPlan frozen dataclass."""
    return HealingPlan(
        trace_id="trace-hp1",
        plan_id="plan-001",
        manifests=("manifest-a", "manifest-b"),
        semantic_clock_tick=5,
        policy_liaison_node="node-alpha",
        emitting_layer="L2",
    )


@pytest.fixture()
def healing_plan_dict():
    """Create a valid HealingPlan as plain dict."""
    return {
        "trace_id": "trace-hp1",
        "plan_id": "plan-001",
        "manifests": ["manifest-a", "manifest-b"],
        "semantic_clock_tick": 5,
        "policy_liaison_node": "node-alpha",
        "emitting_layer": "L2",
    }


# =====================================================================
# 1. ResultArtifact validator
# =====================================================================


class TestResultArtifactValidator:
    """Validator accepts dataclass and dict, rejects missing fields."""

    def test_accepts_dataclass(self, result_artifact_dc):
        result = validate_result_artifact(result_artifact_dc)
        assert result["trace_id"] == "trace-r1"
        assert result["execution_outcome"] == "success"
        assert result["final_state_hash"] == "abc123"
        assert result["artifact_class"] == "RESULT"
        assert result["emitting_layer"] == "L2"

    def test_accepts_dict(self, result_artifact_dict):
        result = validate_result_artifact(result_artifact_dict)
        assert result["trace_id"] == "trace-r1"
        assert result["artifact_class"] == "RESULT"

    def test_missing_trace_id_fails(self):
        with pytest.raises(ValueError, match="VALIDATE_RESULT_ARTIFACT.*trace_id"):
            validate_result_artifact(
                {"execution_outcome": "x", "final_state_hash": "y", "artifact_class": "z"}
            )

    def test_missing_artifact_class_fails(self):
        with pytest.raises(ValueError, match="VALIDATE_RESULT_ARTIFACT.*artifact_class"):
            validate_result_artifact({"trace_id": "t", "execution_outcome": "x", "final_state_hash": "y"})

    def test_empty_trace_id_fails(self):
        with pytest.raises(ValueError, match="VALIDATE_RESULT_ARTIFACT.*trace_id"):
            validate_result_artifact(
                {
                    "trace_id": "",
                    "execution_outcome": "x",
                    "final_state_hash": "y",
                    "artifact_class": "z",
                }
            )

    def test_defaults_emitting_layer(self):
        result = validate_result_artifact(
            {
                "trace_id": "t",
                "execution_outcome": "x",
                "final_state_hash": "y",
                "artifact_class": "z",
            }
        )
        assert result["emitting_layer"] == "L2"


# =====================================================================
# 2. HealingPlan validator
# =====================================================================


class TestHealingPlanValidator:
    """Validator accepts dataclass and dict, rejects missing fields."""

    def test_accepts_dataclass(self, healing_plan_dc):
        result = validate_healing_plan(healing_plan_dc)
        assert result["trace_id"] == "trace-hp1"
        assert result["plan_id"] == "plan-001"
        assert result["manifests"] == ["manifest-a", "manifest-b"]
        assert result["semantic_clock_tick"] == 5
        assert result["policy_liaison_node"] == "node-alpha"
        assert result["emitting_layer"] == "L2"

    def test_accepts_dict(self, healing_plan_dict):
        result = validate_healing_plan(healing_plan_dict)
        assert result["trace_id"] == "trace-hp1"
        assert result["plan_id"] == "plan-001"

    def test_missing_trace_id_fails(self):
        with pytest.raises(ValueError, match="VALIDATE_HEALING_PLAN.*trace_id"):
            validate_healing_plan(
                {
                    "plan_id": "p",
                    "manifests": [],
                    "semantic_clock_tick": 0,
                    "policy_liaison_node": "n",
                }
            )

    def test_missing_plan_id_fails(self):
        with pytest.raises(ValueError, match="VALIDATE_HEALING_PLAN.*plan_id"):
            validate_healing_plan(
                {
                    "trace_id": "t",
                    "manifests": [],
                    "semantic_clock_tick": 0,
                    "policy_liaison_node": "n",
                }
            )

    def test_negative_clock_tick_fails(self):
        with pytest.raises(ValueError, match="VALIDATE_HEALING_PLAN.*semantic_clock_tick"):
            validate_healing_plan(
                {
                    "trace_id": "t",
                    "plan_id": "p",
                    "manifests": [],
                    "semantic_clock_tick": -1,
                    "policy_liaison_node": "n",
                }
            )

    def test_tuple_manifests_coerced_to_list(self, healing_plan_dc):
        result = validate_healing_plan(healing_plan_dc)
        assert isinstance(result["manifests"], list)


# =====================================================================
# 3. IncidentArtifact validator
# =====================================================================


class TestIncidentArtifactValidator:
    """Validator accepts dataclass and dict, rejects missing fields."""

    def test_accepts_dataclass(self):
        dc = IncidentArtifact(
            trace_id="trace-i1",
            incident_id="inc-001",
            correlation_hash="hash-abc",
            severity_enum=SeverityEnum.ERROR,
            telemetry_events=["event-1", "event-2"],
        )
        result = validate_incident_artifact(dc)
        assert result["trace_id"] == "trace-i1"
        assert result["severity_enum"] == "error"
        assert result["telemetry_events"] == ["event-1", "event-2"]

    def test_accepts_dict(self):
        d = {
            "trace_id": "trace-i2",
            "incident_id": "inc-002",
            "correlation_hash": "hash-def",
            "severity_enum": "warning",
            "telemetry_events": ["e1"],
        }
        result = validate_incident_artifact(d)
        assert result["incident_id"] == "inc-002"

    def test_missing_incident_id_fails(self):
        with pytest.raises(ValueError, match="VALIDATE_INCIDENT_ARTIFACT.*incident_id"):
            validate_incident_artifact(
                {
                    "trace_id": "t",
                    "correlation_hash": "h",
                    "severity_enum": "error",
                    "telemetry_events": [],
                }
            )


# =====================================================================
# 4. StaleWriteIncident validator
# =====================================================================


class TestStaleWriteIncidentValidator:
    """Validator accepts dataclass and dict, rejects missing fields."""

    def test_accepts_dataclass(self):
        dc = StaleWriteIncident(
            trace_id="trace-sw1",
            target_path="/foo/bar.py",
            expected_hash="exp-hash",
            actual_hash="act-hash",
            semantic_clock_tick=3,
        )
        result = validate_stale_write_incident(dc)
        assert result["trace_id"] == "trace-sw1"
        assert result["target_path"] == "/foo/bar.py"
        assert result["semantic_clock_tick"] == 3

    def test_accepts_dict(self):
        d = {
            "trace_id": "trace-sw2",
            "target_path": "/baz.py",
            "expected_hash": "e",
            "actual_hash": "a",
            "semantic_clock_tick": 0,
        }
        result = validate_stale_write_incident(d)
        assert result["target_path"] == "/baz.py"

    def test_missing_target_path_fails(self):
        with pytest.raises(ValueError, match="VALIDATE_STALE_WRITE_INCIDENT.*target_path"):
            validate_stale_write_incident(
                {
                    "trace_id": "t",
                    "expected_hash": "e",
                    "actual_hash": "a",
                    "semantic_clock_tick": 0,
                }
            )

    def test_negative_clock_tick_fails(self):
        with pytest.raises(ValueError, match="VALIDATE_STALE_WRITE_INCIDENT.*semantic_clock_tick"):
            validate_stale_write_incident(
                {
                    "trace_id": "t",
                    "target_path": "/p",
                    "expected_hash": "e",
                    "actual_hash": "a",
                    "semantic_clock_tick": -5,
                }
            )


# =====================================================================
# 5. Bridge adapters — round-trip
# =====================================================================


class TestBridgeAdapters:
    """Bridge adapters preserve data without mutation."""

    def test_result_artifact_dict_roundtrip(self, result_artifact_dict):
        out = to_result_artifact_dict(result_artifact_dict)
        assert out == result_artifact_dict

    def test_result_artifact_dc_lossless(self, result_artifact_dc):
        out = to_result_artifact_dict(result_artifact_dc)
        assert out["trace_id"] == "trace-r1"
        assert out["artifact_class"] == "RESULT"

    def test_healing_plan_dict_roundtrip(self, healing_plan_dict):
        out = to_healing_plan_dict(healing_plan_dict)
        assert out == healing_plan_dict

    def test_healing_plan_dc_lossless(self, healing_plan_dc):
        out = to_healing_plan_dict(healing_plan_dc)
        assert out["trace_id"] == "trace-hp1"
        assert out["manifests"] == ["manifest-a", "manifest-b"]

    def test_incident_dict_roundtrip(self):
        d = {
            "trace_id": "t",
            "incident_id": "i",
            "correlation_hash": "h",
            "severity_enum": "error",
            "telemetry_events": ["e1"],
        }
        assert to_incident_artifact_dict(d) == d

    def test_stale_write_dict_roundtrip(self):
        d = {
            "trace_id": "t",
            "target_path": "/p",
            "expected_hash": "e",
            "actual_hash": "a",
            "semantic_clock_tick": 0,
        }
        assert to_stale_write_incident_dict(d) == d

    def test_factory_result_artifact(self, result_artifact_dc):
        out = make_result_artifact_from_dataclass(result_artifact_dc)
        assert out["trace_id"] == "trace-r1"

    def test_factory_healing_plan(self, healing_plan_dc):
        out = make_healing_plan_from_dataclass(healing_plan_dc)
        assert out["plan_id"] == "plan-001"


# =====================================================================
# 6. Structural: TD module exists and exports expected names
# =====================================================================


class TestStructural:
    """TypedDict SSOT module exists with correct exports."""

    def test_td_module_exists(self):
        td_path = Path("agentic_core/L0_routing/types/artifact_typed_compat_types.py")
        assert td_path.exists(), f"Missing: {td_path}"

    def test_validate_module_exists(self):
        val_path = Path("agentic_core/L0_routing/types/artifact_validate_compat_types.py")
        assert val_path.exists(), f"Missing: {val_path}"

    def test_td_module_exports_expected_names(self):
        td_path = Path("agentic_core/L0_routing/types/artifact_typed_compat_types.py")
        source = td_path.read_text(encoding="utf-8")
        tree = ast.parse(source)

        # Find __all__
        all_names: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "__all__":
                        if isinstance(node.value, ast.List):
                            for elt in node.value.elts:
                                if isinstance(elt, ast.Constant):
                                    all_names.append(elt.value)

        expected = {"ResultArtifactTD", "HealingPlanTD", "IncidentArtifactTD", "StaleWriteIncidentTD"}
        missing = expected - set(all_names)
        assert not missing, f"Missing from __all__: {missing}"

    def test_no_dataclass_signature_changes(self):
        """Verify routing_artifact_types.py still has the original dataclass definitions (no breaking changes)."""
        types_path = Path("agentic_core/L0_routing/types/routing_artifact_types.py")
        source = types_path.read_text(encoding="utf-8")
        tree = ast.parse(source)

        class_names = [n.name for n in tree.body if isinstance(n, ast.ClassDef)]
        assert "ResultArtifact" in class_names, (
            "ResultArtifact dataclass missing from routing_artifact_types.py"
        )
        assert "HealingPlan" in class_names, "HealingPlan dataclass missing from routing_artifact_types.py"
        assert "IncidentArtifact" in class_names, (
            "IncidentArtifact dataclass missing from routing_artifact_types.py"
        )
        assert "StaleWriteIncident" in class_names, (
            "StaleWriteIncident dataclass missing from routing_artifact_types.py"
        )

    def test_unsupported_type_raises_type_error(self):
        """Passing a non-dict, non-dataclass object raises TypeError."""
        with pytest.raises(TypeError, match="UNSUPPORTED_TYPE"):
            validate_result_artifact("not_a_dict_or_dc")

        with pytest.raises(TypeError, match="UNSUPPORTED_TYPE"):
            validate_healing_plan(42)
