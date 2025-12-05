"""
Many-Shot Examples for resume generation workflow guidance.

Provides high-quality examples for L1 planners and executors
to improve resume quality and job alignment.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List
from enum import Enum


class ExampleType(str, Enum):
    """
    Type of example for resume generation workflow.

    Defines example categories for improved resume quality guidance.
    """
    
    L1_STRATEGY_PLANNING = "l1_strategy_planning"
    L1_RAG_PLANNING = "l1_rag_planning"
    L1_QA_PLANNING = "l1_qa_planning"
    L1_SAFETY_PLANNING = "l1_safety_planning"
    L1_DRAFTING_PLANNING = "l1_drafting_planning"
    
    L2_STRATEGY_EXECUTION = "l2_strategy_execution"
    L2_RAG_EXECUTION = "l2_rag_execution"
    L2_DRAFTING_EXECUTION = "l2_drafting_execution"
    L2_QA_EXECUTION = "l2_qa_execution"
    L2_SAFETY_EXECUTION = "l2_safety_execution"
    
    L3_WORKFLOW_ORCHESTRATION = "l3_workflow_orchestration"
    L3_DAG_EXECUTION = "l3_dag_execution"
    L3_MULTI_AGENT_COORDINATION = "l3_multi_agent_coordination"


@dataclass
class Example:
    """A single input-output example."""
    
    example_id: str
    example_type: ExampleType
    description: str
    input_data: Dict[str, Any]
    expected_output: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    quality_score: float = 1.0  # 0.0-1.0


# =============================================================================
# L1 Strategy Planning Examples
# =============================================================================

STRATEGY_PLANNING_EXAMPLES = [
    Example(
        example_id="strategy_plan_001",
        example_type=ExampleType.L1_STRATEGY_PLANNING,
        description="Basic strategy planning for software engineer resume",
        input_data={
            "job_title": "Senior Software Engineer",
            "job_description": "Looking for experienced backend engineer with Python, AWS, and microservices experience. Must have 5+ years experience.",
            "resume_summary": "Software engineer with 6 years experience in Python, Django, and cloud infrastructure.",
            "complexity": "medium",
        },
        expected_output={
            "strategy_id": "strat_001",
            "approach": "technical_depth",
            "key_themes": [
                "Backend expertise with Python/Django",
                "Cloud infrastructure (AWS)",
                "Microservices architecture",
                "6 years experience (exceeds requirement)"
            ],
            "emphasis_areas": [
                "Python and Django projects",
                "AWS services used",
                "Microservices design patterns",
                "System scalability achievements"
            ],
            "deemphasis_areas": [
                "Frontend work",
                "Non-Python languages",
                "Desktop applications"
            ],
            "tone": "technical and achievement-focused",
            "estimated_complexity": "medium",
            "confidence": 0.9,
        },
        quality_score=1.0,
    ),
    
    Example(
        example_id="strategy_plan_002",
        example_type=ExampleType.L1_STRATEGY_PLANNING,
        description="Career transition strategy (different domain)",
        input_data={
            "job_title": "Data Scientist",
            "job_description": "Seeking data scientist with ML/AI experience, Python, and statistical modeling. PhD preferred.",
            "resume_summary": "Software engineer with strong Python skills, some ML coursework, no PhD.",
            "complexity": "high",
        },
        expected_output={
            "strategy_id": "strat_002",
            "approach": "transferable_skills",
            "key_themes": [
                "Strong Python foundation",
                "Self-taught ML/AI skills",
                "Analytical problem-solving",
                "Continuous learning mindset"
            ],
            "emphasis_areas": [
                "Python data analysis projects",
                "ML/AI coursework and projects",
                "Statistical analysis experience",
                "Self-directed learning"
            ],
            "deemphasis_areas": [
                "Traditional software engineering",
                "Lack of PhD (address with experience)",
                "Non-data-related work"
            ],
            "gap_mitigation": [
                "Highlight ML projects and coursework",
                "Emphasize practical experience over credentials",
                "Show continuous learning trajectory"
            ],
            "tone": "enthusiastic and growth-oriented",
            "estimated_complexity": "high",
            "confidence": 0.7,
            "risks": ["PhD requirement may be strict", "Limited formal ML experience"],
        },
        quality_score=0.95,
    ),
    
    Example(
        example_id="strategy_plan_003",
        example_type=ExampleType.L1_STRATEGY_PLANNING,
        description="Executive-level strategy (leadership focus)",
        input_data={
            "job_title": "VP of Engineering",
            "job_description": "Leading 50+ person engineering org, scaling systems, building culture, strategic planning.",
            "resume_summary": "Engineering manager with 10 years experience, managed teams of 15, strong technical background.",
            "complexity": "high",
        },
        expected_output={
            "strategy_id": "strat_003",
            "approach": "leadership_and_scale",
            "key_themes": [
                "Team leadership and scaling",
                "Strategic technical vision",
                "Culture building",
                "Cross-functional collaboration"
            ],
            "emphasis_areas": [
                "Team growth (15 → 50+ trajectory)",
                "Strategic initiatives led",
                "Organizational improvements",
                "Mentorship and culture building"
            ],
            "deemphasis_areas": [
                "Individual contributor work",
                "Tactical technical details",
                "Small-scale projects"
            ],
            "tone": "strategic and leadership-focused",
            "estimated_complexity": "high",
            "confidence": 0.85,
        },
        quality_score=0.98,
    ),
    
    Example(
        example_id="strategy_plan_004",
        example_type=ExampleType.L1_STRATEGY_PLANNING,
        description="Entry-level strategy (minimal experience)",
        input_data={
            "job_title": "Junior Developer",
            "job_description": "Entry-level position, CS degree or bootcamp, basic web development skills.",
            "resume_summary": "Recent bootcamp graduate, 2 personal projects, internship experience.",
            "complexity": "low",
        },
        expected_output={
            "strategy_id": "strat_004",
            "approach": "potential_and_enthusiasm",
            "key_themes": [
                "Strong learning ability",
                "Practical project experience",
                "Bootcamp training",
                "Eager to contribute"
            ],
            "emphasis_areas": [
                "Bootcamp projects and skills",
                "Personal projects (show initiative)",
                "Internship contributions",
                "Technical skills acquired"
            ],
            "deemphasis_areas": [
                "Lack of professional experience",
                "Limited portfolio"
            ],
            "tone": "enthusiastic and humble",
            "estimated_complexity": "low",
            "confidence": 0.95,
        },
        quality_score=0.92,
    ),
]


# =============================================================================
# L1 RAG Planning Examples
# =============================================================================

RAG_PLANNING_EXAMPLES = [
    Example(
        example_id="rag_plan_001",
        example_type=ExampleType.L1_RAG_PLANNING,
        description="Basic RAG query planning for technical skills",
        input_data={
            "job_requirements": ["Python", "AWS", "Docker", "Kubernetes"],
            "resume_context": "Software engineer with cloud experience",
            "query_type": "skills_match",
        },
        expected_output={
            "rag_plan_id": "rag_001",
            "queries": [
                {
                    "query": "Python AWS cloud infrastructure projects",
                    "intent": "Find relevant cloud/Python experience",
                    "top_k": 5,
                    "filters": {"category": "technical_skills"},
                },
                {
                    "query": "Docker Kubernetes container orchestration",
                    "intent": "Find containerization experience",
                    "top_k": 3,
                    "filters": {"category": "technical_skills"},
                },
            ],
            "retrieval_strategy": "multi_query",
            "rerank": True,
            "score_threshold": 0.7,
            "estimated_complexity": "low",
        },
        quality_score=1.0,
    ),
    
    Example(
        example_id="rag_plan_002",
        example_type=ExampleType.L1_RAG_PLANNING,
        description="Complex RAG with temporal filtering",
        input_data={
            "job_requirements": ["leadership", "team building", "recent experience"],
            "resume_context": "Engineering manager, 10 years experience",
            "query_type": "leadership_evidence",
            "temporal_constraint": "last_3_years",
        },
        expected_output={
            "rag_plan_id": "rag_002",
            "queries": [
                {
                    "query": "team leadership management experience",
                    "intent": "Find leadership examples",
                    "top_k": 8,
                    "filters": {
                        "category": "leadership",
                        "timestamp": {"$gte": "2021-01-01"},
                    },
                },
                {
                    "query": "team building culture mentorship",
                    "intent": "Find culture-building evidence",
                    "top_k": 5,
                    "filters": {
                        "category": "soft_skills",
                        "timestamp": {"$gte": "2021-01-01"},
                    },
                },
            ],
            "retrieval_strategy": "temporal_multi_query",
            "rerank": True,
            "score_threshold": 0.75,
            "temporal_weighting": "recent_preferred",
            "estimated_complexity": "medium",
        },
        quality_score=0.95,
    ),
]


# =============================================================================
# L2 Execution Examples
# =============================================================================

STRATEGY_EXECUTION_EXAMPLES = [
    Example(
        example_id="strategy_exec_001",
        example_type=ExampleType.L2_STRATEGY_EXECUTION,
        description="Execute strategy plan for technical resume",
        input_data={
            "strategy_plan": {
                "strategy_id": "strat_001",
                "approach": "technical_depth",
                "emphasis_areas": ["Python projects", "AWS services"],
            },
            "job_description": "Senior Software Engineer - Python, AWS",
            "resume_data": {"experience": ["Python developer", "AWS architect"]},
        },
        expected_output={
            "execution_id": "exec_001",
            "status": "success",
            "strategy_result": {
                "chosen_approach": "technical_depth",
                "tailored_sections": ["summary", "experience", "skills"],
                "key_adjustments": [
                    "Emphasized Python and AWS in summary",
                    "Reordered experience to highlight relevant projects",
                    "Added AWS certifications to skills"
                ],
            },
            "metadata": {
                "execution_time_ms": 1250,
                "llm_calls": 1,
            },
        },
        quality_score=1.0,
    ),
]


# =============================================================================
# L3 Orchestration Examples
# =============================================================================

WORKFLOW_ORCHESTRATION_EXAMPLES = [
    Example(
        example_id="workflow_orch_001",
        example_type=ExampleType.L3_WORKFLOW_ORCHESTRATION,
        description="Full workflow orchestration for resume tailoring",
        input_data={
            "workflow_id": "wf_001",
            "job_input": {"title": "Senior Engineer", "company": "TechCo"},
            "resume_input": {"name": "John Doe", "experience": []},
        },
        expected_output={
            "orchestration_id": "orch_001",
            "status": "success",
            "workflow_result": {
                "nodes_executed": ["strategy", "rag", "drafting", "qa", "safety"],
                "execution_order": [
                    "strategy_planning",
                    "rag_planning",
                    "rag_execution",
                    "drafting_planning",
                    "drafting_execution",
                    "qa_planning",
                    "qa_execution",
                    "safety_check",
                ],
                "total_time_ms": 8500,
                "final_output": {"tailored_resume": "..."},
            },
            "metadata": {
                "nodes_total": 8,
                "nodes_succeeded": 8,
                "nodes_failed": 0,
            },
        },
        quality_score=1.0,
    ),
]


# =============================================================================
# Example Registry
# =============================================================================

EXAMPLE_REGISTRY: Dict[ExampleType, List[Example]] = {
    ExampleType.L1_STRATEGY_PLANNING: STRATEGY_PLANNING_EXAMPLES,
    ExampleType.L1_RAG_PLANNING: RAG_PLANNING_EXAMPLES,
    ExampleType.L2_STRATEGY_EXECUTION: STRATEGY_EXECUTION_EXAMPLES,
    ExampleType.L3_WORKFLOW_ORCHESTRATION: WORKFLOW_ORCHESTRATION_EXAMPLES,
}


def get_examples(
    example_type: ExampleType,
    max_examples: int = 4,
    min_quality: float = 0.8,
) -> List[Example]:
    """Retrieve examples by type with quality filtering.
    
    Args:
        example_type: Type of examples to retrieve
        max_examples: Maximum number of examples to return
        min_quality: Minimum quality score threshold
        
    Returns:
        List of examples sorted by quality score (descending)
    """
    examples = EXAMPLE_REGISTRY.get(example_type, [])
    
    # Filter by quality
    filtered = [ex for ex in examples if ex.quality_score >= min_quality]
    
    # Sort by quality (descending)
    sorted_examples = sorted(filtered, key=lambda x: x.quality_score, reverse=True)
    
    # Limit to max_examples
    return sorted_examples[:max_examples]


def format_examples_for_prompt(examples: List[Example]) -> str:
    """Format examples for inclusion in a prompt.
    
    Args:
        examples: List of examples to format
        
    Returns:
        Formatted string with examples
    """
    if not examples:
        return ""
    
    sections = ["## EXAMPLES", ""]
    
    for i, example in enumerate(examples, 1):
        sections.append(f"### Example {i}: {example.description}")
        sections.append("")
        sections.append("**Input:**")
        sections.append("```json")
        import json
        sections.append(json.dumps(example.input_data, indent=2))
        sections.append("```")
        sections.append("")
        sections.append("**Expected Output:**")
        sections.append("```json")
        sections.append(json.dumps(example.expected_output, indent=2))
        sections.append("```")
        sections.append("")
    
    return "\n".join(sections)



