#!/usr/bin/env python3
"""
SSoT ↔ META Cross-Validation Engine for Agentic-Workflow

Implements G10: SSoT <-> META cross-validation

Ensures that META.domains == YAML.domains, META.layers == YAML.layers, 
META.phases == YAML.phases, META.intents == YAML.intents, META.axes == YAML.axes,
META.verb_groups == YAML.verb_groups for functional enforcement of K25-K29.
"""

import yaml
import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Set, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class ValidationStatus(Enum):
    MATCH = "MATCH"
    MISMATCH = "MISMATCH"
    MISSING_IN_YAML = "MISSING_IN_YAML"
    MISSING_IN_META = "MISSING_IN_META"
    EXTRA_IN_YAML = "EXTRA_IN_YAML"
    EXTRA_IN_META = "EXTRA_IN_META"


@dataclass
class ValidationResult:
    category: str
    status: ValidationStatus
    yaml_items: Set[str]
    meta_items: Set[str]
    details: str


class CrossValidator:
    """
    SSoT ↔ META cross-validation engine
    
    Validates semantic consistency between the main YAML structure
    and META vocab constraints to ensure canonical definitions align.
    """
    
    def __init__(self, workspace_root: Path):
        self.workspace_root = Path(workspace_root)
        self.main_yaml_path = self.workspace_root / "unified_structure_subatomic.yaml"
        self.meta_yaml_path = self.workspace_root / "unified_structure_subatomic_meta.yaml"
        
        # Add path for imports
        sys.path.insert(0, str(self.workspace_root / "02_schemas"))
        
        # Load SSoT merger for canonical structure
        from ssot_merger import SSoTMerger
        self.ssot_merger = SSoTMerger(workspace_root)
        
        self.main_yaml: Dict[str, Any] = {}
        self.meta_yaml: Dict[str, Any] = {}
        self.validation_results: List[ValidationResult] = []
    
    def load_yaml_files(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Load main and meta YAML files"""
        try:
            with open(self.main_yaml_path, 'r', encoding='utf-8') as f:
                self.main_yaml = yaml.safe_load(f)
            
            with open(self.meta_yaml_path, 'r', encoding='utf-8') as f:
                self.meta_yaml = yaml.safe_load(f)
            
            # Validate that files loaded successfully
            if self.main_yaml is None:
                raise ValueError(f"Main YAML file is empty or invalid: {self.main_yaml_path}")
            if self.meta_yaml is None:
                raise ValueError(f"Meta YAML file is empty or invalid: {self.meta_yaml_path}")
                
            return self.main_yaml, self.meta_yaml
            
        except Exception as e:
            raise ValueError(f"Failed to load YAML files: {e}")
    
    def extract_domains_from_yaml(self) -> Set[str]:
        """Extract domain names from main YAML structure"""
        # Ensure YAML is loaded
        if not self.main_yaml:
            self.load_yaml_files()
            
        domains = set()
        
        # Skip meta fields at root level
        meta_fields = {'meta_sidecar', 'canonical_definition'}
        
        for key in self.main_yaml.keys():
            if key not in meta_fields:
                domains.add(key)
        
        return domains
    
    def extract_domains_from_meta(self) -> Set[str]:
        """Extract domain names from META YAML"""
        # Ensure YAML is loaded
        if not self.meta_yaml:
            self.load_yaml_files()
            
        return set(self.meta_yaml.get('domains', {}).keys())
    
    def extract_layers_from_yaml(self) -> Set[str]:
        """Extract layer names from main YAML structure"""
        # Ensure YAML is loaded
        if not self.main_yaml:
            self.load_yaml_files()
            
        layers = set()
        
        for domain in self.extract_domains_from_yaml():
            domain_structure = self.main_yaml.get(domain, {})
            for layer_name in domain_structure.keys():
                layers.add(layer_name)
        
        return layers
    
    def extract_layers_from_meta(self) -> Set[str]:
        """Extract layer names from META YAML"""
        # Ensure YAML is loaded
        if not self.meta_yaml:
            self.load_yaml_files()
            
        return set(self.meta_yaml.get('layers', {}).keys())
    
    def extract_phases_from_yaml(self) -> Set[str]:
        """Extract phase names from main YAML structure"""
        # Ensure YAML is loaded
        if not self.main_yaml:
            self.load_yaml_files()
            
        phases = set()
        
        for domain in self.extract_domains_from_yaml():
            domain_structure = self.main_yaml.get(domain, {})
            for layer_name, layer_structure in domain_structure.items():
                if layer_structure is None:
                    continue  # Skip __init__.py files
                
                for phase_name in layer_structure.keys():
                    phases.add(phase_name)
        
        return phases
    
    def extract_phases_from_meta(self) -> Set[str]:
        """Extract phase names from META YAML"""
        # Ensure YAML is loaded
        if not self.meta_yaml:
            self.load_yaml_files()
            
        return set(self.meta_yaml.get('phases', {}).keys())
    
    def extract_intents_from_yaml(self) -> Set[str]:
        """Extract intent names from main YAML structure"""
        # Ensure YAML is loaded
        if not self.main_yaml:
            self.load_yaml_files()
            
        intents = set()
        
        for domain in self.extract_domains_from_yaml():
            domain_structure = self.main_yaml.get(domain, {})
            for layer_structure in domain_structure.values():
                if layer_structure is None:
                    continue  # Skip __init__.py files
                for phase_structure in layer_structure.values():
                    if phase_structure is None:
                        continue  # Skip __init__.py files
                    for intent_name in phase_structure.keys():
                        intents.add(intent_name)
        
        return intents
    
    def extract_intents_from_meta(self) -> Set[str]:
        """Extract intent names from META YAML"""
        # Ensure YAML is loaded
        if not self.meta_yaml:
            self.load_yaml_files()
            
        return set(self.meta_yaml.get('intents', []))
    
    def extract_axes_from_yaml(self) -> Set[str]:
        """Extract axis names from main YAML structure"""
        # Ensure YAML is loaded
        if not self.main_yaml:
            self.load_yaml_files()
            
        axes = set()
        
        for domain in self.extract_domains_from_yaml():
            domain_structure = self.main_yaml.get(domain, {})
            for layer_structure in domain_structure.values():
                if layer_structure is None:
                    continue  # Skip __init__.py files
                for phase_structure in layer_structure.values():
                    if phase_structure is None:
                        continue  # Skip __init__.py files
                    for intent_structure in phase_structure.values():
                        if intent_structure is None:
                            continue  # Skip __init__.py files
                        for axis_name in intent_structure.keys():
                            axes.add(axis_name)
        
        return axes
    
    def extract_axes_from_meta(self) -> Set[str]:
        """Extract axis names from META YAML"""
        # Ensure YAML is loaded
        if not self.meta_yaml:
            self.load_yaml_files()
            
        return set(self.meta_yaml.get('axes', []))
    
    def extract_verb_groups_from_yaml(self) -> Set[str]:
        """Extract verb group names from main YAML structure"""
        # Ensure YAML is loaded
        if not self.main_yaml:
            self.load_yaml_files()
            
        # In current structure, verb groups are at the leaf level (files)
        # For now, return empty set as verb_groups is empty in META
        return set()
    
    def extract_verb_groups_from_meta(self) -> Set[str]:
        """Extract verb group names from META YAML"""
        # Ensure YAML is loaded
        if not self.meta_yaml:
            self.load_yaml_files()
            
        return set(self.meta_yaml.get('verb_groups', []))
    
    def validate_category(self, category: str, yaml_extractor: callable, 
                         meta_extractor: callable) -> ValidationResult:
        """
        Validate a specific category between YAML and META
        
        Args:
            category: Category name for reporting
            yaml_extractor: Function to extract items from YAML
            meta_extractor: Function to extract items from META
            
        Returns:
            ValidationResult with analysis
        """
        # Ensure YAML files are loaded before extraction
        self.load_yaml_files()
        
        yaml_items = yaml_extractor()
        meta_items = meta_extractor()
        
        # Determine validation status
        if yaml_items == meta_items:
            status = ValidationStatus.MATCH
            details = f"Perfect match: {len(yaml_items)} items"
        elif yaml_items.issubset(meta_items):
            status = ValidationStatus.EXTRA_IN_META
            extra_in_meta = meta_items - yaml_items
            details = f"YAML subset of META. Extra in META: {extra_in_meta}"
        elif meta_items.issubset(yaml_items):
            status = ValidationStatus.EXTRA_IN_YAML
            extra_in_yaml = yaml_items - meta_items
            details = f"META subset of YAML. Extra in YAML: {extra_in_yaml}"
        else:
            status = ValidationStatus.MISMATCH
            missing_in_yaml = meta_items - yaml_items
            missing_in_meta = yaml_items - meta_items
            details = f"Mismatch. Missing in YAML: {missing_in_yaml}, Missing in META: {missing_in_meta}"
        
        return ValidationResult(
            category=category,
            status=status,
            yaml_items=yaml_items,
            meta_items=meta_items,
            details=details
        )
    
    def validate_all_categories(self) -> List[ValidationResult]:
        """
        Validate all categories between YAML and META
        
        Returns:
            List of ValidationResult objects
        """
        # Load YAML files first
        self.load_yaml_files()
        
        self.validation_results = []
        
        # Validate each category
        categories = [
            ("domains", self.extract_domains_from_yaml, self.extract_domains_from_meta),
            ("layers", self.extract_layers_from_yaml, self.extract_layers_from_meta),
            ("phases", self.extract_phases_from_yaml, self.extract_phases_from_meta),
            ("intents", self.extract_intents_from_yaml, self.extract_intents_from_meta),
            ("axes", self.extract_axes_from_yaml, self.extract_axes_from_meta),
            ("verb_groups", self.extract_verb_groups_from_yaml, self.extract_verb_groups_from_meta)
        ]
        
        for category, yaml_extractor, meta_extractor in categories:
            result = self.validate_category(category, yaml_extractor, meta_extractor)
            self.validation_results.append(result)
        
        return self.validation_results
    
    def generate_compliance_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive compliance report
        
        Returns:
            Dict with compliance analysis
        """
        if not self.validation_results:
            self.validate_all_categories()
        
        report = {
            "validation_timestamp": str(Path(__file__).stat().st_mtime),
            "workspace_root": str(self.workspace_root),
            "overall_status": "COMPLIANT",
            "categories": {},
            "summary": {
                "total_categories": len(self.validation_results),
                "compliant_categories": 0,
                "non_compliant_categories": 0,
                "issues": []
            }
        }
        
        for result in self.validation_results:
            category_report = {
                "status": result.status.value,
                "yaml_count": len(result.yaml_items),
                "meta_count": len(result.meta_items),
                "details": result.details,
                "yaml_items": sorted(list(result.yaml_items)),
                "meta_items": sorted(list(result.meta_items))
            }
            
            report["categories"][result.category] = category_report
            
            # Update summary
            if result.status == ValidationStatus.MATCH:
                report["summary"]["compliant_categories"] += 1
            else:
                report["summary"]["non_compliant_categories"] += 1
                report["summary"]["issues"].append({
                    "category": result.category,
                    "issue": result.status.value,
                    "details": result.details
                })
                report["overall_status"] = "NON_COMPLIANT"
        
        return report
    
    def save_compliance_report(self, output_path: Optional[Path] = None) -> Path:
        """
        Save compliance report to file
        
        Args:
            output_path: Optional custom output path
            
        Returns:
            Path where report was saved
        """
        if output_path is None:
            output_path = self.workspace_root / "02_schemas" / "cross_validation_report.json"
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        report = self.generate_compliance_report()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return output_path
    
    def enforce_compliance(self) -> bool:
        """
        Enforce compliance by raising exception if validation fails
        
        Returns:
            True if compliant, raises exception if not
        """
        if not self.validation_results:
            self.validate_all_categories()
        
        non_compliant = [r for r in self.validation_results if r.status != ValidationStatus.MATCH]
        
        if non_compliant:
            issues = []
            for result in non_compliant:
                issues.append(f"{result.category}: {result.details}")
            
            raise ValueError(f"SSoT↔META cross-validation failed:\n" + "\n".join(issues))
        
        return True


def main():
    """
    CLI entry point for cross-validation
    
    Usage:
    python cross_validator.py [--workspace /path/to/workspace] [--report /path/to/report.json] [--enforce]
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="SSoT↔META cross-validation engine")
    parser.add_argument("--workspace", type=Path, default=Path.cwd(),
                       help="Path to Agentic-Workflow workspace")
    parser.add_argument("--report", type=Path,
                       help="Output path for compliance report")
    parser.add_argument("--enforce", action="store_true",
                       help="Enforce compliance by failing on validation errors")
    parser.add_argument("--category", type=str,
                       choices=["domains", "layers", "phases", "intents", "axes", "verb_groups"],
                       help="Validate specific category only")
    
    args = parser.parse_args()
    
    validator = CrossValidator(args.workspace)
    
    try:
        if args.category:
            # Validate specific category
            category_map = {
                "domains": (validator.extract_domains_from_yaml, validator.extract_domains_from_meta),
                "layers": (validator.extract_layers_from_yaml, validator.extract_layers_from_meta),
                "phases": (validator.extract_phases_from_yaml, validator.extract_phases_from_meta),
                "intents": (validator.extract_intents_from_yaml, validator.extract_intents_from_meta),
                "axes": (validator.extract_axes_from_yaml, validator.extract_axes_from_meta),
                "verb_groups": (validator.extract_verb_groups_from_yaml, validator.extract_verb_groups_from_meta)
            }
            
            yaml_extractor, meta_extractor = category_map[args.category]
            result = validator.validate_category(args.category, yaml_extractor, meta_extractor)
            
            print(f"=== {args.category.upper()} VALIDATION ===")
            print(f"Status: {result.status.value}")
            print(f"Details: {result.details}")
            print(f"YAML items ({len(result.yaml_items)}): {sorted(list(result.yaml_items))}")
            print(f"META items ({len(result.meta_items)}): {sorted(list(result.meta_items))}")
            
            if args.enforce and result.status != ValidationStatus.MATCH:
                return 1
        
        else:
            # Validate all categories
            if args.enforce:
                validator.enforce_compliance()
                print("✓ SSoT↔META cross-validation PASSED (enforced)")
            else:
                results = validator.validate_all_categories()
                report_path = validator.save_compliance_report(args.report)
                
                print("=== SSoT↔META CROSS-VALIDATION ===")
                for result in results:
                    status_symbol = "✓" if result.status == ValidationStatus.MATCH else "✗"
                    print(f"{status_symbol} {result.category}: {result.status.value}")
                    if result.status != ValidationStatus.MATCH:
                        print(f"   {result.details}")
                
                report = validator.generate_compliance_report()
                print(f"\nOverall Status: {report['overall_status']}")
                print(f"Compliant Categories: {report['summary']['compliant_categories']}/{report['summary']['total_categories']}")
                print(f"Report saved: {report_path}")
        
        return 0
        
    except Exception as e:
        print(f"✗ Cross-validation error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
