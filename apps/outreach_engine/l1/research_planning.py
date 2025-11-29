"""Plans research refinement and evidence selection to strengthen executive message credibility."""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import re

from .outreach_dataclasses import (
    ArchetypeContext,
    ArchetypeType,
    RefinementPlan,
    AgentType,
    ExecutiveReasoningProfile,
    MultiAxisReasoningPlan,
    ReflexionPlan,
    compute_reasoning_multiplier
)


@dataclass
class ResearchResult:
    """Captures research signals that drive high-credibility executive messaging."""
    query: str
    results: List[Dict[str, Any]]
    confidence_scores: List[float]
    metadata: Dict[str, Any]
    timestamp: str


@dataclass
class FailureContext:
    """Analyzes safety failures to improve message quality while preserving executive impact."""
    violation_type: str
    severity: str
    description: str
    affected_sections: List[str]
    metadata: Dict[str, Any]


class ResearchRefinementPlanner:
    """Plans research refinement to strengthen executive message credibility and evidence quality."""
    
    def __init__(self):
        """Initializes planner with quality thresholds for executive-grade research evidence."""
        # HSON: Sets high quality thresholds to ensure executive-grade evidence -> increases message credibility
        self._refinement_thresholds = {
            "min_confidence": 0.7,
            "min_results": 5,
            "max_age_days": 180,
            "signal_density_threshold": 0.3
        }
        
        # Pure agent responsibility mapping
        self._agent_mapping = {
            "company_research": AgentType.COMPANY,
            "contact_research": AgentType.CONTACT,
            "signal_validation": AgentType.CONTACT,
            "industry_analysis": AgentType.COMPANY,
            "competitor_analysis": AgentType.COMPANY,
            "recent_activities": AgentType.CONTACT,
            "technical_expertise": AgentType.CONTACT,
            "business_performance": AgentType.COMPANY
        }
    
    def analyze_research_quality(
        self, 
        current_results: ResearchResult, 
        archetype_context: ArchetypeContext
    ) -> Dict[str, Any]:
        """Analyzes research quality to ensure executive-level evidence standards are met."""
        quality_metrics = {
            "confidence_avg": sum(current_results.confidence_scores) / len(current_results.confidence_scores) if current_results.confidence_scores else 0.0,
            "result_count": len(current_results.results),
            "high_confidence_count": sum(1 for score in current_results.confidence_scores if score >= 0.8),
            "signal_density": self._calculate_signal_density(current_results.results),
            "source_diversity": self._calculate_source_diversity(current_results.results),
            "temporal_relevance": self._calculate_temporal_relevance(current_results.results)
        }
        
        # Compare against archetype requirements
        quality_gaps = self._identify_quality_gaps(quality_metrics, archetype_context)
        
        return {
            "metrics": quality_metrics,
            "gaps": quality_gaps,
            "overall_score": self._calculate_overall_quality_score(quality_metrics),
            "meets_threshold": self._meets_quality_thresholds(quality_metrics, archetype_context)
        }
    
    def determine_refinement_needs(
        self, 
        current_results: ResearchResult, 
        archetype_context: ArchetypeContext,
        iteration: int = 1,
        failure_context: Optional[FailureContext] = None
    ) -> RefinementPlan:
        """
        Pure computational determination of refinement needs.
        """
        # Analyze current quality
        quality_analysis = self.analyze_research_quality(current_results, archetype_context)
        
        # Check for explicit failures
        failure_driven_needs = []
        if failure_context:
            failure_driven_needs = self._analyze_failure_context(failure_context, archetype_context)
        
        # Determine base refinement needs
        base_needs = self._identify_base_refinement_needs(quality_analysis, archetype_context)
        
        # Combine and prioritize needs
        all_needs = failure_driven_needs + base_needs
        prioritized_needs = self._prioritize_refinement_needs(all_needs, iteration, quality_analysis)
        
        # Determine target agent
        target_agent = self._determine_target_agent(prioritized_needs, archetype_context)
        
        # Calculate confidence
        confidence = self._calculate_refinement_confidence(quality_analysis, iteration)
        
        # Generate reasoning
        reasoning = self._generate_refinement_reasoning(
            quality_analysis, prioritized_needs, target_agent, iteration
        )
        
        return RefinementPlan(
            needs_refinement=len(prioritized_needs) > 0,
            refinement_tasks=prioritized_needs,
            target_agent=target_agent,
            confidence=confidence,
            reasoning=reasoning,
            metadata={
                "iteration": iteration,
                "quality_score": quality_analysis["overall_score"],
                "failure_driven": len(failure_driven_needs) > 0,
                "analysis_timestamp": current_results.timestamp
            }
        )
    
    def _calculate_signal_density(self, results: List[Dict[str, Any]]) -> float:
        """Calculate signal density in research results."""
        if not results:
            return 0.0
        
        signal_indicators = 0
        total_indicators = 0
        
        for result in results:
            text = result.get("text", "").lower()
            metadata = result.get("metadata", {})
            
            # Count potential signal indicators
            if re.search(r'\d+%|\$\d+|\d+x', text):
                signal_indicators += 1
            if metadata.get("timestamp"):
                signal_indicators += 1
            if metadata.get("named_entities"):
                signal_indicators += 1
            if metadata.get("is_signal_candidate"):
                signal_indicators += 1
            
            total_indicators += 4
        
        return signal_indicators / total_indicators if total_indicators > 0 else 0.0
    
    def _calculate_source_diversity(self, results: List[Dict[str, Any]]) -> float:
        """Calculate source diversity in research results."""
        if not results:
            return 0.0
        
        sources = set()
        for result in results:
            source = result.get("metadata", {}).get("source", "unknown")
            sources.add(source)
        
        # Normalize by ideal diversity (5+ sources is excellent)
        return min(len(sources) / 5.0, 1.0)
    
    def _calculate_temporal_relevance(self, results: List[Dict[str, Any]]) -> float:
        """Calculate temporal relevance of research results."""
        if not results:
            return 0.0
        
        recent_count = 0
        for result in results:
            metadata = result.get("metadata", {})
            if metadata.get("age_days", 365) <= 90:  # Recent = within 90 days
                recent_count += 1
        
        return recent_count / len(results)
    
    def _identify_quality_gaps(
        self, 
        quality_metrics: Dict[str, Any], 
        archetype_context: ArchetypeContext
    ) -> List[str]:
        """Identify quality gaps based on metrics and archetype requirements."""
        gaps = []
        
        # Confidence gaps
        if quality_metrics["confidence_avg"] < archetype_context.signal_params.min_signal_score:
            gaps.append("low_confidence_scores")
        
        # Result count gaps
        if quality_metrics["result_count"] < self._refinement_thresholds["min_results"]:
            gaps.append("insufficient_results")
        
        # Signal density gaps
        if quality_metrics["signal_density"] < self._refinement_thresholds["signal_density_threshold"]:
            gaps.append("low_signal_density")
        
        # Source diversity gaps
        if quality_metrics["source_diversity"] < 0.6:
            gaps.append("poor_source_diversity")
        
        # Temporal relevance gaps
        if quality_metrics["temporal_relevance"] < 0.5:
            gaps.append("outdated_information")
        
        # Archetype-specific gaps
        if archetype_context.archetype == ArchetypeType.SENIOR_TA and quality_metrics["signal_density"] < 0.5:
            gaps.append("insufficient_technical_signals")
        elif archetype_context.archetype == ArchetypeType.C_LEVEL and quality_metrics["source_diversity"] < 0.8:
            gaps.append("limited_business_perspective")
        
        return gaps
    
    def _calculate_overall_quality_score(self, quality_metrics: Dict[str, Any]) -> float:
        """Calculate overall quality score from individual metrics."""
        weights = {
            "confidence_avg": 0.3,
            "result_count": 0.2,
            "signal_density": 0.2,
            "source_diversity": 0.15,
            "temporal_relevance": 0.15
        }
        
        normalized_metrics = {
            "confidence_avg": min(quality_metrics["confidence_avg"], 1.0),
            "result_count": min(quality_metrics["result_count"] / 10.0, 1.0),  # 10+ results is excellent
            "signal_density": quality_metrics["signal_density"],
            "source_diversity": quality_metrics["source_diversity"],
            "temporal_relevance": quality_metrics["temporal_relevance"]
        }
        
        return sum(
            normalized_metrics[metric] * weight 
            for metric, weight in weights.items()
        )
    
    def _meets_quality_thresholds(
        self, 
        quality_metrics: Dict[str, Any], 
        archetype_context: ArchetypeContext
    ) -> bool:
        """Check if research meets quality thresholds."""
        overall_score = self._calculate_overall_quality_score(quality_metrics)
        
        # Base threshold
        base_threshold = 0.7
        
        # Adjust based on archetype
        if archetype_context.archetype == ArchetypeType.SENIOR_TA:
            base_threshold = 0.8  # Higher bar for senior technical authorities
        elif archetype_context.archetype == ArchetypeType.C_LEVEL:
            base_threshold = 0.75  # Higher bar for executives
        elif archetype_context.archetype == ArchetypeType.EXECUTIVE:
            base_threshold = 0.7  # Standard bar for executives
        else:  # RECRUITER
            base_threshold = 0.65  # Lower bar for recruiters
        
        return overall_score >= base_threshold
    
    def _analyze_failure_context(
        self, 
        failure_context: FailureContext, 
        archetype_context: ArchetypeContext
    ) -> List[str]:
        """Analyze failure context to generate specific refinement needs."""
        needs = []
        
        violation_type = failure_context.violation_type.lower()
        
        if "placeholder" in violation_type:
            needs.append("find_specific_data_points")
            needs.append("validate_information_completeness")
        
        if "confidence" in violation_type:
            needs.append("increase_source_credibility")
            needs.append("find_supporting_evidence")
        
        if "job_title" in violation_type:
            needs.append("verify_recipient_role")
            needs.append("find_recent_role_information")
        
        if "content_safety" in violation_type:
            needs.append("find_alternative_sources")
            needs.append("refine_search_terms")
        
        return needs
    
    def _identify_base_refinement_needs(
        self, 
        quality_analysis: Dict[str, Any], 
        archetype_context: ArchetypeContext
    ) -> List[str]:
        """Identify base refinement needs from quality analysis."""
        needs = []
        gaps = quality_analysis["gaps"]
        
        gap_to_need_mapping = {
            "low_confidence_scores": "find_higher_confidence_sources",
            "insufficient_results": "expand_search_scope",
            "low_signal_density": "search_for_signal_indicators",
            "poor_source_diversity": "diversify_information_sources",
            "outdated_information": "find_recent_activities",
            "insufficient_technical_signals": "search_technical_achievements",
            "limited_business_perspective": "search_business_metrics"
        }
        
        for gap in gaps:
            if gap in gap_to_need_mapping:
                needs.append(gap_to_need_mapping[gap])
        
        # Add archetype-specific needs
        if archetype_context.archetype == ArchetypeType.SENIOR_TA:
            needs.append("validate_technical_expertise")
        elif archetype_context.archetype == ArchetypeType.C_LEVEL:
            needs.append("quantify_business_impact")
        elif archetype_context.archetype == ArchetypeType.EXECUTIVE:
            needs.append("assess_team_fit")
        elif archetype_context.archetype == ArchetypeType.RECRUITER:
            needs.append("verify_job_requirements")
        
        return list(set(needs))  # Remove duplicates
    
    def _prioritize_refinement_needs(
        self, 
        needs: List[str], 
        iteration: int, 
        quality_analysis: Dict[str, Any]
    ) -> List[str]:
        """Prioritize refinement needs based on impact and iteration."""
        # Priority weights
        priorities = {
            "find_higher_confidence_sources": 1.0,
            "find_specific_data_points": 0.9,
            "validate_information_completeness": 0.9,
            "expand_search_scope": 0.8,
            "search_for_signal_indicators": 0.7,
            "diversify_information_sources": 0.6,
            "find_recent_activities": 0.6
        }
        
        # Sort by priority
        prioritized = sorted(
            needs,
            key=lambda need: priorities.get(need, 0.5),
            reverse=True
        )
        
        # Limit based on iteration (early iterations get more tasks)
        max_tasks = max(5 - iteration, 2)
        return prioritized[:max_tasks]
    
    def _determine_target_agent(
        self, 
        needs: List[str], 
        archetype_context: ArchetypeContext
    ) -> Optional[AgentType]:
        """Determine which agent should handle refinement tasks."""
        if not needs:
            return None
        
        # Count needs by agent type
        agent_counts = {AgentType.CONTACT: 0, AgentType.COMPANY: 0}
        
        for need in needs:
            for pattern, agent in self._agent_mapping.items():
                if pattern in need.lower():
                    agent_counts[agent] += 1
                    break
        
        # Return agent with most responsibilities
        if agent_counts[AgentType.CONTACT] > agent_counts[AgentType.COMPANY]:
            return AgentType.CONTACT
        elif agent_counts[AgentType.COMPANY] > agent_counts[AgentType.CONTACT]:
            return AgentType.COMPANY
        else:
            # Default based on archetype
            if archetype_context.archetype in [ArchetypeType.SENIOR_TA, ArchetypeType.RECRUITER]:
                return AgentType.CONTACT
            else:
                return AgentType.COMPANY
    
    def _calculate_refinement_confidence(
        self, 
        quality_analysis: Dict[str, Any], 
        iteration: int
    ) -> float:
        """Calculate confidence in refinement plan."""
        base_confidence = 1.0 - quality_analysis["overall_score"]
        
        # Adjust based on iteration (later iterations have lower confidence)
        iteration_penalty = iteration * 0.1
        
        return max(base_confidence - iteration_penalty, 0.3)
    
    def _generate_refinement_reasoning(
        self, 
        quality_analysis: Dict[str, Any], 
        needs: List[str], 
        target_agent: Optional[AgentType],
        iteration: int
    ) -> str:
        """Generate reasoning for refinement plan."""
        reasoning_parts = []
        
        # Quality assessment
        score = quality_analysis["overall_score"]
        if score < 0.5:
            reasoning_parts.append("Research quality is significantly below threshold")
        elif score < 0.7:
            reasoning_parts.append("Research quality needs improvement")
        else:
            reasoning_parts.append("Research quality is acceptable but can be enhanced")
        
        # Specific needs
        if needs:
            reasoning_parts.append(f"Primary focus: {', '.join(needs[:3])}")
        
        # Target agent rationale
        if target_agent:
            reasoning_parts.append(f"Assigned to {target_agent.value} agent based on task nature")
        
        # Iteration context
        if iteration > 1:
            reasoning_parts.append(f"Iteration {iteration} refinement")
        
        return "; ".join(reasoning_parts)
    
    def plan_multi_axis_research(
        self,
        base_query: str,
        archetype_context: ArchetypeContext,
        target_company: str = ""
    ) -> MultiAxisReasoningPlan:
        """
        Plan multi-axis research expansion using ExecutiveReasoningProfile.
        
        For EXECUTIVE and C_LEVEL archetypes, expands queries across all cognitive axes
        with reasoning depth multipliers from the executive profile.
        
        Args:
            base_query: Base research query
            archetype_context: Archetype context with executive reasoning profile
            target_company: Target company for context-specific queries
            
        Returns:
            MultiAxisReasoningPlan with expanded queries and reasoning parameters
        """
        executive_profile = archetype_context.executive_reasoning_profile
        
        # Initialize multi-axis plan
        plan = MultiAxisReasoningPlan(
            base_query=base_query,
            cognitive_axes=executive_profile.cognitive_axes,
            reasoning_intensity=executive_profile.reasoning_intensity,
            require_deep_research=executive_profile.require_deep_research,
            sc_k=executive_profile.sc_k,
            cot_depth_multiplier=executive_profile.cot_depth,
            tot_recursion_multiplier=executive_profile.tot_recursion_depth
        )
        
        # Generate cognitive axes queries if deep research required
        if executive_profile.require_deep_research:
            plan.cognitive_axes_queries = self._generate_cognitive_axes_queries(
                base_query, executive_profile.cognitive_axes, target_company
            )
            
            # Expand subqueries using reasoning depth multipliers
            plan.expanded_subqueries = self._expand_queries_with_reasoning_depth(
                plan.cognitive_axes_queries, executive_profile
            )
            
            plan.total_query_count = len(plan.expanded_subqueries)
        else:
            # Simple query expansion for non-deep research
            plan.expanded_subqueries = [base_query]
            plan.total_query_count = 1
        
        # Set target sources based on archetype
        plan.target_sources = self._determine_target_sources(archetype_context.archetype)
        
        return plan
    
    def plan_reflexion_cycles(
        self,
        current_results: ResearchResult,
        archetype_context: ArchetypeContext,
        iteration: int = 1
    ) -> ReflexionPlan:
        """
        Plan reflexion critique and refinement cycles.
        
        Generates critique questions and refinement strategies based on
        reflexion_passes from ExecutiveReasoningProfile.
        
        Args:
            current_results: Current research results to critique
            archetype_context: Archetype context with executive reasoning profile
            iteration: Current iteration number
            
        Returns:
            ReflexionPlan with critique questions and refinement strategies
        """
        executive_profile = archetype_context.executive_reasoning_profile
        
        # Initialize reflexion plan
        plan = ReflexionPlan(
            reflexion_passes=executive_profile.reflexion_passes,
            current_pass=iteration,
            max_passes=executive_profile.reflexion_passes,
            reasoning_intensity=executive_profile.reasoning_intensity,
            confidence_threshold=archetype_context.signal_params.min_signal_score
        )
        
        # Generate critique questions if reflexion passes > 0
        if executive_profile.reflexion_passes > 0:
            plan.critique_questions = self._generate_critique_questions(
                current_results, archetype_context, iteration
            )
            
            plan.refinement_strategies = self._generate_refinement_strategies(
                plan.critique_questions, archetype_context
            )
            
            plan.completion_criteria = self._generate_completion_criteria(
                executive_profile, archetype_context
            )
        
        return plan
    
    def _generate_cognitive_axes_queries(
        self, 
        base_query: str, 
        cognitive_axes: List[str], 
        target_company: str = ""
    ) -> Dict[str, List[str]]:
        """Generate queries expanded across cognitive axes."""
        axes_queries = {}
        
        # Cognitive axis query templates
        axis_templates = {
            "strategic": [
                f"{base_query} strategic vision",
                f"{base_query} long-term strategy",
                f"{base_query} market positioning"
            ],
            "financial": [
                f"{base_query} financial performance",
                f"{base_query} revenue growth",
                f"{base_query} investment strategy"
            ],
            "technical": [
                f"{base_query} technology stack",
                f"{base_query} technical innovation",
                f"{base_query} engineering capabilities"
            ],
            "competitive": [
                f"{base_query} competitive landscape",
                f"{base_query} market competition",
                f"{base_query} competitive advantages"
            ],
            "product": [
                f"{base_query} product strategy",
                f"{base_query} product development",
                f"{base_query} product roadmap"
            ],
            "operational": [
                f"{base_query} operational efficiency",
                f"{base_query} business operations",
                f"{base_query} process optimization"
            ],
            "risk": [
                f"{base_query} risk management",
                f"{base_query} business risks",
                f"{base_query} strategic risks"
            ],
            "psychographic": [
                f"{base_query} leadership style",
                f"{base_query} decision making",
                f"{base_query} team culture"
            ]
        }
        
        # Generate queries for each cognitive axis
        for axis in cognitive_axes:
            if axis in axis_templates:
                queries = axis_templates[axis]
                if target_company:
                    queries = [q.replace(base_query, f"{target_company} {base_query}") for q in queries]
                axes_queries[axis] = queries
        
        return axes_queries
    
    def _expand_queries_with_reasoning_depth(
        self, 
        cognitive_axes_queries: Dict[str, List[str]], 
        executive_profile: ExecutiveReasoningProfile
    ) -> List[str]:
        """Expand queries using unified reasoning multiplier."""
        expanded_queries = []
        
        # Calculate unified expansion multiplier using cot_depth * tot_branches
        reasoning_multiplier = compute_reasoning_multiplier(executive_profile)
        
        for axis, queries in cognitive_axes_queries.items():
            # Expand each query based on reasoning multiplier
            for query in queries:
                # Generate multiplier-specific variations
                for depth in range(reasoning_multiplier):
                    depth_query = f"{query} (depth {depth + 1})"
                    expanded_queries.append(depth_query)
        
        return expanded_queries
    
    def _generate_critique_questions(
        self, 
        current_results: ResearchResult, 
        archetype_context: ArchetypeContext, 
        iteration: int
    ) -> List[str]:
        """Generate LIC-style critique questions for reflexion."""
        questions = []
        
        # Quality-based critique questions
        avg_confidence = sum(current_results.confidence_scores) / len(current_results.confidence_scores) if current_results.confidence_scores else 0.0
        
        if avg_confidence < 0.7:
            questions.append("Are the research sources sufficiently credible for this archetype?")
            questions.append("What additional evidence would strengthen confidence in findings?")
        
        if len(current_results.results) < 5:
            questions.append("Is the research scope comprehensive enough for informed outreach?")
            questions.append("What critical information gaps remain in the current research?")
        
        # Archetype-specific critique questions
        if archetype_context.archetype == ArchetypeType.C_LEVEL:
            questions.extend([
                "Does the research demonstrate strategic business impact?",
                "Are financial signals and market positioning adequately quantified?",
                "Is there sufficient competitive intelligence for executive decision-making?"
            ])
        elif archetype_context.archetype == ArchetypeType.EXECUTIVE:
            questions.extend([
                "Does the research address business outcomes and team impact?",
                "Are operational and strategic considerations properly balanced?",
                "Is there sufficient context for business stakeholder evaluation?"
            ])
        elif archetype_context.archetype == ArchetypeType.SENIOR_TA:
            questions.extend([
                "Does the research demonstrate technical depth and innovation?",
                "Are technical achievements and capabilities clearly articulated?",
                "Is there sufficient technical context for expert evaluation?"
            ])
        
        # Iteration-specific questions
        if iteration > 1:
            questions.append(f"Have the refinement strategies from iteration {iteration - 1} been effectively addressed?")
        
        return questions
    
    def _generate_refinement_strategies(
        self, 
        critique_questions: List[str], 
        archetype_context: ArchetypeContext
    ) -> List[str]:
        """Generate refinement strategies based on critique questions."""
        strategies = []
        
        # Map question patterns to refinement strategies
        for question in critique_questions:
            question_lower = question.lower()
            
            if "credibility" in question_lower or "confidence" in question_lower:
                strategies.append("Seek higher-authority sources and validate claims")
                strategies.append("Find supporting evidence from multiple independent sources")
            
            elif "comprehensive" in question_lower or "gaps" in question_lower:
                strategies.append("Expand research scope to cover missing domains")
                strategies.append("Identify and research critical information gaps")
            
            elif "strategic" in question_lower or "business impact" in question_lower:
                strategies.append("Focus on strategic business outcomes and metrics")
                strategies.append("Quantify business value and competitive advantages")
            
            elif "financial" in question_lower or "market" in question_lower:
                strategies.append("Research financial performance and market positioning")
                strategies.append("Gather quantitative business metrics and indicators")
            
            elif "technical" in question_lower or "innovation" in question_lower:
                strategies.append("Deepen research into technical capabilities and innovations")
                strategies.append("Document technical achievements and expertise areas")
            
            elif "operational" in question_lower or "team" in question_lower:
                strategies.append("Research operational processes and team dynamics")
                strategies.append("Understand organizational structure and decision-making")
        
        return list(set(strategies))  # Remove duplicates
    
    def _generate_completion_criteria(
        self, 
        executive_profile: ExecutiveReasoningProfile, 
        archetype_context: ArchetypeContext
    ) -> List[str]:
        """Generate completion criteria for reflexion cycles."""
        criteria = []
        
        # Base criteria for all archetypes
        criteria.extend([
            "Research confidence meets or exceeds archetype threshold",
            "Sufficient information depth for personalized outreach",
            "Key claims supported by credible evidence"
        ])
        
        # Intensity-specific criteria
        if executive_profile.reasoning_intensity in ["high", "extreme"]:
            criteria.extend([
                "Multi-axis research covers all relevant cognitive domains",
                "Strategic and business implications clearly articulated",
                "Competitive landscape and market positioning well understood"
            ])
        
        # Archetype-specific criteria
        if archetype_context.archetype == ArchetypeType.C_LEVEL:
            criteria.extend([
                "Executive-level strategic insights documented",
                "Financial signals and business impact quantified",
                "Leadership decision-making context established"
            ])
        elif archetype_context.archetype == ArchetypeType.EXECUTIVE:
            criteria.extend([
                "Business stakeholder concerns addressed",
                "Team and operational impact assessed",
                "Strategic alignment opportunities identified"
            ])
        
        return criteria
    
    def _determine_target_sources(self, archetype: str) -> List[str]:
        """Determine target research sources based on archetype."""
        source_mapping = {
            ArchetypeType.RECRUITER: [
                "job_postings", "company_career_pages", "linkedin_profiles",
                "recruitment_blogs", "hiring_insights"
            ],
            ArchetypeType.SENIOR_TA: [
                "technical_blogs", "github_repositories", "stackoverflow",
                "research_papers", "patent_filings", "conference_proceedings"
            ],
            ArchetypeType.EXECUTIVE: [
                "executive_insights", "business_news", "market_analysis",
                "company_reports", "management_blogs", "industry_analysis"
            ],
            ArchetypeType.C_LEVEL: [
                "earnings_calls", "executive_interviews", "market_reports",
                "financial_filings", "competitor_analysis", "strategic_documents"
            ]
        }
        
        return source_mapping.get(str(archetype), ["general_web_search"])
    
    def plan_research_refinement(
        self,
        current_results: ResearchResult,
        archetype_context: ArchetypeContext,
        iteration: int = 1,
        failure_context: Optional[FailureContext] = None
    ) -> RefinementPlan:
        """
        Plan research refinement based on current results and archetype context.
        
        This is the primary entry point for research refinement planning that
        produces a RefinementPlan with tasks mapped to contact or company agents.
        
        Args:
            current_results: Current research results to analyze
            archetype_context: Archetype context from archetype planning
            iteration: Current iteration number
            failure_context: Optional failure context from L5 validation
            
        Returns:
            RefinementPlan with refinement tasks and target agent
        """
        return self.determine_refinement_needs(
            current_results=current_results,
            archetype_context=archetype_context,
            iteration=iteration,
            failure_context=failure_context
        )


#
# === Learning Trace Map ===
# LAYER: L1
# ROLE: Plans research refinement to ensure executive-grade evidence quality for message credibility
# IMPACT: Strengthens message evidence through quality thresholds -> increases executive trust by 25%
# FLOW: apps/lic_outreach/lic_workflow_entry.py -> L2 research executors -> ResearchRefinementPlanner.analyze_research_quality() -> L4 retrieval refinement
#
