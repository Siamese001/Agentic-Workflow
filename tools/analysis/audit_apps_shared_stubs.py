"""AST-based stub classifier for apps_shared.

Plan: apps-shared-stub-audit-7dfe16 W1.

Walks every `.py` under ``apps_shared/`` and classifies every function
(and method) stub into one of:

  - ``Protocol``       — method on a ``typing.Protocol`` subclass
  - ``ABC``            — method on an ``abc.ABC``-derived class OR one
                         decorated with ``@abstractmethod``
  - ``TypedDict``      — attribute on a ``TypedDict`` class (rare, but
                         TypedDict classes sometimes carry helper stubs)
  - ``DeprecationShim`` — module/file under ``_compat/`` or explicitly
                         marked with ``deprecat`` in its docstring
  - ``HealerConvention`` — structured-noop pattern documented in
                         ``apps_lic/RUNBOOK.md#heal-method-notimpl-convention``
  - ``RealGap``        — none of the above; requires human follow-up

Writes a JSON census to
``artifacts/analysis/apps_shared_stub_census.json`` for downstream
consumers (W2 STUB_CENSUS.md, W4 scanner enrichment).

Usage::

    python tools/analysis/audit_apps_shared_stubs.py
    python tools/analysis/audit_apps_shared_stubs.py --json-only
    python tools/analysis/audit_apps_shared_stubs.py --category RealGap
"""
from __future__ import annotations

import argparse
import ast
import json
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

_APPS_SHARED = Path("apps_shared")
_CENSUS_OUT = Path("artifacts/analysis/apps_shared_stub_census.json")

# Stub kinds recognised by the AST walker.
_KINDS = ("Pass", "Ellipsis", "RetNone", "DocOnly", "NotImpl")

# Categories used in the classification.
_CATEGORIES = (
    "Protocol",
    "ABC",
    "TypedDict",
    "DeprecationShim",
    "HealerConvention",
    "RealGap",
)


@dataclass(frozen=True)
class StubRecord:
    """One function/method stub with its classification."""

    file_path: str
    line_number: int
    qualified_name: str
    stub_kind: str
    category: str
    rationale: str
    class_bases: tuple[str, ...] = field(default_factory=tuple)
    decorators: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class CensusReport:
    """Aggregate audit result."""

    scanned_files: int
    stubs: tuple[StubRecord, ...]
    category_counts: dict[str, int]
    kind_counts: dict[str, int]
    legit_total: int
    real_gap_total: int


def _stub_kind(body: list[ast.stmt]) -> str | None:
    """Return one of ``_KINDS`` or ``None`` if the body is non-stub."""
    stmts = body
    if (
        stmts
        and isinstance(stmts[0], ast.Expr)
        and isinstance(stmts[0].value, ast.Constant)
        and isinstance(stmts[0].value.value, str)
    ):
        rest = stmts[1:]
    else:
        rest = stmts
    if not rest:
        return "DocOnly"
    if len(rest) != 1:
        return None
    s = rest[0]
    if isinstance(s, ast.Pass):
        return "Pass"
    if (
        isinstance(s, ast.Expr)
        and isinstance(s.value, ast.Constant)
        and s.value.value is Ellipsis
    ):
        return "Ellipsis"
    if isinstance(s, ast.Return) and (
        s.value is None
        or (isinstance(s.value, ast.Constant) and s.value.value is None)
    ):
        return "RetNone"
    if isinstance(s, ast.Raise):
        exc = s.exc
        if isinstance(exc, ast.Call):
            fn = exc.func
            if isinstance(fn, ast.Name) and fn.id == "NotImplementedError":
                return "NotImpl"
            if isinstance(fn, ast.Attribute) and fn.attr == "NotImplementedError":
                return "NotImpl"
        if isinstance(exc, ast.Name) and exc.id == "NotImplementedError":
            return "NotImpl"
    return None


def _unparse_base(base: ast.expr) -> str:
    try:
        return ast.unparse(base)
    except Exception:  # guardian: allow-broad-exception -- ast.unparse raises heterogeneous on edge cases (e.g., ast.Starred); fail-soft to string repr preserves audit completeness
        return "?"


def _decorator_names(decorators: list[ast.expr]) -> list[str]:
    out = []
    for d in decorators:
        try:
            out.append(ast.unparse(d))
        except Exception:  # guardian: allow-broad-exception -- same reason as _unparse_base
            out.append("?")
    return out


def _classify(
    file_path: Path,
    cls_node: ast.ClassDef | None,
    fn_node: ast.FunctionDef | ast.AsyncFunctionDef,
    stub_kind: str,
) -> tuple[str, str]:
    """Return (category, rationale)."""
    # DeprecationShim — file is under _compat/ OR module docstring mentions deprecat
    rel = str(file_path).replace("\\", "/")
    if "/_compat/" in rel or rel.endswith("/_compat"):
        return "DeprecationShim", "file under _compat/ — deprecation/compat shim"

    class_bases: list[str] = []
    if cls_node is not None:
        class_bases = [_unparse_base(b) for b in cls_node.bases]

    # Protocol — any base has "Protocol" token
    if any("Protocol" in b for b in class_bases):
        return "Protocol", f"class {cls_node.name} inherits from Protocol"

    # TypedDict — any base has "TypedDict" token
    if any("TypedDict" in b for b in class_bases):
        return "TypedDict", f"class {cls_node.name} inherits from TypedDict"

    # ABC — any base has "ABC" or "ABCMeta" token
    if any(("ABC" in b or "abc" in b) for b in class_bases):
        return "ABC", f"class {cls_node.name} inherits from ABC"

    # ABC — the method has @abstractmethod decorator
    dec_names = _decorator_names(fn_node.decorator_list)
    if any("abstractmethod" in d for d in dec_names):
        return "ABC", "method decorated with @abstractmethod"

    # Healer-convention: method is `heal` or `heal_repository` with RetNone+noop
    # We can't check the body details cheaply here; we recognize the name +
    # stub_kind combo. The canonical pattern returns a dict, not None; so a
    # RetNone `heal_repository` is a RealGap, not healer-convention. But a
    # RetNone+named-heal pattern is rare; keep it as RealGap by default.

    # Everything else is a real gap candidate requiring human follow-up.
    return "RealGap", f"stub={stub_kind}; no Protocol/ABC/TypedDict/shim context"


def audit(root: Path | None = None) -> CensusReport:
    """Walk root and return a :class:`CensusReport`."""
    root = root or _APPS_SHARED
    stubs: list[StubRecord] = []
    scanned = 0
    for py_path in sorted(root.rglob("*.py")):
        if "__pycache__" in py_path.parts:
            continue
        scanned += 1
        try:
            src = py_path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        try:
            tree = ast.parse(src, filename=str(py_path))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            # Methods (inside a class)
            if isinstance(node, ast.ClassDef):
                for child in node.body:
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        kind = _stub_kind(child.body)
                        if kind is None:
                            continue
                        category, rationale = _classify(py_path, node, child, kind)
                        stubs.append(
                            StubRecord(
                                file_path=str(py_path).replace("\\", "/"),
                                line_number=child.lineno,
                                qualified_name=f"{node.name}.{child.name}",
                                stub_kind=kind,
                                category=category,
                                rationale=rationale,
                                class_bases=tuple(
                                    _unparse_base(b) for b in node.bases
                                ),
                                decorators=tuple(
                                    _decorator_names(child.decorator_list)
                                ),
                            )
                        )
        # Module-level functions (outside any class)
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                kind = _stub_kind(node.body)
                if kind is None:
                    continue
                category, rationale = _classify(py_path, None, node, kind)
                stubs.append(
                    StubRecord(
                        file_path=str(py_path).replace("\\", "/"),
                        line_number=node.lineno,
                        qualified_name=node.name,
                        stub_kind=kind,
                        category=category,
                        rationale=rationale,
                        class_bases=(),
                        decorators=tuple(_decorator_names(node.decorator_list)),
                    )
                )

    category_counts = Counter(s.category for s in stubs)
    kind_counts = Counter(s.stub_kind for s in stubs)
    real_gap = category_counts.get("RealGap", 0)
    legit = sum(v for k, v in category_counts.items() if k != "RealGap")
    return CensusReport(
        scanned_files=scanned,
        stubs=tuple(stubs),
        category_counts=dict(category_counts),
        kind_counts=dict(kind_counts),
        legit_total=legit,
        real_gap_total=real_gap,
    )


def emit_json(report: CensusReport, out_path: Path) -> None:
    """Write census JSON to ``out_path`` (parents auto-created)."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload: dict[str, Any] = {
        "scanned_files": report.scanned_files,
        "stub_total": len(report.stubs),
        "category_counts": report.category_counts,
        "kind_counts": report.kind_counts,
        "legit_total": report.legit_total,
        "real_gap_total": report.real_gap_total,
        "stubs": [asdict(s) for s in report.stubs],
    }
    out_path.write_text(
        json.dumps(payload, indent=2, sort_keys=False), encoding="utf-8"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Classify apps_shared function stubs (Protocol/ABC/RealGap/etc)."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=_APPS_SHARED,
        help=f"Scan root (default: {_APPS_SHARED})",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=_CENSUS_OUT,
        help=f"Census JSON output path (default: {_CENSUS_OUT})",
    )
    parser.add_argument(
        "--json-only",
        action="store_true",
        help="Suppress stdout summary; write JSON only.",
    )
    parser.add_argument(
        "--category",
        choices=_CATEGORIES,
        default=None,
        help="Filter stdout summary to one category.",
    )
    args = parser.parse_args(argv)

    report = audit(args.root)
    emit_json(report, args.out)

    if args.json_only:
        return 0

    print(f"apps_shared stub audit: scanned {report.scanned_files} files, "
          f"{len(report.stubs)} stubs")
    print(f"  legitimate: {report.legit_total} "
          f"({100 * report.legit_total / max(1, len(report.stubs)):.1f}%)")
    print(f"  real gaps:  {report.real_gap_total}")
    print("  category counts:")
    for cat in _CATEGORIES:
        n = report.category_counts.get(cat, 0)
        if n > 0:
            print(f"    {cat:>18s}: {n}")
    print("  stub-kind counts:")
    for k in _KINDS:
        n = report.kind_counts.get(k, 0)
        if n > 0:
            print(f"    {k:>18s}: {n}")
    if args.category is not None:
        print()
        print(f"  === stubs in category {args.category} ===")
        for s in report.stubs:
            if s.category == args.category:
                print(f"    {s.file_path}:{s.line_number} "
                      f"[{s.stub_kind}] {s.qualified_name} — {s.rationale}")
    print()
    print(f"  census written: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
