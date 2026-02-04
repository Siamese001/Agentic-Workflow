#!/usr/bin/env python3
"""
FORENSIC DISCOVERY PREP - V10 GAP ANALYSIS TOOL
===============================================
Generates the authoritative "Environment Under Test" artifact for the
V10 Target State Gap Analysis.

USAGE:
    python forensic_discovery_prep.py > audit_context.json

OUTPUT:
    A structured JSON artifact containing:
    1. Validated Agent Manifest (Identity + Path)
    2. Precise MRO Signatures (for Safety Mixin verification)
    3. Ghost/Invalid Agent Report
"""

from __future__ import annotations

import ast
import json
import logging
import sys
from pathlib import Path
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

# ==============================================================================
# IMPORT STRATEGY: Inherit strict SSOT paths from production environment
# ==============================================================================
try:
    from agentic_core.L5_safety.validators.structure_blueprint_config import (
        AGENT_DISCOVERY_JSON,
        get_validated_project_root,
        validate_path_within_project,
    )
    from agentic_core.utils.ssot_discovery_validator import (
        load_agent_discovery,
    )
except ImportError:
    # Fallback for standalone auditing (if outside strict env)
    print("CRITICAL: SSOT imports failed. Ensure PYTHONPATH includes project root.", file=sys.stderr)
    sys.exit(1)

# Configure simplified logging for the tool
logging.basicConfig(level=logging.ERROR, format="%(message)s")
Logger = logging.getLogger("ForensicAudit")

# ==============================================================================
# Forensic Data Structures
# ==============================================================================

@dataclass
class ForensicAgentRecord:
    """The absolute truth for a single agent under audit."""
    agent_name: str
    layer: str
    file_path: str
    class_name: str
    mro_signature: List[str]  # Critical for Point 8.3 (Mixin Order)
    status: str  # ACTIVE | STUB | GHOST | INVALID
    methods_detected: List[str]

# ==============================================================================
# Deep Inspection Logic (Enhanced for Gap Analysis)
# ==============================================================================

def extract_precise_mro(node: ast.ClassDef) -> List[str]:
    """
    Extracts base classes in exact declaration order to detect 'Inheritance Traps'.
    Example: class MyAgent(SafetyMixin, BaseAgent) -> ["SafetyMixin", "BaseAgent"]
    """
    bases = []
    for base in node.bases:
        if isinstance(base, ast.Name):
            bases.append(base.id)
        elif isinstance(base, ast.Attribute):
            bases.append(f"{base.value.id}.{base.attr}" if isinstance(base.value, ast.Name) else base.attr)
        else:
            bases.append("UnknownBase")
    return bases

def forensic_inspect(name: str, layer: str, file_path: Path) -> ForensicAgentRecord:
    """
    Analyzes a file to build the Forensic Record.
    """
    record = ForensicAgentRecord(
        agent_name=name,
        layer=layer,
        file_path=str(file_path),
        class_name="Unknown",
        mro_signature=[],
        status="INVALID",
        methods_detected=[]
    )

    if not file_path.exists():
        record.status = "GHOST"
        return record

    try:
        content = file_path.read_text(encoding="utf-8")
        
        # Fast fail for Stubs
        if "NOT_AN_AGENT" in content:
            record.status = "STUB"
            return record

        try:
            tree = ast.parse(content)
        except SyntaxError:
            record.status = "SYNTAX_ERROR"
            return record

        # Walk the AST looking for the Agent definition
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Heuristic: The agent class usually matches the file name or contains "Agent"
                # For audit purposes, we grab the class that looks most like an agent
                is_candidate = "Agent" in node.name or "Healer" in node.name
                
                if is_candidate:
                    record.class_name = node.name
                    record.mro_signature = extract_precise_mro(node)
                    record.status = "ACTIVE"
                    
                    # Scan for critical V10 methods
                    for item in node.body:
                        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            record.methods_detected.append(item.name)
                    
                    # Stop after finding the primary class
                    break

    except Exception as e:
        record.status = f"ERROR: {str(e)}"

    return record

# ==============================================================================
# Execution
# ==============================================================================

def run_forensic_discovery():
    project_root = get_validated_project_root()
    
    # 1. Load the Candidate List from SSOT
    raw_candidates = load_agent_discovery(project_root, force_reload=True)
    
    manifest = {
        "audit_meta": {
            "root": str(project_root),
            "total_candidates": len(raw_candidates),
            "generated_at": "Pre-Audit Check"
        },
        "environment_under_test": [],
        "ignored_artifacts": []
    }

    # 2. Inspect every candidate
    for candidate in raw_candidates:
        rel_path = candidate.get("path", "")
        name = candidate.get("name", "Unknown")
        layer = candidate.get("layer", "Unknown")
        
        full_path = project_root / rel_path
        
        record = forensic_inspect(name, layer, full_path)
        
        if record.status == "ACTIVE":
            manifest["environment_under_test"].append(asdict(record))
        else:
            manifest["ignored_artifacts"].append(asdict(record))

    # 3. Output Pure JSON for the Auditor
    print(json.dumps(manifest, indent=2))

if __name__ == "__main__":
    try:
        run_forensic_discovery()
    except Exception as e:
        print(json.dumps({"fatal_error": str(e)}))
        sys.exit(1)
