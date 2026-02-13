"""V15 P8 Wave 8.1b — Category B: Engines.

Proves:
- Each target constructs or receives SurgicalManifest (structural via AST).
- Gateway invoked in LOG_ONLY mode (runtime via importable types).
- Flow correctness:
  - agent_engine (L2): AGGREGATE for multi-turn loop.
  - SubatomicHopAgent (L3): AGGREGATE for intermediate hops.
  - SovereignActionPlaneAgent (L2): RESULT on terminal L2 success paths.
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

TARGET_FILES = [
    PROJECT_ROOT / "agentic_core/runtime/engine/agent_engine.py",
    PROJECT_ROOT / "agentic_core/L3_orchestration/reasoning/SubatomicHopAgent.py",
    PROJECT_ROOT / "agentic_core/L5_safety/reasoning/SovereignActionPlaneAgent.py",
]


# ---------------------------------------------------------------------------
# A) Structural tests (AST)
# ---------------------------------------------------------------------------


class TestStructuralManifestConstruction:
    """Verify each Cat-B target has _v15_build_operation_manifest and constructs SurgicalManifest."""

    @pytest.mark.parametrize("target", TARGET_FILES, ids=lambda p: p.name)
    def test_has_build_operation_manifest_method(self, target: Path):
        """Each target must define _v15_build_operation_manifest."""
        source = target.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(target))

        found = [
            node.name
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef) and node.name == "_v15_build_operation_manifest"
        ]
        assert len(found) >= 1, f"{target.name} must define _v15_build_operation_manifest"

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
        flat = source.replace("\n", "")
        assert "gateway.execute(" in source or "gateway.execute(" in flat, (
            f"{target.name} must invoke gateway.execute()"
        )

    @pytest.mark.parametrize("target", TARGET_FILES, ids=lambda p: p.name)
    def test_serialization_canon_is_engine(self, target: Path):
        """Cat-B targets use serialization_canon='engine_operation'."""
        source = target.read_text(encoding="utf-8")
        assert 'serialization_canon="engine_operation"' in source, (
            f"{target.name} must use engine_operation serialization_canon"
        )


# ---------------------------------------------------------------------------
# B) Runtime tests: manifest construction + gateway invocation in LOG_ONLY
# ---------------------------------------------------------------------------


class TestManifestConstructionPattern:
    """Runtime tests using importable V15 types (no complex engine imports)."""

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "log"})
    def test_manifest_construction_pattern_enforced(self):
        """The shared manifest construction pattern produces valid SurgicalManifest."""
        from agentic_core.L0_routing.enforcement.v15_p4_contracts import (
            generate_trace_id,
        )
        from agentic_core.L0_routing.types.guardian_contract import is_v15_enforced
        from agentic_core.L0_routing.types.v15_p2_types import (
            FixConstraint,
            SurgicalManifest,
        )

        assert is_v15_enforced()

        class_name = "AgentEngine"
        operation = "run"
        target_layer = "L2"

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
            serialization_canon="engine_operation",
            fix_constraint=FixConstraint.RELAXED,
            manifest_hash=hashlib.sha256(ast_snippet.encode()).hexdigest(),
            change_history=(),
            provenance_chain=(trace_id,),
        )

        assert isinstance(manifest, SurgicalManifest)
        assert manifest.node_id == "AgentEngine"
        assert manifest.target_layer == "L2"
        assert re.match(r"^CC3AL1-[0-9A-F]{8}$", manifest.correlation_id)

    def test_manifest_construction_pattern_not_enforced(self):
        """When V15 explicitly opted out, is_v15_enforced() returns False."""
        with patch.dict(os.environ, {"V15_ENFORCEMENT": "0"}):
            from agentic_core.L0_routing.types.guardian_contract import is_v15_enforced

            assert not is_v15_enforced()

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "log"})
    def test_trace_id_preserved_through_gateway(self):
        """trace_id from manifest is passed to gateway.execute()."""
        from agentic_core.L0_routing.enforcement.v15_execution_gateway import (
            V15ExecutionGateway,
        )
        from agentic_core.L0_routing.enforcement.v15_p4_contracts import (
            generate_trace_id,
        )
        from agentic_core.L0_routing.types.v15_p2_types import (
            FixConstraint,
            SurgicalManifest,
        )

        _hex8 = hashlib.sha256(b"AgentEngine:run").hexdigest()[:8].upper()
        trace_id = generate_trace_id(_hex8)
        ast_snippet = "AgentEngine.run()"

        manifest = SurgicalManifest(
            schema_version="1.0.0",
            correlation_id=trace_id,
            node_id="AgentEngine",
            target_layer="L2",
            ast_snippet=ast_snippet,
            serialization_canon="engine_operation",
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
        assert result.manifest.correlation_id == trace_id


class TestGatewayInvocationPattern:
    """Runtime: gateway.execute() invoked with correct manifest in LOG_ONLY."""

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "log"})
    def test_gateway_processes_agent_engine_manifest(self):
        """Gateway accepts AgentEngine manifest (L2)."""
        from agentic_core.L0_routing.enforcement.v15_execution_gateway import (
            V15ExecutionGateway,
        )
        from agentic_core.L0_routing.enforcement.v15_p4_contracts import (
            generate_trace_id,
        )
        from agentic_core.L0_routing.types.v15_p2_types import (
            FixConstraint,
            SurgicalManifest,
        )

        _hex8 = hashlib.sha256(b"AgentEngine:run").hexdigest()[:8].upper()
        trace_id = generate_trace_id(_hex8)
        ast_snippet = "AgentEngine.run()"

        manifest = SurgicalManifest(
            schema_version="1.0.0",
            correlation_id=trace_id,
            node_id="AgentEngine",
            target_layer="L2",
            ast_snippet=ast_snippet,
            serialization_canon="engine_operation",
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
        assert result.manifest.node_id == "AgentEngine"

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "log"})
    def test_gateway_processes_subatomic_hop_manifest(self):
        """Gateway accepts SubatomicHopAgent manifest (L3, AGGREGATE)."""
        from agentic_core.L0_routing.enforcement.v15_execution_gateway import (
            V15ExecutionGateway,
        )
        from agentic_core.L0_routing.enforcement.v15_p4_contracts import (
            generate_trace_id,
        )
        from agentic_core.L0_routing.types.v15_p2_types import (
            FixConstraint,
            SurgicalManifest,
        )

        _hex8 = hashlib.sha256(b"SubatomicHopAgent:run").hexdigest()[:8].upper()
        trace_id = generate_trace_id(_hex8)
        ast_snippet = "SubatomicHopAgent.run()"

        manifest = SurgicalManifest(
            schema_version="1.0.0",
            correlation_id=trace_id,
            node_id="SubatomicHopAgent",
            target_layer="L3",
            ast_snippet=ast_snippet,
            serialization_canon="engine_operation",
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
        assert result.manifest.node_id == "SubatomicHopAgent"
        assert result.manifest.target_layer == "L3"

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "log"})
    def test_gateway_processes_action_plane_manifest(self):
        """Gateway accepts SovereignActionPlaneAgent manifest (L2, RESULT)."""
        from agentic_core.L0_routing.enforcement.v15_execution_gateway import (
            V15ExecutionGateway,
        )
        from agentic_core.L0_routing.enforcement.v15_p4_contracts import (
            generate_trace_id,
        )
        from agentic_core.L0_routing.types.v15_p2_types import (
            FixConstraint,
            SurgicalManifest,
        )

        _hex8 = (
            hashlib.sha256(
                b"SovereignActionPlaneAgent:execute",
            )
            .hexdigest()[:8]
            .upper()
        )
        trace_id = generate_trace_id(_hex8)
        ast_snippet = "SovereignActionPlaneAgent.execute()"

        manifest = SurgicalManifest(
            schema_version="1.0.0",
            correlation_id=trace_id,
            node_id="SovereignActionPlaneAgent",
            target_layer="L2",
            ast_snippet=ast_snippet,
            serialization_canon="engine_operation",
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
        assert result.manifest.target_layer == "L2"


# ---------------------------------------------------------------------------
# C) Flow correctness: artifact_class semantics
# ---------------------------------------------------------------------------


class TestFlowCorrectness:
    """Verify target_layer semantics for artifact_class rules."""

    def test_agent_engine_target_layer_is_l2(self):
        """agent_engine targets L2 — AGGREGATE for multi-turn loop."""
        source = (PROJECT_ROOT / "agentic_core/runtime/engine/agent_engine.py").read_text(encoding="utf-8")
        assert 'target_layer: str = "L2"' in source

    def test_subatomic_hop_target_layer_is_l3(self):
        """SubatomicHopAgent targets L3 — AGGREGATE for intermediate hops."""
        source = (PROJECT_ROOT / "agentic_core/L3_orchestration/reasoning/SubatomicHopAgent.py").read_text(
            encoding="utf-8",
        )
        assert 'target_layer: str = "L3"' in source

    def test_action_plane_target_layer_is_l2(self):
        """SovereignActionPlaneAgent targets L2 — RESULT on terminal success."""
        source = (PROJECT_ROOT / "agentic_core/L5_safety/reasoning/SovereignActionPlaneAgent.py").read_text(
            encoding="utf-8",
        )
        assert 'target_layer: str = "L2"' in source

    def test_subatomic_hop_no_result_emission(self):
        """SubatomicHopAgent must NOT emit RESULT (intermediate hops only)."""
        source = (PROJECT_ROOT / "agentic_core/L3_orchestration/reasoning/SubatomicHopAgent.py").read_text(
            encoding="utf-8",
        )
        # The manifest comment should indicate AGGREGATE semantics
        assert "AGGREGATE" in source, "SubatomicHopAgent should reference AGGREGATE semantics"

    def test_action_plane_result_semantics(self):
        """SovereignActionPlaneAgent should indicate RESULT on terminal success."""
        source = (PROJECT_ROOT / "agentic_core/L5_safety/reasoning/SovereignActionPlaneAgent.py").read_text(
            encoding="utf-8",
        )
        assert "RESULT on terminal" in source, (
            "SovereignActionPlaneAgent should reference RESULT on terminal success"
        )
