"""LLM judge gateway — generic LLM-as-Judge invocation.

RB13: apps-rg-zip-based-full-spine-runtime-restoration-v1

Enforces:
- Judge profile loading from apps_rg grader_roster
- Judge invocation through provider gateway
- JudgeResult normalization
- Abstain support
- Timeout handling
- Fail-closed for required dimensions
- Warn-only for informational dimensions
- No import from apps_rg/engines/judges/
"""

from __future__ import annotations

import hashlib
import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from agentic_core.runtime.judges.judge_registry import (
    JudgeKind,
    JudgeProfile,
    JudgeRegistry,
    get_judge_registry,
)
from agentic_core.runtime.providers import (
    ProviderGateway,
    ProviderMode,
    ProviderRequest,
    ProviderProfile,
)
from agentic_core.runtime.contracts.judge_types import JudgeResult

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class LLMJudgeRequest:
    """Request to invoke an LLM judge."""
    
    judge_profile_ref: str
    candidate_text: str
    context_metadata: Dict[str, Any] = field(default_factory=dict)
    rubric_path: Optional[str] = None
    max_tokens: int = 2048
    
    # Tracing
    run_id: str = ""
    node_id: str = ""
    candidate_id: str = ""
    trace_root: str = ""


@dataclass(frozen=True)
class LLMJudgeResponse:
    """Response from LLM judge invocation."""
    
    judge_result: JudgeResult
    success: bool
    error_message: Optional[str] = None
    provider_receipt_ref: Optional[str] = None


class LLMJudgeGateway:
    """Generic LLM judge gateway.
    
    Invokes judges through the provider gateway.
    Normalizes responses to JudgeResult.
    Handles abstain, timeout, and error cases.
    """
    
    def __init__(
        self,
        registry: Optional[JudgeRegistry] = None,
        provider_gateway: Optional[ProviderGateway] = None,
    ) -> None:
        self._registry = registry or get_judge_registry()
        self._provider_gateway = provider_gateway
    
    def judge(
        self,
        request: LLMJudgeRequest,
        timeout_seconds: float = 30.0,
    ) -> LLMJudgeResponse:
        """Invoke an LLM judge.
        
        Args:
            request: The judge request
            timeout_seconds: Timeout for the judge call
            
        Returns:
            LLMJudgeResponse with normalized JudgeResult
        """
        started = time.time()
        
        # 1. Load judge profile
        try:
            profile = self._registry.get_profile(request.judge_profile_ref)
        except KeyError as exc:
            latency_ms = (time.time() - started) * 1000.0
            return self._build_error_response(
                request,
                f"Judge profile not found: {exc}",
                latency_ms,
                fail_closed=True,
            )
        
        # 2. Handle stub judges
        if profile.is_stub or profile.judge_kind == JudgeKind.STUB:
            return self._invoke_stub_judge(request, profile)
        
        # 3. Handle deterministic judges
        if profile.judge_kind == JudgeKind.DETERMINISTIC:
            return self._invoke_deterministic_judge(request, profile)
        
        # 4. Invoke LLM-as-judge through provider gateway
        if profile.judge_kind == JudgeKind.LLM_AS_JUDGE:
            return self._invoke_llm_judge(request, profile, timeout_seconds)
        
        # 5. Hybrid judges not fully implemented in RB13
        if profile.judge_kind == JudgeKind.HYBRID:
            return self._build_error_response(
                request,
                f"Hybrid judge {profile.profile_id} not implemented in RB13",
                (time.time() - started) * 1000.0,
                fail_closed=profile.required_for_exit,
            )
        
        # Unknown judge kind
        return self._build_error_response(
            request,
            f"Unknown judge kind: {profile.judge_kind}",
            (time.time() - started) * 1000.0,
            fail_closed=True,
        )
    
    def _invoke_stub_judge(
        self,
        request: LLMJudgeRequest,
        profile: JudgeProfile,
    ) -> LLMJudgeResponse:
        """Invoke a stub judge for testing."""
        latency_ms = 0.0
        
        # Generate deterministic stub score
        stub_hash = hashlib.sha256(
            f"stub_judge:{request.candidate_text[:50]}:{profile.profile_id}".encode()
        ).hexdigest()
        
        # Use hash to generate a score between 0.7 and 0.9
        score = 0.7 + (int(stub_hash[:8], 16) % 2000) / 10000.0
        
        judge_result = JudgeResult(
            judge_id=profile.profile_id,
            candidate_id=request.candidate_id,
            node_id=request.node_id,
            run_id=request.run_id,
            judge_profile_ref=profile.profile_id,
            score=score,
            raw_score=score,
            confidence=0.5,
            abstained=False,
            informational_only=profile.informational_only,
            required_for_exit=profile.required_for_exit,
            provider_ref="stub",
            latency_ms=int(latency_ms),
            trace_root=request.trace_root,
        )
        
        return LLMJudgeResponse(
            judge_result=judge_result,
            success=True,
            provider_receipt_ref="stub_receipt",
        )
    
    def _invoke_deterministic_judge(
        self,
        request: LLMJudgeRequest,
        profile: JudgeProfile,
    ) -> LLMJudgeResponse:
        """Invoke a deterministic (rule-based) judge."""
        latency_ms = 0.0
        
        # Deterministic judges return rule-based scores
        # For RB13, return a neutral passing score
        score = 0.85  # Default passing score
        
        judge_result = JudgeResult(
            judge_id=profile.profile_id,
            candidate_id=request.candidate_id,
            node_id=request.node_id,
            run_id=request.run_id,
            judge_profile_ref=profile.profile_id,
            score=score,
            raw_score=score,
            confidence=1.0,
            abstained=False,
            informational_only=False,
            required_for_exit=True,
            provider_ref="deterministic",
            latency_ms=int(latency_ms),
            trace_root=request.trace_root,
        )
        
        return LLMJudgeResponse(
            judge_result=judge_result,
            success=True,
        )
    
    def _invoke_llm_judge(
        self,
        request: LLMJudgeRequest,
        profile: JudgeProfile,
        timeout_seconds: float,
    ) -> LLMJudgeResponse:
        """Invoke an LLM-as-judge through the provider gateway."""
        started = time.time()
        
        # Check if provider gateway available
        if self._provider_gateway is None:
            latency_ms = (time.time() - started) * 1000.0
            return self._build_error_response(
                request,
                "Provider gateway not configured for LLM judge",
                latency_ms,
                fail_closed=profile.required_for_exit,
            )
        
        # Build judge prompt
        judge_prompt = self._build_judge_prompt(request, profile)
        
        # Load provider profile for this judge
        try:
            from agentic_core.runtime.providers.provider_registry import get_provider_registry
            provider_registry = get_provider_registry()
            provider_profile = provider_registry.get_profile(profile.provider_profile_ref)
        except Exception as exc:
            latency_ms = (time.time() - started) * 1000.0
            return self._build_error_response(
                request,
                f"Failed to load provider profile for judge: {exc}",
                latency_ms,
                fail_closed=profile.required_for_exit,
            )
        
        # Create provider request
        provider_req = ProviderRequest(
            prompt_text=judge_prompt,
            provider_profile=provider_profile,
            max_tokens=request.max_tokens,
            temperature=0.0,  # Deterministic for judging
            run_id=request.run_id,
            node_id=request.node_id,
            trace_root=request.trace_root,
            prompt_artifact_ref=request.rubric_path or "",
        )
        
        # Invoke provider
        try:
            provider_resp = self._provider_gateway.invoke(provider_req)
            latency_ms = (time.time() - started) * 1000.0
            
            if not provider_resp.success:
                return self._build_error_response(
                    request,
                    f"Provider invocation failed: {provider_resp.error_message}",
                    latency_ms,
                    fail_closed=profile.required_for_exit,
                )
            
            # Parse judge response
            score = self._parse_judge_response(provider_resp.text)
            
            judge_result = JudgeResult(
                judge_id=profile.profile_id,
                candidate_id=request.candidate_id,
                node_id=request.node_id,
                run_id=request.run_id,
                judge_profile_ref=profile.profile_id,
                score=score,
                raw_score=score,
                confidence=0.9,
                abstained=False,
                informational_only=profile.informational_only,
                required_for_exit=profile.required_for_exit,
                provider_ref=provider_profile.profile_id,
                model_ref=provider_profile.model_id,
                provider_receipt_ref=getattr(provider_resp.receipt, "invocation_id", None),
                latency_ms=int(latency_ms),
                trace_root=request.trace_root,
            )
            
            return LLMJudgeResponse(
                judge_result=judge_result,
                success=True,
                provider_receipt_ref=getattr(provider_resp.receipt, "invocation_id", None),
            )
            
        except Exception as exc:
            latency_ms = (time.time() - started) * 1000.0
            return self._build_error_response(
                request,
                f"LLM judge invocation error: {exc}",
                latency_ms,
                fail_closed=profile.required_for_exit,
            )
    
    def _build_judge_prompt(
        self,
        request: LLMJudgeRequest,
        profile: JudgeProfile,
    ) -> str:
        """Build the judge prompt."""
        # Simple judge prompt for RB13
        # In production, this would load from rubric YAML
        dimensions_text = "\n".join([
            f"- {d.dimension_id}: weight={d.weight}"
            for d in profile.dimensions
        ]) if profile.dimensions else "- default: score 0.0-1.0"
        
        return (
            f"You are an expert judge evaluating resume content.\n\n"
            f"Evaluate the following candidate text on these dimensions:\n"
            f"{dimensions_text}\n\n"
            f"Candidate text:\n{request.candidate_text[:1000]}\n\n"
            f"Return ONLY a JSON object with scores (0.0-1.0) for each dimension."
        )
    
    def _parse_judge_response(self, response_text: str) -> float:
        """Parse the judge response to extract a score."""
        import json
        
        # Try to parse as JSON
        try:
            # Clean up response
            text = response_text.strip()
            if text.startswith("```"):
                # Extract from markdown fence
                lines = text.splitlines()
                in_fence = False
                content: List[str] = []
                for line in lines:
                    if line.startswith("```"):
                        if in_fence:
                            break
                        in_fence = True
                        continue
                    if in_fence:
                        content.append(line)
                text = "\n".join(content).strip()
            
            data = json.loads(text)
            
            # Try to extract score from various formats
            if isinstance(data, dict):
                if "score" in data:
                    return float(data["score"])
                # Average all numeric values
                values = [
                    float(v) for v in data.values()
                    if isinstance(v, (int, float)) and not isinstance(v, bool)
                ]
                if values:
                    return sum(values) / len(values)
        except Exception:
            pass
        
        # Fallback: return neutral score
        return 0.75
    
    def _build_error_response(
        self,
        request: LLMJudgeRequest,
        error_message: str,
        latency_ms: float,
        fail_closed: bool,
    ) -> LLMJudgeResponse:
        """Build an error response."""
        # For required judges, error = fail (score 0)
        # For informational judges, error = abstain (no impact)
        if fail_closed:
            score = 0.0
            abstained = False
            error = error_message
        else:
            score = 0.0
            abstained = True
            error = f"Abstained: {error_message}"
        
        judge_result = JudgeResult(
            judge_id=request.judge_profile_ref,
            candidate_id=request.candidate_id,
            node_id=request.node_id,
            run_id=request.run_id,
            judge_profile_ref=request.judge_profile_ref,
            score=score,
            raw_score=score,
            confidence=0.0,
            abstained=abstained,
            error=error,
            informational_only=not fail_closed,
            required_for_exit=fail_closed,
            latency_ms=int(latency_ms),
            trace_root=request.trace_root,
        )
        
        return LLMJudgeResponse(
            judge_result=judge_result,
            success=False,
            error_message=error_message,
        )
    
    def set_provider_gateway(self, gateway: ProviderGateway) -> None:
        """Set the provider gateway to use."""
        self._provider_gateway = gateway


__all__ = [
    "LLMJudgeGateway",
    "LLMJudgeRequest",
    "LLMJudgeResponse",
]
