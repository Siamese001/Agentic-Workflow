"""3.5: Reasoning output contract type + scanner.

ReasoningOutput is the mandatory output envelope for all domain agent .process()
and .execute() methods.  A contract scanner (scan_for_violations) checks all
agents in apps_rg/ and apps_lic/ for methods returning bare dicts instead of
ReasoningOutput.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config.path_constants import (
    APPS_LIC_DIR,
    APPS_RG_DIR,
)
from tqdm import tqdm


@dataclass
class ReasoningOutput:
    """Mandatory output envelope for agent .process()/.execute() methods.

    Fields:
        status   — "success" | "partial" | "error" | "skipped"
        payload  — domain-specific result data
        trace_id — correlation ID for cross-agent tracing
        agent    — name of the agent that produced this output
        errors   — list of error messages (empty on success)
    """

    status: str
    payload: dict[str, Any] = field(default_factory=dict)
    trace_id: str = ""
    agent: str = ""
    errors: list[str] = field(default_factory=list)

    def is_success(self) -> bool:
        return self.status == "success"

    def is_error(self) -> bool:
        return self.status == "error"

    @classmethod
    def success(cls, payload: dict[str, Any], agent: str = "", trace_id: str = "") -> ReasoningOutput:
        return cls(status="success", payload=payload, agent=agent, trace_id=trace_id)

    @classmethod
    def error(cls, errors: list[str], agent: str = "", trace_id: str = "") -> ReasoningOutput:
        return cls(status="error", errors=errors, agent=agent, trace_id=trace_id)

    @classmethod
    def skipped(cls, reason: str, agent: str = "", trace_id: str = "") -> ReasoningOutput:
        return cls(status="skipped", payload={"reason": reason}, agent=agent, trace_id=trace_id)


def scan_for_violations(scan_dirs: list[Path] | None = None) -> list[tuple[str, int, str]]:
    """Scan agent files for methods that return bare dict instead of ReasoningOutput.

    Returns list of (file_path, lineno, description) for each violation.

    Heuristic: any method named process/execute/run that has a ``return {``
    statement and does NOT also have a ``return ReasoningOutput`` anywhere in the
    same function is flagged.
    """
    if scan_dirs is None:
        repo_root = Path(__file__).resolve().parents[2]
        scan_dirs = [repo_root / APPS_RG_DIR, repo_root / APPS_LIC_DIR]

    violations: list[tuple[str, int, str]] = []

    for scan_dir in tqdm(scan_dirs, desc="Processing", unit="item"):
        if not scan_dir.exists():
            continue
        for py_file in tqdm(sorted(scan_dir.rglob("*.py")), desc="Processing", unit="item"):
            try:
                source = py_file.read_text(encoding="utf-8", errors="replace")
                tree = ast.parse(source, filename=str(py_file))
            except (
                SyntaxError,
                OSError,
            ):  # review: Multiple exceptions (SyntaxError, OSError) need specific handling
                continue

            for node in tqdm(ast.walk(tree), desc="Processing", unit="item"):
                if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                if node.name not in ("process", "execute", "run"):
                    continue

                has_bare_dict_return = False
                has_reasoning_output_return = False

                for child in tqdm(ast.walk(node), desc="Processing", unit="item"):
                    if isinstance(child, ast.Return) and child.value is not None:
                        if isinstance(child.value, ast.Dict):
                            has_bare_dict_return = True
                        elif isinstance(child.value, ast.Call):
                            func = child.value.func
                            name = ""
                            if isinstance(func, ast.Name):
                                name = func.id
                            elif isinstance(func, ast.Attribute):
                                name = func.attr
                            if name == "ReasoningOutput":
                                has_reasoning_output_return = True

                if has_bare_dict_return and not has_reasoning_output_return:
                    violations.append(
                        (
                            str(py_file),
                            node.lineno,
                            f"{node.name}() returns bare dict — wrap in ReasoningOutput",
                        ),
                    )

    return violations


__all__ = ["ReasoningOutput", "scan_for_violations"]
