from __future__ import annotations
# File: config_loader.py
# Description: Centralized config loader for LIC Outreach Engine
# CREATED: 2026-01-01 - Prompt externalization for sovereignty compliance

"""
Config Loader for LIC Outreach Engine.

Provides centralized access to:
- Agent specs (from agentic_core/config/lic_agent_specs.json)
- Prompts (from agentic_core/config/lic_prompts.json)
- Validator rules (from apps_lic/domain/validator_rules.json)

Usage:
    from apps_lic.engines.outreach_engine.config_loader import PROMPTS, AGENT_SPECS
    
    prompt = PROMPTS["research_synthesis"]["template"].format(
        target_company=company,
        gaps=gaps
    )
"""

import json
import os
from pathlib import Path
from typing import Any, Dict

from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    AGENT_DISCOVERY_JSON,
    AGENT_DISCOVERY_MANIFEST_JSON,
    AGENTIC_CORE_DIR,
    SCRIPTS_DIR,
    TESTS_DIR,
    DASHBOARD_DIR,
    L0_MAINTENANCE_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
    L6_OBSERVABILITY_DIR,
    get_validated_project_root,
)

# Resolve config root relative to this file
_THIS_DIR = Path(__file__).parent
_REPO_ROOT = _THIS_DIR.parent.parent.parent.parent  # apps_lic/engines/outreach_engine -> repo root
_CONFIG_ROOT = _REPO_ROOT / AGENTIC_CORE_DIR / "config"
_DOMAIN_ROOT = _THIS_DIR.parent.parent / "domain"  # apps_lic/domain


def _load_json(path: Path) -> Dict[str, Any]:
    """Load JSON file with error handling."""
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_prompts() -> Dict[str, Any]:
    """Load LIC prompts from agentic_core/config/lic_prompts.json."""
    config_path = os.getenv("LIC_PROMPTS_PATH", str(_CONFIG_ROOT / "lic_prompts.json"))
    return _load_json(Path(config_path))


def load_agent_specs() -> Dict[str, Any]:
    """Load LIC agent specs from agentic_core/config/lic_agent_specs.json."""
    config_path = os.getenv("LIC_AGENT_SPECS_PATH", str(_CONFIG_ROOT / "lic_agent_specs.json"))
    return _load_json(Path(config_path))


def load_validator_rules() -> Dict[str, Any]:
    """Load LIC validator rules from apps_lic/domain/validator_rules.json."""
    config_path = os.getenv("LIC_VALIDATOR_RULES_PATH", str(_DOMAIN_ROOT / "validator_rules.json"))
    return _load_json(Path(config_path))


# Lazy-loaded singletons (load on first access)
_PROMPTS: Dict[str, Any] = None
_AGENT_SPECS: Dict[str, Any] = None
_VALIDATOR_RULES: Dict[str, Any] = None


def get_prompts() -> Dict[str, Any]:
    """Get prompts (lazy-loaded singleton)."""
    global _PROMPTS
    if _PROMPTS is None:
        _PROMPTS = load_prompts()
    return _PROMPTS


def get_agent_specs() -> Dict[str, Any]:
    """Get agent specs (lazy-loaded singleton)."""
    global _AGENT_SPECS
    if _AGENT_SPECS is None:
        _AGENT_SPECS = load_agent_specs()
    return _AGENT_SPECS


def get_validator_rules() -> Dict[str, Any]:
    """Get validator rules (lazy-loaded singleton)."""
    global _VALIDATOR_RULES
    if _VALIDATOR_RULES is None:
        _VALIDATOR_RULES = load_validator_rules()
    return _VALIDATOR_RULES


# Convenient module-level access (lazy-loaded on first access)
PROMPTS = property(lambda self: get_prompts())
AGENT_SPECS = property(lambda self: get_agent_specs())
VALIDATOR_RULES = property(lambda self: get_validator_rules())


# For direct imports (loads immediately)
def init_configs():
    """Pre-load all configs. Call at application startup if needed."""
    global _PROMPTS, _AGENT_SPECS, _VALIDATOR_RULES
    _PROMPTS = load_prompts()
    _AGENT_SPECS = load_agent_specs()
    _VALIDATOR_RULES = load_validator_rules()
    return {
        "prompts": _PROMPTS,
        "agent_specs": _AGENT_SPECS,
        "validator_rules": _VALIDATOR_RULES,
    }
