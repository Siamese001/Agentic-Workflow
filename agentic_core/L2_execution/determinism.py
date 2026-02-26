"""Deterministic Phase 5/6 artifact generation.

Provides canonical, reproducible outputs for:
- P5 determinism digest (registry + gateway policy surface)
- Phase 6 fleet inventory artifact (agent_2x2_inventory.json)
- W6 determinism digest (inventory + audited path surface)
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from agentic_core.agents.agent_registry import AGENT_REGISTRY, registry_digest

REPO_ROOT = Path(__file__).resolve().parents[2]
GATEWAY_PATH = REPO_ROOT / "agentic_core" / "L2_execution" / "enforcement" / "SovereignLLMGateway.py"
APPS_LIC_SPECS_PATH = REPO_ROOT / "apps_lic" / "config" / "agent_specs.json"
APPS_RG_SPECS_PATH = REPO_ROOT / "apps_rg" / "config" / "rg_agent_specs.json"
INVENTORY_ARTIFACT_PATH = REPO_ROOT / "artifacts" / "discovery" / "agent_2x2_inventory.json"


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical_json(obj: object) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _file_hash(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def compute_p5_determinism_digest() -> str:
    """Compute stable P5 determinism digest (64-char hex)."""
    allowed_models_map = {
        agent_id: sorted(profile.allowed_models)
        for agent_id, profile in sorted(AGENT_REGISTRY.items())
        if profile.execution_mode.value == "LLM_API"
    }
    allowed_providers_map = {
        agent_id: sorted(profile.allowed_providers)
        for agent_id, profile in sorted(AGENT_REGISTRY.items())
        if profile.execution_mode.value == "LLM_API"
    }
    policy_versions = {
        agent_id: profile.policy_version for agent_id, profile in sorted(AGENT_REGISTRY.items())
    }

    payload = {
        "registry_digest": registry_digest(),
        "allowed_models_map": allowed_models_map,
        "allowed_providers_map": allowed_providers_map,
        "policy_versions": policy_versions,
        "gateway_hash": _file_hash(GATEWAY_PATH),
        "gateway_path": GATEWAY_PATH.relative_to(REPO_ROOT).as_posix(),
    }
    return _sha256_bytes(_canonical_json(payload).encode("utf-8"))


def build_agent_2x2_inventory() -> dict:
    """Build canonical Phase 6 fleet inventory document."""
    lic_specs = _load_json(APPS_LIC_SPECS_PATH)
    rg_specs = _load_json(APPS_RG_SPECS_PATH)

    ssot_agents = [
        {
            "agent_id": agent_id,
            "reasoning_intensity": profile.reasoning_intensity.value,
            "execution_mode": profile.execution_mode.value,
            "allowed_models": sorted(profile.allowed_models),
            "allowed_providers": sorted(profile.allowed_providers),
            "policy_version": profile.policy_version,
        }
        for agent_id, profile in sorted(AGENT_REGISTRY.items())
    ]

    return {
        "ssot_registry_agents": ssot_agents,
        "apps_lic_spec_keys": sorted(lic_specs.keys()),
        "apps_rg_spec_keys": sorted(rg_specs.keys()),
        "counts": {
            "ssot_registry": len(ssot_agents),
            "apps_lic_specs": len(lic_specs),
            "apps_rg_specs": len(rg_specs),
            "fleet_total": len(ssot_agents) + len(lic_specs) + len(rg_specs),
        },
    }


def write_agent_2x2_inventory(path: Path = INVENTORY_ARTIFACT_PATH) -> Path:
    """Write canonical fleet inventory artifact JSON and return file path."""
    path.parent.mkdir(parents=True, exist_ok=True)
    inventory = build_agent_2x2_inventory()
    path.write_text(  # guardian: allow-direct-write
        json.dumps(inventory, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8"
    )
    return path


def compute_w6_determinism_digest() -> str:
    """Compute stable W6 digest from canonical inventory + policy surface."""
    inventory = build_agent_2x2_inventory()
    payload = {
        "inventory": inventory,
        "audited_paths": [
            "agentic_core/L2_execution/enforcement/SovereignLLMGateway.py",
            "agentic_core/L2_execution/healers/healing_tier_router.py",
            "agentic_core/agents/agent_registry.py",
        ],
    }
    return _sha256_bytes(_canonical_json(payload).encode("utf-8"))


def generate_determinism_digest() -> str:
    """Backward-compatible Phase 5 digest API."""
    return f"P5-DETERMINISM-DIGEST: {compute_p5_determinism_digest()}"


__all__ = [
    "build_agent_2x2_inventory",
    "compute_p5_determinism_digest",
    "compute_w6_determinism_digest",
    "generate_determinism_digest",
    "write_agent_2x2_inventory",
]


if __name__ == "__main__":
    artifact_path = write_agent_2x2_inventory()
    print(f"P5-DETERMINISM-DIGEST: {compute_p5_determinism_digest()}")
    print(f"W6-DETERMINISM-DIGEST: {compute_w6_determinism_digest()}")
    print(f"AGENT_2X2_INVENTORY: {artifact_path.relative_to(REPO_ROOT).as_posix()}")
