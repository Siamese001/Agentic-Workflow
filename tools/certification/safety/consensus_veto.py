"""W2b Rewrite — Consensus-Jury Veto (R2.1 foundation).

ConsensusVeto orchestrates N parallel LLM judges and aggregates their
verdicts via strict-majority SAFE for ALLOW. Implements the VetoStage
Protocol so it is interchangeable with single-juror LLMJudgeVeto.

Aggregation rules (per plan § 2.2):
  - 3/3 SAFE       -> allow (mode=unanimous)
  - 2/3 SAFE       -> allow (mode=majority), dissent recorded
  - 1/3 SAFE       -> block (mode=no_majority)
  - 0/3 SAFE       -> block (mode=unanimous_unsafe)
  - Any ERROR      -> block (mode=incomplete) — fail-closed

All juror model IDs are sourced from the L0 routing model registry
SSOT (agentic_core.L0_routing.config.model_registry). No hardcoded
model strings in this module.

Plan: .windsurf/plans/rtc-w2b-consensus-jury-rewrite-9a4c71.md § 2.
Status: R2.1 foundation. Provider calls (OpenAI, Anthropic, Google)
land as R2.2 when LLMJudgeVeto is refactored for multi-provider.
Until then, ConsensusVeto requires callers to pass explicit
`_juror_call_impl` or relies on test mocking.
"""

from __future__ import annotations

import hashlib
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

# Repo-root path fix for imports when invoked from CI or ad-hoc scripts
REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agentic_core.L0_routing.config.model_registry import (
    ANTHROPIC_MODEL_ID,
    GEMINI_PRO_MODEL_ID,
    OPENAI_MODEL_ID,
    QWEN_LOCAL_MODEL_ID,
)
from tools.certification.safety.veto_protocol import VetoResult, VetoStatus

# Default 3-juror fleet per registry SSOT. Optional 4th Qwen juror
# activated via env var for local-first deployments.
DEFAULT_JURORS: tuple[tuple[str, str], ...] = (
    ("openai", OPENAI_MODEL_ID),
    ("anthropic", ANTHROPIC_MODEL_ID),
    ("google", GEMINI_PRO_MODEL_ID),
)

DEFAULT_TIMEOUT_MS_PER_JUROR = 15000  # matches W2B_VETO_TIMEOUT_MS default


def _env_key_for_juror(juror_family: str) -> str:
    """API-key env var by juror family."""
    return {
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "google": "GOOGLE_API_KEY",
        "local_qwen": "__vllm_no_key__",  # local — no key needed
    }.get(juror_family, "__unknown__")


@dataclass(frozen=True)
class JurorVerdict:
    """Per-juror outcome record — serialized into attestation schema v2."""

    juror_id: str  # e.g. "openai_gpt-5.4-mini"
    family: str  # "openai" | "anthropic" | "google" | "local_qwen"
    model_id: str
    verdict: str  # SAFE | UNSAFE_DIFFERENT_INTENT | UNSAFE_POLICY_DRIFT | UNCERTAIN | ERROR
    confidence: float
    rationale: str
    latency_ms: float
    raw_response_sha256: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "juror_id": self.juror_id,
            "family": self.family,
            "model_id": self.model_id,
            "verdict": self.verdict,
            "confidence": self.confidence,
            "rationale": self.rationale,
            "latency_ms": self.latency_ms,
            "raw_response_sha256": self.raw_response_sha256,
        }


# Type alias for the per-juror call implementation that ConsensusVeto
# dispatches to. Real impl (R2.2) lives in llm_judge_veto.py after the
# multi-provider refactor. Tests supply a mock.
JurorCallImpl = Callable[
    [str, str, str, str, str | None, dict[str, Any] | None],  # family, model_id, query, cached_q, cached_a, ctx
    JurorVerdict,
]


class ConsensusVeto:
    """Consensus-jury veto implementing VetoStage Protocol.

    Instantiates and evaluates N jurors in parallel via a thread pool.
    Each juror call returns a JurorVerdict. Aggregation is strict
    majority SAFE with fail-closed semantics on any ERROR.
    """

    def __init__(
        self,
        jurors: tuple[tuple[str, str], ...] | None = None,
        rubric_path: Path | None = None,
        timeout_ms_per_juror: int = DEFAULT_TIMEOUT_MS_PER_JUROR,
        temperature: float = 0.0,
        max_workers: int | None = None,
        juror_call_impl: JurorCallImpl | None = None,
    ) -> None:
        # Optional 4th Qwen juror: append QWEN_LOCAL when USE_CERT_JURY_QWEN=1.
        base_jurors = jurors if jurors is not None else DEFAULT_JURORS
        if (
            jurors is None
            and os.environ.get("USE_CERT_JURY_QWEN", "").strip().lower()
            in ("1", "true", "yes", "on")
        ):
            base_jurors = base_jurors + (("local_qwen", QWEN_LOCAL_MODEL_ID),)

        self._jurors = base_jurors
        self._rubric_path = rubric_path
        self._timeout_ms_per_juror = timeout_ms_per_juror
        self._temperature = temperature
        self._max_workers = max_workers or max(1, len(self._jurors))
        # Dependency-inject the per-juror caller. Tests supply a mock;
        # R2.2 wires the real multi-provider implementation.
        self._juror_call_impl = juror_call_impl

    # ----- VetoStage protocol -----

    @property
    def name(self) -> str:
        return "consensus_veto"

    def is_available(self) -> bool:
        """Available iff every juror has its API key present.

        local_qwen is treated as always-available here (availability is
        endpoint-probed inside the juror call itself). Missing any
        cloud-juror API key fails-closed at this stage.
        """
        for family, _ in self._jurors:
            key_env = _env_key_for_juror(family)
            if key_env == "__unknown__":
                return False
            if key_env == "__vllm_no_key__":
                continue  # local — no key check here
            if not os.environ.get(key_env):
                return False
        return True

    def evaluate(
        self,
        query: str,
        cached_query: str,
        cached_answer: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> VetoResult:
        """Dispatch jurors in parallel and aggregate."""
        start = time.perf_counter()

        if self._juror_call_impl is None:
            # R2.1 foundation: no real provider calls wired yet. Fail-closed.
            return VetoResult.error(
                stage_name=self.name,
                error=(
                    "ConsensusVeto missing juror_call_impl. R2.2 wires the "
                    "real multi-provider implementation; until then callers "
                    "must inject an impl or tests must mock."
                ),
                latency_ms=(time.perf_counter() - start) * 1000,
            )

        per_juror: list[JurorVerdict] = []
        with ThreadPoolExecutor(max_workers=self._max_workers) as pool:
            futures = {
                pool.submit(
                    self._juror_call_impl,
                    family,
                    model_id,
                    query,
                    cached_query,
                    cached_answer,
                    context,
                ): (family, model_id)
                for family, model_id in self._jurors
            }
            for fut in as_completed(futures):
                family, model_id = futures[fut]
                try:
                    per_juror.append(fut.result())
                except Exception as e:  # noqa: BLE001 — fail-closed captures any juror failure
                    per_juror.append(
                        JurorVerdict(
                            juror_id=f"{family}_{model_id}",
                            family=family,
                            model_id=model_id,
                            verdict="ERROR",
                            confidence=0.0,
                            rationale=f"Juror exception: {e}",
                            latency_ms=0.0,
                        )
                    )

        latency_ms = (time.perf_counter() - start) * 1000
        return self._aggregate(per_juror, latency_ms)

    # ----- Aggregation -----

    def _aggregate(
        self, per_juror: list[JurorVerdict], latency_ms: float
    ) -> VetoResult:
        n = len(per_juror)
        if n == 0:
            return VetoResult.error(
                stage_name=self.name,
                error="No jurors evaluated",
                latency_ms=latency_ms,
            )

        safe_count = sum(1 for v in per_juror if v.verdict == "SAFE")
        error_count = sum(
            1 for v in per_juror if v.verdict in ("ERROR", "UNCERTAIN")
        )
        # Strict-majority threshold: (N // 2) + 1 matches
        # consensus_majority_threshold in agentic_core/utils/path_constants
        threshold = (n // 2) + 1

        shared_metadata: dict[str, Any] = {
            "consensus_mode": None,
            "safe_count": safe_count,
            "dissent_count": n - safe_count,
            "error_count": error_count,
            "juror_count": n,
            "threshold": threshold,
            "per_juror": [v.to_dict() for v in per_juror],
        }

        # Fail-closed: any juror ERROR => CONSENSUS_INCOMPLETE (schema v2 reason)
        raw_errors = sum(1 for v in per_juror if v.verdict == "ERROR")
        if raw_errors > 0:
            shared_metadata["consensus_mode"] = "incomplete"
            return VetoResult(
                status=VetoStatus.VETO,
                stage_name=self.name,
                confidence=0.0,
                rationale=(
                    f"{self.name}: CONSENSUS_INCOMPLETE — "
                    f"{raw_errors}/{n} jurors errored (fail-closed)"
                ),
                latency_ms=latency_ms,
                metadata=shared_metadata,
            )

        if safe_count == n:
            shared_metadata["consensus_mode"] = "unanimous"
            avg_conf = sum(v.confidence for v in per_juror) / n
            return VetoResult.safe(
                stage_name=self.name,
                confidence=avg_conf,
                rationale=f"Unanimous SAFE verdict from all {n} jurors",
                latency_ms=latency_ms,
                metadata=shared_metadata,
            )

        if safe_count >= threshold:
            shared_metadata["consensus_mode"] = "majority"
            safe_jurors = [v for v in per_juror if v.verdict == "SAFE"]
            avg_safe_conf = (
                sum(v.confidence for v in safe_jurors) / len(safe_jurors)
            )
            return VetoResult.safe(
                stage_name=self.name,
                confidence=avg_safe_conf,
                rationale=(
                    f"Strict majority SAFE ({safe_count}/{n}); "
                    f"{n - safe_count} dissenting juror(s) recorded"
                ),
                latency_ms=latency_ms,
                metadata=shared_metadata,
            )

        if safe_count == 0:
            shared_metadata["consensus_mode"] = "unanimous_unsafe"
            return VetoResult(
                status=VetoStatus.VETO,
                stage_name=self.name,
                confidence=0.0,
                rationale=(
                    f"{self.name}: UNANIMOUS_NOT_SAFE — "
                    f"all {n} jurors returned non-SAFE verdict"
                ),
                latency_ms=latency_ms,
                metadata=shared_metadata,
            )

        # 1 SAFE / 2 non-SAFE — no majority
        shared_metadata["consensus_mode"] = "no_majority"
        return VetoResult(
            status=VetoStatus.VETO,
            stage_name=self.name,
            confidence=0.0,
            rationale=(
                f"{self.name}: CONSENSUS_NO_MAJORITY — "
                f"{safe_count}/{n} SAFE (need {threshold})"
            ),
            latency_ms=latency_ms,
            metadata=shared_metadata,
        )


def hash_raw_response(raw: str) -> str:
    """SHA-256 of a raw provider response string. Used in JurorVerdict."""
    return hashlib.sha256(raw.encode("utf-8")).hexdigest() if raw else ""


__all__ = [
    "ConsensusVeto",
    "DEFAULT_JURORS",
    "DEFAULT_TIMEOUT_MS_PER_JUROR",
    "JurorCallImpl",
    "JurorVerdict",
    "hash_raw_response",
]
