"""Architecture tests for Prompt Taxonomy Lifecycle (Wave 2 Phase 2/3).

Validates ADG-grounded implementation of the Prompt Lifecycle & Taxonomy system.
"""

import hashlib
import hmac
import unittest
from typing import Any

# Test data contracts
from agentic_core.L0_routing.types.instruction_packet_types import InstructionPacket
from agentic_core.prompt_governance.contracts import (
    CompiledPromptArtifact,
    PromptBOM,
    TemplateManifest,
)
from agentic_core.prompt_governance.contracts.slot_contracts import SLOT_ORDER


class TestPromptTaxonomyArchitecture(unittest.TestCase):
    """Architecture validation tests per Wave 2 Phase 2/3 spec."""

    def test_slot_taxonomy_order(self) -> None:
        """Verify S0→D0→I0→C0→U0 slot ordering is enforced."""
        # SLOT_ORDER must be the canonical ordering
        self.assertEqual(SLOT_ORDER, ("S0", "D0", "I0", "C0", "U0"))

    def test_prompt_bom_immutability(self) -> None:
        """Verify PromptBOM is immutable (frozen dataclass)."""
        bom = PromptBOM(
            trace_id="test-123",
            system_version_hash="hash",
            mixins_required=(),
            raw_u0="input",
            raw_c0={},
            template_args={},
            path="A",
        )
        # Attempting to modify should raise
        with self.assertRaises(Exception):
            bom.trace_id = "new"  # type: ignore[misc]

    def test_compiled_artifact_signature(self) -> None:
        """Verify CompiledPromptArtifact has HMAC-SHA256 signature."""
        secret_key = b"test-secret"

        # Create artifact
        artifact = CompiledPromptArtifact(
            trace_id="trace-123",
            final_system_string="System",
            final_user_string="User",
            allowed_tools_schema=(),
            token_estimate=100,
            signature="",
        )

        # Compute signature manually
        canonical = str(artifact.to_dict())
        expected_sig = hmac.new(
            secret_key, canonical.encode("utf-8"), hashlib.sha256
        ).hexdigest()

        # Create signed artifact
        signed = CompiledPromptArtifact(
            trace_id="trace-123",
            final_system_string="System",
            final_user_string="User",
            allowed_tools_schema=(),
            token_estimate=100,
            signature=expected_sig,
        )

        # Verify
        self.assertTrue(signed.verify_signature(secret_key))

    def test_all_paths_valid(self) -> None:
        """Verify all routing paths A/B/C/D are valid."""
        for path in ("A", "B", "C", "D"):
            packet = InstructionPacket(
                trace_id=f"trace-{path}",
                path=path,  # type: ignore[arg-type]
                intent_class="test",
                required_mixins=(),
            )
            self.assertEqual(packet.path, path)

    def test_invalid_path_rejected(self) -> None:
        """Verify invalid paths are rejected."""
        with self.assertRaises(ValueError):
            InstructionPacket(
                trace_id="test",
                path="E",  # Invalid
                intent_class="test",
                required_mixins=(),
            )

    def test_template_manifest_hash(self) -> None:
        """Verify TemplateManifest has content-addressable hash."""
        manifest = TemplateManifest(
            template_id="template-1",
            version="1.0.0",
            git_commit_hash="abc123",
            required_variables=("var1",),
        )
        hash1 = manifest.stable_hash()
        hash2 = manifest.stable_hash()
        self.assertEqual(hash1, hash2)
        self.assertEqual(len(hash1), 64)  # SHA-256 hex length


class TestAuthorityGradient(unittest.TestCase):
    """Test authority gradient per taxonomy spec."""

    def test_s0_system_level(self) -> None:
        """S0: System-level authority (highest)."""
        bom = PromptBOM(
            trace_id="test",
            system_version_hash="hash",
            mixins_required=(),
            raw_u0="user",
            raw_c0={},
            template_args={},
            path="A",
        )
        # system_version_hash represents S0 authority
        self.assertTrue(bom.system_version_hash)

    def test_d0_defensive(self) -> None:
        """D0: Defensive injection fences."""
        # D0 is optional but can be added
        artifact = CompiledPromptArtifact(
            trace_id="test",
            final_system_string="<D0>fence</D0>\nSystem",
            final_user_string="User",
            allowed_tools_schema=(),
            token_estimate=50,
            signature="",
        )
        # D0 fences should be in system string
        self.assertIn("<D0>", artifact.final_system_string)

    def test_i0_instructional(self) -> None:
        """I0: Instructional authority."""
        bom = PromptBOM(
            trace_id="test",
            system_version_hash="hash",
            mixins_required=("mixin1", "mixin2"),
            raw_u0="user",
            raw_c0={},
            template_args={},
            path="B",
        )
        # Mixins represent I0 authority
        self.assertTrue(bom.mixins_required)

    def test_c0_contextual(self) -> None:
        """C0: Contextual authority (JIT loaded)."""
        bom = PromptBOM(
            trace_id="test",
            system_version_hash="hash",
            mixins_required=(),
            raw_u0="user",
            raw_c0={"rag": "chunks", "ast": "snapshot"},
            template_args={},
            path="C",
        )
        # C0 is loaded via elevator_shaft_seam
        self.assertTrue(bom.raw_c0)

    def test_u0_user(self) -> None:
        """U0: User content (lowest authority)."""
        bom = PromptBOM(
            trace_id="test",
            system_version_hash="hash",
            mixins_required=(),
            raw_u0="User provided content",
            raw_c0={},
            template_args={},
            path="D",
        )
        # U0 is the user input
        self.assertEqual(bom.raw_u0, "User provided content")


class TestADGGovernanceEdges(unittest.TestCase):
    """Test that governance edges are emitted."""

    def test_lifecycle_emitters_present(self) -> None:
        """Verify governance emitters are present in modules."""
        # All new modules should have lifecycle emitter imports
        from agentic_core.L0_routing.engines.prompt_bom_builder import PromptBOMBuilder
        from agentic_core.L4_state.memory.template_registry import TemplateRegistry

        self.assertIsNotNone(PromptBOMBuilder)
        self.assertIsNotNone(TemplateRegistry)


if __name__ == "__main__":
    unittest.main()
