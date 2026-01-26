"""Onboarding Planner Agent - 30-60-90 Day Roadmap Generator.

This agent generates strategic onboarding roadmaps that demonstrate operational
readiness for leadership roles. It creates a 3-phase plan based on job
description analysis and company maturity.
"""

from __future__ import annotations
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class PlanPhase:
    """A single phase of the onboarding plan."""

    phase_name: str
    primary_objective: str
    key_deliverables: list[str]
    stakeholder_focus: str


@dataclass
class OnboardingPlan:
    """Complete 30-60-90 day onboarding plan."""

    phases: list[PlanPhase]
    risk_assessment: str
    resource_requirements: list[str]


class OnboardingPlannerAgent:
    def __init__(self):
        # Base priorities by company type
        self.startup_priorities = {
            "growth": "Drive revenue growth and customer acquisition",
            "product": "Develop and launch new products or features",
            "team": "Build and manage high-performing teams",
            "tech_debt": "Address technical debt and system scalability",
        }

        self.enterprise_priorities = {
            "governance": "Establish compliance and risk frameworks",
            "integration": "Align with existing systems and processes",
            "stakeholders": "Build consensus across business units",
            "optimization": "Identify and deliver cost efficiencies",
        }

        # Technology-specific audit items
        self.tech_audit_mapping = {
            "kubernetes": "Audit Kubernetes cluster utilization and costs",
            "aws": "Review AWS service usage and optimize spend",
            "gcp": "Analyze GCP resource allocation and performance",
            "azure": "Evaluate Azure deployment patterns",
            "microservices": "Map microservice dependencies and bottlenecks",
            "ml pipelines": "Audit ML pipeline efficiency and reproducibility",
            "data warehouse": "Assess data warehouse performance and costs",
            "llm": "Review LLM deployment and inference costs",
        }

        logger.info("Initialized OnboardingPlannerAgent")

    def generate_plan(
        self, job_description: str, company_maturity: str, role_title: str
    ) -> OnboardingPlan:
        """Generate a 30-60-90 day onboarding plan.

        Args:
            job_description: Job description text
            company_maturity: "startup" or "enterprise"
            role_title: Specific role being targeted

        Returns:
            Complete onboarding plan
        """
        try:
            # Extract priorities from JD
            priorities = self._extract_priorities(job_description, company_maturity)

            # Generate the three phases
            phases = self._generate_phases(
                priorities, job_description, company_maturity, role_title
            )

            # Assess risks and requirements
            risk_assessment = self._assess_risks(company_maturity, role_title)
            resource_requirements = self._identify_resources(phases, company_maturity)

            plan = OnboardingPlan(
                phases=phases,
                risk_assessment=risk_assessment,
                resource_requirements=resource_requirements,
            )

            logger.info(f"Generated onboarding plan for {role_title} at {company_maturity}")

            return plan

        except Exception as e:
            logger.error(f"Error generating onboarding plan: {str(e)}")
            return self._generate_fallback_plan(role_title)

    def tailor_to_role(self, plan: OnboardingPlan, role_title: str) -> OnboardingPlan:
        """Tailor the plan to specific role focus.

        Args:
            plan: Base onboarding plan
            role_title: Target role title

        Returns:
            Tailored onboarding plan
        """
        try:
            role_lower = role_title.lower()

            if "staff engineer" in role_lower or "principal engineer" in role_lower:
                # Focus on technical excellence
                for phase in plan.phases:
                    phase.key_deliverables = [
                        d
                        for d in phase.key_deliverables
                        if "architecture" in d.lower()
                        or "code" in d.lower()
                        or "technical" in d.lower()
                    ] + [
                        "Complete technical debt assessment",
                        "Establish coding standards and review process",
                        "Create system architecture documentation",
                    ][:3]

            elif (
                "head of ai" in role_lower
                or "vp of ai" in role_lower
                or "director of ai" in role_lower
            ):
                # Focus on leadership and strategy
                for phase in plan.phases:
                    phase.key_deliverables = [
                        d
                        for d in phase.key_deliverables
                        if "team" in d.lower() or "strategy" in d.lower() or "budget" in d.lower()
                    ] + [
                        "Develop AI talent acquisition strategy",
                        "Create 2026 AI roadmap and budget proposal",
                        "Establish AI governance framework",
                    ][:3]

            return plan

        except Exception as e:
            logger.error(f"Error tailoring plan to role: {str(e)}")
            return plan

    def render_roadmap_md(self, plan: OnboardingPlan) -> str:
        """Render the plan as a 1-page Markdown document.

        Args:
            plan: Onboarding plan to render

        Returns:
            Formatted Markdown document
        """
        try:
            lines = [
                "# Operational Roadmap: Q1 Objectives",
                "",
                "## Overview",
                "This 90-day roadmap focuses on strategic value delivery while ensuring smooth integration and team alignment.",
                "",
                "---",
                "",
            ]

            # Render each phase
            for i, phase in enumerate(plan.phases, 1):
                lines.extend(
                    [
                        f"## {phase.phase_name}",
                        "",
                        f"**Primary Objective:** {phase.primary_objective}",
                        "",
                        f"**Stakeholder Focus:** {phase.stakeholder_focus}",
                        "",
                        "**Key Deliverables:**",
                        "",
                    ]
                )

                for deliverable in phase.key_deliverables:
                    lines.append(f"- [ ] {deliverable}")

                lines.extend(["", "---", ""])

            # Add risk and resources
            lines.extend(
                ["## Risk Assessment", "", plan.risk_assessment, "", "## Resource Requirements", ""]
            )

            for resource in plan.resource_requirements:
                lines.append(f"- {resource}")

            lines.extend(
                [
                    "",
                    "---",
                    "",
                    "*This roadmap demonstrates operational readiness and strategic thinking for the role.*",
                ]
            )

            return "\n".join(lines)

        except Exception as e:
            logger.error(f"Error rendering roadmap: {str(e)}")
            return "# Onboarding Roadmap\n\nError rendering plan."

    def _extract_priorities(self, job_description: str, company_maturity: str) -> dict[str, str]:
        """Extract priorities from job description.

        Args:
            job_description: Job description text
            company_maturity: Company maturity level

        Returns:
            Dictionary of priorities
        """
        try:
            jd_lower = job_description.lower()

            # Base priorities by company type
            if company_maturity.lower() == "startup":
                priorities = self.startup_priorities.copy()
            else:
                priorities = self.enterprise_priorities.copy()

            # Extract specific priorities from JD
            if "migration" in jd_lower:
                priorities["tech_debt"] = "Audit and plan legacy system migration"
            if "new product" in jd_lower or "product launch" in jd_lower:
                priorities["customer"] = "Voice of customer research and validation"
            if "scale" in jd_lower or "growth" in jd_lower:
                priorities["scaling"] = "Prepare infrastructure and team for scale"
            if "cost" in jd_lower or "budget" in jd_lower:
                priorities["efficiency"] = "Identify and deliver cost optimizations"
            if "team" in jd_lower or "hire" in jd_lower:
                priorities["hiring"] = "Build and structure high-performing team"

            return priorities

        except Exception as e:
            logger.error(f"Error extracting priorities: {str(e)}")
            return {"general": "Execute on core job responsibilities"}

    def _generate_phases(
        self,
        priorities: dict[str, str],
        job_description: str,
        company_maturity: str,
        role_title: str,
    ) -> list[PlanPhase]:
        """Generate the three phases of the plan.

        Args:
            priorities: Extracted priorities
            job_description: Job description text
            company_maturity: Company maturity
            role_title: Role title

        Returns:
            List of three plan phases
        """
        try:
            # Extract specific technologies mentioned
            tech_keywords = self._extract_tech_keywords(job_description)

            # Phase 1: Discovery and Audit (Listen First rule)
            phase1_deliverables = [
                "Complete listening tour with key stakeholders",
                "Audit current tech stack and processes",
            ]

            # Add specific technology audits
            for tech in tech_keywords:
                if tech in self.tech_audit_mapping:
                    phase1_deliverables.append(self.tech_audit_mapping[tech])
                    break  # Add only one specific tech audit

            phase1_deliverables.extend(
                [
                    "Establish baseline metrics and KPIs",
                    "Identify and deliver one quick win (30-day impact)",
                ]
            )

            # Phase 2: Execute and Stabilize
            phase2_deliverables = [
                "Address critical technical debt identified in Phase 1",
                "Structure team roles and responsibilities",
            ]

            if company_maturity.lower() == "startup":
                phase2_deliverables.extend(
                    ["Ship MVP feature or improvement", "Establish development velocity metrics"]
                )
            else:
                phase2_deliverables.extend(
                    [
                        "Launch pilot program or beta feature",
                        "Implement governance and compliance frameworks",
                    ]
                )

            # Phase 3: Strategize and Scale
            phase3_deliverables = [
                "Develop 2026 strategic roadmap",
                "Optimize costs and performance",
            ]

            if "head of" in role_title.lower() or "director" in role_title.lower():
                phase3_deliverables.extend(
                    [
                        "Hand off operational tasks to team leads",
                        "Establish succession planning for key roles",
                    ]
                )
            else:
                phase3_deliverables.extend(
                    [
                        "Document best practices and patterns",
                        "Mentor team members on advanced techniques",
                    ]
                )

            phases = [
                PlanPhase(
                    phase_name="Days 1-30: Discovery & Quick Win",
                    primary_objective="Understand current state and deliver immediate value",
                    key_deliverables=phase1_deliverables,
                    stakeholder_focus="Direct reports, peers, and key business stakeholders",
                ),
                PlanPhase(
                    phase_name="Days 31-60: Execution & Stabilization",
                    primary_objective="Execute on critical priorities and stabilize operations",
                    key_deliverables=phase2_deliverables,
                    stakeholder_focus="Team members and cross-functional partners",
                ),
                PlanPhase(
                    phase_name="Days 61-90: Strategy & Scale",
                    primary_objective="Establish long-term strategy and scale impact",
                    key_deliverables=phase3_deliverables,
                    stakeholder_focus="Leadership team and key decision makers",
                ),
            ]

            return phases

        except Exception as e:
            logger.error(f"Error generating phases: {str(e)}")
            return self._generate_fallback_phases()

    def _extract_tech_keywords(self, job_description: str) -> list[str]:
        """Extract technology keywords from job description.

        Args:
            job_description: Job description text

        Returns:
            List of technology keywords
        """
        try:
            jd_lower = job_description.lower()
            found_tech = []

            for tech in self.tech_audit_mapping.keys():
                if tech in jd_lower:
                    found_tech.append(tech)

            return found_tech

        except Exception as e:
            logger.error(f"Error extracting tech keywords: {str(e)}")
            return []

    def _assess_risks(self, company_maturity: str, role_title: str) -> str:
        """Assess potential risks for the plan.

        Args:
            company_maturity: Company maturity level
            role_title: Role title

        Returns:
            Risk assessment string
        """
        try:
            if company_maturity.lower() == "startup":
                return (
                    "Primary risks include resource constraints and rapid priority changes. "
                    "Mitigation: Maintain flexible roadmap, focus on MVP delivery, "
                    "and establish clear communication channels with leadership."
                )
            else:
                return (
                    "Primary risks include organizational resistance and complex stakeholder landscape. "
                    "Mitigation: Build coalitions, demonstrate quick wins, "
                    "and align initiatives with existing business processes."
                )

        except Exception as e:
            logger.error(f"Error assessing risks: {str(e)}")
            return "Standard onboarding risks apply with appropriate mitigations."

    def _identify_resources(self, phases: list[PlanPhase], company_maturity: str) -> list[str]:
        """Identify resources needed for the plan.

        Args:
            phases: Plan phases
            company_maturity: Company maturity

        Returns:
            List of required resources
        """
        try:
            base_resources = [
                "Access to key systems and documentation",
                "Dedicated time with direct reports and stakeholders",
                "Budget for team building and tools",
            ]

            if company_maturity.lower() == "startup":
                base_resources.extend(
                    [
                        "Authority to make rapid technical decisions",
                        "Support for recruiting key hires",
                    ]
                )
            else:
                base_resources.extend(
                    ["Cross-functional liaison support", "Change management resources"]
                )

            return base_resources

        except Exception as e:
            logger.error(f"Error identifying resources: {str(e)}")
            return ["Standard onboarding resources"]

    def _generate_fallback_plan(self, role_title: str) -> OnboardingPlan:
        """Generate fallback plan when errors occur.

        Args:
            role_title: Role title

        Returns:
            Basic onboarding plan
        """
        return OnboardingPlan(
            phases=self._generate_fallback_phases(),
            risk_assessment="Standard onboarding risks apply",
            resource_requirements=["Basic onboarding resources"],
        )

    def _generate_fallback_phases(self) -> list[PlanPhase]:
        """Generate fallback phases.

        Returns:
            Basic three phases
        """
        return [
            PlanPhase(
                phase_name="Days 1-30: Discovery",
                primary_objective="Understand role and organization",
                key_deliverables=[
                    "Meet with key stakeholders",
                    "Learn current processes",
                    "Identify initial opportunities",
                ],
                stakeholder_focus="Team and immediate stakeholders",
            ),
            PlanPhase(
                phase_name="Days 31-60: Execution",
                primary_objective="Begin delivering value",
                key_deliverables=[
                    "Complete first project",
                    "Build relationships",
                    "Demonstrate competence",
                ],
                stakeholder_focus="Team and peers",
            ),
            PlanPhase(
                phase_name="Days 61-90: Strategy",
                primary_objective="Establish long-term impact",
                key_deliverables=[
                    "Develop strategic plan",
                    "Show measurable results",
                    "Prepare for next quarter",
                ],
                stakeholder_focus="Leadership and stakeholders",
            ),
        ]


# Factory function for easy instantiation
def create_onboarding_planner_agent() -> OnboardingPlannerAgent:
    """Create an OnboardingPlannerAgent instance.

    Returns:
        Configured OnboardingPlannerAgent
    """
    return OnboardingPlannerAgent()


# Convenience function for quick plan generation
def generate_onboarding_plan(job_description: str, company_maturity: str, role_title: str) -> str:
    """Quickly generate an onboarding roadmap.

    Args:
        job_description: Job description text
        company_maturity: Company maturity level
        role_title: Target role

    Returns:
        Rendered Markdown roadmap
    """
    agent = create_onboarding_planner_agent()
    plan = agent.generate_plan(job_description, company_maturity, role_title)
    return agent.render_roadmap_md(plan)
