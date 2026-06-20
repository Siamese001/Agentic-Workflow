"""L6 Observer-Law CI Gate.

Plan: .codex/plans/l6-doctrinal-alignment-noninvasive-b9d3f5.md W4.

Forbids `agentic_core/L6_system_learning/` (L6 active surface) from importing modules
that perform write-side actions on L0..L5 runtime layers. The L6
observer-law doctrine (chapter 06.2) requires that L6 reads runtime
exhaust but never writes back to runtime — the only path from L6 back
into runtime is the UWG promotion gate (chapter 06.7).

Heuristic
---------
For every .py file under agentic_core/L6_system_learning/ (excluding __pycache__,
logs/, raw/, snapshots/), parse the AST for top-level `import` and
`from ... import ...` statements. Flag any whose source module path
matches:

- `agentic_core.L0_routing.*`
- `agentic_core.L1_cognition.*`
- `agentic_core.L2_execution.*`
- `agentic_core.L3_orchestration.*`
- `agentic_core.L4_state.*`
- `agentic_core.L5_*`

AND whose final segment matches one of the writer-suffix patterns:
`_writer`, `_emitter`, `_dispatcher`, `_router`, `_executor`,
`_invoker`, `_publisher`, `_promoter`. Type-only / contract / config
imports are allowed.

Modes
-----
- Default: advisory (exit 0, prints findings).
- Fail-closed: set `L6_OBSERVER_LAW_FAIL_CLOSED=1` (exit 2 on findings).
- Bypass: set `L6_OBSERVER_LAW_BYPASS=1` (exit 0, log bypass row).

Output
------
Writes findings to `artifacts/governance/l6_observer_law_violations.json`.
"""
from __future__ import annotations

import ast
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SL_ROOT = REPO_ROOT / "agentic_core" / "L6_system_learning"
SKIP_SUBDIRS = {"__pycache__", "logs", "raw", "snapshots"}

FORBIDDEN_LAYER_PREFIXES = (
    "agentic_core.L0_routing",
    "agentic_core.L1_cognition",
    "agentic_core.L2_execution",
    "agentic_core.L3_orchestration",
    "agentic_core.L4_state",
    "agentic_core.L5_",  # any L5_<name>
)

WRITER_SUFFIXES = (
    "_writer",
    "_emitter",
    "_dispatcher",
    "_router",
    "_executor",
    "_invoker",
    "_publisher",
    "_promoter",
)


@dataclass
class Finding:
    file: str
    line: int
    module: str
    reason: str

    def to_dict(self) -> dict[str, object]:
        return {
            "file": self.file,
            "line": self.line,
            "module": self.module,
            "reason": self.reason,
        }


def _is_forbidden(module_name: str) -> str | None:
    """Return reason string if module_name violates observer-law, else None."""
    if not any(module_name.startswith(p) for p in FORBIDDEN_LAYER_PREFIXES):
        return None
    last_segment = module_name.rsplit(".", 1)[-1]
    if any(last_segment.endswith(suf) for suf in WRITER_SUFFIXES):
        return f"writer-suffix import from runtime layer ({last_segment})"
    return None


def _type_checking_line_numbers(tree: ast.Module) -> frozenset[int]:
    """Lines inside ``if TYPE_CHECKING:`` blocks are typing-only (not runtime imports)."""
    lines: set[int] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.If):
            continue
        test = node.test
        is_tc = (
            isinstance(test, ast.Name)
            and test.id == "TYPE_CHECKING"
        ) or (
            isinstance(test, ast.Attribute)
            and isinstance(test.value, ast.Name)
            and test.value.id == "typing"
            and test.attr == "TYPE_CHECKING"
        )
        if not is_tc:
            continue
        for child in ast.walk(node):
            if isinstance(child, (ast.Import, ast.ImportFrom)) and hasattr(child, "lineno"):
                lines.add(int(child.lineno))
    return frozenset(lines)


def _scan_file(path: Path) -> list[Finding]:
    try:
        source = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError:
        return []
    findings: list[Finding] = []
    rel = path.relative_to(REPO_ROOT).as_posix()
    tc_lines = _type_checking_line_numbers(tree)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if node.lineno in tc_lines:
                continue
            for alias in node.names:
                reason = _is_forbidden(alias.name)
                if reason:
                    findings.append(
                        Finding(
                            file=rel, line=node.lineno, module=alias.name, reason=reason
                        )
                    )
        elif isinstance(node, ast.ImportFrom):
            if node.lineno in tc_lines:
                continue
            if node.module is None:
                continue
            # Compose qualified module + last segment from the imported names
            # to detect `from agentic_core.L0_routing.uwg_writer import X`.
            for alias in node.names:
                qualified = f"{node.module}.{alias.name}"
                # First check the source module itself (e.g. uwg_writer module).
                reason = _is_forbidden(node.module)
                if reason:
                    findings.append(
                        Finding(
                            file=rel,
                            line=node.lineno,
                            module=node.module,
                            reason=reason,
                        )
                    )
                # Then check qualified import in case a writer is named directly.
                if any(qualified.startswith(p) for p in FORBIDDEN_LAYER_PREFIXES):
                    last = alias.name
                    if any(last.endswith(suf) for suf in WRITER_SUFFIXES):
                        findings.append(
                            Finding(
                                file=rel,
                                line=node.lineno,
                                module=qualified,
                                reason=f"writer-suffix symbol from runtime layer ({last})",
                            )
                        )
    return findings


def _iter_files() -> list[Path]:
    files: list[Path] = []
    if not SL_ROOT.exists():
        return files
    for root, dirnames, filenames in os.walk(SL_ROOT):
        # In-place prune of skip dirs.
        dirnames[:] = [d for d in dirnames if d not in SKIP_SUBDIRS]
        for fname in filenames:
            if fname.endswith(".py"):
                files.append(Path(root) / fname)
    return files


def main() -> int:
    if os.environ.get("L6_OBSERVER_LAW_BYPASS") == "1":
        print("[l6_observer_law] BYPASS active (L6_OBSERVER_LAW_BYPASS=1)")
        return 0

    findings: list[Finding] = []
    for path in _iter_files():
        findings.extend(_scan_file(path))

    out_dir = REPO_ROOT / "artifacts" / "governance"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "l6_observer_law_violations.json"
    out_path.write_text(
        json.dumps(
            {"findings": [f.to_dict() for f in findings], "count": len(findings)},
            indent=2,
        ),
        encoding="utf-8",
    )

    if not findings:
        print(f"[l6_observer_law] OK — 0 findings ({out_path.relative_to(REPO_ROOT)})")
        return 0

    print(f"[l6_observer_law] {len(findings)} finding(s):")
    for f in findings:
        print(f"  {f.file}:{f.line}  {f.module}  ({f.reason})")
    print(f"[l6_observer_law] report: {out_path.relative_to(REPO_ROOT)}")

    if os.environ.get("L6_OBSERVER_LAW_FAIL_CLOSED") == "1":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
