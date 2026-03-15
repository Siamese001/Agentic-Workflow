"""
AST-based detector for unsafe I/O and subprocess usage.

This module provides tools to detect potentially unsafe file I/O and subprocess
operations that could bypass the mutation fence and write to protected roots.
"""

import ast
from dataclasses import dataclass
from pathlib import Path


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
        run_id="unsafe_io_detector",
        capability_token="default",
        policy_hash="default",
        execution_input=str(payload),
        execution_target=target,
        action_class=ActionClass.PRIVILEGED_LOCAL,
    )


from agentic_core.L0_routing.config import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
)
from agentic_core.L0_routing.config.path_constants import (
    TESTS_DIR,
    TOOLS_DIR,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
)


@dataclass
class UnsafePattern:
    """Represents an unsafe pattern found in code."""

    file_path: str
    line_number: int
    pattern_type: str
    node_text: str
    context: str


class UnsafePatternVisitor(ast.NodeVisitor):
    """AST visitor to detect unsafe I/O and subprocess patterns."""

    # File write patterns
    WRITE_MODES = {"w", "a", "x", "wb", "ab", "xb"}
    UNSAFE_FUNCTIONS = {
        # File operations
        "open",
        "Path.write_text",
        "Path.write_bytes",
        "os.remove",
        "os.unlink",
        "os.rename",
        "os.replace",
        "shutil.rmtree",
        "shutil.move",
        # Subprocess operations
        "subprocess.run",
        "subprocess.call",
        "subprocess.check_call",
        "subprocess.check_output",
        "subprocess.Popen",
    }

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.findings: list[UnsafePattern] = []

    def visit_Call(self, node: ast.Call):
        """Visit function calls to detect unsafe patterns."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "UnsafePatternVisitor.visit_Call")
        import hashlib as _hashlib  # noqa: PLC0415
        _seg_hash = _hashlib.sha256(f"{_trace_id}:UnsafePatternVisitor.visit_Call".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        # Check for open() with write modes
        if isinstance(node.func, ast.Name) and node.func.id == "open":
            if len(node.args) >= 2:
                mode_arg = node.args[1]
                if isinstance(mode_arg, ast.Constant) and mode_arg.value in self.WRITE_MODES:
                    self.add_finding(node, "open_write")

        # Check for Path.write_text/write_bytes
        elif isinstance(node.func, ast.Attribute):
            if node.func.attr in {"write_text", "write_bytes"}:
                self.add_finding(node, f"path_{node.func.attr}")
            elif node.func.attr in {"remove", "unlink", "rename", "replace"}:
                if isinstance(node.func.value, ast.Name) and node.func.value.id == "os":
                    self.add_finding(node, f"os_{node.func.attr}")
            elif node.func.attr in {"rmtree", "move"}:
                if isinstance(node.func.value, ast.Name) and node.func.value.id == "shutil":
                    self.add_finding(node, f"shutil_{node.func.attr}")
            elif node.func.attr in {"run", "call", "check_call", "check_output", "Popen"}:
                if isinstance(node.func.value, ast.Name) and node.func.value.id == "subprocess":
                    self.add_finding(node, f"subprocess_{node.func.attr}")

        self.generic_visit(node)

    def add_finding(self, node: ast.AST, pattern_type: str):
        """Add a finding to the list."""
        line_text = ast.get_source_segment(self.source, node) if hasattr(self, "source") else ""
        context = self._get_context(node)

        finding = UnsafePattern(
            file_path=self.file_path,
            line_number=node.lineno,
            pattern_type=pattern_type,
            node_text=line_text,
            context=context,
        )
        self.findings.append(finding)

    def _get_context(self, node: ast.AST) -> str:
        """Get context line for the finding."""
        if hasattr(self, "source_lines"):
            line_idx = node.lineno - 1
            if 0 <= line_idx < len(self.source_lines):
                return self.source_lines[line_idx].strip()
        return ""

    def visit(self, node: ast.AST, source: str = None) -> list[UnsafePattern]:
        """Visit AST with optional source code for context."""
        if source:
            self.source = source
            self.source_lines = source.splitlines()
        super().visit(node)
        return self.findings


def scan_for_unsafe_patterns(code: str, file_path: str) -> list[UnsafePattern]:
    """
    Scan Python code for unsafe I/O and subprocess patterns.

    Args:
        code: Python source code to scan
        file_path: Path to the file being scanned (for reporting)

    Returns:
        List of unsafe patterns found
    """
    _ectx = _make_execution_context(file_path, "unsafe_io_detector.scan_for_unsafe_patterns")
    _invoke_authorize_and_execute(
        _ectx,
        lambda p: p,
        "default",
        file_path,
        target_name="unsafe_io_detector.scan_for_unsafe_patterns",
    )
    try:
        tree = ast.parse(code)
        visitor = UnsafePatternVisitor(file_path)
        return visitor.visit(tree, code)
    # guardian: allow-silent-swallow
    except SyntaxError:
        # Return empty list for files that can't be parsed
        return []


def scan_directory_for_unsafe_patterns(
    directory: Path, recursive: bool = True, file_pattern: str = "*.py"
) -> list[UnsafePattern]:
    """
    Scan a directory for unsafe patterns in Python files.

    Args:
        directory: Directory to scan
        recursive: Whether to scan subdirectories
        file_pattern: File pattern to match (default: *.py)

    Returns:
        List of unsafe patterns found
    """
    all_findings = []

    if recursive:
        files = directory.rglob(file_pattern)
    else:
        files = directory.glob(file_pattern)

    for file_path in files:
        if file_path.is_file():
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()
                findings = scan_for_unsafe_patterns(content, str(file_path))
                all_findings.extend(findings)
            # guardian: allow-silent-swallow
            except Exception:
                # Skip files that can't be read or parsed
                continue

    return all_findings


def get_scoped_directories(repo_root: Path) -> list[Path]:
    """Get the list of directories that should be scanned for unsafe patterns."""
    scoped_dirs = [
        repo_root / AGENTIC_CORE_DIR / "L0_routing" / "reasoning",
        repo_root / AGENTIC_CORE_DIR / "L1_cognition" / "reasoning",
        repo_root / AGENTIC_CORE_DIR / "L2_execution" / "reasoning",
        repo_root / AGENTIC_CORE_DIR / "L3_orchestration" / "reasoning",
        repo_root / AGENTIC_CORE_DIR / APPS_LIC_DIR / "reasoning",
        repo_root / AGENTIC_CORE_DIR / APPS_RG_DIR / "reasoning",
        repo_root / AGENTIC_CORE_DIR / APPS_SHARED_DIR / "reasoning",
        repo_root / AGENTIC_CORE_DIR / TOOLS_DIR,
        repo_root / AGENTIC_CORE_DIR / "L0_routing" / "scripts",
        repo_root / AGENTIC_CORE_DIR / "L1_cognition" / "scripts",
        repo_root / AGENTIC_CORE_DIR / "L2_execution" / "scripts",
    ]

    return [d for d in scoped_dirs if d.exists()]


def is_protected_root_path(path_str: str) -> bool:
    """Check if a path string points to a protected root."""
    path = Path(path_str).resolve()

    protected_roots = {AGENTIC_CORE_DIR, TESTS_DIR, ".github"}

    # Check if any part of the path starts with a protected root
    for part in path.parts:
        if part in protected_roots:
            return True

    return False
