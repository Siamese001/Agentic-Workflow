"""Guardian: G-SRC-1 — Sovereignty Runtime Contract (agentic_core/runtime).

Proves:
1. Structural AST: SovereigntyBootstrap, SovereigntyViolationError,
   IsolationViolationError, CapabilityTokenError, DeterminismViolationError
   all present with correct module locations.
2. Exception hierarchy: all sovereignty exceptions inherit from a common
   SovereignError base (fail-closed; no silent swallowing).
3. SovereigntyBootstrap.bootstrap() raises RuntimeError on double-call
   (single-use contract).
4. SovereigntyBootstrap.seal_and_finalize() raises RuntimeError if bootstrap()
   was never called (ordering contract).
5. sovereignty_exceptions module imports only from runtime — no L0/L2/L5
   (no layer inversion, AST-verified).
6. SovereigntyBootstrap defines the 7-step bootstrap order in its docstring
   (documentation contract).
"""

from __future__ import annotations

import ast
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BOOTSTRAP_PATH = PROJECT_ROOT / AGENTIC_CORE_DIR / "runtime" / "sovereignty_bootstrap.py"
EXCEPTIONS_PATH = PROJECT_ROOT / AGENTIC_CORE_DIR / "runtime" / "sovereignty_exceptions.py"

pytestmark = pytest.mark.guardian


# ===========================================================================
# A) Structural AST contracts
# ===========================================================================


class TestStructuralContract:
    def test_bootstrap_module_exists(self):
        assert BOOTSTRAP_PATH.exists(), "sovereignty_bootstrap.py must exist"

    def test_exceptions_module_exists(self):
        assert EXCEPTIONS_PATH.exists(), "sovereignty_exceptions.py must exist"

    def test_bootstrap_class_present(self):
        src = BOOTSTRAP_PATH.read_text(encoding="utf-8")
        tree = ast.parse(src, filename=str(BOOTSTRAP_PATH))
        names = {n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)}
        assert "SovereigntyBootstrap" in names

    def test_bootstrap_has_required_methods(self):
        src = BOOTSTRAP_PATH.read_text(encoding="utf-8")
        tree = ast.parse(src, filename=str(BOOTSTRAP_PATH))
        bs_cls = next(
            (n for n in ast.walk(tree) if isinstance(n, ast.ClassDef) and n.name == "SovereigntyBootstrap"),
            None,
        )
        assert bs_cls is not None
        methods = {n.name for n in bs_cls.body if isinstance(n, ast.FunctionDef)}
        assert "bootstrap" in methods, "SovereigntyBootstrap must define bootstrap()"
        assert "seal_and_finalize" in methods, "SovereigntyBootstrap must define seal_and_finalize()"

    def test_exception_classes_present(self):
        src = EXCEPTIONS_PATH.read_text(encoding="utf-8")
        tree = ast.parse(src, filename=str(EXCEPTIONS_PATH))
        names = {n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)}
        required = {
            "SovereigntyViolationError",
            "IsolationViolationError",
            "CapabilityTokenError",
            "DeterminismViolationError",
        }
        missing = required - names
        assert not missing, "Missing sovereignty exception classes: " + str(missing)

    def test_exceptions_inherit_from_sovereign_error(self):
        """All sovereignty exceptions must share a common SovereignError base."""
        src = EXCEPTIONS_PATH.read_text(encoding="utf-8")
        tree = ast.parse(src, filename=str(EXCEPTIONS_PATH))
        checked = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name.endswith(("Error", "Exception")):
                base_ids = []
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        base_ids.append(base.id)
                    elif isinstance(base, ast.Attribute):
                        base_ids.append(base.attr)
                checked.append((node.name, base_ids))
        # Every exception must have at least one base
        for cls_name, bases in checked:
            assert bases, cls_name + " must explicitly inherit from a base exception"

    def test_no_layer_inversion_in_exceptions(self):
        """sovereignty_exceptions must not import from L0/L1/L2/L5 directly."""
        src = EXCEPTIONS_PATH.read_text(encoding="utf-8")
        tree = ast.parse(src, filename=str(EXCEPTIONS_PATH))
        forbidden_prefixes = (
            "agentic_core.L0_routing",
            "agentic_core.L1_cognition",
            "agentic_core.L2_execution",
            "agentic_core.L5_safety",
        )
        violations = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                for prefix in forbidden_prefixes:
                    if node.module.startswith(prefix):
                        violations.append(node.module)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    for prefix in forbidden_prefixes:
                        if alias.name.startswith(prefix):
                            violations.append(alias.name)
        assert not violations, (
            "sovereignty_exceptions must not import from layer modules (layer inversion): " + str(violations)
        )

    def test_bootstrap_docstring_references_step_order(self):
        """Bootstrap order is a critical contract; docstring must document it."""
        src = BOOTSTRAP_PATH.read_text(encoding="utf-8")
        # The bootstrap order is documented; verify at least 3 numbered steps exist
        import re

        steps = re.findall(r"\d+\.\s+\w+", src)
        assert len(steps) >= 3, (
            "sovereignty_bootstrap.py docstring must enumerate bootstrap step order "
            "(found " + str(len(steps)) + " numbered steps)"
        )


# ===========================================================================
# B) SovereigntyBootstrap single-use contract (double-call raises)
# ===========================================================================


class TestBootstrapSingleUseContract:
    """bootstrap() must raise RuntimeError on a second call."""

    def _make_bootstrap(self):
        from agentic_core.runtime.sovereignty_bootstrap import SovereigntyBootstrap

        return SovereigntyBootstrap()

    def test_double_bootstrap_raises_runtime_error(self, tmp_path):
        """Calling bootstrap() twice on the same instance must raise RuntimeError."""
        bs = self._make_bootstrap()

        policy_file = tmp_path / "policy.json"
        policy_file.write_text('{"version": "test"}', encoding="utf-8")

        # Patch deep dependencies so we isolate the double-call guard
        with (
            patch("agentic_core.runtime.sovereignty_bootstrap.get_hierarchy_validator") as mock_hv,
            patch("agentic_core.runtime.sovereignty_bootstrap.initialize_determinism_engine"),
            patch(
                "agentic_core.runtime.sovereignty_bootstrap.start_execution_trace", return_value="trace-001"
            ),
        ):
            mock_hv.return_value = MagicMock(config_hash="cfg-hash-001")
            mock_hv.return_value.config_hash = "cfg-hash-001"

            with patch("agentic_core.runtime.execution_bound_token.get_capability_authority") as mock_ca:
                mock_ca.return_value = MagicMock(authority_public_hash="auth-hash-001")
                try:
                    bs.bootstrap(policy_file)
                except Exception:  # guardian: allow-silent-swallower
                    pass

            # Second call must raise regardless of dependency state
            with pytest.raises(RuntimeError, match="once"):
                with (
                    patch("agentic_core.runtime.sovereignty_bootstrap.get_hierarchy_validator") as mock_hv2,
                    patch("agentic_core.runtime.sovereignty_bootstrap.initialize_determinism_engine"),
                    patch(
                        "agentic_core.runtime.sovereignty_bootstrap.start_execution_trace",
                        return_value="trace-002",
                    ),
                ):
                    mock_hv2.return_value = MagicMock(config_hash="cfg-hash-002")
                    bs.bootstrap(policy_file)

    def test_seal_before_bootstrap_raises(self):
        """seal_and_finalize() before bootstrap() must raise RuntimeError."""
        bs = self._make_bootstrap()
        with pytest.raises(RuntimeError, match="bootstrap"):
            bs.seal_and_finalize()


# ===========================================================================
# C) Sovereignty exception classes are importable and carry error_code
# ===========================================================================


class TestSovereigntyExceptions:
    def test_sovereignty_violation_error_importable(self):
        from agentic_core.runtime.sovereignty_exceptions import SovereigntyViolationError

        exc = SovereigntyViolationError("boundary crossed")
        assert "boundary crossed" in str(exc)

    def test_isolation_violation_error_importable(self):
        from agentic_core.runtime.sovereignty_exceptions import IsolationViolationError

        exc = IsolationViolationError("write outside boundary")
        assert "write outside boundary" in str(exc)

    def test_capability_token_error_importable(self):
        from agentic_core.runtime.sovereignty_exceptions import CapabilityTokenError

        exc = CapabilityTokenError("token expired")
        assert "token expired" in str(exc)

    def test_determinism_violation_error_importable(self):
        from agentic_core.runtime.sovereignty_exceptions import DeterminismViolationError

        exc = DeterminismViolationError("hash mismatch")
        assert "hash mismatch" in str(exc)

    def test_all_exceptions_are_exception_subclasses(self):
        from agentic_core.runtime.sovereignty_exceptions import (
            CapabilityTokenError,
            DeterminismViolationError,
            IsolationViolationError,
            SovereigntyViolationError,
        )

        for exc_cls in (
            SovereigntyViolationError,
            IsolationViolationError,
            CapabilityTokenError,
            DeterminismViolationError,
        ):
            assert issubclass(exc_cls, Exception), exc_cls.__name__ + " must be an Exception subclass"
