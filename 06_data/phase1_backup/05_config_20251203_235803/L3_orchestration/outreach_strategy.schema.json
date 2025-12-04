"""
Outreach Validation Endpoint
LEVEL 5 - API endpoint for validating outreach message quality and effectiveness
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
from datetime import datetime

from ...services.utils.scoring import OutreachScorer
from ...services.pipelines.validation_pipeline import ValidationPipeline

router = APIRouter(prefix="/validate", tags=["outreach-validation"])

# Initialize services
outreach_scorer = OutreachScorer()
validation_pipeline = ValidationPipeline()

class OutreachValidationEndpoint:
    """Handles outreach message validation requests"""
    
    def __init__(self):
        self.scorer = outreach_scorer
        self.validator = validation_pipeline
    
    async def validate_outreach_message(
        self,
        request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate outreach message quality and effectiveness
        
        Args:
            request: Validation request with outreach content and context
            
        Returns:
            Comprehensive validation results with scores and recommendations
        """
        try:
            # Validate request
            validation_result = await self._validate_request(request)
            if not validation_result["valid"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid request: {validation_result['error']}"
                )
            
            # Extract outreach content
            outreach_content = request["outreach_content"]
            context = request.get("context", {})
            
            # Perform comprehensive validation
            scoring_result = await self._perform_scoring(outreach_content, context)
            compliance_result = await self._check_compliance(outreach_content, context)
            effectiveness_result = await self._assess_effectiveness(outreach_content, context)
            
            # Calculate overall validation score
            overall_score = await self._calculate_overall_score(
                scoring_result, compliance_result, effectiveness_result
            )
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(
                scoring_result, compliance_result, effectiveness_result
            )
            
            return {
                "success": True,
                "validation_results": {
                    "overall_score": overall_score,
                    "grade": await self._get_grade(overall_score),
                    "scoring_metrics": scoring_result,
                    "compliance_metrics": compliance_result,
                    "effectiveness_metrics": effectiveness_result,
                    "recommendations": recommendations,
                    "strengths": await self._identify_strengths(scoring_result, compliance_result, effectiveness_result),
                    "improvement_areas": await self._identify_improvement_areas(scoring_result, compliance_result, effectiveness_result)
                },
                "metadata": {
                    "validated_at": datetime.utcnow().isoformat(),
                    "message_type": context.get("outreach_type", "unknown"),
                    "word_count": await self._count_words(outreach_content)
                }
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to validate outreach message: {str(e)}"
            )
    
    async def _validate_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Validate validation request"""
        if "outreach_content" not in request:
            return {
                "valid": False,
                "error": "Missing outreach_content field"
            }
        
        outreach_content = request["outreach_content"]
        
        if not isinstance(outreach_content, dict):
            return {
                "valid": False,
                "error": "outreach_content must be a dictionary"
            }
        
        # Check for required content fields
        required_fields = ["subject", "body", "call_to_action"]
        for field in required_fields:
            if field not in outreach_content:
                return {
                    "valid": False,
                    "error": f"Missing required field in outreach_content: {field}"
                }
        
        # Validate content quality
        if len(outreach_content["body"].strip()) < 50:
            return {
                "valid": False,
                "error": "Message body is too short (minimum 50 characters)"
            }
        
        if len(outreach_content["body"].strip()) > 1000:
            return {
                "valid": False,
                "error": "Message body is too long (maximum 1000 characters)"
            }
        
        return {"valid": True}
    
    async def _perform_scoring(
        self,
        outreach_content: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform quality scoring on outreach content"""
        try:
            # Use outreach scorer for comprehensive analysis
            scoring_result = await self.scorer.calculate_comprehensive_score(
                outreach_content, context
            )
            
            return {
                "content_quality": scoring_result["individual_scores"]["content_quality"].score,
                "personalization": scoring_result["individual_scores"]["personalization"].score,
                "clarity": scoring_result["individual_scores"]["clarity"].score,
                "professionalism": scoring_result["individual_scores"]["professionalism"].score,
                "engagement": scoring_result["individual_scores"]["engagement"].score,
                "details": scoring_result
            }
            
        except Exception as e:
            # Return default scores if scoring fails
            return {
                "content_quality": 0.7,
                "personalization": 0.7,
                "clarity": 0.7,
                "professionalism": 0.7,
                "engagement": 0.7,
                "error": str(e)
            }
    
    async def _check_compliance(
        self,
        outreach_content: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check compliance with outreach best practices and regulations"""
        compliance_score = 1.0
        issues = []
        
        # Check subject line compliance
        subject = outreach_content.get("subject", "")
        if len(subject) < 10:
            compliance_score -= 0.1
            issues.append("Subject line too short")
        
        if len(subject) > 100:
            compliance_score -= 0.1
            issues.append("Subject line too long")
        
        # Check for spam indicators
        body = outreach_content.get("body", "").lower()
        spam_indicators = ["free", "guarantee", "click here", "act now", "limited time"]
        found_spam = [indicator for indicator in spam_indicators if indicator in body]
        
        if found_spam:
            compliance_score -= 0.2
            issues.append(f"Contains potential spam indicators: {', '.join(found_spam)}")
        
        # Check call-to-action compliance
        cta = outreach_content.get("call_to_action", "")
        if not cta or len(cta.strip()) < 10:
            compliance_score -= 0.15
            issues.append("Call-to-action is missing or too brief")
        
        # Check personalization indicators
        recipient_name = context.get("recipient_profile", {}).get("name", "")
        if recipient_name and recipient_name.lower() not in body:
            compliance_score -= 0.1
            issues.append("Message not personalized with recipient name")
        
        # Check for contact information
        has_contact = any(info in body for info in ["@", "phone", "linkedin", "website"])
        if not has_contact:
            compliance_score -= 0.1
            issues.append("Missing contact information")
        
        return {
            "compliance_score": max(compliance_score, 0.0),
            "issues_found": issues,
            "spam_score": len(found_spam) / len(spam_indicators),
            "personalization_score": 0.9 if recipient_name.lower() in body else 0.7,
            "contact_info_present": has_contact
        }
    
    async def _assess_effectiveness(
        self,
        outreach_content: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess potential effectiveness of outreach message"""
        effectiveness_score = 0.8  # Base score
        factors = {}
        
        # Subject line effectiveness
        subject = outreach_content.get("subject", "")
        subject_effectiveness = 0.8
        
        if any(word in subject.lower() for word in ["question", "introduction", "opportunity"]):
            subject_effectiveness += 0.1
        
        if "?" in subject:
            subject_effectiveness += 0.1
        
        factors["subject_effectiveness"] = min(subject_effectiveness, 1.0)
        
        # Body structure effectiveness
        body = outreach_content.get("body", "")
        sentences = body.split(".")
        
        if 3 <= len(sentences) <= 7:
            structure_score = 1.0
        else:
            structure_score = 0.7
        
        factors["structure_score"] = structure_score
        
        # Call-to-action effectiveness
        cta = outreach_content.get("call_to_action", "")
        cta_effectiveness = 0.7
        
        action_words = ["schedule", "call", "meet", "discuss", "connect", "reply"]
        if any(word in cta.lower() for word in action_words):
            cta_effectiveness += 0.2
        
        if "?" in cta:
            cta_effectiveness += 0.1
        
        factors["cta_effectiveness"] = min(cta_effectiveness, 1.0)
        
        # Personalization effectiveness
        recipient_profile = context.get("recipient_profile", {})
        personalization_score = 0.7
        
        if recipient_profile.get("company") and recipient_profile["company"].lower() in body.lower():
            personalization_score += 0.1
        
        if recipient_profile.get("role") and recipient_profile["role"].lower() in body.lower():
            personalization_score += 0.1
        
        factors["personalization_effectiveness"] = min(personalization_score, 1.0)
        
        # Calculate overall effectiveness
        effectiveness_score = sum(factors.values()) / len(factors)
        
        return {
            "effectiveness_score": effectiveness_score,
            "factors": factors,
            "predicted_response_rate": min(effectiveness_score * 0.4, 0.5),  # Max 50% predicted
            "engagement_potential": effectiveness_score
        }
    
    async def _calculate_overall_score(
        self,
        scoring_result: Dict[str, Any],
        compliance_result: Dict[str, Any],
        effectiveness_result: Dict[str, Any]
    ) -> float:
        """Calculate weighted overall validation score"""
        weights = {
            "scoring": 0.4,
            "compliance": 0.3,
            "effectiveness": 0.3
        }
        
        scoring_score = sum([
            scoring_result["content_quality"],
            scoring_result["personalization"],
            scoring_result["clarity"],
            scoring_result["professionalism"],
            scoring_result["engagement"]
        ]) / 5
        
        compliance_score = compliance_result["compliance_score"]
        effectiveness_score = effectiveness_result["effectiveness_score"]
        
        overall_score = (
            scoring_score * weights["scoring"] +
            compliance_score * weights["compliance"] +
            effectiveness_score * weights["effectiveness"]
        )
        
        return round(overall_score, 2)
    
    async def _generate_recommendations(
        self,
        scoring_result: Dict[str, Any],
        compliance_result: Dict[str, Any],
        effectiveness_result: Dict[str, Any]
    ) -> list:
        """Generate improvement recommendations"""
        recommendations = []
        
        # Scoring recommendations
        if scoring_result["content_quality"] < 0.8:
            recommendations.append("Improve content quality with more specific details")
        
        if scoring_result["personalization"] < 0.8:
            recommendations.append("Add more personalization based on recipient profile")
        
        if scoring_result["clarity"] < 0.8:
            recommendations.append("Improve message clarity and readability")
        
        # Compliance recommendations
        recommendations.extend(compliance_result["issues_found"])
        
        # Effectiveness recommendations
        factors = effectiveness_result["factors"]
        
        if factors["subject_effectiveness"] < 0.8:
            recommendations.append("Make subject line more engaging with questions or value propositions")
        
        if factors["cta_effectiveness"] < 0.8:
            recommendations.append("Strengthen call-to-action with clear next steps")
        
        if factors["personalization_effectiveness"] < 0.8:
            recommendations.append("Add more specific references to recipient's background")
        
        return recommendations[:8]  # Limit to top 8 recommendations
    
    async def _identify_strengths(
        self,
        scoring_result: Dict[str, Any],
        compliance_result: Dict[str, Any],
        effectiveness_result: Dict[str, Any]
    ) -> list:
        """Identify message strengths"""
        strengths = []
        
        # Scoring strengths
        for metric, score in scoring_result.items():
            if metric != "details" and score >= 0.8:
                strengths.append(f"Strong {metric.replace('_', ' ')}")
        
        # Compliance strengths
        if compliance_result["compliance_score"] >= 0.9:
            strengths.append("Excellent compliance with best practices")
        
        # Effectiveness strengths
        factors = effectiveness_result["factors"]
        for factor, score in factors.items():
            if score >= 0.8:
                strengths.append(f"Strong {factor.replace('_', ' ')}")
        
        return strengths
    
    async def _identify_improvement_areas(
        self,
        scoring_result: Dict[str, Any],
        compliance_result: Dict[str, Any],
        effectiveness_result: Dict[str, Any]
    ) -> list:
        """Identify areas needing improvement"""
        improvements = []
        
        # Scoring improvements
        for metric, score in scoring_result.items():
            if metric != "details" and score < 0.7:
                improvements.append(f"Improve {metric.replace('_', ' ')}")
        
        # Compliance improvements
        if compliance_result["compliance_score"] < 0.7:
            improvements.append("Address compliance issues")
        
        # Effectiveness improvements
        factors = effectiveness_result["factors"]
        for factor, score in factors.items():
            if score < 0.7:
                improvements.append(f"Enhance {factor.replace('_', ' ')}")
        
        return improvements
    
    async def _get_grade(self, score: float) -> str:
        """Get letter grade for validation score"""
        if score >= 0.9:
            return "A"
        elif score >= 0.8:
            return "B"
        elif score >= 0.7:
            return "C"
        elif score >= 0.6:
            return "D"
        else:
            return "F"
    
    async def _count_words(self, outreach_content: Dict[str, Any]) -> int:
        """Count total words in outreach content"""
        total_words = 0
        
        for field in ["subject", "body", "call_to_action"]:
            content = outreach_content.get(field, "")
            total_words += len(content.split())
        
        return total_words

# Create endpoint instance
validation_endpoint = OutreachValidationEndpoint()

@router.post("/message")
async def validate_outreach_message(request: Dict[str, Any]):
    """Validate outreach message quality and effectiveness"""
    return await validation_endpoint.validate_outreach_message(request)

@router.get("/metrics")
async def get_validation_metrics():
    """Get validation metrics and scoring criteria"""
    return {
        "scoring_criteria": {
            "content_quality": {"weight": 0.2, "description": "Overall content quality and relevance"},
            "personalization": {"weight": 0.2, "description": "Degree of personalization for recipient"},
            "clarity": {"weight": 0.2, "description": "Message clarity and readability"},
            "professionalism": {"weight": 0.2, "description": "Professional tone and language"},
            "engagement": {"weight": 0.2, "description": "Potential to engage recipient"}
        },
        "compliance_checks": [
            "Subject line length and quality",
            "Spam indicator detection",
            "Call-to-action presence",
            "Personalization indicators",
            "Contact information inclusion"
        ],
        "effectiveness_factors": [
            "Subject line effectiveness",
            "Message structure",
            "Call-to-action strength",
            "Personalization depth"
        ],
        "grade_thresholds": {
            "A": "90-100%",
            "B": "80-89%",
            "C": "70-79%",
            "D": "60-69%",
            "F": "Below 60%"
        }
    }

__all__ = ["router", "OutreachValidationEndpoint"]
