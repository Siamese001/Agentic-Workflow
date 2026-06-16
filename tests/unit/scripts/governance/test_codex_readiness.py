"""Tests for scripts/governance/codex_readiness.py."""

from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "governance"))

import codex_readiness as mod  # noqa: E402


def _transport_report(routes: dict[str, str], processes: dict | None = None) -> dict:
    return {
        "env": {
            "AGENTIC_REPO_ROOT": {"state": "set", "has_unresolved_placeholder": False},
            "ADG_REDIS_URL": {"state": "set", "has_unresolved_placeholder": False},
            "PYTEST_DISABLE_PLUGIN_AUTOLOAD": {"state": "unset", "has_unresolved_placeholder": False},
        },
        "route_evidence": {
            "available": True,
            "counts": {},
            "servers": {
                server_id: {"classification": classification}
                for server_id, classification in routes.items()
            },
        },
        "processes": {"servers": processes or {}},
    }


def test_required_route_must_be_callable() -> None:
    checks = mod._check_required_routes(_transport_report({"memory": "PROCESS_ONLY"}), ["memory"])

    assert checks[0].status == "FAIL"
    assert checks[0].id == "mcp.memory"


def test_required_route_accepts_callable() -> None:
    checks = mod._check_required_routes(_transport_report({"memory": "CALLABLE"}), ["memory"])

    assert checks[0].status == "PASS"


def test_adg_sqlite_fallback_warns_when_snapshot_exists(monkeypatch, tmp_path: Path) -> None:
    snapshot = tmp_path / "artifacts" / "adg" / "adg_indexed_06162026_1200.sqlite"
    snapshot.parent.mkdir(parents=True)
    snapshot.write_text("", encoding="utf-8")
    monkeypatch.setattr(mod, "_latest_adg_snapshot", lambda root: snapshot)

    check = mod._check_adg(_transport_report({"adg_sqlite": "HOST_MCP_REQUIRED"}), tmp_path, True)

    assert check.status == "WARN"
    assert "direct SQLite fallback" in check.summary


def test_adg_sqlite_fallback_checks_primary_root(tmp_path: Path) -> None:
    worktree = tmp_path / "worktree"
    primary = tmp_path / "primary"
    snapshot = primary / "artifacts" / "adg" / "adg_indexed_06162026_1200.sqlite"
    snapshot.parent.mkdir(parents=True)
    snapshot.write_text("", encoding="utf-8")
    report = _transport_report({"adg_sqlite": "HOST_MCP_REQUIRED"})
    report["primary_root"] = str(primary)

    check = mod._check_adg(report, worktree, True)

    assert check.status == "WARN"
    assert str(snapshot) == check.detail


def test_duplicate_process_can_fail_strict_mode() -> None:
    checks = mod._check_process_hygiene(
        _transport_report({}, {"memory": {"classification": "duplicate", "process_count": 2}}),
        fail_duplicates=True,
    )

    assert checks[0].status == "FAIL"


def test_hook_parity_failure_is_critical(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        mod.codex_hook_parity,
        "validate_hook_matrix",
        lambda root: ["missing hook"],
    )

    check = mod._check_hook_parity(tmp_path)

    assert check.status == "FAIL"
    assert check.severity == "critical"


def test_summarize_prefers_failure_over_warning() -> None:
    checks = [
        mod.ReadinessCheck("a", "WARN", "advisory", "warn"),
        mod.ReadinessCheck("b", "FAIL", "critical", "fail"),
    ]

    assert mod.summarize(checks) == "FAIL"
