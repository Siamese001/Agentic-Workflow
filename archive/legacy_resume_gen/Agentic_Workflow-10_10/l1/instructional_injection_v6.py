"""Instructional Injection v6 - 30 Base Layers + 6 Extensions

This module implements the Instructional Injection v6 framework for prompt
engineering. It provides a layered approach to building robust, context-aware
prompts for agentic systems.

## 30 Base Layers (Core Foundation)

### Identity & Role (Layers 1-3)
1. Agent Identity: Who the agent is
2. Role Definition: What the agent does
3. Capability Scope: What the agent can/cannot do

### Context & Environment (Layers 4-7)
4. Domain Context: Business domain and terminology
5. Temporal Context: Time-aware reasoning
6. Spatial Context: Location/structure awareness
7. Relational Context: Entity relationships

### Task & Objectives (Layers 8-11)
8. Primary Objective: Main goal
9. Success Criteria: How to measure success
10. Constraints: Hard limits and boundaries
11. Preferences: Soft preferences and priorities

### Reasoning & Logic (Layers 12-15)
12. Reasoning Mode: How to think (analytical, creative, etc.)
13. Logic Framework: Deductive, inductive, abductive
14. Uncertainty Handling: How to deal with ambiguity
15. Error Recovery: How to handle failures

### Knowledge & Memory (Layers 16-19)
16. Domain Knowledge: Relevant facts and rules
17. Episodic Memory: Past interactions
18. Semantic Memory: Conceptual knowledge
19. Procedural Memory: How-to knowledge

### Communication & Output (Layers 20-23)
20. Output Format: Structure and schema
21. Tone & Style: Communication style
22. Verbosity Level: Detail level
23. Audience Adaptation: Who is the recipient

### Safety & Ethics (Layers 24-27)
24. Safety Constraints: What to avoid
25. Ethical Guidelines: Moral principles
26. Privacy Rules: Data protection
27. Bias Mitigation: Fairness considerations

### Meta & Reflection (Layers 28-30)
28. Self-Monitoring: Track own performance
29. Explanation: Justify decisions
30. Improvement: Learn from feedback

## 6 Extensions (Advanced Features)

### Extension 1: Temporal Reasoning
- Time-series analysis
- Trend detection
- Forecasting
- Historical context

### Extension 2: Multi-Agent Coordination
- Agent communication protocols
- Consensus mechanisms
- Conflict resolution
- Task delegation

### Extension 3: Mixture-of-Reasoners (MoR)
- Multiple reasoning strategies
- Strategy selection
- Result aggregation
- Confidence weighting

### Extension 4: Retrieval-Augmented Generation (RAG)
- Query formulation
- Evidence retrieval
- Source attribution
- Relevance filtering

### Extension 5: Chain-of-Thought (CoT)
- Step-by-step reasoning
- Intermediate steps
- Verification checkpoints
- Backtracking support

### Extension 6: Self-Correction
- Error detection
- Alternative generation
- Quality assessment
- Iterative refinement

Layer: Meta
Responsibilities:
- Define prompt layer structure
- Provide layer templates
- Validate layer completeness
- Support layer composition

Non-responsibilities:
- LLM invocation
- Planning
- Execution
- State management
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum


class InstructionalLayer(str, Enum):
    """30 base instructional layers."""
    
    # Identity & Role (1-3)
    AGENT_IDENTITY = "agent_identity"
    ROLE_DEFINITION = "role_definition"
    CAPABILITY_SCOPE = "capability_scope"
    
    # Context & Environment (4-7)
    DOMAIN_CONTEXT = "domain_context"
    TEMPORAL_CONTEXT = "temporal_context"
    SPATIAL_CONTEXT = "spatial_context"
    RELATIONAL_CONTEXT = "relational_context"
    
    # Task & Objectives (8-11)
    PRIMARY_OBJECTIVE = "primary_objective"
    SUCCESS_CRITERIA = "success_criteria"
    CONSTRAINTS = "constraints"
    PREFERENCES = "preferences"
    
    # Reasoning & Logic (12-15)
    REASONING_MODE = "reasoning_mode"
    LOGIC_FRAMEWORK = "logic_framework"
    UNCERTAINTY_HANDLING = "uncertainty_handling"
    ERROR_RECOVERY = "error_recovery"
    
    # Knowledge & Memory (16-19)
    DOMAIN_KNOWLEDGE = "domain_knowledge"
    EPISODIC_MEMORY = "episodic_memory"
    SEMANTIC_MEMORY = "semantic_memory"
    PROCEDURAL_MEMORY = "procedural_memory"
    
    # Communication & Output (20-23)
    OUTPUT_FORMAT = "output_format"
    TONE_STYLE = "tone_style"
    VERBOSITY_LEVEL = "verbosity_level"
    AUDIENCE_ADAPTATION = "audience_adaptation"
    
    # Safety & Ethics (24-27)
    SAFETY_CONSTRAINTS = "safety_constraints"
    ETHICAL_GUIDELINES = "ethical_guidelines"
    PRIVACY_RULES = "privacy_rules"
    BIAS_MITIGATION = "bias_mitigation"
    
    # Meta & Reflection (28-30)
    SELF_MONITORING = "self_monitoring"
    EXPLANATION = "explanation"
    IMPROVEMENT = "improvement"


class InstructionalExtension(str, Enum):
    """6 advanced extensions."""
    
    TEMPORAL_REASONING = "temporal_reasoning"
    MULTI_AGENT_COORDINATION = "multi_agent_coordination"
    MIXTURE_OF_REASONERS = "mixture_of_reasoners"
    RAG_INTEGRATION = "rag_integration"
    CHAIN_OF_THOUGHT = "chain_of_thought"
    SELF_CORRECTION = "self_correction"


@dataclass
class LayerContent:
    """Content for a single instructional layer."""
    
    layer: InstructionalLayer
    content: str
    priority: int = 5  # 1-10, higher = more important
    required: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExtensionContent:
    """Content for an extension."""
    
    extension: InstructionalExtension
    content: str
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class InstructionalPrompt:
    """Complete v6 instructional prompt with layers and extensions."""
    
    prompt_id: str
    agent_type: str  # "planner", "executor", "orchestrator", etc.
    layer_type: str  # "L1", "L2", "L3", "L4", "L5"
    
    # 30 base layers
    layers: Dict[InstructionalLayer, LayerContent] = field(default_factory=dict)
    
    # 6 extensions
    extensions: Dict[InstructionalExtension, ExtensionContent] = field(default_factory=dict)
    
    # Metadata
    version: str = "v6.0"
    created_by: str = "system"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_layer(self, layer_content: LayerContent) -> None:
        """Add or update a layer."""
        self.layers[layer_content.layer] = layer_content
    
    def add_extension(self, extension_content: ExtensionContent) -> None:
        """Add or update an extension."""
        self.extensions[extension_content.extension] = extension_content
    
    def render(self) -> str:
        """Render the complete prompt with all layers and extensions."""
        sections = []
        
        # Render base layers in order
        for layer in InstructionalLayer:
            if layer in self.layers:
                layer_content = self.layers[layer]
                if layer_content.content:
                    sections.append(f"## {layer.value.upper().replace('_', ' ')}")
                    sections.append(layer_content.content.strip())
                    sections.append("")  # Blank line
        
        # Render extensions
        if self.extensions:
            sections.append("## EXTENSIONS")
            for ext in InstructionalExtension:
                if ext in self.extensions:
                    ext_content = self.extensions[ext]
                    if ext_content.enabled and ext_content.content:
                        sections.append(f"### {ext.value.upper().replace('_', ' ')}")
                        sections.append(ext_content.content.strip())
                        sections.append("")  # Blank line
        
        return "\n".join(sections).strip()
    
    def validate(self) -> List[str]:
        """Validate prompt completeness and return list of issues."""
        issues = []
        
        # Check required layers
        required_layers = [
            InstructionalLayer.AGENT_IDENTITY,
            InstructionalLayer.ROLE_DEFINITION,
            InstructionalLayer.PRIMARY_OBJECTIVE,
            InstructionalLayer.OUTPUT_FORMAT,
        ]
        
        for layer in required_layers:
            if layer not in self.layers:
                issues.append(f"Missing required layer: {layer.value}")
            elif not self.layers[layer].content:
                issues.append(f"Empty required layer: {layer.value}")
        
        # Check layer priorities
        for layer, content in self.layers.items():
            if content.priority < 1 or content.priority > 10:
                issues.append(f"Invalid priority for {layer.value}: {content.priority}")
        
        return issues


# =============================================================================
# Layer Templates for Common Agent Types
# =============================================================================


def create_l1_planner_prompt(
    agent_name: str,
    domain: str,
    objective: str,
) -> InstructionalPrompt:
    """Create a v6 prompt for an L1 planner agent."""
    
    prompt = InstructionalPrompt(
        prompt_id=f"l1_planner_{agent_name}",
        agent_type="planner",
        layer_type="L1",
    )
    
    # Identity & Role
    prompt.add_layer(LayerContent(
        layer=InstructionalLayer.AGENT_IDENTITY,
        content=f"You are {agent_name}, a specialized planning agent in the {domain} domain.",
        priority=10,
    ))
    
    prompt.add_layer(LayerContent(
        layer=InstructionalLayer.ROLE_DEFINITION,
        content="Your role is to analyze inputs and produce structured plans. You do NOT execute tasks or call tools directly.",
        priority=10,
    ))
    
    prompt.add_layer(LayerContent(
        layer=InstructionalLayer.CAPABILITY_SCOPE,
        content="You can: analyze requirements, decompose tasks, estimate complexity, identify dependencies. You cannot: execute code, call APIs, modify state.",
        priority=9,
    ))
    
    # Task & Objectives
    prompt.add_layer(LayerContent(
        layer=InstructionalLayer.PRIMARY_OBJECTIVE,
        content=objective,
        priority=10,
    ))
    
    prompt.add_layer(LayerContent(
        layer=InstructionalLayer.SUCCESS_CRITERIA,
        content="A successful plan is: complete, executable, deterministic, and includes all necessary context for execution.",
        priority=8,
    ))
    
    # Reasoning
    prompt.add_layer(LayerContent(
        layer=InstructionalLayer.REASONING_MODE,
        content="Use analytical reasoning. Break down complex objectives into atomic steps. Consider dependencies and ordering.",
        priority=8,
    ))
    
    # Output
    prompt.add_layer(LayerContent(
        layer=InstructionalLayer.OUTPUT_FORMAT,
        content="Output a structured plan in JSON format with fields: steps (list), dependencies (dict), estimated_complexity (string), metadata (dict).",
        priority=10,
    ))
    
    # Safety
    prompt.add_layer(LayerContent(
        layer=InstructionalLayer.SAFETY_CONSTRAINTS,
        content="Never include destructive operations in plans. Always validate inputs. Flag ambiguous requirements.",
        priority=9,
    ))
    
    return prompt


def create_l2_executor_prompt(
    agent_name: str,
    domain: str,
    capabilities: List[str],
) -> InstructionalPrompt:
    """Create a v6 prompt for an L2 executor agent."""
    
    prompt = InstructionalPrompt(
        prompt_id=f"l2_executor_{agent_name}",
        agent_type="executor",
        layer_type="L2",
    )
    
    # Identity & Role
    prompt.add_layer(LayerContent(
        layer=InstructionalLayer.AGENT_IDENTITY,
        content=f"You are {agent_name}, a specialized execution agent in the {domain} domain.",
        priority=10,
    ))
    
    prompt.add_layer(LayerContent(
        layer=InstructionalLayer.ROLE_DEFINITION,
        content="Your role is to execute plans produced by L1 planners. You do NOT create plans or orchestrate workflows.",
        priority=10,
    ))
    
    prompt.add_layer(LayerContent(
        layer=InstructionalLayer.CAPABILITY_SCOPE,
        content=f"You can: {', '.join(capabilities)}. You cannot: plan, orchestrate, modify state directly.",
        priority=9,
    ))
    
    # Task & Objectives
    prompt.add_layer(LayerContent(
        layer=InstructionalLayer.PRIMARY_OBJECTIVE,
        content="Execute the provided plan step-by-step, producing structured results for each step.",
        priority=10,
    ))
    
    # Reasoning
    prompt.add_layer(LayerContent(
        layer=InstructionalLayer.REASONING_MODE,
        content="Use procedural reasoning. Follow the plan exactly. Report errors immediately. Do not improvise.",
        priority=9,
    ))
    
    # Error Recovery
    prompt.add_layer(LayerContent(
        layer=InstructionalLayer.ERROR_RECOVERY,
        content="On error: stop execution, report the error with context, do not attempt recovery without explicit instructions.",
        priority=9,
    ))
    
    # Output
    prompt.add_layer(LayerContent(
        layer=InstructionalLayer.OUTPUT_FORMAT,
        content="Output structured results in JSON format with fields: status (success/error), results (dict), errors (list), metadata (dict).",
        priority=10,
    ))
    
    return prompt


# =============================================================================
# Extension Templates
# =============================================================================


def add_rag_extension(prompt: InstructionalPrompt, rag_config: Dict[str, Any]) -> None:
    """Add RAG extension to a prompt."""
    
    top_k = rag_config.get("top_k", 10)
    score_threshold = rag_config.get("score_threshold", 0.7)
    
    prompt.add_extension(ExtensionContent(
        extension=InstructionalExtension.RAG_INTEGRATION,
        content=f"""
You have access to retrieved context from a vector database.

Retrieval Configuration:
- Top K results: {top_k}
- Score threshold: {score_threshold}
- Metadata filters: {rag_config.get('filters', 'none')}

How to use retrieved context:
1. Review all retrieved documents for relevance
2. Cite sources when using retrieved information
3. Flag low-confidence retrievals
4. Combine multiple sources when appropriate
5. Do not hallucinate beyond retrieved context
""".strip(),
        enabled=True,
        metadata=rag_config,
    ))


def add_temporal_extension(prompt: InstructionalPrompt) -> None:
    """Add temporal reasoning extension to a prompt."""
    
    prompt.add_extension(ExtensionContent(
        extension=InstructionalExtension.TEMPORAL_REASONING,
        content="""
You have access to temporal context and historical data.

Temporal Reasoning Guidelines:
1. Consider time-series trends and patterns
2. Account for temporal dependencies between events
3. Distinguish between current state and historical state
4. Use timestamps to order and correlate events
5. Detect anomalies in temporal sequences
6. Forecast future states when appropriate
""".strip(),
        enabled=True,
    ))


def add_cot_extension(prompt: InstructionalPrompt) -> None:
    """Add Chain-of-Thought extension to a prompt."""
    
    prompt.add_extension(ExtensionContent(
        extension=InstructionalExtension.CHAIN_OF_THOUGHT,
        content="""
Use step-by-step reasoning for complex tasks.

Chain-of-Thought Process:
1. Break down the problem into sub-problems
2. Solve each sub-problem explicitly
3. Show your reasoning at each step
4. Verify intermediate results
5. Combine sub-solutions into final answer
6. Double-check the final answer

Format your reasoning as:
Step 1: [description] → [result]
Step 2: [description] → [result]
...
Final Answer: [answer]
""".strip(),
        enabled=True,
    ))



