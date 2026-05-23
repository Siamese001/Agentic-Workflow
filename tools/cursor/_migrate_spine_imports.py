"""Bulk-update imports from deleted bridge modules to apps_rg.runtime.spine.*."""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
REPLACEMENTS = [
    ("apps_rg.runtime.spine.front_contracts", "apps_rg.runtime.spine.front_contracts"),
    ("apps_rg.runtime.spine.c0_fec_compose", "apps_rg.runtime.spine.c0_fec_compose"),
    ("apps_rg.runtime.spine.exit_artifacts", "apps_rg.runtime.spine.exit_artifacts"),
    ("apps_rg.runtime.spine.exit_lane_hooks", "apps_rg.runtime.spine.exit_lane_hooks"),
    ("apps_rg.runtime.c0.section_proof_loader", "apps_rg.runtime.c0.section_proof_loader"),
    ("wire_spine_c0_fec_for_section", "wire_spine_c0_fec_for_section"),
    ("build_spine_c0_fec_artifact(", "build_spine_c0_fec_artifact("),
    ("emit_spine_c0_fec_artifacts", "emit_spine_c0_fec_artifacts"),
    ("build_spine_c0_fec_receipt", "build_spine_c0_fec_receipt"),
]
SKIP = {".git", "__pycache__", ".venv", "node_modules", "artifacts"}


def main() -> None:
    changed = 0
    for path in REPO.rglob("*.py"):
        if any(part in SKIP for part in path.parts):
            continue
        if path.is_relative_to(REPO / "apps_rg/runtime/spine"):
            continue
        text = path.read_text(encoding="utf-8")
        orig = text
        for old, new in REPLACEMENTS:
            text = text.replace(old, new)
        if text != orig:
            path.write_text(text, encoding="utf-8")
            changed += 1
            print(path.relative_to(REPO))
    print("files_changed", changed)


if __name__ == "__main__":
    main()
