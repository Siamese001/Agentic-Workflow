#!/usr/bin/env python3
"""
Outreach Engine Seniority - Lift & Shift + Enhanced from LIC
Recipient classification and seniority mapping
"""

from typing import Dict, List, Any, Tuple
import re

from ..models import (
    SeniorityClassification, ValidationResult, ValidationSeverity
)


class RecipientClassifier:
    """Recipient seniority classifier - Enhanced from LIC"""
    
    def __init__(self, seniority_rules: Dict[str, Any]):
        self.classifier_config = seniority_rules.get("recipient_classifier_taxonomy", {})
        self.types = self.classifier_config.get("types", [])
        self.type_definitions = self.classifier_config.get("type_definitions", {})
    
    def classify_recipient(self, recipient_profile: Dict[str, Any]) -> SeniorityClassification:
        """Classify recipient into seniority type"""
        title = recipient_profile.get("title", "").lower()
        company = recipient_profile.get("company", "").lower()
        department = recipient_profile.get("department", "").lower()
        
        # Classification rules by priority
        classification_rules = []
        
        # C-Level classification
        if self._is_c_level(title):
            classification_rules.append(("C_LEVEL", 0.9, "Executive title detected"))
        
        # Executive classification
        elif self._is_executive(title):
            classification_rules.append(("EXECUTIVE", 0.8, "Executive title detected"))
        
        # Senior TA classification
        elif self._is_senior_technical(title, department):
            classification_rules.append(("SENIOR_TA", 0.8, "Senior technical title detected"))
        
        # Recruiter classification
        elif self._is_recruiter(title, department):
            classification_rules.append(("RECRUITER", 0.9, "Recruiter title detected"))
        
        # Default fallback
        if not classification_rules:
            classification_rules.append(("EXECUTIVE", 0.5, "Default classification"))
        
        # Select highest confidence classification
        best_type, confidence, reason = max(classification_rules, key=lambda x: x[1])
        
        return SeniorityClassification(
            recipient_type=best_type,
            confidence=confidence,
            classification_rules=[reason],
            title_analysis={
                "title": title,
                "company": company,
                "department": department,
                "keywords_found": self._extract_title_keywords(title)
            }
        )
    
    def _is_c_level(self, title: str) -> bool:
        """Check if title is C-level"""
        c_level_patterns = [
            r'\bceo\b', r'\bcto\b', r'\bcfo\b', r'\bcoo\b', r'\bcso\b', r'\bcmo\b',
            r'\bchief\s+\w+\s+officer\b', r'\bpresident\b', r'\bvice\s+president\b',
            r'\bvp\b', r'\bsvp\b', r'\bevp\b'
        ]
        
        return any(re.search(pattern, title, re.IGNORECASE) for pattern in c_level_patterns)
    
    def _is_executive(self, title: str) -> bool:
        """Check if title is executive level"""
        executive_patterns = [
            r'\bdirector\b', r'\bhead\s+of\b', r'\blead\b', r'\bmanager\b',
            r'\bsenior\s+manager\b', r'\bprincipal\b', r'\bsenior\s+director\b'
        ]
        
        return any(re.search(pattern, title, re.IGNORECASE) for pattern in executive_patterns)
    
    def _is_senior_technical(self, title: str, department: str) -> bool:
        """Check if title is senior technical"""
        senior_patterns = [
            r'\bsenior\b', r'\bprincipal\b', r'\blead\b', r'\bstaff\b',
            r'\barchitect\b', r'\bprincipal\s+engineer\b', r'\bsenior\s+engineer\b'
        ]
        
        technical_patterns = [
            r'\bengineer\b', r'\bdeveloper\b', r'\bprogrammer\b', r'\bsoftware\b',
            r'\bdata\s+scientist\b', r'\bdevops\b', r'\bsre\b', r'\bqa\b'
        ]
        
        is_senior = any(re.search(pattern, title, re.IGNORECASE) for pattern in senior_patterns)
        is_technical = any(re.search(pattern, title, re.IGNORECASE) for pattern in technical_patterns)
        
        return is_senior and is_technical
    
    def _is_recruiter(self, title: str, department: str) -> bool:
        """Check if title is recruiter/HR"""
        recruiter_patterns = [
            r'\brecruiter\b', r'\btalent\s+acquisition\b', r'\bsourcer\b',
            r'\bhr\b', r'\bhuman\s+resources\b', r'\bpeople\s+partner\b',
            r'\brecruitment\b', r'\bstaffing\b'
        ]
        
        return any(re.search(pattern, title, re.IGNORECASE) for pattern in recruiter_patterns)
    
    def _extract_title_keywords(self, title: str) -> List[str]:
        """Extract meaningful keywords from title"""
        # Remove common stop words and extract meaningful terms
        stop_words = {"a", "an", "the", "and", "or", "of", "in", "for", "to", "with", "at"}
        words = re.findall(r'\b\w+\b', title.lower())
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        return keywords
    
    def validate_classification(self, classification: SeniorityClassification) -> List[ValidationResult]:
        """Validate classification results"""
        validation_results = []
        
        # Check confidence threshold
        if classification.confidence < 0.6:
            validation_results.append(ValidationResult(
                rule_id="LOW_CLASSIFICATION_CONFIDENCE",
                passed=False,
                severity=ValidationSeverity.MEDIUM,
                message=f"Classification confidence {classification.confidence:.3f} below recommended threshold",
                details={
                    "confidence": classification.confidence,
                    "recipient_type": classification.recipient_type
                }
            ))
        
        # Check valid recipient type
        if classification.recipient_type not in self.types:
            validation_results.append(ValidationResult(
                rule_id="INVALID_RECIPIENT_TYPE",
                passed=False,
                severity=ValidationSeverity.HIGH,
                message=f"Invalid recipient type: {classification.recipient_type}",
                details={
                    "recipient_type": classification.recipient_type,
                    "valid_types": self.types
                }
            ))
        
        return validation_results


class SeniorityMapper:
    """Seniority mapping to outreach parameters - Lift & Shift from LIC"""
    
    def __init__(self, seniority_rules: Dict[str, Any]):
        self.seniority_rules = seniority_rules
        self.type_definitions = seniority_rules.get("recipient_classifier_taxonomy", {}).get("type_definitions", {})
    
    def map_to_outreach_parameters(self, recipient_type: str) -> Dict[str, Any]:
        """Map recipient type to outreach parameters"""
        type_config = self.type_definitions.get(recipient_type, {})
        
        return {
            "recipient_type": recipient_type,
            "message_tone": type_config.get("message_tone", "professional"),
            "formality_level": type_config.get("formality_level", "medium"),
            "preferred_verbs": type_config.get("preferred_verbs", []),
            "focus_areas": type_config.get("focus_areas", []),
            "communication_style": type_config.get("communication_style", "direct"),
            "expected_response_time": type_config.get("expected_response_time", "standard"),
            "optimal_send_times": type_config.get("optimal_send_times", []),
            "content_preferences": type_config.get("content_preferences", {})
        }
    
    def get_personalization_strategy(self, recipient_type: str) -> Dict[str, Any]:
        """Get personalization strategy for recipient type"""
        strategies = {
            "C_LEVEL": {
                "approach": "strategic_value",
                "length_preference": "concise",
                "data_requirements": "business_metrics_only",
                "tone_guidance": "peer_to_peer_executive",
                "personalization_depth": "light"
            },
            "EXECUTIVE": {
                "approach": "operational_impact",
                "length_preference": "balanced",
                "data_requirements": "team_metrics",
                "tone_guidance": "professional_collaborative",
                "personalization_depth": "moderate"
            },
            "SENIOR_TA": {
                "approach": "technical_peer",
                "length_preference": "detailed",
                "data_requirements": "technical_details",
                "tone_guidance": "consultative_expert",
                "personalization_depth": "deep"
            },
            "RECRUITER": {
                "approach": "skill_alignment",
                "length_preference": "efficient",
                "data_requirements": "skills_experience",
                "tone_guidance": "warm_professional",
                "personalization_depth": "moderate"
            }
        }
        
        return strategies.get(recipient_type, strategies["EXECUTIVE"])


class SeniorityEngine:
    """Main seniority engine - Lift & Shift + Enhanced from LIC"""
    
    def __init__(self, lic_capabilities: Dict[str, Any]):
        self.seniority_rules = lic_capabilities.get("seniority_rules", {})
        self.classifier = RecipientClassifier(self.seniority_rules)
        self.mapper = SeniorityMapper(self.seniority_rules)
    
    def analyze_recipient_seniority(
        self, 
        recipient_profile: Dict[str, Any]
    ) -> Tuple[SeniorityClassification, Dict[str, Any], List[ValidationResult]]:
        """Complete seniority analysis"""
        validation_results = []
        
        # Classify recipient
        classification = self.classifier.classify_recipient(recipient_profile)
        
        # Validate classification
        classification_validations = self.classifier.validate_classification(classification)
        validation_results.extend(classification_validations)
        
        # Map to outreach parameters
        outreach_params = self.mapper.map_to_outreach_parameters(classification.recipient_type)
        
        # Get personalization strategy
        personalization_strategy = self.mapper.get_personalization_strategy(classification.recipient_type)
        
        # Combine results
        analysis_result = {
            "classification": classification,
            "outreach_parameters": outreach_params,
            "personalization_strategy": personalization_strategy
        }
        
        return classification, analysis_result, validation_results
    
    def enhance_routing_with_seniority(
        self,
        recipient_profile: Dict[str, Any],
        base_route: str
    ) -> Dict[str, Any]:
        """Enhance routing decision with seniority analysis"""
        classification, analysis_result, _ = self.analyze_recipient_seniority(recipient_profile)
        
        # Route adjustments based on seniority
        route_adjustments = {}
        
        if classification.recipient_type == "C_LEVEL":
            route_adjustments["subject_line_priority"] = "high"
            route_adjustments["length_preference"] = "concise"
            route_adjustments["formality_boost"] = True
        
        elif classification.recipient_type == "RECRUITER":
            route_adjustments["response_time_expectation"] = "fast"
            route_adjustments["skills_highlight_priority"] = "high"
        
        elif classification.recipient_type == "SENIOR_TA":
            route_adjustments["technical_detail_allowed"] = True
            route_adjustments["evidence_requirement"] = "strong"
        
        return {
            "base_route": base_route,
            "seniority_enhanced_route": route_adjustments,
            "classification": classification.recipient_type,
            "confidence": classification.confidence
        }
    
    def get_seniority_guidance(self, recipient_type: str) -> Dict[str, Any]:
        """Get comprehensive guidance for recipient type"""
        outreach_params = self.mapper.map_to_outreach_parameters(recipient_type)
        personalization_strategy = self.mapper.get_personalization_strategy(recipient_type)
        
        return {
            "recipient_type": recipient_type,
            "outreach_parameters": outreach_params,
            "personalization_strategy": personalization_strategy,
            "recommended_approach": personalization_strategy.get("approach", "professional"),
            "tone_guidance": outreach_params.get("message_tone", "professional"),
            "formality_level": outreach_params.get("formality_level", "medium")
        }
    
    def validate_seniority_analysis(self, analysis_result: Dict[str, Any]) -> List[ValidationResult]:
        """Validate complete seniority analysis"""
        validation_results = []
        
        classification = analysis_result.get("classification")
        if not classification:
            validation_results.append(ValidationResult(
                rule_id="MISSING_CLASSIFICATION",
                passed=False,
                severity=ValidationSeverity.CRITICAL,
                message="Seniority classification is missing",
                details={}
            ))
            return validation_results
        
        # Validate confidence
        if classification.confidence < 0.5:
            validation_results.append(ValidationResult(
                rule_id="VERY_LOW_CONFIDENCE",
                passed=False,
                severity=ValidationSeverity.HIGH,
                message=f"Classification confidence {classification.confidence:.3f} is very low",
                details={"confidence": classification.confidence}
            ))
        
        # Validate outreach parameters
        outreach_params = analysis_result.get("outreach_parameters", {})
        if not outreach_params.get("message_tone"):
            validation_results.append(ValidationResult(
                rule_id="MISSING_MESSAGE_TONE",
                passed=False,
                severity=ValidationSeverity.MEDIUM,
                message="Message tone not specified in outreach parameters",
                details={}
            ))
        
        return validation_results
    
    def get_classification_summary(self) -> Dict[str, Any]:
        """Get summary of classification system"""
        return {
            "supported_types": self.classifier.types,
            "type_definitions": self.type_definitions,
            "classification_method": "rule_based_with_confidence_scoring",
            "confidence_threshold": 0.6,
            "default_fallback": "EXECUTIVE"
        }
