"""Preflight Codex primary execution readiness.

The check is read-only. It composes repo anchors, git state, MCP transport
evidence, process hygiene, and ADG fallback state before expensive Codex runs.
Shell scripts cannot directly inspect the live Codex MCP namespace, so callable
proof is supplied through the existing CODEX_MCP_CALLABLE_* environment values
or a route contract consumed by audit_codex_mcp_transports.py.
"""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
GOVERNANCE_DIR = Path(__file__).resolve().parent
if str(GOVERNANCE_DIR) not in sys.path:
    sys.path.insert(0, str(GOVERNANCE_DIR))

import audit_codex_mcp_transports  # noqa: E402


DEFAULT_REQUIRED_CALLABLE_ROUTES = ("memory", "GitKraken", "vector_db")
CALLABLE_CLASSIFICATIONS = {"CALLABLE", "PLUGIN_SUBSTITUTE", "SUBSTITUTE_CALLABLE"}
DUPLICATE_PROCESS_CLASSIFICATIONS = {"duplicate", "duplicate_launch_tree"}


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
                    f"{server_id} is not proven callable for Codex primary execution.",
                    json.dumps(state, sort_keys=True),
                )
            )
    return checks


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
    fail_duplicate_processes: bool = False,
    required_callable_routes: Sequence[str] = DEFAULT_REQUIRED_CALLABLE_ROUTES,
    allow_adg_sqlite_fallback: bool = True,
    route_contract: Path | None = None,
) -> dict[str, Any]:
    transport_report = audit_codex_mcp_transports.build_report(route_contract)
    checks: list[ReadinessCheck] = []
    checks.extend(_check_contract_files(root))
    checks.append(_check_git_state(root, require_clean))
    checks.extend(_check_env(transport_report))
    checks.extend(_check_required_routes(transport_report, required_callable_routes))
    checks.append(_check_adg(transport_report, root, allow_adg_sqlite_fallback))
    checks.extend(_check_process_hygiene(transport_report, fail_duplicate_processes))

    return {
        "schema_version": "codex-readiness/v1",
        "repo_root": str(root),
        "status": summarize(checks),
        "checks": [asdict(check) for check in checks],
        "transport_summary": {
            "route_counts": transport_report.get("route_evidence", {}).get("counts", {}),
            "route_contract_path": transport_report.get("route_contract_path"),
        },
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    parser.add_argument("--require-clean-worktree", action="store_true", help="Fail when git status is dirty")
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
    parser.add_argument("--no-adg-sqlite-fallback", action="store_true", help="Fail if ADG MCP is not callable")
    parser.add_argument("--route-contract", type=Path, help="Optional route contract JSON")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    required_routes: tuple[str, ...]
    supplied = tuple(args.required_callable_routes or ())
    if args.no_default_callable_routes:
        required_routes = supplied
    else:
        required_routes = DEFAULT_REQUIRED_CALLABLE_ROUTES + supplied
    report = build_readiness_report(
        require_clean=args.require_clean_worktree,
        fail_duplicate_processes=args.fail_duplicate_processes,
        required_callable_routes=required_routes,
        allow_adg_sqlite_fallback=not args.no_adg_sqlite_fallback,
        route_contract=args.route_contract,
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
