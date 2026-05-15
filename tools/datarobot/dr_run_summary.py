"""Emit a DataRobot-friendly run summary span for agentic spine missions."""

from __future__ import annotations

import logging
from typing import Any

from tools.datarobot.dr_otel_config import configure_datarobot_otel, is_datarobot_export_enabled

logger = logging.getLogger(__name__)

_MAX_ATTR_LEN = 4000


def _truncate(value: str, limit: int = _MAX_ATTR_LEN) -> str:
    if len(value) <= limit:
        return value
    return value[: limit - 3] + "..."


def edge_kinds_from_bridge(bridge: Any) -> list[str]:
    """Collect unique ``adg.*`` edge kinds buffered by the lifecycle bridge."""
    spans = getattr(bridge, "_spans", None)
    if not spans:
        return []
    kinds: set[str] = set()
    for span in spans:
        name = span.get("name", "")
        if isinstance(name, str) and name.startswith("adg."):
            kinds.add(name[4:])
    return sorted(kinds)


def emit_datarobot_run_summary(
    mission: str,
    *,
    prompt: str = "",
    completion: str = "",
    tools: list[str] | None = None,
    span_count: int = 0,
    success: bool = True,
    extra_attributes: dict[str, str | int | float | bool] | None = None,
) -> bool:
    """Export one summary trace with attributes DataRobot's Traces UI recognizes.

    Returns True when a span was emitted; False when export is disabled or OTel missing.
    """
    if not is_datarobot_export_enabled():
        return False
    if not configure_datarobot_otel():
        return False

    try:
        from opentelemetry import trace
    except ImportError:
        return False

    tracer = trace.get_tracer("agentic-workflow.datarobot")
    tool_list = tools or []
    primary_tool = tool_list[0] if tool_list else "agentic_spine"

    with tracer.start_as_current_span(mission) as span:
        if prompt:
            span.set_attribute("gen_ai.prompt", _truncate(prompt))
        if completion:
            span.set_attribute("gen_ai.completion", _truncate(completion))
        span.set_attribute("tool_name", primary_tool)
        span.set_attribute("agentic.mission", mission)
        span.set_attribute("agentic.span_count", span_count)
        span.set_attribute("agentic.success", success)
        if tool_list:
            span.set_attribute("tool.parameters", _truncate(",".join(tool_list)))
        if extra_attributes:
            for key, value in extra_attributes.items():
                span.set_attribute(key, value)

    logger.info(
        "DataRobot run summary exported mission=%s spans=%d tools=%d",
        mission,
        span_count,
        len(tool_list),
    )
    return True
