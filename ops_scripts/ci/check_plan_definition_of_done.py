"""PLAN-DOD CI gate — every active plan file must have a `## Definition of Done` section.

Per plan apps-rg-runtime-wiring-completion-d4e8a1 W6 (DoD discipline).

This gate prevents the c8b3e1 failure mode: a plan was marked Completed
without an explicit DoD against which "Completed" could be objectively
falsified. A plan that says "all waves done" but has no DoD-pass-criteria
table cannot be audit-checked. The c8b3e1 plan would have caught its own
non-functional runtime if a DoD row had said "DoD-N: `python -m apps_rg
--dry-run` exit 0".

Scan: `.claude/plans/*.md` (excluding `_archive/`, `_orphan_review/`).
Required: a `## Definition of Done` heading (case-insensitive, accepts
`## Definition of Done` and `## Definitions of Done`) followed by content.

Exit 0 → all active plans have a DoD section.
Exit 1 → at least one plan missing DoD (advisory by default, fail-closed
via PLAN_DOD_GATE_FAIL_CLOSED=1).
Bypass: PLAN_DOD_GATE_BYPASS=1.

Allowlist: plans whose frontmatter contains `dod_exempt: true` are skipped.
This is for legitimate cases (RCA-only plans, doc plans, audit plans where
the DoD is "report written and reviewed").
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
# SSOT: active plans live under `.claude/plans/` (plan-location.mdc). Only
# top-level `*.md` is scanned — not `_archive/` trees — to cap gate cost.
_PLANS_DIR = _REPO_ROOT / ".claude" / "plans"
# Forward-only relocation (plan relocate-plans-ssot-outside-claude-c1a17d):
# canonical NEW plans live in repo-root plans/; .claude/plans/ stays legacy-valid.
_PLANS_DIRS = [_REPO_ROOT / "plans", _PLANS_DIR]
_REPORT_PATH = _REPO_ROOT / "artifacts" / "ci" / "plan_dod_gate.json"

_DOD_HEADING_RE = re.compile(
    # Match `## Definition of Done` with optional leading numbering like
    # `## 10.`, `## §10`, `## W6 —`, etc.
    r"^##\s+(?:[\d§\w]{1,6}[.)\-—:]\s+)?definitions?\s+of\s+done\b",
    re.IGNORECASE | re.MULTILINE,
)
_DOD_EXEMPT_RE = re.compile(
    r"^\s*dod_exempt\s*:\s*true\s*$",
    re.IGNORECASE | re.MULTILINE,
)
_FRONTMATTER_RE = re.compile(r"^---\n(.+?)\n---\n", re.DOTALL)


def _scan_plan_files() -> list[Path]:
    """Return all .md files directly under .claude/plans/ excluding archive subfolders."""
    out: list[Path] = []
    for _d in _PLANS_DIRS:
        if _d.is_dir():
            out.extend(p for p in _d.glob("*.md") if p.is_file())
    return sorted(out)


def _is_exempt(content: str) -> bool:
    fm_match = _FRONTMATTER_RE.match(content)
    if not fm_match:
        return False
    return bool(_DOD_EXEMPT_RE.search(fm_match.group(1)))


def _has_dod_section(content: str) -> bool:
    return bool(_DOD_HEADING_RE.search(content))


def _emit_report(violations: list[dict], scanned: int, exempt: int) -> None:
    _REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    _REPORT_PATH.write_text(
        json.dumps(
            {
                "gate": "PLAN-DOD",
                "plans_scanned": scanned,
                "plans_exempt": exempt,
                "violations_count": len(violations),
                "violations": violations,
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    _ = argv
    if os.environ.get("PLAN_DOD_GATE_BYPASS", "").strip() in ("1", "true", "yes"):
        print("[PLAN-DOD] BYPASS — PLAN_DOD_GATE_BYPASS=1")
        _emit_report([], 0, 0)
        return 0

    fail_closed = os.environ.get("PLAN_DOD_GATE_FAIL_CLOSED", "").strip() in (
        "1",
        "true",
        "yes",
    )

    plans = _scan_plan_files()
    if not plans:
        print(f"[PLAN-DOD] OK — no plans found under {_PLANS_DIR.relative_to(_REPO_ROOT)}")
        _emit_report([], 0, 0)
        return 0

    violations: list[dict] = []
    exempt_count = 0
    for plan in plans:
        try:
            content = plan.read_text(encoding="utf-8")
        except OSError as exc:
            violations.append(
                {
                    "plan": str(plan.relative_to(_REPO_ROOT)).replace("\\", "/"),
                    "reason": f"unreadable: {exc}",
                }
            )
            continue

        if _is_exempt(content):
            exempt_count += 1
            continue

        if not _has_dod_section(content):
            violations.append(
                {
                    "plan": str(plan.relative_to(_REPO_ROOT)).replace("\\", "/"),
                    "reason": "missing `## Definition of Done` heading",
                }
            )

    _emit_report(violations, len(plans), exempt_count)

    if not violations:
        print(
            f"[PLAN-DOD] OK — {len(plans)} plan(s) scanned, {exempt_count} exempt, "
            "0 violations"
        )
        return 0

    print(
        f"[PLAN-DOD] {'FAIL' if fail_closed else 'WARN'} — "
        f"{len(violations)} of {len(plans)} plans missing `## Definition of Done`:"
    )
    for v in violations[:20]:  # cap stdout noise
        print(f"  - {v['plan']}: {v['reason']}")
    if len(violations) > 20:
        print(f"  ... ({len(violations) - 20} more, see {_REPORT_PATH.relative_to(_REPO_ROOT)})")

    return 1 if fail_closed else 0


if __name__ == "__main__":
    sys.exit(main())
