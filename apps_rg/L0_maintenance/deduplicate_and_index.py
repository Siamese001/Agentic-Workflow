#!/usr/bin/env python3
"""
The Librarian - Phase A Sanitization Boot Sequence
Creates active_manifest.json as the single source of truth for all valid files.
Implements content-hashing deduplication to eliminate duplicate files.
"""

import hashlib
import json
import logging
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from shared.config.exclusions import get_python_files, is_excluded_path

logger = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


class FileLibrarian:
    """
    The Librarian manages file deduplication and creates the active manifest.
    Ensures no duplicate, broken, or junk files are processed by the system.
    """
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir).resolve()
        self.content_hashes: Dict[str, str] = {}
        self.duplicates: List[Tuple[str, str]] = []
        self.active_files: List[Dict[str, any]] = []
        self.stats = {
            "total_scanned": 0,
            "excluded": 0,
            "duplicates_removed": 0,
            "active_files": 0
        }
    
    def scan_and_deduplicate(self) -> None:
        """
        Scan all Python files, identify duplicates, and build the active file list.
        """
        logger.info(f"🔍 Starting scan in: {self.root_dir}")
        
        # Get all Python files that are not excluded
        python_files = get_python_files(str(self.root_dir))
        self.stats["total_scanned"] = len(python_files)
        
        logger.info(f"   Found {len(python_files)} Python files to analyze")
        
        # Process each file and build hash map
        for file_path in python_files:
            self._process_file(file_path)
        
        # Identify duplicates
        self._identify_duplicates()
        
        # Build active file list (excluding duplicates)
        self._build_active_manifest()
        
        logger.info(f"✅ Scan complete:")
        logger.info(f"   - Total scanned: {self.stats['total_scanned']}")
        logger.info(f"   - Duplicates removed: {self.stats['duplicates_removed']}")
        logger.info(f"   - Active files: {self.stats['active_files']}")
    
    def _process_file(self, file_path: str) -> None:
        """
        Process a single file: calculate hash and store metadata.
        """
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Calculate SHA-256 hash
            content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
            
            # Store file metadata
            file_info = {
                "path": str(Path(file_path).relative_to(self.root_dir)),
                "absolute_path": str(Path(file_path).resolve()),
                "size": len(content),
                "lines": content.count('\n') + 1,
                "hash": content_hash,
                "last_modified": datetime.fromtimestamp(
                    Path(file_path).stat().st_mtime
                ).isoformat()
            }
            
            # Store in hash map
            if content_hash in self.content_hashes:
                self.duplicates.append((self.content_hashes[content_hash], file_path))
            else:
                self.content_hashes[content_hash] = file_path
                self.active_files.append(file_info)
                
        except Exception as e:
            logger.warning(f"   ⚠️  Failed to process {file_path}: {e}")
            self.stats["excluded"] += 1
    
    def _identify_duplicates(self) -> None:
        """
        Identify and log all duplicate files.
        """
        if self.duplicates:
            logger.info(f"🔍 Found {len(self.duplicates)} duplicate file pairs:")
            for original, duplicate in self.duplicates:
                logger.info(f"   - {duplicate} (duplicate of {original})")
                self.stats["duplicates_removed"] += 1
    
    def _build_active_manifest(self) -> None:
        """
        Build the active manifest with only unique files.
        """
        # Sort files by path for consistent ordering
        self.active_files.sort(key=lambda x: x["path"])
        self.stats["active_files"] = len(self.active_files)
    
    def save_manifest(self, output_path: str = "active_manifest.json") -> None:
        """
        Save the active manifest to a JSON file with atomic write.
        """
        manifest = {
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "root_directory": str(self.root_dir),
            "stats": self.stats,
            "files": self.active_files,
            "duplicates_removed": [
                {"original": orig, "duplicate": dup} 
                for orig, dup in self.duplicates
            ]
        }
        
        # Atomic write: write to temp file first, then rename
        temp_path = f"{output_path}.tmp"
        try:
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)
            
            # Atomic rename
            os.replace(temp_path, output_path)
            logger.info(f"💾 Manifest saved to: {output_path}")
            
        except Exception as e:
            logger.error(f"❌ Failed to save manifest: {e}")
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise
    
    def load_manifest(self, manifest_path: str = "active_manifest.json") -> Dict:
        """
        Load an existing manifest file.
        """
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"⚠️  Manifest not found: {manifest_path}")
            return {}
        except Exception as e:
            logger.error(f"❌ Failed to load manifest: {e}")
            return {}


def get_target_files(manifest_path: str = "active_manifest.json") -> List[str]:
    """
    Helper function for other components to get the list of active files.
    
    Args:
        manifest_path: Path to the active manifest
        
    Returns:
        List of absolute file paths to process
    """
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        return [file_info["absolute_path"] for file_info in manifest["files"]]
        
    except Exception as e:
        logger.error(f"❌ Failed to read manifest: {e}")
        return []


def main():
    """
    Main entry point for the Librarian.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Deduplicate files and create active manifest")
    parser.add_argument("--root", default=".", help="Root directory to scan")
    parser.add_argument("--output", default="active_manifest.json", help="Output manifest file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    parser.add_argument("--check-only", action="store_true", help="Check existing manifest without creating new one")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Check existing manifest if requested
    if args.check_only:
        if os.path.exists(args.output):
            librarian = FileLibrarian(args.root)
            manifest = librarian.load_manifest(args.output)
            if manifest:
                logger.info(f"✅ Existing manifest found:")
                logger.info(f"   - Created: {manifest.get('created_at')}")
                logger.info(f"   - Active files: {manifest.get('stats', {}).get('active_files', 0)}")
                logger.info(f"   - Duplicates removed: {manifest.get('stats', {}).get('duplicates_removed', 0)}")
            else:
                logger.error("❌ Failed to load manifest")
                sys.exit(1)
        else:
            logger.error("❌ No manifest found")
            sys.exit(1)
        return
    
    # Run the librarian
    logger.info("🚀 Starting Librarian - Phase A Sanitization")
    
    librarian = FileLibrarian(args.root)
    librarian.scan_and_deduplicate()
    librarian.save_manifest(args.output)
    
    logger.info("✅ Phase A Sanitization Complete - System Ready for Execution")


if __name__ == "__main__":
    main()
