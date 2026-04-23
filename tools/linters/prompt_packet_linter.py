"""C5 PA conformance linter for assembled PromptEnvelope packets.

Implements the five PA contracts from
``docs/reference/C5_Retrieval_Prompt_Assembly.md``:

  PA.0  canonical block ordering in the serialized packet
  PA.1a schema shape (required keys present, correct types)
  PA.1b block taxonomy (no instructions in document_content,
        no evidence in output_format)
  PA.2a grounding-step presence with a numbered directive
  PA.3a stable-prefix byte stability across repeated serialization

The linter accepts either a ``PromptEnvelope`` dataclass instance (from
``tools/adg/prompt_assembly/contracts.py``) or an already-serialized
``dict`` of the same shape, so it can lint assembled packets in-memory
or stored JSON blobs.

Returns a ``LintReport`` with per-violation records. Structural errors
(wrong type, missing packet entirely) raise ``PromptPacketLintError``.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any

# PA.0 — canonical block order used by `PromptEnvelope.to_dict`.
CANONICAL_BLOCK_ORDER: tuple[str, ...] = (
    "packet_type",
    "packet_id",
    "schema_version",
    "system_block",
    "policy_block",
    "task_block",
    "must_use_evidence",
    "optional_evidence",
    "contradiction_flags",
    "abstain_instructions",
    "refine_instructions",
    "output_schema",
    "replay_metadata",
)

# PA.1a — required keys and their expected Python types.
_REQUIRED_SCHEMA: dict[str, tuple[type, ...]] = {
    "packet_type": (str,),
    "packet_id": (str,),
    "schema_version": (str,),
    "system_block": (str,),
    "policy_block": (str,),
    "task_block": (str,),
    "must_use_evidence": (list,),
    "optional_evidence": (list,),
    "contradiction_flags": (list,),
    "abstain_instructions": (str,),
    "refine_instructions": (str,),
    "output_schema": (dict,),
    "replay_metadata": (dict,),
}

# PA.2a — numbered grounding directive regex (e.g. "1." or "1)" at line start
# after optional whitespace / markdown bullet).
_NUMBERED_DIRECTIVE = re.compile(r"(?m)^\s*(?:[-*]\s*)?1[.)]\s+\S")

# PA.1b — tokens that must NOT appear in document_content blocks.
_FORBIDDEN_IN_DOCUMENT_CONTENT = ("INSTRUCTION:", "SYSTEM:", "ASSISTANT:")
# PA.1b — keys that must NOT appear inside output_schema / output_format.
_FORBIDDEN_IN_OUTPUT_FORMAT = ("evidence", "must_use_evidence", "optional_evidence")


class PromptPacketLintError(TypeError):
    """Raised for structural errors (wrong input type). Not a soft violation."""


@dataclass(frozen=True)
class LintViolation:
    """A single contract violation."""

    contract: str  # e.g. "PA.0", "PA.1a"
    code: str  # short machine-readable code
    message: str
    path: str = ""  # dotted path to the offending field, if any


@dataclass
class LintReport:
    """Result of linting a single packet."""

    packet_id: str
    violations: list[LintViolation] = field(default_factory=list)

    @property
    def is_clean(self) -> bool:
        return not self.violations

    def by_contract(self, contract: str) -> list[LintViolation]:
        return [v for v in self.violations if v.contract == contract]

    def format_report(self) -> str:
        if self.is_clean:
            return f"[OK] packet={self.packet_id!r} clean"
        lines = [f"[FAIL] packet={self.packet_id!r} violations={len(self.violations)}"]
        for v in self.violations:
            path = f" @ {v.path}" if v.path else ""
            lines.append(f"  - {v.contract} {v.code}: {v.message}{path}")
        return "\n".join(lines)


def _coerce_to_dict(packet: Any) -> dict[str, Any]:
    """Accept a PromptEnvelope or a dict; return dict preserving insertion order."""
    if isinstance(packet, dict):
        return packet
    to_dict = getattr(packet, "to_dict", None)
    if callable(to_dict):
        result = to_dict()
        if not isinstance(result, dict):
            raise PromptPacketLintError(
                f"{type(packet).__name__}.to_dict() must return dict, got {type(result).__name__}"
            )
        return result
    raise PromptPacketLintError(
        f"cannot lint {type(packet).__name__}: expected dict or object with to_dict()"
    )


def _check_pa0_ordering(data: dict[str, Any]) -> list[LintViolation]:
    """PA.0 — canonical block order."""
    violations: list[LintViolation] = []
    present_in_order = [k for k in data if k in CANONICAL_BLOCK_ORDER]
    expected_order = [k for k in CANONICAL_BLOCK_ORDER if k in data]
    if present_in_order != expected_order:
        violations.append(
            LintViolation(
                contract="PA.0",
                code="block_order",
                message=(f"block order {present_in_order!r} does not match canonical {expected_order!r}"),
            )
        )
    return violations


def _pa1a_check_one(key: str, allowed_types: tuple[type, ...], data: dict[str, Any]) -> LintViolation | None:
    if key not in data:
        return LintViolation(
            contract="PA.1a",
            code="missing_key",
            message=f"required key {key!r} missing",
            path=key,
        )
    value = data[key]
    if not isinstance(value, allowed_types):
        names = "|".join(t.__name__ for t in allowed_types)
        return LintViolation(
            contract="PA.1a",
            code="wrong_type",
            message=f"{key!r} must be {names}, got {type(value).__name__}",
            path=key,
        )
    return None


def _check_pa1a_schema(data: dict[str, Any]) -> list[LintViolation]:
    """PA.1a — required keys present with correct types."""
    results = [_pa1a_check_one(k, t, data) for k, t in _REQUIRED_SCHEMA.items()]
    return [v for v in results if v is not None]


def _pa1b_scan_item(bucket: str, idx: int, item: Any) -> list[LintViolation]:
    if not isinstance(item, dict):
        return []
    doc = item.get("document_content") or item.get("content") or ""
    if not isinstance(doc, str):
        return []
    upper = doc.upper()
    hits = [f for f in _FORBIDDEN_IN_DOCUMENT_CONTENT if f in upper]
    return [
        LintViolation(
            contract="PA.1b",
            code="instruction_leak_in_evidence",
            message=f"forbidden token {f!r} found in {bucket}[{idx}] document_content",
            path=f"{bucket}[{idx}]",
        )
        for f in hits
    ]


def _pa1b_scan_bucket(bucket: str, data: dict[str, Any]) -> list[LintViolation]:
    items = data.get(bucket)
    if not isinstance(items, list):
        return []
    return [v for idx, item in enumerate(items) for v in _pa1b_scan_item(bucket, idx, item)]


def _pa1b_scan_output_schema(data: dict[str, Any]) -> list[LintViolation]:
    schema = data.get("output_schema")
    if not isinstance(schema, dict):
        return []
    hits = [f for f in _FORBIDDEN_IN_OUTPUT_FORMAT if f in schema]
    return [
        LintViolation(
            contract="PA.1b",
            code="evidence_leak_in_output_schema",
            message=f"output_schema must not contain evidence key {f!r}",
            path=f"output_schema.{f}",
        )
        for f in hits
    ]


def _check_pa1b_taxonomy(data: dict[str, Any]) -> list[LintViolation]:
    """PA.1b — no instructions in document_content, no evidence in output_format."""
    violations: list[LintViolation] = []
    violations.extend(_pa1b_scan_bucket("must_use_evidence", data))
    violations.extend(_pa1b_scan_bucket("optional_evidence", data))
    violations.extend(_pa1b_scan_output_schema(data))
    return violations


def _check_pa2a_grounding(data: dict[str, Any]) -> list[LintViolation]:
    """PA.2a — task_block or policy_block contains a numbered grounding directive."""
    violations: list[LintViolation] = []
    task = data.get("task_block") or ""
    policy = data.get("policy_block") or ""
    combined = f"{policy}\n{task}" if isinstance(policy, str) and isinstance(task, str) else ""
    if not _NUMBERED_DIRECTIVE.search(combined):
        violations.append(
            LintViolation(
                contract="PA.2a",
                code="missing_grounding_directive",
                message=(
                    "no numbered grounding directive (line starting with '1.' "
                    "or '1)') found in policy_block or task_block"
                ),
                path="task_block",
            )
        )
    return violations


def _check_pa3a_byte_stability(packet: Any, data: dict[str, Any]) -> list[LintViolation]:
    """PA.3a — re-serialization must produce identical bytes.

    Only meaningful when we have the live packet object (with a to_json method).
    For plain-dict inputs we check deterministic JSON dumps of the dict itself.
    """
    violations: list[LintViolation] = []
    to_json = getattr(packet, "to_json", None)
    if callable(to_json):
        try:
            a = to_json()
            b = to_json()
        except (TypeError, ValueError) as exc:
            violations.append(
                LintViolation(
                    contract="PA.3a",
                    code="serialization_error",
                    message=f"to_json() raised {type(exc).__name__}: {exc}",
                )
            )
            return violations
        if a != b:
            violations.append(
                LintViolation(
                    contract="PA.3a",
                    code="byte_drift",
                    message="two successive to_json() calls returned different bytes",
                )
            )
        return violations

    a = json.dumps(data, sort_keys=False, ensure_ascii=False)
    b = json.dumps(data, sort_keys=False, ensure_ascii=False)
    if a != b:  # pragma: no cover — json.dumps is deterministic given dict order
        violations.append(
            LintViolation(
                contract="PA.3a",
                code="byte_drift",
                message="repeated json.dumps produced different output",
            )
        )
    return violations


def lint_prompt_packet(packet: Any) -> LintReport:
    """Lint a single PromptEnvelope (or its dict form) against C5 PA contracts.

    Parameters
    ----------
    packet : PromptEnvelope | dict
        The assembled packet to validate.

    Returns
    -------
    LintReport
        Report with one entry per violation. ``is_clean`` when all pass.

    Raises
    ------
    PromptPacketLintError
        If the input type is not dict-like / does not implement ``to_dict``.
    """
    data = _coerce_to_dict(packet)
    packet_id = str(data.get("packet_id") or "<unknown>")

    violations: list[LintViolation] = []
    violations.extend(_check_pa0_ordering(data))
    violations.extend(_check_pa1a_schema(data))
    violations.extend(_check_pa1b_taxonomy(data))
    violations.extend(_check_pa2a_grounding(data))
    violations.extend(_check_pa3a_byte_stability(packet, data))

    return LintReport(packet_id=packet_id, violations=violations)


def lint_prompt_packets(packets: list[Any]) -> list[LintReport]:
    """Lint an iterable of packets; returns one LintReport each."""
    return [lint_prompt_packet(p) for p in packets]


__all__ = [
    "CANONICAL_BLOCK_ORDER",
    "LintReport",
    "LintViolation",
    "PromptPacketLintError",
    "lint_prompt_packet",
    "lint_prompt_packets",
]
