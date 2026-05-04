"""W5 T-suite — C0 bypass + PreloadedInputContextManifest governance tests (6 tests).

apps_rg bypasses C0 corpus retrieval.  These tests verify that:
1. The C0 bypass is declared in the static DAG.
2. PreloadedInputContextManifest can be built, hashed, and round-tripped.
3. The manifest_hash is stable (same inputs → same hash).
4. The manifest write() produces a valid JSON file.
5. No C0 retrieval imports exist in apps_rg (no vector_db, no C0 index call).
6. rg_identity_resolver produces a deterministic identity for CLI runs.

All tests are pure static analysis or in-process construction — no live run.
"""
from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_MODULE = (
    REPO_ROOT / "apps_rg" / "integrations" / "preloaded_input_context_manifest.py"
)
IDENTITY_MODULE = (
    REPO_ROOT / "apps_rg" / "integrations" / "rg_identity_resolver.py"
)
STATIC_DAG = REPO_ROOT / "apps_rg" / "config" / "apps_rg_static_dag.yaml"


# ---------------------------------------------------------------------------
# Test 1: C0 bypass declared in static DAG
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_rg_c0_bypass_declared_in_static_dag() -> None:
    """apps_rg_static_dag.yaml must declare c0_bypass with reason GROUNDING_NOT_REQUIRED."""
    assert STATIC_DAG.exists(), f"Static DAG not found: {STATIC_DAG}"
    content = STATIC_DAG.read_text(encoding="utf-8")
    assert "c0_bypass" in content, (
        "apps_rg_static_dag.yaml must declare c0_bypass block. "
        "apps_rg uses preloaded inputs, not corpus retrieval (W4 P9)."
    )
    assert "GROUNDING_NOT_REQUIRED" in content, (
        "c0_bypass reason must be GROUNDING_NOT_REQUIRED."
    )


# ---------------------------------------------------------------------------
# Test 2: PreloadedInputContextManifest module exists
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_rg_preloaded_manifest_module_exists() -> None:
    """apps_rg/integrations/preloaded_input_context_manifest.py must exist (W3 P7)."""
    assert MANIFEST_MODULE.exists(), (
        f"PreloadedInputContextManifest not found at {MANIFEST_MODULE}. "
        "W3 P7 must land before this test can pass."
    )
    src = MANIFEST_MODULE.read_text(encoding="utf-8")
    assert "PreloadedInputContextManifest" in src
    assert "build_preloaded_input_context_manifest" in src
    assert "manifest_hash" in src


# ---------------------------------------------------------------------------
# Test 3: Manifest builder produces stable hash (deterministic)
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_rg_manifest_hash_is_deterministic() -> None:
    """Same inputs must produce the same manifest_hash on repeated calls."""
    import importlib.util  # noqa: PLC0415
    spec = importlib.util.spec_from_file_location(
        "preloaded_input_context_manifest", MANIFEST_MODULE
    )
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]

    with tempfile.TemporaryDirectory() as tmpdir:
        jd = Path(tmpdir) / "jd.json"
        brief = Path(tmpdir) / "brief.json"
        resume = Path(tmpdir) / "resume.json"
        jd.write_text('{"title": "SVP", "description": "lead the team"}', encoding="utf-8")
        brief.write_text('{"company": "Acme"}', encoding="utf-8")
        resume.write_text('{"name": "Amit"}', encoding="utf-8")

        m1 = mod.build_preloaded_input_context_manifest(
            jd_path=jd,
            brief_path=brief,
            master_resume_path=resume,
            run_id="run-abc-123",
            replay_key="rk-abc",
        )
        m2 = mod.build_preloaded_input_context_manifest(
            jd_path=jd,
            brief_path=brief,
            master_resume_path=resume,
            run_id="run-abc-123",
            replay_key="rk-abc",
        )

    assert m1.manifest_hash == m2.manifest_hash, (
        "manifest_hash must be deterministic: same inputs must produce same hash. "
        f"Got {m1.manifest_hash!r} vs {m2.manifest_hash!r}."
    )


# ---------------------------------------------------------------------------
# Test 4: Manifest write() produces valid JSON with required keys
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_rg_manifest_write_produces_valid_json() -> None:
    """manifest.write(dir) must produce a valid JSON file with required top-level keys."""
    import importlib.util  # noqa: PLC0415
    spec = importlib.util.spec_from_file_location(
        "preloaded_input_context_manifest", MANIFEST_MODULE
    )
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]

    with tempfile.TemporaryDirectory() as tmpdir:
        jd = Path(tmpdir) / "jd.json"
        brief = Path(tmpdir) / "brief.json"
        resume = Path(tmpdir) / "resume.json"
        jd.write_text('{"title": "SVP"}', encoding="utf-8")
        brief.write_text('{}', encoding="utf-8")
        resume.write_text('{}', encoding="utf-8")

        manifest = mod.build_preloaded_input_context_manifest(
            jd_path=jd,
            brief_path=brief,
            master_resume_path=resume,
            run_id="run-write-test",
        )
        out_dir = Path(tmpdir) / "artifacts"
        written = manifest.write(out_dir)

        assert written.exists(), f"manifest.write() did not produce a file at {written}"
        data = json.loads(written.read_text(encoding="utf-8"))

    required_keys = {
        "schema_version", "run_id", "manifest_hash",
        "replay_key", "c0_bypass_reason", "inputs", "audit_refs",
    }
    missing = required_keys - set(data.keys())
    assert not missing, (
        f"Manifest JSON missing required keys: {missing}. "
        "PreloadedInputContextManifest must record full provenance (W3 P7)."
    )
    assert data["c0_bypass_reason"] == "GROUNDING_NOT_REQUIRED"


# ---------------------------------------------------------------------------
# Test 5: No C0 retrieval imports in apps_rg source tree
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_rg_has_no_c0_retrieval_imports() -> None:
    """apps_rg must not import any C0 corpus retrieval module."""
    apps_rg_dir = REPO_ROOT / "apps_rg"
    forbidden_patterns = [
        "from agentic_core.L0_routing.c0_retrieval",
        "import c0_retrieval",
        "from agentic_core.knowledge.retrieval.vector",
        "vector_db.query",
        "chromadb",
    ]
    violations = []
    for py_file in apps_rg_dir.rglob("*.py"):
        src = py_file.read_text(encoding="utf-8")
        for pattern in forbidden_patterns:
            if pattern in src:
                violations.append((str(py_file.relative_to(REPO_ROOT)), pattern))

    assert not violations, (
        f"apps_rg contains C0 retrieval imports — apps_rg is a preloaded-context "
        f"app and must NOT perform corpus retrieval (W3 P5 / spine_manifest R4).\n"
        f"Violations: {violations}"
    )


# ---------------------------------------------------------------------------
# Test 6: rg_identity_resolver produces deterministic identity
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_rg_identity_resolver_is_deterministic() -> None:
    """resolve_rg_identity() must produce the same principal_hash for same inputs."""
    assert IDENTITY_MODULE.exists(), (
        f"rg_identity_resolver.py not found at {IDENTITY_MODULE}. W4 P12 required."
    )
    import importlib.util  # noqa: PLC0415
    spec = importlib.util.spec_from_file_location("rg_identity_resolver", IDENTITY_MODULE)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]

    id1 = mod.resolve_rg_identity(user_id="amit", tenant_id="local")
    id2 = mod.resolve_rg_identity(user_id="amit", tenant_id="local")

    assert id1.principal_hash == id2.principal_hash, (
        "resolve_rg_identity must be deterministic: same user_id + tenant_id "
        f"must produce same principal_hash. Got {id1.principal_hash!r} vs {id2.principal_hash!r}."
    )
    assert id1.source_channel == "apps_rg_cli", (
        "Default source_channel must be 'apps_rg_cli'."
    )
    # Different user_id must produce a different hash
    id3 = mod.resolve_rg_identity(user_id="other", tenant_id="local")
    assert id1.principal_hash != id3.principal_hash, (
        "Different user_id must produce different principal_hash."
    )
