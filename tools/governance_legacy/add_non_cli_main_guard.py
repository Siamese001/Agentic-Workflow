"""Insert top-of-file guard: ``python -m`` raises ImportError (not a runnable CLI)."""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

GUARD = '''
if __name__ == "__main__":
    raise ImportError(
        "This module is not an operator CLI entrypoint. "
        "Use: python -m apps_rg or python -m apps_rg --section <lane>"
    )

'''

TARGET_DIRS = (
    REPO / "apps_rg/runtime/internal",
    REPO / "apps_rg/runtime/sections",
)

TARGET_SUFFIXES = ("_lane_api.py",)


def main() -> None:
    for base in TARGET_DIRS:
        if not base.is_dir():
            continue
        for path in base.glob("*.py"):
            if path.name == "__init__.py":
                continue
            if base.name == "sections" and not path.name.endswith("_lane_api.py"):
                continue
            text = path.read_text(encoding="utf-8")
            if 'if __name__ == "__main__"' in text or "if __name__ == '__main__'" in text:
                continue
            if "not an operator CLI entrypoint" in text:
                continue
            # After module docstring / __future__
            lines = text.splitlines(keepends=True)
            insert_at = 0
            if lines and lines[0].startswith('"""'):
                for i, line in enumerate(lines[1:], 1):
                    if line.strip().endswith('"""'):
                        insert_at = i + 1
                        break
            if insert_at < len(lines) and "from __future__" in lines[insert_at]:
                insert_at += 1
            new_text = "".join(lines[:insert_at]) + GUARD + "".join(lines[insert_at:])
            path.write_text(new_text, encoding="utf-8")
            print("guarded", path.relative_to(REPO).as_posix())


if __name__ == "__main__":
    main()
