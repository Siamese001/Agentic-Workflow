"""W6 tests for synthesis bridge."""

from __future__ import annotations

import pytest

from agentic_core.L2_execution.enforcement.synthesis_bridge import (
    DEFAULT_MAX_BYTES,
    SynthesisBridgeError,
    SynthesisProvenance,
    wrap_synthesis_output,
)
from agentic_core.L2_execution.reasoning.compiled_artifact import AuthorityLevel
from agentic_core.L2_execution.reasoning.slot_assembly_engine import SlotAssemblyEngine


def _prov() -> SynthesisProvenance:
    return SynthesisProvenance(
        producer="apps_research.synthesis_engine_service",
        source_trace_ids=("trace-1", "trace-2"),
        model="claude-3-5-sonnet",
        synthesis_kind="knowledge",
    )


class TestWrapBasicBehavior:
    def test_wraps_to_c0_info_slot(self) -> None:
        slot = wrap_synthesis_output(text="Some grounded summary.", provenance=_prov())
        assert slot.slot_type == "C0"
        assert slot.authority_level is AuthorityLevel.INFO
        assert slot.source_layer == "L3"
        assert slot.content == "Some grounded summary."

    def test_provenance_attached(self) -> None:
        slot = wrap_synthesis_output(text="x", provenance=_prov())
        assert slot.metadata["synthesis_producer"] == (
            "apps_research.synthesis_engine_service"
        )
        assert slot.metadata["synthesis_source_trace_ids"] == ["trace-1", "trace-2"]
        assert slot.metadata["synthesis_model"] == "claude-3-5-sonnet"
        assert slot.metadata["synthesis_kind"] == "knowledge"
        assert slot.metadata["synthesis_truncated"] is False

    def test_custom_source_layer(self) -> None:
        slot = wrap_synthesis_output(
            text="x", provenance=_prov(), source_layer="L1"
        )
        assert slot.source_layer == "L1"


class TestValidation:
    @pytest.mark.parametrize("bad", ["", "   ", "\n\t\n"])
    def test_empty_text_rejected(self, bad: str) -> None:
        with pytest.raises(SynthesisBridgeError, match="empty"):
            wrap_synthesis_output(text=bad, provenance=_prov())

    def test_empty_producer_rejected(self) -> None:
        bad_prov = SynthesisProvenance(producer="")
        with pytest.raises(SynthesisBridgeError, match="producer"):
            wrap_synthesis_output(text="x", provenance=bad_prov)

    def test_nonpositive_max_bytes_rejected(self) -> None:
        with pytest.raises(SynthesisBridgeError, match="max_bytes"):
            wrap_synthesis_output(text="x", provenance=_prov(), max_bytes=0)

    def test_invalid_source_layer_rejected(self) -> None:
        with pytest.raises(SynthesisBridgeError, match="L0..L6"):
            wrap_synthesis_output(text="x", provenance=_prov(), source_layer="L99")


class TestTruncation:
    def test_truncation_applied_when_over_budget(self) -> None:
        huge = "a" * (DEFAULT_MAX_BYTES + 5000)
        slot = wrap_synthesis_output(text=huge, provenance=_prov())
        assert "TRUNCATED" in slot.content
        assert len(slot.content.encode("utf-8")) <= DEFAULT_MAX_BYTES
        assert slot.metadata["synthesis_truncated"] is True
        assert slot.metadata["synthesis_original_bytes"] == len(huge.encode("utf-8"))

    def test_no_truncation_when_under_budget(self) -> None:
        slot = wrap_synthesis_output(
            text="short", provenance=_prov(), max_bytes=10_000
        )
        assert "TRUNCATED" not in slot.content
        assert slot.metadata["synthesis_truncated"] is False

    def test_custom_budget(self) -> None:
        slot = wrap_synthesis_output(
            text="a" * 200, provenance=_prov(), max_bytes=50
        )
        assert len(slot.content.encode("utf-8")) <= 50
        assert slot.metadata["synthesis_truncated"] is True


class TestAssemblyIntegration:
    """Regression: the wrapped slot must be accepted by SlotAssemblyEngine."""

    def test_slot_integrates_into_assembler(self) -> None:
        synthesis_slot = wrap_synthesis_output(
            text="Grounded summary of prior retrieval.", provenance=_prov()
        )

        from agentic_core.L2_execution.reasoning.compiled_artifact import (
            AuthoritySlot as _AS,
        )

        engine = SlotAssemblyEngine(secret_key=b"x" * 32)
        engine.add_slot(
            _AS(
                slot_type="S0",
                content="you are helpful",
                authority_level=AuthorityLevel.ABSOLUTE,
                source_layer="L0",
            )
        )
        engine.add_slot(synthesis_slot)
        engine.add_slot(
            _AS(
                slot_type="U0",
                content="Use this context.",
                authority_level=AuthorityLevel.ZERO,
                source_layer="L0",
            )
        )
        artifact = engine.assemble()
        assert "Grounded summary" in artifact.final_user_string
        assert "C0" in artifact.slots_used
