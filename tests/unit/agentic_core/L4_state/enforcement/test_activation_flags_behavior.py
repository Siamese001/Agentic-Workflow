"""Behavioral tests for L4_state/enforcement/activation_flags.py.

Covers L4-persisted signed activation flags, the activation gate, and the
module-level exported facade. All store operations use ``tmp_path`` so the
real project .activation directory is never touched.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agentic_core.L4_state.enforcement.activation_flags import (
    ActivationFlags,
    ActivationFlagsStore,
    ActivationGate,
    ActivationProof,
)


@pytest.fixture
def store(tmp_path: Path) -> ActivationFlagsStore:
    return ActivationFlagsStore(storage_path=tmp_path / ".activation")


# ---- Dataclass defaults ---------------------------------------------


class TestActivationFlagsDefaults:
    def test_defaults_all_false(self) -> None:
        f = ActivationFlags()
        assert f.execution_hardened is False
        assert f.mutation_surface_zero is False
        assert f.guardian_coverage == 0.0
        assert f.meta_learning_enabled is False
        assert f.replay_digest_hash == ""
        assert f.signature == ""
        assert f.activation_timestamp == 0.0

    def test_frozen(self) -> None:
        f = ActivationFlags()
        with pytest.raises((AttributeError, Exception)):
            f.meta_learning_enabled = True  # type: ignore[misc]


class TestActivationProofDefaults:
    def test_frozen(self) -> None:
        p = ActivationProof(flags_hash="h", guardian_signature="s", timestamp=0.0, previous_flags_hash="")
        with pytest.raises((AttributeError, Exception)):
            p.flags_hash = "tampered"  # type: ignore[misc]


# ---- ActivationFlagsStore construction ------------------------------


class TestActivationFlagsStoreConstruction:
    def test_fresh_store_has_default_flags(self, store: ActivationFlagsStore) -> None:
        flags = store.get_current_flags()
        assert flags is not None
        assert flags.execution_hardened is False

    def test_fresh_store_has_no_proof(self, store: ActivationFlagsStore) -> None:
        assert store.get_activation_proof() is None


# ---- update_flags ---------------------------------------------------


class TestUpdateFlags:
    def test_requires_signature(self, store: ActivationFlagsStore) -> None:
        with pytest.raises(RuntimeError, match="signature required"):
            store.update_flags(ActivationFlags(), guardian_signature="")

    def test_meta_learning_requires_replay_digest(
        self,
        store: ActivationFlagsStore,
    ) -> None:
        flags = ActivationFlags(meta_learning_enabled=True, replay_digest_hash="")
        with pytest.raises(RuntimeError, match="Replay digest required"):
            store.update_flags(flags, guardian_signature="sig")

    def test_successful_update_returns_proof(
        self,
        store: ActivationFlagsStore,
    ) -> None:
        proof = store.update_flags(ActivationFlags(), guardian_signature="sig")
        assert isinstance(proof, ActivationProof)
        assert proof.guardian_signature == "sig"
        assert proof.flags_hash
        assert proof.previous_flags_hash == ""

    def test_chained_update_records_previous_hash(
        self,
        store: ActivationFlagsStore,
    ) -> None:
        first = store.update_flags(ActivationFlags(), guardian_signature="sig1")
        second = store.update_flags(
            ActivationFlags(execution_hardened=True),
            guardian_signature="sig2",
        )
        assert second.previous_flags_hash == first.flags_hash

    def test_update_persists_to_disk(
        self,
        store: ActivationFlagsStore,
        tmp_path: Path,
    ) -> None:
        store.update_flags(ActivationFlags(), guardian_signature="sig")
        assert (tmp_path / ".activation" / "activation_flags.json").exists()
        assert (tmp_path / ".activation" / "activation_proof.json").exists()

    def test_update_sets_current_flags(
        self,
        store: ActivationFlagsStore,
    ) -> None:
        store.update_flags(
            ActivationFlags(execution_hardened=True),
            guardian_signature="sig",
        )
        current = store.get_current_flags()
        assert current is not None
        assert current.execution_hardened is True
        assert current.signature == "sig"


# ---- verify_activation_chain ----------------------------------------


class TestVerifyActivationChain:
    def test_no_proof_is_trivially_valid(
        self,
        store: ActivationFlagsStore,
    ) -> None:
        assert store.verify_activation_chain() is True

    def test_after_update_chain_valid(self, store: ActivationFlagsStore) -> None:
        store.update_flags(ActivationFlags(), guardian_signature="sig")
        assert store.verify_activation_chain() is True

    def test_tampered_flags_detected(
        self,
        store: ActivationFlagsStore,
        tmp_path: Path,
    ) -> None:
        store.update_flags(
            ActivationFlags(execution_hardened=True),
            guardian_signature="sig",
        )
        # Tamper with the on-disk flags — simulate attacker modification
        flags_file = tmp_path / ".activation" / "activation_flags.json"
        data = json.loads(flags_file.read_text())
        data["execution_hardened"] = False  # mutate
        flags_file.write_text(json.dumps(data))
        # Reload into a fresh store — hash will no longer match proof
        fresh = ActivationFlagsStore(storage_path=tmp_path / ".activation")
        assert fresh.verify_activation_chain() is False


# ---- verify_replay_binding ------------------------------------------


class TestVerifyReplayBinding:
    def test_match(self, store: ActivationFlagsStore) -> None:
        store.update_flags(
            ActivationFlags(replay_digest_hash="abc123"),
            guardian_signature="sig",
        )
        assert store.verify_replay_binding("abc123") is True

    def test_mismatch(self, store: ActivationFlagsStore) -> None:
        store.update_flags(
            ActivationFlags(replay_digest_hash="abc"),
            guardian_signature="sig",
        )
        assert store.verify_replay_binding("wrong") is False

    def test_no_flags_returns_false(self, tmp_path: Path) -> None:
        s = ActivationFlagsStore(storage_path=tmp_path / ".activation")
        # fresh store has default flags (empty digest) — any non-empty expected
        # value should mismatch
        assert s.verify_replay_binding("expected") is False


# ---- reset_to_defaults ----------------------------------------------


class TestResetToDefaults:
    def test_resets_flags_and_proof(self, store: ActivationFlagsStore) -> None:
        store.update_flags(
            ActivationFlags(execution_hardened=True),
            guardian_signature="sig",
        )
        store.reset_to_defaults()
        flags = store.get_current_flags()
        assert flags is not None
        assert flags.execution_hardened is False
        assert store.get_activation_proof() is None


# ---- Corrupt payload on load ----------------------------------------


class TestCorruptPayloadFailClosed:
    def test_corrupt_flags_file_resets_to_default(self, tmp_path: Path) -> None:
        act = tmp_path / ".activation"
        act.mkdir()
        (act / "activation_flags.json").write_text("{not json")
        store = ActivationFlagsStore(storage_path=act)
        flags = store.get_current_flags()
        assert flags is not None
        assert flags.execution_hardened is False  # fail-closed default


# ---- ActivationGate --------------------------------------------------


class TestActivationGate:
    def test_p0_requires_all_three(self, store: ActivationFlagsStore) -> None:
        gate = ActivationGate(store)
        # defaults → not ready
        assert gate.check_p0_ready() is False
        store.update_flags(
            ActivationFlags(
                execution_hardened=True,
                mutation_surface_zero=True,
                guardian_coverage=0.95,
            ),
            guardian_signature="sig",
        )
        assert gate.check_p0_ready() is True

    def test_p0_coverage_below_threshold(
        self,
        store: ActivationFlagsStore,
    ) -> None:
        gate = ActivationGate(store)
        store.update_flags(
            ActivationFlags(
                execution_hardened=True,
                mutation_surface_zero=True,
                guardian_coverage=0.94,
            ),
            guardian_signature="sig",
        )
        assert gate.check_p0_ready() is False

    def test_p1_ready(self, store: ActivationFlagsStore) -> None:
        gate = ActivationGate(store)
        assert gate.check_p1_ready() is False
        store.update_flags(
            ActivationFlags(freeze_authority_active=True),
            guardian_signature="sig",
        )
        assert gate.check_p1_ready() is True

    def test_p2_ready_requires_both(self, store: ActivationFlagsStore) -> None:
        gate = ActivationGate(store)
        store.update_flags(
            ActivationFlags(meta_learning_prepared=True),
            guardian_signature="sig",
        )
        assert gate.check_p2_ready() is False  # blast_radius_containment missing
        store.update_flags(
            ActivationFlags(
                meta_learning_prepared=True,
                blast_radius_containment_active=True,
            ),
            guardian_signature="sig2",
        )
        assert gate.check_p2_ready() is True

    def test_check_meta_learning_allowed_requires_p0(
        self,
        store: ActivationFlagsStore,
    ) -> None:
        gate = ActivationGate(store)
        with pytest.raises(RuntimeError):
            gate.check_meta_learning_allowed()

    def test_assert_meta_learning_allowed_raises_when_not_ready(
        self,
        store: ActivationFlagsStore,
    ) -> None:
        gate = ActivationGate(store)
        with pytest.raises(RuntimeError):
            gate.assert_meta_learning_allowed()

    def test_check_meta_learning_allowed_full_happy_path(
        self,
        store: ActivationFlagsStore,
    ) -> None:
        gate = ActivationGate(store)
        store.update_flags(
            ActivationFlags(
                execution_hardened=True,
                mutation_surface_zero=True,
                guardian_coverage=1.0,
                freeze_authority_active=True,
                meta_learning_prepared=True,
                blast_radius_containment_active=True,
                meta_learning_enabled=True,
                replay_digest_hash="digest",
            ),
            guardian_signature="sig",
        )
        assert gate.check_meta_learning_allowed() is True
