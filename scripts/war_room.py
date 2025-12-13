"""
War Room Script - Executive Strategy Execution

Manually runs the expensive executive strategy agents (K.11, K.12, K.13)
for competitive intelligence before critical interviews.

Usage:
    python war_room.py --company "TechCorp" --jd-file job_description.txt
    python war_room.py --company "TechCorp" --interviewer "https://linkedin.com/in/interviewer"
"""

import asyncio
import argparse
import json
import logging
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

    ExecutiveAgentOrchestrator,
    DataSourceProvider,
    create_executive_orchestrator
)
    TechnicalSWOT,
    StrategyRoadmap,
    InterviewerProfile,
    ExecutiveIntelligenceReport
)
    HardenedBraveSearch,
    create_brave_search_config
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("WarRoom")

class WarRoom:
    """
    War Room execution environment for executive strategy agents.

    Provides a controlled environment to run expensive intelligence
    gathering operations with proper logging and output formatting.
    """

    def __init__(self, brave_api_key: Optional[str] = None):
        """Initialize the War Room.

        Args:
            brave_api_key: Optional Brave Search API key
        """
        # Initialize search tool if API key provided
        search_tool = None
        if brave_api_key:
            try:
                search_config = create_brave_search_config(brave_api_key)
                search_tool = HardenedBraveSearch(brave_api_key)
                logger.info("Brave Search initialized for external data gathering")
            except Exception as e:
                logger.warning(f"Failed to initialize Brave Search: {e}")

        # Initialize data source provider
        self.data_sources = DataSourceProvider(search_tool)

        # Initialize executive orchestrator
        self.orchestrator = create_executive_orchestrator(
            brave_search_tool=search_tool,
            data_source_provider=self.data_sources
        )

        # Load workflow configuration
        self.workflow_config = self._load_workflow_config()

        # Execution context
        self.session_id = f"war_room_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.results = {}

        logger.info(f"War Room initialized with session ID: {self.session_id}")

    def _load_workflow_config(self) -> Dict[str, Any]:
        """Load workflow configuration.

        Returns:
            Workflow configuration dictionary
        """
        config_path = project_root / "Job_Workflow_v24.9.json"

        if config_path.exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        else:
            logger.warning("Workflow config not found, using defaults")
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for executive agents.

        Returns:
            Default configuration
        """
        return {
            "4.reasoning": {
                "K.11_shadow_audit": {
                    "node_id": "K.11",
                    "name": "Technical Due Diligence (Shadow Audit)",
                    "infrastructure_config": {
                        "compute_tier": "HIGH_REASONING",
                        "primary_model": "claude-3-5-sonnet-20241022",
                        "temperature_override": 0.2
                    },
                    "schema_enforcement": {
                        "pydantic_model": "TechnicalSWOT",
                        "enabled": True
                    }
                },
                "K.12_strategy_roadmap": {
                    "node_id": "K.12",
                    "name": "30-60-90 Day Architect",
                    "infrastructure_config": {
                        "compute_tier": "HIGH_REASONING",
                        "primary_model": "gpt-4o",
                        "temperature_override": 0.5
                    },
                    "schema_enforcement": {
                        "pydantic_model": "StrategyRoadmap",
                        "enabled": True
                    }
                },
                "K.13_interviewer_sim": {
                    "node_id": "K.13",
                    "name": "Oppositional Simulation",
                    "infrastructure_config": {
                        "compute_tier": "STANDARD",
                        "primary_model": "gpt-4o",
                        "temperature_override": 0.7
                    },
                    "schema_enforcement": {
                        "pydantic_model": "InterviewerProfile",
                        "enabled": True
                    }
                }
            }
        }

    async def execute_shadow_audit(self, company_name: str) -> TechnicalSWOT:
        """Execute K.11 Shadow Audit.

        Args:
            company_name: Target company name

        Returns:
            Technical SWOT analysis
        """
        logger.info(f"🕵️  Running K.11 Shadow Audit for {company_name}...")

        config = self.workflow_config["4.reasoning"]["K.11_shadow_audit"]

        try:
            swot = await self.orchestrator.execute_k11_shadow_audit(
                company_name=company_name,
                config=config
            )

            self.results["k11_swot"] = swot

            logger.info(f"⚠️  Identified {len(swot.suspected_bottlenecks)} bottlenecks")
            logger.info(f"🎯 Strategic Opportunity: {swot.strategic_opportunity[:100]}...")

            return swot

        except Exception as e:
            logger.error(f"K.11 execution failed: {e}")
            raise

    async def execute_strategy_roadmap(
        """Docstring."""
        self,
        job_description: str,
        technical_swot: TechnicalSWOT
    ) -> StrategyRoadmap:
        """Execute K.12 Strategy Roadmap.

        Args:
            job_description: Job description text
            technical_swot: Results from shadow audit

        Returns:
            30-60-90 day strategy roadmap
        """
        logger.info("🗺️  Generating K.12 Strategy Roadmap...")

        config = self.workflow_config["4.reasoning"]["K.12_strategy_roadmap"]

        try:
            roadmap = await self.orchestrator.execute_k12_strategy(
                job_description=job_description,
                technical_swot=technical_swot,
                config=config
            )

            self.results["k12_roadmap"] = roadmap

            logger.info("✅ Strategy Generated")
            logger.info(f"📅 {len(roadmap.milestones)} milestones planned")
            logger.info(f"⚡ {len(roadmap.immediate_wins)} immediate wins identified")

            # Show immediate wins
            logger.info("\nImmediate Wins:")
            for win in roadmap.immediate_wins:
                logger.info(f"  • {win['initiative']} (Impact: {win['impact']},
                    Effort: {win['effort']})")

            return roadmap

        except Exception as e:
            logger.error(f"K.12 execution failed: {e}")
            raise

    async def execute_interviewer_simulation(
        """Docstring."""
        self,
        interviewer_linkedin: str,
        resume_text: str
    ) -> InterviewerProfile:
        """Execute K.13 Interviewer Simulation.

        Args:
            interviewer_linkedin: LinkedIn profile URL
            resume_text: Candidate resume text

        Returns:
            Interviewer profile with predicted questions
        """
        logger.info("🎭 Running K.13 Interviewer Simulation...")

        config = self.workflow_config["4.reasoning"]["K.13_interviewer_sim"]

        try:
            profile = await self.orchestrator.execute_k13_simulation(
                interviewer_linkedin=interviewer_linkedin,
                resume_text=resume_text,
                config=config
            )

            self.results["k13_interviewer"] = profile

            logger.info(f"👤 Interviewer Archetype: {profile.dominant_archetype}")
            logger.info(f"❓ {len(profile.kill_chain_questions)} predicted questions")

            # Show hardest questions
            logger.info("\nToughest Questions to Prepare For:")
            for i, question in enumerate(profile.kill_chain_questions[:3], 1):
                logger.info(f"\n{i}. {question['question_text']}")
                logger.info(f"   Recommended Angle: {question['recommended_angle']}")

            return profile

        except Exception as e:
            logger.error(f"K.13 execution failed: {e}")
            raise

    def generate_intelligence_report(
        """Docstring."""
        self,
        company_name: str,
        position: str,
        interview_date: Optional[str] = None
    ) -> ExecutiveIntelligenceReport:
        """Generate comprehensive intelligence report.

        Args:
            company_name: Target company
            position: Position being interviewed for
            interview_date: Scheduled interview date

        Returns:
            Complete intelligence report
        """
        logger.info("📊 Generating Executive Intelligence Report...")

        # Compile key differentiators
        differentiators = []

        if "k12_roadmap" in self.results:
            roadmap = self.results["k12_roadmap"]
            differentiators.append(f"Strategic 90-day plan with {len(roadmap.milestones)} specific m
    ilestones")

        if "k11_swot" in self.results:
            swot = self.results["k11_swot"]
            differentiators.append(f"Deep technical understanding of their {swot.gen_ai_maturity_sco
    re}/5 AI maturity")

        # Risk mitigation strategies
        risks = []
        if "k11_swot" in self.results:
            swot = self.results["k11_swot"]
            for bottleneck in swot.suspected_bottlenecks[:2]:
                risks.append(f"Address {bottleneck.lower()} with phased approach")

        if "k13_interviewer" in self.results:
            profile = self.results["k13_interviewer"]
            risks.append(f"Align with {profile.dominant_archetype} interview style")

        # Create report
        report = ExecutiveIntelligenceReport(
            target_company=company_name,
            position=position,
            interview_date=interview_date,
            technical_swot=self.results.get("k11_swot"),
            strategy_roadmap=self.results.get("k12_roadmap"),
            interviewer_profile=self.results.get("k13_interviewer"),
            key_differentiators=differentiators,
            risk_mitigation=risks,
            generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        return report

    def save_results(self, output_dir: Path) -> None:
        """Save all results to files.

        Args:
            output_dir: Directory to save results
        """
        output_dir.mkdir(exist_ok=True)

        # Save individual results
        for key, result in self.results.items():
            filename = f"{self.session_id}_{key}.json"
            filepath = output_dir / filename

            if hasattr(result, 'model_dump'):
                data = result.model_dump()
            else:
                data = result

            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)

            logger.info(f"Saved {filename}")

        # Save combined report
        if all(k in self.results for k in ["k11_swot", "k12_roadmap"]):
            report = self.generate_intelligence_report(
                company_name="Target Corp",  # Would be passed in
                position="Senior Role"
            )

            report_file = output_dir / f"{self.session_id}_intelligence_report.json"
            with open(report_file, 'w') as f:
                json.dump(report.model_dump(), f, indent=2)

            logger.info(f"Saved intelligence_report.json")

    def print_summary(self) -> None:
        """Print execution summary."""
        stats = self.orchestrator.get_statistics()

        logger.info("\n" + "="*60)
        logger.info("WAR ROOM EXECUTION SUMMARY")
        logger.info("="*60)
        logger.info(f"Session ID: {self.session_id}")
        logger.info(f"K.11 Executions: {stats['k11_executions']}")
        logger.info(f"K.12 Executions: {stats['k12_executions']}")
        logger.info(f"K.13 Executions: {stats['k13_executions']}")
        logger.info(f"Estimated Cost: ${stats['total_cost_estimate']:.2f}")
        logger.info("="*60)

async def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description="Executive Strategy War Room")
    parser.add_argument("--company", required=True, help="Target company name")
    parser.add_argument("--jd-file", help="Path to job description file")
    parser.add_argument("--jd-text", help="Job description text directly")
    parser.add_argument("--interviewer", help="Interviewer LinkedIn URL")
    parser.add_argument("--resume-file", help="Path to resume file")
    parser.add_argument("--resume-text", help="Resume text directly")
    parser.add_argument("--output-dir", default="./war_room_output", help="Output directory")
    parser.add_argument("--brave-key", help="Brave Search API key (or set BRAVE_API_KEY env var)")

    args = parser.parse_args()

    # Get API key
    brave_key = args.brave_key or os.getenv("BRAVE_API_KEY")

    # Initialize War Room
    war_room = WarRoom(brave_api_key=brave_key)

    try:
        # Get job description
        jd_text = None
        if args.jd_file and Path(args.jd_file).exists():
            with open(args.jd_file, 'r') as f:
                jd_text = f.read()
        elif args.jd_text:
            jd_text = args.jd_text
        else:
            logger.error("Job description required (--jd-file or --jd-text)")
            return

        # Execute K.11 Shadow Audit
        logger.info("\n🚀 Starting War Room Execution...")
        swot = await war_room.execute_shadow_audit(args.company)

        # Execute K.12 Strategy Roadmap
        roadmap = await war_room.execute_strategy_roadmap(jd_text, swot)

        # Execute K.13 Interviewer Simulation (if provided)
        if args.interviewer:
            resume_text = None
            if args.resume_file and Path(args.resume_file).exists():
                with open(args.resume_file, 'r') as f:
                    resume_text = f.read()
            elif args.resume_text:
                resume_text = args.resume_text
            else:
                logger.warning("No resume provided for interviewer simulation")

            if resume_text:
                profile = await war_room.execute_interviewer_simulation(
                    args.interviewer,
                    resume_text
                )

        # Save results
        output_dir = Path(args.output_dir)
        war_room.save_results(output_dir)

        # Print summary
        war_room.print_summary()

        logger.info(f"\n✅ War Room complete! Results saved to: {output_dir}")

    except Exception as e:
        logger.error(f"War Room execution failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
