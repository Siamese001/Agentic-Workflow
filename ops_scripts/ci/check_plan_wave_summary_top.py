"""PLAN-WAVE-TOP CI gate — consolidated wave + phase summary at top, in execution order.

Requires (for ``plan_format: v2`` plans) ``## Status Tables`` → ``### Wave Progress`` (canonical
7 columns) AND ``### Phase Progress`` summary tables **before** the first ``## Wave N`` detail
section, and waves numbered in ascending execution order with no backward dependency.

Scan: ``plans/*.md`` + ``.codex/plans/*.md`` (top-level only; excludes ``_archive/`` trees).

Enforce-going-forward: v2 plans (the template carries the marker) are enforced — any FAIL → exit 1.
Legacy plans (no marker) are grandfathered to advisory WARN unless
``PLAN_WAVE_SUMMARY_TOP_FAIL_CLOSED=1`` forces strict on them too.
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
    is_plan_format_v2,
    is_plan_wave_summary_exempt,
    validate_plan_format,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_PLANS_DIR = _REPO_ROOT / ".codex" / "plans"
# Forward-only relocation (plan relocate-plans-ssot-outside-claude-c1a17d):
# canonical NEW plans live in repo-root plans/; .codex/plans/ stays legacy-valid.
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

    # Legacy plans (no `plan_format: v2` marker) are grandfathered to advisory WARN unless this env
    # forces strict on them too. v2 plans always block (enforce going forward — user directive).
    legacy_fail_closed = os.environ.get("PLAN_WAVE_SUMMARY_TOP_FAIL_CLOSED", "").strip() in (
        "1",
        "true",
        "yes",
    )

    plans = _scan_plan_files()
    if not plans:
        print(f"[PLAN-WAVE-TOP] OK — no plans found under {_PLANS_DIR.relative_to(_REPO_ROOT)}")
        _emit_report([], 0, 0)
        return 0

    blocking: list[dict] = []  # v2 plan FAILs — block by default
    advisory: list[dict] = []  # legacy plan FAILs — WARN unless legacy_fail_closed
    exempt_count = 0
    for plan in plans:
        rel = str(plan.relative_to(_REPO_ROOT)).replace("\\", "/")
        try:
            content = plan.read_text(encoding="utf-8")
        except OSError as exc:
            advisory.append({"plan": rel, "rule_id": "READ-ERROR", "reason": f"unreadable: {exc}"})
            continue

        if not content.strip():
            continue
        if is_plan_wave_summary_exempt(content, rel):
            exempt_count += 1
            continue

        v2 = is_plan_format_v2(content)
        fail_wvs = [
            w for w in validate_plan_format(content, rel) if w.severity == WaveSummarySeverity.FAIL
        ]
        bucket = blocking if v2 else advisory
        for w in fail_wvs:
            bucket.append(
                {
                    "plan": rel,
                    "rule_id": w.rule_id,
                    "line": w.line_num,
                    "reason": w.message,
                    "format": "v2" if v2 else "legacy",
                }
            )

    _emit_report(blocking + advisory, len(plans), exempt_count)

    if not blocking and not advisory:
        print(
            f"[PLAN-WAVE-TOP] OK — {len(plans)} plan(s) scanned, {exempt_count} exempt, "
            "0 FAIL violations"
        )
        return 0

    if blocking:
        print(
            f"[PLAN-WAVE-TOP] FAIL — {len(blocking)} violation(s) in v2 plans (enforced going forward):"
        )
        for v in blocking[:25]:
            print(f"  - {v['plan']}:{v.get('line', '?')} [{v['rule_id']}] {v['reason']}")
    if advisory:
        label = "FAIL" if legacy_fail_closed else "WARN"
        print(
            f"[PLAN-WAVE-TOP] {label} — {len(advisory)} violation(s) in legacy plans "
            "(grandfathered; set PLAN_WAVE_SUMMARY_TOP_FAIL_CLOSED=1 to enforce):"
        )
        for v in advisory[:25]:
            print(f"  - {v['plan']}:{v.get('line', '?')} [{v['rule_id']}] {v['reason']}")

    if blocking:
        return 1
    if advisory and legacy_fail_closed:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
