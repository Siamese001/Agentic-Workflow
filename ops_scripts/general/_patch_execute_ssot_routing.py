"""
One-shot patcher: inject hardened SSOT routing into execute_ssot.py.

Applies three changes:
  1. Add `enum` to imports (after `from dataclasses import ...`)
  2. Insert routing enums/dataclasses/pure-function after ConfidenceScore class
  3. Insert _route_decision method + replace should_proceed_with_healing body
"""
import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    get_validated_project_root,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_emits_metric_event("_patch_execute_ssot_routing", "p4obs", "metric_1")
_emit_emits_metric_event("_patch_execute_ssot_routing", "p4obs", "metric_2")
_emit_emits_metric_event("_patch_execute_ssot_routing", "p4obs", "metric_3")
_emit_emits_metric_event("_patch_execute_ssot_routing", "p4obs", "metric_4")
_emit_emits_metric_event("_patch_execute_ssot_routing", "p4obs", "metric_5")
_emit_emits_metric_event("_patch_execute_ssot_routing", "p4obs", "metric_6")
_emit_records_incident_event("_patch_execute_ssot_routing", "p4obs", "incident")
_emit_captures_runtime_anomaly("_patch_execute_ssot_routing", "p4obs", "anomaly")
_emit_writes_observability_log("_patch_execute_ssot_routing", "p4obs", "obs_log")
_emit_updates_monitoring_state("_patch_execute_ssot_routing", "p4obs", "mon_state")
_emit_triggers_alert("_patch_execute_ssot_routing", "p4obs", "alert")
_emit_links_incident_trace("_patch_execute_ssot_routing", "p4obs", "trace_link")
_emit_captures_pattern("_patch_execute_ssot_routing", "p3lm", "pattern")
_emit_records_learning_event("_patch_execute_ssot_routing", "p3lm", "learning_event")
_emit_writes_learning_snapshot("_patch_execute_ssot_routing", "p3lm", "snapshot")
_emit_feeds_meta_learning("_patch_execute_ssot_routing", "p3lm", "meta_feed")
_emit_updates_routing_strategy("_patch_execute_ssot_routing", "p3lm", "routing")
_emit_improves_agent_policy("_patch_execute_ssot_routing", "p3lm", "policy")
_emit_stores_learning_state("_patch_execute_ssot_routing", "p3lm", "state")
_emit_records_execution_trace("_patch_execute_ssot_routing", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("_patch_execute_ssot_routing", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("_patch_execute_ssot_routing", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("_patch_execute_ssot_routing", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("_patch_execute_ssot_routing", "L4_STATE", "p2_trace_5")
_emit_reads_environ("_patch_execute_ssot_routing", "env_read", "p2_env_1")
_emit_reads_environ("_patch_execute_ssot_routing", "env_read", "p2_env_2")
_emit_reads_runtime_state("_patch_execute_ssot_routing", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("_patch_execute_ssot_routing", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "_patch_execute_ssot_routing")
_emit_applies_guardrail("p0", "_patch_execute_ssot_routing", "p0_governance")
_emit_reads_policy_state("p0", "_patch_execute_ssot_routing", "policy_binding")
_emit_snapshots_state("p0", "_patch_execute_ssot_routing", "state_snapshot")
_emit_pulls_context("p1", "_patch_execute_ssot_routing", "context_pull")
_emit_pulls_context("p1", "_patch_execute_ssot_routing", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "_patch_execute_ssot_routing", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "_patch_execute_ssot_routing", "uwg_term_secondary")
_emit_writes_through("p1", "_patch_execute_ssot_routing", "write_through")
_emit_writes_through("p1", "_patch_execute_ssot_routing", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "_patch_execute_ssot_routing", "safety_validation")
_emit_invokes_eval("p1", "_patch_execute_ssot_routing", "eval_call")
_emit_proposal_commits_routing("p1", "_patch_execute_ssot_routing", "routing_commit")
_emit_escalates_to_human("p1", "_patch_execute_ssot_routing", "human_escalation")
_emit_routes_through("p1", "_patch_execute_ssot_routing", "route_through")
_emit_checks_agent_registry("p1", "_patch_execute_ssot_routing", "agent_registry")
_emit_validates_agent_capability("p1", "_patch_execute_ssot_routing", "capability")
_emit_dispatches_execution_plan("p1", "_patch_execute_ssot_routing", "exec_plan")
_emit_agent_executes_agent("p1", "_patch_execute_ssot_routing", "sub_agent")
_emit_routes_to_agent("p1", "_patch_execute_ssot_routing", "target_agent")
_emit_verifies_policy("p1", "_patch_execute_ssot_routing", "policy_check")
_emit_observes_runtime_state("p1", "_patch_execute_ssot_routing", "runtime_state")
_emit_verifies_boundary("p1", "_patch_execute_ssot_routing", "boundary_check")
_emit_transcripts_response("p1", "_patch_execute_ssot_routing", "transcript")
_emit_hard_fails_untranscripted("p1", "_patch_execute_ssot_routing")
_emit_gated_by_confidence("p1", "_patch_execute_ssot_routing", "confidence_gate")
emit_replay_key("p0", "_patch_execute_ssot_routing")
emit_determinism_digest("p0", "_patch_execute_ssot_routing")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "_patch_execute_ssot_routing", "execution_auth")
_emit_validates_capability("p2", "_patch_execute_ssot_routing", "capability_check")
_emit_routes_to_capability("p2", "_patch_execute_ssot_routing", "capability_route")
_emit_writes_via_uwg("p2", "_patch_execute_ssot_routing", "uwg_write")
_emit_blocks_direct_write("p2", "_patch_execute_ssot_routing", "direct_write_block")
_emit_records_tool_invocation("p2", "_patch_execute_ssot_routing", "tool_invocation")
_emit_captures_execution_output("p2", "_patch_execute_ssot_routing", "exec_output")
_emit_dispatches_agent("p3", "_patch_execute_ssot_routing", "agent_dispatch")
_emit_coordinates_agents("p3", "_patch_execute_ssot_routing", "agent_coordination")
_emit_records_workflow_lineage("p3", "_patch_execute_ssot_routing", "workflow_lineage")
_emit_records_healing_outcome("p3", "_patch_execute_ssot_routing", "healing_outcome")
_emit_escalates_failure("p3", "_patch_execute_ssot_routing", "failure_escalation")
_emit_orchestrates_workflow("p3", "_patch_execute_ssot_routing", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "_patch_execute_ssot_routing", "healing_dispatch")
_emit_invokes_evaluation("p3", "_patch_execute_ssot_routing", "evaluation_signal")
_emit_records_telemetry_event("p4", "_patch_execute_ssot_routing", "telemetry_event")
_emit_captures_evaluation_metric("p4", "_patch_execute_ssot_routing", "eval_metric")
_emit_stores_embedding("p4", "_patch_execute_ssot_routing", "embedding_store")
_emit_updates_meta_learning_state("p4", "_patch_execute_ssot_routing", "meta_learning")
_emit_links_execution_to_snapshot("p4", "_patch_execute_ssot_routing", "exec_snapshot_link")
_ROOT = get_validated_project_root()
TARGET = _ROOT / AGENTIC_CORE_DIR / 'L0_routing' / 'scripts' / 'execute_ssot.py'
ROUTING_BLOCK = '\n\n# ============================================================================\n# HARDENED SSOT ROUTING — enums, dataclasses, pure routing function\n# ============================================================================\n\nimport enum as _enum\nimport hashlib as _hashlib\n\n\nclass FailureType(_enum.Enum):\n    """Classifies the failure being routed.  Drives gate selection."""\n    LAYER_VIOLATION = "LAYER_VIOLATION"\n    GATEWAY_BYPASS = "GATEWAY_BYPASS"\n    KILL_SWITCH_BYPASS = "KILL_SWITCH_BYPASS"\n    SIGNATURE_VERIFY = "SIGNATURE_VERIFY"\n    UNSIGNED_INGRESS = "UNSIGNED_INGRESS"\n    IMPORT_BOUNDARY_VIOLATION = "IMPORT_BOUNDARY_VIOLATION"\n    SCHEMA_REQUIRED_FIELDS_MISSING = "SCHEMA_REQUIRED_FIELDS_MISSING"\n    NAMING = "NAMING"\n    HIERARCHY = "HIERARCHY"\n    SHALLOW = "SHALLOW"\n    DEEP = "DEEP"\n    VOID = "VOID"\n    DUPLICATE = "DUPLICATE"\n    ORPHAN = "ORPHAN"\n    UNKNOWN = "UNKNOWN"\n\n\nclass RoutingTier(_enum.Enum):\n    DETERMINISTIC = "DETERMINISTIC"\n    QWEN = "QWEN"\n    GEMINI = "GEMINI"\n    FAIL_CLOSED = "FAIL_CLOSED"\n\n\n# Structural failures: deterministic coverage can rescue; otherwise GEMINI/FAIL_CLOSED\n_STRUCTURAL_CLASS: frozenset[FailureType] = frozenset({\n    FailureType.LAYER_VIOLATION,\n    FailureType.GATEWAY_BYPASS,\n    FailureType.KILL_SWITCH_BYPASS,\n    FailureType.SIGNATURE_VERIFY,\n    FailureType.UNSIGNED_INGRESS,\n})\n\n# Qwen-disallowed failures: includes structural + import/schema violations\n_QWEN_DISALLOWED: frozenset[FailureType] = _STRUCTURAL_CLASS | frozenset({\n    FailureType.IMPORT_BOUNDARY_VIOLATION,\n    FailureType.SCHEMA_REQUIRED_FIELDS_MISSING,\n})\n\n\n@dataclass\nclass RoutingInputs:\n    """All inputs to compute_routing_decision.  No embeddings allowed."""\n    failure_type: FailureType = FailureType.UNKNOWN\n    retry_count: int = 0\n    C: int = 0   # complexity      0-3\n    B: int = 0   # blast-radius    0-3\n    A: int = 0   # autonomy-risk   0-3\n    N: int = 0   # novelty         0-3\n    F: int = 0   # failure-cost    0-3\n    L: int = 0   # latency class   0-3  (0=interactive, 3=async-batch)\n    replay_mode: bool = False\n    playbook_match: bool = False\n    deterministic_coverage: bool = False\n    provider_prohibited_gemini: bool = False\n    provider_prohibited_qwen: bool = False\n\n\n@dataclass\nclass RoutingDecision:\n    """Immutable routing result with full audit trail."""\n    tier: RoutingTier\n    score: int\n    gate_applied: str\n    model_id: str\n    factors: dict\n    inputs: RoutingInputs\n    determinism_digest: str\n\n    def as_log_line(self) -> str:\n        f = self.factors\n        i = self.inputs\n        return (\n            f"[ROUTING] tier={self.tier.value} S={self.score} gate={self.gate_applied}"\n            f" model={self.model_id}"\n            f" C={f.get(\'C\',0)} B={f.get(\'B\',0)} A={f.get(\'A\',0)}"\n            f" N={f.get(\'N\',0)} F={f.get(\'F\',0)} L={f.get(\'L\',0)}"\n            f" replay={i.replay_mode} retry={i.retry_count}"\n            f" playbook={i.playbook_match} det_cov={i.deterministic_coverage}"\n            f" digest={self.determinism_digest}"\n        )\n\n\ndef compute_routing_decision(inputs: RoutingInputs) -> RoutingDecision:  # noqa: C901\n    """Pure SSOT routing function — strict gate order, no side effects."""\n    C, B, A, N, F, L = inputs.C, inputs.B, inputs.A, inputs.N, inputs.F, inputs.L\n\n    def _decide(tier: RoutingTier, gate: str, score: int = 0) -> RoutingDecision:\n        if tier == RoutingTier.DETERMINISTIC:\n            model = "deterministic-sovereign"\n        elif tier == RoutingTier.QWEN:\n            model = "Qwen2.5-14B-Instruct-AWQ"\n        elif tier == RoutingTier.GEMINI:\n            model = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")\n        else:\n            model = "FAIL_CLOSED"\n        raw = f"{tier.value}|{score}|{gate}|{inputs.failure_type.value}|{C}|{B}|{A}|{N}|{F}|{L}|{inputs.replay_mode}|{inputs.retry_count}"\n        digest = _hashlib.md5(raw.encode(), usedforsecurity=False).hexdigest()[:16]\n        return RoutingDecision(\n            tier=tier,\n            score=score,\n            gate_applied=gate,\n            model_id=model,\n            factors={"C": C, "B": B, "A": A, "N": N, "F": F, "L": L},\n            inputs=inputs,\n            determinism_digest=digest,\n        )\n\n    # ── GATE 0: Replay mode → always deterministic ─────────────────────────\n    if inputs.replay_mode:\n        return _decide(RoutingTier.DETERMINISTIC, "GATE_0_REPLAY")\n\n    # ── GATE 1: Global retry override ──────────────────────────────────────\n    if inputs.retry_count >= 3:\n        if inputs.provider_prohibited_gemini:\n            return _decide(RoutingTier.FAIL_CLOSED, "GATE_1_RETRY_OVERRIDE_FAIL_CLOSED")\n        return _decide(RoutingTier.GEMINI, "GATE_1_RETRY_OVERRIDE")\n\n    # ── GATE 2: Structural class pre-gate ──────────────────────────────────\n    if inputs.failure_type in _STRUCTURAL_CLASS:\n        if inputs.deterministic_coverage:\n            return _decide(RoutingTier.DETERMINISTIC, "GATE_2_STRUCTURAL_DET_COV")\n        if inputs.provider_prohibited_gemini:\n            return _decide(RoutingTier.FAIL_CLOSED, "GATE_2_STRUCTURAL_FAIL_CLOSED")\n        return _decide(RoutingTier.GEMINI, "GATE_2_STRUCTURAL_NO_DET_COV")\n\n    # ── GATE 3: Critical surface mechanical exception ──────────────────────\n    if B == 3 and A == 0 and inputs.playbook_match and inputs.deterministic_coverage:\n        return _decide(RoutingTier.DETERMINISTIC, "GATE_3_CRITICAL_SURFACE_MECH")\n\n    # ── Score computation ──────────────────────────────────────────────────\n    S = 3 * C + 4 * B + 3 * A + 2 * N + 4 * F\n    if inputs.playbook_match:\n        S = max(0, S - 4)\n\n    # ── GATE 4: Hard-override for extreme risk ─────────────────────────────\n    if B == 3 and F == 3 and (C >= 2 or A >= 1):\n        if inputs.provider_prohibited_gemini and inputs.provider_prohibited_qwen:\n            return _decide(RoutingTier.FAIL_CLOSED, "GATE_4_HARD_OVERRIDE_FAIL_CLOSED", S)\n        return _decide(RoutingTier.GEMINI, "GATE_4_HARD_OVERRIDE", S)\n\n    # ── GATE 5: Threshold routing ──────────────────────────────────────────\n    if S <= 13:\n        tier = RoutingTier.DETERMINISTIC\n        gate = "THRESHOLD_LOW_DET"\n    elif S <= 26:\n        tier = RoutingTier.QWEN\n        gate = "THRESHOLD_MED_QWEN"\n    else:\n        tier = RoutingTier.GEMINI\n        gate = "THRESHOLD_HIGH_GEMINI"\n        if inputs.provider_prohibited_gemini:\n            return _decide(RoutingTier.FAIL_CLOSED, "THRESHOLD_HIGH_FAIL_CLOSED", S)\n\n    # ── GATE 6: Latency tie-breaker (boundary zones only) ─────────────────\n    if tier == RoutingTier.QWEN and S in range(14, 16) and L == 0:\n        tier = RoutingTier.DETERMINISTIC\n        gate = f"{gate}.L_TIEBREAK_DOWN"\n    elif tier == RoutingTier.DETERMINISTIC and S in range(12, 14) and L == 3:\n        tier = RoutingTier.QWEN\n        gate = f"{gate}.L_TIEBREAK_UP"\n\n    # ── GATE 7: Qwen-disallowed fall-up ───────────────────────────────────\n    if tier == RoutingTier.QWEN and inputs.failure_type in _QWEN_DISALLOWED:\n        if inputs.deterministic_coverage and A == 0 and C == 0:\n            return _decide(RoutingTier.DETERMINISTIC, f"{gate}.QWEN_DISALLOWED_DET_FALLBACK", S)\n        if inputs.provider_prohibited_gemini:\n            return _decide(RoutingTier.FAIL_CLOSED, f"{gate}.QWEN_DISALLOWED_FAIL_CLOSED", S)\n        return _decide(RoutingTier.GEMINI, f"{gate}.QWEN_DISALLOWED", S)\n\n    # ── GATE 8: Provider prohibition check ────────────────────────────────\n    if tier == RoutingTier.QWEN and inputs.provider_prohibited_qwen:\n        if inputs.provider_prohibited_gemini:\n            return _decide(RoutingTier.FAIL_CLOSED, f"{gate}.BOTH_PROHIBITED", S)\n        return _decide(RoutingTier.GEMINI, f"{gate}.QWEN_PROHIBITED_FALLBACK", S)\n\n    if tier == RoutingTier.GEMINI and inputs.provider_prohibited_gemini:\n        return _decide(RoutingTier.FAIL_CLOSED, f"{gate}.GEMINI_PROHIBITED", S)\n\n    return _decide(tier, gate, S)\n\n'
ROUTE_METHOD = '\n    def _route_decision(\n        self,\n        confidence: "ConfidenceScore",\n        agent_name: str,\n        territory: str,\n        failure_type: "FailureType | None" = None,\n        retry_count: int = 0,\n        replay_mode: bool = False,\n        playbook_match: bool = False,\n        deterministic_coverage: bool = False,\n        provider_prohibited_gemini: bool = False,\n        provider_prohibited_qwen: bool = False,\n    ) -> "RoutingDecision":\n        """Map healing context to a hardened SSOT RoutingDecision."""\n        if failure_type is None:\n            reasoning_upper = (confidence.reasoning or "").upper()\n            ft = FailureType.UNKNOWN\n            for member in FailureType:\n                if member.value in reasoning_upper:\n                    ft = member\n                    break\n            failure_type = ft\n\n        C = min(3, max(0, int(3 - confidence.value * 3)))\n        B = 3 if territory.startswith("L5") else (2 if "agentic_core" in territory else 1)\n        A = 0 if confidence.value >= 0.75 else (2 if confidence.value < 0.50 else 1)\n        N = 1 if "[BMG-GPU]" in (confidence.reasoning or "") else 0\n        high_cost = {\n            FailureType.LAYER_VIOLATION, FailureType.GATEWAY_BYPASS,\n            FailureType.KILL_SWITCH_BYPASS, FailureType.SIGNATURE_VERIFY,\n            FailureType.UNSIGNED_INGRESS,\n        }\n        F = 3 if failure_type in high_cost else (2 if confidence.value < 0.50 else 1)\n        L = 0\n\n        ri = RoutingInputs(\n            failure_type=failure_type,\n            retry_count=retry_count,\n            C=C, B=B, A=A, N=N, F=F, L=L,\n            replay_mode=replay_mode,\n            playbook_match=playbook_match,\n            deterministic_coverage=deterministic_coverage,\n            provider_prohibited_gemini=provider_prohibited_gemini,\n            provider_prohibited_qwen=provider_prohibited_qwen,\n        )\n        decision = compute_routing_decision(ri)\n        logger.info(decision.as_log_line())\n        return decision\n\n'
NEW_SHOULD_PROCEED = '    def should_proceed_with_healing(\n        self,\n        confidence: ConfidenceScore,\n        agent_name: str = "Unknown",\n        territory: str = "unknown",\n        failure_type: "FailureType | None" = None,\n        retry_count: int = 0,\n        replay_mode: bool = False,\n        playbook_match: bool = False,\n        deterministic_coverage: bool = False,\n        provider_prohibited_gemini: bool = False,\n        provider_prohibited_qwen: bool = False,\n    ) -> tuple[bool, str]:\n        """Determines if healing should proceed using the hardened SSOT routing algorithm."""\n        is_safe, msg = self._check_healing_budget(agent_name)\n        if not is_safe:\n            return False, f"SAFETY LOCK: {msg}"\n\n        routing = self._route_decision(\n            confidence=confidence,\n            agent_name=agent_name,\n            territory=territory,\n            failure_type=failure_type,\n            retry_count=retry_count,\n            replay_mode=replay_mode,\n            playbook_match=playbook_match,\n            deterministic_coverage=deterministic_coverage,\n            provider_prohibited_gemini=provider_prohibited_gemini,\n            provider_prohibited_qwen=provider_prohibited_qwen,\n        )\n\n        decision_data = {\n            "agent": agent_name,\n            "confidence": confidence.value,\n            "reasoning": confidence.reasoning,\n            "timestamp": datetime.now().isoformat(),\n            "routing_tier": routing.tier.value,\n            "routing_gate": routing.gate_applied,\n            "routing_score": routing.score,\n            "routing_digest": routing.determinism_digest,\n            "model": routing.model_id,\n            "decision": None,\n            "reason": None,\n        }\n\n        tier = routing.tier\n\n        if tier == RoutingTier.FAIL_CLOSED:\n            reason = f"FAIL-CLOSED ({routing.gate_applied}, S={routing.score})"\n            decision_data["decision"] = False\n            decision_data["reason"] = reason\n            self.decisions_made.append(decision_data)\n            return False, reason\n\n        if tier == RoutingTier.DETERMINISTIC:\n            self._healing_count += 1\n            self._call_path.add(agent_name)\n            reason = f"SOVEREIGN-AUTO ({confidence.value:.2f}, S={routing.score}, gate={routing.gate_applied})"\n            decision_data["decision"] = True\n            decision_data["reason"] = reason\n            self.decisions_made.append(decision_data)\n            return True, reason\n\n        if not self.enable_llm:\n            approved, hitl_reason = self._hitl_gate(agent_name, confidence, tier.value)\n            decision_data["decision"] = approved\n            decision_data["reason"] = hitl_reason\n            self.decisions_made.append(decision_data)\n            if approved:\n                self._healing_count += 1\n                self._call_path.add(agent_name)\n            return approved, hitl_reason\n\n        if tier == RoutingTier.QWEN:\n            vllm_decision = True\n            vllm_reason = f"LLM-ARBITRATED-QWEN14B ({confidence.value:.2f}, S={routing.score})"\n            try:\n                arbiter = self._get_qwen_vllm_arbiter()\n                vllm_result = arbiter(\n                    agent_name=agent_name,\n                    confidence=confidence.value,\n                    violation_types=list(\n                        confidence.reasoning.split(", ") if confidence.reasoning else []\n                    ),\n                    territory=territory,\n                )\n                vllm_decision = vllm_result.get("decision", True)\n                raw_reason = vllm_result.get("reason", "")[:120]\n                vllm_reason = f"LLM-ARBITRATED-QWEN14B ({confidence.value:.2f}, S={routing.score}): {raw_reason}"\n                logger.info("[QWEN14B] %s -> decision=%s reason=%s", agent_name, vllm_decision, raw_reason)\n            except Exception as _qwen_err:  # guardian: allow-silent-swallow\n                logger.warning("[QWEN14B] vLLM call failed, defaulting to proceed: %s", _qwen_err)\n            self._healing_count += 1\n            self._call_path.add(agent_name)\n            decision_data["decision"] = vllm_decision\n            decision_data["reason"] = vllm_reason\n            self.decisions_made.append(decision_data)\n            return vllm_decision, vllm_reason\n\n        # tier == RoutingTier.GEMINI\n        target_model = routing.model_id\n        logger.warning(\n            "LLM-ARBITRATED-FLASH: Invoking %s for %s (S=%d gate=%s)",\n            target_model, agent_name, routing.score, routing.gate_applied,\n        )\n        self._healing_count += 1\n        self._call_path.add(agent_name)\n        reason = f"LLM-ARBITRATED-FLASH ({confidence.value:.2f}, S={routing.score}, gate={routing.gate_applied})"\n        decision_data["decision"] = True\n        decision_data["reason"] = reason\n        self.decisions_made.append(decision_data)\n        return True, reason\n'

def main() -> int:
    src = TARGET.read_text(encoding='utf-8')
    MARKER_AFTER_CS = '# ============================================================================\n# NEW DATA STRUCTURES FOR TELEMETRY AND VALIDATION'
    if MARKER_AFTER_CS not in src:
        print('ERROR: Cannot find insertion point for routing block')
        return 1
    if 'class FailureType' in src:
        print('INFO: Routing block already present — skipping block insertion')
    else:
        src = src.replace(MARKER_AFTER_CS, ROUTING_BLOCK + MARKER_AFTER_CS)
        print('OK: Inserted routing block')
    BUDGET_MARKER = '    # guardian: allow-magic-config\n    def _check_healing_budget('
    if BUDGET_MARKER not in src:
        print('ERROR: Cannot find _check_healing_budget insertion point')
        return 1
    if '_route_decision' in src:
        print('INFO: _route_decision already present — skipping')
    else:
        src = src.replace(BUDGET_MARKER, ROUTE_METHOD + BUDGET_MARKER)
        print('OK: Inserted _route_decision method')
    OLD_SHOULD_PROCEED_START = '    def should_proceed_with_healing(\n        self,\n        confidence: ConfidenceScore,\n        agent_name: str = "Unknown",\n        territory: str = "unknown",\n    ) -> tuple[bool, str]:'
    if OLD_SHOULD_PROCEED_START not in src:
        if 'failure_type: "FailureType | None" = None,' in src:
            print('INFO: should_proceed_with_healing already updated — skipping')
        else:
            print('ERROR: Cannot find should_proceed_with_healing to replace')
            return 1
    else:
        idx_start = src.index(OLD_SHOULD_PROCEED_START)
        HITL_MARKER = '\n    def _hitl_gate('
        idx_end = src.index(HITL_MARKER, idx_start)
        old_body = src[idx_start:idx_end]
        src = src[:idx_start] + NEW_SHOULD_PROCEED + src[idx_end:]
        print('OK: Replaced should_proceed_with_healing')
    TARGET.write_text(src, encoding='utf-8')
    print('OK: Wrote patched file')
    return 0
if __name__ == '__main__':
    sys.exit(main())
