"""Ensure the local SearXNG container is usable for apps_research.

The check is intentionally narrow: it manages the repo-standard local
``agentic_searxng`` container when Docker is available, verifies its restart
policy, and probes JSON search output. It does not create a missing container,
because pulling images or inventing port bindings is a larger operator choice.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from dataclasses import asdict, dataclass, field
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

DEFAULT_CONTAINER_NAME = "agentic_searxng"
DEFAULT_BASE_URL = "http://localhost:8080"
ACCEPTED_RESTART_POLICIES = {"always", "unless-stopped"}


@dataclass
class StepResult:
    step: str
    status: str
    detail: str = ""


@dataclass
class SearxngReadinessReport:
    schema_version: str = "searxng-readiness/v1"
    container_name: str = DEFAULT_CONTAINER_NAME
    base_url: str = DEFAULT_BASE_URL
    status: str = "FAIL"
    running: bool = False
    restart_policy: str = ""
    json_search_ready: bool = False
    restarted: bool = False
    restart_policy_updated: bool = False
    steps: list[StepResult] = field(default_factory=list)


class DockerCommandError(RuntimeError):
    """Raised when a docker command fails."""


def _run_docker(argv: list[str], *, timeout: int = 30) -> subprocess.CompletedProcess[str]:
    try:
        proc = subprocess.run(
            ["docker", *argv],
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=False,
        )
    except FileNotFoundError as exc:
        raise DockerCommandError("docker executable not found") from exc
    except subprocess.TimeoutExpired as exc:
        raise DockerCommandError(f"docker {' '.join(argv)} timed out after {timeout}s") from exc
    if proc.returncode != 0:
        msg = (proc.stderr or proc.stdout or "").strip()
        raise DockerCommandError(msg or f"docker {' '.join(argv)} failed with rc={proc.returncode}")
    return proc


def _inspect_container(container_name: str) -> dict[str, Any] | None:
    try:
        proc = _run_docker(["inspect", container_name])
    except DockerCommandError:
        return None
    try:
        loaded = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise DockerCommandError(f"docker inspect returned invalid JSON: {exc}") from exc
    if not isinstance(loaded, list) or not loaded:
        return None
    first = loaded[0]
    return first if isinstance(first, dict) else None


def _container_running(inspected: dict[str, Any] | None) -> bool:
    state = inspected.get("State", {}) if isinstance(inspected, dict) else {}
    return bool(state.get("Running"))


def _restart_policy(inspected: dict[str, Any] | None) -> str:
    host = inspected.get("HostConfig", {}) if isinstance(inspected, dict) else {}
    policy = host.get("RestartPolicy", {}) if isinstance(host, dict) else {}
    return str(policy.get("Name") or "")


def _probe_json_search(base_url: str, *, timeout: int = 20) -> tuple[bool, str]:
    url = base_url.rstrip("/") + "/search?" + urlencode({"q": "Anthropic Claude AWS", "format": "json"})
    request = Request(url, headers={"User-Agent": "agentic-workflow-codex-readiness/1.0"})
    try:
        with urlopen(request, timeout=timeout) as response:
            body = response.read(2_000_000)
    except HTTPError as exc:
        return False, f"HTTP {exc.code}: {exc.reason}"
    except URLError as exc:
        return False, f"URL error: {exc.reason}"
    except TimeoutError:
        return False, f"timed out after {timeout}s"
    try:
        parsed = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return False, f"invalid JSON response: {exc}"
    if not isinstance(parsed, dict):
        return False, "JSON response was not an object"
    if "results" not in parsed:
        return False, "JSON response missing results"
    return True, f"results={len(parsed.get('results') or [])}"


def build_report(
    *,
    container_name: str = DEFAULT_CONTAINER_NAME,
    base_url: str = DEFAULT_BASE_URL,
    restart: bool = False,
    set_restart_policy: bool = False,
    probe_timeout: int = 20,
    restart_wait_seconds: float = 8.0,
) -> SearxngReadinessReport:
    report = SearxngReadinessReport(container_name=container_name, base_url=base_url)
    inspected = _inspect_container(container_name)
    if inspected is None:
        report.steps.append(StepResult("inspect", "FAIL", f"container {container_name!r} not found"))
        report.status = "FAIL"
        return report
    report.steps.append(StepResult("inspect", "PASS", "container found"))

    report.running = _container_running(inspected)
    report.restart_policy = _restart_policy(inspected)

    if set_restart_policy and report.restart_policy not in ACCEPTED_RESTART_POLICIES:
        try:
            _run_docker(["update", "--restart", "unless-stopped", container_name])
            report.restart_policy_updated = True
            report.steps.append(StepResult("restart_policy", "PASS", "set to unless-stopped"))
            inspected = _inspect_container(container_name) or inspected
            report.restart_policy = _restart_policy(inspected)
        except DockerCommandError as exc:
            report.steps.append(StepResult("restart_policy", "FAIL", str(exc)))
    elif report.restart_policy in ACCEPTED_RESTART_POLICIES:
        report.steps.append(StepResult("restart_policy", "PASS", report.restart_policy))
    else:
        report.steps.append(StepResult("restart_policy", "WARN", report.restart_policy or "none"))

    if not report.running and restart:
        try:
            _run_docker(["start", container_name])
            report.restarted = True
            report.steps.append(StepResult("start", "PASS", "container started"))
            time.sleep(restart_wait_seconds)
            inspected = _inspect_container(container_name) or inspected
            report.running = _container_running(inspected)
        except DockerCommandError as exc:
            report.steps.append(StepResult("start", "FAIL", str(exc)))
    elif report.running:
        report.steps.append(StepResult("running", "PASS", "container running"))
    else:
        report.steps.append(StepResult("running", "FAIL", "container stopped"))

    ready, detail = _probe_json_search(base_url, timeout=probe_timeout) if report.running else (False, "container not running")
    if not ready and restart and report.running:
        try:
            _run_docker(["restart", container_name])
            report.restarted = True
            report.steps.append(StepResult("restart", "PASS", "restarted after failed JSON probe"))
            time.sleep(restart_wait_seconds)
            ready, detail = _probe_json_search(base_url, timeout=probe_timeout)
        except DockerCommandError as exc:
            report.steps.append(StepResult("restart", "FAIL", str(exc)))
    report.json_search_ready = ready
    report.steps.append(StepResult("json_search", "PASS" if ready else "FAIL", detail))

    policy_ok = report.restart_policy in ACCEPTED_RESTART_POLICIES
    report.status = "PASS" if report.running and report.json_search_ready and policy_ok else "FAIL"
    return report


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    parser.add_argument("--container-name", default=DEFAULT_CONTAINER_NAME)
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--restart", action="store_true", help="Start/restart the container when readiness fails")
    parser.add_argument("--set-restart-policy", action="store_true", help="Set Docker restart policy to unless-stopped")
    parser.add_argument("--probe-timeout", type=int, default=20)
    parser.add_argument("--restart-wait-seconds", type=float, default=8.0)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        report = build_report(
            container_name=args.container_name,
            base_url=args.base_url,
            restart=args.restart,
            set_restart_policy=args.set_restart_policy,
            probe_timeout=args.probe_timeout,
            restart_wait_seconds=args.restart_wait_seconds,
        )
    except DockerCommandError as exc:
        report = SearxngReadinessReport(container_name=args.container_name, base_url=args.base_url)
        report.steps.append(StepResult("docker", "FAIL", str(exc)))
        report.status = "FAIL"
    payload = asdict(report)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"SearXNG readiness: {report.status}")
        for step in report.steps:
            print(f"- {step.status} {step.step}: {step.detail}")
    return 0 if report.status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
