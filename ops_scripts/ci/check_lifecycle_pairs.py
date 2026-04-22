"""CI gate: enforce resource-lifecycle open/close pairs.

Purpose
-------
ADG catches forbidden imports. Expected-wiring catches positive call-site
assertions. Neither sees a resource leak — a `sqlite3.connect(...)` or
`open(...)` or `redis.Redis(...)` call whose result is never closed and
never assigned to an instance attribute. That class of bug shipped the
ChromaDB `NotFoundError` collection-fetch leak recently.

Scope
-----
Reads ``config/lifecycle_pairs.yaml`` and, for each declared opener, AST-
scans every tracked Python file under the code roots. An opener call is
SATISFIED when any of the declared closers resolves in the same function
(or class, for ``attr:self.*``):

- ``with_stmt``        — opener appears inside a `with` statement
- ``.<method>()``      — a call to that method on any name exists in the
                         enclosing function body
- ``attr:self.<name>`` — opener's result is assigned to ``self.<name>``
                         anywhere in the enclosing class (covers
                         long-lived owner-managed resources)

Ratchet
-------
Pre-existing debt is frozen in
``ops_scripts/ci/baselines/lifecycle_pairs_baseline.json``. The gate fails
only on NEW leaks. Regenerate with ``--regenerate-baseline``.

Scope exclusions
----------------
Canonical ``GLOBAL_EXCLUDED_DIRS`` plus frozen archive subtrees. Tests are
excluded — fixtures legitimately open handles for teardown verification.

Exit 0 on clean, 1 on net-new leaks, 2 on config error.
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path

try:
    import yaml  # type: ignore[import-untyped]
except ImportError:
    sys.stderr.write("[check_lifecycle_pairs] PyYAML required\n")
    raise SystemExit(2) from None

try:
    from tqdm import tqdm
except ImportError:

    def tqdm(iterable, **_):  # type: ignore[no-redef]
        return iterable


try:
    from agentic_core.L0_routing.config.path_constants import GLOBAL_EXCLUDED_DIRS
except ImportError as _exc:
    sys.stderr.write(f"[check_lifecycle_pairs] cannot import GLOBAL_EXCLUDED_DIRS: {_exc}\n")
    raise SystemExit(2) from _exc


REPO = Path(__file__).resolve().parents[2]
CONFIG_PATH = REPO / "config" / "lifecycle_pairs.yaml"
BASELINE_PATH = REPO / "ops_scripts" / "ci" / "baselines" / "lifecycle_pairs_baseline.json"

SCAN_ROOTS = [
    REPO / "agentic_core",
    REPO / "apps_eval",
    REPO / "apps_exec",
    REPO / "apps_lic",
    REPO / "apps_research",
    REPO / "apps_rfp",
    REPO / "apps_rg",
    REPO / "apps_shared",
    REPO / "apps_underwriting_ai",
    REPO / "infrastructure",
    REPO / "ops_scripts",
    REPO / "system_learning",
    REPO / "tools",
]

_FROZEN_SUBTREES: frozenset[str] = frozenset(
    {"archives", "archive", "_deleted", "tools_graveyard_w5.12", "v15_legacy", "seq_thinking_k25"}
)
SKIP_DIR_NAMES: frozenset[str] = GLOBAL_EXCLUDED_DIRS | _FROZEN_SUBTREES


def _load_pairs() -> list[dict]:
    if not CONFIG_PATH.is_file():
        return []
    data = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8")) or {}
    pairs = data.get("pairs", []) if isinstance(data, dict) else []
    return pairs if isinstance(pairs, list) else []


def _call_name(call: ast.Call) -> str | None:
    """Return the dotted trailing identifier of a call — e.g. 'sqlite3.connect'
    for ``sqlite3.connect(...)``, ``open`` for bare ``open(...)``.
    """
    func = call.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        parts: list[str] = [func.attr]
        node: ast.AST = func.value
        while isinstance(node, ast.Attribute):
            parts.append(node.attr)
            node = node.value
        if isinstance(node, ast.Name):
            parts.append(node.id)
        return ".".join(reversed(parts))
    return None


def _match_opener(name: str | None, opener_pattern: str) -> bool:
    """True if ``name`` equals the pattern or ends with ``.<pattern_tail>``."""
    if not name:
        return False
    if name == opener_pattern:
        return True
    # Trailing-match: redis.Redis matches both redis.Redis and foo.redis.Redis
    if name.endswith("." + opener_pattern):
        return True
    # Tail match for single segment patterns: "open" matches bare calls
    if "." not in opener_pattern and name.split(".")[-1] == opener_pattern:
        return True
    return False


def _enclosing_function(stack: list[ast.AST]) -> ast.FunctionDef | ast.AsyncFunctionDef | None:
    for node in reversed(stack):
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            return node
    return None


def _enclosing_class(stack: list[ast.AST]) -> ast.ClassDef | None:
    for node in reversed(stack):
        if isinstance(node, ast.ClassDef):
            return node
    return None


def _in_with_statement(call: ast.Call, stack: list[ast.AST]) -> bool:
    """True if ``call`` is (part of) the context expression of any enclosing
    `with` statement in the ancestor chain.
    """
    for node in reversed(stack):
        if isinstance(node, ast.With | ast.AsyncWith):
            for item in node.items:
                for sub in ast.walk(item.context_expr):
                    if sub is call:
                        return True
    return False


def _function_has_method_call(func: ast.AST, method: str) -> bool:
    """True if any Call in ``func`` targets attribute ``.<method>`` on any receiver."""
    for sub in ast.walk(func):
        if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Attribute):
            if sub.func.attr == method:
                return True
    return False


def _class_assigns_self_attr(cls: ast.ClassDef, attr: str) -> bool:
    """True if any Assign/AnnAssign in the class body sets ``self.<attr>``."""
    for sub in ast.walk(cls):
        if isinstance(sub, ast.Assign):
            targets = sub.targets
        elif isinstance(sub, ast.AnnAssign):
            targets = [sub.target]
        else:
            continue
        for tgt in targets:
            if (
                isinstance(tgt, ast.Attribute)
                and isinstance(tgt.value, ast.Name)
                and tgt.value.id == "self"
                and tgt.attr == attr
            ):
                return True
    return False


def _closer_satisfied(
    closer: str,
    call: ast.Call,
    stack: list[ast.AST],
) -> bool:
    if closer == "with_stmt":
        return _in_with_statement(call, stack)
    if closer.startswith("attr:self."):
        attr = closer[len("attr:self.") :]
        cls = _enclosing_class(stack)
        return bool(cls and _class_assigns_self_attr(cls, attr))
    if closer.startswith(".") and closer.endswith("()"):
        method = closer[1:-2]
        func = _enclosing_function(stack)
        return bool(func and _function_has_method_call(func, method))
    return False


class _LeakScanner(ast.NodeVisitor):
    """Walk an AST and report opener calls whose closers are not satisfied."""

    def __init__(self, pair_config: dict) -> None:
        self.pair = pair_config
        self.opener_pattern = pair_config.get("opener", "")
        self.closers: list[str] = pair_config.get("closers", []) or []
        self.hits: list[tuple[int, int]] = []  # (lineno, col_offset)
        self._stack: list[ast.AST] = []

    def generic_visit(self, node: ast.AST) -> None:
        self._stack.append(node)
        try:
            super().generic_visit(node)
        finally:
            self._stack.pop()

    def visit_Call(self, node: ast.Call) -> None:  # noqa: N802
        name = _call_name(node)
        if _match_opener(name, self.opener_pattern):
            satisfied = any(_closer_satisfied(c, node, self._stack) for c in self.closers)
            if not satisfied:
                self.hits.append((node.lineno, node.col_offset))
        self.generic_visit(node)


def _iter_python_files() -> list[Path]:
    files: list[Path] = []
    for root in SCAN_ROOTS:
        if not root.is_dir():
            continue
        for path in root.rglob("*.py"):
            if set(path.parts) & SKIP_DIR_NAMES:
                continue
            files.append(path)
    return files


def _scan_file(path: Path, pairs: list[dict]) -> dict[str, list[int]]:
    """Return {pair_name: [line, ...]} of leaks in ``path``."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (SyntaxError, UnicodeDecodeError):
        return {}
    out: dict[str, list[int]] = {}
    for pair in pairs:
        scanner = _LeakScanner(pair)
        scanner.visit(tree)
        if scanner.hits:
            out[pair.get("name", pair.get("opener", "?"))] = [h[0] for h in scanner.hits]
    return out


def _leak_key(path: Path, pair_name: str, lineno: int) -> str:
    return f"{path.relative_to(REPO).as_posix()}::{pair_name}::{lineno}"


def _load_baseline() -> set[str]:
    if not BASELINE_PATH.is_file():
        return set()
    try:
        data = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return set()
    entries = data.get("accepted_leaks", []) if isinstance(data, dict) else []
    return {str(x) for x in entries if isinstance(x, str)}


def _write_baseline(keys: set[str]) -> None:
    BASELINE_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "_doc": (
            "Accepted legacy-debt lifecycle-pair leaks. Format: "
            "'<relpath>::<pair_name>::<lineno>'. The ratchet fails only on "
            "leaks NOT in this list. Shrink over time; do NOT grow."
        ),
        "accepted_leaks": sorted(keys),
        "count": len(keys),
    }
    BASELINE_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--regenerate-baseline",
        action="store_true",
        help="Overwrite the baseline snapshot with current leak set (operator opt-in).",
    )
    args = parser.parse_args()

    pairs = _load_pairs()
    if not pairs:
        print(f"[check_lifecycle_pairs] SKIP: no pairs in {CONFIG_PATH}")
        return 0

    baseline = _load_baseline()
    files = _iter_python_files()
    all_leaks: dict[str, tuple[Path, str, int]] = {}
    for path in tqdm(files, desc="scan lifecycle", unit="file"):
        result = _scan_file(path, pairs)
        for pair_name, lines in result.items():
            for lineno in lines:
                key = _leak_key(path, pair_name, lineno)
                all_leaks[key] = (path, pair_name, lineno)

    if args.regenerate_baseline:
        _write_baseline(set(all_leaks.keys()))
        print(
            f"[check_lifecycle_pairs] BASELINE REGENERATED — "
            f"{len(all_leaks)} leak(s) recorded at "
            f"{BASELINE_PATH.relative_to(REPO).as_posix()}"
        )
        return 0

    new_leaks = {k: v for k, v in all_leaks.items() if k not in baseline}
    baseline_still = {k: v for k, v in all_leaks.items() if k in baseline}
    baseline_gone = sorted(baseline - set(all_leaks.keys()))

    exit_code = 0

    # Separate errors from warns by severity
    severity_by_pair = {p.get("name"): p.get("severity", "error") for p in pairs}
    new_errors = {k: v for k, v in new_leaks.items() if severity_by_pair.get(v[1]) != "warn"}
    new_warns = {k: v for k, v in new_leaks.items() if severity_by_pair.get(v[1]) == "warn"}

    if new_errors:
        print(
            f"[check_lifecycle_pairs] FAIL — {len(new_errors)} NEW lifecycle-pair leak(s) (error severity):"
        )
        for key, (path, pair_name, lineno) in sorted(new_errors.items()):
            rel = path.relative_to(REPO).as_posix()
            print(f"  - [{pair_name}] {rel}:{lineno}")
        print(
            "\nFix options:"
            "\n  1. Wrap the opener in a `with` statement."
            "\n  2. Store the result on `self.<attr>` (ownership model)."
            "\n  3. Call `.close()` explicitly in the same function."
            "\n  4. (Debt row) `python ops_scripts/ci/check_lifecycle_pairs.py "
            "--regenerate-baseline`."
        )
        exit_code = 1

    if new_warns:
        print(f"[check_lifecycle_pairs] WARN — {len(new_warns)} NEW lifecycle-pair leak(s) (warn):")
        for key, (path, pair_name, lineno) in sorted(new_warns.items()):
            rel = path.relative_to(REPO).as_posix()
            print(f"  - [{pair_name}] {rel}:{lineno}")

    if baseline_gone:
        print(f"[check_lifecycle_pairs] RATCHET-DOWN — {len(baseline_gone)} baseline leak(s) resolved:")
        for key in baseline_gone[:10]:
            print(f"  - {key}")
        if len(baseline_gone) > 10:
            print(f"  ... and {len(baseline_gone) - 10} more")

    if exit_code == 0:
        print(
            f"[check_lifecycle_pairs] PASS — "
            f"{len(all_leaks)} total leak(s), {len(baseline_still)} legacy-debt, "
            f"0 new errors"
        )
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
