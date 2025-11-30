"""
Outreach Scoring Utilities
LEVEL 5 - Quality scoring and evaluation algorithms for outreach messages
"""

from typing import Dict, List, Any, Optional
import asyncio
import logging
import re
from datetime import datetime

class OutreachScorer:
    """Utility class for scoring outreach message quality and effectiveness"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Scoring weights for different quality dimensions
        self.scoring_weights = {
            "personalization": 0.25,
            "clarity": 0.20,
            "engagement": 0.20,
            "professionalism": 0.15,
            "actionability": 0.10,
            "value_proposition": 0.10
        }
        
        # Scoring criteria and thresholds
        self.scoring_criteria = {
            "personalization": {
                "name_mention": 0.3,
                "company_reference": 0.2,
                "role_reference": 0.2,
                "context_relevance": 0.2,
                "mutual_connections": 0.1
            },
            "clarity": {
                "sentence_structure": 0.3,
                "readability": 0.3,
                "logical_flow": 0.2,
                "conciseness": 0.2
            },
            "engagement": {
                "questions": 0.25,
                "emotional_appeal": 0.25,
                "curiosity_inducing": 0.25,
                "relevance": 0.25
            },
            "professionalism": {
                "tone": 0.3,
                "language": 0.3,
                "structure": 0.2,
                "etiquette": 0.2
            },
            "actionability": {
                "clear_cta": 0.4,
                "specific_next_steps": 0.3,
                "low_friction": 0.3
            },
            "value_proposition": {
                "benefit_clarity": 0.4,
                "recipient_focus": 0.3,
                "differentiation": 0.3
            }
        }
        
        # Quality thresholds
        self.quality_thresholds = {
            "excellent": 0.9,
            "good": 0.75,
            "average": 0.6,
            "below_average": 0.4,
            "poor": 0.0
        }
    
    async def calculate_quality_scores(
        self,
        outreach_content: Dict[str, str],
        context: Dict[str, Any] = None
    ) -> Dict[str, float]:
        """
        Calculate comprehensive quality scores for outreach message
        
        Args:
            outreach_content: The outreach message content
            context: Additional context for scoring
            
        Returns:
            Dictionary of quality scores by dimension
        """
        try:
            self.logger.info("Calculating outreach quality scores")
            
            scores = {}
            
            # Calculate scores for each dimension
            scores["personalization"] = await self._score_personalization(outreach_content, context)
            scores["clarity"] = await self._score_clarity(outreach_content, context)
            scores["engagement"] = await self._score_engagement(outreach_content, context)
            scores["professionalism"] = await self._score_professionalism(outreach_content, context)
            scores["actionability"] = await self._score_actionability(outreach_content, context)
            scores["value_proposition"] = await self._score_value_proposition(outreach_content, context)
            
            # Calculate overall score
            scores["overall"] = await self._calculate_overall_score(scores)
            
            return scores
            
        except Exception as e:
            self.logger.error(f"Error calculating quality scores: {e}")
            raise e
    
    async def _score_personalization(
        self,
        outreach_content: Dict[str, str],
        context: Dict[str, Any] = None
    ) -> float:
        """Score personalization quality"""
        
        content_text = " ".join(outreach_content.values()).lower()
        score = 0.0
        
        # Check for recipient name
        recipient_name = context.get("recipient_profile", {}).get("name", "").lower() if context else ""
        if recipient_name and recipient_name in content_text:
            score += self.scoring_criteria["personalization"]["name_mention"]
        
        # Check for company reference
        recipient_company = context.get("recipient_profile", {}).get("company", "").lower() if context else ""
        if recipient_company and recipient_company in content_text:
            score += self.scoring_criteria["personalization"]["company_reference"]
        
        # Check for role reference
        recipient_role = context.get("recipient_profile", {}).get("role", "").lower() if context else ""
        if recipient_role and recipient_role in content_text:
            score += self.scoring_criteria["personalization"]["role_reference"]
        
        # Check for context relevance
        if context and context.get("mutual_connections"):
            if "connected with" in content_text or "mutual" in content_text:
                score += self.scoring_criteria["personalization"]["context_relevance"]
        
        # Check for shared interests
        if context and context.get("shared_interests"):
            if "share" in content_text and "interest" in content_text:
                score += self.scoring_criteria["personalization"]["mutual_connections"]
        
        return min(score, 1.0)
    
    async def _score_clarity(
        self,
        outreach_content: Dict[str, str],
        context: Dict[str, Any] = None
    ) -> float:
        """Score message clarity"""
        
        body = outreach_content.get("body", "")
        score = 0.0
        
        # Sentence structure score
        sentences = re.split(r'[.!?]+', body)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if sentences:
            avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
            
            # Optimal sentence length is 15-25 words
            if 15 <= avg_sentence_length <= 25:
                score += self.scoring_criteria["clarity"]["sentence_structure"]
            elif 10 <= avg_sentence_length <= 35:
                score += self.scoring_criteria["clarity"]["sentence_structure"] * 0.7
            else:
                score += self.scoring_criteria["clarity"]["sentence_structure"] * 0.4
        
        # Readability score
        words = body.split()
        complex_words = [word for word in words if len(word) > 6]
        complexity_ratio = len(complex_words) / len(words) if words else 0
        
        # Lower complexity is better for outreach
        if complexity_ratio < 0.2:
            score += self.scoring_criteria["clarity"]["readability"]
        elif complexity_ratio < 0.3:
            score += self.scoring_criteria["clarity"]["readability"] * 0.7
        else:
            score += self.scoring_criteria["clarity"]["readability"] * 0.5
        
        # Logical flow score
        flow_indicators = ["furthermore", "additionally", "however", "therefore", "because"]
        flow_count = sum(1 for indicator in flow_indicators if indicator in body.lower())
        
        if flow_count > 0:
            score += self.scoring_criteria["clarity"]["logical_flow"]
        else:
            score += self.scoring_criteria["clarity"]["logical_flow"] * 0.6
        
        # Conciseness score
        if len(body) > 0:
            word_count = len(body.split())
            if 50 <= word_count <= 300:
                score += self.scoring_criteria["clarity"]["conciseness"]
            elif 300 < word_count <= 500:
                score += self.scoring_criteria["clarity"]["conciseness"] * 0.7
            else:
                score += self.scoring_criteria["clarity"]["conciseness"] * 0.5
        
        return min(score, 1.0)
    
    async def _score_engagement(
        self,
        outreach_content: Dict[str, str],
        context: Dict[str, Any] = None
    ) -> float:
        """Score engagement potential"""
        
        content_text = " ".join(outreach_content.values()).lower()
        score = 0.0
        
        # Questions score
        question_count = content_text.count('?')
        if question_count >= 1:
            score += self.scoring_criteria["engagement"]["questions"]
        else:
            score += self.scoring_criteria["engagement"]["questions"] * 0.3
        
        # Emotional appeal score
        emotional_words = ["excited", "interested", "impressed", "opportunity", "valuable", "benefit"]
        emotional_count = sum(1 for word in emotional_words if word in content_text)
        
        if emotional_count >= 2:
            score += self.scoring_criteria["engagement"]["emotional_appeal"]
        elif emotional_count >= 1:
            score += self.scoring_criteria["engagement"]["emotional_appeal"] * 0.6
        else:
            score += self.scoring_criteria["engagement"]["emotional_appeal"] * 0.3
        
        # Curiosity inducing score
        curiosity_words = ["explore", "discover", "learn", "opportunity", "potential", "innovative"]
        curiosity_count = sum(1 for word in curiosity_words if word in content_text)
        
        if curiosity_count >= 2:
            score += self.scoring_criteria["engagement"]["curiosity_inducing"]
        elif curiosity_count >= 1:
            score += self.scoring_criteria["engagement"]["curiosity_inducing"] * 0.7
        else:
            score += self.scoring_criteria["engagement"]["curiosity_inducing"] * 0.4
        
        # Relevance score
        subject = outreach_content.get("subject", "").lower()
        body = outreach_content.get("body", "").lower()
        
        # Check if subject aligns with body content
        subject_words = set(subject.split())
        body_words = set(body.split())
        relevance_ratio = len(subject_words & body_words) / len(subject_words) if subject_words else 0
        
        if relevance_ratio > 0.3:
            score += self.scoring_criteria["engagement"]["relevance"]
        elif relevance_ratio > 0.1:
            score += self.scoring_criteria["engagement"]["relevance"] * 0.7
        else:
            score += self.scoring_criteria["engagement"]["relevance"] * 0.5
        
        return min(score, 1.0)
    
    async def _score_professionalism(
        self,
        outreach_content: Dict[str, str],
        context: Dict[str, Any] = None
    ) -> float:
        """Score professionalism"""
        
        content_text = " ".join(outreach_content.values()).lower()
        score = 0.0
        
        # Tone score
        professional_openings = ["dear", "hello", "hi"]
        unprofessional_openings = ["hey", "yo", "what's up"]
        
        opening = outreach_content.get("opening", "").lower()
        if any(professional in opening for professional in professional_openings):
            score += self.scoring_criteria["professionalism"]["tone"]
        elif any(unprofessional in opening for unprofessional in unprofessional_openings):
            score += self.scoring_criteria["professionalism"]["tone"] * 0.5
        else:
            score += self.scoring_criteria["professionalism"]["tone"] * 0.7
        
        # Language score
        professional_words = ["opportunity", "collaboration", "expertise", "experience", "professional"]
        unprofessional_words = ["awesome", "cool", "dude", "man", "bro"]
        
        prof_count = sum(1 for word in professional_words if word in content_text)
        unprof_count = sum(1 for word in unprofessional_words if word in content_text)
        
        if prof_count >= 2 and unprof_count == 0:
            score += self.scoring_criteria["professionalism"]["language"]
        elif prof_count >= 1 and unprof_count == 0:
            score += self.scoring_criteria["professionalism"]["language"] * 0.8
        elif unprof_count > 0:
            score += self.scoring_criteria["professionalism"]["language"] * 0.4
        else:
            score += self.scoring_criteria["professionalism"]["language"] * 0.6
        
        # Structure score
        has_subject = bool(outreach_content.get("subject"))
        has_body = bool(outreach_content.get("body"))
        has_closing = bool(outreach_content.get("closing"))
        has_cta = bool(outreach_content.get("call_to_action"))
        
        structure_score = 0
        if has_subject:
            structure_score += 0.25
        if has_body:
            structure_score += 0.25
        if has_closing:
            structure_score += 0.25
        if has_cta:
            structure_score += 0.25
        
        score += self.scoring_criteria["professionalism"]["structure"] * structure_score
        
        # Etiquette score
        closing = outreach_content.get("closing", "").lower()
        if any(word in closing for word in ["regards", "sincerely", "best", "thanks"]):
            score += self.scoring_criteria["professionalism"]["etiquette"]
        else:
            score += self.scoring_criteria["professionalism"]["etiquette"] * 0.6
        
        return min(score, 1.0)
    
    async def _score_actionability(
        self,
        outreach_content: Dict[str, str],
        context: Dict[str, Any] = None
    ) -> float:
        """Score actionability of call to action"""
        
        cta = outreach_content.get("call_to_action", "").lower()
        score = 0.0
        
        # Clear CTA score
        action_words = ["call", "schedule", "meet", "discuss", "connect", "reply", "respond"]
        if any(word in cta for word in action_words):
            score += self.scoring_criteria["actionability"]["clear_cta"]
        else:
            score += self.scoring_criteria["actionability"]["clear_cta"] * 0.3
        
        # Specific next steps score
        time_words = ["week", "minutes", "available", "schedule", "time"]
        if any(word in cta for word in time_words):
            score += self.scoring_criteria["actionability"]["specific_next_steps"]
        else:
            score += self.scoring_criteria["actionability"]["specific_next_steps"] * 0.5
        
        # Low friction score
        friction_words = ["quick", "brief", "short", "15 minutes", "30 minutes"]
        if any(word in cta for word in friction_words):
            score += self.scoring_criteria["actionability"]["low_friction"]
        else:
            score += self.scoring_criteria["actionability"]["low_friction"] * 0.6
        
        return min(score, 1.0)
    
    async def _score_value_proposition(
        self,
        outreach_content: Dict[str, str],
        context: Dict[str, Any] = None
    ) -> float:
        """Score value proposition quality"""
        
        content_text = " ".join(outreach_content.values()).lower()
        score = 0.0
        
        # Benefit clarity score
        benefit_words = ["benefit", "advantage", "improve", "enhance", "save", "increase", "value"]
        benefit_count = sum(1 for word in benefit_words if word in content_text)
        
        if benefit_count >= 2:
            score += self.scoring_criteria["value_proposition"]["benefit_clarity"]
        elif benefit_count >= 1:
            score += self.scoring_criteria["value_proposition"]["benefit_clarity"] * 0.7
        else:
            score += self.scoring_criteria["value_proposition"]["benefit_clarity"] * 0.4
        
        # Recipient focus score
        recipient_focus_words = ["you", "your", "help", "support", "assist"]
        focus_count = sum(1 for word in recipient_focus_words if word in content_text)
        
        if focus_count >= 3:
            score += self.scoring_criteria["value_proposition"]["recipient_focus"]
        elif focus_count >= 2:
            score += self.scoring_criteria["value_proposition"]["recipient_focus"] * 0.8
        elif focus_count >= 1:
            score += self.scoring_criteria["value_proposition"]["recipient_focus"] * 0.6
        else:
            score += self.scoring_criteria["value_proposition"]["recipient_focus"] * 0.3
        
        # Differentiation score
        differentiation_words = ["unique", "specialized", "expertise", "experience", "background"]
        diff_count = sum(1 for word in differentiation_words if word in content_text)
        
        if diff_count >= 2:
            score += self.scoring_criteria["value_proposition"]["differentiation"]
        elif diff_count >= 1:
            score += self.scoring_criteria["value_proposition"]["differentiation"] * 0.7
        else:
            score += self.scoring_criteria["value_proposition"]["differentiation"] * 0.5
        
        return min(score, 1.0)
    
    async def _calculate_overall_score(self, dimension_scores: Dict[str, float]) -> float:
        """Calculate overall quality score from dimension scores"""
        
        overall_score = 0.0
        
        for dimension, score in dimension_scores.items():
            if dimension in self.scoring_weights:
                weight = self.scoring_weights[dimension]
                overall_score += score * weight
        
        return overall_score
    
    async def get_quality_rating(self, score: float) -> str:
        """Get quality rating based on score"""
        
        for rating, threshold in self.quality_thresholds.items():
            if score >= threshold:
                return rating
        
        return "poor"
    
    async def get_improvement_suggestions(
        self,
        dimension_scores: Dict[str, float],
        outreach_content: Dict[str, str],
        context: Dict[str, Any] = None
    ) -> List[str]:
        """Get improvement suggestions based on scores"""
        
        suggestions = []
        
        # Personalization suggestions
        if dimension_scores.get("personalization", 0) < 0.6:
            suggestions.append("Add recipient's name and company for better personalization")
            suggestions.append("Include references to mutual connections or shared interests")
        
        # Clarity suggestions
        if dimension_scores.get("clarity", 0) < 0.6:
            suggestions.append("Use shorter sentences and simpler language")
            suggestions.append("Ensure logical flow between paragraphs")
            suggestions.append("Be more concise and to the point")
        
        # Engagement suggestions
        if dimension_scores.get("engagement", 0) < 0.6:
            suggestions.append("Add questions to encourage response")
            suggestions.append("Include more engaging and positive language")
            suggestions.append("Create curiosity with intriguing statements")
        
        # Professionalism suggestions
        if dimension_scores.get("professionalism", 0) < 0.6:
            suggestions.append("Use more professional language and tone")
            suggestions.append("Ensure proper message structure with all sections")
            suggestions.append("Add appropriate closing and signature")
        
        # Actionability suggestions
        if dimension_scores.get("actionability", 0) < 0.6:
            suggestions.append("Make call to action more specific and clear")
            suggestions.append("Include specific timing or next steps")
            suggestions.append("Reduce friction by suggesting brief meetings")
        
        # Value proposition suggestions
        if dimension_scores.get("value_proposition", 0) < 0.6:
            suggestions.append("Clearly articulate benefits for the recipient")
            suggestions.append("Focus more on recipient's needs and interests")
            suggestions.append("Highlight unique expertise or experience")
        
        return suggestions[:8]  # Limit to top 8 suggestions
    
    async def benchmark_againstandards(
        self,
        dimension_scores: Dict[str, float],
        industry: str = "general"
    ) -> Dict[str, Any]:
        """Benchmark scores against industry standards"""
        
        # Industry benchmarks (simplified for demo)
        industry_benchmarks = {
            "technology": {
                "personalization": 0.7,
                "clarity": 0.8,
                "engagement": 0.6,
                "professionalism": 0.8,
                "actionability": 0.7,
                "value_proposition": 0.7
            },
            "finance": {
                "personalization": 0.6,
                "clarity": 0.9,
                "engagement": 0.5,
                "professionalism": 0.9,
                "actionability": 0.6,
                "value_proposition": 0.8
            },
            "general": {
                "personalization": 0.6,
                "clarity": 0.7,
                "engagement": 0.6,
                "professionalism": 0.7,
                "actionability": 0.6,
                "value_proposition": 0.6
            }
        }
        
        benchmarks = industry_benchmarks.get(industry.lower(), industry_benchmarks["general"])
        
        comparison = {}
        for dimension, user_score in dimension_scores.items():
            if dimension in benchmarks:
                benchmark_score = benchmarks[dimension]
                comparison[dimension] = {
                    "user_score": user_score,
                    "benchmark_score": benchmark_score,
                    "performance": "above" if user_score > benchmark_score else "below",
                    "gap": user_score - benchmark_score
                }
        
        return comparison
    
    async def generate_score_report(
        self,
        dimension_scores: Dict[str, float],
        outreach_content: Dict[str, str],
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive score report"""
        
        overall_score = dimension_scores.get("overall", 0.0)
        quality_rating = await self.get_quality_rating(overall_score)
        suggestions = await self.get_improvement_suggestions(dimension_scores, outreach_content, context)
        
        # Get industry benchmark if available
        industry = context.get("recipient_profile", {}).get("industry", "general") if context else "general"
        benchmark_comparison = await self.benchmark_againstandards(dimension_scores, industry)
        
        return {
            "overall_score": overall_score,
            "quality_rating": quality_rating,
            "dimension_scores": dimension_scores,
            "improvement_suggestions": suggestions,
            "benchmark_comparison": benchmark_comparison,
            "scoring_timestamp": datetime.utcnow().isoformat(),
            "scoring_version": "1.0.0"
        }

__all__ = ["OutreachScorer"]
