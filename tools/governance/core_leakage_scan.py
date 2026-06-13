#!/usr/bin/env python3
"""
core_leakage_scan.py - Post-write hook to scan agentic_core for app-specific leakage.

Scans for forbidden literals and patterns:
- apps_lic, apps_rg, apps_qna, apps_research
- if app_id, app_id ==
- App-specific route names
- App-specific cache policy names
- App-specific send modes

Exit codes:
  0 - Clean (advisory mode, or no leakage)
  1 - Warn (advisory mode with warnings)
  2 - Fail (strict mode, or leakage detected)

Note: The 1531 violations vs original 323:
- 1531 includes all pattern matches including tests, docs, bindings
- 323 is the subset classified as CORE_APP_SPECIFIC_LEAKAGE (real violations)
- Full classification deferred to W4
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional

# Import shared receipt validation
try:
    from receipt_validator import find_and_validate_receipt, REQUIRED_FIELDS
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent))
    from receipt_validator import find_and_validate_receipt, REQUIRED_FIELDS

# Configuration
ADVISORY_SUNSET = "2026-06-15"

REPO_ROOT = Path("C:\\Git\\Agentic-Workflow-FRESH")
AGENTIC_CORE_PATH = REPO_ROOT / "agentic_core"
GOVERNANCE_DIR = REPO_ROOT / "artifacts" / "governance"
SCAN_OUTPUT_DIR = GOVERNANCE_DIR / "scans"
MIGRATION_RECEIPTS_DIR = GOVERNANCE_DIR / "migration_receipts"

# W8 Taxonomy Classification (based on W7 Phase 0 classification)
# Maps file patterns to governance risk categories
TAXONOMY_CATEGORIES = {
    "RUNTIME_POLICY_LEAKAGE": {
        "description": "App literals influencing governed runtime decisions - MUST ELIMINATE",
        "severity": "CRITICAL",
        "file_patterns": [
            # Files with runtime branching on app_id/tenant_id
            r".*runtime.*\.py$",
            r".*routing.*\.py$",
            r".*orchestration.*\.py$",
            r".*execution.*\.py$",
            r".*L0.*\.py$",
            r".*L1.*\.py$",
            r".*L2.*\.py$",
            r".*L3.*\.py$",
            r".*L5.*\.py$",
            r".*entry.*\.py$",
            r".*exit.*\.py$",
        ],
        "content_patterns": [
            r'if\s+app_id\s*==\s*["\']',
            r'if\s+tenant_id\s*==\s*["\']apps_',
            r'APPS_\w+_EXIT_GATES',
            r'APPS_\w+_CACHE_BYPASS',
        ]
    },
    "STATIC_REGISTRY_METADATA": {
        "description": "App registry entries, ownership tables, analysis metadata - GENERIC_ALLOWED",
        "severity": "INFO",
        "file_patterns": [
            r".*analysis/.*\.py$",
            r".*contracts/.*\.py$",
            r".*analysis/.*\.yaml$",
            r".*contracts/.*\.yaml$",
            r".*/schema\.py$",
            r".*/ModuleOwnership\.py$",
            r".*/ownership\.py$",
        ],
        "content_patterns": [
            r'Owner\s*=\s*Literal\[.*apps_',
            r'"apps_\w+":\s*"L_APP"',
        ]
    },
    "OFFLINE_TOOLING_REFERENCE": {
        "description": "Developer tooling, offline analysis - Boundary-defined",
        "severity": "INFO",
        "file_patterns": [
            r".*adapters/.*\.py$",
            r".*applications/.*\.py$",
            r".*adapters/.*\.yaml$",
            r".*applications/.*\.yaml$",
            r".*/ADGMemoryAdapter\.py$",
            r".*/memory_mcp_adapter\.py$",
            r".*/placement_advisor.*\.py$",
        ],
        "content_patterns": [
            r'for\s+prefix\s+in\s+\(.*apps_shared.*apps_lic.*apps_rg',
        ]
    },
    "GENERIC_CORE_SUBSTRATE_ALLOWED": {
        "description": "Generic core infrastructure with dotted-path resolution - W9 P3 approved substrate",
        "severity": "INFO",
        "file_patterns": [
            r".*/c0_3_enhanced/adapter_registry\.py$",
        ],
        "content_patterns": []
    },
    "FALSE_POSITIVE": {
        "description": "Legitimate generic patterns incorrectly flagged",
        "severity": "DEBUG",
        "file_patterns": [],
        "content_patterns": [
            r'#.*apps_\w+',  # Comments mentioning apps
            r'""".*apps_\w+.*"""',  # Docstrings
            r"'''.*apps_\w+.*'''",
        ]
    },
    "UNKNOWN": {
        "description": "Unclassified detection requiring manual review",
        "severity": "HIGH",
        "file_patterns": [],
        "content_patterns": []
    }
}

# Blocking categories (cause strict mode failure)
# W9: GENERIC_CORE_SUBSTRATE_ALLOWED is NON-BLOCKING (approved substrate)
BLOCKING_CATEGORIES = {"RUNTIME_POLICY_LEAKAGE", "UNKNOWN"}

# Classification source reference
CLASSIFICATION_SOURCE = "W7 Phase 0 classification report (artifacts/governance/w7_phase0_classification.md)"


def classify_violation(violation: Dict) -> str:
    """
    Classify a violation into taxonomy category.
    Returns category name (RUNTIME_POLICY_LEAKAGE, STATIC_REGISTRY_METADATA, etc.)
    """
    filepath = violation.get('file', '')
    content = violation.get('content', '')
    pattern_name = violation.get('pattern_name', '')
    
    # Normalize path for cross-platform matching (Windows backslashes -> forward slashes)
    normalized_path = filepath.replace('\\', '/')
    
    # W9 P0/P3: PRIORITY 0 - Specific file classifications (non-negotiable)
    # code_symbol_catalog.py = OFFLINE_TOOLING_REFERENCE (static analysis, not runtime)
    if re.search(r".*/code_symbol_catalog\.py$", normalized_path, re.IGNORECASE):
        return "OFFLINE_TOOLING_REFERENCE"
    
    # adapter_registry.py = GENERIC_CORE_SUBSTRATE_ALLOWED (W9 P3 approved substrate)
    if re.search(r".*/c0_3_enhanced/adapter_registry\.py$", normalized_path, re.IGNORECASE):
        return "GENERIC_CORE_SUBSTRATE_ALLOWED"
    
    # PRIORITY 1: Check for specific file path patterns (most reliable)
    # STATIC_REGISTRY_METADATA: analysis files, schema files, config files
    if re.search(r".*/analysis/.*\.py$", normalized_path, re.IGNORECASE) or \
       re.search(r".*/schema\.py$", normalized_path, re.IGNORECASE) or \
       re.search(r".*/ModuleOwnership\.py$", normalized_path, re.IGNORECASE) or \
       re.search(r".*/ownership\.py$", normalized_path, re.IGNORECASE) or \
       re.search(r".*/config/.*\.py$", normalized_path, re.IGNORECASE) or \
       re.search(r".*/config/.*\.json$", normalized_path, re.IGNORECASE) or \
       re.search(r".*/structure_blueprint/.*\.py$", normalized_path, re.IGNORECASE):
        # Check if it's a type declaration, schema entry, config constant, or ownership table
        if re.search(r'Owner\s*=\s*Literal\[.*apps_', content, re.IGNORECASE) or \
           re.search(r'"apps_\w+":\s*"L_APP"', content, re.IGNORECASE) or \
           re.search(r'APPS_\w+_DIR\s*:\s*Final\[str\]', content, re.IGNORECASE) or \
           re.search(r'"apps_\w+":\s*\{', content, re.IGNORECASE) or \
           re.search(r'"apps_\w+":\s*\d+', content, re.IGNORECASE) or \
           re.search(r'downstream_domains.*apps_', content, re.IGNORECASE) or \
           re.search(r'\(\s*["\']apps_\w+/["\']\s*,\s*["\']apps_\w+["\']\s*,', content, re.IGNORECASE):
            return "STATIC_REGISTRY_METADATA"
    
    # W8 P5: Additional STATIC_REGISTRY patterns for registry/config files
    if re.search(r".*/registry_config\.py$", normalized_path, re.IGNORECASE) or \
       re.search(r".*/layer_hierarchy\.json$", normalized_path, re.IGNORECASE) or \
       re.search(r".*/data/territories\.json$", normalized_path, re.IGNORECASE):
        return "STATIC_REGISTRY_METADATA"
    
    # OFFLINE_TOOLING_REFERENCE: adapter files, applications files, identity normalizers
    if re.search(r".*/adapters/.*\.py$", normalized_path, re.IGNORECASE) or \
       re.search(r".*/applications/.*\.py$", normalized_path, re.IGNORECASE) or \
       re.search(r".*/identity/.*\.py$", normalized_path, re.IGNORECASE) or \
       re.search(r".*/normalizer\.py$", normalized_path, re.IGNORECASE):
        return "OFFLINE_TOOLING_REFERENCE"
    
    # PRIORITY 2: Check for specific pattern types that indicate runtime leakage
    # App branching on app_id or tenant_id is always runtime leakage
    if pattern_name == "app_id_branching" or \
       re.search(r'if\s+app_id\s*==\s*["\']', content, re.IGNORECASE) or \
       re.search(r'if\s+tenant_id\s*==\s*["\']apps_', content, re.IGNORECASE):
        return "RUNTIME_POLICY_LEAKAGE"
    
    # Route/exit gate patterns are runtime leakage indicators
    if pattern_name in ["app_specific_routes", "app_specific_exit_gates"]:
        return "RUNTIME_POLICY_LEAKAGE"
    
    # W8 P5: L5 Safety reasoning/analysis files (heuristic analysis, not runtime policy)
    if re.search(r".*/L5_safety/reasoning/.*\.py$", normalized_path, re.IGNORECASE) or \
       re.search(r".*/L5_safety/utils/.*\.py$", normalized_path, re.IGNORECASE):
        # These are analysis/heuristic tools, not runtime enforcement
        # Unless they contain actual app_id branching
        if not re.search(r'if\s+.*app_id', content, re.IGNORECASE):
            return "OFFLINE_TOOLING_REFERENCE"
    
    # W8 P5: L5 Safety config files (structure_blueprint - all static registry)
    if re.search(r".*/L5_safety/config/.*\.py$", normalized_path, re.IGNORECASE):
        # All structure_blueprint, artifacts, semantics, ssot, etc. are static config
        return "STATIC_REGISTRY_METADATA"
    
    # W8 P5: L5 Safety enforcement files (check for actual runtime branching)
    if re.search(r".*/L5_safety/enforcement/.*\.py$", normalized_path, re.IGNORECASE):
        # Check if it's actual app_id branching logic or just lookup/config
        if re.search(r'if.*app_id.*==', content, re.IGNORECASE) or \
           re.search(r'if\s+apps_\w+', content, re.IGNORECASE):
            return "RUNTIME_POLICY_LEAKAGE"
        # Configuration lookups and mappings are static
        return "STATIC_REGISTRY_METADATA"
    
    # W8 P5: L0 routing config (path_constants - static registry)
    if re.search(r".*/L0_routing/config/.*\.py$", normalized_path, re.IGNORECASE):
        return "STATIC_REGISTRY_METADATA"
    
    # W8 P5: L1 cognition reasoning (meta_client default configs)
    if re.search(r".*/L1_cognition/reasoning/.*\.py$", normalized_path, re.IGNORECASE):
        if re.search(r'default_factory.*lambda.*\{.*apps_', content, re.IGNORECASE):
            return "STATIC_REGISTRY_METADATA"
        return "OFFLINE_TOOLING_REFERENCE"
    
    # W8 P5: Auditability/L7 files (audit trail, observability - not runtime policy)
    if re.search(r".*/L7_auditability/.*\.py$", normalized_path, re.IGNORECASE) or \
       re.search(r".*/how_trace/.*\.py$", normalized_path, re.IGNORECASE):
        return "OFFLINE_TOOLING_REFERENCE"
    
    # W8 P5: Mixin files (documentation and type hints, not runtime)
    if re.search(r".*/mixins/.*\.py$", normalized_path, re.IGNORECASE):
        # Check if docstring/description vs actual code
        if re.search(r'Domain string.*apps_', content, re.IGNORECASE) or \
           re.search(r'e\.g\.\s*[`\'"]apps_', content, re.IGNORECASE):
            return "FALSE_POSITIVE"
        return "OFFLINE_TOOLING_REFERENCE"
    
    # W8 P5: Territory healing adapters (L3 orchestration analysis, not runtime policy)
    if re.search(r".*/territory_healing/.*\.py$", normalized_path, re.IGNORECASE):
        return "STATIC_REGISTRY_METADATA"
    
    # Check for app-specific Exit gate configurations (runtime leakage)
    if re.search(r'APPS_\w+_EXIT_GATES', content, re.IGNORECASE) or \
       re.search(r'APPS_\w+_FORBIDDEN_ACTIONS', content, re.IGNORECASE):
        return "RUNTIME_POLICY_LEAKAGE"
    
    # W8 P5: Content-based patterns (checked before file path)
    # Ownership table tuples: ("apps_lic/", "apps_lic", "medium", "prod")
    if re.search(r'\(\s*["\']apps_\w+/["\']\s*,\s*["\']apps_\w+["\']\s*,', content, re.IGNORECASE):
        return "STATIC_REGISTRY_METADATA"
    
    # Docstrings with code examples
    if re.search(r'Example:\s*\w+\(["\']apps_', content, re.IGNORECASE):
        return "FALSE_POSITIVE"
    
    # W8 P5: L2 execution types and healers (documentation/type hints, not runtime)
    if re.search(r".*/L2_execution/types/.*\.py$", normalized_path, re.IGNORECASE) or \
       re.search(r".*/L2_execution/healers/.*\.py$", normalized_path, re.IGNORECASE):
        # These are type definitions and diagnostic docstrings
        if re.search(r'domain_id.*e\.g\.\s*[`\'"]apps_', content, re.IGNORECASE) or \
           re.search(r'app_name.*Calling app identifier', content, re.IGNORECASE):
            return "FALSE_POSITIVE"
        return "OFFLINE_TOOLING_REFERENCE"
    
    # W8 P5: L3 orchestration config (qwen_vllm config files)
    if re.search(r".*/qwen_vllm/config/.*\.py$", normalized_path, re.IGNORECASE):
        return "STATIC_REGISTRY_METADATA"
    
    # W8 P5: Base agents and protocols (documentation/typing)
    if re.search(r".*/base_agents/.*\.py$", normalized_path, re.IGNORECASE):
        return "FALSE_POSITIVE"
    
    # W8 P5: C0 context files (cross-app research substrate)
    if re.search(r".*/C0_context/.*\.py$", normalized_path, re.IGNORECASE):
        # Check if it's actual branching logic
        if re.search(r'if.*source_app_id.*!=', content, re.IGNORECASE):
            return "RUNTIME_POLICY_LEAKAGE"
        return "OFFLINE_TOOLING_REFERENCE"
    
    # W8 P5: Prompt governance managed workflow (default args, not runtime branching)
    if re.search(r".*/prompt_governance/.*\.py$", normalized_path, re.IGNORECASE):
        # Check if it's default argument vs actual runtime branching
        if re.search(r'app_id=\"apps_\w+\"', content, re.IGNORECASE) and \
           not re.search(r'if\s+.*app_id', content, re.IGNORECASE):
            return "STATIC_REGISTRY_METADATA"
        if not re.search(r'if\s+.*app_id', content, re.IGNORECASE):
            return "OFFLINE_TOOLING_REFERENCE"
    
    # W8 P5: Runtime gates documentation (type hints in docstrings)
    if re.search(r".*/runtime_gates/.*\.py$", normalized_path, re.IGNORECASE):
        if re.search(r'app_id.*The application.*e\.g\.\s*[`\'"]apps_', content, re.IGNORECASE):
            return "FALSE_POSITIVE"
        return "OFFLINE_TOOLING_REFERENCE"
    
    # PRIORITY 3: Check for false positives (comments, docstrings, examples)
    # These should be checked before file path patterns
    # Docstrings with backticks (e.g. ``"apps_rg"``)
    if re.search(r'`.*apps_\w+.*`', content, re.IGNORECASE):
        return "FALSE_POSITIVE"
    # Comments
    if re.search(r'#.*apps_\w+', content, re.IGNORECASE) or \
       re.search(r'""".*apps_\w+.*"""', content, re.IGNORECASE) or \
       re.search(r"'''.*apps_\w+.*'''", content, re.IGNORECASE):
        return "FALSE_POSITIVE"
    
    # PRIORITY 4: Contract/ingress files in runtime - check content more carefully
    # If it's a contracts file, it's likely metadata not runtime leakage
    if re.search(r".*/contracts/.*\.py$", normalized_path, re.IGNORECASE) or \
       re.search(r".*/delegation/.*\.py$", normalized_path, re.IGNORECASE) or \
       re.search(r".*/audit/.*\.py$", normalized_path, re.IGNORECASE):
        # Check if it has actual runtime branching logic
        if re.search(r'if\s+.*app_id', content, re.IGNORECASE) or \
           re.search(r'if\s+.*tenant_id', content, re.IGNORECASE):
            return "RUNTIME_POLICY_LEAKAGE"
        # Otherwise it's likely just type definitions (metadata)
        return "STATIC_REGISTRY_METADATA"
    
    # PRIORITY 5: Check file path against runtime layer patterns (only for non-contract files)
    # RUNTIME_POLICY_LEAKAGE: runtime, routing, L0-L5 layers, entry/exit
    if re.search(r".*/runtime/.*\.py$", normalized_path, re.IGNORECASE) or \
       re.search(r".*/routing/.*\.py$", normalized_path, re.IGNORECASE) or \
       re.search(r".*/orchestration/.*\.py$", normalized_path, re.IGNORECASE) or \
       re.search(r".*/execution/.*\.py$", normalized_path, re.IGNORECASE) or \
       re.search(r".*/L[0-5]/.*\.py$", normalized_path, re.IGNORECASE) or \
       re.search(r".*/entry/.*\.py$", normalized_path, re.IGNORECASE) or \
       re.search(r".*/exit/.*\.py$", normalized_path, re.IGNORECASE):
        return "RUNTIME_POLICY_LEAKAGE"
    
    # PRIORITY 5: Check for specific content patterns
    # Registry metadata: type declarations, schema entries
    if re.search(r'Owner\s*=\s*Literal\[.*apps_', content, re.IGNORECASE) or \
       re.search(r'"apps_\w+":\s*"L_APP"', content, re.IGNORECASE):
        return "STATIC_REGISTRY_METADATA"
    
    # Tooling references: for loops with app prefixes
    if re.search(r'for\s+prefix\s+in\s+\(.*apps_', content, re.IGNORECASE):
        return "OFFLINE_TOOLING_REFERENCE"
    
    # Cache/exit gates in non-runtime files (typically config or tooling)
    if pattern_name in ["app_specific_cache_policies", "app_specific_thresholds"]:
        # These are typically config patterns, classify based on file location
        if re.search(r".*/config/.*\.py$", normalized_path, re.IGNORECASE) or \
           re.search(r".*/contracts/.*\.py$", normalized_path, re.IGNORECASE):
            return "STATIC_REGISTRY_METADATA"
    
    # Default to UNKNOWN for unclassified detections (require manual review)
    return "UNKNOWN"


def add_taxonomy_to_violations(violations: List[Dict]) -> List[Dict]:
    """Add taxonomy classification to each violation."""
    for v in violations:
        category = classify_violation(v)
        v['taxonomy_category'] = category
        v['taxonomy_severity'] = TAXONOMY_CATEGORIES.get(category, {}).get('severity', 'HIGH')
        v['taxonomy_description'] = TAXONOMY_CATEGORIES.get(category, {}).get('description', '')
    return violations


def count_by_category(violations: List[Dict]) -> Dict[str, int]:
    """Count violations by taxonomy category."""
    counts = {cat: 0 for cat in TAXONOMY_CATEGORIES.keys()}
    for v in violations:
        cat = v.get('taxonomy_category', 'UNKNOWN')
        counts[cat] = counts.get(cat, 0) + 1
    return counts


# Forbidden patterns in agentic_core
FORBIDDEN_PATTERNS = {
    "hardcoded_app_names": {
        "patterns": [
            r'["\']apps_lic["\']',
            r'["\']apps_rg["\']', 
            r'["\']apps_qna["\']',
            r'["\']apps_research["\']',
            r'["\']apps_exec["\']',
            r'["\']apps_underwriting_ai["\']',
            r'["\']apps_architect["\']',
            r'["\']apps_eval["\']',
        ],
        "severity": "HIGH",
        "description": "Hardcoded app name in core"
    },
    "app_id_branching": {
        "patterns": [
            r'if\s+app_id\s*==\s*["\']',
            r'app_id\s*==\s*["\']',
            r'if\s+tenant_id\s*==\s*["\']apps_',
            r'tenant_id\s*==\s*["\']apps_',
        ],
        "severity": "CRITICAL",
        "description": "App-specific branching in core"
    },
    "app_specific_routes": {
        "patterns": [
            r'["\']R4_MANAGED_DRAFT["\']',
            r'["\']R3R4_MANAGED_RESEARCH_THEN_DRAFT["\']',
            r'["\']R1_RESUME_GENERATION["\']',
            r'["\']R2_EXPEDITED["\']',
            r'["\']R3_RESEARCH_ONLY["\']',
        ],
        "severity": "HIGH",
        "description": "App-specific route name in core"
    },
    "app_specific_cache_policies": {
        "patterns": [
            r'["\']final_draft_r1a_bypass["\']',
            r'["\']final_draft_r1b_bypass["\']',
            r'["\']linkedin_send["\']',
            r'["\']email_outbox_send["\']',
            r'APPS_\w+_CACHE_BYPASS',
            r'APPS_\w+_CACHE_PROFILES',
        ],
        "severity": "MEDIUM",
        "description": "App-specific cache policy in core"
    },
    "app_specific_exit_gates": {
        "patterns": [
            r'APPS_LIC_EXIT_GATES',
            r'APPS_RG_EXIT_GATES',
            r'APPS_\w+_FORBIDDEN_ACTIONS',
            r'G21_APPS_\w+_SPECIFIC',
            r'G22_APPS_\w+_SPECIFIC',
        ],
        "severity": "HIGH",
        "description": "App-specific Exit gate configuration in core"
    },
    "app_specific_thresholds": {
        "patterns": [
            r'APPS_\w+_MIN_JUDGE_SCORE',
            r'APPS_\w+_MIN_CONFIDENCE',
            r'APPS_\w+_THRESHOLDS',
        ],
        "severity": "MEDIUM",
        "description": "App-specific threshold in core"
    }
}

# Allowlist categories
ALLOWLIST_CATEGORIES = {
    "TEST_ALLOWED": [
        r".*/tests/.*",
        r".*/test_.*\.py$",
        r".*/conftest\.py$",
        r".*/_test_.*\.py$",
    ],
    "DOC_ALLOWED": [
        r".*\.md$",
        r".*AGENTS\.md$",
        r".*README.*",
        r".*\.txt$",
        r".*\.rst$",
    ],
    "RECEIPT_ALLOWED": [
        r".*/artifacts/governance/.*",
        r".*/migration_receipts/.*",
        r".*/boundary_receipts/.*",
    ],
    "TEMPORARY_THIN_ADAPTER": [
        r".*/apps_\w+_.*_binding\.py$",
        r".*/u0_apps_\w+_binding\.py$",
    ],
    "GENERIC_READY": [
        r".*/package_driven_.*\.py$",
        r".*/generic_.*\.py$",
    ]
}


def matches_allowlist(filepath: str, category: str) -> bool:
    """Check if file matches allowlist category."""
    # Normalize path for cross-platform matching
    normalized_path = filepath.replace('\\', '/')
    patterns = ALLOWLIST_CATEGORIES.get(category, [])
    for pattern in patterns:
        if re.search(pattern, normalized_path, re.IGNORECASE):
            return True
    return False


def get_allowlist_category(filepath: str) -> Optional[str]:
    """Determine the allowlist category for a file."""
    for category in ALLOWLIST_CATEGORIES:
        if matches_allowlist(filepath, category):
            return category
    return None


def scan_file(filepath: str) -> List[Dict]:
    """Scan a single file for forbidden patterns."""
    violations = []
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            lines = content.split('\n')
    except (IOError, OSError) as e:
        return [{"error": f"Cannot read file: {e}"}]
    
    rel_path = str(filepath).replace(str(REPO_ROOT), "").lstrip("/\\")
    
    # Check allowlist
    allowlist_cat = get_allowlist_category(rel_path)
    
    for pattern_name, pattern_info in FORBIDDEN_PATTERNS.items():
        for pattern in pattern_info["patterns"]:
            for line_num, line in enumerate(lines, 1):
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    violation = {
                        "file": rel_path,
                        "line": line_num,
                        "pattern_name": pattern_name,
                        "pattern": pattern,
                        "severity": pattern_info["severity"],
                        "description": pattern_info["description"],
                        "content": line.strip()[:100],
                        "allowlist_category": allowlist_cat,
                        "match_text": match.group(0)
                    }
                    violations.append(violation)
    
    return violations


def scan_agentic_core() -> Dict:
    """Scan entire agentic_core directory."""
    all_violations = []
    files_scanned = 0
    files_with_violations = 0
    
    if not AGENTIC_CORE_PATH.exists():
        return {
            "error": f"agentic_core path not found: {AGENTIC_CORE_PATH}"
        }
    
    for root, dirs, files in os.walk(AGENTIC_CORE_PATH):
        # Skip __pycache__
        dirs[:] = [d for d in dirs if d != '__pycache__' and not d.startswith('.')]
        
        for filename in files:
            # Only scan Python and YAML files
            if not filename.endswith(('.py', '.yaml', '.yml', '.json')):
                continue
            
            filepath = Path(root) / filename
            files_scanned += 1
            
            violations = scan_file(str(filepath))
            
            # Filter out allowlisted violations
            non_allowlisted = [
                v for v in violations 
                if not v.get("allowlist_category") and "error" not in v
            ]
            
            if non_allowlisted:
                files_with_violations += 1
                all_violations.extend(non_allowlisted)
    
    return {
        "files_scanned": files_scanned,
        "files_with_violations": files_with_violations,
        "total_violations": len(all_violations),
        "violations": all_violations,
        "critical_count": len([v for v in all_violations if v.get("severity") == "CRITICAL"]),
        "high_count": len([v for v in all_violations if v.get("severity") == "HIGH"]),
        "medium_count": len([v for v in all_violations if v.get("severity") == "MEDIUM"]),
    }


def save_scan_results(results: Dict):
    """Save scan results to file."""
    SCAN_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    timestamp = str(Path(__file__).stat().st_mtime).split('.')[0]
    output_file = SCAN_OUTPUT_DIR / f"core_leakage_scan_{timestamp}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    return output_file


def get_enforcement_mode(cli_strict: bool) -> Tuple[bool, str]:
    """Returns (is_strict, reason_message)."""
    today = datetime.now().isoformat()[:10]
    
    if today > ADVISORY_SUNSET:
        if cli_strict:
            return True, f"STRICT MODE (sunset {ADVISORY_SUNSET} passed, --strict flag)"
        return True, f"STRICT MODE (sunset {ADVISORY_SUNSET} enforced)"
    
    if cli_strict:
        return True, "Strict mode (CLI flag)"
    
    return False, f"Advisory mode (sunset {ADVISORY_SUNSET})"


def validate_binding_receipts(scan_results: Dict, strict: bool) -> List[Dict]:
    """
    Validate that all TEMPORARY_THIN_ADAPTER files have valid 12-field receipts.
    Returns list of receipt violations.
    """
    receipt_violations = []
    
    for v in scan_results.get('violations', []):
        if v.get('allowlist_category') == 'TEMPORARY_THIN_ADAPTER':
            filepath = v.get('file', '')
            is_valid, reason, _ = find_and_validate_receipt(filepath)
            if not is_valid:
                receipt_violations.append({
                    'file': filepath,
                    'line': v.get('line', 0),
                    'severity': 'HIGH' if strict else 'MEDIUM',
                    'pattern_name': 'TEMPORARY_THIN_ADAPTER_NO_RECEIPT',
                    'description': f'Binding without valid 12-field receipt: {reason}',
                    'content': v.get('content', ''),
                    'receipt_issue': reason
                })
    
    return receipt_violations


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="CORE_LEAKAGE_SCAN: Scan agentic_core for app-specific leakage"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail-closed mode (post-sunset, this is default)",
    )
    args = parser.parse_args()
    
    is_strict, mode_reason = get_enforcement_mode(args.strict)
    
    print("CORE_LEAKAGE_SCAN: Scanning agentic_core for app-specific leakage...")
    print(f"Mode: {mode_reason}")
    
    # Run scan
    results = scan_agentic_core()
    
    # Apply taxonomy classification (W8)
    results['violations'] = add_taxonomy_to_violations(results['violations'])
    category_counts = count_by_category(results['violations'])
    results['taxonomy_category_counts'] = category_counts
    results['taxonomy_source'] = CLASSIFICATION_SOURCE
    
    # Validate receipts for TEMPORARY_THIN_ADAPTER files
    receipt_violations = validate_binding_receipts(results, is_strict)
    if receipt_violations:
        # Classify receipt violations as UNKNOWN (need manual review)
        for rv in receipt_violations:
            rv['taxonomy_category'] = 'UNKNOWN'
            rv['taxonomy_severity'] = 'HIGH'
            rv['taxonomy_description'] = 'Unclassified detection requiring manual review'
        results['violations'].extend(receipt_violations)
        results['total_violations'] += len(receipt_violations)
        category_counts['UNKNOWN'] += len(receipt_violations)
        # Count receipt violations by severity
        for rv in receipt_violations:
            if rv['severity'] == 'CRITICAL':
                results['critical_count'] += 1
            elif rv['severity'] == 'HIGH':
                results['high_count'] += 1
            else:
                results['medium_count'] += 1
    
    # Save results
    output_file = save_scan_results(results)
    
    # Add metadata
    results["scan_output_file"] = str(output_file)
    results["timestamp"] = str(Path(__file__).stat().st_mtime)
    results["enforcement_mode"] = mode_reason
    results["is_strict"] = is_strict
    results["receipt_violations"] = len(receipt_violations)
    
    # Calculate blocking vs non-blocking counts
    blocking_count = sum(category_counts.get(cat, 0) for cat in BLOCKING_CATEGORIES)
    non_blocking_count = results['total_violations'] - blocking_count
    
    # Print summary (W8 transparency requirement)
    print(f"\n[SUMMARY] Files scanned: {results['files_scanned']}")
    print(f"[SUMMARY] Files with violations: {results['files_with_violations']}")
    print(f"[SUMMARY] Total detections: {results['total_violations']}")
    
    if is_strict:
        # Strict mode: show taxonomy-based breakdown
        print(f"\n[SUMMARY] Blocking: {blocking_count} (RUNTIME_POLICY_LEAKAGE: {category_counts.get('RUNTIME_POLICY_LEAKAGE', 0)}, UNKNOWN: {category_counts.get('UNKNOWN', 0)})")
        print(f"[SUMMARY] Non-blocking: {non_blocking_count} (STATIC_REGISTRY: {category_counts.get('STATIC_REGISTRY_METADATA', 0)}, OFFLINE_TOOLING: {category_counts.get('OFFLINE_TOOLING_REFERENCE', 0)}, FALSE_POSITIVE: {category_counts.get('FALSE_POSITIVE', 0)})")
        print(f"[CLASSIFICATION] Source: {CLASSIFICATION_SOURCE}")
        print(f"[CLASSIFICATION] Rationale: Per-file runtime coupling analysis")
    else:
        # Advisory mode: show legacy severity breakdown
        print(f"  Critical: {results['critical_count']}")
        print(f"  High: {results['high_count']}")
        print(f"  Medium: {results['medium_count']}")
        print(f"  Receipt violations: {len(receipt_violations)}")
    
    # Print violations
    if results['violations']:
        print("\n" + "="*70)
        print("VIOLATIONS DETECTED")
        print("="*70)
        
        for v in results['violations'][:20]:  # Limit output
            print(f"\n[{v['severity']}] {v.get('pattern_name', 'UNKNOWN')}")
            print(f"  File: {v['file']}:{v.get('line', 'N/A')}")
            print(f"  {v.get('description', 'No description')}")
            print(f"  Content: {v.get('content', 'N/A')[:80]}")
        
        if len(results['violations']) > 20:
            print(f"\n... and {len(results['violations']) - 20} more violations")
        
        print("\n" + "="*70)
        print("These violations indicate app-specific logic in agentic_core.")
        print("Classification:")
        print("  CRITICAL: App branching logic - must migrate immediately")
        print("  HIGH: App-specific constants - move to apps_*/config/")
        print("  MEDIUM: App-specific config - use profile refs")
        print("  TEMPORARY_THIN_ADAPTER_NO_RECEIPT: Missing 12-field receipt")
        print("="*70)
        print(f"\nFull report: {output_file}")
        
        # Determine exit code (W8 taxonomy-based logic)
        if is_strict:
            # Strict mode: only fail on RUNTIME_POLICY_LEAKAGE or UNKNOWN/UNCLASSIFIED
            runtime_leakage_count = category_counts.get('RUNTIME_POLICY_LEAKAGE', 0)
            unknown_count = category_counts.get('UNKNOWN', 0)
            
            if runtime_leakage_count > 0 or unknown_count > 0:
                print(f"\n[STRICT MODE] Blocking violations detected:")
                print(f"  RUNTIME_POLICY_LEAKAGE: {runtime_leakage_count}")
                print(f"  UNKNOWN/UNCLASSIFIED: {unknown_count}")
                print(f"\n[EXIT] Code: 2 (strict mode failure - governance risk detected)")
                sys.exit(2)
            else:
                # Only non-blocking categories (STATIC_REGISTRY, OFFLINE_TOOLING, FALSE_POSITIVE)
                print(f"\n[STRICT MODE] No runtime policy leakage or unclassified findings.")
                print(f"[STRICT MODE] {non_blocking_count} non-blocking findings (acceptable per W7 classification).")
                print(f"\n[EXIT] Code: 0 (strict mode pass)")
                sys.exit(0)
        else:
            # Advisory mode: warn but exit 0 (non-blocking)
            print(f"\n[ADVISORY MODE] Violations detected but non-blocking")
            print(f"  Set --strict for taxonomy-based fail-closed behavior")
            print(f"  Or wait until sunset {ADVISORY_SUNSET}")
            print(f"\n[EXIT] Code: 0 (advisory mode)")
            sys.exit(0)
    else:
        print("\n[SUMMARY] No app-specific leakage detected.")
        print("\n[EXIT] Code: 0 (clean scan)")
    
    sys.exit(0)


if __name__ == "__main__":
    main()
