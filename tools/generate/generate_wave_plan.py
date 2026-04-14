#!/usr/bin/env python3
"""Generate wave plan for placeholder test conversions."""

from __future__ import annotations

import json
from pathlib import Path
from tempfile import NamedTemporaryFile

WAVE_SIZE = 38
STARTING_WAVE = 13


def _atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as tmp:
        tmp.write(content)
        tmp.flush()
        tmp_path = Path(tmp.name)
    tmp_path.replace(path)


def _atomic_write_json(path: Path, payload: dict[int, dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as tmp:
        json.dump(payload, tmp, indent=2)
        tmp.flush()
        tmp_path = Path(tmp.name)
    tmp_path.replace(path)


def main() -> int:
    repo_root = Path.cwd()
    placeholders_path = repo_root / "remaining_placeholders.json"
    if not placeholders_path.exists():
        raise FileNotFoundError(f"Missing input file: {placeholders_path}")

    all_files = json.loads(placeholders_path.read_text(encoding="utf-8"))
    if not isinstance(all_files, list):
        raise ValueError("remaining_placeholders.json must contain a JSON list")

    waves: dict[int, dict[str, object]] = {}
    wave_num = STARTING_WAVE

    for i in range(0, len(all_files), WAVE_SIZE):
        wave_files = all_files[i : i + WAVE_SIZE]
        waves[wave_num] = {
            "files": wave_files,
            "count": len(wave_files),
        }
        wave_num += 1

    plan_content = f"""# Wave 13-30: Placeholder Test Conversion Plan
## Generated: {repo_root}

## Summary
- **Total Remaining Placeholder Files:** {len(all_files)}
- **Waves Required:** {len(waves)}
- **Files Per Wave:** {WAVE_SIZE}

## Wave Assignments

"""

    for current_wave_num, wave_data in waves.items():
        plan_content += f"### Wave {current_wave_num} ({wave_data['count']} files)\n"
        for file_path in wave_data["files"]:
            plan_content += f"- [ ] `{file_path}`\n"
        plan_content += "\n"

    plan_path = repo_root / "docs" / "reports" / "plans" / "wave_13_30_placeholder_conversion_plan.md"
    _atomic_write_text(plan_path, plan_content)

    assignments_path = repo_root / "wave_assignments.json"
    _atomic_write_json(assignments_path, waves)

    print(f"Plan saved to: {plan_path}")
    print(f"Total waves: {len(waves)}")

    for current_wave_num, wave_data in waves.items():
        print(f"Wave {current_wave_num}: {wave_data['count']} files")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
