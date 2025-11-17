import pytest

from arbitration_engine import ArbitrationEngine


def test_arbitration_escalate_on_safety_blocked():
    engine = ArbitrationEngine()
    state = {"messages": ["msg"]}
    qa_report = {"findings": []}
    safety_patch = {"safety_gateway": {"status": "blocked"}}

    result = engine.evaluate(state, qa_report, safety_patch)

    assert result["action"] == "escalate"


def test_arbitration_retry_on_pending_qa():
    engine = ArbitrationEngine()
    state = {"messages": ["msg"]}
    qa_report = {"findings": [{"status": "pending"}]}
    safety_patch = {"safety_gateway": {"status": "allowed"}}

    result = engine.evaluate(state, qa_report, safety_patch)

    assert result["action"] == "retry"


def test_arbitration_replan_on_empty_messages():
    engine = ArbitrationEngine()
    state = {"messages": []}
    qa_report = {"findings": []}
    safety_patch = {"safety_gateway": {"status": "allowed"}}

    result = engine.evaluate(state, qa_report, safety_patch)

    assert result["action"] == "replan"


def test_arbitration_accept_default():
    engine = ArbitrationEngine()
    state = {"messages": ["msg"]}
    qa_report = {"findings": []}
    safety_patch = {"safety_gateway": {"status": "allowed"}}

    result = engine.evaluate(state, qa_report, safety_patch)

    assert result["action"] == "accept"
