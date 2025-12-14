#!/usr/bin/env python3
"""Fix deep nesting violations by flattening directory structures."""

import os
import shutil
from pathlib import Path

# Sovereign domains with depth limit 3 (except agentic_core and apps_* which get 4)
SOVEREIGN_DOMAINS = {
    'agentic_core', 'apps_lic', 'apps_rg', 'apps_shared',
    'tests', 'config', 'data', 'archives', 'schemas',
    'prompt_governance', 'observability', 'scripts', 'docs'
}

def fix_deep_nesting():
    """Find and fix deep nesting violations."""
    violations = []
    
    # Find all deep directories
    for root, dirs, files in os.walk('.'):
        # Skip system directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        
        # Calculate depth
        parts = Path(root).parts
        if not parts or parts[0] == '.':
            parts = parts[1:]
        if not parts:
            continue
            
        depth = len(parts)
        root_folder = parts[0]
        
        # Check if in sovereign domain
        if root_folder not in SOVEREIGN_DOMAINS:
            continue
            
        # Determine depth limit
        if 'agentic_core' in root_folder or 'apps_' in root_folder:
            limit = 4
        else:
            limit = 3
            
        if depth > limit:
            violations.append((root, depth, limit))
    
    print(f"Found {len(violations)} deep nesting violations")
    
    # Fix violations by flattening
    for root, depth, limit in violations[:10]:  # Process first 10
        parts = Path(root).parts
        if not parts or parts[0] == '.':
            parts = parts[1:]
            
        # Find target directory (at limit depth)
        target_parts = parts[:limit]
        target_dir = Path(*target_parts)
        
        print(f"Moving contents from {root} to {target_dir}")
        
        # Move all files to target
        for item in os.listdir(root):
            src = Path(root) / item
            dst = target_dir / item
            
            if dst.exists():
                if item.endswith('.py'):
                    # Rename conflicting Python files
                    base, ext = os.path.splitext(item)
                    dst = target_dir / f"{base}_{len(parts)}{ext}"
                else:
                    # Skip other conflicts
                    continue
                    
            try:
                shutil.move(str(src), str(dst))
            except Exception as e:
                print(f"  Error moving {src}: {e}")
        
        # Remove empty directory
        try:
            if not os.listdir(root):
                os.rmdir(root)
        except:
            pass
    
    print(f"Processed {min(10, len(violations))} violations")

if __name__ == "__main__":
    fix_deep_nesting()
