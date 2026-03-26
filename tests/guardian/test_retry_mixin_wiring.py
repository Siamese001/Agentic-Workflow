"""V15 P8.1d — Category D: Retry Mixin Wiring Tests.

Structural (AST) + runtime tests proving:
- SurgicalManifest is constructed once before the retry loop
- trace_id remains stable across all retry attempts
- gateway.execute receives the same manifest instance
- No RESULT emitted from retry wrapper itself
- Manifest + trace_id survive >=2 retries
- Retry wrapper does not drop kwargs
"""

from __future__ import annotations

import ast
import os
import re
from pathlib import Path
from unittest.mock import patch

#  # MOVED: from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
)
#  # MOVED: from agentic_core.L0_routing.types.determinism_types import (
    SurgicalManifest,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MIXIN_PATH = PROJECT_ROOT / AGENTIC_CORE_DIR / "mixins" / "tool_reliability_mixin.py"
MIXIN_SRC = MIXIN_PATH.read_text(encoding="utf-8")
MIXIN_AST = ast.parse(MIXIN_SRC)


# ---------------------------------------------------------------------------
# AST helpers
# ---------------------------------------------------------------------------


def _find_method_node(tree: ast.Module, class_name: str, method_name: str):
    """Find a method inside a class in the AST."""
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for item in ast.walk(node):
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == method_name:
                    return item
    return None


def _method_body_source(class_name: str, method_name: str) -> str:
    """Extract source lines of a method body."""
    node = _find_method_node(MIXIN_AST, class_name, method_name)
    if node is None:
        return ""
    start = node.lineno - 1
    end = node.end_lineno or start + 1
    lines = MIXIN_SRC.splitlines()
    return "\n".join(lines[start:end])


# ===========================================================================
# A) Structural (AST) Tests
# ===========================================================================


class TestStructuralRetryMixin:
    """AST-level proof of retry mixin wiring."""

    def test_build_retry_manifest_exists(self):
                from agentic_core.L0_routing.config.path_constants import (
                from agentic_core.L0_routing.types.determinism_types import (
                from agentic_core.mixins.tool_reliability_mixin import ToolReliabilityMixin
                from agentic_core.L0_routing.enforcement.execution_gateway import (
                from agentic_core.L0_routing.enforcement.execution_gateway import (
                node = _find_method_node(MIXIN_AST, "ToolReliabilityMixin", "_v15_build_retry_manifest")
                assert node is not None

        assert node is not None

    def test_retry_audit_exists(self):
        node = _find_method_node(MIXIN_AST, "ToolReliabilityMixin", "_v15_retry_audit")
        assert node is not None

    def test_with_retry_calls_build_manifest(self):
    """Test with_retry_calls_build_manifest runtime behavior."""
    # Arrange
    # TODO: Set up execution parameters
    input_data = {}  # Replace with actual test data
    """Test with_retry_sync_calls_build_manifest runtime behavior."""
    # Arrange
    # TODO: Set up execution parameters
    input_data = {}  # Replace with actual test data
    """Test with_retry_calls_audit runtime behavior."""
    # Arrange
    # TODO: Set up execution parameters
    input_data = {}  # Replace with actual test data
    """Test with_retry_sync_calls_audit runtime behavior."""
    # Arrange
    # TODO: Set up execution parameters
    input_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute with_retry_sync_calls_audit
    result = None  # Replace with actual execution

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"
    # TODO: Add specific execution assertions
        loop_pos = body.find("for attempt in range")
        assert manifest_pos < loop_pos, "manifest must be built before retry loop"

    def test_build_manifest_constructs_surgical_manifest(self):
        body = _method_body_source("ToolReliabilityMixin", "_v15_build_retry_manifest")
        assert "SurgicalManifest(" in body
    def test_build_manifest_checks_enforcement(self):
        body = _method_body_source("ToolReliabilityMixin", "_v15_build_retry_manifest")
        assert "is_v15_enforced()" in body
    def test_audit_calls_gateway_execute(self):
    """Test audit_calls_gateway_execute runtime behavior."""
    # Arrange
    # TODO: Set up execution parameters
    input_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute audit_calls_gateway_execute
    result = None  # Replace with actual execution

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"
    # TODO: Add specific execution assertions
            body = _method_body_source("ToolReliabilityMixin", method)
            # RESULT should not appear as an artifact_class in retry bodies
            assert "RESULT" not in body or "retry_audit" in body
# ===========================================================================
# B) Runtime Tests — manifest + trace_id survive retries
# ===========================================================================
class _StubMixin:
    """Minimal stub to test ToolReliabilityMixin without deep agent deps."""
    def __init__(self):
        # Satisfy ToolReliabilityMixin.__init__ expectations
        import threading
        self._retry_policies = {}
        self._circuit_configs = {}
        self._tool_health = {}
        self._circuit_opened_at = {}
        self._half_open_calls = {}
        self._reliability_lock = threading.RLock()
        self._tool_reliability_initialized = True
class _TestableReliabilityMixin(_StubMixin):
    """Combine stub with the real mixin methods for isolated testing."""
    pass
# Dynamically attach mixin methods to the testable class
#  # MOVED: from agentic_core.mixins.tool_reliability_mixin import ToolReliabilityMixin

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300

for _name in (
    "_v15_build_retry_manifest",
    "_v15_retry_audit",
    "with_retry_sync",
    "_check_circuit_breaker",
    "_record_success",
    "_record_failure",
    "_calculate_delay",
    "_ensure_tool_health",
    "configure_tool_retry",
):
    setattr(_TestableReliabilityMixin, _name, getattr(ToolReliabilityMixin, _name))
class TestRuntimeRetryManifest:
    """Runtime proof that manifest + trace_id survive retries."""
    @patch.dict(os.environ, {"V15_ENFORCEMENT": "log"})
    def test_manifest_constructed_when_enforced(self):
        mixin = _TestableReliabilityMixin()
        manifest = mixin._v15_build_retry_manifest("test_tool")
        assert manifest is not None
        assert isinstance(manifest, SurgicalManifest)
        assert manifest.target_layer == "L2"
        assert manifest.serialization_canon == "tool_reliability_mixin"
    @patch.dict(os.environ, {"V15_ENFORCEMENT": "0"})
    def test_manifest_none_when_not_enforced(self):
        mixin = _TestableReliabilityMixin()
        manifest = mixin._v15_build_retry_manifest("test_tool")
        assert manifest is None
    @patch.dict(os.environ, {"V15_ENFORCEMENT": "log"})
    def test_trace_id_format(self):
        mixin = _TestableReliabilityMixin()
        manifest = mixin._v15_build_retry_manifest("test_tool")
        assert manifest is not None
        assert re.match(r"^CC3AL1-[0-9A-F]{8}$", manifest.correlation_id)
    @patch.dict(os.environ, {"V15_ENFORCEMENT": "log"})
    def test_manifest_survives_multiple_retries_sync(self):
        """Prove manifest + trace_id are stable across >=2 retries."""
#  # MOVED: from agentic_core.L0_routing.enforcement.execution_gateway import (
            V15ExecutionGateway,
        )
        mixin = _TestableReliabilityMixin()
        mixin.configure_tool_retry("flaky", max_retries=MAX_RETRIES, base_delay_seconds=0.0, jitter=False)
        captured_manifests = []
        _orig = V15ExecutionGateway.execute
        def _spy(self_gw, execution_input, *args, **kwargs):
            captured_manifests.append(execution_input)
            return _orig(self_gw, execution_input, *args, **kwargs)
        call_count = 0
        def _flaky_op():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError(f"Flaky failure #{call_count}")
            return "success"
        with patch.object(V15ExecutionGateway, "execute", _spy):
            result = mixin.with_retry_sync("flaky", _flaky_op)
        assert result == "success"
        assert call_count == 3, "operation should have been called 3 times"
        # Manifest was constructed once and passed to gateway once (at entry)
        assert len(captured_manifests) == 1
        assert isinstance(captured_manifests[0], SurgicalManifest)
    @patch.dict(os.environ, {"V15_ENFORCEMENT": "log"})
    def test_trace_id_stable_across_retries(self):
        """The single manifest's trace_id must not change across retries."""
        mixin = _TestableReliabilityMixin()
        mixin.configure_tool_retry("flaky2", max_retries=MAX_RETRIES, base_delay_seconds=0.0, jitter=False)
        # Build manifest once (same as what with_retry_sync does internally)
        manifest = mixin._v15_build_retry_manifest("flaky2")
        assert manifest is not None
        trace_id_before = manifest.correlation_id
        # Simulate retries — manifest object is the same, trace_id unchanged
        call_count = 0
        def _flaky():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("fail")
            return "ok"
        result = mixin.with_retry_sync("flaky2", _flaky)
        assert result == "ok"
        # Build manifest again with same tool_name — deterministic trace_id
        manifest2 = mixin._v15_build_retry_manifest("flaky2")
        assert manifest2.correlation_id == trace_id_before
    @patch.dict(os.environ, {"V15_ENFORCEMENT": "log"})
    def test_gateway_receives_manifest_instance(self):
        """Gateway.execute must receive the exact manifest instance."""
#  # MOVED: from agentic_core.L0_routing.enforcement.execution_gateway import (
            V15ExecutionGateway,
        )
        mixin = _TestableReliabilityMixin()
        captured = []
        _orig = V15ExecutionGateway.execute
        def _spy(self_gw, execution_input, *args, **kwargs):
            captured.append({"manifest": execution_input, "trace_id": kwargs.get("trace_id")})
            return _orig(self_gw, execution_input, *args, **kwargs)
        manifest = mixin._v15_build_retry_manifest("gw_test")
        assert manifest is not None
        with patch.object(V15ExecutionGateway, "execute", _spy):
            mixin._v15_retry_audit(manifest, trace_id=manifest.correlation_id)
        assert len(captured) == 1
        assert captured[0]["manifest"] is manifest
        assert captured[0]["trace_id"] == manifest.correlation_id
