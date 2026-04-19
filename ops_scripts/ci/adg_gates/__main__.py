"""Entry point for running as python -m ops_scripts.ci.adg_gates."""

import sys

from ops_scripts.ci.adg_gates.cli import main

if __name__ == "__main__":
    sys.exit(main())
