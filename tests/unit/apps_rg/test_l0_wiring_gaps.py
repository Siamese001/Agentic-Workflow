"""Regression tests for apps_rg L0 wiring gaps (plan apps-rg-l0-wiring-gap-remediation-f3c9d1).

Covers:
  - GAP-1/W1: R1A exact-cache pre-flight check short-circuits pipeline on hit
  - GAP-2/W2: R1B semantic-cache pre-flight check short-circuits pipeline on hit
  - GAP-3/W3: Env-flag off path (R1A still runs; R1B gated by SEMANTIC_CACHE_D2_ENABLED)
  - GAP-4/W4: R1A post-run stamp called after clean pipeline exit
  - GAP-5/W4: R1B post-run store called after clean pipeline exit when env flag on
  - GAP-6/W5: route_registry.yaml reader resolves route_id; fallback to ROUTE_ID constant
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest


def _fake_r4_result(fault: str = "", terminal_r5: bool = False) -> Any:
    """Build a minimal fake R4IntegratedRunResult."""
    result = MagicMock()
    result.run_id = "run-test-abc123"
    result.x3_disposition = "allow"
    result.terminal_r5 = terminal_r5
    result.terminal_r5_reason = ""
    result.artifact_dir = Path(tempfile.mkdtemp())
    result.fault = fault
    return result


# ---------------------------------------------------------------------------
# R1A adapter unit tests (GAP-1 / W1)
# ---------------------------------------------------------------------------

class TestR1ACacheAdapter:
    """Tests for apps_rg.cache.r1a_adapter — verifies the adapter is correct."""

    def test_compute_r1a_key_is_deterministic(self):
        from apps_rg.cache.r1a_adapter import compute_r1a_key

        key1 = compute_r1a_key(
            source_resume_hash="abc",
            target_company="Acme Corp",
            target_role="SWE",
        )
        key2 = compute_r1a_key(
            source_resume_hash="abc",
            target_company="Acme Corp",
            target_role="SWE",
        )
        assert key1 == key2
        assert len(key1) == 64  # sha256 hex

    def test_compute_r1a_key_differs_on_company_change(self):
        from apps_rg.cache.r1a_adapter import compute_r1a_key

        key1 = compute_r1a_key(source_resume_hash="abc", target_company="Acme", target_role="SWE")
        key2 = compute_r1a_key(source_resume_hash="abc", target_company="Other", target_role="SWE")
        assert key1 != key2

    def test_compute_r1a_key_case_insensitive_company(self):
        from apps_rg.cache.r1a_adapter import compute_r1a_key

        key1 = compute_r1a_key(source_resume_hash="abc", target_company="ACME", target_role="swe")
        key2 = compute_r1a_key(source_resume_hash="abc", target_company="acme", target_role="swe")
        assert key1 == key2

    def test_check_r1a_cache_miss_on_empty_dir(self, tmp_path):
        from apps_rg.cache.r1a_adapter import check_r1a_cache

        result = check_r1a_cache("somekey", runs_dir=tmp_path)
        assert result is None

    def test_check_r1a_cache_hit_when_key_and_output_exist(self, tmp_path):
        from apps_rg.cache.r1a_adapter import check_r1a_cache, compute_r1a_key, stamp_r1a_cache

        key = compute_r1a_key(source_resume_hash="abc", target_company="acme", target_role="swe")
        run_dir = tmp_path / "run_001"
        run_dir.mkdir()
        (run_dir / "generated_resume.json").write_text('{"ok": true}', encoding="utf-8")
        stamp_r1a_cache(key, str(run_dir))

        result = check_r1a_cache(key, runs_dir=tmp_path)
        assert result == str(run_dir)

    def test_check_r1a_cache_miss_when_only_key_file_exists(self, tmp_path):
        from apps_rg.cache.r1a_adapter import check_r1a_cache

        run_dir = tmp_path / "run_002"
        run_dir.mkdir()
        (run_dir / "r1a_key.txt").write_text("somekey", encoding="utf-8")
        # no generated_resume.json

        result = check_r1a_cache("somekey", runs_dir=tmp_path)
        assert result is None

    def test_stamp_r1a_cache_writes_key_file(self, tmp_path):
        from apps_rg.cache.r1a_adapter import stamp_r1a_cache

        run_dir = tmp_path / "run_003"
        run_dir.mkdir()
        stamp_r1a_cache("testkey", str(run_dir))

        key_file = run_dir / "r1a_key.txt"
        assert key_file.exists()
        assert key_file.read_text(encoding="utf-8") == "testkey"


# ---------------------------------------------------------------------------
# __main__.py wiring integration tests (GAP-1/W1, GAP-2/W2, GAP-4/W4, GAP-5/W4)
# ---------------------------------------------------------------------------

class TestMainR1AWiring:
    """Tests that __main__.main() calls R1A check before the pipeline."""

    def _make_args(self, tmp_path):
        args = MagicMock()
        args.target_company = "TestCo"
        args.target_role = "Engineer"
        args.candidate = None
        args.jd = None
        args.manual_brief = str(tmp_path / "brief.json")
        args.target_level = None
        args.research_via = None
        args.auto_research_internal = False
        args.auto_research_tavily = False
        args.tenant_id = "default"
        return args

    def test_r1a_cache_hit_exits_without_running_pipeline(self, tmp_path, monkeypatch):
        """When R1A returns a hit, pipeline is never called and sys.exit(0) fires."""
        from apps_rg import __main__ as m

        monkeypatch.setattr(m, "check_r1a_cache", lambda key, runs_dir: str(tmp_path))
        pipeline_called = []

        def fake_pipeline(**kwargs):
            pipeline_called.append(True)
            return _fake_r4_result()

        monkeypatch.setattr(m, "run_integrated_r4_deterministic_pipeline", fake_pipeline)

        args = self._make_args(tmp_path)
        with pytest.raises(SystemExit) as exc_info:
            m._run_with_args(args, runs_dir=tmp_path)
        assert exc_info.value.code == 0
        assert not pipeline_called

    def test_r1a_cache_miss_runs_pipeline(self, tmp_path, monkeypatch):
        """When R1A misses, pipeline is called."""
        from apps_rg import __main__ as m

        monkeypatch.setattr(m, "check_r1a_cache", lambda key, runs_dir: None)
        monkeypatch.setenv("SEMANTIC_CACHE_D2_ENABLED", "0")
        pipeline_called = []

        def fake_pipeline(**kwargs):
            pipeline_called.append(True)
            return _fake_r4_result()

        monkeypatch.setattr(m, "run_integrated_r4_deterministic_pipeline", fake_pipeline)

        args = self._make_args(tmp_path)
        with pytest.raises(SystemExit) as exc_info:
            m._run_with_args(args, runs_dir=tmp_path)
        assert exc_info.value.code == 0
        assert pipeline_called

    def test_r1a_stamp_called_on_clean_run(self, tmp_path, monkeypatch):
        """After a clean pipeline run, stamp_r1a_cache is called."""
        from apps_rg import __main__ as m

        monkeypatch.setattr(m, "check_r1a_cache", lambda key, runs_dir: None)
        monkeypatch.setenv("SEMANTIC_CACHE_D2_ENABLED", "0")

        stamped_keys = []

        def fake_stamp(key, run_dir):
            stamped_keys.append(key)

        monkeypatch.setattr(m, "stamp_r1a_cache", fake_stamp)

        def fake_pipeline(**kwargs):
            return _fake_r4_result(fault="")

        monkeypatch.setattr(m, "run_integrated_r4_deterministic_pipeline", fake_pipeline)

        args = self._make_args(tmp_path)
        with pytest.raises(SystemExit):
            m._run_with_args(args, runs_dir=tmp_path)

        assert len(stamped_keys) == 1

    def test_r1a_stamp_skipped_on_fault(self, tmp_path, monkeypatch):
        """When pipeline returns a fault, stamp is NOT called."""
        from apps_rg import __main__ as m

        monkeypatch.setattr(m, "check_r1a_cache", lambda key, runs_dir: None)
        monkeypatch.setenv("SEMANTIC_CACHE_D2_ENABLED", "0")

        stamped_keys = []

        def fake_stamp(key, run_dir):
            stamped_keys.append(key)

        monkeypatch.setattr(m, "stamp_r1a_cache", fake_stamp)

        def fake_pipeline(**kwargs):
            return _fake_r4_result(fault="L2_EXECUTION_ERROR:something")

        monkeypatch.setattr(m, "run_integrated_r4_deterministic_pipeline", fake_pipeline)

        args = self._make_args(tmp_path)
        with pytest.raises(SystemExit) as exc_info:
            m._run_with_args(args, runs_dir=tmp_path)
        assert exc_info.value.code == 1  # fault → exit 1
        assert not stamped_keys

    def test_r1a_stamp_skipped_on_terminal_r5(self, tmp_path, monkeypatch):
        """When pipeline returns terminal_r5=True, stamp is NOT called."""
        from apps_rg import __main__ as m

        monkeypatch.setattr(m, "check_r1a_cache", lambda key, runs_dir: None)
        monkeypatch.setenv("SEMANTIC_CACHE_D2_ENABLED", "0")

        stamped_keys = []

        def fake_stamp(key, run_dir):
            stamped_keys.append(key)

        monkeypatch.setattr(m, "stamp_r1a_cache", fake_stamp)

        def fake_pipeline(**kwargs):
            return _fake_r4_result(terminal_r5=True)

        monkeypatch.setattr(m, "run_integrated_r4_deterministic_pipeline", fake_pipeline)

        args = self._make_args(tmp_path)
        with pytest.raises(SystemExit):
            m._run_with_args(args, runs_dir=tmp_path)
        assert not stamped_keys


class TestMainR1BWiring:
    """Tests that __main__.main() calls R1B check when env flag is on."""

    def _make_args(self, tmp_path):
        args = MagicMock()
        args.target_company = "TestCo"
        args.target_role = "Engineer"
        args.candidate = None
        args.jd = None
        args.manual_brief = str(tmp_path / "brief.json")
        args.target_level = None
        args.research_via = None
        args.auto_research_internal = False
        args.auto_research_tavily = False
        args.tenant_id = "default"
        return args

    def test_r1b_not_called_when_env_flag_off(self, tmp_path, monkeypatch):
        from apps_rg import __main__ as m

        monkeypatch.setattr(m, "check_r1a_cache", lambda key, runs_dir: None)
        monkeypatch.setattr(m, "stamp_r1a_cache", lambda key, run_dir: None)
        monkeypatch.setenv("SEMANTIC_CACHE_D2_ENABLED", "0")

        r1b_called = []

        def fake_check_r1b(**kwargs):
            r1b_called.append(True)
            return None

        with patch("apps_rg.cache.r1b_adapter.check_r1b_for_apps_rg", fake_check_r1b):
            def fake_pipeline(**kwargs):
                return _fake_r4_result()

            monkeypatch.setattr(m, "run_integrated_r4_deterministic_pipeline", fake_pipeline)
            args = self._make_args(tmp_path)
            with pytest.raises(SystemExit):
                m._run_with_args(args, runs_dir=tmp_path)

        assert not r1b_called

    def test_r1b_hit_exits_without_running_pipeline(self, tmp_path, monkeypatch):
        """When R1B returns a hit and env flag is on, pipeline is never called."""
        from apps_rg import __main__ as m

        monkeypatch.setattr(m, "check_r1a_cache", lambda key, runs_dir: None)
        monkeypatch.setenv("SEMANTIC_CACHE_D2_ENABLED", "1")

        pipeline_called = []

        def fake_pipeline(**kwargs):
            pipeline_called.append(True)
            return _fake_r4_result()

        monkeypatch.setattr(m, "run_integrated_r4_deterministic_pipeline", fake_pipeline)

        with patch("apps_rg.cache.r1b_adapter.check_r1b_for_apps_rg", return_value={"cached": True}):
            args = self._make_args(tmp_path)
            with pytest.raises(SystemExit) as exc_info:
                m._run_with_args(args, runs_dir=tmp_path)
            assert exc_info.value.code == 0
            assert not pipeline_called

    def test_r1b_miss_runs_pipeline(self, tmp_path, monkeypatch):
        """When R1B misses, pipeline still runs."""
        from apps_rg import __main__ as m

        monkeypatch.setattr(m, "check_r1a_cache", lambda key, runs_dir: None)
        monkeypatch.setattr(m, "stamp_r1a_cache", lambda key, run_dir: None)
        monkeypatch.setenv("SEMANTIC_CACHE_D2_ENABLED", "1")

        pipeline_called = []

        def fake_pipeline(**kwargs):
            pipeline_called.append(True)
            return _fake_r4_result()

        monkeypatch.setattr(m, "run_integrated_r4_deterministic_pipeline", fake_pipeline)

        with patch("apps_rg.cache.r1b_adapter.check_r1b_for_apps_rg", return_value=None):
            args = self._make_args(tmp_path)
            with pytest.raises(SystemExit):
                m._run_with_args(args, runs_dir=tmp_path)

        assert pipeline_called

    def test_r1b_store_called_on_clean_run_with_chunks(self, tmp_path, monkeypatch):
        """R1B store is called after a clean run when output chunks are available."""
        from apps_rg import __main__ as m

        monkeypatch.setattr(m, "check_r1a_cache", lambda key, runs_dir: None)
        monkeypatch.setattr(m, "stamp_r1a_cache", lambda key, run_dir: None)
        monkeypatch.setenv("SEMANTIC_CACHE_D2_ENABLED", "1")

        artifact_dir = tmp_path / "r4_abc"
        artifact_dir.mkdir(parents=True)
        (artifact_dir / "generated_resume.json").write_text(
            json.dumps([{"section": "summary", "content": "hello"}]), encoding="utf-8"
        )

        def fake_pipeline(**kwargs):
            r = _fake_r4_result()
            r.artifact_dir = artifact_dir
            return r

        monkeypatch.setattr(m, "run_integrated_r4_deterministic_pipeline", fake_pipeline)

        mock_adapter = MagicMock()
        mock_adapter.store_intent_and_output.return_value = None

        with patch("apps_rg.cache.r1b_adapter.check_r1b_for_apps_rg", return_value=None):
            with patch("apps_rg.cache.r1b_adapter.AppsRgR1BCacheAdapter", return_value=mock_adapter):
                args = self._make_args(tmp_path)
                with pytest.raises(SystemExit):
                    m._run_with_args(args, runs_dir=tmp_path, artifact_dir_override=artifact_dir)

        assert mock_adapter.store_intent_and_output.called

    def test_r1b_store_skipped_when_no_chunks(self, tmp_path, monkeypatch):
        """R1B store is NOT called when generated_resume.json is absent."""
        from apps_rg import __main__ as m

        monkeypatch.setattr(m, "check_r1a_cache", lambda key, runs_dir: None)
        monkeypatch.setattr(m, "stamp_r1a_cache", lambda key, run_dir: None)
        monkeypatch.setenv("SEMANTIC_CACHE_D2_ENABLED", "1")

        def fake_pipeline(**kwargs):
            return _fake_r4_result()

        monkeypatch.setattr(m, "run_integrated_r4_deterministic_pipeline", fake_pipeline)

        mock_adapter = MagicMock()

        with patch("apps_rg.cache.r1b_adapter.check_r1b_for_apps_rg", return_value=None):
            with patch("apps_rg.cache.r1b_adapter.AppsRgR1BCacheAdapter", return_value=mock_adapter):
                args = self._make_args(tmp_path)
                with pytest.raises(SystemExit):
                    m._run_with_args(args, runs_dir=tmp_path)

        assert not mock_adapter.store_intent_and_output.called


# ---------------------------------------------------------------------------
# Route registry reader tests (GAP-6 / W5)
# ---------------------------------------------------------------------------

class TestLoadRouteIdForApp:
    """Tests for _load_route_id_for_app helper in integrated_r4_deterministic_pipeline_run."""

    def test_returns_route_id_constant_when_no_app(self):
        from agentic_core.runtime.entrypoints.integrated_r4_deterministic_pipeline_run import (
            _load_route_id_for_app,
            ROUTE_ID,
        )
        assert _load_route_id_for_app("") == ROUTE_ID

    def test_returns_route_id_constant_when_registry_absent(self, tmp_path, monkeypatch):
        from agentic_core.runtime.entrypoints.integrated_r4_deterministic_pipeline_run import (
            _load_route_id_for_app,
            ROUTE_ID,
        )
        monkeypatch.chdir(tmp_path)
        assert _load_route_id_for_app("nonexistent_app") == ROUTE_ID

    def test_reads_route_id_from_yaml(self, tmp_path, monkeypatch):
        from agentic_core.runtime.entrypoints.integrated_r4_deterministic_pipeline_run import (
            _load_route_id_for_app,
        )
        monkeypatch.chdir(tmp_path)
        registry_dir = tmp_path / "my_app" / "config"
        registry_dir.mkdir(parents=True)
        (registry_dir / "route_registry.yaml").write_text(
            "app_name: my_app\nroutes:\n  - route_id: my_app.primary_v1\n",
            encoding="utf-8",
        )
        result = _load_route_id_for_app("my_app")
        assert result == "my_app.primary_v1"

    def test_fallback_on_malformed_yaml(self, tmp_path, monkeypatch):
        from agentic_core.runtime.entrypoints.integrated_r4_deterministic_pipeline_run import (
            _load_route_id_for_app,
            ROUTE_ID,
        )
        monkeypatch.chdir(tmp_path)
        registry_dir = tmp_path / "bad_app" / "config"
        registry_dir.mkdir(parents=True)
        (registry_dir / "route_registry.yaml").write_text(
            ":::not valid yaml:::", encoding="utf-8"
        )
        result = _load_route_id_for_app("bad_app")
        assert result == ROUTE_ID

    def test_fallback_on_empty_routes(self, tmp_path, monkeypatch):
        from agentic_core.runtime.entrypoints.integrated_r4_deterministic_pipeline_run import (
            _load_route_id_for_app,
            ROUTE_ID,
        )
        monkeypatch.chdir(tmp_path)
        registry_dir = tmp_path / "empty_app" / "config"
        registry_dir.mkdir(parents=True)
        (registry_dir / "route_registry.yaml").write_text(
            "app_name: empty_app\nroutes: []\n", encoding="utf-8"
        )
        result = _load_route_id_for_app("empty_app")
        assert result == ROUTE_ID

    def test_apps_rg_registry_resolves_correct_route_id(self):
        """Integration: actual apps_rg registry returns the declared route_id."""
        from agentic_core.runtime.entrypoints.integrated_r4_deterministic_pipeline_run import (
            _load_route_id_for_app,
        )
        result = _load_route_id_for_app("apps_rg")
        assert result == "apps_rg.resume_generation_v1"
