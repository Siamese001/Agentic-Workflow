"""
Validation Pipeline Service
LEVEL 5 - Pipeline for validating outreach message quality and compliance
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime
import logging

from ..utils.scoring import OutreachScorer
from ..utils.formatting import OutreachFormatter

@dataclass
class ValidationResult:
    """Result of outreach message validation"""
    is_valid: bool
    validation_score: float
    issues_found: List[Dict[str, Any]]
    recommendations: List[str]
    compliance_checks: Dict[str, bool]
    quality_metrics: Dict[str, float]
    metadata: Dict[str, Any]

class ValidationPipeline:
    """Pipeline for validating outreach message quality and compliance"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Initialize validation components
        self.outreach_scorer = OutreachScorer()
        self.outreach_formatter = OutreachFormatter()

        # Validation stages
        self.validation_stages = [
            "content_validation",
            "format_validation",
            "compliance_validation",
            "quality_validation",
            "engagement_validation"
        ]

        # Validation rules
        self.validation_rules = {
            "content": {
                "min_body_length": 50,
                "max_body_length": 2000,
                "min_subject_length": 5,
                "max_subject_length": 100,
                "required_sections": ["subject", "body", "call_to_action"],
                "forbidden_words": ["spam", "scam", "guarantee", "free money", "click here"],
                "required_personalization": ["recipient_name"]
            },
            "format": {
                "max_line_length": 80,
                "proper_paragraphs": True,
                "no_excessive_caps": True,
                "proper_punctuation": True
            },
            "compliance": {
                "anti_spam_rules": True,
                "gdpr_compliance": True,
                "professional_standards": True,
                "no_misleading_claims": True
            },
            "quality": {
                "min_clarity_score": 0.6,
                "min_personalization_score": 0.5,
                "min_professionalism_score": 0.7,
                "min_actionability_score": 0.6
            },
            "engagement": {
                "min_engagement_score": 0.5,
                "has_clear_purpose": True,
                "has_value_proposition": True,
                "appropriate_urgency": True
            }
        }

    async def validate_outreach(
        self,
        outreach_content: Dict[str, str],
        context: Dict[str, Any] = None,
        validation_level: str = "standard"
    ) -> ValidationResult:
        """
        Validate outreach message comprehensively
        
        Args:
            outreach_content: The outreach message content to validate
            context: Additional context for validation
            validation_level: Level of validation strictness (basic, standard, strict)
            
        Returns:
            Comprehensive validation result
        """
        try:
            self.logger.info(f"Starting outreach validation at level: {validation_level}")

            # Execute validation stages
            stage_results = {}
            all_issues = []
            all_recommendations = []

            for stage in self.validation_stages:
                stage_result = await self._execute_validation_stage(
                    stage, outreach_content, context, validation_level
                )
                stage_results[stage] = stage_result

                # Collect issues and recommendations
                all_issues.extend(stage_result.get("issues", []))
                all_recommendations.extend(stage_result.get("recommendations", []))

            # Calculate overall validation score
            validation_score = await self._calculate_validation_score(stage_results)

            # Determine overall validity
            is_valid = await self._determine_validity(stage_results, validation_level)

            # Generate compliance checks
            compliance_checks = await self._generate_compliance_checks(stage_results)

            # Extract quality metrics
            quality_metrics = await self._extract_quality_metrics(stage_results)

            # Generate metadata
            metadata = await self._generate_validation_metadata(
                stage_results, validation_level, validation_score
            )

            result = ValidationResult(
                is_valid=is_valid,
                validation_score=validation_score,
                issues_found=all_issues,
                recommendations=all_recommendations,
                compliance_checks=compliance_checks,
                quality_metrics=quality_metrics,
                metadata=metadata
            )

            self.logger.info(f"Validation completed with score: {validation_score:.2f}")
            return result

        except Exception as e:
            self.logger.error(f"Validation pipeline failed: {e}")
            raise e

    async def _execute_validation_stage(
        self,
        stage: str,
        outreach_content: Dict[str, str],
        context: Dict[str, Any] = None,
        validation_level: str = "standard"
    ) -> Dict[str, Any]:
        """Execute a specific validation stage"""

        try:
            if stage == "content_validation":
                return await self._validate_content(outreach_content, context)
            elif stage == "format_validation":
                return await self._validate_format(outreach_content, context)
            elif stage == "compliance_validation":
                return await self._validate_compliance(outreach_content, context)
            elif stage == "quality_validation":
                return await self._validate_quality(outreach_content, context)
            elif stage == "engagement_validation":
                return await self._validate_engagement(outreach_content, context)
            else:
                raise ValueError(f"Unknown validation stage: {stage}")

        except Exception as e:
            self.logger.error(f"Validation stage {stage} failed: {e}")
            return {
                "stage": stage,
                "status": "failed",
                "error": str(e),
                "issues": [],
                "recommendations": []
            }

    async def _validate_content(
        self,
        outreach_content: Dict[str, str],
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Validate content structure and requirements"""

        issues = []
        recommendations = []

        # Check required sections
        required_sections = self.validation_rules["content"]["required_sections"]
        for section in required_sections:
            if section not in outreach_content or not outreach_content[section].strip():
                issues.append({
                    "type": "missing_section",
                    "section": section,
                    "severity": "high",
                    "message": f"Required section '{section}' is missing or empty"
                })

        # Check body length
        body = outreach_content.get("body", "")
        min_length = self.validation_rules["content"]["min_body_length"]
        max_length = self.validation_rules["content"]["max_body_length"]

        if len(body) < min_length:
            issues.append({
                "type": "content_too_short",
                "section": "body",
                "severity": "medium",
                "message": f"Body is too short ({len(body)} chars, minimum {min_length})"
            })
            recommendations.append("Expand the body content to provide more value and context")

        if len(body) > max_length:
            issues.append({
                "type": "content_too_long",
                "section": "body",
                "severity": "medium",
                "message": f"Body is too long ({len(body)} chars, maximum {max_length})"
            })
            recommendations.append("Condense the body content to improve readability")

        # Check subject length
        subject = outreach_content.get("subject", "")
        min_subject = self.validation_rules["content"]["min_subject_length"]
        max_subject = self.validation_rules["content"]["max_subject_length"]

        if len(subject) < min_subject:
            issues.append({
                "type": "subject_too_short",
                "section": "subject",
                "severity": "medium",
                "message": f"Subject is too short ({len(subject)} chars, minimum {min_subject})"
            })
            recommendations.append("Make the subject line more descriptive and engaging")

        if len(subject) > max_subject:
            issues.append({
                "type": "subject_too_long",
                "section": "subject",
                "severity": "medium",
                "message": f"Subject is too long ({len(subject)} chars, maximum {max_subject})"
            })
            recommendations.append("Shorten the subject line for better email client display")

        # Check for forbidden words
        forbidden_words = self.validation_rules["content"]["forbidden_words"]
        content_lower = " ".join(outreach_content.values()).lower()

        for word in forbidden_words:
            if word in content_lower:
                issues.append({
                    "type": "forbidden_content",
                    "section": "general",
                    "severity": "high",
                    "message": f"Contains forbidden word: '{word}'"
                })
                recommendations.append(f"Remove or replace the word '{word}' to avoid spam filters")

        # Check personalization requirements
        required_personalization = self.validation_rules["content"]["required_personalization"]
        recipient_name = context.get("recipient_profile", {}).get("name", "") if context else ""

        if "recipient_name" in required_personalization and recipient_name:
            if recipient_name.lower() not in content_lower:
                issues.append({
                    "type": "missing_personalization",
                    "section": "personalization",
                    "severity": "medium",
                    "message": "Message not personalized with recipient name"
                })
                recommendations.append("Add recipient's name to improve personalization")

        return {
            "stage": "content_validation",
            "status": "completed",
            "issues": issues,
            "recommendations": recommendations,
            "score": max(0.0, 1.0 - len(issues) * 0.1)
        }

    async def _validate_format(
        self,
        outreach_content: Dict[str, str],
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Validate formatting and structure"""

        issues = []
        recommendations = []

        for section_name, content in outreach_content.items():
            if not content:
                continue

            # Check line length
            max_line_length = self.validation_rules["format"]["max_line_length"]
            lines = content.split("\n")

            for i, line in enumerate(lines):
                if len(line) > max_line_length:
                    issues.append({
                        "type": "line_too_long",
                        "section": section_name,
                        "line_number": i + 1,
                        "severity": "low",
                        "message": f"Line {i + 1} is too long ({len(line)} chars)"
                    })

            # Check for excessive caps
            if self.validation_rules["format"]["no_excessive_caps"]:
                caps_ratio = sum(1 for c in content if c.isupper()) / len(content) if content else 0
                if caps_ratio > 0.3:  # More than 30% caps
                    issues.append({
                        "type": "excessive_caps",
                        "section": section_name,
                        "severity": "low",
                        "message": f"Too many capital letters ({caps_ratio:.1%})"
                    })
                    recommendations.append("Reduce use of capital letters for better readability")

            # Check proper punctuation
            if self.validation_rules["format"]["proper_punctuation"]:
                if not content.endswith(('.', '!', '?')):
                    issues.append({
                        "type": "missing_punctuation",
                        "section": section_name,
                        "severity": "low",
                        "message": "Missing ending punctuation"
                    })

        return {
            "stage": "format_validation",
            "status": "completed",
            "issues": issues,
            "recommendations": recommendations,
            "score": max(0.0, 1.0 - len(issues) * 0.05)
        }

    async def _validate_compliance(
        self,
        outreach_content: Dict[str, str],
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Validate compliance with regulations and standards"""

        issues = []
        recommendations = []

        content_text = " ".join(outreach_content.values()).lower()

        # Anti-spam validation
        if self.validation_rules["compliance"]["anti_spam_rules"]:
            spam_indicators = [
                "click here", "act now", "limited time", "free offer",
                "guarantee", "risk free", "no cost"
            ]

            for indicator in spam_indicators:
                if indicator in content_text:
                    issues.append({
                        "type": "spam_indicator",
                        "section": "compliance",
                        "severity": "medium",
                        "message": f"Contains spam indicator: '{indicator}'"
                    })
                    recommendations.append(f"Remove or rephrase '{indicator}' to avoid spam filters")

        # GDPR compliance check
        if self.validation_rules["compliance"]["gdpr_compliance"]:
            if "unsubscribe" not in content_text and context.get("outreach_type") == "email":
                issues.append({
                    "type": "missing_unsubscribe",
                    "section": "compliance",
                    "severity": "medium",
                    "message": "Email missing unsubscribe option (GDPR requirement)"
                })
                recommendations.append("Add unsubscribe link for GDPR compliance")

        # Professional standards check
        if self.validation_rules["compliance"]["professional_standards"]:
            unprofessional_phrases = [
                "get rich quick", "make money fast", "lose weight instantly",
                "cure guaranteed", "100% effective"
            ]

            for phrase in unprofessional_phrases:
                if phrase in content_text:
                    issues.append({
                        "type": "unprofessional_content",
                        "section": "compliance",
                        "severity": "high",
                        "message": f"Contains unprofessional phrase: '{phrase}'"
                    })
                    recommendations.append(f"Remove unprofessional phrase '{phrase}'")

        # Check for misleading claims
        if self.validation_rules["compliance"]["no_misleading_claims"]:
            misleading_words = ["guaranteed", "promise", "always", "never", "instant"]

            for word in misleading_words:
                if word in content_text:
                    issues.append({
                        "type": "potentially_misleading",
                        "section": "compliance",
                        "severity": "medium",
                        "message": f"Potentially misleading claim with word: '{word}'"
                    })
                    recommendations.append(f"Consider rephrasing claims using '{word}' for more accurate messaging")

        return {
            "stage": "compliance_validation",
            "status": "completed",
            "issues": issues,
            "recommendations": recommendations,
            "score": max(0.0, 1.0 - len(issues) * 0.15)
        }

    async def _validate_quality(
        self,
        outreach_content: Dict[str, str],
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Validate overall quality metrics"""

        issues = []
        recommendations = []

        # Use outreach scorer for quality metrics
        try:
            quality_scores = await self.outreach_scorer.calculate_quality_scores(
                outreach_content, context
            )

            # Check minimum quality thresholds
            quality_thresholds = self.validation_rules["quality"]

            for metric, threshold in quality_thresholds.items():
                if metric in quality_scores and quality_scores[metric] < threshold:
                    issues.append({
                        "type": "quality_below_threshold",
                        "section": "quality",
                        "severity": "medium",
                        "message": f"{metric} score ({quality_scores[metric]:.2f}) below threshold ({threshold})"
                    })

                    # Generate specific recommendations
                    if metric == "min_clarity_score":
                        recommendations.append("Improve message clarity with simpler language and better structure")
                    elif metric == "min_personalization_score":
                        recommendations.append("Add more personalization to better connect with recipient")
                    elif metric == "min_professionalism_score":
                        recommendations.append("Enhance professional tone and language")
                    elif metric == "min_actionability_score":
                        recommendations.append("Make call to action more specific and actionable")

        except Exception as e:
            self.logger.warning(f"Quality scoring failed: {e}")
            # Add default quality check
            issues.append({
                "type": "quality_check_failed",
                "section": "quality",
                "severity": "low",
                "message": "Unable to perform comprehensive quality check"
            })

        return {
            "stage": "quality_validation",
            "status": "completed",
            "issues": issues,
            "recommendations": recommendations,
            "score": max(0.0, 1.0 - len(issues) * 0.1)
        }

    async def _validate_engagement(
        self,
        outreach_content: Dict[str, str],
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Validate engagement potential"""

        issues = []
        recommendations = []

        content_text = " ".join(outreach_content.values()).lower()

        # Check for clear purpose
        if self.validation_rules["engagement"]["has_clear_purpose"]:
            purpose_indicators = ["discuss", "explore", "collaborate", "connect", "opportunity"]
            has_purpose = any(indicator in content_text for indicator in purpose_indicators)

            if not has_purpose:
                issues.append({
                    "type": "unclear_purpose",
                    "section": "engagement",
                    "severity": "medium",
                    "message": "Message purpose is not clearly stated"
                })
                recommendations.append("Clearly state the purpose of your outreach")

        # Check for value proposition
        if self.validation_rules["engagement"]["has_value_proposition"]:
            value_indicators = ["benefit", "advantage", "improve", "enhance", "value", "opportunity"]
            has_value = any(indicator in content_text for indicator in value_indicators)

            if not has_value:
                issues.append({
                    "type": "missing_value_proposition",
                    "section": "engagement",
                    "severity": "medium",
                    "message": "No clear value proposition for recipient"
                })
                recommendations.append("Include a clear value proposition for the recipient")

        # Check for appropriate urgency
        if self.validation_rules["engagement"]["appropriate_urgency"]:
            urgency_indicators = ["urgent", "immediate", "asap", "emergency"]
            has_excessive_urgency = any(indicator in content_text for indicator in urgency_indicators)

            if has_excessive_urgency and context.get("urgency") != "urgent":
                issues.append({
                    "type": "excessive_urgency",
                    "section": "engagement",
                    "severity": "low",
                    "message": "Excessive urgency may seem spammy"
                })
                recommendations.append("Reduce urgency language unless truly urgent")

        # Check for engagement elements
        engagement_elements = 0

        # Questions increase engagement
        if "?" in content_text:
            engagement_elements += 1

        # Personalization increases engagement
        recipient_name = context.get("recipient_profile", {}).get("name", "").lower() if context else ""
        if recipient_name and recipient_name in content_text:
            engagement_elements += 1

        # Clear call to action increases engagement
        cta = outreach_content.get("call_to_action", "").lower()
        action_words = ["call", "schedule", "meet", "discuss", "connect"]
        if any(word in cta for word in action_words):
            engagement_elements += 1

        if engagement_elements < 2:
            issues.append({
                "type": "low_engagement_potential",
                "section": "engagement",
                "severity": "medium",
                "message": f"Low engagement potential ({engagement_elements}/3 elements)"
            })
            recommendations.append("Add more engagement elements like questions and personalization")

        return {
            "stage": "engagement_validation",
            "status": "completed",
            "issues": issues,
            "recommendations": recommendations,
            "score": max(0.0, 1.0 - len(issues) * 0.1)
        }

    async def _calculate_validation_score(self, stage_results: Dict[str, Any]) -> float:
        """Calculate overall validation score from stage results"""

        scores = []
        for stage_name, stage_result in stage_results.items():
            if "score" in stage_result:
                scores.append(stage_result["score"])

        if scores:
            return sum(scores) / len(scores)
        else:
            return 0.5  # Default score

    async def _determine_validity(
        self,
        stage_results: Dict[str, Any],
        validation_level: str
    ) -> bool:
        """Determine overall validity based on validation level"""

        # Count issues by severity
        high_severity_issues = 0
        medium_severity_issues = 0

        for stage_result in stage_results.values():
            for issue in stage_result.get("issues", []):
                severity = issue.get("severity", "low")
                if severity == "high":
                    high_severity_issues += 1
                elif severity == "medium":
                    medium_severity_issues += 1

        # Determine validity based on validation level
        if validation_level == "strict":
            return high_severity_issues == 0 and medium_severity_issues == 0
        elif validation_level == "standard":
            return high_severity_issues == 0
        else:  # basic
            return high_severity_issues < 2

    async def _generate_compliance_checks(self, stage_results: Dict[str, Any]) -> Dict[str, bool]:
        """Generate compliance check summary"""

        compliance_checks = {}

        # Check each validation stage
        for stage_name, stage_result in stage_results.items():
            stage_passed = len(stage_result.get("issues", [])) == 0
            compliance_checks[stage_name] = stage_passed

        # Overall compliance
        all_passed = all(compliance_checks.values())
        compliance_checks["overall"] = all_passed

        return compliance_checks

    async def _extract_quality_metrics(self, stage_results: Dict[str, Any]) -> Dict[str, float]:
        """Extract quality metrics from validation results"""

        quality_metrics = {}

        # Extract scores from each stage
        for stage_name, stage_result in stage_results.items():
            if "score" in stage_result:
                quality_metrics[f"{stage_name}_score"] = stage_result["score"]

        # Add overall metrics
        scores = [stage_result.get("score", 0.5) for stage_result in stage_results.values()]
        if scores:
            quality_metrics["overall_quality"] = sum(scores) / len(scores)

        return quality_metrics

    async def _generate_validation_metadata(
        self,
        stage_results: Dict[str, Any],
        validation_level: str,
        validation_score: float
    ) -> Dict[str, Any]:
        """Generate validation metadata"""

        total_issues = sum(len(stage_result.get("issues", [])) for stage_result in stage_results.values())
        total_recommendations = sum(len(stage_result.get("recommendations", [])) for stage_result in stage_results.values())

        return {
            "validation_timestamp": datetime.utcnow().isoformat(),
            "validation_level": validation_level,
            "stages_executed": list(stage_results.keys()),
            "total_issues": total_issues,
            "total_recommendations": total_recommendations,
            "validation_score": validation_score,
            "pipeline_version": "1.0.0"
        }

__all__ = ["ValidationPipeline", "ValidationResult"]
