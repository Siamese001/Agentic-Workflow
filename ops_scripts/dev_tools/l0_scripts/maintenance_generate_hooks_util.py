"""Compatibility wrapper that redirects to generate_hooks_util.py with passthrough arguments."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    target = Path(__file__).resolve().with_name("generate_hooks_util.py")
    print("[*] maintenance_generate_hooks_util.py is deprecated. Redirecting to generate_hooks_util.py...")
    result = subprocess.run([sys.executable, str(target), *argv], check=False)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
