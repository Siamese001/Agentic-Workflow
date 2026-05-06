"""apps_shared.cli — shared CLI helpers for apps_* entrypoints.

The interactive_wizard module provides a TTY-only prompt helper for apps that
have mandatory target inputs that risk silent cross-target contamination if
auto-filled (e.g. apps_rg's company/role/JD).
"""

from apps_shared.cli.interactive_wizard import (
    WizardField,
    read_multiline_or_file,
    run_wizard,
)

__all__ = ["WizardField", "read_multiline_or_file", "run_wizard"]
