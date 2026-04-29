"""Wave 2 unit tests — _DynamicExecutionVisitor synthetic-import emission.

When the visitor encounters ``importlib.import_module("x.y")``, ``__import__``,
or ``importlib.util.find_spec`` with a literal-string first arg, it MUST emit
a synthetic ``imports`` edge with ``edge_kind='dynamic_import'`` (in addition
to the existing ``invokes_dynamic`` edge). Variable / non-literal arguments
must NOT produce a synthetic import.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[6]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agentic_core.adg.extraction.visitors.dynamic import _DynamicExecutionVisitor  # noqa: E402


class _StubContext:
    """Minimal VisitorContext stand-in — only the fields the visitor reads."""

    def __init__(self, source_file: str = "agentic_core/loader.py") -> None:
        self.source_file = source_file
        self.module_adg_name = "ADG::Module::agentic_core.loader"
        self.module_path = "agentic_core.loader"
        self.layer = "L0"
        self.tree = None  # set per-test
        self.scope_stack: list[str] = []
        self.call_chain: list[str] = []


def _run_visitor(source: str) -> list:
    """Parse source, run the dynamic visitor, return collected edges."""
    tree = ast.parse(source)
    ctx = _StubContext()
    ctx.tree = tree
    visitor = _DynamicExecutionVisitor(ctx)
    visitor.visit(tree)
    return list(visitor.edges)


class TestLiteralImportEmission:
    def test_importlib_import_module_literal_emits_dynamic_import(self) -> None:
        edges = _run_visitor("import importlib\nx = importlib.import_module('agentic_core.real')\n")
        dynamic_imports = [e for e in edges if e.edge_kind == "dynamic_import"]
        assert len(dynamic_imports) == 1
        assert dynamic_imports[0].relation_type == "imports"
        assert dynamic_imports[0].to_name == "ADG::Symbol::agentic_core.real"
        assert "import_module" in dynamic_imports[0].symbol
        assert "agentic_core.real" in dynamic_imports[0].symbol

    def test_dunder_import_literal_emits_dynamic_import(self) -> None:
        edges = _run_visitor("__import__('agentic_core.x')\n")
        dynamic_imports = [e for e in edges if e.edge_kind == "dynamic_import"]
        assert len(dynamic_imports) == 1
        assert dynamic_imports[0].to_name == "ADG::Symbol::agentic_core.x"

    def test_find_spec_literal_emits_dynamic_import(self) -> None:
        edges = _run_visitor("import importlib.util\nspec = importlib.util.find_spec('agentic_core.maybe')\n")
        dynamic_imports = [e for e in edges if e.edge_kind == "dynamic_import"]
        assert len(dynamic_imports) == 1
        assert dynamic_imports[0].to_name == "ADG::Symbol::agentic_core.maybe"

    def test_bare_find_spec_literal_emits_dynamic_import(self) -> None:
        # Direct import: from importlib.util import find_spec
        edges = _run_visitor("from importlib.util import find_spec\nfind_spec('agentic_core.bare')\n")
        dynamic_imports = [e for e in edges if e.edge_kind == "dynamic_import"]
        assert len(dynamic_imports) == 1
        assert dynamic_imports[0].to_name == "ADG::Symbol::agentic_core.bare"


class TestNonLiteralArgsSkipped:
    @pytest.mark.parametrize(
        "src",
        [
            # Variable arg
            "import importlib\nname='x'\nimportlib.import_module(name)\n",
            # f-string arg
            "import importlib\nimportlib.import_module(f'x.{var}')\n",
            # concatenated arg
            "import importlib\nimportlib.import_module('x.' + suffix)\n",
            # No args
            "import importlib\nimportlib.import_module()\n",
            # Empty literal
            "import importlib\nimportlib.import_module('')\n",
        ],
    )
    def test_no_dynamic_import_emitted(self, src: str) -> None:
        edges = _run_visitor(src)
        dynamic_imports = [e for e in edges if e.edge_kind == "dynamic_import"]
        assert len(dynamic_imports) == 0


class TestInvokesDynamicCoexists:
    def test_eval_emits_invokes_dynamic_only(self) -> None:
        # `eval` is in DYNAMIC_EXEC_SYMBOLS but is NOT an import-resolution call,
        # so it produces exactly one edge: invokes_dynamic, no synthetic import.
        edges = _run_visitor("eval('1 + 1')\n")
        invokes = [e for e in edges if e.relation_type == "invokes_dynamic"]
        imports = [e for e in edges if e.edge_kind == "dynamic_import"]
        assert len(invokes) == 1
        assert len(imports) == 0

    def test_import_module_emits_dynamic_import_only(self) -> None:
        # `importlib.import_module` is NOT in DYNAMIC_EXEC_SYMBOLS, so it does
        # not emit `invokes_dynamic`. The new synthetic `dynamic_import` edge
        # is the SOLE emission. This is by design — invokes_dynamic is reserved
        # for code-evaluation primitives (eval/exec); import-resolution calls
        # are import edges.
        edges = _run_visitor("import importlib\nimportlib.import_module('agentic_core.x')\n")
        invokes = [e for e in edges if e.relation_type == "invokes_dynamic"]
        imports = [e for e in edges if e.edge_kind == "dynamic_import"]
        assert len(invokes) == 0
        assert len(imports) == 1


class TestRegressionCase:
    """The pre-2026-04-28 seam typo bug — now caught at extraction time."""

    def test_seam_path_typo_emits_dynamic_import_to_wrong_target(self) -> None:
        # Even though this typo TARGETS a non-existent module, the extractor
        # still emits the edge with the literal as written. The edge is then
        # classified at backfill time: dst node has empty resolved_path →
        # the edge is dynamic-by-kind, but the validity of the target string
        # is governed by the unresolved/verified axis after JOIN to nodes.
        edges = _run_visitor(
            "import importlib\n"
            "importlib.import_module('agentic_core.L5_safety.core_kernel.classification_kernel')\n"
        )
        dynamic_imports = [e for e in edges if e.edge_kind == "dynamic_import"]
        assert len(dynamic_imports) == 1
        assert (
            dynamic_imports[0].to_name
            == "ADG::Symbol::agentic_core.L5_safety.core_kernel.classification_kernel"
        )
