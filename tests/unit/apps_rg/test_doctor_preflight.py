"""W1 / G1 + G2-preflight: `python -m apps_rg doctor` fails loud on a clean checkout.

Plan: apps-rg-e2e-gap-remediation-7e2d9c.

- G1: doctor --strict exits non-zero with the exact missing-key list.
- G2-preflight: a checkout without fact_vectors exits non-zero with a bootstrap suggestion.

Deterministic product-mode unit tests: ``bootstrap_env=False`` so .env is not reloaded and the
environment is fully controlled by the test.
"""

from __future__ import annotations

import pytest

from apps_rg.runtime import doctor as mod
from apps_rg.runtime.cli_exit_codes import EXIT_CONFIG_ERROR, EXIT_SUCCESS


@pytest.fixture
def _clean_env(monkeypatch: pytest.MonkeyPatch):
    for var in (
        "ANTHROPIC_API_KEY",
        "GOOGLE_API_KEY",
        "OPENAI_API_KEY",
        "CHROMA_PERSIST_DIR",
    ):
        monkeypatch.delenv(var, raising=False)


def _by_name(checks: list[mod.DoctorCheck], name: str) -> mod.DoctorCheck:
    return next(c for c in checks if c.name == name)


def test_strict_missing_generation_key_blocks(_clean_env) -> None:
    checks, code = mod.run_doctor(strict=True, bootstrap_env=False)
    assert code == EXIT_CONFIG_ERROR
    key_check = _by_name(checks, "generation_provider_key")
    assert key_check.is_blocking
    assert "ANTHROPIC_API_KEY" in key_check.detail
    assert "OPENAI_API_KEY" in key_check.detail


def test_missing_fact_vectors_suggests_bootstrap(_clean_env) -> None:
    checks, code = mod.run_doctor(strict=True, bootstrap_env=False)
    assert code == EXIT_CONFIG_ERROR
    fv = _by_name(checks, "fact_vectors_collection")
    assert not fv.ok
    assert "bootstrap fact-vectors" in fv.remediation


def test_judge_keys_are_recommended_never_blocking(_clean_env) -> None:
    checks, _ = mod.run_doctor(strict=True, bootstrap_env=False)
    for var in ("GOOGLE_API_KEY", "OPENAI_API_KEY"):
        jk = _by_name(checks, f"judge_key:{var}")
        assert jk.severity == mod.RECOMMENDED
        assert jk.is_blocking is False


def test_non_strict_exits_zero_even_with_failures(_clean_env) -> None:
    checks, code = mod.run_doctor(strict=False, bootstrap_env=False)
    assert code == EXIT_SUCCESS
    assert any(c.is_blocking for c in checks), "expected blocking checks in cleaned env"


def test_fact_vectors_empty_collection_blocks(_clean_env, tmp_path, monkeypatch) -> None:
    """A present-but-empty fact_vectors collection must block (PASS-but-empty is invalid)."""
    chromadb = pytest.importorskip("chromadb")
    monkeypatch.setenv("CHROMA_PERSIST_DIR", str(tmp_path))
    # Create the collection but leave it empty.
    from apps_rg.runtime.chroma_precomputed_collection import (
        get_precomputed_embeddings_collection,
    )

    client = chromadb.PersistentClient(path=str(tmp_path))
    get_precomputed_embeddings_collection(client, mod.FACT_VECTORS_COLLECTION)
    fv = mod._check_fact_vectors()
    assert not fv.ok
    assert "EMPTY" in fv.detail or "0 atoms" in fv.detail
    assert "bootstrap fact-vectors" in fv.remediation


def test_cli_renders_and_returns_exit_code(monkeypatch, capsys) -> None:
    sentinel = [mod.DoctorCheck("generation_provider_key", False, mod.REQUIRED, "missing", "set it")]
    monkeypatch.setattr(mod, "run_doctor", lambda **kw: (sentinel, EXIT_CONFIG_ERROR))
    rc = mod.run_doctor_cli(["--strict"])
    assert rc == EXIT_CONFIG_ERROR
    out = capsys.readouterr().out
    assert "FAIL" in out
    assert "set it" in out


def test_cli_json_mode(monkeypatch, capsys) -> None:
    sentinel = [mod.DoctorCheck("generation_provider_key", False, mod.REQUIRED, "missing", "set it")]
    monkeypatch.setattr(mod, "run_doctor", lambda **kw: (sentinel, EXIT_CONFIG_ERROR))
    rc = mod.run_doctor_cli(["--json"])
    assert rc == EXIT_CONFIG_ERROR
    out = capsys.readouterr().out
    assert '"exit_code": 2' in out
    assert '"generation_provider_key"' in out


def test_main_dispatches_doctor_before_run_schema(monkeypatch) -> None:
    """`python -m apps_rg doctor ...` routes to the doctor CLI, not the generation parser."""
    import apps_rg.__main__ as entry

    monkeypatch.setattr("apps_rg.runtime.doctor.run_doctor_cli", lambda argv: 99)
    assert entry.main(["doctor", "--strict"]) == 99
