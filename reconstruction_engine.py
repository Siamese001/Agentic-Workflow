#!/usr/bin/env python3
"""
Agentic-Workflow Reconstruction Engine
Phase 1: Parse YAML, build target map, index sources
Phase 2: Semantic matching algorithm
Phase 3: File placement and import fixing
Phase 4: Cleanup and validation
"""

import yaml
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Set, Optional
from dataclasses import dataclass, asdict
import hashlib
from collections import defaultdict

@dataclass
class FileInfo:
    """Represents a file in the target structure"""
    yaml_path: str  # Full path in YAML structure
    l4_layer: str   # Layer name (e.g., "planner-microagent-layer")
    l5_phase: str   # Phase name (e.g., "expand-phase-group")
    l6_ops: str     # Operations name (e.g., "vectorization-ops")
    l7_file: str    # Leaf filename (e.g., "goal_definitions.py")
    tokens: List[str]  # Tokenized components
    is_synthetic: bool  # True if L7 name doesn't exist literally
    
@dataclass
class SourceFile:
    """Represents a source file from archives or GitHub"""
    path: str
    content: str
    tokens: List[str]
    source_type: str  # "resume_archive", "reachout_archive", "github_main"
    commit_hash: Optional[str] = None

@dataclass
class GitHubFile:
    """Represents a file from GitHub history"""
    path: str
    commit_hash: str
    tokens: List[str]

class ReconstructionEngine:
    def __init__(self):
        self.yaml_structure = {}
        self.target_files: Dict[str, FileInfo] = {}
        self.source_files: List[SourceFile] = []
        self.github_files: List[GitHubFile] = []
        self.matches: Dict[str, SourceFile] = {}
        
        # Archive paths
        self.resume_archive_path = r"C:\Users\amita\Documents\Work\AI Job Search\AI\ML\DL\GenAI\LLM 101\LLM Pipelines\Resume Gen\Git\Resume Engine Archive"
        self.reachout_archive_path = r"C:\Users\amita\Documents\Work\AI Job Search\AI\ML\DL\GenAI\LLM 101\LLM Pipelines\Resume Gen\Git\Reachout Engine Archive"
        self.agentic_workflow_path = Path.cwd()
        
    def load_yaml_structure(self, yaml_path: str) -> bool:
        """Load and parse the unified_structure_subatomic.yaml file"""
        try:
            with open(yaml_path, 'r', encoding='utf-8') as f:
                self.yaml_structure = yaml.safe_load(f)
            print(f"✅ Loaded YAML structure from {yaml_path}")
            return True
        except Exception as e:
            print(f"❌ Failed to load YAML: {e}")
            return False
    
    def tokenize_path(self, path: str) -> List[str]:
        """Extract meaningful tokens from a file path"""
        # Remove file extensions, split on common delimiters
        clean_path = re.sub(r'\.(py|yaml|json)$', '', path.lower())
        tokens = re.split(r'[-_\/\\]', clean_path)
        
        # Filter out common stop words and normalize
        stop_words = {'ops', 'group', 'phase', 'layer', 'microagent', 'general', 'operations', 'utility', 'functions', 'helper', 'methods'}
        meaningful_tokens = [t for t in tokens if t and t not in stop_words and len(t) > 2]
        
        return meaningful_tokens
    
    def build_target_file_map(self, structure: dict, current_path: List[str] = [], l4: str = "", l5: str = "", l6: str = ""):
        """Recursively build map of all target files from YAML structure"""
        for key, value in structure.items():
            new_path = current_path + [key]
            
            if isinstance(value, dict):
                # Check if we're at L4/L5/L6 levels
                if key.endswith('-layer'):
                    l4 = key
                elif key.endswith('-group'):
                    l5 = key
                elif key.endswith('-ops'):
                    l6 = key
                    
                self.build_target_file_map(value, new_path, l4, l5, l6)
            elif value is None or isinstance(value, str):
                # This is a leaf file (L7)
                yaml_path = '/'.join(new_path)
                
                # Handle special case where value contains comments
                if isinstance(value, str) and '#' in value:
                    actual_filename = value.split('#')[0].strip()
                    # Clean up quotes and extra spaces
                    actual_filename = actual_filename.strip().strip("'\"")
                else:
                    actual_filename = key
                
                # Extract tokens from all levels
                all_tokens = []
                if l4: all_tokens.extend(self.tokenize_path(l4))
                if l5: all_tokens.extend(self.tokenize_path(l5))
                if l6: all_tokens.extend(self.tokenize_path(l6))
                all_tokens.extend(self.tokenize_path(actual_filename))
                
                file_info = FileInfo(
                    yaml_path=yaml_path,
                    l4_layer=l4,
                    l5_phase=l5,
                    l6_ops=l6,
                    l7_file=actual_filename,
                    tokens=list(set(all_tokens)),  # Remove duplicates
                    is_synthetic=True  # All L7 names are synthetic in this structure
                )
                
                self.target_files[yaml_path] = file_info
    
    def scan_archive_directory(self, archive_path: str, source_type: str) -> List[SourceFile]:
        """Recursively scan an archive directory and index all files"""
        source_files = []
        archive_root = Path(archive_path)
        
        if not archive_root.exists():
            print(f"⚠️ Archive path does not exist: {archive_path}")
            return source_files
            
        print(f"📁 Scanning {source_type}: {archive_path}")
        
        for file_path in archive_root.rglob('*'):
            if file_path.is_file() and file_path.suffix in {'.py', '.yaml', '.json'}:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    relative_path = str(file_path.relative_to(archive_root))
                    tokens = self.tokenize_path(relative_path)
                    
                    source_file = SourceFile(
                        path=relative_path,
                        content=content,
                        tokens=tokens,
                        source_type=source_type
                    )
                    
                    source_files.append(source_file)
                    
                except Exception as e:
                    print(f"⚠️ Failed to read {file_path}: {e}")
        
        print(f"✅ Found {len(source_files)} files in {source_type}")
        return source_files
    
    def scan_github_history(self) -> List[GitHubFile]:
        """Scan GitHub main branch history for all files"""
        github_files = []
        
        print("🔍 Scanning GitHub main branch history...")
        
        try:
            # Get all commits on main branch with file lists
            cmd = ['git', 'log', 'main', '--name-only', '--pretty=format:%H']
            print(f"🔍 Running command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.agentic_workflow_path)
            
            if result.returncode != 0:
                print(f"❌ Git command failed: {result.stderr}")
                # Try alternative approach if main branch doesn't exist
                cmd_alt = ['git', 'log', '--name-only', '--pretty=format:%H']
                print(f"🔄 Trying alternative command: {' '.join(cmd_alt)}")
                result = subprocess.run(cmd_alt, capture_output=True, text=True, cwd=self.agentic_workflow_path)
                if result.returncode != 0:
                    print(f"❌ Alternative git command also failed: {result.stderr}")
                    return github_files
            
            lines = result.stdout.strip().split('\n')
            print(f"📊 Git output has {len(lines)} lines")
            current_commit = None
            
            for line in lines:
                line = line.strip()
                if line and len(line) == 40:  # Commit hash
                    current_commit = line
                elif line and current_commit and line.endswith(('.py', '.yaml', '.json')):
                    # This is a file path in the current commit
                    github_file = GitHubFile(
                        path=line,
                        commit_hash=current_commit,
                        tokens=self.tokenize_path(line)
                    )
                    github_files.append(github_file)
            
            print(f"✅ Found {len(github_files)} historical files in GitHub")
            
        except Exception as e:
            print(f"❌ Failed to scan GitHub history: {e}")
        
        return github_files
    
    def get_file_content_from_commit(self, commit_hash: str, file_path: str) -> Optional[str]:
        """Retrieve file content from a specific commit"""
        try:
            cmd = ['git', 'show', f'{commit_hash}:{file_path}']
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.agentic_workflow_path)
            
            if result.returncode == 0:
                return result.stdout
            else:
                return None
                
        except Exception as e:
            print(f"⚠️ Failed to get content for {file_path} at {commit_hash}: {e}")
            return None
    
    def compute_semantic_similarity(self, target_tokens: List[str], source_tokens: List[str]) -> float:
        """Compute semantic similarity score between target and source tokens"""
        if not target_tokens or not source_tokens:
            return 0.0
            
        # Token overlap score
        target_set = set(target_tokens)
        source_set = set(source_tokens)
        overlap = len(target_set.intersection(source_set))
        
        # Jaccard similarity
        union = len(target_set.union(source_set))
        jaccard = overlap / union if union > 0 else 0.0
        
        # Domain-specific weighting
        domain_keywords = {
            'resume': ['resume', 'cv', 'profile', 'experience', 'skills'],
            'outreach': ['outreach', 'email', 'message', 'contact', 'linkedin'],
            'vector': ['vector', 'embedding', 'normalize', 'similarity'],
            'validation': ['validate', 'validation', 'check', 'schema'],
            'routing': ['route', 'router', 'direct', 'dispatch'],
            'safety': ['safety', 'guard', 'block', 'filter', 'policy']
        }
        
        # Bonus for domain alignment
        domain_bonus = 0.0
        for domain, keywords in domain_keywords.items():
            target_domain = len(set(target_tokens).intersection(keywords)) > 0
            source_domain = len(set(source_tokens).intersection(keywords)) > 0
            if target_domain and source_domain:
                domain_bonus += 0.1
        
        return jaccard + domain_bonus
    
    def find_best_match(self, target_file: FileInfo) -> Optional[SourceFile]:
        """Find the best matching source file for a target file"""
        best_score = 0.0
        best_match = None
        
        # First try archive files
        for source_file in self.source_files:
            score = self.compute_semantic_similarity(target_file.tokens, source_file.tokens)
            
            # Bonus for exact filename matches
            if target_file.l7_file.lower() in source_file.path.lower():
                score += 0.2
                
            # Bonus for file type matches
            target_ext = os.path.splitext(target_file.l7_file)[1]
            source_ext = os.path.splitext(source_file.path)[1]
            if target_ext == source_ext:
                score += 0.1
            
            if score > best_score:
                best_score = score
                best_match = source_file
        
        # If no good archive match, try GitHub history
        if best_score < 0.4:
            for github_file in self.github_files:
                score = self.compute_semantic_similarity(target_file.tokens, github_file.tokens)
                
                # Bonus for exact filename matches
                if target_file.l7_file.lower() in github_file.path.lower():
                    score += 0.2
                    
                # Bonus for file type matches
                target_ext = os.path.splitext(target_file.l7_file)[1]
                source_ext = os.path.splitext(github_file.path)[1]
                if target_ext == source_ext:
                    score += 0.1
                
                if score > best_score:
                    # Get actual content from GitHub
                    content = self.get_file_content_from_commit(github_file.commit_hash, github_file.path)
                    if content:
                        source_file = SourceFile(
                            path=github_file.path,
                            content=content,
                            tokens=github_file.tokens,
                            source_type="github_main",
                            commit_hash=github_file.commit_hash
                        )
                        best_score = score
                        best_match = source_file
        
        # Only return matches with reasonable confidence
        if best_score > 0.3:  # Threshold can be adjusted
            return best_match
        return None
    
    def run_phase1(self):
        """Execute Phase 1: Parse YAML and index sources"""
        print("🚀 Starting Phase 1: YAML Parsing and Source Indexing")
        
        # Load YAML structure
        yaml_path = r"c:\Users\amita\Documents\Work\AI Job Search\AI\ML\DL\GenAI\LLM 101\LLM Pipelines\Resume Gen\Git\Agentic Folder Structure\unified_structure_subatomic.yaml"
        if not self.load_yaml_structure(yaml_path):
            return False
        
        # Build target file map
        self.build_target_file_map(self.yaml_structure)
        print(f"📋 Built target map with {len(self.target_files)} files")
        
        # Scan archives
        resume_files = self.scan_archive_directory(self.resume_archive_path, "resume_archive")
        reachout_files = self.scan_archive_directory(self.reachout_archive_path, "reachout_archive")
        
        self.source_files.extend(resume_files)
        self.source_files.extend(reachout_files)
        
        # Scan GitHub history
        self.github_files = self.scan_github_history()
        
        print(f"📚 Total source files indexed: {len(self.source_files)} (archives) + {len(self.github_files)} (GitHub history)")
        
        # Save target map for inspection
        target_map_path = self.agentic_workflow_path / "target_file_map.json"
        with open(target_map_path, 'w') as f:
            serializable_map = {k: asdict(v) for k, v in self.target_files.items()}
            json.dump(serializable_map, f, indent=2)
        
        print(f"💾 Saved target file map to {target_map_path}")
        return True
    
    def run_phase2(self):
        """Execute Phase 2: Semantic matching"""
        print("\n🚀 Starting Phase 2: Semantic Matching")
        
        matched_count = 0
        unmatched_files = []
        
        for yaml_path, target_file in self.target_files.items():
            best_match = self.find_best_match(target_file)
            if best_match:
                self.matches[yaml_path] = best_match
                matched_count += 1
                print(f"✅ Matched {target_file.l7_file} -> {best_match.path} ({best_match.source_type})")
            else:
                unmatched_files.append(yaml_path)
                print(f"❌ No match found for {target_file.l7_file}")
        
        print(f"\n📊 Matching Results:")
        print(f"   Matched: {matched_count}/{len(self.target_files)} ({matched_count/len(self.target_files)*100:.1f}%)")
        print(f"   Unmatched: {len(unmatched_files)}")
        
        # Save matching results
        matches_path = self.agentic_workflow_path / "matching_results.json"
        with open(matches_path, 'w') as f:
            serializable_matches = {
                k: {
                    'source_path': v.path,
                    'source_type': v.source_type,
                    'tokens': v.tokens
                } for k, v in self.matches.items()
            }
            json.dump(serializable_matches, f, indent=2)
        
        # Save unmatched files for GitHub search
        with open(self.agentic_workflow_path / "unmatched_files.json", 'w') as f:
            json.dump(unmatched_files, f, indent=2)
        
        return len(unmatched_files) == 0
    
    def sanitize_path_component(self, component: str) -> str:
        """Sanitize a single path component for Windows compatibility"""
        if not component:
            return ""
            
        # Sanitize component for Windows compatibility
        sanitized = component.replace('*', 'star').replace('<', 'lt').replace('>', 'gt')
        sanitized = sanitized.replace('?', 'question').replace(':', 'colon').replace('|', 'pipe')
        sanitized = sanitized.replace('"', 'quote').replace('\\', 'backslash')
        
        # Handle special case for problematic components
        if 'data_meta' in sanitized or 'artifacts' in sanitized:
            sanitized = 'data_meta_artifacts'
        
        # Remove any remaining invalid characters
        import re
        sanitized = re.sub(r'[^\w\-_]', '_', sanitized)
        sanitized = re.sub(r'_+', '_', sanitized).strip('_')
        
        return sanitized
    
    def sanitize_directory_path(self, dir_path: str) -> str:
        """Sanitize an entire directory path"""
        if not dir_path:
            return ""
            
        dir_components = dir_path.split('/')
        sanitized_components = []
        
        for component in dir_components:
            sanitized = self.sanitize_path_component(component)
            if sanitized:
                sanitized_components.append(sanitized)
        
        return '/'.join(sanitized_components)
    
    def create_directory_structure(self):
        """Create the exact directory structure from YAML"""
        print("\n🏗️ Creating directory structure from YAML...")
        
        directories_created = 0
        
        for yaml_path, file_info in self.target_files.items():
            # Extract directory path from full yaml_path
            dir_path = os.path.dirname(yaml_path)
            
            # Use shared sanitization method
            sanitized_dir_path = self.sanitize_directory_path(dir_path)
            full_dir_path = self.agentic_workflow_path / sanitized_dir_path
            
            if not full_dir_path.exists():
                try:
                    full_dir_path.mkdir(parents=True, exist_ok=True)
                    directories_created += 1
                    print(f"📁 Created: {sanitized_dir_path}")
                except Exception as e:
                    print(f"❌ Failed to create {sanitized_dir_path}: {e}")
        
        print(f"✅ Created {directories_created} directories")
        return True
    
    def copy_matched_files(self):
        """Copy matched source files to their exact YAML paths"""
        print("\n📋 Copying matched files to target structure...")
        
        files_copied = 0
        failed_copies = []
        
        for yaml_path, source_file in self.matches.items():
            try:
                # Clean up the target filename from YAML
                target_filename = self.target_files[yaml_path].l7_file
                
                # Sanitize filename for Windows compatibility
                target_filename = target_filename.replace('*', 'star').replace('<', 'lt').replace('>', 'gt')
                target_filename = target_filename.replace('?', 'question').replace(':', 'colon').replace('|', 'pipe')
                target_filename = target_filename.replace('"', 'quote').replace('/', 'slash').replace('\\', 'backslash')
                
                # Handle special case for problematic filenames (after sanitization)
                if 'data_meta' in target_filename or 'artifacts' in target_filename:
                    target_filename = 'data_meta_artifacts.json'
                
                # Remove any remaining invalid characters and spaces
                import re
                target_filename = re.sub(r'[^\w\-_\.]', '_', target_filename)
                # Clean up multiple underscores and trailing underscores
                target_filename = re.sub(r'_+', '_', target_filename).strip('_')
                
                # Ensure filename is not empty
                if not target_filename or target_filename == '_':
                    target_filename = 'placeholder_file.py'
                
                # Create full target path using shared sanitization
                dir_path = os.path.dirname(yaml_path)
                sanitized_dir_path = self.sanitize_directory_path(dir_path)
                target_dir = self.agentic_workflow_path / sanitized_dir_path
                target_path = target_dir / target_filename
                
                # Ensure directory exists
                target_dir.mkdir(parents=True, exist_ok=True)
                
                # Write the file content with proper encoding
                with open(target_path, 'w', encoding='utf-8', errors='ignore') as f:
                    f.write(source_file.content)
                
                files_copied += 1
                print(f"✅ Copied: {source_file.path} -> {yaml_path}")
                
            except Exception as e:
                failed_copies.append((yaml_path, str(e)))
                print(f"❌ Failed to copy {yaml_path}: {e}")
        
        print(f"\n📊 File Copy Results:")
        print(f"   Successfully copied: {files_copied}")
        print(f"   Failed copies: {len(failed_copies)}")
        
        if failed_copies:
            print("\n❌ Failed copies:")
            for path, error in failed_copies[:10]:  # Show first 10
                print(f"   {path}: {error}")
        
        return len(failed_copies) == 0
    
    def improve_matching_for_remaining(self):
        """Try to find matches for remaining unmatched files with lower threshold"""
        print("\n🔍 Attempting to improve matching for remaining files...")
        
        unmatched_files = [path for path in self.target_files.keys() if path not in self.matches]
        additional_matches = 0
        
        for yaml_path in unmatched_files:
            target_file = self.target_files[yaml_path]
            
            # Try with lower threshold and different scoring
            best_score = 0.0
            best_match = None
            
            # Check archives with lower threshold
            for source_file in self.source_files:
                score = self.compute_semantic_similarity(target_file.tokens, source_file.tokens)
                
                # More generous filename matching
                if any(token in source_file.path.lower() for token in target_file.tokens if len(token) > 3):
                    score += 0.15
                
                # File type bonus
                target_ext = os.path.splitext(target_file.l7_file)[1]
                source_ext = os.path.splitext(source_file.path)[1]
                if target_ext == source_ext:
                    score += 0.1
                
                if score > best_score and score > 0.2:  # Lower threshold
                    best_score = score
                    best_match = source_file
            
            # Check GitHub with lower threshold
            if best_score < 0.3:
                for github_file in self.github_files:
                    score = self.compute_semantic_similarity(target_file.tokens, github_file.tokens)
                    
                    # More generous filename matching
                    if any(token in github_file.path.lower() for token in target_file.tokens if len(token) > 3):
                        score += 0.15
                    
                    if score > best_score and score > 0.2:  # Lower threshold
                        content = self.get_file_content_from_commit(github_file.commit_hash, github_file.path)
                        if content:
                            source_file = SourceFile(
                                path=github_file.path,
                                content=content,
                                tokens=github_file.tokens,
                                source_type="github_main",
                                commit_hash=github_file.commit_hash
                            )
                            best_score = score
                            best_match = source_file
            
            if best_match:
                self.matches[yaml_path] = best_match
                additional_matches += 1
                print(f"✅ Additional match: {target_file.l7_file} -> {best_match.path} ({best_match.source_type}) - score: {best_score:.2f}")
        
        print(f"\n📊 Additional matching results:")
        print(f"   Additional matches found: {additional_matches}")
        print(f"   Total matches now: {len(self.matches)}/{len(self.target_files)} ({len(self.matches)/len(self.target_files)*100:.1f}%)")
        
        return additional_matches
    
    def run_phase3(self):
        """Execute Phase 3: File placement and structure creation"""
        print("\n🚀 Starting Phase 3: Structure Creation and File Placement")
        
        # Try to improve matching first
        self.improve_matching_for_remaining()
        
        # Create directory structure
        if not self.create_directory_structure():
            return False
        
        # Copy matched files
        if not self.copy_matched_files():
            return False
        
        print("\n✅ Phase 3 completed successfully")
        return True

if __name__ == "__main__":
    engine = ReconstructionEngine()
    
    # Run Phase 1
    if engine.run_phase1():
        print("\n✅ Phase 1 completed successfully")
        
        # Run Phase 2
        phase2_result = engine.run_phase2()
        if phase2_result:
            print("\n✅ Phase 2 completed successfully")
        else:
            print("\n⚠️ Phase 2 completed with some unmatched files")
        
        # Run Phase 3 regardless of Phase 2 result (we can still place matched files)
        if engine.run_phase3():
            print("\n✅ Phase 3 completed successfully")
            print(f"\n🎉 RECONSTRUCTION COMPLETE!")
            print(f"📊 Final Results:")
            print(f"   Target files: {len(engine.target_files)}")
            print(f"   Matched files: {len(engine.matches)} ({len(engine.matches)/len(engine.target_files)*100:.1f}%)")
            print(f"   Unmatched files: {len(engine.target_files) - len(engine.matches)}")
        else:
            print("\n❌ Phase 3 failed")
    else:
        print("\n❌ Phase 1 failed")
