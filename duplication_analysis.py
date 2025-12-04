#!/usr/bin/env python3
"""
Repository Content Duplication Analysis Tool

Analyzes the agentic-workflow repository for file content duplication across folders and files.
Uses hybrid approach: hash-based comparison + pattern analysis for semantic duplication.
"""

import os
import hashlib
import json
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Set
import time

# Configuration
PROJECT_ROOT = Path(r"C:/Git/Agentic-Workflow").resolve()
TARGET_ROOTS = [
    "01_agentic_core", "02_schemas", "03_runtime", "04_prompt_governance",
    "05_config", "06_data", "07_observability", "08_scripts", "09_apps", "10_tests"
]

# Protected paths to exclude from duplication reports (intentional shared resources)
PROTECTED_PATTERNS = [
    "shared_engine_ops",
    "semantic_cache", 
    "phase1_",
    "__pycache__",
    ".git",
    ".venv"
]

# File extensions to analyze
INCLUDE_EXTENSIONS = {'.py', '.yaml', '.yml', '.md', '.txt', '.json'}

# Size threshold for meaningful comparison (ignore very small files)
MIN_SIZE_BYTES = 10

class DuplicationAnalyzer:
    def __init__(self):
        self.file_hashes = {}  # hash -> list of file paths
        self.file_info = {}    # path -> {size, hash, content_sample}
        self.pattern_matches = defaultdict(list)  # pattern -> list of files
        self.duplicates_by_type = defaultdict(list)
        self.semantic_duplicates = []
        
    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file content"""
        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            print(f"Error hashing {file_path}: {e}")
            return ""
    
    def should_exclude_file(self, file_path: Path) -> bool:
        """Check if file should be excluded from analysis"""
        # Check protected patterns
        path_str = str(file_path).lower()
        for pattern in PROTECTED_PATTERNS:
            if pattern in path_str:
                return True
        
        # Check extension
        if file_path.suffix not in INCLUDE_EXTENSIONS:
            return True
        
        # Check size
        try:
            if file_path.stat().st_size < MIN_SIZE_BYTES:
                return True
        except:
            return True
        
        return False
    
    def collect_all_files(self) -> List[Path]:
        """Collect all files for analysis"""
        all_files = []
        for root in TARGET_ROOTS:
            root_path = PROJECT_ROOT / root
            if not root_path.exists():
                continue
                
            for file_path in root_path.rglob("*"):
                if file_path.is_file() and not self.should_exclude_file(file_path):
                    all_files.append(file_path)
        
        return all_files
    
    def analyze_exact_duplicates(self, file_list: List[Path]):
        """Find byte-identical duplicate files using hash comparison"""
        print("Analyzing exact duplicates...")
        
        for file_path in file_list:
            file_hash = self.calculate_file_hash(file_path)
            if not file_hash:
                continue
                
            # Store hash mapping
            if file_hash not in self.file_hashes:
                self.file_hashes[file_hash] = []
            self.file_hashes[file_hash].append(file_path)
            
            # Store file info
            try:
                size = file_path.stat().st_size
                content_sample = ""
                if file_path.suffix == '.py' and size < 1000:
                    # Sample small Python files for pattern analysis
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content_sample = f.read(200)
                    except:
                        pass
                        
                self.file_info[str(file_path)] = {
                    'size': size,
                    'hash': file_hash,
                    'content_sample': content_sample,
                    'extension': file_path.suffix
                }
            except Exception as e:
                print(f"Error getting info for {file_path}: {e}")
        
        # Find duplicates (hashes with multiple files)
        duplicate_hashes = {h: files for h, files in self.file_hashes.items() if len(files) > 1}
        
        print(f"Found {len(duplicate_hashes)} sets of exact duplicates")
        
        # Group by file type
        for hash_val, files in duplicate_hashes.items():
            file_ext = files[0].suffix
            self.duplicates_by_type[file_ext].append({
                'hash': hash_val,
                'files': [str(f.relative_to(PROJECT_ROOT)) for f in files],
                'count': len(files),
                'size': files[0].stat().st_size
            })
    
    def analyze_semantic_patterns(self, file_list: List[Path]):
        """Analyze semantic duplication patterns"""
        print("Analyzing semantic patterns...")
        
        # Pattern 1: Similar __init__.py files
        init_files = [f for f in file_list if f.name == '__init__.py']
        self.analyze_init_files(init_files)
        
        # Pattern 2: Similar cognitive engine structures
        self.analyze_cognitive_engine_patterns(file_list)
        
        # Pattern 3: YAML structural similarities
        yaml_files = [f for f in file_list if f.suffix in {'.yaml', '.yml'}]
        self.analyze_yaml_patterns(yaml_files)
    
    def analyze_init_files(self, init_files: List[Path]):
        """Analyze __init__.py files for duplication"""
        empty_inits = []
        standard_inits = []
        
        for init_file in init_files:
            try:
                with open(init_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    
                if not content or content == '""""':
                    empty_inits.append(str(init_file.relative_to(PROJECT_ROOT)))
                elif len(content) < 100:
                    standard_inits.append({
                        'file': str(init_file.relative_to(PROJECT_ROOT)),
                        'content': content
                    })
            except:
                pass
        
        if empty_inits:
            self.semantic_duplicates.append({
                'type': 'empty_init_files',
                'description': f'Empty __init__.py files',
                'files': empty_inits,
                'count': len(empty_inits),
                'recommendation': 'Consider removing empty __init__.py files or consolidating them'
            })
        
        # Group similar standard init files
        content_groups = defaultdict(list)
        for init_info in standard_inits:
            content_groups[init_info['content']].append(init_info['file'])
        
        for content, files in content_groups.items():
            if len(files) > 1:
                self.semantic_duplicates.append({
                    'type': 'similar_init_files',
                    'description': f'Similar __init__.py content',
                    'content': content,
                    'files': files,
                    'count': len(files),
                    'recommendation': 'Consider creating a shared template or utility for common init patterns'
                })
    
    def analyze_cognitive_engine_patterns(self, file_list: List[Path]):
        """Analyze cognitive engine structure duplication"""
        # Look for similar file patterns across L1-L5 and P1-P4 structures
        cognitive_patterns = defaultdict(list)
        
        for file_path in file_list:
            rel_path = str(file_path.relative_to(PROJECT_ROOT))
            
            # Extract cognitive patterns
            if any(layer in rel_path for layer in ['L1_', 'L2_', 'L3_', 'L4_', 'L5_']):
                if any(phase in rel_path for phase in ['P1_', 'P2_', 'P3_', 'P4_']):
                    # Extract the operation part (after phase)
                    parts = Path(rel_path).parts
                    if len(parts) >= 3:
                        operation = parts[-2] if len(parts) > 2 else parts[-1]
                        cognitive_patterns[operation].append(rel_path)
        
        # Find patterns that appear in multiple domains
        for pattern, files in cognitive_patterns.items():
            # Count unique domains
            domains = set()
            for file_path in files:
                for target in TARGET_ROOTS:
                    if file_path.startswith(target):
                        domains.add(target)
                        break
            
            if len(domains) > 2 and len(files) > 3:  # Appears in >2 domains with multiple files
                self.semantic_duplicates.append({
                    'type': 'cognitive_engine_pattern',
                    'pattern': pattern,
                    'files': files,
                    'domains': list(domains),
                    'count': len(files),
                    'recommendation': f'Consider consolidating pattern "{pattern}" into shared_engine_ops or creating base classes'
                })
    
    def analyze_yaml_patterns(self, yaml_files: List[Path]):
        """Analyze YAML file structural similarities"""
        yaml_structures = defaultdict(list)
        
        for yaml_file in yaml_files:
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract top-level keys as structure signature
                lines = [line.strip() for line in content.split('\n') if line.strip() and not line.strip().startswith('#')]
                top_level_keys = []
                for line in lines:
                    if line.endswith(':') and not line.startswith(' '):
                        key = line[:-1]
                        top_level_keys.append(key)
                
                signature = tuple(sorted(top_level_keys))
                yaml_structures[signature].append(str(yaml_file.relative_to(PROJECT_ROOT)))
                
            except Exception as e:
                print(f"Error analyzing YAML {yaml_file}: {e}")
        
        # Find similar structures
        for signature, files in yaml_structures.items():
            if len(files) > 1 and len(signature) > 2:  # Non-trivial structures
                self.semantic_duplicates.append({
                    'type': 'yaml_structure_similarity',
                    'structure_signature': signature,
                    'files': files,
                    'count': len(files),
                    'recommendation': 'Consider creating YAML templates or inheritance for common structures'
                })
    
    def generate_report(self) -> Dict:
        """Generate comprehensive duplication report"""
        print("Generating report...")
        
        # Calculate statistics
        total_files_analyzed = len(self.file_info)
        total_exact_duplicates = sum(len(dup['files']) - 1 for dup_list in self.duplicates_by_type.values() for dup in dup_list)
        
        report = {
            'summary': {
                'total_files_analyzed': total_files_analyzed,
                'exact_duplicate_sets': sum(len(dup_list) for dup_list in self.duplicates_by_type.values()),
                'total_exact_duplicate_files': total_exact_duplicates,
                'semantic_duplicate_patterns': len(self.semantic_duplicates),
                'analysis_timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            },
            'exact_duplicates_by_type': dict(self.duplicates_by_type),
            'semantic_duplicates': self.semantic_duplicates,
            'recommendations': []
        }
        
        # Generate high-level recommendations
        recommendations = []
        
        # Exact duplicate recommendations
        if report['summary']['exact_duplicate_sets'] > 0:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Exact Duplicates',
                'action': 'Consolidate identical files using symlinks or shared modules',
                'affected_files': total_exact_duplicates
            })
        
        # Semantic duplicate recommendations
        high_impact_semantic = [d for d in self.semantic_duplicates if d['count'] > 5]
        if high_impact_semantic:
            recommendations.append({
                'priority': 'MEDIUM',
                'category': 'Semantic Duplication',
                'action': 'Create shared utilities or base classes for repeated patterns',
                'patterns_found': len(high_impact_semantic)
            })
        
        # Empty files recommendation
        empty_inits = [d for d in self.semantic_duplicates if d['type'] == 'empty_init_files']
        if empty_inits:
            recommendations.append({
                'priority': 'LOW',
                'category': 'Empty Files',
                'action': 'Remove unnecessary empty __init__.py files',
                'count': empty_inits[0]['count'] if empty_inits else 0
            })
        
        report['recommendations'] = recommendations
        
        return report
    
    def run_analysis(self) -> Dict:
        """Run complete duplication analysis"""
        print("Starting repository duplication analysis...")
        start_time = time.time()
        
        # Collect files
        file_list = self.collect_all_files()
        print(f"Collected {len(file_list)} files for analysis")
        
        # Analyze exact duplicates
        self.analyze_exact_duplicates(file_list)
        
        # Analyze semantic patterns
        self.analyze_semantic_patterns(file_list)
        
        # Generate report
        report = self.generate_report()
        
        elapsed_time = time.time() - start_time
        print(f"Analysis completed in {elapsed_time:.2f} seconds")
        
        return report

def main():
    analyzer = DuplicationAnalyzer()
    report = analyzer.run_analysis()
    
    # Save report
    report_file = PROJECT_ROOT / "duplication_analysis_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\nReport saved to: {report_file}")
    
    # Print summary
    print("\n" + "="*60)
    print("DUPLICATION ANALYSIS SUMMARY")
    print("="*60)
    summary = report['summary']
    print(f"Total files analyzed: {summary['total_files_analyzed']}")
    print(f"Exact duplicate sets: {summary['exact_duplicate_sets']}")
    print(f"Total exact duplicate files: {summary['total_exact_duplicate_files']}")
    print(f"Semantic duplicate patterns: {summary['semantic_duplicate_patterns']}")
    
    print(f"\nRECOMMENDATIONS:")
    for rec in report['recommendations']:
        print(f"- [{rec['priority']}] {rec['category']}: {rec['action']}")
    
    return report

if __name__ == "__main__":
    main()
