"""Unit tests for the W3 ADG scanner improvements in
``agentic_core.adg.extraction.visitors.core._CallVisitor``.

Covers:
  * ``open(...)`` mode-awareness — read modes MUST NOT emit writes_to.
  * Two-tier write classification — only exact ``WRITE_SIDE_EFFECT_SYMBOLS``
    matches OR curated ``WRITE_SIDE_EFFECT_TAIL_SYMBOLS`` matches emit writes_to.
  * Ambiguous tails (``run``, ``call``, ``copy``, ``move``) are NOT writes
    unless the full symbol is exactly in ``WRITE_SIDE_EFFECT_SYMBOLS``.
"""
from __future__ import annotations

import ast

import pytest

from agentic_core.adg.extraction.visitors import VisitorContext
from agentic_core.adg.extraction.visitors.core import _CallVisitor


def _classify(code: str) -> tuple[str, str]:
    """Parse a single Call expression and return (edge_kind, relation)."""
    tree = ast.parse(code, mode="eval")
    assert isinstance(tree.body, ast.Call), f"expected Call expr, got {type(tree.body)}"
    ctx = VisitorContext(module_adg_name="Module:test", source_file="test.py")
    visitor = _CallVisitor(ctx)
    sym = visitor._extract_symbol(tree.body.func)
    return visitor._classify_call(sym, tree.body)


class TestOpenModeAwareness:
    """``open(path, mode)`` MUST be classified by the mode argument."""

    @pytest.mark.parametrize("code", [
        "open('x.txt')",                    # default mode 'r'
        "open('x.txt', 'r')",
        "open('x.txt', 'rb')",
        "open('x.txt', 'rt')",
        "open('x.txt', mode='r')",
        "open('x.txt', mode='rb')",
        "p.open()",                         # Path.open default 'r'
        "p.open('r')",
        "aiofiles.open('x.txt', 'rb')",
    ])
    def test_read_mode_does_not_emit_write(self, code: str) -> None:
        kind, relation = _classify(code)
        assert kind == "" and relation == "", (
            f"read-mode open() {code!r} must NOT emit writes_to (got {kind!r}, {relation!r})"
        )

    @pytest.mark.parametrize("code", [
        "open('x.txt', 'w')",
        "open('x.txt', 'wb')",
        "open('x.txt', 'a')",
        "open('x.txt', 'ab')",
        "open('x.txt', 'x')",
        "open('x.txt', 'w+')",              # read+write -> write
        "open('x.txt', 'r+')",              # read+write -> write
        "open('x.txt', mode='w')",
        "p.open('w')",
        "aiofiles.open('x.txt', 'w')",
    ])
    def test_write_mode_emits_write(self, code: str) -> None:
        kind, relation = _classify(code)
        assert kind == "write" and relation == "writes_to", (
            f"write-mode open() {code!r} must emit writes_to (got {kind!r}, {relation!r})"
        )

    def test_variable_mode_treated_as_write(self) -> None:
        """Conservative: when mode is not a string literal, treat as write."""
        kind, relation = _classify("open('x.txt', mode_var)")
        assert kind == "write" and relation == "writes_to"


class TestAmbiguousTailsNotWrites:
    """Tails like ``run``, ``call``, ``copy`` MUST NOT match by suffix anymore."""

    @pytest.mark.parametrize("code", [
        "orch.run(req)",                    # orchestrator dispatch
        "self.runner.run('arg')",
        "pipeline.run()",
        "self.callback.call(x)",
        "violation.copy()",                 # dict.copy / list.copy — not a write
        "obj.move()",                       # generic .move
        "f.write(b)",                       # file-like write — borderline; tail not in list
    ])
    def test_ambiguous_tail_does_not_emit_write(self, code: str) -> None:
        kind, relation = _classify(code)
        assert kind == "" and relation == "", (
            f"ambiguous tail {code!r} must NOT emit writes_to (got {kind!r}, {relation!r})"
        )


class TestExactSymbolStillMatches:
    """Exact full-symbol matches in WRITE_SIDE_EFFECT_SYMBOLS still emit writes_to."""

    @pytest.mark.parametrize("code", [
        "subprocess.run(['ls'])",
        "subprocess.Popen(['ls'])",
        "subprocess.call(['ls'])",
        "subprocess.check_call(['ls'])",
        "os.remove('x.txt')",
        "os.rename('a', 'b')",
        "os.makedirs('a/b/c')",
        "os.mkdir('a')",
        "shutil.move('a', 'b')",
        "shutil.copy('a', 'b')",
        "shutil.rmtree('a')",
    ])
    def test_exact_symbol_emits_write(self, code: str) -> None:
        kind, relation = _classify(code)
        assert kind == "write" and relation == "writes_to", (
            f"exact symbol {code!r} must emit writes_to (got {kind!r}, {relation!r})"
        )


class TestCuratedTailMatching:
    """Curated tails (write_text, write_bytes, writelines, makedirs, rmtree) match."""

    @pytest.mark.parametrize("code", [
        "path.write_text('x')",
        "p.write_bytes(b'x')",
        "f.writelines(['a', 'b'])",
        "self.dir.makedirs()",
        "self.tmp.rmtree()",
    ])
    def test_curated_tail_emits_write(self, code: str) -> None:
        kind, relation = _classify(code)
        assert kind == "write" and relation == "writes_to", (
            f"curated tail {code!r} must emit writes_to (got {kind!r}, {relation!r})"
        )
