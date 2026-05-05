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

from tools.certification.safety.rtc_req_056_panel import (
    ANTHROPIC_JUROR,
    GEMINI_JUROR,
    OPENAI_JUROR,
    REQUIRED_JURORS as _PANEL_REQUIRED_JURORS,
)
from tools.certification.safety.veto_protocol import VetoResult, VetoStatus

# Default juror fleet is sourced from the RTC-REQ-056 panel registry.
# The tuple shape is (provider_family, model_id) — the ConsensusVeto
# then dispatches to the juror_call_impl with that family string. The
# real impl (``make_real_juror_call_impl`` in consensus_juror_clients.py)
# validates provider_family against the registry on every call.
DEFAULT_JURORS: tuple[tuple[str, str], ...] = tuple(
    (j.provider_family, j.model_id) for j in _PANEL_REQUIRED_JURORS
)

DEFAULT_TIMEOUT_MS_PER_JUROR = 15000  # matches W2B_VETO_TIMEOUT_MS default


def _env_key_for_juror(juror_family: str) -> str:
    """Primary API-key env var by juror family. Resolves via the
    RTC-REQ-056 panel registry when possible; falls back to a small
    compatibility map for legacy values used by older tests."""
    # Panel-registry families first
    for j in _PANEL_REQUIRED_JURORS:
        if j.provider_family.lower() == (juror_family or "").lower():
            return j.env_key
    # Legacy compatibility (older test / prototype names)
    return {
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "google": "GOOGLE_API_KEY",
        "google_gemini": "GOOGLE_API_KEY",  # GEMINI_API_KEY deprecated alias
        "local_qwen": "__vllm_no_key__",
    }.get(juror_family, "__unknown__")


def _env_key_aliases_for_juror(juror_family: str) -> tuple[str, ...]:
    """Registered aliases for a juror's API key, per panel registry."""
    for j in _PANEL_REQUIRED_JURORS:
        if j.provider_family.lower() == (juror_family or "").lower():
            return j.env_key_aliases
    return ()


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
        # Panel registry is the ONLY source of default jurors. No Qwen
        # opt-in is permitted for the RTC-REQ-056 certification path per
        # operator directive 2026-05-01. Explicit ``jurors`` arg is kept
        # for tests and experimental configurations only.
        base_jurors = jurors if jurors is not None else DEFAULT_JURORS
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
        """Available iff every juror has its API key (or a registered
        alias) present in the environment.

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
            aliases = _env_key_aliases_for_juror(family)
            candidates = (key_env, *aliases)
            if not any(os.environ.get(c) for c in candidates):
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
        """Aggregate under the ``all_required_safe`` quorum rule.

        The RTC-REQ-056 panel requires ALL registered jurors to return
        SAFE. Any other outcome (UNSAFE, UNKNOWN, ERROR, or missing)
        results in a fail-closed VETO. Majority vote is deliberately
        NOT implemented — adding it requires updating the registry,
        the gate logic in ``rtc_req_056_gate.py``, and new tests.
        """
        n = len(per_juror)
        if n == 0:
            return VetoResult.error(
                stage_name=self.name,
                error="No jurors evaluated",
                latency_ms=latency_ms,
            )

        safe_count = sum(1 for v in per_juror if v.verdict == "SAFE")
        error_count = sum(1 for v in per_juror if v.verdict == "ERROR")
        unknown_count = sum(1 for v in per_juror if v.verdict == "UNCERTAIN")
        unsafe_count = sum(
            1 for v in per_juror
            if v.verdict in ("UNSAFE_DIFFERENT_INTENT", "UNSAFE_POLICY_DRIFT")
        )

        shared_metadata: dict[str, Any] = {
            "consensus_mode": None,
            "quorum_rule": "all_required_safe",
            "safe_count": safe_count,
            "dissent_count": n - safe_count,
            "error_count": error_count,
            "unknown_count": unknown_count,
            "unsafe_count": unsafe_count,
            "juror_count": n,
            "required_juror_count": n,
            "per_juror": [v.to_dict() for v in per_juror],
        }

        # Fail-closed: any juror ERROR => CONSENSUS_INCOMPLETE
        if error_count > 0:
            shared_metadata["consensus_mode"] = "incomplete"
            return VetoResult(
                status=VetoStatus.VETO,
                stage_name=self.name,
                confidence=0.0,
                rationale=(
                    f"{self.name}: CONSENSUS_INCOMPLETE — "
                    f"{error_count}/{n} jurors errored (fail-closed)"
                ),
                latency_ms=latency_ms,
                metadata=shared_metadata,
            )

        # all_required_safe: only 3/3 SAFE allows
        if safe_count == n:
            shared_metadata["consensus_mode"] = "unanimous"
            avg_conf = sum(v.confidence for v in per_juror) / n
            return VetoResult.safe(
                stage_name=self.name,
                confidence=avg_conf,
                rationale=(
                    f"all_required_safe met: {n}/{n} jurors returned SAFE"
                ),
                latency_ms=latency_ms,
                metadata=shared_metadata,
            )

        # Any non-SAFE -> fail closed
        if safe_count == 0 and unsafe_count == n:
            mode = "unanimous_unsafe"
        elif unknown_count > 0 and unsafe_count == 0 and error_count == 0:
            mode = "quorum_fail_unknown"
        else:
            mode = "quorum_fail"
        shared_metadata["consensus_mode"] = mode
        return VetoResult(
            status=VetoStatus.VETO,
            stage_name=self.name,
            confidence=0.0,
            rationale=(
                f"{self.name}: QUORUM_FAIL ({mode}) — "
                f"{safe_count}/{n} SAFE "
                f"(unsafe={unsafe_count} unknown={unknown_count} "
                f"error={error_count})"
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
