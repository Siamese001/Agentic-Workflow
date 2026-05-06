"""Compatibility shim for ADG generator migration.

Deprecated: This module redirects to tools.generate.generate_full_adg.
The ADG generator has moved from tools/adg/ to tools/generate/.

Migration:
    OLD: from tools.adg.generate_full_adg import main
    NEW: from tools.generate.generate_full_adg import main

This shim will be removed in a future release.
"""
import warnings
from pathlib import Path

# Emit deprecation warning on import
warnings.warn(
    "tools.adg.generate_full_adg is deprecated. "
    "Use tools.generate.generate_full_adg instead. "
    "This shim will be removed in a future release.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export from canonical location
try:
    from tools.generate.generate_full_adg import main, generate_full_adg
    
    __all__ = ["main", "generate_full_adg"]
except ImportError as e:
    # If import fails, provide helpful error message
    import sys
    repo_root = Path(__file__).resolve().parents[2]
    canonical_path = repo_root / "tools" / "generate"
    
    if not (canonical_path / "generate_full_adg.py").exists():
        print(
            f"ERROR: ADG generator not found at expected location: {canonical_path}",
            file=sys.stderr,
        )
        print(
            "The ADG generator has been relocated. Please update your imports:",
            file=sys.stderr,
        )
        print("  OLD: tools.adg.generate_full_adg", file=sys.stderr)
        print("  NEW: tools.generate.generate_full_adg", file=sys.stderr)
    
    raise

# For command-line backward compatibility
if __name__ == "__main__":
    main()
