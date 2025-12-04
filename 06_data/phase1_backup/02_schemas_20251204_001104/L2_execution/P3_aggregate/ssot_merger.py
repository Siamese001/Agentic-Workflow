#!/usr/bin/env python3
"""
Canonical SSoT MERGE Implementation for Agentic-Workflow

Implements G5: COMBINED_SSoT = MERGE(SSoT_YAML, SSoT_META)

This module provides the canonical merge function that combines the main
unified_structure_subatomic.yaml with unified_structure_subatomic_meta.yaml
to produce the authoritative Single Source of Truth structure.
"""

import yaml
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from copy import deepcopy


class SSoTMerger:
    """
    Canonical SSoT MERGE implementation
    
    Combines main YAML structure with meta YAML according to binding rules:
    - Main YAML provides the file system structure
    - Meta YAML provides vocab constraints and protected paths
    - MERGE produces canonical SSoT for all phases
    """
    
    def __init__(self, workspace_root: Path):
        self.workspace_root = Path(workspace_root)
        self.main_yaml_path = self.workspace_root / "unified_structure_subatomic.yaml"
        self.meta_yaml_path = self.workspace_root / "unified_structure_subatomic_meta.yaml"
        
    def load_yaml_files(self) -> tuple[Dict[str, Any], Dict[str, Any]]:
        """Load main and meta YAML files"""
        try:
            with open(self.main_yaml_path, 'r', encoding='utf-8') as f:
                main_yaml = yaml.safe_load(f)
            
            with open(self.meta_yaml_path, 'r', encoding='utf-8') as f:
                meta_yaml = yaml.safe_load(f)
                
            return main_yaml, meta_yaml
            
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Required SSoT file not found: {e}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML format: {e}")
    
    def validate_binding(self, main_yaml: Dict[str, Any], meta_yaml: Dict[str, Any]) -> bool:
        """
        Validate G1-G2: Confirm YAML/META binding is correct
        
        Returns True if binding is valid, raises exception if invalid
        """
        # Check main YAML references meta sidecar
        if main_yaml.get('meta_sidecar') != 'unified_structure_subatomic_meta.yaml':
            raise ValueError("Main YAML does not reference correct meta sidecar")
        
        if 'canonical_definition' not in main_yaml:
            raise ValueError("Main YAML missing canonical_definition")
        
        # Check meta YAML binds to main YAML
        if meta_yaml.get('binds_to') != 'unified_structure_subatomic.yaml':
            raise ValueError("Meta YAML does not bind to correct main YAML")
        
        if 'canonical_role' not in meta_yaml:
            raise ValueError("Meta YAML missing canonical_role")
        
        return True
    
    def extract_structure_from_main(self, main_yaml: Dict[str, Any]) -> Dict[str, Any]:
        """Extract the domain structure from main YAML"""
        structure = {}
        
        # Extract all top-level domains (excluding meta fields)
        meta_fields = {'meta_sidecar', 'canonical_definition'}
        
        for key, value in main_yaml.items():
            if key not in meta_fields:
                structure[key] = deepcopy(value)
        
        return structure
    
    def extract_constraints_from_meta(self, meta_yaml: Dict[str, Any]) -> Dict[str, Any]:
        """Extract vocab constraints and protected paths from meta YAML"""
        constraints = {
            'domains': meta_yaml.get('domains', {}),
            'layers': meta_yaml.get('layers', {}),
            'phases': meta_yaml.get('phases', {}),
            'intents': meta_yaml.get('intents', []),
            'axes': meta_yaml.get('axes', []),
            'verb_groups': meta_yaml.get('verb_groups', []),
            'protected_paths': meta_yaml.get('protected_paths', []),
            'structure_version': meta_yaml.get('structure_version'),
            'description': meta_yaml.get('description')
        }
        
        return constraints
    
    def merge_structure_with_constraints(self, structure: Dict[str, Any], 
                                        constraints: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform the canonical MERGE operation
        
        Combines file system structure with vocab constraints to produce
        the authoritative SSoT used by all phases.
        """
        # Start with deep copy of structure
        combined = deepcopy(structure)
        
        # Add canonical metadata and constraints
        combined['_meta'] = {
            'canonical_definition': "Canonical SSoT = MERGE(main_yaml, meta_yaml)",
            'structure_version': constraints['structure_version'],
            'description': constraints['description'],
            'domains': constraints['domains'],
            'layers': constraints['layers'], 
            'phases': constraints['phases'],
            'intents': constraints['intents'],
            'axes': constraints['axes'],
            'verb_groups': constraints['verb_groups'],
            'protected_paths': constraints['protected_paths']
        }
        
        # Validate that all structure domains exist in meta domains
        structure_domains = set(combined.keys()) - {'_meta'}
        meta_domains = set(constraints['domains'].keys())
        
        missing_domains = structure_domains - meta_domains
        if missing_domains:
            raise ValueError(f"Structure domains missing from meta: {missing_domains}")
        
        return combined
    
    def merge(self) -> Dict[str, Any]:
        """
        Main MERGE function: COMBINED_SSoT = MERGE(SSoT_YAML, SSoT_META)
        
        Returns:
            Dict containing the canonical merged SSoT structure
        """
        # Load both YAML files
        main_yaml, meta_yaml = self.load_yaml_files()
        
        # Validate binding (G1-G2)
        self.validate_binding(main_yaml, meta_yaml)
        
        # Extract components
        structure = self.extract_structure_from_main(main_yaml)
        constraints = self.extract_constraints_from_meta(meta_yaml)
        
        # Perform canonical merge
        combined_ssot = self.merge_structure_with_constraints(structure, constraints)
        
        return combined_ssot
    
    def save_combined_ssot(self, combined_ssot: Dict[str, Any], 
                          output_path: Optional[Path] = None) -> Path:
        """
        Save the combined SSoT to a file for consumption by phases
        
        Args:
            combined_ssot: The merged SSoT structure
            output_path: Optional custom output path
            
        Returns:
            Path where the combined SSoT was saved
        """
        if output_path is None:
            output_path = self.workspace_root / "02_schemas" / "combined_ssot_canonical.json"
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(combined_ssot, f, indent=2, ensure_ascii=False)
        
        return output_path
    
    def get_canonical_loader(self) -> callable:
        """
        Returns a callable that phases can use to load the canonical SSoT
        
        Usage in phases:
        COMBINED_SSoT_CANONICAL = ssot_loader()
        """
        def load_canonical_ssot():
            return self.merge()
        
        return load_canonical_ssot


def main():
    """
    CLI entry point for SSoT merger
    
    Usage:
    python ssot_merger.py [--workspace /path/to/workspace]
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate canonical SSoT from YAML and META")
    parser.add_argument("--workspace", type=Path, default=Path.cwd(),
                       help="Path to Agentic-Workflow workspace")
    parser.add_argument("--output", type=Path, 
                       help="Output path for combined SSoT")
    parser.add_argument("--validate-only", action="store_true",
                       help="Only validate binding, don't generate output")
    
    args = parser.parse_args()
    
    merger = SSoTMerger(args.workspace)
    
    try:
        if args.validate_only:
            main_yaml, meta_yaml = merger.load_yaml_files()
            merger.validate_binding(main_yaml, meta_yaml)
            print("✓ YAML/META binding validation passed")
        else:
            combined_ssot = merger.merge()
            output_path = merger.save_combined_ssot(combined_ssot, args.output)
            print(f"✓ Canonical SSoT generated: {output_path}")
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
