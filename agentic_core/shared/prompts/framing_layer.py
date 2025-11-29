"""
Framing Layer Prompts - Instructional Injection v5 Framework

Implements Framing Layer instructions (1-5) for subatomic agents.
"""

from typing import Optional

class FramingLayer:
    """Framing Layer prompt templates for establishing agent context and goals."""
    
    @staticmethod
    def global_goal_state(goal: str, context: str = "") -> str:
        """1. Global Goal-State Injection - Anchor all reasoning to overarching objective."""
        return f"""
# GLOBAL OBJECTIVE
{goal}

{context}

All reasoning, analysis, and output must serve this primary objective. 
Every decision should be traceable back to this goal.
"""
    
    @staticmethod
    def success_criteria(criteria: list) -> str:
        """2. Success Criteria Injection - Define explicit quality thresholds."""
        criteria_text = "\n".join([f"- {criterion}" for criterion in criteria])
        return f"""
# SUCCESS CRITERIA
{criteria_text}

Output must meet ALL specified criteria before completion.
Each criterion should be explicitly validated and scored.
"""
    
    @staticmethod
    def task_mode_declaration(mode: str, description: str = "") -> str:
        """3. Task Mode Declaration - Specify cognitive mode."""
        modes = {
            "analytical": "Break down complex problems systematically",
            "synthesis": "Integrate multiple sources into coherent output",
            "adversarial": "Challenge assumptions and find weaknesses",
            "meta": "Reflect on reasoning process and improve it",
            "security": "Prioritize safety, ethics, and compliance"
        }
        
        mode_desc = modes.get(mode, mode)
        return f"""
# COGNITIVE MODE: {mode.upper()}
{mode_desc}
{description}

Adopt this cognitive mode throughout the entire reasoning process.
"""
    
    @staticmethod
    def scope_boundaries(scope: str, constraints: list, forbidden: Optional[list] = None) -> str:
        """4. Scope & Boundaries Injection - State exact constraints."""
        constraints_text = "\n".join([f"- {constraint}" for constraint in constraints])
        forbidden_text = ""
        if forbidden:
            forbidden_text = "\n# FORBIDDEN ACTIONS\n" + "\n".join([f"- {item}" for item in forbidden])
        
        return f"""
# SCOPE AND BOUNDARIES
{scope}

# CONSTRAINTS
{constraints_text}
{forbidden_text}

Strictly adhere to these boundaries. Do not exceed scope or violate constraints.
"""
    
    @staticmethod
    def cost_latency_targets(max_tokens: Optional[int] = None, max_time: Optional[str] = None, efficiency_mode: str = "balanced") -> str:
        """5. Cost/Latency Targets - Guide toward efficient reasoning."""
        token_constraint = f"Maximum {max_tokens} tokens" if max_tokens else "Optimize for token efficiency"
        time_constraint = f"Complete within {max_time}" if max_time else "Optimize for response time"
        
        return f"""
# EFFICIENCY TARGETS
- Token Budget: {token_constraint}
- Time Constraint: {time_constraint}
- Efficiency Mode: {efficiency_mode}

Prioritize concise, efficient reasoning while maintaining quality.
Avoid unnecessary elaboration or redundant analysis.
"""
