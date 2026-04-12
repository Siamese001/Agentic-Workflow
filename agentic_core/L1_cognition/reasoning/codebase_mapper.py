from __future__ import annotations

import logging

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_signs_execution_trace,
)

"Brief description of functionality and purpose."
"Brief description of functionality and purpose."
import os
from pathlib import Path
from typing import Any

# GLOBAL_EXCLUDED_DIRS, SOVEREIGN_EXCLUDED_FOLDERS imported lazily to avoid L1->L5 violation
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_snapshots_state,
)

LOGGER = logging.getLogger(__name__)
Logger: Any = logging.getLogger(__name__)


class TheCartographer:
    """
    Maps codebases into semantic context for architectural queries.

    Scans:
    - Primary repository root
    - ADDITIONAL_REPO_ROOTS from environment variables
    - Generates file summaries using Gemini
    - Excludes patterns: .git, __pycache__, node_modules, etc.
    """

    def __init__(self, llm_client: Any = None):
        """
        Initialize TheCartographer.

        Args:
            llm_client: LLM client for generating summaries
        """
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "TheCartographer.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "TheCartographer.__init__", "p0_governance")
        self.llm_client = llm_client
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.primary_root = Path.cwd()
        self.additional_roots = self._get_additional_roots()
        self.file_summaries: dict[str, str] = {}
        self = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS

    def _get_additional_roots(self) -> list[Path]:
        """
        Get additional repository roots from environment variables.

        Returns:
            List of additional repository root paths
        """
        roots: list[Path] = []
        env_roots = os.getenv("ADDITIONAL_REPO_ROOTS", "")
        if env_roots:
            for root_path in env_roots.split(","):
                root_path = root_path.strip()
                if root_path:
                    path_obj = Path(root_path)
                    if path_obj.exists():
                        roots.append(path_obj.resolve())
                        LOGGER.info(f"📍 Scanning additional root: {root_path}")
        return roots

    async def map_all_repositories(self) -> dict[str, Any]:
        """
        Map all repositories (primary + additional).

        Returns:
            Dictionary with mapping results
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L1_REASONING,
            "TheCartographer.map_all_repositories",
        )

        LOGGER.info("🗺️  TheCartographer: Beginning semantic mapping")
        results: dict[str, Any] = {
            "primary_root": str(self.primary_root),
            "additional_roots": [str(r) for r in self.additional_roots],
            "files_mapped": 0,
            "summaries_generated": 0,
            "repositories": {},
        }
        primary_result: Any = await self._map_repository(self.primary_root, "primary")
        results["repositories"]["primary"] = primary_result
        results["files_mapped"] += primary_result.get("files_mapped", 0)
        results["summaries_generated"] += primary_result.get("summaries_generated", 0)
        for i, root in enumerate(self.additional_roots):
            repo_name: Any = f"additional_{i + 1}"
            repo_result: Any = await self._map_repository(root, repo_name)
            results["repositories"][repo_name] = repo_result
            results["files_mapped"] += repo_result.get("files_mapped", 0)
            results["summaries_generated"] += repo_result.get("summaries_generated", 0)
        LOGGER.info(f"[OK] TheCartographer: Mapped {results['files_mapped']} files")
        return results

    async def _map_repository(self, root_path: Path, repo_name: str) -> dict[str, Any]:
        """
        Map a single repository.

        Args:
            root_path: Root directory of the repository
            repo_name: Name identifier for the repository

        Returns:
            Mapping result for this repository
        """
        result: dict[str, Any] = {
            "repo_name": repo_name,
            "root_path": str(root_path),
            "files_mapped": 0,
            "summaries_generated": 0,
            "files": [],
        }
        return result
