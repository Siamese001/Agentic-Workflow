"""Canonical entrypoint for apps_qna."""

from __future__ import annotations

import logging
import sys


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    from apps_qna.scripts.run_qna import main as run_main

    return int(run_main())


if __name__ == "__main__":
    raise SystemExit(main())
