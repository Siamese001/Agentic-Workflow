"""
Intelligence Bundles for 10_12
ST-02: Company Intelligence Reasoning Bundle
ST-03: Product Intelligence Reasoning Bundle

Specialized analysis capabilities that provide competitive
advantage through deeper business intelligence insights.
"""

import logging
from typing import Dict, List, object, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import scripts.check_canonical_structure
from collections import defaultdict

logger = logging.getLogger(__name__)


class BusinessStage(Enum):
    """Company business stages"""
    STARTUP = "startup"
    GROWTH = "growth"
    MATURE = "mature"
    ENTERPRISE = "enterprise"


class ProductCategory(Enum):
    """Product categories for analysis"""
    SAAS = "saas"
    HARDWARE = "hardware"
    SERVICE = "service"
    PLATFORM = "platform"
    MARKETPLACE = "marketplace"


@dataclass
class CompanyInsights:
    """Comprehensive company intelligence analysis"""
    company_name: str
    business_stage: BusinessStage
    market_position: str
    competitive_advantages: List[str]
    growth_indicators: List[str]
    risk_factors: List[str]
    strategic_priorities: List[str]
    confidence_score: float


@dataclass
class ProductInsights:
    """Deep product intelligence analysis"""
    product_name: str
    category: ProductCategory
    value_proposition: str
    target_market: str
    competitive_differentiators: List[str]
    technical_strengths: List[str]
    market_opportunities: List[str]
    adoption_challenges: List[str]
    confidence_score: float


class CompanyIntelligenceBundle:
    """
    Specialized Company Analysis
    
    Comprehensive company intelligence analysis that provides
    competitive advantage through deeper business insights.
    """
    
    def __init__(self):
        self.stage_indicators = {
            BusinessStage.STARTUP: ['seed', 'early', 'founded', 'launch', 'startup'],
            BusinessStage.GROWTH: ['series', 'funding', 'scaling', 'expansion', 'growth'],
            BusinessStage.MATURE: ['established', 'profitable', 'market leader', 'stable'],
            BusinessStage.ENTERPRISE: ['fortune', 'global', 'enterprise', 'large scale']
        }
        
        self.competitive_keywords = {
            'advantage': ['leading', 'innovative', 'proprietary', 'unique', 'first-mover'],
            'growth': ['expanding', 'growing', 'scaling', 'increasing', 'accelerating'],
            'risk': ['challenge', 'competition', 'market', 'regulatory', 'technical']
        }
    
    def analyze_company(self, company_data: Dict[str, object]) -> CompanyInsights:
        """
        Comprehensive company intelligence analysis.
        
        Args:
            company_data: Company information including description, funding, market data
            
        Returns:
            CompanyInsights with comprehensive analysis
        """
        company_name = company_data.get('name', 'Unknown Company')
        description = company_data.get('description', '')
        funding_info = company_data.get('funding', {})
        market_data = company_data.get('market', {})
        
        # Analyze business stage
        business_stage = self._determine_business_stage(company_data)
        
        # Analyze market position
        market_position = self._analyze_market_position(company_data)
        
        # Identify competitive advantages
        competitive_advantages = self._identify_competitive_advantages(company_data)
        
        # Extract growth indicators
        growth_indicators = self._extract_growth_indicators(company_data)
        
        # Assess risk factors
        risk_factors = self._assess_risk_factors(company_data)
        
        # Determine strategic priorities
        strategic_priorities = self._determine_strategic_priorities(company_data, business_stage)
        
        # Calculate confidence score
        confidence_score = self._calculate_company_confidence(company_data)
        
        insights = CompanyInsights(
            company_name=company_name,
            business_stage=business_stage,
            market_position=market_position,
            competitive_advantages=competitive_advantages,
            growth_indicators=growth_indicators,
            risk_factors=risk_factors,
            strategic_priorities=strategic_priorities,
            confidence_score=confidence_score
        )
        
        logger.info(f"Analyzed company {company_name}: {business_stage.value} stage, {confidence_score:.2f} confidence")
        
        return insights
    
    def _determine_business_stage(self, company_data: Dict[str, object]) -> BusinessStage:
        """Determine company business stage based on available data."""
        description = company_data.get('description', '').lower()
        funding = company_data.get('funding', {})
        
        stage_scores = defaultdict(int)
        
        # Check description for stage indicators
        for stage, indicators in self.stage_indicators.items():
            for indicator in indicators:
                if indicator in description:
                    stage_scores[stage] += 1
        
        # Check funding information
        if funding:
            funding_stage = funding.get('stage', '').lower()
            if 'seed' in funding_stage or 'pre-seed' in funding_stage:
                stage_scores[BusinessStage.STARTUP] += 3
            elif 'series' in funding_stage:
                stage_scores[BusinessStage.GROWTH] += 3
            elif 'ipo' in funding_stage or 'public' in funding_stage:
                stage_scores[BusinessStage.ENTERPRISE] += 3
        
        # Return stage with highest score
        if stage_scores:
            return max(stage_scores, key=stage_scores.get)
        
        return BusinessStage.GROWTH  # Default assumption
    
    def _analyze_market_position(self, company_data: Dict[str, object]) -> str:
        """Analyze company's market position."""
        description = company_data.get('description', '').lower()
        market_data = company_data.get('market', {})
        
        position_indicators = {
            'leader': ['leader', 'leading', 'dominant', 'market leader', 'number one'],
            'challenger': ['challenger', 'competitor', 'alternative', 'disruptor'],
            'niche': ['specialized', 'niche', 'focused', 'specific', 'targeted'],
            'emerging': ['emerging', 'growing', 'expanding', 'up-and-coming']
        }
        
        position_scores = defaultdict(int)
        
        for position, indicators in position_indicators.items():
            for indicator in indicators:
                if indicator in description:
                    position_scores[position] += 1
        
        if position_scores:
            return max(position_scores, key=position_scores.get)
        
        return 'competitive'  # Default position
    
    def _identify_competitive_advantages(self, company_data: Dict[str, object]) -> List[str]:
        """Identify company's competitive advantages."""
        description = company_data.get('description', '')
        advantages = []
        
        advantage_patterns = {
            'technology': [r'proprietary\s+\w+', r'patented\s+\w+', r'unique\s+technology'],
            'team': [r'experienced\s+team', r'expert\s+\w+', r'industry\s+veterans'],
            'market': [r'first\s+mover', r'market\s+leader', r'established\s+brand'],
            'business_model': [r'recurring\s+revenue', r'subscription\s+model', r'scalable\s+business']
        }
        
        for advantage_type, patterns in advantage_patterns.items():
            for pattern in patterns:
                if re.search(pattern, description, re.IGNORECASE):
                    advantages.append(f"{advantage_type.title()} advantage")
                    break
        
        return advantages[:5]  # Limit to top 5 advantages
    
    def _extract_growth_indicators(self, company_data: Dict[str, object]) -> List[str]:
        """Extract growth indicators from company data."""
        description = company_data.get('description', '').lower()
        funding = company_data.get('funding', {})
        growth_indicators = []
        
        # Check for growth keywords
        growth_keywords = ['growing', 'expanding', 'scaling', 'increasing', 'accelerating']
        for keyword in growth_keywords:
            if keyword in description:
                growth_indicators.append(f"Growth momentum ({keyword})")
        
        # Check funding growth
        if funding:
            amount = funding.get('amount', '')
            if amount and any(char.isdigit() for char in amount):
                growth_indicators.append("Recent funding secured")
        
        # Check market expansion
        if 'expansion' in description or 'global' in description:
            growth_indicators.append("Market expansion opportunities")
        
        return growth_indicators[:4]  # Limit to top 4 indicators
    
    def _assess_risk_factors(self, company_data: Dict[str, object]) -> List[str]:
        """Assess potential risk factors."""
        description = company_data.get('description', '').lower()
        market_data = company_data.get('market', {})
        risk_factors = []
        
        # Competition risks
        if 'competitive' in description or 'challenging' in description:
            risk_factors.append("Competitive market pressure")
        
        # Market risks
        if market_data.get('competition_level', '') == 'high':
            risk_factors.append("High competitive intensity")
        
        # Technology risks
        if 'complex' in description or 'technical' in description:
            risk_factors.append("Technical execution risk")
        
        # Regulatory risks (for certain industries)
        regulated_industries = ['healthcare', 'finance', 'energy', 'transportation']
        for industry in regulated_industries:
            if industry in description:
                risk_factors.append(f"Regulatory compliance in {industry}")
                break
        
        return risk_factors[:3]  # Limit to top 3 risk factors
    
    def _determine_strategic_priorities(
        self, 
        company_data: Dict[str, object], 
        business_stage: BusinessStage
    ) -> List[str]:
        """Determine strategic priorities based on business stage."""
        priorities = []
        
        if business_stage == BusinessStage.STARTUP:
            priorities = ["Product-market fit", "Initial traction", "Team building"]
        elif business_stage == BusinessStage.GROWTH:
            priorities = ["Scaling operations", "Market expansion", "Customer acquisition"]
        elif business_stage == BusinessStage.MATURE:
            priorities = ["Market leadership", "Innovation", "Operational efficiency"]
        elif business_stage == BusinessStage.ENTERPRISE:
            priorities = ["Global expansion", "Diversification", "Sustainable growth"]
        
        # Adjust based on company-specific data
        description = company_data.get('description', '').lower()
        
        if 'technology' in description and 'R&D' not in priorities:
            priorities.append("R&D investment")
        
        if 'customer' in description and 'customer success' not in priorities:
            priorities.append("Customer success")
        
        return priorities[:4]  # Limit to top 4 priorities
    
    def _calculate_company_confidence(self, company_data: Dict[str, object]) -> float:
        """Calculate confidence score for company analysis."""
        confidence = 0.5  # Base confidence
        
        # Increase confidence based on data completeness
        if company_data.get('description'):
            confidence += 0.1
        if company_data.get('funding'):
            confidence += 0.1
        if company_data.get('market'):
            confidence += 0.1
        if company_data.get('team'):
            confidence += 0.1
        
        # Increase confidence based on data quality
        description = company_data.get('description', '')
        if len(description) > 100:
            confidence += 0.1
        
        return min(confidence, 1.0)


class ProductIntelligenceBundle:
    """
    Specialized Product Analysis
    
    Deep product intelligence analysis for enhanced
    product understanding and competitive positioning.
    """
    
    def __init__(self):
        self.category_indicators = {
            ProductCategory.SAAS: ['software', 'platform', 'subscription', 'cloud', 'api'],
            ProductCategory.HARDWARE: ['device', 'hardware', 'physical', 'equipment', 'machine'],
            ProductCategory.SERVICE: ['service', 'consulting', 'professional', 'support', 'expertise'],
            ProductCategory.PLATFORM: ['platform', 'ecosystem', 'marketplace', 'network', 'community'],
            ProductCategory.MARKETPLACE: ['marketplace', 'exchange', 'connecting', 'matching', 'transactions']
        }
        
        self.value_proposition_keywords = {
            'efficiency': ['save time', 'reduce cost', 'improve efficiency', 'automate'],
            'revenue': ['increase revenue', 'generate income', 'monetize', 'profit'],
            'experience': ['better experience', 'user-friendly', 'intuitive', 'seamless'],
            'insights': ['data', 'analytics', 'insights', 'intelligence', 'visibility']
        }
    
    def analyze_product(self, product_data: Dict[str, object]) -> ProductInsights:
        """
        Deep product intelligence analysis.
        
        Args:
            product_data: Product information including description, features, market fit
            
        Returns:
            ProductInsights with comprehensive product analysis
        """
        product_name = product_data.get('name', 'Unknown Product')
        description = product_data.get('description', '')
        features = product_data.get('features', [])
        market_data = product_data.get('market', {})
        
        # Determine product category
        category = self._determine_product_category(product_data)
        
        # Extract value proposition
        value_proposition = self._extract_value_proposition(product_data)
        
        # Identify target market
        target_market = self._identify_target_market(product_data)
        
        # Find competitive differentiators
        competitive_differentiators = self._find_competitive_differentiators(product_data)
        
        # Assess technical strengths
        technical_strengths = self._assess_technical_strengths(product_data)
        
        # Identify market opportunities
        market_opportunities = self._identify_market_opportunities(product_data)
        
        # Assess adoption challenges
        adoption_challenges = self._assess_adoption_challenges(product_data)
        
        # Calculate confidence score
        confidence_score = self._calculate_product_confidence(product_data)
        
        insights = ProductInsights(
            product_name=product_name,
            category=category,
            value_proposition=value_proposition,
            target_market=target_market,
            competitive_differentiators=competitive_differentiators,
            technical_strengths=technical_strengths,
            market_opportunities=market_opportunities,
            adoption_challenges=adoption_challenges,
            confidence_score=confidence_score
        )
        
        logger.info(f"Analyzed product {product_name}: {category.value} category, {confidence_score:.2f} confidence")
        
        return insights
    
    def _determine_product_category(self, product_data: Dict[str, object]) -> ProductCategory:
        """Determine product category based on description and features."""
        description = product_data.get('description', '').lower()
        features = [f.lower() for f in product_data.get('features', [])]
        
        combined_text = description + ' ' + ' '.join(features)
        
        category_scores = defaultdict(int)
        
        for category, indicators in self.category_indicators.items():
            for indicator in indicators:
                if indicator in combined_text:
                    category_scores[category] += 1
        
        if category_scores:
            return max(category_scores, key=category_scores.get)
        
        return ProductCategory.SERVICE  # Default category
    
    def _extract_value_proposition(self, product_data: Dict[str, object]) -> str:
        """Extract core value proposition from product data."""
        description = product_data.get('description', '')
        
        # Look for value proposition patterns
        value_patterns = [
            r'helps?\s+(?:customers?\s+)?(\w+(?:\s+\w+)*)\s+(?:to\s+)?(\w+(?:\s+\w+)*)',
            r'enables?\s+(\w+(?:\s+\w+)*)\s+to\s+(\w+(?:\s+\w+)*)',
            r'provides?\s+(\w+(?:\s+\w+)*)\s+(?:with|for)\s+(\w+(?:\s+\w+)*)'
        ]
        
        for pattern in value_patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                return f"Enables {match.group(1)} to {match.group(2)}"
        
        # Fallback: extract key benefits
        benefits = []
        for value_type, keywords in self.value_proposition_keywords.items():
            for keyword in keywords:
                if keyword in description.lower():
                    benefits.append(value_type)
                    break
        
        if benefits:
            return f"Delivers {', '.join(benefits[:2])}"
        
        return "Provides unique value to customers"
    
    def _identify_target_market(self, product_data: Dict[str, object]) -> str:
        """Identify primary target market."""
        description = product_data.get('description', '').lower()
        market_data = product_data.get('market', {})
        
        # Market segment indicators
        market_segments = {
            'enterprise': ['enterprise', 'large organizations', 'fortune 500'],
            'small business': ['small business', 'smb', 'small companies'],
            'consumers': ['consumers', 'individuals', 'personal'],
            'developers': ['developers', 'engineers', 'technical teams'],
            'healthcare': ['healthcare', 'medical', 'hospitals', 'clinics']
        }
        
        for segment, indicators in market_segments.items():
            for indicator in indicators:
                if indicator in description:
                    return segment.capitalize()
        
        return "General market"  # Default
    
    def _find_competitive_differentiators(self, product_data: Dict[str, object]) -> List[str]:
        """Find competitive differentiators."""
        description = product_data.get('description', '')
        features = product_data.get('features', [])
        differentiators = []
        
        # Differentiator patterns
        differentiator_patterns = {
            'technology': ['proprietary', 'patented', 'unique technology', 'innovative'],
            'ease_of_use': ['easy to use', 'user-friendly', 'intuitive', 'simple'],
            'integration': ['integrates with', 'connects to', 'compatible with'],
            'scalability': ['scalable', 'enterprise-grade', 'high-performance'],
            'cost': ['cost-effective', 'affordable', 'budget-friendly']
        }
        
        combined_text = (description + ' ' + ' '.join(features)).lower()
        
        for diff_type, keywords in differentiator_patterns.items():
            for keyword in keywords:
                if keyword in combined_text:
                    differentiators.append(f"{diff_type.replace('_', ' ').title()}")
                    break
        
        return differentiators[:4]  # Limit to top 4 differentiators
    
    def _assess_technical_strengths(self, product_data: Dict[str, object]) -> List[str]:
        """Assess technical strengths of the product."""
        features = product_data.get('features', [])
        description = product_data.get('description', '')
        strengths = []
        
        # Technical strength indicators
        technical_indicators = {
            'architecture': ['scalable', 'robust', 'architecture', 'infrastructure'],
            'performance': ['fast', 'performance', 'optimized', 'efficient'],
            'security': ['secure', 'encrypted', 'compliant', 'protected'],
            'reliability': ['reliable', 'stable', 'available', 'uptime'],
            'integration': ['api', 'integration', 'connectivity', 'compatible']
        }
        
        combined_text = (description + ' ' + ' '.join(features)).lower()
        
        for strength_type, keywords in technical_indicators.items():
            for keyword in keywords:
                if keyword in combined_text:
                    strengths.append(f"{strength_type.title()}")
                    break
        
        return strengths[:3]  # Limit to top 3 strengths
    
    def _identify_market_opportunities(self, product_data: Dict[str, object]) -> List[str]:
        """Identify market opportunities for the product."""
        market_data = product_data.get('market', {})
        opportunities = []
        
        # Market opportunity indicators
        if market_data.get('growing_market', False):
            opportunities.append("Expanding market size")
        
        if market_data.get('underserved', False):
            opportunities.append("Underserved market segment")
        
        if market_data.get('new_technology', False):
            opportunities.append("Emerging technology adoption")
        
        # Default opportunities based on common patterns
        description = product_data.get('description', '').lower()
        
        if 'global' in description or 'international' in description:
            opportunities.append("International expansion")
        
        if 'enterprise' in description:
            opportunities.append("Enterprise market penetration")
        
        return opportunities[:3]  # Limit to top 3 opportunities
    
    def _assess_adoption_challenges(self, product_data: Dict[str, object]) -> List[str]:
        """Assess potential adoption challenges."""
        description = product_data.get('description', '').lower()
        features = product_data.get('features', [])
        challenges = []
        
        # Complexity challenge
        if len(features) > 10 or 'complex' in description:
            challenges.append("Learning curve complexity")
        
        # Integration challenge
        if 'integration' not in description and 'api' not in description:
            challenges.append("Integration complexity")
        
        # Cost challenge
        if 'expensive' in description or 'premium' in description:
            challenges.append("Price sensitivity")
        
        # Market education challenge
        if 'innovative' in description or 'new' in description:
            challenges.append("Market education required")
        
        return challenges[:2]  # Limit to top 2 challenges
    
    def _calculate_product_confidence(self, product_data: Dict[str, object]) -> float:
        """Calculate confidence score for product analysis."""
        confidence = 0.5  # Base confidence
        
        # Increase confidence based on data completeness
        if product_data.get('description'):
            confidence += 0.1
        if product_data.get('features'):
            confidence += 0.1
        if product_data.get('market'):
            confidence += 0.1
        
        # Increase confidence based on description quality
        description = product_data.get('description', '')
        if len(description) > 50:
            confidence += 0.1
        
        features = product_data.get('features', [])
        if len(features) > 2:
            confidence += 0.1
        
        return min(confidence, 1.0)


class IntelligenceBundleSystem:
    """
    Unified Intelligence Bundle System
    
    Combines company and product intelligence for comprehensive
    business analysis and competitive advantage.
    """
    
    def __init__(self):
        self.company_analyzer = CompanyIntelligenceBundle()
        self.product_analyzer = ProductIntelligenceBundle()
    
    def analyze_business_intelligence(
        self,
        company_data: Dict[str, object],
        product_data: Dict[str, object]
    ) -> Tuple[CompanyInsights, ProductInsights]:
        """
        Apply comprehensive business intelligence analysis.
        
        Args:
            company_data: Company information
            product_data: Product information
            
        Returns:
            Tuple of (company_insights, product_insights)
        """
        # Analyze company intelligence
        company_insights = self.company_analyzer.analyze_company(company_data)
        
        # Analyze product intelligence
        product_insights = self.product_analyzer.analyze_product(product_data)
        
        logger.info(f"Completed business intelligence analysis for {company_insights.company_name}")
        
        return company_insights, product_insights


# Factory functions for easy integration
def create_company_intelligence_bundle() -> CompanyIntelligenceBundle:
    """Create company intelligence bundle instance."""
    return CompanyIntelligenceBundle()


def create_product_intelligence_bundle() -> ProductIntelligenceBundle:
    """Create product intelligence bundle instance."""
    return ProductIntelligenceBundle()


def create_intelligence_bundle_system() -> IntelligenceBundleSystem:
    """Create unified intelligence bundle system instance."""
    return IntelligenceBundleSystem()
