"""Fix all indentation errors - Re-export from fix_all_indentation for compatibility."""

from apps_shared.scripts.fix_all_indentation import (
    fix_all_indentation,
)
from apps_shared.scripts.fix_all_indentation import (
    fix_all_indentation as fix_all_files,
)
from apps_shared.scripts.fix_all_indentation import (
    fix_all_indentation as main,
)

__all__ = ["fix_all_indentation", "fix_all_files", "main"]
