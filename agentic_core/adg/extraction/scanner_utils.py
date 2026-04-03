"""Utility classes and helpers for static scanner.

Contains:
- _HollowFileAnnotator: Phase 1.4 hollow file classification
- _TypeSurfaceCollector: Phase 3b type annotation collection
- _annotation_str: Helper to extract type strings from AST
- _infer_literal_type: Helper to infer types from literals
"""

from __future__ import annotations

import ast


def canonical_name(kind: str, path: str) -> str:
    """Generate canonical ADG name."""
    # Avoid circular import - inline the logic
    if "::" in path:
        return path
    clean_path = path.replace("/", ".").replace("\\", ".")
    return f"ADG::{kind}::{clean_path}"


class _HollowFileAnnotator(ast.NodeVisitor):
    """Phase 1.4: Annotate modules with hollow file classification.

    Identifies files with minimal behavioral content relative to boilerplate.
    Results are stored in surface_evidence for downstream processing.
    """

    def __init__(self, module_adg: str, rel_path: str):
        self.module_adg = module_adg
        self.rel_path = rel_path
        self.behavioral_functions = 0
        self.behavioral_classes = 0
        self.behavioral_methods = 0
        self.total_statements = 0
        self.boilerplate_statements = 0
        self.import_statements = 0
        self.string_literals = 0

    def visit_Module(self, node: ast.Module):
        """Visit module level."""
        for stmt in node.body:
            self.total_statements += 1
            self.visit(stmt)
        return node

    def visit_Import(self, node: ast.Import):
        """Count import statements."""
        self.import_statements += 1
        return node

    def visit_ImportFrom(self, node: ast.ImportFrom):
        """Count import from statements."""
        self.import_statements += 1
        return node

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Analyze function definition."""
        if self._has_behavioral_body(node.body):
            if node.name.startswith("_emit_"):
                self.boilerplate_statements += 1
            else:
                self.behavioral_functions += 1
        return node

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        """Analyze async function definition."""
        if self._has_behavioral_body(node.body):
            if node.name.startswith("_emit_"):
                self.boilerplate_statements += 1
            else:
                self.behavioral_functions += 1
        return node

    def visit_ClassDef(self, node: ast.ClassDef):
        """Analyze class definition."""
        behavioral_methods = 0
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if self._has_behavioral_body([item]):
                    if not item.name.startswith("_emit_"):
                        behavioral_methods += 1

        if behavioral_methods > 0:
            self.behavioral_classes += 1
            self.behavioral_methods += behavioral_methods
        return node

    def visit_Expr(self, node: ast.Expr):
        """Analyze expression statements."""
        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            self.string_literals += 1
        elif (
            isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Name)
            and node.value.func.id.startswith("_emit_")
        ):
            self.boilerplate_statements += 1
        return node

    def _has_behavioral_body(self, body: list[ast.stmt]) -> bool:
        """Check if function/class body has behavioral content."""
        if len(body) == 0:
            return False

        if len(body) == 1:
            stmt = body[0]
            if isinstance(stmt, ast.Pass):
                return False
            elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant):
                if stmt.value.value == Ellipsis:
                    return False
            elif (
                isinstance(stmt, ast.Raise)
                and isinstance(stmt.exc, ast.Call)
                and isinstance(stmt.exc.func, ast.Name)
                and stmt.exc.func.id == "NotImplementedError"
            ):
                return False

        for stmt in body:
            if self._is_behavioral_statement(stmt):
                return True

        return False

    def _is_behavioral_statement(self, stmt: ast.stmt) -> bool:
        """Check if statement represents behavioral logic."""
        if isinstance(stmt, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
            return True
        elif isinstance(stmt, ast.Return):
            return True
        elif isinstance(stmt, (ast.If, ast.For, ast.While, ast.Try)):
            return True
        elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
            call = stmt.value
            if not (isinstance(call.func, ast.Name) and call.func.id.startswith("_emit_")):
                return True
        elif isinstance(stmt, ast.With):
            return True

        return False

    @property
    def is_hollow(self) -> bool:
        """Check if file is hollow (no behavioral content)."""
        behavioral_nodes = self.behavioral_functions + self.behavioral_classes
        return behavioral_nodes == 0

    @property
    def boilerplate_ratio(self) -> float:
        """Calculate ratio of boilerplate to total statements."""
        if self.total_statements == 0:
            return 0.0
        return self.boilerplate_statements / self.total_statements


class _TypeSurfaceCollector(ast.NodeVisitor):
    """Phase 3b: Collect type annotations from AST.

    Populates type_surface_map on ScanResult for downstream enrichment.
    """

    def __init__(self, source_file: str) -> None:
        self.source_file = source_file
        self.type_map: dict[str, str] = {}
        self._class_stack: list[str] = []
        self._func_stack: list[str] = []
        self._base = source_file.replace("/", ".").replace("\\", ".").removesuffix(".py")

    def _symbol(self, name: str) -> str:
        parts = [self._base] + self._class_stack + self._func_stack + [name]
        return canonical_name("Symbol", "::".join(parts))

    def _current_scope_symbol(self) -> str:
        parts = [self._base] + self._class_stack + self._func_stack
        return canonical_name("Symbol", "::".join(parts))

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        sym = self._symbol(node.name)
        bases = [_annotation_str(b) for b in node.bases]
        self.type_map[sym] = f"class({', '.join(bases)})" if bases else "class"
        self._class_stack.append(node.name)
        self.generic_visit(node)
        self._class_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        sym = self._symbol(node.name)
        ret = _annotation_str(node.returns) if node.returns else "None"
        params: list[str] = []
        for arg in node.args.args:
            if arg.annotation:
                params.append(f"{arg.arg}: {_annotation_str(arg.annotation)}")
            else:
                params.append(arg.arg)
        self.type_map[sym] = f"({', '.join(params)}) -> {ret}"
        self._func_stack.append(node.name)
        self.generic_visit(node)
        self._func_stack.pop()

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if isinstance(node.target, ast.Name) and node.annotation:
            sym = self._symbol(node.target.id)
            self.type_map[sym] = _annotation_str(node.annotation)
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        for tgt in node.targets:
            if isinstance(tgt, ast.Name):
                inferred = _infer_literal_type(node.value)
                if inferred:
                    sym = self._symbol(tgt.id)
                    self.type_map[sym] = inferred
        self.generic_visit(node)


def _annotation_str(node: ast.expr | None) -> str:
    """Extract a human-readable type string from an AST annotation node."""
    if node is None:
        return ""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Constant):
        return repr(node.value)
    if isinstance(node, ast.Attribute):
        return f"{_annotation_str(node.value)}.{node.attr}"
    if isinstance(node, ast.Subscript):
        return f"{_annotation_str(node.value)}[{_annotation_str(node.slice)}]"
    if isinstance(node, ast.Tuple):
        return ", ".join(_annotation_str(e) for e in node.elts)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
        return f"{_annotation_str(node.left)} | {_annotation_str(node.right)}"
    return ast.dump(node)


def _infer_literal_type(node: ast.expr) -> str:
    """Infer type from simple literal/constructor expressions."""
    if isinstance(node, ast.Constant):
        return type(node.value).__name__
    if isinstance(node, ast.List):
        return "list"
    if isinstance(node, ast.Dict):
        return "dict"
    if isinstance(node, ast.Set):
        return "set"
    if isinstance(node, ast.Tuple):
        return "tuple"
    if isinstance(node, ast.Call):
        sym = _sym_of(node.func)
        if sym:
            return sym.split(".")[-1]
    return ""


def _sym_of(node: ast.expr) -> str:
    """Shared symbol extractor used by gap-plane visitors."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parts: list[str] = []
        cur: ast.expr = node
        while isinstance(cur, ast.Attribute):
            parts.append(cur.attr)
            cur = cur.value
        if isinstance(cur, ast.Name):
            parts.append(cur.id)
        return ".".join(reversed(parts))
    return ""


def _get_call_name(node: ast.expr) -> str:
    """Extract full call name from AST expression node."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parts = []
        cur: ast.expr = node
        while isinstance(cur, ast.Attribute):
            parts.append(cur.attr)
            cur = cur.value
        if isinstance(cur, ast.Name):
            parts.append(cur.id)
        return ".".join(reversed(parts))
    return ""


def _is_property_accessor(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """Return True if a function is decorated as a property getter, setter, or deleter."""
    for dec in node.decorator_list:
        if isinstance(dec, ast.Name) and dec.id == "property":
            return True
        if isinstance(dec, ast.Attribute) and dec.attr in ("setter", "deleter", "getter"):
            return True
    return False


__all__ = [
    "_HollowFileAnnotator",
    "_TypeSurfaceCollector",
    "_annotation_str",
    "_infer_literal_type",
    "_sym_of",
    "_get_call_name",
    "_is_property_accessor",
    "canonical_name",
]
