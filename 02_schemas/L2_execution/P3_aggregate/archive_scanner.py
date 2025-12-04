#!/usr/bin/env python3
"""
Phase 0.5 Semantic Cache Rebuild - Archive Scanner with File Hasher

Implements archive scanning functionality for historical Resume Engine (RG)
and Outreach Engine (LIC) archives with proper file type filtering, depth
limits, and SHA-256 hashing for deduplication.

ZERO-LOSS CONSTRAINTS:
- Only scans specified archive directories (never live folders)
- Max recursion depth = 7
- Eligible file types: .py, .json, .yaml, .yml, .md, .txt
- Excluded directories: __pycache__, .pytest_cache, .git, .venv, etc.
- Generates integrity records for ALL files (eligible and non-eligible)
- Docker-safe paths only
"""

import hashlib
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any, Iterator
from dataclasses import dataclass, asdict
from datetime import datetime
import json

# Project constants
PROJECT_ROOT = Path("C:/Git/Agentic-Workflow")
SEMANTIC_CACHE_ROOT = PROJECT_ROOT / "06_data" / "semantic_cache"

# Resume Engine Archive (RG) - PRUNED VERSIONS ONLY
RESUME_ENGINE_ARCHIVES = [
    "C:/Git/Resume Engine Archive/Agentic-Workflow-10_11",
    "C:/Git/Resume Engine Archive/Agentic_Workflow-10_10", 
    "C:/Git/Resume Engine Archive/Agentic-Workflow-10_9",
    "C:/Git/Resume Engine Archive/Agentic-Workflow-10_8_core",
    "C:/Git/Resume Engine Archive/Agentic-Workflow-10_7_main",
    "C:/Git/Resume Engine Archive/Microservices Model",
    "C:/Git/Resume Engine Archive/Monolith",
    "C:/Git/Resume Engine Archive/Monolithic",
    "C:/Git/Resume Engine Archive/v2",
    "C:/Git/Resume Engine Archive/v6.0"
]

# Special case: Old Resume Gen Python (specific files only)
OLD_RESUME_GEN_FILES = [
    "C:/Git/Resume Engine Archive/Old Resume Gen Python/Resume_Generation_v14_19.py",
    "C:/Git/Resume Engine Archive/Old Resume Gen Python/Resume_Generation_v11.40.py", 
    "C:/Git/Resume Engine Archive/Old Resume Gen Python/Resume_Generation_v9_82.py",
    "C:/Git/Resume Engine Archive/Old Resume Gen Python/Resume_Generation_v5_44.py"
]

# Outreach Engine Archives (LIC) - ALL VERSIONS
OUTREACH_ENGINE_ARCHIVES = [
    "C:/Git/Reachout Engine Archive/Agentic-LIC",
    "C:/Git/Reachout Engine Archive/Agentic LIC",
    "C:/Git/Reachout Engine Archive/Monolithic",
    "C:/Git/Reachout Engine Archive/Old LIC",
    "C:/Git/Reachout Engine Archive/deprecated in v13"
]

# File eligibility rules
ELIGIBLE_EXTENSIONS = {'.py', '.json', '.yaml', '.yml', '.md', '.txt'}
EXCLUDED_DIRECTORIES = {
    '__pycache__', '.pytest_cache', '.mypy_cache', '.ruff_cache',
    '.git', '.venv', '.idea', '.vscode', 'node_modules', '.DS_Store'
}

MAX_DEPTH = 7

@dataclass
class FileInfo:
    """Information about a scanned file"""
    archive_root: str
    archive_name: str  # e.g., "Agentic-Workflow-10_10"
    relative_path: str
    absolute_path: str
    file_size: int
    file_extension: str
    is_eligible: bool
    sha256_hash: str
    scan_timestamp: str

@dataclass
class ScanResult:
    """Result of scanning an archive"""
    archive_name: str
    archive_root: str
    total_files: int
    eligible_files: int
    non_eligible_files: int
    scan_duration_seconds: float
    files: List[FileInfo]

class ArchiveScanner:
    """
    Scanner for historical Resume Engine and Outreach Engine archives.
    
    Scans archives with proper depth limits, file type filtering, and
    generates SHA-256 hashes for all files to enable deduplication.
    """
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.semantic_cache_root = SEMANTIC_CACHE_ROOT
        self.scanned_files: List[FileInfo] = []
        self.hash_index: Dict[str, List[FileInfo]] = {}  # hash -> files mapping
        
        # Ensure cache directories exist
        self._ensure_cache_structure()
    
    def _ensure_cache_structure(self):
        """Create required cache directories for archive scanning"""
        cache_dirs = [
            "resume_engine", "outreach_engine", "integrity"
        ]
        
        for dir_name in cache_dirs:
            dir_path = self.semantic_cache_root / dir_name
            if not self.dry_run:
                dir_path.mkdir(parents=True, exist_ok=True)
    
    def _is_eligible_file(self, file_path: Path) -> bool:
        """Check if file is eligible for semantic processing"""
        # Check extension
        if file_path.suffix.lower() not in ELIGIBLE_EXTENSIONS:
            return False
        
        # Check if it's a binary or non-semantic file
        non_semantic_patterns = {
            '*.pyc', '*.pyo', '*.pyd', '*.db', '*.sqlite', 
            '*.log', '*.bin', '*.exe', '*.dll', '*.so', '*.dylib'
        }
        
        for pattern in non_semantic_patterns:
            if file_path.match(pattern):
                return False
        
        return True
    
    def _should_exclude_directory(self, dir_path: Path) -> bool:
        """Check if directory should be excluded from scanning"""
        return dir_path.name in EXCLUDED_DIRECTORIES
    
    def _compute_sha256(self, file_path: Path) -> str:
        """Compute SHA-256 hash of file content"""
        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                # Read file in chunks to handle large files
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            print(f"Error hashing {file_path}: {str(e)}")
            return ""
    
    def _scan_directory_recursive(self, root_path: Path, current_depth: int = 0, archive_root: Path = None) -> Iterator[FileInfo]:
        """Recursively scan directory up to MAX_DEPTH"""
        if current_depth > MAX_DEPTH:
            return
        
        # Use provided archive_root or default to root_path
        if archive_root is None:
            archive_root = root_path
        
        try:
            for item in root_path.iterdir():
                if item.is_file():
                    # Process file - calculate relative path from actual archive root
                    relative_path = item.relative_to(archive_root)
                    file_ext = item.suffix.lower()
                    is_eligible = self._is_eligible_file(item)
                    file_hash = self._compute_sha256(item)
                    
                    file_info = FileInfo(
                        archive_root=str(archive_root),
                        archive_name=archive_root.name,
                        relative_path=str(relative_path),
                        absolute_path=str(item),
                        file_size=item.stat().st_size,
                        file_extension=file_ext,
                        is_eligible=is_eligible,
                        sha256_hash=file_hash,
                        scan_timestamp=datetime.now().isoformat()
                    )
                    
                    yield file_info
                    
                elif item.is_dir():
                    # Check if should exclude
                    if self._should_exclude_directory(item):
                        continue
                    
                    # Recurse into subdirectory
                    yield from self._scan_directory_recursive(item, current_depth + 1, archive_root)
                    
        except PermissionError:
            print(f"Permission denied accessing {root_path}")
        except Exception as e:
            print(f"Error scanning {root_path}: {str(e)}")
    
    def scan_resume_engine_archives(self) -> List[ScanResult]:
        """Scan all Resume Engine archives"""
        results = []
        
        print("Scanning Resume Engine Archives...")
        
        for archive_root in RESUME_ENGINE_ARCHIVES:
            archive_path = Path(archive_root)
            if not archive_path.exists():
                print(f"Archive not found: {archive_root}")
                continue
            
            print(f"  Scanning: {archive_path.name}")
            start_time = datetime.now()
            
            files = list(self._scan_directory_recursive(archive_path))
            eligible_files = [f for f in files if f.is_eligible]
            non_eligible_files = [f for f in files if not f.is_eligible]
            
            duration = (datetime.now() - start_time).total_seconds()
            
            result = ScanResult(
                archive_name=archive_path.name,
                archive_root=archive_root,
                total_files=len(files),
                eligible_files=len(eligible_files),
                non_eligible_files=len(non_eligible_files),
                scan_duration_seconds=duration,
                files=files
            )
            
            results.append(result)
            self.scanned_files.extend(files)
            
            print(f"    Total files: {len(files)}, Eligible: {len(eligible_files)}")
        
        # Scan special Old Resume Gen Python files
        print("Scanning Old Resume Gen Python files...")
        for file_path in OLD_RESUME_GEN_FILES:
            path_obj = Path(file_path)
            if not path_obj.exists():
                print(f"File not found: {file_path}")
                continue
            
            print(f"  Scanning: {path_obj.name}")
            start_time = datetime.now()
            
            file_hash = self._compute_sha256(path_obj)
            is_eligible = self._is_eligible_file(path_obj)
            
            file_info = FileInfo(
                archive_root=str(path_obj.parent),
                archive_name="Old Resume Gen Python",
                relative_path=path_obj.name,
                absolute_path=str(path_obj),
                file_size=path_obj.stat().st_size,
                file_extension=path_obj.suffix.lower(),
                is_eligible=is_eligible,
                sha256_hash=file_hash,
                scan_timestamp=datetime.now().isoformat()
            )
            
            # Create a scan result for this special case
            result = ScanResult(
                archive_name="Old Resume Gen Python",
                archive_root=str(path_obj.parent),
                total_files=1,
                eligible_files=1 if is_eligible else 0,
                non_eligible_files=0 if is_eligible else 1,
                scan_duration_seconds=(datetime.now() - start_time).total_seconds(),
                files=[file_info]
            )
            
            results.append(result)
            self.scanned_files.append(file_info)
        
        return results
    
    def scan_outreach_engine_archives(self) -> List[ScanResult]:
        """Scan all Outreach Engine archives"""
        results = []
        
        print("Scanning Outreach Engine Archives...")
        
        for archive_root in OUTREACH_ENGINE_ARCHIVES:
            archive_path = Path(archive_root)
            if not archive_path.exists():
                print(f"Archive not found: {archive_root}")
                continue
            
            print(f"  Scanning: {archive_path.name}")
            start_time = datetime.now()
            
            files = list(self._scan_directory_recursive(archive_path))
            eligible_files = [f for f in files if f.is_eligible]
            non_eligible_files = [f for f in files if not f.is_eligible]
            
            duration = (datetime.now() - start_time).total_seconds()
            
            result = ScanResult(
                archive_name=archive_path.name,
                archive_root=archive_root,
                total_files=len(files),
                eligible_files=len(eligible_files),
                non_eligible_files=len(non_eligible_files),
                scan_duration_seconds=duration,
                files=files
            )
            
            results.append(result)
            self.scanned_files.extend(files)
            
            print(f"    Total files: {len(files)}, Eligible: {len(eligible_files)}")
        
        return results
    
    def build_hash_index(self):
        """Build hash index for deduplication"""
        self.hash_index = {}
        for file_info in self.scanned_files:
            hash_val = file_info.sha256_hash
            if hash_val not in self.hash_index:
                self.hash_index[hash_val] = []
            self.hash_index[hash_val].append(file_info)
        
        # Print hash collision statistics
        collisions = {h: files for h, files in self.hash_index.items() if len(files) > 1}
        if collisions:
            print(f"Found {len(collisions)} hash collisions (duplicates)")
        else:
            print("No hash collisions found")
    
    def generate_integrity_records(self) -> bool:
        """Generate integrity records for all scanned files"""
        try:
            integrity_dir = self.semantic_cache_root / "integrity"
            
            for file_info in self.scanned_files:
                integrity_file = integrity_dir / f"{file_info.sha256_hash}.integrity.json"
                
                integrity_data = {
                    "hash": file_info.sha256_hash,
                    "archive_root": file_info.archive_root,
                    "archive_name": file_info.archive_name,
                    "relative_path": file_info.relative_path,
                    "file_size": file_info.file_size,
                    "file_extension": file_info.file_extension,
                    "is_eligible": file_info.is_eligible,
                    "scan_timestamp": file_info.scan_timestamp,
                    "integrity_timestamp": datetime.now().isoformat()
                }
                
                if not self.dry_run:
                    with open(integrity_file, 'w', encoding='utf-8') as f:
                        json.dump(integrity_data, f, indent=2)
            
            print(f"Generated {len(self.scanned_files)} integrity records")
            return True
            
        except Exception as e:
            print(f"Failed to generate integrity records: {str(e)}")
            return False
    
    def save_scan_report(self, resume_results: List[ScanResult], outreach_results: List[ScanResult]) -> bool:
        """Save comprehensive scan report"""
        try:
            report_data = {
                "scan_timestamp": datetime.now().isoformat(),
                "scan_summary": {
                    "total_archives": len(resume_results) + len(outreach_results),
                    "resume_engine_archives": len(resume_results),
                    "outreach_engine_archives": len(outreach_results),
                    "total_files_scanned": len(self.scanned_files),
                    "total_eligible_files": sum(1 for f in self.scanned_files if f.is_eligible),
                    "total_non_eligible_files": sum(1 for f in self.scanned_files if not f.is_eligible),
                    "unique_hashes": len(self.hash_index)
                },
                "resume_engine_results": [asdict(r) for r in resume_results],
                "outreach_engine_results": [asdict(r) for r in outreach_results],
                "hash_collisions": {h: [asdict(f) for f in files] 
                                  for h, files in self.hash_index.items() if len(files) > 1}
            }
            
            if not self.dry_run:
                report_path = self.semantic_cache_root / "meta" / "archive_scan_report.json"
                with open(report_path, 'w', encoding='utf-8') as f:
                    json.dump(report_data, f, indent=2)
            
            print("Archive scan report saved")
            return True
            
        except Exception as e:
            print(f"Failed to save scan report: {str(e)}")
            return False
    
    def get_scanned_files(self) -> List[FileInfo]:
        """Get all scanned files"""
        return self.scanned_files
    
    def get_hash_index(self) -> Dict[str, List[FileInfo]]:
        """Get hash index for deduplication"""
        return self.hash_index

def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Archive Scanner with File Hasher")
    parser.add_argument("--dry-run", action="store_true", help="Run in dry-run mode")
    parser.add_argument("--resume-only", action="store_true", help="Scan only Resume Engine archives")
    parser.add_argument("--outreach-only", action="store_true", help="Scan only Outreach Engine archives")
    args = parser.parse_args()
    
    scanner = ArchiveScanner(dry_run=args.dry_run)
    
    print("=== Phase 0.5 Archive Scanner ===")
    print(f"Dry Run: {args.dry_run}")
    print(f"Max Depth: {MAX_DEPTH}")
    print(f"Eligible Extensions: {sorted(ELIGIBLE_EXTENSIONS)}")
    print()
    
    resume_results = []
    outreach_results = []
    
    if not args.outreach_only:
        resume_results = scanner.scan_resume_engine_archives()
    
    if not args.resume_only:
        outreach_results = scanner.scan_outreach_engine_archives()
    
    # Build hash index for deduplication
    scanner.build_hash_index()
    
    # Generate integrity records
    scanner.generate_integrity_records()
    
    # Save scan report
    scanner.save_scan_report(resume_results, outreach_results)
    
    # Print final summary
    total_files = len(scanner.get_scanned_files())
    eligible_files = sum(1 for f in scanner.get_scanned_files() if f.is_eligible)
    unique_hashes = len(scanner.get_hash_index())
    
    print()
    print("=== Scan Summary ===")
    print(f"Total files scanned: {total_files}")
    print(f"Eligible files: {eligible_files}")
    print(f"Non-eligible files: {total_files - eligible_files}")
    print(f"Unique hashes: {unique_hashes}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
