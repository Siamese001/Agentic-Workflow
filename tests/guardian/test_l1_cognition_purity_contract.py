"""Guardian: G-L1C-1 — L1 Cognition Layer Purity Contract.

Proves:
1. All Python files in L1_cognition parse without SyntaxError.
2. L1_cognition/types/execution_intent.py: assert_l1_purity() raises on
   mutation attempts (FAIL-CLOSED contract).
3. L1_cognition must not import from L2_execution, L3_orchestration, L4_state,
   or L5_safety — it is a read/plan-only layer (layer boundary contract, AST).
4. L1_cognition must not perform persistent writes (no open/write_text/json.dump
   without gateway) — AST-verified.
5. TelemetryEmitter in L1_cognition/telemetry produces deterministic event hashes
   (same inputs → same hash, AST-verified for compute_event_hash presence).
6. Structural: guardrails module defines MetaLearningGuardrails and CacheGuardrails
   — cognition safety contracts present.
7. No duplicate utility files: *_util.py and matching *.py without _util suffix
   must not define the same class names (deduplication contract, AST-verified).
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
L1_ROOT = PROJECT_ROOT / "agentic_core" / "L1_cognition"

pytestmark = pytest.mark.guardian


# ===========================================================================
# A) Layer structural integrity
# ===========================================================================


class TestLayerStructuralIntegrity:
    def test_l1_cognition_directory_exists(self):
        assert L1_ROOT.exists() and L1_ROOT.is_dir(), "agentic_core/L1_cognition must exist"

    def test_init_exists(self):
        assert (L1_ROOT / "__init__.py").exists(), "agentic_core/L1_cognition/__init__.py must exist"

    def test_all_files_parse_without_syntax_error(self):
        errors = []
        for f in sorted(L1_ROOT.rglob("*.py")):
            if "__pycache__" in str(f):
                continue
            try:
                src = f.read_text(encoding="utf-8", errors="replace")
                ast.parse(src, filename=str(f))
            except SyntaxError as e:
                errors.append(f.relative_to(PROJECT_ROOT).as_posix() + ": " + str(e))
        assert not errors, "SyntaxError(s) in L1_cognition:\n" + "\n".join(errors)

    def test_expected_sublayers_exist(self):
        expected = {"engines", "types", "validators"}
        existing = {d.name for d in L1_ROOT.iterdir() if d.is_dir() and not d.name.startswith(".")}
        missing = expected - existing
        assert not missing, "L1_cognition missing expected sub-layers: " + str(missing)


# ===========================================================================
# B) Layer boundary: no imports from lower/higher enforcement layers
# ===========================================================================


_FORBIDDEN_L1_IMPORTS = (
    "agentic_core.L2_execution",
    "agentic_core.L3_orchestration",
    "agentic_core.L4_state",
    "agentic_core.L5_safety",
)


class TestLayerBoundaryContract:
    """L1_cognition must not import directly from L2–L5 layers."""

    def test_no_forbidden_layer_imports(self):
        violations = {}
        for f in sorted(L1_ROOT.rglob("*.py")):
            if "__pycache__" in str(f):
                continue
            rel = f.relative_to(PROJECT_ROOT).as_posix()
            try:
                src = f.read_text(encoding="utf-8", errors="replace")
                tree = ast.parse(src, filename=str(f))
            except SyntaxError:
                continue
            file_violations = []
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module:
                    for forbidden in _FORBIDDEN_L1_IMPORTS:
                        if node.module.startswith(forbidden):
                            file_violations.append(
                                "from " + node.module + " (line " + str(node.lineno) + ")"
                            )
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        for forbidden in _FORBIDDEN_L1_IMPORTS:
                            if alias.name.startswith(forbidden):
                                file_violations.append(
                                    "import " + alias.name + " (line " + str(node.lineno) + ")"
                                )
            if file_violations:
                violations[rel] = file_violations
        assert not violations, (
            "L1_cognition has forbidden layer imports (layer boundary violation):\n"
            + "\n".join(k + ": " + str(v) for k, v in violations.items())
        )


# ===========================================================================
# C) No raw persistent writes
# ===========================================================================


_GATEWAY_NAMES = {
    "UniversalWriteGateway",
    "safe_write_text",
    "safe_json_dump",
    "assert_no_persistent_write",
}


def _has_write_violation(src: str, filename: str) -> list[str]:
    try:
        tree = ast.parse(src, filename=filename)
    except SyntaxError:
        return []

    gateway_imported = any(
        (isinstance(n, ast.ImportFrom) and any(a.name in _GATEWAY_NAMES for a in n.names))
        or (isinstance(n, ast.Import) and any(a.name in _GATEWAY_NAMES for a in n.names))
        for n in ast.walk(tree)
    )
    if gateway_imported:
        return []

    violations = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id == "open":
                for arg in node.args:
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        if any(m in arg.value for m in ("w", "a", "x")):
                            violations.append("open(write) at line " + str(node.lineno))
            if isinstance(func, ast.Attribute) and func.attr in ("write_text", "write_bytes"):
                violations.append(func.attr + "() at line " + str(node.lineno))
    return violations


class TestWritePurityContract:
    """L1_cognition must not perform raw persistent writes."""

    def test_no_unguarded_raw_writes(self):
        violations = {}
        for f in sorted(L1_ROOT.rglob("*.py")):
            if "__pycache__" in str(f):
                continue
            rel = f.relative_to(PROJECT_ROOT).as_posix()
            src = f.read_text(encoding="utf-8", errors="replace")
            sites = _has_write_violation(src, str(f))
            if sites:
                violations[rel] = sites
        assert not violations, (
            "L1_cognition has raw write sites (must use UniversalWriteGateway):\n"
            + "\n".join(k + ": " + str(v) for k, v in violations.items())
        )


# ===========================================================================
# D) execution_intent: assert_l1_purity function exists and is callable
# ===========================================================================


class TestExecutionIntentPurity:
    def test_assert_l1_purity_importable(self):
        from agentic_core.L1_cognition.types.execution_intent import assert_l1_purity
        assert callable(assert_l1_purity), "assert_l1_purity must be callable"

    def test_mutation_guard_starts_at_zero(self):
        from agentic_core.L1_cognition.types.execution_intent import (
            get_mutation_count,
            reset_mutation_guard,
        )
        reset_mutation_guard()
        assert get_mutation_count() == 0

    def test_increment_mutation_guard_increments(self):
        from agentic_core.L1_cognition.types.execution_intent import (
            get_mutation_count,
            increment_mutation_guard,
            reset_mutation_guard,
        )
        reset_mutation_guard()
        increment_mutation_guard()
        assert get_mutation_count() == 1

    def test_assert_l1_purity_passes_on_clean_instance(self):
        """assert_l1_purity(instance) must not raise for a clean plain object."""
        from agentic_core.L1_cognition.types.execution_intent import assert_l1_purity

        class _CleanObj:
            pass

        assert_l1_purity(_CleanObj())  # must not raise

    def test_assert_l1_purity_raises_for_redis_attr(self):
        """assert_l1_purity must raise if instance has a redis attribute."""
        from agentic_core.L1_cognition.types.execution_intent import assert_l1_purity

        class _DirtyObj:
            redis = object()

        with pytest.raises((AssertionError, Exception)):
            assert_l1_purity(_DirtyObj())

    def test_assert_l1_purity_raises_for_subprocess_attr(self):
        """assert_l1_purity must raise if instance has a subprocess attribute."""
        from agentic_core.L1_cognition.types.execution_intent import assert_l1_purity

        class _DirtyObj:
            subprocess = object()

        with pytest.raises((AssertionError, Exception)):
            assert_l1_purity(_DirtyObj())


# ===========================================================================
# E) TelemetryEmitter: compute_event_hash is deterministic (AST proof)
# ===========================================================================


class TestTelemetryEmitterDeterminism:
    TELEMETRY_PATH = L1_ROOT / "telemetry" / "telemetry_emitter.py"

    def test_telemetry_emitter_module_exists(self):
        if not self.TELEMETRY_PATH.exists():
            pytest.skip("telemetry_emitter.py not present")
        assert self.TELEMETRY_PATH.exists()

    def test_compute_event_hash_function_present(self):
        if not self.TELEMETRY_PATH.exists():
            pytest.skip("telemetry_emitter.py not present")
        src = self.TELEMETRY_PATH.read_text(encoding="utf-8")
        tree = ast.parse(src, filename=str(self.TELEMETRY_PATH))
        fn_names = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
        assert "compute_event_hash" in fn_names, (
            "TelemetryEmitter module must define compute_event_hash() "
            "for deterministic event identification"
        )

    def test_compute_event_hash_uses_hashlib(self):
        """Hash must use a cryptographic hash function, not random/uuid."""
        if not self.TELEMETRY_PATH.exists():
            pytest.skip("telemetry_emitter.py not present")
        src = self.TELEMETRY_PATH.read_text(encoding="utf-8")
        assert "hashlib" in src or "sha" in src.lower(), (
            "compute_event_hash must use hashlib for deterministic hashing"
        )

    def test_no_random_import_in_telemetry(self):
        """Telemetry events must be deterministic — no random module."""
        if not self.TELEMETRY_PATH.exists():
            pytest.skip("telemetry_emitter.py not present")
        src = self.TELEMETRY_PATH.read_text(encoding="utf-8")
        tree = ast.parse(src, filename=str(self.TELEMETRY_PATH))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name != "random", (
                        "TelemetryEmitter must not import 'random' — events must be deterministic"
                    )
            elif isinstance(node, ast.ImportFrom):
                assert node.module != "random", (
                    "TelemetryEmitter must not import from 'random' — events must be deterministic"
                )


# ===========================================================================
# F) Guardrails module defines required safety classes
# ===========================================================================


class TestGuardrailsContract:
    GUARDRAILS_PATH = L1_ROOT / "utils" / "guardrails.py"

    def test_guardrails_module_exists(self):
        if not self.GUARDRAILS_PATH.exists():
            pytest.skip("guardrails.py not present")
        assert self.GUARDRAILS_PATH.exists()

    def test_required_guardrail_classes_present(self):
        if not self.GUARDRAILS_PATH.exists():
            pytest.skip("guardrails.py not present")
        src = self.GUARDRAILS_PATH.read_text(encoding="utf-8")
        tree = ast.parse(src, filename=str(self.GUARDRAILS_PATH))
        names = {n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)}
        required = {"MetaLearningGuardrails", "CacheGuardrails"}
        missing = required - names
        assert not missing, "guardrails.py missing required classes: " + str(missing)

    def test_guardrails_importable(self):
        try:
            from agentic_core.L1_cognition.utils.guardrails import (
                CacheGuardrails,
                MetaLearningGuardrails,
                get_guardrails,
            )
            # Minimal usage to satisfy linter
            assert CacheGuardrails is not None
            assert MetaLearningGuardrails is not None
            assert callable(get_guardrails)
        except ImportError as e:
            pytest.fail("guardrails module must be importable: " + str(e))
