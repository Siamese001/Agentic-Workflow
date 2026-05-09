"""Tool Output Airlock — isolates model/tool responses before downstream consumption.

Ensures tool/model output is data-only and cannot:
- Widen authority
- Modify route/provider/model/schema
- Grant write permission
- Bypass HITL
- Commit durable state

Per PROMPT_BOUNDARY_CONTRACT.md §3.3.
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any

from apps_rg.prompt_assembly._pa_boundary import make_pa_boundary_receipt, PABoundaryStatus
from apps_rg.airlocks._otel_spans import airlock_span

_log = logging.getLogger(__name__)


class ToolOutputStatus(str, Enum):
    """Status of tool output validation."""

    DATA_ONLY = "DATA_ONLY"  # Clean, data-only output
    CONTAINS_INSTRUCTIONS = "CONTAINS_INSTRUCTIONS"  # Detected instruction-like content
    OVERRREACH_ATTEMPT = "OVERREACH_ATTEMPT"  # Attempt to widen scope/authority
    QUARANTINED = "QUARANTINED"  # Quarantined pending review


class OverreachClass(str, Enum):
    """Classes of overreach attempts."""

    AUTHORITY_WIDEN = "authority_widen_attempt"
    ROUTE_MODIFY = "route_modification_attempt"
    PROVIDER_SWITCH = "provider_switch_attempt"
    MODEL_SWITCH = "model_switch_attempt"
    SCHEMA_CHANGE = "schema_change_attempt"
    WRITE_PERMISSION = "write_permission_attempt"
    HITL_BYPASS = "hitl_bypass_attempt"
    STATE_COMMIT = "state_commit_attempt"
    TOOL_CHANGE = "tool_change_attempt"


@dataclass(frozen=True)
class ToolOutputResult:
    """Result of tool output airlock processing."""

    output_hash: str
    status: str
    overreach_detections: list[dict[str, Any]]
    sanitized_output: str | None
    receipt: dict[str, Any]


class ToolOutputAirlock:
    """Tool Output Airlock.

    Validates model/tool responses are data-only and do not attempt
    to modify execution parameters or bypass controls.
    """

    def __init__(self):
        # Patterns that suggest overreach attempts
        self._overreach_patterns: list[tuple[str, OverreachClass]] = [
            # Authority/route changes
            (r"now\s+you\s+(?:should|must|can|may)", OverreachClass.AUTHORITY_WIDEN),
            (r"change\s+(?:the\s+)?route\s+(?:to|into)", OverreachClass.ROUTE_MODIFY),
            (r"switch\s+(?:to\s+)?(?:provider|model|llm)", OverreachClass.PROVIDER_SWITCH),
            (r"use\s+(?:a\s+)?different\s+(?:model|provider)", OverreachClass.MODEL_SWITCH),
            # Schema/format changes
            (r"output\s+(?:should\s+)?(?:be\s+)?(?:in\s+)?(?:json|yaml|xml|csv)", OverreachClass.SCHEMA_CHANGE),
            (r"format\s+(?:as|to)\s+", OverreachClass.SCHEMA_CHANGE),
            # Write/state changes
            (r"write\s+(?:this|that)\s+(?:to|into)\s+(?:disk|file|database|db)", OverreachClass.WRITE_PERMISSION),
            (r"commit\s+(?:this|the|your)\s+changes", OverreachClass.STATE_COMMIT),
            (r"save\s+(?:this|that)\s+(?:state|data)", OverreachClass.STATE_COMMIT),
            # HITL bypass
            (r"skip\s+(?:the\s+)?(?:human|hitl|review)\s+(?:review|step|check)", OverreachClass.HITL_BYPASS),
            (r"bypass\s+(?:the\s+)?(?:human|hitl|review)", OverreachClass.HITL_BYPASS),
            # Tool changes
            (r"call\s+(?:a\s+)?different\s+tool", OverreachClass.TOOL_CHANGE),
            (r"use\s+(?:the\s+)?(?:function|api)\s+instead", OverreachClass.TOOL_CHANGE),
        ]
        import re
        self._compiled_patterns = [(re.compile(p, re.IGNORECASE), oc) for p, oc in self._overreach_patterns]

        # Instruction-like content patterns (not overreach, but flagged)
        self._instruction_patterns = [
            re.compile(r"you\s+should\s+now\s+", re.IGNORECASE),
            re.compile(r"next\s*,?\s*(?:you\s+)?(?:need\s+to|should)", re.IGNORECASE),
            re.compile(r"(?:as\s+)?(?:your\s+)?(?:next\s+)?(?:step|action|task)", re.IGNORECASE),
        ]

    def process(
        self,
        tool_output: str,
        *,
        request_id: str = "",
        run_id: str = "",
        trace_id: str = "",
        route_id: str = "",
        tool_name: str = "",
        step_name: str = "",
        schema_hint: dict[str, Any] | None = None,
    ) -> ToolOutputResult:
        """Process tool output through airlock.

        Args:
            tool_output: Raw tool/model response text
            request_id: Request identifier for receipt
            run_id: Run identifier for receipt
            trace_id: Trace identifier for receipt
            route_id: Route identifier for receipt
            tool_name: Name of tool that produced output
            step_name: L2 step name consuming the output
            schema_hint: Optional expected schema for validation

        Returns:
            ToolOutputResult with validation status and receipt
        """
        output_hash = hashlib.sha256(tool_output.encode()).hexdigest()[:16]

        # Check for overreach attempts
        overreach_detections: list[dict[str, Any]] = []
        for pattern, oclass in self._compiled_patterns:
            for match in pattern.finditer(tool_output):
                overreach_detections.append({
                    "overreach_class": oclass.value,
                    "matched_text": match.group(0)[:100],
                    "position": match.start(),
                })

        # Check for instruction-like content (informational only)
        instruction_hints = 0
        for pattern in self._instruction_patterns:
            instruction_hints += len(pattern.findall(tool_output))

        # Determine status
        if overreach_detections:
            status = ToolOutputStatus.OVERRREACH_ATTEMPT.value
            reason_codes = ["OVERREACH_DETECTED", "QUARANTINE_RECOMMENDED"]
            sanitized = self._sanitize_output(tool_output, overreach_detections)
        elif instruction_hints > 2:  # Arbitrary threshold
            status = ToolOutputStatus.CONTAINS_INSTRUCTIONS.value
            reason_codes = ["INSTRUCTION_LIKE_CONTENT", "REVIEW_RECOMMENDED"]
            sanitized = None
        else:
            status = ToolOutputStatus.DATA_ONLY.value
            reason_codes = ["DATA_ONLY"]
            sanitized = None

        # Validate against schema hint if provided (basic key check)
        schema_validation = "skipped"
        if schema_hint and overreach_detections:
            # Can't validate if overreach detected
            schema_validation = "blocked_by_overreach"
        elif schema_hint:
            try:
                parsed = json.loads(tool_output)
                if isinstance(parsed, dict):
                    missing_keys = [k for k in schema_hint.get("required_keys", []) if k not in parsed]
                    if missing_keys:
                        schema_validation = f"missing_keys:{','.join(missing_keys)}"
                    else:
                        schema_validation = "passed"
            except json.JSONDecodeError:
                schema_validation = "not_json"

        receipt = make_pa_boundary_receipt(
            request_id=request_id or "NOT_BOUND",
            run_id=run_id or "NOT_BOUND",
            trace_id=trace_id or "NOT_BOUND",
            route_id=route_id or "NOT_BOUND",
            policy_hash="tool_output_airlock_v1",
            blueprint_hash=output_hash,
            prompt_hash="NOT_BOUND",  # Tool output is not a prompt
            compiled_artifact_hash="NOT_BOUND",
            bom_hash="NOT_BOUND",
            registry_hash="NOT_BOUND",
            template_hash="NOT_BOUND",
            source_refs={
                "tool_name": tool_name or "NOT_BOUND",
                "step_name": step_name or "NOT_BOUND",
                "schema_validation": schema_validation,
            },
            lineage_refs={
                "airlock": "TOOL_OUTPUT",
                "overreach_count": str(len(overreach_detections)),
                "instruction_hints": str(instruction_hints),
            },
            status=PABoundaryStatus.PA_SECURITY_PASS if status == ToolOutputStatus.DATA_ONLY.value else PABoundaryStatus.PA_SECURITY_GAP,
            reason_codes=reason_codes,
            unavailable_fields=["prompt_hash", "compiled_artifact_hash", "bom_hash", "registry_hash", "template_hash"],
        )

        _log.info(
            "[TOOL] processed: tool=%s step=%s status=%s overreach=%d",
            tool_name, step_name, status, len(overreach_detections),
        )

        if status == ToolOutputStatus.OVERRREACH_ATTEMPT.value:
            span_name = "pa.unsafe_payload_rejection"
        elif status == ToolOutputStatus.CONTAINS_INSTRUCTIONS.value:
            span_name = "pa.injection_neutralization"
        else:
            span_name = "pa.airlock_security_pass"
        with airlock_span(
            span_name,
            airlock="TOOL_OUTPUT",
            request_id=request_id,
            run_id=run_id,
            trace_id=trace_id,
            tool_name=tool_name,
            step_name=step_name,
            status=status,
            overreach_count=len(overreach_detections),
        ):
            pass

        return ToolOutputResult(
            output_hash=output_hash,
            status=status,
            overreach_detections=overreach_detections,
            sanitized_output=sanitized,
            receipt=receipt.to_dict(),
        )

    def _sanitize_output(
        self,
        output: str,
        detections: list[dict[str, Any]],
    ) -> str:
        """Sanitize output by masking overreach attempts."""
        # Simple replacement strategy: mask the detected sections
        sanitized = output
        for det in sorted(detections, key=lambda d: d["position"], reverse=True):
            start = det["position"]
            end = start + len(det["matched_text"])
            replacement = f"[AIRLOCK_MASKED:{det['overreach_class']}]"
            sanitized = sanitized[:start] + replacement + sanitized[end:]
        return sanitized


def process_tool_output(
    tool_output: str,
    *,
    request_id: str = "",
    run_id: str = "",
    trace_id: str = "",
    route_id: str = "",
    tool_name: str = "",
    step_name: str = "",
    schema_hint: dict[str, Any] | None = None,
) -> ToolOutputResult:
    """Convenience function for tool output airlock processing."""
    airlock = ToolOutputAirlock()
    return airlock.process(
        tool_output,
        request_id=request_id,
        run_id=run_id,
        trace_id=trace_id,
        route_id=route_id,
        tool_name=tool_name,
        step_name=step_name,
        schema_hint=schema_hint,
    )


__all__ = [
    "ToolOutputAirlock",
    "ToolOutputResult",
    "ToolOutputStatus",
    "OverreachClass",
    "process_tool_output",
]
