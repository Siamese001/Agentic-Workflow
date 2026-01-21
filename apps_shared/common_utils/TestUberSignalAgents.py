"""Test Suite for Uber High Signal Agents.

This test file demonstrates the three new high-signal components:
1. Architecture Visualizer (Mermaid.js diagrams)
2. Cultural Decoder (Company culture alignment)
3. Pre-Mortem Agent (Risk analysis)

Run with: python -m asyncio runtime.shared.test_uber_signal_agents.py
"""

import asyncio
import logging

# Import the three agents
from runtime.shared import (
    ArchitectureVisualizerAgent,
    CulturalDecoderAgent,
    DiagramType,
    PreMortemAgent,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UberSignalTestSuite:
    """Test suite for the three Uber High Signal agents."""

    def __init__(self):
        """Initialize the test suite with all three agents."""
        self.architecture_agent = ArchitectureVisualizerAgent()
        self.cultural_agent = CulturalDecoderAgent()
        self.pre_mortem_agent = PreMortemAgent()

        # Test data
        self.test_architecture_bullet = (
            "Built a scalable RAG pipeline using FastAPI, Redis caching, and Pinecone vector database "
            "to serve 10M+ queries with 99.9% uptime"
        )

        self.test_resume_summary = (
            "Experienced engineering leader with 8+ years building high-performance teams. "
            "Led the migration of monolithic systems to microservices, reducing latency by 60%. "
            "Passionate about mentorship and delivering exceptional user experiences."
        )

        self.test_onboarding_plan = """
        30-60-90 Day Plan for VP of Engineering:

        Days 1-30:
        - Meet with all engineering teams to understand current challenges
        - Audit existing tech stack and identify quick wins
        - Establish communication rhythms and stakeholder relationships

        Days 31-60:
        - Implement agile transformation across all teams
        - Launch new developer onboarding program
        - Begin migration to cloud infrastructure

        Days 61-90:
        - Complete cloud migration of critical services
        - Establish engineering metrics dashboard
        - Hire 2 senior engineers and 1 engineering manager
        """

    async def test_architecture_visualizer(self):
        """Test the Architecture Visualizer Agent."""
        logger.info("\n" + "=" * 60)
        logger.info("TESTING: Architecture Visualizer Agent")
        logger.info("=" * 60)

        try:
            # Test 1: Generate diagram from bullet
            diagram_artifact = await self.architecture_agent.generate_diagram(
                description=self.test_architecture_bullet,
                diagram_type=DiagramType.FLOWCHART,
                caption="RAG Pipeline Architecture",
            )

            if diagram_artifact:
                logger.info("✅ Diagram generated successfully!")
                logger.info(f"   - Nodes: {diagram_artifact.node_count}")
                logger.info(f"   - Complexity: {diagram_artifact.complexity_score:.1%}")

                # Render the diagram
                rendered = self.architecture_agent.render_artifact(diagram_artifact)
                logger.info("\n📊 Generated Mermaid Diagram:")
                logger.info(rendered)
            else:
                logger.error("❌ Failed to generate diagram")

            # Test 2: Visualize bullet directly
            bullet_diagram = await self.architecture_agent.visualize_bullet(
                self.test_architecture_bullet
            )

            if bullet_diagram:
                logger.info("\n✅ Bullet visualization successful!")
            else:
                logger.error("❌ Bullet visualization failed")

        except Exception as e:
            logger.error(f"❌ Architecture Visualizer test failed: {e}")

    async def test_cultural_decoder(self):
        """Test the Cultural Decoder Agent."""
        logger.info("\n" + "=" * 60)
        logger.info("TESTING: Cultural Decoder Agent")
        logger.info("=" * 60)

        try:
            # Test 1: Load pre-loaded DNA
            amazon_dna = self.cultural_agent._load_dna("Amazon")
            logger.info("✅ Loaded Amazon DNA profile")
            logger.info(f"   - Core Values: {len(amazon_dna.core_values)} values")
            logger.info(f"   - Writing Style: {amazon_dna.writing_style}")
            logger.info(f"   - Buzzwords: {amazon_dna.buzzwords[:3]}...")

            # Test 2: Rewrite for culture
            aligned_content = await self.cultural_agent.rewrite_for_culture(
                original_text=self.test_resume_summary, company_dna=amazon_dna, text_type="resume"
            )

            logger.info("\n✅ Content rewritten for Amazon culture!")
            logger.info(f"   - Alignment Score: {aligned_content.alignment_score:.1%}")
            logger.info(f"   - Key Changes: {len(aligned_content.key_changes)}")
            logger.info(f"\n📝 Original: {self.test_resume_summary[:100]}...")
            logger.info(f"\n📝 Aligned: {aligned_content.aligned_text[:100]}...")
            logger.info(f"\n💡 Rationale: {aligned_content.alignment_rationale}")

            # Test 3: Audit cultural fit
            audit_result = self.cultural_agent.audit_fit(
                text=self.test_resume_summary, company_name="Google"
            )

            logger.info("\n✅ Cultural fit audit completed!")
            logger.info(f"   - Company: {audit_result['company']}")
            logger.info(f"   - Alignment Score: {audit_result['alignment_score']:.1%}")
            logger.info(f"   - Grade: {audit_result['grade']}")
            logger.info(f"   - Suggestions: {len(audit_result['suggestions'])}")

            for suggestion in audit_result["suggestions"]:
                logger.info(f"     • {suggestion}")

        except Exception as e:
            logger.error(f"❌ Cultural Decoder test failed: {e}")

    async def test_pre_mortem_agent(self):
        """Test the Pre-Mortem Agent."""
        logger.info("\n" + "=" * 60)
        logger.info("TESTING: Pre-Mortem Agent")
        logger.info("=" * 60)

        try:
            # Test 1: Analyze onboarding plan
            pre_mortem_report = await self.pre_mortem_agent.analyze_plan(
                plan_text=self.test_onboarding_plan, plan_type="onboarding"
            )

            logger.info("✅ Pre-mortem analysis completed!")
            logger.info(f"   - Overall Risk Score: {pre_mortem_report.overall_risk_score:.1%}")
            logger.info(f"   - Recommendation: {pre_mortem_report.go_no_go_recommendation}")
            logger.info(f"   - Top Risks Identified: {len(pre_mortem_report.top_risks)}")

            # Display top risks
            logger.info("\n⚠️  Top Risks:")
            for i, risk in enumerate(pre_mortem_report.top_risks[:3], 1):
                logger.info(f"\n   {i}. {risk.risk}")
                logger.info(f"      Category: {risk.category}")
                logger.info(f"      Probability: {risk.probability:.0%}")
                logger.info(f"      Impact: {risk.impact}")
                logger.info(f"      Risk Score: {risk.risk_score:.2f}")
                logger.info(f"      Mitigation: {risk.mitigation_strategy}")

            # Display critical success factors
            logger.info("\n🎯 Critical Success Factors:")
            for factor in pre_mortem_report.critical_success_factors:
                logger.info(f"   • {factor}")

            # Render full report
            rendered_report = self.pre_mortem_agent.render_risk_assessment(pre_mortem_report)
            logger.info("\n📊 Full Pre-Mortem Report:")
            logger.info(rendered_report)

        except Exception as e:
            logger.error(f"❌ Pre-Mortem Agent test failed: {e}")

    async def test_integration_scenario(self):
        """Test all three agents working together on a complete scenario."""
        logger.info("\n" + "=" * 60)
        logger.info("TESTING: Integrated Scenario")
        logger.info("=" * 60)

        try:
            # Scenario: A candidate applying for Head of AI at Netflix
            target_company = "Netflix"
            role_description = """
            Seeking Head of AI to lead our machine learning initiatives.
            You will build and scale our recommendation systems,
            manage a team of 15 ML engineers, and drive innovation
            in content personalization using cutting-edge AI technologies.
            """

            # Step 1: Cultural alignment
            netflix_dna = self.cultural_agent._load_dna(target_company)
            aligned_summary = await self.cultural_agent.rewrite_for_culture(
                original_text=self.test_resume_summary,
                company_dna=netflix_dna,
                text_type="executive_summary",
            )

            logger.info("✅ Step 1: Cultural alignment complete")
            logger.info(f"   Alignment Score: {aligned_summary.alignment_score:.1%}")

            # Step 2: Architecture visualization
            tech_bullet = """
            Architected Netflix's recommendation engine using TensorFlow,
            Kafka for real-time data streaming, and Elasticsearch for
            content search, serving 200M+ users with 95% accuracy.
            """
            architecture_diagram = await self.architecture_agent.generate_diagram(
                description=tech_bullet,
                diagram_type=DiagramType.FLOWCHART,
                caption="Netflix ML Architecture",
            )

            logger.info("✅ Step 2: Architecture diagram generated")
            logger.info(f"   Nodes: {architecture_diagram.node_count}")

            # Step 3: Risk analysis for 90-day plan
            ai_plan = """
            90-Day Plan for Head of AI:

            Month 1: Assess current ML systems, team capabilities, and data infrastructure
            Month 2: Implement A/B testing framework, launch model optimization initiative
            Month 3: Deploy new recommendation algorithm, establish ML governance board
            """

            risk_analysis = await self.pre_mortem_agent.analyze_plan(
                plan_text=ai_plan, plan_type="AI leadership"
            )

            logger.info("✅ Step 3: Risk analysis complete")
            logger.info(f"   Risk Score: {risk_analysis.overall_risk_score:.1%}")

            # Generate integrated output
            logger.info("\n" + "=" * 60)
            logger.info("🚀 INTEGRATED OUTPUT FOR NETFLIX APPLICATION")
            logger.info("=" * 60)

            logger.info("\n📋 Executive Summary (Culturally Aligned):")
            logger.info(aligned_summary.aligned_text)

            logger.info("\n🏗️  Technical Architecture:")
            logger.info(self.architecture_agent.render_artifact(architecture_diagram))

            logger.info("\n⚠️  Risk Assessment:")
            logger.info(
                f"Overall Risk: {risk_analysis.overall_risk_score:.1%} - {risk_analysis.go_no_go_recommendation}"
            )

            logger.info("\n✅ Integration test successful!")

        except Exception as e:
            logger.error(f"❌ Integration test failed: {e}")

    async def run_all_tests(self):
        """Run all tests sequentially."""
        logger.info("🚀 Starting Uber High Signal Agents Test Suite")
        logger.info("=" * 60)

        await self.test_architecture_visualizer()
        await self.test_cultural_decoder()
        await self.test_pre_mortem_agent()
        await self.test_integration_scenario()

        logger.info("\n" + "=" * 60)
        logger.info("✅ ALL TESTS COMPLETED")
        logger.info("=" * 60)


async def main():
    """Main entry point for running tests."""
    test_suite = UberSignalTestSuite()
    await test_suite.run_all_tests()


if __name__ == "__main__":
    # Run the test suite
    asyncio.run(main())
