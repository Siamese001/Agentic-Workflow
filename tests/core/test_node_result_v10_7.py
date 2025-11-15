import pytest

from core_v10_7 import NodeResult, NodeStatus


def test_node_result_serialization_includes_expected_fields():
    payload = {"foo": "bar"}
    result = NodeResult(node="unit", status=NodeStatus.SUCCESS, payload=payload)

    data = result.model_dump()

    assert data["node"] == "unit"
    assert data["status"] == NodeStatus.SUCCESS
    assert data["payload"] == payload
    assert data["error_kind"] is None
    assert data["error_message"] is None


@pytest.mark.parametrize("status", list(NodeStatus))
def test_node_result_handles_all_status_values(status):
    result = NodeResult(node="node", status=status)
    serialized = result.model_dump()

    assert serialized["status"] == status
    assert serialized["payload"] == {}


def test_node_result_defaults_to_empty_payload():
    result = NodeResult(node="node", status=NodeStatus.BLOCKED)
    assert result.payload == {}
