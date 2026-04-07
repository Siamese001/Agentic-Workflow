"""
Feature Derivation Engine - Computes all RiskFeatures deterministically.
"""
from typing import List, Optional

from ..engines.document_reconciliation_engine import ReconciliationResult
from ..types import (
    CapacityFeatures,
    CollateralFeatures,
    CompositeFeatures,
    CreditFeatures,
    DocumentationFeatures,
    FinancialPeriod,
    LiquidityFeatures,
    OperatingRiskFeatures,
    PolicyFeatures,
    RelationshipFeatures,
    RiskFeatures,
    UnderwritingRequest,
)


class FeatureDerivationEngine:
    """
    Derives explicit risk features from underwriting request data.

    Computes:
    - Capacity metrics (DSCR, leverage, margins)
    - Liquidity ratios
    - Collateral coverage
    - Credit scores
    - Operating risks
    - Relationship scores
    - Documentation completeness
    """

    # Industry risk weights (NAICS-based)
    INDUSTRY_RISK_WEIGHTS = {
        "111": 0.6,  # Crop production
        "112": 0.6,  # Animal production
        "211": 0.4,  # Oil & gas extraction
        "213": 0.4,  # Mining support
        "221": 0.3,  # Utilities
        "236": 0.5,  # Construction
        "311": 0.5,  # Food manufacturing
        "332": 0.5,  # Fabricated metal
        "334": 0.4,  # Computer/electronic
        "541": 0.3,  # Professional services
        "621": 0.3,  # Healthcare
        "722": 0.6,  # Food services (higher risk)
        "811": 0.5,  # Repair & maintenance
    }

    # Document staleness thresholds (days)
    DOCUMENT_FRESHNESS = {
        "financial_statement": 365,
        "tax_return": 180,
        "bank_statement": 90,
        "ar_aging": 60,
        "ap_aging": 60,
        "debt_schedule": 90,
        "appraisal": 365,
    }

    def derive_features(
        self,
        request: UnderwritingRequest,
        reconciliation: Optional[ReconciliationResult] = None,
    ) -> RiskFeatures:
        """
        Derive complete risk feature set from underwriting request.

        Args:
            request: UnderwritingRequest
            reconciliation: Optional reconciliation results

        Returns:
            RiskFeatures with all derived metrics
        """
        features = RiskFeatures()

        # Derive capacity features
        features.capacity = self._derive_capacity_features(request)

        # Derive liquidity features
        features.liquidity = self._derive_liquidity_features(request)

        # Derive collateral features
        features.collateral = self._derive_collateral_features(request)

        # Derive credit features
        features.credit = self._derive_credit_features(request)

        # Derive operating risk features
        features.operating_risk = self._derive_operating_risk_features(request)

        # Derive relationship features
        features.relationship = self._derive_relationship_features(request)

        # Derive documentation features
        features.documentation = self._derive_documentation_features(
            request, reconciliation,
        )

        # Derive policy features
        features.policy = self._derive_policy_features(request)

        # Derive composite features
        features.composite = self._derive_composite_features(
            features, reconciliation,
        )

        return features

    def _derive_capacity_features(self, request: UnderwritingRequest) -> CapacityFeatures:
        """Derive debt service capacity features."""
        periods = request.financials.periods
        metrics = request.financials.calculated_metrics

        features = CapacityFeatures()

        # Use calculated metrics if available
        features.dscr_ttm = metrics.dscr_ttm
        features.debt_to_ebitda_ttm = metrics.debt_to_ebitda_ttm
        features.ebitda_margin_ttm = metrics.ebitda_margin_ttm

        # Calculate from periods if metrics missing
        if periods and not features.dscr_ttm:
            latest = periods[-1]
            if latest.ebitda and latest.debt_service and latest.debt_service > 0:
                features.dscr_ttm = latest.ebitda / latest.debt_service

        if periods and not features.debt_to_ebitda_ttm:
            latest = periods[-1]
            if latest.total_debt and latest.ebitda and latest.ebitda > 0:
                features.debt_to_ebitda_ttm = latest.total_debt / latest.ebitda

        # Revenue trend score (0-1, higher = better)
        features.revenue_trend_score = self._calculate_revenue_trend_score(periods)

        # Earnings stability score
        features.earnings_stability_score = self._calculate_earnings_stability(periods)

        return features

    def _derive_liquidity_features(self, request: UnderwritingRequest) -> LiquidityFeatures:
        """Derive liquidity and cash flow features."""
        features = LiquidityFeatures()

        periods = request.financials.periods
        if periods:
            latest = periods[-1]

            # Current ratio
            if latest.cash is not None and latest.ar is not None and latest.ap is not None:
                current_assets = (latest.cash or 0) + (latest.ar or 0) + (latest.inventory or 0)
                current_liabilities = latest.ap or 0  # Simplified
                if current_liabilities > 0:
                    features.current_ratio = current_assets / current_liabilities

            # Quick ratio (cash + AR) / current liabilities
            if latest.cash is not None and latest.ar is not None and latest.ap is not None:
                quick_assets = (latest.cash or 0) + (latest.ar or 0)
                current_liabilities = latest.ap or 0
                if current_liabilities > 0:
                    features.quick_ratio = quick_assets / current_liabilities

            # Cash buffer months
            if latest.cash and request.credit.delinquencies_24m is not None:
                # Simplified: cash / average monthly operating expenses
                # Would need more detailed data for accurate calculation
                if latest.debt_service:
                    features.cash_buffer_months = latest.cash / (latest.debt_service / 12)

        # Deposit stability score from banking data
        banking = request.banking
        if banking.nsf_count_12m is not None and banking.overdraft_days_12m is not None:
            # Lower NSF count and overdraft days = higher score
            nsf_penalty = min(1.0, banking.nsf_count_12m / 12) * 0.5
            od_penalty = min(1.0, banking.overdraft_days_12m / 30) * 0.5
            features.deposit_stability_score = max(0.0, 1.0 - nsf_penalty - od_penalty)
        else:
            features.deposit_stability_score = 0.5  # Neutral if no data

        return features

    def _derive_collateral_features(self, request: UnderwritingRequest) -> CollateralFeatures:
        """Derive collateral coverage features."""
        features = CollateralFeatures()

        collateral = request.collateral

        # LTV calculation
        if collateral.estimated_value and collateral.estimated_value > 0:
            features.ltv = request.requested_amount / collateral.estimated_value

        # Borrowing base coverage
        if collateral.borrowing_base_value:
            features.borrowing_base_coverage = collateral.borrowing_base_value / request.requested_amount

        # Collateral quality score
        quality_score = 0.5  # Base score

        # Adjust by collateral type
        type_scores = {
            "real_estate": 0.8,
            "equipment": 0.6,
            "ar": 0.5,
            "inventory": 0.4,
            "mixed": 0.5,
            "unsecured": 0.0,
        }
        quality_score = type_scores.get(collateral.collateral_type, 0.5)

        # Adjust by lien position
        if collateral.lien_position == "first":
            quality_score += 0.1
        elif collateral.lien_position == "junior":
            quality_score -= 0.2

        # Adjust by appraisal recency
        if collateral.appraisal_date:
            from datetime import datetime
            try:
                appraisal_dt = datetime.fromisoformat(collateral.appraisal_date.replace('Z', '+00:00'))
                days_old = (datetime.now() - appraisal_dt).days
                if days_old > 365:
                    quality_score -= 0.1
            except Exception:
                pass

        features.collateral_quality_score = max(0.0, min(1.0, quality_score))

        return features

    def _derive_credit_features(self, request: UnderwritingRequest) -> CreditFeatures:
        """Derive credit bureau and scoring features."""
        features = CreditFeatures()

        credit = request.credit

        # Personal FICO min
        if credit.personal_fico_scores:
            features.personal_fico_min = min(credit.personal_fico_scores)

        # Business credit score
        features.business_credit_score = credit.business_bureau_score

        # Derogatory event score (0 = clean, 1 = many issues)
        derogatory_count = (
            credit.delinquencies_24m +
            credit.defaults_ever * 5 +
            credit.bankruptcies_ever * 10 +
            credit.judgments_or_liens * 3
        )
        features.derogatory_event_score = min(1.0, derogatory_count / 10)

        return features

    def _derive_operating_risk_features(self, request: UnderwritingRequest) -> OperatingRiskFeatures:
        """Derive operating and business risk features."""
        features = OperatingRiskFeatures()

        borrower = request.borrower

        # Industry risk score
        naics_prefix = borrower.industry_code[:3] if borrower.industry_code else ""
        features.industry_risk_score = self.INDUSTRY_RISK_WEIGHTS.get(naics_prefix, 0.5)

        # Years in business score (more years = lower risk = higher score)
        if borrower.years_in_business >= 10:
            features.years_in_business_score = 0.9
        elif borrower.years_in_business >= 5:
            features.years_in_business_score = 0.7
        elif borrower.years_in_business >= 2:
            features.years_in_business_score = 0.5
        else:
            features.years_in_business_score = 0.3

        # Customer concentration (would need AR aging data)
        # For now, use placeholder
        features.customer_concentration_score = None
        features.supplier_concentration_score = None

        return features

    def _derive_relationship_features(self, request: UnderwritingRequest) -> RelationshipFeatures:
        """Derive relationship and behavioral features."""
        features = RelationshipFeatures()

        rel = request.relationship_context

        # Tenure score
        if rel.tenure_years:
            if rel.tenure_years >= 5:
                features.tenure_score = 0.9
            elif rel.tenure_years >= 2:
                features.tenure_score = 0.7
            else:
                features.tenure_score = 0.5
        else:
            features.tenure_score = 0.3  # New relationship

        # Deposit relationship score
        features.deposit_relationship_score = 0.7 if rel.deposit_relationship else 0.0

        # Historical performance score
        if rel.past_due_history:
            # Deduct for past due incidents
            features.historical_performance_score = max(0.0, 1.0 - len(rel.past_due_history) * 0.2)
        else:
            features.historical_performance_score = 1.0  # Clean history

        return features

    def _derive_documentation_features(
        self,
        request: UnderwritingRequest,
        reconciliation: Optional[ReconciliationResult],
    ) -> DocumentationFeatures:
        """Derive documentation and data quality features."""
        features = DocumentationFeatures()

        docs = request.documents

        # Document completeness score
        required_docs = [
            docs.financial_statements,
            docs.tax_returns,
            docs.bank_statements,
        ]
        present_count = sum(1 for doc_list in required_docs if doc_list)
        features.document_completeness_score = present_count / len(required_docs)

        # Data consistency score from reconciliation
        if reconciliation:
            features.data_consistency_score = reconciliation.pass_rate
        else:
            features.data_consistency_score = 0.5  # Unknown

        # Staleness score (placeholder - would check dates)
        features.staleness_score = 0.0  # Assume fresh

        return features

    def _derive_policy_features(self, request: UnderwritingRequest) -> PolicyFeatures:
        """Derive policy compliance features."""
        features = PolicyFeatures()

        policy = request.policy_context

        # Count policy exceptions triggered
        exception_count = 0

        # Check DSCR
        if policy.min_dscr and request.financials.calculated_metrics.dscr_ttm:
            if request.financials.calculated_metrics.dscr_ttm < policy.min_dscr:
                exception_count += 1

        # Check leverage
        if policy.max_debt_to_ebitda and request.financials.calculated_metrics.debt_to_ebitda_ttm:
            if request.financials.calculated_metrics.debt_to_ebitda_ttm > policy.max_debt_to_ebitda:
                exception_count += 1

        # Check FICO
        if policy.min_fico and request.credit.personal_fico_scores:
            min_fico = min(request.credit.personal_fico_scores)
            if min_fico < policy.min_fico:
                exception_count += 1

        # Check industry restrictions
        if policy.restricted_industries:
            for restricted in policy.restricted_industries:
                if request.borrower.industry_code.startswith(restricted):
                    exception_count += 1

        features.policy_exception_count = exception_count
        features.prohibited_attribute_detected = False  # Would be set by validator
        features.mandatory_review_triggered = exception_count > 0

        return features

    def _derive_composite_features(
        self,
        features: RiskFeatures,
        reconciliation: Optional[ReconciliationResult],
    ) -> CompositeFeatures:
        """Derive aggregated composite risk features."""
        composite = CompositeFeatures()

        # Calculate raw risk score (weighted average of components)
        # Lower score = lower risk
        weights = {
            'capacity': 0.25,
            'liquidity': 0.20,
            'collateral': 0.15,
            'credit': 0.15,
            'operating': 0.15,
            'documentation': 0.10,
        }

        # Capacity risk (inverse of DSCR, higher leverage = more risk)
        capacity_risk = 0.5
        if features.capacity.dscr_ttm:
            # DSCR < 1.0 is critical, > 2.0 is good
            if features.capacity.dscr_ttm >= 2.0:
                capacity_risk = 0.2
            elif features.capacity.dscr_ttm >= 1.25:
                capacity_risk = 0.4
            elif features.capacity.dscr_ttm >= 1.0:
                capacity_risk = 0.6
            else:
                capacity_risk = 0.9

        if features.capacity.debt_to_ebitda_ttm:
            if features.capacity.debt_to_ebitda_ttm > 4.0:
                capacity_risk += 0.2
            elif features.capacity.debt_to_ebitda_ttm > 3.0:
                capacity_risk += 0.1

        capacity_risk = min(1.0, capacity_risk)

        # Credit risk
        credit_risk = 0.3
        if features.credit.derogatory_event_score > 0.5:
            credit_risk = 0.7
        if features.credit.personal_fico_min:
            if features.credit.personal_fico_min < 650:
                credit_risk += 0.3
            elif features.credit.personal_fico_min < 680:
                credit_risk += 0.1
        credit_risk = min(1.0, credit_risk)

        # Documentation risk
        doc_risk = 0.5
        if reconciliation and reconciliation.has_critical_issues:
            doc_risk = 0.8
        doc_risk = min(1.0, doc_risk + (1 - features.documentation.document_completeness_score) * 0.3)

        # Weighted average
        composite.raw_risk_score = (
            capacity_risk * weights['capacity'] +
            (1 - features.liquidity.deposit_stability_score) * weights['liquidity'] +
            (1 - features.collateral.collateral_quality_score) * weights['collateral'] +
            credit_risk * weights['credit'] +
            features.operating_risk.industry_risk_score * weights['operating'] +
            doc_risk * weights['documentation']
        )

        # Normalize to 1-10 grade
        if composite.raw_risk_score <= 0.2:
            composite.normalized_risk_grade = "1"
        elif composite.raw_risk_score <= 0.3:
            composite.normalized_risk_grade = "2"
        elif composite.raw_risk_score <= 0.4:
            composite.normalized_risk_grade = "3"
        elif composite.raw_risk_score <= 0.5:
            composite.normalized_risk_grade = "4"
        elif composite.raw_risk_score <= 0.6:
            composite.normalized_risk_grade = "5"
        elif composite.raw_risk_score <= 0.7:
            composite.normalized_risk_grade = "6"
        elif composite.raw_risk_score <= 0.8:
            composite.normalized_risk_grade = "7"
        elif composite.raw_risk_score <= 0.9:
            composite.normalized_risk_grade = "8"
        else:
            composite.normalized_risk_grade = "9"

        # Confidence based on data completeness and quality
        confidence_factors = [
            features.documentation.document_completeness_score,
            features.documentation.data_consistency_score,
            1.0 if reconciliation and not reconciliation.has_critical_issues else 0.5,
        ]
        composite.confidence_score = sum(confidence_factors) / len(confidence_factors)

        return composite

    def _calculate_revenue_trend_score(self, periods: List[FinancialPeriod]) -> float:
        """Calculate revenue trend score based on period-over-period growth."""
        if len(periods) < 2:
            return 0.5  # Neutral with insufficient data

        revenues = [p.revenue for p in periods if p.revenue]
        if len(revenues) < 2:
            return 0.5

        # Calculate growth rates
        growth_rates = []
        for i in range(1, len(revenues)):
            if revenues[i-1] > 0:
                growth_rates.append((revenues[i] - revenues[i-1]) / revenues[i-1])

        if not growth_rates:
            return 0.5

        avg_growth = sum(growth_rates) / len(growth_rates)

        # Convert growth rate to score
        if avg_growth > 0.20:
            return 0.9
        elif avg_growth > 0.10:
            return 0.75
        elif avg_growth > 0.05:
            return 0.6
        elif avg_growth > 0:
            return 0.5
        elif avg_growth > -0.05:
            return 0.4
        elif avg_growth > -0.10:
            return 0.3
        else:
            return 0.2

    def _calculate_earnings_stability(self, periods: List[FinancialPeriod]) -> float:
        """Calculate earnings stability score from EBITDA volatility."""
        if len(periods) < 2:
            return 0.5

        ebitdas = [p.ebitda for p in periods if p.ebitda]
        if len(ebitdas) < 2:
            return 0.5

        # Calculate coefficient of variation
        import statistics
        try:
            mean_ebitda = statistics.mean(ebitdas)
            if mean_ebitda == 0:
                return 0.5
            std_ebitda = statistics.stdev(ebitdas)
            cv = std_ebitda / abs(mean_ebitda)

            # Lower CV = more stable = higher score
            if cv < 0.1:
                return 0.9
            elif cv < 0.2:
                return 0.75
            elif cv < 0.3:
                return 0.6
            elif cv < 0.5:
                return 0.5
            else:
                return 0.3
        except statistics.StatisticsError:
            return 0.5
