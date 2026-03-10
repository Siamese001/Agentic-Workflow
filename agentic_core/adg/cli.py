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
    import json
    from pathlib import Path

    from agentic_core.adg.ci.invariant_scanner import run_ci_scan

    diff_files = args.diff_files if args.diff_files else None
    include_tests = not getattr(args, "exclude_tests", False)
    report = run_ci_scan(
        repo_root=args.repo_root,
        diff_files=diff_files,
        commit_sha=args.commit or "",
        print_digest=True,
        include_tests=include_tests,
    )
    report.print_summary()

    # A1: write scan_manifest.json if requested
    if (
        getattr(args, "write_manifest", False)
        and hasattr(report, "scan_result")
        and report.scan_result is not None
    ):
        manifest_path = Path(args.repo_root) / "artifacts" / "adg" / "scan_manifest.json"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(
            json.dumps(report.scan_result.manifest.to_dict(), indent=2),
            encoding="utf-8",
        )
        print(f"ADG-MANIFEST: {manifest_path}")

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


def _cmd_build_artifact(args: argparse.Namespace) -> int:
    import json

    from agentic_core.adg.artifact.builder import build_artifact
    from agentic_core.adg.artifact.serializer import write_artifact
    from agentic_core.adg.extraction.static_scanner import ADGStaticScanner

    repo_root = Path(args.repo_root)
    scanner = ADGStaticScanner(repo_root=repo_root)
    result = scanner.scan(commit_sha=args.commit or "")
    result.print_digest()

    artifact = build_artifact(result, repo_root=repo_root)

    if getattr(args, "output", None):
        out_path = Path(args.output)
    else:
        out_path = repo_root / "artifacts" / "adg" / "adg_canonical_artifact.json"

    write_artifact(artifact, out_path)
    print(f"ADG-ARTIFACT: {out_path}")
    print(f"ADG-ARTIFACT-DIGEST: {artifact.artifact_digest}")
    print(f"ADG-ARTIFACT-ENTITIES: {len(artifact.entities)}")
    print(f"ADG-ARTIFACT-RELATIONS: {len(artifact.relations)}")
    print(f"ADG-ARTIFACT-UNRESOLVED: {len(artifact.unresolved_imports)}")
    return 0


def _cmd_impact(args: argparse.Namespace) -> int:
    import json

    from agentic_core.adg.runtime.cache_loader import load_or_scan
    from tools.change_impact_engine import ChangeImpactEngine

    repo_root = Path(args.repo_root)
    result = load_or_scan(repo_root=str(repo_root))
    engine = ChangeImpactEngine(result, repo_root=repo_root)
    impact = engine.analyze(args.changed or [], include_tests=True)

    if getattr(args, "output", None):
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(impact.to_dict(), indent=2), encoding="utf-8")
        print(f"ADG-IMPACT: {out_path}")
    else:
        print(json.dumps(impact.to_dict(), indent=2))

    return 0 if impact.route_mode == "NORMAL" else 1


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
    scan_p.add_argument(
        "--exclude-tests",
        action="store_true",
        default=False,
        help="Exclude tests/ and ops_scripts/ from scan roots",
    )
    scan_p.add_argument(
        "--write-manifest",
        action="store_true",
        default=False,
        help="Write artifacts/adg/scan_manifest.json after scan (A1)",
    )

    br_p = subparsers.add_parser("blast-radius", help="Compute blast-radius score")
    br_p.add_argument(
        "--changed",
        nargs="*",
        metavar="FILE",
        help="Changed files for blast-radius computation",
    )

    art_p = subparsers.add_parser("build-artifact", help="Build canonical ADG artifact (schema v3)")
    art_p.add_argument(
        "--output",
        default=None,
        help="Output path for artifact JSON (default: artifacts/adg/adg_canonical_artifact.json)",
    )

    impact_p = subparsers.add_parser("impact", help="Compute change impact for changed files")
    impact_p.add_argument(
        "--changed",
        nargs="*",
        metavar="FILE",
        help="Changed files for impact analysis",
    )
    impact_p.add_argument(
        "--output",
        default=None,
        help="Output path for impact JSON",
    )

    parsed = parser.parse_args(argv)

    if parsed.command == "scan":
        return _cmd_scan(parsed)
    if parsed.command == "blast-radius":
        return _cmd_blast_radius(parsed)
    if parsed.command == "build-artifact":
        return _cmd_build_artifact(parsed)
    if parsed.command == "impact":
        return _cmd_impact(parsed)

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
