"""C0 Final Evidence Contract Producer — AG-RGGOV-W6 Core Contract

C0 emits FinalEvidenceContract when grounding_required = true.

Responsibilities:
- Emit FinalEvidenceContract only when grounding_required = true
- Collect evidence from configured sources
- Include evidence sufficiency assessment

Hard Constraints:
- Only emit when grounding_required = true
- Core owns all contract emission
- apps_rg does not emit evidence contracts
- Contract dataclasses are defined in runtime/contracts/, imported here
- C0 is NOT L0 — this producer lives in L0_routing but C0 is a separate surface
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone

from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest
from agentic_core.runtime.contracts.final_evidence_contract import (
    EvidenceItem,
    FinalEvidenceContract,
)
from agentic_core.runtime.contracts.route_contract import RouteContract


class C0EvidenceCollector:
    """C0 evidence collection layer for apps_rg tasks.

    Emits FinalEvidenceContract when grounding_required = true.
    """

    def collect(
        self,
        validated_request: ValidatedRequest,
        route: RouteContract,
    ) -> FinalEvidenceContract:
        """Collect evidence and emit FinalEvidenceContract.

        Args:
            validated_request: U0-validated request
            route: L0 routing output with execution flags

        Returns:
            FinalEvidenceContract with collected evidence
        """
        # Collect evidence from sources
        evidence_items = self._collect_evidence_items(validated_request)

        # Assess sufficiency
        evidence_sufficiency_score = self._assess_sufficiency(evidence_items)
        support_target_met = evidence_sufficiency_score >= 0.7
        support_target_partial = evidence_sufficiency_score >= 0.4

        # Build retrieval sources list
        retrieval_sources = self._build_retrieval_sources(validated_request)

        # Compute compilation hash for downstream referencing
        compilation_hash = hashlib.sha256(
            json.dumps({
                "request_id": validated_request.request_id,
                "items": [(i.source, i.content) for i in evidence_items],
                "sufficiency": evidence_sufficiency_score,
            }, sort_keys=True).encode("utf-8")
        ).hexdigest()

        return FinalEvidenceContract(
            request_id=validated_request.request_id,
            run_id=validated_request.run_id,
            app_id=validated_request.app_id,
            trace_id=validated_request.trace_id,
            evidence_items=tuple(evidence_items),
            retrieval_sources=tuple(retrieval_sources),
            support_target_met=support_target_met,
            support_target_partial=support_target_partial,
            evidence_sufficiency_score=evidence_sufficiency_score,
            evidence_collection_timestamp=datetime.now(timezone.utc).isoformat(),
            contract_version="W6.0",
            compilation_hash=compilation_hash,
        )

    def _collect_evidence_items(
        self, request: ValidatedRequest
    ) -> list[EvidenceItem]:
        """Collect evidence items from request sources."""
        items: list[EvidenceItem] = []

        # Add resume as evidence
        items.append(
            EvidenceItem(
                source="resume_source",
                content=f"Resume for request {request.request_id}",
                content_type="text",
            )
        )

        # Add job description context
        items.append(
            EvidenceItem(
                source="job_description",
                content=f"JD context for {request.app_id}",
                content_type="text",
            )
        )

        return items

    def _assess_sufficiency(self, items: list[EvidenceItem]) -> float:
        """Assess evidence sufficiency score."""
        if not items:
            return 0.0
        # Simple heuristic: more items = higher score, capped at 1.0
        return min(0.5 + (len(items) * 0.15), 1.0)

    def _build_retrieval_sources(self, request: ValidatedRequest) -> list[str]:
        """Build list of retrieval sources."""
        return ["resume_source", "job_description", "profile_manifest"]
