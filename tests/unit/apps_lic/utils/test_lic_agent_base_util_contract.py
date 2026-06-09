"""W8 contract tests for the zero-cover LIC agent base utility surface."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from apps_lic.utils.lic_agent_base_util import APPS_LIC_DIR, LICAgentBase


def _bare_agent(monkeypatch: pytest.MonkeyPatch) -> LICAgentBase:
    agent = object.__new__(LICAgentBase)
    agent._resource_prefix = "lic"
    agent._namespace = APPS_LIC_DIR
    agent._guardrails = None
    monkeypatch.setattr(agent, "guardrails_validate_cache_key", lambda key: True)
    monkeypatch.setattr(agent, "guardrails_validate_cache_value", lambda value: True)
    return agent


def test_cache_namespacing_and_domain_isolation_are_apps_lic_only(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    agent = _bare_agent(monkeypatch)
    payload: dict[str, Any] = {"pattern": "ok"}

    assert agent.get_namespaced_cache_key("candidate:1") == "apps_lic:lic:candidate:1"
    assert agent.validate_domain_pattern({}) is True
    assert agent.validate_domain_pattern({"domain": APPS_LIC_DIR}) is True
    assert agent.validate_domain_pattern({"_domain": APPS_LIC_DIR}) is True
    assert agent.validate_domain_pattern({"domain": "apps_rg"}) is False

    success, namespaced_key = agent.isolate_cache_operation(
        "set",
        "candidate:1",
        payload,
    )
    assert success is True
    assert namespaced_key == "apps_lic:lic:candidate:1"
    assert payload["_domain"] == APPS_LIC_DIR
    assert payload["_namespace"] == APPS_LIC_DIR

    monkeypatch.setattr(agent, "guardrails_validate_cache_key", lambda key: False)
    assert agent.isolate_cache_operation("get", "unsafe:key") == (False, None)


def test_safe_cache_set_returns_false_on_backend_error_without_sending_or_writing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    agent = _bare_agent(monkeypatch)
    updates: list[int] = []

    monkeypatch.setattr(agent, "check_and_enforce_rate_limit", lambda operation="request": True)
    monkeypatch.setattr(agent, "check_cache_capacity", lambda: True)
    monkeypatch.setattr(agent, "update_cache_metrics", lambda delta=1: updates.append(delta))

    def _raise_runtime_error(key: str, value: Any) -> bool:
        _ = (key, value)
        raise RuntimeError("cache backend unavailable")

    monkeypatch.setattr(agent, "ml_cache_set", _raise_runtime_error)

    assert agent.safe_cache_set("candidate:1", {"ok": True}) is False
    assert updates == []

    source = Path("apps_lic/utils/lic_agent_base_util.py").read_text(encoding="utf-8")
    for forbidden in ("connector_send", "linkedin_send", "email_outbox_send", "send_now"):
        assert forbidden not in source
