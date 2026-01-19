"""
SOVEREIGN DEDUPLICATOR: Identify the 5 "Extra" Agents
Analyzes the difference between 289 (old baseline) and 294 (true count)
to determine if these are functional duplicates or unique sovereign entities.
"""

import ast
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict

from agentic_core.L5_safety.validators.structure_blueprint import (
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
from agentic_core.utils.file_utils import safe_read_file, safe_write_file


class AgentDeduplicator:
    """
    Identifies duplicate agent classes and analyzes their differences.
    """
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.registry = self._load_registry()
        
    def _load_registry(self) -> List[Dict]:
        """Load agent discovery registry."""
        registry_path = self.root_dir / AGENT_DISCOVERY_JSON
        if not registry_path.exists():
            raise FileNotFoundError(f"Registry not found: {registry_path}")
        
        with open(registry_path) as f:
            return json.load(f)
    
    def find_duplicate_names(self) -> Dict[str, List[Dict]]:
        """
        Find agent classes with the same name in different files.
        
        Returns:
            Dict mapping agent names to list of locations
        """
        agents_by_name = defaultdict(list)
        
        for agent in self.registry:
            agents_by_name[agent['class_name']].append(agent)
        
        # Filter to only duplicates
        duplicates = {
            name: locations 
            for name, locations in agents_by_name.items() 
            if len(locations) > 1
        }
        
        return duplicates
    
    def find_multi_class_files(self) -> Dict[str, List[str]]:
        """
        Find files containing multiple agent classes.
        
        Returns:
            Dict mapping file paths to list of agent names
        """
        files_by_path = defaultdict(list)
        
        for agent in self.registry:
            files_by_path[agent['path']].append(agent['class_name'])
        
        # Filter to only multi-class files
        multi_files = {
            path: agents 
            for path, agents in files_by_path.items() 
            if len(agents) > 1
        }
        
        return multi_files
    
    def analyze_duplicate(self, agent_name: str, locations: List[Dict]) -> Dict:
        """
        Deep analysis of a duplicate agent to determine if it's a true duplicate.
        
        Checks:
        - Are the implementations identical?
        - Are they in different layers (L0-L5)?
        - Are they legacy vs current versions?
        - Do they have different base classes?
        """
        analysis = {
            "agent_name": agent_name,
            "count": len(locations),
            "locations": [],
            "verdict": "unknown",
            "recommendation": ""
        }
        
        for loc in locations:
            file_path = self.root_dir / loc['path']
            
            location_info = {
                "path": loc['path'],
                "line": loc.get('line_number', 0),
                "layer": self._extract_layer(loc['path']),
                "is_legacy": "_Legacy" in agent_name or "legacy" in loc['path'].lower(),
                "is_test": "test" in loc['path'].lower() or loc['path'].startswith("tests/"),
                "base_classes": []
            }
            
            # Try to extract base classes
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef) and node.name == agent_name:
                        location_info["base_classes"] = [
                            base.id if isinstance(base, ast.Name) else str(base)
                            for base in node.bases
                        ]
                        break
            except Exception:
                pass
            
            analysis["locations"].append(location_info)
        
        # Determine verdict
        analysis["verdict"], analysis["recommendation"] = self._determine_verdict(analysis)
        
        return analysis
    
    def _extract_layer(self, path: str) -> str:
        """Extract layer (L0-L5, apps_lic, apps_rg) from path."""
        if "L0_" in path:
            return "L0"
        elif "L1_" in path:
            return "L1"
        elif "L2_" in path:
            return "L2"
        elif "L3_" in path:
            return "L3"
        elif "L4_" in path:
            return "L4"
        elif "L5_" in path:
            return "L5"
        elif APPS_LIC_DIR in path:
            return APPS_LIC_DIR
        elif APPS_RG_DIR in path:
            return APPS_RG_DIR
        else:
            return "other"
    
    def _determine_verdict(self, analysis: Dict) -> Tuple[str, str]:
        """
        Determine if duplicate is legitimate or should be removed.
        
        Returns:
            (verdict, recommendation)
        """
        locations = analysis["locations"]
        
        # Check if one is a test file
        test_count = sum(1 for loc in locations if loc["is_test"])
        if test_count > 0:
            return "test_duplicate", "Test classes should not be counted as agents"
        
        # Check if one is legacy
        legacy_count = sum(1 for loc in locations if loc["is_legacy"])
        if legacy_count > 0 and legacy_count < len(locations):
            return "legacy_duplicate", "Remove legacy version, keep current implementation"
        
        # Check if in different layers
        layers = set(loc["layer"] for loc in locations)
        if len(layers) > 1:
            return "cross_layer_duplicate", "Investigate: Same agent in multiple layers (architectural issue)"
        
        # Check if base classes differ
        base_classes = [tuple(loc["base_classes"]) for loc in locations]
        if len(set(base_classes)) > 1:
            return "different_implementations", "Different base classes - may be legitimate variants"
        
        # Default: true duplicate
        return "true_duplicate", "Remove duplicate - identical implementations in multiple files"
    
    def generate_report(self) -> Dict:
        """
        Generate comprehensive deduplication report.
        """
        print("="*80)
        print("SOVEREIGN DEDUPLICATOR: Analyzing Agent Registry")
        print("="*80)
        print()
        
        # Find duplicates
        duplicates = self.find_duplicate_names()
        multi_files = self.find_multi_class_files()
        
        print(f"📊 REGISTRY STATS")
        print(f"  Total agents: {len(self.registry)}")
        print(f"  Duplicate names: {len(duplicates)}")
        print(f"  Multi-class files: {len(multi_files)}")
        print()
        
        # Analyze each duplicate
        duplicate_analyses = []
        
        if duplicates:
            print("="*80)
            print("DUPLICATE AGENT ANALYSIS")
            print("="*80)
            print()
            
            for agent_name, locations in sorted(duplicates.items()):
                analysis = self.analyze_duplicate(agent_name, locations)
                duplicate_analyses.append(analysis)
                
                print(f"🔍 {agent_name} ({len(locations)} instances)")
                print(f"   Verdict: {analysis['verdict']}")
                print(f"   Recommendation: {analysis['recommendation']}")
                
                for i, loc in enumerate(analysis['locations'], 1):
                    flags = []
                    if loc['is_legacy']:
                        flags.append("LEGACY")
                    if loc['is_test']:
                        flags.append("TEST")
                    
                    flag_str = f" [{', '.join(flags)}]" if flags else ""
                    print(f"   {i}. {loc['path']}{flag_str}")
                    print(f"      Layer: {loc['layer']}, Line: {loc['line']}")
                    if loc['base_classes']:
                        print(f"      Bases: {', '.join(loc['base_classes'])}")
                
                print()
        else:
            print("✅ No duplicate agent names found")
            print()
        
        # Multi-class file analysis
        if multi_files:
            print("="*80)
            print("MULTI-CLASS FILES (Extraction Candidates)")
            print("="*80)
            print()
            
            for path, agents in sorted(multi_files.items(), key=lambda x: len(x[1]), reverse=True):
                print(f"📁 {path} ({len(agents)} agents)")
                for agent in agents:
                    print(f"   - {agent}")
                print()
        
        # Summary
        print("="*80)
        print("DEDUPLICATION SUMMARY")
        print("="*80)
        
        verdicts = defaultdict(int)
        for analysis in duplicate_analyses:
            verdicts[analysis['verdict']] += 1
        
        if verdicts:
            print("\nDuplicate categories:")
            for verdict, count in sorted(verdicts.items()):
                print(f"  {verdict}: {count}")
        
        # Calculate potential agent count after deduplication
        removable = sum(
            len(analysis['locations']) - 1  # Keep one, remove rest
            for analysis in duplicate_analyses
            if analysis['verdict'] in ['true_duplicate', 'legacy_duplicate', 'test_duplicate']
        )
        
        print(f"\nCurrent count: {len(self.registry)} agents")
        print(f"Removable duplicates: {removable}")
        print(f"Post-deduplication count: {len(self.registry) - removable}")
        print()
        
        # The "5 extra agents" analysis
        if len(self.registry) == 294:
            print("="*80)
            print("THE '5 EXTRA AGENTS' MYSTERY (294 vs 289)")
            print("="*80)
            print()
            print("The baseline was 289, but we now detect 294 agents.")
            print(f"Difference: +{len(self.registry) - 289} agents")
            print()
            
            if removable >= 5:
                print(f"✅ Found {removable} removable duplicates (>= 5)")
                print("   The '5 extra agents' are likely duplicates that were")
                print("   previously hidden by import errors or discovery bugs.")
            else:
                print(f"⚠️  Only {removable} removable duplicates found (< 5)")
                print("   The remaining agents may be legitimate additions or")
                print("   the 289 baseline was incorrect from the start.")
            print()
        
        return {
            "total_agents": len(self.registry),
            "duplicates": len(duplicates),
            "multi_class_files": len(multi_files),
            "duplicate_analyses": duplicate_analyses,
            "removable_count": removable,
            "post_dedup_count": len(self.registry) - removable
        }


def main():
    deduplicator = AgentDeduplicator()
    report = deduplicator.generate_report()
    
    # Save report
    output_path = Path("deduplication_report.json")
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"📝 Full report saved: {output_path}")


if __name__ == "__main__":
    main()
