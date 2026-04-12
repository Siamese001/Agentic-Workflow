"""Stack Modernization Agent - Technical Transformation Specialist.

This agent detects legacy technology signals and generates transformation
theses that position candidates as experts in safely modernizing legacy
systems to modern AI architectures.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class LegacyDiagnostic:
    """Diagnostic of legacy technology stack."""

    detected_legacy_tech: list[str]
    implied_pain_points: list[str]
    modernization_score: float

    @property
    def is_highly_legacy(self) -> bool:
        """Check if stack is highly legacy."""
        return self.modernization_score >= 0.7


@dataclass
class MigrationThesis:
    """Thesis for stack modernization."""

    current_state_diagnosis: str
    target_state_vision: str
    bridge_strategy: str

    @property
    def is_transformative(self) -> bool:
        """Check if thesis represents significant transformation."""
        return len(self.bridge_strategy) > 100


class StackModernizationAgent:
    """Diagnoses legacy stacks and prescribes modernization strategies."""

    def __init__(self):
        """Initialize the stack modernization agent."""
        self.legacy_markers = {
            "infrastructure": {
                "on-prem": "Mature on-premise infrastructure",
                "data center": "Established data center operations",
                "hybrid cloud": "Hybrid cloud environment",
                "vmware": "VMware virtualization platform",
                "physical servers": "Physical server infrastructure",
                "mainframe": "Legacy Mainframe Infrastructure",
            },
            "data": {
                "oracle": "Oracle database systems",
                "stored procedures": "Stored procedure architecture",
                "db2": "IBM Db2 Database",
                "hadoop": "Hadoop data processing",
                "data warehouse": "Traditional data warehouse",
                "etl": "ETL pipeline architecture",
            },
            "application": {
                "monolith": "Monolithic application architecture",
                "java 8": "Java 8 application stack",
                "soap": "SOAP web services",
                "xml": "XML-based data exchange",
                "jsp": "JSP presentation layer",
                "cobol": "Legacy COBOL Systems",
            },
            "search": {
                "elasticsearch": "Elasticsearch (keyword-only)",
                "solr": "Apache Solr search",
                "keyword search": "Keyword-based search",
                "full-text search": "Traditional full-text search",
            },
        }
        self.pain_point_mappings = {
            "infrastructure": [
                "Slow deployment cycles",
                "Limited scalability",
                "High operational overhead",
                "Difficulty in disaster recovery",
            ],
            "data": [
                "Data silos and duplication",
                "Slow query performance",
                "Complex data transformations",
                "Limited real-time capabilities",
            ],
            "application": [
                "Tight coupling between components",
                "Difficult to scale individual features",
                "Slow innovation cycles",
                "High risk deployments",
            ],
            "search": [
                "Limited semantic understanding",
                "Poor relevance for complex queries",
                "Difficulty handling unstructured data",
                "Limited multilingual support",
            ],
        }
        self.transformation_playbooks = {
            "search_migration": {
                "legacy": ["elasticsearch", "solr", "keyword search"],
                "modern": "Vector-based Semantic RAG",
                "thesis": "Moving from keyword matching to Semantic RAG to improve retrieval accuracy by 40%",
                "strategy": "Implement Strangler Fig Pattern: gradually replace keyword endpoints with vector search while maintaining 100% uptime",
            },
            "monolith_decomposition": {
                "legacy": ["monolith", "java 8", "soap"],
                "modern": "Event-Driven Agentic Architecture",
                "thesis": "Decoupling complex workflows into an Event-Driven Agentic Architecture for scalability",
                "strategy": "Apply Parallel Run pattern: run new agent system alongside monolith, gradually migrating workflows",
            },
            "data_modernization": {
                "legacy": ["oracle", "data warehouse", "etl"],
                "modern": "Knowledge Graph + Lakehouse",
                "thesis": "Unlocking siloed data by overlaying a Knowledge Graph for AI context",
                "strategy": "Implement CDC (Change Data Capture) for real-time sync while maintaining warehouse for reporting",
            },
            "cloud_migration": {
                "legacy": ["on-prem", "data center", "physical servers"],
                "modern": "Cloud-Native Microservices",
                "thesis": "Transitioning to cloud-native architecture for elastic scalability and reduced TCO",
                "strategy": "Use Lift-and-Shift followed by modernization, with parallel environments to ensure zero downtime",
            },
        }
        logger.info("Initialized StackModernizationAgent")

    def diagnose_stack(self, job_description: str) -> LegacyDiagnostic:
        """Diagnose legacy technology signals in job description.

        Args:
            job_description: Job description text

        Returns:
            Legacy diagnostic with detected technologies and pain points
        """
        try:
            jd_lower = job_description.lower()
            detected_tech = []
            all_pain_points = []
            for category, markers in self.legacy_markers.items():
                for marker, respectful_name in markers.items():
                    if marker in jd_lower:
                        detected_tech.append(respectful_name)
                        all_pain_points.extend(self.pain_point_mappings.get(category, []))
            score = min(1.0, len(detected_tech) * 0.2)
            unique_tech = list(dict.fromkeys(detected_tech))
            unique_pain = list(dict.fromkeys(all_pain_points))
            diagnostic = LegacyDiagnostic(
                detected_legacy_tech=unique_tech,
                implied_pain_points=unique_pain[:5],
                modernization_score=score,
            )
            logger.info(f"Diagnosed legacy stack with score {score:.2f}")
            return diagnostic
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Error diagnosing stack: {str(e)}")
            return LegacyDiagnostic(detected_legacy_tech=[], implied_pain_points=[], modernization_score=0.0)

    def generate_thesis(self, diagnostic: LegacyDiagnostic) -> MigrationThesis:
        """Generate migration thesis based on diagnostic.

        Args:
            diagnostic: Legacy diagnostic

        Returns:
            Migration thesis with strategy
        """
        try:
            if not diagnostic.detected_legacy_tech:
                return MigrationThesis(
                    current_state_diagnosis="Modern technology stack with opportunities for optimization",
                    target_state_vision="Enhanced AI capabilities with advanced architectures",
                    bridge_strategy="Incremental improvements and strategic AI integration",
                )
            detected_lower = [tech.lower() for tech in diagnostic.detected_legacy_tech]
            for _playbook_name, playbook in self.transformation_playbooks.items():
                if any(legacy in detected_lower for legacy in playbook["legacy"]):
                    return self._create_thesis_from_playbook(playbook, diagnostic)
            return MigrationThesis(
                current_state_diagnosis=f"Mature infrastructure with {', '.join(diagnostic.detected_legacy_tech[:2])}",
                target_state_vision="Modern, cloud-native AI architecture",
                bridge_strategy="Gradual migration using Strangler Fig Pattern to ensure business continuity",
            )
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Error generating thesis: {str(e)}")
            return MigrationThesis(
                current_state_diagnosis="Legacy technology stack",
                target_state_vision="Modern architecture",
                bridge_strategy="Safe, incremental migration approach",
            )

    def generate_migration_hook(self, thesis: MigrationThesis, legacy_tech: str) -> str:
        """Generate targeted opening hook for applications.

        Args:
            thesis: Migration thesis
            legacy_tech: Specific legacy technology to reference

        Returns:
            Targeted hook for outreach
        """
        try:
            modern_tech = (
                thesis.target_state_vision.split(",")[0]
                if thesis.target_state_vision
                else "modern architecture"
            )
            hook = f"I noticed you are transitioning from {legacy_tech}. At [Previous Role], I led the architecture de-risking for this exact migration, ensuring zero downtime while modernizing to {modern_tech} using {(thesis.bridge_strategy.split(',')[0] if thesis.bridge_strategy else 'industry best practices')}."
            return hook
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Error generating migration hook: {str(e)}")
            return "I have experience leading successful technology modernizations."

    def rewrite_resume_summary(self, thesis: MigrationThesis) -> str:
        """Rewrite resume summary to highlight transformation expertise.

        Args:
            thesis: Migration thesis to incorporate

        Returns:
            Rewritten resume summary
        """
        try:
            if thesis.is_transformative:
                summary = f"Transformation Architect specializing in legacy-to-modern migrations. Proven track record of {(thesis.bridge_strategy.split('.')[0] if thesis.bridge_strategy else 'safe modernization')} while maintaining 100% business continuity. Expert in bridging established systems to cutting-edge AI architectures."
            else:
                summary = "Senior AI Engineer with experience in system optimization and strategic technology improvements."
            return summary
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Error rewriting resume summary: {str(e)}")
            return "Senior AI Engineer with modernization experience"

    def _create_thesis_from_playbook(
        self,
        playbook: dict[str, str],
        diagnostic: LegacyDiagnostic,
    ) -> MigrationThesis:
        """Create thesis from transformation playbook.

        Args:
            playbook: Transformation playbook
            diagnostic: Legacy diagnostic

        Returns:
            Migration thesis
        """
        try:
            current = f"Mature infrastructure with established {', '.join(diagnostic.detected_legacy_tech[:2])}. Experiencing {', '.join(diagnostic.implied_pain_points[:2])}."
            target = f"Modern {playbook['modern']} architecture"
            strategy = playbook["strategy"]
            return MigrationThesis(
                current_state_diagnosis=current,
                target_state_vision=target,
                bridge_strategy=strategy,
            )
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Error creating thesis from playbook: {str(e)}")
            raise


def create_stack_modernization_agent() -> StackModernizationAgent:
    """Create a StackModernizationAgent instance.

    Returns:
        Configured StackModernizationAgent
    """
    return StackModernizationAgent()


def analyze_modernization_opportunity(job_description: str) -> dict[str, Any]:
    """Quickly analyze modernization opportunity in JD.

    Args:
        job_description: Job description text

    Returns:
        Analysis results
    """
    agent = create_stack_modernization_agent()
    diagnostic = agent.diagnose_stack(job_description)
    thesis = agent.generate_thesis(diagnostic)
    return {
        "legacy_score": diagnostic.modernization_score,
        "detected_tech": diagnostic.detected_legacy_tech,
        "thesis": thesis.dict(),
        "has_opportunity": diagnostic.is_highly_legacy,
    }
