"""End-to-end smoke tests for the Prompt Lifecycle & Taxonomy system.

These tests verify the complete flow from intent to LLM execution.
"""

import hashlib
import hmac
import unittest

from agentic_core.L0_routing.types.l0_instruction_packet import InstructionPacket
from agentic_core.prompt_governance.contracts import (
    CompiledPromptArtifact,
    PromptBOM,
    TemplateManifest,
)


class TestE2ESmoke(unittest.TestCase):
    """End-to-end smoke tests."""

    def test_contracts_can_be_constructed(self) -> None:
        """Smoke test: All core contracts can be constructed."""
        # InstructionPacket
        packet = InstructionPacket(
            trace_id="test-trace",
            path="A",
            intent_class="test",
            required_mixins=(),
        )
        self.assertEqual(packet.path, "A")

        # PromptBOM
        bom = PromptBOM(
            trace_id="test-trace",
            system_version_hash="hash123",
            mixins_required=(),
            raw_u0="Hello",
            raw_c0={},
            template_args={},
            path="B",
        )
        self.assertEqual(bom.path, "B")

        # CompiledPromptArtifact
        artifact = CompiledPromptArtifact(
            trace_id="test-trace",
            final_system_string="System",
            final_user_string="User",
            allowed_tools_schema=(),
            token_estimate=100,
            signature="sig",
        )
        self.assertEqual(artifact.token_estimate, 100)

        # TemplateManifest
        manifest = TemplateManifest(
            template_id="template-1",
            version="1.0.0",
            git_commit_hash="abc123",
            required_variables=("var1",),
        )
        self.assertEqual(manifest.version, "1.0.0")

    def test_slot_taxonomy_constants(self) -> None:
        """Test that slot taxonomy constants exist and are valid."""
        from agentic_core.prompt_governance.contracts.slot_contracts import SLOT_ORDER

        # SLOT_ORDER should be S0, D0, I0, C0, U0
        expected = ("S0", "D0", "I0", "C0", "U0")
        self.assertEqual(SLOT_ORDER, expected)

    def test_path_router_integration(self) -> None:
        """Test PathRouter can be imported and used."""
        from agentic_core.L0_routing.reasoning.path_router import Path, PathRouter

        router = PathRouter()
        self.assertIsNotNone(router)

        # Test path enum
        self.assertEqual(Path.A.value, "A")
        self.assertEqual(Path.B.value, "B")
        self.assertEqual(Path.C.value, "C")
        self.assertEqual(Path.D.value, "D")

    def test_signature_verification_flow(self) -> None:
        """Test the complete signature verification flow."""
        secret_key = b"my-secret-key"

        # Create an artifact
        # Create artifact without signature first
        artifact = CompiledPromptArtifact(
            trace_id="trace-123",
            final_system_string="System prompt",
            final_user_string="User prompt",
            allowed_tools_schema=(),
            token_estimate=50,
            signature="",  # Will compute below
        )

        # Compute signature using the same canonical format as verify_signature
        canonical = str(
            {
                "trace_id": "trace-123",
                "final_system_string": "System prompt",
                "final_user_string": "User prompt",
                "allowed_tools_schema": tuple(sorted([], key=lambda x: str(x))),
                "token_estimate": 50,
            }
        )
        signature = hmac.new(
            secret_key,
            canonical.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        # Create final artifact with signature
        signed_artifact = CompiledPromptArtifact(
            trace_id="trace-123",
            final_system_string="System prompt",
            final_user_string="User prompt",
            allowed_tools_schema=(),
            token_estimate=50,
            signature=signature,
        )

        # Verify
        self.assertTrue(signed_artifact.verify_signature(secret_key))

        # Wrong key should fail
        self.assertFalse(signed_artifact.verify_signature(b"wrong-key"))


class TestIntegrationHealth(unittest.TestCase):
    """Integration health checks."""

    def test_all_modules_importable(self) -> None:
        """Test that all lifecycle modules can be imported."""
        modules = [
            "agentic_core.prompt_governance.contracts.prompt_bom_types",
            "agentic_core.prompt_governance.contracts.compiled_artifact_types",
            "agentic_core.prompt_governance.contracts.template_manifest_types",
            "agentic_core.L0_routing.reasoning.prompt_bom_builder",
            "agentic_core.L0_routing.reasoning.assembly_stage",
            "agentic_core.L4_state.memory.template_registry",
            "agentic_core.L0_routing.utils.elevator_shaft_seam",
        ]

        for module_name in modules:
            try:
                __import__(module_name)
            except ImportError as e:
                self.fail(f"Failed to import {module_name}: {e}")

    def test_governance_emitters_present(self) -> None:
        """Test that governance emitters are present in key modules."""
        # All new modules should have governance wiring
        # This is a smoke test - just verify imports work
        from agentic_core.L0_routing.reasoning.prompt_bom_builder import (
            get_prompt_bom_builder,
        )
        from agentic_core.L4_state.utils.memory.template_registry import get_template_registry

        self.assertIsNotNone(get_prompt_bom_builder)
        self.assertIsNotNone(get_template_registry)


class TestDeterminism(unittest.TestCase):
    """Test determinism guarantees."""

    def test_stable_hash_determinism(self) -> None:
        """Test that stable_hash is deterministic."""
        bom1 = PromptBOM(
            trace_id="trace-123",
            system_version_hash="hash",
            mixins_required=("a", "b"),
            raw_u0="Input",
            raw_c0={"k": "v"},
            template_args={"x": "y"},
            path="A",
        )

        bom2 = PromptBOM(
            trace_id="trace-123",
            system_version_hash="hash",
            mixins_required=("a", "b"),
            raw_u0="Input",
            raw_c0={"k": "v"},
            template_args={"x": "y"},
            path="A",
        )

        # Same inputs → same hash
        self.assertEqual(bom1.stable_hash(), bom2.stable_hash())

    def test_different_inputs_different_hashes(self) -> None:
        """Test that different inputs produce different hashes."""
        bom1 = PromptBOM(
            trace_id="trace-123",
            system_version_hash="hash1",
            mixins_required=(),
            raw_u0="Input",
            raw_c0={},
            template_args={},
            path="A",
        )

        bom2 = PromptBOM(
            trace_id="trace-123",
            system_version_hash="hash2",  # Different
            mixins_required=(),
            raw_u0="Input",
            raw_c0={},
            template_args={},
            path="A",
        )

        # Different inputs → different hashes
        self.assertNotEqual(bom1.stable_hash(), bom2.stable_hash())


if __name__ == "__main__":
    unittest.main()
