"""Section merge engine — W5 generic managed-workflow merge step.

Plan: apps-rg-zip-based-full-spine-runtime-restoration-a3f7e2 W5

Accepts a workflow manifest (as a list of node descriptors) and a collection of
SealedSectionArtifact instances, validates them, then produces a merged payload
digest and a SealedWorkflowPackage.

Scope invariants (non-negotiable):
  - No apps_rg-specific section names hardcoded.
  - No provider names hardcoded.
  - No L4 writes.
  - No X3 emission.
  - No model/tool calls.
  - No imports of apps_rg.integrations.hops or gates.
"""
from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence

from agentic_core.runtime.contracts.sealed_workflow_types import (
    SealedSectionArtifact,
    SealedWorkflowPackage,
)

_log = logging.getLogger(__name__)


# ── Public exception ─────────────────────────────────────────────────────────

class SectionMergeError(Exception):
    """Raised by SectionMergeEngine on any fail-closed path."""

    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(f"SectionMergeError: {reason}")


# ── Node descriptor (thin projection of YAML node entry) ────────────────────

@dataclass(frozen=True)
class NodeDescriptor:
    """Minimal projection of a workflow manifest node for merge purposes."""
    node_id: str
    optional: bool = False
    node_order: int = 0


# ── Engine ────────────────────────────────────────────────────────────────────

class SectionMergeEngine:
    """Validates and merges SealedSectionArtifacts into a SealedWorkflowPackage.

    Generic: contains no app-specific section names or provider names.
    """

    def merge(
        self,
        *,
        workflow_ref: str,
        workflow_manifest_ref: str,
        run_id: str,
        route_contract_ref: str,
        manifest_nodes: List[NodeDescriptor],
        artifacts: Sequence[SealedSectionArtifact],
        merge_strategy_ref: str = "",
        trace_root: str = "",
        dependency_graph_ref: str = "",
        runtime_gate_refs: Sequence[str] = (),
        replay_manifest: str = "",
    ) -> SealedWorkflowPackage:
        """Validate and merge artifacts into a SealedWorkflowPackage.

        Raises:
            SectionMergeError: on duplicate node_id, missing critical node,
                or structural validation failure.
        """
        # ── 1. Reject duplicate node_ids ────────────────────────────────────
        seen_ids: list[str] = []
        for art in artifacts:
            if art.node_id in seen_ids:
                raise SectionMergeError(
                    f"Duplicate node_id={art.node_id!r} in artifacts — merge aborted."
                )
            seen_ids.append(art.node_id)

        # ── 2. Check critical node presence ─────────────────────────────────
        artifact_map: Dict[str, SealedSectionArtifact] = {
            a.node_id: a for a in artifacts
        }
        missing_critical: list[str] = []
        skipped_optional: list[str] = []

        for nd in manifest_nodes:
            if nd.node_id not in artifact_map:
                if nd.optional:
                    skipped_optional.append(nd.node_id)
                    _log.debug(
                        "[section_merge] optional node=%r absent — skipped", nd.node_id
                    )
                else:
                    missing_critical.append(nd.node_id)

        if missing_critical:
            raise SectionMergeError(
                f"Missing critical node(s): {missing_critical}. "
                "Critical nodes must have sealed artifacts before merge."
            )

        # ── 3. Order artifacts by manifest node order (stable sort) ─────────
        node_order_map: Dict[str, int] = {nd.node_id: nd.node_order for nd in manifest_nodes}
        ordered = sorted(
            artifact_map.values(),
            key=lambda a: node_order_map.get(a.node_id, 999),
        )

        # ── 4. Compute merged payload digest ─────────────────────────────────
        merged_payload_digest = self._compute_merged_digest(ordered)

        # ── 5. Build section artifact refs ───────────────────────────────────
        section_artifact_refs = tuple(
            a.artifact_id or a.node_id for a in ordered
        )

        # ── 6. Build replay manifest ─────────────────────────────────────────
        if not replay_manifest:
            replay_manifest = json.dumps(
                {
                    "workflow_ref": workflow_ref,
                    "run_id": run_id,
                    "node_ids": [a.node_id for a in ordered],
                },
                separators=(",", ":"),
            )

        import uuid
        from datetime import datetime, timezone

        package = SealedWorkflowPackage(
            package_id=f"swp::{workflow_ref}::{run_id}::{uuid.uuid4().hex[:8]}",
            route_contract_ref=route_contract_ref,
            workflow_ref=workflow_ref,
            workflow_manifest_ref=workflow_manifest_ref,
            workflow_id=workflow_ref,
            run_id=run_id,
            app_context="",
            trace_root=trace_root,
            completed_at=datetime.now(tz=timezone.utc).isoformat(),
            sealed_sections=tuple(ordered),
            section_count=len(ordered),
            section_artifact_refs=section_artifact_refs,
            merged_content_digest=merged_payload_digest,
            merge_strategy_ref=merge_strategy_ref,
            merged_payload_digest=merged_payload_digest,
            skipped_node_refs=tuple(skipped_optional),
            unresolved_node_refs=(),
            failed_node_refs=(),
            dependency_graph_ref=dependency_graph_ref,
            runtime_gate_refs=tuple(runtime_gate_refs),
            terminal_class="success",
            decisive_reason="All critical nodes merged; optional skips within policy.",
            replay_manifest=replay_manifest,
            manifest_digest="",
        )

        _log.info(
            "[section_merge] MERGED workflow_ref=%r run_id=%r nodes=%d skipped=%d digest=%s",
            workflow_ref,
            run_id,
            len(ordered),
            len(skipped_optional),
            merged_payload_digest[:16],
        )
        return package

    # ── Internal helpers ─────────────────────────────────────────────────────

    @staticmethod
    def _compute_merged_digest(ordered: list[SealedSectionArtifact]) -> str:
        h = hashlib.sha256()
        for art in ordered:
            h.update((art.node_id + ":").encode())
            digest = art.payload_digest or art.content_digest
            h.update(digest.encode() if digest else b"")
        return h.hexdigest()


__all__ = ["SectionMergeEngine", "SectionMergeError", "NodeDescriptor"]
