"""PLAN-WAVE-TOP CI gate — consolidated wave summary at top of every active plan.

Requires ``## Status Tables`` → ``### Wave Progress`` with a wave summary markdown
table (Wave, Focus, Status minimum; canonical 7 columns advised) **before** the first
``## Wave N`` detail section.

Scan: ``.claude/plans/*.md`` (top-level only; excludes ``_archive/`` trees).

Exit 0 → all active non-exempt plans comply (or advisory WARN only).
Exit 1 → violations when ``PLAN_WAVE_SUMMARY_TOP_FAIL_CLOSED=1``.
Bypass: ``PLAN_WAVE_SUMMARY_TOP_BYPASS=1``.

Allowlist: ``dod_exempt: true`` frontmatter (same as PLAN-DOD).
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

from ops_scripts.ci.plan_wave_summary_top import (
    WaveSummarySeverity,
    validate_consolidated_wave_summary_at_top,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_PLANS_DIR = _REPO_ROOT / ".claude" / "plans"
# Forward-only relocation (plan relocate-plans-ssot-outside-claude-c1a17d):
# canonical NEW plans live in repo-root plans/; .claude/plans/ stays legacy-valid.
_PLANS_DIRS = [_REPO_ROOT / "plans", _PLANS_DIR]
_REPORT_PATH = _REPO_ROOT / "artifacts" / "ci" / "plan_wave_summary_top_gate.json"


_PLAN_STEM_RE = re.compile(r"^[A-Za-z0-9_\-]+-[0-9a-f]{6}$", re.IGNORECASE)


def _scan_plan_files() -> list[Path]:
    out: list[Path] = []
    for p in sorted(p for _d in _PLANS_DIRS if _d.is_dir() for p in _d.glob("*.md")):
        if not p.is_file():
            continue
        stem = p.stem
        if stem.upper().endswith("_TEMPLATE") or stem.upper().endswith("TEMPLATE"):
            continue
        if not _PLAN_STEM_RE.match(stem):
            continue
        out.append(p)
    return out


def _emit_report(violations: list[dict], scanned: int, exempt: int) -> None:
    _REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    _REPORT_PATH.write_text(
        json.dumps(
            {
                "gate": "PLAN-WAVE-TOP",
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
    if os.environ.get("PLAN_WAVE_SUMMARY_TOP_BYPASS", "").strip() in ("1", "true", "yes"):
        print("[PLAN-WAVE-TOP] BYPASS — PLAN_WAVE_SUMMARY_TOP_BYPASS=1")
        _emit_report([], 0, 0)
        return 0

    fail_closed = os.environ.get("PLAN_WAVE_SUMMARY_TOP_FAIL_CLOSED", "").strip() in (
        "1",
        "true",
        "yes",
    )

    plans = _scan_plan_files()
    if not plans:
        print(f"[PLAN-WAVE-TOP] OK — no plans found under {_PLANS_DIR.relative_to(_REPO_ROOT)}")
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
                    "rule_id": "READ-ERROR",
                    "reason": f"unreadable: {exc}",
                }
            )
            continue

        rel = str(plan.relative_to(_REPO_ROOT)).replace("\\", "/")
        wvs = validate_consolidated_wave_summary_at_top(content, rel)
        if not wvs and not content.strip():
            continue

        # Exempt plans produce empty violation list from validator
        from ops_scripts.ci.plan_wave_summary_top import is_plan_wave_summary_exempt

        if is_plan_wave_summary_exempt(content, rel):
            exempt_count += 1
            continue

        fail_wvs = [w for w in wvs if w.severity == WaveSummarySeverity.FAIL]
        if fail_wvs:
            for w in fail_wvs:
                violations.append(
                    {
                        "plan": rel,
                        "rule_id": w.rule_id,
                        "line": w.line_num,
                        "reason": w.message,
                    }
                )

    _emit_report(violations, len(plans), exempt_count)

    if not violations:
        print(
            f"[PLAN-WAVE-TOP] OK — {len(plans)} plan(s) scanned, {exempt_count} exempt, "
            "0 FAIL violations"
        )
        return 0

    print(
        f"[PLAN-WAVE-TOP] {'FAIL' if fail_closed else 'WARN'} — "
        f"{len(violations)} violation(s) across active plans:"
    )
    for v in violations[:25]:
        print(f"  - {v['plan']}:{v.get('line', '?')} [{v['rule_id']}] {v['reason']}")
    if len(violations) > 25:
        print(f"  ... ({len(violations) - 25} more, see {_REPORT_PATH.relative_to(_REPO_ROOT)})")

    return 1 if fail_closed else 0


if __name__ == "__main__":
    raise SystemExit(main())
