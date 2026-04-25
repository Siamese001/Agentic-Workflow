"""Identifier References — JIT (just-in-time) retrieval primitives for C0 context assembly.

Implements the G4 gap: the Anthropic context-engineering pattern of carrying
lightweight identifiers in the prompt instead of full content, with
dereferencer tools that the agent can invoke on demand.

Architecture reference:
  - Anthropic — *Effective Context Engineering for AI Agents* (2025)
    §Just-in-time retrieval, §Tool-result clearing
  - C0 Context Engine.md §C0.1 (retrieval plan)
  - RAGFlow 2025: "Decouple Search (small chunks) from Retrieve (large
    hydrated fragments)"

Design:
  - ``IdentifierRef`` is a lightweight placeholder that carries a reference
    to retrievable content (chunk, document, tool result, memory entity).
  - ``Dereferencer`` resolves an ``IdentifierRef`` to its full content on
    demand, with ACL gating and budget bounding.
  - ``IdentifierRefRegistry`` tracks all issued refs for audit and replay.
  - Safety: refs are scoped to the current query context and cannot be
    followed across tenant boundaries.
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# IdentifierRefKind — what kind of content the ref points to
# ---------------------------------------------------------------------------


class IdentifierRefKind(str, Enum):
    """Kind of content an IdentifierRef points to."""

    CHUNK = "chunk"
    DOCUMENT = "document"
    TOOL_RESULT = "tool_result"
    MEMORY_ENTITY = "memory_entity"
    GRAPH_NODE = "graph_node"


# ---------------------------------------------------------------------------
# IdentifierRef — lightweight placeholder for JIT retrieval
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class IdentifierRef:
    """Lightweight reference to retrievable content.

    Carried in the prompt instead of full content.  The agent dereferences
    on demand via the ``Dereferencer``.

    Attributes
    ----------
    ref_id : str
        Unique identifier for this reference.
    kind : IdentifierRefKind
        What kind of content this ref points to.
    source_key : str
        Source-specific key (chunk_id, doc_id, entity name, etc.).
    summary : str
        One-line summary for the agent to decide whether to dereference.
    token_estimate : int
        Estimated token count of the full content (for budget tracking).
    tenant : str
        Tenant scope — refs cannot be followed across tenants.
    acl_required : list[str]
        ACL tags required to dereference (empty = no restriction).
    """

    ref_id: str
    kind: IdentifierRefKind
    source_key: str
    summary: str = ""
    token_estimate: int = 0
    tenant: str = ""
    acl_required: list[str] = field(default_factory=list)

    def to_prompt_text(self) -> str:
        """Render as compact prompt text for the agent."""
        acl_tag = " [ACL]" if self.acl_required else ""
        return f"[ref:{self.ref_id}|{self.kind.value}|{self.summary}{acl_tag}]"


# ---------------------------------------------------------------------------
# DereferenceResult — outcome of a dereference operation
# ---------------------------------------------------------------------------


@dataclass
class DereferenceResult:
    """Result of dereferencing an IdentifierRef.

    Attributes
    ----------
    ref : IdentifierRef
        The reference that was dereferenced.
    content : str
        The full content retrieved.
    tokens_used : int
        Actual token count of the retrieved content.
    success : bool
        Whether dereferencing succeeded.
    error : str
        Error message if dereferencing failed.
    """

    ref: IdentifierRef
    content: str = ""
    tokens_used: int = 0
    success: bool = True
    error: str = ""


# ---------------------------------------------------------------------------
# Dereferencer — resolves IdentifierRefs on demand
# ---------------------------------------------------------------------------

# Type alias for resolver callbacks
ResolveFn = Callable[[IdentifierRef], str | None]


class Dereferencer:
    """Resolves IdentifierRefs to their full content on demand.

    Each ``IdentifierRefKind`` has a registered resolver function.
    Resolvers receive the ref and return the full content string, or
    ``None`` if the content is unavailable.

    Args:
        tenant : str
            Current tenant scope — refs from other tenants are blocked.
        token_budget : int
            Maximum tokens the dereferencer may consume per session.
        acl_tags : list[str]
            ACL tags the current session holds (for gated refs).
    """

    def __init__(
        self,
        tenant: str = "",
        token_budget: int = 8192,
        acl_tags: list[str] | None = None,
    ) -> None:
        self._tenant = tenant
        self._token_budget = token_budget
        self._tokens_consumed = 0
        self._acl_tags = set(acl_tags or [])
        self._resolvers: dict[IdentifierRefKind, ResolveFn] = {}
        log.info("Dereferencer initialized (tenant=%s, budget=%d)", tenant, token_budget)

    def register_resolver(self, kind: IdentifierRefKind, fn: ResolveFn) -> None:
        """Register a resolver function for a given ref kind."""
        self._resolvers[kind] = fn
        log.debug("Registered resolver for kind=%s", kind.value)

    def dereference(self, ref: IdentifierRef) -> DereferenceResult:
        """Dereference a single IdentifierRef.

        Checks tenant scope, ACL, and token budget before resolving.

        Args:
            ref: The reference to dereference.

        Returns:
            ``DereferenceResult`` with the resolved content or error.
        """
        # Tenant check
        if ref.tenant and self._tenant and ref.tenant != self._tenant:
            return DereferenceResult(
                ref=ref,
                success=False,
                error=f"Tenant mismatch: ref={ref.tenant}, session={self._tenant}",
            )

        # ACL check
        if ref.acl_required:
            missing = set(ref.acl_required) - self._acl_tags
            if missing:
                return DereferenceResult(
                    ref=ref,
                    success=False,
                    error=f"ACL denied: missing tags {sorted(missing)}",
                )

        # Budget check
        if self._tokens_consumed + ref.token_estimate > self._token_budget:
            return DereferenceResult(
                ref=ref,
                success=False,
                error=(
                    f"Budget exceeded: consumed={self._tokens_consumed}, "
                    f"estimate={ref.token_estimate}, budget={self._token_budget}"
                ),
            )

        # Resolve
        resolver = self._resolvers.get(ref.kind)
        if resolver is None:
            return DereferenceResult(
                ref=ref,
                success=False,
                error=f"No resolver registered for kind={ref.kind.value}",
            )

        try:
            content = resolver(ref)
        except (OSError, ValueError, KeyError) as exc:
            return DereferenceResult(
                ref=ref,
                success=False,
                error=f"Resolver error: {exc}",
            )

        if content is None:
            return DereferenceResult(
                ref=ref,
                success=False,
                error="Content unavailable",
            )

        tokens_used = ref.token_estimate or len(content.split())
        self._tokens_consumed += tokens_used

        return DereferenceResult(
            ref=ref,
            content=content,
            tokens_used=tokens_used,
            success=True,
        )

    def dereference_batch(
        self,
        refs: list[IdentifierRef],
    ) -> list[DereferenceResult]:
        """Dereference multiple refs in order, respecting budget.

        Stops early if budget is exhausted.
        """
        results: list[DereferenceResult] = []
        for ref in refs:
            result = self.dereference(ref)
            results.append(result)
            if not result.success and "Budget exceeded" in result.error:
                break
        return results

    @property
    def tokens_consumed(self) -> int:
        """Total tokens consumed so far."""
        return self._tokens_consumed

    @property
    def tokens_remaining(self) -> int:
        """Tokens remaining in budget."""
        return max(0, self._token_budget - self._tokens_consumed)


# ---------------------------------------------------------------------------
# IdentifierRefRegistry — tracks issued refs for audit and replay
# ---------------------------------------------------------------------------


class IdentifierRefRegistry:
    """Registry of all IdentifierRefs issued in a session.

    Used for audit tracing and replay: the registry records which refs
    were issued, which were dereferenced, and the token cost.

    Attributes
    ----------
    query_id : str
        The query this registry is scoped to.
    """

    def __init__(self, query_id: str = "") -> None:
        self.query_id = query_id
        self._refs: dict[str, IdentifierRef] = {}
        self._dereferenced: dict[str, DereferenceResult] = {}

    def issue(
        self,
        kind: IdentifierRefKind,
        source_key: str,
        summary: str = "",
        token_estimate: int = 0,
        tenant: str = "",
        acl_required: list[str] | None = None,
    ) -> IdentifierRef:
        """Issue a new IdentifierRef and register it.

        Args:
            kind: What kind of content this ref points to.
            source_key: Source-specific key.
            summary: One-line summary.
            token_estimate: Estimated tokens of full content.
            tenant: Tenant scope.
            acl_required: Required ACL tags.

        Returns:
            The newly issued ``IdentifierRef``.
        """
        ref_id = f"ref-{uuid.uuid4().hex[:8]}"
        ref = IdentifierRef(
            ref_id=ref_id,
            kind=kind,
            source_key=source_key,
            summary=summary,
            token_estimate=token_estimate,
            tenant=tenant,
            acl_required=acl_required or [],
        )
        self._refs[ref_id] = ref
        log.debug("Issued ref %s (kind=%s, key=%s)", ref_id, kind.value, source_key)
        return ref

    def record_dereference(self, result: DereferenceResult) -> None:
        """Record that a ref was dereferenced."""
        self._dereferenced[result.ref.ref_id] = result

    def get_ref(self, ref_id: str) -> IdentifierRef | None:
        """Look up a ref by ID."""
        return self._refs.get(ref_id)

    @property
    def issued_refs(self) -> list[IdentifierRef]:
        """All issued refs."""
        return list(self._refs.values())

    @property
    def dereferenced_refs(self) -> list[DereferenceResult]:
        """All dereferenced refs."""
        return list(self._dereferenced.values())

    def audit_summary(self) -> dict[str, Any]:
        """Produce an audit summary of the registry."""
        total_issued = len(self._refs)
        total_deref = len(self._dereferenced)
        tokens_total = sum(r.tokens_used for r in self._dereferenced.values())
        failed = sum(1 for r in self._dereferenced.values() if not r.success)
        return {
            "query_id": self.query_id,
            "refs_issued": total_issued,
            "refs_dereferenced": total_deref,
            "refs_failed": failed,
            "tokens_consumed": tokens_total,
        }


# ---------------------------------------------------------------------------
# Convenience resolver factories
# ---------------------------------------------------------------------------


def make_graph_node_resolver(
    graph_stage: Any,
) -> ResolveFn:
    """Create a resolver for ``IdentifierRefKind.GRAPH_NODE``.

    Uses the injected ``GraphRecallStage`` to resolve graph node refs
    via ``graph_hop``.  The ``source_key`` on the ref is interpreted
    as ``chunk_id:source_path``.

    Args:
        graph_stage: ``GraphRecallStage`` instance with a provider wired.

    Returns:
        A ``ResolveFn`` suitable for ``dereferencer.register_resolver()``.
    """

    def _resolve(ref: IdentifierRef) -> str | None:
        parts = ref.source_key.split(":", 1)
        chunk_id = parts[0]
        source_path = parts[1] if len(parts) > 1 else ""

        try:
            results = graph_stage.graph_hop(
                chunk_id=chunk_id,
                source_path=source_path,
            )
        except (OSError, ValueError):
            return None

        if not results:
            return None

        # Concatenate hop result contents
        return "\n".join(r.content for r in results if r.content)

    return _resolve
