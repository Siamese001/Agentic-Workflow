"""Lane batch constants and repo-root helpers — offline orchestration is test-only.

``run_orchestration`` lives in ``tests.helpers.offline_lane_orchestration`` (not product proof).
"""
from __future__ import annotations

if __name__ == "__main__":
    raise ImportError(
        "This module is not an operator CLI entrypoint. "
        "Use: python -m apps_rg or python -m apps_rg --section <lane>"
    )

from pathlib import Path

from apps_rg.l2_recipe.modular_resume_generation import LANE_DISPATCH_MODULES
from apps_rg.runtime.internal.generated_lane_rollup import GENERATED_LANES

RUNTIME_PROOFS = "artifacts/apps_rg/runtime_proofs"
PLANNED_DOCX_REL = f"{RUNTIME_PROOFS}/docx/amit_ayer_resume_v1.docx"
POINTER_PATH = Path("apps_rg/resume/base/active_base_resume_pointer.json")
CANONICAL_BASE_RESUME_REPO_REL = Path("apps_rg/resume/base/amit_ayer_base_resume_v1.json")

LANE_MODULES: tuple[str, ...] = LANE_DISPATCH_MODULES
SECTION_ORDER: tuple[str, ...] = GENERATED_LANES


def find_repo_root(start: Path | None = None) -> Path:
    here = (start or Path(__file__)).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "apps_rg" / "resume" / "base").exists():
            return parent
    return Path.cwd()


def resolve_effective_base_resume(repo: Path, base_resume_override: Path | None) -> tuple[Path, bool]:
    rr = repo.resolve()
    if base_resume_override is None:
        return (rr / CANONICAL_BASE_RESUME_REPO_REL).resolve(), True
    cand = base_resume_override if base_resume_override.is_absolute() else (rr / base_resume_override)
    return cand.resolve(), False


def run_orchestration(*_args: object, **_kwargs: object) -> None:
    """Retired from product runtime — use tests.helpers.offline_lane_orchestration."""
    raise ImportError(
        "apps_rg.runtime.internal.lane_batch.run_orchestration is retired. "
        "Use tests.helpers.offline_lane_orchestration.run_orchestration in tests only."
    )


__all__ = [
    "CANONICAL_BASE_RESUME_REPO_REL",
    "LANE_MODULES",
    "PLANNED_DOCX_REL",
    "POINTER_PATH",
    "RUNTIME_PROOFS",
    "SECTION_ORDER",
    "find_repo_root",
    "resolve_effective_base_resume",
    "run_orchestration",
]
