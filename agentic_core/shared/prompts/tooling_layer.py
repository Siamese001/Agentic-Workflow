"""
Tooling Layer Prompts - Instructional Injection v5 Framework

Implements Tooling Layer instructions (16-20) for subatomic agents.
"""

from typing import Dict

class ToolingLayer:
    """Tooling Layer prompt templates for integrating external tools and feedback loops."""
    
    @staticmethod
    def tool_feedback_loop(tools: Dict[str, str]) -> str:
        """16. Tool-Feedback Loop Injection - Incorporate structured tool outputs into reasoning."""
        tools_text = "\n".join([f"- {tool}: {description}" for tool, description in tools.items()])
        return f"""
# TOOL FEEDBACK LOOP INTEGRATION
AVAILABLE TOOLS:
{tools_text}

FEEDBACK PROTOCOL:
1. Execute tool with structured input
2. Parse tool output into standardized format
3. Incorporate results into subsequent reasoning steps
4. Validate tool output against expectations
5. Adjust strategy based on tool feedback

Each tool output must be explicitly referenced in reasoning decisions.
Document how tool results influenced the final outcome.
"""
    
    @staticmethod
    def evidence_binding() -> str:
        """17. Evidence Binding/Citation Anchors - Ground claims to explicit evidence."""
        return """
# EVIDENCE BINDING REQUIREMENTS
All claims must be grounded to explicit evidence sources:

CITATION FORMAT:
[Source: tool_name, result_id, confidence_score]

EVIDENCE REQUIREMENTS:
- Direct quotes for factual claims
- Data sources for numerical claims  
- Tool outputs for analytical claims
- Cross-references for complex claims

VALIDATION:
- Each citation must be traceable to original source
- Evidence strength must match claim confidence
- Conflicting evidence must be acknowledged and resolved

Never make unsupported claims. Always provide evidence anchors.
"""
    
    @staticmethod
    def cross_tool_reconciliation() -> str:
        """18. Cross-Tool Reconciliation - Resolve conflicting outputs across tools."""
        return """
# CROSS-TOOL RECONCILIATION PROTOCOL

CONFLICT DETECTION:
1. Compare outputs from multiple tools
2. Identify contradictions or discrepancies
3. Assess confidence levels of conflicting sources
4. Prioritize evidence by reliability and relevance

RESOLUTION STRATEGIES:
- High-confidence tool overrides low-confidence tool
- Multiple consistent sources override single source
- Recent data overrides outdated data
- Domain-specific tools override general tools

DOCUMENTATION:
- Record all conflicts detected
- Explain resolution rationale
- Note any remaining uncertainties
- Provide confidence-adjusted final output

Ensure all tool outputs are reconciled before final reasoning.
"""
    
    @staticmethod
    def shadow_validation() -> str:
        """19. Shadow Validation - Run rapid internal sanity checks before output."""
        return """
# SHADOW VALIDATION PROTOCOL

INTERNAL VALIDATION CHECKS:
1. Semantic Consistency: Does output make logical sense?
2. Structural Integrity: Is format/schema correct?
3. Constraint Compliance: Are all constraints satisfied?
4. Goal Alignment: Does output serve primary objective?
5. Risk Assessment: Are there safety or quality concerns?

VALIDATION PROCESS:
- Run checks in parallel with main reasoning
- Flag any failures for immediate attention
- Document validation results and confidence scores
- Only proceed to output if all checks pass

SHADOW MODE OPERATIONS:
- Simulate alternative approaches
- Test edge cases and boundary conditions
- Verify robustness under uncertainty
- Maintain fallback options for critical failures

Shadow validation ensures reliability before external output.
"""
    
    @staticmethod
    def model_switch_aware() -> str:
        """20. Model-Switch Aware Instructions - Adapt based on model capabilities."""
        return """
# MODEL-SWITCH ADAPTATION PROTOCOL

MODEL CAPABILITY DETECTION:
- Fast Model: Quick responses, limited complexity
- High-Accuracy Model: Detailed analysis, higher cost
- Specialized Model: Domain-specific expertise

ADAPTATION STRATEGIES:
FAST MODEL USAGE:
- Simplified reasoning chains
- Reduced validation depth
- Conservative confidence estimates
- Quick decision protocols

HIGH-ACCURACY MODEL USAGE:
- Comprehensive analysis
- Multi-branch reasoning
- Extensive validation
- Detailed uncertainty quantification

SPECIALIZED MODEL USAGE:
- Domain-specific knowledge integration
- Specialized tool usage
- Expert-level reasoning patterns
- Industry-standard validation

SELECTION CRITERIA:
- Task complexity requirements
- Time/budget constraints
- Accuracy criticality
- Available model options

Always adapt reasoning depth and validation to model capabilities.
"""
