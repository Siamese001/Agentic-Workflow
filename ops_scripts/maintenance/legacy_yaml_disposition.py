"""Legacy YAML disposition classifier + per-file header writer.

Plan: `docs/archive/windsurf/legacy-tree/plans/legacy-yaml-deletion-audit-c8e3a4.md`.

Classifies each of the 13 "legacy" YAML files into one of three
dispositions and writes an appropriate header stamp:

- **(a) CANONICAL_SSOT** — file is the authoritative source. Header:
  `# CANONICAL SSOT — actively imported by <consumers>. Do not deprecate.`
- **(b) MIGRATION_CANDIDATE** — file has active consumers AND a migration
  path to `config/domain_contract/`. Header: `# MIGRATION CANDIDATE — ...`
- **(c) ORPHANED** — no active consumers (empty grep). Header:
  `# ORPHANED — no known consumers; deletion candidate.`

Classification is driven by a static CONSUMER_MAP derived from the
grep audit run in `apps-eval-harness-terminal-3c9f81` W5. Re-audit
before running by rerunning `legacy_yaml_audit.py` against the repo.

Authority
---------
WRITES only YAML comment headers. Never deletes files.
"""

from __future__ import annotations

import argparse
import json
import logging
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional

Logger = logging.getLogger(__name__)


class Disposition(str, Enum):
    CANONICAL_SSOT = "canonical_ssot"
    MIGRATION_CANDIDATE = "migration_candidate"
    ORPHANED = "orphaned"


@dataclass(frozen=True)
class FileDisposition:
    rel_path: str
    disposition: Disposition
    consumers: tuple[str, ...]
    migration_target: str = ""
    rationale: str = ""


# Static audit results from grep pass in terminal-3c9f81 W5 + extended
# audit in this plan. Updated 2026-05-03.
DISPOSITIONS: tuple[FileDisposition, ...] = (
    FileDisposition(
        rel_path="config/routing_thresholds.yaml",
        disposition=Disposition.CANONICAL_SSOT,
        consumers=(
            "agentic_core/runtime/config/routing_thresholds.py",
            "ops_scripts/calibration/calibration_drift_detector.py",
            "ops_scripts/calibration/weekly_refresh.py",
            "agentic_core/L0_routing/reasoning/route_gates.py",
            "agentic_core/L0_routing/reasoning/v15_route_selector.py",
        ),
        rationale="L0 routing's authoritative threshold file; not legacy despite _thresholds.yaml suffix.",
    ),
    FileDisposition(
        rel_path="apps_eval/config/eval_policies.yaml",
        disposition=Disposition.CANONICAL_SSOT,
        consumers=(
            "ops_scripts/calibration/calibration_drift_detector.py",
            "apps_eval/engines/_taxonomy.py",
        ),
        rationale="Owns calibration_drift_policy block consumed by drift detector. Migration would require refactoring drift detector first.",
    ),
    FileDisposition(
        rel_path="apps_eval/config/eval_thresholds.yaml",
        disposition=Disposition.ORPHANED,
        consumers=(),
        rationale="Re-audit 2026-05-03 (Pathway C activation, AG dec_19dedcd1c109ebf25 follow-up): no Python file-load consumers found. The regression_detector.py docstring reference is a comment, not a load. tools/apps_proof/generate_compact_app_contracts.py mentions the filename in a contract description string only. Safe to delete via Author-Gate marker.",
    ),
    FileDisposition(
        rel_path="apps_exec/config/exec_policies.yaml",
        disposition=Disposition.ORPHANED,
        consumers=(),
        rationale="Re-audit 2026-05-03: no Python file-load consumers; the speculative 'indirect via config loader' from the original audit does not exist in apps_exec. Safe to delete via Author-Gate marker.",
    ),
    FileDisposition(
        rel_path="apps_exec/config/exec_thresholds.yaml",
        disposition=Disposition.ORPHANED,
        consumers=(),
        rationale="Re-audit 2026-05-03: no Python file-load consumers. Safe to delete via Author-Gate marker.",
    ),
    FileDisposition(
        rel_path="apps_lic/config/lic_policies.yaml",
        disposition=Disposition.ORPHANED,
        consumers=(),
        rationale="Re-audit 2026-05-03: no Python file-load consumers. Declarative references exist in agent_spec.outreach_messaging.v1.0.0.yaml (rule_set_refs), domain_contract/{capability_profiles,input_contract,retrieval_profiles}.yaml (source_app_config_ref provenance), THREAT_MODEL.md, SVP_ENGINEERING_REVIEW.md — these are declarative pointers, not loads. The active SSOT is apps_lic/config/domain_contract/. Safe to delete via Author-Gate marker; provenance pointers will become dangling but cause no runtime failure.",
    ),
    FileDisposition(
        rel_path="apps_lic/config/lic_thresholds.yaml",
        disposition=Disposition.ORPHANED,
        consumers=(),
        rationale="Re-audit 2026-05-03: no Python file-load consumers; only one source_app_config_ref provenance pointer in domain_contract/threshold_profiles.yaml. The active SSOT is domain_contract/threshold_profiles.yaml. Safe to delete via Author-Gate marker.",
    ),
    FileDisposition(
        rel_path="apps_research/config/research_policies.yaml",
        disposition=Disposition.ORPHANED,
        consumers=(),
        rationale="Re-audit 2026-05-03: no Python file-load consumers. Safe to delete via Author-Gate marker.",
    ),
    FileDisposition(
        rel_path="apps_research/config/research_thresholds.yaml",
        disposition=Disposition.ORPHANED,
        consumers=(),
        rationale="Re-audit 2026-05-03: no Python file-load consumers. Safe to delete via Author-Gate marker.",
    ),
    FileDisposition(
        rel_path="apps_rg/config/rg_policies.yaml",
        disposition=Disposition.ORPHANED,
        consumers=(),
        rationale="Re-audit 2026-05-03: no Python file-load consumers in the 52 apps_rg engine files; the original audit's '52 files' figure was a directory count, not a consumer count. Safe to delete via Author-Gate marker.",
    ),
    FileDisposition(
        rel_path="apps_rg/config/rg_thresholds.yaml",
        disposition=Disposition.CANONICAL_SSOT,
        consumers=("apps_rg engines (intentional_zero_dims consumer)",),
        rationale="Has active intentional_zero_dims annotation consumed by harness parity gate. Treat as canonical.",
    ),
)


def _header_for(disp: FileDisposition) -> str:
    if disp.disposition is Disposition.CANONICAL_SSOT:
        consumers = ", ".join(disp.consumers)
        return (
            "# CANONICAL SSOT — actively imported; do NOT deprecate.\n"
            f"# Consumers: {consumers}\n"
            f"# Rationale: {disp.rationale}\n"
            "# Plan: docs/archive/windsurf/legacy-tree/plans/legacy-yaml-deletion-audit-c8e3a4.md\n"
            "\n"
        )
    if disp.disposition is Disposition.MIGRATION_CANDIDATE:
        return (
            "# MIGRATION CANDIDATE — active consumers exist; migration target identified.\n"
            f"# Migration target: {disp.migration_target}\n"
            f"# Rationale: {disp.rationale}\n"
            "# Plan: docs/archive/windsurf/legacy-tree/plans/legacy-yaml-deletion-audit-c8e3a4.md\n"
            "# Do NOT delete without (1) migrating consumers + (2) Author-Gate.\n"
            "\n"
        )
    return (
        "# ORPHANED — no known active consumers; deletion candidate.\n"
        f"# Rationale: {disp.rationale}\n"
        "# Plan: docs/archive/windsurf/legacy-tree/plans/legacy-yaml-deletion-audit-c8e3a4.md\n"
        "# Delete via Author-Gate after confirming no consumers exist.\n"
        "\n"
    )


def apply(repo_root: Path, dry_run: bool = False) -> list[dict]:
    """Apply disposition headers to each registered file. Returns summary."""
    summary: list[dict] = []
    for disp in DISPOSITIONS:
        path = repo_root / disp.rel_path
        if not path.is_file():
            summary.append({"path": disp.rel_path, "action": "skipped_missing"})
            continue
        text = path.read_text(encoding="utf-8")
        # Strip any prior disposition header we may have written.
        lines = text.splitlines(keepends=False)
        stripped = []
        in_header = True
        skipped = 0
        for line in lines:
            if in_header and line.startswith("#") and any(
                marker in line
                for marker in (
                    "CANONICAL SSOT",
                    "MIGRATION CANDIDATE",
                    "ORPHANED",
                    "legacy-yaml-deletion-audit-c8e3a4",
                    "Consumers:",
                    "Migration target:",
                    "Rationale:",
                    "Delete via Author-Gate",
                    "Do NOT delete without",
                    "Plan: docs/archive/windsurf/legacy-tree/plans/legacy-yaml",
                )
            ):
                skipped += 1
                continue
            in_header = False
            stripped.append(line)
        body = "\n".join(stripped).lstrip("\n")
        new_text = _header_for(disp) + body
        action = "dry_run" if dry_run else "written"
        if not dry_run:
            path.write_text(new_text, encoding="utf-8", newline="\n")
        summary.append(
            {
                "path": disp.rel_path,
                "disposition": disp.disposition.value,
                "action": action,
                "consumers_count": len(disp.consumers),
                "prior_header_lines_stripped": skipped,
            }
        )
    return summary


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Apply legacy YAML disposition headers")
    p.add_argument("--root", type=Path, default=Path("."))
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--out", type=Path, default=None)
    return p


def main(argv: Optional[list[str]] = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    args = _build_parser().parse_args(argv)
    summary = apply(args.root.resolve(), dry_run=args.dry_run)
    text = json.dumps(summary, indent=2, sort_keys=True)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
