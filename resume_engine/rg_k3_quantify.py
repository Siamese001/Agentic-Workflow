"""RG K3 Quantify - Resume Metrics and Achievement Quantification

Incorporated from historical agentic_workflow/l2/rg_k3_quant.py to execute
advanced resume metrics extraction and achievement quantification.

This is the third execution phase in the resume generation pipeline:
K1 Extract → K2 Clean → K3 Quantify → K4 Rewrite → K5 Skillmap → K6 Assemble → K7 Format → K8 Validate
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
import logging
import re

logger = logging.getLogger(__name__)


@dataclass
class QuantifiedMetric:
    """Individual quantified metric from resume content."""
    metric_id: str
    metric_type: str  # "percentage", "currency", "time", "count", "impact"
    value: Union[str, float, int]
    unit: str  # "%", "$", "years", "months", "count", etc.
    context: str  # Surrounding text for context
    confidence_score: float
    extraction_method: str  # "pattern_based", "semantic", "hybrid"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QuantifiedAchievement:
    """Quantified achievement with impact metrics and evidence ranking."""
    achievement_id: str
    description: str
    quantified_metrics: List[QuantifiedMetric]
    impact_category: str  # "efficiency", "growth", "cost_savings", "quality", "innovation"
    impact_score: float  # 0.0 to 1.0
    confidence_score: float
    ranking_score: float = 0.0  # Combined evidence ranking score
    rank: int = 0  # Position in ranked list (1=best)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QuantificationMetrics:
    """Metrics from resume quantification process."""
    total_metrics_extracted: int
    total_achievements_quantified: int
    metrics_by_type: Dict[str, int]
    achievements_by_category: Dict[str, int]
    average_impact_score: float
    quantification_confidence: float
    processing_time_ms: int


@dataclass
class QuantificationOutput:
    """Complete output from K3 quantification phase."""
    quantified_metrics: List[QuantifiedMetric]
    quantified_achievements: List[QuantifiedAchievement]
    quantified_content: str
    metrics: QuantificationMetrics
    quantification_plan: Dict[str, Any]
    success: bool
    error_message: str
    processing_trace: List[Dict[str, Any]] = field(default_factory=list)


class RGK3Quantify:
    """K3 Resume Quantifier - Third hop in sequential processing pipeline.
    
    Executes advanced resume metrics extraction and achievement quantification:
    - Extract numerical metrics (percentages, currency, time periods)
    - Quantify achievements with impact scoring
    - Categorize impact by business value
    - Calculate confidence scores for quantifications
    """
    
    def __init__(self, 
                 quantification_plan: Optional[Dict[str, Any]] = None,
                 telemetry_bus: Optional[Any] = None) -> None:
        """Initialize K3 resume quantifier."""
        self.quantification_plan = quantification_plan or {}
        self.telemetry_bus = telemetry_bus
        
        # Metric extraction patterns
        self.metric_patterns = {
            "percentage": [
                (r'(\d+(?:\.\d+)?)\s*%?', 'percentage'),
                (r'(\d+(?:\.\d+)?)\s*percent', 'percentage'),
                (r'(\d+(?:\.\d+)?)\s*pct', 'percentage'),
            ],
            "currency": [
                (r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)', 'currency'),
                (r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:dollars?|usd)', 'currency'),
                (r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:k|thousand)', 'currency_k'),
            ],
            "time": [
                (r'(\d+)\s*(?:years?|yrs?)', 'years'),
                (r'(\d+)\s*(?:months?|mos?)', 'months'),
                (r'(\d+)\s*(?:weeks?|wks?)', 'weeks'),
                (r'(\d+)\s*(?:days?)', 'days'),
            ],
            "count": [
                (r'(\d+)\s*(?:people?|employees?|staff|team members?)', 'people'),
                (r'(\d+)\s*(?:projects?|initiatives?)', 'projects'),
                (r'(\d+)\s*(?:clients?|customers?)', 'clients'),
                (r'(\d+)\s*(?:products?|services?)', 'products'),
            ],
            "impact": [
                (r'(?:increased|grew|boosted)\s+(?:by\s+)?(\d+(?:\.\d+)?)\s*%?', 'increase_percentage'),
                (r'(?:reduced|decreased|cut|saved)\s+(?:by\s+)?(\d+(?:\.\d+)?)\s*%?', 'reduction_percentage'),
                (r'(?:improved|enhanced|optimized)\s+(?:by\s+)?(\d+(?:\.\d+)?)\s*%?', 'improvement_percentage'),
            ]
        }
        
        # Achievement impact indicators
        self.impact_indicators = {
            "efficiency": [
                "streamlined", "optimized", "automated", "simplified", "reduced time",
                "faster", "quicker", "efficient", "productivity", "workflow"
            ],
            "growth": [
                "grew", "increased", "expanded", "scaled", "growth", "revenue",
                "market share", "customer base", "adoption", "engagement"
            ],
            "cost_savings": [
                "saved", "reduced costs", "cut expenses", "budget", "cost-effective",
                "economical", "financial", "monetary", "savings", "profitability"
            ],
            "quality": [
                "improved quality", "enhanced", "better", "accuracy", "precision",
                "reliability", "standards", "compliance", "excellence", "performance"
            ],
            "innovation": [
                "innovated", "created", "developed", "designed", "invented",
                "pioneered", "breakthrough", "novel", "cutting-edge", "first"
            ]
        }
        
        # Action verbs for achievement identification
        self.action_verbs = [
            "managed", "led", "developed", "implemented", "created", "designed",
            "optimized", "improved", "increased", "reduced", "achieved", "delivered",
            "launched", "built", "engineered", "transformed", "revolutionized"
        ]
    
    def quantify_resume_content(
        self,
        *,
        cleaning_output: Any,  # From K2 cleaning
        job_requirements: Optional[Dict[str, Any]] = None,  # Job context for ranking
        quantification_params: Optional[Dict[str, Any]] = None
    ) -> QuantificationOutput:
        """Execute resume content quantification with evidence ranking.
        
        Args:
            cleaning_output: Output from K2 cleaning phase
            job_requirements: Job requirements for evidence ranking
            quantification_params: Quantification strategy and parameters
            
        Returns:
            Complete quantification output with ranked metrics and achievements
        """
        quantification_params = quantification_params or {}
        processing_trace: List[Dict[str, Union[str, int]]] = []
        
        try:
            # 1. Initialize quantification strategy
            strategy = self._initialize_quantification_strategy(quantification_params)
            processing_trace.append({
                "step": "strategy_initialization",
                "strategy": strategy,
                "timestamp": "2024-01-01T00:00:01Z"
            })
            
            # 2. Extract cleaned content
            content = self._extract_cleaned_content(cleaning_output)
            processing_trace.append({
                "step": "content_extraction",
                "content_length": len(content),
                "timestamp": "2024-01-01T00:00:02Z"
            })
            
            # 3. Extract numerical metrics
            metrics = self._extract_numerical_metrics(content, strategy)
            processing_trace.append({
                "step": "metrics_extraction",
                "metrics_found": len(metrics),
                "timestamp": "2024-01-01T00:00:03Z"
            })
            
            # 4. Identify and quantify achievements
            achievements = self._quantify_achievements(content, metrics, strategy)
            processing_trace.append({
                "step": "achievement_quantification",
                "achievements_quantified": len(achievements),
                "timestamp": "2024-01-01T00:00:04Z"
            })
            
            # 5. Apply evidence ranking to achievements
            ranked_achievements = self._rank_achievements(achievements, job_requirements, strategy)
            processing_trace.append({
                "step": "evidence_ranking",
                "achievements_ranked": len(ranked_achievements),
                "top_rank_score": ranked_achievements[0].ranking_score if ranked_achievements else 0.0,
                "timestamp": "2024-01-01T00:00:05Z"
            })
            
            # 5. Generate quantified content
            quantified_content = self._generate_quantified_content(metrics, ranked_achievements)
            processing_trace.append({
                "step": "content_generation",
                "quantified_length": len(quantified_content),
                "timestamp": "2024-01-01T00:00:05Z"
            })
            
            # 6. Calculate quantification metrics
            quant_metrics = self._calculate_quantification_metrics(metrics, ranked_achievements)
            processing_trace.append({
                "step": "metrics_calculation",
                "quantification_confidence": quant_metrics.quantification_confidence,
                "timestamp": "2024-01-01T00:00:06Z"
            })
            
            # 7. Build quantification output
            quantification_output = QuantificationOutput(
                quantified_metrics=metrics,
                quantified_achievements=ranked_achievements,  # Use ranked achievements
                quantified_content=quantified_content,
                metrics=quant_metrics,
                quantification_plan={
                    "strategy": strategy,
                    "parameters": quantification_params,
                    "patterns_used": list(self.metric_patterns.keys()),
                    "evidence_ranking_enabled": job_requirements is not None
                },
                success=True,
                error_message="",
                processing_trace=processing_trace
            )
            
            # 8. Record telemetry (best-effort)
            self._safe_record_telemetry(quantification_output)
            
            return quantification_output
            
        except Exception as e:
            logger.error(f"Resume quantification failed: {e}")
            
            error_output = QuantificationOutput(
                quantified_metrics=[],
                quantified_achievements=[],
                quantified_content="",
                metrics=QuantificationMetrics(0, 0, {}, {}, 0.0, 0.0, 0),
                quantification_plan={},
                success=False,
                error_message=str(e),
                processing_trace=processing_trace + [{
                    "step": "error",
                    "error": str(e),
                    "timestamp": "2024-01-01T00:00:07Z"
                }]
            )
            
            return error_output
    
    def _initialize_quantification_strategy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize quantification strategy based on parameters."""
        return {
            "approach": params.get("approach", "achievements"),
            "extract_metrics": params.get("extract_metrics", True),
            "focus_on_impact": params.get("focus_on_impact", True),
            "confidence_threshold": params.get("confidence_threshold", 0.6),
            "min_metric_value": params.get("min_metric_value", 1),
            "evidence_ranking": params.get("evidence_ranking", True)
        }
    
    def _rank_achievements(self, achievements: List[QuantifiedAchievement], job_requirements: Optional[Dict[str, Any]], strategy: Dict[str, Any]) -> List[QuantifiedAchievement]:
        """Apply evidence ranking to achievements based on multiple factors."""
        if not strategy.get("evidence_ranking", True):
            return achievements
        
        # Calculate ranking scores for each achievement
        for achievement in achievements:
            achievement.ranking_score = self._calculate_ranking_score(achievement, job_requirements)
        
        # Sort achievements by ranking score (descending)
        ranked_achievements = sorted(achievements, key=lambda x: x.ranking_score, reverse=True)
        
        # Assign ranks (1-based)
        for i, achievement in enumerate(ranked_achievements):
            achievement.rank = i + 1
        
        return ranked_achievements
    
    def _calculate_ranking_score(self, achievement: QuantifiedAchievement, job_requirements: Optional[Dict[str, Any]]) -> float:
        """Calculate comprehensive ranking score for an achievement."""
        base_score = 0.0
        
        # 1. Impact score weight (30%)
        base_score += achievement.impact_score * 0.3
        
        # 2. Confidence score weight (20%)
        base_score += achievement.confidence_score * 0.2
        
        # 3. Quantifiable metrics score weight (25%)
        metrics_score = self._calculate_metrics_score(achievement.quantified_metrics)
        base_score += metrics_score * 0.25
        
        # 4. Action verb strength weight (15%)
        verb_score = self._calculate_verb_strength_score(achievement.description)
        base_score += verb_score * 0.15
        
        # 5. Job relevance score weight (10%)
        relevance_score = self._calculate_job_relevance_score(achievement, job_requirements)
        base_score += relevance_score * 0.1
        
        return min(base_score, 1.0)
    
    def _calculate_metrics_score(self, metrics: List[QuantifiedMetric]) -> float:
        """Calculate score based on quality and quantity of metrics."""
        if not metrics:
            return 0.0
        
        score = 0.0
        
        # High-value metric types
        high_value_types = {"percentage", "currency", "time"}
        metric_count = len(metrics)
        high_value_count = sum(1 for m in metrics if m.metric_type in high_value_types)
        
        # Base score for having metrics
        score += min(metric_count * 0.1, 0.3)  # Max 0.3 for quantity
        
        # Bonus for high-value metrics
        score += min(high_value_count * 0.2, 0.4)  # Max 0.4 for quality
        
        # Bonus for large values
        for metric in metrics:
            if metric.metric_type == "percentage" and isinstance(metric.value, (int, float)):
                if metric.value >= 50:
                    score += 0.1
            elif metric.metric_type == "currency" and isinstance(metric.value, (int, float)):
                if metric.value >= 1000000:  # $1M+
                    score += 0.1
                elif metric.value >= 100000:  # $100k+
                    score += 0.05
            elif metric.metric_type == "time" and isinstance(metric.value, (int, float)):
                if metric.value >= 5:  # 5+ years
                    score += 0.05
        
        return min(score, 1.0)
    
    def _calculate_verb_strength_score(self, description: str) -> float:
        """Calculate score based on strength of action verbs."""
        description_lower = description.lower()
        
        # Strong action verbs with their scores
        verb_strengths = {
            "revolutionized": 1.0, "transformed": 0.95, "pioneered": 0.9,
            "engineered": 0.85, "architected": 0.85, "orchestrated": 0.8,
            "led": 0.75, "managed": 0.7, "directed": 0.7,
            "developed": 0.65, "implemented": 0.65, "created": 0.6,
            "optimized": 0.6, "improved": 0.55, "enhanced": 0.5,
            "increased": 0.45, "reduced": 0.45, "achieved": 0.4,
            "delivered": 0.35, "launched": 0.35, "built": 0.3
        }
        
        max_score = 0.0
        for verb, score in verb_strengths.items():
            if verb in description_lower:
                max_score = max(max_score, score)
        
        return max_score
    
    def _calculate_job_relevance_score(self, achievement: QuantifiedAchievement, job_requirements: Optional[Dict[str, Any]]) -> float:
        """Calculate score based on relevance to job requirements."""
        if not job_requirements:
            return 0.5  # Neutral score when no job requirements
        
        score = 0.0
        achievement_text = achievement.description.lower()
        
        # Check skills relevance
        job_skills = job_requirements.get("skills", [])
        for skill in job_skills:
            if isinstance(skill, str) and skill.lower() in achievement_text:
                score += 0.2
        
        # Check requirements relevance
        job_requirements_text = " ".join(job_requirements.get("requirements", [])).lower()
        for req_word in job_requirements_text.split():
            if len(req_word) > 4 and req_word in achievement_text:
                score += 0.1
        
        # Check industry alignment
        job_title = job_requirements.get("title", "").lower()
        if "software" in job_title or "developer" in job_title:
            tech_keywords = ["developed", "implemented", "coded", "engineered", "programmed"]
            for keyword in tech_keywords:
                if keyword in achievement_text:
                    score += 0.15
                    break
        elif "manager" in job_title or "lead" in job_title:
            mgmt_keywords = ["led", "managed", "directed", "coordinated", "oversaw"]
            for keyword in mgmt_keywords:
                if keyword in achievement_text:
                    score += 0.15
                    break
        
        return min(score, 1.0)
    
    def _extract_cleaned_content(self, cleaning_output: Any) -> str:
        """Extract cleaned content from K2 output."""
        if hasattr(cleaning_output, 'cleaned_content'):
            return cleaning_output.cleaned_content
        elif isinstance(cleaning_output, dict):
            return cleaning_output.get("cleaned_content", "")
        else:
            return ""
    
    def _extract_numerical_metrics(self, content: str, strategy: Dict[str, Any]) -> List[QuantifiedMetric]:
        """Extract numerical metrics from content."""
        metrics = []
        
        if not strategy["extract_metrics"]:
            return metrics
        
        for metric_type, patterns in self.metric_patterns.items():
            for pattern, unit_type in patterns:
                matches = list(re.finditer(pattern, content, re.IGNORECASE))
                
                for match in matches:
                    try:
                        # Extract value and convert to appropriate type
                        value_str = match.group(1)
                        
                        if metric_type == "percentage":
                            value = float(value_str)
                        elif metric_type == "currency":
                            # Remove commas and convert to float
                            clean_value = value_str.replace(',', '')
                            value = float(clean_value)
                            if unit_type == "currency_k":
                                value *= 1000
                        elif metric_type in ["time", "count", "impact"]:
                            value = int(value_str)
                        else:
                            value = value_str
                        
                        # Get context around the match
                        start = max(0, match.start() - 50)
                        end = min(len(content), match.end() + 50)
                        context = content[start:end].strip()
                        
                        # Determine unit
                        if unit_type == "percentage":
                            unit = "%"
                        elif unit_type.startswith("currency"):
                            unit = "$"
                        elif unit_type in ["years", "months", "weeks", "days"]:
                            unit = unit_type
                        elif unit_type in ["people", "projects", "clients", "products"]:
                            unit = unit_type
                        elif unit_type.endswith("_percentage"):
                            unit = "%"
                        else:
                            unit = unit_type
                        
                        metric = QuantifiedMetric(
                            metric_id=f"{metric_type}_{len(metrics)}",
                            metric_type=metric_type,
                            value=value,
                            unit=unit,
                            context=context,
                            confidence_score=self._calculate_metric_confidence(value, context, metric_type),
                            extraction_method="pattern_based",
                            metadata={
                                "pattern": pattern,
                                "match_position": match.start(),
                                "raw_value": value_str
                            }
                        )
                        
                        # Filter by minimum value threshold
                        if isinstance(value, (int, float)) and value >= strategy["min_metric_value"]:
                            metrics.append(metric)
                        
                    except (ValueError, IndexError) as e:
                        logger.debug(f"Failed to parse metric: {e}")
                        continue
        
        return self._deduplicate_metrics(metrics)
    
    def _quantify_achievements(self, content: str, metrics: List[QuantifiedMetric], strategy: Dict[str, Any]) -> List[QuantifiedAchievement]:
        """Identify and quantify achievements from content."""
        achievements = []
        
        if not strategy["focus_on_impact"]:
            return achievements
        
        # Split content into sentences/bullet points
        sentences = re.split(r'[.!?]+|•', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        for i, sentence in enumerate(sentences):
            # Check if sentence contains action verb
            if any(verb in sentence.lower() for verb in self.action_verbs):
                # Find associated metrics
                associated_metrics = self._find_associated_metrics(sentence, metrics)
                
                # Determine impact category
                impact_category = self._determine_impact_category(sentence)
                
                # Calculate impact score
                impact_score = self._calculate_impact_score(sentence, associated_metrics, impact_category)
                
                # Calculate confidence
                confidence_score = self._calculate_achievement_confidence(sentence, associated_metrics, impact_score)
                
                if confidence_score >= strategy["confidence_threshold"]:
                    achievement = QuantifiedAchievement(
                        achievement_id=f"achievement_{len(achievements)}",
                        description=sentence,
                        quantified_metrics=associated_metrics,
                        impact_category=impact_category,
                        impact_score=impact_score,
                        confidence_score=confidence_score,
                        metadata={
                            "sentence_index": i,
                            "has_metrics": len(associated_metrics) > 0,
                            "action_verbs": [verb for verb in self.action_verbs if verb in sentence.lower()]
                        }
                    )
                    achievements.append(achievement)
        
        return achievements
    
    def _find_associated_metrics(self, sentence: str, metrics: List[QuantifiedMetric]) -> List[QuantifiedMetric]:
        """Find metrics associated with a sentence."""
        associated = []
        
        for metric in metrics:
            # Check if metric context overlaps with sentence
            if metric.context.lower() in sentence.lower() or sentence.lower() in metric.context.lower():
                associated.append(metric)
            # Check if metric value appears in sentence
            elif str(metric.value) in sentence:
                associated.append(metric)
        
        return associated
    
    def _determine_impact_category(self, text: str) -> str:
        """Determine impact category based on text content."""
        text_lower = text.lower()
        
        category_scores = {}
        for category, indicators in self.impact_indicators.items():
            score = sum(1 for indicator in indicators if indicator in text_lower)
            category_scores[category] = score
        
        if category_scores:
            return max(category_scores, key=category_scores.get)
        else:
            return "general"
    
    def _calculate_impact_score(self, sentence: str, metrics: List[QuantifiedMetric], impact_category: str) -> float:
        """Calculate impact score for an achievement."""
        base_score = 0.3
        
        # Factor in metrics
        if metrics:
            metric_score = min(len(metrics) * 0.2, 0.4)
            base_score += metric_score
            
            # Factor in metric values
            for metric in metrics:
                if isinstance(metric.value, (int, float)):
                    if metric.metric_type == "percentage":
                        base_score += min(metric.value / 100 * 0.1, 0.2)
                    elif metric.metric_type == "currency":
                        base_score += min(metric.value / 100000 * 0.1, 0.2)
                    elif metric.metric_type in ["time", "count"]:
                        base_score += min(metric.value / 10 * 0.05, 0.1)
        
        # Factor in impact category
        category_bonus = {
            "efficiency": 0.1,
            "growth": 0.15,
            "cost_savings": 0.2,
            "quality": 0.1,
            "innovation": 0.15,
            "general": 0.05
        }
        
        base_score += category_bonus.get(impact_category, 0.05)
        
        return min(base_score, 1.0)
    
    def _calculate_metric_confidence(self, value: Union[str, float, int], context: str, metric_type: str) -> float:
        """Calculate confidence score for a metric."""
        base_confidence = 0.7
        
        # Context quality
        if len(context) > 20:
            base_confidence += 0.1
        
        # Value reasonableness
        if isinstance(value, (int, float)):
            if metric_type == "percentage" and 0 <= value <= 100:
                base_confidence += 0.1
            elif metric_type == "currency" and 0 < value < 10000000:
                base_confidence += 0.1
            elif metric_type in ["time", "count"] and 0 < value < 100:
                base_confidence += 0.1
        
        return min(base_confidence, 1.0)
    
    def _calculate_achievement_confidence(self, sentence: str, metrics: List[QuantifiedMetric], impact_score: float) -> float:
        """Calculate confidence score for an achievement."""
        base_confidence = 0.5
        
        # Factor in action verbs
        action_verb_count = sum(1 for verb in self.action_verbs if verb in sentence.lower())
        base_confidence += min(action_verb_count * 0.1, 0.2)
        
        # Factor in metrics
        if metrics:
            avg_metric_confidence = sum(m.confidence_score for m in metrics) / len(metrics)
            base_confidence += avg_metric_confidence * 0.2
        
        # Factor in impact score
        base_confidence += impact_score * 0.1
        
        return min(base_confidence, 1.0)
    
    def _deduplicate_metrics(self, metrics: List[QuantifiedMetric]) -> List[QuantifiedMetric]:
        """Remove duplicate metrics, keeping highest confidence ones."""
        seen_metrics = {}
        deduplicated = []
        
        for metric in metrics:
            key = f"{metric.metric_type}_{metric.value}_{metric.unit}"
            if key not in seen_metrics or metric.confidence_score > seen_metrics[key].confidence_score:
                seen_metrics[key] = metric
        
        return list(seen_metrics.values())
    
    def _generate_quantified_content(self, metrics: List[QuantifiedMetric], achievements: List[QuantifiedAchievement]) -> str:
        """Generate content with quantified metrics highlighted."""
        content_parts = []
        
        # Add metrics summary
        if metrics:
            content_parts.append("## Quantified Metrics\n")
            for metric in metrics:
                content_parts.append(f"• {metric.metric_type.title()}: {metric.value} {metric.unit} (confidence: {metric.confidence_score:.2f})")
            content_parts.append("")
        
        # Add achievements summary
        if achievements:
            content_parts.append("## Quantified Achievements\n")
            for achievement in achievements:
                content_parts.append(f"• **{achievement.impact_category.title()} Impact** (Score: {achievement.impact_score:.2f}): {achievement.description}")
                if achievement.quantified_metrics:
                    metric_summary = ", ".join([f"{m.value} {m.unit}" for m in achievement.quantified_metrics])
                    content_parts.append(f"  Metrics: {metric_summary}")
            content_parts.append("")
        
        return '\n'.join(content_parts)
    
    def _calculate_quantification_metrics(self, metrics: List[QuantifiedMetric], achievements: List[QuantifiedAchievement]) -> QuantificationMetrics:
        """Calculate quantification performance metrics."""
        total_metrics = len(metrics)
        total_achievements = len(achievements)
        
        # Count metrics by type
        metrics_by_type = {}
        for metric in metrics:
            metrics_by_type[metric.metric_type] = metrics_by_type.get(metric.metric_type, 0) + 1
        
        # Count achievements by category
        achievements_by_category = {}
        for achievement in achievements:
            category = achievement.impact_category
            achievements_by_category[category] = achievements_by_category.get(category, 0) + 1
        
        # Calculate average impact score
        if achievements:
            avg_impact = sum(a.impact_score for a in achievements) / len(achievements)
        else:
            avg_impact = 0.0
        
        # Calculate overall quantification confidence
        if metrics or achievements:
            metric_confidence = sum(m.confidence_score for m in metrics) / len(metrics) if metrics else 0.0
            achievement_confidence = sum(a.confidence_score for a in achievements) / len(achievements) if achievements else 0.0
            overall_confidence = (metric_confidence + achievement_confidence) / 2
        else:
            overall_confidence = 0.0
        
        return QuantificationMetrics(
            total_metrics_extracted=total_metrics,
            total_achievements_quantified=total_achievements,
            metrics_by_type=metrics_by_type,
            achievements_by_category=achievements_by_category,
            average_impact_score=avg_impact,
            quantification_confidence=overall_confidence,
            processing_time_ms=200  # Placeholder
        )
    
    def _safe_record_telemetry(self, quantification_output: QuantificationOutput) -> None:
        """Record telemetry data (best-effort)."""
        try:
            if self.telemetry_bus:
                self.telemetry_bus.record("rg_k3_quantify_executed", {
                    "metrics_extracted": quantification_output.metrics.total_metrics_extracted,
                    "achievements_quantified": quantification_output.metrics.total_achievements_quantified,
                    "average_impact_score": quantification_output.metrics.average_impact_score,
                    "success": quantification_output.success
                })
        except Exception as e:
            logger.debug(f"Failed to record telemetry: {e}")
    
    def get_quantification_summary(self, quantification_output: QuantificationOutput) -> Dict[str, Any]:
        """Get a summary of the quantification execution for debugging/telemetry."""
        return {
            "execution_id": "rg_k3_quantify",
            "metrics_extracted": quantification_output.metrics.total_metrics_extracted,
            "achievements_quantified": quantification_output.metrics.total_achievements_quantified,
            "average_impact_score": quantification_output.metrics.average_impact_score,
            "quantification_confidence": quantification_output.metrics.quantification_confidence,
            "success": quantification_output.success
        }
