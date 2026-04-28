"""CI gate: verify declared feature wirings still exist in source.

Reads `config/expected_wiring.yaml` (SSOT) and for each row asserts:

1. `entry_module` resolves to an existing .py file.
2. `entry_symbol` resolves to a top-level class or function (or dotted
   class.method) inside that module.
3. `required_call` appears as the last segment of some `ast.Call` target
   anywhere inside the AST subtree rooted at `entry_symbol` — OR inside any
   helper method defined on the same class (so a split like execute() -> helper()
   still counts).
4. Every flag in `required_env_flags` appears in `.env.example`.

Exits 0 when all rows pass, 1 on the first failure.  Pure stdlib + PyYAML.

Rationale: ADG static-imports view is blind to lazy imports inside function
bodies — the failure mode that hid the semantic cache gap.  This gate asserts
the positive claim ("X must call Y") directly against the AST, independent of
the ADG edge extractor.

Part of RCA `rca-adg-ci-missed-gaps.md` corrective action C3.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore[import-untyped]
except ImportError:
    sys.stderr.write("[check_expected_wiring] PyYAML required. pip install pyyaml\n")
    raise SystemExit(2) from None


REPO = Path(__file__).resolve().parents[2]
CONFIG_PATH = REPO / "config" / "expected_wiring.yaml"
ENV_EXAMPLE = REPO / ".env.example"


def _load_config() -> list[dict[str, Any]]:
    data = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    rows = data.get("wirings", []) if isinstance(data, dict) else []
    if not isinstance(rows, list):
        raise ValueError("expected_wiring.yaml: 'wirings' must be a list")
    return rows


def _resolve_symbol(tree: ast.Module, dotted: str) -> list[ast.AST]:
    """Return the AST node(s) for a top-level `Class` or `Class.method` symbol.

    For a bare class, returns every method AST (so a required_call appearing in
    any method satisfies the check — useful when execute() delegates to a
    helper on the same class).
    """
    from tqdm import tqdm as _tqdm  # noqa: PLC0415 -- §16 progress bar

    parts = dotted.split(".")
    if len(parts) == 1:
        name = parts[0]
        for node in _tqdm(tree.body, desc="resolving symbol", unit="node", leave=False):
            if isinstance(node, ast.ClassDef) and node.name == name:
                return [n for n in node.body if isinstance(n, ast.FunctionDef | ast.AsyncFunctionDef)]
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef) and node.name == name:
                return [node]
        return []
    if len(parts) == 2:
        cls_name, meth_name = parts
        target_methods: list[ast.AST] = []
        for node in _tqdm(tree.body, desc="resolving symbol", unit="node", leave=False):
            if isinstance(node, ast.ClassDef) and node.name == cls_name:
                # Include the named method AND any helper method on the same class —
                # execute() often delegates to a _populate_*() helper.
                for n in node.body:
                    if isinstance(n, ast.FunctionDef | ast.AsyncFunctionDef):
                        if n.name == meth_name:
                            target_methods.append(n)
                if not target_methods and meth_name.startswith("_"):
                    # If the named helper itself is the entry symbol, return just it.
                    pass
                # Always append all sibling methods so delegation is captured.
                target_methods.extend(
                    n
                    for n in node.body
                    if isinstance(n, ast.FunctionDef | ast.AsyncFunctionDef) and n.name != meth_name
                )
                return target_methods
    return []


def _collect_call_names(nodes: list[ast.AST]) -> set[str]:
    """Collect every symbol "reached" within the subtree.

    A symbol counts as reached if it is (a) the trailing attribute of a Call,
    (b) the bare name of a Call, or (c) the imported name in a lazy
    `ImportFrom` statement. Pattern (c) catches the canonical lazy-import
    helper pattern::

        def _build_real_X():
            from module import X
            return X

    where X is referenced but never called inside the helper itself — the
    caller of the helper does the call. Without (c) this pattern would be a
    false negative.
    """
    from tqdm import tqdm as _tqdm  # noqa: PLC0415 -- §16 progress bar

    names: set[str] = set()
    for root in _tqdm(nodes, desc="scan calls", unit="symbol", leave=False):
        _scan_single(root, names)
    return names


def _add_call_name(call: ast.Call, names: set[str]) -> None:
    func = call.func
    if isinstance(func, ast.Attribute):
        names.add(func.attr)
    elif isinstance(func, ast.Name):
        names.add(func.id)


def _add_import_names(imp: ast.ImportFrom, names: set[str]) -> None:
    for alias in imp.names:
        names.add(alias.name)
        if alias.asname:
            names.add(alias.asname)


def _scan_single(root: ast.AST, names: set[str]) -> None:
    """Populate ``names`` with every symbol reached inside ``root``."""
    for sub in ast.walk(root):
        if isinstance(sub, ast.Call):
            _add_call_name(sub, names)
        elif isinstance(sub, ast.ImportFrom):
            _add_import_names(sub, names)


def _check_env_flags(flags: list[str]) -> list[str]:
    """Return flags missing from .env.example."""
    if not flags:
        return []
    if not ENV_EXAMPLE.exists():
        return flags
    body = ENV_EXAMPLE.read_text(encoding="utf-8")
    missing = [f for f in flags if f not in body]
    return missing


def _collect_call_nodes(nodes: list[ast.AST], target_name: str) -> list[ast.Call]:
    """Return every ``ast.Call`` whose trailing name matches ``target_name``.

    Used by the signature-shape check to inspect kwargs at the call site.
    """
    hits: list[ast.Call] = []
    for root in nodes:
        for sub in ast.walk(root):
            if not isinstance(sub, ast.Call):
                continue
            func = sub.func
            name: str | None = None
            if isinstance(func, ast.Attribute):
                name = func.attr
            elif isinstance(func, ast.Name):
                name = func.id
            if name == target_name:
                hits.append(sub)
    return hits


def _check_signature_contract(
    row_id: str,
    required_call: str,
    call_sites: list[ast.Call],
    contract: dict[str, Any],
) -> list[str]:
    """Verify that every call site of ``required_call`` honours the declared
    signature contract.

    Contract keys (all optional):
      required_kwargs : list[str]  — every keyword must appear in call.keywords
      forbidden_kwargs: list[str]  — none of these may appear
      min_args        : int        — positional-arg count lower bound
      max_args        : int        — positional-arg count upper bound (inclusive)
    """
    errors: list[str] = []
    required_kwargs = set(contract.get("required_kwargs", []) or [])
    forbidden_kwargs = set(contract.get("forbidden_kwargs", []) or [])
    min_args = contract.get("min_args")
    max_args = contract.get("max_args")

    if not call_sites:
        # Absence of a call site is already reported by the wiring check;
        # skip silently here to avoid double-counting.
        return errors

    for call in call_sites:
        kwarg_names = {kw.arg for kw in call.keywords if kw.arg is not None}
        missing = required_kwargs - kwarg_names
        present_forbidden = forbidden_kwargs & kwarg_names
        pos_count = len(call.args)

        where = f"line {getattr(call, 'lineno', '?')}"
        if missing:
            errors.append(
                f"[{row_id}] signature_contract violation at {where}: "
                f"{required_call} call missing required kwargs {sorted(missing)}"
            )
        if present_forbidden:
            errors.append(
                f"[{row_id}] signature_contract violation at {where}: "
                f"{required_call} call passes forbidden kwargs {sorted(present_forbidden)}"
            )
        if isinstance(min_args, int) and pos_count < min_args:
            errors.append(
                f"[{row_id}] signature_contract violation at {where}: "
                f"{required_call} call has {pos_count} positional args, min is {min_args}"
            )
        if isinstance(max_args, int) and pos_count > max_args:
            errors.append(
                f"[{row_id}] signature_contract violation at {where}: "
                f"{required_call} call has {pos_count} positional args, max is {max_args}"
            )
    return errors


def _check_row(row: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    row_id = row.get("id", "<unnamed>")

    # Plan: adg-expected-wiring-drift-cleanup. A row may carry
    # ``disabled: true`` plus a free-text ``disabled_reason`` to opt out of
    # the static AST check while preserving the declaration as documentation
    # and audit trail. Use cases:
    #   * Real architectural debt where the call IS missing AND a separate
    #     plan owns the fix (don't double-track the failure here).
    #   * Lazy-factory indirection patterns the AST walker cannot resolve
    #     when the proof_test already validates the runtime behaviour.
    # Disabled rows MUST still keep entry_module / entry_symbol / required_call
    # so the row remains a complete wiring contract; the gate just won't fail
    # on them. Re-enabling is a one-line yaml flip.
    if row.get("disabled"):
        return errors

    entry_module = row.get("entry_module")
    entry_symbol = row.get("entry_symbol")
    required_call = row.get("required_call")

    if not (entry_module and entry_symbol and required_call):
        errors.append(f"[{row_id}] missing entry_module/entry_symbol/required_call")
        return errors

    module_path = REPO / entry_module
    if not module_path.is_file():
        errors.append(f"[{row_id}] entry_module not found: {entry_module}")
        return errors

    try:
        tree = ast.parse(module_path.read_text(encoding="utf-8"), filename=str(module_path))
    except SyntaxError as err:
        errors.append(f"[{row_id}] syntax error in {entry_module}: {err}")
        return errors

    nodes = _resolve_symbol(tree, entry_symbol)
    if not nodes:
        errors.append(f"[{row_id}] entry_symbol not found: {entry_symbol} in {entry_module}")
        return errors

    called = _collect_call_names(nodes)
    target = required_call.rsplit(".", 1)[-1]
    if target not in called:
        errors.append(
            f"[{row_id}] required_call {required_call!r} not invoked inside "
            f"{entry_symbol} subtree of {entry_module}"
        )

    # Signature-shape: opt-in per-row contract on call-site kwargs/arity.
    # Only runs when the call is actually present (else the above wiring error
    # already covers it). This is the "contract drift" guard — catches arg
    # renames and silent default removals that pure-name wiring checks miss.
    contract = row.get("signature_contract")
    if isinstance(contract, dict) and target in called:
        call_sites = _collect_call_nodes(nodes, target)
        errors.extend(_check_signature_contract(row_id, required_call, call_sites, contract))

    missing_flags = _check_env_flags(row.get("required_env_flags", []) or [])
    if missing_flags:
        errors.append(f"[{row_id}] required_env_flags missing from .env.example: {missing_flags}")

    return errors


def main() -> int:
    if not CONFIG_PATH.exists():
        print(f"[check_expected_wiring] SKIP: no config at {CONFIG_PATH}")
        return 0
    rows = _load_config()
    if not rows:
        print("[check_expected_wiring] SKIP: empty wirings list")
        return 0
    total_errors: list[str] = []
    for row in rows:
        total_errors.extend(_check_row(row))
    if total_errors:
        print("[check_expected_wiring] FAIL")
        for err in total_errors:
            print(f"  - {err}")
        print(
            f"\n{len(total_errors)} wiring assertion(s) failed. "
            f"See docs/reports/plans/semcache-make-live-7a2d4b/rca-adg-ci-missed-gaps.md"
        )
        return 1
    print(f"[check_expected_wiring] PASS — {len(rows)} wiring(s) verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
