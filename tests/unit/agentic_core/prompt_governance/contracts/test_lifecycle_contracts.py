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

import pytest

# ---------------------------------------------------------------------------
# Lazy import fixtures - avoid collection-time import errors
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def plc_imports():
    from agentic_core.L0_routing.types.l0_instruction_packet import InstructionPacket
    from agentic_core.prompt_governance.contracts import (
        CompiledPromptArtifact,
        PromptBOM,
        TemplateManifest,
    )
    return {
        "CompiledPromptArtifact": CompiledPromptArtifact,
        "PromptBOM": PromptBOM,
        "TemplateManifest": TemplateManifest,
        "InstructionPacket": InstructionPacket,
    }


@pytest.fixture(scope="session")
def plc_direct_imports():
    from agentic_core.prompt_governance.contracts.compiled_artifact_types import (
        CompiledPromptArtifact as CompiledPromptArtifactDirect,
    )
    from agentic_core.prompt_governance.contracts.prompt_bom_types import (
        PromptBOM as PromptBOMDirect,
    )
    from agentic_core.prompt_governance.contracts.template_manifest_types import (
        TemplateManifest as TemplateManifestDirect,
    )
    return {
        "CompiledPromptArtifactDirect": CompiledPromptArtifactDirect,
        "PromptBOMDirect": PromptBOMDirect,
        "TemplateManifestDirect": TemplateManifestDirect,
    }


# =============================================================================
# PromptBOM Tests
# =============================================================================

class TestPromptBOM:
    """Test PromptBOM data contract."""

    def test_creation_valid(self, plc_imports) -> None:
        """Test creating a valid PromptBOM."""
        PromptBOM = plc_imports["PromptBOM"]
        bom = PromptBOM(
            trace_id="trace-123",
            system_version_hash="sha256-hash",
            mixins_required=("mixin1", "mixin2"),
            raw_u0="User input",
            raw_c0={"key": "value"},
            template_args={"var": "value"},
            path="A",
        )
        assert bom.trace_id == "trace-123"
        assert bom.path == "A"

    def test_creation_invalid_path(self, plc_imports) -> None:
        """Test that invalid path raises ValueError."""
        PromptBOM = plc_imports["PromptBOM"]
        with pytest.raises(ValueError):
            PromptBOM(
                trace_id="trace-123",
                system_version_hash="sha256-hash",
                mixins_required=(),
                raw_u0="User input",
                raw_c0={},
                template_args={},
                path="E",
            )

    def test_empty_trace_id_raises(self, plc_imports) -> None:
        """Test that empty trace_id raises ValueError."""
        PromptBOM = plc_imports["PromptBOM"]
        with pytest.raises(ValueError):
            PromptBOM(
                trace_id="",
                system_version_hash="sha256-hash",
                mixins_required=(),
                raw_u0="User input",
                raw_c0={},
                template_args={},
                path="A",
            )

    def test_empty_system_hash_raises(self, plc_imports) -> None:
        """Test that empty system_version_hash raises ValueError."""
        PromptBOM = plc_imports["PromptBOM"]
        with pytest.raises(ValueError):
            PromptBOM(
                trace_id="trace-123",
                system_version_hash="",
                mixins_required=(),
                raw_u0="User input",
                raw_c0={},
                template_args={},
                path="A",
            )

    def test_to_dict(self, plc_imports) -> None:
        """Test conversion to dictionary."""
        PromptBOM = plc_imports["PromptBOM"]
        bom = PromptBOM(
            trace_id="trace-123",
            system_version_hash="sha256-hash",
            mixins_required=("mixin2", "mixin1"),
            raw_u0="User input",
            raw_c0={"key": "value"},
            template_args={"var": "value"},
            path="B",
        )
        d = bom.to_dict()
        assert d["trace_id"] == "trace-123"
        assert d["path"] == "B"
        assert d["mixins_required"] == ("mixin1", "mixin2")

    def test_stable_hash(self, plc_imports) -> None:
        """Test stable hash computation."""
        PromptBOM = plc_imports["PromptBOM"]
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
        assert bom1.stable_hash() == bom2.stable_hash()

    def test_to_dict_includes_exemplars_required(self, plc_imports) -> None:
        """Test to_dict includes exemplars_required field."""
        PromptBOM = plc_imports["PromptBOM"]
        bom = PromptBOM(
            trace_id="trace-123",
            system_version_hash="sha256-hash",
            mixins_required=("mixin1",),
            raw_u0="User input",
            raw_c0={"key": "value"},
            template_args={"var": "value"},
            path="B",
            exemplars_required=("ex1", "ex2"),
        )
        d = bom.to_dict()
        assert d["exemplars_required"] == ("ex1", "ex2")

    def test_exemplars_required_sorted_in_to_dict(self, plc_imports) -> None:
        """Test exemplars_required is sorted in to_dict output."""
        PromptBOM = plc_imports["PromptBOM"]
        bom = PromptBOM(
            trace_id="trace-123",
            system_version_hash="sha256-hash",
            mixins_required=(),
            raw_u0="input",
            raw_c0={},
            template_args={},
            path="A",
            exemplars_required=("z_exemplar", "a_exemplar", "m_exemplar"),
        )
        d = bom.to_dict()
        assert d["exemplars_required"] == ("a_exemplar", "m_exemplar", "z_exemplar")

class TestCompiledPromptArtifact:
    """Test CompiledPromptArtifact data contract."""

    def test_creation_valid(self, plc_imports) -> None:
        """Test creating a valid CompiledPromptArtifact."""
        CompiledPromptArtifact = plc_imports["CompiledPromptArtifact"]
        artifact = CompiledPromptArtifact(
            trace_id="trace-123",
            final_system_string="System prompt",
            final_user_string="User prompt",
            allowed_tools_schema=(),
            token_estimate=100,
            signature="hmac-signature",
        )
        assert artifact.trace_id == "trace-123"
        assert artifact.token_estimate == 100

    def test_empty_trace_id_raises(self, plc_imports) -> None:
        """Test that empty trace_id raises ValueError."""
        CompiledPromptArtifact = plc_imports["CompiledPromptArtifact"]
        with pytest.raises(ValueError):
            CompiledPromptArtifact(
                trace_id="",
                final_system_string="System",
                final_user_string="User",
                allowed_tools_schema=(),
                token_estimate=100,
                signature="sig",
            )

    def test_negative_token_estimate_raises(self, plc_imports) -> None:
        """Test that negative token_estimate raises ValueError."""
        CompiledPromptArtifact = plc_imports["CompiledPromptArtifact"]
        with pytest.raises(ValueError):
            CompiledPromptArtifact(
                trace_id="trace-123",
                final_system_string="System",
                final_user_string="User",
                allowed_tools_schema=(),
                token_estimate=-1,
                signature="sig",
            )

    def test_verify_signature_valid(self, plc_imports) -> None:
        """Test signature verification with valid key."""
        CompiledPromptArtifact = plc_imports["CompiledPromptArtifact"]
        secret_key = b"test-secret-key"
        canonical = str({
            "trace_id": "trace-123",
            "final_system_string": "System",
            "final_user_string": "User",
            "allowed_tools_schema": (),
            "token_estimate": 100,
        })
        signature = hmac.new(
            secret_key, canonical.encode("utf-8"), hashlib.sha256,
        ).hexdigest()
        artifact = CompiledPromptArtifact(
            trace_id="trace-123",
            final_system_string="System",
            final_user_string="User",
            allowed_tools_schema=(),
            token_estimate=100,
            signature=signature,
        )
        assert artifact.verify_signature(secret_key)

    def test_verify_signature_invalid(self, plc_imports) -> None:
        """Test signature verification with invalid key."""
        CompiledPromptArtifact = plc_imports["CompiledPromptArtifact"]
        artifact = CompiledPromptArtifact(
            trace_id="trace-123",
            final_system_string="System",
            final_user_string="User",
            allowed_tools_schema=(),
            token_estimate=100,
            signature="wrong-signature",
        )
        assert not artifact.verify_signature(b"different-key")

    def test_to_dict(self, plc_imports) -> None:
        """Test conversion to dictionary."""
        CompiledPromptArtifact = plc_imports["CompiledPromptArtifact"]
        artifact = CompiledPromptArtifact(
            trace_id="trace-123",
            final_system_string="System",
            final_user_string="User",
            allowed_tools_schema=(),
            token_estimate=100,
            signature="sig",
        )
        d = artifact.to_dict()
        assert d["trace_id"] == "trace-123"
        assert d["token_estimate"] == 100


# =============================================================================
# TemplateManifest Tests
# =============================================================================

class TestTemplateManifest:
    """Test TemplateManifest data contract."""

    def test_creation_valid(self, plc_imports) -> None:
        """Test creating a valid TemplateManifest."""
        TemplateManifest = plc_imports["TemplateManifest"]
        manifest = TemplateManifest(
            template_id="template-123",
            version="1.0.0",
            git_commit_hash="abc123",
            required_variables=("var1", "var2"),
            schema_version="1.0",
        )
        assert manifest.template_id == "template-123"
        assert manifest.schema_version == "1.0"

    def test_empty_template_id_raises(self, plc_imports) -> None:
        """Test that empty template_id raises ValueError."""
        TemplateManifest = plc_imports["TemplateManifest"]
        with pytest.raises(ValueError):
            TemplateManifest(
                template_id="",
                version="1.0.0",
                git_commit_hash="abc123",
                required_variables=(),
            )

    def test_empty_version_raises(self, plc_imports) -> None:
        """Test that empty version raises ValueError."""
        TemplateManifest = plc_imports["TemplateManifest"]
        with pytest.raises(ValueError):
            TemplateManifest(
                template_id="template-123",
                version="",
                git_commit_hash="abc123",
                required_variables=(),
            )

    def test_empty_git_commit_raises(self, plc_imports) -> None:
        """Test that empty git_commit_hash raises ValueError."""
        TemplateManifest = plc_imports["TemplateManifest"]
        with pytest.raises(ValueError):
            TemplateManifest(
                template_id="template-123",
                version="1.0.0",
                git_commit_hash="",
                required_variables=(),
            )

    def test_default_schema_version(self, plc_imports) -> None:
        """Test default schema_version."""
        TemplateManifest = plc_imports["TemplateManifest"]
        manifest = TemplateManifest(
            template_id="template-123",
            version="1.0.0",
            git_commit_hash="abc123",
            required_variables=(),
        )
        assert manifest.schema_version == "1.0"

    def test_to_dict(self, plc_imports) -> None:
        """Test conversion to dictionary."""
        TemplateManifest = plc_imports["TemplateManifest"]
        manifest = TemplateManifest(
            template_id="template-123",
            version="1.0.0",
            git_commit_hash="abc123",
            required_variables=("var2", "var1"),
        )
        d = manifest.to_dict()
        assert d["required_variables"] == ("var1", "var2")

    def test_stable_hash(self, plc_imports) -> None:
        """Test stable hash computation."""
        TemplateManifest = plc_imports["TemplateManifest"]
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
        assert manifest1.stable_hash() == manifest2.stable_hash()


# =============================================================================
# InstructionPacket Tests
# =============================================================================

class TestInstructionPacket:
    """Test InstructionPacket data contract."""

    def test_creation_valid(self, plc_imports) -> None:
        """Test creating a valid InstructionPacket."""
        InstructionPacket = plc_imports["InstructionPacket"]
        packet = InstructionPacket(
            trace_id="trace-123",
            path="A",
            intent_class="classification",
            required_mixins=("mixin1",),
            escalation_threshold=0.9,
        )
        assert packet.trace_id == "trace-123"
        assert packet.path == "A"
        assert packet.escalation_threshold == 0.9

    def test_invalid_path_raises(self, plc_imports) -> None:
        """Test that invalid path raises ValueError."""
        InstructionPacket = plc_imports["InstructionPacket"]
        with pytest.raises(ValueError):
            InstructionPacket(
                trace_id="trace-123",
                path="E",
                intent_class="classification",
                required_mixins=(),
            )

    def test_empty_trace_id_raises(self, plc_imports) -> None:
        """Test that empty trace_id raises ValueError."""
        InstructionPacket = plc_imports["InstructionPacket"]
        with pytest.raises(ValueError):
            InstructionPacket(
                trace_id="",
                path="A",
                intent_class="classification",
                required_mixins=(),
            )

    def test_empty_intent_class_raises(self, plc_imports) -> None:
        """Test that empty intent_class raises ValueError."""
        InstructionPacket = plc_imports["InstructionPacket"]
        with pytest.raises(ValueError):
            InstructionPacket(
                trace_id="trace-123",
                path="A",
                intent_class="",
                required_mixins=(),
            )

    def test_escalation_threshold_bounds(self, plc_imports) -> None:
        """Test escalation threshold bounds."""
        InstructionPacket = plc_imports["InstructionPacket"]
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
        with pytest.raises(ValueError):
            InstructionPacket(
                trace_id="trace-123",
                path="A",
                intent_class="classification",
                required_mixins=(),
                escalation_threshold=-0.1,
            )
        with pytest.raises(ValueError):
            InstructionPacket(
                trace_id="trace-123",
                path="A",
                intent_class="classification",
                required_mixins=(),
                escalation_threshold=1.1,
            )

    def test_default_escalation_threshold(self, plc_imports) -> None:
        """Test default escalation threshold."""
        InstructionPacket = plc_imports["InstructionPacket"]
        packet = InstructionPacket(
            trace_id="trace-123",
            path="A",
            intent_class="classification",
            required_mixins=(),
        )
        assert packet.escalation_threshold == 0.85

    def test_all_paths_valid(self, plc_imports) -> None:
        """Test that all valid paths work."""
        InstructionPacket = plc_imports["InstructionPacket"]
        for path in ("A", "B", "C", "D"):
            packet = InstructionPacket(
                trace_id=f"trace-{path}",
                path=path,
                intent_class="classification",
                required_mixins=(),
            )
            assert packet.path == path


# =============================================================================
# Contract Export Tests
# =============================================================================

class TestContractExports:
    """Test that all contracts are properly exported."""

    def test_prompt_bom_exported(self, plc_direct_imports) -> None:
        """Test PromptBOM is exported from contracts module."""
        from agentic_core.prompt_governance.contracts import PromptBOM as ExportedBOM
        assert ExportedBOM is plc_direct_imports["PromptBOMDirect"]

    def test_compiled_artifact_exported(self, plc_direct_imports) -> None:
        """Test CompiledPromptArtifact is exported from contracts module."""
        from agentic_core.prompt_governance.contracts import (
            CompiledPromptArtifact as ExportedArtifact,
        )
        assert ExportedArtifact is plc_direct_imports["CompiledPromptArtifactDirect"]

    def test_template_manifest_exported(self, plc_direct_imports) -> None:
        """Test TemplateManifest is exported from contracts module."""
        from agentic_core.prompt_governance.contracts import (
            TemplateManifest as ExportedManifest,
        )
        assert ExportedManifest is plc_direct_imports["TemplateManifestDirect"]


if __name__ == "__main__":
    unittest.main()
