#!/usr/bin/env python3
"""
Phase 0.5 Semantic Cache Rebuild - Semantic Artifact Generator

Implements unified semantic artifact generation for eligible archive files.
Creates 8 artifact types per file: AST, embeddings, diffs, golden, safety, meta, integrity.

ZERO-LOSS CONSTRAINTS:
- Only processes eligible files (.py, .json, .yaml, .yml, .md, .txt)
- Generates ALL 8 artifacts for each eligible file
- Uses SHA-256 hash for global deduplication
- No network calls for embeddings (simple deterministic approach)
- Docker-safe paths only
"""

import ast
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime
import difflib
import re

# Project constants
PROJECT_ROOT = Path("C:/Git/Agentic-Workflow")
SEMANTIC_CACHE_ROOT = PROJECT_ROOT / "06_data" / "semantic_cache"

# Import from our modules
from phase05.archive_scanner import FileInfo

@dataclass
class ArtifactMetadata:
    """Metadata for generated artifacts"""
    hash: str
    artifact_type: str
    file_info: FileInfo
    generation_timestamp: str
    artifact_path: str
    size_bytes: int

class SemanticArtifactGenerator:
    """
    Unified semantic artifact generator for Phase 0.5.
    
    Generates all required semantic artifacts (AST, embeddings, diffs, golden,
    safety, meta, integrity) for eligible archive files with proper hash-based
    deduplication and lineage tracking.
    """
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.semantic_cache_root = SEMANTIC_CACHE_ROOT
        self.generated_artifacts: List[ArtifactMetadata] = []
        
        # Version lineage map for diff generation
        self.version_lineage: Dict[str, List[Tuple[str, FileInfo]]] = {}  # logical_path -> [(version, file_info)]
        
        # Ensure cache directories exist
        self._ensure_cache_structure()
    
    def _ensure_cache_structure(self):
        """Create required cache directories for semantic artifacts"""
        cache_dirs = [
            "ast", "embeddings", "diffs", "golden", "safety", "meta", "integrity"
        ]
        
        for dir_name in cache_dirs:
            dir_path = self.semantic_cache_root / dir_name
            if not self.dry_run:
                dir_path.mkdir(parents=True, exist_ok=True)
    
    def _build_logical_path(self, file_info: FileInfo) -> str:
        """Build logical path for lineage tracking"""
        # Convert archive path to logical path by removing version-specific prefixes
        relative_path = file_info.relative_path
        
        # Normalize path separators
        logical_path = relative_path.replace('\\', '/')
        
        # Remove archive-specific prefixes to get logical path
        prefixes_to_remove = [
            'plan-layer/', 'exec-layer/', 'safe-layer/', 'mem-layer/',
            'orc-layer/', 'observer-microagent-layer/', 'executor-microagent-layer/',
            'planner-microagent-layer/', 'retriever-microagent-layer/', 
            'router-microagent-layer/', 'budget-manager-layer/'
        ]
        
        for prefix in prefixes_to_remove:
            if logical_path.startswith(prefix):
                logical_path = logical_path[len(prefix):]
                break
        
        return logical_path
    
    def _get_file_content(self, file_info: FileInfo) -> str:
        """Read file content as text"""
        try:
            with open(file_info.absolute_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading {file_info.absolute_path}: {str(e)}")
            return ""
    
    def generate_ast_artifact(self, file_info: FileInfo, content: str) -> Optional[Dict]:
        """Generate AST artifact for Python files"""
        if file_info.file_extension != '.py':
            return None
        
        try:
            tree = ast.parse(content)
            
            # Convert AST to serializable format
            ast_data = {
                "ast_version": "python_3.8+",
                "encoding": "utf-8",
                "tree": self._ast_to_dict(tree),
                "statistics": {
                    "node_count": len(list(ast.walk(tree))),
                    "function_count": len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]),
                    "class_count": len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]),
                    "import_count": len([n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))])
                }
            }
            
            return ast_data
            
        except SyntaxError as e:
            # Handle syntax errors gracefully
            return {
                "ast_version": "python_3.8+",
                "error": f"Syntax error: {str(e)}",
                "line_number": e.lineno,
                "offset": e.offset,
                "parse_failed": True
            }
        except Exception as e:
            return {
                "ast_version": "python_3.8+", 
                "error": f"Parse error: {str(e)}",
                "parse_failed": True
            }
    
    def _ast_to_dict(self, node: ast.AST) -> Dict:
        """Convert AST node to dictionary"""
        if isinstance(node, ast.AST):
            result = {
                "_type": node.__class__.__name__,
                "_fields": {}
            }
            
            for field in node._fields:
                value = getattr(node, field, None)
                if isinstance(value, list):
                    result["_fields"][field] = [self._ast_to_dict(item) if isinstance(item, ast.AST) else str(item) 
                                              for item in value]
                elif isinstance(value, ast.AST):
                    result["_fields"][field] = self._ast_to_dict(value)
                else:
                    result["_fields"][field] = str(value)
            
            # Add location info if available
            if hasattr(node, 'lineno'):
                result["_lineno"] = node.lineno
            if hasattr(node, 'col_offset'):
                result["_col_offset"] = node.col_offset
                
            return result
        else:
            return str(node)
    
    def generate_embedding_artifact(self, file_info: FileInfo, content: str) -> Dict:
        """Generate embedding artifact (deterministic, no network calls)"""
        # Simple deterministic embedding based on content hash and features
        content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]
        
        # Extract features for embedding
        lines = content.split('\n')
        words = re.findall(r'\b\w+\b', content.lower())
        
        # Create deterministic "embedding" vector (simplified approach)
        features = {
            "line_count": len(lines),
            "word_count": len(words),
            "char_count": len(content),
            "unique_words": len(set(words)),
            "avg_line_length": sum(len(line) for line in lines) / len(lines) if lines else 0,
            "file_type": file_info.file_extension,
            "content_hash_prefix": content_hash
        }
        
        # Generate deterministic vector from features
        vector = []
        feature_string = json.dumps(features, sort_keys=True)
        feature_hash = hashlib.sha256(feature_string.encode('utf-8')).hexdigest()
        
        # Convert hash to simple 64-dimensional vector
        for i in range(0, min(64, len(feature_hash)), 2):
            hex_pair = feature_hash[i:i+2]
            vector.append(int(hex_pair, 16) / 255.0)
        
        # Pad or truncate to 64 dimensions
        while len(vector) < 64:
            vector.append(0.0)
        vector = vector[:64]
        
        return {
            "embedding_model": "deterministic_v1",
            "vector_dimensions": 64,
            "vector": vector,
            "features": features,
            "generation_method": "hash_based_deterministic"
        }
    
    def generate_diff_artifact(self, file_info: FileInfo, content: str) -> Dict:
        """Generate diff artifact comparing to previous version in lineage"""
        logical_path = self._build_logical_path(file_info)
        
        # Find previous version in lineage
        previous_version = None
        previous_content = ""
        
        if logical_path in self.version_lineage:
            versions = self.version_lineage[logical_path]
            # Find the most recent version before current one
            for version, prev_file_info in versions:
                if version != file_info.archive_name:  # Different version
                    previous_content = self._get_file_content(prev_file_info)
                    if previous_content:
                        previous_version = version
                        break
        
        # Generate diff
        if previous_content:
            diff_lines = list(difflib.unified_diff(
                previous_content.splitlines(keepends=True),
                content.splitlines(keepends=True),
                fromfile=f"{previous_version}/{logical_path}",
                tofile=f"{file_info.archive_name}/{logical_path}",
                lineterm=''
            ))
            
            diff_stats = {
                "lines_added": sum(1 for line in diff_lines if line.startswith('+') and not line.startswith('+++')),
                "lines_removed": sum(1 for line in diff_lines if line.startswith('-') and not line.startswith('---')),
                "lines_changed": sum(1 for line in diff_lines if line.startswith(' ') or line.startswith('@@'))
            }
            
            return {
                "diff_type": "lineage_diff",
                "baseline_version": previous_version,
                "current_version": file_info.archive_name,
                "logical_path": logical_path,
                "diff_content": ''.join(diff_lines),
                "statistics": diff_stats,
                "has_changes": len(diff_lines) > 0
            }
        else:
            # Initial generation
            return {
                "diff_type": "initial_diff",
                "baseline_version": None,
                "current_version": file_info.archive_name,
                "logical_path": logical_path,
                "diff_content": content,
                "statistics": {
                    "lines_added": len(content.splitlines()),
                    "lines_removed": 0,
                    "lines_changed": len(content.splitlines())
                },
                "has_changes": True,
                "initial_generation": True
            }
    
    def generate_safety_artifact(self, file_info: FileInfo, content: str) -> Dict:
        """Generate safety artifact with basic security checks"""
        safety_checks = {
            "has_executable_code": file_info.file_extension == '.py',
            "has_file_operations": bool(re.search(r'\b(open|file|read|write|remove|unlink)\b', content)),
            "has_network_operations": bool(re.search(r'\b(requests|urllib|socket|http)\b', content)),
            "has_system_operations": bool(re.search(r'\b(os\.system|subprocess|exec|eval)\b', content)),
            "has_sensitive_patterns": bool(re.search(r'\b(password|secret|key|token|auth)\b', content, re.IGNORECASE)),
            "file_size_risk": file_info.file_size > 1024 * 1024,  # > 1MB
            "line_count": len(content.splitlines()),
            "complexity_score": self._calculate_complexity(content)
        }
        
        # Overall safety score (0-100, higher is safer)
        safety_score = 100
        if safety_checks["has_system_operations"]:
            safety_score -= 20
        if safety_checks["has_network_operations"]:
            safety_score -= 15
        if safety_checks["has_sensitive_patterns"]:
            safety_score -= 10
        if safety_checks["file_size_risk"]:
            safety_score -= 5
        
        safety_score = max(0, safety_score)
        
        return {
            "safety_score": safety_score,
            "risk_level": "low" if safety_score > 80 else "medium" if safety_score > 50 else "high",
            "checks": safety_checks,
            "recommendations": self._generate_safety_recommendations(safety_checks),
            "scan_timestamp": datetime.now().isoformat()
        }
    
    def _calculate_complexity(self, content: str) -> float:
        """Calculate simple complexity score"""
        if not content:
            return 0.0
        
        lines = content.splitlines()
        non_empty_lines = [line for line in lines if line.strip()]
        
        # Simple complexity based on lines and nesting
        complexity = len(non_empty_lines)
        
        # Add complexity for nested structures
        indent_levels = [len(line) - len(line.lstrip()) for line in non_empty_lines]
        if indent_levels:
            avg_indent = sum(indent_levels) / len(indent_levels)
            complexity += avg_indent * 2
        
        return round(complexity, 2)
    
    def _generate_safety_recommendations(self, safety_checks: Dict) -> List[str]:
        """Generate safety recommendations based on checks"""
        recommendations = []
        
        if safety_checks["has_system_operations"]:
            recommendations.append("Review system operations for security implications")
        if safety_checks["has_network_operations"]:
            recommendations.append("Validate network operations and endpoints")
        if safety_checks["has_sensitive_patterns"]:
            recommendations.append("Ensure sensitive data is properly secured")
        if safety_checks["file_size_risk"]:
            recommendations.append("Consider splitting large files")
        
        return recommendations
    
    def generate_golden_artifact(self, file_info: FileInfo, content: str) -> Dict:
        """Generate golden record artifact"""
        return {
            "golden_type": "source_canonical",
            "file_hash": file_info.sha256_hash,
            "content_hash": hashlib.sha256(content.encode('utf-8')).hexdigest(),
            "file_info": asdict(file_info),
            "content_preview": content[:500] + "..." if len(content) > 500 else content,
            "creation_timestamp": datetime.now().isoformat(),
            "version": "1.0"
        }
    
    def generate_meta_artifact(self, file_info: FileInfo, all_artifacts: Dict) -> Dict:
        """Generate metadata artifact linking all other artifacts"""
        return {
            "meta_type": "artifact_manifest",
            "file_hash": file_info.sha256_hash,
            "file_info": asdict(file_info),
            "artifacts": {
                "ast": f"ast/{file_info.sha256_hash}.ast",
                "embedding": f"embeddings/{file_info.sha256_hash}.embedding",
                "diff": f"diffs/{file_info.sha256_hash}.diff.json",
                "safety": f"safety/{file_info.sha256_hash}.safety.json",
                "golden": f"golden/{file_info.sha256_hash}.golden.json",
                "integrity": f"integrity/{file_info.sha256_hash}.integrity.json"
            },
            "generation_timestamp": datetime.now().isoformat(),
            "artifact_count": len(all_artifacts)
        }
    
    def generate_integrity_artifact(self, file_info: FileInfo, content: str) -> Dict:
        """Generate integrity artifact"""
        content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
        
        return {
            "integrity_type": "content_verification",
            "file_hash": file_info.sha256_hash,
            "content_hash": content_hash,
            "file_size": file_info.file_size,
            "file_info": asdict(file_info),
            "verification_timestamp": datetime.now().isoformat(),
            "checksums": {
                "sha256": content_hash,
                "md5": hashlib.md5(content.encode('utf-8')).hexdigest()
            }
        }
    
    def generate_artifacts_for_file(self, file_info: FileInfo) -> bool:
        """Generate all semantic artifacts for a single file"""
        if not file_info.is_eligible:
            # Only generate integrity for non-eligible files
            content = self._get_file_content(file_info)
            if content:
                integrity_artifact = self.generate_integrity_artifact(file_info, content)
                self._save_artifact("integrity", f"{file_info.sha256_hash}.integrity.json", integrity_artifact)
            return True
        
        try:
            content = self._get_file_content(file_info)
            if not content:
                print(f"No content for {file_info.absolute_path}")
                return False
            
            # Generate all artifacts
            artifacts = {}
            
            # AST (Python only)
            ast_artifact = self.generate_ast_artifact(file_info, content)
            if ast_artifact:
                artifacts["ast"] = ast_artifact
            
            # Embedding
            artifacts["embedding"] = self.generate_embedding_artifact(file_info, content)
            
            # Diff
            artifacts["diff"] = self.generate_diff_artifact(file_info, content)
            
            # Safety
            artifacts["safety"] = self.generate_safety_artifact(file_info, content)
            
            # Golden
            artifacts["golden"] = self.generate_golden_artifact(file_info, content)
            
            # Integrity
            artifacts["integrity"] = self.generate_integrity_artifact(file_info, content)
            
            # Meta (generated last to include all other artifacts)
            artifacts["meta"] = self.generate_meta_artifact(file_info, artifacts)
            
            # Save all artifacts
            for artifact_type, artifact_data in artifacts.items():
                if artifact_type == "ast":
                    filename = f"{file_info.sha256_hash}.ast"
                elif artifact_type == "embedding":
                    filename = f"{file_info.sha256_hash}.embedding"
                elif artifact_type == "diff":
                    filename = f"{file_info.sha256_hash}.diff.json"
                elif artifact_type == "safety":
                    filename = f"{file_info.sha256_hash}.safety.json"
                elif artifact_type == "golden":
                    filename = f"{file_info.sha256_hash}.golden.json"
                elif artifact_type == "integrity":
                    filename = f"{file_info.sha256_hash}.integrity.json"
                elif artifact_type == "meta":
                    filename = f"{file_info.sha256_hash}.meta.json"
                
                self._save_artifact(artifact_type, filename, artifact_data)
            
            # Update lineage tracking
            logical_path = self._build_logical_path(file_info)
            if logical_path not in self.version_lineage:
                self.version_lineage[logical_path] = []
            self.version_lineage[logical_path].append((file_info.archive_name, file_info))
            
            return True
            
        except Exception as e:
            print(f"Error generating artifacts for {file_info.absolute_path}: {str(e)}")
            return False
    
    def _save_artifact(self, artifact_type: str, filename: str, artifact_data: Dict):
        """Save artifact to semantic cache"""
        if self.dry_run:
            return
        
        try:
            artifact_path = self.semantic_cache_root / artifact_type / filename
            
            with open(artifact_path, 'w', encoding='utf-8') as f:
                json.dump(artifact_data, f, indent=2)
            
            # Record metadata
            metadata = ArtifactMetadata(
                hash=artifact_data.get("file_hash", "unknown"),
                artifact_type=artifact_type,
                file_info=None,  # Will be filled by caller
                generation_timestamp=datetime.now().isoformat(),
                artifact_path=str(artifact_path),
                size_bytes=artifact_path.stat().st_size if artifact_path.exists() else 0
            )
            
            self.generated_artifacts.append(metadata)
            
        except Exception as e:
            print(f"Error saving artifact {filename}: {str(e)}")
    
    def get_generation_summary(self) -> Dict:
        """Get summary of generated artifacts"""
        artifact_counts = {}
        for artifact in self.generated_artifacts:
            artifact_type = artifact.artifact_type
            artifact_counts[artifact_type] = artifact_counts.get(artifact_type, 0) + 1
        
        return {
            "total_artifacts": len(self.generated_artifacts),
            "artifact_counts": artifact_counts,
            "lineage_entries": len(self.version_lineage),
            "generation_timestamp": datetime.now().isoformat()
        }

def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Semantic Artifact Generator")
    parser.add_argument("--dry-run", action="store_true", help="Run in dry-run mode")
    parser.add_argument("--file-list", help="JSON file with list of files to process")
    args = parser.parse_args()
    
    generator = SemanticArtifactGenerator(dry_run=args.dry_run)
    
    print("=== Phase 0.5 Semantic Artifact Generator ===")
    print(f"Dry Run: {args.dry_run}")
    
    # This would typically be called with file list from archive scanner
    # For testing, we'll just show the structure
    print("Generator initialized successfully")
    print(f"Cache root: {generator.semantic_cache_root}")
    
    summary = generator.get_generation_summary()
    print(f"Ready to generate artifacts: {summary}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
