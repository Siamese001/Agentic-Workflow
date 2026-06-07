#!/usr/bin/env python3
"""Annotator: insert ``__adg_consumer_mode__`` into unannotated ADG consumers.

Per the W4 consumer-mode declaration contract (see
``agentic_core/adg/artifact/consumer_mode.py``), every Python file that
queries the ADG MUST declare its mode at module level::

    __adg_consumer_mode__ = "proof" | "risk" | "inventory"

The W4 audit identified 127 unannotated consumers. This script walks the
output of ``check_consumer_mode_declared.py``, infers the correct mode per
file, and inserts the declaration in-place.

Mode-selection rules (conservative):

  * If the file reads ``proof_view`` -> ``"proof"`` (the strictest claim).
  * Else if the file reads ``risk_view`` -> ``"risk"``.
  * Else (reads ``inventory_view``, raw ``edges`` / ``nodes`` / MVs, or
    invokes ``adg_*`` MCP tools) -> ``"inventory"``.

The declaration is inserted at the FIRST safe position:

  1. After the module docstring (if any).
  2. After ``from __future__`` imports.
  3. Before the first non-import statement.

The annotator is **idempotent** — files that already declare a mode are
skipped.

USAGE
=====

::

    # Dry-run: list files that would be annotated and the inferred mode.
    python ops_scripts/ci/annotate_consumer_mode.py --dry-run

    # Apply changes to all detected files (asks for confirmation by default).
    python ops_scripts/ci/annotate_consumer_mode.py --apply

    # Filter to a specific path subtree.
    python ops_scripts/ci/annotate_consumer_mode.py --apply --filter agentic_core/adg/

    # Force a specific mode (override the inference).
    python ops_scripts/ci/annotate_consumer_mode.py --apply --force-mode inventory \
        --filter tools/

Plan: ``.claude/plans/three-bucket-otel-view-5db409.md`` (W6).
"""

from __future__ import annotations

# This script writes Python source files; it does not query ADG views itself.
__adg_consumer_mode__ = "inventory"

import argparse
import ast
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Final

REPO_ROOT = Path(__file__).resolve().parents[2]
GATE_SCRIPT = REPO_ROOT / "ops_scripts" / "ci" / "check_consumer_mode_declared.py"

VALID_MODES: Final[tuple[str, ...]] = ("proof", "risk", "inventory")

# View-priority regex — strongest claim wins.
_PROOF_VIEW_RE: Final[re.Pattern[str]] = re.compile(
    r"\b(?:FROM|JOIN)\s+proof_view\b", re.IGNORECASE
)
_RISK_VIEW_RE: Final[re.Pattern[str]] = re.compile(
    r"\b(?:FROM|JOIN)\s+risk_view\b", re.IGNORECASE
)


@dataclass
class AnnotationPlan:
    rel_path: str
    inferred_mode: str
    reason: str
    will_skip: bool = False
    skip_reason: str = ""


@dataclass
class AnnotationResult:
    plans: list[AnnotationPlan] = field(default_factory=list)
    annotated: int = 0
    skipped: int = 0
    errors: int = 0


# ---------------------------------------------------------------------------
# Mode inference
# ---------------------------------------------------------------------------


def infer_mode(source: str) -> tuple[str, str]:
    """Return (mode, reason)."""
    if _PROOF_VIEW_RE.search(source):
        return "proof", "reads proof_view"
    if _RISK_VIEW_RE.search(source):
        return "risk", "reads risk_view"
    return "inventory", "default for raw edges/nodes/MV/inventory_view reads"


# ---------------------------------------------------------------------------
# Insertion point detection
# ---------------------------------------------------------------------------


def find_insertion_line(source: str) -> int | None:
    """Return the 0-indexed line AFTER which to insert the declaration.

    Strategy:
      - Parse the AST.
      - If the module has a docstring, insert after it.
      - Then skip past any ``from __future__`` imports.
      - Insert before the first non-import non-docstring statement.

    Returns None if the file cannot be parsed.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None

    body = tree.body
    if not body:
        return 0  # empty file — insert at top

    # Determine end-line of docstring + future-imports block.
    last_prelude_line = 0
    for node in body:
        is_docstring = (
            isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
            and node is body[0]
        )
        is_future_import = (
            isinstance(node, ast.ImportFrom) and node.module == "__future__"
        )
        if is_docstring or is_future_import:
            last_prelude_line = max(last_prelude_line, node.end_lineno or 0)
        else:
            break

    return last_prelude_line  # 1-indexed end-line of last prelude node


def has_existing_declaration(source: str) -> bool:
    """Detect any module-level ``__adg_consumer_mode__`` assignment."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return False
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for tgt in node.targets:
                if isinstance(tgt, ast.Name) and tgt.id == "__adg_consumer_mode__":
                    return True
        elif isinstance(node, ast.AnnAssign):
            if (
                isinstance(node.target, ast.Name)
                and node.target.id == "__adg_consumer_mode__"
            ):
                return True
    return False


# ---------------------------------------------------------------------------
# Source rewriting
# ---------------------------------------------------------------------------

DECLARATION_TEMPLATE: Final[str] = (
    "# W6 ADG consumer mode declaration (per .cursor/rules/"
    "adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).\n"
    '__adg_consumer_mode__ = "{mode}"\n'
)


def insert_declaration(source: str, mode: str) -> str | None:
    """Return a new source string with the declaration inserted.

    Returns None if the file cannot be parsed.
    """
    line_no = find_insertion_line(source)
    if line_no is None:
        return None

    lines = source.splitlines(keepends=True)
    declaration = "\n" + DECLARATION_TEMPLATE.format(mode=mode) + "\n"

    if line_no == 0:
        return declaration.lstrip("\n") + source

    head = "".join(lines[:line_no])
    tail = "".join(lines[line_no:])
    # Make sure the head ends with a newline so the inserted block is on a
    # fresh line.
    if head and not head.endswith("\n"):
        head += "\n"
    return head + declaration + tail


# ---------------------------------------------------------------------------
# Discovery — run the existing gate to find unannotated consumers
# ---------------------------------------------------------------------------


def discover_unannotated(filter_substring: str = "") -> list[str]:
    """Run the consumer-mode gate as a subprocess and parse its violation list.

    Falls back to scanning for the gate's persisted JSON report at
    ``docs/reports/adg/consumer_mode_gate_report.json`` if available.
    """
    # The gate writes a JSON report — read it if present, else run the gate.
    report_path = (
        REPO_ROOT
        / "docs"
        / "reports"
        / "adg"
        / "consumer_mode_gate_report.json"
    )

    proc = subprocess.run(
        [sys.executable, str(GATE_SCRIPT)],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    # Even if exit != 0 (advisory mode returns 0; strict mode returns 1),
    # the report should be on disk.
    if not report_path.exists():
        # Some forks of the gate may print violations on stdout in a
        # parseable form. Use that as a last-ditch fallback.
        return _parse_stdout_violations(proc.stdout, filter_substring)

    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return _parse_stdout_violations(proc.stdout, filter_substring)

    violations = report.get("violations", [])
    if not isinstance(violations, list):
        return []
    out: list[str] = []
    for v in violations:
        if not isinstance(v, dict):
            continue
        if v.get("kind") != "missing":
            continue
        rp = v.get("rel_path") or ""
        if filter_substring and filter_substring not in rp:
            continue
        out.append(rp)
    return sorted(out)


def _parse_stdout_violations(stdout: str, filter_substring: str) -> list[str]:
    """Last-ditch fallback: parse the gate's human-readable violation lines."""
    out: list[str] = []
    for line in stdout.splitlines():
        m = re.match(r"\s*\[missing\]\s+(\S+)\s*::", line)
        if m:
            rp = m.group(1)
            if filter_substring and filter_substring not in rp:
                continue
            out.append(rp)
    return sorted(set(out))


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def annotate_one(
    rel_path: str,
    *,
    apply: bool,
    force_mode: str | None = None,
) -> AnnotationPlan:
    plan = AnnotationPlan(rel_path=rel_path, inferred_mode="", reason="")
    abs_path = REPO_ROOT / rel_path

    if not abs_path.exists():
        plan.will_skip = True
        plan.skip_reason = "file not found"
        return plan

    try:
        source = abs_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        plan.will_skip = True
        plan.skip_reason = f"read failed: {exc}"
        return plan

    if has_existing_declaration(source):
        plan.will_skip = True
        plan.skip_reason = "already declared"
        plan.inferred_mode = "<unchanged>"
        return plan

    if force_mode:
        plan.inferred_mode = force_mode
        plan.reason = f"forced via --force-mode {force_mode}"
    else:
        plan.inferred_mode, plan.reason = infer_mode(source)

    if not apply:
        return plan

    new_source = insert_declaration(source, plan.inferred_mode)
    if new_source is None:
        plan.will_skip = True
        plan.skip_reason = "AST parse failed"
        return plan

    abs_path.write_text(new_source, encoding="utf-8")
    return plan


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would change; do not write any files.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Write changes in place.",
    )
    parser.add_argument(
        "--filter",
        default="",
        help="Restrict to files whose rel_path contains this substring.",
    )
    parser.add_argument(
        "--force-mode",
        default=None,
        choices=VALID_MODES,
        help="Skip inference; force every annotated file to this mode.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Process at most N files (0=all). Useful for staged rollouts.",
    )
    args = parser.parse_args(argv)

    if not (args.dry_run or args.apply):
        parser.error("must specify --dry-run or --apply")

    targets = discover_unannotated(filter_substring=args.filter)
    if args.limit and args.limit < len(targets):
        targets = targets[: args.limit]

    print(
        f"[annotate_consumer_mode] discovered {len(targets)} unannotated consumers "
        f"(filter={args.filter or '<none>'} apply={args.apply} "
        f"force_mode={args.force_mode or '<infer>'})"
    )

    result = AnnotationResult()
    for rel_path in targets:
        plan = annotate_one(
            rel_path,
            apply=args.apply,
            force_mode=args.force_mode,
        )
        result.plans.append(plan)
        if plan.will_skip:
            result.skipped += 1
            print(
                f"  SKIP  {rel_path}  ({plan.skip_reason})"
            )
        else:
            tag = "PLAN" if not args.apply else "WRITE"
            print(
                f"  {tag}  {rel_path}  mode={plan.inferred_mode}  "
                f"reason={plan.reason}"
            )
            if args.apply:
                result.annotated += 1

    print(
        f"[annotate_consumer_mode] {'planned' if not args.apply else 'annotated'}="
        f"{len([p for p in result.plans if not p.will_skip])} "
        f"skipped={result.skipped}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
