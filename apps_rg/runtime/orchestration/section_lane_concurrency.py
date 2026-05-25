"""vLLM-aware Phase-1 lane wave scheduling (plan apps-rg-parallel-section-orchestration-f2a8c4)."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from apps_rg.runtime.internal.generated_lane_rollup import GENERATED_LANES

_MANIFEST_REL = (
    Path("apps_rg") / "config" / "domain_contract" / "workflow_manifest.resume_sections.v1.yaml"
)
_ENV_MAX_PARALLEL = "APPS_RG_PHASE1_MAX_PARALLEL"
_ENV_PARALLEL = "APPS_RG_PARALLEL_PHASE1_LANES"


@dataclass(frozen=True)
class LaneWave:
    wave_id: int
    lanes: tuple[str, ...]
    max_parallel: int


def _repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "pyproject.toml").exists():
            return parent
    return here.parents[4]


def load_section_dag_manifest() -> dict[str, Any]:
    path = _repo_root() / _MANIFEST_REL
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"invalid manifest: {path}")
    return raw


def phase1_parallel_enabled(*, profile_flag: bool = False) -> bool:
    env = str(os.environ.get(_ENV_PARALLEL, "")).strip().lower()
    if env in ("1", "true", "yes", "on"):
        return True
    if env in ("0", "false", "no", "off"):
        return False
    return bool(profile_flag)


def resolve_max_parallel(*, default: int = 2) -> int:
    raw = str(os.environ.get(_ENV_MAX_PARALLEL, "")).strip()
    if raw.isdigit():
        return max(1, min(7, int(raw)))
    return max(1, min(7, default))


def build_phase1_waves() -> tuple[LaneWave, ...]:
    """Ordered waves respecting DAG; wave 0 exec solo when parallel mode on."""
    manifest = load_section_dag_manifest()
    waves_raw = manifest.get("waves") or []
    out: list[LaneWave] = []
    for w in waves_raw:
        if not isinstance(w, dict):
            continue
        wid = int(w.get("id", 0))
        lanes = tuple(str(x) for x in (w.get("lanes") or []) if str(x) in GENERATED_LANES)
        mp = int(w.get("max_parallel", 0) or 0)
        if mp <= 0:
            mp = resolve_max_parallel(default=int(w.get("default_max_parallel", 2) or 2))
        out.append(LaneWave(wave_id=wid, lanes=lanes, max_parallel=mp))
    if not out:
        return (LaneWave(wave_id=1, lanes=GENERATED_LANES, max_parallel=1),)
    return tuple(sorted(out, key=lambda x: x.wave_id))


__all__ = [
    "LaneWave",
    "build_phase1_waves",
    "load_section_dag_manifest",
    "phase1_parallel_enabled",
    "resolve_max_parallel",
]
