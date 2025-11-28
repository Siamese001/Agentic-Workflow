from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class ValidationOutput:
    is_valid: bool
    error_codes: List[str]
    validation_results: Dict[str, Any]
    blocked_violations: List[str]
    warning_violations: List[str]

class LIC_K5_Validation:
    def __init__(self, validator_plan: Dict[str, Any], constraint_plan: Dict[str, Any]):
        self.validators = validator_plan
        self.constraints = constraint_plan
        
    def validate_ascii_hygiene(self, text: str) -> List[str]:
        violations = []
        ascii_rules = self.constraints["ascii_rules"]
        
        if ascii_rules.get("no_smart_quotes", True):
            if "'" in text or '"' in text:
                violations.append("LIC-E007: Non-ASCII characters detected - smart quotes")
                
        if ascii_rules.get("no_em_dashes", True):
            if "—" in text:
                violations.append("LIC-E007: Non-ASCII characters detected - em dashes")
                
        if ascii_rules.get("no_unicode_bullets", True):
            if "•" in text or "○" in text:
                violations.append("LIC-E007: Non-ASCII characters detected - unicode bullets")
                
        return violations
    
    def validate_content_cleanliness(self, text: str) -> List[str]:
        violations = []
        
        forbidden_verbs = self.constraints["forbidden_verbs"]
        for verb in forbidden_verbs:
            if verb.lower() in text.lower():
                violations.append(f"LIC-E008: Forbidden corporate verb detected - {verb}")
        
        filler_patterns = self.constraints["filler_patterns"]
        for pattern in filler_patterns:
            import re
            if re.search(pattern, text, re.IGNORECASE):
                violations.append(f"LIC-E009: Weak filler phrase detected - {pattern}")
                
        return violations
    
    def validate_structural_requirements(self, draft_output: Dict[str, Any], message_context: Dict[str, Any]) -> List[str]:
        violations = []
        
        message_body = draft_output.get("message_body", "")
        word_count = draft_output.get("word_count", 0)
        
        if word_count < 50:
            violations.append("LIC-E005: Message too short - minimum 50 words required")
            
        recipient = message_context.get("recipient", {})
        title = recipient.get("title", "")
        
        if title and title.lower() not in message_body.lower():
            violations.append("LIC-E005: Job title not in first 50 words")
            
        company = recipient.get("company", "")
        if company and company.lower() not in message_body.lower():
            violations.append("LIC-E006: Company name misspelled or missing")
            
        return violations
    
    def validate_confidence_requirements(self, insight_output: Dict[str, Any]) -> List[str]:
        violations = []
        
        per_claim_scores = insight_output.get("per_claim_scores", [])
        for i, claim_score in enumerate(per_claim_scores):
            score = claim_score.get("score", 0.0)
            if score < 0.8:
                violations.append(f"LIC-E002: Per-claim confidence below threshold - Claim {i+1}: {score:.3f}")
        
        aggregate_confidence = insight_output.get("aggregate_confidence", 0.0)
        if aggregate_confidence < 0.95:
            violations.append(f"LIC-VAL-CONF-001: Aggregate confidence below threshold - {aggregate_confidence:.3f}")
            
        return violations
    
    def validate_signal_quality(self, research_output: Dict[str, Any]) -> List[str]:
        violations = []
        
        signal_score = research_output.get("signal_score", 0.0)
        if signal_score < 0.7:
            violations.append(f"LIC-E011: Signal quality score below threshold - {signal_score:.3f}")
            
        return violations
    
    def categorize_violations(self, violations: List[str]) -> Dict[str, List[str]]:
        blocked = []
        warnings = []
        
        for violation in violations:
            if "LIC-E001" in violation or "LIC-E002" in violation or "LIC-E003" in violation:
                blocked.append(violation)
            elif "LIC-E012" in violation or "LIC-E013" in violation or "LIC-E014" in violation or "LIC-E015" in violation:
                blocked.append(violation)
            elif "LIC-VAL-CONF-001" in violation:
                blocked.append(violation)
            else:
                warnings.append(violation)
                
        return {"blocked": blocked, "warnings": warnings}
    
    def execute(self, draft_output: Dict[str, Any], insight_output: Dict[str, Any], research_output: Dict[str, Any], message_context: Dict[str, Any]) -> ValidationOutput:
        all_violations = []
        
        full_text = f"{draft_output.get('greeting', '')} {draft_output.get('message_body', '')} {draft_output.get('cta_draft', '')} {draft_output.get('signature', '')}"
        
        all_violations.extend(self.validate_ascii_hygiene(full_text))
        all_violations.extend(self.validate_content_cleanliness(full_text))
        all_violations.extend(self.validate_structural_requirements(draft_output, message_context))
        all_violations.extend(self.validate_confidence_requirements(insight_output))
        all_violations.extend(self.validate_signal_quality(research_output))
        
        categorized = self.categorize_violations(all_violations)
        
        is_valid = len(categorized["blocked"]) == 0
        
        return ValidationOutput(
            is_valid=is_valid,
            error_codes=[v.split(":")[0] for v in all_violations],
            validation_results={
                "total_violations": len(all_violations),
                "blocked_violations": len(categorized["blocked"]),
                "warning_violations": len(categorized["warnings"]),
                "confidence_score": insight_output.get("aggregate_confidence", 0.0),
                "signal_quality": research_output.get("signal_score", 0.0)
            },
            blocked_violations=categorized["blocked"],
            warning_violations=categorized["warnings"]
        )
