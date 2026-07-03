"""apps_rg runtime subpackage."""
from __future__ import annotations

# Re-export the run-output contract so the package surface keeps a direct
# module import edge for ADG graph reachability.
from . import run_output_contract

__all__ = ["run_output_contract"]
