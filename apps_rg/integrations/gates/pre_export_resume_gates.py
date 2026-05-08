"""PRE-EXPORT Resume Gates — Final artifact validation.

Gates that run before DOCX export (W7).
W4 gate: Education/certs unchanged verification.
W7 gate: No empty sections or placeholders in final render.

Spec reference: .windsurf/plans/apps-rg-runtime-gate-catalog-c4d7e1.md (W4, W7)
"""

from __future__ import annotations

import hashlib
import logging
import re
from pathlib import Path
from typing import Any

from agentic_core.L5_safety.runtime_gates.types import Result
from agentic_core.runtime_gates import GateVerdict

_log = logging.getLogger("apps_rg.gates.pre_export")


def _compute_sha256(data: bytes) -> str:
    """Compute SHA256 hex digest of data."""
    return hashlib.sha256(data).hexdigest()


def degree_certification_unchanged_gate(artifact: Any, context: dict[str, Any]) -> GateVerdict:
    """W4: Education/certs must be byte-identical to master_resume.
    
    Ensures credentials section is never hallucinated or modified.
    Strict identity check for immutable sections.
    """
    gate_id = "degree_certification_unchanged"
    
    # Get rendered education/certs section
    rendered_edu = ""
    if isinstance(artifact, dict):
        rendered_edu = artifact.get("education_section", "")
    elif hasattr(artifact, "education_section"):
        rendered_edu = str(getattr(artifact, "education_section", ""))
    
    # Get reference from master resume
    master_edu_path = context.get("master_resume_education_path")
    master_edu_sha = context.get("master_resume_education_sha")
    
    if not rendered_edu:
        # No education section to verify
        return GateVerdict(
            gate_id=gate_id,
            result=Result.UNKNOWN,
            reason="No education section in rendered artifact",
            reason_codes=("missing_education_section",),
        )
    
    if not master_edu_path and not master_edu_sha:
        # No reference to compare against
        return GateVerdict(
            gate_id=gate_id,
            result=Result.UNKNOWN,
            reason="No master resume education reference for comparison",
            reason_codes=("missing_master_reference",),
        )
    
    # Compute SHA of rendered section
    rendered_bytes = rendered_edu.encode("utf-8") if isinstance(rendered_edu, str) else rendered_edu
    rendered_sha = _compute_sha256(rendered_bytes)
    
    # Compare against expected SHA if provided
    if master_edu_sha:
        if rendered_sha != master_edu_sha:
            _log.error(
                "[W4] Education section modified! SHA mismatch: expected %s, got %s",
                master_edu_sha[:16], rendered_sha[:16]
            )
            return GateVerdict(
                gate_id=gate_id,
                result=Result.FAIL,
                reason="Education/certification section modified from master resume",
                reason_codes=(
                    "education_modified",
                    "credential_integrity_violation",
                    f"expected:{master_edu_sha[:16]}",
                    f"actual:{rendered_sha[:16]}",
                ),
                evidence_refs=(
                    f"expected_sha:{master_edu_sha}",
                    f"actual_sha:{rendered_sha}",
                ),
            )
        
        return GateVerdict(
            gate_id=gate_id,
            result=Result.PASS,
            reason=f"Education section verified: SHA {rendered_sha[:16]}... matches master",
            reason_codes=("education_unchanged", f"sha:{rendered_sha[:16]}"),
        )
    
    # If no SHA but path provided, compute and compare
    if master_edu_path:
        path = Path(master_edu_path) if isinstance(master_edu_path, str) else master_edu_path
        if not path.exists():
            return GateVerdict(
                gate_id=gate_id,
                result=Result.UNKNOWN,
                reason=f"Master education reference not found: {path}",
                reason_codes=("master_reference_missing",),
            )
        
        try:
            master_bytes = path.read_bytes()
            computed_master_sha = _compute_sha256(master_bytes)
            
            if rendered_sha != computed_master_sha:
                return GateVerdict(
                    gate_id=gate_id,
                    result=Result.FAIL,
                    reason="Education section differs from master resume",
                    reason_codes=(
                        "education_modified",
                        f"expected:{computed_master_sha[:16]}",
                        f"actual:{rendered_sha[:16]}",
                    ),
                )
            
            return GateVerdict(
                gate_id=gate_id,
                result=Result.PASS,
                reason="Education section matches master resume exactly",
                reason_codes=("education_unchanged",),
            )
            
        except (OSError, IOError) as e:
            return GateVerdict(
                gate_id=gate_id,
                result=Result.UNKNOWN,
                reason=f"Failed to read master education reference: {e}",
                reason_codes=("read_error", type(e).__name__),
            )
    
    return GateVerdict(
        gate_id=gate_id,
        result=Result.UNKNOWN,
        reason="Insufficient data to verify education section",
        reason_codes=("verification_impossible",),
    )


def docx_render_no_orphan_gate(artifact: Any, context: dict[str, Any]) -> GateVerdict:
    """W7: Final DOCX has no empty sections or placeholders.
    
    Prevents export of incomplete resumes with:
    - Empty sections (no content)
    - Placeholder text (e.g., "[PLACEHOLDER]", "TBD", "TODO")
    - Null/None values rendered as strings
    """
    gate_id = "docx_render_no_orphan"
    
    # Get resume sections from artifact
    sections: dict[str, str] = {}
    if isinstance(artifact, dict):
        sections = artifact.get("sections", {})
    elif hasattr(artifact, "sections"):
        sections = getattr(artifact, "sections", {})
    
    if not sections:
        return GateVerdict(
            gate_id=gate_id,
            result=Result.UNKNOWN,
            reason="No resume sections to validate",
            reason_codes=("missing_sections",),
        )
    
    # Check for empty sections
    empty_sections = []
    placeholder_sections = []
    null_sections = []
    
    # Patterns for placeholder detection
    placeholder_patterns = [
        r'\[PLACEHOLDER\]',
        r'\[TBD\]',
        r'\[TODO\]',
        r'\[INSERT',
        r'TBD',
        r'TODO',
        r'XXX',
        r'PLACEHOLDER',
    ]
    
    # Patterns for null-like values
    null_patterns = [
        r'^null$',
        r'^none$',
        r'^undefined$',
        r'^n/a$',
        r'^-$',
    ]
    
    for section_id, content in sections.items():
        if not content or not str(content).strip():
            empty_sections.append(section_id)
            continue
        
        content_str = str(content).strip()
        content_lower = content_str.lower()
        
        # Check for placeholders
        for pattern in placeholder_patterns:
            if re.search(pattern, content_str, re.IGNORECASE):
                placeholder_sections.append({
                    "section": section_id,
                    "content_preview": content_str[:50],
                })
                break
        
        # Check for null-like values
        for pattern in null_patterns:
            if re.match(pattern, content_lower):
                null_sections.append({
                    "section": section_id,
                    "value": content_str,
                })
                break
    
    # Aggregate violations
    total_violations = len(empty_sections) + len(placeholder_sections) + len(null_sections)
    
    if total_violations > 0:
        _log.error(
            "[W7] %d sections with render issues: %d empty, %d placeholders, %d null",
            total_violations, len(empty_sections), len(placeholder_sections), len(null_sections)
        )
        
        reason_parts = []
        if empty_sections:
            reason_parts.append(f"{len(empty_sections)} empty")
        if placeholder_sections:
            reason_parts.append(f"{len(placeholder_sections)} placeholders")
        if null_sections:
            reason_parts.append(f"{len(null_sections)} null values")
        
        return GateVerdict(
            gate_id=gate_id,
            result=Result.FAIL,
            reason=f"DOCX render issues: {', '.join(reason_parts)}",
            reason_codes=(
                "orphan_sections_detected",
                f"empty:{len(empty_sections)}",
                f"placeholders:{len(placeholder_sections)}",
                f"nulls:{len(null_sections)}",
            ),
            evidence_refs=tuple(
                f"section:{s},issue:empty" for s in empty_sections[:3]
            ) + tuple(
                f"section:{p['section']},issue:placeholder" for p in placeholder_sections[:3]
            ),
        )
    
    return GateVerdict(
        gate_id=gate_id,
        result=Result.PASS,
        reason=f"All {len(sections)} sections rendered without orphans or placeholders",
        reason_codes=(
            "no_orphans",
            f"sections:{len(sections)}",
        ),
    )


def pre_export_composite_gate(artifact: Any, context: dict[str, Any]) -> GateVerdict:
    """W7: Composite PRE-EXPORT gate running all export validation checks.
    
    Final validation before DOCX generation.
    """
    gates = [
        ("education_unchanged", degree_certification_unchanged_gate),
        ("no_orphans", docx_render_no_orphan_gate),
    ]
    
    failures = []
    passes = []
    unknowns = []
    
    for name, gate_fn in gates:
        verdict = gate_fn(artifact, context)
        if verdict.result == Result.FAIL:
            failures.append((name, verdict))
        elif verdict.result == Result.PASS:
            passes.append((name, verdict))
        else:
            unknowns.append((name, verdict))
    
    # Composite result
    if failures:
        return GateVerdict(
            gate_id="pre_export_composite",
            result=Result.FAIL,
            reason=f"PRE-EXPORT validation failed: {', '.join(f[0] for f in failures)}",
            reason_codes=tuple(f"fail:{f[0]}" for f in failures),
        )
    
    if unknowns and not passes:
        return GateVerdict(
            gate_id="pre_export_composite",
            result=Result.UNKNOWN,
            reason=f"PRE-EXPORT validation indeterminate: {', '.join(u[0] for u in unknowns)}",
            reason_codes=tuple(f"unknown:{u[0]}" for u in unknowns),
        )
    
    return GateVerdict(
        gate_id="pre_export_composite",
        result=Result.PASS,
        reason=f"PRE-EXPORT validation passed: {len(passes)} checks",
        reason_codes=tuple(f"pass:{p[0]}" for p in passes),
    )


__all__ = [
    "degree_certification_unchanged_gate",
    "docx_render_no_orphan_gate",
    "pre_export_composite_gate",
]
