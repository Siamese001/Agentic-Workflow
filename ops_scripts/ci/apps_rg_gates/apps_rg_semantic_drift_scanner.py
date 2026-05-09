#!/usr/bin/env python3
"""
DS-5: Semantic Drift Scanner for apps_rg Profile YAMLs
Detects semantic drift between profile YAMLs and contract schemas.
"""
import json
import sys
from pathlib import Path
from typing import Dict, List, Any

try:
    import yaml
except ImportError:
    print(json.dumps({
        "passed": False,
        "error": "PyYAML required: pip install pyyaml",
        "scanner": "apps_rg_semantic_drift_scanner"
    }))
    sys.exit(1)

# Schema definitions for contract fields
CONTRACT_SCHEMAS = {
    "AppsRgIngressPayload": {
        "required": ["target_company", "target_role", "jd_text"],
        "optional": ["manual_brief", "auto_research", "profile_pack_digest"],
        "forbidden": ["planner_config", "router_config", "executor_config", "provider_config"]
    },
    "AppsRgProfileManifest": {
        "required": ["schema_version", "profiles"],
        "optional": ["capability_hints", "style_preferences"],
        "forbidden": ["runtime_bindings", "execution_plan"]
    }
}

# Profile YAML allowed top-level keys
PROFILE_SCHEMA = {
    "planning": ["duplicate_similarity_target", "min_quality_score", "pass_threshold", "scoring_weights", "power_verbs"],
    "evidence": ["required_evidence_types", "optional_evidence_types", "evidence_sufficiency_threshold"],
    "prompt": ["template_preferences", "slot_mappings", "pa_boundary_rules"],
    "style": ["tone_preferences", "formatting_rules", "section_order"],
    "capability": ["supported_output_formats", "max_sections", "length_budget"]
}


def scan_profile_yaml(path: Path) -> List[Dict[str, Any]]:
    """Scan a profile YAML for semantic drift from contract schemas."""
    violations = []
    
    try:
        content = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as e:
        violations.append({
            "file": str(path),
            "type": "parse_error",
            "message": f"Failed to parse YAML: {e}"
        })
        return violations
    
    if not isinstance(content, dict):
        violations.append({
            "file": str(path),
            "type": "schema_error",
            "message": "Profile YAML must be a dictionary"
        })
        return violations
    
    # Check for forbidden runtime keys at top level
    forbidden_runtime_keys = [
        "planner", "router", "orchestrator", "executor", "provider", 
        "gateway", "judge", "disposition", "state_write", "learning"
    ]
    
    for key in content.keys():
        if any(forbid in key.lower() for forbid in forbidden_runtime_keys):
            violations.append({
                "file": str(path),
                "type": "semantic_drift",
                "severity": "CRITICAL",
                "message": f"Profile contains runtime-forbidden key: '{key}' (violates AG-RGGOV-1)",
                "contract_ref": "AppsRgRuntimeAuthorityPolicy"
            })
    
    # Check for schema_version field presence
    if "schema_version" not in content and "version" not in content:
        violations.append({
            "file": str(path),
            "type": "missing_field",
            "severity": "WARNING",
            "message": "Profile missing schema_version - may drift from contract"
        })
    
    return violations


def scan_contract_consistency(repo_root: Path) -> List[Dict[str, Any]]:
    """Scan for consistency between profiles and contracts."""
    violations = []
    
    profiles_dir = repo_root / "apps_rg" / "profiles"
    contracts_dir = repo_root / "agentic_core" / "runtime" / "contracts"
    
    if not profiles_dir.exists():
        violations.append({
            "type": "setup_error",
            "message": f"Profiles directory not found: {profiles_dir}"
        })
        return violations
    
    # Scan all profile YAMLs
    for yaml_file in profiles_dir.glob("*.yaml"):
        violations.extend(scan_profile_yaml(yaml_file))
    
    # Check contract schemas exist
    if not contracts_dir.exists():
        violations.append({
            "type": "setup_error",
            "message": f"Contracts directory not found: {contracts_dir}"
        })
    
    return violations


def main():
    import argparse
    parser = argparse.ArgumentParser(description="apps_rg Semantic Drift Scanner")
    parser.add_argument("--repo-path", default=".", help="Repository root path")
    parser.add_argument("--output-format", choices=["json", "text"], default="text")
    args = parser.parse_args()
    
    repo_root = Path(args.repo_path).resolve()
    violations = scan_contract_consistency(repo_root)
    
    passed = len(violations) == 0
    
    result = {
        "passed": passed,
        "violations": violations,
        "scanner": "apps_rg_semantic_drift_scanner",
        "version": "DS-5.0",
        "scan_timestamp": str(Path(__file__).stat().st_mtime)
    }
    
    if args.output_format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(f"Semantic Drift Scanner: {'PASS' if passed else 'FAIL'}")
        print(f"Violations: {len(violations)}")
        for v in violations:
            print(f"  - [{v.get('severity', 'ERROR')}] {v.get('file', 'N/A')}: {v.get('message', '')}")
    
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
