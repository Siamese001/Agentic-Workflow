"""
Tests for WAVE 2.2 — Schema binding on PromptTemplate + AssembledPrompt threading.

Covers:
  - PromptTemplate.response_schema field exists (default None)
  - PromptTemplate.__repr__ does not leak full schema payload
  - AssembledPrompt carries text + response_schema
  - assemble() stores schema on _last_response_schema
  - assemble_with_schema() returns AssembledPrompt with bound schema
  - AST verification of structural additions
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

# ── Fixtures ─────────────────────────────────────────────────────────────────

PERSON_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer"},
    },
    "required": ["name", "age"],
}

ASSEMBLER_SRC = Path("agentic_core/prompt_governance/core/prompt_assembler.py")


# ── 1) PromptTemplate model ─────────────────────────────────────────────────


class TestPromptTemplateSchemaField:
    """PromptTemplate has response_schema as first-class field."""

    def test_schema_field_exists_default_none(self):
        """AST: PromptTemplate model has response_schema field."""
        tree = ast.parse(ASSEMBLER_SRC.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "PromptTemplate":
                assigns = [
                    n
                    for n in ast.walk(node)
                    if isinstance(n, ast.AnnAssign)
                    and isinstance(n.target, ast.Name)
                    and n.target.id == "response_schema"
                ]
                assert len(assigns) >= 1, "PromptTemplate must have response_schema annotated field"
                return
        pytest.fail("PromptTemplate class not found")

    def test_schema_not_leaked_in_repr(self):
        """AST: PromptTemplate.__repr__ uses has_schema, not raw schema."""
        tree = ast.parse(ASSEMBLER_SRC.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "PromptTemplate":
                for method in ast.walk(node):
                    if isinstance(method, ast.FunctionDef) and method.name == "__repr__":
                        src_lines = ASSEMBLER_SRC.read_text(encoding="utf-8").splitlines()
                        repr_src = "\n".join(src_lines[method.lineno - 1 : method.end_lineno])
                        assert "has_schema" in repr_src, "__repr__ must use has_schema flag, not raw schema"
                        assert "response_schema" not in repr_src.replace(
                            "self.response_schema is not None", ""
                        ).replace("has_schema", ""), "__repr__ must not include raw response_schema value"
                        return
        pytest.fail("PromptTemplate.__repr__ not found")


# ── 2) AssembledPrompt NamedTuple ────────────────────────────────────────────


class TestAssembledPrompt:
    """AssembledPrompt carries text + response_schema."""

    def test_class_exists_with_fields(self):
        """AST: AssembledPrompt is a NamedTuple with text and response_schema."""
        tree = ast.parse(ASSEMBLER_SRC.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "AssembledPrompt":
                field_names = []
                for item in node.body:
                    if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                        field_names.append(item.target.id)
                assert "text" in field_names, "AssembledPrompt must have 'text' field"
                assert "response_schema" in field_names, "AssembledPrompt must have 'response_schema' field"
                return
        pytest.fail("AssembledPrompt class not found")

    def test_namedtuple_base_class(self):
        """AST: AssembledPrompt inherits from NamedTuple."""
        tree = ast.parse(ASSEMBLER_SRC.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "AssembledPrompt":
                base_names = [b.id if isinstance(b, ast.Name) else str(b) for b in node.bases]
                assert "NamedTuple" in base_names, "AssembledPrompt must inherit from NamedTuple"
                return
        pytest.fail("AssembledPrompt class not found")

    def test_response_schema_has_default_none(self):
        """AST: response_schema field has default value of None."""
        src = ASSEMBLER_SRC.read_text(encoding="utf-8")
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "AssembledPrompt":
                for item in node.body:
                    if (
                        isinstance(item, ast.AnnAssign)
                        and isinstance(item.target, ast.Name)
                        and item.target.id == "response_schema"
                        and item.value is not None
                    ):
                        # Check default is None constant
                        if isinstance(item.value, ast.Constant) and item.value.value is None:
                            return
                pytest.fail("response_schema must have default=None")
        pytest.fail("AssembledPrompt class not found")


# ── 3) Schema binding in assemble() ─────────────────────────────────────────


class TestAssembleSchemaBinding:
    """assemble() stores schema on _last_response_schema."""

    def test_last_response_schema_set_after_assemble(self):
        """AST: assemble() assigns self._last_response_schema = output_schema."""
        src = ASSEMBLER_SRC.read_text(encoding="utf-8")
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "PromptAssembler":
                for method in ast.walk(node):
                    if isinstance(method, ast.FunctionDef) and method.name == "assemble":
                        method_src = "\n".join(src.splitlines()[method.lineno - 1 : method.end_lineno])
                        assert "_last_response_schema" in method_src, (
                            "assemble() must bind _last_response_schema"
                        )
                        assert "output_schema" in method_src, "assemble() must reference output_schema"
                        return
        pytest.fail("PromptAssembler.assemble not found")

    def test_assemble_with_schema_method_exists(self):
        """AST: PromptAssembler has assemble_with_schema method."""
        src = ASSEMBLER_SRC.read_text(encoding="utf-8")
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "PromptAssembler":
                methods = [n.name for n in ast.walk(node) if isinstance(n, ast.FunctionDef)]
                assert "assemble_with_schema" in methods, (
                    "PromptAssembler must have assemble_with_schema method"
                )
                return
        pytest.fail("PromptAssembler class not found")

    def test_assemble_with_schema_returns_assembled_prompt(self):
        """AST: assemble_with_schema returns AssembledPrompt."""
        src = ASSEMBLER_SRC.read_text(encoding="utf-8")
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "PromptAssembler":
                for method in ast.walk(node):
                    if isinstance(method, ast.FunctionDef) and method.name == "assemble_with_schema":
                        method_src = "\n".join(src.splitlines()[method.lineno - 1 : method.end_lineno])
                        assert "AssembledPrompt" in method_src, (
                            "assemble_with_schema must return AssembledPrompt"
                        )
                        return
        pytest.fail("assemble_with_schema not found")


# ── 4) Module-level convenience function ─────────────────────────────────────


class TestModuleLevelConvenience:
    """Module-level assemble_prompt_with_schema exists and delegates."""

    def test_function_exists(self):
        """AST: module-level assemble_prompt_with_schema function."""
        src = ASSEMBLER_SRC.read_text(encoding="utf-8")
        tree = ast.parse(src)
        top_level_funcs = [n.name for n in tree.body if isinstance(n, ast.FunctionDef)]
        assert "assemble_prompt_with_schema" in top_level_funcs, (
            "Module must export assemble_prompt_with_schema"
        )

    def test_function_calls_assemble_with_schema(self):
        """AST: assemble_prompt_with_schema delegates to assembler.assemble_with_schema."""
        src = ASSEMBLER_SRC.read_text(encoding="utf-8")
        tree = ast.parse(src)
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name == "assemble_prompt_with_schema":
                func_src = "\n".join(src.splitlines()[node.lineno - 1 : node.end_lineno])
                assert "assemble_with_schema" in func_src, "Must delegate to assemble_with_schema"
                return
        pytest.fail("assemble_prompt_with_schema not found")


# ── 5) Gateway response_schema param exists ──────────────────────────────────


class TestGatewaySchemaParam:
    """SovereignLLMGateway.generate accepts response_schema."""

    def test_generate_has_response_schema_param(self):
        """AST: generate() has response_schema kwarg."""
        gw_src = Path("agentic_core/L2_execution/enforcement/SovereignLLMGateway.py")
        assert gw_src.exists()
        tree = ast.parse(gw_src.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "SovereignLLMGateway":
                for method in ast.walk(node):
                    if (
                        isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef))
                        and method.name == "generate"
                    ):
                        all_args = [a.arg for a in method.args.args + method.args.kwonlyargs]
                        assert "response_schema" in all_args, (
                            "generate() must accept response_schema parameter"
                        )
                        return
        pytest.fail("SovereignLLMGateway.generate not found")
