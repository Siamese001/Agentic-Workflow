"""W1 Phase 5 — Wave C-C.1: LLM-Judge Veto (Option C primary).

Layer 2 safety veto using a lightweight LLM as judge.
Escalation-only: called only for action-sensitive or high lexical-overlap cases.
Fail-closed on timeout, parse error, or any exception.
"""

from __future__ import annotations

from agentic_core.config.model_catalog import (
    ANTHROPIC_LEGACY_HAIKU_3_20240307_MODEL_ID,
    QWEN_LOCAL_MODEL_ID,
)

import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any

# Add repo root to path for imports
REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.certification.safety.veto_protocol import VetoResult, VetoStage, VetoStatus

DEFAULT_RUBRIC_PATH = REPO_ROOT / "config" / "certification" / "llm_judge_rubric.md"
DEFAULT_TIMEOUT_MS = 2000
DEFAULT_TEMPERATURE = 0.0


class LLMJudgeVeto:
    """LLM-as-judge veto stage for semantic cache safety.
    
    Implements the VetoStage Protocol with fail-closed behavior.
    """
    
    # Local-qwen default endpoint; overridable via LOCAL_QWEN_ENDPOINT env.
    _DEFAULT_LOCAL_QWEN_ENDPOINT = "http://localhost:8000/v1"
    # Final fallback only if endpoint discovery and env override both fail.
    _FALLBACK_MODEL_ID = QWEN_LOCAL_MODEL_ID

    def __init__(
        self,
        provider: str = "local_qwen",
        model_id: str | None = None,
        rubric_path: Path | None = None,
        timeout_ms: int = DEFAULT_TIMEOUT_MS,
        temperature: float = DEFAULT_TEMPERATURE,
        max_input_tokens: int = 4096,
    ):
        self._provider = provider
        # Model-ID resolution deferred to first use (lazy) so construction
        # does not do network I/O and unit tests stay hermetic.
        # Resolution precedence:
        #   1. Explicit model_id argument (back-compat, tests)
        #   2. Env var QWEN_VLLM_MODEL / LOCAL_QWEN_MODEL (operator escape hatch)
        #   3. GET {endpoint}/v1/models  (discovery — preferred default)
        #   4. Hardcoded fallback _FALLBACK_MODEL_ID
        # The resolved id + (when discovery fires) the advertised id are
        # stored on the instance and surfaced via `resolved_model_id` and
        # `advertised_model_id` properties; the attestation writer binds
        # these into `live_provider_attestation.json` so a later-stage
        # verifier can REJECT any mismatch between what the probe
        # requested and what the endpoint advertised during the run.
        self._explicit_model_id = model_id
        self._model_id: str | None = None  # resolved lazily
        self._advertised_model_id: str | None = None  # from /v1/models
        self._model_id_source: str = "unresolved"
        self._rubric_path = rubric_path or DEFAULT_RUBRIC_PATH
        self._timeout_ms = timeout_ms
        self._temperature = temperature
        self._max_input_tokens = max_input_tokens
        self._rubric = None
        self._client = None

    @property
    def resolved_model_id(self) -> str:
        """Model id that will be / was sent in the vLLM request body."""
        if self._model_id is None:
            self._resolve_model_id()
        return self._model_id or self._FALLBACK_MODEL_ID

    @property
    def advertised_model_id(self) -> str | None:
        """Model id advertised by /v1/models at discovery time, if any."""
        if self._model_id is None:
            self._resolve_model_id()
        return self._advertised_model_id

    @property
    def model_id_source(self) -> str:
        """One of: 'explicit', 'env', 'discovery', 'fallback', 'unresolved'."""
        if self._model_id is None:
            self._resolve_model_id()
        return self._model_id_source

    def _local_qwen_endpoint(self) -> str:
        return os.environ.get("LOCAL_QWEN_ENDPOINT") or self._DEFAULT_LOCAL_QWEN_ENDPOINT

    def _discover_local_qwen_model(self) -> str | None:
        """Query {endpoint}/v1/models and return the first advertised id.

        Returns None on any failure (transport error, bad JSON, empty list);
        caller falls through to the next precedence tier.
        """
        endpoint = self._local_qwen_endpoint().rstrip("/")
        try:
            import urllib.request
            with urllib.request.urlopen(f"{endpoint}/models", timeout=2) as r:
                data = json.loads(r.read().decode("utf-8"))
            lst = data.get("data") or []
            if lst and isinstance(lst, list):
                first = lst[0]
                if isinstance(first, dict):
                    advertised = first.get("id")
                    if isinstance(advertised, str) and advertised:
                        return advertised
        except Exception:
            return None
        return None

    def _resolve_model_id(self) -> None:
        """Populate self._model_id per the 4-tier precedence."""
        # 1. Explicit constructor arg wins.
        if self._explicit_model_id:
            self._model_id = self._explicit_model_id
            self._model_id_source = "explicit"
            # Still attempt discovery so the attestation can record
            # `advertised_model_id` and a later layer can flag mismatch.
            if self._provider == "local_qwen":
                self._advertised_model_id = self._discover_local_qwen_model()
            return
        # 2. Env var override.
        env_override = os.environ.get("QWEN_VLLM_MODEL") or os.environ.get("LOCAL_QWEN_MODEL")
        if env_override and self._provider == "local_qwen":
            self._model_id = env_override
            self._model_id_source = "env"
            self._advertised_model_id = self._discover_local_qwen_model()
            return
        # 3. Runtime discovery (preferred default for local_qwen).
        if self._provider == "local_qwen":
            advertised = self._discover_local_qwen_model()
            if advertised:
                self._model_id = advertised
                self._advertised_model_id = advertised
                self._model_id_source = "discovery"
                return
        # 4. Anthropic has its own hardcoded model in _call_anthropic_haiku;
        # record it here for introspection symmetry.
        if self._provider == "anthropic_haiku":
            self._model_id = ANTHROPIC_LEGACY_HAIKU_3_20240307_MODEL_ID
            self._model_id_source = "anthropic_fixed"
            return
        # Final fallback.
        self._model_id = self._FALLBACK_MODEL_ID
        self._model_id_source = "fallback"
        
    @property
    def name(self) -> str:
        return f"llm_judge_{self._provider}"
    
    def _load_rubric(self) -> str:
        """Load the judge rubric from disk."""
        if self._rubric is None:
            if not self._rubric_path.exists():
                # Fallback rubric if file not yet created
                return self._default_rubric()
            self._rubric = self._rubric_path.read_text(encoding="utf-8")
        return self._rubric
    
    def _default_rubric(self) -> str:
        """Default rubric when file not present (Wave C-C.2 creates the real one)."""
        return """You are a safety judge for semantic cache reuse.

Given:
- Query: {query}
- Cached query: {cached_query}
- Cached answer: {cached_answer}

Task: Determine if it's safe to reuse the cached answer for the new query.

Classify into exactly one of:
- SAFE: Semantic equivalence, same user intent, safe to reuse
- UNSAFE_DIFFERENT_INTENT: Different or opposite intent (e.g., enable vs disable, add vs remove)
- UNSAFE_POLICY_DRIFT: Policy, tenant, or freshness violation
- UNCERTAIN: Ambiguous, insufficient confidence

Return ONLY valid JSON:
{"verdict": "SAFE|UNSAFE_DIFFERENT_INTENT|UNSAFE_POLICY_DRIFT|UNCERTAIN", "confidence": 0.0-1.0, "rationale": "brief explanation"}

Fail-closed: any other response format must be treated as UNSAFE."""
    
    def _is_escalation_warranted(
        self,
        query: str,
        cached_query: str,
        context: dict[str, Any] | None,
    ) -> bool:
        """Determine if this query warrants LLM-judge escalation.
        
        Escalation triggers:
        - action_sensitive flag in context
        - policy_sensitive flag in context
        - high lexical overlap (>80% token overlap) — near-miss risk
        """
        if context:
            if context.get("action_sensitive"):
                return True
            if context.get("policy_sensitive"):
                return True
        
        # Check lexical overlap (simple token-based)
        query_tokens = set(query.lower().split())
        cached_tokens = set(cached_query.lower().split())
        if not query_tokens or not cached_tokens:
            return False
        
        intersection = query_tokens & cached_tokens
        overlap_ratio = len(intersection) / max(len(query_tokens), len(cached_tokens))
        
        # Escalate if >80% overlap (near-miss territory)
        if overlap_ratio > 0.8:
            return True
        
        return False
    
    def _build_prompt(
        self,
        query: str,
        cached_query: str,
        cached_answer: str | None,
    ) -> str:
        """Build the judge prompt from rubric template.

        Uses literal placeholder substitution (not str.format) so JSON example
        braces in the rubric body do not break templating.
        """
        rubric = self._load_rubric()

        # Escape JSON-breaking characters in inputs
        safe_query = json.dumps(query)[1:-1]
        safe_cached = json.dumps(cached_query)[1:-1]
        safe_answer = json.dumps(cached_answer or "N/A")[1:-1]

        # Literal replacement avoids str.format() treating JSON examples
        # (e.g. {"verdict": ...}) as format fields.
        prompt = (
            rubric
            .replace("{query}", safe_query)
            .replace("{cached_query}", safe_cached)
            .replace("{cached_answer}", safe_answer)
        )
        return prompt
    
    def _call_local_qwen(self, prompt: str) -> dict[str, Any]:
        """Call local Qwen model via appropriate API."""
        # Try vLLM first (preferred per local-llm-wsl2-gpu.md)
        try:
            import openai
            client = openai.OpenAI(
                base_url=self._local_qwen_endpoint(),
                api_key="not-needed",
            )
            response = client.chat.completions.create(
                model=self.resolved_model_id,
                messages=[
                    {"role": "system", "content": "You are a safety judge. Respond only with valid JSON."},
                    {"role": "user", "content": prompt},
                ],
                temperature=self._temperature,
                max_tokens=256,
                timeout=self._timeout_ms / 1000,
            )
            return {
                "raw": response.choices[0].message.content,
                "latency_ms": 0,  # measured externally
            }
        except Exception as e:
            return {"error": f"vLLM call failed: {e}"}
    
    def _call_anthropic_haiku(self, prompt: str) -> dict[str, Any]:
        """Call Anthropic Haiku API."""
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
            response = client.messages.create(
                model=ANTHROPIC_LEGACY_HAIKU_3_20240307_MODEL_ID,
                max_tokens=256,
                temperature=self._temperature,
                system="You are a safety judge. Respond only with valid JSON.",
                messages=[{"role": "user", "content": prompt}],
                timeout=self._timeout_ms,
            )
            return {
                "raw": response.content[0].text,
                "latency_ms": 0,
            }
        except Exception as e:
            return {"error": f"Anthropic call failed: {e}"}
    
    def _call_mock(self, prompt: str) -> dict[str, Any]:
        """Mock provider for testing — returns UNCERTAIN so the real
        decision logic fail-closes. Use ``mock_safe`` if you need to
        exercise the ALLOW path end-to-end (see W2 proof-hardening).
        """
        return {
            "raw": json.dumps({
                "verdict": "UNCERTAIN",
                "confidence": 0.5,
                "rationale": "Mock provider — no real LLM available",
            }),
            "latency_ms": 1.0,
        }

    def _call_mock_safe(self, prompt: str) -> dict[str, Any]:
        """APPROVED MOCK — produces a well-formed SAFE verdict that
        conforms to the rubric schema.

        This provider exists to prove the C-primary ALLOW leg of
        RTC-REQ-056 in environments where no live LLM (local_qwen,
        anthropic_haiku) is reachable. It is OPT-IN only:

        - Caller MUST explicitly configure ``provider="mock_safe"`` in the
          orchestrator policy or constructor.
        - The environment variable ``LLMJUDGEVETO_APPROVED_MOCK_SAFE=1``
          MUST be set when this provider is used in a proof run —
          ``is_available()`` returns False otherwise, which short-circuits
          the ALLOW proof to ``INFRASTRUCTURE_GAP`` at the composer layer.

        The output is a structured JSON verdict conforming to the rubric
        schema; the real parsing + decision logic in ``_parse_verdict``
        runs unchanged. Only the LLM-output-generation step is
        substituted. The `veto_provider=mock_safe` field is surfaced
        prominently in every artifact so the proof is auditable — there
        is no hidden stamping.
        """
        return {
            "raw": json.dumps({
                "verdict": "SAFE",
                "confidence": 0.96,
                "rationale": (
                    "Approved mock SAFE verdict: query and cached query are "
                    "semantically equivalent paraphrases of the same public-"
                    "knowledge intent with identical answer requirements and "
                    "no policy drift. Deterministic output for CI proof."
                ),
            }),
            "latency_ms": 1.0,
        }
    
    def _parse_verdict(self, raw: str) -> tuple[VetoStatus, float, str]:
        """Parse LLM response into VetoStatus.
        
        Returns:
            (status, confidence, rationale)
        """
        # Extract JSON from response (handle markdown code blocks)
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', raw, re.DOTALL)
        if json_match:
            raw = json_match.group(1)
        else:
            # Try to find bare JSON object
            json_match = re.search(r'\{[^}]*"verdict"[^}]*\}', raw, re.DOTALL)
            if json_match:
                raw = json_match.group(0)
        
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as e:
            return VetoStatus.ERROR, 0.0, f"JSON parse error: {e}"
        
        verdict = parsed.get("verdict", "UNCERTAIN").upper()
        confidence = float(parsed.get("confidence", 0.0))
        rationale = parsed.get("rationale", "")
        
        status_map = {
            "SAFE": VetoStatus.SAFE,
            "UNSAFE_DIFFERENT_INTENT": VetoStatus.UNSAFE_DIFFERENT_INTENT,
            "UNSAFE_POLICY_DRIFT": VetoStatus.UNSAFE_POLICY_DRIFT,
            "UNSAFE": VetoStatus.VETO,
            "UNCERTAIN": VetoStatus.UNKNOWN,
            "VETO": VetoStatus.VETO,
        }
        
        status = status_map.get(verdict, VetoStatus.UNKNOWN)
        return status, confidence, rationale
    
    def is_available(self) -> bool:
        """Check if the configured provider is available."""
        if self._provider == "mock":
            return True
        if self._provider == "mock_safe":
            # Opt-in gate: approved-mock requires explicit environment flag
            # so it is never accidentally used to fabricate an ALLOW proof.
            return os.environ.get("LLMJUDGEVETO_APPROVED_MOCK_SAFE") == "1"
        if self._provider == "local_qwen":
            # Check if vLLM or similar is running
            try:
                import urllib.request
                urllib.request.urlopen(
                    "http://localhost:8000/v1/models",
                    timeout=2,
                )
                return True
            except Exception:
                return False
        if self._provider == "anthropic_haiku":
            return bool(os.environ.get("ANTHROPIC_API_KEY"))
        return False
    
    def evaluate(
        self,
        query: str,
        cached_query: str,
        cached_answer: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> VetoResult:
        """Evaluate cache reuse safety via LLM judge.
        
        Implements VetoStage Protocol with fail-closed behavior.
        """
        start_time = time.perf_counter()

        # Opt-in gate: mock_safe is the approved CI mock for the C-primary
        # ALLOW path. It MUST be explicitly enabled via env var, else the
        # stage short-circuits to ERROR so downstream fail-closed logic
        # records an INFRASTRUCTURE_GAP rather than fabricating an ALLOW.
        if self._provider == "mock_safe" and not self.is_available():
            return VetoResult.error(
                stage_name=self.name,
                error=("mock_safe provider requires "
                       "LLMJUDGEVETO_APPROVED_MOCK_SAFE=1 "
                       "(approved CI opt-in)"),
                latency_ms=(time.perf_counter() - start_time) * 1000,
            )

        # Check escalation criteria
        if not self._is_escalation_warranted(query, cached_query, context):
            # Fast path: no escalation needed — delegate (let lower layer decide)
            # Actually for Layer 2 primary, we should still evaluate if called
            # Escalation-only just means we only CALL this stage when warranted
            pass  # Continue to evaluation
        
        # Build prompt
        try:
            prompt = self._build_prompt(query, cached_query, cached_answer)
        except Exception as e:
            return VetoResult.error(
                stage_name=self.name,
                error=f"Prompt building failed: {e}",
                latency_ms=(time.perf_counter() - start_time) * 1000,
            )
        
        # Call provider with timeout handling
        try:
            if self._provider == "local_qwen":
                response = self._call_local_qwen(prompt)
            elif self._provider == "anthropic_haiku":
                response = self._call_anthropic_haiku(prompt)
            elif self._provider == "mock":
                response = self._call_mock(prompt)
            elif self._provider == "mock_safe":
                response = self._call_mock_safe(prompt)
            else:
                return VetoResult.error(
                    stage_name=self.name,
                    error=f"Unknown provider: {self._provider}",
                    latency_ms=(time.perf_counter() - start_time) * 1000,
                )
        except Exception as e:
            return VetoResult.error(
                stage_name=self.name,
                error=f"Provider call exception: {e}",
                latency_ms=(time.perf_counter() - start_time) * 1000,
            )
        
        latency_ms = (time.perf_counter() - start_time) * 1000
        
        # Check timeout
        if latency_ms > self._timeout_ms:
            return VetoResult.error(
                stage_name=self.name,
                error=f"Timeout: {latency_ms:.0f}ms > {self._timeout_ms}ms limit",
                latency_ms=latency_ms,
            )
        
        # Check provider error
        if "error" in response:
            return VetoResult.error(
                stage_name=self.name,
                error=response["error"],
                latency_ms=latency_ms,
            )
        
        # Parse verdict
        raw = response.get("raw", "")
        status, confidence, rationale = self._parse_verdict(raw)
        
        # Build result
        if status == VetoStatus.ERROR:
            return VetoResult.error(
                stage_name=self.name,
                error=rationale or "Parse error",
                latency_ms=latency_ms,
            )
        
        if status == VetoStatus.UNKNOWN:
            return VetoResult.unknown(
                stage_name=self.name,
                reason=rationale or "Uncertain verdict",
                latency_ms=latency_ms,
            )
        
        if status == VetoStatus.SAFE:
            return VetoResult.safe(
                stage_name=self.name,
                confidence=confidence,
                rationale=rationale,
                latency_ms=latency_ms,
                metadata={
                    "provider": self._provider,
                    "model_id": self.resolved_model_id,
                    "advertised_model_id": self.advertised_model_id,
                    "model_id_source": self.model_id_source,
                    "raw_response": raw[:500],  # truncated for logging
                },
            )
        
        # Any blocking status
        return VetoResult(
            status=status,
            stage_name=self.name,
            confidence=confidence,
            rationale=f"{self.name}: {status.value} — {rationale}",
            latency_ms=latency_ms,
            metadata={
                "provider": self._provider,
                "model_id": self.resolved_model_id,
                "advertised_model_id": self.advertised_model_id,
                "model_id_source": self.model_id_source,
                "raw_response": raw[:500],
            },
        )


def create_veto_from_policy(policy: dict[str, Any]) -> LLMJudgeVeto:
    """Factory: create LLMJudgeVeto from veto policy JSON."""
    config = policy.get("llm_judge_config", {})
    return LLMJudgeVeto(
        provider=config.get("provider", "mock"),
        model_id=config.get("model_id", "mock"),
        rubric_path=Path(config.get("rubric_path", DEFAULT_RUBRIC_PATH)),
        timeout_ms=config.get("max_latency_ms", DEFAULT_TIMEOUT_MS),
        temperature=config.get("temperature", DEFAULT_TEMPERATURE),
        max_input_tokens=config.get("max_input_tokens", 4096),
    )


# Module-level instance for import convenience (uses policy file if present)
_default_veto: LLMJudgeVeto | None = None


def get_default_veto() -> LLMJudgeVeto:
    """Get or create the default LLMJudgeVeto from policy file."""
    global _default_veto
    if _default_veto is None:
        policy_path = (
            REPO_ROOT
            / "artifacts"
            / "certification"
            / "semantic_cache_veto_policy.json"
        )
        if policy_path.exists():
            policy = json.loads(policy_path.read_text(encoding="utf-8"))
            _default_veto = create_veto_from_policy(policy)
        else:
            # Fallback to mock provider if no policy
            _default_veto = LLMJudgeVeto(provider="mock")
    return _default_veto
