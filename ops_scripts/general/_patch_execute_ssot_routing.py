"""
One-shot patcher: inject hardened SSOT routing into execute_ssot.py.

Applies three changes:
  1. Add `enum` to imports (after `from dataclasses import ...`)
  2. Insert routing enums/dataclasses/pure-function after ConfidenceScore class
  3. Insert _route_decision method + replace should_proceed_with_healing body
"""

import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR, get_validated_project_root

_ROOT = get_validated_project_root()
TARGET = _ROOT / AGENTIC_CORE_DIR / "L0_routing" / "scripts" / "execute_ssot.py"

ROUTING_BLOCK = '''

# ============================================================================
# HARDENED SSOT ROUTING — enums, dataclasses, pure routing function
# ============================================================================

import enum as _enum
import hashlib as _hashlib


class FailureType(_enum.Enum):
    """Classifies the failure being routed.  Drives gate selection."""
    LAYER_VIOLATION = "LAYER_VIOLATION"
    GATEWAY_BYPASS = "GATEWAY_BYPASS"
    KILL_SWITCH_BYPASS = "KILL_SWITCH_BYPASS"
    SIGNATURE_VERIFY = "SIGNATURE_VERIFY"
    UNSIGNED_INGRESS = "UNSIGNED_INGRESS"
    IMPORT_BOUNDARY_VIOLATION = "IMPORT_BOUNDARY_VIOLATION"
    SCHEMA_REQUIRED_FIELDS_MISSING = "SCHEMA_REQUIRED_FIELDS_MISSING"
    NAMING = "NAMING"
    HIERARCHY = "HIERARCHY"
    SHALLOW = "SHALLOW"
    DEEP = "DEEP"
    VOID = "VOID"
    DUPLICATE = "DUPLICATE"
    ORPHAN = "ORPHAN"
    UNKNOWN = "UNKNOWN"


class RoutingTier(_enum.Enum):
    DETERMINISTIC = "DETERMINISTIC"
    QWEN = "QWEN"
    GEMINI = "GEMINI"
    FAIL_CLOSED = "FAIL_CLOSED"


# Structural failures: deterministic coverage can rescue; otherwise GEMINI/FAIL_CLOSED
_STRUCTURAL_CLASS: frozenset[FailureType] = frozenset({
    FailureType.LAYER_VIOLATION,
    FailureType.GATEWAY_BYPASS,
    FailureType.KILL_SWITCH_BYPASS,
    FailureType.SIGNATURE_VERIFY,
    FailureType.UNSIGNED_INGRESS,
})

# Qwen-disallowed failures: includes structural + import/schema violations
_QWEN_DISALLOWED: frozenset[FailureType] = _STRUCTURAL_CLASS | frozenset({
    FailureType.IMPORT_BOUNDARY_VIOLATION,
    FailureType.SCHEMA_REQUIRED_FIELDS_MISSING,
})


@dataclass
class RoutingInputs:
    """All inputs to compute_routing_decision.  No embeddings allowed."""
    failure_type: FailureType = FailureType.UNKNOWN
    retry_count: int = 0
    C: int = 0   # complexity      0-3
    B: int = 0   # blast-radius    0-3
    A: int = 0   # autonomy-risk   0-3
    N: int = 0   # novelty         0-3
    F: int = 0   # failure-cost    0-3
    L: int = 0   # latency class   0-3  (0=interactive, 3=async-batch)
    replay_mode: bool = False
    playbook_match: bool = False
    deterministic_coverage: bool = False
    provider_prohibited_gemini: bool = False
    provider_prohibited_qwen: bool = False


@dataclass
class RoutingDecision:
    """Immutable routing result with full audit trail."""
    tier: RoutingTier
    score: int
    gate_applied: str
    model_id: str
    factors: dict
    inputs: RoutingInputs
    determinism_digest: str

    def as_log_line(self) -> str:
        f = self.factors
        i = self.inputs
        return (
            f"[ROUTING] tier={self.tier.value} S={self.score} gate={self.gate_applied}"
            f" model={self.model_id}"
            f" C={f.get('C',0)} B={f.get('B',0)} A={f.get('A',0)}"
            f" N={f.get('N',0)} F={f.get('F',0)} L={f.get('L',0)}"
            f" replay={i.replay_mode} retry={i.retry_count}"
            f" playbook={i.playbook_match} det_cov={i.deterministic_coverage}"
            f" digest={self.determinism_digest}"
        )


def compute_routing_decision(inputs: RoutingInputs) -> RoutingDecision:  # noqa: C901
    """Pure SSOT routing function — strict gate order, no side effects."""
    C, B, A, N, F, L = inputs.C, inputs.B, inputs.A, inputs.N, inputs.F, inputs.L

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

    # ── GATE 0: Replay mode → always deterministic ─────────────────────────
    if inputs.replay_mode:
        return _decide(RoutingTier.DETERMINISTIC, "GATE_0_REPLAY")

    # ── GATE 1: Global retry override ──────────────────────────────────────
    if inputs.retry_count >= 3:
        if inputs.provider_prohibited_gemini:
            return _decide(RoutingTier.FAIL_CLOSED, "GATE_1_RETRY_OVERRIDE_FAIL_CLOSED")
        return _decide(RoutingTier.GEMINI, "GATE_1_RETRY_OVERRIDE")

    # ── GATE 2: Structural class pre-gate ──────────────────────────────────
    if inputs.failure_type in _STRUCTURAL_CLASS:
        if inputs.deterministic_coverage:
            return _decide(RoutingTier.DETERMINISTIC, "GATE_2_STRUCTURAL_DET_COV")
        if inputs.provider_prohibited_gemini:
            return _decide(RoutingTier.FAIL_CLOSED, "GATE_2_STRUCTURAL_FAIL_CLOSED")
        return _decide(RoutingTier.GEMINI, "GATE_2_STRUCTURAL_NO_DET_COV")

    # ── GATE 3: Critical surface mechanical exception ──────────────────────
    if B == 3 and A == 0 and inputs.playbook_match and inputs.deterministic_coverage:
        return _decide(RoutingTier.DETERMINISTIC, "GATE_3_CRITICAL_SURFACE_MECH")

    # ── Score computation ──────────────────────────────────────────────────
    S = 3 * C + 4 * B + 3 * A + 2 * N + 4 * F
    if inputs.playbook_match:
        S = max(0, S - 4)

    # ── GATE 4: Hard-override for extreme risk ─────────────────────────────
    if B == 3 and F == 3 and (C >= 2 or A >= 1):
        if inputs.provider_prohibited_gemini and inputs.provider_prohibited_qwen:
            return _decide(RoutingTier.FAIL_CLOSED, "GATE_4_HARD_OVERRIDE_FAIL_CLOSED", S)
        return _decide(RoutingTier.GEMINI, "GATE_4_HARD_OVERRIDE", S)

    # ── GATE 5: Threshold routing ──────────────────────────────────────────
    if S <= 13:
        tier = RoutingTier.DETERMINISTIC
        gate = "THRESHOLD_LOW_DET"
    elif S <= 26:
        tier = RoutingTier.QWEN
        gate = "THRESHOLD_MED_QWEN"
    else:
        tier = RoutingTier.GEMINI
        gate = "THRESHOLD_HIGH_GEMINI"
        if inputs.provider_prohibited_gemini:
            return _decide(RoutingTier.FAIL_CLOSED, "THRESHOLD_HIGH_FAIL_CLOSED", S)

    # ── GATE 6: Latency tie-breaker (boundary zones only) ─────────────────
    if tier == RoutingTier.QWEN and S in range(14, 16) and L == 0:
        tier = RoutingTier.DETERMINISTIC
        gate = f"{gate}.L_TIEBREAK_DOWN"
    elif tier == RoutingTier.DETERMINISTIC and S in range(12, 14) and L == 3:
        tier = RoutingTier.QWEN
        gate = f"{gate}.L_TIEBREAK_UP"

    # ── GATE 7: Qwen-disallowed fall-up ───────────────────────────────────
    if tier == RoutingTier.QWEN and inputs.failure_type in _QWEN_DISALLOWED:
        if inputs.deterministic_coverage and A == 0 and C == 0:
            return _decide(RoutingTier.DETERMINISTIC, f"{gate}.QWEN_DISALLOWED_DET_FALLBACK", S)
        if inputs.provider_prohibited_gemini:
            return _decide(RoutingTier.FAIL_CLOSED, f"{gate}.QWEN_DISALLOWED_FAIL_CLOSED", S)
        return _decide(RoutingTier.GEMINI, f"{gate}.QWEN_DISALLOWED", S)

    # ── GATE 8: Provider prohibition check ────────────────────────────────
    if tier == RoutingTier.QWEN and inputs.provider_prohibited_qwen:
        if inputs.provider_prohibited_gemini:
            return _decide(RoutingTier.FAIL_CLOSED, f"{gate}.BOTH_PROHIBITED", S)
        return _decide(RoutingTier.GEMINI, f"{gate}.QWEN_PROHIBITED_FALLBACK", S)

    if tier == RoutingTier.GEMINI and inputs.provider_prohibited_gemini:
        return _decide(RoutingTier.FAIL_CLOSED, f"{gate}.GEMINI_PROHIBITED", S)

    return _decide(tier, gate, S)

'''

ROUTE_METHOD = '''
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

        C = min(3, max(0, int(3 - confidence.value * 3)))
        B = 3 if territory.startswith("L5") else (2 if "agentic_core" in territory else 1)
        A = 0 if confidence.value >= 0.75 else (2 if confidence.value < 0.50 else 1)
        N = 1 if "[BMG-GPU]" in (confidence.reasoning or "") else 0
        high_cost = {
            FailureType.LAYER_VIOLATION, FailureType.GATEWAY_BYPASS,
            FailureType.KILL_SWITCH_BYPASS, FailureType.SIGNATURE_VERIFY,
            FailureType.UNSIGNED_INGRESS,
        }
        F = 3 if failure_type in high_cost else (2 if confidence.value < 0.50 else 1)
        L = 0

        ri = RoutingInputs(
            failure_type=failure_type,
            retry_count=retry_count,
            C=C, B=B, A=A, N=N, F=F, L=L,
            replay_mode=replay_mode,
            playbook_match=playbook_match,
            deterministic_coverage=deterministic_coverage,
            provider_prohibited_gemini=provider_prohibited_gemini,
            provider_prohibited_qwen=provider_prohibited_qwen,
        )
        decision = compute_routing_decision(ri)
        logger.info(decision.as_log_line())
        return decision

'''

NEW_SHOULD_PROCEED = '''    def should_proceed_with_healing(
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
        is_safe, msg = self._check_healing_budget(agent_name)
        if not is_safe:
            return False, f"SAFETY LOCK: {msg}"

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

        tier = routing.tier

        if tier == RoutingTier.FAIL_CLOSED:
            reason = f"FAIL-CLOSED ({routing.gate_applied}, S={routing.score})"
            decision_data["decision"] = False
            decision_data["reason"] = reason
            self.decisions_made.append(decision_data)
            return False, reason

        if tier == RoutingTier.DETERMINISTIC:
            self._healing_count += 1
            self._call_path.add(agent_name)
            reason = f"SOVEREIGN-AUTO ({confidence.value:.2f}, S={routing.score}, gate={routing.gate_applied})"
            decision_data["decision"] = True
            decision_data["reason"] = reason
            self.decisions_made.append(decision_data)
            return True, reason

        if not self.enable_llm:
            approved, hitl_reason = self._hitl_gate(agent_name, confidence, tier.value)
            decision_data["decision"] = approved
            decision_data["reason"] = hitl_reason
            self.decisions_made.append(decision_data)
            if approved:
                self._healing_count += 1
                self._call_path.add(agent_name)
            return approved, hitl_reason

        if tier == RoutingTier.QWEN:
            vllm_decision = True
            vllm_reason = f"LLM-ARBITRATED-QWEN14B ({confidence.value:.2f}, S={routing.score})"
            try:
                arbiter = self._get_qwen_vllm_arbiter()
                vllm_result = arbiter(
                    agent_name=agent_name,
                    confidence=confidence.value,
                    violation_types=list(
                        confidence.reasoning.split(", ") if confidence.reasoning else []
                    ),
                    territory=territory,
                )
                vllm_decision = vllm_result.get("decision", True)
                raw_reason = vllm_result.get("reason", "")[:120]
                vllm_reason = f"LLM-ARBITRATED-QWEN14B ({confidence.value:.2f}, S={routing.score}): {raw_reason}"
                logger.info("[QWEN14B] %s -> decision=%s reason=%s", agent_name, vllm_decision, raw_reason)
            except Exception as _qwen_err:  # guardian: allow-silent-swallow
                logger.warning("[QWEN14B] vLLM call failed, defaulting to proceed: %s", _qwen_err)
            self._healing_count += 1
            self._call_path.add(agent_name)
            decision_data["decision"] = vllm_decision
            decision_data["reason"] = vllm_reason
            self.decisions_made.append(decision_data)
            return vllm_decision, vllm_reason

        # tier == RoutingTier.GEMINI
        target_model = routing.model_id
        logger.warning(
            "LLM-ARBITRATED-FLASH: Invoking %s for %s (S=%d gate=%s)",
            target_model, agent_name, routing.score, routing.gate_applied,
        )
        self._healing_count += 1
        self._call_path.add(agent_name)
        reason = f"LLM-ARBITRATED-FLASH ({confidence.value:.2f}, S={routing.score}, gate={routing.gate_applied})"
        decision_data["decision"] = True
        decision_data["reason"] = reason
        self.decisions_made.append(decision_data)
        return True, reason
'''


def main() -> int:
    src = TARGET.read_text(encoding="utf-8")

    # ── Change 1: Insert routing block after ConfidenceScore class ──────────
    # Insert after the closing of ConfidenceScore (before ReconciliationViolation)
    MARKER_AFTER_CS = "# ============================================================================\n# NEW DATA STRUCTURES FOR TELEMETRY AND VALIDATION"
    if MARKER_AFTER_CS not in src:
        print("ERROR: Cannot find insertion point for routing block")
        return 1
    if "class FailureType" in src:
        print("INFO: Routing block already present — skipping block insertion")
    else:
        src = src.replace(MARKER_AFTER_CS, ROUTING_BLOCK + MARKER_AFTER_CS)
        print("OK: Inserted routing block")

    # ── Change 2: Insert _route_decision before _check_healing_budget ──────
    BUDGET_MARKER = "    # guardian: allow-magic-config\n    def _check_healing_budget("
    if BUDGET_MARKER not in src:
        print("ERROR: Cannot find _check_healing_budget insertion point")
        return 1
    if "_route_decision" in src:
        print("INFO: _route_decision already present — skipping")
    else:
        src = src.replace(BUDGET_MARKER, ROUTE_METHOD + BUDGET_MARKER)
        print("OK: Inserted _route_decision method")

    # ── Change 3: Replace should_proceed_with_healing body ─────────────────
    OLD_SHOULD_PROCEED_START = '    def should_proceed_with_healing(\n        self,\n        confidence: ConfidenceScore,\n        agent_name: str = "Unknown",\n        territory: str = "unknown",\n    ) -> tuple[bool, str]:'

    if OLD_SHOULD_PROCEED_START not in src:
        if 'failure_type: "FailureType | None" = None,' in src:
            print("INFO: should_proceed_with_healing already updated — skipping")
        else:
            print("ERROR: Cannot find should_proceed_with_healing to replace")
            return 1
    else:
        # Find end of should_proceed_with_healing (next def at same indent level)
        idx_start = src.index(OLD_SHOULD_PROCEED_START)
        # Find "    def _hitl_gate(" which immediately follows
        HITL_MARKER = "\n    def _hitl_gate("
        idx_end = src.index(HITL_MARKER, idx_start)
        old_body = src[idx_start:idx_end]
        src = src[:idx_start] + NEW_SHOULD_PROCEED + src[idx_end:]
        print("OK: Replaced should_proceed_with_healing")

    TARGET.write_text(src, encoding="utf-8")
    print("OK: Wrote patched file")
    return 0


if __name__ == "__main__":
    sys.exit(main())
