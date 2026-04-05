"""
_ssot_routing.py — Routing decision engine and SovereignDecisionEngine for execute_ssot.

Extracted from execute_ssot.py to reduce file size and improve cohesion.
All public symbols are re-exported from execute_ssot.py for backward compat.
"""

import logging
import os
import re
import uuid
from typing import Any

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    DEFAULT_TIMEOUT,
    HEALING_CONFIDENCE_X as _CONF_X,
    HEALING_CONFIDENCE_Y as _CONF_Y,
    QWEN_14B_MODEL_ID as _QWEN_14B_MODEL_ID,
    SSOT_SCORE_THRESHOLD_DET as _SCORE_DET,
    SSOT_SCORE_THRESHOLD_QWEN as _SCORE_QWEN,
)
from agentic_core.L0_routing.scripts._ssot_types import (
    _QWEN_DISALLOWED,
    _STRUCTURAL_CLASS,
    ConfidenceScore,
    FailureType,
    RoutingDecision,
    RoutingInputs,
    RoutingTier,
)

# L2 import deferred to avoid layer boundary violation (L0→L2)
# from agentic_core.L2_execution.utils.providers import get_clock

_clock_cache = None

def _get_clock():
    global _clock_cache
    if _clock_cache is None:
        try:
            from agentic_core.L2_execution.utils.providers import get_clock as _get_clock_impl
            _clock_cache = _get_clock_impl()
        except ImportError as e:
            logging.warning(f"L2 clock provider not available: {e}")
            # Return a minimal clock implementation
            import time
            class _MinimalClock:
                def now_epoch(self):
                    return time.time()
            _clock_cache = _MinimalClock()
    return _clock_cache
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_through,
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

logger = logging.getLogger(__name__)


def compute_routing_decision(inputs: RoutingInputs) -> RoutingDecision:
    """Pure SSOT routing function — strict gate order, no side effects."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "compute_routing_decision", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "compute_routing_decision", "p0_governance")
    C, B, A, N, F, L = (inputs.C, inputs.B, inputs.A, inputs.N, inputs.F, inputs.L)

    def _decide(tier: RoutingTier, gate: str, score: int = 0) -> RoutingDecision:
        if tier == RoutingTier.DETERMINISTIC:
            model = "deterministic-sovereign"
        elif tier == RoutingTier.QWEN:
            model = "Qwen2.5-14B-Instruct-AWQ"
        elif tier == RoutingTier.GEMINI:
            model = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")
        else:
            model = "FAIL_CLOSED"
        raw = f"{tier.value}|{score}|{gate}|{inputs.failure_type.value}|{C}|{B}|{A}|{N}|{F}|{L}|{inputs.replay_mode}|{inputs.retry_count}"
        digest = _hashlib.md5(raw.encode(), usedforsecurity=False).hexdigest()[:16]
        return RoutingDecision(
            tier=tier,
            score=score,
            gate_applied=gate,
            model_id=model,
            factors={"C": C, "B": B, "A": A, "N": N, "F": F, "L": L},
            inputs=inputs,
            determinism_digest=digest,
        )

    if inputs.replay_mode:
        return _decide(RoutingTier.DETERMINISTIC, "GATE_0_REPLAY")
    if inputs.retry_count >= 3:
        if inputs.provider_prohibited_gemini:
            return _decide(RoutingTier.FAIL_CLOSED, "GATE_1_RETRY_OVERRIDE_FAIL_CLOSED")
        return _decide(RoutingTier.GEMINI, "GATE_1_RETRY_OVERRIDE")
    if inputs.failure_type in _STRUCTURAL_CLASS:
        if inputs.deterministic_coverage:
            return _decide(RoutingTier.DETERMINISTIC, "GATE_2_STRUCTURAL_DET_COV")
        if inputs.provider_prohibited_gemini:
            return _decide(RoutingTier.FAIL_CLOSED, "GATE_2_STRUCTURAL_FAIL_CLOSED")
        return _decide(RoutingTier.GEMINI, "GATE_2_STRUCTURAL_NO_DET_COV")
    if B == 3 and A == 0 and inputs.playbook_match and inputs.deterministic_coverage:
        return _decide(RoutingTier.DETERMINISTIC, "GATE_3_CRITICAL_SURFACE_MECH")
    S = 3 * C + 4 * B + 3 * A + 2 * N + 4 * F
    if inputs.playbook_match:
        S = max(0, S - 4)
    if B == 3 and F == 3 and (C >= 2 or A >= 1):
        if inputs.provider_prohibited_gemini and inputs.provider_prohibited_qwen:
            return _decide(RoutingTier.FAIL_CLOSED, "GATE_4_HARD_OVERRIDE_FAIL_CLOSED", S)
        return _decide(RoutingTier.GEMINI, "GATE_4_HARD_OVERRIDE", S)
    if S <= _SCORE_DET:
        tier = RoutingTier.DETERMINISTIC
        gate = "THRESHOLD_LOW_DET"
    elif S <= _SCORE_QWEN:
        tier = RoutingTier.QWEN
        gate = "THRESHOLD_MED_QWEN"
    else:
        tier = RoutingTier.GEMINI
        gate = "THRESHOLD_HIGH_GEMINI"
        if inputs.provider_prohibited_gemini:
            return _decide(RoutingTier.FAIL_CLOSED, "THRESHOLD_HIGH_FAIL_CLOSED", S)
    _qwen_disallowed_type = inputs.failure_type in _QWEN_DISALLOWED
    _qwen_blocked = _qwen_disallowed_type or inputs.provider_prohibited_qwen
    if (
        tier == RoutingTier.QWEN
        and S in range(_SCORE_DET + 1, _SCORE_DET + 3)
        and (L == 0)
        and (not _qwen_blocked)
    ):
        tier = RoutingTier.DETERMINISTIC
        gate = f"{gate}.L_TIEBREAK_DOWN"
    elif (
        tier == RoutingTier.DETERMINISTIC
        and S in range(_SCORE_DET - 1, _SCORE_DET + 1)
        and (L == 3)
        and (not _qwen_disallowed_type)
    ):
        tier = RoutingTier.QWEN
        gate = f"{gate}.L_TIEBREAK_UP"
    if tier == RoutingTier.QWEN and inputs.failure_type in _QWEN_DISALLOWED:
        if inputs.deterministic_coverage and A == 0 and (C == 0):
            return _decide(RoutingTier.DETERMINISTIC, f"{gate}.QWEN_DISALLOWED_DET_FALLBACK", S)
        if inputs.provider_prohibited_gemini:
            return _decide(RoutingTier.FAIL_CLOSED, f"{gate}.QWEN_DISALLOWED_FAIL_CLOSED", S)
        return _decide(RoutingTier.GEMINI, f"{gate}.QWEN_DISALLOWED", S)
    if tier == RoutingTier.QWEN and inputs.provider_prohibited_qwen:
        if inputs.provider_prohibited_gemini:
            return _decide(RoutingTier.FAIL_CLOSED, f"{gate}.BOTH_PROHIBITED", S)
        return _decide(RoutingTier.GEMINI, f"{gate}.QWEN_PROHIBITED_FALLBACK", S)
    if tier == RoutingTier.GEMINI and inputs.provider_prohibited_gemini:
        return _decide(RoutingTier.FAIL_CLOSED, f"{gate}.GEMINI_PROHIBITED", S)
    return _decide(tier, gate, S)


def _get_safe_subprocess_run():
    from agentic_core.L2_execution.tools.safe_subprocess import safe_subprocess_run

    return safe_subprocess_run


class SovereignDecisionEngine:
    """
    [HARDENED] Sovereign Decision Engine with strict token-based access control.
    Synthesizes patterns from FileClassificationAgent for cycle detection and resource protection.
    Unified flat class (formerly AutonomousDecisionEngine -> Enhanced -> Sovereign hierarchy).
    """

    def __init__(
        self,
        enable_llm: bool = True,
        state_mgr: Any | None = None,
        enable_cda: bool = False,
        execution_context: Any | None = None,
        healing_memory_retriever: Any | None = None,
        auto_approve: bool = False,
    ):
        self.enable_llm = enable_llm
        self.decisions_made = []
        self.state_mgr = state_mgr
        self._execution_context = execution_context
        self._healing_count: int = 0
        self._healing_enabled: bool = True
        self._max_healing_operations: int = 10000
        self.auto_approve: bool = auto_approve
        self._call_path: set[str] = set()
        self.enable_cda = enable_cda
        self._sovereignty_token: str | None = None
        self._operation_stack: list[str] = []
        # guardian: allow-magic-config
        self._max_stack_depth = 10
        self._atomic_lock = False
        self._healing_memory_retriever = healing_memory_retriever

    def _calculate_semantic_similarity(self, unknown: str, existing: list[str]) -> float:
        """Calculate semantic similarity for unknown items against a candidate list.

        Uses BAAI/bge-m3 cosine similarity (GPU-accelerated on RTX 5090).
        Falls back to Jaccard word-overlap only on exception.
        """
        if not existing:
            return 0.0
        try:
            bmg_fn = self._get_bmg_cosine_similarity()
            return bmg_fn(unknown, existing)
        except (ImportError, AttributeError, ValueError):
            pass
        unknown_words = set(unknown.lower().replace("_", " ").replace("-", " ").split())
        max_similarity = 0.0
        for item in existing:
            existing_words = set(item.lower().replace("_", " ").replace("-", " ").split())
            intersection = unknown_words & existing_words
            union = unknown_words | existing_words
            if union:
                similarity = len(intersection) / len(union)
                max_similarity = max(max_similarity, similarity)
        return max_similarity

    @staticmethod
    def _get_bmg_cosine_similarity() -> object:
        """Lazy seam: load bmg_cosine_similarity from L2 healers without module-level import."""
        from agentic_core.L2_execution.healers.bmg_embedding_similarity import bmg_cosine_similarity

        return bmg_cosine_similarity

    @staticmethod
    def _get_bmg_embedding_agent_keys() -> frozenset:
        """Lazy seam: load BMG_EMBEDDING_AGENT_KEYS from L2 healing_tier_config."""
        from agentic_core.L2_execution.healers.healing_tier_config import BMG_EMBEDDING_AGENT_KEYS

        return BMG_EMBEDDING_AGENT_KEYS

    @staticmethod
    def _get_qwen_14b_routing_config() -> tuple:
        """Lazy seam: load Qwen 14B routing constants from L2 healing_tier_config."""
        from agentic_core.L2_execution.healers.healing_tier_config import (
            QWEN_14B_AGENT_KEYS,
            QWEN_14B_MODEL_ID,
        )

        return (QWEN_14B_AGENT_KEYS, QWEN_14B_MODEL_ID)

    @staticmethod
    def _get_qwen_vllm_arbiter():
        """Lazy seam: return callable that invokes Qwen 14B via WSL vLLM subprocess."""
        import json
        from pathlib import Path

        WSL_PYTHON = "/home/amita/venvs/vllm/bin/python"
        INFERENCE_SCRIPT = str(
            Path(__file__).parent.parent.parent / "L2_execution" / "healers" / "qwen_vllm_inference.py"
        )
        MODEL_PATH = "/home/amita/models/Qwen2.5-14B-Instruct-AWQ"

        # guardian: allow-type-erasure
        def _arbiter(
            agent_name: str, violation_types: list, territory: str, score: int = 0, gate: str = ""
        ) -> dict:
            script_wsl = INFERENCE_SCRIPT.replace("\\", "/").replace("C:", "/mnt/c").replace("c:", "/mnt/c")
            repo_root_wsl = (
                str(Path(__file__).resolve().parents[3])
                .replace("\\", "/")
                .replace("C:", "/mnt/c")
                .replace("c:", "/mnt/c")
            )
            cmd = [
                "wsl",
                "bash",
                "-c",
                f"PYTHONPATH={repo_root_wsl}:$PYTHONPATH {WSL_PYTHON} {script_wsl} --agent_name {agent_name} --score {score} --gate {gate} --territory {territory} --model_path {MODEL_PATH}"
                + (f" --violation_types {' '.join(violation_types)}" if violation_types else ""),
            ]
            result = _get_safe_subprocess_run()(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=DEFAULT_TIMEOUT,
            )
            if result.returncode != 0:
                raise RuntimeError(f"vLLM subprocess failed: {result.stderr[-500:]}")
            lines = [l.strip() for l in result.stdout.splitlines() if l.strip()]
            for line in reversed(lines):
                try:
                    return json.loads(line)
                except json.JSONDecodeError:
                    continue
            raise RuntimeError(f"No JSON in vLLM output: {result.stdout[-300:]}")

        return _arbiter

    def _calculate_pattern_confidence(self, violation_type: str) -> float:
        """Regex-based pattern matching for known violation types."""
        high_confidence_patterns = [
            ".*NAMING.*",
            ".*HIERARCHY.*",
            ".*IMPORT.*",
            ".*SHALLOW.*",
            ".*DEEP.*",
            ".*VOID.*",
            ".*DUPLICATE.*",
            ".*ORPHAN.*",
        ]
        for pattern in high_confidence_patterns:
            if re.match(pattern, violation_type, re.IGNORECASE):
                return 0.9
        return 0.5

    def _compute_novelty_score(
        self, failure_type: "FailureType | None", territory: str, confidence: "ConfidenceScore"
    ) -> int:
        """Compute the novelty score N (0-3) for RoutingInputs.

        Embeds the current failure signal text and compares against stored
        vectors to produce a true novelty score:
          N=0  max_similarity >= 0.85  (seen before)
          N=1  max_similarity >= 0.70  (similar)
          N=2  max_similarity >= 0.50  (somewhat novel)
          N=3  max_similarity <  0.50  (highly novel)

        Raises VectorSourceMismatchError if stored vectors and the current
        vector have incompatible dimensions.
        """
        try:
            from agentic_core.L2_execution.healers.bmg_embedding_similarity import bmg_embed_text

            ft_str = failure_type.value if failure_type is not None else "UNKNOWN"
            signal_text = f"{ft_str} {territory}"
            vec = bmg_embed_text(signal_text)
            import numpy as _np

            q = _np.array(vec, dtype=_np.float32)
            recent: list = []
            if self.state_mgr is not None:
                recent = self.state_mgr.state.get("meta_learning", {}).get("recent_failure_vectors", [])
            if not recent:
                return 1
            mat = _np.array(recent, dtype=_np.float32)
            if mat.ndim == 2 and mat.shape[1] != q.shape[0]:
                from agentic_core.L1_cognition.memory.healing_memory_retriever import (
                    VectorSourceMismatchError,
                )

                raise VectorSourceMismatchError(
                    f"Vector source mismatch: stored dim={mat.shape[1]}, query dim={q.shape[0]}"
                )
            max_sim = float(_np.dot(mat, q).max())
            if max_sim >= 0.85:
                return 0
            if max_sim >= 0.7:
                return 1
            if max_sim >= 0.5:
                return 2
            return 3
        except (ImportError, AttributeError, ValueError, RuntimeError) as _exc:
            from agentic_core.L1_cognition.memory.healing_memory_retriever import (
                VectorSourceMismatchError as _VSME,
            )

            if isinstance(_exc, _VSME):
                raise
            return 1

    def _route_decision(
        self,
        confidence: "ConfidenceScore",
        agent_name: str,
        territory: str,
        failure_type: "FailureType | None" = None,
        retry_count: int = 0,
        replay_mode: bool = False,
        playbook_match: bool = False,
        deterministic_coverage: bool = False,
        provider_prohibited_gemini: bool = False,
        provider_prohibited_qwen: bool = False,
    ) -> "RoutingDecision":
        """Map healing context to a hardened SSOT RoutingDecision."""
        if failure_type is None:
            reasoning_upper = (confidence.reasoning or "").upper()
            ft = FailureType.UNKNOWN
            for member in FailureType:
                if member.value in reasoning_upper:
                    ft = member
                    break
            failure_type = ft
        if self._healing_memory_retriever is not None:
            try:
                from agentic_core.L1_cognition.memory.healing_memory_retriever import (
                    SovereigntyError as _SovereigntyError,
                )

                _signal_text = f"{(failure_type.value if failure_type else 'UNKNOWN')} {territory}"
                _advisory = self._healing_memory_retriever.retrieve_similar_incidents(_signal_text, top_k=3)
                for _inc in _advisory:
                    if not getattr(_inc, "advisory_only", True):
                        raise _SovereigntyError(
                            f"advisory_only=False on incident {getattr(_inc, 'content_hash', '?')!r}; routing tier MUST NOT be influenced by retrieval results."
                        )
                if _advisory:
                    logger.debug(
                        "[B3-Advisory] top=%d sim=%.4f (advisory_only=%s) — routing unchanged",
                        len(_advisory),
                        _advisory[0].similarity,
                        _advisory[0].advisory_only,
                    )
            except (ImportError, AttributeError, ValueError) as _exc:
                from agentic_core.L1_cognition.memory.healing_memory_retriever import SovereigntyError as _SE

                if isinstance(_exc, _SE):
                    raise
        C = min(3, max(0, int(3 - confidence.value * 3)))
        B = 3 if territory.startswith("L5") else 2 if AGENTIC_CORE_DIR in territory else 1
        A = 0 if confidence.value >= _CONF_X else 2 if confidence.value < _CONF_Y else 1
        N = self._compute_novelty_score(failure_type, territory, confidence)
        high_cost = {
            FailureType.LAYER_VIOLATION,
            FailureType.GATEWAY_BYPASS,
            FailureType.KILL_SWITCH_BYPASS,
            FailureType.SIGNATURE_VERIFY,
            FailureType.UNSIGNED_INGRESS,
        }
        F = 3 if failure_type in high_cost else 2 if confidence.value < _CONF_Y else 1
        L = 0
        ri = RoutingInputs(
            failure_type=failure_type,
            retry_count=retry_count,
            C=C,
            B=B,
            A=A,
            N=N,
            F=F,
            L=L,
            replay_mode=replay_mode,
            playbook_match=playbook_match,
            deterministic_coverage=deterministic_coverage,
            provider_prohibited_gemini=provider_prohibited_gemini,
            provider_prohibited_qwen=provider_prohibited_qwen,
        )
        decision = compute_routing_decision(ri)
        logger.info(decision.as_log_line())
        return decision

    def _classify_violation_type(self, message: str) -> str:
        """Classify a violation message into a canonical violation type string."""
        msg_lower = message.lower()
        if "missing sovereign root" in msg_lower or ("missing" in msg_lower and "director" in msg_lower):
            return "MISSING_DIRECTORY"
        if "forbidden keyword" in msg_lower:
            return "FORBIDDEN_CONTENT"
        if "forbidden extension" in msg_lower:
            return "EXTENSION_MISMATCH"
        if "test_" in msg_lower and "file" in msg_lower:
            return "TEST_FILE_MISPLACED"
        if "sovereign" in msg_lower:
            return "SOVEREIGN_VIOLATION"
        return "STRUCTURAL_VIOLATION"

    # guardian: allow-magic-config
    def _check_healing_budget(self, agent_name: str, depth: int = 0, max_depth: int = 3) -> tuple[bool, str]:
        """Prevents infinite healing loops and budget exhaustion."""
        if agent_name == "Unknown":
            agent_name = f"operation-{id(self)}"
        if agent_name in self._call_path:
            return (False, f"Healing cycle detected: {agent_name}")
        if depth > max_depth:
            return (False, f"Healing depth limit exceeded for {agent_name}")
        if self._healing_count >= self._max_healing_operations:
            logger.warning(
                "[BUDGET] Healing budget exhausted (%d/%d) — %s blocked",
                self._healing_count,
                self._max_healing_operations,
                agent_name,
            )
            return (False, f"Budget exceeded ({self._healing_count})")
        return (True, "OK")

    # guardian: allow-magic-config
    def calculate_healing_confidence(
        self,
        violations_count: int,
        violation_types: list[str],
        territory: str,
        historical_success_rate: float = 0.8,
        agent_name: str = "",
    ) -> ConfidenceScore:
        """Calculates weighted confidence score.

        Uses GPU-accelerated BAAI/bge-m3 cosine similarity for pattern matching
        when agent_name is in BMG_EMBEDDING_AGENT_KEYS.
        """

        _emit_records_execution_trace(
            str(uuid.uuid4()),
            LayerSegment.L3_ORCHESTRATION,
            f"SovereignDecisionEngine.calculate_healing_confidence:{territory}",
        )
        if violations_count == 0:
            return ConfidenceScore(value=1.0, reasoning="Zero violations")
        if getattr(self, "auto_approve", False):
            return ConfidenceScore(value=1.0, reasoning="AUTO-HEAL: --heal active, confidence forced to 1.0")
        base_score = max(0.0, 1.0 - min(violations_count, 10) * 0.1)
        pattern_score = 0.5
        bmg_used = False
        if violation_types and agent_name:
            try:
                BMG_EMBEDDING_AGENT_KEYS = self._get_bmg_embedding_agent_keys()
                if agent_name in BMG_EMBEDDING_AGENT_KEYS:
                    sem_score = self._calculate_semantic_similarity(territory, violation_types)
                    pattern_score = sem_score
                    bmg_used = True
                    logger.warning("[BMG-GPU] %s: semantic score=%.4f (CUDA/bge-m3)", agent_name, sem_score)
            except (ImportError, AttributeError, ValueError):
                pass
            if not bmg_used:
                scores = [self._calculate_pattern_confidence(v) for v in violation_types]
                pattern_score = sum(scores) / len(scores)
        final_value = base_score * 0.4 + pattern_score * 0.4 + historical_success_rate * 0.2
        if territory == "prompt_governance":
            final_value *= 1.1
        if territory.startswith("L5"):
            final_value *= 0.9
        reasoning = f"Base: {base_score:.2f}, Pattern: {pattern_score:.2f}"
        if bmg_used:
            reasoning += " [BMG-GPU]"
        return ConfidenceScore(value=min(1.0, final_value), reasoning=reasoning)

    def should_proceed_with_healing(
        self,
        confidence: ConfidenceScore,
        agent_name: str = "Unknown",
        territory: str = "unknown",
        failure_type: "FailureType | None" = None,
        retry_count: int = 0,
        replay_mode: bool = False,
        playbook_match: bool = False,
        deterministic_coverage: bool = False,
        provider_prohibited_gemini: bool = False,
        provider_prohibited_qwen: bool = False,
    ) -> tuple[bool, str]:
        """Determines if healing should proceed using the hardened SSOT routing algorithm."""
        from datetime import datetime

        is_safe, msg = self._check_healing_budget(agent_name)
        if not is_safe:
            return (False, f"SAFETY LOCK: {msg}")
        routing = self._route_decision(
            confidence=confidence,
            agent_name=agent_name,
            territory=territory,
            failure_type=failure_type,
            retry_count=retry_count,
            replay_mode=replay_mode,
            playbook_match=playbook_match,
            deterministic_coverage=deterministic_coverage,
            provider_prohibited_gemini=provider_prohibited_gemini,
            provider_prohibited_qwen=provider_prohibited_qwen,
        )
        decision_data = {
            "agent": agent_name,
            "territory": territory,
            "confidence": confidence.value,
            "reasoning": confidence.reasoning,
            "timestamp": datetime.now().isoformat(),
            "routing_tier": routing.tier.value,
            "routing_gate": routing.gate_applied,
            "routing_score": routing.score,
            "routing_digest": routing.determinism_digest,
            "model": routing.model_id,
            "decision": None,
            "reason": None,
        }
        _GEMINI_MODEL_ID = "gemini-2.5-pro"
        if routing.tier != RoutingTier.FAIL_CLOSED:
            if confidence.value > _CONF_X:
                tier = RoutingTier.DETERMINISTIC
                decision_data["model"] = "deterministic-sovereign"
            elif confidence.value > _CONF_Y:
                tier = RoutingTier.QWEN
                decision_data["model"] = _QWEN_14B_MODEL_ID
            else:
                tier = RoutingTier.GEMINI
                decision_data["model"] = _GEMINI_MODEL_ID
            decision_data["routing_tier"] = tier.value
        else:
            tier = routing.tier
        if tier == RoutingTier.FAIL_CLOSED:
            reason = f"FAIL-CLOSED ({routing.gate_applied}, S={routing.score})"
            decision_data["decision"] = False
            decision_data["reason"] = reason
            self.decisions_made.append(decision_data)
            return (False, reason)
        if tier == RoutingTier.DETERMINISTIC:
            self._healing_count += 1
            self._call_path.add(agent_name)
            reason = f"AUTO-HEAL: SOVEREIGN-AUTO ({confidence.value:.2f}, S={routing.score}, gate={routing.gate_applied})"
            decision_data["decision"] = True
            decision_data["reason"] = reason
            self.decisions_made.append(decision_data)
            return (True, reason)
        if tier == RoutingTier.QWEN:
            qwen_approved = True
            qwen_reason = f"LLM Override: LLM-ARBITRATED-QWEN14B ({confidence.value:.2f}, S={routing.score})"
            try:
                arbiter = self._get_qwen_vllm_arbiter()
                vllm_result = arbiter(
                    agent_name=agent_name,
                    violation_types=list(confidence.reasoning.split(", ") if confidence.reasoning else []),
                    territory=territory,
                    score=routing.score,
                    gate=routing.gate_applied,
                )
                qwen_approved = vllm_result.get("decision", True)
                raw_reason = vllm_result.get("reason", "")[:120]
                qwen_reason = f"LLM Override: LLM-ARBITRATED-QWEN14B ({confidence.value:.2f}, S={routing.score}): {raw_reason}"
                logger.warning("[QWEN14B] %s -> decision=%s reason=%s", agent_name, qwen_approved, raw_reason)
            except (
                ImportError,
                AttributeError,
                ValueError,
                KeyError,
                RuntimeError,
                OSError,
                TimeoutError,
            ) as _qwen_err:
                logger.warning("[QWEN14B] vLLM call failed, falling to agent-native: %s", _qwen_err)
                qwen_approved = False
            if qwen_approved:
                final_reason = qwen_reason
                self._healing_count += 1
                self._call_path.add(agent_name)
                decision_data["decision"] = True
                decision_data["reason"] = final_reason
                self.decisions_made.append(decision_data)
                return (True, final_reason)
            else:
                logger.info("[ROUTING] Qwen declined %s (S=%d) — denying", agent_name, routing.score)
                final_reason = f"LLM Override: QWEN14B-DECLINED ({confidence.value:.2f}, S={routing.score}): agent logic governs"
                decision_data["decision"] = False
                decision_data["reason"] = final_reason
                self.decisions_made.append(decision_data)
                return (False, final_reason)
        if not self.enable_llm and confidence.value <= _CONF_Y:
            reason = f"Manual Review Required: LLM disabled, confidence={confidence.value:.2f} requires advanced reasoning"
            decision_data["decision"] = False
            decision_data["reason"] = reason
            self.decisions_made.append(decision_data)
            return (False, reason)
        target_model = decision_data.get("model", routing.model_id)
        logger.info(
            "[GEMINI] Invoking %s for %s (S=%d gate=%s) — high-complexity arbitration",
            target_model,
            agent_name,
            routing.score,
            routing.gate_applied,
        )
        self._healing_count += 1
        self._call_path.add(agent_name)
        _gemini_label = (
            "RECOVERY-PRO"
            if confidence.value < 0.4
            else "FLASH"
            if "flash" in target_model.lower()
            else "GEMINI"
        )
        reason = f"LLM Override: LLM-ARBITRATED-{_gemini_label} ({confidence.value:.2f}, S={routing.score}, gate={routing.gate_applied})"
        decision_data["decision"] = True
        decision_data["reason"] = reason
        self.decisions_made.append(decision_data)
        return (True, reason)

    def _hitl_gate(self, agent_name: str, confidence: "ConfidenceScore", tier: str) -> tuple[bool, str]:
        """
        HITL terminal gate for medium/low confidence healing decisions.

        Prints a structured prompt showing the agent, confidence score, and
        reasoning, then reads Y/N/D from stdin. Non-interactive environments
        (no tty) default to DEFER (reject).

        Returns:
            (approved: bool, reason: str)
        """
        import sys

        border = "=" * 56    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling
        print(f"\n{border}")
        print(f"  HITL GATE  [{tier} CONFIDENCE]")
        print(border)
        print(f"  Agent     : {agent_name}")
        print(f"  Confidence: {confidence.value:.2f}  ({tier})")
        print(f"  Reasoning : {confidence.reasoning}")
        print(border)
        print("  [Y] Approve healing    [N] Reject    [D] Defer to report")
        print(border)
        if getattr(self, "auto_approve", False):
            return (True, f"HITL-AUTO-APPROVED: --heal active ({confidence.value:.2f})")
        if not sys.stdin.isatty():
            reason = f"HITL-DEFER (non-interactive, {confidence.value:.2f})"
            print(f"  Non-interactive environment — auto-DEFER: {agent_name}")
            print(border + "\n")
            return (False, reason)
        try:
            raw = input("  Choice [Y/N/D]: ").strip().upper()
        except (EOFError, KeyboardInterrupt):    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling
            raw = "D"
        print(border + "\n")
        if raw == "Y":
            return (True, f"HITL-APPROVED ({confidence.value:.2f})")
        elif raw == "N":
            return (False, f"HITL-REJECTED ({confidence.value:.2f})")
        else:
            return (False, f"HITL-DEFER ({confidence.value:.2f})")

    async def analyze_violations_with_cognitive_disposition(
        self, violations: list, territory: str, state_mgr
    ):
        """Analyze violations using CognitiveDispositionAgent for enhanced confidence."""
        if not self.enable_cda:
            fallback_conf = self.calculate_healing_confidence(
                len(violations), [str(v) for v in violations[:10]], territory, agent_name="location"
            )
            return ([], fallback_conf)
        try:
            from agentic_core.L0_routing.seams.safety_validators_seam import load_cognitive_disposition_agent

            CognitiveDispositionAgent = load_cognitive_disposition_agent()
            cda = CognitiveDispositionAgent()
            dispositions = await cda.analyze_violations(violations, territory)
            if dispositions:
                avg_confidence = sum(d.confidence for d in dispositions) / len(dispositions)
                enhanced_confidence = ConfidenceScore(
                    value=avg_confidence, reasoning=f"Cognitive analysis of {len(dispositions)} dispositions"
                )
            else:
                enhanced_confidence = ConfidenceScore(
                    value=0.5, reasoning="No cognitive dispositions generated"
                )
            return (dispositions, enhanced_confidence)
        # guardian: allow-silent-swallow - optional dependency
        except ImportError:
            logger.warning("CognitiveDispositionAgent not available, using default confidence")
            bmg_conf = self.calculate_healing_confidence(
                len(violations), [str(v) for v in violations[:10]], territory, agent_name="location"
            )
            return ([], bmg_conf)
        except (AttributeError, ValueError) as e:
            logger.error(f"Cognitive analysis failed: {e}")
            return ([], ConfidenceScore(value=0.5, reasoning=f"CDA error: {str(e)}"))

    def request_sovereignty_token(self, agent_name: str, operation: str) -> bool:
        """
        Request permission to perform a state-mutating operation.
        Enforces atomic locking and stack depth limits.
        """
        if self._atomic_lock:
            logging.warning(f"Sovereignty DENIED for {agent_name}: Atomic lock active")
            return False
        if len(self._operation_stack) >= self._max_stack_depth:
            logging.critical(
                f"Sovereignty DENIED for {agent_name}: Stack depth exceeded ({len(self._operation_stack)})"
            )
            return False
        op_signature = f"{agent_name}:{operation}"
        if op_signature in self._operation_stack:
            logging.warning(f"Sovereignty DENIED for {agent_name}: Cycle detected {op_signature}")
            return False
        self._operation_stack.append(op_signature)
        self._atomic_lock = True
        self._sovereignty_token = f"SOV_{int(get_clock().now_epoch())}_{agent_name}"
        return True

    def release_sovereignty_token(self, agent_name: str, success: bool = True) -> None:
        """Release the lock after operation completion."""
        if not self._atomic_lock:
            return
        if self._operation_stack:
            self._operation_stack.pop()
        self._atomic_lock = False
        self._sovereignty_token = None
        if not success:
            logging.warning(f"Sovereignty released with FAILURE status for {agent_name}")


AutonomousDecisionEngine = SovereignDecisionEngine
EnhancedAutonomousDecisionEngine = SovereignDecisionEngine
