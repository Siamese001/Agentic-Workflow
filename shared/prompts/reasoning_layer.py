"""
Reasoning Layer Prompts - Instructional Injection v5 Framework

Implements Reasoning Layer instructions (11-15) for subatomic agents.
"""

class ReasoningLayer:
    """Reasoning Layer prompt templates for structured cognitive processes."""
    
    @staticmethod
    def failure_anticipation(common_failures: list) -> str:
        """11. Failure Anticipation Injection - Predict and mitigate likely mistakes."""
        failures_text = "\n".join([f"- {failure}" for failure in common_failures])
        return f"""
# FAILURE ANTICIPATION
COMMON FAILURE MODES:
{failures_text}

MITIGATION STRATEGY:
1. Before each reasoning step, check against failure modes
2. Implement preventive measures for high-risk operations
3. Add validation checkpoints after critical decisions
4. Maintain fallback options for complex operations
5. Document assumptions to catch invalid premises

Actively monitor for these failure patterns throughout reasoning.
"""
    
    @staticmethod
    def multi_branch_thinking(branches: int = 3) -> str:
        """12. Self-Consistency/Multi-Branch Thinking - Generate and vote on reasoning paths."""
        return f"""
# MULTI-BRANCH REASONING
Generate {branches} distinct reasoning branches:
- Branch 1: Conservative/Safe approach
- Branch 2: Optimistic/Innovative approach  
- Branch 3: Balanced/Pragmatic approach

EVALUATION CRITERIA:
- Logical consistency
- Evidence support
- Risk assessment
- Goal alignment
- Efficiency consideration

After generating all branches, vote for the strongest path and explain reasoning.
Document why other branches were rejected.
"""
    
    @staticmethod
    def confidence_uncertainty() -> str:
        """13. Confidence & Uncertainty Injection - Provide numeric confidence with justification."""
        return """
# CONFIDENCE SCORING
For each key conclusion, provide:
- Confidence Score: 0.0-1.0 (where 1.0 = certain)
- Uncertainty Sources: List specific factors creating doubt
- Evidence Weight: How much supporting evidence exists
- Risk Assessment: Potential impact of being wrong

CONFIDENCE LEVELS:
- 0.9-1.0: High confidence (strong evidence, low uncertainty)
- 0.7-0.9: Moderate confidence (good evidence, some uncertainty)
- 0.5-0.7: Low confidence (limited evidence, high uncertainty)
- 0.0-0.5: Very low confidence (speculative, should seek more data)

Always quantify uncertainty and justify confidence levels.
"""
    
    @staticmethod
    def reason_then_answer() -> str:
        """14. Reason-Then-Answer Structure - Think privately, then output structured result."""
        return """
# REASONING-THEN-ANSWER PROTOCOL

STEP 1: PRIVATE REASONING
<thinking>
Perform all analysis, calculations, and deliberations here.
This section is for internal processing only.
Explore multiple approaches, test assumptions, validate logic.
</thinking>

STEP 2: STRUCTURED OUTPUT
After completing private reasoning, provide:
- Clear, concise final answer
- Key supporting points
- Confidence assessment
- Any important caveats

Keep reasoning separate from final output for clarity and auditability.
"""
    
    @staticmethod
    def error_simulation() -> str:
        """15. Error Simulation Injection - Test potential failures before finalizing."""
        return """
# ERROR SIMULATION PROTOCOL

SIMULATION PHASE:
1. Imagine the output contains critical errors
2. Identify most likely error sources:
   - Data interpretation mistakes
   - Logic flaws or missed edge cases
   - Incomplete understanding of requirements
   - Technical implementation errors

VALIDATION PHASE:
3. Run rapid error detection:
   - Cross-check against constraints
   - Verify internal consistency
   - Test boundary conditions
   - Validate against success criteria

CORRECTION PHASE:
4. If errors found, correct and re-simulate
5. Only proceed to final output after error-free simulation

This defensive approach prevents common mistakes and improves reliability.
"""
