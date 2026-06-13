"""Remove ``main`` / ``run_dispatch`` from legacy lane dispatch modules."""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def _drop_function(text: str, name: str) -> str:
    pattern = rf"\ndef {name}\([^)]*\)[^:]*:.*?(?=\n(?:def |class |__all__|\Z))"
    return re.sub(pattern, "\n", text, flags=re.S)


def main() -> None:
    for path in (REPO / "apps_rg/runtime/dispatch").glob("*_dispatch.py"):
        if path.name == "apps_rg_dispatch.py":
            continue
        text = path.read_text(encoding="utf-8")
        text2 = _drop_function(text, "main")
        text2 = _drop_function(text2, "run_dispatch")
        for token in ('"main",', "'main',", '"run_dispatch",', "'run_dispatch',"):
            text2 = text2.replace(token, "")
        if text2 != text:
            path.write_text(text2, encoding="utf-8")
            print(f"trimmed {path.name}")


if __name__ == "__main__":
    main()
