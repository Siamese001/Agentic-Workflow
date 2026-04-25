"""Synthesis-output bridge into the governed assembler \u2014 W6 RH6.1.

Closes the gap identified in the prompt-reception audit where synthesis
producers (e.g. ``apps_research.services.synthesis_engine_service``,
``apps_research.reasoning.KnowledgeSynthesisAgent``,
``ops_scripts.dev_tools.L0_routing_scripts.core_synthesis_executor``)
emit grounded summaries that bypass the governed prompt-assembly pipeline.

This module provides a minimal, non-breaking bridge: synthesis producers
call ``wrap_synthesis_output`` to produce a validated ``AuthoritySlot``
they can feed into ``SlotAssemblyEngine``. No caller is forced to change;
adoption is opt-in.

Design notes
------------
- Synthesis output is grounding \u2014 it summarizes prior retrieval / reasoning,
  then lands in the prompt as context. It therefore maps to the ``C0`` slot
  (``AuthorityLevel.INFO``), NOT a new slot.
- Provenance metadata is attached to the slot for audit trail.
- Size enforcement: a ``max_bytes`` guard prevents synthesis output from
  exceeding a caller-specified budget when integrated into assembly.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agentic_core.L2_execution.reasoning.compiled_artifact import (
    AuthorityLevel,
    AuthoritySlot,
)


DEFAULT_MAX_BYTES = 16 * 1024  # 16 KiB budget for a single synthesis blob.


@dataclass(frozen=True)
class SynthesisProvenance:
    """Minimum provenance record attached to every synthesis-derived slot.

    Attributes
    ----------
    producer:
        Module or agent name that generated the synthesis text.
    source_trace_ids:
        Upstream trace IDs the synthesis summarizes (for cross-linking).
    model:
        LLM model that produced the synthesis, if any. Empty string when
        synthesis is deterministic / rule-based.
    synthesis_kind:
        Free-form label (e.g. ``"knowledge"``, ``"pattern"``, ``"plan"``).
    """

    producer: str
    source_trace_ids: tuple[str, ...] = ()
    model: str = ""
    synthesis_kind: str = "knowledge"

    def to_metadata(self) -> dict[str, Any]:
        return {
            "synthesis_producer": self.producer,
            "synthesis_source_trace_ids": list(self.source_trace_ids),
            "synthesis_model": self.model,
            "synthesis_kind": self.synthesis_kind,
        }


class SynthesisBridgeError(ValueError):
    """Raised when a synthesis output cannot be wrapped safely."""


def wrap_synthesis_output(
    *,
    text: str,
    provenance: SynthesisProvenance,
    source_layer: str = "L3",
    max_bytes: int = DEFAULT_MAX_BYTES,
) -> AuthoritySlot:
    """Produce a governed ``AuthoritySlot`` from synthesis output text.

    Parameters
    ----------
    text:
        Synthesized prose to inject into the prompt's C0 slot.
    provenance:
        Provenance record. Required \u2014 synthesis without provenance cannot
        be traced for audits and is rejected.
    source_layer:
        Layer that produced the synthesis. Defaults to ``"L3"`` since
        orchestration is the most common producer. Must be one of the
        canonical L0..L6 layer codes.
    max_bytes:
        Byte budget for the wrapped content. Synthesis exceeding this is
        truncated with a trailing ``"\u2026 [TRUNCATED]"`` marker; the original
        byte count is preserved in metadata.

    Returns
    -------
    AuthoritySlot
        An ``AuthoritySlot`` of type ``"C0"`` with ``AuthorityLevel.INFO``,
        populated content, and synthesis-provenance metadata. Safe to feed
        directly into ``SlotAssemblyEngine.add_slot``.

    Raises
    ------
    SynthesisBridgeError
        If ``text`` is empty, ``provenance.producer`` is empty, or
        ``max_bytes`` is non-positive.
    """
    if not text or not text.strip():
        raise SynthesisBridgeError("synthesis text must not be empty")
    if not provenance.producer:
        raise SynthesisBridgeError("provenance.producer must not be empty")
    if max_bytes <= 0:
        raise SynthesisBridgeError(f"max_bytes must be > 0, got {max_bytes}")
    if source_layer not in {"L0", "L1", "L2", "L3", "L4", "L5", "L6"}:
        raise SynthesisBridgeError(f"source_layer must be L0..L6, got {source_layer!r}")

    raw_bytes = text.encode("utf-8")
    original_byte_len = len(raw_bytes)
    truncated = False
    if original_byte_len > max_bytes:
        # Leave room for the truncation marker.
        marker = "\u2026 [TRUNCATED]"
        marker_bytes = marker.encode("utf-8")
        budget = max_bytes - len(marker_bytes)
        # Slice on character boundaries so UTF-8 never splits mid-code-point.
        trimmed = raw_bytes[:budget].decode("utf-8", errors="ignore")
        text = trimmed + marker
        truncated = True

    metadata = provenance.to_metadata()
    metadata["synthesis_original_bytes"] = original_byte_len
    metadata["synthesis_truncated"] = truncated
    metadata["synthesis_max_bytes"] = max_bytes

    return AuthoritySlot(
        slot_type="C0",
        content=text,
        authority_level=AuthorityLevel.INFO,
        source_layer=source_layer,
        metadata=metadata,
    )


__all__ = [
    "DEFAULT_MAX_BYTES",
    "SynthesisBridgeError",
    "SynthesisProvenance",
    "wrap_synthesis_output",
]
