"""
Business Intelligence - Company and Product Analysis
Ported from legacy_engines/intelligence_bundles.py

Specialized analysis capabilities that provide competitive
advantage through deeper business intelligence insights.
Includes company and product intelligence bundles.
"""

import logging
import time
from typing import Dict, List, object, Optional
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class BusinessStage(Enum):
    """Business lifecycle stages"""
    STARTUP = "startup"
    GROWTH = "growth"
    SCALE_UP = "scale_up"
    MATURE = "mature"
    ENTERPRISE = "enterprise"


class MarketPosition(Enum):
    """Market position categories"""
    LEADER = "leader"
    CHALLENGER = "challenger"
    FOLLOWER = "follower"
    NICHE = "niche"
    EMERGING = "emerging"


class ProductCategory(Enum):
    """Product categories"""
    SAAS = "saas"
    PLATFORM = "platform"
    INFRASTRUCTURE = "infrastructure"
    CONSUMER = "consumer"
    ENTERPRISE = "enterprise"
    MARKETPLACE = "marketplace"


@dataclass
class CompanyInsights:
    """Company intelligence insights"""
    company_name: str
    business_stage: BusinessStage
    market_position: MarketPosition
    competitive_advantages: List[str]
    growth_indicators: List[str]
    risk_factors: List[str]
    strategic_priorities: List[str]
    confidence_score: float
    metadata: Dict[str, object] = field(default_factory=dict)


@dataclass
class ProductInsights:
    """Product intelligence insights"""
    product_name: str
    category: ProductCategory
    value_proposition: str
    target_market: str
    competitive_differentiators: List[str]
    technical_strengths: List[str]
    market_opportunities: List[str]
    adoption_challenges: List[str]
    confidence_score: float
    metadata: Dict[str, object] = field(default_factory=dict)


@dataclass
class IntelligenceResult:
    """Combined intelligence analysis result"""
    company_insights: Optional[CompanyInsights]
    product_insights: Optional[ProductInsights]
    overall_confidence: float
    analysis_timestamp: float
    processing_time_ms: int


class CompanyIntelligenceBundle:
    """
    Company Intelligence Analysis
    
    Analyzes company data to determine business stage, market position,
    competitive advantages, growth indicators, and strategic priorities.
    """
    
    def __init__(self):
        """Initialize company intelligence bundle."""
        self.stage_indicators = self._load_stage_indicators()
        self.position_indicators = self._load_position_indicators()
    
    def analyze(
        self,
        company_data: Dict[str, object],
        context: Optional[Dict[str, object]] = None
    ) -> CompanyInsights:
        """
        Analyze company data for business intelligence.
        
        Args:
            company_data: Company information
            context: Additional context
            
        Returns:
            CompanyInsights with analysis results
        """
        context = context or {}
        company_name = company_data.get('name', 'Unknown Company')
        
        # Determine business stage
        business_stage = self._determine_business_stage(company_data)
        
        # Determine market position
        market_position = self._determine_market_position(company_data)
        
        # Extract competitive advantages
        competitive_advantages = self._extract_competitive_advantages(company_data)
        
        # Identify growth indicators
        growth_indicators = self._identify_growth_indicators(company_data)
        
        # Assess risk factors
        risk_factors = self._assess_risk_factors(company_data)
        
        # Determine strategic priorities
        strategic_priorities = self._determine_strategic_priorities(
            company_data, business_stage, market_position
        )
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence(company_data)
        
        logger.info(f"Company analysis complete for {company_name}: stage={business_stage.value}, position={market_position.value}")
        
        return CompanyInsights(
            company_name=company_name,
            business_stage=business_stage,
            market_position=market_position,
            competitive_advantages=competitive_advantages,
            growth_indicators=growth_indicators,
            risk_factors=risk_factors,
            strategic_priorities=strategic_priorities,
            confidence_score=confidence_score,
            metadata={
                'data_completeness': self._assess_data_completeness(company_data),
                'analysis_version': '1.0'
            }
        )
    
    def _determine_business_stage(self, data: Dict[str, object]) -> BusinessStage:
        """Determine company's business stage."""
        employee_count = data.get('employee_count', 0)
        revenue = data.get('revenue', 0)
        funding_stage = data.get('funding_stage', '').lower()
        years_in_business = data.get('years_in_business', 0)
        
        # Stage determination logic
        if funding_stage in ['seed', 'pre-seed'] or employee_count < 20:
            return BusinessStage.STARTUP
        elif funding_stage in ['series a', 'series b'] or employee_count < 100:
            return BusinessStage.GROWTH
        elif funding_stage in ['series c', 'series d'] or employee_count < 500:
            return BusinessStage.SCALE_UP
        elif employee_count < 5000 or years_in_business < 15:
            return BusinessStage.MATURE
        else:
            return BusinessStage.ENTERPRISE
    
    def _determine_market_position(self, data: Dict[str, object]) -> MarketPosition:
        """Determine company's market position."""
        market_share = data.get('market_share', 0)
        brand_recognition = data.get('brand_recognition', 'low').lower()
        competitive_rank = data.get('competitive_rank', 10)
        
        if market_share > 30 or competitive_rank == 1:
            return MarketPosition.LEADER
        elif market_share > 15 or competitive_rank <= 3:
            return MarketPosition.CHALLENGER
        elif market_share > 5:
            return MarketPosition.FOLLOWER
        elif data.get('niche_focus', False):
            return MarketPosition.NICHE
        else:
            return MarketPosition.EMERGING
    
    def _extract_competitive_advantages(self, data: Dict[str, object]) -> List[str]:
        """Extract competitive advantages from company data."""
        advantages = []
        
        # Technology advantages
        if data.get('proprietary_technology', False):
            advantages.append("Proprietary technology platform")
        
        if data.get('patents', 0) > 5:
            advantages.append(f"Strong IP portfolio ({data['patents']} patents)")
        
        # Market advantages
        if data.get('first_mover', False):
            advantages.append("First-mover advantage in market")
        
        if data.get('network_effects', False):
            advantages.append("Strong network effects")
        
        # Operational advantages
        if data.get('cost_leadership', False):
            advantages.append("Cost leadership position")
        
        if data.get('customer_retention', 0) > 90:
            advantages.append(f"High customer retention ({data['customer_retention']}%)")
        
        # Team advantages
        if data.get('experienced_leadership', False):
            advantages.append("Experienced leadership team")
        
        # Default if none found
        if not advantages:
            advantages.append("Market presence and customer relationships")
        
        return advantages[:5]  # Limit to top 5
    
    def _identify_growth_indicators(self, data: Dict[str, object]) -> List[str]:
        """Identify growth indicators."""
        indicators = []
        
        revenue_growth = data.get('revenue_growth', 0)
        if revenue_growth > 50:
            indicators.append(f"Strong revenue growth ({revenue_growth}% YoY)")
        elif revenue_growth > 20:
            indicators.append(f"Healthy revenue growth ({revenue_growth}% YoY)")
        
        customer_growth = data.get('customer_growth', 0)
        if customer_growth > 30:
            indicators.append(f"Rapid customer acquisition ({customer_growth}% growth)")
        
        if data.get('recent_funding', False):
            indicators.append("Recent funding round completed")
        
        if data.get('market_expansion', False):
            indicators.append("Active market expansion")
        
        if data.get('product_launches', 0) > 0:
            indicators.append(f"Recent product launches ({data['product_launches']})")
        
        if data.get('hiring_growth', 0) > 20:
            indicators.append("Significant hiring growth")
        
        return indicators[:5]
    
    def _assess_risk_factors(self, data: Dict[str, object]) -> List[str]:
        """Assess risk factors."""
        risks = []
        
        if data.get('customer_concentration', 0) > 30:
            risks.append(f"High customer concentration ({data['customer_concentration']}%)")
        
        if data.get('burn_rate', 0) > data.get('monthly_revenue', 1):
            risks.append("High burn rate relative to revenue")
        
        if data.get('competitive_pressure', 'low').lower() == 'high':
            risks.append("Intense competitive pressure")
        
        if data.get('regulatory_risk', False):
            risks.append("Regulatory compliance challenges")
        
        if data.get('technology_debt', 'low').lower() == 'high':
            risks.append("Significant technology debt")
        
        if data.get('key_person_dependency', False):
            risks.append("Key person dependency")
        
        return risks[:5]
    
    def _determine_strategic_priorities(
        self,
        data: Dict[str, object],
        stage: BusinessStage,
        position: MarketPosition
    ) -> List[str]:
        """Determine strategic priorities based on stage and position."""
        priorities = []
        
        # Stage-based priorities
        if stage == BusinessStage.STARTUP:
            priorities.extend(["Product-market fit", "Customer acquisition", "Funding"])
        elif stage == BusinessStage.GROWTH:
            priorities.extend(["Scale operations", "Market expansion", "Team building"])
        elif stage == BusinessStage.SCALE_UP:
            priorities.extend(["Operational efficiency", "Market leadership", "Profitability"])
        elif stage == BusinessStage.MATURE:
            priorities.extend(["Innovation", "Market defense", "Diversification"])
        else:
            priorities.extend(["Digital transformation", "Efficiency", "New markets"])
        
        # Position-based adjustments
        if position == MarketPosition.CHALLENGER:
            priorities.append("Competitive differentiation")
        elif position == MarketPosition.NICHE:
            priorities.append("Niche dominance")
        elif position == MarketPosition.EMERGING:
            priorities.append("Market awareness")
        
        return priorities[:5]
    
    def _calculate_confidence(self, data: Dict[str, object]) -> float:
        """Calculate confidence score based on data completeness."""
        key_fields = [
            'name', 'employee_count', 'revenue', 'industry',
            'funding_stage', 'years_in_business'
        ]
        
        present_fields = sum(1 for field in key_fields if data.get(field))
        confidence = present_fields / len(key_fields)
        
        return round(confidence, 3)
    
    def _assess_data_completeness(self, data: Dict[str, object]) -> str:
        """Assess data completeness level."""
        key_fields = ['name', 'employee_count', 'revenue', 'industry', 'funding_stage']
        present = sum(1 for f in key_fields if data.get(f))
        
        if present >= 4:
            return "high"
        elif present >= 2:
            return "medium"
        else:
            return "low"
    
    def _load_stage_indicators(self) -> Dict[BusinessStage, List[str]]:
        """Load stage indicator patterns."""
        return {
            BusinessStage.STARTUP: ["seed", "early", "founding", "launch"],
            BusinessStage.GROWTH: ["series a", "series b", "expansion", "scaling"],
            BusinessStage.SCALE_UP: ["series c", "series d", "growth", "international"],
            BusinessStage.MATURE: ["established", "profitable", "market leader"],
            BusinessStage.ENTERPRISE: ["fortune", "global", "multinational"]
        }
    
    def _load_position_indicators(self) -> Dict[MarketPosition, List[str]]:
        """Load position indicator patterns."""
        return {
            MarketPosition.LEADER: ["market leader", "#1", "dominant", "leading"],
            MarketPosition.CHALLENGER: ["challenger", "competitor", "alternative"],
            MarketPosition.FOLLOWER: ["follower", "similar to", "like"],
            MarketPosition.NICHE: ["specialized", "focused", "niche"],
            MarketPosition.EMERGING: ["new", "startup", "emerging"]
        }


class ProductIntelligenceBundle:
    """
    Product Intelligence Analysis
    
    Analyzes product data to determine category, value proposition,
    competitive differentiators, and market opportunities.
    """
    
    def __init__(self):
        """Initialize product intelligence bundle."""
        self.category_indicators = self._load_category_indicators()
    
    def analyze(
        self,
        product_data: Dict[str, object],
        context: Optional[Dict[str, object]] = None
    ) -> ProductInsights:
        """
        Analyze product data for business intelligence.
        
        Args:
            product_data: Product information
            context: Additional context
            
        Returns:
            ProductInsights with analysis results
        """
        context = context or {}
        product_name = product_data.get('name', 'Unknown Product')
        
        # Determine product category
        category = self._determine_category(product_data)
        
        # Extract value proposition
        value_proposition = self._extract_value_proposition(product_data)
        
        # Identify target market
        target_market = self._identify_target_market(product_data)
        
        # Extract competitive differentiators
        differentiators = self._extract_differentiators(product_data)
        
        # Identify technical strengths
        technical_strengths = self._identify_technical_strengths(product_data)
        
        # Identify market opportunities
        opportunities = self._identify_opportunities(product_data, category)
        
        # Identify adoption challenges
        challenges = self._identify_challenges(product_data, category)
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence(product_data)
        
        logger.info(f"Product analysis complete for {product_name}: category={category.value}")
        
        return ProductInsights(
            product_name=product_name,
            category=category,
            value_proposition=value_proposition,
            target_market=target_market,
            competitive_differentiators=differentiators,
            technical_strengths=technical_strengths,
            market_opportunities=opportunities,
            adoption_challenges=challenges,
            confidence_score=confidence_score,
            metadata={
                'data_completeness': self._assess_data_completeness(product_data),
                'analysis_version': '1.0'
            }
        )
    
    def _determine_category(self, data: Dict[str, object]) -> ProductCategory:
        """Determine product category."""
        product_type = data.get('type', '').lower()
        description = data.get('description', '').lower()
        
        if 'saas' in product_type or 'subscription' in description:
            return ProductCategory.SAAS
        elif 'platform' in product_type or 'platform' in description:
            return ProductCategory.PLATFORM
        elif 'infrastructure' in product_type or 'cloud' in description:
            return ProductCategory.INFRASTRUCTURE
        elif 'consumer' in product_type or 'b2c' in description:
            return ProductCategory.CONSUMER
        elif 'marketplace' in product_type:
            return ProductCategory.MARKETPLACE
        else:
            return ProductCategory.ENTERPRISE
    
    def _extract_value_proposition(self, data: Dict[str, object]) -> str:
        """Extract value proposition."""
        if data.get('value_proposition'):
            return data['value_proposition']
        
        # Generate from available data
        name = data.get('name', 'This product')
        benefit = data.get('primary_benefit', 'improves efficiency')
        target = data.get('target_audience', 'businesses')
        
        return f"{name} helps {target} by {benefit}"
    
    def _identify_target_market(self, data: Dict[str, object]) -> str:
        """Identify target market."""
        if data.get('target_market'):
            return data['target_market']
        
        segments = []
        
        if data.get('enterprise_focus', False):
            segments.append("Enterprise")
        if data.get('smb_focus', False):
            segments.append("SMB")
        if data.get('consumer_focus', False):
            segments.append("Consumer")
        
        industry = data.get('industry', '')
        if industry:
            segments.append(industry)
        
        return ", ".join(segments) if segments else "standard market"
    
    def _extract_differentiators(self, data: Dict[str, object]) -> List[str]:
        """Extract competitive differentiators."""
        differentiators = []
        
        if data.get('unique_technology'):
            differentiators.append(f"Unique technology: {data['unique_technology']}")
        
        if data.get('pricing_advantage', False):
            differentiators.append("Competitive pricing model")
        
        if data.get('ease_of_use', 0) > 8:
            differentiators.append("Superior user experience")
        
        if data.get('integration_ecosystem', False):
            differentiators.append("Rich integration ecosystem")
        
        if data.get('customer_support', 0) > 8:
            differentiators.append("Exceptional customer support")
        
        if data.get('performance_advantage', False):
            differentiators.append("Performance leadership")
        
        if not differentiators:
            differentiators.append("Market-specific expertise")
        
        return differentiators[:5]
    
    def _identify_technical_strengths(self, data: Dict[str, object]) -> List[str]:
        """Identify technical strengths."""
        strengths = []
        
        if data.get('scalability', 0) > 7:
            strengths.append("Highly scalable architecture")
        
        if data.get('security_certifications'):
            strengths.append(f"Security certified: {data['security_certifications']}")
        
        if data.get('api_first', False):
            strengths.append("API-first design")
        
        if data.get('ai_powered', False):
            strengths.append("AI/ML capabilities")
        
        if data.get('real_time', False):
            strengths.append("Real-time processing")
        
        if data.get('mobile_native', False):
            strengths.append("Mobile-native experience")
        
        return strengths[:5]
    
    def _identify_opportunities(
        self,
        data: Dict[str, object],
        category: ProductCategory
    ) -> List[str]:
        """Identify market opportunities."""
        opportunities = []
        
        # Category-specific opportunities
        if category == ProductCategory.SAAS:
            opportunities.append("Vertical market expansion")
            opportunities.append("Enterprise tier development")
        elif category == ProductCategory.PLATFORM:
            opportunities.append("Developer ecosystem growth")
            opportunities.append("Marketplace monetization")
        elif category == ProductCategory.INFRASTRUCTURE:
            opportunities.append("Multi-cloud expansion")
            opportunities.append("Edge computing integration")
        
        # standard opportunities
        if data.get('international_potential', False):
            opportunities.append("International market expansion")
        
        if data.get('partnership_potential', False):
            opportunities.append("Strategic partnerships")
        
        if data.get('adjacent_markets'):
            opportunities.append(f"Adjacent market: {data['adjacent_markets']}")
        
        return opportunities[:5]
    
    def _identify_challenges(
        self,
        data: Dict[str, object],
        category: ProductCategory
    ) -> List[str]:
        """Identify adoption challenges."""
        challenges = []
        
        if data.get('complexity', 0) > 7:
            challenges.append("Implementation complexity")
        
        if data.get('learning_curve', 0) > 7:
            challenges.append("Steep learning curve")
        
        if data.get('integration_requirements'):
            challenges.append("Integration requirements")
        
        if data.get('price_sensitivity', False):
            challenges.append("Price sensitivity in market")
        
        if data.get('competitive_saturation', False):
            challenges.append("Competitive market saturation")
        
        if data.get('regulatory_requirements', False):
            challenges.append("Regulatory compliance requirements")
        
        return challenges[:5]
    
    def _calculate_confidence(self, data: Dict[str, object]) -> float:
        """Calculate confidence score."""
        key_fields = [
            'name', 'type', 'description', 'target_market',
            'value_proposition', 'features'
        ]
        
        present_fields = sum(1 for field in key_fields if data.get(field))
        confidence = present_fields / len(key_fields)
        
        return round(confidence, 3)
    
    def _assess_data_completeness(self, data: Dict[str, object]) -> str:
        """Assess data completeness level."""
        key_fields = ['name', 'type', 'description', 'target_market']
        present = sum(1 for f in key_fields if data.get(f))
        
        if present >= 3:
            return "high"
        elif present >= 2:
            return "medium"
        else:
            return "low"
    
    def _load_category_indicators(self) -> Dict[ProductCategory, List[str]]:
        """Load category indicator patterns."""
        return {
            ProductCategory.SAAS: ["saas", "subscription", "cloud software"],
            ProductCategory.PLATFORM: ["platform", "ecosystem", "developer"],
            ProductCategory.INFRASTRUCTURE: ["infrastructure", "cloud", "hosting"],
            ProductCategory.CONSUMER: ["consumer", "b2c", "app"],
            ProductCategory.ENTERPRISE: ["enterprise", "b2b", "business"],
            ProductCategory.MARKETPLACE: ["marketplace", "exchange", "network"]
        }


class IntelligenceBundleSystem:
    """
    Complete Business Intelligence System
    
    Combines company and product intelligence for comprehensive
    business analysis.
    """
    
    def __init__(self):
        """Initialize intelligence bundle system."""
        self.company_bundle = CompanyIntelligenceBundle()
        self.product_bundle = ProductIntelligenceBundle()
    
    def analyze(
        self,
        company_data: Optional[Dict[str, object]] = None,
        product_data: Optional[Dict[str, object]] = None,
        context: Optional[Dict[str, object]] = None
    ) -> IntelligenceResult:
        """
        Perform comprehensive business intelligence analysis.
        
        Args:
            company_data: Company information
            product_data: Product information
            context: Additional context
            
        Returns:
            IntelligenceResult with complete analysis
        """
        start_time = time.time()
        
        company_insights = None
        product_insights = None
        
        if company_data:
            company_insights = self.company_bundle.analyze(company_data, context)
        
        if product_data:
            product_insights = self.product_bundle.analyze(product_data, context)
        
        # Calculate overall confidence
        confidences = []
        if company_insights:
            confidences.append(company_insights.confidence_score)
        if product_insights:
            confidences.append(product_insights.confidence_score)
        
        overall_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        processing_time = int((time.time() - start_time) * 1000)
        
        logger.info(f"Business intelligence analysis complete: confidence={overall_confidence:.2f}")
        
        return IntelligenceResult(
            company_insights=company_insights,
            product_insights=product_insights,
            overall_confidence=overall_confidence,
            analysis_timestamp=time.time(),
            processing_time_ms=processing_time
        )
    
    def get_summary(self, result: IntelligenceResult) -> Dict[str, object]:
        """Get summary of intelligence analysis."""
        summary = {
            'overall_confidence': result.overall_confidence,
            'processing_time_ms': result.processing_time_ms
        }
        
        if result.company_insights:
            summary['company'] = {
                'name': result.company_insights.company_name,
                'stage': result.company_insights.business_stage.value,
                'position': result.company_insights.market_position.value,
                'advantages_count': len(result.company_insights.competitive_advantages),
                'risks_count': len(result.company_insights.risk_factors)
            }
        
        if result.product_insights:
            summary['product'] = {
                'name': result.product_insights.product_name,
                'category': result.product_insights.category.value,
                'differentiators_count': len(result.product_insights.competitive_differentiators),
                'opportunities_count': len(result.product_insights.market_opportunities)
            }
        
        return summary


# builder functions
def create_intelligence_system() -> IntelligenceBundleSystem:
    """Create intelligence bundle system instance."""
    return IntelligenceBundleSystem()


def create_company_bundle() -> CompanyIntelligenceBundle:
    """Create company intelligence bundle instance."""
    return CompanyIntelligenceBundle()


def create_product_bundle() -> ProductIntelligenceBundle:
    """Create product intelligence bundle instance."""
    return ProductIntelligenceBundle()


def analyze_company(company_data: Dict[str, object]) -> CompanyInsights:
    """Convenience function to analyze company."""
    bundle = CompanyIntelligenceBundle()
    return bundle.analyze(company_data)


def analyze_product(product_data: Dict[str, object]) -> ProductInsights:
    """Convenience function to analyze product."""
    bundle = ProductIntelligenceBundle()
    return bundle.analyze(product_data)
