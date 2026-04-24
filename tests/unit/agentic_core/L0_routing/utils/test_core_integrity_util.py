"""Behavioral tests for ``core_integrity_util``.

Exercises the real merkle-root / golden-seal / emergency-shutdown code paths.
Uses monkeypatching against a temporary directory to avoid mutating the
actual sovereign-core seal during the test run.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from agentic_core.L0_routing.utils.core_integrity_util import (
    ConfigurationError,
    CoreIntegrityVerifier,
    SovereignLockError,
    emergency_shutdown,
)

pytestmark = pytest.mark.unit


@pytest.fixture
def fake_core(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Create a minimal fake base_agents/ dir and redirect CORE_PATH to it.

    Yields the fake core dir path; also redirects GOLDEN_SEAL_FILE into
    tmp_path so the real .core_golden_seal is never touched.
    """
    core = tmp_path / "base_agents"
    core.mkdir()
    (core / "a.py").write_text("print('a')\n", encoding="utf-8")
    (core / "b.py").write_text("print('b')\n", encoding="utf-8")
    nested = core / "nested"
    nested.mkdir()
    (nested / "c.py").write_text("print('c')\n", encoding="utf-8")

    monkeypatch.setattr(CoreIntegrityVerifier, "CORE_PATH", core)
    monkeypatch.setattr(CoreIntegrityVerifier, "GOLDEN_SEAL_FILE", tmp_path / ".seal")
    return core


class TestCalculateFileHash:
    def test_hash_matches_sha256_of_bytes(self, tmp_path: Path) -> None:
        f = tmp_path / "sample.py"
        content = b"hello world\n"
        f.write_bytes(content)

        got = CoreIntegrityVerifier._calculate_file_hash(f)

        assert got == hashlib.sha256(content).hexdigest()

    def test_hash_is_deterministic(self, tmp_path: Path) -> None:
        f = tmp_path / "sample.py"
        f.write_bytes(b"deterministic payload")

        h1 = CoreIntegrityVerifier._calculate_file_hash(f)
        h2 = CoreIntegrityVerifier._calculate_file_hash(f)

        assert h1 == h2

    def test_hash_differs_on_content_change(self, tmp_path: Path) -> None:
        f = tmp_path / "sample.py"
        f.write_bytes(b"v1")
        h1 = CoreIntegrityVerifier._calculate_file_hash(f)

        f.write_bytes(b"v2")
        h2 = CoreIntegrityVerifier._calculate_file_hash(f)

        assert h1 != h2

    def test_raises_configuration_error_on_missing_file(self, tmp_path: Path) -> None:
        missing = tmp_path / "nope.py"

        with pytest.raises(ConfigurationError):
            CoreIntegrityVerifier._calculate_file_hash(missing)


class TestCalculateMerkleRoot:
    def test_returns_hex_sha256_length(self, fake_core: Path) -> None:
        root = CoreIntegrityVerifier._calculate_merkle_root()

        assert isinstance(root, str)
        assert len(root) == 64  # sha256 hex digest
        int(root, 16)  # must parse as hex

    def test_is_deterministic_across_calls(self, fake_core: Path) -> None:
        r1 = CoreIntegrityVerifier._calculate_merkle_root()
        r2 = CoreIntegrityVerifier._calculate_merkle_root()

        assert r1 == r2

    def test_changes_when_a_file_is_modified(self, fake_core: Path) -> None:
        r1 = CoreIntegrityVerifier._calculate_merkle_root()

        (fake_core / "a.py").write_text("print('a-modified')\n", encoding="utf-8")
        r2 = CoreIntegrityVerifier._calculate_merkle_root()

        assert r1 != r2

    def test_changes_when_a_file_is_renamed(self, fake_core: Path) -> None:
        """Rel-path is included in the hash input, so renames must affect root."""
        r1 = CoreIntegrityVerifier._calculate_merkle_root()

        (fake_core / "a.py").rename(fake_core / "a_renamed.py")
        r2 = CoreIntegrityVerifier._calculate_merkle_root()

        assert r1 != r2

    def test_raises_when_no_python_files(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        empty = tmp_path / "empty_core"
        empty.mkdir()
        monkeypatch.setattr(CoreIntegrityVerifier, "CORE_PATH", empty)

        with pytest.raises(ConfigurationError, match="No Python files found"):
            CoreIntegrityVerifier._calculate_merkle_root()


class TestForceVerify:
    def test_returns_true_on_clean_core(self, fake_core: Path) -> None:
        assert CoreIntegrityVerifier.force_verify() is True

    @pytest.mark.parametrize("bad_suffix", [".tmp", ".bak", ".pyc"])
    def test_raises_on_unsafe_artifacts(
        self, fake_core: Path, bad_suffix: str
    ) -> None:
        (fake_core / f"bad{bad_suffix}").write_bytes(b"x")

        with pytest.raises(ConfigurationError, match="Integrity Breach"):
            CoreIntegrityVerifier.force_verify()

    def test_raises_when_core_missing(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            CoreIntegrityVerifier, "CORE_PATH", tmp_path / "nonexistent_core"
        )

        with pytest.raises(ConfigurationError, match="Sovereign Core Missing"):
            CoreIntegrityVerifier.force_verify()


class TestUpdateGoldenSeal:
    def test_writes_current_merkle_root_to_seal_file(self, fake_core: Path) -> None:
        returned = CoreIntegrityVerifier.update_golden_seal()

        assert CoreIntegrityVerifier.GOLDEN_SEAL_FILE.exists()
        on_disk = CoreIntegrityVerifier.GOLDEN_SEAL_FILE.read_text().strip()
        assert on_disk == returned
        assert on_disk == CoreIntegrityVerifier._calculate_merkle_root()


class TestVerifyCoreIntegrity:
    def test_creates_golden_seal_on_first_run(self, fake_core: Path) -> None:
        assert not CoreIntegrityVerifier.GOLDEN_SEAL_FILE.exists()

        assert CoreIntegrityVerifier.verify_core_integrity() is True

        assert CoreIntegrityVerifier.GOLDEN_SEAL_FILE.exists()
        seal = CoreIntegrityVerifier.GOLDEN_SEAL_FILE.read_text().strip()
        assert seal == CoreIntegrityVerifier._calculate_merkle_root()

    def test_passes_when_seal_matches(self, fake_core: Path) -> None:
        CoreIntegrityVerifier.verify_core_integrity()  # creates seal
        assert CoreIntegrityVerifier.verify_core_integrity() is True

    def test_auto_reseals_when_files_mutated(self, fake_core: Path) -> None:
        CoreIntegrityVerifier.verify_core_integrity()  # creates seal
        original_seal = CoreIntegrityVerifier.GOLDEN_SEAL_FILE.read_text().strip()

        (fake_core / "a.py").write_text("print('mutated')\n", encoding="utf-8")
        assert CoreIntegrityVerifier.verify_core_integrity() is True

        new_seal = CoreIntegrityVerifier.GOLDEN_SEAL_FILE.read_text().strip()
        assert new_seal != original_seal
        assert new_seal == CoreIntegrityVerifier._calculate_merkle_root()

    @pytest.mark.parametrize("bad_suffix", [".tmp", ".bak", ".pyc"])
    def test_raises_on_unsafe_artifacts(
        self, fake_core: Path, bad_suffix: str
    ) -> None:
        (fake_core / f"bad{bad_suffix}").write_bytes(b"x")

        with pytest.raises(ConfigurationError, match="Integrity Breach"):
            CoreIntegrityVerifier.verify_core_integrity()


class TestEmergencyShutdown:
    def test_raises_sovereign_lock_error(self) -> None:
        with pytest.raises(SovereignLockError, match="test breach"):
            emergency_shutdown("test breach")

    def test_sovereign_lock_error_is_configuration_error_subclass(self) -> None:
        """SovereignLockError must be catchable as ConfigurationError."""
        assert issubclass(SovereignLockError, ConfigurationError)

        with pytest.raises(ConfigurationError):
            emergency_shutdown("caught as ConfigurationError")
