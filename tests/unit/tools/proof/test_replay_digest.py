"""Tests for the replay invariant digest (W3.1)."""

from __future__ import annotations

from tools.proof.replay_digest import (
    ReplayInvariant,
    compute_digest,
    digests_match,
)


def _basic(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "route_id": "lic.standard",
        "gate_decisions": [("gate_a", "pass"), ("gate_b", "pass")],
        "evidence_packet_ids": ["EV-1", "EV-2"],
        "final_disposition": "X3.PASS",
    }
    base.update(overrides)
    return base


class TestDeterminism:
    def test_same_inputs_same_digest(self) -> None:
        d1 = compute_digest(**_basic())
        d2 = compute_digest(**_basic())
        assert d1 == d2

    def test_gate_decision_order_does_not_matter(self) -> None:
        d1 = compute_digest(**_basic())
        d2 = compute_digest(**_basic(gate_decisions=[("gate_b", "pass"), ("gate_a", "pass")]))
        assert d1 == d2, "gate_decisions must be order-invariant"

    def test_evidence_packet_order_does_not_matter(self) -> None:
        d1 = compute_digest(**_basic())
        d2 = compute_digest(**_basic(evidence_packet_ids=["EV-2", "EV-1"]))
        assert d1 == d2

    def test_evidence_packet_dedup(self) -> None:
        d1 = compute_digest(**_basic())
        d2 = compute_digest(**_basic(evidence_packet_ids=["EV-1", "EV-1", "EV-2"]))
        assert d1 == d2

    def test_dict_form_of_gate_decisions(self) -> None:
        d_pairs = compute_digest(**_basic())
        d_dict = compute_digest(**_basic(gate_decisions={"gate_a": "pass", "gate_b": "pass"}))
        assert d_pairs == d_dict


class TestSensitivity:
    def test_route_id_change_changes_digest(self) -> None:
        d1 = compute_digest(**_basic())
        d2 = compute_digest(**_basic(route_id="lic.fast"))
        assert d1 != d2

    def test_gate_verdict_change_changes_digest(self) -> None:
        d1 = compute_digest(**_basic())
        d2 = compute_digest(**_basic(gate_decisions=[("gate_a", "fail"), ("gate_b", "pass")]))
        assert d1 != d2

    def test_evidence_packet_change_changes_digest(self) -> None:
        d1 = compute_digest(**_basic())
        d2 = compute_digest(**_basic(evidence_packet_ids=["EV-1", "EV-3"]))
        assert d1 != d2

    def test_disposition_change_changes_digest(self) -> None:
        d1 = compute_digest(**_basic())
        d2 = compute_digest(**_basic(final_disposition="X4.FAIL"))
        assert d1 != d2

    def test_extra_field_affects_digest(self) -> None:
        d1 = compute_digest(**_basic())
        d2 = compute_digest(**_basic(extra={"k": "v"}))
        assert d1 != d2


class TestUnicodeNormalization:
    def test_nfc_drift_does_not_change_digest(self) -> None:
        # 'é' as single codepoint U+00E9 vs 'e' + combining U+0301
        precomposed = "\u00e9"
        decomposed = "e\u0301"
        d1 = compute_digest(**_basic(route_id=f"route.{precomposed}"))
        d2 = compute_digest(**_basic(route_id=f"route.{decomposed}"))
        assert d1 == d2


class TestReplayInvariantClass:
    def test_canonical_dict_shape(self) -> None:
        inv = ReplayInvariant(
            route_id="r",
            gate_decisions=(("a", "pass"),),
            evidence_packet_ids=("EV-1",),
            final_disposition="ok",
        )
        d = inv.canonical_dict()
        assert d["route_id"] == "r"
        assert d["gate_decisions"] == [["a", "pass"]]
        assert d["evidence_packet_ids"] == ["EV-1"]
        assert d["final_disposition"] == "ok"
        assert d["extra"] == {}

    def test_digest_is_64_hex_chars(self) -> None:
        inv = ReplayInvariant(
            route_id="r",
            gate_decisions=(("a", "pass"),),
            evidence_packet_ids=("EV-1",),
            final_disposition="ok",
        )
        digest = inv.digest()
        assert len(digest) == 64
        assert all(c in "0123456789abcdef" for c in digest)


class TestDigestsMatch:
    def test_match(self) -> None:
        assert digests_match("a" * 64, "a" * 64) is True

    def test_no_match_different_length(self) -> None:
        assert digests_match("a" * 64, "a" * 63) is False

    def test_no_match_different_content(self) -> None:
        assert digests_match("a" * 64, "b" * 64) is False
