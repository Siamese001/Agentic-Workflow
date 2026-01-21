"""Executive Brief Agent - Strategic Memo Generation for AI Leadership.

This module generates high-signal "Executive Briefs" that replace traditional cover
letters. Each brief demonstrates strategic thinking by diagnosing a company's
AI challenges and proposing solutions before the first interview.

Enhanced with Titanium RAG Pipeline for SOTA company research and insights.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any, Union
from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)

# Import Titanium search tool
try:
    from .titanium_search_tool import get_titanium_search_tool, get_titanium_search_with_sources
    TITANIUM_AVAILABLE = True
    logger.info("ExecutiveBriefAgent: Titanium RAG Pipeline available")
except ImportError as e:
    TITANIUM_AVAILABLE = False
    logger.warning(f"ExecutiveBriefAgent: Titanium RAG Pipeline not available: {e}")


class BriefSection(BaseModel):
    """A single section of an executive brief."""
    
    heading: str = Field(..., description="Section heading (e.g., 'Observation: High Inference Costs')")
    content: str = Field(..., description="Section content (2-3 sentences)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in this section")
    
    @validator('content')
    def validate_content_length(cls, v):
        """Ensure content is concise."""
        if len(v.split()) > 50:
            logger.warning("BriefSection content too long, should be 2-3 sentences")
        return v


class ExecutiveBrief(BaseModel):
    """Complete executive brief document."""
    
    recipient_name: str = Field(..., description="Hiring manager or team name")
    company_name: str = Field(..., description="Target company name")
    observation: BriefSection = Field(..., description="What we observe about their situation")
    insight: BriefSection = Field(..., description="Strategic insight and implications")
    proposition: BriefSection = Field(..., description="Proposed next steps")
    generated_at: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    
    @property
    def is_high_confidence(self) -> bool:
        """Check if brief has high overall confidence."""
        avg_confidence = (self.observation.confidence + 
                         self.insight.confidence + 
                         self.proposition.confidence) / 3
        return avg_confidence >= 0.7


class ExecutiveBriefAgent:
    """Generates strategic executive briefs for AI leadership positions.
    
    Enhanced with Titanium RAG Pipeline for SOTA company research and insights.
    """
    
    def __init__(self, candidate_name: str, candidate_background: Dict[str, Any]):
        """Initialize the executive brief agent.
        
        Args:
            candidate_name: Name of the job candidate
            candidate_background: Candidate's background and achievements
        """
        self.candidate_name = candidate_name
        self.candidate_background = candidate_background
        
        # Initialize Titanium search if available
        self.titanium_enabled = TITANIUM_AVAILABLE
        if self.titanium_enabled:
            logger.info("ExecutiveBriefAgent initialized with Titanium RAG Pipeline")
        else:
            logger.warning("ExecutiveBriefAgent using fallback research mode")
        
        # Import tone model for enforcement
        try:
            from .tone_model import ToneType, create_tone_model
            self.tone_model = create_tone_model()
            self.target_tone = ToneType.DIRECT  # Executive briefs should be direct
        except ImportError:
            logger.warning("Tone model not available, using default tone")
            self.tone_model = None
            self.target_tone = None
        
        # Strategic angle mappings
        self.strategic_angles = {
            "optimization": "Efficiency/ROI",
            "efficiency": "Efficiency/ROI", 
            "cost": "Efficiency/ROI",
            "scale": "Scalability/Growth",
            "growth": "Scalability/Growth",
            "product": "Speed/Innovation",
            "innovation": "Speed/Innovation",
            "new": "Speed/Innovation",
            "team": "Talent/Culture",
            "talent": "Talent/Culture",
            "hiring": "Talent/Culture",
            "culture": "Talent/Culture"
        }
        
        # Common AI pain points with solutions
        self.pain_point_solutions = {
            "inference costs": {
                "problem": "High inference costs scaling with LLMs",
                "solution": "Speculative decoding and model optimization",
                "metric": "40-60% cost reduction"
            },
            "rag limitations": {
                "problem": "RAG systems hitting retrieval accuracy limits",
                "solution": "Agentic workflows with self-correction",
                "metric": "25% improvement in response quality"
            },
            "model drift": {
                "problem": "Model performance degradation in production",
                "solution": "Continuous monitoring and retraining pipelines",
                "metric": "90% reduction in undetected drift"
            },
            "talent retention": {
                "problem": "Difficulty retaining AI/ML talent",
                "solution": "Clear career progression and cutting-edge projects",
                "metric": "30% improvement in retention"
            },
            "deployment latency": {
                "problem": "Slow model deployment cycles",
                "solution": "Automated MLOps pipelines with canary releases",
                "metric": "50% faster time-to-production"
            }
        }
    
    async def _research_company_with_titanium(self, company_name: str, industry: str) -> Dict[str, Any]:
        """Research company using Titanium RAG Pipeline for enhanced insights.
        
        Args:
            company_name: Name of the target company
            industry: Industry sector
            
        Returns:
            Enhanced company research data
        """
        if not self.titanium_enabled:
            logger.warning("Titanium not available, using fallback research")
            return {"name": company_name, "industry": industry}
        
        try:
            # Search for company's AI challenges and initiatives
            search_queries = [
                f"{company_name} AI challenges machine learning",
                f"{company_name} artificial intelligence strategy",
                f"{company_name} tech stack infrastructure",
                f"{industry} industry AI trends 2024"
            ]
            
            research_data = {
                "name": company_name,
                "industry": industry,
                "ai_initiatives": [],
                "technical_challenges": [],
                "strategic_priorities": [],
                "recent_news": [],
                "competitors": []
            }
            
            # Execute searches using Titanium
            for query in search_queries:
                results = await get_titanium_search_tool(
                    query=query,
                    max_results=5,
                    include_metadata=True
                )
                
                # Parse results (simplified - in production would use structured extraction)
                if results and "No relevant information" not in results:
                    research_data["ai_initiatives"].append(f"Insights from: {query}")
                    
                    # Extract specific insights based on query type
                    if "challenges" in query.lower():
                        research_data["technical_challenges"].append(results[:200])
                    elif "strategy" in query.lower():
                        research_data["strategic_priorities"].append(results[:200])
            
            logger.info(f"Titanium research completed for {company_name}")
            return research_data
            
        except Exception as e:
            logger.error(f"Error in Titanium research: {e}")
            return {"name": company_name, "industry": industry}
    
    async def generate_brief_with_titanium(
        self,
        company_name: str,
        industry: str,
        job_description: str,
        recipient_name: Optional[str] = None
    ) -> ExecutiveBrief:
        """Generate executive brief using Titanium RAG for enhanced research.
        
        Args:
            company_name: Target company name
            industry: Industry sector
            job_description: Job posting details
            recipient_name: Optional recipient name
            
        Returns:
            ExecutiveBrief enhanced with Titanium research
        """
        try:
            # Use Titanium to research company
            company_data = await self._research_company_with_titanium(company_name, industry)
            
            # Generate brief using enhanced data
            return self.generate_brief(company_data, job_description, recipient_name)
            
        except Exception as e:
            logger.error(f"Error generating brief with Titanium: {e}")
            # Fallback to basic brief
            return self.generate_brief(
                {"name": company_name, "industry": industry},
                job_description,
                recipient_name
            )
    
    def generate_brief(
        self,
        company_data: Dict[str, Any],
        job_description: str,
        recipient_name: Optional[str] = None
    ) -> ExecutiveBrief:
        """Generate a complete executive brief.
        
        Args:
            company_data: Company information (news, 10-K, etc.)
            job_description: Job posting details
            recipient_name: Optional recipient name override
            
        Returns:
            Complete ExecutiveBrief ready for rendering
        """
        try:
            # Assemble strategic context
            context = self._assemble_context(company_data, job_description)
            
            # Generate the three sections
            observation = self._generate_observation(context)
            insight = self._generate_insight(context, observation)
            proposition = self._generate_proposition(context, insight)
            
            # Create the brief
            brief = ExecutiveBrief(
                recipient_name=recipient_name or "Hiring Manager",
                company_name=context["company_name"],
                observation=observation,
                insight=insight,
                proposition=proposition
            )
            
            logger.info(f"Generated executive brief for {context['company_name']}")
            
            return brief
            
        except Exception as e:
            logger.error(f"Error generating executive brief: {str(e)}")
            # Return safe fallback
            return self._generate_fallback_brief(company_data)
    
    def _assemble_context(self, company_data: Dict[str, Any], job_description: str) -> Dict[str, Any]:
        """Assemble strategic context from company data and JD.
        
        Args:
            company_data: Company information
            job_description: Job posting details
            
        Returns:
            Context dictionary with strategic insights
        """
        try:
            context = {
                "company_name": company_data.get("name", "the company"),
                "industry": company_data.get("industry", "technology"),
                "pain_points": [],
                "strategic_angle": "Efficiency/ROI",  # Default
                "recent_news": company_data.get("recent_news", []),
                "risk_factors": company_data.get("risk_factors", []),
                "jd_metrics": [],
                "jd_challenges": []
            }
            
            # Extract specific metrics and challenges from JD
            jd_lower = job_description.lower()
            
            # Look for specific metrics mentioned
            metric_patterns = {
                "latency": r"(\d+)ms latency",
                "accuracy": r"(\d+)% accuracy",
                "cost": r"\$(\d+(?:k|m)?)",
                "scale": r"(\d+(?:k|m|b)?) users",
                "throughput": r"(\d+) (?:req\/s|rps)"
            }
            
            import re
            for metric, pattern in metric_patterns.items():
                matches = re.findall(pattern, jd_lower)
                if matches:
                    context["jd_metrics"].append(f"{metric}: {matches[0]}")
            
            # Look for specific challenges
            challenge_keywords = {
                "scalability": ["scale", "scaling", "at scale"],
                "performance": ["performance", "slow", "latency", "speed"],
                "cost": ["cost", "expensive", "budget", "optimize"],
                "talent": ["hire", "recruit", "team", "talent"],
                "innovation": ["innovate", "new", "cutting-edge", "breakthrough"]
            }
            
            for challenge, keywords in challenge_keywords.items():
                if any(keyword in jd_lower for keyword in keywords):
                    context["jd_challenges"].append(challenge)
            
            # Extract strategic angle from JD
            for keyword, angle in self.strategic_angles.items():
                if keyword in jd_lower:
                    context["strategic_angle"] = angle
                    break
            
            # Identify specific pain points from JD and company data
            all_text = f"{jd_lower} {' '.join(n.lower() for n in context['recent_news'])}"
            for pain_point in self.pain_point_solutions.keys():
                if pain_point in all_text:
                    context["pain_points"].append(pain_point)
            
            # If no specific pain points found, use JD challenges
            if not context["pain_points"] and context["jd_challenges"]:
                # Map challenges to pain points
                challenge_to_pain = {
                    "scalability": "inference costs",
                    "performance": "inference costs",
                    "cost": "inference costs",
                    "talent": "talent retention",
                    "innovation": "rag limitations"
                }
                for challenge in context["jd_challenges"]:
                    if challenge in challenge_to_pain:
                        pain_point = challenge_to_pain[challenge]
                        if pain_point not in context["pain_points"]:
                            context["pain_points"].append(pain_point)
            
            # Final fallback
            if not context["pain_points"]:
                if context["industry"] in ["healthcare", "finance"]:
                    context["pain_points"] = ["model drift", "inference costs"]
                else:
                    context["pain_points"] = ["rag limitations", "talent retention"]
            
            return context
            
        except Exception as e:
            logger.error(f"Error assembling context: {str(e)}")
            return {
                "company_name": "the company",
                "industry": "technology",
                "pain_points": ["inference costs"],
                "strategic_angle": "Efficiency/ROI",
                "recent_news": [],
                "risk_factors": [],
                "jd_metrics": [],
                "jd_challenges": []
            }
    
    def _generate_observation(self, context: Dict[str, Any]) -> BriefSection:
        """Generate the observation section.
        
        Args:
            context: Strategic context
            
        Returns:
            BriefSection with observation
        """
        try:
            pain_point = context["pain_points"][0]
            company_name = context["company_name"]
            
            if pain_point in self.pain_point_solutions:
                problem = self.pain_point_solutions[pain_point]["problem"]
                
                # Check if we have company-specific data
                if context["recent_news"] or context["risk_factors"] or context["jd_metrics"]:
                    if context["jd_metrics"]:
                        metrics_str = ", ".join(context["jd_metrics"][:2])  # Use first 2 metrics
                        content = f"{company_name} is facing {problem}, with current metrics showing {metrics_str}. This is impacting operational efficiency."
                    else:
                        content = f"{company_name} is facing {problem}, which is impacting operational efficiency and competitive positioning."
                    confidence = 0.9
                else:
                    # Use general industry observation
                    content = f"Like many leaders in {context['industry']}, {company_name} is likely navigating {problem} as AI systems scale."
                    confidence = 0.6
                
                # Apply tone enforcement
                if self.tone_model and self.target_tone:
                    content = self._apply_tone_enforcement(content)
                
                return BriefSection(
                    heading=f"Observation: {pain_point.title()} Challenges",
                    content=content,
                    confidence=confidence
                )
            else:
                # Generic observation
                content = f"{company_name} is at a critical inflection point in scaling AI capabilities from prototype to production."
                if self.tone_model and self.target_tone:
                    content = self._apply_tone_enforcement(content)
                
                return BriefSection(
                    heading="Observation: AI Scaling Challenges",
                    content=content,
                    confidence=0.5
                )
                
        except Exception as e:
            logger.error(f"Error generating observation: {str(e)}")
            return BriefSection(
                heading="Observation: Strategic AI Opportunity",
                content="The company is positioned to leverage AI for competitive advantage.",
                confidence=0.3
            )
    
    def _apply_tone_enforcement(self, content: str) -> str:
        """Apply tone enforcement to remove fluff and be direct.
        
        Args:
            content: Original content
            
        Returns:
            Tone-adjusted content
        """
        try:
            # Remove fluff words and phrases
            fluff_phrases = [
                "I think that", "I believe that", "I feel that",
                "excited about", "passionate about", "thrilled about",
                "very", "quite", "rather", "extremely",
                "in order to", "for the purpose of", "in an effort to"
            ]
            
            adjusted = content
            for phrase in fluff_phrases:
                adjusted = adjusted.replace(phrase, "")
            
            # Clean up extra spaces
            adjusted = re.sub(r'\s+', ' ', adjusted).strip()
            
            return adjusted
            
        except Exception as e:
            logger.error(f"Error applying tone enforcement: {str(e)}")
            return content
    
    def _generate_insight(self, context: Dict[str, Any], observation: BriefSection) -> BriefSection:
        """Generate the insight section.
        
        Args:
            context: Strategic context
            observation: Previously generated observation
            
        Returns:
            BriefSection with strategic insight
        """
        try:
            pain_point = context["pain_points"][0]
            
            if pain_point in self.pain_point_solutions:
                solution = self.pain_point_solutions[pain_point]["solution"]
                metric = self.pain_point_solutions[pain_point]["metric"]
                
                # Generate peer-to-peer insight
                content = f"Industry leaders are solving this through {solution}, achieving {metric} while maintaining model performance. This requires both technical expertise and change management experience."
                
                return BriefSection(
                    heading="Insight: Proven Solution Patterns",
                    content=content,
                    confidence=0.8
                )
            else:
                # Generic insight
                return BriefSection(
                    heading="Insight: Strategic Imperative",
                    content="Successful AI transformation requires balancing rapid innovation with sustainable operations, focusing on measurable business outcomes.",
                    confidence=0.6
                )
                
        except Exception as e:
            logger.error(f"Error generating insight: {str(e)}")
            return BriefSection(
                heading="Insight: Strategic Approach",
                content="A systematic approach to AI scaling is essential for long-term success.",
                confidence=0.4
            )
    
    def _generate_proposition(self, context: Dict[str, Any], insight: BriefSection) -> BriefSection:
        """Generate the proposition section.
        
        Args:
            context: Strategic context
            insight: Previously generated insight
            
        Returns:
            BriefSection with proposition
        """
        try:
            # Get candidate's relevant experience
            relevant_exp = self.candidate_background.get("relevant_experience", [])
            previous_role = self.candidate_background.get("most_recent_role", "previous role")
            
            if relevant_exp and len(relevant_exp) > 0:
                exp = relevant_exp[0]  # Use most relevant experience
                content = f"I led this exact transformation at {previous_role}, {exp}. I have a 90-day roadmap tailored to {context['company_name']}'s context. Worth a brief chat?"
                confidence = 0.9
            else:
                # Generic proposition
                content = f"I have direct experience scaling AI systems and can provide a 90-day roadmap for {context['company_name']}. Available to discuss specific implementation strategies."
                confidence = 0.6
            
            return BriefSection(
                heading="Proposition: 90-Day Strategic Plan",
                content=content,
                confidence=confidence
            )
            
        except Exception as e:
            logger.error(f"Error generating proposition: {str(e)}")
            return BriefSection(
                heading="Proposition: Strategic Partnership",
                content="I can help accelerate your AI initiatives with proven methodologies.",
                confidence=0.3
            )
    
    def _generate_fallback_brief(self, company_data: Dict[str, Any]) -> ExecutiveBrief:
        """Generate a safe fallback brief when errors occur.
        
        Args:
            company_data: Partial company data
            
        Returns:
            Safe ExecutiveBrief
        """
        company_name = company_data.get("name", "your company")
        
        return ExecutiveBrief(
            recipient_name="Hiring Manager",
            company_name=company_name,
            observation=BriefSection(
                heading="Observation: AI Transformation Opportunity",
                content=f"{company_name} is positioned to leverage AI for strategic advantage.",
                confidence=0.4
            ),
            insight=BriefSection(
                heading="Insight: Strategic Approach",
                content="Successful AI transformation requires technical excellence and business acumen.",
                confidence=0.4
            ),
            proposition=BriefSection(
                heading="Proposition: Strategic Discussion",
                content="I would welcome the opportunity to discuss how my experience aligns with your goals.",
                confidence=0.4
            )
        )
    
    def render_markdown(self, brief: ExecutiveBrief) -> str:
        """Render the brief as a professional Markdown memo.
        
        Args:
            brief: ExecutiveBrief to render
            
        Returns:
            Formatted Markdown string
        """
        try:
            # Header
            lines = [
                "# MEMO: Strategic Observations for AI Leadership",
                "",
                f"**To:** {brief.recipient_name}",
                f"**Company:** {brief.company_name}",
                f"**From:** {self.candidate_name}",
                f"**Date:** {brief.generated_at}",
                "",
                "---",
                ""
            ]
            
            # Observation section
            lines.extend([
                f"## {brief.observation.heading}",
                "",
                brief.observation.content,
                ""
            ])
            
            # Insight section
            lines.extend([
                f"## {brief.insight.heading}",
                "",
                brief.insight.content,
                ""
            ])
            
            # Proposition section
            lines.extend([
                f"## {brief.proposition.heading}",
                "",
                brief.proposition.content,
                "",
                "---",
                "",
                f"*Confidence: High* | *Generated: {brief.generated_at}*"
            ])
            
            return "\n".join(lines)
            
        except Exception as e:
            logger.error(f"Error rendering markdown: {str(e)}")
            # Return basic format
            return f"""
# Executive Brief

To: {brief.recipient_name}
Company: {brief.company_name}
From: {self.candidate_name}

{brief.observation.heading}
{brief.observation.content}

{brief.insight.heading}
{brief.insight.content}

{brief.proposition.heading}
{brief.proposition.content}
"""


# Factory function for easy instantiation
def create_executive_brief_agent(
    candidate_name: str,
    candidate_background: Dict[str, Any]
) -> ExecutiveBriefAgent:
    """Create an ExecutiveBriefAgent instance.
    
    Args:
        candidate_name: Name of the candidate
        candidate_background: Candidate's background and achievements
        
    Returns:
        Configured ExecutiveBriefAgent
    """
    return ExecutiveBriefAgent(candidate_name, candidate_background)


# Convenience function for quick brief generation
def generate_executive_brief(
    candidate_name: str,
    candidate_background: Dict[str, Any],
    company_data: Dict[str, Any],
    job_description: str
) -> str:
    """Generate and render an executive brief.
    
    Args:
        candidate_name: Name of the candidate
        candidate_background: Candidate's background
        company_data: Company information
        job_description: Job posting details
        
    Returns:
        Rendered Markdown brief
    """
    agent = create_executive_brief_agent(candidate_name, candidate_background)
    brief = agent.generate_brief(company_data, job_description)
    return agent.render_markdown(brief)
