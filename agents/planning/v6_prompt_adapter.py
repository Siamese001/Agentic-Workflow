"""V6 Prompt Adapter - Wire v6 prompts to L1 planners

This module adapts v6 instructional prompts for use in L1 planning agents.
It bridges the v6 prompt system with existing L1 planning functions.

Layer: L1 (Planning)
Responsibilities:
- Adapt v6 prompts to L1 planner interface
- Inject many-shot examples into planning
- Wire extensions (RAG, CoT, temporal) to planners
- Provide backward-compatible interface

Non-responsibilities:
- LLM invocation (L2)
- Orchestration (L3)
- State management (L4)
- Policy enforcement (L5)
"""

from __future__ import annotations

from typing import Any, Dict, Optional
from dataclasses import dataclass

from core.models.models import ExecutionContext
from prompts.v6_prompt_integration import (
    create_strategy_planner_prompt,
    create_rag_planner_prompt,
    create_qa_planner_prompt,
    create_safety_planner_prompt,
)


@dataclass
class V6PromptConfig:
    """Configuration for v6 prompt generation."""
    
    include_examples: bool = True
    enable_cot: bool = True
    rag_config: Optional[Dict[str, Any]] = None


def build_v6_strategy_prompt(
    ctx: ExecutionContext,
    job: Any,
    resume: Any,
    config: Any,
    v6_config: Optional[V6PromptConfig] = None,
) -> str:
    """Build v6 strategy planner prompt with context.
    
    Args:
        ctx: Execution context with L4 adapters
        job: Job description
        resume: Resume data
        config: Configuration
        v6_config: V6 prompt configuration
        
    Returns:
        Rendered v6 prompt string
    """
    if v6_config is None:
        v6_config = V6PromptConfig()
    
    # Generate base v6 prompt
    base_prompt = create_strategy_planner_prompt(
        include_examples=v6_config.include_examples,
        enable_cot=v6_config.enable_cot,
    )
    
    # Add context-specific information
    context_section = _build_context_section(ctx, job, resume, config)
    
    # Combine base prompt with context
    full_prompt = f"{base_prompt}\n\n{context_section}"
    
    return full_prompt


def build_v6_rag_prompt(
    ctx: ExecutionContext,
    rag_plan: Any,
    v6_config: Optional[V6PromptConfig] = None,
) -> str:
    """Build v6 RAG planner prompt with context.
    
    Args:
        ctx: Execution context with L4 adapters
        rag_plan: RAG plan from workflow
        v6_config: V6 prompt configuration
        
    Returns:
        Rendered v6 prompt string
    """
    if v6_config is None:
        v6_config = V6PromptConfig(
            rag_config={
                "top_k": 10,
                "score_threshold": 0.7,
            }
        )
    
    # Generate base v6 prompt with RAG extension
    base_prompt = create_rag_planner_prompt(
        include_examples=v6_config.include_examples,
        rag_config=v6_config.rag_config,
    )
    
    # Add RAG-specific context
    rag_context = _build_rag_context_section(ctx, rag_plan)
    
    # Combine
    full_prompt = f"{base_prompt}\n\n{rag_context}"
    
    return full_prompt


def build_v6_qa_prompt(
    ctx: ExecutionContext,
    qa_plan: Any,
    draft_result: Any,
    v6_config: Optional[V6PromptConfig] = None,
) -> str:
    """Build v6 QA planner prompt with context.
    
    Args:
        ctx: Execution context
        qa_plan: QA plan from workflow
        draft_result: Drafting result to QA
        v6_config: V6 prompt configuration
        
    Returns:
        Rendered v6 prompt string
    """
    if v6_config is None:
        v6_config = V6PromptConfig()
    
    # Generate base v6 prompt
    base_prompt = create_qa_planner_prompt(
        include_examples=v6_config.include_examples,
    )
    
    # Add QA-specific context
    qa_context = _build_qa_context_section(ctx, qa_plan, draft_result)
    
    # Combine
    full_prompt = f"{base_prompt}\n\n{qa_context}"
    
    return full_prompt


def build_v6_safety_prompt(
    ctx: ExecutionContext,
    safety_plan: Any,
    draft_result: Any,
    v6_config: Optional[V6PromptConfig] = None,
) -> str:
    """Build v6 safety planner prompt with context.
    
    Args:
        ctx: Execution context
        safety_plan: Safety plan from workflow
        draft_result: Drafting result to check
        v6_config: V6 prompt configuration
        
    Returns:
        Rendered v6 prompt string
    """
    if v6_config is None:
        v6_config = V6PromptConfig()
    
    # Generate base v6 prompt
    base_prompt = create_safety_planner_prompt(
        include_examples=v6_config.include_examples,
    )
    
    # Add safety-specific context
    safety_context = _build_safety_context_section(ctx, safety_plan, draft_result)
    
    # Combine
    full_prompt = f"{base_prompt}\n\n{safety_context}"
    
    return full_prompt


# =============================================================================
# Context Section Builders
# =============================================================================


def _build_context_section(
    ctx: ExecutionContext,
    job: Any,
    resume: Any,
    config: Any,
) -> str:
    """Build context section for strategy planning."""
    
    sections = ["## CURRENT CONTEXT", ""]
    
    # Job information
    if job:
        job_title = getattr(job, "title", "Unknown")
        job_company = getattr(job, "company", "Unknown")
        sections.append(f"**Job Title:** {job_title}")
        sections.append(f"**Company:** {job_company}")
        sections.append("")
    
    # Resume information
    if resume:
        resume_name = getattr(resume, "name", "Candidate")
        sections.append(f"**Candidate:** {resume_name}")
        sections.append("")
    
    # L4 Context (if available)
    if ctx.pinecone_adapter:
        namespace = ctx.get_pinecone_namespace()
        sections.append(f"**Vector Store Namespace:** {namespace}")
        sections.append("")
    
    # RAG Results (if available)
    if ctx.rag_results:
        sections.append(f"**Retrieved Evidence:** {len(ctx.rag_results)} items")
        sections.append("")
    
    # Temporal KG Facts (if available)
    if ctx.temporal_kg_facts:
        sections.append(f"**Temporal Facts:** {len(ctx.temporal_kg_facts)} facts")
        sections.append("")
    
    sections.append("## YOUR TASK")
    sections.append("")
    sections.append("Analyze the above context and produce a structured strategy plan in JSON format.")
    
    return "\n".join(sections)


def _build_rag_context_section(
    ctx: ExecutionContext,
    rag_plan: Any,
) -> str:
    """Build context section for RAG planning."""
    
    sections = ["## CURRENT CONTEXT", ""]
    
    # L4 Pinecone adapter info
    if ctx.pinecone_adapter:
        namespace = ctx.get_pinecone_namespace()
        sections.append(f"**Vector Store Namespace:** {namespace}")
        sections.append("")
    
    # RAG plan details
    if rag_plan:
        top_k = getattr(rag_plan, "top_k", 10)
        sections.append(f"**Requested Results:** {top_k}")
        sections.append("")
    
    sections.append("## YOUR TASK")
    sections.append("")
    sections.append("Create optimized retrieval queries to find relevant evidence from the vector store.")
    
    return "\n".join(sections)


def _build_qa_context_section(
    ctx: ExecutionContext,
    qa_plan: Any,
    draft_result: Any,
) -> str:
    """Build context section for QA planning."""
    
    sections = ["## CURRENT CONTEXT", ""]
    
    # Draft sections to QA
    if draft_result:
        sections_count = len(getattr(draft_result, "sections", []))
        sections.append(f"**Draft Sections:** {sections_count}")
        sections.append("")
    
    sections.append("## YOUR TASK")
    sections.append("")
    sections.append("Create a comprehensive QA plan to validate the drafted resume content.")
    
    return "\n".join(sections)


def _build_safety_context_section(
    ctx: ExecutionContext,
    safety_plan: Any,
    draft_result: Any,
) -> str:
    """Build context section for safety planning."""
    
    sections = ["## CURRENT CONTEXT", ""]
    
    # Draft sections to check
    if draft_result:
        sections_count = len(getattr(draft_result, "sections", []))
        sections.append(f"**Draft Sections:** {sections_count}")
        sections.append("")
    
    sections.append("## YOUR TASK")
    sections.append("")
    sections.append("Create a safety review plan to detect and prevent problematic content.")
    
    return "\n".join(sections)



