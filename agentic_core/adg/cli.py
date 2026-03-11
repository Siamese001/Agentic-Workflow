"""ADG CLI entry point.

Usage:
    python -m agentic_core.adg.cli scan [--repo-root .] [--commit <sha>] [--diff-files f1 f2]
    python -m agentic_core.adg.cli blast-radius --changed f1 f2 [--repo-root .]
    python -m agentic_core.adg.cli refactor --analyze FILE [--repo-root .]
    python -m agentic_core.adg.cli refactor --rename OLD NEW [--repo-root .]
    python -m agentic_core.adg.cli refactor --plan [--files f1 f2] [--repo-root .]
    python -m agentic_core.adg.cli hotspots [--top N] [--repo-root .]
    python -m agentic_core.adg.cli test-gaps [--repo-root .]
    python -m agentic_core.adg.cli coupling [--repo-root .]
    python -m agentic_core.adg.cli api-surface [--repo-root .]
    python -m agentic_core.adg.cli dip-check [--repo-root .]

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


def _cmd_refactor(args: argparse.Namespace) -> int:
    import json

    from agentic_core.adg.runtime.cache_loader import load_or_scan

    repo_root = Path(args.repo_root)
    result = load_or_scan(repo_root=str(repo_root))
    result.print_digest()

    if getattr(args, "rename", None):
        from agentic_core.adg.applications.rename_safety import analyze_rename

        old_path, new_path = args.rename
        report = analyze_rename(result, old_path=old_path, new_path=new_path)
        print(report.summary)
        print(json.dumps(report.to_dict(), indent=2))
        return 0 if report.is_safe else 1

    if getattr(args, "analyze", None):
        from agentic_core.adg.analysis.coupling_metrics import compute_coupling_metrics
        from agentic_core.adg.analysis.hotspot_index import HotspotIndex
        from agentic_core.adg.analysis.test_gap import detect_test_gaps
        from agentic_core.adg.applications.placement_advisor import PlacementAdvisor

        target = args.analyze
        idx = HotspotIndex.build(result)
        coupling = compute_coupling_metrics(result)
        gaps = detect_test_gaps(result, hotspot_index=idx)
        advisor = PlacementAdvisor(result, repo_root=repo_root)
        ctx = advisor.get_file_context(target)

        m = idx.metrics(target)
        has_gap = target in {e.module_path for e in gaps.uncovered_modules}
        output = {
            "target": target,
            "coupling": m.to_dict(),
            "zone": coupling.metrics_by_module.get(target, None)
            and coupling.metrics_by_module[target].to_dict(),
            "test_gap": has_gap,
            "file_context": {
                "layer": ctx.layer,
                "direct_importers": ctx.direct_importers,
                "direct_imports": ctx.direct_imports,
                "likely_tests": ctx.likely_tests,
                "structural_risks": ctx.structural_risks,
            },
        }
        print(json.dumps(output, indent=2))
        return 0

    if getattr(args, "plan", False):
        from agentic_core.adg.applications.refactoring_planner import build_refactoring_plan

        files = getattr(args, "files", None) or []
        plan = build_refactoring_plan(result, target_files=files or None)
        print(plan.summary)
        print(json.dumps(plan.to_dict(), indent=2))
        return 0

    print("refactor: specify --rename OLD NEW, --analyze FILE, or --plan", file=sys.stderr)
    return 1


def _cmd_hotspots(args: argparse.Namespace) -> int:
    import json

    from agentic_core.adg.analysis.hotspot_index import HotspotIndex
    from agentic_core.adg.runtime.cache_loader import load_or_scan

    repo_root = Path(args.repo_root)
    result = load_or_scan(repo_root=str(repo_root))
    result.print_digest()

    idx = HotspotIndex.build(result)
    n = getattr(args, "top", 20) or 20
    key = getattr(args, "key", "coupling") or "coupling"
    hotspots = idx.top_hotspots(n=n, threshold=0, key=key)
    print(
        json.dumps(
            {"stats": idx.stats(), "hotspots": [h.to_dict() for h in hotspots]},
            indent=2,
        )
    )
    return 0


def _cmd_test_gaps(args: argparse.Namespace) -> int:
    import json

    from agentic_core.adg.analysis.hotspot_index import HotspotIndex
    from agentic_core.adg.analysis.test_gap import detect_test_gaps
    from agentic_core.adg.runtime.cache_loader import load_or_scan

    repo_root = Path(args.repo_root)
    result = load_or_scan(repo_root=str(repo_root))
    result.print_digest()

    idx = HotspotIndex.build(result)
    report = detect_test_gaps(result, hotspot_index=idx)
    print(report.summary)
    print(json.dumps(report.to_dict(), indent=2))
    return 0


def _cmd_coupling(args: argparse.Namespace) -> int:
    import json

    from agentic_core.adg.analysis.coupling_metrics import compute_coupling_metrics
    from agentic_core.adg.runtime.cache_loader import load_or_scan

    repo_root = Path(args.repo_root)
    result = load_or_scan(repo_root=str(repo_root))
    result.print_digest()

    report = compute_coupling_metrics(result)
    pain = [m.to_dict() for m in report.top_pain_zone[:20]]
    useless = [m.to_dict() for m in report.top_uselessness_zone[:20]]
    unstable = [m.to_dict() for m in report.most_unstable[:20]]
    print(
        json.dumps(
            {
                "pain_zone": pain,
                "uselessness_zone": useless,
                "most_unstable": unstable,
            },
            indent=2,
        )
    )
    return 0


def _cmd_api_surface(args: argparse.Namespace) -> int:
    import json

    from agentic_core.adg.applications.api_surface import build_api_surface
    from agentic_core.adg.runtime.cache_loader import load_or_scan

    repo_root = Path(args.repo_root)
    result = load_or_scan(repo_root=str(repo_root))
    result.print_digest()

    report = build_api_surface(result)
    print(json.dumps(report.to_dict(), indent=2))
    return 0


def _cmd_dip_check(args: argparse.Namespace) -> int:
    import json

    from agentic_core.adg.analysis.dep_inversion import detect_dip_violations
    from agentic_core.adg.runtime.cache_loader import load_or_scan

    repo_root = Path(args.repo_root)
    result = load_or_scan(repo_root=str(repo_root))
    result.print_digest()

    report = detect_dip_violations(result)
    print(report.summary)
    print(json.dumps(report.to_dict(), indent=2))
    return 1 if report.violation_count > 0 else 0


def _cmd_runtime_graph(args: argparse.Namespace) -> int:
    import json

    from agentic_core.adg.applications.runtime_graph import build_runtime_graph
    from agentic_core.adg.runtime.cache_loader import load_or_scan

    repo_root = Path(args.repo_root)
    result = load_or_scan(repo_root=str(repo_root))
    result.print_digest()

    report = build_runtime_graph(result)
    print(report.summary)
    print(json.dumps(report.to_dict(), indent=2))
    return 0


def _cmd_layer_authority(args: argparse.Namespace) -> int:
    import json

    from agentic_core.adg.analysis.layer_authority import detect_layer_authority_violations
    from agentic_core.adg.runtime.cache_loader import load_or_scan

    repo_root = Path(args.repo_root)
    result = load_or_scan(repo_root=str(repo_root))
    result.print_digest()

    report = detect_layer_authority_violations(result)
    print(report.summary)
    print(json.dumps(report.to_dict(), indent=2))
    return 1 if report.violation_count > 0 else 0


def _cmd_mutation_paths(args: argparse.Namespace) -> int:
    import json

    from agentic_core.adg.analysis.mutation_authority import verify_mutation_paths
    from agentic_core.adg.runtime.cache_loader import load_or_scan

    repo_root = Path(args.repo_root)
    result = load_or_scan(repo_root=str(repo_root))
    result.print_digest()

    report = verify_mutation_paths(result)
    print(report.summary)
    print(json.dumps(report.to_dict(), indent=2))
    critical = len(report.critical_violations())
    return 1 if critical > 0 else 0


def _cmd_state_lineage(args: argparse.Namespace) -> int:
    import json

    from agentic_core.adg.applications.state_lineage import build_lineage_index
    from agentic_core.adg.runtime.cache_loader import load_or_scan

    repo_root = Path(args.repo_root)
    result = load_or_scan(repo_root=str(repo_root))
    result.print_digest()

    index = build_lineage_index(result)
    summary = index.coverage_summary()

    if args.query:
        records = index.mutations_for_state(args.query)
        print(f"Mutations for state key '{args.query}': {len(records)} records")
        print(json.dumps([r.to_dict() for r in records[:50]], indent=2))
    else:
        print(json.dumps(summary, indent=2))
    return 0


def _cmd_verify_architecture(args: argparse.Namespace) -> int:
    from agentic_core.adg.applications.architecture_verifier import verify_architecture
    from agentic_core.adg.runtime.cache_loader import load_or_scan

    repo_root = Path(args.repo_root)
    result = load_or_scan(repo_root=str(repo_root))
    result.print_digest()

    skip: frozenset[str] = frozenset(args.skip_planes) if args.skip_planes else frozenset()
    report = verify_architecture(result, skip_planes=skip)
    report.print_summary()

    if args.json:
        import json

        print(json.dumps(report.to_dict(), indent=2))

    return report.exit_code()


def _cmd_policy_hash(args: argparse.Namespace) -> int:
    import json

    from agentic_core.adg.analysis.policy_hash_validator import validate_policy_hash_coupling
    from agentic_core.adg.runtime.cache_loader import load_or_scan

    repo_root = Path(args.repo_root)
    result = load_or_scan(repo_root=str(repo_root))
    result.print_digest()

    report = validate_policy_hash_coupling(result)
    print(report.summary)
    print(json.dumps(report.to_dict(), indent=2))
    return 1 if report.violation_count > 0 else 0


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

    ref_p = subparsers.add_parser("refactor", help="Refactoring safety and planning (E12, E17)")
    ref_p.add_argument("--rename", nargs=2, metavar=("OLD", "NEW"), help="Rename/move safety analysis")
    ref_p.add_argument("--analyze", metavar="FILE", help="Full structural analysis of a file")
    ref_p.add_argument("--plan", action="store_true", default=False, help="Generate refactoring plan")
    ref_p.add_argument("--files", nargs="*", metavar="FILE", help="Target files for refactoring plan")

    hs_p = subparsers.add_parser("hotspots", help="Show fan-in/fan-out hotspot index (E14)")
    hs_p.add_argument("--top", type=int, default=20, help="Number of hotspots to show")
    hs_p.add_argument(
        "--key", default="coupling", choices=["coupling", "fan_in", "fan_out", "instability"], help="Sort key"
    )

    subparsers.add_parser("test-gaps", help="Detect modules with no test coverage signal (E15)")
    subparsers.add_parser("coupling", help="Coupling/cohesion metrics — Martin stability (E16)")
    subparsers.add_parser("api-surface", help="Public API surface extraction (E13)")
    subparsers.add_parser("dip-check", help="Dependency Inversion Principle check (E18)")

    # P6 prompt governance
    subparsers.add_parser(
        "prompt-authority", help="Prompt authority DAG enforcement — slot hierarchy violations (E21)"
    )
    subparsers.add_parser("prompt-lifecycle", help="Prompt lifecycle graph — generates/consumes edges (E20)")
    pi_p = subparsers.add_parser("prompt-impact", help="Prompt blast radius for changed files (E24)")
    pi_p.add_argument("--changed", nargs="*", metavar="FILE", help="Changed files for prompt impact analysis")

    # P3 runtime / authority / mutation / policy
    subparsers.add_parser(
        "runtime-graph", help="Runtime execution graph — AgentAction/ToolInvocation/LayerTransition (E26)"
    )
    subparsers.add_parser(
        "layer-authority", help="Layer authority enforcement — behavioral contract violations (E27)"
    )
    subparsers.add_parser("mutation-paths", help="Mutation path verification — UWG bypass detection (E28)")
    sl_p = subparsers.add_parser("state-lineage", help="State lineage query — who mutated this state? (E29)")
    sl_p.add_argument(
        "--query", default="", metavar="STATE_KEY", help="State symbol key to trace mutations for"
    )
    va_p = subparsers.add_parser(
        "verify-architecture", help="Unified architecture verification across all planes (E30)"
    )
    va_p.add_argument(
        "--skip-planes",
        nargs="*",
        metavar="PLANE",
        help="Planes to skip: runtime_graph layer_authority mutation_paths policy_hash",
    )
    va_p.add_argument("--json", action="store_true", default=False, help="Emit full JSON report")
    subparsers.add_parser("policy-hash", help="Policy hash runtime coupling validation (E31)")

    parsed = parser.parse_args(argv)

    if parsed.command == "scan":
        return _cmd_scan(parsed)
    if parsed.command == "blast-radius":
        return _cmd_blast_radius(parsed)
    if parsed.command == "build-artifact":
        return _cmd_build_artifact(parsed)
    if parsed.command == "impact":
        return _cmd_impact(parsed)
    if parsed.command == "refactor":
        return _cmd_refactor(parsed)
    if parsed.command == "hotspots":
        return _cmd_hotspots(parsed)
    if parsed.command == "test-gaps":
        return _cmd_test_gaps(parsed)
    if parsed.command == "coupling":
        return _cmd_coupling(parsed)
    if parsed.command == "api-surface":
        return _cmd_api_surface(parsed)
    if parsed.command == "dip-check":
        return _cmd_dip_check(parsed)

    # P6 prompt governance
    if parsed.command == "prompt-authority":
        return _cmd_prompt_authority(parsed)
    if parsed.command == "prompt-lifecycle":
        return _cmd_prompt_lifecycle(parsed)
    if parsed.command == "prompt-impact":
        return _cmd_prompt_impact(parsed)

    # P3 runtime / authority / mutation / policy
    if parsed.command == "runtime-graph":
        return _cmd_runtime_graph(parsed)
    if parsed.command == "layer-authority":
        return _cmd_layer_authority(parsed)
    if parsed.command == "mutation-paths":
        return _cmd_mutation_paths(parsed)
    if parsed.command == "state-lineage":
        return _cmd_state_lineage(parsed)
    if parsed.command == "verify-architecture":
        return _cmd_verify_architecture(parsed)
    if parsed.command == "policy-hash":
        return _cmd_policy_hash(parsed)

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
