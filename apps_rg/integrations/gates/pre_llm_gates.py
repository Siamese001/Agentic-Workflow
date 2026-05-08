"""PRE-LLM Resume Gates — Input/replay integrity.

Gates that run before LLM generation (W3):
- prompt_assembly_sha: Log SHA256 of assembled prompt for replay
- master_resume_sha_pinned: Pin master_resume.json SHA, detect concurrent edits

Spec reference: .windsurf/plans/apps-rg-runtime-gate-catalog-c4d7e1.md (W3)
"""

from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path
from typing import Any

from agentic_core.L5_safety.runtime_gates.types import Result
from agentic_core.runtime_gates import GateVerdict

_log = logging.getLogger("apps_rg.gates.pre_llm")


def _compute_sha256(data: bytes | str) -> str:
    """Compute SHA256 hex digest of data."""
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def prompt_assembly_sha_gate(artifact: Any, context: dict[str, Any]) -> GateVerdict:
    """Log SHA256 of assembled prompt for replay verification.
    
    W3: Input/replay integrity. The SHA is logged to the run report for later
    verification that the same prompt was used during replay.
    """
    gate_id = "prompt_assembly_sha"
    
    # Extract prompt from artifact or context
    prompt_text = ""
    if isinstance(artifact, dict):
        prompt_text = artifact.get("prompt", "")
    elif hasattr(artifact, "prompt"):
        prompt_text = str(getattr(artifact, "prompt", ""))
    
    if not prompt_text and "prompt" in context:
        prompt_text = context["prompt"]
    
    if not prompt_text:
        return GateVerdict(
            gate_id=gate_id,
            result=Result.UNKNOWN,
            reason="No prompt text available for SHA computation",
            reason_codes=("missing_prompt", "replay_impossible"),
        )
    
    # Compute SHA256
    prompt_sha = _compute_sha256(prompt_text)
    
    # Log for replay tracking
    _log.info("[W3] Prompt assembly SHA: %s (len=%d)", prompt_sha[:16], len(prompt_text))
    
    # Store in context for downstream use
    context["prompt_assembly_sha"] = prompt_sha
    
    return GateVerdict(
        gate_id=gate_id,
        result=Result.PASS,
        reason=f"Prompt SHA256 logged: {prompt_sha[:16]}... (len={len(prompt_text)})",
        reason_codes=("sha256_computed", f"sha:{prompt_sha[:16]}"),
        evidence_refs=(f"sha256:{prompt_sha}", f"len:{len(prompt_text)}"),
    )


def master_resume_sha_pinned_gate(artifact: Any, context: dict[str, Any]) -> GateVerdict:
    """Pin master_resume.json SHA256 and detect concurrent edits.
    
    W3: Input/replay integrity. Computes SHA of master_resume at pipeline start
    and verifies it hasn't changed. Detects concurrent edits during generation.
    """
    gate_id = "master_resume_sha_pinned"
    
    # Get master_resume path from context
    master_resume_path = context.get("master_resume_path")
    if not master_resume_path:
        return GateVerdict(
            gate_id=gate_id,
            result=Result.UNKNOWN,
            reason="master_resume_path not provided in context",
            reason_codes=("missing_master_resume_path",),
        )
    
    path = Path(master_resume_path) if isinstance(master_resume_path, str) else master_resume_path
    
    if not path.exists():
        return GateVerdict(
            gate_id=gate_id,
            result=Result.FAIL,
            reason=f"master_resume.json not found: {path}",
            reason_codes=("master_resume_missing",),
        )
    
    try:
        # Read and compute SHA
        content = path.read_bytes()
        current_sha = _compute_sha256(content)
        
        # Check for concurrent modification
        expected_sha = context.get("master_resume_expected_sha")
        
        if expected_sha and expected_sha != current_sha:
            _log.error(
                "[W3] master_resume.json changed during pipeline! Expected %s, got %s",
                expected_sha[:16],
                current_sha[:16],
            )
            return GateVerdict(
                gate_id=gate_id,
                result=Result.FAIL,
                reason=f"master_resume.json modified during pipeline: SHA mismatch",
                reason_codes=(
                    "concurrent_modification_detected",
                    f"expected:{expected_sha[:16]}",
                    f"actual:{current_sha[:16]}",
                ),
                evidence_refs=(
                    f"path:{path}",
                    f"expected_sha:{expected_sha}",
                    f"actual_sha:{current_sha}",
                ),
            )
        
        # Store SHA in context for later verification
        context["master_resume_sha"] = current_sha
        
        _log.info("[W3] master_resume.json SHA pinned: %s", current_sha[:16])
        
        return GateVerdict(
            gate_id=gate_id,
            result=Result.PASS,
            reason=f"master_resume.json SHA pinned: {current_sha[:16]}... (len={len(content)} bytes)",
            reason_codes=("sha256_pinned", f"sha:{current_sha[:16]}"),
            evidence_refs=(
                f"path:{path}",
                f"sha256:{current_sha}",
                f"size:{len(content)}",
            ),
        )
        
    except (OSError, IOError) as e:
        return GateVerdict(
            gate_id=gate_id,
            result=Result.UNKNOWN,
            reason=f"Failed to read master_resume.json: {e}",
            reason_codes=("read_error", type(e).__name__),
        )


def verify_master_resume_unchanged(
    master_resume_path: Path,
    expected_sha: str,
) -> GateVerdict:
    """Verification helper: Check if master_resume has expected SHA.
    
    Called at key checkpoints during pipeline to detect concurrent edits.
    """
    gate_id = "master_resume_verification"
    
    if not master_resume_path.exists():
        return GateVerdict(
            gate_id=gate_id,
            result=Result.FAIL,
            reason=f"master_resume.json not found during verification: {master_resume_path}",
            reason_codes=("verification_failed", "file_not_found"),
        )
    
    try:
        content = master_resume_path.read_bytes()
        actual_sha = _compute_sha256(content)
        
        if actual_sha != expected_sha:
            return GateVerdict(
                gate_id=gate_id,
                result=Result.FAIL,
                reason=f"master_resume.json SHA mismatch: expected {expected_sha[:16]}, got {actual_sha[:16]}",
                reason_codes=(
                    "sha_mismatch",
                    f"expected:{expected_sha[:16]}",
                    f"actual:{actual_sha[:16]}",
                ),
            )
        
        return GateVerdict(
            gate_id=gate_id,
            result=Result.PASS,
            reason=f"master_resume.json verified: SHA {actual_sha[:16]}... matches",
            reason_codes=("sha_verified",),
        )
        
    except (OSError, IOError) as e:
        return GateVerdict(
            gate_id=gate_id,
            result=Result.UNKNOWN,
            reason=f"Verification read failed: {e}",
            reason_codes=("verification_error", type(e).__name__),
        )


__all__ = [
    "prompt_assembly_sha_gate",
    "master_resume_sha_pinned_gate",
    "verify_master_resume_unchanged",
]
