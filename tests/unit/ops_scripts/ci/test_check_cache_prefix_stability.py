"""Tests for the EQ-9 cache-prefix stability CI gate.

Plan: ``docs/archive/windsurf/legacy-tree/plans/prompt-assembly-best-practices-gap-b4e1c2.md``
ADR:  ADR-PROMPT-ASSEMBLY-002 §10
"""

from __future__ import annotations

import pytest

from ops_scripts.ci import check_cache_prefix_stability as gate


class TestCachePrefixStabilityGate:
    def test_clean_repo_exits_zero(self) -> None:
        # With no tampering the three invariants hold; gate must pass.
        assert gate.check() == 0

    def test_bypass_env_short_circuits(self, monkeypatch) -> None:
        monkeypatch.setenv(gate._BYPASS_ENV, "1")
        assert gate.check() == 0

    def test_reports_nonzero_when_insertion_order_matters(self, monkeypatch) -> None:
        """Simulate an AuthoritySlot hashing bug by making the canonical
        payload order-sensitive, and verify the gate catches it."""
        from agentic_core.L2_execution.reasoning import compiled_artifact

        # Monkeypatch the property-backing method so manifest_hash now
        # includes dict iteration order.
        original = compiled_artifact.CompiledPromptArtifact.manifest_hash

        def leaky_hash(self) -> str:
            import hashlib

            keys_in_order = list(self.structured_slots.keys()) if self.structured_slots else []
            return hashlib.sha256(("|".join(keys_in_order) + self.final_system_string).encode()).hexdigest()

        monkeypatch.setattr(
            compiled_artifact.CompiledPromptArtifact,
            "manifest_hash",
            property(leaky_hash),
        )
        assert gate.check() == 1

        # Restore automatic via monkeypatch teardown.
        _ = original

    def test_reports_nonzero_when_nonce_leaks_into_hash(self, monkeypatch) -> None:
        """Simulate a nonce leak into manifest_hash and verify the gate catches it."""
        from agentic_core.L2_execution.reasoning import compiled_artifact

        def nonce_leaking_hash(self) -> str:
            import hashlib

            return hashlib.sha256((self.final_system_string + self.idempotency_nonce).encode()).hexdigest()

        monkeypatch.setattr(
            compiled_artifact.CompiledPromptArtifact,
            "manifest_hash",
            property(nonce_leaking_hash),
        )
        assert gate.check() == 1


class TestHelperBuilders:
    def test_make_slots_respects_order(self) -> None:
        slots = gate._make_slots(["U0", "S0"])
        assert list(slots.keys()) == ["U0", "S0"]

    def test_build_artifact_populates_structured_slots(self) -> None:
        art = gate._build_artifact(gate._make_slots(["S0", "U0"]))
        assert set(art.structured_slots.keys()) == {"S0", "U0"}
        assert art.slots_used == ["S0", "U0"]

    def test_build_artifact_accepts_nonce(self) -> None:
        art = gate._build_artifact(gate._make_slots(["S0"]), nonce="z" * 16)
        assert art.idempotency_nonce == "z" * 16
