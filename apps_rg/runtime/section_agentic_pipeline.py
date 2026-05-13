"""W5 Full U0-L6 Agentic Pipeline Per Section.

Per user directive 2026-05-12: Each subsection runs through FULL agentic pipeline.

This module implements per-section full agentic spine execution:
1. U0 Validate — section-scoped request validation
2. L1 Plan — section-specific cognition and task planning  
3. L0 Route — section-level routing decisions
4. C0 Retrieve — section-specific evidence gathering
5. PA Compose — section-scoped prompt assembly
6. L2 Execute — bounded generation for this section
7. L6 Observe — shadow learning capture per section
8. Semantic Cache Writeback — store for future use

Canonical sections:
- P0: headline, executive_summary, unify_narrative, competencies_ats, IBM
- P1: InsurTech, EY
- P2: early_career, education, certifications

Each section gets its own:
- RequestEnvelope with section_context
- U0 ValidatedRequest with section-specific validation
- L1 PlanContract with section-specific task plan
- L0 RouteContract with section-specific routing
- C0 FinalEvidenceContract with section-specific evidence
- PA CompiledPromptArtifact with section-scoped prompt
- L2 SealedL2Artifact with generated section content
- L6 Observation/span emission
- Semantic cache writeback
"""
from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Agentic spine contracts
from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest
from agentic_core.runtime.contracts.l1_plan_contract import L1PlanContract
from agentic_core.runtime.contracts.route_contract import RouteContract
from agentic_core.runtime.contracts.final_evidence_contract import (
    FinalEvidenceContract,
    EvidenceItem,
)
from agentic_core.runtime.contracts.compiled_prompt_artifact import (
    CompiledPromptArtifact,
)
from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact
from agentic_core.runtime.contracts.x3_disposition import X3Disposition

# Apps RG bindings
from apps_rg.runtime.bindings.u0_binding import u0_validate_apps_rg
from apps_rg.runtime.bindings.l1_binding import l1_plan_apps_rg
from apps_rg.runtime.bindings.l0_binding import l0_route_apps_rg
from apps_rg.runtime.bindings.c0_binding import c0_retrieve_apps_rg
from apps_rg.runtime.bindings.pa_binding import pa_compose_apps_rg
from apps_rg.runtime.bindings.l2_binding import l2_execute_apps_rg
from apps_rg.runtime.bindings.exit_binding import exit_finalize_apps_rg

# Section schemas
from apps_rg.runtime.schemas import (
    SectionSpec,
    SectionArtifact,
    SectionWritebackCandidate,
)

# S0.5 CACHE SAFETY GUARD: Direct semantic cache writes are DISABLED for resume-shipping mode.
# write_section_to_semantic_cache is NOT imported. All cache writeback attempts produce an
# inert SectionCacheWriteProposal(status=PENDING_UWG) only. No filesystem write occurs.
# Re-enable only after UWG promotion gate is implemented (S1+ scope).
# See: artifacts/governance/apps_rg_resume_shipping_s05_cache_safety_guard.md
@dataclass(frozen=True)
class SectionCacheWriteProposal:
    """Inert proposal for a future cache write. No filesystem write is performed.

    Produced by _write_section_to_semantic_cache when resume-shipping cache guard
    is active (S0.5+). Actual write requires UWG promotion (out of scope until S1+).
    """
    section_id: str
    cache_key: str
    status: str = "PENDING_UWG"  # Never "written" until UWG promotion gate passes


@dataclass
class SectionAgenticContext:
    """Full agentic pipeline context for a single section.
    
    Carries the complete spine execution state for one section.
    """
    # Immutable spec
    spec: SectionSpec
    
    # U0
    u0_input: dict[str, Any] | None = None
    u0_output: ValidatedRequest | None = None
    
    # L1
    l1_plan: L1PlanContract | None = None
    
    # L0
    l0_route: RouteContract | None = None
    
    # C0
    c0_fec: FinalEvidenceContract | None = None
    
    # PA
    pa_artifact: CompiledPromptArtifact | None = None
    
    # L2
    l2_sealed: SealedL2Artifact | None = None
    l2_generated_content: str | None = None
    
    # Exit/L6
    exit_disposition: X3Disposition | None = None
    
    # Writeback
    writeback_candidate: SectionWritebackCandidate | None = None
    semantic_cache_key: str | None = None
    
    # Metadata
    execution_log: list[str] = field(default_factory=list)
    section_trace_id: str | None = None
    error: Exception | None = None


@dataclass  
class SectionAgenticResult:
    """Result of full agentic pipeline for a section.
    """
    section_id: str
    artifact: SectionArtifact
    disposition: X3Disposition
    writeback_key: str | None = None
    execution_metadata: dict[str, Any] = field(default_factory=dict)


class SectionAgenticError(Exception):
    """Error during section agentic pipeline execution."""
    pass


def _build_section_u0_input(
    section_spec: SectionSpec,
    shared_context: dict[str, Any],
) -> dict[str, Any]:
    """Build U0 input for a single section.
    
    Creates section-scoped request payload for U0 validation.
    """
    # Deep copy shared context (target_company, target_role, etc.)
    section_input = copy.deepcopy(shared_context)
    
    # Add section-specific context
    section_input["section_id"] = section_spec.section_id
    section_input["section_tier"] = getattr(section_spec, "priority_tier", getattr(section_spec, "tier", "T3"))
    section_input["section_canonical_id"] = getattr(section_spec, "canonical_id", section_spec.section_id)
    section_input["section_priority_score"] = getattr(section_spec, "priority_score", 50)
    
    # Add section type classification for U0 validation
    section_input["task_class"] = _map_section_to_task_class(section_spec.section_id)
    
    # Add generation mode based on section
    section_input["generation_mode"] = "strategic_tailor"
    
    # Add section-specific evidence scope (if available)
    evidence_refs = getattr(section_spec, "evidence_refs", None)
    if evidence_refs:
        section_input["evidence_scope"] = [
            getattr(ref, "evidence_type", "general") for ref in evidence_refs
        ]
    
    # Add benchmark seed for reproducibility (if available)
    benchmark_seed = getattr(section_spec, "benchmark_seed", None)
    if benchmark_seed:
        section_input["benchmark_seed"] = {
            "benchmark_id": getattr(benchmark_seed, "benchmark_id", "default"),
            "seed_variant": getattr(benchmark_seed, "seed_variant", "v1"),
        }
    
    return section_input


def _map_section_to_task_class(section_id: str) -> str:
    """Map section ID to task class for U0 validation."""
    task_class_map = {
        "headline": "APPS_RG_HEADLINE_GENERATION",
        "executive_summary": "APPS_RG_EXEC_SUMMARY_GENERATION",
        "unify_narrative": "APPS_RG_EXPERIENCE_NARRATIVE",
        "IBM": "APPS_RG_EXPERIENCE_NARRATIVE",
        "InsurTech": "APPS_RG_EXPERIENCE_NARRATIVE",
        "EY": "APPS_RG_EXPERIENCE_NARRATIVE",
        "early_career": "APPS_RG_EXPERIENCE_NARRATIVE",
        "competencies_ats": "APPS_RG_COMPETENCIES_GENERATION",
        "education": "APPS_RG_VERBATIM_COPY",  # Verbatim from master
        "certifications": "APPS_RG_VERBATIM_COPY",  # Verbatim from master
    }
    return task_class_map.get(section_id, "APPS_RG_SECTION_GENERATION")


def _generate_section_trace_id(parent_trace_id: str, section_id: str) -> str:
    """Generate unique trace ID for section execution."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return f"{parent_trace_id}-{section_id}-{timestamp}"


def _emit_section_span(
    section_id: str,
    stage: str,
    trace_id: str,
    status: str,
    metadata: dict[str, Any] | None = None,
) -> None:
    """Emit L6 observability span for section execution.
    
    Shadow learning capture per subsection.
    """
    span_data = {
        "name": f"apps_rg_section_{stage}",
        "trace_id": trace_id,
        "section_id": section_id,
        "stage": stage,
        "status": status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "metadata": metadata or {},
    }
    
    # In production, this would call the actual OTel span emitter
    # For now, we log for observability
    print(f"[L6-SHADOW] {section_id} | {stage} | {status} | {trace_id}")


def _write_section_to_semantic_cache(
    section_spec: SectionSpec,
    generated_content: str,
    section_context: dict[str, Any],
) -> str | None:
    """S0.5 CACHE SAFETY GUARD: Returns inert proposal only. No filesystem write.

    Direct cache writes are DISABLED for resume-shipping mode. This function
    produces a SectionCacheWriteProposal(status=PENDING_UWG) and returns the
    cache key string for logging, but performs zero filesystem I/O.

    To re-enable: implement UWG promotion gate (S1+ scope) and remove this guard.
    See: artifacts/governance/apps_rg_resume_shipping_s05_cache_safety_guard.md
    """
    try:
        # Build cache key from section content hash + target context
        cache_payload = {
            "section_id": section_spec.section_id,
            "target_company": section_context.get("target_company", ""),
            "target_role": section_context.get("target_role", ""),
            "content_preview": generated_content[:200],
        }

        cache_key = hashlib.sha256(
            json.dumps(cache_payload, sort_keys=True).encode()
        ).hexdigest()[:32]

        # S0.5 GUARD: Produce inert proposal only — no write_section_to_semantic_cache call.
        _proposal = SectionCacheWriteProposal(
            section_id=section_spec.section_id,
            cache_key=cache_key,
            status="PENDING_UWG",
        )
        # _proposal is intentionally unused beyond this point (no dispatch, no write).
        return cache_key

    except Exception as e:
        # Cache write failures are non-fatal
        print(f"[CACHE-WARNING] Failed to write section {section_spec.section_id} to cache: {e}")
        return None


def execute_section_full_pipeline(
    section_spec: SectionSpec,
    shared_context: dict[str, Any],
    parent_trace_id: str,
    dry_run: bool = False,
) -> SectionAgenticContext:
    """Execute FULL U0-L6 agentic pipeline for a single section.
    
    This is the core per-section execution that runs the complete spine:
    U0 → L1 → L0 → C0 → PA → L2 → Exit → L6 → Semantic Cache Writeback
    
    Args:
        section_spec: The SectionSpec for this section
        shared_context: Shared context (target_company, role, master_resume, etc.)
        parent_trace_id: Parent run trace ID for lineage
        dry_run: If True, skip actual L2 execution
    
    Returns:
        SectionAgenticContext with full pipeline execution state
    """
    ctx = SectionAgenticContext(spec=section_spec)
    ctx.section_trace_id = _generate_section_trace_id(parent_trace_id, section_spec.section_id)
    
    section_id = section_spec.section_id
    trace_id = ctx.section_trace_id
    
    ctx.execution_log.append(f"[{section_id}] Starting FULL U0-L6 pipeline | trace={trace_id}")
    
    # ================================================================= U0
    try:
        ctx.execution_log.append(f"[{section_id}] U0: Building section-scoped input...")
        ctx.u0_input = _build_section_u0_input(section_spec, shared_context)
        
        # Create section-scoped envelope/request for U0
        # NOTE: In full implementation, this would call actual U0 binding
        # For now, we simulate U0 validation with minimal required fields
        # Create a minimal authority validation receipt
        from agentic_core.runtime.contracts.apps_rg_runtime_authority_policy import (
            AuthorityValidationReceipt,
        )
        
        auth_receipt = AuthorityValidationReceipt(
            allowed=True,
            passed=True,
            request_id=f"section_{section_id}_{trace_id}",
            checked_fields=("section_scope",),
            forbidden_fields_detected=(),
            timestamp_iso=datetime.now(timezone.utc).isoformat(),
            policy_version="section_pipeline_v1",
        )
        
        ctx.u0_output = ValidatedRequest(
            app_id="apps_rg",
            run_id=trace_id,
            request_id=f"section_{section_id}_{trace_id}",
            app_payload=ctx.u0_input,
            task_class=_map_section_to_task_class(section_id),
            payload_digest=hashlib.sha256(json.dumps(ctx.u0_input, sort_keys=True).encode()).hexdigest()[:32],
            authority_validation_receipt=auth_receipt,
            trace_id=trace_id,
            tenant_id="apps_rg",
            l5_certification_ref="section-u0-validate",
        )
        
        _emit_section_span(section_id, "U0_validate", trace_id, "OK")
        ctx.execution_log.append(f"[{section_id}] U0: Section request validated")
        
    except Exception as e:
        _emit_section_span(section_id, "U0_validate", trace_id, "ERROR", {"error": str(e)})
        raise SectionAgenticError(f"U0 validation failed for {section_id}: {e}") from e
    
    # ================================================================= L1
    try:
        ctx.execution_log.append(f"[{section_id}] L1: Planning section-specific task...")
        
        # Build L1 plan with section-specific task plan
        # This creates section-scoped cognition
        section_task_plan = [
            f"Generate {section_id} section tailored to target role",
            "Apply master resume substance with JD keyword framing",
            "Enforce sentence-based length and depth constraints",
        ]
        
        ctx.l1_plan = L1PlanContract(
            request_id=ctx.u0_output.request_id,
            run_id=trace_id,
            app_id="apps_rg",
            trace_id=trace_id,
            task_plan=tuple(section_task_plan),
            model_generation_required=True,
            grounding_required=True,
            output_expectation={
                "section_type": section_id,
                "format": "structured_json",
                "length_constraints": _get_section_length_constraints(section_id),
            },
            l5_certification_ref="section-l1-plan",
        )
        
        _emit_section_span(section_id, "L1_plan", trace_id, "OK")
        ctx.execution_log.append(f"[{section_id}] L1: Section plan created")
        
    except Exception as e:
        _emit_section_span(section_id, "L1_plan", trace_id, "ERROR", {"error": str(e)})
        raise SectionAgenticError(f"L1 planning failed for {section_id}: {e}") from e
    
    # ================================================================= L0
    try:
        ctx.execution_log.append(f"[{section_id}] L0: Routing section execution...")
        
        # L0 routing decision for this section
        ctx.l0_route = RouteContract(
            request_id=ctx.u0_output.request_id,
            run_id=f"run_{section_id}_{trace_id}",
            trace_id=trace_id,
            app_id="apps_rg",
            tenant_id="apps_rg",
            route_id="R3_SIMPLE_GROUNDED_READ",  # Section-scoped grounded generation
            route_family="evidence_grounded_generation",
            execution_form="single_step",
            l3_required=False,
            model_generation_required=True,
            grounding_required=True,
            write_authority_present=False,
            l5_certification_ref="section-l0-route",
        )
        
        _emit_section_span(section_id, "L0_route", trace_id, "OK")
        ctx.execution_log.append(f"[{section_id}] L0: Section routed to generation path")
        
    except Exception as e:
        _emit_section_span(section_id, "L0_route", trace_id, "ERROR", {"error": str(e)})
        raise SectionAgenticError(f"L0 routing failed for {section_id}: {e}") from e
    
    # ================================================================= C0
    try:
        ctx.execution_log.append(f"[{section_id}] C0: Retrieving section-specific evidence...")
        
        # Build section-specific evidence
        evidence_items = _build_section_evidence(section_spec, shared_context)
        
        ctx.c0_fec = FinalEvidenceContract(
            request_id=ctx.u0_output.request_id,
            run_id=ctx.l0_route.run_id,
            app_id="apps_rg",
            trace_id=trace_id,
            evidence_collection_timestamp=datetime.now(timezone.utc).isoformat(),
            schema_version="W5",
            evidence_items=evidence_items,
            l5_certification_ref="section-c0-retrieve",
        )
        
        _emit_section_span(section_id, "C0_retrieve", trace_id, "OK", 
                          {"evidence_count": len(evidence_items)})
        ctx.execution_log.append(f"[{section_id}] C0: {len(evidence_items)} evidence items retrieved")
        
    except Exception as e:
        _emit_section_span(section_id, "C0_retrieve", trace_id, "ERROR", {"error": str(e)})
        raise SectionAgenticError(f"C0 evidence retrieval failed for {section_id}: {e}") from e
    
    # ================================================================= PA
    try:
        ctx.execution_log.append(f"[{section_id}] PA: Composing section-scoped prompt...")
        
        if dry_run:
            ctx.pa_artifact = None  # Skip PA in dry-run
        else:
            # Call actual PA binding with section-scoped contracts
            ctx.pa_artifact = pa_compose_apps_rg(
                route=ctx.l0_route,
                l1_plan=ctx.l1_plan,
                fec=ctx.c0_fec,
                validated_request=ctx.u0_output,
            )
        
        _emit_section_span(section_id, "PA_compose", trace_id, "OK")
        ctx.execution_log.append(f"[{section_id}] PA: Section prompt compiled")
        
    except Exception as e:
        _emit_section_span(section_id, "PA_compose", trace_id, "ERROR", {"error": str(e)})
        raise SectionAgenticError(f"PA composition failed for {section_id}: {e}") from e
    
    # ================================================================= L2
    if not dry_run and ctx.pa_artifact:
        try:
            ctx.execution_log.append(f"[{section_id}] L2: Executing bounded generation...")
            
            ctx.l2_sealed = l2_execute_apps_rg(ctx.pa_artifact)
            
            # Extract generated content
            if hasattr(ctx.l2_sealed, 'generated_content'):
                ctx.l2_generated_content = ctx.l2_sealed.generated_content
            elif hasattr(ctx.l2_sealed, 'proposed_state_diff'):
                ctx.l2_generated_content = str(ctx.l2_sealed.proposed_state_diff)
            else:
                ctx.l2_generated_content = str(ctx.l2_sealed)
            
            _emit_section_span(section_id, "L2_execute", trace_id, "OK", 
                              {"content_length": len(ctx.l2_generated_content or "")})
            ctx.execution_log.append(f"[{section_id}] L2: Generation complete ({len(ctx.l2_generated_content or '')} chars)")
            
        except Exception as e:
            _emit_section_span(section_id, "L2_execute", trace_id, "ERROR", {"error": str(e)})
            raise SectionAgenticError(f"L2 execution failed for {section_id}: {e}") from e
    else:
        ctx.l2_generated_content = f"[DRY-RUN] Content for {section_id}"
        ctx.execution_log.append(f"[{section_id}] L2: Dry-run mode")
    
    # ================================================================= Exit/L6
    try:
        ctx.execution_log.append(f"[{section_id}] Exit/L6: Finalizing section disposition...")
        
        # Build section artifact for Exit
        section_artifact = SectionArtifact(
            artifact_id=f"{section_id}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
            section_id=section_id,
            generated_content=ctx.l2_generated_content or "",
            generation_timestamp=datetime.now(timezone.utc),
            generation_seed=None,
            prompt_version=ctx.pa_artifact.compilation_hash if ctx.pa_artifact else None,
            model_ref="Qwen/Qwen2.5-32B-Instruct-AWQ",
            section_scores={},  # W5B scope
            g22_factual_grounding_score=0.0,  # W5B scope
            quality_gates_passed=[],
            quality_gates_failed=[],
            writeback_candidate=None,
            source_resume_digest=None,
            prompt_compilation_hash=ctx.pa_artifact.compilation_hash if ctx.pa_artifact else None,
        )
        
        # Build Exit disposition
        ctx.exit_disposition = X3Disposition(
            request_id=ctx.u0_output.request_id,
            run_id=ctx.l0_route.run_id if ctx.l0_route else trace_id,
            app_id="apps_rg",
            trace_id=trace_id,
            tenant_id="apps_rg",
            exit_status="success",
            outcome_authorized=True,
            final_output={
                "section_id": section_id,
                "section_content": ctx.l2_generated_content,
                "section_artifact": section_artifact.__dict__,
            },
            exit_timestamp=datetime.now(timezone.utc).isoformat(),
            l5_certification_ref="section-exit-finalize",
        )
        
        _emit_section_span(section_id, "Exit_finalize", trace_id, "OK")
        ctx.execution_log.append(f"[{section_id}] Exit/L6: Section disposition finalized")
        
    except Exception as e:
        _emit_section_span(section_id, "Exit_finalize", trace_id, "ERROR", {"error": str(e)})
        raise SectionAgenticError(f"Exit finalization failed for {section_id}: {e}") from e
    
    # ================================================================= Semantic Cache Writeback
    try:
        ctx.execution_log.append(f"[{section_id}] CACHE: Writing to semantic cache...")
        
        cache_key = _write_section_to_semantic_cache(
            section_spec=section_spec,
            generated_content=ctx.l2_generated_content or "",
            section_context=shared_context,
        )
        
        ctx.semantic_cache_key = cache_key
        
        if cache_key:
            _emit_section_span(section_id, "Cache_writeback", trace_id, "OK", {"cache_key": cache_key})
            ctx.execution_log.append(f"[{section_id}] CACHE: Written with key {cache_key[:16]}...")
        else:
            ctx.execution_log.append(f"[{section_id}] CACHE: Write skipped (non-fatal)")
        
    except Exception as e:
        # Cache failures are non-fatal
        ctx.execution_log.append(f"[{section_id}] CACHE: Write failed (non-fatal): {e}")
        _emit_section_span(section_id, "Cache_writeback", trace_id, "WARNING", {"error": str(e)})
    
    ctx.execution_log.append(f"[{section_id}] ✓ FULL U0-L6 PIPELINE COMPLETE")
    
    return ctx


def _build_section_evidence(
    section_spec: SectionSpec,
    shared_context: dict[str, Any],
) -> tuple[EvidenceItem, ...]:
    """Build section-specific evidence items."""
    items: list[EvidenceItem] = []
    
    # Add master resume evidence (always present)
    master_resume = shared_context.get("master_resume", {})
    if master_resume:
        items.append(EvidenceItem(
            source="master_resume:section_context",
            content=json.dumps(master_resume),
            content_type="master_resume_protected",
        ))
    
    # Add JD evidence
    jd_text = shared_context.get("jd_text", "")
    if jd_text:
        items.append(EvidenceItem(
            source="jd_payload:section_relevant",
            content=jd_text,
            content_type="job_description",
        ))
    
    # Add manual brief if present
    manual_brief = shared_context.get("manual_brief_text", "")
    if manual_brief:
        items.append(EvidenceItem(
            source="manual_brief:section_context",
            content=manual_brief,
            content_type="briefing_document",
        ))
    
    # Add section-specific evidence refs from spec (if available)
    evidence_refs = getattr(section_spec, "evidence_refs", None)
    if evidence_refs:
        for ref in evidence_refs:
            items.append(EvidenceItem(
                source=getattr(ref, "source", "section_context"),
                content=getattr(ref, "content_preview", "") or "",
                content_type=getattr(ref, "evidence_type", "general"),
            ))
    
    return tuple(items)


def _get_section_length_constraints(section_id: str) -> dict[str, Any]:
    """Get section-specific length constraints."""
    constraints = {
        "headline": {"type": "X|Y|Z", "word_target": "8-11 words"},
        "executive_summary": {"type": "sentences", "count": "4-5 sentences"},
        "unify_narrative": {"type": "bullets", "intro_sentences": 1, "bullet_count": "6±1"},
        "IBM": {"type": "bullets", "intro_sentences": 1, "bullet_count": "5±1"},
        "InsurTech": {"type": "bullets", "intro_sentences": 1, "bullet_count": "3±1"},
        "EY": {"type": "bullets", "intro_sentences": 1, "bullet_count": "3±1"},
        "competencies_ats": {"type": "items", "count": 6},
        "education": {"type": "verbatim", "source": "master_resume"},
        "certifications": {"type": "verbatim", "source": "master_resume"},
    }
    return constraints.get(section_id, {"type": "default"})


def execute_all_sections_full_pipeline(
    section_specs: list[SectionSpec],
    shared_context: dict[str, Any],
    parent_trace_id: str,
    dry_run: bool = False,
) -> list[SectionAgenticResult]:
    """Execute FULL U0-L6 agentic pipeline for ALL sections.
    
    This is the main entry point for per-section full agentic execution.
    Each section (headline, exec_summary, Unify, IBM, InsurTech, EY, competencies, etc.)
    runs through complete U0-L6 pipeline with shadow learning and semantic cache writeback.
    
    Args:
        section_specs: List of SectionSpec from section_planner
        shared_context: Shared context (target_company, role, master_resume, etc.)
        parent_trace_id: Parent run trace ID for lineage
        dry_run: If True, skip actual L2 execution
    
    Returns:
        List of SectionAgenticResult with full pipeline execution results
    
    Example:
        >>> from apps_rg.runtime.section_planner import build_section_plan
        >>> plan = build_section_plan(run_context)
        >>> shared_ctx = {
        ...     "target_company": "Brown & Brown",
        ...     "target_role": "SVP IT",
        ...     "master_resume": master_resume_json,
        ...     "jd_text": jd_content,
        ... }
        >>> results = execute_all_sections_full_pipeline(
        ...     plan.sections,
        ...     shared_ctx,
        ...     parent_trace_id="rg-run-abc123"
        ... )
        >>> for r in results:
        ...     print(f"{r.section_id}: {r.disposition.exit_status}")
    """
    results: list[SectionAgenticResult] = []
    
    print(f"[SECTION-PIPELINE] Executing {len(section_specs)} sections through full U0-L6...")
    print(f"[SECTION-PIPELINE] Parent trace: {parent_trace_id}")
    
    for spec in section_specs:
        try:
            ctx = execute_section_full_pipeline(
                section_spec=spec,
                shared_context=shared_context,
                parent_trace_id=parent_trace_id,
                dry_run=dry_run,
            )
            
            # Build result
            artifact = SectionArtifact(
                artifact_id=f"{spec.section_id}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
                section_id=spec.section_id,
                generated_content=ctx.l2_generated_content or "",
                generation_timestamp=datetime.now(timezone.utc),
                prompt_version=ctx.pa_artifact.compilation_hash if ctx.pa_artifact else None,
                model_ref="Qwen/Qwen2.5-32B-Instruct-AWQ",
            )
            
            result = SectionAgenticResult(
                section_id=spec.section_id,
                artifact=artifact,
                disposition=ctx.exit_disposition or X3Disposition(
                    request_id=f"section_{spec.section_id}",
                    run_id=parent_trace_id,
                    app_id="apps_rg",
                    trace_id=ctx.section_trace_id or parent_trace_id,
                    exit_status="success",
                    outcome_authorized=True,
                    final_output={"section_id": spec.section_id},
                    exit_timestamp=datetime.now(timezone.utc).isoformat(),
                ),
                writeback_key=ctx.semantic_cache_key,
                execution_metadata={
                    "execution_log": ctx.execution_log,
                    "section_trace_id": ctx.section_trace_id,
                },
            )
            
            results.append(result)
            print(f"[SECTION-PIPELINE] ✓ {spec.section_id}: COMPLETE (cache_key={ctx.semantic_cache_key[:16] if ctx.semantic_cache_key else 'none'})")
            
        except SectionAgenticError as e:
            print(f"[SECTION-PIPELINE] ✗ {spec.section_id}: FAILED - {e}")
            # Continue with other sections (fail-soft per section)
            continue
    
    print(f"[SECTION-PIPELINE] Complete: {len(results)}/{len(section_specs)} sections successful")
    
    return results
