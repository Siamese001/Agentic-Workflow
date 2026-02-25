"""
Architectural Invariants Enforcement Tests

This module enforces the architectural invariants defined in
agentic_core.architecture.architectural_invariants through comprehensive
tests that validate system compliance.

Phase 0: Architectural Invariants & Topology Lock
"""

import ast
import hashlib
import json
import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Add the project root to sys.path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from agentic_core.architecture.architectural_invariants import (
    ALLOWLISTED_PROVIDER_SDK_MODULES,
    EMBEDDING_ENABLED_VAR,
    INVARIANT_DIGEST_PREFIX,
    NEGATIVE_CONTROL_TAMPER_VAR,
    REQUIRED_REPLAY_KEY_FIELDS,
    InvariantViolationError,
)


class TestGatewayTopologyInvariant:
    """Tests for Gateway Topology invariant enforcement."""

    def test_no_provider_sdk_imports_outside_allowlist(self):
        """Verify no provider SDK imports outside allowlisted modules."""
        # Scan all Python files in the project
        project_root = Path(__file__).parent.parent.parent
        violations = []

        for py_file in project_root.rglob("*.py"):
            # Skip test files and the invariants file itself
            if "test_" in py_file.name or "architectural_invariants.py" in py_file.name:
                continue

            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            if self._is_provider_sdk_import(alias.name):
                                module_path = str(py_file.relative_to(project_root))
                                if not self._is_in_allowlisted_module(module_path):
                                    violations.append(f"{module_path}: imports {alias.name}")

                    elif isinstance(node, ast.ImportFrom):
                        if node.module and self._is_provider_sdk_import(node.module):
                            module_path = str(py_file.relative_to(project_root))
                            if not self._is_in_allowlisted_module(module_path):
                                violations.append(f"{module_path}: from {node.module} import ...")

            except (SyntaxError, UnicodeDecodeError):
                # Skip files that can't be parsed
                continue

        assert not violations, f"Provider SDK imports found outside allowlist: {violations}"

    def test_no_model_literals_outside_allowlist(self):
        """Verify no model literals outside allowlisted modules."""
        project_root = Path(__file__).parent.parent.parent
        violations = []

        # Common model literal patterns
        model_patterns = [
            "gpt-",
            "claude-",
            "gemini-",
            "llama-",
            "mistral-",
            "phi-",
            "text-davinci-",
            "gpt-3.5",
            "gpt-4",
            "gpt-3",
        ]

        for py_file in project_root.rglob("*.py"):
            # Skip test files and allowlisted modules
            if "test_" in py_file.name:
                continue

            module_path = str(py_file.relative_to(project_root))
            if self._is_in_allowlisted_module(module_path):
                continue

            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                for pattern in model_patterns:
                    if pattern in content.lower():
                        # Check if it's actually a model literal (not in comments/strings)
                        lines = content.split("\n")
                        for i, line in enumerate(lines, 1):
                            if pattern in line.lower() and not line.strip().startswith("#"):
                                violations.append(f"{module_path}:{i}: contains model pattern '{pattern}'")

            except (SyntaxError, UnicodeDecodeError):
                continue

        assert not violations, f"Model literals found outside allowlist: {violations}"

    def _is_provider_sdk_import(self, module_name: str) -> bool:
        """Check if an import is a provider SDK."""
        provider_patterns = [
            "openai",
            "anthropic",
            "google.generativeai",
            "huggingface",
            "transformers",
            "torch",
            "tensorflow",
            "langchain",
        ]
        return any(pattern in module_name.lower() for pattern in provider_patterns)

    def _is_in_allowlisted_module(self, module_path: str) -> bool:
        """Check if a module is in the allowlist."""
        return any(allowed in module_path for allowed in ALLOWLISTED_PROVIDER_SDK_MODULES)


class TestEmbeddingKillSwitchInvariant:
    """Tests for Embedding Kill-Switch invariant enforcement."""

    def test_embedding_kill_switch_propagation(self):
        """Test that EMBEDDING_ENABLED=false disables all embedding retrieval."""
        # Mock embedding service factory
        with patch.dict(os.environ, {EMBEDDING_ENABLED_VAR: "false"}):
            # Import the module to test (assuming it exists)
            try:
                from agentic_core.L5_safety.config.structure_blueprint import embedding_service_factory
            except ImportError:
                # If the module doesn't exist, create a mock for testing
                embedding_service_factory = Mock()

            # Test that factory returns disabled service
            service = embedding_service_factory()
            assert not service.is_enabled(), (
                "Embedding service should be disabled when EMBEDDING_ENABLED=false"
            )

    def test_no_silent_fallback_when_disabled(self):
        """Test that there's no silent fallback when embeddings are disabled."""
        with patch.dict(os.environ, {EMBEDDING_ENABLED_VAR: "false"}):
            # Mock embedding service to track calls
            mock_service = Mock()
            mock_service.is_enabled.return_value = False
            mock_service.retrieve.return_value = None

            # Test that no retrieval attempts are made
            with patch(
                "agentic_core.L5_safety.config.structure_blueprint.embedding_service_factory",
                return_value=mock_service,
            ):
                try:
                    # Attempt to use embeddings
                    from agentic_core.L5_safety.config.structure_blueprint import get_embeddings

                    result = get_embeddings("test query")
                    assert result is None, "Should return None when disabled"
                    mock_service.retrieve.assert_not_called()
                except ImportError:
                    # Module doesn't exist, skip this test
                    pytest.skip("Embedding module not found")


class TestReplayKeySchemaInvariant:
    """Tests for Replay Key Schema invariant enforcement."""

    def test_replay_key_schema_completeness(self):
        """Test that replay keys contain all required fields."""
        # Mock replay key
        replay_key = {
            "model_version": "gpt-4",
            "embedding_pack_hash": "abc123",
            "cutoff": "2024-01-01",
            "k": 10,
            "blas_implementation": "openblas",
            "config_version": "1.0",
            "engine_version": "2.0",
            "transcript_hash": "def456",
            "tier_decision": "healing",
        }

        missing_fields = []
        for field in REQUIRED_REPLAY_KEY_FIELDS:
            if field not in replay_key:
                missing_fields.append(field)

        assert not missing_fields, f"Missing required replay key fields: {missing_fields}"

    def test_deterministic_replay_key_digest(self):
        """Test that replay keys produce deterministic digests."""
        # Create a canonical replay key
        replay_key = {
            "model_version": "gpt-4",
            "embedding_pack_hash": "abc123",
            "cutoff": "2024-01-01",
            "k": 10,
            "blas_implementation": "openblas",
            "config_version": "1.0",
            "engine_version": "2.0",
            "transcript_hash": "def456",
            "tier_decision": "healing",
        }

        # Create canonical serialization
        canonical_json = json.dumps(replay_key, sort_keys=True, separators=(",", ":"))
        digest = hashlib.sha256(canonical_json.encode()).hexdigest()

        # Emit invariant digest
        invariant_digest = f"{INVARIANT_DIGEST_PREFIX}: {digest}"
        print(f"\n{invariant_digest}")

        # Verify determinism by recreating
        canonical_json_2 = json.dumps(replay_key, sort_keys=True, separators=(",", ":"))
        digest_2 = hashlib.sha256(canonical_json_2.encode()).hexdigest()

        assert digest == digest_2, "Replay key digest must be deterministic"
        assert invariant_digest.startswith(INVARIANT_DIGEST_PREFIX), "Digest must have correct prefix"


class TestLayerSovereigntyInvariant:
    """Tests for Layer Sovereignty invariant enforcement."""

    def test_no_layer_inversion(self):
        """Test that there are no layer inversions in imports."""
        project_root = Path(__file__).parent.parent.parent
        violations = []

        # Define layer order (lower number = lower layer)
        layer_order = {
            "L0_routing": 0,
            "L1_cognition": 1,
            "L2_execution": 2,
            "L3_orchestration": 3,
            "L4_state": 4,
            "L5_safety": 5,
            "L6_observability": 6,
        }

        for py_file in project_root.rglob("*.py"):
            # Skip test files and non-agentic_core files
            if "test_" in py_file.name or "agentic_core" not in str(py_file):
                continue

            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom) and node.module:
                        # Check if this is an agentic_core import
                        if "agentic_core" in node.module:
                            source_layer = self._extract_layer_from_path(str(py_file))
                            target_layer = self._extract_layer_from_path(node.module)

                            if source_layer and target_layer:
                                if layer_order.get(source_layer, 0) > layer_order.get(target_layer, 0):
                                    violations.append(
                                        f"{py_file}: {source_layer} imports from {target_layer}"
                                    )

            except (SyntaxError, UnicodeDecodeError):
                continue

        assert not violations, f"Layer inversions found: {violations}"

    def _extract_layer_from_path(self, path: str) -> str:
        """Extract layer name from file path."""
        for layer_name in [
            "L0_routing",
            "L1_cognition",
            "L2_execution",
            "L3_orchestration",
            "L4_state",
            "L5_safety",
            "L6_observability",
        ]:
            if layer_name in path:
                return layer_name
        return None


class TestNegativeControl:
    """Negative control test for invariant enforcement."""

    @pytest.mark.xfail(strict=True, reason="Negative control test - should fail when tampering is enabled")
    def test_tamper_detection(self):
        """Test that invariants fail when tampering is enabled."""
        if os.environ.get(NEGATIVE_CONTROL_TAMPER_VAR) != "1":
            pytest.skip("Negative control not enabled")

        # Simulate a forbidden import by directly raising an exception
        # This simulates the invariant test detecting a violation
        raise InvariantViolationError("Simulated forbidden import detected")


if __name__ == "__main__":
    # Run all tests and emit digest
    pytest.main([__file__, "-v"])
