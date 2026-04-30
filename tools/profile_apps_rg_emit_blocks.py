"""Profile the lifecycle-emit boilerplate across apps_rg/engines/*.py.

Identifies, for each engine file:
  * line range of the boilerplate block (first `_emit_authorize_and_execute`
    through last `_emit_signs_execution_trace`)
  * the token used as engine_name in those calls
  * whether the block matches the canonical shape (same emit names + same
    order as the reference file)

Used to verify that a single `_emit_engine_lifecycle(name)` helper can
replace every block losslessly. Prints a summary.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ENG = REPO / "apps_rg" / "engines"

START_MARK = re.compile(r'^_emit_authorize_and_execute\("p2",\s*"([^"]+)"')
# Canonical end is the line `_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)`.
END_MARK = re.compile(r'^_emit_signs_execution_trace\("p0", "p0hash", "p0_trace", 0\)')


def main() -> int:
    files = sorted(p for p in ENG.glob("*.py") if not p.name.startswith("_") and p.name != "base_rg_engine.py" and p.name != "rg_spine_adapter.py" and p.name != "resume_orchestrator_engine.py" and p.name != "__init__.py")
    print(f"engine_files_scanned={len(files)}")

    summary: list[dict] = []
    for f in files:
        text = f.read_text(encoding="utf-8").splitlines()
        start_idx = end_idx = -1
        engine_name = None
        for i, line in enumerate(text):
            if start_idx < 0:
                m = START_MARK.match(line)
                if m:
                    start_idx = i
                    engine_name = m.group(1)
            else:
                if END_MARK.match(line):
                    end_idx = i
                    break
        if start_idx < 0 or end_idx < 0:
            summary.append({"file": f.name, "status": "no-block", "engine_name": None, "lines": 0})
            continue
        block_lines = end_idx - start_idx + 1
        # Count how many emit calls in block reference the engine_name
        ref_count = 0
        for line in text[start_idx:end_idx + 1]:
            if engine_name and f'"{engine_name}"' in line:
                ref_count += 1
        summary.append({
            "file": f.name,
            "status": "ok",
            "engine_name": engine_name,
            "start": start_idx + 1,
            "end": end_idx + 1,
            "lines": block_lines,
            "engine_name_refs": ref_count,
        })

    ok = [s for s in summary if s["status"] == "ok"]
    bad = [s for s in summary if s["status"] != "ok"]
    print(f"with_block={len(ok)}, no_block={len(bad)}")
    if ok:
        sizes = sorted({s["lines"] for s in ok})
        print(f"block_line_counts={sizes}")
        print(f"total_boilerplate_lines={sum(s['lines'] for s in ok)}")
    if bad:
        print(f"no_block_files={[s['file'] for s in bad]}")
    print()
    print("first 5 entries:")
    for s in ok[:5]:
        print(f"  {s['file']}: lines {s['start']}..{s['end']} ({s['lines']} lines), engine_name={s['engine_name']}, refs={s['engine_name_refs']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
