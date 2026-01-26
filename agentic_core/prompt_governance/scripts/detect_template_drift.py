#!/usr/bin/env python3
"""
Template Drift Detection Script (Phase 5)

Detects if a template has been modified on disk without a corresponding 
version bump in the Registry (Instruction Drift detection).
"""

import hashlib
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

def calculate_file_hash(file_path: Path) -> str:
    """Calculate SHA256 hash of file content."""
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
        return hashlib.sha256(content).hexdigest()
    except Exception as e:
        print(f"ERROR: Could not hash {file_path}: {e}")
        return ""

def load_registry(registry_path: Path) -> Dict:
    """Load the prompt registry JSON file."""
    try:
        with open(registry_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"ERROR: Failed to load registry: {e}")
        sys.exit(1)

def detect_template_drift(registry_path: Path, base_dir: Path) -> Tuple[List[Dict], List[Dict]]:
    """
    Detect template drift between registry and disk.
    
    Returns:
        Tuple of (synchronized_entries, drifted_entries)
    """
    registry = load_registry(registry_path)
    synchronized = []
    drifted = []
    
    # Access prompts from the nested structure
    prompts = registry.get('prompts', {})
    
    for template_name, prompt_versions in prompts.items():
        for prompt_data in prompt_versions:
            if not prompt_data.get('active', False):
                continue  # Skip inactive entries
            
            template_path = base_dir / 'templates' / template_name
            
            # Check if file exists
            if not template_path.exists():
                drifted.append({
                    'prompt_id': template_name,
                    'template_path': str(template_path.relative_to(base_dir)),
                    'issue': 'Template file missing',
                    'registry_hash': prompt_data.get('content_hash', 'N/A'),
                    'disk_hash': 'MISSING',
                    'status': 'DRIFT'
                })
                continue
            
            # Calculate current disk hash
            disk_hash = calculate_file_hash(template_path)
            registry_hash = prompt_data.get('content_hash', '')
            
            if not registry_hash:
                drifted.append({
                    'prompt_id': template_name,
                    'template_path': str(template_path.relative_to(base_dir)),
                    'issue': 'No content hash in registry',
                    'registry_hash': 'MISSING',
                    'disk_hash': disk_hash,
                    'status': 'DRIFT'
                })
                continue
            
            # Compare hashes
            if disk_hash != registry_hash:
                drifted.append({
                    'prompt_id': template_name,
                    'template_path': str(template_path.relative_to(base_dir)),
                    'issue': 'Content hash mismatch - template modified without registry update',
                    'registry_hash': registry_hash,
                    'disk_hash': disk_hash,
                    'status': 'DRIFT'
                })
            else:
                synchronized.append({
                    'prompt_id': template_name,
                    'template_path': str(template_path.relative_to(base_dir)),
                    'registry_hash': registry_hash,
                    'disk_hash': disk_hash,
                    'status': 'SYNCHRONIZED'
                })
    
    return synchronized, drifted

def main():
    # Determine paths
    script_dir = Path(__file__).parent
    base_dir = script_dir.parent
    registry_path = base_dir / 'registry.json'
    
    print("Template Drift Detection Audit (Phase 5)")
    print("=" * 50)
    print(f"Registry: {registry_path}")
    print(f"Base Directory: {base_dir}")
    print()
    
    if not registry_path.exists():
        print(f"ERROR: Registry file not found: {registry_path}")
        sys.exit(1)
    
    # Run drift detection
    synchronized, drifted = detect_template_drift(registry_path, base_dir)
    
    # Report results
    print(f"RESULTS:")
    print(f"  Active templates checked: {len(synchronized) + len(drifted)}")
    print(f"  Synchronized: {len(synchronized)}")
    print(f"  Drifted: {len(drifted)}")
    print()
    
    if drifted:
        print("🚨 DRIFTED TEMPLATES (Instruction Drift Detected):")
        for entry in drifted:
            print(f"  ❌ {entry['prompt_id']}: {entry['issue']}")
            print(f"     Template: {entry['template_path']}")
            print(f"     Registry Hash: {entry['registry_hash'][:16]}...")
            print(f"     Disk Hash:     {entry['disk_hash'][:16]}...")
            print()
        
        print("⚠️  ACTION REQUIRED:")
        print("   1. Update registry.json with correct content_hash")
        print("   2. Increment version number if changes are intentional")
        print("   3. Re-run this audit to verify synchronization")
        print()
    else:
        print("✅ ALL TEMPLATES SYNCHRONIZED")
        print("No instruction drift detected.")
        print()
    
    # Show synchronized entries (optional)
    if synchronized and len(synchronized) <= 10:
        print("SYNCHRONIZED TEMPLATES:")
        for entry in synchronized:
            print(f"  ✅ {entry['prompt_id']}: {entry['template_path']}")
        print()
    
    # Exit code
    if drifted:
        print("❌ AUDIT FAILED - Template drift detected")
        sys.exit(1)
    else:
        print("✅ AUDIT PASSED - All templates synchronized")
        sys.exit(0)

if __name__ == "__main__":
    main()
