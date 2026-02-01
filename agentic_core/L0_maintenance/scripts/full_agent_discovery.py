#!/usr/bin/env python3
"""
Full Agent Discovery Script - SSOT Compliant Implementation

COMPLETE SSOT REFACTOR: All directory constants and paths MUST be imported
from structure_blueprint.py. NO hardcoded strings allowed.

This script serves as the canonical entry point for agent discovery operations.
It delegates all core functionality to the SSOT discovery utility and provides
standardized interfaces for compliance checking and agent enumeration.

SSOT PRINCIPLE: structure_blueprint.py is the absolute authority for paths/constants.
All agent discovery operations must use ssot_discovery.py as the single source of truth.

USAGE:
    python -m agentic_core.L0_maintenance.scripts.full_agent_discovery

    # Or programmatically:
    from agentic_core.L0_maintenance.scripts.full_agent_discovery import (
        discover_all_agents,
        check_compliance_gate,
        get_agent_discovery_summary,
    )

    agents = discover_all_agents()
    is_compliant = check_compliance_gate()
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
import json
from typing import Any, Dict, List

# CRITICAL SSOT Imports - ALL directory constants MUST come from structure_blueprint.py
from agentic_core.L5_safety.validators.structure_blueprint import (
    AGENT_DISCOVERY_JSON,
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    L0_MAINTENANCE_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
    L6_OBSERVABILITY_DIR,
    get_validated_project_root,
    validate_path_within_project,
)
from agentic_core.utils.ssot_discovery import (
    get_agent_by_name,
    get_agents_by_layer,
    get_healers,
    invalidate_cache,
    load_agent_discovery,
)

# Standard error logging wrapper configuration
Logger = logging.getLogger(__name__)


# Standardized error handling pattern for repo scripts
class DiscoveryError(Exception):
    """Custom exception for agent discovery operations."""

    pass


def setup_logging(verbose: bool = False) -> None:
    """
    Standard logging configuration wrapper.

    Args:
        verbose: Enable debug-level logging if True.
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="[%(asctime)s] %(levelname)s [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def main() -> bool:
    """
    Main entry point for agent discovery operations.

    Performs comprehensive agent discovery and compliance validation.
    Uses SSOT discovery utility for all core operations.

    Returns:
        bool: True if discovery completed successfully, False otherwise.

    Raises:
        DiscoveryError: If critical discovery operations fail.
    """
    try:
        # Get validated project root from SSOT
        project_root = get_validated_project_root()
        Logger.info(f"[DISCOVERY] Starting agent discovery from: {project_root}")

        # Validate project root integrity
        if not validate_path_within_project(project_root, project_root):
            raise DiscoveryError("Project root validation failed")

        # Load agent discovery data from SSOT
        agents = load_agent_discovery(project_root, force_reload=True)
        Logger.info(f"[DISCOVERY] Loaded {len(agents)} agents from SSOT")

        # Validate compliance gate
        if not check_compliance_gate():
            Logger.error("[DISCOVERY] Compliance gate validation failed")
            return False

        # Generate discovery summary
        summary = get_agent_discovery_summary()
        Logger.info(f"[DISCOVERY] Discovery summary: {summary}")

        Logger.info("[DISCOVERY] Agent discovery completed successfully")
        return True

    except DiscoveryError as e:
        Logger.error(f"[DISCOVERY] Discovery operation failed: {e}")
        return False
    except Exception as e:
        Logger.error(f"[DISCOVERY] Unexpected error during discovery: {e}")
        return False


def check_compliance_gate() -> bool:
    """
    Check compliance gate using SSOT validation.

    Validates that the agent discovery system is in a compliant state
    by checking critical directories and SSOT file integrity.

    Returns:
        bool: True if compliance checks pass, False otherwise.
    """
    try:
        # Validate project root structure using SSOT constants
        project_root = get_validated_project_root()

        # Check critical SSOT directories exist using structure_blueprint constants
        critical_dirs = [
            AGENTIC_CORE_DIR,
            APPS_RG_DIR,
            APPS_LIC_DIR,
            APPS_SHARED_DIR,
            L0_MAINTENANCE_DIR,
            L1_COGNITION_DIR,
            L2_EXECUTION_DIR,
            L3_ORCHESTRATION_DIR,
            L4_STATE_DIR,
            L5_SAFETY_DIR,
            L6_OBSERVABILITY_DIR,
        ]

        for dir_name in critical_dirs:
            dir_path = project_root / dir_name
            if not dir_path.exists():
                Logger.error(f"[COMPLIANCE] Critical directory missing: {dir_path}")
                return False

        # Validate agent discovery JSON exists and is readable
        discovery_path = project_root / AGENT_DISCOVERY_JSON
        if not discovery_path.exists():
            Logger.error(f"[COMPLIANCE] SSOT discovery file missing: {discovery_path}")
            return False

        # Try to load discovery data to validate format
        try:
            agents = load_agent_discovery(project_root)
            if not isinstance(agents, list):
                Logger.error("[COMPLIANCE] Invalid discovery data format")
                return False
        except Exception as e:
            Logger.error(f"[COMPLIANCE] Failed to load discovery data: {e}")
            return False

        Logger.info("[COMPLIANCE] All compliance checks passed")
        return True

    except Exception as e:
        Logger.error(f"[COMPLIANCE] Compliance check failed: {e}")
        return False


def discover_all_agents() -> List[Dict[str, Any]]:
    """
    Discover all agents in the repository using SSOT.

    Delegates to ssot_discovery utility for actual agent enumeration.
    Provides standardized interface for backward compatibility.

    Returns:
        List[Dict[str, Any]]: List of agent discovery entries from SSOT.
    """
    try:
        agents = load_agent_discovery()
        Logger.debug(f"[DISCOVERY] Found {len(agents)} agents in SSOT")
        return agents
    except Exception as e:
        Logger.error(f"[DISCOVERY] Failed to discover agents: {e}")
        return []


def get_agent_discovery_summary() -> Dict[str, Any]:
    """
    Generate comprehensive agent discovery summary.

    Provides statistics and breakdowns of the agent ecosystem
    using SSOT data for accurate reporting.

    Returns:
        Dict[str, Any]: Summary statistics and agent breakdowns.
    """
    try:
        project_root = get_validated_project_root()
        agents = load_agent_discovery(project_root)

        # Calculate layer distribution
        layer_counts = {}
        for agent in agents:
            layer = agent.get("layer", "Unknown")
            layer_counts[layer] = layer_counts.get(layer, 0) + 1

        # Calculate directory distribution using SSOT constants
        dir_counts = {}
        for agent in agents:
            path = agent.get("path", "")
            if "/" in path or "\\" in path:
                # Normalize path separators
                normalized_path = path.replace("\\", "/")
                top_dir = normalized_path.split("/")[0]
                dir_counts[top_dir] = dir_counts.get(top_dir, 0) + 1

        # Get healer count
        healers = get_healers(project_root)

        summary = {
            "total_agents": len(agents),
            "layer_distribution": layer_counts,
            "directory_distribution": dir_counts,
            "healer_count": len(healers),
            "project_root": str(project_root),
            "ssot_file": str(project_root / AGENT_DISCOVERY_JSON),
            "last_updated": agents[0].get("last_updated") if agents else None,
        }

        return summary

    except Exception as e:
        Logger.error(f"[DISCOVERY] Failed to generate summary: {e}")
        return {
            "total_agents": 0,
            "layer_distribution": {},
            "directory_distribution": {},
            "healer_count": 0,
            "error": str(e),
        }


def validate_agent_structure(agent_path: Path) -> bool:
    """
    Validate individual agent file structure.

    Checks that agent files follow expected naming and structure patterns
    as defined in the SSOT blueprint.

    Args:
        agent_path: Path to the agent file to validate.

    Returns:
        bool: True if agent structure is valid, False otherwise.
    """
    try:
        if not agent_path.exists():
            Logger.warning(f"[VALIDATION] Agent file not found: {agent_path}")
            return False

        if not agent_path.suffix == ".py":
            Logger.warning(f"[VALIDATION] Non-Python agent file: {agent_path}")
            return False

        # Check for base agent naming patterns
        filename = agent_path.stem
        agent_path_str = str(agent_path)

        if "BaseAgent" in filename:
            # Check if the agent is in the correct base_agents directory
            if "base_agents" not in agent_path_str.replace("\\", "/"):
                Logger.warning(f"[VALIDATION] Base agent not in base_agents: {agent_path}")
                return False

        return True

    except Exception as e:
        Logger.error(f"[VALIDATION] Structure validation failed: {e}")
        return False


def refresh_discovery_cache() -> bool:
    """
    Refresh the agent discovery cache.

    Forces cache invalidation and reload to ensure latest data.
    Useful after repository modifications or healing operations.

    Returns:
        bool: True if cache refresh succeeded, False otherwise.
    """
    try:
        invalidate_cache()
        Logger.info("[CACHE] Discovery cache invalidated successfully")

        # Test reload
        agents = load_agent_discovery(force_reload=True)
        Logger.info(f"[CACHE] Reloaded {len(agents)} agents")

        return True

    except Exception as e:
        Logger.error(f"[CACHE] Cache refresh failed: {e}")
        return False


def get_structured_agent_paths() -> List[str]:
    """
    Return structured list of agent file paths from SSOT.

    This function provides the canonical agent inventory as required
    by the Phase 2 audit pipeline.

    Returns:
        List[str]: List of agent file paths relative to project root.
    """
    try:
        agents = load_agent_discovery()
        paths = []

        for agent in agents:
            path = agent.get("path", "")
            if path:
                # Normalize path separators for consistency
                normalized_path = path.replace("\\", "/")
                paths.append(normalized_path)

        Logger.debug(f"[PATHS] Generated {len(paths)} structured agent paths")
        return paths

    except Exception as e:
        Logger.error(f"[PATHS] Failed to generate structured paths: {e}")
        return []


# CLI interface for direct script execution
def cli_interface() -> None:
    """Command-line interface for discovery operations."""
    import argparse

    parser = argparse.ArgumentParser(description="Agent Discovery Utility")
    parser.add_argument("--summary", action="store_true", help="Show discovery summary")
    parser.add_argument("--check-compliance", action="store_true", help="Run compliance checks")
    parser.add_argument("--refresh-cache", action="store_true", help="Refresh discovery cache")
    parser.add_argument("--layer", help="Filter by layer (L0-L6)")
    parser.add_argument("--name", help="Find specific agent by name")
    parser.add_argument("--json", action="store_true", help="Output full inventory as JSON")
    parser.add_argument("--paths", action="store_true", help="Output structured agent paths")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")

    args = parser.parse_args()

    # Configure logging level
    setup_logging(verbose=args.verbose)

    try:
        if args.check_compliance:
            compliant = check_compliance_gate()
            print(f"Compliance Status: {'PASS' if compliant else 'FAIL'}")
            sys.exit(0 if compliant else 1)

        elif args.refresh_cache:
            success = refresh_discovery_cache()
            print(f"Cache Refresh: {'SUCCESS' if success else 'FAILED'}")
            sys.exit(0 if success else 1)

        elif args.json:
            agents = load_agent_discovery()
            print(json.dumps(agents, indent=2, default=str))

        elif args.paths:
            paths = get_structured_agent_paths()
            print("Structured Agent Paths:")
            for path in paths:
                print(f"  {path}")

        elif args.summary:
            summary = get_agent_discovery_summary()
            print("Agent Discovery Summary:")
            for key, value in summary.items():
                print(f"  {key}: {value}")

        elif args.layer:
            agents = get_agents_by_layer(layer=args.layer)
            print(f"Agents in {args.layer}: {len(agents)}")
            for agent in agents:
                print(f"  - {agent.get('name', 'Unknown')}: {agent.get('path', 'No path')}")

        elif args.name:
            agent = get_agent_by_name(name=args.name)
            if agent:
                print(f"Found agent: {agent.get('name', 'Unknown')}")
                print(f"  Path: {agent.get('path', 'No path')}")
                print(f"  Layer: {agent.get('layer', 'Unknown')}")
            else:
                print(f"Agent '{args.name}' not found")
                sys.exit(1)

        else:
            # Default: run full discovery
            success = main()
            sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        Logger.info("[DISCOVERY] Operation cancelled by user")
        sys.exit(130)
    except Exception as e:
        Logger.error(f"[DISCOVERY] CLI operation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    cli_interface()
