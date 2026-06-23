"""Preflight Codex primary execution readiness.

The check is read-only. It composes repo anchors, git state, MCP transport
evidence, process hygiene, and ADG fallback state before expensive Codex runs.
Shell scripts cannot directly inspect the live Codex MCP namespace, so callable
proof is supplied through the existing CODEX_MCP_CALLABLE_* environment values
or a route contract consumed by audit_codex_mcp_transports.py.

The ``--git-publication`` mode is narrower: it runs the git publication safety
gate used before Codex main-publish automation and intentionally excludes MCP
route/process checks so branch/worktree hazards are not masked by runtime noise.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
GOVERNANCE_DIR = Path(__file__).resolve().parent
MCP_TOOL_EXPOSURE_AUDIT_PATH = REPO_ROOT / ".codex" / "governance" / "scripts" / "mcp_tool_exposure_audit.py"
if str(GOVERNANCE_DIR) not in sys.path:
    sys.path.insert(0, str(GOVERNANCE_DIR))

import audit_codex_mcp_transports  # noqa: E402
import codex_publication_audit  # noqa: E402
import ensure_searxng_readiness  # noqa: E402
from worktree_hygiene import find_dirty_protected_worktrees, summarize_dirty_worktrees  # noqa: E402

DEFAULT_REQUIRED_CALLABLE_ROUTES = ("memory", "GitKraken")
CALLABLE_CLASSIFICATIONS = {"CALLABLE", "PLUGIN_SUBSTITUTE", "SUBSTITUTE_CALLABLE"}
DUPLICATE_PROCESS_CLASSIFICATIONS = {"duplicate", "duplicate_launch_tree"}
VECTOR_SEMANTIC_READY_VALUES = {"ready", "healthy", "true", "1", "semantic_ready"}
VECTOR_SEMANTIC_NOT_READY_VALUES = {"metadata_only", "loading", "timeout", "unavailable", "false", "0"}


@dataclass(frozen=True)
class ReadinessCheck:
    id: str
    status: str
    severity: str
    summary: str
    detail: str = ""


def _run_git_status(root: Path) -> tuple[int, str, str]:
    proc = subprocess.run(
        ["git", "status", "--short"],
        cwd=str(root),
        capture_output=True,
        text=True,
        timeout=30,
    )
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def _latest_adg_snapshot(root: Path) -> Path | None:
    adg_dir = root / "artifacts" / "adg"
    if not adg_dir.exists():
        return None
    candidates = sorted(adg_dir.glob("adg_indexed_*.sqlite"), key=lambda p: (p.stat().st_mtime, p.name), reverse=True)
    return candidates[0] if candidates else None


def _check_contract_files(root: Path) -> list[ReadinessCheck]:
    required = [
        "docs/codex-primary-execution.md",
        "scripts/governance/verify_codex_primary.py",
        "scripts/governance/verify_codex_run_receipt.py",
        "scripts/governance/audit_codex_mcp_transports.py",
        "scripts/governance/check_windows_path_budget.py",
    ]
    missing = [path for path in required if not (root / path).exists()]
    if missing:
        return [
            ReadinessCheck(
                "codex.contract_files",
                "FAIL",
                "critical",
                "Codex primary contract files are missing.",
                ", ".join(missing),
            )
    ]
    return [ReadinessCheck("codex.contract_files", "PASS", "critical", "Codex primary contract files are present.")]


def _check_git_state(root: Path, require_clean: bool) -> ReadinessCheck:
    returncode, stdout, stderr = _run_git_status(root)
    if returncode != 0:
        return ReadinessCheck("git.status", "FAIL", "critical", "git status failed.", stderr)
    if stdout:
        status = "FAIL" if require_clean else "WARN"
        severity = "critical" if require_clean else "advisory"
        return ReadinessCheck("git.clean", status, severity, "Working tree has uncommitted changes.", stdout[:2000])
    return ReadinessCheck("git.clean", "PASS", "critical", "Working tree is clean.")


def _check_protected_worktree_hygiene(root: Path, require_clean: bool) -> ReadinessCheck:
    issues = find_dirty_protected_worktrees(root, skip_paths=(root,))
    if issues:
        status = "FAIL" if require_clean else "WARN"
        severity = "critical" if require_clean else "advisory"
        return ReadinessCheck(
            "git.protected_worktrees",
            status,
            severity,
            "Protected worktrees have uncommitted changes.",
            summarize_dirty_worktrees(issues),
        )
    return ReadinessCheck(
        "git.protected_worktrees",
        "PASS",
        "advisory",
        "Protected worktrees are clean.",
    )


def _checks_from_publication_audit(audit: dict[str, Any]) -> list[ReadinessCheck]:
    checks: list[ReadinessCheck] = []
    current = audit.get("current_worktree", {})
    checks.append(
        ReadinessCheck(
            "git.publication.current_worktree",
            "FAIL" if current.get("dirty") else "PASS",
            "critical",
            "Current publication worktree is clean." if not current.get("dirty") else "Current publication worktree has uncommitted changes.",
            str(current.get("raw", "")),
        )
    )
    checks.append(
        ReadinessCheck(
            "git.publication.conflicts",
            "FAIL" if current.get("conflicted") else "PASS",
            "critical",
            "Current publication worktree has no conflicted paths." if not current.get("conflicted") else "Current publication worktree has conflicted paths.",
            str(current.get("raw", "")),
        )
    )
    dirty_summary = str(audit.get("dirty_protected_summary") or "")
    checks.append(
        ReadinessCheck(
            "git.publication.protected_worktrees",
            "WARN" if audit.get("dirty_protected_worktrees") else "PASS",
            "advisory" if audit.get("dirty_protected_worktrees") else "critical",
            "Protected worktrees are clean." if not audit.get("dirty_protected_worktrees") else "Protected worktrees have uncommitted changes.",
            dirty_summary,
        )
    )
    refs = audit.get("refs", {})
    checks.append(
        ReadinessCheck(
            "git.publication.origin_vs_github_main",
            "PASS" if refs.get("origin_main_equals_github_main") else "FAIL",
            "critical",
            "origin/main matches GitHub main." if refs.get("origin_main_equals_github_main") else "origin/main does not match GitHub main.",
            json.dumps(refs, sort_keys=True),
        )
    )
    fetch = audit.get("fetch")
    if isinstance(fetch, dict):
        checks.append(
            ReadinessCheck(
                "git.publication.fetch",
                "PASS" if fetch.get("ok") else "FAIL",
                "critical",
                "git fetch origin --prune succeeded." if fetch.get("ok") else "git fetch origin --prune failed.",
                str(fetch.get("stderr") or fetch.get("stdout") or ""),
            )
        )
    unmerged = audit.get("unmerged_branches") or []
    unique_count = 0
    for row in unmerged:
        if isinstance(row, dict):
            unique_count += len(row.get("patch_unique_commits") or [])
    checks.append(
        ReadinessCheck(
            "git.publication.unmerged_branch_audit",
            "WARN" if unmerged else "PASS",
            "advisory",
            "Local branches not merged to origin/main were audited." if unmerged else "No local branches are unmerged from origin/main.",
            f"branches={len(unmerged)} patch_unique_commits={unique_count}; branch closeout requires ancestry containment, not patch equivalence",
        )
    )
    single_main = audit.get("single_main_worktree") or {}
    single_main_issues = single_main.get("issues") or []
    single_main_required = bool(single_main.get("required"))
    checks.append(
        ReadinessCheck(
            "git.publication.single_main_worktree",
            "FAIL" if single_main_required and single_main_issues else ("WARN" if single_main_issues else "PASS"),
            "critical" if single_main_required or not single_main_issues else "advisory",
            (
                "Local repo is exactly one clean main worktree."
                if not single_main_issues
                else "Local repo is not exactly one clean main worktree."
            ),
            str(single_main.get("summary") or ""),
        )
    )
    pr_flow = audit.get("pr_flow") or {}
    pr_flow_issues = pr_flow.get("issues") or []
    pr_flow_required = bool(pr_flow.get("required"))
    checks.append(
        ReadinessCheck(
            "git.publication.pr_flow_contract",
            "FAIL" if pr_flow_required and pr_flow_issues else "PASS",
            "critical" if pr_flow_required else "advisory",
            (
                "Publication contract requires a GitHub PR flow."
                if not pr_flow_issues
                else "Publication contract does not enforce a GitHub PR flow."
            ),
            json.dumps(pr_flow, sort_keys=True),
        )
    )
    return checks


def _check_env(report: dict[str, Any]) -> list[ReadinessCheck]:
    checks: list[ReadinessCheck] = []
    env = report.get("env", {})
    for key in ("AGENTIC_REPO_ROOT", "ADG_REDIS_URL"):
        state = env.get(key, {})
        if state.get("state") == "set" and not state.get("has_unresolved_placeholder"):
            checks.append(ReadinessCheck(f"env.{key}", "PASS", "critical", f"{key} is set."))
        else:
            checks.append(ReadinessCheck(f"env.{key}", "FAIL", "critical", f"{key} is not ready.", json.dumps(state, sort_keys=True)))
    pytest_state = env.get("PYTEST_DISABLE_PLUGIN_AUTOLOAD", {})
    if pytest_state.get("state") == "unset":
        checks.append(ReadinessCheck("env.PYTEST_DISABLE_PLUGIN_AUTOLOAD", "PASS", "critical", "Pytest plugin autoload is enabled."))
    else:
        checks.append(
            ReadinessCheck(
                "env.PYTEST_DISABLE_PLUGIN_AUTOLOAD",
                "FAIL",
                "critical",
                "PYTEST_DISABLE_PLUGIN_AUTOLOAD must be unset for this repo.",
                json.dumps(pytest_state, sort_keys=True),
            )
        )
    return checks


def _check_required_routes(report: dict[str, Any], required_routes: Sequence[str]) -> list[ReadinessCheck]:
    route_evidence = report.get("route_evidence", {})
    servers = route_evidence.get("servers", {}) if isinstance(route_evidence, dict) else {}
    checks: list[ReadinessCheck] = []
    if not route_evidence.get("available"):
        return [
            ReadinessCheck(
                "mcp.route_contract",
                "FAIL",
                "critical",
                "No Codex MCP route contract evidence is available.",
                str(route_evidence.get("reason", "")),
            )
        ]
    for server_id in required_routes:
        state = servers.get(server_id)
        if not isinstance(state, dict):
            checks.append(ReadinessCheck(f"mcp.{server_id}", "FAIL", "critical", "Required route is absent from route evidence."))
            continue
        classification = str(state.get("classification", ""))
        if classification in CALLABLE_CLASSIFICATIONS:
            checks.append(ReadinessCheck(f"mcp.{server_id}", "PASS", "critical", f"{server_id} is callable in Codex.", classification))
        else:
            checks.append(
                ReadinessCheck(
                    f"mcp.{server_id}",
                    "FAIL",
                    "critical",
                    f"{server_id} is missing Codex route/callability proof.",
                    _route_failure_detail(server_id, state),
                )
            )
    return checks


def _route_failure_detail(server_id: str, state: dict[str, Any]) -> str:
    """Explain route proof failures without conflating them with process hygiene."""
    detail = dict(state)
    detail["blocker"] = "missing route/callability proof"
    detail["why"] = (
        "MCP process presence only proves startup. It does not prove the active "
        "Codex host exposes a callable tool route."
    )
    detail["process_hygiene"] = "Duplicate process cohorts are reported separately under process.* checks."
    detail["unblock"] = (
        f"Prove a live callable route for {server_id} in the active Codex host, "
        f"or set CODEX_MCP_CALLABLE_{server_id.upper()}=healthy only after that API-level proof. "
        "If Codex Desktop exposes no callable API for this server in this session, keep this check failing."
    )
    return json.dumps(detail, sort_keys=True)


def _check_vector_semantic_guard(required_routes: Sequence[str]) -> ReadinessCheck | None:
    if "vector_db" not in required_routes:
        return None
    import os

    raw = os.environ.get("CODEX_MCP_VECTOR_DB_SEMANTIC_STATE", "").strip().lower()
    if raw in VECTOR_SEMANTIC_READY_VALUES:
        return ReadinessCheck(
            "mcp.vector_db.semantic",
            "PASS",
            "critical",
            "vector_db semantic readiness is explicitly proven.",
            raw,
        )
    if raw in VECTOR_SEMANTIC_NOT_READY_VALUES:
        return ReadinessCheck(
            "mcp.vector_db.semantic",
            "FAIL",
            "critical",
            "vector_db is callable but semantic readiness is not proven ready.",
            f"CODEX_MCP_VECTOR_DB_SEMANTIC_STATE={raw}",
        )
    return ReadinessCheck(
        "mcp.vector_db.semantic",
        "WARN",
        "critical",
        "vector_db semantic readiness was not supplied; stats-only MCP proof is not semantic readiness.",
        "Set CODEX_MCP_VECTOR_DB_SEMANTIC_STATE=ready only after a fast health_snapshot/readiness probe proves semantic_ready=true.",
    )


def _check_adg(report: dict[str, Any], root: Path, allow_sqlite_fallback: bool) -> ReadinessCheck:
    servers = report.get("route_evidence", {}).get("servers", {})
    adg_state = servers.get("adg_sqlite", {}) if isinstance(servers, dict) else {}
    classification = str(adg_state.get("classification", ""))
    if classification in CALLABLE_CLASSIFICATIONS:
        return ReadinessCheck("mcp.adg_sqlite", "PASS", "critical", "ADG MCP is callable in Codex.", classification)
    snapshot = _latest_adg_snapshot(root)
    primary_root = Path(str(report.get("primary_root", ""))) if report.get("primary_root") else None
    if snapshot is None and primary_root and primary_root != root:
        snapshot = _latest_adg_snapshot(primary_root)
    if allow_sqlite_fallback and snapshot:
        try:
            detail = str(snapshot.relative_to(root))
        except ValueError:
            detail = str(snapshot)
        return ReadinessCheck(
            "mcp.adg_sqlite",
            "WARN",
            "critical",
            "ADG MCP is not callable; direct SQLite fallback is available.",
            detail,
        )
    return ReadinessCheck(
        "mcp.adg_sqlite",
        "FAIL",
        "critical",
        "ADG MCP is not callable and no acceptable SQLite fallback was found.",
        json.dumps(adg_state, sort_keys=True),
    )


def _check_process_hygiene(report: dict[str, Any], fail_duplicates: bool) -> list[ReadinessCheck]:
    servers = report.get("processes", {}).get("servers", {})
    checks: list[ReadinessCheck] = []
    for server_id, state in servers.items():
        classification = str(state.get("classification", "none"))
        if classification in DUPLICATE_PROCESS_CLASSIFICATIONS:
            status = "FAIL" if fail_duplicates else "WARN"
            severity = "critical" if fail_duplicates else "advisory"
            checks.append(
                ReadinessCheck(
                    f"process.{server_id}",
                    status,
                    severity,
                    f"{server_id} has duplicate MCP process cohorts.",
                    f"process_count={state.get('process_count')} classification={classification}",
                )
            )
    if not checks:
        checks.append(ReadinessCheck("process.duplicates", "PASS", "advisory", "No duplicate MCP process cohorts detected."))
    return checks


def _load_mcp_tool_exposure_audit() -> Any:
    spec = importlib.util.spec_from_file_location("_codex_readiness_mcp_tool_exposure_audit", MCP_TOOL_EXPOSURE_AUDIT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load MCP exposure audit at {MCP_TOOL_EXPOSURE_AUDIT_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _build_major_mcp_exposure_summary() -> dict[str, Any]:
    try:
        module = _load_mcp_tool_exposure_audit()
        results = module.audit()
    except Exception as exc:  # pragma: no cover - defensive preflight boundary
        return {
            "available": False,
            "readiness_status": "WARN",
            "reason": f"{type(exc).__name__}: {exc}",
        }

    counts = {"GREEN": 0, "YELLOW": 0, "RED": 0}
    servers: dict[str, Any] = {}
    for result in results:
        counts[result.status] = counts.get(result.status, 0) + 1
        servers[result.server_id] = {
            "status": result.status,
            "declared": result.declared,
            "host_exposed": result.host_exposed,
            "native_ok": result.native_ok,
            "reasons": list(result.reasons),
        }
    readiness_status = "FAIL" if counts.get("RED") else ("WARN" if counts.get("YELLOW") else "PASS")
    return {
        "available": True,
        "readiness_status": readiness_status,
        "counts": counts,
        "servers": servers,
    }


def _check_major_mcp_exposure(summary: dict[str, Any]) -> ReadinessCheck:
    if not summary.get("available"):
        return ReadinessCheck(
            "mcp.major_exposure",
            "WARN",
            "advisory",
            "Major MCP exposure audit could not run.",
            str(summary.get("reason", "")),
        )
    readiness_status = str(summary.get("readiness_status", "WARN"))
    if readiness_status == "PASS":
        return ReadinessCheck(
            "mcp.major_exposure",
            "PASS",
            "advisory",
            "Major MCP exposure audit is green.",
            json.dumps(summary.get("counts", {}), sort_keys=True),
        )
    return ReadinessCheck(
        "mcp.major_exposure",
        "WARN",
        "advisory",
        "Major MCP exposure audit found unproven or unavailable tools.",
        json.dumps(summary.get("counts", {}), sort_keys=True),
    )


def _check_searxng(
    *,
    restart: bool = False,
    set_restart_policy: bool = False,
) -> ReadinessCheck:
    try:
        report = ensure_searxng_readiness.build_report(
            restart=restart,
            set_restart_policy=set_restart_policy,
            restart_wait_seconds=2.0,
        )
    except ensure_searxng_readiness.DockerCommandError as exc:
        return ReadinessCheck(
            "docker.searxng",
            "WARN",
            "advisory",
            "SearXNG Docker readiness could not be proven.",
            str(exc),
        )
    detail = json.dumps(asdict(report), sort_keys=True)
    if report.status == "PASS":
        return ReadinessCheck(
            "docker.searxng",
            "PASS",
            "advisory",
            "SearXNG Docker search is running, restart-managed, and JSON-ready.",
            detail,
        )
    return ReadinessCheck(
        "docker.searxng",
        "WARN",
        "advisory",
        "SearXNG Docker search is not fully ready for apps_research.",
        detail,
    )


def summarize(checks: Sequence[ReadinessCheck]) -> str:
    if any(check.status == "FAIL" for check in checks):
        return "FAIL"
    if any(check.status == "WARN" for check in checks):
        return "WARN"
    return "PASS"


def build_readiness_report(
    root: Path = REPO_ROOT,
    *,
    require_clean: bool = False,
    git_publication: bool = False,
    require_single_main_worktree: bool = False,
    require_pr_flow: bool = False,
    fail_duplicate_processes: bool = False,
    required_callable_routes: Sequence[str] = DEFAULT_REQUIRED_CALLABLE_ROUTES,
    allow_adg_sqlite_fallback: bool = False,
    route_contract: Path | None = None,
    check_searxng: bool = True,
    restart_searxng: bool = False,
) -> dict[str, Any]:
    if git_publication:
        audit = codex_publication_audit.build_publication_audit(
            root,
            fetch=True,
            require_single_main_worktree=require_single_main_worktree,
            require_pr_flow=require_pr_flow,
        )
        checks = [*_check_contract_files(root), *_checks_from_publication_audit(audit)]
        return {
            "schema_version": "codex-readiness/v1",
            "mode": "git-publication",
            "repo_root": str(root),
            "status": summarize(checks),
            "checks": [asdict(check) for check in checks],
            "publication_audit": audit,
        }

    transport_report = audit_codex_mcp_transports.build_report(route_contract)
    exposure_summary = _build_major_mcp_exposure_summary()
    checks: list[ReadinessCheck] = []
    checks.extend(_check_contract_files(root))
    checks.append(_check_git_state(root, require_clean))
    checks.append(_check_protected_worktree_hygiene(root, require_clean))
    checks.extend(_check_env(transport_report))
    checks.extend(_check_required_routes(transport_report, required_callable_routes))
    vector_guard = _check_vector_semantic_guard(required_callable_routes)
    if vector_guard is not None:
        checks.append(vector_guard)
    checks.append(_check_adg(transport_report, root, allow_adg_sqlite_fallback))
    checks.extend(_check_process_hygiene(transport_report, fail_duplicate_processes))
    checks.append(_check_major_mcp_exposure(exposure_summary))
    if check_searxng:
        checks.append(
            _check_searxng(
                restart=restart_searxng,
                set_restart_policy=restart_searxng,
            )
        )

    return {
        "schema_version": "codex-readiness/v1",
        "repo_root": str(root),
        "status": summarize(checks),
        "checks": [asdict(check) for check in checks],
        "transport_summary": {
            "route_counts": transport_report.get("route_evidence", {}).get("counts", {}),
            "route_contract_path": transport_report.get("route_contract_path"),
            "major_mcp_exposure": exposure_summary,
        },
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    parser.add_argument("--require-clean-worktree", action="store_true", help="Fail when git status is dirty")
    parser.add_argument(
        "--git-publication",
        action="store_true",
        help="Run only git publication safety checks and skip MCP route/process readiness.",
    )
    parser.add_argument(
        "--require-single-main-worktree",
        action="store_true",
        help="In --git-publication mode, fail unless the local repo is one clean main worktree.",
    )
    parser.add_argument(
        "--require-pr-flow",
        action="store_true",
        help="In --git-publication mode, fail unless the on-demand PR publisher forbids direct main push.",
    )
    parser.add_argument("--fail-duplicate-processes", action="store_true", help="Fail on duplicate MCP process cohorts")
    parser.add_argument(
        "--require-callable-route",
        action="append",
        dest="required_callable_routes",
        help="Additional or replacement required callable MCP route; repeatable.",
    )
    parser.add_argument(
        "--no-default-callable-routes",
        action="store_true",
        help="Only require routes supplied by --require-callable-route.",
    )
    parser.add_argument(
        "--allow-adg-sqlite-fallback",
        action="store_true",
        help="Allow direct SQLite fallback when ADG MCP is not callable.",
    )
    parser.add_argument(
        "--no-adg-sqlite-fallback",
        action="store_true",
        help="Compatibility alias for strict ADG callable mode.",
    )
    parser.add_argument("--route-contract", type=Path, help="Optional route contract JSON")
    parser.add_argument(
        "--skip-searxng",
        action="store_true",
        help="Skip advisory SearXNG Docker readiness check.",
    )
    parser.add_argument(
        "--restart-searxng",
        action="store_true",
        help="Start/restart agentic_searxng and set restart policy while checking readiness.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    required_routes: tuple[str, ...]
    supplied = tuple(args.required_callable_routes or ())
    if args.no_default_callable_routes:
        required_routes = supplied
    else:
        required_routes = DEFAULT_REQUIRED_CALLABLE_ROUTES + supplied
    allow_adg_sqlite_fallback = bool(args.allow_adg_sqlite_fallback and not args.no_adg_sqlite_fallback)
    report = build_readiness_report(
        require_clean=args.require_clean_worktree,
        git_publication=args.git_publication,
        require_single_main_worktree=args.require_single_main_worktree,
        require_pr_flow=args.require_pr_flow,
        fail_duplicate_processes=args.fail_duplicate_processes,
        required_callable_routes=required_routes,
        allow_adg_sqlite_fallback=allow_adg_sqlite_fallback,
        route_contract=args.route_contract,
        check_searxng=not args.skip_searxng,
        restart_searxng=args.restart_searxng,
    )
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"Codex readiness: {report['status']}")
        for check in report["checks"]:
            print(f"- {check['status']} {check['id']}: {check['summary']}")
            if check.get("detail"):
                print(f"  {check['detail']}")
    return 1 if report["status"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
