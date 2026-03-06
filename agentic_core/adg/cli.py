"""ADG CLI entry point.

Usage:
    python -m agentic_core.adg.cli scan [--repo-root .] [--commit <sha>] [--diff-files f1 f2]
    python -m agentic_core.adg.cli blast-radius --changed f1 f2 [--repo-root .]

Each invocation prints:
    ADG-DETERMINISM-DIGEST: <sha256_hex>
and exits 0 (pass) or 1 (invariant violations found).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _cmd_scan(args: argparse.Namespace) -> int:
    from agentic_core.adg.ci.invariant_scanner import run_ci_scan

    diff_files = args.diff_files if args.diff_files else None
    report = run_ci_scan(
        repo_root=args.repo_root,
        diff_files=diff_files,
        commit_sha=args.commit or "",
        print_digest=True,
    )
    report.print_summary()
    return report.exit_code()


def _cmd_blast_radius(args: argparse.Namespace) -> int:
    from agentic_core.adg.applications.blast_radius import compute_blast_radius
    from agentic_core.adg.extraction.static_scanner import ADGStaticScanner

    scanner = ADGStaticScanner(repo_root=Path(args.repo_root))
    result = scanner.scan(commit_sha=args.commit or "")
    result.print_digest()

    br = compute_blast_radius(
        changed_files=args.changed or [],
        result=result,
        commit_sha=args.commit or "",
    )
    br.print_summary()
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="adg",
        description="Architecture Dependency Graph CLI",
    )
    parser.add_argument("--repo-root", default=".", help="Path to repo root")
    parser.add_argument("--commit", default="", help="Git commit SHA")

    subparsers = parser.add_subparsers(dest="command")

    scan_p = subparsers.add_parser("scan", help="Run full invariant scan")
    scan_p.add_argument(
        "--diff-files",
        nargs="*",
        metavar="FILE",
        help="Scan only these files (PR diff mode)",
    )

    br_p = subparsers.add_parser("blast-radius", help="Compute blast-radius score")
    br_p.add_argument(
        "--changed",
        nargs="*",
        metavar="FILE",
        help="Changed files for blast-radius computation",
    )

    parsed = parser.parse_args(argv)

    if parsed.command == "scan":
        return _cmd_scan(parsed)
    if parsed.command == "blast-radius":
        return _cmd_blast_radius(parsed)

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
