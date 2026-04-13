"""RetrievalPlan — structured C0.1 retrieval plan with pre-retrieval filter gate.

Produced by L0 routing BEFORE any fetch occurs.  The plan binds:
  - source scope (collections)
  - retrieval mode (dense / sparse / hybrid / graph)
  - ACL / tenant bind
  - freshness window
  - schema version pin
  - replay / policy metadata for determinism

Architecture reference:
  - 03_Route_Decision_Switching.md §Pre-Routing Gates (tenant, ACL, freshness, version binds)
  - C5_Retrieval_Prompt_Assembly.md §C0.1 Retrieval Plan
  - 00C_index_materialization_runtime_handoff.md §Query-Time Handoff

Design invariants:
  - L0 creates the plan; C0 executes it.  C0 MUST NOT create plans.
  - Pre-filter runs against ChunkManifest sidecars, NOT raw content.
  - Fail-closed: if manifest is absent the chunk is EXCLUDED.
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from agentic_core.knowledge.canonical.chunk_manifest import (
    ChunkManifest,
    FreshnessBand,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
)

log = logging.getLogger(__name__)


class RetrievalMode:
    """Supported retrieval modes."""

    DENSE = "dense"
    SPARSE = "sparse"
    HYBRID = "hybrid"
    GRAPH = "graph"

    @classmethod
    def all(cls) -> list[str]:
        return [cls.DENSE, cls.SPARSE, cls.HYBRID, cls.GRAPH]


@dataclass
class RetrievalPlan:
    """Structured retrieval plan (C0.1).

    Created by L0 routing before any fetch.  Passed to C0 (HybridRecallStage)
    which executes the plan without modifying it.

    Attributes
    ----------
    plan_id : str
        Stable identifier for this plan; defaults to a new UUID.
    query_id : str
        Identifier of the originating query.
    retrieval_mode : str
        One of ``RetrievalMode`` constants.
    source_collections : list[str]
        Canonical collection names to query (empty = all).
    top_k : int
        Maximum number of recall results to return per stage.
    allowed_principals : list[str]
        ACL principals that must be satisfied; empty = open access.
    tenant_id : str
        Owning tenant; chunks with a different tenant_id are excluded.
    max_freshness_band : str
        Oldest freshness band allowed; chunks colder than this are excluded.
    effective_date_window : tuple[datetime, datetime] | None
        If provided, only chunks whose effective_date falls within this window
        are included.  ``None`` = no window constraint.
    schema_version_bind : str | None
        Only chunks indexed under this schema version are included.
        ``None`` = accept any version.
    replay_key : str | None
        Replay key for deterministic runs; ``None`` = live run.
    policy_hash : str
        Hash of the active governance policy at plan creation time.
    metadata : dict
        Arbitrary plan-level metadata (request_id, trace_id, …).
    """

    query_id: str
    plan_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    retrieval_mode: str = RetrievalMode.HYBRID
    source_collections: list[str] = field(default_factory=list)
    top_k: int = 10
    allowed_principals: list[str] = field(default_factory=list)
    tenant_id: str = "default"
    max_freshness_band: str = FreshnessBand.COLD  # accept everything by default
    effective_date_window: tuple[datetime, datetime] | None = None
    schema_version_bind: str | None = None
    replay_key: str | None = None
    policy_hash: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class PrefilterVerdict:
    """Verdict constants from RetrievalPrefilter."""

    PASS = "pass"
    FAIL_ACL = "fail_acl"
    FAIL_TENANT = "fail_tenant"
    FAIL_FRESHNESS = "fail_freshness"
    FAIL_EXPIRY = "fail_expiry"
    FAIL_VERSION = "fail_version"
    FAIL_DATE_WINDOW = "fail_date_window"
    FAIL_NO_MANIFEST = "fail_no_manifest"


@dataclass
class PrefilterResult:
    """Result of a single chunk pre-filter check.

    Attributes
    ----------
    chunk_id : str
        Chunk being evaluated.
    verdict : str
        One of ``PrefilterVerdict`` constants.
    passes : bool
        ``True`` iff verdict == ``PrefilterVerdict.PASS``.
    reason : str
        Human-readable explanation.
    """

    chunk_id: str
    verdict: str
    passes: bool
    reason: str = ""


class RetrievalPrefilter:
    """Pre-retrieval filter gate.

    Evaluates a ``ChunkManifest`` against a ``RetrievalPlan`` before any
    dense / sparse / graph fetch.  Fail-closed: absent manifest → FAIL.

    Architecture reference: 03_Route_Decision_Switching §Pre-Routing Gates.

    Usage::

        plan = RetrievalPlan(query_id="q1", tenant_id="acme")
        prefilter = RetrievalPrefilter()
        result = prefilter.check(manifest, plan)
        if result.passes:
            # include chunk in recall
    """

    def check(
        self,
        manifest: ChunkManifest | None,
        plan: RetrievalPlan,
        now: datetime | None = None,
    ) -> PrefilterResult:
        """Evaluate *manifest* against *plan*.

        Args:
            manifest: The ``ChunkManifest`` for the candidate chunk.
                      ``None`` triggers fail-closed (no manifest → excluded).
            plan: The active ``RetrievalPlan``.
            now: Override "current time" for testing.

        Returns:
            ``PrefilterResult`` with pass/fail verdict.
        """
        _emit_records_execution_trace(
            f"prefilter_{plan.plan_id}",
            LayerSegment.L0_ROUTING,
            "RetrievalPrefilter.check",
        )

        now = now or datetime.utcnow()

        if manifest is None:
            return PrefilterResult(
                chunk_id="unknown",
                verdict=PrefilterVerdict.FAIL_NO_MANIFEST,
                passes=False,
                reason="Chunk manifest absent; fail-closed.",
            )

        # --- Tenant bind ---
        if manifest.acl.tenant_id != plan.tenant_id:
            return PrefilterResult(
                chunk_id=manifest.chunk_id,
                verdict=PrefilterVerdict.FAIL_TENANT,
                passes=False,
                reason=f"tenant_id mismatch: chunk={manifest.acl.tenant_id} plan={plan.tenant_id}",
            )

        # --- ACL bind ---
        if plan.allowed_principals:
            if not any(manifest.acl.allows(p) for p in plan.allowed_principals):
                return PrefilterResult(
                    chunk_id=manifest.chunk_id,
                    verdict=PrefilterVerdict.FAIL_ACL,
                    passes=False,
                    reason=f"No plan principal in chunk ACL {manifest.acl.allowed_principals}",
                )

        # --- Freshness bind ---
        bands = FreshnessBand.ordered()
        try:
            chunk_band_idx = bands.index(manifest.freshness.freshness_band)
            max_band_idx = bands.index(plan.max_freshness_band)
        except ValueError:
            chunk_band_idx = 0
            max_band_idx = len(bands) - 1

        if chunk_band_idx > max_band_idx:
            return PrefilterResult(
                chunk_id=manifest.chunk_id,
                verdict=PrefilterVerdict.FAIL_FRESHNESS,
                passes=False,
                reason=(
                    f"Chunk band '{manifest.freshness.freshness_band}' colder than "
                    f"plan max '{plan.max_freshness_band}'"
                ),
            )

        # --- Expiry check ---
        if manifest.freshness.is_expired(now):
            return PrefilterResult(
                chunk_id=manifest.chunk_id,
                verdict=PrefilterVerdict.FAIL_EXPIRY,
                passes=False,
                reason=f"Chunk expired at {manifest.freshness.expiry_date}",
            )

        # --- Date window bind ---
        if plan.effective_date_window is not None:
            eff = manifest.freshness.effective_date
            win_start, win_end = plan.effective_date_window
            if eff is None or not (win_start <= eff <= win_end):
                return PrefilterResult(
                    chunk_id=manifest.chunk_id,
                    verdict=PrefilterVerdict.FAIL_DATE_WINDOW,
                    passes=False,
                    reason=f"Chunk effective_date {eff} outside window {plan.effective_date_window}",
                )

        # --- Schema version bind ---
        if plan.schema_version_bind is not None:
            if manifest.schema_version != plan.schema_version_bind:
                return PrefilterResult(
                    chunk_id=manifest.chunk_id,
                    verdict=PrefilterVerdict.FAIL_VERSION,
                    passes=False,
                    reason=(
                        f"Schema version mismatch: chunk={manifest.schema_version} "
                        f"plan={plan.schema_version_bind}"
                    ),
                )

        return PrefilterResult(
            chunk_id=manifest.chunk_id,
            verdict=PrefilterVerdict.PASS,
            passes=True,
            reason="All pre-filters passed.",
        )

    def filter_batch(
        self,
        manifests: dict[str, ChunkManifest | None],
        plan: RetrievalPlan,
        now: datetime | None = None,
    ) -> tuple[list[str], dict[str, PrefilterResult]]:
        """Apply pre-filter to a batch of chunk IDs → manifests.

        Args:
            manifests: Mapping chunk_id → ``ChunkManifest`` (or ``None``).
            plan: Active retrieval plan.
            now: Override current time for testing.

        Returns:
            Tuple of (passing_chunk_ids, all_results_by_chunk_id).
        """
        passing: list[str] = []
        results: dict[str, PrefilterResult] = {}

        for chunk_id, manifest in manifests.items():
            result = self.check(manifest, plan, now)
            results[chunk_id] = result
            if result.passes:
                passing.append(chunk_id)

        log.debug(
            "PrefilterBatch: %d/%d chunks passed plan=%s",
            len(passing),
            len(manifests),
            plan.plan_id,
        )
        return passing, results


# --- Module-level singleton ---

_global_prefilter: RetrievalPrefilter | None = None


def get_retrieval_prefilter() -> RetrievalPrefilter:
    """Get or create the global prefilter instance."""
    global _global_prefilter
    if _global_prefilter is None:
        _global_prefilter = RetrievalPrefilter()
    return _global_prefilter


__all__ = [
    "FreshnessBand",
    "PrefilterResult",
    "PrefilterVerdict",
    "RetrievalMode",
    "RetrievalPlan",
    "RetrievalPrefilter",
    "get_retrieval_prefilter",
]
