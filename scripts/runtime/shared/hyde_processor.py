"""Archetype-Aware HyDE Processor - Hypothetical Document Embeddings.

This module implements HyDE (Hypothetical Document Embeddings) to improve retrieval
recall by generating archetype-specific hypothetical documents that guide vector
search toward the most relevant content for each recipient type.
"""

import logging
from dataclasses import dataclass
from enum import Enum

LOGGER = logging.getLogger(__name__)


class ExpansionStrategy(str, Enum):
    """Strategies for query expansion."""
    ARCHETYPE_SPECIFIC = "archetype_specific"
    INDUSTRY_AWARE = "industry_aware"
    KEYWORD_BOOST = "keyword_boost"
    HYBRID = "hybrid"


@dataclass
class HyDEDocument:
    """A hypothetical document generated for query expansion."""

    content: str
    archetype: str
    industry: str
    strategy: ExpansionStrategy
    word_count: int
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_valid(self) -> bool:
            """Check if the generated document meets quality criteria."""
        return (
            len(self.content.strip()) > 20 and  # Minimum length
            self.word_count > 10 and  # Minimum word count
            not self.content.lower().startswith(("i cannot", "i'm unable", "as an ai"))
        )

@dataclass
class HyDEResult:
    """Result of HyDE processing."""

    original_query: str
    expanded_query: str
    hypothetical_doc: Optional[HyDEDocument]
    success: bool
    fallback_used: bool = False
    error_message: Optional[str] = None

# Archetype-specific prompt templates
HYDE_TEMPLATES = {
    # Technical Leadership
    "CTO": (
        "Write a snippet from a performance review describing a high-impact technical "
        "achievement in {industry}. Focus on system architecture, scalability, distributed "
        "systems, and specific stack details like {keywords}. Avoid buzzwords; use "
        "engineering metrics. Keep it 50-75 words."
    ),
    "VP Engineering": (
        "Write a snippet from a performance review describing a high-impact technical "
        "achievement in {industry}. Focus on system architecture, scalability, distributed "
        "systems, and specific stack details like {keywords}. Avoid buzzwords; use "
        "engineering metrics. Keep it 50-75 words."
    ),
    "Engineering Manager": (
        "Write a performance review snippet highlighting team leadership and technical "
        "delivery in {industry}. Focus on mentoring, process improvements, and successful "
        "project execution using {keywords}. Include team size and delivery metrics. "
        "Keep it 50-75 words."
    ),
    "Staff Engineer": (
        "Write a technical achievement description for a staff engineer in {industry}. "
        "Focus on complex problem-solving, technical innovation, and cross-team influence "
        "using {keywords}. Include specific technologies and measurable outcomes. "
        "Keep it 50-75 words."
    ),
    "Principal Engineer": (
        "Write a principal engineer achievement description in {industry}. Focus on "
        "technical strategy, architecture decisions, and organizational impact using "
        "{keywords}. Include scale, complexity, and business outcomes. Keep it 50-75 words."
    ),

    # Executive Leadership
    "CEO": (
        "Write a bullet point describing a strategic business outcome in {industry}. "
        "Focus on revenue growth, cost reduction, speed-to-market, and ROI using "
        "{keywords}. Use executive-level language and board-ready metrics. "
        "Keep it 50-75 words."
    ),
    "Founder": (
        "Write a founder achievement description in {industry}. Focus on company "
        "building, fundraising, product-market fit, and growth metrics using {keywords}. "
        "Include scale and milestone achievements. Keep it 50-75 words."
    ),
    "CFO": (
        "Write a CFO achievement summary in {industry}. Focus on financial optimization, "
        "cost savings, revenue growth, and investor relations using {keywords}. "
        "Include specific financial metrics. Keep it 50-75 words."
    ),
    "CPO": (
        "Write a Chief Product Officer achievement in {industry}. Focus on product "
        "strategy, user growth, retention, and market success using {keywords}. "
        "Include KPIs and business impact. Keep it 50-75 words."
    ),

    # Product & Design
    "VP Product": (
        "Write a product leadership achievement in {industry}. Focus on product "
        "strategy, roadmap execution, and user outcomes using {keywords}. "
        "Include metrics and cross-functional impact. Keep it 50-75 words."
    ),
    "Product Manager": (
        "Write a product manager success story in {industry}. Focus on feature "
        "delivery, user feedback, and business impact using {keywords}. "
        "Include specific metrics and stakeholder value. Keep it 50-75 words."
    ),

    # Talent & HR
    "Recruiter": (
        "Write a resume summary for a candidate in {industry} matching these skills: "
        "{keywords}. Focus on years of experience, specific job titles, certifications, "
        "and pedigree. Keep it keyword-dense and ATS-friendly. Keep it 50-75 words."
    ),
    "Talent Acquisition": (
        "Write a talent acquisition specialist achievement in {industry}. Focus on "
        "hiring metrics, time-to-fill, diversity initiatives, and quality of hire "
        "using {keywords}. Include specific recruiting metrics. Keep it 50-75 words."
    ),
    "HR Manager": (
        "Write an HR manager achievement in {industry}. Focus on employee engagement, "
        "retention programs, policy improvements, and culture initiatives using "
        "{keywords}. Include HR metrics. Keep it 50-75 words."
    ),

    # Sales & Marketing
    "VP Sales": (
        "Write a sales leadership achievement in {industry}. Focus on revenue growth, "
        "team performance, market expansion, and strategic wins using {keywords}. "
        "Include sales metrics and quotas. Keep it 50-75 words."
    ),
    "Account Executive": (
        "Write an account executive success story in {industry}. Focus on deal size, "
        "client relationships, and solution selling using {keywords}. "
        "Include specific sales metrics. Keep it 50-75 words."
    ),

    # Default template
    "DEFAULT": (
        "Write a detailed resume bullet point demonstrating expertise in {keywords} "
        "within {industry}. Focus on clear actions, measurable results, and professional "
        "impact. Use strong action verbs and specific outcomes. Keep it 50-75 words."
    )
}

class HyDEProcessor:
    """Archetype-aware HyDE processor for query expansion.

    This processor generates hypothetical documents tailored to specific recipient
    archetypes to improve vector search recall and relevance.
    """

    def __init__(
        self,
        llm_client: Optional[Any] = None,
        default_industry: str = "Technology",
        max_retries: int = 2,
        fallback_enabled: bool = True
    ):
            """Initialize the HyDE processor.

        Args:
            llm_client: LLM client for document generation
            default_industry: Default industry if not specified
            max_retries: Maximum retry attempts for generation
            fallback_enabled: Whether to use keyword fallback on failure
        """
        self.llm_client = llm_client
        self.default_industry = default_industry
        self.max_retries = max_retries
        self.fallback_enabled = fallback_enabled

        # Archetype normalization map
        self.archetype_aliases = {
            # Technical aliases
            "vp eng": "CTO",
            "vp of engineering": "CTO",
            "head of engineering": "CTO",
            "tech lead": "Staff Engineer",
            "senior engineer": "Staff Engineer",

            # Executive aliases
            "president": "CEO",
            "managing director": "CEO",
            "co-founder": "Founder",

            # Product aliases
            "head of product": "VP Product",
            "product lead": "Product Manager",

            # Talent aliases
            "talent partner": "Recruiter",
            "sourcer": "Recruiter",
            "hr business partner": "HR Manager",

            # Sales aliases
            "sales director": "VP Sales",
            "business development": "Account Executive"
        }

        logger.info(f"Initialized HyDEProcessor with {len(HYDE_TEMPLATES)} templates")

        """Docstring."""
    def expand_query(
        self,
        original_query: str,
        archetype: str,
        industry: Optional[str] = None
    ) -> HyDEResult:
            """Expand query using archetype-aware HyDE.

        Args:
            original_query: Original search query
            archetype: Target recipient archetype
            industry: Industry context

        Returns:
            HyDEResult with expanded query and metadata
        """
        try:
            # Generate hypothetical document
            hypothetical_doc = self.generate_hypothetical_doc(
                original_query, archetype, industry or self.default_industry
            )

            if hypothetical_doc and hypothetical_doc.is_valid:
                # Combine with original query
                expanded_query = f"{original_query}\n\n{hypothetical_doc.content}"

                return HyDEResult(
                    original_query=original_query,
                    expanded_query=expanded_query,
                    hypothetical_doc=hypothetical_doc,
                    SUCCESS=True,
                    fallback_used=False
                )
            else:
                # Use fallback
                if self.fallback_enabled:
                    fallback_query = self._keyword_fallback(original_query, industry)
                    return HyDEResult(
                        original_query=original_query,
                        expanded_query=fallback_query,
                        hypothetical_doc=None,
                        SUCCESS=False,
                        fallback_used=True,
                        error_message="Generated document invalid, used keyword fallback"
                    )
                else:
                    return HyDEResult(
                        original_query=original_query,
                        expanded_query=original_query,
                        hypothetical_doc=None,
                        SUCCESS=False,
                        fallback_used=False,
                        error_message="Generated document invalid and fallback disabled"
                    )

        except Exception as e:
            logger.error(f"HyDE expansion failed: {str(e)}")

            # Emergency fallback
            fallback_query = self._keyword_fallback(original_query,
                industry) if self.fallback_enabled else original_query

            return HyDEResult(
                original_query=original_query,
                expanded_query=fallback_query,
                hypothetical_doc=None,
                SUCCESS=False,
                fallback_used=self.fallback_enabled,
                error_message=str(e)
            )

        """Docstring."""
    def generate_hypothetical_doc(
        self,
        query: str,
        archetype: str,
        industry: str
    ) -> Optional[HyDEDocument]:
            """Generate a hypothetical document for query expansion.

        Args:
            query: Original query keywords
            archetype: Target archetype
            industry: Industry context

        Returns:
            HyDEDocument or None if generation fails
        """
        # Construct the prompt
        PROMPT = self._construct_prompt(query, archetype, industry)

        # Attempt generation with retries
        for attempt in range(self.max_retries + 1):
            try:
                if self.llm_client:
                    # Use actual LLM client
                    CONTENT = self._call_llm(prompt)
                else:
                    # Mock generation for testing
                    CONTENT = self._mock_generation(query, archetype, industry)

                if content:
                    # Create document
                    DOC = HyDEDocument(
                        CONTENT=content.strip(),
                        ARCHETYPE=archetype,
                        INDUSTRY=industry,
                        STRATEGY=ExpansionStrategy.ARCHETYPE_SPECIFIC,
                        word_count=len(content.split()),
                        METADATA={"attempt": attempt + 1}
                    )

                    if doc.is_valid:
                        logger.debug(f"Generated valid HyDE document for {archetype}")
                        return doc
                    else:
                        logger.warning(f"Generated invalid document on attempt {attempt + 1}")

            except Exception as e:
                logger.warning(f"Generation attempt {attempt + 1} failed: {str(e)}")
                if attempt == self.max_retries:
                    break

        logger.error(f"Failed to generate valid document after {self.max_retries + 1} attempts")
        return None

    def _construct_prompt(self, query: str, archetype: str, industry: str) -> str:
            """Construct the prompt for hypothetical document generation.

        Args:
            query: Original query
            archetype: Target archetype
            industry: Industry context

        Returns:
            Formatted prompt string
        """
        # Normalize archetype
        normalized_archetype = self._normalize_archetype(archetype)

        # Get template
        TEMPLATE = HYDE_TEMPLATES.get(normalized_archetype, HYDE_TEMPLATES["DEFAULT"])

        # Fill placeholders
        PROMPT = template.format(
            KEYWORDS=query,
            INDUSTRY=industry
        )

        return prompt

    def _normalize_archetype(self, archetype: str) -> str:
            """Normalize archetype string to match template keys.

        Args:
            archetype: Raw archetype string

        Returns:
            Normalized archetype key
        """
        # Direct match
        if archetype in HYDE_TEMPLATES:
            return archetype

        # Check aliases
        archetype_lower = archetype.lower()
        for alias, target in self.archetype_aliases.items():
            if alias in archetype_lower or archetype_lower in alias:
                return target

        # Fuzzy matching for partial matches
        for key in HYDE_TEMPLATES:
            if key.lower() in archetype_lower or archetype_lower in key.lower():
                return key

        # Default
        return "DEFAULT"

    def _call_llm(self, prompt: str) -> Optional[str]:
            """Call the LLM client for document generation.

        Args:
            prompt: Generation prompt

        Returns:
            Generated content or None
        """
        if not self.llm_client:
            return None

        try:
            # This would be implemented with actual LLM client
            # For now, return None to trigger fallback
            logger.info("LLM client not implemented, using fallback")
            return None
        except Exception as e:
            logger.error(f"LLM call failed: {str(e)}")
            return None

    def _mock_generation(self, query: str, archetype: str, industry: str) -> str:
            """Mock document generation for testing.

        Args:
            query: Original query
            archetype: Target archetype
            industry: Industry context

        Returns:
            Mock generated content
        """
        # Simple mock based on archetype
        if "CTO" in archetype or "VP" in archetype:
            return f"Architected scalable {query} solution handling 10M+ requests, reducing latency
    by 60% through distributed systems design and microservices optimization in {industry}."
        elif "CEO" in archetype or "Founder" in archetype:
            return f"Drove {query} strategy resulting in 200% revenue growth and market expansion, s
    ecuring $50M in funding while building a 100-person team in {industry}."
        elif "Recruiter" in archetype:
            return f"5+ years experience in {query} with proven track record of hiring top talent, f
    ull-cycle recruiting, and building high-performing teams in {industry}."
        else:
            return f"Delivered impactful {query} solutions achieving measurable business outcomes th
    rough technical excellence and strategic thinking in {industry}."

    def _keyword_fallback(self, query: str, industry: Optional[str] = None) -> str:
            """Fallback expansion using keyword enhancement.

        Args:
            query: Original query
            industry: Industry context

        Returns:
            Expanded query with keywords
        """
        # Industry-specific keywords
        industry_keywords = {
            "technology": ["software", "engineering", "development", "architecture", "scalability"],
            "finance": ["financial", "banking", "investment", "trading", "risk"],
            "healthcare": ["medical", "health", "patient", "clinical", "healthcare"],
            "retail": ["sales", "customer", "ecommerce", "merchandise", "retail"],
            "consulting": ["strategy", "advisory", "management", "consulting", "solutions"]
        }

        # Add industry keywords
        expanded_parts = [query]

        if industry and industry.lower() in industry_keywords:
            KEYWORDS = industry_keywords[industry.lower()]
            expanded_parts.append(" ".join(keywords[:3]))  # Add top 3 keywords

        # Add generic professional keywords
        expanded_parts.append("achievement results impact metrics")

        return "\n\n".join(expanded_parts)

# Factory function for easy instantiation
    """Docstring."""
def create_hyde_processor(
    llm_client: Optional[Any] = None,
    default_industry: str = "Technology",
    max_retries: int = 2
) -> HyDEProcessor:
    """Create a HyDEProcessor instance.

    Args:
        llm_client: LLM client for generation
        default_industry: Default industry context
        max_retries: Maximum retry attempts

    Returns:
        Configured HyDEProcessor instance
    """
    return HyDEProcessor(
        llm_client=llm_client,
        default_industry=default_industry,
        max_retries=max_retries,
        fallback_enabled=True
    )

# Convenience function for quick expansion
    """Docstring."""
def expand_query_with_hyde(
    query: str,
    archetype: str,
    industry: Optional[str] = None,
    llm_client: Optional[Any] = None
) -> str:
    """Quickly expand a query using HyDE.

    Args:
        query: Original query
        archetype: Target archetype
        industry: Industry context
        llm_client: LLM client

    Returns:
        Expanded query string
    """
    PROCESSOR = create_hyde_processor(llm_client=llm_client)
    RESULT = processor.expand_query(query, archetype, industry)
    return result.expanded_query

