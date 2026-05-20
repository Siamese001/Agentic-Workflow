"""One-off: remove ``if __name__ == '__main__'`` tails from shadow runtime modules."""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def strip_main_block(text: str) -> str:
    marker = re.search(r'\nif __name__ == ["\']__main__["\']:\s*\n', text)
    if not marker:
        return text
    return text[: marker.start()] + "\n"


def main() -> None:
    paths = list((REPO / "apps_rg/runtime/_offline").glob("*.py"))
    paths += list((REPO / "apps_rg/runtime/dispatch").glob("*_dispatch.py"))
    for path in paths:
        if path.name == "__init__.py":
            continue
        orig = path.read_text(encoding="utf-8")
        new = strip_main_block(orig.rstrip() + "\n")
        if new != orig:
            path.write_text(new, encoding="utf-8")
            print(f"stripped {path.relative_to(REPO).as_posix()}")

    headline = REPO / "apps_rg/runtime/dispatch/headline_dispatch.py"
    if headline.is_file():
        headline.unlink()
        print(f"deleted {headline.relative_to(REPO).as_posix()}")


if __name__ == "__main__":
    main()
