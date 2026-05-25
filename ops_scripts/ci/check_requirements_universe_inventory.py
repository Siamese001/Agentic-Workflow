#!/usr/bin/env python3
"""Repo-wide requirement-universe inventory + drift detector.

The repo has ~14 distinct requirement-bearing artifact families using
different ID prefixes, schemas, and storage formats. Without an inventory
gate, new requirement files drift in (no CI link), or existing ones decay
silently.

This script:

  1. Enumerates every requirement-bearing artifact under canonical roots.
  2. Classifies each into a known universe (or flags ``UNKNOWN``).
  3. For each universe, checks whether at least one CI gate, pytest test,
     or pre-commit hook references it.
  4. Emits an inventory artifact at
     ``artifacts/requirements/universe_inventory.json``.
  5. In ``--strict`` mode, fails if any universe is orphaned (no CI link).

Universes (as of 2026-04-30):

  U1  10C semantic ledger          docs/reports/design/10c_reconciliation/10c_semantic_requirement_ledger.csv
  U2  10C traceability matrix      docs/reports/design/10c_reconciliation/10c_requirements_vs_10a_matrix.csv
  U3  10C metric obligations       docs/reports/design/10c_reconciliation/10c_metric_obligation_matrix.csv
  U4  10C model bindings           docs/reports/design/10c_reconciliation/10c_model_binding_matrix.csv
  U5  10C implementation status    docs/reports/design/10c_reconciliation/IMPLEMENTATION_STATUS.md
  U6  10A baseline                 docs/reports/design/baseline_requirements.md + requirements_traceability_matrix.md
  U7  prove_requirements (Step 1)  artifacts/runtime/requirements_proof/* + scripts/verify_*_gate.py
  U8  MERKLE_ROOT enforcement      docs/reference/contracts/enforcement/ALL_REQUIREMENTS_*.json
  U9  AGEN registry                docs/requirements/registry/{policy,best_practice}/AGEN-*.yaml
  U10 Cross-app contracts          docs/requirements/contracts/REQ-*.contract.yaml
  U11 Crosswalk obligations        config/crosswalk/obligations.yaml
  U12 L5 contract matrix           tools/l5_contracts/_requirement_matrix.json
  U13 Per-doctrine matrices        docs/reports/plans/*_requirements_matrix.md, docs/reference/03A/03B/*.md
  U14 Wave_e schema                docs/wave_e/00_schema/requirement_graph_schema.yaml

Exit codes:
    0  All universes either have a CI link OR are explicitly waived.
    1  At least one universe is orphaned (strict mode only).
    2  Infrastructure error.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[2]

# Where we look for CI links
CI_SCAN_ROOTS = (
    REPO_ROOT / "ops_scripts" / "ci",
    REPO_ROOT / "scripts",
    REPO_ROOT / "tests",
    REPO_ROOT / ".pre-commit-config.yaml",
    REPO_ROOT / ".github" / "workflows",
)

OUTPUT_PATH = REPO_ROOT / "artifacts" / "requirements" / "universe_inventory.json"


@dataclass
class Universe:
    """One requirement-bearing artifact family."""

    universe_id: str
    name: str
    paths: tuple[str, ...]                   # repo-relative globs/files
    id_prefix: str | None = None              # e.g. "10C-REQ-", "AGEN-", "REQ-CROSS-APP-"
    schema_format: str = "csv"                # csv|yaml|json|md
    waiver_reason: str = ""                   # if non-empty, orphan status is OK
    # Filled in at runtime
    files_found: list[str] = field(default_factory=list)
    ci_links: list[str] = field(default_factory=list)
    is_orphaned: bool = False


UNIVERSES: tuple[Universe, ...] = (
    Universe(
        universe_id="U1",
        name="10C semantic requirement ledger",
        paths=("docs/reports/design/10c_reconciliation/10c_semantic_requirement_ledger.csv",),
        id_prefix="10C-REQ-",
        schema_format="csv",
    ),
    Universe(
        universe_id="U2",
        name="10C traceability matrix",
        paths=("docs/reports/design/10c_reconciliation/10c_requirements_vs_10a_matrix.csv",),
        id_prefix="10C-REQ-",
        schema_format="csv",
    ),
    Universe(
        universe_id="U3",
        name="10C metric obligation matrix",
        paths=("docs/reports/design/10c_reconciliation/10c_metric_obligation_matrix.csv",),
        id_prefix="MET-10C-",
        schema_format="csv",
    ),
    Universe(
        universe_id="U4",
        name="10C model binding matrix",
        paths=("docs/reports/design/10c_reconciliation/10c_model_binding_matrix.csv",),
        id_prefix="BIND-10C-",
        schema_format="csv",
    ),
    Universe(
        universe_id="U5",
        name="10C implementation status",
        paths=("docs/reports/design/10c_reconciliation/IMPLEMENTATION_STATUS.md",),
        id_prefix="10C-REQ-",
        schema_format="md",
    ),
    Universe(
        universe_id="U6",
        name="10A baseline + traceability matrix",
        paths=(
            "docs/reports/design/baseline_requirements.md",
            "docs/reports/design/requirements_traceability_matrix.md",
        ),
        id_prefix="REQ-",
        schema_format="md",
        waiver_reason="Historical baseline; superseded by 10C ledger but retained for traceability.",
    ),
    Universe(
        universe_id="U7",
        name="prove_requirements Step 1 (150-REQ universe)",
        paths=(
            "agentic_core/runtime/prove_requirements/*.py",
            "scripts/verify_tier*_gate.py",
            "scripts/verify_all_requirements_gates.py",
        ),
        id_prefix=None,
        schema_format="py",
    ),
    Universe(
        universe_id="U8",
        name="ALL_REQUIREMENTS_MERKLE_ROOT enforcement baseline",
        paths=(
            "docs/reference/contracts/enforcement/ALL_REQUIREMENTS_ENFORCEMENT_BASELINE.json",
            "docs/reference/contracts/enforcement/ALL_REQUIREMENTS_MERKLE_ROOT.json",
        ),
        id_prefix=None,
        schema_format="json",
    ),
    Universe(
        universe_id="U9",
        name="AGEN policy + best-practice registry",
        paths=(
            "docs/requirements/registry/policy/AGEN-*.yaml",
            "docs/requirements/registry/best_practice/AGEN-*.yaml",
        ),
        id_prefix="AGEN-",
        schema_format="yaml",
    ),
    Universe(
        universe_id="U10",
        name="Cross-app contract requirements",
        paths=("docs/requirements/contracts/REQ-*.contract.yaml",),
        id_prefix="REQ-",
        schema_format="yaml",
    ),
    Universe(
        universe_id="U11",
        name="Crosswalk obligations registry",
        paths=("config/crosswalk/obligations.yaml",),
        id_prefix=None,
        schema_format="yaml",
    ),
    Universe(
        universe_id="U12",
        name="L5 contract requirement matrix",
        paths=("tools/l5_contracts/_requirement_matrix.json",),
        id_prefix=None,
        schema_format="json",
    ),
    Universe(
        universe_id="U13",
        name="Per-doctrine requirement matrices",
        paths=(
            "docs/reports/plans/*_requirements_matrix.md",
            "docs/reports/plans/*REQUIREMENTS_MATRIX.md",
            "docs/reference/03A_C0_Context_Engine/C0_Requirements_Traceability_Matrix.md",
            "docs/reference/03B_PA_Prompt_Assembly/REQUIREMENT_TRACEABILITY_MATRIX.md",
            "docs/reference/00X_Requirements_Traceability_and_No_Loss_Map.md",
        ),
        id_prefix=None,
        schema_format="md",
        waiver_reason="Per-doctrine narrative matrices feed the prove_requirements extractor (U7). Indirect link.",
    ),
    Universe(
        universe_id="U14",
        name="Wave_e requirement graph schema",
        paths=("docs/wave_e/00_schema/requirement_graph_schema.yaml",),
        id_prefix=None,
        schema_format="yaml",
        waiver_reason="Schema definition file; consumed by future graph-build tooling (not yet wired).",
    ),
)


def _collect_files(patterns: Iterable[str]) -> list[Path]:
    """Resolve a mix of literal paths and globs against REPO_ROOT."""
    out: list[Path] = []
    for pat in patterns:
        p = REPO_ROOT / pat
        if any(ch in pat for ch in "*?["):
            # Glob — anchor at repo root
            out.extend(sorted(REPO_ROOT.glob(pat)))
        elif p.exists():
            out.append(p)
    return out


def _scan_for_references(needles: Iterable[str]) -> list[str]:
    """Return CI/test/precommit files that mention any of the given needles."""
    needles = [n for n in needles if n]
    if not needles:
        return []
    hits: set[str] = set()
    for root in CI_SCAN_ROOTS:
        if not root.exists():
            continue
        if root.is_file():
            files = [root]
        else:
            files = list(root.rglob("*.py")) + list(root.rglob("*.yaml")) + list(root.rglob("*.yml"))
        for f in files:
            try:
                text = f.read_text(encoding="utf-8", errors="ignore")
            except (OSError, UnicodeDecodeError):
                continue
            for needle in needles:
                if needle in text:
                    hits.add(str(f.relative_to(REPO_ROOT)).replace("\\", "/"))
                    break
    return sorted(hits)


def _evaluate_universe(u: Universe) -> Universe:
    files = _collect_files(u.paths)
    u.files_found = sorted(
        str(f.relative_to(REPO_ROOT)).replace("\\", "/") for f in files
    )

    # Build the needle set: for each path/glob, derive literal substrings
    # that any CI gate would have to mention to claim coverage.
    needles: list[str] = []
    for pat in u.paths:
        # Drop glob characters; the stem of the pattern is usually unique enough
        stem = re.sub(r"[\*\?\[\]]", "", pat)
        stem = stem.rstrip("/")
        if stem:
            needles.append(stem)
        # Also use the basename
        base = Path(stem).name
        if base and base != stem:
            needles.append(base)
        # Also use the parent directory — catches CI gates that match the
        # directory via regex (e.g. docs/requirements/contracts/REQ-CROSS-APP-...)
        # rather than a literal full filename.
        parent = str(Path(pat).parent).replace("\\", "/")
        if parent and parent not in (".", "") and parent not in needles:
            needles.append(parent)
        # If the pattern contains a recognizable ID prefix (REQ-, AGEN-,
        # MET-10C-, BIND-10C-, 10C-REQ-), include it as a needle.
        for prefix in ("10C-REQ-", "REQ-CROSS-APP-", "AGEN-", "MET-10C-", "BIND-10C-"):
            if prefix in pat and prefix not in needles:
                needles.append(prefix)

    raw_links = _scan_for_references(needles)
    # Exclude this inventory script itself — it is a discovery tool, not an
    # enforcement gate. A universe whose ONLY link is the inventory script
    # is functionally orphaned.
    self_path = "ops_scripts/ci/check_requirements_universe_inventory.py"
    u.ci_links = [l for l in raw_links if l != self_path]
    u.is_orphaned = not u.ci_links and not u.waiver_reason
    return u


def _summary(universes: list[Universe]) -> dict[str, object]:
    return {
        "total_universes": len(universes),
        "universes_with_ci_link": sum(1 for u in universes if u.ci_links),
        "universes_waived": sum(1 for u in universes if u.waiver_reason and not u.ci_links),
        "universes_orphaned": sum(1 for u in universes if u.is_orphaned),
        "universes_missing_files": sum(1 for u in universes if not u.files_found),
    }


def _render_universe_block(u: Universe) -> str:
    lines = [
        f"  [{u.universe_id}] {u.name}",
        f"      id_prefix : {u.id_prefix or '(none)'}",
        f"      format    : {u.schema_format}",
        f"      files     : {len(u.files_found)} found",
    ]
    if not u.files_found:
        lines.append("                  (no files match — universe currently empty)")
    lines.append(f"      ci_links  : {len(u.ci_links)}")
    for link in u.ci_links[:3]:
        lines.append(f"                  - {link}")
    if len(u.ci_links) > 3:
        lines.append(f"                  ... +{len(u.ci_links) - 3} more")
    if u.waiver_reason:
        lines.append(f"      waiver    : {u.waiver_reason}")
    if u.is_orphaned:
        lines.append("      STATUS    : ORPHANED -- no CI link, no waiver")
    elif u.waiver_reason and not u.ci_links:
        lines.append("      STATUS    : WAIVED")
    elif u.ci_links:
        lines.append("      STATUS    : LINKED")
    else:
        lines.append("      STATUS    : EMPTY (no files match; nothing to link)")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit 1 if any universe is orphaned.",
    )
    parser.add_argument(
        "--no-write",
        action="store_true",
        help="Skip writing the JSON artifact (read-only mode).",
    )
    args = parser.parse_args()

    print("[Requirements universe inventory]")
    print(f"  repo root : {REPO_ROOT}")
    print(f"  universes : {len(UNIVERSES)}")
    print()

    results = [_evaluate_universe(u) for u in UNIVERSES]

    for u in results:
        print(_render_universe_block(u))
        print()

    summary = _summary(results)
    print("Summary:")
    for k, v in summary.items():
        print(f"  {k:>30s} : {v}")

    # Write artifact
    if not args.no_write:
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "summary": summary,
            "universes": [asdict(u) for u in results],
        }
        OUTPUT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"\nArtifact written: {OUTPUT_PATH.relative_to(REPO_ROOT)}")

    if args.strict and summary["universes_orphaned"] > 0:
        print(
            f"\nFAIL  {summary['universes_orphaned']} universe(s) orphaned. "
            f"Either wire a CI link or add an explicit waiver_reason in this script.",
            file=sys.stderr,
        )
        return 1

    print("\nOK  inventory complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
