"""Unit tests for :class:`AppIngressRunner` and the 6 per-app factories.

Covers W8.1–W8.6 from plan ``request-intake-w7-deferred-4c8e1f``.

The factories are verified parametrically: for each app we assert that
(a) a complete envelope is dispatched, (b) a missing-field envelope yields
:class:`ClarificationRequired`, and (c) a structurally invalid envelope is
rejected by the gate.
"""

from __future__ import annotations

from typing import Any, Callable

import pytest

from agentic_core.L5_safety.enforcement.ingress import (
    ClarificationRequired,
    IngressEnvelopeCheck,
)

from apps_eval.integrations.eval_ingress_runner import (
    EVAL_REQUIRED_FIELDS,
    make_eval_ingress_runner,
)
from apps_exec.integrations.exec_ingress_runner import (
    EXEC_REQUIRED_FIELDS,
    make_exec_ingress_runner,
)
from apps_lic.integrations.lic_ingress_runner import (
    LIC_REQUIRED_FIELDS,
    make_lic_ingress_runner,
)
from apps_rfp.integrations.rfp_ingress_runner import (
    RFP_REQUIRED_FIELDS,
    make_rfp_ingress_runner,
)
from apps_underwriting_ai.integrations.uw_ingress_runner import (
    UW_REQUIRED_FIELDS,
    make_uw_ingress_runner,
)


FactoryFn = Callable[..., Any]


APP_CASES: list[tuple[str, FactoryFn, tuple[str, ...]]] = [
    ("eval", make_eval_ingress_runner, EVAL_REQUIRED_FIELDS),
    ("exec", make_exec_ingress_runner, EXEC_REQUIRED_FIELDS),
    ("lic", make_lic_ingress_runner, LIC_REQUIRED_FIELDS),
    ("rfp", make_rfp_ingress_runner, RFP_REQUIRED_FIELDS),
    ("uw", make_uw_ingress_runner, UW_REQUIRED_FIELDS),
]


def _complete_payload(fields: tuple[str, ...]) -> dict[str, str]:
    return {f: f"value-for-{f}" for f in fields}


@pytest.mark.parametrize("app_name,factory,fields", APP_CASES, ids=[c[0] for c in APP_CASES])
def test_happy_path_dispatches(app_name: str, factory: FactoryFn, fields: tuple[str, ...]) -> None:
    calls: list[dict[str, Any]] = []

    def dispatch(payload: dict[str, Any]) -> str:
        calls.append(payload)
        return f"{app_name}-dispatched"

    runner = factory(dispatch, gate=IngressEnvelopeCheck())
    out = runner.handle_http(
        headers={"X-Caller-Identity": f"svc-{app_name}", "X-Request-Id": f"{app_name}-1"},
        body=_complete_payload(fields),
    )
    assert out == f"{app_name}-dispatched"
    assert len(calls) == 1
    assert all(k in calls[0] for k in fields)


@pytest.mark.parametrize("app_name,factory,fields", APP_CASES, ids=[c[0] for c in APP_CASES])
def test_missing_required_field_clarifies(app_name: str, factory: FactoryFn, fields: tuple[str, ...]) -> None:
    calls: list[Any] = []

    def dispatch(payload: dict[str, Any]) -> str:
        calls.append(payload)
        return "should-not-run"

    runner = factory(dispatch, gate=IngressEnvelopeCheck())
    incomplete = _complete_payload(fields)
    incomplete.pop(fields[0])  # drop the first required field
    out = runner.handle_http(
        headers={"X-Caller-Identity": f"svc-{app_name}", "X-Request-Id": f"{app_name}-miss"},
        body=incomplete,
    )
    assert isinstance(out, ClarificationRequired), f"expected clarification for {app_name}"
    assert fields[0] in out.reason
    assert calls == []


@pytest.mark.parametrize("app_name,factory,fields", APP_CASES, ids=[c[0] for c in APP_CASES])
def test_oversized_payload_rejected(app_name: str, factory: FactoryFn, fields: tuple[str, ...]) -> None:
    calls: list[Any] = []

    def dispatch(payload: dict[str, Any]) -> str:
        calls.append(payload)
        return "should-not-run"

    runner = factory(dispatch, gate=IngressEnvelopeCheck(max_payload_bytes=50))
    payload = _complete_payload(fields)
    payload[fields[0]] = "x" * 5000
    out = runner.handle_http(
        headers={"X-Caller-Identity": f"svc-{app_name}", "X-Request-Id": f"{app_name}-big"},
        body=payload,
    )
    assert isinstance(out, tuple), f"expected rejection tuple for {app_name}"
    status, _, body = out
    assert status == 413
    assert "PAYLOAD_OVERSIZED" in body
    assert calls == []


def test_chat_path_for_one_app() -> None:
    # Chat adapter wraps the message in {"intent": ...} which has none of the
    # required fields, so chat paths for these app shapes should clarify.
    calls: list[Any] = []
    runner = make_exec_ingress_runner(
        lambda p: calls.append(p) or "ran",
        gate=IngressEnvelopeCheck(),
    )
    out = runner.handle_chat({"user_id": "alice", "message": "run my thing"})
    assert isinstance(out, ClarificationRequired)
    assert "task_id" in out.reason


def test_non_dict_payload_clarifies() -> None:
    runner = make_eval_ingress_runner(
        lambda p: "ran",
        gate=IngressEnvelopeCheck(),
    )
    # HTTP body = bare string; after normalization stays a string → not a dict.
    out = runner.handle_http(
        headers={"X-Caller-Identity": "svc", "X-Request-Id": "str-1"},
        body="raw string not object",
    )
    assert isinstance(out, ClarificationRequired)
    assert "must be an object" in out.reason


def test_parse_returning_none_clarifies() -> None:
    # Custom factory that parses to None to exercise the failed-parse branch.
    from agentic_core.runtime.entry.app_ingress_runner import AppIngressRunner

    runner = AppIngressRunner(
        dispatch=lambda _req: "ran",
        parse=lambda _payload: None,
        required_fields=("a", "b"),
        gate=IngressEnvelopeCheck(),
    )
    out = runner.handle_http(
        headers={"X-Caller-Identity": "svc", "X-Request-Id": "parse-1"},
        body={"a": "1", "b": "2"},
    )
    assert isinstance(out, ClarificationRequired)
    assert "could not be parsed" in out.reason
