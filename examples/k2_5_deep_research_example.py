from apps_rg.L1_cognition.k2_5_deep_research_agent import create_k25_research_agent
from apps_rg.L1_cognition.k2_5_deep_research_models import (
    CitationMap,
    DeepResearchOutput,
    ExecutiveProfile,
    FinancialMetric,
    LeadershipLayer,
    StrategicLayer,
    TechnicalImplementation,
    TechnicalLayer,
)
from apps_rg.L2_execution.integrity_gate_executor import validate_research_output


def create_doordash_benchmark_example() -> DeepResearchOutput:
    strategic_layer = StrategicLayer(
        core_thesis="Transition from food delivery to local commerce platform achieving GAAP profitability through efficient growth",
        financial_proof_points=[
            FinancialMetric(
                metric_name="Q2 2025 Revenue",
                value="$3.3B",
                period="Q2 2025",
                yoy_change="+25%",
                source_citation="cite_17"
            ),
            FinancialMetric(
                metric_name="GAAP Net Income",
                value="$285M",
                period="Q2 2025",
                yoy_change="First profitable quarter",
                source_citation="cite_17"
            ),
            FinancialMetric(
                metric_name="Operating Margin",
                value="Expansion",
                period="Q2 2025",
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
                implementation_details="Deep learning models for ETA predictions with dynamic model selection based on delivery context (urban vs suburban, weather, traffic)",
                performance_gain="20% improvement in delivery time accuracy",
                source_citation="cite_65"
            ),
            TechnicalImplementation(
                technology_name="Dot Autonomous Delivery Robot",
                implementation_details="Sidewalk-compatible autonomous vehicle with Level 4 autonomy integrating LiDAR, computer vision, and path planning algorithms",
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
                name="Stanley Tang",
                title="Co-founder & Head of DoorDash Labs",
                ownership="Autonomous delivery initiatives, robotics partnerships",
                strategic_focus="Next-generation delivery technologies"
            ),
            ExecutiveProfile(
                name="Ravi Inukonda",
                title="CFO",
                ownership="Risk & Insurance function, financial operations",
                strategic_focus="Path to sustained profitability, margin expansion"
            ),
            ExecutiveProfile(
                name="Sudeep Das",
                title="Head of ML for New Verticals",
                ownership="Personalization algorithms, expansion beyond food",
                strategic_focus="Grocery, retail, and convenience store ML models"
            ),
        ],
        organizational_structure="Labs division under Stanley Tang, Risk function under CFO Ravi Inukonda, ML verticals under Sudeep Das"
    )
    
    citation_map = CitationMap()
    citation_map.add_citation("cite_17", "https://investors.doordash.com/financials/quarterly-results/default.aspx")
    citation_map.add_citation("cite_25", "https://www.linkedin.com/in/sudeep-das")
    citation_map.add_citation("cite_26", "https://investors.doordash.com/governance/leadership-and-governance/default.aspx")
    citation_map.add_citation("cite_65", "https://doordash.engineering/2024/11/improving-eta-predictions-mixture-of-experts/")
    citation_map.add_citation("cite_72", "https://techcrunch.com/2024/08/doordash-serve-robotics-autonomous-delivery/")
    
    return DeepResearchOutput(
        company_name="DoorDash",
        strategic_layer=strategic_layer,
        technical_layer=technical_layer,
        leadership_layer=leadership_layer,
        citation_map=citation_map,
        research_timestamp="2025-12-12T20:39:00Z"
    )


def example_usage():
    print("=" * 80)
    print("K.2.5 Deep Research Protocol - Example Usage")
    print("=" * 80)
    
    agent = create_k25_research_agent(
        company_name="DoorDash",
        company_url="https://www.doordash.com"
    )
    
    print("\n[1] Generated Research Prompt:")
    print("-" * 80)
    prompt = agent.generate_research_prompt()
    print(prompt[:500] + "...\n")
    
    print("\n[2] DoorDash Benchmark Example:")
    print("-" * 80)
    benchmark = create_doordash_benchmark_example()
    
    print(f"\nCompany: {benchmark.company_name}")
    print(f"\nStrategic Thesis: {benchmark.strategic_layer.core_thesis}")
    print(f"\nFinancial Metrics ({len(benchmark.strategic_layer.financial_proof_points)}):")
    for metric in benchmark.strategic_layer.financial_proof_points:
        print(f"  - {metric.metric_name}: {metric.value} ({metric.yoy_change}) [{metric.source_citation}]")
    
    print(f"\nKey Technologies ({len(benchmark.technical_layer.key_technologies)}):")
    for tech in benchmark.technical_layer.key_technologies:
        print(f"  - {tech.technology_name}")
        print(f"    Performance: {tech.performance_gain}")
        print(f"    Citation: {tech.source_citation}")
    
    print(f"\nKey Executives ({len(benchmark.leadership_layer.key_executives)}):")
    for exec in benchmark.leadership_layer.key_executives:
        print(f"  - {exec.name} ({exec.title})")
        print(f"    Ownership: {exec.ownership}")
    
    print(f"\nCitations ({len(benchmark.citation_map.citations)}):")
    for cite_id, url in benchmark.citation_map.citations.items():
        print(f"  [{cite_id}]: {url}")
    
    print("\n[3] Integrity Gate Validation:")
    print("-" * 80)
    integrity_result = validate_research_output(benchmark)
    
    print(f"Passed: {integrity_result.passed}")
    print(f"Depth Score: {integrity_result.depth_score:.2f}")
    
    if integrity_result.rejection_reasons:
        print(f"\nRejection Reasons:")
        for reason in integrity_result.rejection_reasons:
            print(f"  - {reason.value}")
        print(f"\nDetailed Violations:")
        for violation in integrity_result.detailed_violations:
            print(f"  - {violation}")
    else:
        print("\n✓ All integrity checks passed!")
        print(f"✓ Depth score {integrity_result.depth_score:.2f} exceeds minimum 0.7")
    
    print("\n[4] JSON Output:")
    print("-" * 80)
    import json
    output_dict = benchmark.to_dict()
    print(json.dumps(output_dict, indent=2)[:1000] + "...\n")
    
    print("=" * 80)
    print("Example Complete")
    print("=" * 80)


if __name__ == "__main__":
    example_usage()
