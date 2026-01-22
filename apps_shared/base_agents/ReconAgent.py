"""Competitor Recon Signal - Identifies competitive DNA in candidate history.

This module analyzes a candidate's work history against a target company's
competitive landscape to identify insider knowledge that can be leveraged
for signaling deep authority.
"""

import logging


logger = logging.getLogger(__name__)


class CompetitivePosition(str, Enum):
    """Position of company relative to target."""

    DIRECT_COMPETITOR = "DIRECT_COMPETITOR"  # e.g. Uber vs Lyft
    ADJACENT_MARKET = "ADJACENT_MARKET"  # e.g. Uber vs DoorDash
    UNRELATED = "UNRELATED"


class Company(BaseModel):
    """Company information."""

    name: str
    industry: str
    description: str | None = None
    competitors: list[str] = Field(default_factory=list)
    adjacent_companies: list[str] = Field(default_factory=list)


class ReconSignal(BaseModel):
    """Signal from competitive reconnaissance."""

    target_company: str
    competitor_detected: str | None = None
    position: CompetitivePosition
    strategy_recommendation: str
    confidence_score: float = Field(default=0.0, description="Confidence in signal")
    market_insights: list[str] = Field(default_factory=list)


class ReconAgent:
    """Analyzes candidate history for competitive signals."""

    def __init__(self):
        """Initialize recon agent with competitor database."""
        # Mock competitor database - in production, this would query real data
        self.competitor_db: dict[str, Company] = self._build_competitor_db()

        # Industry mapping for adjacent markets
        self.industry_adjacency: dict[str, list[str]] = {
            "rideshare": ["delivery", "logistics", "transportation"],
            "delivery": ["rideshare", "logistics", "grocery"],
            "fintech": ["banking", "payments", "lending"],
            "banking": ["fintech", "payments", "insurance"],
            "ecommerce": ["retail", "marketplace", "payments"],
            "social": ["messaging", "content", "community"],
            "cloud": ["infrastructure", "devops", "security"],
            "saas": ["enterprise", "productivity", "analytics"],
            "healthcare": ["biotech", "pharma", "wellness"],
            "education": ["edtech", "training", "certification"],
        }

        logger.info("Initialized ReconAgent with competitor database")

    def _build_competitor_db(self) -> dict[str, Company]:
        """Build mock competitor database.

        Returns:
            Dictionary of companies and their competitive data
        """
        # In production, this would be populated from real data sources
        return {
            "Uber": Company(
                name="Uber",
                industry="rideshare",
                description="Ridesharing and delivery platform",
                competitors=["Lyft", "Didi", "Bolt", "Grab"],
                adjacent_companies=["DoorDash", "Grubhub", "Postmates", "Instacart"],
            ),
            "Lyft": Company(
                name="Lyft",
                industry="rideshare",
                description="Ridesharing platform",
                competitors=["Uber", "Didi", "Bolt"],
                adjacent_companies=["DoorDash", "Postmates"],
            ),
            "DoorDash": Company(
                name="DoorDash",
                industry="delivery",
                description="Food delivery platform",
                competitors=["Uber Eats", "Grubhub", "Postmates", "Instacart"],
                adjacent_companies=["Uber", "Lyft", "Grubhub"],
            ),
            "Airbnb": Company(
                name="Airbnb",
                industry="hospitality",
                description="Vacation rental platform",
                competitors=["Booking.com", "Expedia", "Vrbo"],
                adjacent_companies=["Hotels.com", "TripAdvisor", "Hostelworld"],
            ),
            "Stripe": Company(
                name="Stripe",
                industry="fintech",
                description="Payment processing platform",
                competitors=["PayPal", "Square", "Adyen", "Braintree"],
                adjacent_companies=["Plaid", "Razorpay", "Klarna"],
            ),
            "Square": Company(
                name="Square",
                industry="fintech",
                description="Payment and business services",
                competitors=["PayPal", "Stripe", "Adyen"],
                adjacent_companies=["Toast", "Shopify", "Lightspeed"],
            ),
            "Amazon": Company(
                name="Amazon",
                industry="ecommerce",
                description="E-commerce and cloud platform",
                competitors=["Walmart", "Target", "eBay", "Alibaba"],
                adjacent_companies=["Shopify", "BigCommerce", "Magento"],
            ),
            "Shopify": Company(
                name="Shopify",
                industry="ecommerce",
                description="E-commerce platform",
                competitors=["BigCommerce", "Magento", "WooCommerce"],
                adjacent_companies=["Amazon", "eBay", "Etsy"],
            ),
            "Google": Company(
                name="Google",
                industry="tech",
                description="Search and advertising platform",
                competitors=["Microsoft", "Amazon", "Apple", "Meta"],
                adjacent_companies=["Salesforce", "Oracle", "SAP"],
            ),
            "Microsoft": Company(
                name="Microsoft",
                industry="tech",
                description="Software and cloud platform",
                competitors=["Google", "Amazon", "Apple", "Oracle"],
                adjacent_companies=["Salesforce", "IBM", "Red Hat"],
            ),
            "Meta": Company(
                name="Meta",
                industry="social",
                description="Social media platform",
                competitors=["Twitter", "Snapchat", "LinkedIn", "TikTok"],
                adjacent_companies=["Discord", "Reddit", "Telegram"],
            ),
            "Netflix": Company(
                name="Netflix",
                industry="streaming",
                description="Video streaming platform",
                competitors=["Disney+", "HBO Max", "Hulu", "Amazon Prime"],
                adjacent_companies=["YouTube", "Twitch", "Vimeo"],
            ),
            "Tesla": Company(
                name="Tesla",
                industry="automotive",
                description="Electric vehicle manufacturer",
                competitors=["BYD", "Rivian", "Lucid", "Nio"],
                adjacent_companies=["Ford", "GM", "Volkswagen", "Toyota"],
            ),
            "Spotify": Company(
                name="Spotify",
                industry="music",
                description="Music streaming platform",
                competitors=["Apple Music", "Amazon Music", "YouTube Music"],
                adjacent_companies=["Pandora", "SoundCloud", "Tidal"],
            ),
        }

    def analyze(self, target_company: str, candidate_history: list[str]) -> ReconSignal:
        """Analyze candidate history for competitive signals.

        Args:
            target_company: Target company name
            candidate_history: List of companies candidate worked at

        Returns:
            Reconnaissance signal with strategy
        """
        # Get target company info
        target = self.competitor_db.get(target_company)
        if not target:
            # Unknown company - return generic signal
            return ReconSignal(
                target_company=target_company,
                position=CompetitivePosition.UNRELATED,
                strategy_recommendation="No competitive intelligence available. Focus on transferable skills.",
                confidence_score=0.0,
            )

        # Check for direct competitors
        direct_match = self._find_direct_competitor(target, candidate_history)
        if direct_match:
            return self._generate_direct_competitor_signal(target, direct_match)

        # Check for adjacent market companies
        adjacent_match = self._find_adjacent_competitor(target, candidate_history)
        if adjacent_match:
            return self._generate_adjacent_signal(target, adjacent_match)

        # No competitive match found
        return ReconSignal(
            target_company=target_company,
            position=CompetitivePosition.UNRELATED,
            strategy_recommendation="No direct competitive experience. Emphasize industry expertise and transferable skills.",
            confidence_score=0.0,
        )

    def _find_direct_competitor(self, target: Company, candidate_history: list[str]) -> str | None:
        """Find if candidate worked at direct competitor.

        Args:
            target: Target company
            candidate_history: Candidate's work history

        Returns:
            Name of matching competitor or None
        """
        history_lower = [h.lower() for h in candidate_history]

        for competitor in target.competitors:
            if competitor.lower() in history_lower:
                return competitor

        return None

    def _find_adjacent_competitor(
        self, target: Company, candidate_history: list[str]
    ) -> str | None:
        """Find if candidate worked at adjacent market company.

        Args:
            target: Target company
            candidate_history: Candidate's work history

        Returns:
            Name of adjacent company or None
        """
        history_lower = [h.lower() for h in candidate_history]

        for adjacent in target.adjacent_companies:
            if adjacent.lower() in history_lower:
                return adjacent

        # Also check by industry adjacency
        adjacent_industries = self.industry_adjacency.get(target.industry, [])
        for company in candidate_history:
            company_info = self.competitor_db.get(company)
            if company_info and company_info.industry in adjacent_industries:
                return company

        return None

    def _generate_direct_competitor_signal(self, target: Company, competitor: str) -> ReconSignal:
        """Generate signal for direct competitor experience.

        Args:
            target: Target company
            competitor: Competitor name

        Returns:
            Recon signal with strategy
        """
        insights = [
            f"Understands {target.name}'s competitive landscape from inside {competitor}",
            "Has insider knowledge of competitor strategies and pain points",
            "Can speak to industry-specific challenges and solutions",
        ]

        strategy = (
            f"Candidate is an INSIDER with direct experience at {competitor}. "
            f"Emphasize knowledge of {competitor}'s struggles/wins and how that "
            f"translates to solving {target.name}'s challenges. Highlight competitive "
            f"insights and market positioning expertise."
        )

        return ReconSignal(
            target_company=target.name,
            competitor_detected=competitor,
            position=CompetitivePosition.DIRECT_COMPETITOR,
            strategy_recommendation=strategy,
            confidence_score=0.9,
            market_insights=insights,
        )

    def _generate_adjacent_signal(self, target: Company, adjacent: str) -> ReconSignal:
        """Generate signal for adjacent market experience.

        Args:
            target: Target company
            adjacent: Adjacent company name

        Returns:
            Recon signal with strategy
        """
        insights = [
            f"Understands adjacent market dynamics from {adjacent}",
            "Brings cross-industry perspective and fresh ideas",
            "Familiar with related technologies and business models",
        ]

        strategy = (
            f"Candidate knows the MODEL from adjacent experience at {adjacent}. "
            f"Emphasize transferable domain expertise and how insights from "
            f"{adjacent} apply to {target.name}'s market. Highlight ability to "
            f"bridge different but related domains."
        )

        return ReconSignal(
            target_company=target.name,
            competitor_detected=adjacent,
            position=CompetitivePosition.ADJACENT_MARKET,
            strategy_recommendation=strategy,
            confidence_score=0.6,
            market_insights=insights,
        )

    def add_company(self, company: Company) -> None:
        """Add company to competitor database.

        Args:
            company: Company to add
        """
        self.competitor_db[company.name] = company
        logger.debug(f"Added company to database: {company.name}")

    def update_competitors(self, company_name: str, competitors: list[str]) -> None:
        """Update competitor list for a company.

        Args:
            company_name: Company to update
            competitors: New competitor list
        """
        if company_name in self.competitor_db:
            self.competitor_db[company_name].competitors = competitors
            logger.debug(f"Updated competitors for {company_name}")

    def get_competitive_landscape(self, company_name: str) -> dict[str, list[str]] | None:
        """Get competitive landscape for a company.

        Args:
            company_name: Company to analyze

        Returns:
            Dictionary with competitors and adjacent companies
        """
        company = self.competitor_db.get(company_name)
        if not company:
            return None

        return {
            "direct_competitors": company.competitors,
            "adjacent_companies": company.adjacent_companies,
            "industry": company.industry,
        }

    def batch_analyze(
        self, target_companies: list[str], candidate_history: list[str]
    ) -> list[ReconSignal]:
        """Analyze multiple target companies.

        Args:
            target_companies: List of target companies
            candidate_history: Candidate's work history

        Returns:
            List of recon signals
        """
        signals = []
        for target in target_companies:
            signal = self.analyze(target, candidate_history)
            signals.append(signal)

        return signals


# Global agent instance
_recon_agent: ReconAgent | None = None


def get_recon_agent() -> ReconAgent:
    """Get global recon agent instance.

    Returns:
        ReconAgent instance
    """
    global _recon_agent
    if _recon_agent is None:
        _recon_agent = ReconAgent()
    return _recon_agent


# Convenience function
def analyze_competitive_fit(target_company: str, candidate_history: list[str]) -> ReconSignal:
    """Analyze candidate's competitive fit for target company.

    Args:
        target_company: Target company name
        candidate_history: List of companies worked at

    Returns:
        Reconnaissance signal
    """
    agent = get_recon_agent()
    return agent.analyze(target_company, candidate_history)
