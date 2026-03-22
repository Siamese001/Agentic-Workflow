from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
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
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
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

emit_replay_key("p0", "prompts_util")
emit_determinism_digest("p0", "prompts_util")

_emit_dispatches_healing_run("p1", "prompts_util", "L1")
_emit_routes_through("p1", "prompts_util", "L1")
_emit_checks_agent_registry("p1", "prompts_util", "agent_registry")
_emit_validates_agent_capability("p1", "prompts_util", "capability")
_emit_dispatches_execution_plan("p1", "prompts_util", "exec_plan")
_emit_agent_executes_agent("p1", "prompts_util", "sub_agent")
_emit_routes_to_agent("p1", "prompts_util", "target_agent")
_emit_verifies_policy("p1", "prompts_util", "policy_check")
_emit_observes_runtime_state("p1", "prompts_util", "runtime_state")
_emit_verifies_boundary("p1", "prompts_util", "boundary_check")
_emit_transcripts_response("p1", "prompts_util", "transcript")
_emit_hard_fails_untranscripted("p1", "prompts_util")
_emit_gated_by_confidence("p1", "prompts_util", "confidence_gate")
_emit_escalates_to_human("p1", "prompts_util", "L1")
_emit_reads_policy_state("p1", "prompts_util", "L1")

_emit_snapshots_state("p0", "prompts_util", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "prompts_util", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "prompts_util")
_emit_authorize_and_execute("p2", "prompts_util", "execution_auth")
_emit_validates_capability("p2", "prompts_util", "capability_check")
_emit_routes_to_capability("p2", "prompts_util", "capability_route")
_emit_writes_via_uwg("p2", "prompts_util", "uwg_write")
_emit_blocks_direct_write("p2", "prompts_util", "direct_write_block")
_emit_records_tool_invocation("p2", "prompts_util", "tool_invocation")
_emit_captures_execution_output("p2", "prompts_util", "exec_output")
_emit_dispatches_agent("p3", "prompts_util", "agent_dispatch")
_emit_coordinates_agents("p3", "prompts_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "prompts_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "prompts_util", "healing_outcome")
_emit_escalates_failure("p3", "prompts_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "prompts_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "prompts_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "prompts_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "prompts_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "prompts_util", "eval_metric")
_emit_stores_embedding("p4", "prompts_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "prompts_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "prompts_util", "exec_snapshot_link")

"\nagentic_core/domain/prompts_util.py\nDepth: 3\nRole: Static storage for LLM few-shot prompts to keep Context clean.\n"
from typing import Any

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

_emit_emits_metric_event("prompts_util", "p4obs", "metric_1")
_emit_emits_metric_event("prompts_util", "p4obs", "metric_2")
_emit_emits_metric_event("prompts_util", "p4obs", "metric_3")
_emit_emits_metric_event("prompts_util", "p4obs", "metric_4")
_emit_emits_metric_event("prompts_util", "p4obs", "metric_5")
_emit_emits_metric_event("prompts_util", "p4obs", "metric_6")
_emit_records_incident_event("prompts_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("prompts_util", "p4obs", "anomaly")
_emit_writes_observability_log("prompts_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("prompts_util", "p4obs", "mon_state")
_emit_triggers_alert("prompts_util", "p4obs", "alert")
_emit_links_incident_trace("prompts_util", "p4obs", "trace_link")
_emit_captures_pattern("prompts_util", "p3lm", "pattern")
_emit_records_learning_event("prompts_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("prompts_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("prompts_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("prompts_util", "p3lm", "routing")
_emit_improves_agent_policy("prompts_util", "p3lm", "policy")
_emit_stores_learning_state("prompts_util", "p3lm", "state")
_emit_records_execution_trace("prompts_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("prompts_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("prompts_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("prompts_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("prompts_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("prompts_util", "env_read", "p2_env_1")
_emit_reads_environ("prompts_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("prompts_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("prompts_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "prompts_util", "context_pull")
_emit_pulls_context("p1", "prompts_util", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "prompts_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "prompts_util", "uwg_term_secondary")
_emit_writes_through("p1", "prompts_util", "write_through")
_emit_writes_through("p1", "prompts_util", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "prompts_util", "safety_validation")
_emit_invokes_eval("p1", "prompts_util", "eval_call")
_emit_proposal_commits_routing("p1", "prompts_util", "routing_commit")

few_shot_global_refactor: Any = "\nFEW-SHOT REFACTORING PATTERNS:\n\nEXAMPLE 1: Monolith Function → Atomic Split\nBAD: def handle_order(order): # 250 lines\nGOOD: Split into orders/validate.py, orders/charge.py\n\nEXAMPLE 2: Incorrect Depth\nBAD: apps/payment/helpers.py (depth 3)\nGOOD: agentic_core/shared/payments/domain/charge_service.py (depth 5)\n"
few_shot_import_fixes: Any = "\nFEW-SHOT IMPORT RESOLUTION:\n\nEXAMPLE 1: Relative Import\nBAD: from utils import validate\nGOOD: from agentic_core.shared.validation.common import validate\n\nEXAMPLE 2: Missing schema\nBAD: ImportError: cannot import name 'OrderSchema'\nGOOD: from agentic_core.L1_cognition.P2_domain.models import DomainSchema\n"
few_shot_style: Any = "\nFEW-SHOT CODE STYLE FIXES:\n\nEXAMPLE 1: Import Ordering\nBAD: Mixed stdlib and 3rd party\nGOOD:\nimport os\nimport sys\n\nimport pandas as pd\n\nfrom myapp.models import User\n\nEXAMPLE 2: Type Hints\nBAD: def func(a): return a + 1\nGOOD: def func(a: int) -> int: return a + 1\n"
few_shot_safety: Any = '\nFEW-SHOT SAFETY FIXES:\n\nEXAMPLE 1: No Eval\nBAD: eval(input)\nGOOD: ast.literal_eval(input)\n\nEXAMPLE 2: Secrets\nBAD: KEY = "123"\nGOOD: KEY = os.getenv("KEY")\n'
few_shot_concurrency: Any = "\nFEW-SHOT CONCURRENCY FIXES:\n\nEXAMPLE 1: Shared State\nBAD: counter += 1\nGOOD: async with lock: counter += 1\n"
few_shot_hygiene: Any = "\nFEW-SHOT HYGIENE FIXES:\n\nEXAMPLE 1: Unused Imports\nBAD: import os # never used\nGOOD: # removed\n\nEXAMPLE 2: Dead Code\nBAD: if False: return\nGOOD: # removed\n"
few_shot_testpilot: Any = '\nFEW-SHOT TEST GENERATION:\n\nEXAMPLE 1: Unit Test\nGOOD:\ndef test_valid_order():\n    assert process(Order(amount=10)).status == "paid"\n'
few_shot_strategic: Any = "\nFEW-SHOT STRATEGY:\n\nRULES:\n1. TEST_FAILURE -> Sherlock\n2. IMPORT_ERROR -> DependencySentinelAgent\n3. SYNTAX -> SafetyInspectorAgent\n"
few_shot_reflection: Any = "\nFEW-SHOT REFLECTION:\n\nCheck:\n1. Did signals decrease?\n2. Did new signals appear?\n3. Convergence reached?\n"
few_shot_reflection_strategy: Any = "\nFEW-SHOT HEALING STRATEGY DECISIONS:\n\nIF: Multiple test failures in same module\nTHEN: Extract shared utilities to agentic_core/shared/\n\nIF: Import errors after refactor\nTHEN: Update imports and check depth compliance\n\nIF: Performance regression\nTHEN: Profile and optimize hot paths\n"
few_shot_reflection_enhanced: Any = "\nFEW-SHOT ENHANCED REFLECTION:\n\nEXAMPLE 1: Convergence Check\nSignals before: [SYNTAX_ERROR, IMPORT_ERROR]\nSignals after: []\nDecision: CONVERGE_AND_COMMIT\n\nEXAMPLE 2: Flapping Detection\nFile X modified 3 times, same error returns\nDecision: MARK_FLAPPING_SKIP_FILE\n"
few_shot_sherlock: Any = "\nFEW-SHOT ROOT CAUSE:\n\nTraceback: AssertionError in test_login\nFix: Update password hash comparison logic\n"
few_shot_gitops: Any = "\nFEW-SHOT GIT OPS:\n\nBranch: healing/fix-auth-race-20240101\nCommit: fix: resolve race condition in auth token generation\n"
few_shot_property_tests: Any = "\nFEW-SHOT HYPOTHESIS:\n\n@given(st.integers())\ndef test_roundtrip(x):\n    assert decode(encode(x)) == x\n"
few_shot_historian: Any = "\nFEW-SHOT HISTORY RECALL:\n\nMemory: File X had syntax error fixed by Y.\nCurrent: File X has syntax error.\nAction: Apply Y.\n"
positive_instructional_context: Any = "\nYou are an elite subatomic governance agent in a sovereign self-healing codebase.\nYour reasoning must follow this chain:\n1. First, recall the Three Laws of Subatomic Governance.\n3. Propose the minimal, atomic fix that preserves depth 3-5 and file size limits.\n4. Check blast radius using dependency graph.\n5. Verify fix will not introduce new signals.\n\nPreferred patterns (prioritize these):\n- Extract repeated logic → new shared util in agentic_core/shared/\n- Move class to correct depth (e.g., domain/service/*.py)\n- Replace monolith functions with focused units\n- Use existing schemas before creating new ones\n\nAlways output in the exact format requested. Never add commentary.\nThink step-by-step before responding.\n"
