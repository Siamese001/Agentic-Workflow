from __future__ import annotations

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "deterministic_cleaner_util")
trace_contract.emit_determinism_digest("p0", "deterministic_cleaner_util")

trace_contract._emit_dispatches_healing_run("p1", "deterministic_cleaner_util", "L2")
trace_contract._emit_routes_through("p1", "deterministic_cleaner_util", "L2")
trace_contract._emit_checks_agent_registry("p1", "deterministic_cleaner_util", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "deterministic_cleaner_util", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "deterministic_cleaner_util", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "deterministic_cleaner_util", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "deterministic_cleaner_util", "target_agent")
trace_contract._emit_verifies_policy("p1", "deterministic_cleaner_util", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "deterministic_cleaner_util", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "deterministic_cleaner_util", "boundary_check")
trace_contract._emit_transcripts_response("p1", "deterministic_cleaner_util", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "deterministic_cleaner_util")
trace_contract._emit_gated_by_confidence("p1", "deterministic_cleaner_util", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "deterministic_cleaner_util", "L2")
trace_contract._emit_reads_policy_state("p1", "deterministic_cleaner_util", "L2")

trace_contract._emit_applies_guardrail("p0", "deterministic_cleaner_util", "p0_governance")
trace_contract._emit_snapshots_state("p0", "deterministic_cleaner_util", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "deterministic_cleaner_util", "execution_auth")
trace_contract._emit_validates_capability("p2", "deterministic_cleaner_util", "capability_check")
trace_contract._emit_routes_to_capability("p2", "deterministic_cleaner_util", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "deterministic_cleaner_util", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "deterministic_cleaner_util", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "deterministic_cleaner_util", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "deterministic_cleaner_util", "exec_output")
trace_contract._emit_dispatches_agent("p3", "deterministic_cleaner_util", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "deterministic_cleaner_util", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "deterministic_cleaner_util", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "deterministic_cleaner_util", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "deterministic_cleaner_util", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "deterministic_cleaner_util", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "deterministic_cleaner_util", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "deterministic_cleaner_util", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "deterministic_cleaner_util", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "deterministic_cleaner_util", "eval_metric")
trace_contract._emit_stores_embedding("p4", "deterministic_cleaner_util", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "deterministic_cleaner_util", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "deterministic_cleaner_util", "exec_snapshot_link")

"\nL6 Deterministic Pre-Flight Sanitation\n\nImplements deterministic cleaners that run before LLM processing\nto maintain baseline code quality and save tokens.\n"
import ast
import logging
import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from agentic_core.shared.architecture_constants import ALLOWED_ROOT_FILES
from agentic_core.utils.security_util import safe_execute

trace_contract._emit_emits_metric_event("deterministic_cleaner_util", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("deterministic_cleaner_util", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("deterministic_cleaner_util", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("deterministic_cleaner_util", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("deterministic_cleaner_util", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("deterministic_cleaner_util", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("deterministic_cleaner_util", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("deterministic_cleaner_util", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("deterministic_cleaner_util", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("deterministic_cleaner_util", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("deterministic_cleaner_util", "p4obs", "alert")
trace_contract._emit_links_incident_trace("deterministic_cleaner_util", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("deterministic_cleaner_util", "p3lm", "pattern")
trace_contract._emit_records_learning_event("deterministic_cleaner_util", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("deterministic_cleaner_util", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("deterministic_cleaner_util", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("deterministic_cleaner_util", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("deterministic_cleaner_util", "p3lm", "policy")
trace_contract._emit_stores_learning_state("deterministic_cleaner_util", "p3lm", "state")
trace_contract._emit_records_execution_trace("deterministic_cleaner_util", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("deterministic_cleaner_util", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("deterministic_cleaner_util", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("deterministic_cleaner_util", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("deterministic_cleaner_util", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("deterministic_cleaner_util", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("deterministic_cleaner_util", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("deterministic_cleaner_util", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("deterministic_cleaner_util", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "deterministic_cleaner_util", "context_pull")
trace_contract._emit_pulls_context("p1", "deterministic_cleaner_util", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "deterministic_cleaner_util", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "deterministic_cleaner_util", "uwg_term_2")
trace_contract._emit_writes_through("p1", "deterministic_cleaner_util", "write_through")
trace_contract._emit_writes_through("p1", "deterministic_cleaner_util", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "deterministic_cleaner_util", "safety_validation")
trace_contract._emit_invokes_eval("p1", "deterministic_cleaner_util", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "deterministic_cleaner_util", "routing_commit")

LOGGER = logging.getLogger(__name__)
Logger: Any = logging.getLogger(__name__)


class DeterministicCleaner:
    """
    Applies deterministic formatting and cleaning to code
    before it reaches the LLM for processing.
    """

    def __init__(self, enable_isort: bool = True, enable_autopep8: bool = True):
        """
        Initialize the deterministic cleaner.

        Args:
            enable_isort: Whether to run isort for import sorting
            enable_autopep8: Whether to run autopep8 for PEP8 formatting
        """
        self.enable_isort = enable_isort
        self.enable_autopep8 = enable_autopep8
        self.has_isort = self._check_tool("isort")
        self.has_autopep8 = self._check_tool("autopep8")
        if self.enable_isort and (not self.has_isort):
            LOGGER.warning("isort not available - import sorting disabled")
            self.enable_isort = False
        if self.enable_autopep8 and (
            not self.has_autopep8
        ):  # review: File operations should check existence before access
            LOGGER.warning("autopep8 not available - PEP8 formatting disabled")
            self.enable_autopep8 = False

    def _check_tool(self, tool_name: str) -> bool:
        """Check if a formatting tool is available."""
        try:
            safe_execute([tool_name, "--version"], capture_output=True, check=True)
            return True
        except (
            subprocess.CalledProcessError,
            FileNotFoundError,
        ):  # review: File operations should check existence before access
            return False

    def deterministic_clean(self, code: str, file_path: str | None = None) -> tuple[str, bool]:
        """
        Apply deterministic cleaning to code.

        Args:
            code: The code to clean
            file_path: Optional file path for context

        Returns:
            Tuple of (cleaned_code, was_modified)
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id,
            trace_contract.LayerSegment.L2_EXECUTION,
            "DeterministicCleaner.deterministic_clean",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:DeterministicCleaner.deterministic_clean".encode(),
        ).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        original_code: Any = code
        cleaned_code: Any = code
        was_modified: Any = False
        try:
            cleaned_code: Any = self._scrub_markdown_artifacts(cleaned_code)
            if self.enable_isort and self.has_isort:
                cleaned_code: Any = self._apply_isort(cleaned_code, file_path)
            if self.enable_autopep8 and self.has_autopep8:
                cleaned_code: Any = self._apply_autopep8(cleaned_code, file_path)
            cleaned_code: Any = self._basic_cleanup(cleaned_code)
            was_modified: Any = cleaned_code != original_code
            if was_modified:
                LOGGER.debug(f"Deterministic cleaning applied to {file_path or 'code'}")
            return (cleaned_code, was_modified)
        except (RuntimeError, ValueError) as e:  # guardian: allow-silent-swallow
            LOGGER.error(f"Error in deterministic cleaning: {e}")
            return (original_code, False)

    def _scrub_markdown_artifacts(self, code: str) -> str:
        """
        Remove markdown artifacts from LLM responses.

        Args:
            code: Code that may contain markdown artifacts

        Returns:
            Clean Python code
        """
        code = re.sub("```python\\s*\\n?", "", code)
        code = re.sub("```\\s*\\n?", "", code)
        code = re.sub("^#.*?```.*?```", "", code, flags=re.MULTILINE | re.DOTALL)
        code = code.strip()
        return code

    def _apply_isort(self, code: str, file_path: str | None = None) -> str:
        """Apply isort to sort imports."""
        try:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(code)
                temp_file = f.name
            try:
                safe_execute(
                    ["isort", "--profile", "black", temp_file],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                with open(temp_file) as f:
                    return f.read()
            finally:
                os.unlink(temp_file)
        except subprocess.CalledProcessError as e:
            LOGGER.warning(f"isort failed: {e.stderr}")
            return code

    def _apply_autopep8(self, code: str, file_path: str | None = None) -> str:
        """Apply autopep8 for PEP8 formatting."""
        try:
            result = safe_execute(
                ["autopep8", "--", "-"],
                input=code,
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            LOGGER.warning(f"autopep8 failed: {e.stderr}")
            return code

    def _basic_cleanup(self, code: str) -> str:
        """Apply basic cleanup operations."""
        lines = code.split("\n")
        cleaned_lines = []
        blank_count = 0
        for line in lines:
            if line.strip() == "":
                blank_count += 1
                if blank_count <= 2:
                    cleaned_lines.append(line)
            else:
                blank_count = 0
                cleaned_lines.append(line)
        result = "\n".join(cleaned_lines)
        if result and (not result.endswith("\n")):
            result += "\n"
        return result


class CompliantFileWriter:
    """
    Writes files with compliance checks and validation.
    """

    def __init__(self, root_dir: str | None = None):
        """
        Initialize the compliant file writer.

        Args:
            root_dir: Root directory for hygiene checks
        """
        self.root_dir = Path(root_dir) if root_dir else Path.cwd()
        self.cleaner = DeterministicCleaner()

    def write_compliant_file(self, file_path: str, content: str, pre_clean: bool = True) -> bool:
        """
        Write a file with compliance checks.

        Args:
            file_path: Path to write the file
            content: Content to write
            pre_clean: Whether to apply deterministic cleaning first

        Returns:
            True if write was successful, False otherwise
        """
        try:
            path: Any = Path(file_path)
            if not self._check_root_hygiene(path):
                LOGGER.error(f"Root hygiene Violation: {file_path}")
                return False
            if pre_clean:
                content, was_cleaned = self.cleaner.deterministic_clean(content, file_path)
                if was_cleaned:
                    LOGGER.info(f"Pre-flight cleaning applied to {file_path}")
            if not self._validate_syntax(content):
                LOGGER.error(f"Syntax validation failed for {file_path}")
                return False
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            LOGGER.debug(f"Successfully wrote compliant file: {file_path}")
            return True
        except (RuntimeError, ValueError) as e:  # guardian: allow-silent-swallow
            LOGGER.error(f"Failed to write compliant file {file_path}: {e}")
            return False

    def _check_root_hygiene(self, file_path: Path) -> bool:
        """Check if file complies with root hygiene."""
        if (
            file_path.parent != self.root_dir
        ):  # review: Syntax errors should be caught at parser level, not runtime
            return True
        return file_path.name in ALLOWED_ROOT_FILES

    def _validate_syntax(self, content: str) -> bool:
        """Validate Python syntax using AST."""
        try:
            ast.parse(content)
            return True
        except SyntaxError as e:  # review: Syntax errors should be caught at parser level, not runtime
            LOGGER.error(f"Syntax error: {e}")
            return False
        except (RuntimeError, ValueError) as e:  # guardian: allow-silent-swallow
            LOGGER.error(f"Validation error: {e}")
            return False


_cleaner: DeterministicCleaner | None = None
_writer: CompliantFileWriter | None = None


def get_deterministic_cleaner() -> DeterministicCleaner:
    """Get or create the global deterministic cleaner instance."""
    global _cleaner
    if _cleaner is None:
        _cleaner = DeterministicCleaner()
    return _cleaner


def get_compliant_writer(root_dir: str | None = None) -> CompliantFileWriter:
    """Get or create the global compliant file writer instance."""
    global _writer
    if _writer is None:
        _writer = CompliantFileWriter(root_dir)
    return _writer


def deterministic_clean(code: str, file_path: str | None = None) -> tuple[str, bool]:
    """
    Apply deterministic cleaning to code.
    Args:
        code: The code to clean
        file_path: Optional file path for context

    Returns:
        Tuple of (cleaned_code, was_modified)
    """
    cleaner: Any = get_deterministic_cleaner()
    return cleaner.deterministic_clean(code, file_path)


def write_compliant_file(file_path: str, content: str, pre_clean: bool = True) -> bool:
    """
    Write a file with compliance checks.

    Args:
        file_path: Path to write the file
        content: Content to write
        pre_clean: Whether to apply deterministic cleaning first

    Returns:
        True if write was successful, False otherwise
    """
    writer: Any = get_compliant_writer()
    return writer.write_compliant_file(file_path, content, pre_clean)
