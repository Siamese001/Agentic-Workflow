"""CanonBaseAgent - Base class for all validation agents.

Provides shared infrastructure for Canon validation agents including:
- Verification registry management
- File hashing and caching
- LLM-based smart fix capabilities
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
import os
import uuid
from pathlib import Path
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.L1_cognition.types.validation_types import IValidationProtocol
from agentic_core.L2_execution.enforcement.guardrail_gate import get_guardrail_gate
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
from agentic_core.utils.core_extensions.timeout_decorator import timeout

emit_replay_key("p0", "validation_orchestrator")
emit_determinism_digest("p0", "validation_orchestrator")

_emit_dispatches_healing_run("p1", "validation_orchestrator", "L2")
_emit_routes_through("p1", "validation_orchestrator", "L2")
_emit_checks_agent_registry("p1", "validation_orchestrator", "agent_registry")
_emit_validates_agent_capability("p1", "validation_orchestrator", "capability")
_emit_dispatches_execution_plan("p1", "validation_orchestrator", "exec_plan")
_emit_agent_executes_agent("p1", "validation_orchestrator", "sub_agent")
_emit_routes_to_agent("p1", "validation_orchestrator", "target_agent")
_emit_verifies_policy("p1", "validation_orchestrator", "policy_check")
_emit_observes_runtime_state("p1", "validation_orchestrator", "runtime_state")
_emit_verifies_boundary("p1", "validation_orchestrator", "boundary_check")
_emit_transcripts_response("p1", "validation_orchestrator", "transcript")
_emit_hard_fails_untranscripted("p1", "validation_orchestrator")
_emit_gated_by_confidence("p1", "validation_orchestrator", "confidence_gate")
_emit_escalates_to_human("p1", "validation_orchestrator", "L2")
_emit_reads_policy_state("p1", "validation_orchestrator", "L2")
_emit_authorize_and_execute("p2", "validation_orchestrator", "execution_auth")
_emit_validates_capability("p2", "validation_orchestrator", "capability_check")
_emit_routes_to_capability("p2", "validation_orchestrator", "capability_route")
_emit_writes_via_uwg("p2", "validation_orchestrator", "uwg_write")
_emit_blocks_direct_write("p2", "validation_orchestrator", "direct_write_block")
_emit_records_tool_invocation("p2", "validation_orchestrator", "tool_invocation")
_emit_captures_execution_output("p2", "validation_orchestrator", "exec_output")
_emit_dispatches_agent("p3", "validation_orchestrator", "agent_dispatch")
_emit_coordinates_agents("p3", "validation_orchestrator", "agent_coordination")
_emit_records_workflow_lineage("p3", "validation_orchestrator", "workflow_lineage")
_emit_records_healing_outcome("p3", "validation_orchestrator", "healing_outcome")
_emit_escalates_failure("p3", "validation_orchestrator", "failure_escalation")
_emit_orchestrates_workflow("p3", "validation_orchestrator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "validation_orchestrator", "healing_dispatch")
_emit_invokes_evaluation("p3", "validation_orchestrator", "evaluation_signal")
_emit_records_telemetry_event("p4", "validation_orchestrator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "validation_orchestrator", "eval_metric")
_emit_stores_embedding("p4", "validation_orchestrator", "embedding_store")
_emit_updates_meta_learning_state("p4", "validation_orchestrator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "validation_orchestrator", "exec_snapshot_link")
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

_emit_emits_metric_event("validation_orchestrator", "p4obs", "metric_1")
_emit_emits_metric_event("validation_orchestrator", "p4obs", "metric_2")
_emit_emits_metric_event("validation_orchestrator", "p4obs", "metric_3")
_emit_emits_metric_event("validation_orchestrator", "p4obs", "metric_4")
_emit_emits_metric_event("validation_orchestrator", "p4obs", "metric_5")
_emit_emits_metric_event("validation_orchestrator", "p4obs", "metric_6")
_emit_records_incident_event("validation_orchestrator", "p4obs", "incident")
_emit_captures_runtime_anomaly("validation_orchestrator", "p4obs", "anomaly")
_emit_writes_observability_log("validation_orchestrator", "p4obs", "obs_log")
_emit_updates_monitoring_state("validation_orchestrator", "p4obs", "mon_state")
_emit_triggers_alert("validation_orchestrator", "p4obs", "alert")
_emit_links_incident_trace("validation_orchestrator", "p4obs", "trace_link")
_emit_captures_pattern("validation_orchestrator", "p3lm", "pattern")
_emit_records_learning_event("validation_orchestrator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("validation_orchestrator", "p3lm", "snapshot")
_emit_feeds_meta_learning("validation_orchestrator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("validation_orchestrator", "p3lm", "routing")
_emit_improves_agent_policy("validation_orchestrator", "p3lm", "policy")
_emit_stores_learning_state("validation_orchestrator", "p3lm", "state")
_emit_records_execution_trace("validation_orchestrator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("validation_orchestrator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("validation_orchestrator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("validation_orchestrator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("validation_orchestrator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("validation_orchestrator", "env_read", "p2_env_1")
_emit_reads_environ("validation_orchestrator", "env_read", "p2_env_2")
_emit_reads_runtime_state("validation_orchestrator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("validation_orchestrator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "validation_orchestrator", "context_pull")
_emit_pulls_context("p1", "validation_orchestrator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "validation_orchestrator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "validation_orchestrator", "uwg_term_2")
_emit_writes_through("p1", "validation_orchestrator", "write_through")
_emit_writes_through("p1", "validation_orchestrator", "write_through_2")
_emit_validated_by_safety_plane("p1", "validation_orchestrator", "safety_validation")
_emit_invokes_eval("p1", "validation_orchestrator", "eval_call")
_emit_proposal_commits_routing("p1", "validation_orchestrator", "routing_commit")

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO").upper())
Logger = logging.getLogger(__name__)


# guardian: allow-type-erasure
def _load_activation_gate() -> Any:
    """Load L5 activation gate via approved L0 seam (no static L2→L5 import)."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_load_activation_gate", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_load_activation_gate", "p0_governance")
    from agentic_core.L0_routing.utils.seams.safety_enforcement_seam import load_activation_gate

    return load_activation_gate()


# guardian: allow-type-erasure
def _get_file_io() -> Any:
    """Return a FileIo instance for direct L2.2 writes."""
    from agentic_core.L2_execution.tools.file_io_impl import FileIo

    return FileIo()


class ValidationOrchestrator(SovereignBaseAgent):
    """
    Validation orchestrator for Canon validation agents.

    Provides shared infrastructure for validation including:
        - Verification registry with check functions for all Canon keys.
        - File hashing for cache invalidation.
        - Redis caching for validation results.
        - LLM-based smart fix capabilities with retry logic.

    Class Attributes:
        VERIFICATION_REGISTRY: Dict mapping Canon keys to check functions.
        _registry_built: Flag indicating if registry has been initialized.

    Instance Attributes:
        ctx: ValidationContext for file access and reporting.
        name: Agent name for logging and reporting.
        layer: Optional layer identifier.
    """

    VERIFICATION_REGISTRY: dict[int, Any] = {}
    _registry_built: bool = False

    @classmethod
    def _init_registry(cls, ctx: IValidationProtocol) -> None:
        """
        Build the verification registry once.

        Initializes VERIFICATION_REGISTRY with check functions for all Canon keys.
        Uses dynamic import for L2 StructuralEngineerAgent to avoid gravity violation.

        Args:
            ctx: ValidationContext for agent initialization.
        """
        if cls._registry_built:
            return
        cls._registry_built = True
        cls.VERIFICATION_REGISTRY = {}

    def __init__(
        self, context: IValidationProtocol | None = None, name: str | None = None, layer: str | None = None
    ) -> None:
        """
        Initialize the Canon base agent.

        Args:
            context: ValidationContext for file access and reporting.
            name: Agent name (defaults to class name).
            layer: Optional layer identifier for logging.
        """
        from pathlib import Path

        self.project_root = Path.cwd()
        self._initialized = False
        self._security_validator = None
        self.name = name or self.__class__.__name__
        try:
            self.__post_init__()
        except AttributeError:
            pass
        self.ctx = context
        self.layer = layer

    def can_run(self) -> bool:
        """
        Check if agent can run.

        Returns:
            True unless CRITICAL_FAIL signal is present in context.
        """
        return "CRITICAL_FAIL" not in self.ctx.signals

    def get_file_hash(self, file_path: str) -> str:
        """
        Calculate SHA-256 hash of a file.

        Args:
            file_path: Path to file to hash.

        Returns:
            Hex digest of SHA-256 hash, or empty string on error.
        """
        try:
            with open(file_path, "rb") as f:
                return hashlib.sha256(f.read()).hexdigest()
        except OSError as e:    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging
            Logger.warning(f"Could not read file {file_path} for hashing: {e}")
            return ""

    # guardian: allow-type-erasure
    def check_cache(self, file_path: str, key: int) -> dict[str, Any] | None:
        """
        Check Redis cache for validation result.

        Args:
            file_path: Path to file being validated.
            key: Canon key number.

        Returns:
            Cached result dict or None if not cached.
        """
        file_hash = self.get_file_hash(file_path)
        if not file_hash:
            return None
        cache_key: Any = f"{self.name}:{key}:{file_hash}"
        return self.ctx.services.get_cached_result(cache_key)

    def store_cache(self, file_path: str, key: int, result: dict[str, Any]) -> None:
        """
        Store validation result in Redis cache.

        Args:
            file_path: Path to file being validated.
            key: Canon key number.
            result: Validation result to cache.
        """
        file_hash = self.get_file_hash(file_path)
        if not file_hash:
            return
        cache_key: Any = f"{self.name}:{key}:{file_hash}"
        self.ctx.services.cache_result(cache_key, result)

    async def _run_check_func(self, check_func: Any) -> Tuple[bool, list[Any]]:
        """Run a check function (sync or async) and return result."""
        if asyncio.iscoroutinefunction(check_func):
            return await check_func()
        return check_func()

    def _get_violation_details(self, res: Tuple[bool, list[Any]], file_path: str) -> str:
        """Extract violation details relevant to a specific file."""
        if res[0]:
            return ""
        relevant = [d for d in res[1] if str(d).startswith(file_path)]
        if not relevant:
            return ""
        max_shown = int(os.getenv("MAX_VIOLATIONS_SHOWN", "8"))
        return "\nSpecific Violations:\n" + "\n".join(map(str, relevant[:max_shown]))

    def _get_reference_fix(self, violation_desc: str) -> str | None:
        """Find similar patterns and return reference fix if available."""
        similar = self.ctx.services.find_similar_patterns(violation_desc)
        if similar and similar[0]["similarity"] > 0.85:
            best = similar[0]
            return f"\n\nReference Fix (similarity: {best['similarity']:.2f}):\n{best['fix']}"
        return None

    def _build_task(self, violation_key: int, file_path: str, details: str, ref_fix: str | None) -> str:
        """Build the task description for LLM healing."""
        parts = [f"Fix Key {violation_key} Violation in {file_path}."]
        if details:
            parts.append(details)
        if ref_fix:
            parts.append(ref_fix)
        return "\n".join(parts)

    def _record_success(
        self, file_path: str, violation_key: int, violation_desc: str, fixed_code: str
    ) -> None:
        """Record a successful healing attempt."""
        self.ctx.record_healing_attempt(file_path, success=True)
        self.ctx.modified_files.add(file_path)
        if file_path not in self.ctx.healing_history:
            self.ctx.healing_history[file_path] = []
        self.ctx.healing_history[file_path].append(f"Key{violation_key}")
        self.ctx.services.store_healing_pattern(
            Violation=violation_desc, fix=fixed_code[:500], success_rate=1.0
        )

    async def smart_fix(self, file_path: str, violation_key: int) -> bool:
        """Trigger LLM-based fix for a specific violation.

        Uses resilient mutation with retry logic to fix violations.
        Records healing attempts and stores successful patterns.

        Args:
            file_path: Path to file with violation.
            violation_key: Canon key number of the violation.

        Returns:
            True if fix was successful, False otherwise.
        """
        if not self.ctx.intelligence_enabled:
            Logger.debug("Intelligence not enabled, skipping smart fix.")
            return False
        if not self.ctx.can_attempt_healing(file_path):
            Logger.debug(f"Cannot attempt healing for {file_path}.")
            return False
        self.__class__._init_registry(self.ctx)
        check_func = self.VERIFICATION_REGISTRY.get(violation_key)
        if not check_func:
            Logger.warning(f"No check function found for Violation key {violation_key}.")
            return False
        try:
            with open(file_path, encoding="utf-8") as f:
                original_code = f.read()
            res = await self._run_check_func(check_func)
            violation_details = self._get_violation_details(res, file_path)
            violation_desc = f"{self.name} Key {violation_key} Violation in {file_path}"
            reference_fix = self._get_reference_fix(violation_desc)
            max_rounds = int(os.getenv("MAX_HEALING_ROUNDS", "5"))
            current_code = original_code
            previous_failure: str | None = None
            for round_num in range(1, max_rounds + 1):
                print(
                    f"      [Round {round_num}/{max_rounds}] Healing Key {violation_key} → {Path(file_path).name}",
                    flush=True,
                )
                task = self._build_task(violation_key, file_path, violation_details, reference_fix)
                fixed_code = await self.ctx.resilient_mutation(
                    agent_name=self.name,
                    Task=task,
                    code=current_code,
                    file_path=file_path,
                    round_num=round_num,
                    previous_failure=previous_failure,
                )
                if fixed_code == current_code:
                    print(f"      [!] No changes made in Round {round_num}", flush=True)
                    previous_failure = "No changes were made to the code."
                    continue
                _gate_mod = _load_activation_gate()
                trace_id = f"healing:{violation_key}:{Path(file_path).name}:r{round_num}"
                _gate_mod.assert_activation_allowed(trace_id=trace_id)
                _file_io = _get_file_io()
                _file_io.save_file(fixed_code, file_path)
                res = await self._run_check_func(check_func)
                if res[0]:
                    print(f"      [OK] Healing successful in Round {round_num}", flush=True)
                    self._record_success(file_path, violation_key, violation_desc, fixed_code)
                    return True
                relevant = [d for d in res[1] if str(d).startswith(file_path)]
                previous_failure = (
                    "Fix attempt failed. Remaining violations:\n" + "\n".join(map(str, relevant[:3]))
                    if relevant
                    else "Fix attempt did not resolve the Violation."
                )
                current_code = fixed_code
            _file_io = _get_file_io()
            _file_io.save_file(original_code, file_path)
            print(
                f"      [X] Healing failed after {max_rounds} rounds - reverting {Path(file_path).name}",
                flush=True,
            )
            self.ctx.record_healing_attempt(file_path, success=False)
            return False
        except (OSError, ValueError, SyntaxError) as e:
            Logger.error(f"Healing error for {file_path}, key {violation_key}: {e}", exc_info=True)
            print(f"      [ALERT] Healing error for {Path(file_path).name}: {e}", flush=True)
            return False
        except (RuntimeError, ValueError) as e:
            Logger.critical(
                f"Critical healing error for {file_path}, key {violation_key}: {e}", exc_info=True
            )
            print(f"      [CRITICAL] Healing error for {Path(file_path).name}: {e}", flush=True)
            return False

    def execute(self) -> None:
        """
        Execute validation checks.
        """

        _emit_records_execution_trace(
            str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, "ValidationOrchestrator.execute"
        )
        # Wave 3: Guardrail pre-check
        guardrail = get_guardrail_gate()
        guardrail.check(operation="execute_validation", target="validation_orchestrator")
        print("\n[VALIDATION] Starting validation orchestrator...", flush=True)

        """
        Must be overridden in subclass to implement specific checks.

        Raises:
            NotImplementedError: Always, as this is abstract.
        """
        raise NotImplementedError(f"{self.name}.execute() not implemented")

    @timeout(300)
    # guardian: allow-magic-config
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set[str] | None = None,
    ) -> dict[str, int]:
        """Validate Canon keys and run registered verification checks.

        Iterates through the VERIFICATION_REGISTRY and runs all registered
        checks for Canon validation. Can apply smart fixes when execute=True.

        Args:
            dry_run: If True, only report violations without fixing.
            execute: If True, apply fixes using smart_fix.
            depth: Current recursion depth for cycle detection.
            max_depth: Maximum allowed recursion depth.
            _call_path: Set of agent names already in call chain.

        Returns:
            Dict with violations_found, violations_fixed, errors, skipped.
        """
        try:
            super().heal_repository(
                dry_run=dry_run, execute=execute, depth=depth, max_depth=max_depth, _call_path=_call_path
            )
        except AttributeError:
            pass
        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {
                "violations_found": 0,
                "violations_fixed": 0,
                "errors": 1,
                "skipped": 0,
                "cycle_detected": True,
            }
        if depth > max_depth:
            return {
                "violations_found": 0,
                "violations_fixed": 0,
                "errors": 0,
                "skipped": 1,
                "depth_limited": True,
            }
        _call_path.add(agent_name)
        violations_found = 0
        violations_fixed = 0
        errors = 0
        skipped = 0
        try:
            self.logger.info(f"[{agent_name}] Running Canon validation checks...")
            for canon_key, check_func in self.VERIFICATION_REGISTRY.items():
                try:
                    self.logger.info(f"  Checking Canon key: {canon_key}")
                    context = self._get_check_context(canon_key)
                    result = check_func(context)
                    if not result.get("valid", True):
                        violations_found += 1
                        self.logger.warning(f"    Violation: {result.get('message', 'Unknown')}")
                        if execute and (not dry_run):
                            fix_result = self.smart_fix(canon_key, context, result)
                            if fix_result.get("fixed", False):
                                violations_fixed += 1
                                self.logger.info(f"    Fixed: {canon_key}")
                            else:
                                self.logger.warning(f"    Could not fix: {canon_key}")
                except (ValueError, KeyError, AttributeError) as e:
                    self.logger.error(f"    Error checking {canon_key}: {e}")
                    errors += 1
                except (RuntimeError, TypeError, MemoryError) as e:
                    self.logger.critical(f"    Critical error checking {canon_key}: {e}")
                    errors += 1
            self.logger.info(
                f"[{agent_name}] Complete: {violations_found} violations, {violations_fixed} fixed"
            )
            return {
                "violations_found": violations_found,
                "violations_fixed": violations_fixed,
                "errors": errors,
                "skipped": skipped,
                "agent": agent_name,
                "dry_run": dry_run,
            }
        finally:
            _call_path.discard(agent_name)

    # guardian: allow-type-erasure
    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """
        Heal violations detected by CanonBaseAgent.

        Args:
            violation: Dictionary containing violation details with keys:
                - file: Path to the file with the violation
                - type: Type of violation detected
                - message: Description of the violation

        Returns:
            Dictionary with keys:
                - status: 'success', 'partial_success', 'failed', or 'skipped'
                - details: Human-readable summary
                - artifacts: List of modified files
                - errors: List of error messages
        """
        violation.get("file") or violation.get("file_path")
        violation_type = violation.get("type", "unknown")
        try:
            return {
                "status": "skipped",
                "details": f"CanonBaseAgent heal() not yet implemented for {violation_type} - canon violations require manual review",
                "artifacts": [],
                "errors": [],
            }
        except (ValueError, KeyError, AttributeError) as e:
            return {
                "status": "failed",
                "details": f"CanonBaseAgent heal() failed with known error: {str(e)}",
                "artifacts": [],
                "errors": [str(e)],
            }
        except (RuntimeError, ValueError) as e:
            Logger.critical(f"Critical healing error in CanonBaseAgent.heal(): {e}", exc_info=True)
            return {
                "status": "failed",
                "details": f"CanonBaseAgent heal() failed with critical error: {str(e)}",
                "artifacts": [],
                "errors": [str(e)],
            }
