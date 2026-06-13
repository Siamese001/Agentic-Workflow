#!/usr/bin/env python3
"""Gate G-CONSUMER-MODE-DECLARED — every ADG consumer must declare its mode.

ADG consumer mode: ``proof`` — this gate's verdict is enforcement-grade.
It enforces the W4 contract from
``agentic_core/adg/artifact/consumer_mode.py``: every file that reads or
queries the ADG MUST set a module-level ``__adg_consumer_mode__``
constant whose value is one of ``proof`` / ``risk`` / ``inventory``.

Detection criteria for "is a consumer":

* File is under one of the ``CONSUMER_DIRS`` roots
* AND the file contains at least one of the ADG-read signatures (queries
  ``edges``, ``nodes``, or one of the canonical views)

For each detected consumer, the gate validates:

1. Module-level ``__adg_consumer_mode__`` constant exists.
2. Its value is one of the three canonical modes.
3. The declared mode is compatible with the views the file reads
   (proof-mode required to read ``proof_view``; risk-mode required to
   read ``risk_view``; inventory-mode minimum to read
   ``inventory_view``).

Tier: B (blocking once activated). Until an activation flag is set, the
gate runs in advisory-only mode (exit 0, prints violations) so existing
~76 unannotated consumers are surfaced before they block CI.

Bypass: ``CONSUMER_MODE_BYPASS=1``.
Activation flag: ``CONSUMER_MODE_GATE_STRICT=1`` switches advisory →
blocking.
"""

from __future__ import annotations

# W4 ADG consumer mode declaration (per .claude/rules/adg-canonical-invariants.md
# §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "proof"

import argparse
import ast
import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Final

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agentic_core.adg.artifact.consumer_mode import (  # noqa: E402
    ALL_CONSUMER_MODES,
    DECLARATION_NAME,
    VIEW_TO_REQUIRED_MODE,
    is_mode_compatible_with_view,
)


# Directories whose .py files are subject to consumer-mode discipline.
# Test directories are excluded — tests can read any view (test fixtures
# don't drive enforcement).
CONSUMER_DIRS: Final[tuple[str, ...]] = (
    "agentic_core/adg",
    "tools/adg",
    "tools/analysis",
    "ops_scripts/ci",
    "apps_eval/integrations",
    "apps_exec/integrations",
    "apps_research/integrations",
    "apps_lic/integrations",
    "apps_rg/integrations",
    "apps_underwriting_ai",
)

# Files in these dirs are excluded — they are SCHEMA / WRITER files, not
# consumers (they CREATE views, not read them).
EXCLUDE_FILES: Final[tuple[str, ...]] = (
    "agentic_core/adg/artifact/edge_authority.py",
    "agentic_core/adg/artifact/ArtifactPaths.py",
    "agentic_core/adg/artifact/multi_writer.py",
    "agentic_core/adg/artifact/ssot_decision_record.py",
    "agentic_core/adg/artifact/consumer_mode.py",
    "agentic_core/adg/registry/registry_resolvers.py",
    "agentic_core/adg/registry/__init__.py",
    # tools/adg/runtime_bucket_lift.py — RETIRED 2026-04-29 (plan
    # three-bucket-otel-view-5db409 W2). Replaced by runtime VIEW pattern in
    # tools/otel/runtime_view_builder.py — see ADR-074. Archived to
    # archives/tools_adg_lift_5db409/.
    "tools/adg/registry_bucket_lift.py",
    "tools/otel/runtime_view_builder.py",
)

# Read-signature regex — matches every common ADG read pattern.
_READ_SIGNATURE_RE: Final[re.Pattern[str]] = re.compile(
    r"\b(FROM\s+(?:edges|nodes|proof_view|risk_view|inventory_view|mv_\w+|v_p\d_\w+)|"
    r"adg_(?:nodes|edges|node|violations)\b|"
    r"sqlite3\.connect\([^)]*adg_indexed_)",
    re.IGNORECASE,
)

# View-name regex — matches `FROM <view>` / `JOIN <view>`.
_VIEW_USE_RE: Final[re.Pattern[str]] = re.compile(
    r"\b(?:FROM|JOIN)\s+(proof_view|risk_view|inventory_view|"
    r"mv_verified_dependencies|mv_unresolved_dependencies|mv_governance_dependencies)\b",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Detection types
# ---------------------------------------------------------------------------


@dataclass
class Violation:
    rel_path: str
    kind: str  # missing | invalid_value | mode_mismatch
    message: str
    declared_mode: str | None = None
    views_used: list[str] = field(default_factory=list)


@dataclass
class GateReport:
    snapshot_used: str = "n/a (gate is filesystem-only)"
    consumers_scanned: int = 0
    declared: int = 0
    missing: int = 0
    invalid: int = 0
    mode_mismatch: int = 0
    violations: list[Violation] = field(default_factory=list)
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def as_json(self) -> dict[str, object]:
        return {
            "gate": "G-CONSUMER-MODE-DECLARED",
            "tier": "B",
            "timestamp": self.timestamp,
            "snapshot_used": self.snapshot_used,
            "consumers_scanned": self.consumers_scanned,
            "declared": self.declared,
            "missing": self.missing,
            "invalid": self.invalid,
            "mode_mismatch": self.mode_mismatch,
            "violation_count": len(self.violations),
            "violations": [
                {
                    "rel_path": v.rel_path,
                    "kind": v.kind,
                    "declared_mode": v.declared_mode,
                    "views_used": v.views_used,
                    "message": v.message,
                }
                for v in self.violations
            ],
        }


# ---------------------------------------------------------------------------
# AST extraction
# ---------------------------------------------------------------------------


def extract_module_level_constant(source: str, name: str) -> str | None:
    """Return the value of a module-level ``name = "..."`` constant.

    Returns None if no module-level assignment exists or the value is not
    a string literal. Walks only the top-level statements; declarations
    inside ``if __name__ == '__main__'`` blocks are intentionally ignored.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None
    for stmt in tree.body:
        if isinstance(stmt, ast.Assign):
            for target in stmt.targets:
                if isinstance(target, ast.Name) and target.id == name:
                    if isinstance(stmt.value, ast.Constant) and isinstance(
                        stmt.value.value, str
                    ):
                        return stmt.value.value
    return None


def detect_views_used(source: str) -> list[str]:
    """Return the unique sorted list of canonical views the source reads."""
    views: set[str] = set()
    for match in _VIEW_USE_RE.finditer(source):
        views.add(match.group(1).lower())
    return sorted(views)


def is_adg_consumer(rel_path: str, source: str) -> bool:
    """Return True iff the file qualifies as an ADG consumer.

    Conservative test: must be in a CONSUMER_DIRS root, must NOT be in
    the writer/schema EXCLUDE_FILES list, must contain at least one
    ADG-read signature.
    """
    rel_path_norm = rel_path.replace("\\", "/")
    if rel_path_norm in EXCLUDE_FILES:
        return False
    if not any(rel_path_norm.startswith(d + "/") for d in CONSUMER_DIRS):
        return False
    return bool(_READ_SIGNATURE_RE.search(source))


# ---------------------------------------------------------------------------
# Scan + validate
# ---------------------------------------------------------------------------


def iter_candidate_files(root: Path) -> list[Path]:
    paths: list[Path] = []
    for d in CONSUMER_DIRS:
        base = root / d
        if not base.exists():
            continue
        for p in base.rglob("*.py"):
            if "__pycache__" in p.parts:
                continue
            paths.append(p)
    return paths


def scan(root: Path | None = None) -> GateReport:
    if root is None:
        root = REPO_ROOT
    report = GateReport()
    candidates = iter_candidate_files(root)
    for path in candidates:
        rel_path = str(path.relative_to(root)).replace("\\", "/")
        try:
            source = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if not is_adg_consumer(rel_path, source):
            continue
        report.consumers_scanned += 1
        declared = extract_module_level_constant(source, DECLARATION_NAME)
        views_used = detect_views_used(source)
        if declared is None:
            report.missing += 1
            report.violations.append(
                Violation(
                    rel_path=rel_path,
                    kind="missing",
                    message=(
                        f"missing module-level `{DECLARATION_NAME}` declaration "
                        f"(views_used={views_used})"
                    ),
                    views_used=views_used,
                )
            )
            continue
        if declared not in ALL_CONSUMER_MODES:
            report.invalid += 1
            report.violations.append(
                Violation(
                    rel_path=rel_path,
                    kind="invalid_value",
                    message=(
                        f"`{DECLARATION_NAME}` = {declared!r} is not one of "
                        f"{sorted(ALL_CONSUMER_MODES)}"
                    ),
                    declared_mode=declared,
                    views_used=views_used,
                )
            )
            continue
        report.declared += 1
        # Mode-compatibility check.
        for view in views_used:
            if not is_mode_compatible_with_view(
                declared_mode=declared, view_name=view
            ):
                report.mode_mismatch += 1
                report.violations.append(
                    Violation(
                        rel_path=rel_path,
                        kind="mode_mismatch",
                        message=(
                            f"declared `{declared}` cannot read `{view}` "
                            f"(authority rule: see consumer_mode.py)"
                        ),
                        declared_mode=declared,
                        views_used=views_used,
                    )
                )
                # One mismatch per file is enough — break to avoid noise.
                break
    return report


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--report-path",
        type=Path,
        default=None,
        help="Optional JSON report sink",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Override CONSUMER_MODE_GATE_STRICT env var; fail on any violation",
    )
    args = parser.parse_args(argv)

    if os.environ.get("CONSUMER_MODE_BYPASS") == "1":
        print("[BYPASS] CONSUMER_MODE_BYPASS=1 — gate skipped")
        return 0

    report = scan()
    print(
        f"[INFO] consumers_scanned={report.consumers_scanned}  "
        f"declared={report.declared}  missing={report.missing}  "
        f"invalid={report.invalid}  mode_mismatch={report.mode_mismatch}"
    )
    for v in report.violations[:20]:
        print(f"  [{v.kind}] {v.rel_path} :: {v.message}")
    if len(report.violations) > 20:
        print(f"  ... and {len(report.violations) - 20} more")

    if args.report_path is not None:
        args.report_path.parent.mkdir(parents=True, exist_ok=True)
        with args.report_path.open("w", encoding="utf-8") as f:
            json.dump(report.as_json(), f, indent=2)
        print(f"[OK] wrote report → {args.report_path}")

    # W4 of plan three-bucket-gap-remediation-069806: strict mode is now the
    # default. Set CONSUMER_MODE_GATE_STRICT=0 to revert to advisory.
    _env = os.environ.get("CONSUMER_MODE_GATE_STRICT", "1")
    strict = args.strict or _env == "1"
    if not report.violations:
        print("[OK] every detected ADG consumer declares __adg_consumer_mode__")
        return 0
    if strict:
        print(
            f"[FAIL] {len(report.violations)} consumer(s) violate the W4 "
            "consumer-mode contract; set CONSUMER_MODE_BYPASS=1 to bypass"
        )
        return 1
    print(
        "[ADVISORY] gate is in advisory-only mode (export "
        "CONSUMER_MODE_GATE_STRICT=1 to re-enable strict, or unset "
        "CONSUMER_MODE_GATE_STRICT=0); violations listed above"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
