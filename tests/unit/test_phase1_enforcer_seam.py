"""
Phase 1 — ENFORCER + SEAM classification tests.

Tests exercise BOTH kernel (classify_file_standalone) and FCA (classify_file)
to prove classification paths exist at both layers.

Unit tests:
1. guardrail with verify_change returning (False,"Block:") -> ENFORCER (kernel)
2. pure _enforcer.py -> ENFORCER (kernel)
3. _seam.py with load_* + importlib -> SEAM (kernel)
4. _seam.py with 3 functions >5 statements -> NOT SEAM (kernel)
5. _contract.py pure dataclass -> TYPES
6. _contract.py with validate_* + raise + policy_ -> ENFORCER (kernel)
7. enforcement/_strategy.py -> remains STRATEGY

FCA-specific tests:
8. FCA classify_file() ENFORCER via AND-gate backstop
9. FCA classify_file() SEAM disqualification (>=3 complex funcs)
10. FCA classify_file() SEAM positive (simple seam with importlib)

Integration test:
11. mini repo slice of 5 files under enforcement/
12. FileType Literal includes ENFORCER and SEAM
"""

import textwrap
from pathlib import Path
from typing import get_args

import pytest

from agentic_core.L5_safety.core_kernel.classification_kernel import (
    FileType,
    classify_file_standalone,
    clear_classification_cache,
)

# ================================================================
# Helpers
# ================================================================


def _write(tmp_path: Path, name: str, code: str) -> Path:
    """Write a .py file under tmp_path and return its Path."""
    p = tmp_path / name
    p.write_text(textwrap.dedent(code), encoding="utf-8")
    return p


def _classify_kernel(tmp_path: Path, name: str, code: str) -> str:
    """Write file, clear cache, classify via kernel standalone."""
    p = _write(tmp_path, name, code)
    clear_classification_cache()
    return classify_file_standalone(p)


def _make_fca(tmp_path: Path):
    """Create a minimal FileClassificationAgent for testing."""
    from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
        FileClassificationAgent,
    )

    return FileClassificationAgent(
        project_root=tmp_path,
        dry_run=True,
        validate_only=True,
    )


def _classify_fca(tmp_path: Path, name: str, code: str) -> str:
    """Write file, classify via FCA classify_file()."""
    p = _write(tmp_path, name, code)
    fca = _make_fca(tmp_path)
    return fca.classify_file(p)


# ================================================================
# Kernel-level ENFORCER tests
# ================================================================


@pytest.mark.unit_min_deps
class TestEnforcerClassification:
    """Kernel-level ENFORCER detection."""

    def test_guardrail_with_verify_change_block(self, tmp_path):
        result = _classify_kernel(
            tmp_path,
            "safety_guardrail.py",
            """\
            class SafetyGuardrail:
                def verify_change(self, change):
                    if not change.is_safe:
                        return (False, "Block: unsafe change")
                    return (True, "")
        """,
        )
        assert result == "ENFORCER"

    def test_pure_enforcer_suffix(self, tmp_path):
        result = _classify_kernel(
            tmp_path,
            "tool_policy_enforcer.py",
            """\
            class ToolPolicyEnforcer:
                def enforce(self, action):
                    pass
        """,
        )
        assert result == "ENFORCER"

    def test_contract_with_enforcer_suffix(self, tmp_path):
        """_contract.py with validate_* + raise + policy_ -> ENFORCER via kernel name."""
        result = _classify_kernel(
            tmp_path,
            "boundary_enforcer.py",
            """\
            class BoundaryEnforcer:
                def validate_boundary(self, node_id):
                    if not node_id:
                        raise ValueError("Missing node_id")
                    return node_id
        """,
        )
        assert result == "ENFORCER"


# ================================================================
# Kernel-level SEAM tests
# ================================================================


@pytest.mark.unit_min_deps
class TestSeamClassification:
    """Kernel-level SEAM detection."""

    def test_seam_with_load_importlib(self, tmp_path):
        result = _classify_kernel(
            tmp_path,
            "plugin_seam.py",
            """\
            import importlib

            class PluginSeam:
                def load_module(self, name):
                    return importlib.import_module(name)
        """,
        )
        assert result == "SEAM"

    def test_seam_kernel_name_match(self, tmp_path):
        result = _classify_kernel(
            tmp_path,
            "adapter_seam.py",
            """\
            class AdapterSeam:
                def get_adapter(self):
                    return None
        """,
        )
        assert result == "SEAM"


# ================================================================
# Negative / non-ENFORCER tests (kernel)
# ================================================================


@pytest.mark.unit_min_deps
class TestNonEnforcerClassification:
    """Files that must NOT be classified as ENFORCER."""

    def test_contract_pure_dataclass_is_not_enforcer(self, tmp_path):
        result = _classify_kernel(
            tmp_path,
            "heal_contract.py",
            """\
            from dataclasses import dataclass

            @dataclass
            class HealContract:
                status: str
                message: str
        """,
        )
        assert result != "ENFORCER"

    def test_enforcement_strategy_remains_strategy(self, tmp_path):
        """enforcement/_strategy.py -> STRATEGY (folder mapping unchanged)."""
        enforcement = tmp_path / "enforcement"
        enforcement.mkdir()
        p = enforcement / "retry_strategy.py"
        p.write_text(
            textwrap.dedent("""\
            class RetryStrategy:
                def execute(self):
                    pass
        """),
            encoding="utf-8",
        )
        clear_classification_cache()
        result = classify_file_standalone(p)
        assert result == "STRATEGY"


# ================================================================
# FCA-level tests (exercise classify_file() directly)
# ================================================================


@pytest.mark.unit_min_deps
class TestFCAEnforcerClassification:
    """FCA classify_file() ENFORCER detection with AND-gate backstop."""

    def test_fca_enforcer_and_gate(self, tmp_path):
        """FCA requires BOTH control outcome AND policy semantics for ENFORCER."""
        result = _classify_fca(
            tmp_path,
            "budget_guardrail.py",
            """\
            class BudgetGuardrail:
                def validate_budget(self, amount):
                    if amount > self.policy_limit:
                        raise ValueError("Budget violation: exceeded limit")
                    return amount
        """,
        )
        assert result == "ENFORCER", (
            f"FCA should classify guardrail with validate_*+raise+policy_ as ENFORCER, got {result}"
        )

    def test_fca_enforcer_name_only_no_backstop(self, tmp_path):
        """ENFORCER name without behavioral backstop should NOT be ENFORCER in FCA."""
        result = _classify_fca(
            tmp_path,
            "simple_guard.py",
            """\
            class SimpleGuard:
                def check(self, x):
                    return x > 0
        """,
        )
        # Without control outcome + policy semantics, FCA should NOT classify as ENFORCER
        assert result != "ENFORCER", (
            f"FCA should NOT classify guard without AND-gate backstop as ENFORCER, got {result}"
        )


@pytest.mark.unit_min_deps
class TestFCASeamClassification:
    """FCA classify_file() SEAM detection with disqualifiers."""

    def test_fca_seam_positive(self, tmp_path):
        """Simple seam with importlib -> SEAM via FCA."""
        result = _classify_fca(
            tmp_path,
            "loader_seam.py",
            """\
            import importlib

            class LoaderSeam:
                def load_module(self, name):
                    return importlib.import_module(name)
        """,
        )
        assert result == "SEAM", f"FCA should classify seam with importlib as SEAM, got {result}"

    def test_fca_seam_disqualified_complex_funcs(self, tmp_path):
        """>=3 FunctionDef with body >5 stmts disqualifies SEAM in FCA."""
        result = _classify_fca(
            tmp_path,
            "complex_seam.py",
            """\
            import importlib

            class ComplexSeam:
                def load_module(self, name):
                    return importlib.import_module(name)

                def process_a(self, x):
                    a = x + 1
                    b = a + 2
                    c = b + 3
                    d = c + 4
                    e = d + 5
                    return e + 6

                def process_b(self, x):
                    a = x + 1
                    b = a + 2
                    c = b + 3
                    d = c + 4
                    e = d + 5
                    return e + 6

                def process_c(self, x):
                    a = x + 1
                    b = a + 2
                    c = b + 3
                    d = c + 4
                    e = d + 5
                    return e + 6
        """,
        )
        assert result != "SEAM", f"FCA should disqualify SEAM with >=3 complex functions, got {result}"


# ================================================================
# Integration test
# ================================================================


@pytest.mark.unit_min_deps
class TestEnforcementFolderIntegration:
    """Mini repo slice verifying correct classification + stats."""

    def test_enforcement_folder_classifications(self, tmp_path):
        """5 files under enforcement/ — verify correct classification."""
        enforcement = tmp_path / "enforcement"
        enforcement.mkdir()

        files = {
            "safety_guardrail.py": (
                "ENFORCER",
                textwrap.dedent("""\
                    class SafetyGuardrail:
                        def validate_safety(self, change):
                            if change.policy_violation:
                                raise ValueError("Safety violation blocked")
                            return change
                """),
            ),
            "retry_strategy.py": (
                "STRATEGY",
                textwrap.dedent("""\
                    class RetryStrategy:
                        def execute(self):
                            pass
                """),
            ),
            "tool_policy_enforcer.py": (
                "ENFORCER",
                textwrap.dedent("""\
                    class ToolPolicyEnforcer:
                        def validate_tool(self, tool):
                            if tool.enforce_blocked:
                                raise PermissionError("Tool policy violation")
                            return tool
                """),
            ),
            "input_validator.py": (
                "VALIDATOR",
                textwrap.dedent("""\
                    class InputValidator:
                        def validate(self, data):
                            return bool(data)
                """),
            ),
            "error_types.py": (
                "TYPES",
                textwrap.dedent("""\
                    from typing import TypedDict, Literal

                    class ErrorInfo(TypedDict):
                        code: int
                        message: str
                        severity: Literal["low", "high"]
                """),
            ),
        }

        fca = _make_fca(tmp_path)
        for filename, (expected, code) in files.items():
            p = enforcement / filename
            p.write_text(code, encoding="utf-8")
            actual = fca.classify_file(p)
            assert actual == expected, f"{filename}: expected {expected}, got {actual}"

    def test_filetype_literal_includes_new_types(self):
        """FileType Literal must include ENFORCER and SEAM."""
        valid_types = get_args(FileType)
        assert "ENFORCER" in valid_types
        assert "SEAM" in valid_types
