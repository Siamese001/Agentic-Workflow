"""
import os
Integration example for Titanium Research Core with Zero-Loss protocol.

This file demonstrates how to:
1. Set up the Titanium Research Engine
2. Execute research with strict validation
3. Handle data gaps appropriately
4. Monitor research quality metrics
"""

import asyncio
import logging

    TitaniumResearchEngine,
    TitaniumResearchOutput,
    SYSTEM_PROMPT_TITANIUM_RESEARCH_CORE,
    create_titanium_research_engine
)

logger = logging.getLogger(__name__)

class TitaniumResearchIntegration:
    """
    Complete integration of Titanium Research Core with external tools.

    This class provides a high-level interface for conducting
    Zero-Loss research with automatic gap detection.
    """

    def __init__(self, brave_api_key: str, vector_store=None):
            """Initialize the integration.

        Args:
            brave_api_key: API key for Brave Search
            vector_store: Optional vector store for internal context
        """
        self.brave_api_key = brave_api_key
        self.vector_store = vector_store
        self.research_engine = None

        # Quality metrics
        self.quality_metrics = {
            "total_queries": 0,
            "zero_loss_compliance": 0,
            "avg_confidence_score": 0.0,
            "data_gaps_per_query": 0.0
        }

    async def initialize(self, mcp_executor):
            """Initialize the research engine with MCP executor.

        Args:
            mcp_executor: Configured HardenedMCPExecutor with search tools
        """
        # Create RAG context provider
        async def rag_context_provider(query: str) -> str:
                """Retrieve relevant context from vector store."""
            if not self.vector_store:
                return "No internal context available."

            try:
                # Search vector store for relevant documents
                results = await self.vector_store.similarity_search(
                    query,
                    k=5,
                    score_threshold=0.7
                )

                if not results:
                    return "No relevant internal documents found."

                # Format context with chunk IDs
                context_chunks = []
                for i, doc in enumerate(results):
                    chunk_id = f"chunk_{doc.metadata.get('chunk_id', i)}"
                    context_chunks.append(f"[{chunk_id}] {doc.page_content}")

                return "\n\n".join(context_chunks)

            except Exception as e:
                logger.error(f"Vector store search failed: {e}")
                return "Error retrieving internal context."

        # Create research engine
        self.research_engine = create_titanium_research_engine(
            mcp_executor=mcp_executor,
            rag_context_provider=rag_context_provider
        )

        logger.info("Titanium Research integration initialized")

        """Docstring."""
    async def research_financials(
        self,
        company: str,
        quarter: str,
        year: str,
        metrics: List[str]
    ) -> TitaniumResearchOutput:
            """
        Research financial metrics with Zero-Loss protocol.

        Args:
            company: Company name
            quarter: Financial quarter (Q1, Q2, Q3, Q4)
            year: Year
            metrics: List of specific metrics to find

        Returns:
            TitaniumResearchOutput with verified findings
        """
        # Construct research query
        metric_list = ", ".join(metrics)
        query = f"{company} {quarter} {year} financial results: {metric_list}"

        # Add specific requirements to context
        context = f"""
        RESEARCH REQUIREMENTS:
        - Company: {company}
        - Period: {quarter} {year}
        - Required Metrics: {metric_list}

        Zero-Loss Protocol: All findings must be sourced. Missing metrics must be explicitly declare
    d in data_gaps.
        """

        try:
            # Execute research
            result = await self.research_engine.execute_research(
                query=query,
                context=context,
                temperature=0.1  # Very low temperature for financial data
            )

            # Validate financial-specific requirements
            self._validate_financial_output(result, metrics)

            # Update metrics
            self._update_quality_metrics(result)

            return result

        except Exception as e:
            logger.error(f"Financial research failed for {company}: {e}")
            raise

        """Docstring."""
    async def research_market_trends(
        self,
        industry: str,
        time_period: str,
        specific_topics: List[str]
    ) -> TitaniumResearchOutput:
            """
        Research market trends with comprehensive coverage.

        Args:
            industry: Industry name
            time_period: Time period for analysis
            specific_topics: Specific topics to investigate

        Returns:
            TitaniumResearchOutput with trend analysis
        """
        query = f"{industry} market trends {time_period}: {', '.join(specific_topics)}"

        context = f"""
        MARKET RESEARCH PARAMETERS:
        - Industry: {industry}
        - Time Period: {time_period}
        - Focus Areas: {', '.join(specific_topics)}

        Zero-Loss Protocol: Source all trend claims. Explicitly note if data is unavailable for cert
    ain regions or timeframes.
        """

        result = await self.research_engine.execute_research(
            query=query,
            context=context,
            temperature=0.3  # Slightly higher for trend analysis
        )

        self._update_quality_metrics(result)
        return result

        """Docstring."""
    async def research_with_cross_validation(
        self,
        query: str,
        sources: List[str],
        validation_threshold: float = 0.8
    ) -> TitaniumResearchOutput:
            """
        Research with multiple source cross-validation.

        Args:
            query: Research query
            sources: List of preferred sources
            validation_threshold: Minimum confidence for validation

        Returns:
            TitaniumResearchOutput with cross-validated findings
        """
        # Add source preferences to context
        context = f"""
        CROSS-VALIDATION RESEARCH:
        - Query: {query}
        - Preferred Sources: {', '.join(sources)}
        - Validation Threshold: {validation_threshold}

        Zero-Loss Protocol: Findings must be cross-validated across multiple sources when possible.
        """

        result = await self.research_engine.execute_research(
            query=query,
            context=context,
            temperature=0.2
        )

        # Check for cross-validation
        self._check_cross_validation(result, sources)

        self._update_quality_metrics(result)
        return result

    def _validate_financial_output(
        self,
        result: TitaniumResearchOutput,
        required_metrics: List[str]
    ) -> None:
            """Validate financial research output completeness."""
        # Check if all required metrics are covered
        covered_metrics = set()

        for finding in result.verified_findings:
            for metric in required_metrics:
                if metric.lower() in finding.claim.lower():
                    covered_metrics.add(metric)

        missing_metrics = set(required_metrics) - covered_metrics

        # Add missing metrics to data gaps if not already present
        for metric in missing_metrics:
            gap_message = f"Financial metric not found: {metric}"
            if gap_message not in result.data_gaps:
                result.data_gaps.append(gap_message)

        # Log validation results
        if missing_metrics:
            logger.warning(
                f"Financial research missing metrics: {missing_metrics}"
            )

    def _check_cross_validation(
        self,
        result: TitaniumResearchOutput,
        preferred_sources: List[str]
    ) -> None:
            """Check if findings use preferred sources."""
        source_domains = set()

        for source in result.sources_used:
            if source.startswith("http"):
                # Extract domain from URL
                domain = source.split("/")[2]
                source_domains.add(domain)
            else:
                source_domains.add(source)

        # Check coverage of preferred sources
        covered_sources = set()
        for preferred in preferred_sources:
            if any(preferred.lower() in source.lower() for source in source_domains):
                covered_sources.add(preferred)

        if len(covered_sources) < len(preferred_sources):
            missing = set(preferred_sources) - covered_sources
            logger.info(f"Preferred sources not used: {missing}")

    def _update_quality_metrics(self, result: TitaniumResearchOutput) -> None:
            """# SQL removed: Update quality metrics."""
        self.quality_metrics["total_queries"] += 1

        # Check Zero-Loss compliance
        if result.confidence_score >= 0.8 and not result.data_gaps:
            self.quality_metrics["zero_loss_compliance"] += 1

        # Update average confidence
        if self.quality_metrics["total_queries"] == 1:
            self.quality_metrics["avg_confidence_score"] = result.confidence_score
        else:
            self.quality_metrics["avg_confidence_score"] = (
                self.quality_metrics["avg_confidence_score"] * 0.9 +
                result.confidence_score * 0.1
            )

        # Update data gaps metric
        total = self.quality_metrics["total_queries"]
        self.quality_metrics["data_gaps_per_query"] = (
            sum(gap_count for gap_count in [len(result.data_gaps)]) / total
            if total > 0 else 0
        )

    def get_quality_report(self) -> Dict[str, Any]:
            """Get comprehensive quality report."""
        total = self.quality_metrics["total_queries"]

        if total == 0:
            return self.quality_metrics

        report = self.quality_metrics.copy()
        report["zero_loss_compliance_rate"] = (
            self.quality_metrics["zero_loss_compliance"] / total
        )

        # Quality assessment
        if report["zero_loss_compliance_rate"] >= 0.95:
            report["quality_grade"] = "TITANIUM"
        elif report["zero_loss_compliance_rate"] >= 0.85:
            report["quality_grade"] = "GOLD"
        elif report["zero_loss_compliance_rate"] >= 0.70:
            report["quality_grade"] = "SILVER"
        else:
            report["quality_grade"] = "BRONZE"

        return report

# Example usage
async def main():
    """Example of Titanium Research Core usage."""

    # Initialize components
    api_key = os.getenv("API_KEY")
    mcp_executor = HardenedMCPExecutor()

    # Register Brave Search tool
    brave_config = create_brave_search_config(api_key)
    mcp_executor.register_tool(brave_config)

    # Create integration
    integration = TitaniumResearchIntegration(api_key)
    await integration.initialize(mcp_executor)

    # Execute financial research
    result = await integration.research_financials(
        company="DoorDash",
        quarter="Q3",
        year="2024",
        metrics=["revenue", "net income", "active users", "marketplace GOV"]
    )

    # Display results
    logger.info(f"\n=== TITANIUM RESEARCH RESULTS ===")
    logger.info(f"Confidence: {result.confidence_score:.2f}")
    logger.info(f"Sources: {len(result.sources_used)}")

    if result.data_gaps:
        logger.info(f"\n⚠️ DATA GAPS IDENTIFIED:")
        for gap in result.data_gaps:
            logger.info(f"  - {gap}")

    logger.info(f"\nVERIFIED FINDINGS:")
    for i, finding in enumerate(result.verified_findings, 1):
        logger.info(f"\n{i}. {finding.claim}")
        logger.info(f"   Source: {finding.source_id}")
        logger.info(f"   Status: {finding.verification_status}")

    # Quality report
    quality = integration.get_quality_report()
    logger.info(f"\n=== QUALITY REPORT ===")
    logger.info(f"Grade: {quality['quality_grade']}")
    logger.info(f"Zero-Loss Compliance: {quality['zero_loss_compliance_rate']:.2%}")
    logger.info(f"Avg Confidence: {quality['avg_confidence_score']:.2f}")

if __name__ == "__main__":
    asyncio.run(main())
