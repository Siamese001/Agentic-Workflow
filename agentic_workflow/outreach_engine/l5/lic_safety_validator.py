from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class SafetyViolation:
    error_code: str
    severity: str
    description: str
    category: str
    blocking: bool

@dataclass
class SafetyResult:
    is_safe: bool
    violations: List[SafetyViolation]
    safety_score: float
    recommendations: List[str]

class LICSafetyValidator:
    def __init__(self, validator_plan: Dict[str, Any], constraint_plan: Dict[str, Any]):
        self.validators = validator_plan
        self.constraints = constraint_plan
        
    def validate_forbidden_content(self, text: str) -> List[SafetyViolation]:
        violations = []
        
        forbidden_verbs = self.constraints["forbidden_verbs"]
        for verb in forbidden_verbs:
            if verb.lower() in text.lower():
                violations.append(SafetyViolation(
                    error_code="LIC-E008",
                    severity="BLOCKING",
                    description=f"Forbidden corporate verb detected: {verb}",
                    category="content_cleanliness",
                    blocking=True
                ))
        
        filler_patterns = self.constraints["filler_patterns"]
        for pattern in filler_patterns:
            import re
            if re.search(pattern, text, re.IGNORECASE):
                violations.append(SafetyViolation(
                    error_code="LIC-E009",
                    severity="WARNING",
                    description=f"Weak filler phrase detected: {pattern}",
                    category="content_cleanliness",
                    blocking=False
                ))
                
        return violations
    
    def validate_ascii_hygiene(self, text: str) -> List[SafetyViolation]:
        violations = []
        ascii_rules = self.constraints["ascii_rules"]
        
        if ascii_rules.get("no_smart_quotes", True):
            if "'" in text or '"' in text:
                violations.append(SafetyViolation(
                    error_code="LIC-E007",
                    severity="BLOCKING",
                    description="Non-ASCII characters detected - smart quotes",
                    category="ascii_hygiene",
                    blocking=True
                ))
                
        if ascii_rules.get("no_em_dashes", True):
            if "—" in text:
                violations.append(SafetyViolation(
                    error_code="LIC-E007",
                    severity="BLOCKING",
                    description="Non-ASCII characters detected - em dashes",
                    category="ascii_hygiene",
                    blocking=True
                ))
                
        if ascii_rules.get("no_unicode_bullets", True):
            if "•" in text or "○" in text:
                violations.append(SafetyViolation(
                    error_code="LIC-E007",
                    severity="BLOCKING",
                    description="Non-ASCII characters detected - unicode bullets",
                    category="ascii_hygiene",
                    blocking=True
                ))
                
        return violations
    
    def validate_message_structure(self, draft_output: Dict[str, Any], message_context: Dict[str, Any]) -> List[SafetyViolation]:
        violations = []
        
        message_body = draft_output.get("message_body", "")
        word_count = draft_output.get("word_count", 0)
        
        if word_count < 50:
            violations.append(SafetyViolation(
                error_code="LIC-E005",
                severity="BLOCKING",
                description="Message too short - minimum 50 words required",
                category="structural_validation",
                blocking=True
            ))
            
        recipient = message_context.get("recipient", {})
        title = recipient.get("title", "")
        
        if title and title.lower() not in message_body.lower():
            violations.append(SafetyViolation(
                error_code="LIC-E005",
                severity="WARNING",
                description="Job title not in first 50 words",
                category="structural_validation",
                blocking=False
            ))
            
        company = recipient.get("company", "")
        if company and company.lower() not in message_body.lower():
            violations.append(SafetyViolation(
                error_code="LIC-E006",
                severity="BLOCKING",
                description="Company name misspelled or missing",
                category="structural_validation",
                blocking=True
            ))
            
        return violations
    
    def validate_confidence_requirements(self, insight_output: Dict[str, Any]) -> List[SafetyViolation]:
        violations = []
        
        per_claim_scores = insight_output.get("per_claim_scores", [])
        for i, claim_score in enumerate(per_claim_scores):
            score = claim_score.get("score", 0.0)
            if score < 0.8:
                violations.append(SafetyViolation(
                    error_code="LIC-E002",
                    severity="BLOCKING",
                    description=f"Per-claim confidence below threshold - Claim {i+1}: {score:.3f}",
                    category="confidence_validation",
                    blocking=True
                ))
        
        aggregate_confidence = insight_output.get("aggregate_confidence", 0.0)
        if aggregate_confidence < 0.95:
            violations.append(SafetyViolation(
                error_code="LIC-VAL-CONF-001",
                severity="BLOCKING",
                description=f"Aggregate confidence below threshold - {aggregate_confidence:.3f}",
                category="confidence_validation",
                blocking=True
            ))
            
        return violations
    
    def validate_signal_quality(self, research_output: Dict[str, Any]) -> List[SafetyViolation]:
        violations = []
        
        signal_score = research_output.get("signal_score", 0.0)
        if signal_score < 0.7:
            violations.append(SafetyViolation(
                error_code="LIC-E011",
                severity="BLOCKING",
                description=f"Signal quality score below threshold - {signal_score:.3f}",
                category="signal_validation",
                blocking=True
            ))
            
        return violations
    
    def validate_cta_safety(self, cta_output: Dict[str, Any], message_context: Dict[str, Any]) -> List[SafetyViolation]:
        violations = []
        
        cta_text = cta_output.get("final_cta", "")
        
        if "?" not in cta_text:
            violations.append(SafetyViolation(
                error_code="LIC-E010",
                severity="BLOCKING",
                description="CTA must be a question",
                category="cta_validation",
                blocking=True
            ))
            
        forbidden_phrases = ["let me know", "feel free", "don't hesitate"]
        for phrase in forbidden_phrases:
            if phrase in cta_text.lower():
                violations.append(SafetyViolation(
                    error_code="LIC-E010",
                    severity="WARNING",
                    description=f"CTA contains forbidden phrase: {phrase}",
                    category="cta_validation",
                    blocking=False
                ))
                
        word_count = len(cta_text.split())
        if word_count > 25:
            violations.append(SafetyViolation(
                error_code="LIC-E010",
                severity="WARNING",
                description=f"CTA too long: {word_count} words",
                category="cta_validation",
                blocking=False
            ))
            
        return violations
    
    def calculate_safety_score(self, violations: List[SafetyViolation]) -> float:
        if not violations:
            return 1.0
            
        blocking_count = sum(1 for v in violations if v.blocking)
        warning_count = sum(1 for v in violations if not v.blocking)
        
        blocking_penalty = blocking_count * 0.3
        warning_penalty = warning_count * 0.1
        
        score = max(0.0, 1.0 - blocking_penalty - warning_penalty)
        return score
    
    def generate_recommendations(self, violations: List[SafetyViolation]) -> List[str]:
        recommendations = []
        
        for violation in violations:
            if violation.category == "content_cleanliness":
                if "verb" in violation.description:
                    recommendations.append("Replace corporate jargon with simpler, more direct language")
                elif "filler" in violation.description:
                    recommendations.append("Remove weak filler phrases to strengthen message impact")
                    
            elif violation.category == "ascii_hygiene":
                recommendations.append("Convert all special characters to standard ASCII format")
                
            elif violation.category == "structural_validation":
                if "short" in violation.description:
                    recommendations.append("Expand message content to meet minimum word count requirements")
                elif "title" in violation.description:
                    recommendations.append("Include recipient's job title in the message body")
                elif "company" in violation.description:
                    recommendations.append("Ensure company name is correctly spelled and included")
                    
            elif violation.category == "confidence_validation":
                recommendations.append("Strengthen claims with additional supporting evidence")
                
            elif violation.category == "signal_validation":
                recommendations.append("Improve research quality to increase signal score")
                
            elif violation.category == "cta_validation":
                if "question" in violation.description:
                    recommendations.append("Rewrite CTA as a clear question")
                elif "long" in violation.description:
                    recommendations.append("Shorten CTA to be more concise and direct")
                    
        return list(set(recommendations))
    
    def execute_comprehensive_validation(self, draft_output: Dict[str, Any], insight_output: Dict[str, Any], research_output: Dict[str, Any], cta_output: Dict[str, Any], message_context: Dict[str, Any]) -> SafetyResult:
        all_violations = []
        
        full_text = f"{draft_output.get('greeting', '')} {draft_output.get('message_body', '')} {cta_output.get('final_cta', '')} {draft_output.get('signature', '')}"
        
        all_violations.extend(self.validate_forbidden_content(full_text))
        all_violations.extend(self.validate_ascii_hygiene(full_text))
        all_violations.extend(self.validate_message_structure(draft_output, message_context))
        all_violations.extend(self.validate_confidence_requirements(insight_output))
        all_violations.extend(self.validate_signal_quality(research_output))
        all_violations.extend(self.validate_cta_safety(cta_output, message_context))
        
        is_safe = not any(v.blocking for v in all_violations)
        safety_score = self.calculate_safety_score(all_violations)
        recommendations = self.generate_recommendations(all_violations)
        
        return SafetyResult(
            is_safe=is_safe,
            violations=all_violations,
            safety_score=safety_score,
            recommendations=recommendations
        )
