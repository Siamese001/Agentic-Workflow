"""Deterministic Phase 5/6/HARDEN-MERGE-LOCKDOWN artifact generation.

Provides canonical, reproducible outputs for:
- P5 determinism digest (registry + gateway policy surface)
- Phase 6 fleet inventory artifact (agent_2x2_inventory.json)
- W6 determinism digest (inventory + audited path surface)
- HARDEN-MERGE-LOCKDOWN determinism digest (complete sovereignty surface)
- Provider binding determinism (REQ-413)
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

from agentic_core.agents.types.agent_registry import registry_digest
from agentic_core.L0_routing.config import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
)
from agentic_core.L0_routing.types.determinism_types import SemanticClockSnapshot
from agentic_core.L2_execution.enforcement.provider_binding_determinism import compute_provider_binding_digest
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_records_execution_trace,  # noqa: E402
    record_execution_trace,
)

record_execution_trace("determinism", "determinism_trace")


_emit_records_execution_trace("p0", "evidence", "determinism")
REPO_ROOT = Path(__file__).resolve().parents[2]
GATEWAY_PATH = REPO_ROOT / AGENTIC_CORE_DIR / "L2_execution" / "enforcement" / "SovereignLLMGateway.py"
APPS_LIC_SPECS_PATH = REPO_ROOT / APPS_LIC_DIR / "config" / "agent_specs.json"
APPS_RG_SPECS_PATH = REPO_ROOT / APPS_RG_DIR / "config" / "rg_agent_specs.json"
INVENTORY_ARTIFACT_PATH = REPO_ROOT / "artifacts" / "discovery" / "agent_2x2_inventory.json"


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical_json(obj: object) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _file_hash(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def compute_provider_binding_determinism_digest(
    provider_id: str,
    model_id: str,
    semantic_clock: SemanticClockSnapshot,
    additional_context: dict[str, str] | None = None,
) -> str:
    """Compute provider binding determinism digest (REQ-413).

    Args:
        provider_id: LLM provider identifier
        model_id: Model identifier
        semantic_clock: Current semantic clock snapshot
        additional_context: Optional additional context

    Returns:
        SHA-256 hex digest including provider binding information
    """
    gateway_version = os.getenv("GATEWAY_VERSION", "1.0.0")

    return compute_provider_binding_digest(
        provider_id=provider_id,
        model_id=model_id,
        gateway_version=gateway_version,
        semantic_clock=semantic_clock,
        additional_context=additional_context,
    )


def compute_p5_determinism_digest() -> str:
    """Compute stable P5 determinism digest (64-char hex)."""
    allowed_models_map = {
        agent_id: sorted(profile.allowed_models)
        for agent_id, profile in sorted(AGENT_REGISTRY.items())
        if profile.execution_mode.value == "LLM_API"
    }
    policy_versions = {
        agent_id: getattr(profile, "policy_version", "1.0")
        for agent_id, profile in sorted(AGENT_REGISTRY.items())
    }

    payload = {
        "registry_digest": registry_digest(),
        "allowed_models_map": allowed_models_map,
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
            "policy_version": getattr(profile, "policy_version", "1.0"),
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
        json.dumps(inventory, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
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


def compute_lockdown_determinism_digest() -> str:
    """Compute comprehensive HARDEN-MERGE-LOCKDOWN determinism digest."""
    # Registry hash
    registry_hash_val = registry_digest()

    # Tool inventory hash
    tool_inventory_map = {
        agent_id: {
            "allowed_models": sorted(profile.allowed_models),
            "execution_mode": profile.execution_mode.value,
            "reasoning_intensity": profile.reasoning_intensity.value,
            "policy_version": getattr(profile, "policy_version", "1.0"),
        }
        for agent_id, profile in sorted(AGENT_REGISTRY.items())
    }
    tool_inventory_hash = _sha256_bytes(_canonical_json(tool_inventory_map).encode("utf-8"))

    # Healer registry hash
    healer_registry_path = (
        REPO_ROOT / AGENTIC_CORE_DIR / "L2_execution" / "healers" / "healing_tier_router.py"
    )
    healer_registry_hash = _file_hash(healer_registry_path) if healer_registry_path.exists() else ""

    # Allowlists hash
    allowlists_path = REPO_ROOT / AGENTIC_CORE_DIR / "L2_execution" / "healers" / "tiering_allowlist.py"
    allowlists_hash = _file_hash(allowlists_path) if allowlists_path.exists() else ""

    # Routing ruleset hash
    routing_ruleset = {
        "execution_modes": sorted({profile.execution_mode.value for profile in AGENT_REGISTRY.values()}),
        "policy_versions": sorted(
            {getattr(profile, "policy_version", "1.0") for profile in AGENT_REGISTRY.values()},
        ),
        "reasoning_intensities": sorted(
            {profile.reasoning_intensity.value for profile in AGENT_REGISTRY.values()},
        ),
    }
    routing_ruleset_hash = _sha256_bytes(_canonical_json(routing_ruleset).encode("utf-8"))

    # Embedding pack hash
    embedding_config = get_embedding_config_surface()
    embedding_pack_hash = _sha256_bytes(_canonical_json(embedding_config).encode("utf-8"))

    # Meta-learning config surface hash
    meta_learning_config = get_meta_learning_config_surface()
    meta_learning_hash = _sha256_bytes(_canonical_json(meta_learning_config).encode("utf-8"))

    # Combine all components
    components = {
        "registry_hash": registry_hash_val,
        "tool_inventory_hash": tool_inventory_hash,
        "healer_registry_hash": healer_registry_hash,
        "allowlists_hash": allowlists_hash,
        "routing_ruleset_hash": routing_ruleset_hash,
        "embedding_pack_hash": embedding_pack_hash,
        "meta_learning_config_hash": meta_learning_hash,
    }

    return _sha256_bytes(_canonical_json(components).encode("utf-8"))


def get_embedding_config_surface() -> dict:
    """Get embedding configuration surface for determinism."""
    config = {
        "model_version": "multilingual-e5-large",
        "threads": int(os.environ.get("OMP_NUM_THREADS", "1")),
        "top_k": 20,
        "cutoff": 0.0,
        "enabled": os.environ.get("EMBEDDING_ENABLED", "1") == "1",
    }

    # Add tampering if negative control is active
    if os.environ.get("W_HARDEN_NEGCTRL_TAMPER") == "1":
        config["top_k"] = 999
        config["cutoff"] = 0.999
        config["tampered"] = True

    return config


def get_meta_learning_config_surface() -> dict:
    """Get meta-learning configuration surface for determinism."""
    return {
        "proposal_only": True,  # Default safety setting
        "validators_enabled": True,
        "shadow_evaluator_enabled": True,
        "oscillation_detector_enabled": True,
        "rlhf_delta_min": 0.1,
        "rlhf_delta_max": 2.0,
        "decision_delta_limit": 0.1,
    }


def generate_lockdown_determinism_digest() -> str:
    """Generate HARDEN-MERGE-LOCKDOWN determinism digest with emission format."""
    digest = compute_lockdown_determinism_digest()
    return f"HARDEN-MERGE-LOCKDOWN-DETERMINISM-DIGEST: {digest}"


__all__ = [
    "build_agent_2x2_inventory",
    "compute_p5_determinism_digest",
    "compute_w6_determinism_digest",
    "compute_lockdown_determinism_digest",
    "compute_provider_binding_determinism_digest",
    "generate_determinism_digest",
    "generate_lockdown_determinism_digest",
    "write_agent_2x2_inventory",
    "get_embedding_config_surface",
    "get_meta_learning_config_surface",
]


if __name__ == "__main__":
    artifact_path = write_agent_2x2_inventory()
    print(f"P5-DETERMINISM-DIGEST: {compute_p5_determinism_digest()}")
    print(f"W6-DETERMINISM-DIGEST: {compute_w6_determinism_digest()}")
    print(f"HARDEN-MERGE-LOCKDOWN-DETERMINISM-DIGEST: {compute_lockdown_determinism_digest()}")
    print(f"AGENT_2X2_INVENTORY: {artifact_path.relative_to(REPO_ROOT).as_posix()}")
