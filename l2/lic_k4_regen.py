from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class RegenOutput:
    regenerated_draft: Dict[str, Any]
    regeneration_count: int
    final_confidence: float
    regeneration_reasons: List[str]

class LIC_K4_Regen:
    def __init__(self, validator_plan: Dict[str, Any], constraint_plan: Dict[str, Any]):
        self.validators = validator_plan
        self.constraints = constraint_plan
        self.max_retries = 3
        
    def check_forbidden_patterns(self, text: str) -> List[str]:
        violations = []
        
        forbidden_verbs = self.constraints["forbidden_verbs"]
        for verb in forbidden_verbs:
            if verb.lower() in text.lower():
                violations.append(f"Forbidden verb detected: {verb}")
        
        filler_patterns = self.constraints["filler_patterns"]
        for pattern in filler_patterns:
            import re
            if re.search(pattern, text, re.IGNORECASE):
                violations.append(f"Filler pattern detected: {pattern}")
        
        placeholder_patterns = self.constraints["placeholder_patterns"]
        for pattern in placeholder_patterns:
            import re
            if re.search(pattern, text):
                violations.append(f"Placeholder pattern detected: {pattern}")
                
        return violations
    
    def check_confidence_thresholds(self, insight_output: Dict[str, Any]) -> List[str]:
        violations = []
        
        per_claim_min = 0.8
        aggregate_min = 0.95
        
        for claim_score in insight_output.get("per_claim_scores", []):
            score = claim_score.get("score", 0.0)
            if score < per_claim_min:
                violations.append(f"Per-claim confidence below threshold: {score:.3f}")
        
        aggregate_confidence = insight_output.get("aggregate_confidence", 0.0)
        if aggregate_confidence < aggregate_min:
            violations.append(f"Aggregate confidence below threshold: {aggregate_confidence:.3f}")
            
        return violations
    
    def check_word_count_violations(self, draft_output: Dict[str, Any], archetype: str) -> List[str]:
        violations = []
        
        word_count_targets = {
            "C_LEVEL": [190, 230],
            "EXECUTIVE": [160, 220],
            "SENIOR_TA": [150, 190],
            "RECRUITER": [140, 170]
        }
        
        target_range = word_count_targets.get(archetype, [160, 220])
        current_count = draft_output.get("word_count", 0)
        
        tolerance = self.constraints["word_count_tolerance"]
        min_allowed = target_range[0] * (1 - tolerance)
        max_allowed = target_range[1] * (1 + tolerance)
        
        if current_count < min_allowed:
            violations.append(f"Word count too low: {current_count} < {min_allowed:.0f}")
        elif current_count > max_allowed:
            violations.append(f"Word count too high: {current_count} > {max_allowed:.0f}")
            
        return violations
    
    def apply_regeneration_strategy(self, draft_output: Dict[str, Any], violation_type: str) -> Dict[str, Any]:
        regenerated = draft_output.copy()
        
        if violation_type == "forbidden_patterns":
            message_body = regenerated.get("message_body", "")
            
            for verb in self.constraints["forbidden_verbs"]:
                if verb.lower() in message_body.lower():
                    replacements = {
                        "spearheaded": "led",
                        "leveraged": "used", 
                        "utilized": "used",
                        "facilitated": "enabled",
                        "orchestrated": "coordinated",
                        "championed": "advocated for",
                        "pioneered": "developed",
                        "revolutionized": "transformed",
                        "optimized": "improved",
                        "enhanced": "improved",
                        "streamlined": "simplified",
                        "synergized": "integrated",
                        "enabled": "supported",
                        "empowered": "supported",
                        "drove": "led",
                        "drive": "lead"
                    }
                    message_body = message_body.replace(verb, replacements.get(verb, "achieved"))
            
            regenerated["message_body"] = message_body
            
        elif violation_type == "word_count":
            current_count = regenerated.get("word_count", 0)
            message_body = regenerated.get("message_body", "")
            
            if current_count < 160:
                additional_content = " This approach has demonstrated success in similar environments and could provide significant value."
                regenerated["message_body"] = message_body + additional_content
                regenerated["word_count"] = len((message_body + additional_content).split())
            elif current_count > 250:
                words = message_body.split()
                truncated_body = " ".join(words[:220])
                regenerated["message_body"] = truncated_body
                regenerated["word_count"] = len(truncated_body.split())
                
        elif violation_type == "confidence":
            message_body = regenerated.get("message_body", "")
            enhanced_body = message_body + " Based on extensive experience and proven methodologies, this approach delivers measurable results."
            regenerated["message_body"] = enhanced_body
            regenerated["word_count"] = len(enhanced_body.split())
            
        return regenerated
    
    def execute(self, draft_output: Dict[str, Any], insight_output: Dict[str, Any], archetype: str) -> RegenOutput:
        regeneration_count = 0
        regeneration_reasons = []
        current_draft = draft_output.copy()
        
        for attempt in range(self.max_retries + 1):
            violations = []
            
            text_to_check = f"{current_draft.get('message_body', '')} {current_draft.get('cta_draft', '')}"
            violations.extend(self.check_forbidden_patterns(text_to_check))
            violations.extend(self.check_confidence_thresholds(insight_output))
            violations.extend(self.check_word_count_violations(current_draft, archetype))
            
            if not violations:
                break
                
            if attempt < self.max_retries:
                primary_violation = violations[0].split(":")[0]
                current_draft = self.apply_regeneration_strategy(current_draft, primary_violation)
                regeneration_count += 1
                regeneration_reasons.extend(violations)
        
        final_confidence = insight_output.get("aggregate_confidence", 0.0)
        
        return RegenOutput(
            regenerated_draft=current_draft,
            regeneration_count=regeneration_count,
            final_confidence=final_confidence,
            regeneration_reasons=regeneration_reasons
        )
