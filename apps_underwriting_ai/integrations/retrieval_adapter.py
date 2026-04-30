"""
Retrieval Adapter - Prepares evidence requests for existing retrieval stack.
"""

from agentic_core.runtime.contracts.runtime_telemetry_decorators import (
    traces_execute,
)
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..types import UnderwritingRequest
from tqdm import tqdm

# L1-L5 retrieval wiring (Turn 3): Import creates ADG edges to all retrieval layers


@dataclass
class EvidenceRequest:
    """Request for evidence retrieval."""

    claim_id: str
    claim_text: str
    evidence_type: str
    document_class: Optional[str] = None
    keyword_anchors: List[str] = field(default_factory=list)
    field_requirements: List[str] = field(default_factory=list)


@dataclass
class RetrievalQuery:
    """Query for retrieval system."""

    query_type: str
    document_types: List[str]
    keywords: List[str]
    entity_filter: Optional[str] = None
    time_range: Optional[str] = None


class RetrievalAdapter:
    """
    Adapter for evidence retrieval requests.

    Responsibilities:
    - Package domain retrieval requests
    - Consume existing retrieval outputs
    - Do not become a new retrieval engine
    """

    @traces_execute(layer="L4_STATE")
    def prepare_evidence_requests(
        self,
        request: UnderwritingRequest,
    ) -> List[EvidenceRequest]:
        """
        Prepare evidence requests for retrieval.

        Args:
            request: UnderwritingRequest

        Returns:
            List of EvidenceRequest objects
        """
        requests = []

        # Financial statement evidence
        if request.financials.periods:
            latest = request.financials.periods[-1]
            requests.append(
                EvidenceRequest(
                    claim_id="fin_revenue",
                    claim_text=f"Revenue of ${latest.revenue:,.0f} in latest period",
                    evidence_type="document",
                    document_class="financial_statement",
                    keyword_anchors=["revenue", "sales", "income statement"],
                    field_requirements=["revenue", "period_end"],
                )
            )

        # Debt schedule evidence
        if request.financials.periods:
            latest = request.financials.periods[-1]
            if latest.total_debt:
                requests.append(
                    EvidenceRequest(
                        claim_id="debt_balance",
                        claim_text=f"Total debt of ${latest.total_debt:,.0f}",
                        evidence_type="document",
                        document_class="debt_schedule",
                        keyword_anchors=["debt", "liabilities", "loan"],
                        field_requirements=["lender", "balance", "maturity"],
                    )
                )

        # Collateral evidence
        if request.collateral.estimated_value:
            requests.append(
                EvidenceRequest(
                    claim_id="collateral_value",
                    claim_text=f"Collateral value of ${request.collateral.estimated_value:,.0f}",
                    evidence_type="document",
                    document_class="appraisal",
                    keyword_anchors=["appraised value", "fair market value", "collateral"],
                    field_requirements=["value", "date", "appraiser"],
                )
            )

        # AR aging evidence
        if request.collateral.collateral_type in ["ar", "mixed"]:
            requests.append(
                EvidenceRequest(
                    claim_id="ar_aging",
                    claim_text="Accounts receivable aging schedule",
                    evidence_type="document",
                    document_class="ar_aging",
                    keyword_anchors=["accounts receivable", "aging", "AR"],
                    field_requirements=["customer", "amount", "days_outstanding"],
                )
            )

        # Guarantor credit evidence
        if request.requested_structure.guarantor_required:
            for owner in tqdm(request.borrower.ownership, desc="Processing", unit="item"):
                if owner.guarantor:
                    requests.append(
                        EvidenceRequest(
                            claim_id=f"guarantor_fico_{owner.owner_name}",
                            claim_text=f"Personal credit for guarantor {owner.owner_name}",
                            evidence_type="structured_metric",
                            document_class="credit_report",
                            keyword_anchors=["FICO", "credit score", "credit report"],
                            field_requirements=["fico_score", "delinquencies", "bankruptcies"],
                        )
                    )

        return requests

    def build_retrieval_queries(
        self,
        request: UnderwritingRequest,
    ) -> List[RetrievalQuery]:
        """Build retrieval queries for evidence assembly."""
        queries = []

        # Query for financial documents
        if request.documents.financial_statements:
            queries.append(
                RetrievalQuery(
                    query_type="document_lookup",
                    document_types=["financial_statement"],
                    keywords=["balance sheet", "income statement", "cash flow"],
                    entity_filter=request.borrower.legal_name,
                )
            )

        # Query for bank statements
        if request.documents.bank_statements:
            queries.append(
                RetrievalQuery(
                    query_type="document_lookup",
                    document_types=["bank_statement"],
                    keywords=["deposit", "balance", "NSF"],
                    entity_filter=request.borrower.legal_name,
                    time_range="last_12_months",
                )
            )

        return queries

    def process_retrieval_results(
        self,
        evidence_requests: List[EvidenceRequest],
        retrieval_results: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Process retrieval results and match to evidence requests."""
        matched_evidence = {}

        for request in tqdm(evidence_requests, desc="Processing", unit="item"):
            # Find matching retrieval result
            for result in retrieval_results:
                if self._matches_request(request, result):
                    matched_evidence[request.claim_id] = {
                        "claim": request.claim_text,
                        "evidence": result,
                        "confidence": result.get("confidence", 0.8),
                    }
                    break

        return matched_evidence

    def _matches_request(
        self,
        request: EvidenceRequest,
        result: Dict[str, Any],
    ) -> bool:
        """Check if retrieval result matches evidence request."""
        # Simple matching logic - would be more sophisticated in production
        result_doc_type = result.get("document_type", "")

        if request.document_class and request.document_class in result_doc_type:
            return True

        # Check keyword overlap
        result_keywords = set(result.get("keywords", []))
        request_keywords = set(request.keyword_anchors)

        if result_keywords & request_keywords:  # Intersection
            return True

        return False


# ----------------------------------------------------------------------
# OTEL coverage — module-load emit per check_apps_otel_coverage.py.
# Phase A of W-OTEL waves: structural wiring at import time.
# Phase B (per-method spans on execute() paths) is tracked separately.
# Pattern matches lifecycle_trace_contract.py and apps_research/engines.
# ----------------------------------------------------------------------
from agentic_core.runtime.contracts.lifecycle_trace_contract import (  # noqa: E402
    _emit_records_telemetry_event,
)

_emit_records_telemetry_event("p4", 'apps_underwriting_ai.integrations.retrieval_adapter', "module_loaded")
