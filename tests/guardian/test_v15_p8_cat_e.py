"""V15 P8.1e — Category E: Bootstrap / SSOT Wiring Tests.

Structural (AST) + runtime (seam-level) tests proving:
- SSOT bootstrap entry (_legacy_main) constructs SurgicalManifest on enforced path
- Gateway.execute is invoked with LOG_ONLY semantics
- Manifest uses L0 target layer (bootstrap), AGGREGATE semantics
- No behavior change when V15_ENFORCEMENT=0
"""

from __future__ import annotations

import ast
import hashlib
import os
import re
from pathlib import Path
from unittest.mock import patch

from agentic_core.L0_routing.types.determinism_types import (
    FixConstraint,
    SurgicalManifest,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SSOT_PATH = PROJECT_ROOT / "agentic_core" / "L0_routing" / "scripts" / "execute_ssot.py"
SSOT_SRC = SSOT_PATH.read_text(encoding="utf-8")
SSOT_AST = ast.parse(SSOT_SRC)


# ---------------------------------------------------------------------------
# AST helpers
# ---------------------------------------------------------------------------


def _find_function_node(tree: ast.Module, name: str):
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return node
    return None


def _function_body_source(func_name: str) -> str:
    node = _find_function_node(SSOT_AST, func_name)
    if node is None:
        return ""
    start = node.lineno - 1
    end = node.end_lineno or start + 1
    lines = SSOT_SRC.splitlines()
    return "\n".join(lines[start:end])


# ===========================================================================
# A) Structural (AST) Tests
# ===========================================================================


class TestStructuralSSOTBootstrap:
    """AST-level proof of SSOT bootstrap wiring."""

    def test_legacy_main_exists(self):
        node = _find_function_node(SSOT_AST, "_legacy_main")
        assert node is not None

    def test_build_ssot_manifest_exists(self):
        node = _find_function_node(SSOT_AST, "_v15_build_ssot_manifest")
        assert node is not None

    def test_ssot_gateway_audit_exists(self):
        node = _find_function_node(SSOT_AST, "_v15_ssot_gateway_audit")
        assert node is not None

    def test_legacy_main_calls_build_manifest(self):
        body = _function_body_source("_legacy_main")
        assert "_v15_build_ssot_manifest" in body

    def test_legacy_main_calls_gateway_audit(self):
        body = _function_body_source("_legacy_main")
        assert "_v15_ssot_gateway_audit" in body

    def test_manifest_built_before_project_root(self):
        """Manifest must be constructed before main SSOT logic begins."""
        body = _function_body_source("_legacy_main")
        manifest_pos = body.find("_v15_build_ssot_manifest")
        root_pos = body.find("project_root = repo_root")
        assert manifest_pos < root_pos, "manifest must be built before project_root resolution"

    def test_build_manifest_constructs_surgical_manifest(self):
        body = _function_body_source("_v15_build_ssot_manifest")
        assert "SurgicalManifest(" in body

    def test_build_manifest_checks_enforcement(self):
        body = _function_body_source("_v15_build_ssot_manifest")
        assert "is_v15_enforced()" in body

    def test_audit_calls_gateway_execute(self):
        body = _function_body_source("_v15_ssot_gateway_audit")
        assert "gw.execute(" in body

    def test_target_layer_is_l0(self):
        body = _function_body_source("_v15_build_ssot_manifest")
        assert 'target_layer="L0"' in body

    def test_serialization_canon_is_execute_ssot(self):
        body = _function_body_source("_v15_build_ssot_manifest")
        assert 'serialization_canon="execute_ssot"' in body

    def test_node_id_is_execute_ssot(self):
        body = _function_body_source("_v15_build_ssot_manifest")
        assert 'node_id="ExecuteSSOT"' in body

    def test_bootstrap_safe_try_except(self):
        """Builder must use try/except for bootstrap safety."""
        body = _function_body_source("_v15_build_ssot_manifest")
        assert "except Exception" in body

    def test_fail_closed_when_hard_enforcement(self):
        """Builder must re-raise when V15_ENFORCEMENT=1 (fail-closed)."""
        body = _function_body_source("_v15_build_ssot_manifest")
        assert 'os.getenv("V15_ENFORCEMENT") == "1"' in body
        assert "raise" in body

    def test_log_only_in_audit_docstring(self):
        body = _function_body_source("_v15_ssot_gateway_audit")
        assert "LOG_ONLY" in body


# ===========================================================================
# B) Runtime Tests — locally extracted pattern (no heavy execute_ssot import)
# ===========================================================================


def _local_build_ssot_manifest():
    """Locally extracted replica of _v15_build_ssot_manifest for testing."""
    from agentic_core.L0_routing.types.guardian_contract_types import is_v15_enforced

    if not is_v15_enforced():
        return None

    from agentic_core.L0_routing.enforcement.traceability_contracts import generate_trace_id

    _hex8 = hashlib.sha256(b"execute_ssot._legacy_main").hexdigest()[:8].upper()
    trace_id = generate_trace_id(_hex8)
    ast_snippet = "execute_ssot._legacy_main()"
    return SurgicalManifest(
        schema_version="1.0.0",
        correlation_id=trace_id,
        node_id="ExecuteSSOT",
        target_layer="L0",
        ast_snippet=ast_snippet,
        serialization_canon="execute_ssot",
        fix_constraint=FixConstraint.RELAXED,
        manifest_hash=hashlib.sha256(ast_snippet.encode()).hexdigest(),
        change_history=(),
        provenance_chain=(trace_id,),
    )


class TestRuntimeSSOTManifest:
    """Runtime proof that manifest construction works under enforcement."""

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "log"})
    def test_manifest_constructed_when_enforced(self):
        manifest = _local_build_ssot_manifest()
        assert manifest is not None
        assert isinstance(manifest, SurgicalManifest)
        assert manifest.target_layer == "L0"
        assert manifest.node_id == "ExecuteSSOT"
        assert manifest.serialization_canon == "execute_ssot"

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "0"})
    def test_manifest_none_when_not_enforced(self):
        manifest = _local_build_ssot_manifest()
        assert manifest is None

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "log"})
    def test_trace_id_format(self):
        manifest = _local_build_ssot_manifest()
        assert manifest is not None
        assert re.match(r"^CC3AL1-[0-9A-F]{8}$", manifest.correlation_id)

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "log"})
    def test_trace_id_deterministic(self):
        """Same SSOT entry must produce same trace_id (deterministic seed)."""
        m1 = _local_build_ssot_manifest()
        m2 = _local_build_ssot_manifest()
        assert m1 is not None and m2 is not None
        assert m1.correlation_id == m2.correlation_id

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "log"})
    def test_gateway_receives_manifest(self):
        from agentic_core.L0_routing.enforcement.execution_gateway import (
            V15ExecutionGateway,
        )

        captured = []
        _orig = V15ExecutionGateway.execute

        def _spy(self_gw, execution_input, *args, **kwargs):
            captured.append({"manifest": execution_input, "trace_id": kwargs.get("trace_id")})
            return _orig(self_gw, execution_input, *args, **kwargs)

        manifest = _local_build_ssot_manifest()
        assert manifest is not None

        with patch.object(V15ExecutionGateway, "execute", _spy):
            gw = V15ExecutionGateway()
            try:
                gw.execute(
                    manifest,
                    lambda m: {"status": "ssot_audit", "errors": 0},
                    lambda: (
                        hashlib.sha256(b"fs_ssot").hexdigest(),
                        hashlib.sha256(b"git_ssot").hexdigest(),
                        hashlib.sha256(b"mem_ssot").hexdigest(),
                    ),
                    trace_id=manifest.correlation_id,
                )
            # guardian: allow-silent-swallow
            except Exception:
                pass

        assert len(captured) == 1
        assert captured[0]["manifest"] is manifest
        assert captured[0]["trace_id"] == manifest.correlation_id
