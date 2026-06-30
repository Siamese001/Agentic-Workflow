"""Tests for scripts/governance/codex_readiness.py."""

from __future__ import annotations

import json
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
    assert "missing route/callability proof" in checks[0].detail


def test_process_only_without_callable_contract_remains_route_failure() -> None:
    report = _transport_report(
        {"memory": "PROCESS_ONLY"},
        {"memory": {"classification": "single", "process_count": 1}},
    )

    check = mod._check_required_routes(report, ["memory"])[0]

    assert check.status == "FAIL"
    assert check.severity == "critical"
    assert check.summary == "memory is missing Codex route/callability proof."


def test_required_route_failure_detail_is_actionable_for_missing_host_route() -> None:
    report = _transport_report({"GitKraken": "PROCESS_ONLY"})
    report["route_evidence"]["servers"]["GitKraken"] = {
        "classification": "PROCESS_ONLY",
        "callable_status": "absent",
        "selected_codex_route": None,
        "process_classification": "duplicate",
        "process_count": 3,
    }

    check = mod._check_required_routes(report, ["GitKraken"])[0]
    detail = json.loads(check.detail)

    assert check.status == "FAIL"
    assert check.summary == "GitKraken is missing Codex route/callability proof."
    assert detail["blocker"] == "missing route/callability proof"
    assert "only proves startup" in detail["why"]
    assert "CODEX_MCP_CALLABLE_GITKRAKEN=healthy" in detail["unblock"]


def test_required_route_accepts_callable() -> None:
    checks = mod._check_required_routes(_transport_report({"memory": "CALLABLE"}), ["memory"])

    assert checks[0].status == "PASS"


def test_required_route_accepts_substitute_callable() -> None:
    checks = mod._check_required_routes(_transport_report({"GitKraken": "SUBSTITUTE_CALLABLE"}), ["GitKraken"])

    assert checks[0].status == "PASS"


def test_default_required_callable_routes_cover_core_only() -> None:
    assert mod.DEFAULT_REQUIRED_CALLABLE_ROUTES == ("memory", "GitKraken")


def test_docs_only_mode_omits_default_callable_routes_and_allows_adg_fallback() -> None:
    args = mod.parse_args(["--docs-only"])

    assert mod._resolve_required_callable_routes(args) == ()
    assert mod._resolve_allow_adg_sqlite_fallback(args) is True


def test_docs_only_mode_keeps_explicit_required_routes() -> None:
    args = mod.parse_args(["--docs-only", "--require-callable-route", "vector_db"])

    assert mod._resolve_required_callable_routes(args) == ("vector_db",)


def test_no_adg_sqlite_fallback_overrides_docs_only() -> None:
    args = mod.parse_args(["--docs-only", "--no-adg-sqlite-fallback"])

    assert mod._resolve_allow_adg_sqlite_fallback(args) is False


def test_vector_semantic_guard_warns_without_explicit_state(monkeypatch) -> None:
    monkeypatch.delenv("CODEX_MCP_VECTOR_DB_SEMANTIC_STATE", raising=False)

    check = mod._check_vector_semantic_guard(["vector_db"])

    assert check is not None
    assert check.status == "WARN"
    assert "stats-only" in check.summary


def test_vector_semantic_guard_fails_on_metadata_only(monkeypatch) -> None:
    monkeypatch.setenv("CODEX_MCP_VECTOR_DB_SEMANTIC_STATE", "metadata_only")

    check = mod._check_vector_semantic_guard(["vector_db"])

    assert check is not None
    assert check.status == "FAIL"


def test_vector_semantic_guard_passes_on_ready(monkeypatch) -> None:
    monkeypatch.setenv("CODEX_MCP_VECTOR_DB_SEMANTIC_STATE", "ready")

    check = mod._check_vector_semantic_guard(["vector_db"])

    assert check is not None
    assert check.status == "PASS"


def test_adg_sqlite_fallback_warns_when_snapshot_exists(monkeypatch, tmp_path: Path) -> None:
    snapshot = tmp_path / "artifacts" / "adg" / "adg_indexed_06162026_1200.sqlite"
    snapshot.parent.mkdir(parents=True)
    snapshot.write_text("", encoding="utf-8")
    monkeypatch.setattr(mod, "_latest_adg_snapshot", lambda root: snapshot)

    check = mod._check_adg(_transport_report({"adg_sqlite": "HOST_MCP_REQUIRED"}), tmp_path, True)

    assert check.status == "WARN"
    assert "direct SQLite fallback" in check.summary


def test_adg_sqlite_fallback_is_strict_by_default(monkeypatch, tmp_path: Path) -> None:
    snapshot = tmp_path / "artifacts" / "adg" / "adg_indexed_06162026_1200.sqlite"
    snapshot.parent.mkdir(parents=True)
    snapshot.write_text("", encoding="utf-8")
    monkeypatch.setattr(mod, "_latest_adg_snapshot", lambda root: snapshot)

    check = mod._check_adg(_transport_report({"adg_sqlite": "HOST_MCP_REQUIRED"}), tmp_path, False)

    assert check.status == "FAIL"
    assert "no acceptable SQLite fallback" in check.summary


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


def test_duplicate_process_hygiene_is_separate_from_route_failure() -> None:
    report = _transport_report(
        {"memory": "PROCESS_ONLY"},
        {"memory": {"classification": "duplicate", "process_count": 3}},
    )
    report["route_evidence"]["servers"]["memory"].update(
        {
            "callable_status": "absent",
            "process_classification": "duplicate",
            "process_count": 3,
        }
    )

    route_check = mod._check_required_routes(report, ["memory"])[0]
    process_check = mod._check_process_hygiene(report, fail_duplicates=False)[0]

    assert route_check.id == "mcp.memory"
    assert route_check.status == "FAIL"
    assert "missing route/callability proof" in route_check.detail
    assert process_check.id == "process.memory"
    assert process_check.status == "WARN"
    assert process_check.severity == "advisory"


def test_major_mcp_exposure_check_is_advisory_warn() -> None:
    check = mod._check_major_mcp_exposure(
        {
            "available": True,
            "readiness_status": "FAIL",
            "counts": {"GREEN": 1, "YELLOW": 2, "RED": 1},
        }
    )

    assert check.id == "mcp.major_exposure"
    assert check.status == "WARN"
    assert check.severity == "advisory"


def test_build_readiness_report_includes_major_mcp_exposure(monkeypatch, tmp_path: Path) -> None:
    for path in (
        "docs/codex-primary-execution.md",
        "scripts/governance/verify_codex_primary.py",
        "scripts/governance/verify_codex_run_receipt.py",
        "scripts/governance/audit_codex_mcp_transports.py",
        "scripts/governance/check_windows_path_budget.py",
    ):
        target = tmp_path / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("", encoding="utf-8")
    monkeypatch.setattr(mod, "_run_git_status", lambda root: (0, "", ""))
    monkeypatch.setattr(mod, "find_dirty_protected_worktrees", lambda root, skip_paths=(): [])
    monkeypatch.setenv("CODEX_MCP_VECTOR_DB_SEMANTIC_STATE", "ready")
    monkeypatch.setattr(
        mod.audit_codex_mcp_transports,
        "build_report",
        lambda route_contract=None: _transport_report(
            {
                "memory": "CALLABLE",
                "GitKraken": "SUBSTITUTE_CALLABLE",
                "vector_db": "CALLABLE",
                "adg_sqlite": "CALLABLE",
            }
        ),
    )
    exposure = {
        "available": True,
        "readiness_status": "PASS",
        "counts": {"GREEN": 8, "YELLOW": 0, "RED": 0},
        "servers": {},
    }
    monkeypatch.setattr(mod, "_build_major_mcp_exposure_summary", lambda: exposure)
    monkeypatch.setattr(mod, "_check_searxng", lambda restart=False, set_restart_policy=False: mod.ReadinessCheck("docker.searxng", "PASS", "advisory", "ok"))

    report = mod.build_readiness_report(tmp_path)

    assert report["status"] == "PASS"
    assert report["transport_summary"]["major_mcp_exposure"] == exposure
    assert any(check["id"] == "mcp.major_exposure" for check in report["checks"])
    assert any(check["id"] == "docker.searxng" for check in report["checks"])


def test_searxng_check_passes_when_report_ready(monkeypatch) -> None:
    report = mod.ensure_searxng_readiness.SearxngReadinessReport(status="PASS")
    report.running = True
    report.restart_policy = "unless-stopped"
    report.json_search_ready = True
    monkeypatch.setattr(mod.ensure_searxng_readiness, "build_report", lambda **kwargs: report)

    check = mod._check_searxng()

    assert check.id == "docker.searxng"
    assert check.status == "PASS"


def test_searxng_check_warns_when_not_ready(monkeypatch) -> None:
    report = mod.ensure_searxng_readiness.SearxngReadinessReport(status="FAIL")
    report.running = True
    report.restart_policy = "no"
    report.json_search_ready = False
    monkeypatch.setattr(mod.ensure_searxng_readiness, "build_report", lambda **kwargs: report)

    check = mod._check_searxng()

    assert check.status == "WARN"
    assert check.severity == "advisory"


def test_summarize_prefers_failure_over_warning() -> None:
    checks = [
        mod.ReadinessCheck("a", "WARN", "advisory", "warn"),
        mod.ReadinessCheck("b", "FAIL", "critical", "fail"),
    ]

    assert mod.summarize(checks) == "FAIL"


def test_protected_worktree_hygiene_warns_when_dirty(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(mod, "find_dirty_protected_worktrees", lambda root, skip_paths=(): ["issue"])
    monkeypatch.setattr(mod, "summarize_dirty_worktrees", lambda issues: "main @ /tmp/repo: docs/foo.md")

    check = mod._check_protected_worktree_hygiene(tmp_path, False)
    strict = mod._check_protected_worktree_hygiene(tmp_path, True)

    assert check.status == "WARN"
    assert check.id == "git.protected_worktrees"
    assert "main @ /tmp/repo" in check.detail
    assert strict.status == "FAIL"


def test_git_publication_mode_skips_mcp_route_checks(monkeypatch, tmp_path: Path) -> None:
    def fail_if_called(route_contract=None):
        raise AssertionError("MCP transport audit should not run in git-publication mode")

    monkeypatch.setattr(mod.audit_codex_mcp_transports, "build_report", fail_if_called)
    monkeypatch.setattr(
        mod.codex_publication_audit,
        "build_publication_audit",
        lambda root, fetch=True, require_single_main_worktree=False, require_pr_flow=False: {
            "current_worktree": {"dirty": False, "conflicted": False, "raw": ""},
            "dirty_protected_worktrees": [],
            "dirty_protected_summary": "",
            "refs": {"origin_main_equals_github_main": True},
            "fetch": {"ok": True, "stdout": "", "stderr": ""},
            "unmerged_branches": [],
            "single_main_worktree": {"required": require_single_main_worktree, "issues": [], "summary": ""},
            "pr_flow": {"required": require_pr_flow, "clean": True, "issues": []},
        },
    )
    for path in (
        "docs/codex-primary-execution.md",
        "scripts/governance/verify_codex_primary.py",
        "scripts/governance/verify_codex_run_receipt.py",
        "scripts/governance/audit_codex_mcp_transports.py",
        "scripts/governance/check_windows_path_budget.py",
    ):
        target = tmp_path / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("", encoding="utf-8")

    report = mod.build_readiness_report(tmp_path, git_publication=True)

    assert report["mode"] == "git-publication"
    assert report["status"] == "PASS"
    assert not any(check["id"].startswith("mcp.") for check in report["checks"])


def test_git_publication_strict_single_main_fails(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        mod.codex_publication_audit,
        "build_publication_audit",
        lambda root, fetch=True, require_single_main_worktree=False, require_pr_flow=False: {
            "current_worktree": {"dirty": False, "conflicted": False, "raw": ""},
            "dirty_protected_worktrees": [],
            "dirty_protected_summary": "",
            "refs": {"origin_main_equals_github_main": True},
            "fetch": {"ok": True, "stdout": "", "stderr": ""},
            "unmerged_branches": [],
            "single_main_worktree": {
                "required": require_single_main_worktree,
                "issues": [{"code": "worktree_count", "detail": "expected=1 actual=2"}],
                "summary": "- worktree_count: expected=1 actual=2",
            },
            "pr_flow": {"required": require_pr_flow, "clean": True, "issues": []},
        },
    )
    for path in (
        "docs/codex-primary-execution.md",
        "scripts/governance/verify_codex_primary.py",
        "scripts/governance/verify_codex_run_receipt.py",
        "scripts/governance/audit_codex_mcp_transports.py",
        "scripts/governance/check_windows_path_budget.py",
    ):
        target = tmp_path / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("", encoding="utf-8")

    report = mod.build_readiness_report(
        tmp_path,
        git_publication=True,
        require_single_main_worktree=True,
    )

    assert report["status"] == "FAIL"
    check = next(check for check in report["checks"] if check["id"] == "git.publication.single_main_worktree")
    assert check["status"] == "FAIL"
    assert "expected=1 actual=2" in check["detail"]


def test_git_publication_require_pr_flow_fails_on_direct_push_contract(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        mod.codex_publication_audit,
        "build_publication_audit",
        lambda root, fetch=True, require_single_main_worktree=False, require_pr_flow=False: {
            "current_worktree": {"dirty": False, "conflicted": False, "raw": ""},
            "dirty_protected_worktrees": [],
            "dirty_protected_summary": "",
            "refs": {"origin_main_equals_github_main": True},
            "fetch": {"ok": True, "stdout": "", "stderr": ""},
            "unmerged_branches": [],
            "single_main_worktree": {"required": require_single_main_worktree, "issues": [], "summary": ""},
            "pr_flow": {
                "required": require_pr_flow,
                "clean": False,
                "issues": [
                    {"code": "allow_direct_main_push", "detail": "expected=false actual=True"},
                    {"code": "require_github_ci_green", "detail": "expected=true actual=False"},
                    {"code": "allow_bypass_merge", "detail": "expected=false actual=True"},
                ],
            },
        },
    )
    for path in (
        "docs/codex-primary-execution.md",
        "scripts/governance/verify_codex_primary.py",
        "scripts/governance/verify_codex_run_receipt.py",
        "scripts/governance/audit_codex_mcp_transports.py",
        "scripts/governance/check_windows_path_budget.py",
    ):
        target = tmp_path / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("", encoding="utf-8")

    report = mod.build_readiness_report(
        tmp_path,
        git_publication=True,
        require_pr_flow=True,
    )

    assert report["status"] == "FAIL"
    check = next(check for check in report["checks"] if check["id"] == "git.publication.pr_flow_contract")
    assert check["status"] == "FAIL"
    assert "allow_direct_main_push" in check["detail"]
    assert "require_github_ci_green" in check["detail"]
    assert "allow_bypass_merge" in check["detail"]
