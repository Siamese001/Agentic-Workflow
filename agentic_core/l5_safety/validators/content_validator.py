#!/usr/bin/env python3
"""
Content Validator
Section 8: Safety Layer - Content validation and compliance checking
"""

from typing import Dict, Any, List, Optional, Union
import logging
import re

logger = logging.getLogger(__name__)

class ContentValidator:
    """Content validation and compliance checking for agentic systems"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.validation_rules = self.config.get("validation_rules", {})
        self.compliance_standards = self.config.get("compliance_standards", ["basic"])
        self.strict_mode = self.config.get("strict_mode", False)
        
        # Load validation patterns
        self.pii_patterns = self._load_pii_patterns()
        self.toxicity_patterns = self._load_toxicity_patterns()
        self.quality_patterns = self._load_quality_patterns()
    
    def validate_content(self, content: Any, content_type: str = "text", context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Comprehensive content validation"""
        try:
            validation_result = {
                "is_valid": True,
                "compliance_score": 1.0,
                "violations": [],
                "warnings": [],
                "recommendations": []
            }
            
            # Convert content to string for validation
            content_str = self._normalize_content(content)
            
            # PII validation
            pii_result = self._validate_pii(content_str)
            if not pii_result["passed"]:
                validation_result["is_valid"] = False
                validation_result["violations"].extend(pii_result["violations"])
                validation_result["compliance_score"] -= 0.3
            
            # Toxicity validation
            toxicity_result = self._validate_toxicity(content_str)
            if not toxicity_result["passed"]:
                validation_result["is_valid"] = False
                validation_result["violations"].extend(toxicity_result["violations"])
                validation_result["compliance_score"] -= 0.4
            
            # Quality validation
            quality_result = self._validate_quality(content_str, content_type)
            if not quality_result["passed"]:
                if self.strict_mode:
                    validation_result["is_valid"] = False
                    validation_result["violations"].extend(quality_result["violations"])
                    validation_result["compliance_score"] -= 0.2
                else:
                    validation_result["warnings"].extend(quality_result["violations"])
            
            # Format validation
            format_result = self._validate_format(content, content_type)
            if not format_result["passed"]:
                validation_result["is_valid"] = False
                validation_result["violations"].extend(format_result["violations"])
                validation_result["compliance_score"] -= 0.1
            
            # Ensure compliance score doesn't go negative
            validation_result["compliance_score"] = max(0.0, validation_result["compliance_score"])
            
            # Generate recommendations
            validation_result["recommendations"] = self._generate_validation_recommendations(validation_result)
            
            logger.info(f"Content validation: score={validation_result['compliance_score']:.2f}, valid={validation_result['is_valid']}")
            return validation_result
            
        except Exception as e:
            logger.error(f"Content validation failed: {e}")
            return {"is_valid": False, "error": str(e), "compliance_score": 0.0}
    
    def validate_resume_content(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate resume-specific content"""
        try:
            validation_result = {
                "is_valid": True,
                "compliance_score": 1.0,
                "resume_specific": {},
                "violations": [],
                "warnings": []
            }
            
            # Validate required sections
            required_sections = ["personal_info", "experience", "education", "skills"]
            missing_sections = [section for section in required_sections if section not in resume_data]
            
            if missing_sections:
                validation_result["is_valid"] = False
                validation_result["violations"].append(f"Missing required sections: {', '.join(missing_sections)}")
                validation_result["compliance_score"] -= 0.2
            
            # Validate experience section
            if "experience" in resume_data:
                exp_validation = self._validate_experience_section(resume_data["experience"])
                validation_result["resume_specific"]["experience"] = exp_validation
                if not exp_validation["valid"]:
                    validation_result["violations"].extend(exp_validation["issues"])
                    validation_result["compliance_score"] -= 0.1
            
            # Validate skills section
            if "skills" in resume_data:
                skills_validation = self._validate_skills_section(resume_data["skills"])
                validation_result["resume_specific"]["skills"] = skills_validation
                if not skills_validation["valid"]:
                    validation_result["violations"].extend(skills_validation["issues"])
                    validation_result["compliance_score"] -= 0.1
            
            # Check for PII in personal info
            if "personal_info" in resume_data:
                personal_str = str(resume_data["personal_info"])
                pii_result = self._validate_pii(personal_str)
                if not pii_result["passed"]:
                    validation_result["warnings"].extend(["PII detected in personal information"])
            
            logger.info(f"Resume validation: score={validation_result['compliance_score']:.2f}")
            return validation_result
            
        except Exception as e:
            logger.error(f"Resume validation failed: {e}")
            return {"is_valid": False, "error": str(e), "compliance_score": 0.0}
    
    def validate_outreach_content(self, outreach_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate outreach-specific content"""
        try:
            validation_result = {
                "is_valid": True,
                "compliance_score": 1.0,
                "outreach_specific": {},
                "violations": [],
                "warnings": []
            }
            
            # Validate message content
            if "message" in outreach_data:
                message_validation = self._validate_outreach_message(outreach_data["message"])
                validation_result["outreach_specific"]["message"] = message_validation
                if not message_validation["valid"]:
                    validation_result["violations"].extend(message_validation["issues"])
                    validation_result["compliance_score"] -= 0.2
            
            # Validate recipient information
            if "recipient" in outreach_data:
                recipient_validation = self._validate_recipient_info(outreach_data["recipient"])
                validation_result["outreach_specific"]["recipient"] = recipient_validation
                if not recipient_validation["valid"]:
                    validation_result["violations"].extend(recipient_validation["issues"])
                    validation_result["compliance_score"] -= 0.1
            
            # Check for spam indicators
            spam_result = self._validate_spam_indicators(str(outreach_data))
            if spam_result["detected"]:
                validation_result["warnings"].extend(["Potential spam indicators detected"])
                validation_result["compliance_score"] -= 0.1
            
            logger.info(f"Outreach validation: score={validation_result['compliance_score']:.2f}")
            return validation_result
            
        except Exception as e:
            logger.error(f"Outreach validation failed: {e}")
            return {"is_valid": False, "error": str(e), "compliance_score": 0.0}
    
    def _normalize_content(self, content: Any) -> str:
        """Normalize content to string for validation"""
        if isinstance(content, str):
            return content
        elif isinstance(content, dict):
            import json
            return json.dumps(content, ensure_ascii=False)
        elif isinstance(content, list):
            return " ".join(str(item) for item in content)
        else:
            return str(content)
    
    def _validate_pii(self, content: str) -> Dict[str, Any]:
        """Validate for PII (Personally Identifiable Information)"""
        violations = []
        
        for pattern_name, pattern in self.pii_patterns.items():
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                violations.append(f"PII detected: {pattern_name}")
                break  # Only report each type once
        
        return {
            "passed": len(violations) == 0,
            "violations": violations
        }
    
    def _validate_toxicity(self, content: str) -> Dict[str, Any]:
        """Validate for toxic content"""
        violations = []
        
        for pattern_name, pattern in self.toxicity_patterns.items():
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                violations.append(f"Toxic content detected: {pattern_name}")
                break
        
        return {
            "passed": len(violations) == 0,
            "violations": violations
        }
    
    def _validate_quality(self, content: str, content_type: str) -> Dict[str, Any]:
        """Validate content quality"""
        violations = []
        
        # Length validation
        if len(content) < 10:
            violations.append("Content too short")
        elif len(content) > 10000:
            violations.append("Content too long")
        
        # Character validation
        if content_type == "text":
            if re.search(r'[^\w\s\-\.\,\!\?\;\:\(\)\[\]\{\}\"\'\/\\]', content):
                violations.append("Contains invalid characters")
        
        # Structure validation
        if content_type == "resume":
            if not re.search(r'\b(experience|education|skills)\b', content, re.IGNORECASE):
                violations.append("Missing resume sections")
        
        return {
            "passed": len(violations) == 0,
            "violations": violations
        }
    
    def _validate_format(self, content: Any, content_type: str) -> Dict[str, Any]:
        """Validate content format"""
        violations = []
        
        if content_type == "json" and not isinstance(content, dict):
            violations.append("Content must be JSON/dict")
        elif content_type == "text" and not isinstance(content, str):
            violations.append("Content must be text/string")
        elif content_type == "resume" and not isinstance(content, dict):
            violations.append("Resume content must be structured data")
        
        return {
            "passed": len(violations) == 0,
            "violations": violations
        }
    
    def _validate_experience_section(self, experience: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate resume experience section"""
        issues = []
        
        if not isinstance(experience, list):
            return {"valid": False, "issues": ["Experience must be a list"]}
        
        for i, exp in enumerate(experience):
            if not isinstance(exp, dict):
                issues.append(f"Experience item {i} must be a dictionary")
                continue
            
            required_fields = ["title", "company", "dates"]
            missing_fields = [field for field in required_fields if field not in exp]
            if missing_fields:
                issues.append(f"Experience item {i} missing: {', '.join(missing_fields)}")
        
        return {"valid": len(issues) == 0, "issues": issues}
    
    def _validate_skills_section(self, skills: Union[List[str], Dict[str, Any]]) -> Dict[str, Any]:
        """Validate resume skills section"""
        issues = []
        
        if isinstance(skills, list):
            if len(skills) == 0:
                issues.append("Skills list cannot be empty")
        elif isinstance(skills, dict):
            if "technical" not in skills and "soft" not in skills:
                issues.append("Skills should include technical or soft skills")
        else:
            issues.append("Skills must be a list or dictionary")
        
        return {"valid": len(issues) == 0, "issues": issues}
    
    def _validate_outreach_message(self, message: str) -> Dict[str, Any]:
        """Validate outreach message"""
        issues = []
        
        if len(message) < 20:
            issues.append("Message too short for professional outreach")
        
        if len(message) > 1000:
            issues.append("Message too long for email outreach")
        
        # Check for proper greeting
        if not re.search(r'\b(hi|hello|dear)\b', message, re.IGNORECASE):
            issues.append("Missing professional greeting")
        
        # Check for proper closing
        if not re.search(r'\b(regards|sincerely|best)\b', message, re.IGNORECASE):
            issues.append("Missing professional closing")
        
        return {"valid": len(issues) == 0, "issues": issues}
    
    def _validate_recipient_info(self, recipient: Dict[str, Any]) -> Dict[str, Any]:
        """Validate recipient information"""
        issues = []
        
        required_fields = ["name", "email"]
        missing_fields = [field for field in required_fields if field not in recipient]
        if missing_fields:
            issues.append(f"Recipient missing: {', '.join(missing_fields)}")
        
        # Validate email format
        if "email" in recipient:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, recipient["email"]):
                issues.append("Invalid email format")
        
        return {"valid": len(issues) == 0, "issues": issues}
    
    def _validate_spam_indicators(self, content: str) -> Dict[str, Any]:
        """Validate for spam indicators"""
        spam_patterns = [
            r'\b(free|money|cash|prize|winner|congratulations)\b',
            r'\b(urgent|immediate|act\s+now|limited\s+time)\b',
            r'\b(click\s+here|buy\s+now|special\s+offer)\b',
            r'(\!{3,}|\${2,})'
        ]
        
        detected_count = 0
        for pattern in spam_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                detected_count += 1
        
        return {
            "detected": detected_count >= 2,
            "indicators": detected_count
        }
    
    def _generate_validation_recommendations(self, validation_result: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on validation results"""
        recommendations = []
        
        if validation_result["compliance_score"] < 0.5:
            recommendations.append("Content requires significant revision")
        
        if any("PII" in violation for violation in validation_result["violations"]):
            recommendations.append("Remove or redact personally identifiable information")
        
        if any("toxic" in violation.lower() for violation in validation_result["violations"]):
            recommendations.append("Review and remove inappropriate content")
        
        if any("format" in violation for violation in validation_result["violations"]):
            recommendations.append("Ensure content matches expected format")
        
        return recommendations
    
    def _load_pii_patterns(self) -> Dict[str, str]:
        """Load PII detection patterns"""
        return {
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "phone": r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
            "credit_card": r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
            "address": r'\b\d+\s+([A-Z][a-z]*\s)+[A-Z]{2}\s+\d{5}\b'
        }
    
    def _load_toxicity_patterns(self) -> Dict[str, str]:
        """Load toxicity detection patterns"""
        return {
            "profanity": r'\b(damn|hell|crap|shit|fuck|bitch)\b',
            "hate_speech": r'\b(hate|kill|die|stupid|idiot|retard)\b',
            "harassment": r'\b(loser|pathetic|worthless|useless)\b'
        }
    
    def _load_quality_patterns(self) -> Dict[str, str]:
        """Load quality validation patterns"""
        return {
            "repetition": r'(\b\w+\b)(\s+\1){2,}',
            "all_caps": r'([A-Z]{4,})',
            "excessive_punctuation": r'([!?]{3,})'
        }
    
    def get_validator_info(self) -> Dict[str, Any]:
        """Get content validator information"""
        return {
            "compliance_standards": self.compliance_standards,
            "strict_mode": self.strict_mode,
            "supported_content_types": ["text", "json", "resume", "outreach"],
            "validation_features": ["pii_detection", "toxicity_checking", "quality_validation", "format_validation"]
        }

def create_content_validator(config: Optional[Dict[str, Any]] = None) -> ContentValidator:
    """Factory function to create content validator instance"""
    return ContentValidator(config)

# Re-export components
__all__ = [
    'ContentValidator', 'create_content_validator'
]





