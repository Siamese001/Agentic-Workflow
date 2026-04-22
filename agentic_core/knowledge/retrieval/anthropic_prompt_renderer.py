"""Anthropic XML prompt renderer — documents-first, query-last shape.

Renders a PromptEnvelope into the Anthropic-recommended long-context prompt
shape:

    <system-prompt block>
    ...
    <document index="1">
      <source>{source_uri}</source>
      <title>{title}</title>
      <metadata>{k=v; ...}</metadata>
      <document_content>
        {verified_chunk.content}
      </document_content>
    </document>
    <document index="2">...</document>
    ...
    <task>
      {task_spec}
    </task>
    <query>
      {user_query}
    </query>
    Please quote the relevant parts of the documents that support your answer
    before synthesizing a final response.

Per Anthropic long-context guidance this structure can improve response
quality by up to 30% in complex multi-document cases
(https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/long-context-tips).

Design invariants:
- Envelope is consumed immutably. The renderer never re-fetches.
- When envelope.abstain_recommended is True, render returns the abstain
  stub prompt — callers MUST NOT send it to the model; downstream policy
  routes to HITL / refine.
- XML-escaping applied to source, title, metadata, and content fields so
  chunk text cannot break the document boundary.
- Must-use chunks render before optional chunks (preserves envelope order).

The `cache_control=ephemeral` marker on the <document> prefix is a W2.P2.1
concern — this renderer emits the string; the gateway adapter decides
where the cache boundary falls (typically after the last <document> block
and before <task>).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from xml.sax.saxutils import escape as xml_escape

from agentic_core.knowledge.retrieval.prompt_envelope import PromptEnvelope

# Anthropic recommends asking the model to quote source material before
# synthesis; this instruction is the last thing the model reads.
_GROUNDING_INSTRUCTION = (
    "Please quote the relevant parts of the documents that support your "
    "answer before synthesizing a final response. If the documents do not "
    "contain the answer, say so explicitly rather than guessing."
)

_ABSTAIN_STUB = (
    "<abstain-recommended>true</abstain-recommended>\n"
    "Evidence is insufficient or contradictory; do not generate."
)

# Metadata fields worth projecting into the <metadata> tag, in stable order
_METADATA_WHITELIST: tuple[str, ...] = (
    "title",
    "file_path",
    "source_url",
    "module",
    "heading_path",
    "doc_type",
    "authority_tier",
    "canonical_digest",
)


@dataclass(frozen=True)
class RenderedPrompt:
    """Result of rendering an envelope to Anthropic XML shape.

    Attributes
    ----------
    text:
        The full prompt string ready for the Messages API user turn.
    document_block_count:
        Number of <document> blocks rendered (0 when abstain_recommended).
    cache_boundary_hint:
        Byte offset after which the gateway adapter may apply
        ``cache_control=ephemeral`` on the static prefix. ``-1`` when
        caching is not applicable (abstain path or empty envelope).
    """

    text: str
    document_block_count: int
    cache_boundary_hint: int


def _escape(value: Any) -> str:
    """XML-escape any value, coercing to str."""
    return xml_escape(str(value)) if value is not None else ""


def _render_metadata(chunk_metadata: dict[str, Any]) -> str:
    """Render the whitelisted chunk metadata into a single <metadata> line.

    Format: ``k1=v1; k2=v2; ...`` — compact for token efficiency.
    Values are XML-escaped; unknown keys are ignored.
    """
    parts: list[str] = []
    for key in _METADATA_WHITELIST:
        if key in chunk_metadata and chunk_metadata[key] not in ("", None):
            parts.append(f"{key}={_escape(chunk_metadata[key])}")
    return "; ".join(parts)


def _render_document(index: int, chunk: Any) -> str:
    """Render a single verified chunk as a <document> block.

    ``chunk`` is duck-typed as a VerifiedChunk with ``.content``,
    ``.metadata``, and optional ``.chunk_id`` / ``.source``.
    """
    metadata = getattr(chunk, "metadata", {}) or {}
    source = metadata.get("source_url") or metadata.get("file_path") or getattr(chunk, "chunk_id", "")
    title = metadata.get("title") or metadata.get("name") or metadata.get("heading_path") or ""
    chunk_context = metadata.get("chunk_context") or ""
    metadata_line = _render_metadata(metadata)

    content = getattr(chunk, "content", "") or ""
    # Preserve chunk_context (from P1.1 Contextual Retrieval) inline so the
    # model sees the narrative grounding alongside the raw chunk.
    if chunk_context:
        inner = (
            f"    <context>{_escape(chunk_context)}</context>\n"
            f"    <document_content>\n{_escape(content)}\n    </document_content>"
        )
    else:
        inner = f"    <document_content>\n{_escape(content)}\n    </document_content>"

    parts = [f"<document index=\"{index}\">"]
    if source:
        parts.append(f"  <source>{_escape(source)}</source>")
    if title:
        parts.append(f"  <title>{_escape(title)}</title>")
    if metadata_line:
        parts.append(f"  <metadata>{metadata_line}</metadata>")
    parts.append(inner)
    parts.append("</document>")
    return "\n".join(parts)


def render_anthropic_prompt(
    envelope: PromptEnvelope,
    query: str,
    *,
    include_grounding_instruction: bool = True,
) -> RenderedPrompt:
    """Render a PromptEnvelope into Anthropic-shape XML prompt.

    Order enforced (Anthropic long-context guidance):
      1. system_blocks (static)
      2. <document> blocks (must-use first, then optional)
      3. <task> (task_spec)
      4. <query> (user query)
      5. grounding instruction (quote-before-synthesize)

    The static prefix ends at the final </document> closing tag — that is
    the ``cache_boundary_hint`` byte offset. A caller applying
    ``cache_control=ephemeral`` should mark the prefix up to and including
    that offset.

    Parameters
    ----------
    envelope:
        Completed PromptEnvelope from PromptEnvelopeFactory.
    query:
        The end-user query string. Rendered last, per Anthropic guidance
        (up to 30% quality improvement for complex multi-document cases).
    include_grounding_instruction:
        When True (default), append the quote-before-answer instruction.
        Set False when callers supply their own grounding prompt via
        task_spec.

    Returns
    -------
    RenderedPrompt with text and cache_boundary_hint.
    """
    if envelope.abstain_recommended:
        return RenderedPrompt(text=_ABSTAIN_STUB, document_block_count=0, cache_boundary_hint=-1)

    lines: list[str] = []

    # 1. System blocks (static — part of cacheable prefix)
    for block in envelope.system_blocks:
        if block.strip():
            lines.append(block.rstrip())
            lines.append("")  # blank separator

    # 2. Document blocks in envelope order (must-use first is already the
    #    contract of PromptEnvelopeFactory.from_contract — we trust the
    #    upstream ordering and do not re-sort here).
    document_count = 0
    for chunk in envelope.verified_chunks:
        document_count += 1
        lines.append(_render_document(document_count, chunk))
        lines.append("")  # blank separator between documents

    # Cache boundary: end of the last document (before <task>)
    # If no documents, cache boundary is -1 (nothing static to cache)
    prefix_text = "\n".join(lines).rstrip()
    cache_boundary = len(prefix_text) if document_count > 0 else -1

    # 3. Task spec (dynamic — per-call, outside cache)
    task_spec = envelope.task_spec.strip() if envelope.task_spec else ""
    if task_spec:
        lines.append("")
        lines.append("<task>")
        lines.append(task_spec)
        lines.append("</task>")

    # 4. Query (dynamic)
    lines.append("")
    lines.append("<query>")
    lines.append(query.strip())
    lines.append("</query>")

    # 5. Grounding instruction
    if include_grounding_instruction:
        lines.append("")
        lines.append(_GROUNDING_INSTRUCTION)

    final_text = "\n".join(line for line in lines if line is not None).strip()
    return RenderedPrompt(
        text=final_text,
        document_block_count=document_count,
        cache_boundary_hint=cache_boundary,
    )


__all__ = [
    "RenderedPrompt",
    "render_anthropic_prompt",
]
