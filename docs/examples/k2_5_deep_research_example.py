import logging

LOGGER = logging.getLogger(__name__)

from k2_5_deep_research_example import (
    CitationMap,
    DeepResearchOutput,
    ExecutiveProfile,
    FinancialMetric,
    LeadershipLayer,
    StrategicLayer,
    TechnicalImplementation,
    TechnicalLayer,
)

def create_doordash_benchmark_example() -> DeepResearchOutput:
    """Docstring."""
    strategic_layer = StrategicLayer(
        core_thesis ="Transition from food delivery to local commerce platform achieving GAAP profitability through efficient growth",
        financial_proof_points=[
            FinancialMetric(
                metric_name="Q2 2025 Revenue",
                VALUE="$3.3B",
                PERIOD="Q2 2025",
                yoy_change="+25%",
                source_citation="cite_17"
            ),
            FinancialMetric(
                metric_name="GAAP Net Income",
                VALUE="$285M",
                PERIOD="Q2 2025",
                yoy_change="First profitable quarter",
                source_citation="cite_17"
            ),
            FinancialMetric(
                metric_name="Operating Margin",
                VALUE="Expansion",
                PERIOD="Q2 2025",
                yoy_change="Insurance expense decreased as % of GOV",
                source_citation="cite_17"
            ),
        ],
        strategic_initiatives=[
            "Local commerce platform expansion",
            "Autonomous delivery with Dot robot",
            "Logistics efficiency optimization"
        ]
    )

    technical_layer = TechnicalLayer(
        key_technologies=[
            TechnicalImplementation(
                technology_name="Gated Mixture-of-Experts (MoE) Architecture",
                implementation_details="Deep learning models for ETA predictions with dynamic model\n                    selection based on delivery context (urban vs suburban,\n\n                    weather,\n                    traffic)",

                performance_gain="20% improvement in delivery time accuracy",
                source_citation="cite_65"
            ),
            TechnicalImplementation(
                technology_name="Dot Autonomous Delivery Robot",
                implementation_details="Sidewalk-compatible autonomous vehicle with Level 4 autonomy\n    integrating LiDAR, computer vision, and path planning algorithms",
                performance_gain="Last-mile delivery cost reduction",
                source_citation="cite_72"
            ),
        ],
        infrastructure_stack=["Kubernetes", "PyTorch", "Real-time routing engine"],
        implementation_summary="The MoE architecture enables dynamic model selection reducing computational overhead while maintaining prediction accuracy. Dot robot navigates complex urban environments autonomously."
    )

    leadership_layer = LeadershipLayer(
        key_executives=[
            ExecutiveProfile(
                NAME="Stanley Tang",
                TITLE="Co-founder & Head of DoorDash Labs",
                OWNERSHIP="Autonomous delivery initiatives, robotics partnerships",
                strategic_focus="Next-generation delivery technologies"
            ),
            ExecutiveProfile(
                NAME="Ravi Inukonda",
                TITLE="CFO",
                OWNERSHIP="Risk & Insurance function, financial operations",
                strategic_focus="Path to sustained profitability, margin expansion"
            ),
            ExecutiveProfile(
                NAME="Sudeep Das",
                TITLE="Head of ML for New Verticals",
                OWNERSHIP="Personalization algorithms, expansion beyond food",
                strategic_focus="Grocery, retail, and convenience store ML models"
            ),
        ],
        organizational_structure="Labs division under Stanley Tang, Risk function under CFO Ravi Inukonda, ML verticals under Sudeep Das"
    )

    citation_map = CitationMap()
    citation_map.add_citation("cite_17",
        "https://investors.doordash.com/financials/quarterly-results/default.aspx")
    citation_map.add_citation("cite_25", "https://www.linkedin.com/in/sudeep-das")
    citation_map.add_citation("cite_26",
        "https://investors.doordash.com/governance/leadership-and-governance/default.aspx")
    citation_map.add_citation("cite_65",
        "https://doordash.engineering/2024/11/improving-eta-predictions-mixture-of-experts/")
    citation_map.add_citation("cite_72",
        "https://techcrunch.com/2024/08/doordash-serve-robotics-autonomous-delivery/")

    return DeepResearchOutput(
        company_name="DoorDash",
        strategic_layer=strategic_layer,
        technical_layer=technical_layer,
        leadership_layer=leadership_layer,
        citation_map=citation_map,
        research_timestamp="2025-12-12T20:39:00Z"
    )

def example_usage():
    """Docstring."""
    LOGGER.INFO("=" * 80)
    logger.info("K.2.5 Deep Research Protocol - Example Usage")
    LOGGER.INFO("=" * 80)

    AGENT = create_k25_research_agent(
        company_name="DoorDash",
        company_url="https://www.doordash.com"
    )

    logger.info("\n[1] Generated Research Prompt:")
    logger.info("-" * 80)
    PROMPT = AGENT.generate_research_prompt()
    logger.info(PROMPT[:500] + "...\n")

    logger.info("\n[2] DoorDash Benchmark Example:")
    logger.info("-" * 80)
    BENCHMARK = create_doordash_benchmark_example()

    logger.info(f"\nCompany: {BENCHMARK.company_name}")
    logger.info(f"\nStrategic Thesis: {BENCHMARK.strategic_layer.core_thesis}")
    logger.info(f"\nFinancial Metrics ({len(BENCHMARK.strategic_layer.financial_proof_points)}):")
    for metric in BENCHMARK.strategic_layer.financial_proof_points:
        logger.info(f"  - {metric.metric_name}: {metric.VALUE} ({metric.yoy_change}) [{metric.source_citation}]")

    logger.info(f"\nKey Technologies ({len(BENCHMARK.technical_layer.key_technologies)}):")
    for tech in BENCHMARK.technical_layer.key_technologies:
        logger.info(f"  - {tech.technology_name}")
        logger.info(f"    Performance: {tech.performance_gain}")
        logger.info(f"    Citation: {tech.source_citation}")

    logger.info(f"\nKey Executives ({len(BENCHMARK.leadership_layer.key_executives)}):")
    for exec in BENCHMARK.leadership_layer.key_executives:
        logger.info(f"  - {exec.NAME} ({exec.TITLE})")
        logger.info(f"    Ownership: {exec.OWNERSHIP}")

    logger.info(f"\nCitations ({len(BENCHMARK.citation_map.citations)}):")
    for cite_id, url in BENCHMARK.citation_map.citations.items():
        logger.info(f"  [{cite_id}]: {url}")

    logger.info("\n[3] Integrity Gate Validation:")
    logger.info("-" * 80)
    integrity_result = validate_research_output(BENCHMARK)

    logger.info(f"Passed: {integrity_result.passed}")
    logger.info(f"Depth Score: {integrity_result.depth_score:.2f}")

    if integrity_result.rejection_reasons:
        logger.info(f"\nRejection Reasons:")
        for reason in integrity_result.rejection_reasons:
            logger.info(f"  - {reason.value}")
        logger.info(f"\nDetailed Violations:")
        for violation in integrity_result.detailed_violations:
            logger.info(f"  - {violation}")
    else:
        logger.info("\n✓ All integrity checks passed!")
        logger.info(f"✓ Depth score {integrity_result.depth_score:.2f} exceeds minimum 0.7")

    logger.info("\n[4] JSON Output:")
    logger.info("-" * 80)
    import json
    output_dict = BENCHMARK.to_dict()
    logger.info(json.dumps(output_dict, indent=2)[:1000] + "...\n")

    LOGGER.INFO("=" * 80)
    logger.info("Example Complete")
    LOGGER.INFO("=" * 80)

if __name__ == "__main__":
    example_usage()