#!/usr/bin/env python3
"""
Fix all Unicode emojis in Python files to ASCII equivalents.
Prevents Windows encoding issues.
"""

from pathlib import Path

EMOJI_MAP = {
    '✅': '[OK]',
    '⚠️': '[!]',
    '🔧': '[+]',
    '🔄': '[~]',
    '🆕': '[NEW]',
    '♻️': '[REUSE]',
    '🚨': '[ALERT]',
    '🚫': '[X]',
    '❌': '[X]',
    '🧹': '[CLEAN]',
    '🏛️': '[ARCH]',
    '💾': '[SAVE]',
    '🔍': '[SCAN]',
    '📊': '[STATS]',
    '📂': '[DIR]',
    '📋': '[PLAN]',
    '🚀': '[START]',
    '🌱': '[GIT]',
    '🧬': '[CYCLE]',
}

def fix_emojis_in_file(file_path: str) -> bool:
    """Replace all emojis in a file with ASCII equivalents."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Replace each emoji
        for emoji, replacement in EMOJI_MAP.items():
            content = content.replace(emoji, replacement)
        
        # Only write if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Fixed: {file_path}")
            return True
        
        return False
    except Exception as e:
        print(f"✗ Error fixing {file_path}: {e}")
        return False

def main():
    """Find and fix all Python files with emojis."""
    root = Path("c:/Git/Agentic-Workflow")
    
    # Target directories
    targets = [
        root / "agentic_core",
        root / "apps_shared",
    ]
    
    fixed_count = 0
    for target_dir in targets:
        if not target_dir.exists():
            continue
            
        for py_file in target_dir.rglob("*.py"):
            if fix_emojis_in_file(str(py_file)):
                fixed_count += 1
    
    print(f"\n[*] Fixed {fixed_count} files")

if __name__ == "__main__":
    main()
