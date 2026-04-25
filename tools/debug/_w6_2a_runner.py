"""Self-contained runner for the W6.2a prefix codemod with guaranteed logging."""

from __future__ import annotations

import sys
import traceback
from pathlib import Path

LOG = Path("artifacts/_w6_2a_runner.log")
LOG.parent.mkdir(parents=True, exist_ok=True)


def main() -> int:
    LOG.write_text("runner start\n", encoding="utf-8")
    try:
        sys.argv = ["ssot_prefix_path_migrator", "--apply"]
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "ssot_prefix_path_migrator",
            Path("tools/migration/ssot_prefix_path_migrator.py"),
        )
        if spec is None or spec.loader is None:
            raise ImportError("could not load ssot_prefix_path_migrator")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        rc = mod.main()
        with LOG.open("a", encoding="utf-8") as f:
            f.write(f"codemod returned {rc}\n")
        return rc
    except SystemExit as exc:
        with LOG.open("a", encoding="utf-8") as f:
            f.write(f"codemod SystemExit code={exc.code}\n")
        return int(exc.code) if isinstance(exc.code, int) else 1
    except (OSError, ImportError, SyntaxError) as exc:
        with LOG.open("a", encoding="utf-8") as f:
            f.write(f"runner failed: {type(exc).__name__}: {exc}\n")
            f.write(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(main())
