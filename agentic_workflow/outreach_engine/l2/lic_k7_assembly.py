from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class AssemblyOutput:
    final_message: str
    message_components: Dict[str, str]
    assembly_metadata: Dict[str, Any]
    validation_status: str

class LIC_K7_Assembly:
    def __init__(self, k_node_plan: Dict[str, Any], validator_plan: Dict[str, Any]):
        self.plan = k_node_plan
        self.validators = validator_plan
        
    def assemble_message_components(self, k_outputs: Dict[str, Any]) -> Dict[str, str]:
        components = {}
        
        k1_output = k_outputs.get("k1_research", {})
        k3_output = k_outputs.get("k3_draft", {})
        k4_output = k_outputs.get("k4_regen", {})
        k6_output = k_outputs.get("k6_cta", {})
        
        greeting = k3_output.get("greeting", "Hi there,")
        
        subject_line = k3_output.get("subject_line")
        
        if k4_output.get("regenerated_draft"):
            message_body = k4_output["regenerated_draft"].get("message_body", "")
        else:
            message_body = k3_output.get("message_body", "")
            
        cta = k6_output.get("final_cta", "Would you be open to a discussion?")
        
        signature = k3_output.get("signature", "Best regards,")
        
        components = {
            "greeting": greeting,
            "message_body": message_body,
            "cta": cta,
            "signature": signature
        }
        
        if subject_line:
            components["subject_line"] = subject_line
            
        return components
    
    def apply_final_validation_gates(self, components: Dict[str, Any], k_outputs: Dict[str, Any]) -> List[str]:
        violations = []
        
        validation_gates = self.plan.get("validation_gates", [])
        
        full_message = " ".join([
            components.get("greeting", ""),
            components.get("message_body", ""),
            components.get("cta", ""),
            components.get("signature", "")
        ])
        
        for gate in validation_gates:
            gate_policy = gate.get("policy", "")
            
            if "VALIDATE_AGAINST_SOURCE_SCAFFOLD" in gate_policy:
                k5_output = k_outputs.get("k5_validation", {})
                if k5_output.get("blocked_violations"):
                    violations.extend(k5_output["blocked_violations"])
                    
            elif "ENFORCE_ROUTE_SPECIFIC_LIMITS" in gate_policy:
                word_count = len(full_message.split())
                if word_count > 300:
                    violations.append("Message exceeds route-specific character limits")
                    
            elif "ENFORCE_ARCHETYPE_SPECIFIC_RANGES" in gate_policy:
                k3_output = k_outputs.get("k3_draft", {})
                archetype = k3_output.get("archetype_applied", "EXECUTIVE")
                
                word_targets = {
                    "C_LEVEL": [190, 230],
                    "EXECUTIVE": [160, 220],
                    "SENIOR_TA": [150, 190],
                    "RECRUITER": [140, 170]
                }
                
                target_range = word_targets.get(archetype, [160, 220])
                current_count = len(full_message.split())
                
                if current_count < target_range[0] or current_count > target_range[1]:
                    violations.append(f"Word count {current_count} outside archetype range {target_range}")
                    
            elif "SANITIZE_ALL_NON_STANDARD_CHARACTERS" in gate_policy:
                if "'" in full_message or '"' in full_message or "—" in full_message:
                    violations.append("Non-ASCII characters detected in final message")
                    
            elif "VALIDATE_AGAINST_ALL_CRITICAL_QA_RULES" in gate_policy:
                k5_output = k_outputs.get("k5_validation", {})
                if not k5_output.get("is_valid", False):
                    violations.extend(k5_output.get("warning_violations", []))
                    
            elif "ENFORCE_PER_CLAIM_AND_AGGREGATE_MINIMUMS" in gate_policy:
                k2_output = k_outputs.get("k2_insights", {})
                aggregate_confidence = k2_output.get("aggregate_confidence", 0.0)
                
                if aggregate_confidence < 0.95:
                    violations.append(f"Final confidence {aggregate_confidence:.3f} below threshold 0.95")
                    
        return violations
    
    def construct_final_message(self, components: Dict[str, str]) -> str:
        message_parts = []
        
        if "subject_line" in components:
            message_parts.append(f"Subject: {components['subject_line']}")
            
        message_parts.append(components["greeting"])
        message_parts.append(components["message_body"])
        message_parts.append(components["cta"])
        message_parts.append(components["signature"])
        
        return "\n\n".join(message_parts)
    
    def generate_assembly_metadata(self, components: Dict[str, str], violations: List[str], k_outputs: Dict[str, Any]) -> Dict[str, Any]:
        metadata = {
            "assembly_policy": self.plan.get("assembly_policy", ""),
            "component_count": len(components),
            "has_subject_line": "subject_line" in components,
            "final_word_count": len(self.construct_final_message(components).split()),
            "validation_violations": len(violations),
            "assembly_status": "SUCCESS" if not violations else "FAILED_VALIDATION"
        }
        
        k1_output = k_outputs.get("k1_research", {})
        k2_output = k_outputs.get("k2_insights", {})
        k3_output = k_outputs.get("k3_draft", {})
        k4_output = k_outputs.get("k4_regen", {})
        
        metadata.update({
            "signal_quality": k1_output.get("signal_score", 0.0),
            "aggregate_confidence": k2_output.get("aggregate_confidence", 0.0),
            "regeneration_count": k4_output.get("regeneration_count", 0),
            "archetype_applied": k3_output.get("archetype_applied", "EXECUTIVE")
        })
        
        return metadata
    
    def execute(self, k_outputs: Dict[str, Any]) -> AssemblyOutput:
        components = self.assemble_message_components(k_outputs)
        
        violations = self.apply_final_validation_gates(components, k_outputs)
        
        final_message = self.construct_final_message(components)
        
        assembly_metadata = self.generate_assembly_metadata(components, violations, k_outputs)
        
        validation_status = "VALID" if not violations else "INVALID"
        
        return AssemblyOutput(
            final_message=final_message,
            message_components=components,
            assembly_metadata=assembly_metadata,
            validation_status=validation_status
        )
