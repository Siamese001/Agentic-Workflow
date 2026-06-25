"""Ensure the local SearXNG container is usable for apps_research.

This governance CLI delegates to the app-owned SearXNG readiness helper so
operator checks and product runtime share the same Docker warmup contract.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict

from apps_research.integrations.searxng_readiness import (
    DEFAULT_BASE_URL,
    DEFAULT_CONTAINER_NAME,
    DockerCommandError,
    SearxngReadinessReport,
    StepResult,
    build_report,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    parser.add_argument("--container-name", default=DEFAULT_CONTAINER_NAME)
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--restart", action="store_true", help="Start/restart the container when readiness fails")
    parser.add_argument(
        "--force-restart",
        action="store_true",
        help="Restart the container before probing JSON search readiness",
    )
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
            force_restart=args.force_restart,
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
