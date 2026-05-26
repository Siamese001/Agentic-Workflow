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


def assert_section_dag_wave_order(manifest: dict[str, Any]) -> None:
    """Every lane ``depends_on`` must appear in a strictly earlier wave than the dependent lane."""
    lanes_raw = manifest.get("lanes") or []
    lane_meta: dict[str, dict[str, Any]] = {}
    for entry in lanes_raw:
        if not isinstance(entry, dict):
            continue
        lid = str(entry.get("id") or "").strip()
        if lid:
            lane_meta[lid] = entry

    lane_wave: dict[str, int] = {}
    for wave in manifest.get("waves") or []:
        if not isinstance(wave, dict):
            continue
        wid = int(wave.get("id", 0))
        for lane_id in wave.get("lanes") or []:
            lane_wave[str(lane_id)] = wid

    for lane_id, entry in lane_meta.items():
        for dep in entry.get("depends_on") or []:
            dep_id = str(dep).strip()
            if dep_id not in lane_meta:
                raise ValueError(f"lane '{lane_id}' depends_on unknown lane '{dep_id}'")
            w_lane = lane_wave.get(lane_id)
            w_dep = lane_wave.get(dep_id)
            if w_lane is None:
                raise ValueError(f"lane '{lane_id}' missing from waves schedule")
            if w_dep is None:
                raise ValueError(f"lane '{lane_id}' depends_on '{dep_id}' missing from waves schedule")
            if w_dep >= w_lane:
                raise ValueError(
                    f"lane '{lane_id}' (wave {w_lane}) must run after '{dep_id}' (wave {w_dep})"
                )


def build_phase1_waves() -> tuple[LaneWave, ...]:
    """Ordered waves respecting DAG; wave 0 exec solo when parallel mode on."""
    manifest = load_section_dag_manifest()
    assert_section_dag_wave_order(manifest)
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
    "assert_section_dag_wave_order",
    "build_phase1_waves",
    "load_section_dag_manifest",
    "phase1_parallel_enabled",
    "resolve_max_parallel",
]
