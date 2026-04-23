"""Tests for ADR-027 Anthropic-alignment privacy defaults in the runtime ADG materializer.

Covers:
- Tool I/O redaction is ON by default (OTEL_MCP_LOG_TOOL_CONTENT unset or "0")
- Opt-in keeps content verbatim (OTEL_MCP_LOG_TOOL_CONTENT=1)
- attributes_json is capped at OTEL_MCP_SPAN_ATTR_MAX_BYTES with marker
"""

from __future__ import annotations

import json
import os

import pytest

from system_learning.runtime_adg.materializer import (
    _TRUNCATED_SUFFIX,
    _cap_attributes_json,
    _extract_node,
    _redact_tool_content,
)


def _span(**overrides):
    base = {
        "span_id": "s1",
        "name": "tool.search",
        "kind": "tool",
        "layer": "L2",
        "component": "Tool.search",
        "ts_utc": 1700000000,
        "duration_ms": 12.5,
        "status": "ok",
        "attributes": {},
    }
    base.update(overrides)
    return base


class TestRedaction:
    def test_redact_tool_content_replaces_sensitive_keys(self):
        redacted = _redact_tool_content(
            {
                "tool_input": "secret-query",
                "tool_output": "secret-response",
                "tool_name": "search",  # non-sensitive, must be preserved
            }
        )
        assert redacted["tool_input"] == "[REDACTED]"
        assert redacted["tool_output"] == "[REDACTED]"
        assert redacted["tool_name"] == "search"

    def test_redact_tolerates_non_dict(self):
        assert _redact_tool_content("not-a-dict") == {}  # type: ignore[arg-type]


class TestExtractNodeDefaultPrivacy:
    def test_default_env_redacts_tool_content(self, monkeypatch):
        monkeypatch.delenv("OTEL_MCP_LOG_TOOL_CONTENT", raising=False)
        span = _span(
            attributes={
                "tool_input": "very-sensitive",
                "tool_output": "also-sensitive",
                "tool_name": "search",
            }
        )
        node = _extract_node(span)
        assert node is not None
        attrs = json.loads(node.attributes_json)
        assert attrs["tool_input"] == "[REDACTED]"
        assert attrs["tool_output"] == "[REDACTED]"
        assert attrs["tool_name"] == "search"

    def test_optin_preserves_tool_content(self, monkeypatch):
        monkeypatch.setenv("OTEL_MCP_LOG_TOOL_CONTENT", "1")
        span = _span(
            attributes={
                "tool_input": "very-sensitive",
                "tool_name": "search",
            }
        )
        node = _extract_node(span)
        assert node is not None
        attrs = json.loads(node.attributes_json)
        assert attrs["tool_input"] == "very-sensitive"


class TestAttributeCap:
    def test_cap_under_limit_returns_verbatim(self):
        s = '{"k":"v"}'
        assert _cap_attributes_json(s, 1024) == s

    def test_cap_over_limit_truncates_with_marker(self):
        big = json.dumps({"k": "x" * 2000})
        capped = _cap_attributes_json(big, 256)
        assert capped.endswith(_TRUNCATED_SUFFIX)
        assert len(capped.encode("utf-8")) <= 256

    def test_extract_node_applies_byte_cap_via_env(self, monkeypatch):
        monkeypatch.setenv("OTEL_MCP_LOG_TOOL_CONTENT", "1")
        monkeypatch.setenv("OTEL_MCP_SPAN_ATTR_MAX_BYTES", "1024")
        span = _span(attributes={"payload": "y" * 5000})
        node = _extract_node(span)
        assert node is not None
        assert len(node.attributes_json.encode("utf-8")) <= 1024
        assert node.attributes_json.endswith(_TRUNCATED_SUFFIX)
