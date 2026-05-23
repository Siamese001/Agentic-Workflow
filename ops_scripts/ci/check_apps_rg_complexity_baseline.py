"""W5.0 — diff live complexity audit vs committed baseline (no auto-update)."""

from __future__ import annotations

import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

_BASELINE_PATH = (
    _REPO / "tests" / "unit" / "apps_rg" / "section_rigor" / "fixtures" / "complexity_baseline.json"
)
_ALLOWLIST_PATH = (
    _REPO / "tests" / "unit" / "apps_rg" / "section_rigor" / "fixtures" / "complexity_allowlist.json"
)


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _section_map(doc: dict) -> dict[str, dict]:
    return {str(s["section_id"]): s for s in doc.get("sections") or []}


def _module_map(doc: dict) -> dict[str, dict]:
    return {str(m["module_path"]): m for m in doc.get("modules") or []}


def run_check() -> dict:
    from ops_scripts.apps_rg.section_complexity_reduction_audit import export_complexity_baseline_snapshot

    baseline = _load_json(_BASELINE_PATH)
    live = export_complexity_baseline_snapshot()
    allowlist_doc = _load_json(_ALLOWLIST_PATH) if _ALLOWLIST_PATH.is_file() else {"entries": []}
    allow_by_path = {str(e["module_path"]): e for e in allowlist_doc.get("entries") or []}

    base_sec = _section_map(baseline)
    live_sec = _section_map(live)
    base_mod = _module_map(baseline)
    live_mod = _module_map(live)

    loc_delta: dict[str, int] = {}
    module_delta: dict[str, int] = {}
    new_modules: list[str] = []
    removed_modules: list[str] = []
    allowlist_hits: list[str] = []
    allowlist_expired: list[str] = []
    decisive_failures: list[str] = []
    changed_sections: list[str] = []

    today = date.today()

    for sid in sorted(set(base_sec) | set(live_sec)):
        b = base_sec.get(sid, {})
        l = live_sec.get(sid, {})
        d_loc = int(l.get("tagged_runtime_loc", 0)) - int(b.get("tagged_runtime_loc", 0))
        d_mod = int(l.get("module_count", 0)) - int(b.get("module_count", 0))
        if d_loc or d_mod:
            changed_sections.append(sid)
            loc_delta[sid] = d_loc
            module_delta[sid] = d_mod
        max_loc = int((baseline.get("thresholds") or {}).get("loc_increase_max", 0))
        max_mod = int((baseline.get("thresholds") or {}).get("module_count_increase_max", 0))
        if d_loc > max_loc:
            decisive_failures.append(f"{sid}:loc_delta={d_loc}>{max_loc}")
        if d_mod > max_mod:
            decisive_failures.append(f"{sid}:module_count_delta={d_mod}>{max_mod}")

    for path in sorted(set(live_mod) - set(base_mod)):
        entry = allow_by_path.get(path)
        if entry:
            allowlist_hits.append(path)
            review_after = str(entry.get("review_after") or "").strip()
            if review_after:
                try:
                    exp = date.fromisoformat(review_after)
                    if exp < today:
                        allowlist_expired.append(path)
                        decisive_failures.append(f"allowlist_expired:{path}")
                except ValueError:
                    decisive_failures.append(f"allowlist_bad_date:{path}")
        else:
            new_modules.append(path)
            decisive_failures.append(f"new_module_without_allowlist:{path}")

    for path in sorted(set(base_mod) - set(live_mod)):
        removed_modules.append(path)
        decisive_failures.append(f"removed_module_still_in_registry:{path}")

    status = "FAIL" if decisive_failures else "PASS"
    return {
        "STATUS": status,
        "changed_sections": changed_sections,
        "loc_delta_by_section": loc_delta,
        "module_delta_by_section": module_delta,
        "new_modules": new_modules,
        "removed_modules": removed_modules,
        "allowlist_hits": allowlist_hits,
        "allowlist_expired": allowlist_expired,
        "decisive_failures": decisive_failures,
    }


def main() -> int:
    if not _BASELINE_PATH.is_file():
        print(json.dumps({"STATUS": "BLOCKED", "decisive_failures": ["missing_baseline_fixture"]}, indent=2))
        return 2
    report = run_check()
    print(json.dumps(report, indent=2))
    return 0 if report["STATUS"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
