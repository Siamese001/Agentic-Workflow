#!/usr/bin/env python3
"""
Outreach Engine Validation - Lift & Shift + Enhanced from LIC
Validation engine, entity grounding, and error code registry
"""

from typing import Dict, List, Optional, Any, Set, Tuple
import re
from datetime import datetime

from ..models import (
    ValidationResult, ValidationSeverity, ValidationRule, 
    EntityConstraint, ValidationError
)


class ErrorCodeRegistry:
    """Error code registry for LIC validation rules - Lift & Shift"""
    
    def __init__(self):
        self.error_codes = {
            # Content validation errors (LIC-E001 to LIC-E005)
            "LIC-E001": ValidationRule(
                rule_id="LIC-E001",
                name="Forbidden Verb Usage",
                phase="POST_GENERATION",
                description="Corporate clichés and forbidden verbs detected",
                enforcement="SOFT_REJECT",
                severity=ValidationSeverity.MEDIUM
            ),
            "LIC-E002": ValidationRule(
                rule_id="LIC-E002", 
                name="Filler Phrase Usage",
                phase="POST_GENERATION",
                description="Weak filler phrases detected",
                enforcement="SOFT_REJECT",
                severity=ValidationSeverity.MEDIUM
            ),
            "LIC-E003": ValidationRule(
                rule_id="LIC-E003",
                name="Placeholder Text Detected", 
                phase="POST_GENERATION",
                description="Placeholder text found in message",
                enforcement="HARD_BLOCK",
                severity=ValidationSeverity.CRITICAL
            ),
            "LIC-E004": ValidationRule(
                rule_id="LIC-E004",
                name="Word Count Violation",
                phase="POST_GENERATION", 
                description="Message word count outside route constraints",
                enforcement="HARD_BLOCK",
                severity=ValidationSeverity.HIGH
            ),
            "LIC-E005": ValidationRule(
                rule_id="LIC-E005",
                name="Character Limit Exceeded",
                phase="POST_GENERATION",
                description="Message exceeds character limit",
                enforcement="HARD_BLOCK", 
                severity=ValidationSeverity.CRITICAL
            ),
            
            # Entity grounding errors (LIC-E006 to LIC-E010)
            "LIC-E006": ValidationRule(
                rule_id="LIC-E006",
                name="Company Name Validation Failed",
                phase="PRE_GENERATION",
                description="Company not in validated whitelist",
                enforcement="HARD_BLOCK",
                severity=ValidationSeverity.CRITICAL
            ),
            "LIC-E007": ValidationRule(
                rule_id="LIC-E007", 
                name="Entity Cross-Reference Failed",
                phase="POST_GENERATION",
                description="Proper noun not found in RAG sources",
                enforcement="REJECT",
                severity=ValidationSeverity.HIGH
            ),
            "LIC-E008": ValidationRule(
                rule_id="LIC-E008",
                name="Metric Source Validation Failed", 
                phase="POST_GENERATION",
                description="Metric without source mapping",
                enforcement="REJECT",
                severity=ValidationSeverity.HIGH
            ),
            "LIC-E009": ValidationRule(
                rule_id="LIC-E009",
                name="Role Drift Detected",
                phase="POST_GENERATION",
                description="Team description doesn't match source",
                enforcement="REJECT", 
                severity=ValidationSeverity.HIGH
            ),
            "LIC-E010": ValidationRule(
                rule_id="LIC-E010",
                name="Team Whitelist Violation",
                phase="DURING_GENERATION",
                description="Generic team terms used",
                enforcement="SOFT_REJECT",
                severity=ValidationSeverity.MEDIUM
            ),
            
            # Structural and format errors (LIC-E011 to LIC-E015)
            "LIC-E011": ValidationRule(
                rule_id="LIC-E011",
                name="Subject Line Missing",
                phase="POST_GENERATION",
                description="Subject line required but not found",
                enforcement="HARD_BLOCK",
                severity=ValidationSeverity.CRITICAL
            ),
            "LIC-E012": ValidationRule(
                rule_id="LIC-E012",
                name="Subject Line Format Invalid",
                phase="POST_GENERATION", 
                description="Subject line doesn't meet format requirements",
                enforcement="SOFT_REJECT",
                severity=ValidationSeverity.MEDIUM
            ),
            "LIC-E013": ValidationRule(
                rule_id="LIC-E013",
                name="Greeting Format Invalid",
                phase="POST_GENERATION",
                description="Greeting doesn't follow format rules",
                enforcement="SOFT_REJECT",
                severity=ValidationSeverity.LOW
            ),
            "LIC-E014": ValidationRule(
                rule_id="LIC-E014", 
                name="Signature Format Invalid",
                phase="POST_GENERATION",
                description="Signature missing required elements",
                enforcement="SOFT_REJECT",
                severity=ValidationSeverity.LOW
            ),
            "LIC-E015": ValidationRule(
                rule_id="LIC-E015",
                name="Unicode Compliance Failed",
                phase="POST_GENERATION",
                description="Unicode characters need normalization",
                enforcement="AUTO_FIX",
                severity=ValidationSeverity.LOW
            )
        }
    
    def get_error_rule(self, error_code: str) -> Optional[ValidationRule]:
        """Get validation rule for error code"""
        return self.error_codes.get(error_code)
    
    def get_all_error_codes(self) -> List[str]:
        """Get all registered error codes"""
        return list(self.error_codes.keys())


class EntityGroundingFramework:
    """Entity grounding framework - Lift & Shift from LIC"""
    
    def __init__(self, scenario_rules: Dict[str, Any]):
        self.entity_grounding = scenario_rules.get("entity_grounding_framework", {})
        self.pre_generation_extractor = PreGenerationExtractor(self.entity_grounding)
        self.team_whitelist = TeamWhitelist(self.entity_grounding)
        self.entity_validator = EntityValidator(self.entity_grounding)
    
    def validate_entity_grounding(
        self, 
        message: str, 
        rag_sources: List[Dict[str, Any]],
        sender_profile: Dict[str, Any]
    ) -> List[ValidationResult]:
        """Comprehensive entity grounding validation"""
        all_results = []
        
        # Pre-generation extraction validation
        all_results.extend(self.pre_generation_extractor.validate_entities(message, sender_profile))
        
        # Team whitelist validation
        all_results.extend(self.team_whitelist.validate_team_mentions(message, rag_sources))
        
        # Entity cross-reference validation
        all_results.extend(self.entity_validator.validate_entities(message, rag_sources))
        
        return all_results


class PreGenerationExtractor:
    """Pre-generation entity extraction - Lift & Shift from LIC"""
    
    def __init__(self, entity_grounding: Dict[str, Any]):
        self.extraction_config = entity_grounding.get("pre_generation_extraction", {})
        self.targets = self.extraction_config.get("targets", [])
    
    def extract_critical_entities(self, sender_profile: Dict[str, Any]) -> Dict[str, Set[str]]:
        """Extract and lock critical entities before generation"""
        extracted_entities = {}
        
        # Extract companies from sender history
        if "sender_employment_history" in self.targets:
            companies = set()
            for exp in sender_profile.get("experience", []):
                company = exp.get("company", "")
                if company:
                    companies.add(company)
            extracted_entities["validated_companies"] = companies
        
        # Extract role titles
        if "role_titles" in self.targets:
            roles = set()
            for exp in sender_profile.get("experience", []):
                title = exp.get("title", "")
                if title:
                    roles.add(title)
            extracted_entities["validated_roles"] = roles
        
        # Extract metrics with sources
        if "metrics_with_sources" in self.targets:
            metrics = set()
            for exp in sender_profile.get("experience", []):
                # Extract numbers and their context
                text = exp.get("description", "")
                metric_matches = re.findall(r'(\d+%|\d+x|\d+\.?\d*\s*(?:million|billion|thousand))', text, re.IGNORECASE)
                metrics.update(metric_matches)
            extracted_entities["validated_metrics"] = metrics
        
        return extracted_entities
    
    def validate_entities(self, message: str, sender_profile: Dict[str, Any]) -> List[ValidationResult]:
        """Validate that message only uses extracted entities"""
        validation_results = []
        extracted_entities = self.extract_critical_entities(sender_profile)
        
        # Check company references
        if "validated_companies" in extracted_entities:
            message_companies = self._extract_companies_from_text(message)
            unauthorized_companies = message_companies - extracted_entities["validated_companies"]
            
            if unauthorized_companies:
                validation_results.append(ValidationResult(
                    rule_id="LIC-E006",
                    passed=False,
                    severity=ValidationSeverity.CRITICAL,
                    message=f"Unauthorized companies mentioned: {', '.join(unauthorized_companies)}",
                    details={"unauthorized_companies": list(unauthorized_companies)}
                ))
        
        return validation_results
    
    def _extract_companies_from_text(self, text: str) -> Set[str]:
        """Extract company names from text"""
        # Simple pattern matching for capitalized words that might be companies
        company_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+(?:Inc|Corp|LLC|Ltd|Co))?\b'
        matches = re.findall(company_pattern, text)
        return set(matches)


class TeamWhitelist:
    """Team whitelist validation - Enhanced from LIC"""
    
    def __init__(self, entity_grounding: Dict[str, Any]):
        self.whitelist_config = entity_grounding.get("team_whitelist", {})
        self.similarity_threshold = self.whitelist_config.get("validation", {}).get("threshold", 0.92)
    
    def validate_team_mentions(self, message: str, rag_sources: List[Dict[str, Any]]) -> List[ValidationResult]:
        """Validate team descriptions against whitelist"""
        validation_results = []
        
        # Extract team descriptions from message
        team_phrases = self._extract_team_phrases(message)
        
        # Check each phrase against whitelist
        for phrase in team_phrases:
            similarity = self._calculate_similarity(phrase, rag_sources)
            
            if similarity < self.similarity_threshold:
                validation_results.append(ValidationResult(
                    rule_id="LIC-E010",
                    passed=False,
                    severity=ValidationSeverity.MEDIUM,
                    message=f"Team description too generic: '{phrase}'",
                    details={"phrase": phrase, "similarity": similarity, "threshold": self.similarity_threshold}
                ))
        
        return validation_results
    
    def _extract_team_phrases(self, text: str) -> List[str]:
        """Extract team-related phrases from message"""
        # Look for patterns like "my team", "our team", "team of X", etc.
        team_patterns = [
            r'(?:my|our|the)\s+team\s+(?:of\s+\d+|of\s+\w+|\w+(?:\s+\w+)*)',
            r'team\s+(?:of\s+\d+|of\s+\w+|\w+(?:\s+\w+)*)',
            r'(?:led|managed|built)\s+(?:a\s+)?team\s+(?:of\s+\d+|\w+)'
        ]
        
        phrases = []
        for pattern in team_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            phrases.extend(matches)
        
        return phrases
    
    def _calculate_similarity(self, phrase: str, rag_sources: List[Dict[str, Any]]) -> float:
        """Calculate semantic similarity between phrase and RAG sources"""
        # Simplified similarity calculation - in real implementation would use embeddings
        max_similarity = 0.0
        
        for source in rag_sources:
            content = source.get("content", "").lower()
            phrase_lower = phrase.lower()
            
            # Simple word overlap similarity
            phrase_words = set(phrase_lower.split())
            content_words = set(content.split())
            
            if phrase_words and content_words:
                overlap = len(phrase_words & content_words)
                union = len(phrase_words | content_words)
                similarity = overlap / union if union > 0 else 0.0
                max_similarity = max(max_similarity, similarity)
        
        return max_similarity


class EntityValidator:
    """Entity cross-reference validation - Lift & Shift from LIC"""
    
    def __init__(self, entity_grounding: Dict[str, Any]):
        self.constraints = entity_grounding.get("generation_constraints", {})
    
    def validate_entities(self, message: str, rag_sources: List[Dict[str, Any]]) -> List[ValidationResult]:
        """Validate that all entities exist in RAG sources"""
        validation_results = []
        
        # Extract proper nouns/entities from message
        entities = self._extract_entities(message)
        
        # Check each entity against RAG sources
        for entity in entities:
            if not self._entity_in_sources(entity, rag_sources):
                validation_results.append(ValidationResult(
                    rule_id="LIC-E007",
                    passed=False,
                    severity=ValidationSeverity.HIGH,
                    message=f"Entity not found in RAG sources: '{entity}'",
                    details={"entity": entity, "source_count": len(rag_sources)}
                ))
        
        return validation_results
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract proper nouns and entities from text"""
        # Simple pattern for capitalized words/phrases
        entity_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
        return re.findall(entity_pattern, text)
    
    def _entity_in_sources(self, entity: str, rag_sources: List[Dict[str, Any]]) -> bool:
        """Check if entity exists in RAG sources"""
        entity_lower = entity.lower()
        
        for source in rag_sources:
            content = source.get("content", "").lower()
            if entity_lower in content:
                return True
        
        return False


class ValidationEngine:
    """Main validation engine - Lift & Shift + Enhanced from LIC"""
    
    def __init__(self, lic_capabilities: Dict[str, Any]):
        self.error_registry = ErrorCodeRegistry()
        self.entity_grounding = EntityGroundingFramework(lic_capabilities.get("scenario_rules", {}))
    
    def validate_message(
        self,
        message: str,
        rag_sources: List[Dict[str, Any]],
        sender_profile: Dict[str, Any],
        validation_rules: Optional[List[str]] = None
    ) -> List[ValidationResult]:
        """Comprehensive message validation"""
        all_results = []
        
        # Entity grounding validation
        all_results.extend(self.entity_grounding.validate_entity_grounding(message, rag_sources, sender_profile))
        
        # Apply specific validation rules if provided
        if validation_rules:
            for rule_id in validation_rules:
                rule = self.error_registry.get_error_rule(rule_id)
                if rule:
                    # Apply rule-specific validation
                    rule_results = self._apply_validation_rule(rule, message, rag_sources, sender_profile)
                    all_results.extend(rule_results)
        
        return all_results
    
    def _apply_validation_rule(
        self,
        rule: ValidationRule,
        message: str,
        rag_sources: List[Dict[str, Any]],
        sender_profile: Dict[str, Any]
    ) -> List[ValidationResult]:
        """Apply a specific validation rule"""
        # This would contain rule-specific validation logic
        # For now, return empty list as individual rules are handled by components
        return []
    
    def get_validation_summary(self, validation_results: List[ValidationResult]) -> Dict[str, Any]:
        """Get summary of validation results"""
        passed_count = sum(1 for r in validation_results if r.passed)
        failed_count = len(validation_results) - passed_count
        
        severity_counts = {}
        for result in validation_results:
            severity = result.severity.value
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        return {
            "total_validations": len(validation_results),
            "passed": passed_count,
            "failed": failed_count,
            "severity_breakdown": severity_counts,
            "can_proceed": failed_count == 0 or all(r.severity != ValidationSeverity.CRITICAL for r in validation_results if not r.passed)
        }





