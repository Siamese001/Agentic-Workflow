"""Entry point for ``python -m agentic_core.runtime.prove_requirements``."""

from __future__ import annotations

import sys

from agentic_core.runtime.prove_requirements.cli import main


if __name__ == "__main__":
    sys.exit(main())
