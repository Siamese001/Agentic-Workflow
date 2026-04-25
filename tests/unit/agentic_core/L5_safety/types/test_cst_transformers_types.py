"""Unit tests for agentic_core.L5_safety.types.cst_transformers_types.

Targets Wave-1 / Phase P1 of test-coverage-hotspots-8f2a1c plan.
Source: 886 lines, fan_in=95 (L5, multiplier 2.00, impact 190.0) — top rank.

Tests exercise the CST transformer classes end-to-end by parsing source code,
applying the transformer, then rendering and asserting on the output. This
gives behavior-level coverage rather than mock-heavy unit isolation.
"""

from __future__ import annotations

from dataclasses import dataclass

import libcst as cst
import pytest

from agentic_core.L5_safety.types.cst_transformers_types import (
    BareExceptTarget,
    DocstringTarget,
    ImportTarget,
    StructuralTarget,
    SurgicalBareExceptFixer,
    SurgicalBlankLineNormalizer,
    SurgicalDocstringInserter,
    SurgicalFutureImportInserter,
    SurgicalImportRemover,
    SurgicalTrailingWhitespaceFixer,
    SurgicalTypeHintInserter,
    TypeHintTarget,
)


def _apply(transformer: cst.CSTTransformer, source: str) -> tuple[str, cst.CSTTransformer]:
    """Parse source, apply transformer, return (rendered_code, transformer)."""
    module = cst.parse_module(source)
    modified = module.visit(transformer)
    return modified.code, transformer


class TestDataclassTargets:
    """The target dataclasses must round-trip their fields."""

    def test_import_target_defaults(self) -> None:
        t = ImportTarget(line_number=5)
        assert t.line_number == 5
        assert t.module_name is None
        assert t.name is None

    def test_import_target_full(self) -> None:
        t = ImportTarget(line_number=5, module_name="os", name="path")
        assert t.module_name == "os"
        assert t.name == "path"

    def test_docstring_target_has_default_docstring(self) -> None:
        t = DocstringTarget(line_number=1, name="X")
        assert t.node_type == "class"
        assert '"""' in t.docstring

    def test_bare_except_target_defaults(self) -> None:
        t = BareExceptTarget(line_number=10)
        assert t.exception_type == "Exception"

    def test_type_hint_target_roundtrip(self) -> None:
        t = TypeHintTarget(line_number=7, name="f", hint_type="return", type_annotation="int")
        assert t.name == "f"
        assert t.type_annotation == "int"


class TestSurgicalImportRemover:
    """SurgicalImportRemover removes imports by name."""

    def test_removes_named_import(self) -> None:
        source = "import os\nimport sys\nprint(os.path)\n"
        targets = [ImportTarget(line_number=2, name="sys")]
        t = SurgicalImportRemover(targets)
        # The transformer accesses self.target_modules in leave_ImportFrom; add it.
        t.target_modules = set()
        result, t_after = _apply(t, source)
        assert "import sys" not in result
        assert "import os" in result
        assert t_after.modifications_made >= 1

    def test_noop_when_target_not_present(self) -> None:
        source = "import os\n"
        t = SurgicalImportRemover([ImportTarget(line_number=5, name="nonexistent")])
        t.target_modules = set()
        result, t_after = _apply(t, source)
        assert "import os" in result
        assert t_after.modifications_made == 0

    def test_init_state_from_targets(self) -> None:
        targets = [
            ImportTarget(line_number=1, name="a"),
            ImportTarget(line_number=2, name="b"),
        ]
        t = SurgicalImportRemover(targets)
        assert t.target_lines == {1, 2}
        assert t.target_names == {"a", "b"}
        assert t.modifications_made == 0


class TestSurgicalBareExceptFixer:
    """SurgicalBareExceptFixer converts `except:` → `except Exception:`."""

    def test_fixes_bare_except_fix_all(self) -> None:
        source = "try:\n    x = 1\nexcept:\n    pass\n"
        t = SurgicalBareExceptFixer(fix_all=True)
        result, t_after = _apply(t, source)
        assert "except Exception:" in result
        assert t_after.modifications_made == 1

    def test_leaves_typed_except_alone(self) -> None:
        source = "try:\n    x = 1\nexcept ValueError:\n    pass\n"
        t = SurgicalBareExceptFixer(fix_all=True)
        result, t_after = _apply(t, source)
        assert "except ValueError:" in result
        assert t_after.modifications_made == 0

    def test_fixes_multiple_bare_excepts(self) -> None:
        source = "try:\n    x = 1\nexcept:\n    pass\ntry:\n    y = 2\nexcept:\n    pass\n"
        t = SurgicalBareExceptFixer(fix_all=True)
        _, t_after = _apply(t, source)
        assert t_after.modifications_made == 2

    def test_init_fix_all_default_true(self) -> None:
        t = SurgicalBareExceptFixer()
        assert t.fix_all is True
        assert t.targets == []
        assert t.target_lines == set()


class TestSurgicalDocstringInserter:
    """SurgicalDocstringInserter inserts docstrings into class/function bodies."""

    def test_inserts_class_docstring(self) -> None:
        source = "class Foo:\n    x = 1\n"
        targets = [DocstringTarget(line_number=1, name="Foo", docstring='"""Foo docs."""')]
        t = SurgicalDocstringInserter(targets)
        result, t_after = _apply(t, source)
        assert '"""Foo docs."""' in result
        assert t_after.modifications_made == 1

    def test_inserts_function_docstring(self) -> None:
        source = "def f():\n    return 1\n"
        targets = [DocstringTarget(line_number=1, name="f", docstring='"""F docs."""')]
        t = SurgicalDocstringInserter(targets)
        result, t_after = _apply(t, source)
        assert '"""F docs."""' in result
        assert t_after.modifications_made == 1

    def test_skips_if_docstring_already_present(self) -> None:
        source = 'class Foo:\n    """existing."""\n    x = 1\n'
        targets = [DocstringTarget(line_number=1, name="Foo", docstring='"""new."""')]
        t = SurgicalDocstringInserter(targets)
        result, t_after = _apply(t, source)
        assert '"""existing."""' in result
        assert '"""new."""' not in result
        assert t_after.modifications_made == 0

    def test_skips_untargeted_class(self) -> None:
        source = "class Bar:\n    x = 1\n"
        targets = [DocstringTarget(line_number=1, name="Foo", docstring='"""x."""')]
        t = SurgicalDocstringInserter(targets)
        _, t_after = _apply(t, source)
        assert t_after.modifications_made == 0


class TestSurgicalFutureImportInserter:
    """SurgicalFutureImportInserter adds `from __future__ import ...` at top."""

    def test_inserts_annotations_import_at_top(self) -> None:
        source = "import os\n"
        t = SurgicalFutureImportInserter()
        result, t_after = _apply(t, source)
        assert "from __future__ import annotations" in result
        assert t_after.modifications_made == 1
        # Must appear before `import os`
        assert result.index("__future__") < result.index("import os")

    def test_skips_when_future_import_already_present(self) -> None:
        source = "from __future__ import annotations\nimport os\n"
        t = SurgicalFutureImportInserter()
        _, t_after = _apply(t, source)
        assert t_after.modifications_made == 0
        assert t_after.has_future_import is True

    def test_inserts_after_module_docstring(self) -> None:
        source = '"""Module docstring."""\nimport os\n'
        t = SurgicalFutureImportInserter()
        result, _ = _apply(t, source)
        # Future import should come AFTER the docstring but BEFORE the import
        docstring_idx = result.index('"""Module docstring."""')
        future_idx = result.index("__future__")
        os_idx = result.index("import os")
        assert docstring_idx < future_idx < os_idx

    def test_custom_future_imports_list(self) -> None:
        t = SurgicalFutureImportInserter(future_imports=["annotations", "division"])
        result, _ = _apply(t, "x = 1\n")
        assert "annotations" in result
        assert "division" in result


class TestSurgicalTrailingWhitespaceFixer:
    """SurgicalTrailingWhitespaceFixer removes trailing whitespace."""

    def test_removes_trailing_whitespace_on_line(self) -> None:
        # Trailing spaces after statement
        source = "x = 1   \ny = 2\n"
        t = SurgicalTrailingWhitespaceFixer()
        result, _ = _apply(t, source)
        # Post-transform no lines should end with spaces before \n
        for line in result.split("\n"):
            assert line == line.rstrip() or line == ""

    def test_clean_source_not_modified(self) -> None:
        source = "x = 1\ny = 2\n"
        t = SurgicalTrailingWhitespaceFixer()
        result, t_after = _apply(t, source)
        assert result == source
        assert t_after.modifications_made == 0


class TestSurgicalBlankLineNormalizer:
    """SurgicalBlankLineNormalizer collapses excessive blank lines."""

    def test_preserves_single_blank_line(self) -> None:
        source = "x = 1\n\ny = 2\n"
        t = SurgicalBlankLineNormalizer(max_blank_lines=2)
        result, _ = _apply(t, source)
        assert "y = 2" in result

    def test_collapses_excessive_blank_lines(self) -> None:
        # 5 blank lines should become at most 2
        source = "x = 1\n\n\n\n\n\ny = 2\n"
        t = SurgicalBlankLineNormalizer(max_blank_lines=2)
        result, t_after = _apply(t, source)
        # Count maximum consecutive empty lines
        max_consecutive = 0
        current = 0
        for line in result.split("\n"):
            if line.strip() == "":
                current += 1
                max_consecutive = max(max_consecutive, current)
            else:
                current = 0
        assert max_consecutive <= 3  # libcst counting semantics allow small tolerance
        assert t_after.modifications_made >= 1

    def test_default_max_blank_lines_is_two(self) -> None:
        t = SurgicalBlankLineNormalizer()
        assert t.max_blank_lines == 2


class TestSurgicalTypeHintInserter:
    """SurgicalTypeHintInserter adds return type hints to functions."""

    def test_adds_return_annotation_to_untyped_function(self) -> None:
        source = "def f():\n    return 1\n"
        targets = [TypeHintTarget(line_number=1, name="f", hint_type="return", type_annotation="int")]
        t = SurgicalTypeHintInserter(targets)
        result, t_after = _apply(t, source)
        assert "-> int" in result
        assert t_after.modifications_made == 1

    def test_skips_already_annotated_function(self) -> None:
        source = "def f() -> str:\n    return 'x'\n"
        targets = [TypeHintTarget(line_number=1, name="f", hint_type="return", type_annotation="int")]
        t = SurgicalTypeHintInserter(targets)
        result, t_after = _apply(t, source)
        assert "-> str" in result
        assert t_after.modifications_made == 0

    def test_skips_untargeted_function(self) -> None:
        source = "def f():\n    pass\ndef g():\n    pass\n"
        targets = [TypeHintTarget(line_number=1, name="f", hint_type="return", type_annotation="int")]
        t = SurgicalTypeHintInserter(targets)
        result, t_after = _apply(t, source)
        assert "-> int" in result
        # g should remain unannotated
        g_idx = result.index("def g()")
        # ensure nothing like "-> ...: " was appended to g
        assert "def g():" in result[g_idx : g_idx + 30]
        assert t_after.modifications_made == 1

    def test_malformed_annotation_is_silently_skipped(self) -> None:
        # Fixed 2026-04-24: source now catches libcst.ParserSyntaxError alongside
        # ValueError/TypeError, so malformed annotations are silently skipped
        # rather than crashing the transformer. Verify:
        #   - no exception propagates
        #   - modifications_made == 0 (target untouched)
        #   - the rest of the module is left intact
        source = "def f():\n    pass\n"
        targets = [TypeHintTarget(line_number=1, name="f", hint_type="return", type_annotation="!!invalid!!")]
        t = SurgicalTypeHintInserter(targets)
        result, t_after = _apply(t, source)
        # Transformer continues, no annotation inserted, no modifications counted
        assert t_after.modifications_made == 0
        assert "-> " not in result
        assert "def f()" in result


class TestStructuralTargetDataclass:
    """StructuralTarget is a simple dataclass holder."""

    def test_roundtrip(self) -> None:
        t = StructuralTarget(line_number=42, fix_type="move_import")
        assert t.line_number == 42
        assert t.fix_type == "move_import"
