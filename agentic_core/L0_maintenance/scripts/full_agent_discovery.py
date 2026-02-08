#!/usr/bin/env python3
"""
Full Agent Discovery Script - SSOT Compliant Implementation
With Advanced AST Analysis & Architectural Integrity Verification

COMPLETE SSOT REFACTOR: All directory constants and paths MUST be imported
from structure_blueprint.py. NO hardcoded strings allowed.

This script serves as the canonical entry point for agent discovery operations.
It delegates core enumeration to the SSOT discovery utility but strictly
ENFORCES architectural integrity using deep AST analysis.

ADVANCED CAPABILITIES:
- Intrinsic AST Verification (Deep Code Analysis)
- Stub Sovereignty (Respects NOT_AN_AGENT markers)
- Architectural Role Detection (Base vs. Implementation)
- Ghost Detection (Verifies physical existence of cached agents)

SSOT PRINCIPLE: structure_blueprint.py is the absolute authority.
"""

from __future__ import annotations

import ast
import hashlib
import json
import logging
import platform
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from agentic_core.L0_maintenance.utils.ssot_discovery_util import (
    get_healers,
    invalidate_cache,
    load_agent_discovery,
)

# CRITICAL SSOT Imports - ALL directory constants MUST come from structure_blueprint.py
from agentic_core.L5_safety.config.structure_blueprint_config import (
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

# Standard error logging wrapper configuration
Logger = logging.getLogger(__name__)

# Output schema version for downstream auditors
OUTPUT_SCHEMA_VERSION = "2.0.0"

# ==============================================================================
# Advanced Data Structures
# ==============================================================================


@dataclass
class AgentIntegrityReport:
    """Detailed AST analysis result for a single agent file."""

    path: Path
    is_valid: bool = False
    is_stub: bool = False
    is_base_agent: bool = False
    class_name: str | None = None
    inheritance: list[str] = field(default_factory=list)
    decorators: list[str] = field(default_factory=list)
    critical_methods: list[str] = field(default_factory=list)
    rejection_reason: str | None = None
    architectural_role: str = "Unknown"
    file_sha256: str = ""
    file_size_bytes: int = 0
    parse_error: str = ""
    selection_reason: str = ""
    mro_signature: list[str] = field(default_factory=list)


class DiscoveryError(Exception):
    """Custom exception for agent discovery operations."""

    pass


# ==============================================================================
# Core Setup
# ==============================================================================


def setup_logging(verbose: bool = False) -> None:
    """
    Standard logging configuration wrapper.
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="[%(asctime)s] %(levelname)s [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_unparse(node: ast.AST) -> str:
    try:
        return ast.unparse(node)  # py>=3.9
    except Exception:
        return node.__class__.__name__


def get_git_commit(root: Path) -> str:
    try:
        out = subprocess.check_output(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            stderr=subprocess.DEVNULL,
        )
        return out.decode("utf-8").strip()
    except Exception:
        return ""


def main() -> bool:
    """
    Main entry point for agent discovery operations.
    Performs comprehensive agent discovery and strict integrity validation.
    """
    try:
        # Get validated project root from SSOT
        project_root = get_validated_project_root()
        Logger.info(f"[DISCOVERY] Starting Deep Agent Discovery from: {project_root}")

        # Validate project root integrity (treat validator as raising, not bool-return)
        try:
            validate_path_within_project(project_root, project_root)
        except Exception as e:
            raise DiscoveryError(f"Project root validation failed: {e}")

        # Load agent discovery data from SSOT (The List)
        raw_agents = load_agent_discovery(project_root, force_reload=True)
        raw_agents = sorted(
            raw_agents,
            key=lambda a: (a.get("layer", ""), a.get("name", ""), a.get("path", "")),
        )
        Logger.info(f"[DISCOVERY] Loaded {len(raw_agents)} candidates from SSOT registry")

        # Perform Deep AST Integrity Scan (The Verification)
        valid_agents, validation_stats = perform_deep_integrity_scan(raw_agents, project_root)

        # Log Validation Results
        Logger.info("[DISCOVERY] Deep Scan Complete:")
        Logger.info(f"   - Verified Active Agents: {validation_stats['verified']}")
        Logger.info(f"   - Stubs/Exempt: {validation_stats['stubs']}")
        Logger.info(f"   - Invalid/Ghosts: {validation_stats['invalid']}")

        # Validate compliance gate based on scan results
        if not check_compliance_gate(validation_stats):
            Logger.error("[DISCOVERY] Compliance gate validation failed (Integrity violations detected)")
            return False

        Logger.info("[DISCOVERY] Agent discovery and verification completed successfully")
        return True

    except DiscoveryError as e:
        Logger.error(f"[DISCOVERY] Discovery operation failed: {e}")
        return False
    except Exception as e:
        Logger.error(f"[DISCOVERY] Unexpected error during discovery: {e}")
        return False


# ==============================================================================
# Advanced AST Analysis Engine
# ==============================================================================


def analyze_agent_integrity(file_path: Path) -> AgentIntegrityReport:
    """
    Performs deep AST analysis on a file to verify it is a legitimate Agent.

    Criteria matches FileClassificationAgent logic:
    1. Checks for STUB markers (Priority 1)
    2. Parses AST for ClassDef
    3. Verifies Inheritance (SovereignBaseAgent, etc.)
    4. Verifies Decorators (@agent)
    5. Verifies Method Signatures (execute, act, run)
    """
    report = AgentIntegrityReport(path=file_path)

    if not file_path.exists():
        report.rejection_reason = "File not found (Ghost)"
        return report

    try:
        report.file_size_bytes = file_path.stat().st_size
        report.file_sha256 = sha256_file(file_path)
        content = file_path.read_text(encoding="utf-8", errors="replace")

        # [CRITICAL] Priority 1: Explicit Stub Detection
        # Mirrors FileClassificationAgent logic exactly
        head = "\n".join(content.splitlines()[:60])
        if any(line.strip() == "NOT_AN_AGENT" for line in head.splitlines()):
            report.is_stub = True
            report.is_valid = False
            report.rejection_reason = "Explicit NOT_AN_AGENT marker found"
            report.architectural_role = "STUB"
            return report

        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            report.parse_error = f"SyntaxError: {e}"
            report.rejection_reason = report.parse_error
            return report

        # Markers for synthesis
        has_agent_inheritance = False
        has_agent_decorator = False
        has_execute_method = False
        class_nodes: list[ast.ClassDef] = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
        if not class_nodes:
            report.rejection_reason = "No ClassDef nodes"
            return report

        # Deterministic selection: score by explicit agent bases, then name signals, then critical methods
        def extract_mro_signature(cls: ast.ClassDef) -> list[str]:
            return [safe_unparse(b) for b in cls.bases]

        def class_score(cls: ast.ClassDef) -> int:
            bases = " ".join(extract_mro_signature(cls))
            methods = [i.name for i in cls.body if isinstance(i, ast.FunctionDef | ast.AsyncFunctionDef)]
            s = 0
            if "SovereignBaseAgent" in bases or "BaseAgent" in bases:
                s += 100
            if "Agent" in cls.name:
                s += 10
            if "Healer" in cls.name:
                s += 5
            if "heal" in methods:
                s += 20
            if any(m in methods for m in ("execute", "run", "act")):
                s += 8
            return s

        chosen = sorted(class_nodes, key=lambda c: (class_score(c), c.name), reverse=True)[0]
        if class_score(chosen) <= 0:
            report.rejection_reason = "No viable agent-like class (score<=0)"
            return report

        report.class_name = chosen.name
        report.mro_signature = extract_mro_signature(chosen)
        report.selection_reason = "Selected highest-scoring ClassDef deterministically"

        # Check Inheritance
        for base_expr in chosen.bases:
            base_id = safe_unparse(base_expr)
            if base_id:
                report.inheritance.append(base_id)

                # Detect Base Agents vs Implementations
                if "BaseAgent" in base_id:
                    report.is_base_agent = True
                    report.architectural_role = "BASE_AGENT"
                    has_agent_inheritance = True
                elif "Agent" in base_id:
                    has_agent_inheritance = True

        # Check Decorators
        for dec in chosen.decorator_list:
            dec_id = ""
            if isinstance(dec, ast.Name):
                dec_id = dec.id
            elif isinstance(dec, ast.Attribute):
                dec_id = dec.attr

            if dec_id:
                report.decorators.append(dec_id)
                if dec_id in ["agent", "sovereign_agent", "register_agent"]:
                    has_agent_decorator = True

        # Check Methods
        for item in chosen.body:
            if isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef):
                if item.name in ["execute", "act", "run", "heal"]:
                    report.critical_methods.append(item.name)
                    has_execute_method = True

        # [SYNTHESIS] Determine Validity
        # A valid agent must have Inheritance OR Decorator OR (Execute method + 'Agent' in name)
        is_named_agent = report.class_name and "Agent" in report.class_name

        if report.is_base_agent:
            report.is_valid = True  # Base agents are valid architectural components
        elif has_agent_inheritance or has_agent_decorator:
            report.is_valid = True
            report.architectural_role = "AGENT"
        elif is_named_agent and has_execute_method:
            report.is_valid = True
            report.architectural_role = "AGENT (Implicit)"
        else:
            report.is_valid = False
            report.rejection_reason = "Lacks Agent inheritance, decorators, or execution patterns"

        return report

    except Exception as e:
        report.rejection_reason = f"Analysis failed: {e}"
        return report


def perform_deep_integrity_scan(
    agents: list[dict[str, Any]],
    project_root: Path,
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """
    Iterates over discovered agents and validates them using AST analysis.
    Returns:
        tuple: (List of verified agents, Statistics Dictionary)
    """
    verified_agents = []
    stats = {"verified": 0, "stubs": 0, "invalid": 0, "base_agents": 0, "ghosts": 0}

    for agent_entry in agents:
        # Normalize path
        rel_path = agent_entry.get("path", "")
        if not rel_path:
            stats["invalid"] += 1
            continue

        full_path = project_root / rel_path
        try:
            validate_path_within_project(project_root, full_path)
        except Exception:
            stats["invalid"] += 1
            agent_entry["verification_status"] = {
                "valid": False,
                "role": "INVALID",
                "class": None,
                "methods": [],
                "reason": "Path fails validate_path_within_project",
            }
            continue
        # Run Analysis
        report = analyze_agent_integrity(full_path)

        # Augment agent entry with analysis data
        agent_entry["verification_status"] = {
            "valid": report.is_valid,
            "role": report.architectural_role,
            "class": report.class_name,
            "methods": report.critical_methods,
            "mro_signature": report.mro_signature,
            "file_sha256": report.file_sha256,
            "file_size_bytes": report.file_size_bytes,
            "selection_reason": report.selection_reason,
            "parse_error": report.parse_error,
        }

        if report.is_valid:
            stats["verified"] += 1
            if report.is_base_agent:
                stats["base_agents"] += 1
            verified_agents.append(agent_entry)
        elif report.is_stub:
            stats["stubs"] += 1
            Logger.debug(f"[SCAN] Detected Stub: {rel_path}")
        elif report.rejection_reason and "not found" in report.rejection_reason:
            stats["ghosts"] += 1
            stats["invalid"] += 1
            Logger.warning(f"[SCAN] Ghost Agent (Cache invalid): {rel_path}")
        else:
            stats["invalid"] += 1
            Logger.debug(f"[SCAN] Rejected {rel_path}: {report.rejection_reason}")

    return verified_agents, stats


# ==============================================================================
# Compliance & Interfaces
# ==============================================================================


def check_compliance_gate(scan_stats: dict[str, int] | None = None) -> bool:
    """
    Check compliance gate using SSOT validation AND Integrity Stats.

    Args:
        scan_stats: Optional dict from perform_deep_integrity_scan.
                    If provided, enforces thresholds on invalid agents.

    Returns:
        bool: True if compliance checks pass, False otherwise.
    """
    try:
        # 1. Validate project root structure using SSOT constants
        project_root = get_validated_project_root()

        # 2. Check critical SSOT directories
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

        # 3. Validate agent discovery JSON integrity
        discovery_path = project_root / AGENT_DISCOVERY_JSON
        if not discovery_path.exists():
            Logger.error(f"[COMPLIANCE] SSOT discovery file missing: {discovery_path}")
            return False

        # 4. Strict Integrity Check (if stats provided)
        if scan_stats:
            ghosts = scan_stats.get("ghosts", 0)
            if ghosts > 0:
                Logger.error(
                    f"[COMPLIANCE] FAILED: {ghosts} ghost agents detected in registry. Run refresh_cache.",
                )
                return False

            # Warn but don't necessarily fail on simple invalids (might be works in progress)
            invalids = scan_stats.get("invalid", 0)
            if invalids > 0:
                Logger.warning(f"[COMPLIANCE] Warning: {invalids} files in registry failed validation.")

        Logger.info("[COMPLIANCE] All compliance checks passed")
        return True

    except Exception as e:
        Logger.error(f"[COMPLIANCE] Compliance check failed: {e}")
        return False


def discover_all_agents(strict_mode: bool = True) -> list[dict[str, Any]]:
    """
    Discover all agents in the repository using SSOT and AST Validation.

    Args:
        strict_mode: If True, filters out agents that fail AST validation.

    Returns:
        List[Dict[str, Any]]: List of verified agent discovery entries.
    """
    try:
        project_root = get_validated_project_root()
        raw_agents = load_agent_discovery(project_root)
        raw_agents = sorted(
            raw_agents,
            key=lambda a: (a.get("layer", ""), a.get("name", ""), a.get("path", "")),
        )

        if not strict_mode:
            return raw_agents

        verified_agents, _ = perform_deep_integrity_scan(raw_agents, project_root)
        Logger.debug(f"[DISCOVERY] Returning {len(verified_agents)} verified agents")
        return verified_agents

    except Exception as e:
        Logger.error(f"[DISCOVERY] Failed to discover agents: {e}")
        return []


def get_agent_discovery_summary() -> dict[str, Any]:
    """
    Generate comprehensive agent discovery summary with Integrity Stats.
    """
    try:
        project_root = get_validated_project_root()
        # Load and Scan
        raw_agents = load_agent_discovery(project_root)
        verified_agents, stats = perform_deep_integrity_scan(raw_agents, project_root)

        # Calculate layer distribution (Verified Only)
        layer_counts = {}
        for agent in verified_agents:
            layer = agent.get("layer", "Unknown")
            layer_counts[layer] = layer_counts.get(layer, 0) + 1

        # Get healer count
        healers = get_healers(project_root)

        summary = {
            "output_schema_version": OUTPUT_SCHEMA_VERSION,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "python_version": sys.version.split()[0],
            "platform": platform.platform(),
            "git_commit": get_git_commit(project_root),
            "total_candidates": len(raw_agents),
            "verified_active_agents": len(verified_agents),
            "integrity_stats": stats,
            "layer_distribution": layer_counts,
            "healer_count": len(healers),
            "project_root": str(project_root),
            "ssot_file": str(project_root / AGENT_DISCOVERY_JSON),
        }

        return summary

    except Exception as e:
        Logger.error(f"[DISCOVERY] Failed to generate summary: {e}")
        return {"error": str(e)}


def refresh_discovery_cache() -> bool:
    """
    Refresh the agent discovery cache.
    Forces cache invalidation and reload to ensure latest data.
    """
    try:
        invalidate_cache()
        Logger.info("[CACHE] Discovery cache invalidated successfully")

        # Test reload
        project_root = get_validated_project_root()
        agents = load_agent_discovery(project_root, force_reload=True)
        Logger.info(f"[CACHE] Reloaded {len(agents)} agents from disk")

        return True

    except Exception as e:
        Logger.error(f"[CACHE] Cache refresh failed: {e}")
        return False


def get_structured_agent_paths() -> list[str]:
    """
    Return structured list of verified agent file paths.
    """
    try:
        agents = discover_all_agents(strict_mode=True)
        paths = []

        for agent in agents:
            path = agent.get("path", "")
            if path:
                normalized_path = path.replace("\\", "/")
                paths.append(normalized_path)

        return paths

    except Exception as e:
        Logger.error(f"[PATHS] Failed to generate structured paths: {e}")
        return []


# ==============================================================================
# CLI Interface
# ==============================================================================


def cli_interface() -> None:
    """Command-line interface for discovery operations."""
    import argparse

    parser = argparse.ArgumentParser(description="Deep Agent Discovery Utility")
    parser.add_argument("--summary", action="store_true", help="Show discovery summary with integrity stats")
    parser.add_argument("--check-compliance", action="store_true", help="Run strict compliance checks")
    parser.add_argument("--refresh-cache", action="store_true", help="Refresh discovery cache")
    parser.add_argument("--layer", help="Filter by layer (L0-L6)")
    parser.add_argument("--name", help="Find specific agent by name")
    parser.add_argument("--json", action="store_true", help="Output full inventory as JSON")
    parser.add_argument("--paths", action="store_true", help="Output structured agent paths")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")

    # New flags for deep analysis
    parser.add_argument("--inspect", help="Deep inspect specific agent file path")
    parser.add_argument("--show-invalid", action="store_true", help="List agents that failed integrity check")

    args = parser.parse_args()

    setup_logging(verbose=args.verbose)

    try:
        if args.check_compliance:
            # Run scan first to get stats
            project_root = get_validated_project_root()
            raw = load_agent_discovery(project_root)
            _, stats = perform_deep_integrity_scan(raw, project_root)

            compliant = check_compliance_gate(stats)
            print(f"Compliance Status: {'PASS' if compliant else 'FAIL'}")
            if not compliant:
                print(f"Integrity Issues: {stats['invalid']} invalid, {stats['ghosts']} missing files.")
            sys.exit(0 if compliant else 1)

        elif args.refresh_cache:
            success = refresh_discovery_cache()
            print(f"Cache Refresh: {'SUCCESS' if success else 'FAILED'}")
            sys.exit(0 if success else 1)

        elif args.inspect:
            project_root = get_validated_project_root()
            path = Path(args.inspect)
            if not path.is_absolute():
                path = project_root / path

            print(f"Inspecting: {path}")
            report = analyze_agent_integrity(path)
            print(
                json.dumps(
                    {
                        "valid": report.is_valid,
                        "role": report.architectural_role,
                        "class": report.class_name,
                        "inheritance": report.inheritance,
                        "methods": report.critical_methods,
                        "rejection_reason": report.rejection_reason,
                    },
                    indent=2,
                ),
            )

        elif args.json:
            agents = discover_all_agents(strict_mode=True)
            print(json.dumps(agents, indent=2, default=str))

        elif args.paths:
            paths = get_structured_agent_paths()
            print("Structured Agent Paths (Verified Only):")
            for path in paths:
                print(f"  {path}")

        elif args.summary:
            summary = get_agent_discovery_summary()
            print("Agent Discovery Summary:")
            print(json.dumps(summary, indent=2, default=str))

        elif args.show_invalid:
            project_root = get_validated_project_root()
            raw = load_agent_discovery(project_root)
            _, stats = perform_deep_integrity_scan(raw, project_root)
            print(f"Found {stats['invalid']} invalid agents:")
            for agent in raw:
                # Re-run single analysis to print reason (inefficient but fine for CLI)
                path = project_root / agent.get("path", "")
                report = analyze_agent_integrity(path)
                if not report.is_valid and not report.is_stub:
                    print(f"  - {agent.get('name')}: {report.rejection_reason}")

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
