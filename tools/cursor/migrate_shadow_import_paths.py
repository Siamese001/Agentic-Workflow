"""One-shot import path migration: _offline -> internal, dispatch -> sections lane_api."""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

DISPATCH_SUBS = [
    ("apps_rg.runtime.dispatch.executive_summary_dispatch", "apps_rg.runtime.sections.executive_summary_lane_api"),
    ("apps_rg.runtime.dispatch.competencies_dispatch", "apps_rg.runtime.sections.competencies_lane_api"),
    ("apps_rg.runtime.dispatch.unify_bullets_dispatch", "apps_rg.runtime.sections.unify_bullets_lane_api"),
    ("apps_rg.runtime.dispatch.unify_narrative_dispatch", "apps_rg.runtime.sections.unify_narrative_lane_api"),
    ("apps_rg.runtime.dispatch.ibm_narrative_dispatch", "apps_rg.runtime.sections.ibm_narrative_lane_api"),
    ("apps_rg.runtime.dispatch.ibm_bullets_dispatch", "apps_rg.runtime.sections.ibm_bullets_lane_api"),
    ("apps_rg/runtime/dispatch/executive_summary_dispatch.py", "apps_rg/runtime/sections/executive_summary_lane_api.py"),
    ("apps_rg/runtime/dispatch/competencies_dispatch.py", "apps_rg/runtime/sections/competencies_lane_api.py"),
    ("apps_rg/runtime/dispatch/unify_bullets_dispatch.py", "apps_rg/runtime/sections/unify_bullets_lane_api.py"),
    ("apps_rg/runtime/dispatch/unify_narrative_dispatch.py", "apps_rg/runtime/sections/unify_narrative_lane_api.py"),
    ("apps_rg/runtime/dispatch/ibm_narrative_dispatch.py", "apps_rg/runtime/sections/ibm_narrative_lane_api.py"),
    ("apps_rg/runtime/dispatch/ibm_bullets_dispatch.py", "apps_rg/runtime/sections/ibm_bullets_lane_api.py"),
]

OFFLINE_SUBS = [
    ("apps_rg.runtime._offline", "apps_rg.runtime.internal"),
    ("apps_rg/runtime/_offline/", "apps_rg/runtime/internal/"),
]


def main() -> None:
    subs = OFFLINE_SUBS + DISPATCH_SUBS
    skip = {".git", "__pycache__", ".pytest_cache", "node_modules"}
    count = 0
    for path in REPO.rglob("*"):
        if not path.is_file() or path.suffix not in {".py", ".md", ".mdc", ".yml", ".json"}:
            continue
        if any(s in path.parts for s in skip):
            continue
        if "migrate_shadow_import_paths.py" in path.name:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        orig = text
        for a, b in subs:
            text = text.replace(a, b)
        if text != orig:
            path.write_text(text, encoding="utf-8")
            count += 1
    print("files_updated", count)


if __name__ == "__main__":
    main()
