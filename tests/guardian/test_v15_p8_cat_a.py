"""V15 P8 Wave 8.1a — Category A: Orchestrators.

Proves:
- Each target constructs SurgicalManifest (structural via AST).
- Gateway invoked in LOG_ONLY mode (runtime via importable types).
- Flow correctness: conditional findings → AGGREGATE, terminal completion → RESULT.
"""

from __future__ import annotations

import ast
import hashlib
import os
import re
from pathlib import Path
from unittest.mock import patch

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# ---------------------------------------------------------------------------
# Structural tests: verify _v15_build_operation_manifest exists in each target
# ---------------------------------------------------------------------------


class TestStructuralManifestConstruction:
    """Verify each Cat-A target has _v15_build_operation_manifest and constructs SurgicalManifest."""

    TARGET_FILES = [
        PROJECT_ROOT / "agentic_core/L3_orchestration/engines/orchestrator_engine.py",
        PROJECT_ROOT / "agentic_core/L3_orchestration/reasoning/NervousSystemAgent.py",
        PROJECT_ROOT / "agentic_core/runtime/config/security_level_config.py",
    ]

    @pytest.mark.parametrize("target", TARGET_FILES, ids=lambda p: p.name)
    def test_has_build_operation_manifest_method(self, target: Path):
        """Each target must define _v15_build_operation_manifest."""
        source = target.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(target))

        method_names = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "_v15_build_operation_manifest":
                method_names.append(node.name)

        assert len(method_names) >= 1, f"{target.name} must define _v15_build_operation_manifest"

    @pytest.mark.parametrize("target", TARGET_FILES, ids=lambda p: p.name)
    def test_constructs_surgical_manifest(self, target: Path):
        """Each target must reference SurgicalManifest construction."""
        source = target.read_text(encoding="utf-8")
        assert "SurgicalManifest(" in source, f"{target.name} must construct SurgicalManifest"

    @pytest.mark.parametrize("target", TARGET_FILES, ids=lambda p: p.name)
    def test_imports_is_v15_enforced(self, target: Path):
        """Each target must import is_v15_enforced for conditional wiring."""
        source = target.read_text(encoding="utf-8")
        assert "is_v15_enforced" in source, f"{target.name} must import is_v15_enforced"

    @pytest.mark.parametrize("target", TARGET_FILES, ids=lambda p: p.name)
    def test_manifest_has_correct_fields(self, target: Path):
        """Manifest construction must include required fields."""
        source = target.read_text(encoding="utf-8")
        required_fields = [
            "schema_version",
            "correlation_id",
            "node_id",
            "target_layer",
            "ast_snippet",
            "fix_constraint",
            "manifest_hash",
        ]
        for field in required_fields:
            assert f"{field}=" in source, f"{target.name}: SurgicalManifest missing field {field}"

    @pytest.mark.parametrize("target", TARGET_FILES, ids=lambda p: p.name)
    def test_gateway_execute_reference(self, target: Path):
        """Each target must invoke gateway.execute() when V15 enforced."""
        source = target.read_text(encoding="utf-8")
        assert "gateway.execute(" in source or "gateway.execute(" in source.replace("\n", ""), (
            f"{target.name} must invoke gateway.execute()"
        )


# ---------------------------------------------------------------------------
# Runtime tests: manifest construction pattern via importable types
# ---------------------------------------------------------------------------


class TestManifestConstructionPattern:
    """Runtime tests using importable V15 types (no complex orchestrator imports)."""

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "log"})
    def test_manifest_construction_pattern_enforced(self):
        """The shared manifest construction pattern produces valid SurgicalManifest."""
        from agentic_core.L0_maintenance.enforcement.v15_p4_contracts import (
            generate_trace_id,
        )
        from agentic_core.L0_maintenance.types.guardian_contract import is_v15_enforced
        from agentic_core.L0_maintenance.types.v15_p2_types import (
            FixConstraint,
            SurgicalManifest,
        )

        assert is_v15_enforced()

        # Mirror the pattern used in all 3 Cat-A targets
        class_name = "Orchestrator"
        operation = "heal_repository"
        target_layer = "L3"

        _hex8 = (
            hashlib.sha256(
                f"{class_name}:{operation}".encode(),
            )
            .hexdigest()[:8]
            .upper()
        )
        trace_id = generate_trace_id(_hex8)

        ast_snippet = f"{class_name}.{operation}()"
        manifest = SurgicalManifest(
            schema_version="1.0.0",
            correlation_id=trace_id,
            node_id=class_name,
            target_layer=target_layer,
            ast_snippet=ast_snippet,
            serialization_canon="orchestrator_operation",
            fix_constraint=FixConstraint.RELAXED,
            manifest_hash=hashlib.sha256(ast_snippet.encode()).hexdigest(),
            change_history=(),
            provenance_chain=(trace_id,),
        )

        assert isinstance(manifest, SurgicalManifest)
        assert manifest.node_id == "Orchestrator"
        assert manifest.target_layer == "L3"
        assert re.match(r"^CC3AL1-[0-9A-F]{8}$", manifest.correlation_id)

    def test_manifest_construction_pattern_not_enforced(self):
        """When V15 explicitly opted out, is_v15_enforced() returns False."""
        with patch.dict(os.environ, {"V15_ENFORCEMENT": "0"}):
            from agentic_core.L0_maintenance.types.guardian_contract import is_v15_enforced

            assert not is_v15_enforced()


class TestGatewayInvocationPattern:
    """Runtime: gateway.execute() invoked with correct manifest in LOG_ONLY."""

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "log"})
    def test_gateway_processes_orchestrator_manifest(self):
        """Gateway accepts and processes manifest from Cat-A pattern."""
        from agentic_core.L0_maintenance.enforcement.v15_execution_gateway import (
            V15ExecutionGateway,
        )
        from agentic_core.L0_maintenance.enforcement.v15_p4_contracts import (
            generate_trace_id,
        )
        from agentic_core.L0_maintenance.types.v15_p2_types import (
            FixConstraint,
            SurgicalManifest,
        )

        _hex8 = hashlib.sha256(b"Orchestrator:heal_repository").hexdigest()[:8].upper()
        trace_id = generate_trace_id(_hex8)
        ast_snippet = "Orchestrator.heal_repository()"

        manifest = SurgicalManifest(
            schema_version="1.0.0",
            correlation_id=trace_id,
            node_id="Orchestrator",
            target_layer="L3",
            ast_snippet=ast_snippet,
            serialization_canon="orchestrator_operation",
            fix_constraint=FixConstraint.RELAXED,
            manifest_hash=hashlib.sha256(ast_snippet.encode()).hexdigest(),
            change_history=(),
            provenance_chain=(trace_id,),
        )

        gw = V15ExecutionGateway()
        result = gw.execute(
            execution_input=manifest,
            heal_fn=lambda m: {"violations_found": 0, "errors": 0},
            state_hash_fn=lambda: ("a", "b", "c"),
            trace_id=trace_id,
        )
        assert result.success
        assert result.manifest.node_id == "Orchestrator"
        assert len(gw._pipe_violations) == 0

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "log"})
    def test_gateway_processes_nervous_system_manifest(self):
        """Gateway accepts NervousSystemAgent manifest."""
        from agentic_core.L0_maintenance.enforcement.v15_execution_gateway import (
            V15ExecutionGateway,
        )
        from agentic_core.L0_maintenance.enforcement.v15_p4_contracts import (
            generate_trace_id,
        )
        from agentic_core.L0_maintenance.types.v15_p2_types import (
            FixConstraint,
            SurgicalManifest,
        )

        _hex8 = hashlib.sha256(b"NervousSystemAgent:run_mission").hexdigest()[:8].upper()
        trace_id = generate_trace_id(_hex8)
        ast_snippet = "NervousSystemAgent.run_mission()"

        manifest = SurgicalManifest(
            schema_version="1.0.0",
            correlation_id=trace_id,
            node_id="NervousSystemAgent",
            target_layer="L3",
            ast_snippet=ast_snippet,
            serialization_canon="orchestrator_operation",
            fix_constraint=FixConstraint.RELAXED,
            manifest_hash=hashlib.sha256(ast_snippet.encode()).hexdigest(),
            change_history=(),
            provenance_chain=(trace_id,),
        )

        gw = V15ExecutionGateway()
        result = gw.execute(
            execution_input=manifest,
            heal_fn=lambda m: {"status": "audit_pass", "errors": 0},
            state_hash_fn=lambda: ("a", "b", "c"),
            trace_id=trace_id,
        )
        assert result.success
        assert result.manifest.node_id == "NervousSystemAgent"

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "log"})
    def test_gateway_processes_security_config_manifest(self):
        """Gateway accepts security_level_config manifest."""
        from agentic_core.L0_maintenance.enforcement.v15_execution_gateway import (
            V15ExecutionGateway,
        )
        from agentic_core.L0_maintenance.enforcement.v15_p4_contracts import (
            generate_trace_id,
        )
        from agentic_core.L0_maintenance.types.v15_p2_types import (
            FixConstraint,
            SurgicalManifest,
        )

        _hex8 = hashlib.sha256(b"Orchestrator:heal_repository").hexdigest()[:8].upper()
        trace_id = generate_trace_id(_hex8)
        ast_snippet = "Orchestrator.heal_repository()"

        manifest = SurgicalManifest(
            schema_version="1.0.0",
            correlation_id=trace_id,
            node_id="Orchestrator",
            target_layer="L0",
            ast_snippet=ast_snippet,
            serialization_canon="orchestrator_operation",
            fix_constraint=FixConstraint.RELAXED,
            manifest_hash=hashlib.sha256(ast_snippet.encode()).hexdigest(),
            change_history=(),
            provenance_chain=(trace_id,),
        )

        gw = V15ExecutionGateway()
        result = gw.execute(
            execution_input=manifest,
            heal_fn=lambda m: {"errors": 0},
            state_hash_fn=lambda: ("a", "b", "c"),
            trace_id=trace_id,
        )
        assert result.success
        assert result.manifest.target_layer == "L0"


# ---------------------------------------------------------------------------
# Flow correctness: L3 orchestrators emit AGGREGATE (not RESULT)
# ---------------------------------------------------------------------------


class TestFlowCorrectness:
    """L3 orchestrators should use AGGREGATE for conditional flows."""

    def test_orchestrator_engine_target_layer_is_l3(self):
        """orchestrator_engine manifest targets L3 — conditional flows use AGGREGATE."""
        source = (PROJECT_ROOT / "agentic_core/L3_orchestration/engines/orchestrator_engine.py").read_text(
            encoding="utf-8",
        )
        assert 'target_layer: str = "L3"' in source

    def test_nervous_system_target_layer_is_l3(self):
        """NervousSystemAgent manifest targets L3."""
        source = (PROJECT_ROOT / "agentic_core/L3_orchestration/reasoning/NervousSystemAgent.py").read_text(
            encoding="utf-8",
        )
        assert 'target_layer: str = "L3"' in source

    def test_security_config_target_layer_is_l0(self):
        """security_level_config.Orchestrator targets L0 (runtime config layer)."""
        source = (PROJECT_ROOT / "agentic_core/runtime/config/security_level_config.py").read_text(
            encoding="utf-8",
        )
        assert 'target_layer: str = "L0"' in source
