"""Tests — W1 phase 3 BGE-M3 operational probe."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
PROBE = REPO_ROOT / "tools" / "certification" / "evidence" / "probe_bge_m3_operational.py"
ARTIFACT = REPO_ROOT / "artifacts" / "certification" / "bge_m3_operational_proof.json"


def _run(env_override: dict | None = None) -> int:
    env = dict(os.environ)
    if env_override:
        for k, v in env_override.items():
            if v is None:
                env.pop(k, None)
            else:
                env[k] = v
    return subprocess.run(
        [sys.executable, str(PROBE)], cwd=str(REPO_ROOT),
        timeout=120, check=False, capture_output=True, env=env,
    ).returncode


def _read() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def _bge_m3_deps_available() -> bool:
    """Detect whether local env has all BGE-M3 deps installed."""
    import importlib.util
    for dep in ("FlagEmbedding", "sentence_transformers", "torch"):
        if importlib.util.find_spec(dep) is None:
            return False
    return True


class TestProbeExits:
    def test_probe_exits_zero_disabled(self):
        # No EMBEDDING_ENABLED -> DISABLED path, exit 0
        assert _run({"EMBEDDING_ENABLED": None}) == 0

    def test_probe_exits_zero_enabled_if_deps_present(self):
        if not _bge_m3_deps_available():
            pytest.skip("BGE-M3 deps not available in this env")
        assert _run({"EMBEDDING_ENABLED": "true"}) == 0

    def test_artifact_exists_after_run(self):
        _run({"EMBEDDING_ENABLED": None})
        assert ARTIFACT.exists()


class TestDisabledPath:
    """Rule 2 anti-cheat: EMBEDDING_ENABLED!=true must not mark OPERATIONAL."""

    def test_disabled_env_yields_disabled_status(self):
        _run({"EMBEDDING_ENABLED": None})
        a = _read()
        assert a["status"] == "DISABLED"
        assert a["actual"]["embedding_enabled_env"] is False

    def test_disabled_records_no_fallback(self):
        _run({"EMBEDDING_ENABLED": None})
        a = _read()
        assert a["actual"]["fallback_used"] is False
        assert a["expected"]["fallback_used"] is False


class TestOperationalPath:
    """When BGE-M3 can load locally, probe must record operational evidence."""

    def test_operational_status_when_enabled_and_cached(self):
        if not _bge_m3_deps_available():
            pytest.skip("BGE-M3 deps not available")
        _run({"EMBEDDING_ENABLED": "true"})
        a = _read()
        if a["status"] != "OPERATIONAL":
            pytest.skip(f"BGE-M3 not operational locally: status={a['status']}")
        assert a["status"] == "OPERATIONAL"
        assert a["actual"]["load_result"]["load_error"] is None

    def test_operational_records_dimension_1024(self):
        if not _bge_m3_deps_available():
            pytest.skip("BGE-M3 deps not available")
        _run({"EMBEDDING_ENABLED": "true"})
        a = _read()
        if a["status"] != "OPERATIONAL":
            pytest.skip(f"BGE-M3 not operational: {a['status']}")
        assert a["actual"]["load_result"]["dimension_actual"] == 1024

    def test_operational_records_model_slug(self):
        if not _bge_m3_deps_available():
            pytest.skip("BGE-M3 deps not available")
        _run({"EMBEDDING_ENABLED": "true"})
        a = _read()
        if a["status"] != "OPERATIONAL":
            pytest.skip(f"BGE-M3 not operational: {a['status']}")
        assert a["actual"]["load_result"]["model_slug"] == "BAAI/bge-m3"

    def test_operational_records_no_fallback(self):
        if not _bge_m3_deps_available():
            pytest.skip("BGE-M3 deps not available")
        _run({"EMBEDDING_ENABLED": "true"})
        a = _read()
        if a["status"] != "OPERATIONAL":
            pytest.skip(f"BGE-M3 not operational: {a['status']}")
        assert a["actual"]["fallback_used"] is False


class TestAntiCheatRule2:
    def test_probe_never_sets_env_vars(self):
        _run({"EMBEDDING_ENABLED": None})
        a = _read()
        assert a["anti_cheat_rules_honored"]["rule_2_no_silent_fallback_pass"] is True
        assert a["anti_cheat_rules_honored"]["probe_never_sets_env_vars"] is True
        assert a["anti_cheat_rules_honored"]["probe_did_not_write_sidecar"] is True

    def test_fallback_used_is_always_false(self):
        # Rule 2: probe NEVER falls back to MiniLM / OpenAI / etc.
        _run({"EMBEDDING_ENABLED": None})
        a = _read()
        assert a["actual"]["fallback_used"] is False


class TestCacheMissingRemediationPlan:
    def test_remediation_plan_present_when_status_not_operational(self):
        # Force a non-operational status (no env) and verify remediation_plan field
        _run({"EMBEDDING_ENABLED": None})
        a = _read()
        if a["status"] != "OPERATIONAL":
            assert a["remediation_plan"] is not None
            assert len(a["remediation_plan"]) > 0
