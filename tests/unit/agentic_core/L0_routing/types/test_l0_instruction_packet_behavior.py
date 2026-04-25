"""Behavioral tests for ``agentic_core.L0_routing.types.l0_instruction_packet``.

Covers the InstructionPacket data contract (L0 Router → PromptBOM Builder handoff):
- Required field validation (trace_id, intent_class non-empty).
- path Literal validation (A/B/C/D only).
- escalation_threshold bounds [0.0, 1.0].
- Default escalation_threshold = 0.85.
- to_dict sorts required_mixins tuple and preserves fields.
- stable_hash is deterministic for identical packets.
- stable_hash differs for different payloads.
- Frozen dataclass — mutation rejected.
"""

from __future__ import annotations

import hashlib

import pytest

from agentic_core.L0_routing.types.l0_instruction_packet import InstructionPacket


def _ip(**overrides: object) -> InstructionPacket:
    kwargs: dict[str, object] = {
        "trace_id": "t1",
        "path": "A",
        "intent_class": "retrieval",
        "required_mixins": ("m2", "m1"),
    }
    kwargs.update(overrides)
    return InstructionPacket(**kwargs)  # type: ignore[arg-type]


class TestValidation:
    def test_valid(self) -> None:
        p = _ip()
        assert p.trace_id == "t1"
        assert p.escalation_threshold == 0.85  # default

    def test_empty_trace_id_rejected(self) -> None:
        with pytest.raises(ValueError, match="trace_id"):
            _ip(trace_id="")

    def test_empty_intent_class_rejected(self) -> None:
        with pytest.raises(ValueError, match="intent_class"):
            _ip(intent_class="")

    @pytest.mark.parametrize("path", ["X", "a", "AA", "", "E"])
    def test_invalid_path_rejected(self, path: str) -> None:
        with pytest.raises(ValueError, match="path must be A/B/C/D"):
            _ip(path=path)  # type: ignore[arg-type]

    @pytest.mark.parametrize("path", ["A", "B", "C", "D"])
    def test_valid_paths_accepted(self, path: str) -> None:
        assert _ip(path=path).path == path  # type: ignore[arg-type]

    @pytest.mark.parametrize("th", [-0.01, 1.01, 2.0, -1.0])
    def test_threshold_out_of_range(self, th: float) -> None:
        with pytest.raises(ValueError, match="escalation_threshold"):
            _ip(escalation_threshold=th)

    @pytest.mark.parametrize("th", [0.0, 0.5, 1.0])
    def test_threshold_boundaries_accepted(self, th: float) -> None:
        assert _ip(escalation_threshold=th).escalation_threshold == th


class TestFrozen:
    def test_cannot_mutate(self) -> None:
        p = _ip()
        with pytest.raises(AttributeError):
            p.trace_id = "other"  # type: ignore[misc]


class TestToDict:
    def test_shape(self) -> None:
        p = _ip()
        d = p.to_dict()
        assert set(d.keys()) == {
            "trace_id",
            "path",
            "intent_class",
            "required_mixins",
            "escalation_threshold",
        }

    def test_mixins_sorted(self) -> None:
        p = _ip(required_mixins=("m3", "m1", "m2"))
        assert p.to_dict()["required_mixins"] == ("m1", "m2", "m3")

    def test_mixins_as_tuple(self) -> None:
        p = _ip()
        assert isinstance(p.to_dict()["required_mixins"], tuple)


class TestStableHash:
    def test_is_sha256_hex(self) -> None:
        h = _ip().stable_hash()
        assert len(h) == 64
        int(h, 16)  # parses as hex

    def test_deterministic(self) -> None:
        assert _ip().stable_hash() == _ip().stable_hash()

    def test_different_for_different_trace(self) -> None:
        assert _ip(trace_id="a").stable_hash() != _ip(trace_id="b").stable_hash()

    def test_different_for_different_path(self) -> None:
        assert _ip(path="A").stable_hash() != _ip(path="B").stable_hash()

    def test_different_for_different_threshold(self) -> None:
        h1 = _ip(escalation_threshold=0.5).stable_hash()
        h2 = _ip(escalation_threshold=0.7).stable_hash()
        assert h1 != h2

    def test_mixin_order_invariant(self) -> None:
        """Because to_dict sorts mixins, hashes should match regardless of input order."""
        h1 = _ip(required_mixins=("m1", "m2", "m3")).stable_hash()
        h2 = _ip(required_mixins=("m3", "m1", "m2")).stable_hash()
        assert h1 == h2

    def test_matches_manual_sha256(self) -> None:
        p = _ip()
        expected = hashlib.sha256(str(p.to_dict()).encode("utf-8")).hexdigest()
        assert p.stable_hash() == expected
