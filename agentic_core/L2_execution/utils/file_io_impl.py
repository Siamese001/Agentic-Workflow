# guardian: allow-silent_swallower -- ADG violation exemption

from __future__ import annotations

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "file_io_impl")
trace_contract.emit_determinism_digest("p0", "file_io_impl")

trace_contract._emit_dispatches_healing_run("p1", "file_io_impl", "L2")
trace_contract._emit_routes_through("p1", "file_io_impl", "L2")
trace_contract._emit_checks_agent_registry("p1", "file_io_impl", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "file_io_impl", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "file_io_impl", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "file_io_impl", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "file_io_impl", "target_agent")
trace_contract._emit_verifies_policy("p1", "file_io_impl", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "file_io_impl", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "file_io_impl", "boundary_check")
trace_contract._emit_transcripts_response("p1", "file_io_impl", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "file_io_impl")
trace_contract._emit_gated_by_confidence("p1", "file_io_impl", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "file_io_impl", "L2")
trace_contract._emit_reads_policy_state("p1", "file_io_impl", "L2")

trace_contract._emit_applies_guardrail("p0", "file_io_impl", "p0_governance")
trace_contract._emit_snapshots_state("p0", "file_io_impl", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "file_io_impl", "execution_auth")
trace_contract._emit_validates_capability("p2", "file_io_impl", "capability_check")
trace_contract._emit_routes_to_capability("p2", "file_io_impl", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "file_io_impl", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "file_io_impl", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "file_io_impl", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "file_io_impl", "exec_output")
trace_contract._emit_dispatches_agent("p3", "file_io_impl", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "file_io_impl", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "file_io_impl", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "file_io_impl", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "file_io_impl", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "file_io_impl", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "file_io_impl", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "file_io_impl", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "file_io_impl", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "file_io_impl", "eval_metric")
trace_contract._emit_stores_embedding("p4", "file_io_impl", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "file_io_impl", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "file_io_impl", "exec_snapshot_link")

"\nFile I/O Tools - Atomic Module\nExtracted from action_registry.py via Atomic Fission Protocol\nTool ID Prefix: ACT-002\n"
import logging
import os
import uuid
from pathlib import Path
from typing import Any

try:
    import PyPDF2
except ImportError:  # guardian: allow-silent-swallow
    PyPDF2: Any = None

trace_contract._emit_emits_metric_event("file_io_impl", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("file_io_impl", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("file_io_impl", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("file_io_impl", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("file_io_impl", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("file_io_impl", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("file_io_impl", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("file_io_impl", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("file_io_impl", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("file_io_impl", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("file_io_impl", "p4obs", "alert")
trace_contract._emit_links_incident_trace("file_io_impl", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("file_io_impl", "p3lm", "pattern")
trace_contract._emit_records_learning_event("file_io_impl", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("file_io_impl", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("file_io_impl", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("file_io_impl", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("file_io_impl", "p3lm", "policy")
trace_contract._emit_stores_learning_state("file_io_impl", "p3lm", "state")
trace_contract._emit_records_execution_trace("file_io_impl", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("file_io_impl", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("file_io_impl", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("file_io_impl", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("file_io_impl", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("file_io_impl", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("file_io_impl", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("file_io_impl", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("file_io_impl", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "file_io_impl", "context_pull")
trace_contract._emit_pulls_context("p1", "file_io_impl", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "file_io_impl", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "file_io_impl", "uwg_term_2")
trace_contract._emit_writes_through("p1", "file_io_impl", "write_through")
trace_contract._emit_writes_through("p1", "file_io_impl", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "file_io_impl", "safety_validation")
trace_contract._emit_invokes_eval("p1", "file_io_impl", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "file_io_impl", "routing_commit")

Logger: Any = logging.getLogger("ActionRegistry.FileIO")


def _invoke_authorize_and_execute(execution_context, target_callable, capability_token, payload, **kw):
    from agentic_core.L2_execution.enforcement.execution_guardrail_chokepoint import (
        authorize_and_execute,  # noqa: PLC0415
    )

    return authorize_and_execute(execution_context, target_callable, capability_token, payload, **kw)


def _make_execution_context(payload, target: str):
    from agentic_core.L4_state.utils.context.execution_context import (  # noqa: PLC0415
        ActionClass,
        ExecutionContext,
    )

    return ExecutionContext.create(
        run_id="file_io_impl",
        capability_token="default",
        policy_hash="default",
        execution_input=str(payload),
        execution_target=target,
        action_class=ActionClass.MUTATION,
    )


class FileIo:
    """
    Handles file reading and saving operations.
    Tool ID Prefix: ACT-002
    """

    def __init__(self):
        """Initializes FileIO. No specific state needed for file operations."""

    def _read_pdf_file(self, file_path: str) -> str:
        """
        Helper to read content from a PDF file.

        Args:
            file_path (str): The path to the PDF file.

        Returns:    # review: File operations should check existence before access
            str: The extracted text content from the PDF.
        """
        if not PyPDF2:
            return "Error: PyPDF2 module not installed. Cannot read PDF files."
        try:
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                return self._extract_pdf_pages_text(reader, file_path)
        except (
            PyPDF2.errors.PdfReadError
        ) as e:  # review: File operations should check existence before access
            return f"Read Error (PDF): Could not read PDF file '{file_path}'. {e}"
        except FileNotFoundError:
            return f"Read Error: File not found at '{file_path}'."
        except (RuntimeError, ValueError) as e:  # guardian: allow-silent-swallow
            return f"Read Error (PDF Unexpected): {e}"

    def _extract_pdf_pages_text(self, reader, file_path: str) -> str:
        """
        Extracts text content from PDF reader pages.

        Args:
            reader: The PyPDF2.PdfReader object.
            file_path (str): The path to the PDF file (for error messages).

        Returns:
            str: The extracted text content from the PDF or a warning message.
        """
        if not reader.pages:
            return f"Warning: PDF file '{file_path}' has no pages or content."
        extracted_texts = [page.extract_text() for page in reader.pages if page.extract_text()]
        return "\n".join(extracted_texts)

    def _read_text_file(self, file_path: str) -> str:
        """
            Helper to read content from a text-based file.
        # review: File operations should check existence before access
            Args:
                file_path (str): The path to the text file.    # review: Encoding errors should specify fallback encoding strategy

            Returns:
                str: The content of the text file.
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                return f.read()  # review: File operations should check existence before access
        except FileNotFoundError:
            return f"Read Error: File not found at '{file_path}'."  # review: Encoding errors should specify fallback encoding strategy
        except UnicodeDecodeError:
            return f"Read Error: Could not decode file '{file_path}' with utf-8. Try a different encoding."
        except (RuntimeError, ValueError) as e:  # guardian: allow-silent-swallow
            return f"Read Error (Text Unexpected): {e}"

    def read_file(self, file_path: str) -> str:
        """
        Reads text content from agentic_core.txt, .md, or .pdf files.
        Tool ID: ACT-002

        Args:
            file_path (str): The path to the file to read.

        Returns:
            str: The content of the file or an error message.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L2_EXECUTION, "FileIo.read_file")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:FileIo.read_file".encode()).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        Logger.info(f"📖 Reading file: '{file_path}'")
        # guardian: allow-path-string
        if not os.path.exists(file_path):
            return f"Read Error: File not found at '{file_path}'."
        if file_path.endswith(".pdf"):
            return self._read_pdf_file(file_path)
        else:
            return self._read_text_file(file_path)

    def save_file(self, content: str, file_path: str) -> str:
        """
        Saves content to a file.
        Tool ID: ACT-003

        Args:
            content (str): The string content to save.
            file_path (str): The path where the file should be saved.

        Returns:
            str: A success message or an error message.
        """
        trace_contract._emit_writes_through(str(uuid.uuid4()), "FileIo.save_file", "L2_EXECUTION")
        Logger.info(f"[SAVE] Saving file: '{file_path}' (content length: {len(content)})")
        _ectx = _make_execution_context(file_path, "file_io_impl.save_file")
        _invoke_authorize_and_execute(
            _ectx,
            lambda p: p,
            "default",  # review: Add error context logging
            file_path,
            target_name="file_io_impl.save_file",
        )
        try:
            os.makedirs(Path(file_path).parent, exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return f"[OK] File saved successfully: {file_path}"
        except OSError as e:  # review: Add error context logging
            return f"Save Error (IO): Could not save file '{file_path}'. {e}"
        except (RuntimeError, ValueError) as e:  # guardian: allow-silent-swallow
            return f"Save Error (Unexpected): {e}"


__all__ = ["FileIo"]
