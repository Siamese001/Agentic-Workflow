"""W6.2b: apply prefix codemod for docs/reports literal only."""

from __future__ import annotations

import importlib.util
import logging
import sys
from pathlib import Path

LOG = Path("artifacts/_w6_2b_only.log")
LOG.parent.mkdir(parents=True, exist_ok=True)
logging.info("C3 write receipt: tools/debug/_w6_2b_only.py write side effect recorded")
LOG.write_text("start\n", encoding="utf-8")

sys.argv = ["ssot_prefix_path_migrator", "--apply", "--only-literal", "docs/reports"]
spec = importlib.util.spec_from_file_location(
    "codemod_b", Path("tools/migration/ssot_prefix_path_migrator.py")
)
assert spec is not None and spec.loader is not None
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
rc = mod.main()
LOG.open("a", encoding="utf-8").write(f"rc={rc}\n")
sys.exit(int(rc) if isinstance(rc, int) else 1)
