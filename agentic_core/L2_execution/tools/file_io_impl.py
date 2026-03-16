from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_routes_through,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "file_io_impl")
emit_determinism_digest("p0", "file_io_impl")

_emit_dispatches_healing_run("p1", "file_io_impl", "L2")
_emit_routes_through("p1", "file_io_impl", "L2")
_emit_escalates_to_human("p1", "file_io_impl", "L2")
_emit_reads_policy_state("p1", "file_io_impl", "L2")

_emit_applies_guardrail("p0", "file_io_impl", "p0_governance")
_emit_snapshots_state("p0", "file_io_impl", "state_snapshot")

"\nFile I/O Tools - Atomic Module\nExtracted from action_registry.py via Atomic Fission Protocol\nTool ID Prefix: ACT-002\n"
import logging
import os
import uuid
from pathlib import Path
from typing import Any

try:
    import PyPDF2
except ImportError:
    PyPDF2: Any = None
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_writes_through,
)

Logger: Any = logging.getLogger("ActionRegistry.FileIO")


def _invoke_authorize_and_execute(execution_context, target_callable, capability_token, payload, **kw):
    from agentic_core.L2_execution.enforcement.execution_guardrail_chokepoint import (
        authorize_and_execute,  # noqa: PLC0415
    )

    return authorize_and_execute(execution_context, target_callable, capability_token, payload, **kw)


def _make_execution_context(payload, target: str):
    from agentic_core.L2_execution.context.execution_context import (  # noqa: PLC0415
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

        Returns:
            str: The extracted text content from the PDF.
        """
        if not PyPDF2:
            return "Error: PyPDF2 module not installed. Cannot read PDF files."
        try:
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                return self._extract_pdf_pages_text(reader, file_path)
        except PyPDF2.errors.PdfReadError as e:
            return f"Read Error (PDF): Could not read PDF file '{file_path}'. {e}"
        except FileNotFoundError:
            return f"Read Error: File not found at '{file_path}'."
        # guardian: allow-silent-swallow
        except Exception as e:
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

        Args:
            file_path (str): The path to the text file.

        Returns:
            str: The content of the text file.
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return f"Read Error: File not found at '{file_path}'."
        except UnicodeDecodeError:
            return f"Read Error: Could not decode file '{file_path}' with utf-8. Try a different encoding."
        # guardian: allow-silent-swallow
        except Exception as e:
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
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "FileIo.read_file")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:FileIo.read_file".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

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
        _emit_writes_through(str(uuid.uuid4()), "FileIo.save_file", "L2_EXECUTION")
        Logger.info(f"[SAVE] Saving file: '{file_path}' (content length: {len(content)})")
        _ectx = _make_execution_context(file_path, "file_io_impl.save_file")
        _invoke_authorize_and_execute(
            _ectx,
            lambda p: p,
            "default",
            file_path,
            target_name="file_io_impl.save_file",
        )
        try:
            os.makedirs(Path(file_path).parent, exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return f"[OK] File saved successfully: {file_path}"
        except OSError as e:
            return f"Save Error (IO): Could not save file '{file_path}'. {e}"
        # guardian: allow-silent-swallow
        except Exception as e:
            return f"Save Error (Unexpected): {e}"


__all__ = ["FileIo"]
