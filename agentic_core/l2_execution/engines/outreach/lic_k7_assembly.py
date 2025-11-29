"""K7 Assembly Executor - Seventh and final hop in the sequential K1-K7 execution pipeline.

Incorporated from L2 lic_k7_assembly.py to assemble all components from
previous K-nodes into the final message output for delivery, completing
the hop-based architecture.

This is the final execution phase in the hop-based architecture that follows:
L1 Planning → K1 Research → K2 Insights → K3 Draft → K4 Regeneration → K5 Validation → K6 CTA → K7 Assembly
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class MessageComponent:
    """Individual message component with assembly metadata."""
    component_type: str                   # "greeting", "subject", "hook", "value", "cta", "signature"
    content: str
    source_k_node: str                     # Which K-node provided this component
    word_count: int
    confidence_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AssemblyOutput:
    """Output from K7 assembly execution phase."""
    final_message: str
    message_components: Dict[str, MessageComponent]
    assembly_metadata: Dict[str, Any]
    validation_status: str
    pipeline_confidence: float
    execution_trace: List[str]
    delivery_format: str
    quality_metrics: Dict[str, Any] = field(default_factory=dict)


class K7AssemblyExecutor:
    """K7 assembly executor - seventh and final hop in sequential execution pipeline.
    
    Assembles all components from previous K-nodes into the final message
    output for delivery, completing the hop-based architecture.
    """
    
    def __init__(self, 
                 k_node_plan: Optional[Dict[str, Any]] = None,
                 validator_plan: Optional[Dict[str, Any]] = None,
                 telemetry_bus: Optional[Any] = None) -> None:
        """Initialize K7 assembly executor."""
        self.k_node_plan = k_node_plan or {}
        self.validator_plan = validator_plan or {}
        self.telemetry_bus = telemetry_bus
        
        # Assembly configuration
        self.assembly_config = {
            "component_priority": {
                "greeting": 1,
                "subject": 2,
                "hook": 3,
                "value": 4,
                "cta": 5,
                "signature": 6
            },
            "required_components": ["greeting", "value", "cta", "signature"],
            "optional_components": ["subject", "hook"],
            "delivery_formats": ["email", "linkedin", "plain_text"],
            "final_validation_gates": [
                "completeness_check",
                "coherence_check", 
                "quality_threshold",
                "length_validation"
            ]
        }
    
    def execute(
        self,
        *,
        k1_research_output: Any,
        k2_insights_output: Any,
        k3_draft_output: Any,
        k4_regen_output: Any,
        k5_validation_output: Any,
        k6_cta_output: Any,
        l1_plans: Dict[str, Any],
        outreach_context: Dict[str, Any] = None,
    ) -> AssemblyOutput:
        """Execute K7 final assembly phase.
        
        Args:
            k1_research_output: Output from K1 research execution
            k2_insights_output: Output from K2 insights execution
            k3_draft_output: Output from K3 draft execution
            k4_regen_output: Output from K4 regeneration execution
            k5_validation_output: Output from K5 validation execution
            k6_cta_output: Output from K6 CTA execution
            l1_plans: Dictionary of all L1 planning outputs
            outreach_context: Additional context for final assembly
            
        Returns:
            Complete assembled message with all components and metadata
        """
        outreach_context = outreach_context or {}
        
        # 1. Collect all K-node outputs
        k_outputs = {
            "k1_research": k1_research_output,
            "k2_insights": k2_insights_output,
            "k3_draft": k3_draft_output,
            "k4_regen": k4_regen_output,
            "k5_validation": k5_validation_output,
            "k6_cta": k6_cta_output
        }
        
        # 2. Assemble message components from K-node outputs
        message_components = self._assemble_message_components(k_outputs)
        
        # 3. Apply final validation gates
        validation_violations = self._apply_final_validation_gates(message_components, k_outputs)
        
        # 4. Construct final message
        final_message = self._construct_final_message(message_components, outreach_context)
        
        # 5. Determine validation status
        validation_status = "valid" if not validation_violations else "invalid"
        
        # 6. Calculate pipeline confidence
        pipeline_confidence = self._calculate_pipeline_confidence(k_outputs, message_components)
        
        # 7. Generate execution trace
        execution_trace = self._generate_execution_trace(k_outputs, l1_plans)
        
        # 8. Determine delivery format
        delivery_format = outreach_context.get("delivery_format", "email")
        
        # 9. Calculate quality metrics
        quality_metrics = self._calculate_quality_metrics(message_components, k_outputs)
        
        # 10. Build assembly metadata
        assembly_metadata = {
            "components_assembled": len(message_components),
            "k_nodes_processed": len(k_outputs),
            "l1_plans_used": len(l1_plans),
            "validation_violations": len(validation_violations),
            "assembly_timestamp": "2024-01-01T00:00:00Z",
            "hop_based_pipeline": True
        }
        
        # 11. Create assembly output
        output = AssemblyOutput(
            final_message=final_message,
            message_components=message_components,
            assembly_metadata=assembly_metadata,
            validation_status=validation_status,
            pipeline_confidence=pipeline_confidence,
            execution_trace=execution_trace,
            delivery_format=delivery_format,
            quality_metrics=quality_metrics
        )
        
        # 12. Record telemetry (best-effort)
        self._safe_record_telemetry(output)
        
        return output
    
    def _assemble_message_components(self, k_outputs: Dict[str, Any]) -> Dict[str, MessageComponent]:
        """Assemble message components from K-node outputs."""
        components = {}
        
        # Extract components from K3 draft (primary source)
        k3_output = k_outputs.get("k3_draft", {})
        
        # Greeting component
        greeting = getattr(k3_output, 'greeting', 'Hello,')
        components["greeting"] = MessageComponent(
            component_type="greeting",
            content=greeting,
            source_k_node="k3_draft",
            word_count=len(greeting.split()),
            confidence_score=0.9,
            metadata={"source": "k3_draft"}
        )
        
        # Subject component (if available)
        subject_line = getattr(k3_output, 'subject_line', None)
        if subject_line:
            components["subject"] = MessageComponent(
                component_type="subject",
                content=subject_line,
                source_k_node="k3_draft",
                word_count=len(subject_line.split()),
                confidence_score=0.8,
                metadata={"source": "k3_draft"}
            )
        
        # Message body components (hook + value)
        if hasattr(k3_output, 'sections'):
            sections = k3_output.sections
            
            # Hook component
            if "hook" in sections:
                hook_content = getattr(sections["hook"], 'content', '')
                components["hook"] = MessageComponent(
                    component_type="hook",
                    content=hook_content,
                    source_k_node="k3_draft",
                    word_count=len(hook_content.split()),
                    confidence_score=getattr(sections["hook"], 'confidence_score', 0.7),
                    metadata={"source": "k3_draft", "section": "hook"}
                )
            
            # Value component
            if "value" in sections:
                value_content = getattr(sections["value"], 'content', '')
                components["value"] = MessageComponent(
                    component_type="value",
                    content=value_content,
                    source_k_node="k3_draft",
                    word_count=len(value_content.split()),
                    confidence_score=getattr(sections["value"], 'confidence_score', 0.7),
                    metadata={"source": "k3_draft", "section": "value"}
                )
        
        # Use regenerated content if available from K4
        k4_output = k_outputs.get("k4_regen", {})
        if hasattr(k4_output, 'regenerated_draft') and k4_output.regenerated_draft:
            regen_draft = k4_output.regenerated_draft
            if "sections" in regen_draft:
                for section_name, section in regen_draft["sections"].items():
                    if section_name in components:
                        # Update with regenerated content
                        components[section_name].content = getattr(section, 'content', components[section_name].content)
                        components[section_name].source_k_node = "k4_regen"
                        components[section_name].confidence_score = getattr(section, 'confidence_score', components[section_name].confidence_score)
                        components[section_name].metadata["regenerated"] = True
        
        # CTA component from K6
        k6_output = k_outputs.get("k6_cta", {})
        final_cta = getattr(k6_output, 'final_cta', 'Would you be open to a discussion?')
        components["cta"] = MessageComponent(
            component_type="cta",
            content=final_cta,
            source_k_node="k6_cta",
            word_count=len(final_cta.split()),
            confidence_score=getattr(k6_output, 'response_probability', 0.7),
            metadata={"source": "k6_cta", "optimized": getattr(k6_output, 'optimization_applied', False)}
        )
        
        # Signature component from K3
        signature = getattr(k3_output, 'signature', 'Best regards,')
        components["signature"] = MessageComponent(
            component_type="signature",
            content=signature,
            source_k_node="k3_draft",
            word_count=len(signature.split()),
            confidence_score=0.9,
            metadata={"source": "k3_draft"}
        )
        
        return components
    
    def _apply_final_validation_gates(self, components: Dict[str, MessageComponent], k_outputs: Dict[str, Any]) -> List[str]:
        """Apply final validation gates to assembled components."""
        violations = []
        
        # Completeness check
        required_components = self.assembly_config["required_components"]
        missing_components = [comp for comp in required_components if comp not in components]
        if missing_components:
            violations.append(f"Missing required components: {missing_components}")
        
        # Coherence check
        if "hook" in components and "value" in components:
            hook_words = set(components["hook"].content.lower().split())
            value_words = set(components["value"].content.lower().split())
            overlap = len(hook_words.intersection(value_words))
            if overlap < 2:
                violations.append("Poor coherence between hook and value sections")
        
        # Quality threshold check
        k5_output = k_outputs.get("k5_validation", {})
        if hasattr(k5_output, 'is_valid') and not k5_output.is_valid:
            violations.append("K5 validation failed - message not ready for delivery")
        
        # Length validation
        total_words = sum(comp.word_count for comp in components.values())
        if total_words < 30:
            violations.append("Message too short for effective communication")
        elif total_words > 200:
            violations.append("Message too long - may reduce engagement")
        
        return violations
    
    def _construct_final_message(self, components: Dict[str, MessageComponent], context: Dict[str, Any]) -> str:
        """Construct final message from assembled components."""
        message_parts = []
        
        # Order components for final assembly
        assembly_order = ["subject", "greeting", "hook", "value", "cta", "signature"]
        
        for component_name in assembly_order:
            if component_name in components:
                component = components[component_name]
                content = component.content.strip()
                
                if content:
                    if component_name == "subject":
                        # Subject is handled separately in metadata
                        pass
                    elif component_name in ["greeting", "signature"]:
                        message_parts.append(content)
                    else:
                        message_parts.append(content)
        
        # Join with appropriate spacing
        final_message = "\n\n".join(message_parts)
        
        return final_message
    
    def _calculate_pipeline_confidence(self, k_outputs: Dict[str, Any], components: Dict[str, MessageComponent]) -> float:
        """Calculate overall pipeline confidence."""
        confidence_scores = []
        
        # Collect confidence from all K-nodes
        for k_name, k_output in k_outputs.items():
            if hasattr(k_output, 'confidence_score'):
                confidence_scores.append(k_output.confidence_score)
            elif hasattr(k_output, 'final_confidence'):
                confidence_scores.append(k_output.final_confidence)
            elif hasattr(k_output, 'aggregate_confidence'):
                confidence_scores.append(k_output.aggregate_confidence)
            elif hasattr(k_output, 'response_probability'):
                confidence_scores.append(k_output.response_probability)
        
        # Collect confidence from components
        for component in components.values():
            confidence_scores.append(component.confidence_score)
        
        if confidence_scores:
            average_confidence = sum(confidence_scores) / len(confidence_scores)
        else:
            average_confidence = 0.5
        
        # Apply final validation penalty if needed
        k5_output = k_outputs.get("k5_validation", {})
        if hasattr(k5_output, 'is_valid') and not k5_output.is_valid:
            average_confidence *= 0.8
        
        return round(average_confidence, 3)
    
    def _generate_execution_trace(self, k_outputs: Dict[str, Any], l1_plans: Dict[str, Any]) -> List[str]:
        """Generate execution trace for debugging and audit."""
        trace = []
        
        # L1 planning phase
        trace.append("L1 Planning Phase:")
        for plan_name in l1_plans.keys():
            trace.append(f"  - {plan_name} executed")
        
        # K-node execution phase
        trace.append("K-Node Execution Phase:")
        for k_name in k_outputs.keys():
            trace.append(f"  - {k_name} executed")
        
        # Assembly phase
        trace.append("K7 Assembly Phase:")
        trace.append("  - Components assembled")
        trace.append("  - Final validation applied")
        trace.append("  - Message constructed")
        
        return trace
    
    def _calculate_quality_metrics(self, components: Dict[str, MessageComponent], k_outputs: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive quality metrics."""
        metrics = {}
        
        # Component metrics
        metrics["component_count"] = len(components)
        metrics["total_word_count"] = sum(comp.word_count for comp in components.values())
        metrics["average_confidence"] = sum(comp.confidence_score for comp in components.values()) / len(components) if components else 0.0
        
        # K-node metrics
        metrics["k_nodes_processed"] = len(k_outputs)
        successful_k_nodes = len([k for k in k_outputs.values() if k is not None])
        metrics["successful_k_nodes"] = successful_k_nodes
        
        # Quality distribution
        high_quality_components = len([c for c in components.values() if c.confidence_score >= 0.8])
        metrics["high_quality_components"] = high_quality_components
        metrics["quality_distribution"] = {
            "high": high_quality_components,
            "medium": len([c for c in components.values() if 0.6 <= c.confidence_score < 0.8]),
            "low": len([c for c in components.values() if c.confidence_score < 0.6])
        }
        
        return metrics
    
    def _safe_record_telemetry(self, output: AssemblyOutput) -> None:
        """Record telemetry data (best-effort)."""
        try:
            if self.telemetry_bus:
                self.telemetry_bus.record("k7_assembly_executed", {
                    "components_assembled": len(output.message_components),
                    "validation_status": output.validation_status,
                    "pipeline_confidence": output.pipeline_confidence,
                    "delivery_format": output.delivery_format,
                    "hop_based_pipeline": True
                })
        except Exception as e:
            logger.debug(f"Failed to record telemetry: {e}")
    
    def get_assembly_summary(self, output: AssemblyOutput) -> Dict[str, Any]:
        """Get a summary of the assembly execution for debugging/telemetry."""
        return {
            "execution_id": "k7_assembly",
            "components_assembled": len(output.message_components),
            "validation_status": output.validation_status,
            "pipeline_confidence": output.pipeline_confidence,
            "delivery_format": output.delivery_format,
            "final_message_length": len(output.final_message),
            "quality_metrics": output.quality_metrics,
            "hop_based_complete": True
        }
    
    def format_for_delivery(self, output: AssemblyOutput, format_type: str = "email") -> Dict[str, Any]:
        """Format assembled message for specific delivery channels."""
        formatted = {
            "format": format_type,
            "subject": None,
            "body": output.final_message,
            "metadata": output.assembly_metadata.copy()
        }
        
        if format_type == "email":
            # Email format with subject
            if "subject" in output.message_components:
                formatted["subject"] = output.message_components["subject"].content
            formatted["body"] = output.final_message
            formatted["metadata"]["delivery_type"] = "email"
            
        elif format_type == "linkedin":
            # LinkedIn format (no subject, more concise)
            formatted["subject"] = None
            formatted["body"] = output.final_message
            formatted["metadata"]["delivery_type"] = "linkedin_message"
            
        elif format_type == "plain_text":
            # Plain text format
            formatted["subject"] = None
            formatted["body"] = output.final_message
            formatted["metadata"]["delivery_type"] = "plain_text"
        
        return formatted





