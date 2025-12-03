#!/usr/bin/env python3
"""
Filesystem Canonicalizer Engine for Agentic-Workflow

Implements Phase 1 filesystem canonicalization for K14-K17 validation

Provides filesystem structure canonicalization, normalization,
and validation capabilities for Phase 1 operations.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class CanonicalizationResult:
    original_structure: Dict[str, Any]
    canonical_structure: Dict[str, Any]
    normalization_applied: List[str]
    validation_status: str
    timestamp: str


class FilesystemCanonicalizer:
    """
    Filesystem canonicalization engine
    
    Normalizes and validates filesystem structure according to
    canonical SSoT definitions for Phase 1 compliance.
    """
    
    def __init__(self, workspace_root: Path):
        self.workspace_root = Path(workspace_root)
        self.canonical_ssot_path = self.workspace_root / "02_schemas" / "canonical_ssot.json"
        
        # Add path for imports
        sys.path.insert(0, str(self.workspace_root / "02_schemas"))
        
        # Load SSoT merger for canonical structure
        from ssot_merger import SSoTMerger
        self.ssot_merger = SSoTMerger(workspace_root)
        
        self.canonical_structure: Dict[str, Any] = {}
        self.normalization_rules: List[str] = []
    
    def load_canonical_structure(self) -> bool:
        """Load canonical SSoT structure"""
        try:
            self.canonical_structure = self.ssot_merger.merge()
            return True
        except Exception as e:
            print(f"Failed to load canonical structure: {e}")
            return False
    
    def extract_filesystem_structure(self) -> Dict[str, Any]:
        """Extract current filesystem structure"""
        def build_structure(path: Path, prefix: str = "") -> Dict[str, Any]:
            structure = {}
            
            try:
                for item in path.iterdir():
                    # Skip system files and directories
                    if item.name.startswith(('.', '_')):
                        continue
                    
                    relative_path = str(item.relative_to(self.workspace_root)).replace('\\', '/')
                    
                    if item.is_dir():
                        # Directory - recurse
                        structure[item.name] = build_structure(item, f"{prefix}/{item.name}")
                    elif item.is_file():
                        # File - represent as null in YAML structure
                        structure[item.name] = None
            except PermissionError:
                # Skip directories we can't access
                pass
            
            return structure
        
        return build_structure(self.workspace_root)
    
    def normalize_structure(self, structure: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
        """Normalize filesystem structure according to canonical rules"""
        normalized = structure.copy()
        applied_rules = []
        
        # Rule 1: Ensure all expected domains exist
        expected_domains = set(self.canonical_structure.keys()) - {'_meta'}
        actual_domains = set(normalized.keys())
        
        missing_domains = expected_domains - actual_domains
        for domain in missing_domains:
            normalized[domain] = {}
            applied_rules.append(f"Added missing domain: {domain}")
        
        # Rule 2: Normalize layer structures within domains
        for domain, canonical_layers in self.canonical_structure.items():
            if domain == '_meta':
                continue
                
            if domain not in normalized:
                continue
                
            actual_layers = normalized[domain]
            expected_layers = set(canonical_layers.keys()) if canonical_layers else set()
            actual_layer_names = set(actual_layers.keys()) if actual_layers else set()
            
            # Add missing layers
            missing_layers = expected_layers - actual_layer_names
            for layer in missing_layers:
                actual_layers[layer] = {}
                applied_rules.append(f"Added missing layer {layer} in domain {domain}")
        
        # Rule 3: Remove unexpected files/directories (non-critical)
        # For now, we keep them but note them in applied rules
        for domain in list(normalized.keys()):
            if domain not in expected_domains and domain not in ['unified_structure_subatomic.yaml', 'unified_structure_subatomic_meta.yaml']:
                applied_rules.append(f"Unexpected domain found: {domain}")
        
        return normalized, applied_rules
    
    def validate_canonical_compliance(self, structure: Dict[str, Any]) -> bool:
        """Validate structure against canonical SSoT"""
        try:
            # Check top-level domains
            expected_domains = set(self.canonical_structure.keys()) - {'_meta'}
            actual_domains = set(structure.keys())
            
            # All expected domains should exist
            missing_domains = expected_domains - actual_domains
            if missing_domains:
                return False
            
            # Validate each domain structure
            for domain, canonical_content in self.canonical_structure.items():
                if domain == '_meta':
                    continue
                    
                if domain not in structure:
                    return False
                
                # Basic structure validation - check if layers exist
                if isinstance(canonical_content, dict) and isinstance(structure[domain], dict):
                    expected_layers = set(canonical_content.keys())
                    actual_layers = set(structure[domain].keys())
                    
                    # Should have at least the expected layers
                    if not expected_layers.issubset(actual_layers):
                        return False
            
            return True
            
        except Exception:
            return False
    
    def generate_canonicalization_report(self) -> CanonicalizationResult:
        """Generate comprehensive canonicalization report"""
        try:
            # Load canonical structure
            if not self.canonical_structure:
                self.load_canonical_structure()
            
            # Extract current filesystem structure
            current_structure = self.extract_filesystem_structure()
            
            # Normalize structure
            normalized_structure, applied_rules = self.normalize_structure(current_structure)
            
            # Validate compliance
            validation_status = "COMPLIANT" if self.validate_canonical_compliance(normalized_structure) else "NON_COMPLIANT"
            
            result = CanonicalizationResult(
                original_structure=current_structure,
                canonical_structure=normalized_structure,
                normalization_applied=applied_rules,
                validation_status=validation_status,
                timestamp=datetime.now().isoformat()
            )
            
            return result
            
        except Exception as e:
            raise ValueError(f"Failed to generate canonicalization report: {e}")
    
    def save_canonicalization_report(self, output_path: Optional[Path] = None) -> Path:
        """Save canonicalization report to file"""
        if output_path is None:
            output_path = self.workspace_root / "02_schemas" / "canonicalization_report.json"
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        report = self.generate_canonicalization_report()
        
        report_dict = {
            "timestamp": report.timestamp,
            "validation_status": report.validation_status,
            "normalization_rules_applied": report.normalization_applied,
            "original_structure": report.original_structure,
            "canonical_structure": report.canonical_structure,
            "compliance_summary": {
                "domains_validated": len(set(self.canonical_structure.keys()) - {'_meta'}),
                "normalizations_applied": len(report.normalization_applied),
                "is_compliant": report.validation_status == "COMPLIANT"
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_dict, f, indent=2, ensure_ascii=False)
        
        return output_path
    
    def is_canonicalizer_operational(self) -> bool:
        """Check if canonicalizer is operational"""
        try:
            return self.load_canonical_structure() and bool(self.canonical_structure)
        except:
            return False


def main():
    """CLI entry point for filesystem canonicalizer"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Filesystem canonicalizer for Phase 1 operations")
    parser.add_argument("--workspace", type=Path, default=Path.cwd(),
                       help="Path to Agentic-Workflow workspace")
    parser.add_argument("--action", type=str, default="check",
                       choices=["validate", "report", "check"],
                       help="Action to perform")
    parser.add_argument("--output", type=Path,
                       help="Output path for report")
    
    args = parser.parse_args()
    
    canonicalizer = FilesystemCanonicalizer(args.workspace)
    
    try:
        if args.action == "validate":
            canonicalizer.load_canonical_structure()
            current_structure = canonicalizer.extract_filesystem_structure()
            is_compliant = canonicalizer.validate_canonical_compliance(current_structure)
            print(f"Filesystem canonical compliance: {'PASS' if is_compliant else 'FAIL'}")
            return 0 if is_compliant else 1
            
        elif args.action == "report":
            output_path = canonicalizer.save_canonicalization_report(args.output)
            print(f"Canonicalization report generated: {output_path}")
            return 0
            
        elif args.action == "check":
            is_operational = canonicalizer.is_canonicalizer_operational()
            print(f"Filesystem canonicalizer operational: {'PASS' if is_operational else 'FAIL'}")
            return 0 if is_operational else 1
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
