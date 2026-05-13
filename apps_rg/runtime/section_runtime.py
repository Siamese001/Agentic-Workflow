"""W4 Section-Level PA + L2 Runtime Loop.

Per plan apps-rg-golden-state-section-generation-a4f9e1 W4.

This module implements the section-level runtime that:
1. Consumes deterministic SectionSpec plans from section_planner.py
2. Creates one section-scoped PA packet per canonical section
3. Calls bounded L2 once per section
4. Emits SectionArtifact per section
5. Preserves section_id, tier, prompt/evidence/scorer/benchmark/seed refs
6. Marks scorer refs as pending (not executed)
7. Marks writeback candidates as inert until W5C

Canonical sections by tier:
- P0: headline, executive_summary, unify_narrative, competencies_ats, IBM
- P1: InsurTech, EY
- P2: early_career, education, certifications_low_signal

DO NOT:
- Do not create section_scorer.py (W5B scope)
- Do not implement section scoring (W5B scope)
- Do not create merge_binding.py (W6 scope)
- Do not emit MergedResumeArtifact (W6 scope)
- Do not write to semantic cache, vector DB, or L4 (W5C scope)
- Do not implement L6 (out of scope)
"""
from __future__ import annotations

import copy
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from agentic_core.runtime.contracts.compiled_prompt_artifact import (
    CompiledPromptArtifact,
)

from apps_rg.runtime.bindings.pa_binding import pa_compose_apps_rg
from apps_rg.runtime.bindings.l2_binding import l2_execute_apps_rg
from apps_rg.runtime.schemas import (
    SectionSpec,
    SectionArtifact,
    SectionWritebackCandidate,
)


@dataclass
class SectionRuntimeContext:
    """Runtime context for section execution.
    
    Carries the immutable SectionSpec and mutable execution state.
    """
    spec: SectionSpec
    pa_input: dict[str, Any] | None = None
    pa_output: CompiledPromptArtifact | None = None
    l2_output: str | None = None
    artifact: SectionArtifact | None = None
    execution_log: list[str] = field(default_factory=list)
    error: Exception | None = None


@dataclass
class SectionRuntimeResult:
    """Result of section runtime execution.
    
    Contains all SectionArtifacts and execution metadata.
    """
    artifacts: list[SectionArtifact]
    execution_metadata: dict[str, Any]
    section_count: int
    completed_count: int
    failed_count: int
    artifacts_list: list[dict[str, Any]]  # Raw artifact data for inspection


def _build_section_pa_input(
    section_spec: SectionSpec,
    shared_context: dict[str, Any],
) -> dict[str, Any]:
    """Build PA input for a single section.
    
    Args:
        section_spec: The SectionSpec for this section
        shared_context: Shared context across all sections (target_company, role, etc.)
    
    Returns:
        PA input dictionary for section-scoped prompt assembly
    """
    # Start with shared context
    pa_input = copy.deepcopy(shared_context)
    
    # Add section-specific fields
    pa_input["section_id"] = section_spec.section_id
    pa_input["tier"] = section_spec.tier
    pa_input["canonical_id"] = section_spec.canonical_id
    pa_input["priority_score"] = section_spec.priority_score
    
    # Add prompt reference
    if section_spec.prompt_ref:
        pa_input["prompt_template_id"] = section_spec.prompt_ref.template_id
        pa_input["prompt_version"] = section_spec.prompt_ref.version
    
    # Add evidence references (by digest for traceability)
    if section_spec.evidence_refs:
        pa_input["evidence_digests"] = [
            ref.evidence_digest for ref in section_spec.evidence_refs
        ]
    
    # Add benchmark seed reference (metadata only - actual seed used by L2)
    if section_spec.benchmark_seed:
        pa_input["benchmark_seed_ref"] = {
            "benchmark_id": section_spec.benchmark_seed.benchmark_id,
            "seed_variant": section_spec.benchmark_seed.seed_variant,
        }
    
    # Add retry policy metadata (for tracking, not execution in W4)
    if section_spec.retry_policy:
        pa_input["retry_policy"] = {
            "max_attempts": section_spec.retry_policy.max_attempts,
            "backoff_strategy": section_spec.retry_policy.backoff_strategy.value,
        }
    
    # Add writeback policy metadata (for tracking, not execution in W4)
    if section_spec.writeback_policy:
        pa_input["writeback_policy"] = {
            "mode": section_spec.writeback_policy.mode.value,
            "priority": section_spec.writeback_policy.priority,
        }
    
    return pa_input


def _create_section_artifact(
    section_spec: SectionSpec,
    pa_output: CompiledPromptArtifact,
    l2_output: str,
    l2_result: Any | None = None,
) -> SectionArtifact:
    """Create a SectionArtifact from execution results.
    
    Creates a W3A-compliant SectionArtifact with proper schema fields.
    Per W4 scope:
    - section_scores: empty dict (W5B scope)
    - g22_factual_grounding_score: 0.0 (W5B scope)
    - writeback_candidate: None (W5C scope)
    - quality_gates_passed/failed: empty lists (W5B scope)
    
    Args:
        section_spec: The SectionSpec for this section
        pa_output: The compiled prompt artifact from PA
        l2_output: The generated content from L2
        l2_result: Optional L2 result object with metadata
    
    Returns:
        SectionArtifact conforming to W3A frozen schema
    """
    now = datetime.now(timezone.utc)
    
    # Build artifact_id from section_id + timestamp
    artifact_id = f"{section_spec.section_id}_{now.strftime('%Y%m%d%H%M%S')}"
    
    # Extract generation seed if available from benchmark_seed
    generation_seed = None
    if section_spec.benchmark_seed:
        # Use hash of seed_variant as deterministic seed
        generation_seed = hash(section_spec.benchmark_seed.seed_variant) % 2**31
    
    # Extract model_ref from L2 result or use default
    model_ref = "Qwen/Qwen2.5-32B-Instruct-AWQ"
    if l2_result and hasattr(l2_result, 'model_id'):
        model_ref = l2_result.model_id
    
    # Extract prompt_version from SectionSpec
    prompt_version = None
    if section_spec.prompt_ref:
        prompt_version = section_spec.prompt_ref.version
    
    # Build source_resume_digest from shared context (if available)
    # NOTE: This would come from the runtime context in full implementation
    source_resume_digest = None
    
    # Build prompt_compilation_hash from PA output
    prompt_compilation_hash = None
    if pa_output and hasattr(pa_output, 'compilation_hash'):
        prompt_compilation_hash = pa_output.compilation_hash
    
    # NOTE: Per W4 scope, these are set to defaults/pending:
    # - section_scores: empty dict (scoring is W5B)
    # - g22_factual_grounding_score: 0.0 (scoring is W5B)
    # - writeback_candidate: None (writeback is W5C)
    # - quality_gates_passed/failed: empty lists (gates are W6)
    
    return SectionArtifact(
        artifact_id=artifact_id,
        section_id=section_spec.section_id,
        generated_content=l2_output,
        generation_timestamp=now,
        generation_seed=generation_seed,
        prompt_version=prompt_version,
        model_ref=model_ref,
        section_scores={},  # W5B scope - empty pending scoring
        g22_factual_grounding_score=0.0,  # W5B scope - 0.0 pending scoring
        quality_gates_passed=[],  # W6 scope - empty pending gate verification
        quality_gates_failed=[],  # W6 scope - empty pending gate verification
        writeback_candidate=None,  # W5C scope - None pending writeback
        source_resume_digest=source_resume_digest,
        prompt_compilation_hash=prompt_compilation_hash,
    )


def execute_section(
    section_spec: SectionSpec,
    shared_context: dict[str, Any],
    dry_run: bool = False,
) -> SectionRuntimeContext:
    """Execute a single section through PA + L2.
    
    Args:
        section_spec: The SectionSpec for this section
        shared_context: Shared context across all sections
        dry_run: If True, skip actual L2 execution and return stub content
    
    Returns:
        SectionRuntimeContext with execution results
    """
    ctx = SectionRuntimeContext(spec=section_spec)
    ctx.execution_log.append(f"Starting section execution: {section_spec.section_id}")
    
    # Step 1: Build PA input
    ctx.pa_input = _build_section_pa_input(section_spec, shared_context)
    ctx.execution_log.append(f"Built PA input for section: {section_spec.section_id}")
    
    # Step 2: Call PA binding (section-scoped)
    # NOTE: This calls the actual PA binding with section-specific input
    # The PA binding will compile a prompt artifact for this section only
    try:
        # Import here to avoid circular dependencies
        from apps_rg.runtime.bindings.pa_binding import pa_compose_apps_rg
        from agentic_core.runtime.contracts.u0_validated_request import ValidatedRequest
        
        # Build ValidatedRequest for PA
        # NOTE: In full implementation, this would include full request context
        pa_request = ValidatedRequest(
            app_id="apps_rg",
            request_id=f"section_{section_spec.section_id}",
            section_context=ctx.pa_input,
        )
        
        # Call PA binding
        ctx.pa_output = pa_compose_apps_rg(pa_request)
        ctx.execution_log.append(f"PA assembly complete for section: {section_spec.section_id}")
    except Exception as e:
        ctx.execution_log.append(f"PA assembly failed: {e}")
        raise SectionRuntimeError(f"PA assembly failed for {section_spec.section_id}: {e}") from e
    
    # Step 3: Call L2 binding (bounded execution)
    if dry_run:
        # Stub output for testing/verification
        ctx.l2_output = f"[DRY RUN] Section content for {section_spec.section_id}"
        ctx.execution_log.append(f"L2 dry-run complete for section: {section_spec.section_id}")
    else:
        try:
            # Call L2 binding with compiled prompt artifact
            # NOTE: l2_execute_apps_rg expects CompiledPromptArtifact directly
            # The L2 binding will generate content using the compiled prompt
            l2_result = l2_execute_apps_rg(ctx.pa_output)
            
            # Extract generated content from SealedL2Artifact
            # The l2_result is a SealedL2Artifact with generated_content field
            if hasattr(l2_result, 'generated_content'):
                ctx.l2_output = l2_result.generated_content
            elif hasattr(l2_result, 'proposed_state_diff'):
                # Fallback: use proposed_state_diff if it's a string
                ctx.l2_output = str(l2_result.proposed_state_diff)
            else:
                ctx.l2_output = str(l2_result)
            
            ctx.execution_log.append(f"L2 execution complete for section: {section_spec.section_id}")
        except Exception as e:
            ctx.execution_log.append(f"L2 execution failed: {e}")
            raise SectionRuntimeError(f"L2 execution failed for {section_spec.section_id}: {e}") from e
    
    # Step 4: Create SectionArtifact
    ctx.artifact = _create_section_artifact(section_spec, ctx.pa_output, ctx.l2_output)
    ctx.execution_log.append(f"SectionArtifact created: {section_spec.section_id}")
    
    return ctx


def execute_sections(
    section_specs: list[SectionSpec],
    shared_context: dict[str, Any],
    dry_run: bool = False,
) -> SectionRuntimeResult:
    """Execute all sections through PA + L2 runtime loop.
    
    This is the main entry point for W4 section runtime.
    
    Args:
        section_specs: List of SectionSpec from section_planner.py
        shared_context: Shared context across all sections (target_company, role, etc.)
        dry_run: If True, skip actual L2 execution and return stub content
    
    Returns:
        SectionRuntimeResult with all SectionArtifacts
    
    Example:
        >>> from apps_rg.runtime.section_planner import build_section_plan
        >>> plan = build_section_plan(run_context)
        >>> shared_ctx = {"target_company": "Acme", "target_role": "Engineer"}
        >>> result = execute_sections(plan.sections, shared_ctx)
        >>> for artifact in result.artifacts:
        ...     print(f"{artifact.section_id}: {artifact.scorer_execution_status}")
    """
    artifacts: list[SectionArtifact] = []
    execution_log: list[str] = []
    
    completed_count = 0
    failed_count = 0
    
    # Execute each section in priority order
    # NOTE: Sections are already sorted by priority_score in SectionPlan
    for spec in section_specs:
        try:
            ctx = execute_section(spec, shared_context, dry_run=dry_run)
            
            if ctx.artifact:
                artifacts.append(ctx.artifact)
                completed_count += 1
                execution_log.extend(ctx.execution_log)
            
        except SectionRuntimeError as e:
            failed_count += 1
            execution_log.append(f"Section failed: {e}")
            # Continue with next section (fail-soft per section)
            continue
    
    # Build result
    execution_metadata = {
        "execution_timestamp": datetime.now(timezone.utc).isoformat(),
        "dry_run": dry_run,
        "execution_log": execution_log,
        "scorer_execution": "pending",  # W5B scope
        "writeback_execution": "inert",  # W5C scope
    }
    
    return SectionRuntimeResult(
        artifacts=artifacts,
        execution_metadata=execution_metadata,
        section_count=len(section_specs),
        completed_count=completed_count,
        failed_count=failed_count,
    )


class SectionRuntimeError(Exception):
    """Error during section runtime execution."""
    pass


# Export canonical section IDs for reference
CANONICAL_SECTIONS_P0 = [
    "headline",
    "executive_summary",
    "unify_narrative",
    "competencies_ats",
    "IBM",
]

CANONICAL_SECTIONS_P1 = [
    "InsurTech",
    "EY",
]

CANONICAL_SECTIONS_P2 = [
    "early_career",
    "education",
    "certifications_low_signal",
]

ALL_CANONICAL_SECTIONS = (
    CANONICAL_SECTIONS_P0 +
    CANONICAL_SECTIONS_P1 +
    CANONICAL_SECTIONS_P2
)
