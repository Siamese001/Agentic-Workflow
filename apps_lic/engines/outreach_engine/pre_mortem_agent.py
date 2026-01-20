"""Pre-Mortem Agent - Strategic Risk Analysis.

This agent critiques proposed plans and identifies potential failure modes
with specific mitigations, demonstrating executive maturity and foresight.
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from pydantic import BaseModel, Field, validator

from .models import LLMResponse


logger = logging.getLogger(__name__)


class RiskCategory(str, Enum):
    """Categories of risks for onboarding plans."""
    CULTURAL_INERTIA = "Cultural Inertia"
    TECHNICAL_DEBT = "Technical Debt"
    RESOURCE_CONSTRAINTS = "Resource Constraints"
    MARKET_TIMING = "Market Timing"
    TEAM_ADOPTION = "Team Adoption"
    STAKEHOLDER_ALIGNMENT = "Stakeholder Alignment"
    EXECUTION_RISK = "Execution Risk"
    EXTERNAL_DEPENDENCIES = "External Dependencies"


class ImpactLevel(str, Enum):
    """Impact levels for identified risks."""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class FailureMode(BaseModel):
    """A potential failure mode with risk assessment."""
    
    risk: str = Field(..., description="Description of the risk")
    category: RiskCategory = Field(..., description="Risk category")
    probability: float = Field(..., ge=0.0, le=1.0, description="Probability of occurrence (0-1)")
    impact: ImpactLevel = Field(..., description="Impact if risk materializes")
    mitigation_strategy: str = Field(..., description="Specific mitigation approach")
    early_warning_signs: List[str] = Field(default_factory=list, description="Early warning indicators")
    owner: Optional[str] = Field(None, description="Who owns this risk")
    
    @property
    def risk_score(self) -> float:
        """Calculate overall risk score (probability x impact weight)."""
        impact_weights = {
            ImpactLevel.LOW: 0.25,
            ImpactLevel.MEDIUM: 0.5,
            ImpactLevel.HIGH: 0.75,
            ImpactLevel.CRITICAL: 1.0
        }
        return self.probability * impact_weights[self.impact]


class PreMortemReport(BaseModel):
    """Complete pre-mortem analysis report."""
    
    plan_summary: str = Field(..., description="Summary of the plan being analyzed")
    top_risks: List[FailureMode] = Field(..., description="Top identified risks")
    overall_risk_score: float = Field(..., ge=0.0, le=1.0, description="Overall plan risk score")
    go_no_go_recommendation: str = Field(..., description="Go/No-Go recommendation")
    critical_success_factors: List[str] = Field(default_factory=list, description="Critical success factors")
    monitoring_plan: Dict[str, str] = Field(default_factory=dict, description="Risk monitoring plan")


class SimpleAgentBase:
    """Simple base class for standalone agents."""
    
    def __init__(self, name: str, model_name: str = "gpt-4"):
        """Initialize the agent.
        
        Args:
            name: Agent name for logging
            model_name: LLM model to use
        """
        self.name = name
        self.model_name = model_name
        logger.info(f"Initialized {self.__class__.__name__}: model={model_name}")


class PreMortemAgent(SimpleAgentBase):
    """Agent that performs pre-mortem analysis on plans."""
    
    def __init__(self, model_name: str = "gpt-4"):
        """Initialize the Pre-Mortem Agent.
        
        Args:
            model_name: LLM model to use for risk analysis
        """
        super().__init__(name="Pre-Mortem Analyzer", model_name=model_name)
        
        # Risk category focus areas
        self.risk_focus_areas = {
            RiskCategory.CULTURAL_INERTIA: [
                "Team resistance to new tools/processes",
                "Existing workflows too entrenched",
                "Lack of buy-in from key stakeholders",
                "Cultural mismatch with new approach"
            ],
            RiskCategory.TECHNICAL_DEBT: [
                "Legacy systems integration challenges",
                "Data quality issues",
                "Scalability bottlenecks",
                "Unexpected technical dependencies"
            ],
            RiskCategory.RESOURCE_CONSTRAINTS: [
                "Insufficient budget for tools/training",
                "Limited team availability",
                "Competing priorities",
                "Skill gaps in team"
            ],
            RiskCategory.TEAM_ADOPTION: [
                "Learning curve too steep",
                "Lack of champions/advocates",
                "Poor change management",
                "Inadequate training"
            ],
            RiskCategory.STAKEHOLDER_ALIGNMENT: [
                "Misaligned expectations",
                "Conflicting priorities",
                "Lack of executive sponsorship",
                "Unclear success metrics"
            ],
            RiskCategory.EXECUTION_RISK: [
                "Aggressive timeline",
                "Complex dependencies",
                "Unclear requirements",
                "Scope creep"
            ],
            RiskCategory.EXTERNAL_DEPENDENCIES: [
                "Vendor reliability",
                "API changes",
                "Market shifts",
                "Regulatory changes"
            ]
        }
    
    async def analyze_plan(self, plan_text: str, plan_type: str = "onboarding") -> PreMortemReport:
        """Perform pre-mortem analysis on a plan.
        
        Args:
            plan_text: The plan to analyze
            plan_type: Type of plan (onboarding, migration, project, etc.)
            
        Returns:
            Complete pre-mortem report
        """
        logger.info(f"Performing pre-mortem analysis on {plan_type} plan")
        
        # Identify failure modes
        failure_modes = await self._identify_failure_modes(plan_text, plan_type)
        
        # Generate mitigations for each failure mode
        for failure in failure_modes:
            failure.mitigation_strategy = self._generate_mitigation(failure, plan_text)
            failure.early_warning_signs = self._identify_warning_signs(failure)
        
        # Select top risks
        top_risks = sorted(failure_modes, key=lambda x: x.risk_score, reverse=True)[:5]
        
        # Calculate overall risk score
        overall_risk = self._calculate_overall_risk(top_risks)
        
        # Generate recommendation
        recommendation = self._generate_recommendation(overall_risk, top_risks)
        
        # Identify critical success factors
        success_factors = self._identify_success_factors(plan_text, top_risks)
        
        # Create monitoring plan
        monitoring = self._create_monitoring_plan(top_risks)
        
        return PreMortemReport(
            plan_summary=self._summarize_plan(plan_text),
            top_risks=top_risks,
            overall_risk_score=overall_risk,
            go_no_go_recommendation=recommendation,
            critical_success_factors=success_factors,
            monitoring_plan=monitoring
        )
    
    async def _identify_failure_modes(self, plan_text: str, plan_type: str) -> List[FailureMode]:
        """Identify potential failure modes using LLM.
        
        Args:
            plan_text: Plan to analyze
            plan_type: Type of plan
            
        Returns:
            List of identified failure modes
        """
        prompt = f"""
        You are a cynical Chief Risk Officer reviewing a {plan_type} plan. 
        Assume this plan FAILS in 6 months. List the top 7 reasons why it might fail.
        
        Plan:
        {plan_text[:2000]}
        
        For each failure mode, provide:
        1. Risk description (what could go wrong)
        2. Category (Cultural Inertia, Technical Debt, Resource Constraints, Team Adoption, 
                    Stakeholder Alignment, Execution Risk, External Dependencies)
        3. Probability (0.0-1.0)
        4. Impact (Low, Medium, High, Critical)
        
        Format as JSON:
        {{
            "failure_modes": [
                {{
                    "risk": "specific risk description",
                    "category": "category_name",
                    "probability": 0.7,
                    "impact": "High"
                }}
            ]
        }}
        
        Be realistic but not fatalistic. Focus on solvable challenges.
        """
        
        try:
            response = await self._call_llm(prompt, temperature=0.2)
            import json
            result = json.loads(response.content.strip())
            
            failure_modes = []
            for fm in result.get("failure_modes", []):
                try:
                    failure = FailureMode(
                        risk=fm["risk"],
                        category=RiskCategory(fm["category"]),
                        probability=fm["probability"],
                        impact=ImpactLevel(fm["impact"]),
                        mitigation_strategy=""  # Will be filled later
                    )
                    failure_modes.append(failure)
                except (KeyError, ValueError) as e:
                    logger.warning(f"Skipping invalid failure mode: {e}")
                    continue
            
            return failure_modes
            
        except Exception as e:
            logger.error(f"Failed to identify failure modes: {e}")
            # Return generic failure modes
            return [
                FailureMode(
                    risk="Team adoption challenges",
                    category=RiskCategory.TEAM_ADOPTION,
                    probability=0.6,
                    impact=ImpactLevel.HIGH,
                    mitigation_strategy=""
                )
            ]
    
    async def _generate_mitigation(self, failure: FailureMode, plan_text: str) -> str:
        """Generate specific mitigation strategy for a failure mode.
        
        Args:
            failure: The failure mode to mitigate
            plan_text: Original plan for context
            
        Returns:
            Mitigation strategy
        """
        prompt = f"""
        For this risk, provide a specific, actionable mitigation strategy:
        
        Risk: {failure.risk}
        Category: {failure.category}
        Probability: {failure.probability}
        Impact: {failure.impact}
        
        Plan context: {plan_text[:500]}
        
        Provide a concrete mitigation that:
        1. Addresses the root cause
        2. Is practical to implement
        3. Has clear success criteria
        4. Can be executed within the plan timeline
        
        Keep it to 2-3 sentences maximum.
        """
        
        try:
            response = await self._call_llm(prompt, temperature=0.3)
            return response.content.strip()
        except Exception as e:
            logger.error(f"Failed to generate mitigation: {e}")
            return "Implement regular check-ins and monitoring to address early signs of this risk."
    
    def _identify_warning_signs(self, failure: FailureMode) -> List[str]:
        """Identify early warning signs for a failure mode.
        
        Args:
            failure: The failure mode to analyze
            
        Returns:
            List of early warning signs
        """
        # Generic warning signs by category
        warning_signs_map = {
            RiskCategory.CULTURAL_INERTIA: [
                "Low attendance at training sessions",
                "Continued use of old processes",
                "Negative feedback in team surveys"
            ],
            RiskCategory.TECHNICAL_DEBT: [
                "Increasing system latency",
                "Rise in bug reports",
                "Frequent system outages"
            ],
            RiskCategory.RESOURCE_CONSTRAINTS: [
                "Budget overruns in early phases",
                "Team member burnout signs",
                "Missed deadlines"
            ],
            RiskCategory.TEAM_ADOPTION: [
                "Low tool usage metrics",
                "Increase in support tickets",
                "Workaround usage increasing"
            ],
            RiskCategory.STAKEHOLDER_ALIGNMENT: [
                "Conflicting stakeholder requests",
                "Scope changes mid-project",
                "Reduced executive engagement"
            ],
            RiskCategory.EXECUTION_RISK: [
                "Missing milestones",
                "Dependency delays",
                "Quality issues in deliverables"
            ],
            RiskCategory.EXTERNAL_DEPENDENCIES: [
                "Vendor service degradation",
                "API response time increases",
                "Regulatory announcements"
            ]
        }
        
        return warning_signs_map.get(failure.category, ["Unexpected deviations from plan"])
    
    def _calculate_overall_risk(self, risks: List[FailureMode]) -> float:
        """Calculate overall risk score for the plan.
        
        Args:
            risks: List of failure modes
            
        Returns:
            Overall risk score (0-1)
        """
        if not risks:
            return 0.0
        
        # Weighted average of top risks
        total_weight = sum(2 ** i for i in range(len(risks)))  # Exponential weighting
        weighted_score = sum(risk.risk_score * (2 ** i) for i, risk in enumerate(risks))
        
        return min(1.0, weighted_score / total_weight * 2)  # Normalize and amplify
    
    def _generate_recommendation(self, risk_score: float, risks: List[FailureMode]) -> str:
        """Generate go/no-go recommendation.
        
        Args:
            risk_score: Overall risk score
            risks: Top risks identified
            
        Returns:
            Recommendation string
        """
        critical_risks = [r for r in risks if r.impact == ImpactLevel.CRITICAL and r.probability > 0.5]
        
        if critical_risks:
            return "NO-GO: Address critical risks before proceeding"
        elif risk_score > 0.7:
            return "CONDITIONAL: Proceed with risk mitigation plan"
        elif risk_score > 0.4:
            return "GO: Monitor risks closely"
        else:
            return "GO: Low risk, proceed as planned"
    
    def _identify_success_factors(self, plan_text: str, risks: List[FailureMode]) -> List[str]:
        """Identify critical success factors.
        
        Args:
            plan_text: Original plan
            risks: Identified risks
            
        Returns:
            List of critical success factors
        """
        factors = []
        
        # Based on risks, identify corresponding success factors
        risk_categories = set(r.category for r in risks)
        
        if RiskCategory.TEAM_ADOPTION in risk_categories:
            factors.append("Strong change management and team buy-in")
        
        if RiskCategory.STAKEHOLDER_ALIGNMENT in risk_categories:
            factors.append("Clear executive sponsorship and aligned expectations")
        
        if RiskCategory.TECHNICAL_DEBT in risk_categories:
            factors.append("Thorough technical assessment and phased migration")
        
        if RiskCategory.RESOURCE_CONSTRAINTS in risk_categories:
            factors.append("Adequate resource allocation and realistic timeline")
        
        # Add generic factors
        factors.extend([
            "Clear communication plan",
            "Defined success metrics",
            "Regular progress reviews"
        ])
        
        return factors[:5]  # Top 5 factors
    
    def _create_monitoring_plan(self, risks: List[FailureMode]) -> Dict[str, str]:
        """Create risk monitoring plan.
        
        Args:
            risks: Risks to monitor
            
        Returns:
            Monitoring plan mapping risks to monitoring actions
        """
        monitoring = {}
        
        for risk in risks[:3]:  # Top 3 risks
            monitoring[risk.risk] = f"Weekly check-ins, track {risk.early_warning_signs[0] if risk.early_warning_signs else 'key metrics'}"
        
        return monitoring
    
    def _summarize_plan(self, plan_text: str) -> str:
        """Create brief summary of the plan.
        
        Args:
            plan_text: Plan to summarize
            
        Returns:
            Plan summary
        """
        # Simple truncation for now
        return plan_text[:200] + "..." if len(plan_text) > 200 else plan_text
    
    def render_risk_assessment(self, report: PreMortemReport) -> str:
        """Render pre-mortem report as Markdown.
        
        Args:
            report: Pre-mortem report to render
            
        Returns:
            Formatted Markdown string
        """
        lines = [
            "## Strategic Risk Assessment (Pre-Mortem)",
            "",
            f"**Overall Risk Score:** {report.overall_risk_score:.1%}",
            f"**Recommendation:** {report.go_no_go_recommendation}",
            "",
            "### Top Risks & Mitigations",
            "",
            "| Risk | Category | Probability | Impact | Mitigation |",
            "|------|----------|-------------|---------|------------|"
        ]
        
        for risk in report.top_risks:
            mitigation = risk.mitigation_strategy[:50] + "..." if len(risk.mitigation_strategy) > 50 else risk.mitigation_strategy
            lines.append(
                f"| {risk.risk[:40]}... | {risk.category} | {risk.probability:.0%} | {risk.impact} | {mitigation} |"
            )
        
        lines.extend([
            "",
            "### Critical Success Factors",
            ""
        ])
        
        for factor in report.critical_success_factors:
            lines.append(f"- {factor}")
        
        lines.extend([
            "",
            "### Risk Monitoring Plan",
            ""
        ])
        
        for risk, monitoring in report.monitoring_plan.items():
            lines.append(f"- **{risk}**: {monitoring}")
        
        return "\n".join(lines)
    
    async def _call_llm(self, prompt: str, temperature: float = 0.3) -> LLMResponse:
        """Call the LLM with the given prompt.
        
        Args:
            prompt: Prompt to send to LLM
            temperature: Sampling temperature
            
        Returns:
            LLM response
        """
        try:
            # Import here to avoid circular imports
            from .multi_provider_clients import get_client, Provider
            
            # Get Anthropic client
            client = get_client(Provider.ANTHROPIC)
            
            # Call LLM
            response = await client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            
            class LLMResponseImpl:
                def __init__(self, content: str):
                    self.content = content
            
            return LLMResponseImpl(response.content[0].text)
            
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            # Return fallback response
            class LLMResponseImpl:
                def __init__(self, content: str):
                    self.content = content
            
            return LLMResponseImpl('{"failure_modes": []}')
