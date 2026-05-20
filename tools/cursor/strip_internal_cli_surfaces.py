"""Remove CLI-shaped ``main()`` from internal post-lane helpers."""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
INTERNAL = REPO / "apps_rg/runtime/internal"


def _drop_function(text: str, name: str) -> str:
    pattern = rf"\ndef {name}\([^)]*\)[^:]*:.*?(?=\n(?:def |class |__all__|\Z))"
    return re.sub(pattern, "\n", text, flags=re.S)


def main() -> None:
    for path in INTERNAL.glob("*.py"):
        if path.name == "__init__.py":
            continue
        text = path.read_text(encoding="utf-8")
        text2 = _drop_function(text, "main")
        text2 = re.sub(r"\nif __name__ == [\"']__main__[\"']:\s*\n.*", "\n", text2, flags=re.S)
        if text2 != text:
            path.write_text(text2.rstrip() + "\n", encoding="utf-8")
            print("stripped", path.name)


if __name__ == "__main__":
    main()
