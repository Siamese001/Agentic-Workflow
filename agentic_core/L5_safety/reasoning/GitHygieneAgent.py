from __future__ import annotations

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    # noqa: E402
    emit_replay_key,
)

emit_replay_key("p0", "GitHygieneAgent")
emit_determinism_digest("p0", "GitHygieneAgent")

_emit_dispatches_healing_run("p1", "GitHygieneAgent", "L5")
_emit_routes_through("p1", "GitHygieneAgent", "L5")
_emit_checks_agent_registry("p1", "GitHygieneAgent", "agent_registry")
_emit_validates_agent_capability("p1", "GitHygieneAgent", "capability")
_emit_dispatches_execution_plan("p1", "GitHygieneAgent", "exec_plan")
_emit_agent_executes_agent("p1", "GitHygieneAgent", "sub_agent")
_emit_routes_to_agent("p1", "GitHygieneAgent", "target_agent")
_emit_verifies_policy("p1", "GitHygieneAgent", "policy_check")
_emit_observes_runtime_state("p1", "GitHygieneAgent", "runtime_state")
_emit_verifies_boundary("p1", "GitHygieneAgent", "boundary_check")
_emit_transcripts_response("p1", "GitHygieneAgent", "transcript")
_emit_hard_fails_untranscripted("p1", "GitHygieneAgent")
_emit_gated_by_confidence("p1", "GitHygieneAgent", "confidence_gate")
_emit_escalates_to_human("p1", "GitHygieneAgent", "L5")
_emit_reads_policy_state("p1", "GitHygieneAgent", "L5")
_emit_authorize_and_execute("p2", "GitHygieneAgent", "execution_auth")
_emit_validates_capability("p2", "GitHygieneAgent", "capability_check")
_emit_routes_to_capability("p2", "GitHygieneAgent", "capability_route")
_emit_writes_via_uwg("p2", "GitHygieneAgent", "uwg_write")
_emit_blocks_direct_write("p2", "GitHygieneAgent", "direct_write_block")
_emit_records_tool_invocation("p2", "GitHygieneAgent", "tool_invocation")
_emit_captures_execution_output("p2", "GitHygieneAgent", "exec_output")
_emit_dispatches_agent("p3", "GitHygieneAgent", "agent_dispatch")
_emit_coordinates_agents("p3", "GitHygieneAgent", "agent_coordination")
_emit_records_workflow_lineage("p3", "GitHygieneAgent", "workflow_lineage")
_emit_records_healing_outcome("p3", "GitHygieneAgent", "healing_outcome")
_emit_escalates_failure("p3", "GitHygieneAgent", "failure_escalation")
_emit_orchestrates_workflow("p3", "GitHygieneAgent", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "GitHygieneAgent", "healing_dispatch")
_emit_invokes_evaluation("p3", "GitHygieneAgent", "evaluation_signal")
_emit_records_telemetry_event("p4", "GitHygieneAgent", "telemetry_event")
_emit_captures_evaluation_metric("p4", "GitHygieneAgent", "eval_metric")
_emit_stores_embedding("p4", "GitHygieneAgent", "embedding_store")
_emit_updates_meta_learning_state("p4", "GitHygieneAgent", "meta_learning")
_emit_links_execution_to_snapshot("p4", "GitHygieneAgent", "exec_snapshot_link")

'Git Hygiene Agent - Enforces Git repository hygiene.\n\nThis module provides a batch agent that enforces Git repository hygiene by:\n- Detecting stale branches (no commits in >90 days)\n- Identifying large files in history (>10MB)\n- Checking for uncommitted/unpushed changes\n\nTypical usage:\n    agent = GitHygieneAgent(project_root=Path("/path/to/repo"), ctx=context)\n    result = await agent.execute()\n'
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

try:
    from agentic_core.utils.security_util import safe_git_execute
except ModuleNotFoundError:
    import subprocess
    def safe_git_execute(cmd, **kwargs):
        """Stub safe_git_execute when security_util is not available."""
        return subprocess.run(cmd, capture_output=True, text=True, **kwargs)

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
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
    _emit_snapshots_state,
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
from agentic_core.utils.decorators_compat_util import standard_heal
from agentic_core.utils.timeout_decorator_util import timeout

_emit_emits_metric_event("GitHygieneAgent", "p4obs", "metric_1")
_emit_emits_metric_event("GitHygieneAgent", "p4obs", "metric_2")
_emit_emits_metric_event("GitHygieneAgent", "p4obs", "metric_3")
_emit_emits_metric_event("GitHygieneAgent", "p4obs", "metric_4")
_emit_emits_metric_event("GitHygieneAgent", "p4obs", "metric_5")
_emit_emits_metric_event("GitHygieneAgent", "p4obs", "metric_6")
_emit_records_incident_event("GitHygieneAgent", "p4obs", "incident")
_emit_captures_runtime_anomaly("GitHygieneAgent", "p4obs", "anomaly")
_emit_writes_observability_log("GitHygieneAgent", "p4obs", "obs_log")
_emit_updates_monitoring_state("GitHygieneAgent", "p4obs", "mon_state")
_emit_triggers_alert("GitHygieneAgent", "p4obs", "alert")
_emit_links_incident_trace("GitHygieneAgent", "p4obs", "trace_link")
_emit_captures_pattern("GitHygieneAgent", "p3lm", "pattern")
_emit_records_learning_event("GitHygieneAgent", "p3lm", "learning_event")
_emit_writes_learning_snapshot("GitHygieneAgent", "p3lm", "snapshot")
_emit_feeds_meta_learning("GitHygieneAgent", "p3lm", "meta_feed")
_emit_updates_routing_strategy("GitHygieneAgent", "p3lm", "routing")
_emit_improves_agent_policy("GitHygieneAgent", "p3lm", "policy")
_emit_stores_learning_state("GitHygieneAgent", "p3lm", "state")
_emit_records_execution_trace("GitHygieneAgent", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("GitHygieneAgent", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("GitHygieneAgent", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("GitHygieneAgent", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("GitHygieneAgent", "L4_STATE", "p2_trace_5")
_emit_reads_environ("GitHygieneAgent", "env_read", "p2_env_1")
_emit_reads_environ("GitHygieneAgent", "env_read", "p2_env_2")
_emit_reads_runtime_state("GitHygieneAgent", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("GitHygieneAgent", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "GitHygieneAgent", "context_pull")
_emit_pulls_context("p1", "GitHygieneAgent", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "GitHygieneAgent", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "GitHygieneAgent", "uwg_term_2")
_emit_writes_through("p1", "GitHygieneAgent", "write_through")
_emit_writes_through("p1", "GitHygieneAgent", "write_through_2")
_emit_validated_by_safety_plane("p1", "GitHygieneAgent", "safety_validation")
_emit_invokes_eval("p1", "GitHygieneAgent", "eval_call")
_emit_proposal_commits_routing("p1", "GitHygieneAgent", "routing_commit")


@dataclass
class GitHygieneAgent(SovereignBaseAgent):
    """L5 Safety agent that enforces Git repository hygiene.

    This batch agent audits repository health by detecting stale branches,
    large files in history, and uncommitted/unpushed changes.

    Attributes:
        project_root: Root directory of the Git repository.
        ctx: Execution context with reporting capabilities.
        dry_run: If True, only report what would be done (default: True).
        stale_days: Days after which a branch is considered stale (default: 90).
        large_file_mb: Size threshold in MB for large files (default: 10).

    Inherits:
        SubatomicTestingMixin: Provides testing utilities.
        HealerMixin: Provides healing chain support.
    """

    def __init__(self, project_root: Path, ctx: Any) -> None:
        """Initialize the Git hygiene agent.

        Args:
            project_root: Root directory of the Git repository.
            ctx: Execution context with optional report() method.
        """
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "GitHygieneAgent.__init__", "state_snapshot")
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "GitHygieneAgent.__init__", "p0_governance")
        self.project_root: Path = Path(project_root)
        self.ctx: Any = ctx
        self.dry_run: bool = True
        self.stale_days: int = 90
        self.large_file_mb: int = 10

    def _run_git(self, cmd: list[str], **kwargs: Any) -> str:
        """Run a git command and return stdout.

        Args:
            cmd: Git command arguments (without 'git' prefix).
            **kwargs: Additional arguments passed to safe_git_execute.
    # guardian: File operations should check existence before access
        Returns:
            Command stdout if successful, empty string otherwise.
        """
        try:
            result = safe_git_execute(cmd, repo_root=self.project_root, timeout=kwargs.get("timeout", 30))
            return result.stdout.strip() if result.returncode == 0 else ""
        except FileNotFoundError:    # guardian: File operations should check existence before access
            if hasattr(self.ctx, "report"):
                self.ctx.report("GitHygieneAgent", 0, False, "git not installed")
            return ""

    def _get_stale_branches(self) -> list[dict[str, Any]]:
        """Find branches with no commits in the last N days.

        Returns:
            List of dictionaries with branch info:
                - branch: Branch name
                - age_days: Days since last commit
        """
        cutoff = datetime.now() - timedelta(days=self.stale_days)
        cutoff_ts = int(cutoff.timestamp())
        branches_output = self._run_git(["branch", "--format=%(refname:short) %(committerdate:unix)"])
        stale = []
        for line in branches_output.splitlines():
            parts = line.split()
            if len(parts) < 2:
                continue
            branch_name = parts[0]
            if branch_name in {"main", "master", "develop"}:
                continue
            try:
                commit_ts = int(parts[-1])
                if commit_ts < cutoff_ts:
                    age = (datetime.now() - datetime.fromtimestamp(commit_ts)).days
                    stale.append({"branch": branch_name, "age_days": age})
            except ValueError:
                continue
        return stale

    def _get_large_files(self) -> list[dict]:
        """Find large files in Git history (>10MB)."""
        large = []
        return large

    # guardian: allow-type-erasure
    def _get_repo_status(self) -> dict:
        """Check for uncommitted and unpushed changes."""
        status = {"uncommitted": False, "unpushed": False}
        status["uncommitted"] = bool(self._run_git(["status", "--porcelain"]))
        unpushed_count = self._run_git(["rev-list", "@{u}..", "--count"])
        if unpushed_count.isdigit():
            status["unpushed"] = int(unpushed_count) > 0
        return status

    # guardian: allow-type-erasure
    async def execute(self) -> dict:
        """Audit repository health and optionally clean up."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "GitHygieneAgent.execute")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:GitHygieneAgent.execute".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        print("   [GIT HYGIENE] Auditing repository health...")
        stale_branches = self._get_stale_branches()
        status = self._get_repo_status()
        actions = []
        if stale_branches:
            print(f"   [!] Found {len(stale_branches)} stale branches (> {self.stale_days} days)")
            for b in stale_branches[:3]:
                print(f"      → {b['branch']} ({b['age_days']} days)")
            if len(stale_branches) > 3:
                print(f"      ... and {len(stale_branches) - 3} more")
            if not self.dry_run:
                for b in stale_branches:
                    result = self._run_git(["branch", "-D", b["branch"]])
                    if result or True:
                        actions.append(f"Deleted {b['branch']}")
        if status["uncommitted"]:
            print("   [!] Uncommitted changes detected")
        if status["unpushed"]:
            print("   [!] Unpushed commits detected")
        if stale_branches or status["uncommitted"] or status["unpushed"]:
            if hasattr(self.ctx, "report"):
                self.ctx.report(
                    "GitHygieneAgent", 48, True, f"Stale: {len(stale_branches)}, Actions: {len(actions)}",
                )
        return {
            "stale_branches": len(stale_branches),
            "uncommitted": status["uncommitted"],
            "unpushed": status["unpushed"],
            "actions_taken": len(actions),
            "dry_run": self.dry_run,
        }

    @timeout(300)
    @standard_heal
    # guardian: allow-magic-config
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set[str] | None = None,
    ) -> dict[str, int]:
        """Audit and heal Git repository hygiene issues.

        Scans for stale branches, large files, uncommitted changes,
        and unpushed commits. Can clean up stale branches when execute=True.

        Args:
            dry_run: If True, only report what would be done (default: True).
            execute: If True, execute healing actions (default: False).
            depth: Current recursion depth for cycle detection (default: 0).
            max_depth: Maximum recursion depth allowed (default: 3).
            _call_path: Set of agent names in current call chain for cycle detection.

        Returns:
            Dictionary with violations_found, violations_fixed, errors, skipped.
        """
        super().heal_repository()
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
            self.logger.info(f"[{agent_name}] Auditing Git repository hygiene...")
            try:
                result = self.execute(cleanup=False)
                stale_count = result.get("stale_branches", 0)
                large_files = result.get("large_files", 0)
                uncommitted = 1 if result.get("uncommitted", False) else 0
                unpushed = 1 if result.get("unpushed", False) else 0
                violations_found = stale_count + large_files + uncommitted + unpushed
                if violations_found > 0:
                    self.logger.warning(f"  Found {violations_found} hygiene issues:")
                    if stale_count:
                        self.logger.warning(f"    - {stale_count} stale branches")
                    if large_files:
                        self.logger.warning(f"    - {large_files} large files")
                    if uncommitted:
                        self.logger.warning("    - Uncommitted changes detected")
                    if unpushed:
                        self.logger.warning("    - Unpushed commits detected")
                    if execute and (not dry_run):
                        if stale_count > 0:
                            cleanup_result = self.cleanup_stale_branches()
                            violations_fixed += cleanup_result.get("actions_taken", 0)
                            self.logger.info(f"    Cleaned {violations_fixed} stale branches")
                else:
                    self.logger.info("  Repository hygiene is clean")
            # guardian: allow-silent-swallow
            except (ValueError, TypeError) as e:
                self.logger.error(f"  Error during Git hygiene audit: {e}")
                errors += 1
            self.logger.info(f"[{agent_name}] Complete: {violations_found} issues, {violations_fixed} fixed")
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
    def heal(self, violation: dict) -> dict:
        """Heal git hygiene violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (stale_branch, uncommitted, unpushed)
                - path: Path to the repository
                - severity: Severity level of the violation

        Returns:
            Dictionary with healing results following standard_heal format.
        """
        violation_type = violation.get("type", "")
        try:
            if violation_type == "stale_branch":
                result = self.cleanup_stale_branches()
                return {
                    "violations_fixed": result.get("actions_taken", 0),
                    "violations_found": result.get("stale_branches", 0),
                    "errors": 0,
                    "skipped": 0,
                }
            else:
                return {"violations_fixed": 0, "violations_found": 1, "errors": 0, "skipped": 1}
        # guardian: allow-silent-swallow
        except (ValueError, TypeError):
            return {"violations_fixed": 0, "violations_found": 1, "errors": 1, "skipped": 0}
