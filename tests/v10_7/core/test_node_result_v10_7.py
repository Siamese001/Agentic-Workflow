import pytest

from core_v10_7.models import NodeResult, NodeStatus
from agent_orchestration_v10_7 import node_success, node_error


def test_node_status_values():
    values = {status.value for status in NodeStatus}
    assert values == {
        "success",
        "retriable_error",
        "fatal_error",
        "blocked",
    }


def test_node_result_serialization_round_trip():
    result = NodeResult(
        node="example",
        status=NodeStatus.SUCCESS,
        error_kind=None,
        error_message=None,
        payload={"foo": "bar"},
    )
    serialized = result.model_dump()
    assert serialized["node"] == "example"
    assert serialized["status"] == NodeStatus.SUCCESS.value
    assert serialized["payload"] == {"foo": "bar"}

    deserialized = NodeResult.model_validate(serialized)
    assert deserialized == result


def test_node_success_helper_builds_successful_result():
    payload = {"state": {"foo": "bar"}}
    result = node_success("test_node", payload)

    assert result["node"] == "test_node"
    assert result["status"] == NodeStatus.SUCCESS.value
    assert result["payload"] == payload


def test_node_error_helper_records_error_details():
    payload = {"state": {"foo": "bar"}}
    result = node_error(
        "test_node",
        status=NodeStatus.FATAL_ERROR,
        error_kind="ValueError",
        error_message="bad value",
        payload=payload,
    )

    assert result["node"] == "test_node"
    assert result["status"] == NodeStatus.FATAL_ERROR.value
    assert result["error_kind"] == "ValueError"
    assert result["error_message"] == "bad value"
    assert result["payload"] == payload
