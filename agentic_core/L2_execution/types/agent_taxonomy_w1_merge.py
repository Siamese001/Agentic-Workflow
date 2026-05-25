"""Merge ADR-088 spine axes onto taxonomy map (W1 inventory-only registration)."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

from agentic_core.L2_execution.types.agent_taxonomy_spine_axes import (
    AgenthoodStatus,
    InventoryRole,
    ProductSpineInvocationStatus,
    RuntimeProofClass,
    W1_REGISTRATION_DEFAULTS,
)
from agentic_core.L2_execution.types.l2_execution_contract import CanonicalAgentRole

_DATA_PATH = Path(__file__).resolve().parent / "data" / "agentic_core_w1_spine_axes.json"

_LAYER_TO_CANONICAL: dict[str, CanonicalAgentRole] = {
    "L0": CanonicalAgentRole.ROUTER,
    "L1": CanonicalAgentRole.PLANNER,
    "L2": CanonicalAgentRole.EXECUTION,
    "L3": CanonicalAgentRole.ORCHESTRATOR,
    "L5": CanonicalAgentRole.SAFETY,
    "L6": CanonicalAgentRole.OBSERVER,
    "knowledge": CanonicalAgentRole.OBSERVER,
    "base": CanonicalAgentRole.EXECUTION,
    "runtime": CanonicalAgentRole.EXECUTION,
}


def _enum_axes(row: dict[str, str]) -> dict[str, object]:
    return {
        "agenthood_status": AgenthoodStatus[row["agenthood_status"]],
        "inventory_role": InventoryRole[row["inventory_role"]],
        "product_spine_invocation_status": ProductSpineInvocationStatus[
            row["product_spine_invocation_status"]
        ],
        "runtime_proof_class": RuntimeProofClass[row["runtime_proof_class"]],
        "spine_proof_ref": row.get("spine_proof_ref") or "",
    }


def _default_axes_for_apps_entry() -> dict[str, object]:
    return {
        "agenthood_status": AgenthoodStatus.NOT_AGENT,
        "inventory_role": InventoryRole.TRUE_AGENT_NOT_ON_PRODUCT_SPINE,
        "product_spine_invocation_status": W1_REGISTRATION_DEFAULTS[
            "product_spine_invocation_status"
        ],
        "runtime_proof_class": W1_REGISTRATION_DEFAULTS["runtime_proof_class"],
        "spine_proof_ref": "",
    }


def _infer_axes_from_legacy(entry: object) -> dict[str, object]:
    """Best-effort axes for legacy agentic_core rows missing assessment JSON."""
    is_shim = bool(getattr(entry, "is_shim", False))
    status = getattr(entry, "status", None)
    name = str(getattr(entry, "class_name", ""))
    if is_shim or (status is not None and str(status.value) in {"shim", "obsolete", "archived"}):
        agenthood = AgenthoodStatus.SHIM_OR_DEAD_LEGACY
        inventory = InventoryRole.SHIM_OR_DEAD_LEGACY
    elif "Validator" in name:
        agenthood = AgenthoodStatus.NOT_AGENT
        inventory = InventoryRole.GOVERNANCE_CERTIFIER_OR_VALIDATOR
    elif "Healer" in name or "heal" in name.lower():
        agenthood = AgenthoodStatus.TRUE_AGENT
        inventory = InventoryRole.HEALER_OR_DEV_AGENT
    else:
        agenthood = AgenthoodStatus.TRUE_AGENT
        inventory = InventoryRole.TRUE_AGENT_NOT_ON_PRODUCT_SPINE
    return {
        "agenthood_status": agenthood,
        "inventory_role": inventory,
        "product_spine_invocation_status": ProductSpineInvocationStatus.NOT_ARTIFACT_PROVEN,
        "runtime_proof_class": RuntimeProofClass.NONE,
        "spine_proof_ref": "",
    }


def load_agentic_core_w1_rows() -> dict[str, dict[str, str]]:
    if not _DATA_PATH.is_file():
        msg = f"Missing W1 axes data: {_DATA_PATH} — run tools/governance/build_agentic_core_w1_taxonomy_axes.py"
        raise FileNotFoundError(msg)
    doc = json.loads(_DATA_PATH.read_text(encoding="utf-8"))
    return {str(r["class_name"]): r for r in doc.get("rows") or []}


def finalize_taxonomy_map(raw_map: dict) -> dict:
    """Apply W1 axes to all entries; register agentic_core inventory gap fill."""
    from agentic_core.L2_execution.types.agent_taxonomy_registry import (
        AgentClassification,
        AgentStatus,
    )

    w1_rows = load_agentic_core_w1_rows()
    merged: dict[str, AgentClassification] = {}

    for key, entry in raw_map.items():
        file_path = str(getattr(entry, "file_path", ""))
        if file_path.startswith("agentic_core/"):
            row = w1_rows.get(key)
            axes = _enum_axes(row) if row else _infer_axes_from_legacy(entry)
        else:
            axes = _default_axes_for_apps_entry()
        merged[key] = replace(entry, **axes)

    for class_name, row in w1_rows.items():
        if class_name in merged:
            continue
        layer = row.get("declared_layer") or "L5"
        canonical = _LAYER_TO_CANONICAL.get(layer, CanonicalAgentRole.SAFETY)
        is_shim = row["inventory_role"] == InventoryRole.SHIM_OR_DEAD_LEGACY.value
        merged[class_name] = AgentClassification(
            file_path=row["file_path"],
            class_name=class_name,
            current_layer=layer,
            canonical_role=canonical,
            status=AgentStatus.SHIM if is_shim else AgentStatus.ACTIVE,
            is_shim=is_shim,
            implements_l2_contract=layer == "L2",
            notes="W1 inventory-only registration (ADR-088); not product-spine invoked",
            **_enum_axes(row),
        )

    return merged
