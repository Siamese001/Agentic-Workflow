"""
L1 Research Refinement Planner - Pure computation for research critique loops.

Implements pure planning logic to determine research refinement needs without
any execution, network calls, or external dependencies.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import re

from .outreach_dataclasses import (
    ArchetypeContext,
    RefinementPlan,
    AgentType
)


@dataclass
class ResearchResult:
    """Pure data structure for current research results."""
    query: str
    results: List[Dict[str, Any]]
    confidence_scores: List[float]
    metadata: Dict[str, Any]
    timestamp: str


@dataclass
class FailureContext:
    """Pure data structure for failure analysis from L5."""
    violation_type: str
    severity: str
    description: str
    affected_sections: List[str]
    metadata: Dict[str, Any]


class ResearchRefinementPlanner:
    """
    Pure L1 planner for research refinement decisions.
    
    Performs only computational analysis to determine if and how research
    should be refined, without executing any searches or calls.
    """
    
    def __init__(self):
        # Pure refinement criteria - no external dependencies
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
        """
        Pure computational analysis of current research quality.
        """
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
        if archetype_context.archetype == "technical_leader" and quality_metrics["signal_density"] < 0.5:
            gaps.append("insufficient_technical_signals")
        elif archetype_context.archetype == "business_executive" and quality_metrics["source_diversity"] < 0.8:
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
        if archetype_context.archetype == "technical_leader":
            base_threshold = 0.8  # Higher bar for technical leaders
        elif archetype_context.archetype == "business_executive":
            base_threshold = 0.75  # Higher bar for executives
        
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
        if archetype_context.archetype == "technical_leader":
            needs.append("validate_technical_expertise")
        elif archetype_context.archetype == "business_executive":
            needs.append("quantify_business_impact")
        elif archetype_context.archetype == "hiring_manager":
            needs.append("assess_team_fit")
        
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
            if archetype_context.archetype in ["technical_leader", "individual_contributor"]:
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
