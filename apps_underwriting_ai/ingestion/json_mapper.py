"""
JSON Mapper - Maps JSON payloads to UnderwritingRequest domain model.
"""
from typing import Dict, Any, Optional
from dataclasses import dataclass, field

from ..types import (
    UnderwritingRequest,
    BorrowerProfile,
    OwnerInfo,
    FinancialPackage,
    FinancialPeriod,
    CalculatedMetrics,
    CollateralPackage,
    CreditPackage,
    BankingPackage,
    DocumentPackage,
    DocumentRef,
    PolicyContext,
    RelationshipContext,
    DecisionConstraints,
    RequestedStructure,
    ExternalSignals,
    CollateralRules,
)
from .structured_ingestion import StructuredIngestion


@dataclass
class JSONMappingResult:
    """Result of JSON mapping."""
    request: Optional[UnderwritingRequest] = None
    warnings: list = field(default_factory=list)
    errors: list = field(default_factory=list)


class JSONMapper:
    """Maps JSON data to canonical UnderwritingRequest."""

    def __init__(self):
        self.structured = StructuredIngestion()

    def map_to_request(
        self,
        data: Dict[str, Any],
        request_id: Optional[str] = None,
        strict_mode: bool = False
    ) -> JSONMappingResult:
        """
        Map JSON data to UnderwritingRequest.

        Args:
            data: Raw JSON data as dict
            request_id: Request ID (generated if None)
            strict_mode: Reject unknown fields

        Returns:
            JSONMappingResult
        """
        result = JSONMappingResult()

        # Normalize field names
        mapping = self.structured.normalize_field_names(data)
        result.warnings.extend(mapping.warnings)

        if mapping.errors:
            result.errors = mapping.errors
            return result

        normalized = mapping.data

        # Normalize booleans and nulls
        normalized = self.structured.normalize_booleans(normalized)
        normalized = self.structured.normalize_nulls(normalized)

        try:
            # Build nested objects
            borrower = self._map_borrower(normalized.get('borrower', {}))
            financials = self._map_financials(normalized.get('financials', {}))
            collateral = self._map_collateral(normalized.get('collateral', {}))
            credit = self._map_credit(normalized.get('credit', {}))
            banking = self._map_banking(normalized.get('banking', {}))
            documents = self._map_documents(normalized.get('documents', {}))
            policy_context = self._map_policy_context(normalized.get('policy_context', {}))
            external_signals = self._map_external_signals(normalized.get('external_signals', {}))
            relationship_context = self._map_relationship_context(normalized.get('relationship_context', {}))
            decision_constraints = self._map_decision_constraints(normalized.get('decision_constraints', {}))
            requested_structure = self._map_requested_structure(normalized.get('requested_structure', {}))

            # Build request
            request = UnderwritingRequest(
                request_id=request_id or normalized.get('request_id', ''),
                submission_ts=normalized.get('submission_ts', ''),
                product_type=normalized.get('product_type', 'term_loan'),
                decision_type=normalized.get('decision_type', 'new'),
                requested_amount=normalized.get('requested_amount', 0),
                requested_term_months=normalized.get('requested_term_months', 0),
                requested_structure=requested_structure,
                borrower=borrower,
                financials=financials,
                collateral=collateral,
                credit=credit,
                banking=banking,
                documents=documents,
                policy_context=policy_context,
                external_signals=external_signals,
                relationship_context=relationship_context,
                decision_constraints=decision_constraints
            )

            result.request = request

        except Exception as e:
            result.errors.append(f"Failed to build UnderwritingRequest: {str(e)}")

        return result

    def _map_borrower(self, data: Dict[str, Any]) -> BorrowerProfile:
        """Map borrower data."""
        ownership = []
        for owner_data in data.get('ownership', []):
            ownership.append(OwnerInfo(
                owner_name=owner_data.get('owner_name', ''),
                ownership_pct=owner_data.get('ownership_pct', 0),
                role=owner_data.get('role', ''),
                fico=owner_data.get('fico'),
                guarantor=owner_data.get('guarantor', False)
            ))

        return BorrowerProfile(
            legal_name=data.get('legal_name', ''),
            entity_type=data.get('entity_type', 'llc'),
            industry_code=data.get('industry_code', ''),
            industry_description=data.get('industry_description', ''),
            years_in_business=data.get('years_in_business', 0),
            state_of_incorporation=data.get('state_of_incorporation', ''),
            operating_states=data.get('operating_states', []),
            employee_count=data.get('employee_count'),
            ownership=ownership,
            naics_risk_flags=data.get('naics_risk_flags', []),
            sanctions_or_watchlist_hits=data.get('sanctions_or_watchlist_hits', [])
        )

    def _map_financials(self, data: Dict[str, Any]) -> FinancialPackage:
        """Map financial data."""
        periods = []
        for period_data in data.get('periods', []):
            periods.append(FinancialPeriod(
                period_end=period_data.get('period_end', ''),
                fiscal_type=period_data.get('fiscal_type', 'annual'),
                revenue=period_data.get('revenue', 0),
                cogs=period_data.get('cogs'),
                gross_profit=period_data.get('gross_profit'),
                ebitda=period_data.get('ebitda'),
                net_income=period_data.get('net_income'),
                cash=period_data.get('cash'),
                ar=period_data.get('ar'),
                inventory=period_data.get('inventory'),
                ap=period_data.get('ap'),
                total_assets=period_data.get('total_assets'),
                total_debt=period_data.get('total_debt'),
                tangible_net_worth=period_data.get('tangible_net_worth'),
                interest_expense=period_data.get('interest_expense'),
                debt_service=period_data.get('debt_service')
            ))

        metrics_data = data.get('calculated_metrics', {})
        calculated_metrics = CalculatedMetrics(
            revenue_cagr_2y=metrics_data.get('revenue_cagr_2y'),
            ebitda_margin_ttm=metrics_data.get('ebitda_margin_ttm'),
            debt_to_ebitda_ttm=metrics_data.get('debt_to_ebitda_ttm'),
            dscr_ttm=metrics_data.get('dscr_ttm'),
            current_ratio=metrics_data.get('current_ratio'),
            quick_ratio=metrics_data.get('quick_ratio'),
            debt_to_tnw=metrics_data.get('debt_to_tnw')
        )

        return FinancialPackage(
            periods=periods,
            calculated_metrics=calculated_metrics,
            quality_flags=data.get('quality_flags', [])
        )

    def _map_collateral(self, data: Dict[str, Any]) -> CollateralPackage:
        """Map collateral data."""
        return CollateralPackage(
            collateral_type=data.get('collateral_type', 'unsecured'),
            estimated_value=data.get('estimated_value'),
            advance_rate_pct=data.get('advance_rate_pct'),
            borrowing_base_value=data.get('borrowing_base_value'),
            lien_position=data.get('lien_position', 'none'),
            appraisal_date=data.get('appraisal_date'),
            field_exam_date=data.get('field_exam_date'),
            collateral_quality_flags=data.get('collateral_quality_flags', [])
        )

    def _map_credit(self, data: Dict[str, Any]) -> CreditPackage:
        """Map credit data."""
        return CreditPackage(
            business_bureau_score=data.get('business_bureau_score'),
            personal_fico_scores=data.get('personal_fico_scores', []),
            delinquencies_24m=data.get('delinquencies_24m', 0),
            defaults_ever=data.get('defaults_ever', 0),
            bankruptcies_ever=data.get('bankruptcies_ever', 0),
            judgments_or_liens=data.get('judgments_or_liens', 0),
            tradeline_utilization_pct=data.get('tradeline_utilization_pct'),
            credit_narrative_flags=data.get('credit_narrative_flags', [])
        )

    def _map_banking(self, data: Dict[str, Any]) -> BankingPackage:
        """Map banking data."""
        return BankingPackage(
            avg_monthly_deposits_12m=data.get('avg_monthly_deposits_12m'),
            avg_ending_balance_12m=data.get('avg_ending_balance_12m'),
            nsf_count_12m=data.get('nsf_count_12m'),
            overdraft_days_12m=data.get('overdraft_days_12m'),
            cash_volatility_score=data.get('cash_volatility_score'),
            deposit_trend=data.get('deposit_trend', 'unknown'),
            bank_statement_flags=data.get('bank_statement_flags', [])
        )

    def _map_documents(self, data: Dict[str, Any]) -> DocumentPackage:
        """Map document references."""
        def map_doc_list(doc_list):
            return [
                DocumentRef(
                    doc_id=d.get('doc_id', ''),
                    doc_type=d.get('doc_type', ''),
                    source_uri=d.get('source_uri', ''),
                    hash=d.get('hash', ''),
                    extracted_text_available=d.get('extracted_text_available', False),
                    parsed_structured_fields=d.get('parsed_structured_fields', {}),
                    document_flags=d.get('document_flags', [])
                )
                for d in doc_list
            ]

        return DocumentPackage(
            financial_statements=map_doc_list(data.get('financial_statements', [])),
            tax_returns=map_doc_list(data.get('tax_returns', [])),
            bank_statements=map_doc_list(data.get('bank_statements', [])),
            ar_aging=map_doc_list(data.get('ar_aging', [])),
            ap_aging=map_doc_list(data.get('ap_aging', [])),
            debt_schedule=map_doc_list(data.get('debt_schedule', [])),
            entity_docs=map_doc_list(data.get('entity_docs', [])),
            insurance_certificates=map_doc_list(data.get('insurance_certificates', [])),
            appraisals=map_doc_list(data.get('appraisals', [])),
            management_comments=map_doc_list(data.get('management_comments', []))
        )

    def _map_policy_context(self, data: Dict[str, Any]) -> PolicyContext:
        """Map policy context."""
        collateral_rules = CollateralRules(
            min_ltv=data.get('collateral_rules', {}).get('min_ltv'),
            max_ltv=data.get('collateral_rules', {}).get('max_ltv'),
            eligible_collateral=data.get('collateral_rules', {}).get('eligible_collateral', [])
        )

        return PolicyContext(
            policy_version=data.get('policy_version', ''),
            min_dscr=data.get('min_dscr'),
            max_debt_to_ebitda=data.get('max_debt_to_ebitda'),
            min_fico=data.get('min_fico'),
            restricted_industries=data.get('restricted_industries', []),
            prohibited_jurisdictions=data.get('prohibited_jurisdictions', []),
            max_single_customer_concentration_pct=data.get('max_single_customer_concentration_pct'),
            collateral_rules=collateral_rules,
            exception_rules=data.get('exception_rules', []),
            human_review_triggers=data.get('human_review_triggers', [])
        )

    def _map_external_signals(self, data: Dict[str, Any]) -> ExternalSignals:
        """Map external signals."""
        return ExternalSignals(
            industry_outlook=data.get('industry_outlook', 'unknown'),
            macro_flags=data.get('macro_flags', []),
            fraud_or_identity_signals=data.get('fraud_or_identity_signals', []),
            litigation_hits=data.get('litigation_hits', []),
            news_reputation_flags=data.get('news_reputation_flags', [])
        )

    def _map_relationship_context(self, data: Dict[str, Any]) -> RelationshipContext:
        """Map relationship context."""
        return RelationshipContext(
            existing_customer=data.get('existing_customer', False),
            tenure_years=data.get('tenure_years'),
            prior_exposure=data.get('prior_exposure'),
            deposit_relationship=data.get('deposit_relationship', False),
            historical_exceptions=data.get('historical_exceptions', []),
            past_due_history=data.get('past_due_history', [])
        )

    def _map_decision_constraints(self, data: Dict[str, Any]) -> DecisionConstraints:
        """Map decision constraints."""
        return DecisionConstraints(
            turnaround_sla_hours=data.get('turnaround_sla_hours', 72),
            max_auto_approval_amount=data.get('max_auto_approval_amount'),
            require_human_if_policy_exception=data.get('require_human_if_policy_exception', True),
            require_human_if_docs_missing=data.get('require_human_if_docs_missing', True),
            require_human_if_risk_score_borderline=data.get('require_human_if_risk_score_borderline', True)
        )

    def _map_requested_structure(self, data: Dict[str, Any]) -> RequestedStructure:
        """Map requested loan structure."""
        return RequestedStructure(
            amortization_months=data.get('amortization_months'),
            interest_type=data.get('interest_type', 'floating'),
            collateral_required=data.get('collateral_required', False),
            guarantor_required=data.get('guarantor_required', False)
        )
