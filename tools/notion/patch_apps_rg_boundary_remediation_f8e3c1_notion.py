#!/usr/bin/env python3
"""PATCH Notion Plans row for apps-rg-agentic-core-boundary-remediation-child-f8e3c1.

Aligns Summary / AI Summary / Status with on-disk plan after post-W6 carry-forward
close-out. Run from repo root with NOTION_TOKEN (or NOTION_API_KEY).

Disk SSOT: .cursor/plans/apps-rg-agentic-core-boundary-remediation-child-f8e3c1.md
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from tools.notion._wave_lifecycle_helpers import (  # noqa: E402
    PROP_AI_SUMMARY,
    PROP_STATUS,
    PROP_SUMMARY,
    NotionPatchSpec,
    STATUS_COMPLETED,
)
from tools.notion.wave_lifecycle_writer import apply_spec  # noqa: E402

SLUG = "apps-rg-agentic-core-boundary-remediation-child-f8e3c1"

SUMMARY = (
    "TARGETED_SCOPE_PASS: W0–W6 closed (narrow proof). Post-2026-05-15: W3 consolidated "
    "provider slice (section_qwen_slice); C0 trace_map_out + per-section SectionEvidenceTrace; "
    "L0 strict mode + l0_app_agnostic_allowlist.json. Open: G4/WIRING-CI, full _apps_contract, "
    "full run_contract_gates, optional trace consumer wiring."
)

AI_SUMMARY = (
    "- Status: Completed (narrow waves done; O4–O6 still tracked as open on disk)\n"
    "- W3: apps_rg/runtime/providers/section_qwen_slice.py\n"
    "- W4/W7: c0_retrieve_apps_rg(trace_map_out=); bounded section traces\n"
    "- L0: check_l0_app_agnostic.py --strict + baselines/l0_app_agnostic_allowlist.json\n"
    "- Receipt: artifacts/apps_rg/boundary_remediation/w6_targeted_ci_no_regression_f8e3c1.md\n"
    "- Frozen slice: 47/47 (five-module border pytest)\n"
    "- Plan file: .cursor/plans/apps-rg-agentic-core-boundary-remediation-child-f8e3c1.md"
)


def main() -> None:
    spec = NotionPatchSpec(
        slug=SLUG,
        properties={
            PROP_STATUS: {"select": {"name": STATUS_COMPLETED}},
            PROP_SUMMARY: {"rich_text": [{"text": {"content": SUMMARY[:1990]}}]},
            PROP_AI_SUMMARY: {"rich_text": [{"text": {"content": AI_SUMMARY[:1990]}}]},
        },
        summary_append=None,
        reason="disk_notion_sync_post_w6_carryforward",
    )
    ok, msg = apply_spec(spec, dry_run=False)
    if not ok:
        print(f"Notion PATCH failed: {msg}", file=sys.stderr)
        raise SystemExit(1)
    print(f"Notion Plans row updated for slug={SLUG} ({msg}).")


if __name__ == "__main__":
    main()
