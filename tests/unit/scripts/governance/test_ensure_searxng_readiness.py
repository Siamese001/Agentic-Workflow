"""Tests for scripts/governance/ensure_searxng_readiness.py."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "governance"))

import ensure_searxng_readiness as mod  # noqa: E402


class _Proc:
    def __init__(self, stdout: str = "") -> None:
        self.stdout = stdout


def _inspect_payload(*, running: bool = True, restart_policy: str = "unless-stopped") -> str:
    return json.dumps(
        [
            {
                "State": {"Running": running},
                "HostConfig": {"RestartPolicy": {"Name": restart_policy}},
            }
        ]
    )


def test_build_report_passes_when_container_is_running_restart_managed_and_json_ready(monkeypatch) -> None:
    monkeypatch.setattr(mod, "_run_docker", lambda argv, timeout=30: _Proc(_inspect_payload()))
    monkeypatch.setattr(mod, "_probe_json_search", lambda base_url, timeout=20: (True, "results=3"))

    report = mod.build_report()

    assert report.status == "PASS"
    assert report.running is True
    assert report.restart_policy == "unless-stopped"
    assert report.json_search_ready is True


def test_build_report_sets_restart_policy_when_requested(monkeypatch) -> None:
    calls: list[list[str]] = []

    def fake_run(argv, timeout=30):
        calls.append(list(argv))
        if argv[0] == "inspect":
            return _Proc(_inspect_payload(restart_policy="no"))
        return _Proc("")

    monkeypatch.setattr(mod, "_run_docker", fake_run)
    monkeypatch.setattr(mod, "_probe_json_search", lambda base_url, timeout=20: (True, "results=1"))

    report = mod.build_report(set_restart_policy=True)

    assert report.restart_policy_updated is True
    assert ["update", "--restart", "unless-stopped", "agentic_searxng"] in calls


def test_build_report_restarts_after_failed_json_probe(monkeypatch) -> None:
    calls: list[list[str]] = []
    probe_results = iter([(False, "HTTP 403: Forbidden"), (True, "results=2")])

    def fake_run(argv, timeout=30):
        calls.append(list(argv))
        if argv[0] == "inspect":
            return _Proc(_inspect_payload())
        return _Proc("")

    monkeypatch.setattr(mod, "_run_docker", fake_run)
    monkeypatch.setattr(mod, "_probe_json_search", lambda base_url, timeout=20: next(probe_results))
    monkeypatch.setattr(mod.time, "sleep", lambda seconds: None)

    report = mod.build_report(restart=True)

    assert report.status == "PASS"
    assert report.restarted is True
    assert ["restart", "agentic_searxng"] in calls


def test_build_report_fails_when_container_missing(monkeypatch) -> None:
    monkeypatch.setattr(mod, "_inspect_container", lambda container_name: None)

    report = mod.build_report()

    assert report.status == "FAIL"
    assert report.steps[0].step == "inspect"
