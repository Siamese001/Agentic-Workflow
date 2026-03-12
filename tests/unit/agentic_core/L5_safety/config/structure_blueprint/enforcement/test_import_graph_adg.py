"""ADG-driven tests for L5 structure_blueprint/enforcement/import_graph.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.config.structure_blueprint.enforcement.import_graph import (
    INTERNAL_ROOTS,
    ImportEdge,
)


class TestInternalRoots:
    def test_is_frozenset(self):
        assert isinstance(INTERNAL_ROOTS, frozenset)

    def test_contains_agentic_core(self):
        assert "agentic_core" in INTERNAL_ROOTS

    def test_contains_apps_rg(self):
        assert "apps_rg" in INTERNAL_ROOTS

    def test_contains_apps_lic(self):
        assert "apps_lic" in INTERNAL_ROOTS


class TestImportEdge:
    def test_creates(self):
        edge = ImportEdge(
            source_file="foo.py",
            target_module="agentic_core.utils",
            imported_names=("helper",),
            lineno=5,
        )
        assert edge.source_file == "foo.py"
        assert edge.target_module == "agentic_core.utils"

    def test_lineno_stored(self):
        edge = ImportEdge("a.py", "b.module", ("x",), 10)
        assert edge.lineno == 10

    def test_is_star_default_false(self):
        edge = ImportEdge("a.py", "b", (), 1)
        assert edge.is_star is False

    def test_is_star_set(self):
        edge = ImportEdge("a.py", "b", (), 1, is_star=True)
        assert edge.is_star is True

    def test_repr_contains_source(self):
        edge = ImportEdge("foo.py", "bar.mod", (), 7)
        assert "foo.py" in repr(edge)
