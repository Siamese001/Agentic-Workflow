"""Comprehensive tests for Prompt Lifecycle data contracts.

Tests all four Phase 1 data contracts:
- PromptBOM
- CompiledPromptArtifact
- TemplateManifest
- InstructionPacket
"""

import hashlib
import hmac
import unittest
from typing import Any

from agentic_core.L0_routing.types.l0_instruction_packet import InstructionPacket
from agentic_core.prompt_governance.contracts import (
    CompiledPromptArtifact,
    PromptBOM,
    TemplateManifest,
)
from agentic_core.prompt_governance.contracts.compiled_artifact_types import (
    CompiledPromptArtifact as CompiledPromptArtifactDirect,
)
from agentic_core.prompt_governance.contracts.prompt_bom_types import PromptBOM as PromptBOMDirect
from agentic_core.prompt_governance.contracts.template_manifest_types import (
    TemplateManifest as TemplateManifestDirect,
)


class TestPromptBOM(unittest.TestCase):
    """Test PromptBOM data contract."""

    def test_creation_valid(self) -> None:
        """Test creating a valid PromptBOM."""
        bom = PromptBOM(
            trace_id="trace-123",
            system_version_hash="sha256-hash",
            mixins_required=("mixin1", "mixin2"),
            raw_u0="User input",
            raw_c0={"key": "value"},
            template_args={"var": "value"},
            path="A",
        )
        self.assertEqual(bom.trace_id, "trace-123")
        self.assertEqual(bom.path, "A")

    def test_creation_invalid_path(self) -> None:
        """Test that invalid path raises ValueError."""
        with self.assertRaises(ValueError):
            PromptBOM(
                trace_id="trace-123",
                system_version_hash="sha256-hash",
                mixins_required=(),
                raw_u0="User input",
                raw_c0={},
                template_args={},
                path="E",  # Invalid path
            )

    def test_empty_trace_id_raises(self) -> None:
        """Test that empty trace_id raises ValueError."""
        with self.assertRaises(ValueError):
            PromptBOM(
                trace_id="",
                system_version_hash="sha256-hash",
                mixins_required=(),
                raw_u0="User input",
                raw_c0={},
                template_args={},
                path="A",
            )

    def test_empty_system_hash_raises(self) -> None:
        """Test that empty system_version_hash raises ValueError."""
        with self.assertRaises(ValueError):
            PromptBOM(
                trace_id="trace-123",
                system_version_hash="",
                mixins_required=(),
                raw_u0="User input",
                raw_c0={},
                template_args={},
                path="A",
            )

    def test_to_dict(self) -> None:
        """Test conversion to dictionary."""
        bom = PromptBOM(
            trace_id="trace-123",
            system_version_hash="sha256-hash",
            mixins_required=("mixin2", "mixin1"),  # Unsorted
            raw_u0="User input",
            raw_c0={"key": "value"},
            template_args={"var": "value"},
            path="B",
        )
        d = bom.to_dict()
        self.assertEqual(d["trace_id"], "trace-123")
        self.assertEqual(d["path"], "B")
        # Mixins should be sorted in to_dict
        self.assertEqual(d["mixins_required"], ("mixin1", "mixin2"))

    def test_stable_hash(self) -> None:
        """Test stable hash computation."""
        bom1 = PromptBOM(
            trace_id="trace-123",
            system_version_hash="sha256-hash",
            mixins_required=("mixin1",),
            raw_u0="User input",
            raw_c0={},
            template_args={},
            path="A",
        )
        bom2 = PromptBOM(
            trace_id="trace-123",
            system_version_hash="sha256-hash",
            mixins_required=("mixin1",),
            raw_u0="User input",
            raw_c0={},
            template_args={},
            path="A",
        )
        self.assertEqual(bom1.stable_hash(), bom2.stable_hash())

    def test_all_paths_valid(self) -> None:
        """Test that all valid paths work."""
        for path in ("A", "B", "C", "D"):
            bom = PromptBOM(
                trace_id=f"trace-{path}",
                system_version_hash="hash",
                mixins_required=(),
                raw_u0="Input",
                raw_c0={},
                template_args={},
                path=path,  # type: ignore[arg-type]
            )
            self.assertEqual(bom.path, path)


class TestCompiledPromptArtifact(unittest.TestCase):
    """Test CompiledPromptArtifact data contract."""

    def test_creation_valid(self) -> None:
        """Test creating a valid CompiledPromptArtifact."""
        artifact = CompiledPromptArtifact(
            trace_id="trace-123",
            final_system_string="System prompt",
            final_user_string="User prompt",
            allowed_tools_schema=(),
            token_estimate=100,
            signature="hmac-signature",
        )
        self.assertEqual(artifact.trace_id, "trace-123")
        self.assertEqual(artifact.token_estimate, 100)

    def test_empty_trace_id_raises(self) -> None:
        """Test that empty trace_id raises ValueError."""
        with self.assertRaises(ValueError):
            CompiledPromptArtifact(
                trace_id="",
                final_system_string="System",
                final_user_string="User",
                allowed_tools_schema=(),
                token_estimate=100,
                signature="sig",
            )

    def test_negative_token_estimate_raises(self) -> None:
        """Test that negative token_estimate raises ValueError."""
        with self.assertRaises(ValueError):
            CompiledPromptArtifact(
                trace_id="trace-123",
                final_system_string="System",
                final_user_string="User",
                allowed_tools_schema=(),
                token_estimate=-1,
                signature="sig",
            )

    def test_verify_signature_valid(self) -> None:
        """Test signature verification with valid key."""
        secret_key = b"test-secret-key"
        # Create artifact with proper signature
        canonical = str({
            "trace_id": "trace-123",
            "final_system_string": "System",
            "final_user_string": "User",
            "allowed_tools_schema": (),
            "token_estimate": 100,
        })
        signature = hmac.new(
            secret_key, canonical.encode("utf-8"), hashlib.sha256
        ).hexdigest()

        artifact = CompiledPromptArtifact(
            trace_id="trace-123",
            final_system_string="System",
            final_user_string="User",
            allowed_tools_schema=(),
            token_estimate=100,
            signature=signature,
        )
        self.assertTrue(artifact.verify_signature(secret_key))

    def test_verify_signature_invalid(self) -> None:
        """Test signature verification with invalid key."""
        artifact = CompiledPromptArtifact(
            trace_id="trace-123",
            final_system_string="System",
            final_user_string="User",
            allowed_tools_schema=(),
            token_estimate=100,
            signature="wrong-signature",
        )
        self.assertFalse(artifact.verify_signature(b"different-key"))

    def test_to_dict(self) -> None:
        """Test conversion to dictionary."""
        artifact = CompiledPromptArtifact(
            trace_id="trace-123",
            final_system_string="System",
            final_user_string="User",
            allowed_tools_schema=(),
            token_estimate=100,
            signature="sig",
        )
        d = artifact.to_dict()
        self.assertEqual(d["trace_id"], "trace-123")
        self.assertEqual(d["token_estimate"], 100)


class TestTemplateManifest(unittest.TestCase):
    """Test TemplateManifest data contract."""

    def test_creation_valid(self) -> None:
        """Test creating a valid TemplateManifest."""
        manifest = TemplateManifest(
            template_id="template-123",
            version="1.0.0",
            git_commit_hash="abc123",
            required_variables=("var1", "var2"),
            schema_version="1.0",
        )
        self.assertEqual(manifest.template_id, "template-123")
        self.assertEqual(manifest.schema_version, "1.0")

    def test_empty_template_id_raises(self) -> None:
        """Test that empty template_id raises ValueError."""
        with self.assertRaises(ValueError):
            TemplateManifest(
                template_id="",
                version="1.0.0",
                git_commit_hash="abc123",
                required_variables=(),
            )

    def test_empty_version_raises(self) -> None:
        """Test that empty version raises ValueError."""
        with self.assertRaises(ValueError):
            TemplateManifest(
                template_id="template-123",
                version="",
                git_commit_hash="abc123",
                required_variables=(),
            )

    def test_empty_git_commit_raises(self) -> None:
        """Test that empty git_commit_hash raises ValueError."""
        with self.assertRaises(ValueError):
            TemplateManifest(
                template_id="template-123",
                version="1.0.0",
                git_commit_hash="",
                required_variables=(),
            )

    def test_default_schema_version(self) -> None:
        """Test default schema_version."""
        manifest = TemplateManifest(
            template_id="template-123",
            version="1.0.0",
            git_commit_hash="abc123",
            required_variables=(),
        )
        self.assertEqual(manifest.schema_version, "1.0")

    def test_to_dict(self) -> None:
        """Test conversion to dictionary."""
        manifest = TemplateManifest(
            template_id="template-123",
            version="1.0.0",
            git_commit_hash="abc123",
            required_variables=("var2", "var1"),  # Unsorted
        )
        d = manifest.to_dict()
        # Variables should be sorted in to_dict
        self.assertEqual(d["required_variables"], ("var1", "var2"))

    def test_stable_hash(self) -> None:
        """Test stable hash computation."""
        manifest1 = TemplateManifest(
            template_id="template-123",
            version="1.0.0",
            git_commit_hash="abc123",
            required_variables=("var1",),
        )
        manifest2 = TemplateManifest(
            template_id="template-123",
            version="1.0.0",
            git_commit_hash="abc123",
            required_variables=("var1",),
        )
        self.assertEqual(manifest1.stable_hash(), manifest2.stable_hash())


class TestInstructionPacket(unittest.TestCase):
    """Test InstructionPacket data contract."""

    def test_creation_valid(self) -> None:
        """Test creating a valid InstructionPacket."""
        packet = InstructionPacket(
            trace_id="trace-123",
            path="A",
            intent_class="classification",
            required_mixins=("mixin1",),
            escalation_threshold=0.9,
        )
        self.assertEqual(packet.trace_id, "trace-123")
        self.assertEqual(packet.path, "A")
        self.assertEqual(packet.escalation_threshold, 0.9)

    def test_invalid_path_raises(self) -> None:
        """Test that invalid path raises ValueError."""
        with self.assertRaises(ValueError):
            InstructionPacket(
                trace_id="trace-123",
                path="E",  # Invalid
                intent_class="classification",
                required_mixins=(),
            )

    def test_empty_trace_id_raises(self) -> None:
        """Test that empty trace_id raises ValueError."""
        with self.assertRaises(ValueError):
            InstructionPacket(
                trace_id="",
                path="A",
                intent_class="classification",
                required_mixins=(),
            )

    def test_empty_intent_class_raises(self) -> None:
        """Test that empty intent_class raises ValueError."""
        with self.assertRaises(ValueError):
            InstructionPacket(
                trace_id="trace-123",
                path="A",
                intent_class="",
                required_mixins=(),
            )

    def test_escalation_threshold_bounds(self) -> None:
        """Test escalation threshold bounds."""
        # Valid bounds
        InstructionPacket(
            trace_id="trace-123",
            path="A",
            intent_class="classification",
            required_mixins=(),
            escalation_threshold=0.0,
        )
        InstructionPacket(
            trace_id="trace-123",
            path="A",
            intent_class="classification",
            required_mixins=(),
            escalation_threshold=1.0,
        )

        # Invalid bounds
        with self.assertRaises(ValueError):
            InstructionPacket(
                trace_id="trace-123",
                path="A",
                intent_class="classification",
                required_mixins=(),
                escalation_threshold=-0.1,
            )
        with self.assertRaises(ValueError):
            InstructionPacket(
                trace_id="trace-123",
                path="A",
                intent_class="classification",
                required_mixins=(),
                escalation_threshold=1.1,
            )

    def test_default_escalation_threshold(self) -> None:
        """Test default escalation threshold."""
        packet = InstructionPacket(
            trace_id="trace-123",
            path="A",
            intent_class="classification",
            required_mixins=(),
        )
        self.assertEqual(packet.escalation_threshold, 0.85)

    def test_all_paths_valid(self) -> None:
        """Test that all valid paths work."""
        for path in ("A", "B", "C", "D"):
            packet = InstructionPacket(
                trace_id=f"trace-{path}",
                path=path,  # type: ignore[arg-type]
                intent_class="classification",
                required_mixins=(),
            )
            self.assertEqual(packet.path, path)


class TestContractExports(unittest.TestCase):
    """Test that all contracts are properly exported."""

    def test_prompt_bom_exported(self) -> None:
        """Test PromptBOM is exported from contracts module."""
        from agentic_core.prompt_governance.contracts import PromptBOM as ExportedBOM
        self.assertIs(ExportedBOM, PromptBOMDirect)

    def test_compiled_artifact_exported(self) -> None:
        """Test CompiledPromptArtifact is exported from contracts module."""
        from agentic_core.prompt_governance.contracts import (
            CompiledPromptArtifact as ExportedArtifact,
        )
        self.assertIs(ExportedArtifact, CompiledPromptArtifactDirect)

    def test_template_manifest_exported(self) -> None:
        """Test TemplateManifest is exported from contracts module."""
        from agentic_core.prompt_governance.contracts import (
            TemplateManifest as ExportedManifest,
        )
        self.assertIs(ExportedManifest, TemplateManifestDirect)


if __name__ == "__main__":
    unittest.main()
