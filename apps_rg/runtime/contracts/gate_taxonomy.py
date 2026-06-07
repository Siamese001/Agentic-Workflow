"""apps_rg gate taxonomy loader.

Wave 8 classifies gates as release blockers, advisory signals, or debug metrics.
Exact YAML entries win over prefix rules so retired X2 gates can stay debug-only
while active lane X2 gates remain release blockers.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Literal, Mapping

import yaml

GateClass = Literal["release_blocker", "advisory", "debug_metric"]

VALID_GATE_CLASSES: frozenset[str] = frozenset(
    {"release_blocker", "advisory", "debug_metric"}
)
GATE_TAXONOMY_RELPATH = Path("apps_rg/runtime/contracts/apps_rg_gate_taxonomy.yaml")


def _repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "pyproject.toml").exists():
            return parent
    return here.parents[3]


def taxonomy_path() -> Path:
    return _repo_root() / GATE_TAXONOMY_RELPATH


def load_gate_taxonomy(path: Path | None = None) -> dict[str, Any]:
    p = path or taxonomy_path()
    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"gate taxonomy must be a mapping: {p}")
    classes = data.get("classes")
    if not isinstance(classes, dict):
        raise ValueError("gate taxonomy missing classes mapping")
    unknown = set(classes) - VALID_GATE_CLASSES
    if unknown:
        raise ValueError(f"unknown gate classes: {sorted(unknown)}")
    return data


def explicit_gate_classes(taxonomy: Mapping[str, Any] | None = None) -> dict[str, GateClass]:
    data = dict(taxonomy or load_gate_taxonomy())
    out: dict[str, GateClass] = {}
    for row in data.get("explicit_gates") or []:
        if not isinstance(row, Mapping):
            continue
        gate_id = str(row.get("gate_id") or "").strip()
        gate_class = str(row.get("gate_class") or "").strip()
        if not gate_id:
            continue
        if gate_class not in VALID_GATE_CLASSES:
            raise ValueError(f"{gate_id}: invalid gate_class={gate_class!r}")
        out[gate_id] = gate_class  # type: ignore[assignment]
    return out


def classify_gate_id(
    gate_id: str,
    *,
    taxonomy: Mapping[str, Any] | None = None,
) -> GateClass:
    gid = str(gate_id or "").strip()
    if not gid:
        raise ValueError("gate_id is required")
    data = dict(taxonomy or load_gate_taxonomy())
    explicit = explicit_gate_classes(data)
    if gid in explicit:
        return explicit[gid]
    for rule in data.get("prefix_rules") or []:
        if not isinstance(rule, Mapping):
            continue
        prefix = str(rule.get("prefix") or "")
        gate_class = str(rule.get("gate_class") or "")
        if prefix and gid.startswith(prefix):
            if gate_class not in VALID_GATE_CLASSES:
                raise ValueError(f"{prefix}: invalid gate_class={gate_class!r}")
            return gate_class  # type: ignore[return-value]
    raise KeyError(f"unclassified apps_rg gate_id: {gid}")


def is_release_blocker(gate_id: str, *, taxonomy: Mapping[str, Any] | None = None) -> bool:
    return classify_gate_id(gate_id, taxonomy=taxonomy) == "release_blocker"


__all__ = [
    "GATE_TAXONOMY_RELPATH",
    "GateClass",
    "VALID_GATE_CLASSES",
    "classify_gate_id",
    "explicit_gate_classes",
    "is_release_blocker",
    "load_gate_taxonomy",
    "taxonomy_path",
]
