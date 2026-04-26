"""Context Platform — unified C0 context assembly engine driven by ContextAssemblyManifest.

Implements the G10 gap: three separate retrieval surfaces (vector, graph,
keyword) currently operate independently with no single manifest governing
what gets retrieved, how it's shaped, and what budget applies.

Architecture reference:
  - C0 Context Engine.md §C0.1 (retrieval plan)
  - Anthropic — *Effective Context Engineering for AI Agents* (2025)
  - RAGFlow 2025: "Unified retrieval + reranking pipeline"

Design:
  - ``ContextAssemblyManifest`` is loaded from JSON config (validated by
    ``context_assembly_manifest.schema.json``).
  - ``ContextPlatform`` reads the manifest, assembles evidence from the
    declared sources, applies gates, and produces an ``EvidenceContract``.
  - Supports three assembly modes:
    1. ``full_prefetch`` — load all evidence up front (current behavior)
    2. ``jit_identifier`` — carry lightweight refs, dereference on demand
    3. ``hybrid`` — must-use prefetch + optional JIT (recommended)
  - Feature-flagged: manifests are inactive until the flag is enabled.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from agentic_core.knowledge.retrieval.evidence_contract_builder import (
    EvidenceContract,
    EvidenceContractBuilder,
    EvidenceStatus,
)
from agentic_core.knowledge.retrieval.identifier_refs import (
    Dereferencer,
    DereferenceResult,
    IdentifierRef,
    IdentifierRefKind,
    IdentifierRefRegistry,
)
from agentic_core.knowledge.retrieval.prompt_envelope import (
    PromptEnvelope,
    PromptEnvelopeFactory,
)
from agentic_core.knowledge.retrieval.tool_selector import (
    ToolDefinition,
    ToolSelector,
)

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Assembly mode
# ---------------------------------------------------------------------------


class AssemblyMode(str, Enum):
    """How evidence is assembled for the prompt."""

    FULL_PREFETCH = "full_prefetch"
    JIT_IDENTIFIER = "jit_identifier"
    HYBRID = "hybrid"


# ---------------------------------------------------------------------------
# SourceSpec — one declared retrieval source
# ---------------------------------------------------------------------------


@dataclass
class SourceSpec:
    """A single retrieval source declaration from the manifest.

    Attributes
    ----------
    kind : str
        Source kind (vector, graph, keyword, memory, tool_result).
    collection : str
        Collection or index name.
    weight : float
        Fusion weight (0–1).
    top_k : int
        Number of results to retrieve.
    """

    kind: str = "vector"
    collection: str = ""
    weight: float = 0.5
    top_k: int = 10


# ---------------------------------------------------------------------------
# ContextAssemblyManifest — declarative retrieval configuration
# ---------------------------------------------------------------------------


@dataclass
class ContextAssemblyManifest:
    """Declarative manifest for C0 context assembly.

    Loaded from JSON config (validated by schema).  Specifies what evidence
    to retrieve, how to shape it, and what budget/gates apply.

    Attributes
    ----------
    manifest_id : str
        Unique identifier for this manifest.
    version : int
        Schema version (currently 1).
    description : str
        Human-readable description.
    feature_flag : str
        Feature flag name (empty = always active).
    sources : list[SourceSpec]
        Declared retrieval sources.
    assembly_mode : AssemblyMode
        How evidence is assembled.
    reranker : str
        Reranker to apply.
    max_chunks : int
        Maximum chunks in the final contract.
    token_budget : int
        Token budget for assembled context.
    min_coverage : float
        Minimum coverage to proceed.
    min_must_use : int
        Minimum must-use chunks required.
    max_refine_attempts : int
        Maximum C0.6 refinement attempts.
    acl_tags : list[str]
        Required ACL tags.
    compaction_enabled : bool
        Enable context compaction.
    compaction_strategy : str
        Compaction strategy name.
    """

    manifest_id: str = ""
    version: int = 1
    description: str = ""
    feature_flag: str = ""
    sources: list[SourceSpec] = field(default_factory=list)
    assembly_mode: AssemblyMode = AssemblyMode.HYBRID
    reranker: str = ""
    max_chunks: int = 20
    token_budget: int = 4096
    min_coverage: float = 0.3
    min_must_use: int = 1
    max_refine_attempts: int = 3
    acl_tags: list[str] = field(default_factory=list)
    compaction_enabled: bool = True
    compaction_strategy: str = "clear_then_summarize"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ContextAssemblyManifest:
        """Construct from a parsed JSON dict."""
        retrieval = data.get("retrieval", {})
        sources_data = retrieval.get("sources", [])
        sources = [
            SourceSpec(
                kind=s.get("kind", "vector"),
                collection=s.get("collection", ""),
                weight=s.get("weight", 0.5),
                top_k=s.get("top_k", 10),
            )
            for s in sources_data
        ]
        assembly = retrieval.get("assembly", {})
        gates = data.get("gates", {})
        compaction = data.get("compaction", {})

        return cls(
            manifest_id=data.get("manifest_id", ""),
            version=data.get("version", 1),
            description=data.get("description", ""),
            feature_flag=data.get("feature_flag", ""),
            sources=sources,
            assembly_mode=AssemblyMode(assembly.get("mode", "hybrid")),
            reranker=assembly.get("reranker", ""),
            max_chunks=assembly.get("max_chunks", 20),
            token_budget=assembly.get("token_budget", 4096),
            min_coverage=gates.get("min_coverage", 0.3),
            min_must_use=gates.get("min_must_use", 1),
            max_refine_attempts=gates.get("max_refine_attempts", 3),
            acl_tags=gates.get("acl_tags", []),
            compaction_enabled=compaction.get("enabled", True),
            compaction_strategy=compaction.get("strategy", "clear_then_summarize"),
        )

    @classmethod
    def from_file(cls, path: str | Path) -> ContextAssemblyManifest:
        """Load from a JSON file."""
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)


# ---------------------------------------------------------------------------
# ContextPlatform — unified C0 context assembly engine
# ---------------------------------------------------------------------------


class ContextPlatform:
    """Unified C0 context assembly engine driven by ContextAssemblyManifest.

    Reads the manifest, assembles evidence from declared sources,
    applies gates, and produces an ``EvidenceContract``.

    Args:
        manifest : ContextAssemblyManifest
            The declarative manifest governing assembly.
        builder : EvidenceContractBuilder or None
            Builder to use for contract construction.  Created from
            manifest gates if not provided.
    """

    def __init__(
        self,
        manifest: ContextAssemblyManifest,
        builder: EvidenceContractBuilder | None = None,
    ) -> None:
        self._manifest = manifest
        self._builder = builder or EvidenceContractBuilder(
            min_coverage_to_proceed=manifest.min_coverage,
            must_use_count=manifest.min_must_use,
            max_refine_attempts=manifest.max_refine_attempts,
        )
        self._registry = IdentifierRefRegistry()
        self._dereferencer = Dereferencer(
            acl_tags=manifest.acl_tags,
            token_budget=manifest.token_budget,
        )
        log.info(
            "ContextPlatform initialized (manifest=%s, mode=%s)",
            manifest.manifest_id, manifest.assembly_mode.value,
        )

    @property
    def manifest(self) -> ContextAssemblyManifest:
        """The governing manifest."""
        return self._manifest

    @property
    def registry(self) -> IdentifierRefRegistry:
        """The identifier ref registry for this platform instance."""
        return self._registry

    @property
    def dereferencer(self) -> Dereferencer:
        """The dereferencer for JIT resolution."""
        return self._dereferencer

    def is_active(self, feature_flags: set[str] | None = None) -> bool:
        """Check if this manifest is active given current feature flags.

        A manifest with no feature_flag is always active.
        """
        if not self._manifest.feature_flag:
            return True
        flags = feature_flags or set()
        return self._manifest.feature_flag in flags

    def assemble(
        self,
        query_id: str,
        query: str,
        retrieved_docs: list[Any],
        query_aspects: list[str] | None = None,
    ) -> EvidenceContract:
        """Assemble evidence according to the manifest.

        Args:
            query_id: Unique query identifier.
            query: The query string.
            retrieved_docs: Pre-fetched documents from declared sources.
            query_aspects: Optional query decomposition aspects.

        Returns:
            ``EvidenceContract`` built according to manifest gates.
        """
        contract = self._builder.build_contract(
            query_id=query_id,
            query=query,
            retrieved_docs=retrieved_docs,
            query_aspects=query_aspects,
        )

        # For JIT_IDENTIFIER or HYBRID mode, issue refs for non-must-use chunks
        if self._manifest.assembly_mode in (
            AssemblyMode.JIT_IDENTIFIER,
            AssemblyMode.HYBRID,
        ):
            self._issue_refs_for_contract(contract)

        return contract

    def _issue_refs_for_contract(self, contract: EvidenceContract) -> None:
        """Issue IdentifierRefs for non-must-use chunks in the contract.

        In HYBRID mode, must-use chunks are prefetched (full content).
        Non-must-use chunks get IdentifierRefs so the agent can
        dereference on demand.
        """
        for chunk in contract.verified_chunks:
            if chunk.is_must_use:
                continue
            if chunk.evidence_class in ("background", "excluded"):
                ref = self._registry.issue(
                    kind=IdentifierRefKind.CHUNK,
                    source_key=chunk.chunk_id,
                    summary=chunk.content[:80],
                    token_estimate=len(chunk.content.split()),
                    acl_required=chunk.exclusion_reason and ["acl"] or [],
                )
                # Attach ref_id to chunk metadata (not modifying the
                # immutable contract — just tracking in the registry)
                log.debug("Issued JIT ref %s for chunk %s", ref.ref_id, chunk.chunk_id)

    def get_audit_summary(self) -> dict[str, Any]:
        """Produce an audit summary of the platform's state."""
        return {
            "manifest_id": self._manifest.manifest_id,
            "assembly_mode": self._manifest.assembly_mode.value,
            "registry": self._registry.audit_summary(),
            "dereferencer_tokens_consumed": self._dereferencer.tokens_consumed,
            "dereferencer_tokens_remaining": self._dereferencer.tokens_remaining,
        }
