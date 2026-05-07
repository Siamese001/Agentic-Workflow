"""CLI interface for apps_architect.

Plan: ``.windsurf/plans/apps-architect-pattern-hardening-d7e4f9.md`` W4.P3.

Commands:
    python -m apps_architect scan --days 30 --output json
    python -m apps_architect delta --against ref/patterns.json
    python -m apps_architect rules --severity recommended
    python -m apps_architect readme --sync --dry-run
    python -m apps_architect readme --sync --pr
"""

from __future__ import annotations

import argparse
import json as _json
import logging
import sys
from pathlib import Path

from apps_architect.engines import (
    ADGClient,
    CorePatternEngine,
    DeltaEngine,
    PatternScanner,
    PlanPatternEngine,
    ReadmeAssembler,
    RuleGenerator,
    RulePatternEngine,
)
from apps_architect.integrations import GitHubSync
from apps_architect.types import PatternCollection

_log = logging.getLogger(__name__)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="apps_architect", description="Pattern collection & repo hardening engine")
    sub = parser.add_subparsers(dest="command")

    scan_p = sub.add_parser("scan", help="Scan for patterns")
    scan_p.add_argument("--days", type=int, default=30, help="Scan depth in days")
    scan_p.add_argument("--output", choices=("json", "text"), default="text")

    delta_p = sub.add_parser("delta", help="Compute delta against reference")
    delta_p.add_argument("--against", type=str, help="Path to reference patterns JSON")

    rules_p = sub.add_parser("rules", help="Generate hardening rules")
    rules_p.add_argument("--severity", choices=("advisory", "recommended", "required"), default="recommended")

    readme_p = sub.add_parser("readme", help="README operations")
    readme_p.add_argument("--sync", action="store_true", help="Sync README")
    readme_p.add_argument("--dry-run", action="store_true", default=True, help="Dry run (default)")
    readme_p.add_argument("--pr", action="store_true", help="Create actual PR")

    return parser


def _cmd_scan(args: argparse.Namespace) -> int:
    _log.info("Scanning patterns (depth=%d days)...", args.days)
    ps = PatternScanner()
    pe = PlanPatternEngine()
    re = RulePatternEngine()
    ce = CorePatternEngine()

    try:
        adg_pats = ps.scan_all()
        plan_pats = pe.extract_all(max_files=args.days)
        rule_pats = re.extract_all()
        core_pats = ce.detect_all()
        combined = PatternCollection.from_patterns(
            adg_pats.patterns + plan_pats + rule_pats + core_pats
        )
    finally:
        ps.close()
        ce.close()

    if args.output == "json":
        data = {
            "total": len(combined.patterns),
            "digest": combined.collection_digest,
            "patterns": [
                {"id": p.pattern_id, "type": p.pattern_type.value, "summary": p.summary}
                for p in combined.patterns
            ],
        }
        print(_json.dumps(data, indent=2, default=str))
    else:
        print(f"Patterns: {len(combined.patterns)} (digest: {combined.collection_digest})")
        for p in combined.patterns[:20]:
            print(f"  [{p.pattern_type.value}] {p.summary[:100]}")
        if len(combined.patterns) > 20:
            print(f"  ... and {len(combined.patterns) - 20} more")
    return 0


def _cmd_delta(args: argparse.Namespace) -> int:
    if args.against:
        data = _json.loads(Path(args.against).read_text(encoding="utf-8"))
        patterns = tuple(
            __import__("apps_architect.types").types.architect_types.Pattern(**p)
            for p in data.get("patterns", [])
        )
        collection = PatternCollection.from_patterns(patterns)
    else:
        ps = PatternScanner()
        pe = PlanPatternEngine()
        re = RulePatternEngine()
        try:
            collection = PatternCollection.from_patterns(
                ps.scan_all().patterns + pe.extract_all(30) + re.extract_all()
            )
        finally:
            ps.close()

    de = DeltaEngine()
    report = de.compute(collection)
    print(f"Delta: total={report.total_patterns} new={report.new_count} "
          f"stale={report.stale_count} missing={report.missing_count} drift={report.drift_count}")
    for e in report.entries[:10]:
        print(f"  [{e.delta_type.value}] {e.recommendation[:100]}")
    return 0


def _cmd_rules(args: argparse.Namespace) -> int:
    ps = PatternScanner()
    pe = PlanPatternEngine()
    re = RulePatternEngine()
    try:
        collection = PatternCollection.from_patterns(
            ps.scan_all().patterns + pe.extract_all(30) + re.extract_all()
        )
    finally:
        ps.close()

    de = DeltaEngine()
    report = de.compute(collection)
    rg = RuleGenerator()
    rules = rg.generate(report)

    severity_filter = args.severity
    filtered = [
        r for r in rules
        if f"severity: {severity_filter}" in r or severity_filter == "advisory"
    ]
    for rule in filtered[:10]:
        print(rule)
        print("---")
    print(f"\n{len(filtered)} rules (severity >= {severity_filter})")
    return 0


def _cmd_readme(args: argparse.Namespace) -> int:
    if not args.sync:
        print("Use --sync to generate README. Options: --dry-run (default), --pr")
        return 0

    ps = PatternScanner()
    pe = PlanPatternEngine()
    re = RulePatternEngine()
    try:
        collection = PatternCollection.from_patterns(
            ps.scan_all().patterns + pe.extract_all(30) + re.extract_all()
        )
    finally:
        ps.close()

    de = DeltaEngine()
    report = de.compute(collection)
    ra = ReadmeAssembler()
    readme = ra.assemble(collection, report)

    if args.pr:
        gs = GitHubSync()
        result = gs.create_pr(readme, dry_run=False)
        print(_json.dumps(result, indent=2))
    else:
        # dry-run: print to stdout
        print(readme)
        print(f"\n--- dry-run: {len(readme)} chars ---")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv or sys.argv[1:])

    if args.command == "scan":
        return _cmd_scan(args)
    elif args.command == "delta":
        return _cmd_delta(args)
    elif args.command == "rules":
        return _cmd_rules(args)
    elif args.command == "readme":
        return _cmd_readme(args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
