"""Prompt reception audit — W1 RH1.1 instrumentation.

Pure-observation logger that records per-call slot reception evidence at the
SovereignLLMGateway seam. Detects which slot boundaries (D0, U0, exemplars,
thinking, documents) are present in the flat system/user strings that today
reach the provider adapter.

No behavior change — log-only. Emits one JSONL line per LLM call to
``artifacts/prompt_reception/reception_evidence.jsonl`` when the
``PROMPT_RECEPTION_AUDIT`` env var is truthy, plus a structured
``prompt_reception`` log entry on the standard logger every call.

Evidence consumed by the W1 audit report at
``docs/reports/plans/prompt_reception_audit.md``.

ADR reference: ADR-PROMPT-ASSEMBLY-001 (provider-aware structured rendering).
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_LOGGER = logging.getLogger(__name__)

_ENV_AUDIT_ENABLE = "PROMPT_RECEPTION_AUDIT"
_ENV_AUDIT_PATH = "PROMPT_RECEPTION_AUDIT_PATH"
_DEFAULT_AUDIT_PATH = Path("artifacts/prompt_reception/reception_evidence.jsonl")

# XML fence markers we look for in today's flat final_system_string / final_user_string.
# Presence of a fence = that slot's content reached the wire (even if as a blob).
_SYSTEM_FENCES: tuple[tuple[str, str], ...] = (
    ("d0_fence", "<D0>"),
    ("instructions_tag", "<instructions>"),
    ("context_tag", "<context>"),
    ("examples_tag", "<examples>"),
    ("example_tag", "<example"),  # singular or with attrs
    ("thinking_tag", "<thinking>"),
    ("document_tag", "<document"),
    ("documents_tag", "<documents>"),
    ("role_tag", "<role>"),
)
_USER_FENCES: tuple[tuple[str, str], ...] = (("u0_fence", "<U0>"),)


@dataclass(frozen=True)
class ReceptionEvidence:
    """Per-call reception evidence — what the LLM actually received."""

    trace_id: str
    timestamp_utc: str
    provider: str
    system_bytes: int
    user_bytes: int
    tools_count: int
    system_fences: dict[str, bool]
    user_fences: dict[str, bool]
    newline_joined_sections: int
    token_estimate: int
    signature_present: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _detect_fences(text: str, fences: tuple[tuple[str, str], ...]) -> dict[str, bool]:
    if not text:
        return {name: False for name, _ in fences}
    return {name: marker in text for name, marker in fences}


def _count_doubled_newlines(text: str) -> int:
    """Rough proxy for how many \\n\\n-joined sections reached the provider.

    Current assembler (AirlockAssembler.assemble_from_bom) joins S0+D0+I0+C0
    with '\\n\\n'. A value >= 3 strongly suggests the undifferentiated-blob
    reception problem ADR-PROMPT-ASSEMBLY-001 addresses.
    """
    if not text:
        return 0
    return text.count("\n\n")


def build_evidence(
    *,
    trace_id: str,
    provider_name: str,
    final_system_string: str,
    final_user_string: str,
    tools_schema: Any,
    token_estimate: int,
    signature: str,
) -> ReceptionEvidence:
    """Build a reception-evidence record from the gateway-seam values."""
    try:
        tools_count = len(tools_schema) if tools_schema is not None else 0
    except TypeError:
        tools_count = 0

    return ReceptionEvidence(
        trace_id=trace_id or "",
        timestamp_utc=datetime.now(timezone.utc).isoformat(),
        provider=provider_name or "",
        system_bytes=len(final_system_string or ""),
        user_bytes=len(final_user_string or ""),
        tools_count=tools_count,
        system_fences=_detect_fences(final_system_string or "", _SYSTEM_FENCES),
        user_fences=_detect_fences(final_user_string or "", _USER_FENCES),
        newline_joined_sections=_count_doubled_newlines(final_system_string or ""),
        token_estimate=int(token_estimate or 0),
        signature_present=bool(signature),
    )


def _audit_enabled() -> bool:
    return os.getenv(_ENV_AUDIT_ENABLE, "").lower() in {"1", "true", "yes", "on"}


def _audit_path() -> Path:
    override = os.getenv(_ENV_AUDIT_PATH, "").strip()
    return Path(override) if override else _DEFAULT_AUDIT_PATH


def emit(evidence: ReceptionEvidence) -> None:
    """Emit evidence to stderr logger and (optionally) a JSONL sink.

    The logger call is always on — at INFO level under the
    ``prompt_reception`` key so consumers can filter cleanly.

    The JSONL sink is gated by ``PROMPT_RECEPTION_AUDIT`` env var to keep
    production runs from writing unbounded artifacts unless the W1 audit is
    actively being collected.
    """
    payload = evidence.to_dict()

    # Always-on structured log line.
    _LOGGER.info("prompt_reception %s", json.dumps(payload, sort_keys=True))

    if not _audit_enabled():
        return

    # Opt-in JSONL append.
    sink = _audit_path()
    try:
        sink.parent.mkdir(parents=True, exist_ok=True)
        with sink.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(payload, sort_keys=True, ensure_ascii=False))
            fh.write("\n")
    except (OSError, ValueError) as exc:  # guardian: allow-log-and-swallow -- audit sink write is best-effort observability; failure must not break the generate() hot path
        _LOGGER.warning("prompt_reception audit sink failed: %s", exc)


__all__ = [
    "ReceptionEvidence",
    "build_evidence",
    "emit",
]
