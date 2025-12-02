"""
Semantic Lineage Merge for Phase 0.5 Cache Rebuild

Processes completed semantic cache entries to generate cross-version semantic diffs,
API drift analysis, and lineage chains for both Resume Engine (RG) and Outreach Engine (LIC)
archives with strict engine separation.
"""

from __future__ import annotations
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any
import logging
from collections import defaultdict

# Add schemas to path for imports
sys.path.append(str(Path(__file__).parent.parent / "schemas"))
from semantic_lineage import (
    EngineType, SemanticDiff, SemanticCacheEntry,
    ASTSignature, FileSignature
)


@dataclass
class VersionInfo:
    """Parsed version information for chronological ordering"""
    version_string: str
    version_number: float
    version_type: str  # "numeric", "semantic", "named"
    sort_key: Tuple[int, float, str]
    
    @classmethod
    def from_string(cls, version_str: str) -> VersionInfo:
        """Parse version string into comparable VersionInfo"""
        version_str = version_str.strip()
        
        # Handle numeric versions (v2, v6.0, v10.7)
        numeric_match = re.match(r'^v?(\d+)(?:\.(\d+))?$', version_str.lower())
        if numeric_match:
            major = int(numeric_match.group(1))
            minor = int(numeric_match.group(2)) if numeric_match.group(2) else 0
            version_number = float(f"{major}.{minor}")
            return cls(
                version_string=version_str,
                version_number=version_number,
                version_type="numeric",
                sort_key=(0, version_number, version_str.lower())
            )
        
        # Handle semantic versions (10_11, 10_10, etc.)
        semantic_match = re.match(r'^(\d+)_(\d+)$', version_str)
        if semantic_match:
            major = int(semantic_match.group(1))
            minor = int(semantic_match.group(2))
            version_number = float(f"{major}.{minor}")
            return cls(
                version_string=version_str,
                version_number=version_number,
                version_type="semantic",
                sort_key=(0, version_number, version_str.lower())
            )
        
        # Handle named versions (Monolithic, Microservices Model, etc.)
        # Assign arbitrary ordering based on name
        name_priority = {
            "monolithic": 1,
            "monolith": 2,
            "old resume gen python": 3,
            "old lic": 4,
            "microservices model": 5,
            "agentic-workflow-10_7_main": 6,
            "agentic-workflow-10_8_core": 7,
            "agentic-workflow-10_9": 8,
            "agentic_workflow-10_10": 9,
            "agentic-workflow-10_11": 10,
            "agentic-lic": 11,
            "agentic lic": 12,
            "deprecated in v13": 13
        }
        
        priority = name_priority.get(version_str.lower(), 999)
        return cls(
            version_string=version_str,
            version_number=float(priority),
            version_type="named",
            sort_key=(1, priority, version_str.lower())
        )


@dataclass
class LineageChain:
    """Lineage chain for a file across versions"""
    file_key: str  # Unique identifier for the file across versions
    engine: EngineType
    versions: List[Tuple[str, str]]  # List of (version, file_hash) tuples
    completeness: float  # How complete the lineage chain is
    gaps: List[str]  # Missing versions in the chain
    current_hash: str  # Hash of the latest version
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_key": self.file_key,
            "engine": self.engine.value,
            "versions": self.versions,
            "completeness": self.completeness,
            "gaps": self.gaps,
            "current_hash": self.current_hash
        }


class SemanticDiffer:
    """Generates semantic diffs between AST signatures"""
    
    @staticmethod
    def compare_ast_signatures(old_signature: ASTSignature, new_signature: ASTSignature) -> SemanticDiff:
        """Compare two AST signatures and generate semantic diff"""
        # Function analysis
        old_functions = set(old_signature.function_signatures.keys())
        new_functions = set(new_signature.function_signatures.keys())
        
        added_functions = list(new_functions - old_functions)
        removed_functions = list(old_functions - new_functions)
        modified_functions = []
        signature_changes = {}
        
        # Check for modified functions
        for func_name in old_functions.intersection(new_functions):
            old_sig = old_signature.function_signatures[func_name]
            new_sig = new_signature.function_signatures[func_name]
            
            if old_sig != new_sig:
                modified_functions.append(func_name)
                signature_changes[func_name] = (old_sig, new_sig)
        
        # Class analysis
        old_classes = set(old_signature.class_signatures.keys())
        new_classes = set(new_signature.class_signatures.keys())
        
        added_functions.extend(new_classes - old_classes)
        removed_functions.extend(old_classes - new_classes)
        
        # Import graph analysis
        old_imports = set(old_signature.import_graph.keys())
        new_imports = set(new_signature.import_graph.keys())
        
        import_changes = list(new_imports - old_imports) + list(old_imports - new_imports)
        
        # Complexity analysis
        complexity_changes = []
        for metric, old_value in old_signature.complexity_metrics.items():
            if metric in new_signature.complexity_metrics:
                new_value = new_signature.complexity_metrics[metric]
                if old_value != new_value:
                    complexity_changes.append(f"{metric}: {old_value} -> {new_value}")
        
        behavior_changes = []
        if import_changes:
            behavior_changes.append(f"Import changes: {import_changes}")
        if complexity_changes:
            behavior_changes.extend(complexity_changes)
        
        return SemanticDiff(
            added_functions=added_functions,
            removed_functions=removed_functions,
            modified_functions=modified_functions,
            signature_changes=signature_changes,
            behavior_changes=behavior_changes
        )
    
    @staticmethod
    def detect_api_drift(old_signature: ASTSignature, new_signature: ASTSignature) -> List[str]:
        """Detect API drift between versions"""
        api_drifts = []
        
        # Check for removed public functions/classes
        old_public_funcs = {name: sig for name, sig in old_signature.function_signatures.items() 
                           if not name.startswith('_')}
        new_public_funcs = {name: sig for name, sig in new_signature.function_signatures.items() 
                           if not name.startswith('_')}
        
        removed_public = set(old_public_funcs.keys()) - set(new_public_funcs.keys())
        if removed_public:
            api_drifts.append(f"Removed public APIs: {list(removed_public)}")
        
        # Check for signature changes in public functions
        for func_name in set(old_public_funcs.keys()).intersection(set(new_public_funcs.keys())):
            old_sig = old_public_funcs[func_name]
            new_sig = new_public_funcs[func_name]
            
            if old_sig != new_sig:
                api_drifts.append(f"API signature changed: {func_name} ({old_sig} -> {new_sig})")
        
        # Check import changes that might affect API
        old_imports = set(old_signature.import_graph.keys())
        new_imports = set(new_signature.import_graph.keys())
        
        removed_imports = old_imports - new_imports
        added_imports = new_imports - old_imports
        
        if removed_imports:
            api_drifts.append(f"Removed imports: {list(removed_imports)}")
        if added_imports:
            api_drifts.append(f"Added imports: {list(added_imports)}")
        
        return api_drifts


class DependencyAnalyzer:
    """Analyzes cross-version dependency graphs"""
    
    @staticmethod
    def build_dependency_graph(signatures: Dict[str, ASTSignature]) -> Dict[str, Set[str]]:
        """Build dependency graph from multiple AST signatures"""
        graph = defaultdict(set)
        
        for file_path, signature in signatures.items():
            for imports in signature.import_graph.values():
                for imported_module in imports:
                    graph[file_path].add(imported_module)
        
        return dict(graph)
    
    @staticmethod
    def detect_dependency_changes(old_graph: Dict[str, Set[str]], 
                                new_graph: Dict[str, Set[str]]) -> List[str]:
        """Detect changes in dependency graph"""
        changes = []
        
        all_files = set(old_graph.keys()).union(set(new_graph.keys()))
        
        for file_path in all_files:
            old_deps = old_graph.get(file_path, set())
            new_deps = new_graph.get(file_path, set())
            
            added_deps = new_deps - old_deps
            removed_deps = old_deps - new_deps
            
            if added_deps:
                changes.append(f"{file_path}: added dependencies {list(added_deps)}")
            if removed_deps:
                changes.append(f"{file_path}: removed dependencies {list(removed_deps)}")
        
        return changes


class LineageMergeProcessor:
    """Main processor for semantic lineage merge operations"""
    
    def __init__(self, cache_root: Path):
        self.cache_root = cache_root
        self.logger = logging.getLogger("LineageMergeProcessor")
        self.differ = SemanticDiffer()
        self.dependency_analyzer = DependencyAnalyzer()
    
    def process_all_lineage_chains(self) -> Dict[str, Any]:
        """Process lineage chains for all engines and archives"""
        self.logger.info("Starting lineage chain processing")
        
        results = {
            "resume_engine": self._process_engine_lineages(EngineType.RESUME_ENGINE),
            "outreach_engine": self._process_engine_lineages(EngineType.OUTREACH_ENGINE),
            "processing_timestamp": datetime.now().isoformat()
        }
        
        self.logger.info("Lineage chain processing completed")
        return results
    
    def _process_engine_lineages(self, engine: EngineType) -> Dict[str, Any]:
        """Process lineage chains for a specific engine"""
        self.logger.info(f"Processing {engine.value} engine lineages")
        
        engine_dir = self.cache_root / ("resume_engine" if engine == EngineType.RESUME_ENGINE else "outreach_engine")
        
        if not engine_dir.exists():
            self.logger.warning(f"Engine directory not found: {engine_dir}")
            return {"error": f"Engine directory not found: {engine_dir}"}
        
        # Get all versions and sort them chronologically
        version_dirs = [d for d in engine_dir.iterdir() if d.is_dir()]
        version_infos = [VersionInfo.from_string(d.name) for d in version_dirs]
        version_infos.sort(key=lambda v: v.sort_key)
        
        self.logger.info(f"Found {len(version_infos)} versions for {engine.value}")
        
        # Load all cache entries for each version
        version_entries = {}
        for version_info in version_infos:
            version_dir = engine_dir / version_info.version_string
            entries = self._load_version_entries(version_dir)
            version_entries[version_info.version_string] = entries
        
        # Build lineage chains
        lineage_chains = self._build_lineage_chains(version_entries, engine)
        
        # Generate semantic diffs
        semantic_diffs = self._generate_semantic_diffs(version_entries, engine)
        
        # Detect API drift
        api_drift = self._detect_api_drift(version_entries, engine)
        
        # Analyze dependency changes
        dependency_changes = self._analyze_dependency_changes(version_entries, engine)
        
        return {
            "engine": engine.value,
            "total_versions": len(version_infos),
            "versions": [v.version_string for v in version_infos],
            "lineage_chains": {chain.file_key: chain.to_dict() for chain in lineage_chains},
            "semantic_diffs": semantic_diffs,
            "api_drift": api_drift,
            "dependency_changes": dependency_changes,
            "processing_summary": {
                "total_files_processed": sum(len(entries) for entries in version_entries.values()),
                "lineage_chains_created": len(lineage_chains),
                "semantic_diffs_generated": len(semantic_diffs)
            }
        }
    
    def _load_version_entries(self, version_dir: Path) -> Dict[str, SemanticCacheEntry]:
        """Load all semantic cache entries for a version"""
        entries = {}
        
        # Look for AST files (main cache entry files)
        ast_files = list(version_dir.glob("*.ast"))
        
        for ast_file in ast_files:
            try:
                # Load AST signature
                with open(ast_file, 'r', encoding='utf-8') as f:
                    ast_data = json.load(f)
                
                # Load file signature metadata
                meta_file = ast_file.with_suffix(".ast.meta.json")
                if not meta_file.exists():
                    self.logger.warning(f"Metadata file missing: {meta_file}")
                    continue
                
                with open(meta_file, 'r', encoding='utf-8') as f:
                    file_sig_data = json.load(f)
                
                # Load other artifacts
                embedding_file = ast_file.with_suffix(".embedding")
                embedding_data = {}
                if embedding_file.exists():
                    with open(embedding_file, 'r', encoding='utf-8') as f:
                        embedding_data = json.load(f)
                
                # Create cache entry (simplified version)
                file_signature = FileSignature(
                    file_path=Path(file_sig_data["file_path"]),
                    file_hash=file_sig_data["file_hash"],
                    size_bytes=file_sig_data["size_bytes"],
                    last_modified=datetime.fromisoformat(file_sig_data["last_modified"]),
                    engine=EngineType(file_sig_data["engine"]),
                    archive_version=file_sig_data["archive_version"],
                    file_extension=file_sig_data["file_extension"]
                )
                
                # Note: This is a simplified reconstruction
                # In practice, you'd reconstruct the full SemanticCacheEntry
                entries[file_sig_data["file_hash"]] = {
                    "file_signature": file_signature,
                    "ast_data": ast_data,
                    "embedding_data": embedding_data
                }
                
            except Exception as e:
                self.logger.error(f"Failed to load cache entry from {ast_file}: {e}")
        
        return entries
    
    def _build_lineage_chains(self, version_entries: Dict[str, Dict[str, Any]], engine: EngineType) -> List[LineageChain]:
        """Build lineage chains across versions"""
        # Group files by their relative path within archives
        file_groups = defaultdict(list)
        
        for version, entries in version_entries.items():
            for file_hash, entry_data in entries.items():
                file_path = entry_data["file_signature"].file_path
                # Create a file key based on relative path
                relative_path = file_path.name  # Simplified - use full relative path in practice
                file_groups[relative_path].append((version, file_hash, entry_data))
        
        lineage_chains = []
        
        for file_key, version_data in file_groups.items():
            # Sort by version chronology
            version_data.sort(key=lambda x: VersionInfo.from_string(x[0]).sort_key)
            
            versions = [(version, file_hash) for version, file_hash, _ in version_data]
            current_hash = versions[-1][1] if versions else ""
            
            # Check for gaps in lineage
            all_versions = set(version_entries.keys())
            present_versions = {version for version, _, _ in version_data}
            gaps = list(all_versions - present_versions)
            
            completeness = len(present_versions) / len(all_versions) if all_versions else 0.0
            
            lineage_chain = LineageChain(
                file_key=file_key,
                engine=engine,
                versions=versions,
                completeness=completeness,
                gaps=gaps,
                current_hash=current_hash
            )
            
            lineage_chains.append(lineage_chain)
        
        return lineage_chains
    
    def _generate_semantic_diffs(self, version_entries: Dict[str, Dict[str, Any]], engine: EngineType) -> Dict[str, Any]:
        """Generate semantic diffs between consecutive versions"""
        versions = sorted(version_entries.keys(), key=lambda v: VersionInfo.from_string(v).sort_key)
        
        diffs = {}
        
        for i in range(len(versions) - 1):
            old_version = versions[i]
            new_version = versions[i + 1]
            
            old_entries = version_entries[old_version]
            new_entries = version_entries[new_version]
            
            version_diffs = self._compare_versions(old_entries, new_entries, old_version, new_version)
            diffs[f"{old_version}_to_{new_version}"] = version_diffs
        
        return diffs
    
    def _compare_versions(self, old_entries: Dict[str, Any], new_entries: Dict[str, Any],
                         old_version: str, new_version: str) -> Dict[str, Any]:
        """Compare two versions and generate diffs"""
        comparison = {
            "old_version": old_version,
            "new_version": new_version,
            "file_diffs": {},
            "summary": {
                "files_added": 0,
                "files_removed": 0,
                "files_modified": 0
            }
        }
        
        old_files = set(old_entries.keys())
        new_files = set(new_entries.keys())
        
        # Added files
        added_files = new_files - old_files
        comparison["summary"]["files_added"] = len(added_files)
        
        # Removed files
        removed_files = old_files - new_files
        comparison["summary"]["files_removed"] = len(removed_files)
        
        # Modified files
        common_files = old_files.intersection(new_files)
        for file_hash in common_files:
            old_entry = old_entries[file_hash]
            new_entry = new_entries[file_hash]
            
            # Compare AST data (simplified comparison)
            old_ast = old_entry["ast_data"]
            new_ast = new_entry["ast_data"]
            
            if old_ast != new_ast:
                comparison["file_diffs"][file_hash] = {
                    "change_type": "modified",
                    "old_function_count": len(old_ast.get("function_signatures", {})),
                    "new_function_count": len(new_ast.get("function_signatures", {})),
                    "old_class_count": len(old_ast.get("class_signatures", {})),
                    "new_class_count": len(new_ast.get("class_signatures", {}))
                }
                comparison["summary"]["files_modified"] += 1
        
        return comparison
    
    def _detect_api_drift(self, version_entries: Dict[str, Dict[str, Any]], engine: EngineType) -> List[str]:
        """Detect API drift across all versions"""
        versions = sorted(version_entries.keys(), key=lambda v: VersionInfo.from_string(v).sort_key)
        
        api_drifts = []
        
        for i in range(len(versions) - 1):
            old_version = versions[i]
            new_version = versions[i + 1]
            
            old_entries = version_entries[old_version]
            new_entries = version_entries[new_version]
            
            # Analyze API changes between consecutive versions
            version_drifts = self._analyze_version_api_drift(old_entries, new_entries, old_version, new_version)
            api_drifts.extend(version_drifts)
        
        return api_drifts
    
    def _analyze_version_api_drift(self, old_entries: Dict[str, Any], new_entries: Dict[str, Any],
                                  old_version: str, new_version: str) -> List[str]:
        """Analyze API drift between two specific versions"""
        drifts = []
        
        # Collect all public functions/classes from both versions
        old_public_apis = set()
        new_public_apis = set()
        
        for entry_data in old_entries.values():
            ast_data = entry_data["ast_data"]
            for func_name in ast_data.get("function_signatures", {}).keys():
                if not func_name.startswith('_'):
                    old_public_apis.add(func_name)
            for class_name in ast_data.get("class_signatures", {}).keys():
                if not class_name.startswith('_'):
                    old_public_apis.add(class_name)
        
        for entry_data in new_entries.values():
            ast_data = entry_data["ast_data"]
            for func_name in ast_data.get("function_signatures", {}).keys():
                if not func_name.startswith('_'):
                    new_public_apis.add(func_name)
            for class_name in ast_data.get("class_signatures", {}).keys():
                if not class_name.startswith('_'):
                    new_public_apis.add(class_name)
        
        # Detect API changes
        removed_apis = old_public_apis - new_public_apis
        added_apis = new_public_apis - old_public_apis
        
        if removed_apis:
            drifts.append(f"{old_version}->{new_version}: Removed public APIs: {list(removed_apis)}")
        if added_apis:
            drifts.append(f"{old_version}->{new_version}: Added public APIs: {list(added_apis)}")
        
        return drifts
    
    def _analyze_dependency_changes(self, version_entries: Dict[str, Dict[str, Any]], engine: EngineType) -> List[str]:
        """Analyze dependency changes across versions"""
        versions = sorted(version_entries.keys(), key=lambda v: VersionInfo.from_string(v).sort_key)
        
        dependency_changes = []
        
        for i in range(len(versions) - 1):
            old_version = versions[i]
            new_version = versions[i + 1]
            
            old_entries = version_entries[old_version]
            new_entries = version_entries[new_version]
            
            # Build dependency graphs for both versions
            old_graph = self._build_version_dependency_graph(old_entries)
            new_graph = self._build_version_dependency_graph(new_entries)
            
            # Detect changes
            version_changes = self.dependency_analyzer.detect_dependency_changes(old_graph, new_graph)
            
            if version_changes:
                dependency_changes.append(f"{old_version}->{new_version}:")
                dependency_changes.extend([f"  {change}" for change in version_changes])
        
        return dependency_changes
    
    def _build_version_dependency_graph(self, entries: Dict[str, Any]) -> Dict[str, Set[str]]:
        """Build dependency graph for a version's entries"""
        graph = defaultdict(set)
        
        for entry_data in entries.values():
            ast_data = entry_data["ast_data"]
            import_graph = ast_data.get("import_graph", {})
            
            for imports in import_graph.values():
                for imported_module in imports:
                    # Simplified - in practice, you'd track file-to-file dependencies
                    graph["all_files"].add(imported_module)
        
        return dict(graph)
    
    def save_lineage_results(self, results: Dict[str, Any]) -> Path:
        """Save lineage merge results to disk"""
        output_dir = self.cache_root / "lineage_results"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"lineage_merge_results_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str)
        
        self.logger.info(f"Lineage merge results saved to: {output_file}")
        return output_file


def main():
    """Main entry point for lineage merge processing"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    cache_root = Path("data/semantic_cache")
    
    if not cache_root.exists():
        print(f"Error: Semantic cache directory not found: {cache_root}")
        sys.exit(1)
    
    processor = LineageMergeProcessor(cache_root)
    
    try:
        results = processor.process_all_lineage_chains()
        output_file = processor.save_lineage_results(results)
        
        print("Lineage merge processing completed successfully")
        print(f"Results saved to: {output_file}")
        
        # Print summary
        for engine, engine_results in results.items():
            if engine == "processing_timestamp":
                continue
            
            if "error" in engine_results:
                print(f"{engine}: {engine_results['error']}")
            else:
                summary = engine_results["processing_summary"]
                print(f"{engine}: {summary['total_files_processed']} files, "
                      f"{summary['lineage_chains_created']} lineage chains, "
                      f"{summary['semantic_diffs_generated']} diffs")
        
    except Exception as e:
        logging.error(f"Lineage merge processing failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
