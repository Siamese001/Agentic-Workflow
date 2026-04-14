"""
Apply regex-based dependency guardrails to move blocking dependencies out of module scope.
"""

from __future__ import annotations

import argparse
import os
import re
from pathlib import Path

from tqdm import tqdm

MODIFICATIONS = [
    (
        "agentic_core/L4_state/memory/in_memory_vector_cache.py",
        r"import logging\nfrom typing import Any\n\nimport chromadb\n\nLogger",
        "import logging\nfrom typing import Any\n\nLogger",
    ),
    (
        "agentic_core/L4_state/enforcement/trace_event.py",
        r"from dataclasses import dataclass\nfrom typing import Any\n\nimport duckdb\n\nLogger",
        "from dataclasses import dataclass\nfrom typing import Any\n\nLogger",
    ),
    (
        "agentic_core/L4_state/memory/bm25_store.py",
        r"from typing import Any\n\nfrom rank_bm25 import BM25Okapi\n\n\nclass Bm25Store:",
        "from typing import Any\n\n\nclass Bm25Store:",
    ),
    (
        "agentic_core/L2_execution/config/hybrid_retriever_config.py",
        r"from pathlib import Path\nfrom typing import Any\n\nfrom rank_bm25 import BM25Okapi\n\n",
        "from pathlib import Path\nfrom typing import Any\n\n",
    ),
    (
        "apps_shared/types/validation_status_types.py",
        r"import numpy as np\nfrom sklearn\.feature_extraction\.text import TfidfVectorizer\nfrom sklearn\.metrics\.pairwise import cosine_similarity\n\nlogger",
        "import numpy as np\n\nlogger",
    ),
    (
        "agentic_core/L2_execution/reasoning/batch_embedding_service.py",
        r"from typing import Any\n\nimport numpy as np\n\nLogger",
        "from typing import Any\n\nLogger",
    ),
    (
        "agentic_core/L2_execution/reasoning/tool_registry.py",
        r"from typing import Any\n\nimport numpy as np\n\nLogger",
        "from typing import Any\n\nLogger",
    ),
    (
        "agentic_core/L3_orchestration/reasoning/CoverageAgent.py",
        r"from typing import Any\n\nimport numpy as np\nfrom agentic_core",
        "from typing import Any\n\nfrom agentic_core",
    ),
    (
        "agentic_core/runtime/types/cache_entry_types.py",
        r"from typing import Any\n\nimport numpy as np\n\ntry:",
        "from typing import Any\n\ntry:",
    ),
    (
        "agentic_core/L4_state/reasoning/PineconeSovereignAgent.py",
        r"from typing import Any\n\nimport numpy as np\nfrom agentic_core",
        "from typing import Any\n\nfrom agentic_core",
    ),
    (
        "apps_shared/validators/cache_entry_validator.py",
        r"from typing import Any\n\nimport numpy as np\nfrom pydantic",
        "from typing import Any\n\nfrom pydantic",
    ),
    (
        "apps_shared/reasoning/GlobalcacheStrategy.py",
        r"from typing import Any\n\nimport numpy as np\nfrom pydantic",
        "from typing import Any\n\nfrom pydantic",
    ),
]


def _resolve_repo_root(explicit_root: str | None = None) -> Path:
    if explicit_root:
        return Path(explicit_root).expanduser().resolve()
    env_root = os.getenv("AGENTIC_WORKFLOW_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve()
    for candidate in Path(__file__).resolve().parents:
        if (candidate / ".git").exists():
            return candidate
    return Path.cwd().resolve()


def _atomic_write(path: Path, content: str) -> None:
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(content, encoding="utf-8")
    tmp_path.replace(path)


def apply_modifications(project_root: Path, execute: bool = False) -> tuple[int, int, int]:
    modified = 0
    skipped = 0
    missing = 0

    for rel_path, old_pattern, new_pattern in tqdm(MODIFICATIONS, desc="Processing", unit="file"):
        file_path = project_root / rel_path
        if not file_path.exists():
            print(f"SKIP (not found): {rel_path}")
            missing += 1
            continue

        content = file_path.read_text(encoding="utf-8", errors="replace")
        new_content, count = re.subn(old_pattern, new_pattern, content)
        if count == 0:
            print(f"SKIP (no match): {rel_path}")
            skipped += 1
            continue

        if execute:
            _atomic_write(file_path, new_content)
            print(f"MODIFIED: {rel_path} ({count} replacement{'s' if count != 1 else ''})")
        else:
            print(f"WOULD MODIFY: {rel_path} ({count} replacement{'s' if count != 1 else ''})")
        modified += 1

    return modified, skipped, missing


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Apply dependency guardrails by removing selected module-level dependency imports.",
    )
    parser.add_argument("--repo-root", help="Override automatic repository root detection.")
    parser.add_argument("--execute", action="store_true", help="Actually write changes. Default is dry-run.")
    args = parser.parse_args(argv)

    project_root = _resolve_repo_root(args.repo_root)
    print("Applying dependency guardrails..." if args.execute else "Dry run: dependency guardrails...")
    modified, skipped, missing = apply_modifications(project_root, execute=args.execute)
    print("\nSummary:")
    print(f"  Candidate files changed: {modified}")
    print(f"  Skipped (no match):      {skipped}")
    print(f"  Missing files:           {missing}")
    if not args.execute:
        print("\nNo files were written. Re-run with --execute to apply changes.")
    else:
        print("\nDone. Module-level imports removed where regex matches succeeded.")
        print("Note: Type hints using np.ndarray may still need annotation hardening.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
