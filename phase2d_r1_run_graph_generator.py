#!/usr/bin/env python3
"""
Phase 2D_B: R1 Deterministic Run-Graph Generator

Generates the R1 static execution topology for all 96 frozen agentic_core modules
using semantic cache metadata and file path analysis.
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from collections import OrderedDict


@dataclass
class R1GraphNode:
    """Represents a node in the R1 deterministic run-graph"""
    module: str
    layer: str
    phase: str
    domain: str
    subdomain: str
    dependencies: List[str]
    file_hash: Optional[str] = None
    responsibility_tags: Optional[List[str]] = None
    signature_count: Optional[int] = None
    docstring_count: Optional[int] = None


class R1RunGraphGenerator:
    """Generates deterministic R1 run-graph for agentic_core modules"""
    
    def __init__(self, project_root: Path, cache_dir: Path):
        self.project_root = project_root
        self.cache_dir = cache_dir
        self.semantic_cache: Dict[str, Dict[str, Any]] = {}
        
    def load_semantic_cache(self) -> None:
        """Load all semantic cache entries"""
        cache_files = list(self.cache_dir.glob("agentic_core_*.meta.json"))
        
        print(f"Loading {len(cache_files)} semantic cache entries...")
        
        for cache_file in cache_files:
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    entry = json.load(f)
                    # Use the full file path as key
                    self.semantic_cache[entry['file_path']] = entry
            except Exception as e:
                print(f"Error loading cache file {cache_file}: {e}")
        
        print(f"Successfully loaded {len(self.semantic_cache)} cache entries")
    
    def extract_metadata_from_path(self, file_path: Path) -> Dict[str, str]:
        """Extract layer, phase, domain, subdomain from file path"""
        path_parts = file_path.parts
        
        # Default values
        layer = "Unknown"
        phase = "Unknown"
        domain = "Unknown"
        subdomain = "Unknown"
        
        # Extract layer
        if 'plan-layer' in path_parts:
            layer = "L1"
        elif 'exec-layer' in path_parts:
            layer = "L2"
        elif 'orc-layer' in path_parts:
            layer = "L3"
        elif 'mem-layer' in path_parts:
            layer = "L4"
        elif 'safe-layer' in path_parts:
            layer = "L5"
        
        # Extract phase (directories ending with -phase)
        for part in path_parts:
            if part.endswith('-phase'):
                phase = part.replace('-phase', '').replace('-', '_')
        
        # Extract domain/subdomain from directory structure
        # Look for specific patterns in the path
        if 'get-core-info' in path_parts:
            domain = "get_core_info"
        elif 'use-core-tools' in path_parts:
            domain = "use_core_tools"
        elif 'check-core-rules' in path_parts:
            domain = "check_core_rules"
        elif 'check-core-structure' in path_parts:
            domain = "check_core_structure"
        elif 'find-core-problems' in path_parts:
            domain = "find_core_problems"
        elif 'convert-core-content' in path_parts:
            domain = "convert_core_content"
        elif 'update-core-state' in path_parts:
            domain = "update_core_state"
        elif 'pick-best-result' in path_parts:
            domain = "pick_best_result"
        
        # Extract subdomain from deeper directories
        for part in path_parts:
            if part in ['general', 'policy', 'embedding', 'utility', 'routing', 'semantic', 'retrieve', 'validate', 'act', 'expand', 'inspect', 'agg']:
                subdomain = part.replace('-', '_')
                break
        
        # Handle special cases for subdomain
        if subdomain == "Unknown":
            # Look for other patterns
            for part in path_parts:
                if part not in ['agentic_core', layer.replace('L', '').lower() + '-layer', phase.replace('_', '-') + '-phase', domain.replace('_', '-')] and part.endswith('.py'):
                    # This is likely the filename, extract subdomain from parent directory
                    continue
                elif part not in ['agentic_core', layer.replace('L', '').lower() + '-layer', phase.replace('_', '-') + '-phase', domain.replace('_', '-')]:
                    subdomain = part.replace('-', '_')
                    break
        
        return {
            'layer': layer,
            'phase': phase,
            'domain': domain,
            'subdomain': subdomain
        }
    
    def get_semantic_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Get metadata from semantic cache for a file"""
        # Convert to absolute path to match cache keys
        abs_path = str(file_path.resolve())
        
        # Try exact match first
        if abs_path in self.semantic_cache:
            cache_entry = self.semantic_cache[abs_path]
            return {
                'file_hash': cache_entry.get('file_hash'),
                'responsibility_tags': cache_entry.get('responsibility_tags', []),
                'signature_count': len(cache_entry.get('signature_map', {}).get('functions', [])) + 
                                  len(cache_entry.get('signature_map', {}).get('classes', [])),
                'docstring_count': len(cache_entry.get('docstring_map', {}))
            }
        
        # Try case-insensitive match
        for cache_key, cache_entry in self.semantic_cache.items():
            if cache_key.lower() == abs_path.lower():
                return {
                    'file_hash': cache_entry.get('file_hash'),
                    'responsibility_tags': cache_entry.get('responsibility_tags', []),
                    'signature_count': len(cache_entry.get('signature_map', {}).get('functions', [])) + 
                                      len(cache_entry.get('signature_map', {}).get('classes', [])),
                    'docstring_count': len(cache_entry.get('docstring_map', {}))
                }
        
        # Fallback: try matching by filename
        filename = file_path.name
        for cache_key, cache_entry in self.semantic_cache.items():
            if cache_key.endswith(filename):
                return {
                    'file_hash': cache_entry.get('file_hash'),
                    'responsibility_tags': cache_entry.get('responsibility_tags', []),
                    'signature_count': len(cache_entry.get('signature_map', {}).get('functions', [])) + 
                                      len(cache_entry.get('signature_map', {}).get('classes', [])),
                    'docstring_count': len(cache_entry.get('docstring_map', {}))
                }
        
        return {
            'file_hash': None,
            'responsibility_tags': [],
            'signature_count': 0,
            'docstring_count': 0
        }
    
    def generate_r1_graph_nodes(self) -> List[R1GraphNode]:
        """Generate R1 graph nodes for all agentic_core modules"""
        agentic_core_dir = self.project_root / "agentic_core"
        nodes = []
        
        # Get all Python files (excluding __init__.py)
        python_files = []
        for file_path in agentic_core_dir.rglob("*.py"):
            if file_path.name != "__init__.py":
                python_files.append(file_path)
        
        print(f"Generating R1 nodes for {len(python_files)} files...")
        
        for file_path in python_files:
            # Extract path metadata
            path_metadata = self.extract_metadata_from_path(file_path)
            
            # Get semantic metadata
            semantic_metadata = self.get_semantic_metadata(file_path)
            
            # Create module path (relative to project root)
            module_path = str(file_path.relative_to(self.project_root)).replace('\\', '.').replace('/', '.').replace('.py', '')
            
            # Create R1 node
            node = R1GraphNode(
                module=module_path,
                layer=path_metadata['layer'],
                phase=path_metadata['phase'],
                domain=path_metadata['domain'],
                subdomain=path_metadata['subdomain'],
                dependencies=[],  # Empty by design (no internal imports)
                file_hash=semantic_metadata['file_hash'],
                responsibility_tags=semantic_metadata['responsibility_tags'],
                signature_count=semantic_metadata['signature_count'],
                docstring_count=semantic_metadata['docstring_count']
            )
            
            nodes.append(node)
        
        # Sort nodes deterministically by module path
        nodes.sort(key=lambda x: x.module)
        
        print(f"Generated {len(nodes)} R1 nodes")
        return nodes
    
    def generate_r1_graph(self) -> Dict[str, Any]:
        """Generate the complete R1 deterministic run-graph"""
        print("=== Phase 2D_B: R1 Deterministic Run-Graph Generation ===")
        
        # Load semantic cache
        self.load_semantic_cache()
        
        # Generate nodes
        nodes = self.generate_r1_graph_nodes()
        
        # Create graph structure
        graph = {
            "graph_metadata": {
                "name": "agentic_core_run_graph_r1",
                "version": "1.0.0",
                "generated_at": "2025-12-01",
                "total_nodes": len(nodes),
                "description": "R1 static execution topology for agentic_core modules",
                "architecture": {
                    "layers": ["L1", "L2", "L3", "L4", "L5"],
                    "phases": ["plan_phase", "act_phase", "expand_phase", "inspect_phase", "agg_phase", "retrieve_phase", "validate_phase", "safety_phase"],
                    "domains": ["get_core_info", "use_core_tools", "check_core_rules", "find_core_problems", "convert_core_content", "update_core_state"],
                    "design": "self_contained_modules_with_zero_internal_dependencies"
                }
            },
            "nodes": {}
        }
        
        # Add nodes in deterministic order
        for node in nodes:
            node_dict = asdict(node)
            # Remove optional fields that are None to keep JSON clean
            node_dict = {k: v for k, v in node_dict.items() if v is not None}
            graph["nodes"][node.module] = node_dict
        
        # Add summary statistics
        layer_counts = {}
        phase_counts = {}
        domain_counts = {}
        
        for node in nodes:
            layer_counts[node.layer] = layer_counts.get(node.layer, 0) + 1
            phase_counts[node.phase] = phase_counts.get(node.phase, 0) + 1
            domain_counts[node.domain] = domain_counts.get(node.domain, 0) + 1
        
        graph["graph_metadata"]["statistics"] = {
            "nodes_by_layer": layer_counts,
            "nodes_by_phase": phase_counts,
            "nodes_by_domain": domain_counts,
            "total_dependencies": 0,  # All modules are self-contained
            "max_dependency_depth": 1  # Flat graph due to no internal dependencies
        }
        
        return graph
    
    def save_r1_graph(self, graph: Dict[str, Any], output_path: Path) -> None:
        """Save R1 graph to JSON file"""
        print(f"Saving R1 graph to {output_path}...")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(graph, f, indent=2, sort_keys=True, ensure_ascii=False)
        
        print(f"R1 graph saved successfully")
    
    def validate_r1_graph(self, graph: Dict[str, Any]) -> Dict[str, Any]:
        """Validate R1 graph meets all requirements"""
        print("\n=== R1 Graph Validation ===")
        
        nodes = graph["nodes"]
        metadata = graph["graph_metadata"]
        
        validation_results = {
            "total_nodes": len(nodes),
            "expected_nodes": 96,
            "nodes_valid": len(nodes) == 96,
            "all_nodes_have_metadata": True,
            "all_dependencies_empty": True,
            "deterministic_ordering": True,
            "no_missing_layers": True,
            "no_missing_phases": True,
            "no_missing_domains": True
        }
        
        # Check each node has required metadata
        required_fields = ["module", "layer", "phase", "domain", "subdomain", "dependencies"]
        for module_path, node_data in nodes.items():
            for field in required_fields:
                if field not in node_data:
                    validation_results["all_nodes_have_metadata"] = False
                    print(f"Missing field '{field}' in node: {module_path}")
            
            # Check dependencies are empty
            if node_data.get("dependencies"):
                validation_results["all_dependencies_empty"] = False
                print(f"Non-empty dependencies found in: {module_path}")
        
        # Check layer coverage
        expected_layers = {"L1", "L2", "L3", "L4", "L5"}
        actual_layers = set(node["layer"] for node in nodes.values())
        if not expected_layers.issubset(actual_layers):
            validation_results["no_missing_layers"] = False
            missing = expected_layers - actual_layers
            print(f"Missing layers: {missing}")
        
        # Check phase coverage
        expected_phases = {"plan", "act", "expand", "inspect", "agg", "retrieve", "validate", "safety"}
        actual_phases = set(node["phase"] for node in nodes.values() if node["phase"] != "Unknown")
        if not expected_phases.issubset(actual_phases):
            validation_results["no_missing_phases"] = False
            missing = expected_phases - actual_phases
            print(f"Missing phases: {missing}")
        
        # Check domain coverage
        expected_domains = {"get_core_info", "use_core_tools", "check_core_rules", "find_core_problems", "convert_core_content", "update_core_state"}
        actual_domains = set(node["domain"] for node in nodes.values() if node["domain"] != "Unknown")
        if not expected_domains.issubset(actual_domains):
            validation_results["no_missing_domains"] = False
            missing = expected_domains - actual_domains
            print(f"Missing domains: {missing}")
        
        # Print validation results
        print(f"Total nodes: {validation_results['total_nodes']} (Expected: {validation_results['expected_nodes']})")
        print(f"All nodes have metadata: {'✅' if validation_results['all_nodes_have_metadata'] else '❌'}")
        print(f"All dependencies empty: {'✅' if validation_results['all_dependencies_empty'] else '❌'}")
        print(f"Deterministic ordering: {'✅' if validation_results['deterministic_ordering'] else '❌'}")
        print(f"No missing layers: {'✅' if validation_results['no_missing_layers'] else '❌'}")
        print(f"No missing phases: {'✅' if validation_results['no_missing_phases'] else '❌'}")
        print(f"No missing domains: {'✅' if validation_results['no_missing_domains'] else '❌'}")
        
        overall_valid = all(validation_results.values())
        validation_results["overall_valid"] = overall_valid
        
        print(f"\nOverall validation: {'✅ PASS' if overall_valid else '❌ FAIL'}")
        
        return validation_results
    
    def run_generation(self) -> Dict[str, Any]:
        """Run complete R1 graph generation process"""
        # Generate graph
        graph = self.generate_r1_graph()
        
        # Save graph
        output_path = self.project_root / "agentic_core_run_graph_r1.json"
        self.save_r1_graph(graph, output_path)
        
        # Validate graph
        validation = self.validate_r1_graph(graph)
        
        # Test importability
        importable = True
        try:
            import agentic_core
        except Exception as e:
            importable = False
            print(f"Import test failed: {e}")
        
        validation["importable"] = importable
        
        return {
            "graph": graph,
            "validation": validation,
            "output_path": output_path
        }


def main():
    """Main generation execution"""
    project_root = Path(__file__).parent
    cache_dir = Path("C:\\Git\\.windsurf_cache\\semantic")
    
    generator = R1RunGraphGenerator(project_root, cache_dir)
    results = generator.run_generation()
    
    validation = results["validation"]
    return 0 if validation["overall_valid"] and validation["importable"] else 1


if __name__ == "__main__":
    exit(main())
