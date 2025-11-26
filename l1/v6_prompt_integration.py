"""
V6 Prompt Integration for resume generation system.

Integrates instructional prompts with planners to ensure consistent
resume improvement and job alignment.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .instructional_injection_v6 import (
    InstructionalPrompt,
    InstructionalLayer,
    InstructionalExtension,
    LayerContent,
    ExtensionContent,
    create_l1_planner_prompt,
    create_l2_executor_prompt,
    add_rag_extension,
    add_temporal_extension,
    add_cot_extension,
)
from .many_shot_examples import (
    ExampleType,
    get_examples,
    format_examples_for_prompt,
)


# =============================================================================
# L1 Planner Prompt Factories
# =============================================================================


def create_strategy_planner_prompt(
    include_examples: bool = True,
    enable_cot: bool = True,
) -> str:
    """
Creates v6 prompt for L1 strategy planner with resume examples.

Generates structured approach for optimal resume job alignment
and enhanced content quality.
    """
    prompt = create_l1_planner_prompt(
        agent_name="Strategy Planner",
        domain="resume tailoring",
        objective="Analyze job description and resume to create a tailored strategy plan that emphasizes relevant experience and skills.",
    )
    
    # Add domain-specific layers
    prompt.add_layer(LayerContent(
        layer=InstructionalLayer.DOMAIN_CONTEXT,
        content="""
Domain: Resume Tailoring for Job Applications

Key Concepts:
- Job requirements: Skills, experience, and qualifications sought by employer
- Resume content: Candidate's experience, skills, and achievements
- Strategy: Approach to emphasize relevant content and deemphasize irrelevant content
- Tone: Professional communication style appropriate for the role level
- Gaps: Missing qualifications that need mitigation strategies
""".strip(),
        priority=8,
    ))
    
    prompt.add_layer(LayerContent(
        layer=InstructionalLayer.DOMAIN_KNOWLEDGE,
        content="""
Resume Tailoring Best Practices:
1. Match keywords from job description (ATS optimization)
2. Quantify achievements with metrics when possible
3. Emphasize recent and relevant experience
4. Address gaps proactively with mitigation strategies
5. Adjust tone based on role level (entry/mid/senior/executive)
6. Highlight transferable skills for career transitions
7. Use action verbs and achievement-focused language
""".strip(),
        priority=7,
    ))
    
    prompt.add_layer(LayerContent(
        layer=InstructionalLayer.CONSTRAINTS,
        content="""
Hard Constraints:
- Never fabricate experience or skills
- Never suggest misleading information
- Plans must be executable by L2 agents
- Output must be valid JSON

Soft Constraints:
- Prefer recent experience (last 3-5 years)
- Limit strategy to 3-5 key themes
- Keep complexity estimates realistic
""".strip(),
        priority=9,
    ))
    
    # Add Chain-of-Thought if enabled
    if enable_cot:
        add_cot_extension(prompt)
    
    # Render base prompt
    base_prompt = prompt.render()
    
    # Add examples if requested
    if include_examples:
        examples = get_examples(
            example_type=ExampleType.L1_STRATEGY_PLANNING,
            max_examples=4,
            min_quality=0.9,
        )
        examples_section = format_examples_for_prompt(examples)
        return f"{base_prompt}\n\n{examples_section}"
    
    return base_prompt


def create_rag_planner_prompt(
    include_examples: bool = True,
    rag_config: Optional[Dict[str, Any]] = None,
) -> str:
    """Create v6 prompt for L1 RAG planner with examples.
    
    Args:
        include_examples: Whether to include many-shot examples
        rag_config: RAG configuration (top_k, filters, etc.)
        
    Returns:
        Rendered prompt string
    """
    prompt = create_l1_planner_prompt(
        agent_name="RAG Planner",
        domain="retrieval-augmented generation",
        objective="Create optimized retrieval plans to find relevant evidence from vector stores and knowledge bases.",
    )
    
    # Add RAG-specific layers
    prompt.add_layer(LayerContent(
        layer=InstructionalLayer.DOMAIN_CONTEXT,
        content="""
Domain: Retrieval-Augmented Generation (RAG)

Key Concepts:
- Query formulation: Crafting effective search queries
- Vector similarity: Semantic search in embedding space
- Metadata filtering: Narrowing results by attributes
- Temporal filtering: Time-based result filtering
- Reranking: Improving result relevance
- Multi-query: Multiple queries for comprehensive coverage
""".strip(),
        priority=8,
    ))
    
    prompt.add_layer(LayerContent(
        layer=InstructionalLayer.DOMAIN_KNOWLEDGE,
        content="""
RAG Best Practices:
1. Use multiple queries for complex information needs
2. Apply metadata filters to narrow scope
3. Set appropriate score thresholds (typically 0.7-0.8)
4. Use temporal filters for time-sensitive queries
5. Enable reranking for better precision
6. Balance recall (top_k) with precision (threshold)
7. Consider query expansion for better coverage
""".strip(),
        priority=7,
    ))
    
    # Add RAG extension
    if rag_config is None:
        rag_config = {"top_k": 10, "score_threshold": 0.7}
    add_rag_extension(prompt, rag_config)
    
    # Render base prompt
    base_prompt = prompt.render()
    
    # Add examples if requested
    if include_examples:
        examples = get_examples(
            example_type=ExampleType.L1_RAG_PLANNING,
            max_examples=3,
            min_quality=0.9,
        )
        examples_section = format_examples_for_prompt(examples)
        return f"{base_prompt}\n\n{examples_section}"
    
    return base_prompt


def create_qa_planner_prompt(
    include_examples: bool = True,
) -> str:
    """Create v6 prompt for L1 QA planner with examples.
    
    Args:
        include_examples: Whether to include many-shot examples
        
    Returns:
        Rendered prompt string
    """
    prompt = create_l1_planner_prompt(
        agent_name="QA Planner",
        domain="quality assurance",
        objective="Create comprehensive QA plans to validate resume quality, accuracy, and alignment with job requirements.",
    )
    
    # Add QA-specific layers
    prompt.add_layer(LayerContent(
        layer=InstructionalLayer.DOMAIN_CONTEXT,
        content="""
Domain: Resume Quality Assurance

Key Concepts:
- Accuracy: Factual correctness of claims
- Completeness: All required sections present
- Consistency: Uniform style and formatting
- Relevance: Alignment with job requirements
- Readability: Clear and professional language
- ATS compatibility: Keyword optimization
""".strip(),
        priority=8,
    ))
    
    prompt.add_layer(LayerContent(
        layer=InstructionalLayer.DOMAIN_KNOWLEDGE,
        content="""
QA Check Categories:
1. Content accuracy (no fabrications)
2. Grammar and spelling
3. Formatting consistency
4. Keyword alignment with job description
5. Achievement quantification
6. Professional tone
7. Section completeness
8. Contact information validity
9. Date consistency
10. ATS optimization
""".strip(),
        priority=7,
    ))
    
    # Render base prompt
    base_prompt = prompt.render()
    
    # Add examples if requested (when available)
    if include_examples:
        # QA examples would be added here when created
        pass
    
    return base_prompt


def create_safety_planner_prompt(
    include_examples: bool = True,
) -> str:
    """Create v6 prompt for L1 safety planner with examples.
    
    Args:
        include_examples: Whether to include many-shot examples
        
    Returns:
        Rendered prompt string
    """
    prompt = create_l1_planner_prompt(
        agent_name="Safety Planner",
        domain="content safety",
        objective="Create safety review plans to detect and prevent problematic content in resumes.",
    )
    
    # Add safety-specific layers
    prompt.add_layer(LayerContent(
        layer=InstructionalLayer.SAFETY_CONSTRAINTS,
        content="""
Safety Categories to Check:
1. No fabricated experience or credentials
2. No misleading claims
3. No protected class information (age, race, religion, etc.)
4. No inappropriate language
5. No confidential information from previous employers
6. No false certifications or degrees
7. No plagiarized content
""".strip(),
        priority=10,
    ))
    
    prompt.add_layer(LayerContent(
        layer=InstructionalLayer.ETHICAL_GUIDELINES,
        content="""
Ethical Guidelines:
1. Truthfulness: All claims must be factually accurate
2. Privacy: Respect confidentiality of previous employers
3. Fairness: Avoid discriminatory content
4. Transparency: Be honest about gaps and transitions
5. Professionalism: Maintain appropriate tone
""".strip(),
        priority=10,
    ))
    
    # Render base prompt
    base_prompt = prompt.render()
    
    return base_prompt


# =============================================================================
# L2 Executor Prompt Factories
# =============================================================================


def create_strategy_executor_prompt(
    include_examples: bool = True,
) -> str:
    """Create v6 prompt for L2 strategy executor with examples.
    
    Args:
        include_examples: Whether to include many-shot examples
        
    Returns:
        Rendered prompt string
    """
    prompt = create_l2_executor_prompt(
        agent_name="Strategy Executor",
        domain="resume tailoring",
        capabilities=[
            "analyze job requirements",
            "identify key themes",
            "select emphasis areas",
            "determine tone",
            "estimate complexity",
        ],
    )
    
    # Add execution-specific layers
    prompt.add_layer(LayerContent(
        layer=InstructionalLayer.PROCEDURAL_MEMORY,
        content="""
Execution Procedure:
1. Parse strategy plan from L1
2. Extract job requirements and resume content
3. Apply strategy approach (technical_depth, transferable_skills, etc.)
4. Generate tailored content sections
5. Validate output against plan
6. Return structured result
""".strip(),
        priority=8,
    ))
    
    # Render base prompt
    base_prompt = prompt.render()
    
    # Add examples if requested
    if include_examples:
        examples = get_examples(
            example_type=ExampleType.L2_STRATEGY_EXECUTION,
            max_examples=2,
            min_quality=0.9,
        )
        examples_section = format_examples_for_prompt(examples)
        return f"{base_prompt}\n\n{examples_section}"
    
    return base_prompt


# =============================================================================
# Prompt Validation
# =============================================================================


def validate_v6_prompt(prompt: InstructionalPrompt) -> List[str]:
    """Validate a v6 prompt for completeness and correctness.
    
    Args:
        prompt: InstructionalPrompt to validate
        
    Returns:
        List of validation issues (empty if valid)
    """
    issues = prompt.validate()
    
    # Additional v6-specific validations
    if prompt.layer_type == "L1":
        # L1 planners should have reasoning layers
        if InstructionalLayer.REASONING_MODE not in prompt.layers:
            issues.append("L1 planner missing REASONING_MODE layer")
        if InstructionalLayer.DOMAIN_KNOWLEDGE not in prompt.layers:
            issues.append("L1 planner missing DOMAIN_KNOWLEDGE layer")
    
    if prompt.layer_type == "L2":
        # L2 executors should have procedural memory
        if InstructionalLayer.PROCEDURAL_MEMORY not in prompt.layers:
            issues.append("L2 executor missing PROCEDURAL_MEMORY layer")
        if InstructionalLayer.ERROR_RECOVERY not in prompt.layers:
            issues.append("L2 executor missing ERROR_RECOVERY layer")
    
    return issues



